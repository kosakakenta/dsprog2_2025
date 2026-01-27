"""
scraper.py
SUUMOから賃貸物件データ取得（新宿区・世田谷区専用）
"""

import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict
import re


class SuumoScraper:
    """SUUMOから不動産データ取得"""
    
    # ★修正: 渋谷区を削除
    AREA_CODES = {
        '新宿区': '13104',
        '世田谷区': '13112'
    }
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_area(self, area_code: str, area_name: str, pages: int = 3) -> List[Dict]:
        """
        指定エリアの賃貸物件取得
        
        Args:
            area_code: エリアコード（使用されません・互換性のため残す）
            area_name: エリア名（新宿区、世田谷区のみ対応）
            pages: 取得ページ数
            
        Returns:
            物件データのリスト
        """
        
        print(f"\n🏠 SUUMO: {area_name}の物件を取得中...")
        
        # エリアコード取得
        suumo_area_code = self.AREA_CODES.get(area_name)
        
        if not suumo_area_code:
            print(f"   ❌ エリア '{area_name}' は未対応です")
            print(f"   ℹ️  対応エリア: {list(self.AREA_CODES.keys())}")
            return []
        
        properties = []
        
        for page in range(1, pages + 1):
            # エリア別URL構築
            url = (
                f"https://suumo.jp/jj/chintai/ichiran/FR301FC001/"
                f"?ar=030&bs=040&ta=13&sc={suumo_area_code}&page={page}"
            )
            
            print(f"   ページ {page}/{pages}...")
            print(f"   ⏳ 3秒待機中（サーバ負荷軽減）...")
            time.sleep(3)  # ★必須：利用規約遵守
            
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code != 200:
                    print(f"   ❌ HTTP {response.status_code}")
                    continue
                
                # HTML解析
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 物件カセット取得
                cassettos = soup.find_all('div', class_='cassetteitem')
                
                if not cassettos:
                    print(f"   ⚠️ データが見つかりません")
                    continue
                
                print(f"   📝 {len(cassettos)}件検出")
                
                for cassetto in cassettos:
                    try:
                        # 物件名
                        title = cassetto.find('div', class_='cassetteitem_content-title')
                        if not title:
                            continue
                        name = title.get_text(strip=True)
                        
                        # 住所
                        address_tag = cassetto.find('li', class_='cassetteitem_detail-col1')
                        address = address_tag.get_text(strip=True) if address_tag else ''
                        
                        # 各部屋の情報
                        rooms = cassetto.find_all('tbody')
                        
                        for room in rooms:
                            try:
                                # 家賃
                                price_tag = room.find('span', class_='cassetteitem_price--rent')
                                if not price_tag:
                                    continue
                                
                                price_text = price_tag.get_text(strip=True)
                                price = self._extract_number(price_text)
                                
                                if price is None or price < 10000:
                                    continue
                                
                                # 管理費
                                admin_fee_tag = room.find('span', class_='cassetteitem_price--administration')
                                admin_fee = 0
                                if admin_fee_tag:
                                    admin_text = admin_fee_tag.get_text(strip=True)
                                    if admin_text != '-':
                                        admin_fee = self._extract_number(admin_text) or 0
                                
                                # 間取り
                                layout_tag = room.find('span', class_='cassetteitem_madori')
                                layout = layout_tag.get_text(strip=True) if layout_tag else ''
                                
                                # 面積
                                area_tag = room.find('span', class_='cassetteitem_menseki')
                                area_size = area_tag.get_text(strip=True) if area_tag else ''
                                
                                properties.append({
                                    'name': name,
                                    'address': address,
                                    'rent': price,
                                    'admin_fee': admin_fee,
                                    'total': price + admin_fee,
                                    'layout': layout,
                                    'area_size': area_size,
                                    'area_name': area_name
                                })
                            
                            except Exception as e:
                                continue
                    
                    except Exception as e:
                        continue
                
                print(f"   ✅ 累計 {len(properties)}件")
            
            except Exception as e:
                print(f"   ⚠️ エラー: {e}")
                continue
        
        return properties
    
    def _extract_number(self, text: str) -> float:
        """
        テキストから数値を抽出
        「8.5万円」→ 85000
        「5000円」→ 5000
        """
        # 万円表記の場合
        if '万' in text:
            match = re.search(r'([\d.]+)万', text)
            if match:
                return float(match.group(1)) * 10000
        
        # 通常の数値
        text = text.replace(',', '').replace('円', '')
        numbers = re.findall(r'[\d.]+', text)
        if numbers:
            return float(numbers[0])
        
        return None
    
    def scrape_multiple_areas(self, areas: List[Dict], pages: int = 3) -> List[Dict]:
        """
        複数エリアから一括取得
        
        Args:
            areas: [{'code': '13', 'name': '新宿区'}, ...]
            pages: 各エリアで取得するページ数
            
        Returns:
            全物件データのリスト
        """
        
        print("="*70)
        print("🏠 SUUMO: 賃貸物件データ取得開始")
        print("="*70)
        print(f"対象: {len(areas)}エリア × {pages}ページ")
        print(f"予想取得時間: 約{len(areas) * pages * 3}秒")
        print("="*70)
        
        all_properties = []
        
        for area in areas:
            props = self.scrape_area(area['code'], area['name'], pages)
            
            if props:
                all_properties.extend(props)
                print(f"   ✅ {area['name']}: {len(props)}件取得")
            else:
                print(f"   ❌ {area['name']}: 取得失敗")
        
        print(f"\n{'='*70}")
        print(f"✅ 合計 {len(all_properties)}件取得完了")
        
        # エリア別件数確認
        from collections import Counter
        area_count = Counter([p['area_name'] for p in all_properties])
        
        print("\n📊 エリア別内訳:")
        for area_name, count in area_count.items():
            print(f"   {area_name:10s}: {count}件")
        
        print(f"{'='*70}")
        
        return all_properties


def main():
    """テスト実行"""
    scraper = SuumoScraper()
    
    # テストエリア
    test_areas = [
        {'code': '13', 'name': '新宿区'},
        {'code': '13', 'name': '世田谷区'}
    ]
    
    properties = scraper.scrape_multiple_areas(test_areas, pages=1)
    
    if properties:
        print(f"\n【取得データサンプル】")
        for p in properties[:10]:
            print(f"   {p['area_name']:8s} | {p['layout']:6s} | ¥{p['total']:>8,.0f} | {p['name'][:30]}")
        
        # エリア別平均を確認
        from collections import defaultdict
        area_totals = defaultdict(list)
        
        for p in properties:
            area_totals[p['area_name']].append(p['total'])
        
        print(f"\n【エリア別平均家賃】")
        for area, totals in area_totals.items():
            avg = sum(totals) / len(totals)
            print(f"   {area:8s}: ¥{avg:>8,.0f} ({len(totals)}件)")


if __name__ == "__main__":
    main()