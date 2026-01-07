#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
java_annotation_parser.py - Python版Javaアノテーション解析

VBAのJavaAnnotationParser.basから移植されたJavaアノテーション解析機能
以下の機能を提供:
1. Javaファイルの読み込みとエンコーディング処理
2. JavaDocコメントブロックの抽出
3. カスタムアノテーション解析（@TestModule, @TestCase等）
4. クラスレベルとメソッドレベルのアノテーション統合

Created: 2026-01-07 (Pythonに移植)
Version: 2.0.0
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime

from .data_types import (
    TestCaseInfo, FileInfo, AnnotationResult, ValidationResult,
    ErrorInfo, ErrorSeverity, AnnotationParsingError
)

class JavaAnnotationParser:
    """Javaアノテーション解析クラス"""

    def __init__(self):
        """初期化"""
        self.logger = logging.getLogger(__name__)

        # アノテーション処理の定数
        self.MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        self.JAVADOC_START = r'/\*\*'
        self.JAVADOC_END = r'\*/'
        self.ANNOTATION_PREFIX = '@'

        # サポートされるアノテーション
        self.supported_annotations = {
            'TestModule', 'TestCase', 'BaselineVersion', 'TestOverview',
            'TestPurpose', 'TestProcess', 'TestResults', 'Creator',
            'CreatedDate', 'Modifier', 'ModifiedDate', 'TestCategory',
            'Priority', 'Requirements', 'Dependencies'
        }

        # 正規表現パターン
        self._compile_regex_patterns()

        # 統計情報
        self.files_processed = 0
        self.test_methods_found = 0
        self.annotations_extracted = 0
        self.errors = []

    def _compile_regex_patterns(self):
        """正規表現パターンをコンパイル"""
        # JavaDocブロック抽出パターン
        self.javadoc_pattern = re.compile(
            r'/\*\*.*?\*/',
            re.DOTALL | re.MULTILINE
        )

        # テストメソッドパターン（複数行対応、メソッド宣言のみ）
        self.test_method_pattern = re.compile(
            r'@(?:Test|ParameterizedTest).*?public\s+void\s+(\w+)\s*\(',
            re.DOTALL | re.MULTILINE
        )

        # クラス宣言パターン
        self.class_pattern = re.compile(
            r'(?:public\s+)?class\s+(\w+)',
            re.MULTILINE
        )

        # アノテーション抽出パターン
        self.annotation_pattern = re.compile(
            r'@(\w+)\s+([^\r\n@]*)',
            re.MULTILINE
        )

        # メソッド宣言パターン
        self.method_declaration_pattern = re.compile(
            r'(?:public|private|protected)?\s*(?:static\s+)?(?:void\s+)?(\w+)\s*\(',
            re.MULTILINE
        )

    def process_java_files(self, java_files: List[FileInfo]) -> List[TestCaseInfo]:
        """
        Javaファイルリストを処理してテストケース情報を抽出

        Args:
            java_files: 処理するJavaファイルのリスト

        Returns:
            List[TestCaseInfo]: 抽出されたテストケース情報のリスト
        """
        all_test_cases = []

        try:
            self.logger.info(f"Javaファイル処理開始: {len(java_files)}個のファイル")

            for i, file_info in enumerate(java_files):
                try:
                    self.logger.debug(f"処理中: {file_info.file_name} ({i+1}/{len(java_files)})")

                    # ファイルからテストケースを抽出
                    test_cases = self._extract_test_cases_from_file(file_info)
                    all_test_cases.extend(test_cases)

                    self.files_processed += 1

                except Exception as e:
                    error_msg = f"ファイル処理エラー: {file_info.file_path} - {str(e)}"
                    self.logger.error(error_msg)
                    self.errors.append(ErrorInfo(
                        error_description=error_msg,
                        error_source="process_java_files",
                        error_severity=ErrorSeverity.ERROR.value
                    ))

            self.logger.info(f"Javaファイル処理完了: {len(all_test_cases)}個のテストケース抽出")

        except Exception as e:
            error_msg = f"Javaファイル処理中にエラー: {str(e)}"
            self.logger.error(error_msg)
            raise AnnotationParsingError(error_msg)

        return all_test_cases

    def _extract_test_cases_from_file(self, file_info: FileInfo) -> List[TestCaseInfo]:
        """
        単一Javaファイルからテストケース情報を抽出

        Args:
            file_info: 処理するファイル情報

        Returns:
            List[TestCaseInfo]: 抽出されたテストケース情報のリスト
        """
        test_cases = []

        try:
            # ファイル読み込み
            content = self._read_java_file(file_info.file_path)
            if not content:
                return test_cases

            # クラス名抽出
            class_name = self._extract_class_name(content)
            if not class_name:
                self.logger.warning(f"クラス名が見つかりません: {file_info.file_path}")
                return test_cases

            # クラスレベルアノテーション抽出
            class_annotations = self._extract_class_annotations(content)

            # テストメソッド検索と処理
            test_methods = self._find_test_methods(content)

            for method_name, method_pos in test_methods:
                # メソッド固有のアノテーション抽出
                method_annotations = self._extract_method_annotations(content, method_pos)

                # アノテーションをマージしてTestCaseInfoを作成
                test_case = self._create_test_case_info(
                    file_info, class_name, method_name,
                    class_annotations, method_annotations
                )

                test_cases.append(test_case)
                self.test_methods_found += 1

        except Exception as e:
            error_msg = f"テストケース抽出エラー: {file_info.file_path} - {str(e)}"
            self.logger.error(error_msg)
            self.errors.append(ErrorInfo(
                error_description=error_msg,
                error_source="_extract_test_cases_from_file",
                error_severity=ErrorSeverity.ERROR.value
            ))

        return test_cases

    def _read_java_file(self, file_path: str) -> Optional[str]:
        """
        Javaファイルを読み込み

        Args:
            file_path: 読み込むファイルのパス

        Returns:
            Optional[str]: ファイル内容（エラーの場合None）
        """
        try:
            path = Path(file_path)

            # ファイルサイズチェック
            if path.stat().st_size > self.MAX_FILE_SIZE:
                self.logger.warning(f"ファイルサイズ上限超過: {file_path}")
                return None

            # エンコーディングを試行（UTF-8 -> Shift_JIS -> CP932）
            for encoding in ['utf-8', 'shift_jis', 'cp932']:
                try:
                    with open(path, 'r', encoding=encoding) as f:
                        content = f.read()
                        self.logger.debug(f"ファイル読み込み成功: {file_path} ({encoding})")
                        return content
                except UnicodeDecodeError:
                    continue

            self.logger.error(f"ファイル読み込み失敗（エンコーディングエラー）: {file_path}")
            return None

        except Exception as e:
            self.logger.error(f"ファイル読み込みエラー: {file_path} - {str(e)}")
            return None

    def _extract_class_name(self, content: str) -> Optional[str]:
        """
        Javaファイルからクラス名を抽出

        Args:
            content: ファイル内容

        Returns:
            Optional[str]: クラス名（見つからない場合None）
        """
        try:
            match = self.class_pattern.search(content)
            if match:
                return match.group(1)
            return None

        except Exception as e:
            self.logger.error(f"クラス名抽出エラー: {str(e)}")
            return None

    def _extract_class_annotations(self, content: str) -> Dict[str, str]:
        """
        クラスレベルのアノテーションを抽出

        Args:
            content: ファイル内容

        Returns:
            Dict[str, str]: アノテーション名と値のマッピング
        """
        annotations = {}

        try:
            # クラス宣言より前のJavaDocブロックを検索
            class_match = self.class_pattern.search(content)
            if not class_match:
                return annotations

            class_pos = class_match.start()

            # クラス宣言の前のJavaDocブロックを検索
            javadoc_blocks = self.javadoc_pattern.findall(content[:class_pos])

            if javadoc_blocks:
                # 最後のJavaDocブロック（クラス直前のもの）を解析
                last_javadoc = javadoc_blocks[-1]
                annotations = self._parse_annotations_from_block(last_javadoc)

        except Exception as e:
            self.logger.error(f"クラスアノテーション抽出エラー: {str(e)}")

        return annotations

    def _find_test_methods(self, content: str) -> List[Tuple[str, int]]:
        """
        テストメソッドを検索

        Args:
            content: ファイル内容

        Returns:
            List[Tuple[str, int]]: (メソッド名, 位置)のリスト
        """
        test_methods = []

        try:
            for match in self.test_method_pattern.finditer(content):
                method_name = match.group(1)
                method_pos = match.start()
                test_methods.append((method_name, method_pos))
                self.logger.debug(f"テストメソッド発見: {method_name} at position {method_pos}")

        except Exception as e:
            self.logger.error(f"テストメソッド検索エラー: {str(e)}")

        return test_methods

    def _extract_method_annotations(self, content: str, method_pos: int) -> Dict[str, str]:
        """
        メソッド固有のアノテーションを抽出

        Args:
            content: ファイル内容
            method_pos: メソッドの位置

        Returns:
            Dict[str, str]: アノテーション名と値のマッピング
        """
        annotations = {}

        try:
            # メソッド宣言より前のJavaDocブロックを検索
            preceding_content = content[:method_pos]

            # 最後のJavaDocブロックを探す（メソッド直前のもの）
            javadoc_matches = list(self.javadoc_pattern.finditer(preceding_content))

            if javadoc_matches:
                # 最後のJavaDocブロックがメソッドに近い位置にある場合
                last_match = javadoc_matches[-1]
                javadoc_end = last_match.end()

                # JavaDoc終了からメソッド開始までの距離チェック（適度な範囲内）
                if method_pos - javadoc_end < 500:  # 500文字以内
                    javadoc_block = last_match.group(0)
                    annotations = self._parse_annotations_from_block(javadoc_block)

        except Exception as e:
            self.logger.error(f"メソッドアノテーション抽出エラー: {str(e)}")

        return annotations

    def _parse_annotations_from_block(self, javadoc_block: str) -> Dict[str, str]:
        """
        JavaDocブロックからアノテーションを解析

        Args:
            javadoc_block: JavaDocブロック文字列

        Returns:
            Dict[str, str]: アノテーション名と値のマッピング
        """
        annotations = {}

        try:
            # JavaDocコメント記号を除去
            cleaned_block = re.sub(r'/\*\*|\*/|\*\s*', '', javadoc_block)

            # 各行を処理してアノテーションを抽出
            for line in cleaned_block.split('\n'):
                line = line.strip()
                if line.startswith(self.ANNOTATION_PREFIX):
                    # アノテーション行を解析
                    annotation_match = self.annotation_pattern.search(line)
                    if annotation_match:
                        name = annotation_match.group(1)
                        value = annotation_match.group(2).strip()

                        # サポートされているアノテーションのみ処理
                        if name in self.supported_annotations:
                            annotations[name] = value
                            self.annotations_extracted += 1

        except Exception as e:
            self.logger.error(f"アノテーション解析エラー: {str(e)}")

        return annotations

    def _create_test_case_info(self, file_info: FileInfo, class_name: str, method_name: str,
                             class_annotations: Dict[str, str], method_annotations: Dict[str, str]) -> TestCaseInfo:
        """
        TestCaseInfoオブジェクトを作成

        Args:
            file_info: ファイル情報
            class_name: クラス名
            method_name: メソッド名
            class_annotations: クラスレベルアノテーション
            method_annotations: メソッドレベルアノテーション

        Returns:
            TestCaseInfo: 作成されたテストケース情報
        """
        test_case = TestCaseInfo()

        try:
            # ファイル情報
            test_case.file_path = file_info.file_path
            test_case.class_name = class_name
            test_case.method_name = method_name

            # アノテーションをマージ（メソッドレベルが優先）
            merged_annotations = {**class_annotations, **method_annotations}

            # 各アノテーション値を設定
            test_case.test_module = merged_annotations.get('TestModule', 'Not Specified')
            test_case.test_case = merged_annotations.get('TestCase', 'Not Specified')
            test_case.baseline_version = merged_annotations.get('BaselineVersion', 'Not Specified')
            test_case.test_overview = merged_annotations.get('TestOverview', 'Not Specified')
            test_case.test_purpose = merged_annotations.get('TestPurpose', 'Not Specified')
            test_case.test_process = merged_annotations.get('TestProcess', 'Not Specified')
            test_case.test_results = merged_annotations.get('TestResults', 'Not Specified')
            test_case.creator = merged_annotations.get('Creator', 'Unknown')
            test_case.modifier = merged_annotations.get('Modifier', '')
            test_case.test_category = merged_annotations.get('TestCategory', '')
            test_case.priority = merged_annotations.get('Priority', '')
            test_case.requirements = merged_annotations.get('Requirements', '')
            test_case.dependencies = merged_annotations.get('Dependencies', '')

            # 日付の解析
            test_case.created_date = self._parse_date(merged_annotations.get('CreatedDate', ''))
            test_case.modified_date = self._parse_date(merged_annotations.get('ModifiedDate', ''))

            # メタデータ
            test_case.processed_date = datetime.now()
            test_case.is_valid = True

        except Exception as e:
            test_case.is_valid = False
            test_case.error_message = f"TestCaseInfo作成エラー: {str(e)}"
            self.logger.error(test_case.error_message)

        return test_case

    def _parse_date(self, date_string: str) -> Optional[datetime]:
        """
        日付文字列を解析

        Args:
            date_string: 日付文字列

        Returns:
            Optional[datetime]: 解析された日付（失敗の場合None）
        """
        if not date_string:
            return None

        try:
            # 複数の日付フォーマットに対応
            date_formats = [
                '%Y-%m-%d',      # 2026-01-07
                '%Y/%m/%d',      # 2026/01/07
                '%m/%d/%Y',      # 01/07/2026
                '%d/%m/%Y',      # 07/01/2026
                '%Y年%m月%d日',   # 2026年01月07日
            ]

            for fmt in date_formats:
                try:
                    return datetime.strptime(date_string.strip(), fmt)
                except ValueError:
                    continue

            self.logger.warning(f"日付解析失敗: {date_string}")
            return None

        except Exception as e:
            self.logger.error(f"日付解析エラー: {date_string} - {str(e)}")
            return None

    def get_processing_stats(self) -> Dict[str, int]:
        """
        処理統計情報を取得

        Returns:
            Dict[str, int]: 統計情報
        """
        return {
            'files_processed': self.files_processed,
            'test_methods_found': self.test_methods_found,
            'annotations_extracted': self.annotations_extracted,
            'error_count': len(self.errors)
        }

    def reset_statistics(self):
        """統計情報をリセット"""
        self.files_processed = 0
        self.test_methods_found = 0
        self.annotations_extracted = 0
        self.errors.clear()

# テスト関数

def test_java_annotation_parser():
    """JavaAnnotationParserのテスト"""
    print("🔍 JavaAnnotationParserテスト開始...")

    parser = JavaAnnotationParser()

    # サンプルJavaファイルでテスト
    test_file = "/root/aws.git/container/claudecode/java-test-specs/sample-java-tests/BasicCalculatorTest.java"

    if Path(test_file).exists():
        file_info = FileInfo()
        file_info.file_path = test_file
        file_info.file_name = "BasicCalculatorTest.java"

        test_cases = parser._extract_test_cases_from_file(file_info)

        print(f"✅ テストケース抽出: {len(test_cases)}個")
        for test_case in test_cases:
            print(f"   - {test_case.class_name}.{test_case.method_name}")
            print(f"     モジュール: {test_case.test_module}")
            print(f"     概要: {test_case.test_overview}")
            print(f"     作成者: {test_case.creator}")
            print()

        stats = parser.get_processing_stats()
        print(f"✅ 処理統計: ファイル{stats['files_processed']}個, メソッド{stats['test_methods_found']}個, アノテーション{stats['annotations_extracted']}個")

    else:
        print(f"❌ テストファイルが見つかりません: {test_file}")

    print("🎉 JavaAnnotationParserテスト完了!")

if __name__ == "__main__":
    # ログ設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    test_java_annotation_parser()