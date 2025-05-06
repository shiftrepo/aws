#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple test script to verify the fix for handling spaces in Japanese URLs
"""

import requests
import urllib.parse
import sys
from urllib.parse import quote

# Set base URL - defaults to localhost:8000 but can be overridden via command line
base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

def test_japanese_with_spaces():
    """Test URL encoding handling with Japanese company names containing spaces"""
    
    print("===== 日本語スペース処理テスト =====")
    
    # Test cases - different representations of "テック 株式会社" (Tech Corporation)
    test_cases = [
        {
            "name": "直接スペース",
            "url": f"{base_url}/applicant/テック 株式会社",
            "description": "URLに直接スペース（問題が発生するケース）"
        },
        {
            "name": "%20によるスペース",
            "url": f"{base_url}/applicant/テック%20株式会社",
            "description": "スペースを%20にエンコード"
        },
        {
            "name": "クオートによるスペース",
            "url": f"{base_url}/applicant/テック 株式会社",
            "quoted": True,
            "description": "クオートでスペースを含むURLをラップ"
        },
        {
            "name": "完全URLエンコード",
            "url": f"{base_url}/applicant/{quote('テック 株式会社')}",
            "description": "すべての文字をURLエンコード"
        }
    ]
    
    for case in test_cases:
        print(f"\n--- テストケース: {case['name']} ---")
        print(f"説明: {case['description']}")
        
        url = case["url"]
        print(f"URL: {url}")
        
        try:
            if case.get("quoted"):
                print("Note: This URL should be passed with quotes in curl")
                # For Python requests, we don't need special handling for quoted URLs
            
            response = requests.get(url)
            print(f"ステータスコード: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 成功しました！")
                data = response.json()
                # Print simplified response to verify contents
                if "applicant_name" in data:
                    print(f"出願人名: {data['applicant_name']}")
                elif "success" in data and data.get("success") and "applicant_name" in data:
                    print(f"出願人名: {data['applicant_name']}")
            else:
                print(f"❌ エラー: {response.text}")
        except Exception as e:
            print(f"❌ テスト失敗: {str(e)}")
    
    print("\n✅ テスト完了")

if __name__ == "__main__":
    print(f"サーバーURL: {base_url}")
    
    try:
        # First check if server is up
        response = requests.get(f"{base_url}/")
        print(f"サーバー接続: ステータスコード {response.status_code}")
        
        # Run tests
        test_japanese_with_spaces()
    except requests.exceptions.ConnectionError:
        print(f"エラー: サーバー {base_url} に接続できません。サーバーが起動していることを確認してください。")
    except Exception as e:
        print(f"エラー: {str(e)}")
