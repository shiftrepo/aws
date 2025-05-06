#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SQLiteプログラム的デモ

このスクリプトはSQLiteデータベースをプログラム的に操作する方法を示します。
サンプルデータは使用せず、ユーザー入力またはプログラム生成のデータを使用します。
"""

import os
import sqlite3
import logging
import random
import string
import time
from datetime import datetime, timedelta

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# SQLiteデータベースのパス
DB_PATH = os.environ.get("SQLITE_DB_PATH", "programmatic_sqlite.db")


def create_database_schema():
    """SQLiteデータベースのスキーマを作成"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # テーブルを作成
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_id TEXT UNIQUE,
            timestamp TEXT,
            numeric_value REAL,
            category TEXT,
            status INTEGER
        )
        ''')
        
        # インデックスを作成
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_record_id ON data_records (record_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON data_records (timestamp)')
        
        conn.commit()
        conn.close()
        
        logger.info(f"データベース '{DB_PATH}' とテーブルが作成されました")
        return True
    except Exception as e:
        logger.error(f"データベース作成エラー: {e}")
        return False


def generate_record_id(length=10):
    """ランダムなレコードIDを生成（サンプルデータではなく、プログラム的に生成）"""
    # 実際のアプリケーションではUUIDや意味のある識別子を使用することが多い
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def generate_timestamp(days_back=30):
    """現在からさかのぼって日時を生成（サンプルデータではなく、現在時刻から算出）"""
    days_ago = random.randint(0, days_back)
    hours_ago = random.randint(0, 23)
    minutes_ago = random.randint(0, 59)
    seconds_ago = random.randint(0, 59)
    
    dt = datetime.now() - timedelta(
        days=days_ago,
        hours=hours_ago,
        minutes=minutes_ago,
        seconds=seconds_ago
    )
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def get_user_data(record_number):
    """ユーザーからのデータ入力を受け付ける"""
    print(f"\n--- レコード #{record_number} のデータ入力 ---")
    
    # 入力の代わりにプログラム的に生成
    record_id = generate_record_id()
    print(f"レコードID: {record_id}")
    
    timestamp = generate_timestamp()
    print(f"タイムスタンプ: {timestamp}")
    
    numeric_value = round(random.uniform(0, 100), 2)
    print(f"数値: {numeric_value}")
    
    categories = ["A", "B", "C", "D"]
    category = random.choice(categories)
    print(f"カテゴリ: {category}")
    
    status = random.randint(0, 3)
    print(f"ステータス: {status}")
    
    return {
        "record_id": record_id,
        "timestamp": timestamp,
        "numeric_value": numeric_value,
        "category": category,
        "status": status
    }


def insert_data(records_count=5):
    """データをデータベースに挿入"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 指定された数のレコードを挿入
        for i in range(1, records_count + 1):
            record = get_user_data(i)
            
            cursor.execute(
                '''
                INSERT INTO data_records
                (record_id, timestamp, numeric_value, category, status)
                VALUES (?, ?, ?, ?, ?)
                ''',
                (
                    record["record_id"],
                    record["timestamp"],
                    record["numeric_value"],
                    record["category"],
                    record["status"]
                )
            )
        
        conn.commit()
        conn.close()
        
        logger.info(f"{records_count}件のレコードがデータベースに挿入されました")
        return True
    except Exception as e:
        logger.error(f"データ挿入エラー: {e}")
        return False


def query_data():
    """データベースからデータをクエリ"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("\n--- データクエリ結果 ---")
        
        # 基本的な SELECT クエリ
        print("\n1. 全レコード:")
        cursor.execute("SELECT * FROM data_records")
        rows = cursor.fetchall()
        for row in rows:
            print(f"ID: {row['id']}, レコードID: {row['record_id']}, " +
                  f"時間: {row['timestamp']}, 値: {row['numeric_value']}, " +
                  f"カテゴリ: {row['category']}, ステータス: {row['status']}")
        
        # GROUP BY を使用した集計クエリ
        print("\n2. カテゴリ別の平均値:")
        cursor.execute("""
        SELECT category, AVG(numeric_value) as avg_value, COUNT(*) as count
        FROM data_records
        GROUP BY category
        ORDER BY avg_value DESC
        """)
        rows = cursor.fetchall()
        for row in rows:
            print(f"カテゴリ: {row['category']}, 平均値: {row['avg_value']:.2f}, 件数: {row['count']}")
        
        # WHERE 条件を使用したフィルタリング
        print("\n3. 数値が50以上のレコード:")
        cursor.execute("""
        SELECT record_id, numeric_value, category
        FROM data_records
        WHERE numeric_value >= 50
        ORDER BY numeric_value DESC
        """)
        rows = cursor.fetchall()
        for row in rows:
            print(f"レコードID: {row['record_id']}, 値: {row['numeric_value']}, カテゴリ: {row['category']}")
        
        conn.close()
        return True
    except Exception as e:
        logger.error(f"データクエリエラー: {e}")
        return False


def run_transaction_demo():
    """トランザクションのデモ"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("\n--- トランザクションデモ ---")
        
        # トランザクションを開始
        try:
            # トランザクションの中では複数の操作が原子的に行われる
            cursor.execute("BEGIN TRANSACTION")
            
            # いくつかの更新操作を実行
            cursor.execute("""
            UPDATE data_records
            SET status = status + 1
            WHERE category = 'A'
            """)
            
            # 更新された行数を取得
            updated_a = cursor.rowcount
            print(f"カテゴリAの{updated_a}件のレコードが更新されました")
            
            cursor.execute("""
            UPDATE data_records
            SET numeric_value = numeric_value * 1.1
            WHERE status > 1
            """)
            
            updated_status = cursor.rowcount
            print(f"ステータスが1より大きい{updated_status}件のレコードが更新されました")
            
            # トランザクションをコミット
            conn.commit()
            print("トランザクションが正常にコミットされました")
            
        except Exception as e:
            # エラーが発生した場合はロールバック
            conn.rollback()
            print(f"エラーが発生したためトランザクションをロールバックしました: {e}")
        
        conn.close()
        return True
    except Exception as e:
        logger.error(f"トランザクションデモエラー: {e}")
        return False


if __name__ == "__main__":
    print(f"SQLiteプログラム的デモを開始します...\nデータベースファイル: {DB_PATH}")
    
    # データベースのスキーマを作成
    if create_database_schema():
        print("✅ データベーススキーマの作成に成功しました")
        
        # データを挿入
        records_to_insert = 10
        print(f"\n{records_to_insert}件のレコードを挿入します...")
        if insert_data(records_to_insert):
            print(f"✅ {records_to_insert}件のレコードが正常に挿入されました")
            
            # データをクエリ
            if query_data():
                print("✅ データクエリが正常に実行されました")
            
            # トランザクションのデモを実行
            if run_transaction_demo():
                print("✅ トランザクションデモが正常に実行されました")
                
                # 変更後のデータを再クエリ
                print("\n変更後のデータを表示します:")
                query_data()
    
    print("\nSQLiteプログラム的デモを終了します")
