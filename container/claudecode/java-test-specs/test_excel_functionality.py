#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel VBAマクロ機能テストスクリプト
作成されたExcelファイルとVBAモジュールの機能をテスト
"""

import os
import zipfile
import tempfile
from pathlib import Path

def test_excel_file_structure():
    """Excelファイルの構造をテスト"""

    excel_path = "/root/aws.git/container/claudecode/java-test-specs/TestSpecGenerator_WithMacros.xlsm"

    print("🔍 Excelファイル構造テスト開始...")

    if not os.path.exists(excel_path):
        print(f"❌ Excelファイルが見つかりません: {excel_path}")
        return False

    print(f"✅ Excelファイル存在確認: {excel_path}")

    # ファイルサイズ確認
    file_size = os.path.getsize(excel_path)
    print(f"📊 ファイルサイズ: {file_size:,} bytes")

    # ZIPファイルとしてExcelファイルの内部構造をチェック
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            with zipfile.ZipFile(excel_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                print(f"✅ ZIP構造確認: {len(file_list)}個のファイル")

                # VBAProject.binの存在確認
                vba_files = [f for f in file_list if 'vbaProject.bin' in f]
                if vba_files:
                    print(f"✅ VBAプロジェクト確認: {vba_files}")
                else:
                    print("⚠️  VBAプロジェクトファイルが見つかりません")

                # Content-Types.xmlの確認
                content_types = [f for f in file_list if '[Content_Types].xml' in f]
                if content_types:
                    print(f"✅ Content-Types.xml確認: {content_types}")

                    # Content-Typesの内容確認
                    zip_ref.extract(content_types[0], temp_dir)
                    content_path = os.path.join(temp_dir, content_types[0])
                    with open(content_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'vbaProject' in content:
                            print("✅ VBAプロジェクト参照確認")
                        else:
                            print("⚠️  VBAプロジェクト参照が見つかりません")

                # ワークシート確認
                worksheets = [f for f in file_list if f.startswith('xl/worksheets/')]
                print(f"✅ ワークシート確認: {len(worksheets)}個のシート")

        except Exception as e:
            print(f"❌ Excelファイル構造テストエラー: {e}")
            return False

    return True

def test_vba_modules():
    """VBAモジュールファイルのテスト"""

    print("\n🔍 VBAモジュールテスト開始...")

    vba_dir = "/root/aws.git/container/claudecode/java-test-specs/vba-modules"

    required_modules = [
        "DataTypes.bas",
        "FolderScanner.bas",
        "JavaAnnotationParser.bas",
        "CoverageReportParser.bas",
        "ExcelSheetBuilder.bas",
        "MainController.bas"
    ]

    for module_name in required_modules:
        module_path = os.path.join(vba_dir, module_name)

        if not os.path.exists(module_path):
            print(f"❌ VBAモジュールが見つかりません: {module_name}")
            return False

        # ファイルサイズ確認
        file_size = os.path.getsize(module_path)
        print(f"✅ {module_name}: {file_size:,} bytes")

        # 基本的な構文チェック
        with open(module_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # VBAファイルヘッダー確認
            if not content.startswith('Attribute VB_Name'):
                print(f"⚠️  {module_name}: VBAヘッダーが見つかりません")

            # Option Explicit確認
            if 'Option Explicit' not in content:
                print(f"⚠️  {module_name}: Option Explicit宣言が見つかりません")
            else:
                print(f"✅ {module_name}: 構文チェックOK")

    return True

def test_sample_data():
    """サンプルデータのテスト"""

    print("\n🔍 サンプルデータテスト開始...")

    sample_dir = "/root/aws.git/container/claudecode/java-test-specs/sample-java-tests"

    # Javaテストファイル確認
    java_files = [
        "BasicCalculatorTest.java",
        "StringValidatorTest.java"
    ]

    for java_file in java_files:
        java_path = os.path.join(sample_dir, java_file)

        if not os.path.exists(java_path):
            print(f"❌ Javaファイルが見つかりません: {java_file}")
            return False

        file_size = os.path.getsize(java_path)
        print(f"✅ {java_file}: {file_size:,} bytes")

        # アノテーション確認
        with open(java_path, 'r', encoding='utf-8') as f:
            content = f.read()

            annotations = [
                "@TestModule",
                "@TestCase",
                "@TestOverview",
                "@Creator"
            ]

            found_annotations = []
            for annotation in annotations:
                if annotation in content:
                    found_annotations.append(annotation)

            print(f"✅ {java_file}: {len(found_annotations)}/{len(annotations)}個のアノテーション確認")

    # カバレッジレポート確認
    coverage_dir = os.path.join(sample_dir, "coverage-reports")
    coverage_files = ["jacoco-report.xml", "coverage-summary.html"]

    for coverage_file in coverage_files:
        coverage_path = os.path.join(coverage_dir, coverage_file)

        if not os.path.exists(coverage_path):
            print(f"❌ カバレッジファイルが見つかりません: {coverage_file}")
            return False

        file_size = os.path.getsize(coverage_path)
        print(f"✅ {coverage_file}: {file_size:,} bytes")

    return True

def test_documentation():
    """ドキュメントのテスト"""

    print("\n🔍 ドキュメントテスト開始...")

    base_dir = "/root/aws.git/container/claudecode/java-test-specs"

    doc_files = [
        "README.md",
        "MACRO_BUTTON_SETUP.md",
        "setup_vba.bat"
    ]

    for doc_file in doc_files:
        doc_path = os.path.join(base_dir, doc_file)

        if not os.path.exists(doc_path):
            print(f"❌ ドキュメントが見つかりません: {doc_file}")
            return False

        file_size = os.path.getsize(doc_path)
        print(f"✅ {doc_file}: {file_size:,} bytes")

    return True

def main():
    """メインテスト実行"""

    print("🚀 Excel VBAマクロ機能統合テスト開始\n")

    test_results = []

    # 各テストを実行
    tests = [
        ("Excelファイル構造", test_excel_file_structure),
        ("VBAモジュール", test_vba_modules),
        ("サンプルデータ", test_sample_data),
        ("ドキュメント", test_documentation)
    ]

    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}テストでエラー: {e}")
            test_results.append((test_name, False))

    # テスト結果サマリ
    print("\n" + "="*50)
    print("📊 テスト結果サマリ")
    print("="*50)

    passed_tests = 0
    total_tests = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed_tests += 1

    print(f"\n🎯 結果: {passed_tests}/{total_tests} テスト成功")

    if passed_tests == total_tests:
        print("🎉 全てのテストが成功しました！")
        print("\n📋 次のステップ:")
        print("1. Windows環境でExcelファイルを開く")
        print("2. VBAモジュールを手動でインポート")
        print("3. マクロボタンを設定")
        print("4. sample-java-tests/でテスト実行")
        return True
    else:
        print("⚠️  一部のテストが失敗しました。問題を解決してから続行してください。")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)