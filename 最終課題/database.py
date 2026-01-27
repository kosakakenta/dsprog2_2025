"""
database.py
SQLiteでデータベース管理
"""

import sqlite3
from typing import List, Dict
import pandas as pd
from pathlib import Path


class PropertyDatabase:
    """不動産データベース管理"""
    
    def __init__(self, db_path: str = 'data/properties.db'):
        """
        データベース初期化
        
        Args:
            db_path: データベースファイルパス
        """
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.create_table()
    
    def create_table(self):
        """テーブル作成"""
        with sqlite3.connect(self.db_path) as conn:
            # 物件テーブル作成
            conn.execute("""
                CREATE TABLE IF NOT EXISTS properties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    address TEXT,
                    rent REAL NOT NULL,
                    admin_fee REAL DEFAULT 0,
                    total REAL NOT NULL,
                    layout TEXT,
                    area_size TEXT,
                    area_name TEXT NOT NULL,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # インデックス作成（検索高速化）
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_area_name 
                ON properties(area_name)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_layout 
                ON properties(layout)
            """)
            
            conn.commit()
        
        print(f"✅ データベース初期化完了: {self.db_path}")
    
    def save_properties(self, properties: List[Dict]) -> int:
        """
        物件データを保存
        
        Args:
            properties: 物件データのリスト
            
        Returns:
            保存した件数
        """
        
        with sqlite3.connect(self.db_path) as conn:
            for p in properties:
                conn.execute("""
                    INSERT INTO properties 
                    (name, address, rent, admin_fee, total, layout, area_size, area_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    p['name'], p['address'], p['rent'], p['admin_fee'],
                    p['total'], p['layout'], p['area_size'], p['area_name']
                ))
            conn.commit()
        
        print(f"✅ {len(properties)}件をデータベースに保存")
        return len(properties)
    
    def get_all_properties(self) -> pd.DataFrame:
        """
        全物件データ取得
        
        Returns:
            全物件のDataFrame
        """
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query("SELECT * FROM properties", conn)
    
    def get_properties_by_area(self, area_name: str) -> pd.DataFrame:
        """
        エリア別物件取得（動的クエリ - 入力に応じて出力が変化）
        
        Args:
            area_name: エリア名
            
        Returns:
            該当エリアの物件DataFrame
        """
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT * FROM properties WHERE area_name = ?"
            return pd.read_sql_query(query, conn, params=(area_name,))
    
    def get_properties_by_conditions(self, 
                                      area: str = None,
                                      min_rent: float = None,
                                      max_rent: float = None,
                                      layout: str = None) -> pd.DataFrame:
        """
        条件指定で物件取得（動的クエリ - 入力に応じて出力が変化）
        
        Args:
            area: エリア名（任意）
            min_rent: 最低家賃（任意）
            max_rent: 最高家賃（任意）
            layout: 間取り（任意）
            
        Returns:
            条件に合う物件のDataFrame
        """
        
        conditions = []
        params = []
        
        if area:
            conditions.append("area_name = ?")
            params.append(area)
        
        if min_rent:
            conditions.append("total >= ?")
            params.append(min_rent)
        
        if max_rent:
            conditions.append("total <= ?")
            params.append(max_rent)
        
        if layout:
            conditions.append("layout = ?")
            params.append(layout)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = f"SELECT * FROM properties WHERE {where_clause}"
        
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(query, conn, params=params)
    
    def get_area_stats(self) -> pd.DataFrame:
        """
        エリア別統計
        
        Returns:
            エリア別の件数・平均・最小・最大のDataFrame
        """
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT 
                    area_name,
                    COUNT(*) as count,
                    AVG(total) as avg_rent,
                    MIN(total) as min_rent,
                    MAX(total) as max_rent
                FROM properties
                GROUP BY area_name
                ORDER BY avg_rent DESC
            """
            return pd.read_sql_query(query, conn)
    
    def get_layout_stats(self) -> pd.DataFrame:
        """
        間取り別統計
        
        Returns:
            間取り別の件数・平均・最小・最大のDataFrame
        """
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT 
                    layout,
                    COUNT(*) as count,
                    AVG(total) as avg_rent,
                    MIN(total) as min_rent,
                    MAX(total) as max_rent
                FROM properties
                WHERE layout != ''
                GROUP BY layout
                HAVING COUNT(*) >= 5
                ORDER BY avg_rent DESC
            """
            return pd.read_sql_query(query, conn)
    
    def clear_all(self):
        """全データ削除"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM properties")
            conn.commit()
        print("🗑️ 全データを削除しました")
    
    def get_count(self) -> int:
        """総件数取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM properties")
            return cursor.fetchone()[0]


def main():
    """テスト"""
    db = PropertyDatabase()
    
    # サンプルデータ
    sample = [{
        'name': 'テストマンション',
        'address': '東京都新宿区',
        'rent': 80000,
        'admin_fee': 5000,
        'total': 85000,
        'layout': '1K',
        'area_size': '25m²',
        'area_name': '新宿区'
    }]
    
    db.save_properties(sample)
    
    # 動的クエリテスト
    print("\n【動的クエリテスト】")
    result = db.get_properties_by_conditions(area='新宿区', max_rent=100000)
    print(f"新宿区で10万円以下: {len(result)}件")
    
    print(f"\n総件数: {db.get_count()}件")


if __name__ == "__main__":
    main()