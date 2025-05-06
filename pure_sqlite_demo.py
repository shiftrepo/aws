#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SQLiteのみのデモ

このスクリプトはBigQueryに接続せず、SQLiteデータベースを作成し
基本的なSQLite操作を実演します。
"""

import os
import sys
import sqlite3
import logging
from datetime import datetime

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# SQLiteデータベースのパス
DB_PATH = os.environ.get("SQLITE_DB_PATH", "pure_sqlite_test.db")


def create_database_schema():
    """
    SQLiteデータベースのスキーマを作成
    """
    try:
        # データベース接続（存在しない場合は自動的に作成される）
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # テーブルを作成
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS publications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            publication_number TEXT UNIQUE,
            filing_date TEXT,
            publication_date TEXT,
            application_number TEXT,
            assignee TEXT,
            title TEXT,
            abstract TEXT,
            ipc_code TEXT,
            family_id TEXT,
            country_code TEXT
        )
        ''')
        
        # インデックスを作成
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pub_number ON publications (publication_number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_app_number ON publications (application_number)')
        
        conn.commit()
        conn.close()
        
        logger.info(f"データベース '{DB_PATH}' とテーブルが作成されました")
        return True
    except Exception as e:
        logger.error(f"データベース作成エラー: {e}")
        return False


def execute_query(query, params=None):
    """
    SQLクエリを実行する
    
    Args:
        query: 実行するSQLクエリ
        params: クエリパラメータ (オプション)
    
    Returns:
        結果の行のリスト
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # 行を辞書のように扱えるようにする
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # SELECTクエリの場合は結果を取得
        if query.strip().upper().startswith("SELECT"):
            rows = [dict(row) for row in cursor.fetchall()]
            result = rows
        else:
            conn.commit()
            result = {"affected_rows": cursor.rowcount}
        
        conn.close()
        return result
    except Exception as e:
        logger.error(f"クエリ実行エラー: {e}")
        return None


def show_database_stats():
    """
    データベースの統計情報を表示
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # データベース内のテーブル一覧を取得
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("\nデータベース内のテーブル:")
        for table in tables:
            table_name = table[0]
            print(f"- {table_name}")
            
            # テーブルのカラム情報を取得
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print("  カラム:")
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                print(f"  - {col_name} ({col_type}){' PRIMARY KEY' if pk else ''}")
            
            # 各テーブルの行数を取得
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            print(f"  行数: {row_count}")
            print()
        
        conn.close()
        return True
    except Exception as e:
        logger.error(f"データベース統計表示エラー: {e}")
        return False


def run_interactive_query():
    """
    インタラクティブなSQLクエリ実行
    """
    print("\nSQLiteインタラクティブクエリ実行（終了するには 'exit' と入力）")
    print("例: SELECT * FROM publications LIMIT 5")
    
    while True:
        sql = input("\nSQLクエリ> ")
        if sql.lower() in ('exit', 'quit', 'q'):
            break
        
        try:
            results = execute_query(sql)
            if results is not None:
                if isinstance(results, list):
                    if len(results) > 0:
                        # カラム名を表示
                        columns = list(results[0].keys())
                        print("\n" + " | ".join(columns))
                        print("-" * (sum(len(c) for c in columns) + 3 * (len(columns) - 1)))
                        
                        # 結果を表示
                        for row in results:
                            print(" | ".join(str(row[c]) for c in columns))
                        
                        print(f"\n{len(results)}行が返されました")
                    else:
                        print("結果はありません")
                else:
                    print(f"クエリが実行されました: {results.get('affected_rows', 0)}行が影響を受けました")
        except Exception as e:
            print(f"エラー: {e}")


if __name__ == "__main__":
    print("SQLiteデモを開始します...")
    print(f"データベースファイル: {DB_PATH}")
    
    # データベースのスキーマを作成
    if create_database_schema():
        print("✅ データベーススキーマの作成に成功しました")
        
        # データベースの統計情報を表示
        show_database_stats()
        
        # インタラクティブなクエリ実行
        print("\nSQLiteの準備ができました。")
        print("以下のオプションから選択してください:")
        print("1. インタラクティブSQLクエリを実行")
        print("2. 終了")
        
        choice = input("\n選択> ")
        
        if choice == '1':
            run_interactive_query()
        
        print("\nSQLiteデモを終了します")
    else:
        print("❌ データベーススキーマの作成に失敗しました")
