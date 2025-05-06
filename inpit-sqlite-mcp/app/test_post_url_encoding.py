#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to verify URL encoding with POST requests containing Japanese characters
"""

import requests
import sys
import subprocess
import json
from urllib.parse import quote

# Set base URL - defaults to localhost:8000 but can be overridden via command line
base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

def test_post_with_urlencode():
    """Test POST requests with URL-encoded Japanese text in form data."""
    
    print("=== テスト: POSTリクエストでの日本語URLエンコーディング ===")
    
    # Test with the SQL endpoint which accepts form data
    test_url = f"{base_url}/sql"
    
    # 1. Test with Japanese characters in the SQL query (no spaces)
    print("\n--- テスト1: 日本語SQLクエリ (スペースなし) ---")
    query = "SELECT * FROM inpit_data WHERE 出願人 LIKE '%テック株式会社%' LIMIT 5"
    data = {"query": query}
    
    print(f"エンドポイント: {test_url}")
    print(f"クエリ: {query}")
    
    try:
        response = requests.post(test_url, data=data)
        print(f"ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            print("成功! レスポンスデータ:")
            result = response.json()
            print_response_summary(result)
        else:
            print(f"エラー: {response.text}")
    except Exception as e:
        print(f"テスト失敗: {str(e)}")
    
    # 2. Test with Japanese characters including spaces
    print("\n--- テスト2: 日本語SQLクエリ (スペースあり) ---")
    query = "SELECT * FROM inpit_data WHERE 出願人 LIKE '%テック 株式会社%' LIMIT 5"
    data = {"query": query}
    
    print(f"エンドポイント: {test_url}")
    print(f"クエリ: {query}")
    
    try:
        response = requests.post(test_url, data=data)
        print(f"ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            print("成功! レスポンスデータ:")
            result = response.json()
            print_response_summary(result)
        else:
            print(f"エラー: {response.text}")
    except Exception as e:
        print(f"テスト失敗: {str(e)}")

def test_post_with_json():
    """Test POST requests with Japanese text in JSON body."""
    
    print("\n=== テスト: JSON形式POSTリクエストでの日本語 ===")
    
    # Test with the SQL JSON endpoint
    test_url = f"{base_url}/sql/json"
    
    # 1. Test with Japanese characters in JSON (no spaces)
    print("\n--- テスト1: 日本語JSON (スペースなし) ---")
    query = "SELECT * FROM inpit_data WHERE 出願人 LIKE '%テック株式会社%' LIMIT 5"
    data = {"query": query}
    
    print(f"エンドポイント: {test_url}")
    print(f"データ: {json.dumps(data, ensure_ascii=False)}")
    
    try:
        response = requests.post(test_url, json=data)
        print(f"ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            print("成功! レスポンスデータ:")
            result = response.json()
            print_response_summary(result)
        else:
            print(f"エラー: {response.text}")
    except Exception as e:
        print(f"テスト失敗: {str(e)}")
    
    # 2. Test with Japanese characters including spaces in JSON
    print("\n--- テスト2: 日本語JSON (スペースあり) ---")
    query = "SELECT * FROM inpit_data WHERE 出願人 LIKE '%テック 株式会社%' LIMIT 5"
    data = {"query": query}
    
    print(f"エンドポイント: {test_url}")
    print(f"データ: {json.dumps(data, ensure_ascii=False)}")
    
    try:
        response = requests.post(test_url, json=data)
        print(f"ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            print("成功! レスポンスデータ:")
            result = response.json()
            print_response_summary(result)
        else:
            print(f"エラー: {response.text}")
    except Exception as e:
        print(f"テスト失敗: {str(e)}")

def test_with_curl():
    """Test using curl with URL encoding."""
    
    print("\n=== テスト: curlを使用した日本語URLエンコーディング ===")
    
    # Test curl with form data and --data-urlencode
    print("\n--- テスト: curl --data-urlencode (スペースを含む日本語) ---")
    curl_cmd = f'curl -X POST "{base_url}/sql" --data-urlencode "query=SELECT * FROM inpit_data WHERE 出願人 LIKE \'%テック 株式会社%\' LIMIT 5"'
    
    print(f"実行コマンド: {curl_cmd}")
    
    try:
        result = subprocess.run(curl_cmd, shell=True, check=True, capture_output=True, text=True)
        print("成功! curlコマンドの出力:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"curlコマンド失敗: {e}")
        print(f"エラー出力: {e.stderr}")
    except Exception as e:
        print(f"テスト失敗: {str(e)}")
    
    # Test another variant similar to the user's example
    print("\n--- テスト: curl POST /applicant --data-urlencode 実例 ---")
    curl_cmd = f'curl -X POST "{base_url}/sql" --data-urlencode "query=SELECT * FROM inpit_data WHERE 出願人 LIKE \'%テック 株式会社%\' LIMIT 5"'
    
    print("ユーザー指定のコマンド構文に沿った例:")
    print(f'curl -X POST "{base_url}/applicant" --data-urlencode "name=テック 株式会社"')
    print("(注: 実際のAPIエンドポイントは実装により異なる場合があります)")
    
    # Create a custom message for the specific test case
    print("\n--- ユーザー指定のコマンドのPython実装例 ---")
    url = f"{base_url}/sql"  # Using SQL endpoint as it's an existing POST endpoint
    encoded_name = quote("テック 株式会社")
    print(f"URLエンコードされた値: name={encoded_name}")
    
    # Show POST request with urlencoded form data
    print("Pythonでの同等実装:")
    print("requests.post(url, data={'query': 'SELECT * FROM inpit_data WHERE 出願人 LIKE \"%テック 株式会社%\" LIMIT 5'})")

def print_response_summary(response):
    """Print a summary of the API response."""
    
    if isinstance(response, dict):
        if "success" in response:
            print(f"  - success: {response['success']}")
        
        if "results" in response:
            results = response["results"]
            print(f"  - 結果件数: {len(results)}")
            
            # Show a sample of the first result if available
            if results and len(results) > 0:
                print("  - 最初の結果サンプル:")
                first = results[0]
                if isinstance(first, dict):
                    for k, v in list(first.items())[:3]:
                        print(f"    {k}: {v}")
                    if len(first) > 3:
                        print(f"    ... (他 {len(first) - 3} フィールド)")
        
        elif "message" in response:
            print(f"  - message: {response['message']}")
    else:
        print(f"  - レスポンス: {response}")

if __name__ == "__main__":
    print(f"サーバーURL: {base_url}")
    
    try:
        # First check if server is up
        requests.get(f"{base_url}/status")
        print("サーバーに接続できました。テストを開始します...\n")
        
        # Run all tests
        test_post_with_urlencode()
        test_post_with_json() 
        test_with_curl()
        
        print("\nすべてのテストが完了しました。")
    except requests.exceptions.ConnectionError:
        print(f"エラー: サーバー {base_url} に接続できません。サーバーが起動していることを確認してください。")
    except Exception as e:
        print(f"テスト実行中にエラーが発生しました: {str(e)}")
