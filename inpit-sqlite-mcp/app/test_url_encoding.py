#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to verify automatic URL encoding handling with Japanese characters
"""

import requests
import sys

# Set base URL - defaults to localhost:8000 but can be overridden via command line
base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

def test_japanese_applicant_name():
    """Test querying using Japanese applicant name directly in URL."""
    
    print("=== テスト: 日本語出願人名での問い合わせ ===")
    
    # 1. スペースなしの名前でテスト
    test_url = f"{base_url}/applicant/テック株式会社"
    print(f"リクエストURL (スペースなし): {test_url}")
    
    try:
        response = requests.get(test_url)
        print(f"ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            print("成功! レスポンスデータ:")
            result = response.json()
            # Print a summary of the response
            if "success" in result:
                print(f"  - success: {result['success']}")
                if result.get("success"):
                    print(f"  - applicant_name: {result.get('applicant_name', 'N/A')}")
                    print(f"  - count: {result.get('count', 0)}")
                    print(f"  - patents: {len(result.get('patents', []))} 件")
                else:
                    print(f"  - message: {result.get('message', 'N/A')}")
        else:
            print(f"エラー: {response.text}")
    except Exception as e:
        print(f"テスト失敗: {str(e)}")
    
    # 2. スペースを含む名前でテスト
    print("\n--- スペースを含む名前でのテスト ---")
    test_url = f"{base_url}/applicant/テック 株式会社"
    print(f"リクエストURL (スペースあり): {test_url}")
    
    try:
        response = requests.get(test_url)
        print(f"ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            print("成功! レスポンスデータ:")
            result = response.json()
            # Print a summary of the response
            if "success" in result:
                print(f"  - success: {result['success']}")
                if result.get("success"):
                    print(f"  - applicant_name: {result.get('applicant_name', 'N/A')}")
                    print(f"  - count: {result.get('count', 0)}")
                    print(f"  - patents: {len(result.get('patents', []))} 件")
                else:
                    print(f"  - message: {result.get('message', 'N/A')}")
        else:
            print(f"エラー: {response.text}")
    except Exception as e:
        print(f"テスト失敗: {str(e)}")

def test_api_endpoints():
    """Test all API endpoints with Japanese characters."""
    
    # Test both without and with spaces
    applicant_names = ["テック株式会社", "テック 株式会社"]
    
    print("\n=== 各エンドポイントのテスト ===")
    
    for applicant_name in applicant_names:
        print(f"\n--- 出願人名: {applicant_name} ---")
        
        endpoints = [
            f"/applicant/{applicant_name}",
            f"/applicant-summary/{applicant_name}",
            f"/visual-report/{applicant_name}",
            f"/assessment/{applicant_name}",
            f"/technical/{applicant_name}",
            f"/compare/{applicant_name}"
        ]
        
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"
            print(f"\nテスト: {url}")
            
            try:
                response = requests.get(url)
                print(f"ステータスコード: {response.status_code}")
                
                if response.status_code == 200:
                    print("成功!")
                    # Just print success/error status to avoid cluttering output
                    result = response.json()
                    if "success" in result:
                        print(f"  - success: {result['success']}")
                        if not result.get("success") and "message" in result:
                            print(f"  - message: {result.get('message')}")
                else:
                    print(f"エラー: {response.text}")
            except Exception as e:
                print(f"テスト失敗: {str(e)}")

def test_server_status():
    """Test server status endpoint."""
    
    print("\n=== サーバーステータスの確認 ===")
    url = f"{base_url}/status"
    
    try:
        response = requests.get(url)
        print(f"ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            print("成功! サーバーが正常に動作しています。")
        else:
            print(f"エラー: {response.text}")
    except Exception as e:
        print(f"テスト失敗: {str(e)}")

if __name__ == "__main__":
    print(f"サーバーURL: {base_url}")
    
    try:
        # First check if server is up
        requests.get(f"{base_url}/")
        print("サーバーに接続できました。テストを開始します...\n")
        
        # Run all tests
        test_japanese_applicant_name()
        test_api_endpoints()
        test_server_status()
        
        print("\nすべてのテストが完了しました。")
    except requests.exceptions.ConnectionError:
        print(f"エラー: サーバー {base_url} に接続できません。サーバーが起動していることを確認してください。")
    except Exception as e:
        print(f"テスト実行中にエラーが発生しました: {str(e)}")
