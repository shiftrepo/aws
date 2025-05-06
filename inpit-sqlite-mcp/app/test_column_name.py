#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to verify column name handling with Japanese characters
"""

import requests
import json
import sys

# Set base URL - defaults to localhost:8000 but can be overridden via command line
base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

def test_column_names():
    """Test accessing different column names with Japanese characters in SQL queries."""
    
    print("=== テスト: 日本語カラム名でのSQLクエリ ===")
    
    # Test endpoint
    endpoint = f"{base_url}/sql/json"
    
    # List of test queries to check various column names
    test_queries = [
        {
            "name": "全カラム取得",
            "query": "SELECT * FROM inpit_data LIMIT 1"
        },
        {
            "name": "審査状況カラムを確認",
            "query": "SELECT DISTINCT 審査状況 FROM inpit_data WHERE 審査状況 IS NOT NULL LIMIT 10"
        },
        {
            "name": "代替カラム名1",
            "query": "SELECT DISTINCT '審査状況' FROM inpit_data LIMIT 10"
        },
        {
            "name": "カラム名のリスト取得",
            "query": "SELECT name FROM pragma_table_info('inpit_data')"
        },
        {
            "name": "代替カラム名2: シングルクォート",
            "query": "SELECT DISTINCT \"審査状況\" FROM inpit_data WHERE \"審査状況\" IS NOT NULL LIMIT 10"
        },
        {
            "name": "代替カラム名3: バックティック",
            "query": "SELECT DISTINCT `審査状況` FROM inpit_data WHERE `審査状況` IS NOT NULL LIMIT 10"
        },
        {
            "name": "代替: shinsajokyo",
            "query": "SELECT DISTINCT shinsajokyo FROM inpit_data WHERE shinsajokyo IS NOT NULL LIMIT 10"
        },
        {
            "name": "別の日本語カラム: 出願人",
            "query": "SELECT DISTINCT 出願人 FROM inpit_data LIMIT 10"
        }
    ]
    
    for test in test_queries:
        print(f"\n--- テスト: {test['name']} ---")
        print(f"クエリ: {test['query']}")
        
        # Create JSON body with query
        data = {"query": test["query"]}
        
        try:
            # Use JSON content type header
            headers = {"Content-Type": "application/json"}
            
            # Use json parameter to properly encode JSON
            response = requests.post(endpoint, json=data)
            
            print(f"ステータスコード: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("成功! レスポンスデータ:")
                
                if "success" in result:
                    print(f"  - success: {result['success']}")
                
                if "columns" in result:
                    print(f"  - カラム: {result['columns']}")
                
                if "results" in result:
                    results = result["results"]
                    print(f"  - 結果件数: {len(results)}")
                    
                    # Show the first few results
                    if results and len(results) > 0:
                        print("  - 結果サンプル:")
                        for i, row in enumerate(results[:3]):
                            print(f"    {i+1}. {row}")
                        if len(results) > 3:
                            print(f"    ... (他 {len(results) - 3} 件)")
            else:
                print(f"エラー: {response.text}")
        except Exception as e:
            print(f"テスト失敗: {str(e)}")

def dump_schema():
    """Try to dump schema information using SQLite system tables."""
    
    print("\n=== スキーマ情報の取得 ===")
    
    # Test endpoint
    endpoint = f"{base_url}/sql/json"
    
    queries = [
        # Try using SQLite master table to get table information
        "SELECT name FROM sqlite_master WHERE type='table'",
        
        # Try alternative approaches to get schema info
        "SELECT * FROM sqlite_master WHERE type='table' AND name='inpit_data'",
    ]
    
    for query in queries:
        print(f"\nクエリ: {query}")
        data = {"query": query}
        
        try:
            response = requests.post(endpoint, json=data)
            print(f"ステータスコード: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("成功! スキーマ情報:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(f"エラー: {response.text}")
        except Exception as e:
            print(f"スキーマ取得失敗: {str(e)}")

if __name__ == "__main__":
    print(f"サーバーURL: {base_url}")
    
    try:
        # First check if server is up
        response = requests.get(f"{base_url}/status")
        print("サーバーに接続できました。テストを開始します...\n")
        
        # Get basic schema information to understand the database
        dump_schema()
        
        # Run column name tests
        test_column_names()
        
        print("\nすべてのテストが完了しました。")
    except requests.exceptions.ConnectionError:
        print(f"エラー: サーバー {base_url} に接続できません。サーバーが起動していることを確認してください。")
    except Exception as e:
        print(f"テスト実行中にエラーが発生しました: {str(e)}")
