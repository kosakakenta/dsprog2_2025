"""
main.py
不動産データ分析メインスクリプト
"""

from scraper import SuumoScraper
from database import PropertyDatabase
from analyzer import PropertyAnalyzer


def main():
    """メインフロー"""
    
    print("\n" + "="*70)
    print("🏠 不動産データ分析プロジェクト")
    print("="*70)
    print("仮説: 新宿区は世田谷区より平均家賃が30%以上高い")
    print("="*70)
    
    # [1/3] データ取得
    print("\n[1/3] 🌐 データ取得中...")
    
    scraper = SuumoScraper()
    
    # ★修正: 新宿区と世田谷区のみ
    target_areas = [
        {'code': '13', 'name': '新宿区'},
        {'code': '13', 'name': '世田谷区'}
    ]
    
    # 各エリア3ページ取得
    properties = scraper.scrape_multiple_areas(target_areas, pages=3)
    
    if not properties:
        print("❌ データ取得失敗")
        return
    
    print(f"\n{'='*70}")
    print(f"✅ 合計 {len(properties)}件取得完了（全て実データ）")
    print(f"{'='*70}")
    
    # [2/3] データベース保存
    print("\n[2/3] 💾 データベース保存中...")
    
    db = PropertyDatabase()
    
    # 既存データクリア
    db.clear_all()
    
    # 新規データ保存
    saved = db.save_properties(properties)
    print(f"✅ {saved}件をデータベースに保存完了")
    
    # [3/3] データ分析
    print("\n[3/3] 📊 データ分析中...")
    
    analyzer = PropertyAnalyzer(db)
    
    # 仮説検証
    result = analyzer.verify_hypothesis()
    
    # グラフ生成
    analyzer.plot_comparison()
    
    # サマリー生成
    summary = analyzer.generate_summary(result)
    print(summary)
    
    print("\n" + "="*70)
    print("✅ 全処理完了！")
    print("="*70)
    print("📁 出力ファイル:")
    print("   - data/properties.db (データベース)")
    print("   - images/area_comparison.png (グラフ1)")
    print("   - images/layout_comparison.png (グラフ2)")
    print("="*70)


if __name__ == "__main__":
    main()