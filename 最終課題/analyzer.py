"""
analyzer.py
Hypothesis Testing: Is Shinjuku 30%+ more expensive than Setagaya?
"""

import pandas as pd
from scipy import stats
from pathlib import Path

# Matplotlib settings (no GUI, image save only)
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import seaborn as sns

from database import PropertyDatabase


class PropertyAnalyzer:
    """Real Estate Data Analysis (Shinjuku vs Setagaya)"""
    
    def __init__(self, db: PropertyDatabase):
        """
        Initialize Analyzer
        
        Args:
            db: PropertyDatabase instance
        """
        self.db = db
        Path('images').mkdir(exist_ok=True)
        sns.set_style("whitegrid")
        
        print(f"✅ Matplotlib backend: {matplotlib.get_backend()}")
    
    def verify_hypothesis(self):
        """
        Hypothesis Testing:
        "Shinjuku's average rent is 30%+ higher than Setagaya"
        
        Returns:
            dict: Test results
        """
        
        print("\n" + "="*70)
        print("Hypothesis Test: Shinjuku vs Setagaya Rent Difference")
        print("="*70)
        
        # Get data
        df = self.db.get_all_properties()
        
        # Extract data
        shinjuku = df[df['area_name'] == '新宿区']['total']
        setagaya = df[df['area_name'] == '世田谷区']['total']
        
        # Basic statistics
        shinjuku_avg = shinjuku.mean()
        shinjuku_std = shinjuku.std()
        setagaya_avg = setagaya.mean()
        setagaya_std = setagaya.std()
        
        # Calculate difference
        diff = shinjuku_avg - setagaya_avg
        diff_rate = (diff / setagaya_avg) * 100
        
        # Welch's t-test (unequal variance)
        t_stat, p_value = stats.ttest_ind(shinjuku, setagaya, equal_var=False)
        
        # Display results
        print(f"\n📊 Data Summary:")
        print(f"   Shinjuku:  {len(shinjuku)} properties")
        print(f"   Setagaya:  {len(setagaya)} properties")
        
        print(f"\n💰 Average Rent:")
        print(f"   Shinjuku:  ¥{shinjuku_avg:>10,.0f} (SD: ¥{shinjuku_std:,.0f})")
        print(f"   Setagaya:  ¥{setagaya_avg:>10,.0f} (SD: ¥{setagaya_std:,.0f})")
        print(f"   Difference: ¥{diff:>10,.0f}")
        print(f"   Diff Rate:  {diff_rate:>10.1f}%")
        
        print(f"\n📈 Statistical Test (Welch's t-test):")
        print(f"   t-statistic: {t_stat:.3f}")
        
        # p-value display
        if p_value < 0.001:
            print(f"   p-value: p < 0.001 (extremely significant)")
            p_display = "p < 0.001"
        elif p_value < 0.01:
            print(f"   p-value: p < 0.01")
            p_display = f"p = {p_value:.3f}"
        elif p_value < 0.05:
            print(f"   p-value: p = {p_value:.3f}")
            p_display = f"p = {p_value:.3f}"
        else:
            print(f"   p-value: p = {p_value:.3f}")
            p_display = f"p = {p_value:.3f}"
        
        if p_value < 0.05:
            print(f"   ✅ Statistically significant (p < 0.05)")
        else:
            print(f"   ⚠️  Not significant (p >= 0.05)")
        
        print(f"\n🎯 Hypothesis Result:")
        if diff_rate >= 30:
            print(f"   ✅ ACCEPTED")
            print(f"      Shinjuku is {diff_rate:.1f}% higher (30%+)")
        else:
            print(f"   ❌ REJECTED")
            print(f"      Difference is {diff_rate:.1f}% (< 30%)")
        
        # Practical implications
        annual_diff = diff * 12
        five_year_diff = annual_diff * 5
        
        print(f"\n💡 Practical Implications:")
        print(f"   Monthly:  ¥{diff:,.0f}")
        print(f"   Annually: ¥{annual_diff:,.0f}")
        print(f"   5-Year:   ¥{five_year_diff:,.0f}")
        print(f"   → Save ¥{five_year_diff/10000:.0f} million in 5 years by choosing Setagaya!")
        
        return {
            'high_area': 'Shinjuku',
            'low_area': 'Setagaya',
            'high_avg': shinjuku_avg,
            'high_std': shinjuku_std,
            'low_avg': setagaya_avg,
            'low_std': setagaya_std,
            'diff': diff,
            'diff_rate': diff_rate,
            't_stat': t_stat,
            'p_value': p_value,
            'p_display': p_display,
            'hypothesis_accepted': diff_rate >= 30,
            'annual_diff': annual_diff,
            'five_year_diff': five_year_diff
        }
    
    def plot_comparison(self):
        """Generate comparison charts (2 types)"""
        
        print("\n📊 Generating charts...")
        
        df = self.db.get_all_properties()
        
        # Filter 2 areas
        df = df[df['area_name'].isin(['新宿区', '世田谷区'])]
        df['area_en'] = df['area_name'].map({'新宿区': 'Shinjuku', '世田谷区': 'Setagaya'})
        
        # Chart 1: Average Rent + Boxplot
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Left: Bar chart
        area_stats = df.groupby('area_en')['total'].agg(['mean', 'count']).reset_index()
        area_stats.columns = ['area', 'avg_rent', 'count']
        area_stats = area_stats.sort_values('avg_rent', ascending=False)
        
        colors = ['#e74c3c', '#2ecc71']
        
        bars = axes[0].bar(area_stats['area'], area_stats['avg_rent'],
                          color=colors, edgecolor='black', linewidth=2, alpha=0.85)
        
        axes[0].set_ylabel('Average Rent (JPY)', fontsize=14, fontweight='bold')
        axes[0].set_title('Average Rent by Area', fontsize=16, fontweight='bold', pad=15)
        axes[0].grid(axis='y', alpha=0.3, linestyle='--')
        
        # Display values
        for bar, count in zip(bars, area_stats['count']):
            height = bar.get_height()
            axes[0].text(bar.get_x() + bar.get_width()/2., height,
                        f'¥{height:,.0f}\n({int(count)} units)',
                        ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # Right: Boxplot
        data_list = []
        labels = []
        for area in ['Shinjuku', 'Setagaya']:
            data = df[df['area_en'] == area]['total']
            if len(data) > 0:
                data_list.append(data)
                labels.append(area)
        
        bp = axes[1].boxplot(data_list, labels=labels, patch_artist=True,
                            widths=0.6, showmeans=True,
                            meanprops=dict(marker='D', markerfacecolor='red', markersize=8))
        
        # Colors
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        axes[1].set_ylabel('Rent (JPY)', fontsize=14, fontweight='bold')
        axes[1].set_title('Rent Distribution by Area', fontsize=16, fontweight='bold', pad=15)
        axes[1].grid(axis='y', alpha=0.3, linestyle='--')
        axes[1].legend(['Mean'], loc='upper right')
        
        plt.suptitle(f'Tokyo 2 Wards: Rental Property Comparison ({len(df)} units)',
                    fontsize=18, fontweight='bold', y=0.98)
        
        plt.tight_layout()
        plt.savefig('images/area_comparison.png', dpi=300, bbox_inches='tight')
        print("✅ images/area_comparison.png saved")
        plt.close()
        
        # Chart 2: By layout
        self._plot_layout_by_area(df)
    
    def _plot_layout_by_area(self, df):
        """Layout × Area comparison chart"""
        
        # Top 8 layouts
        main_layouts = df['layout'].value_counts().head(8).index
        df_main = df[df['layout'].isin(main_layouts)]
        
        # Pivot table
        pivot = df_main.pivot_table(
            values='total',
            index='layout',
            columns='area_en',
            aggfunc='mean'
        )
        
        # Sort by average
        pivot['avg'] = pivot.mean(axis=1)
        pivot = pivot.sort_values('avg', ascending=True)
        pivot = pivot.drop('avg', axis=1)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        pivot.plot(kind='barh', ax=ax, width=0.7,
                  color=['#e74c3c', '#2ecc71'],
                  edgecolor='black', linewidth=1.5)
        
        ax.set_xlabel('Average Rent (JPY)', fontsize=14, fontweight='bold')
        ax.set_ylabel('Layout Type', fontsize=14, fontweight='bold')
        ax.set_title('Average Rent by Layout and Area', fontsize=16, fontweight='bold', pad=15)
        ax.legend(title='Area', fontsize=11, title_fontsize=12, loc='lower right')
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        # Display values
        for container in ax.containers:
            ax.bar_label(container, fmt='¥%.0f', padding=3, fontsize=9)
        
        plt.tight_layout()
        plt.savefig('images/layout_comparison.png', dpi=300, bbox_inches='tight')
        print("✅ images/layout_comparison.png saved")
        plt.close()
    
    def generate_summary(self, result: dict) -> str:
        """
        Generate final summary
        
        Args:
            result: verify_hypothesis() return value
            
        Returns:
            Summary string
        """
        
        df = self.db.get_all_properties()
        area_stats = df.groupby('area_name')['total'].agg(['mean', 'count']).reset_index()
        area_stats.columns = ['area_name', 'avg_rent', 'count']
        area_stats = area_stats.sort_values('avg_rent', ascending=False)
        
        total = len(df)
        date = df['scraped_at'].iloc[0][:10] if len(df) > 0 else 'N/A'
        
        summary = f"""
{'='*70}
📊 Tokyo 2 Wards: Rental Property Data Analysis Report
{'='*70}

[1. Data Overview]
✅ Total Properties: {total} (Real Data)
✅ Target Areas: Shinjuku, Setagaya
✅ Scraped: {date}
✅ Data Source: SUUMO

[2. Area Statistics]
"""
        
        area_map = {'新宿区': 'Shinjuku', '世田谷区': 'Setagaya'}
        for _, row in area_stats.iterrows():
            en_name = area_map.get(row['area_name'], row['area_name'])
            summary += f"   {en_name:10s}: Avg ¥{row['avg_rent']:>8,.0f} ({int(row['count'])} units)\n"
        
        summary += f"""
[3. Hypothesis Test Results]
Hypothesis: "Shinjuku's average rent is 30%+ higher than Setagaya"

Result: {'✅ ACCEPTED' if result['hypothesis_accepted'] else '❌ REJECTED'}

   Shinjuku Avg:  ¥{result['high_avg']:,.0f}
   Setagaya Avg:  ¥{result['low_avg']:,.0f}
   Difference:    {result['diff_rate']:.1f}%
   
   Statistical Test: t = {result['t_stat']:.3f}, {result['p_display']}
   Significance: {'Yes (p < 0.05)' if result['p_value'] < 0.05 else 'No (p >= 0.05)'}

[4. Key Insights]
💰 Monthly Difference:  ¥{result['diff']:,.0f}
💰 Annual Difference:   ¥{result['annual_diff']:,.0f}
💰 5-Year Difference:   ¥{result['five_year_diff']:,.0f}

🎯 Conclusion:
Save ¥{result['annual_diff']/10000:.0f} million/year by choosing Setagaya!
That's ¥{result['five_year_diff']/10000:.0f} million over 5 years.

Data proves a {result['diff_rate']:.1f}% rent difference between
Shinjuku (urban/business) and Setagaya (suburban/residential).

{'='*70}
"""
        
        return summary


def main():
    """Main execution"""
    db = PropertyDatabase()
    analyzer = PropertyAnalyzer(db)
    
    print("\n🏠 Real Estate Data Analysis Started")
    
    # Hypothesis testing
    result = analyzer.verify_hypothesis()
    
    # Generate charts
    analyzer.plot_comparison()
    
    # Summary
    summary = analyzer.generate_summary(result)
    print(summary)
    
    print("\n✅ Analysis Complete!")
    print("   - images/area_comparison.png")
    print("   - images/layout_comparison.png")


if __name__ == "__main__":
    main()