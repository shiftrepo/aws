#!/usr/bin/env python3
"""
Python最新版インストール確認テストスクリプト
作成日: 2025-10-05
"""

import sys
import platform
import subprocess
from datetime import datetime

def main():
    print("🐍 Python最新版インストール確認テスト")
    print("=" * 50)

    # Pythonバージョン情報
    print(f"📊 Python バージョン: {sys.version}")
    print(f"🏗️  Python 実装: {platform.python_implementation()}")
    print(f"🔢 Python バージョン番号: {platform.python_version()}")
    print(f"💻 システム情報: {platform.system()} {platform.release()}")
    print(f"🏛️  アーキテクチャ: {platform.architecture()[0]}")
    print()

    # パス情報
    print(f"📁 Python 実行ファイル: {sys.executable}")
    print(f"📚 Python ライブラリパス: {sys.path[0]}")
    print()

    # 基本機能テスト
    print("🧪 基本機能テスト:")

    # 1. 基本的な計算
    result = 2 ** 100
    print(f"✅ 大きな数値計算: 2^100 = {result}")

    # 2. リスト内包表記
    squares = [x**2 for x in range(10)]
    print(f"✅ リスト内包表記: {squares[:5]}...")

    # 3. f-string (Python 3.6+)
    name = "Python 3.13.7"
    print(f"✅ f-string: Hello, {name}!")

    # 4. 辞書操作
    data = {"version": "3.13.7", "year": 2025}
    print(f"✅ 辞書操作: {data}")

    # 5. エラーハンドリング
    try:
        result = 10 / 2
        print(f"✅ 例外処理: 10/2 = {result}")
    except Exception as e:
        print(f"❌ エラー: {e}")

    print()

    # モジュールインポートテスト
    print("📦 重要なモジュールテスト:")

    modules_to_test = [
        "os", "sys", "datetime", "json", "re",
        "urllib", "http", "pathlib", "collections",
        "itertools", "functools", "math", "random"
    ]

    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name}: OK")
        except ImportError as e:
            print(f"❌ {module_name}: FAILED - {e}")

    print()

    # pip動作確認
    print("📦 pip動作確認:")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ pip: {result.stdout.strip()}")
        else:
            print(f"❌ pip エラー: {result.stderr}")
    except Exception as e:
        print(f"❌ pip テスト失敗: {e}")

    print()
    print("🎉 Python最新版インストール確認完了！")
    print(f"⏰ テスト実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()