#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
coverage_report_parser.py - Python版カバレッジレポート解析

VBAのCoverageReportParser.basから移植されたJaCoCoカバレッジレポート解析機能
以下の機能を提供:
1. JaCoCoXMLレポートの解析
2. JaCoCoHTMLレポート（基本）の解析
3. ブランチカバレッジ（C1カバレッジ）情報の抽出
4. 命令、ライン、複雑度カバレッジメトリクスの抽出
5. メソッドレベル詳細カバレッジ情報の取得

Created: 2026-01-07 (Pythonに移植)
Version: 2.0.0
"""

import xml.etree.ElementTree as ET
import re
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup

from .data_types import (
    CoverageInfo, FileInfo, ErrorInfo, ErrorSeverity,
    ReportFormat, CoverageParsingError
)

class CoverageReportParser:
    """JaCoCoカバレッジレポート解析クラス"""

    def __init__(self):
        """初期化"""
        self.logger = logging.getLogger(__name__)

        # JaCoCo XML要素名
        self.JACOCO_ELEMENTS = {
            'report': 'report',
            'package': 'package',
            'class': 'class',
            'method': 'method',
            'counter': 'counter'
        }

        # カウンタータイプ
        self.COUNTER_TYPES = {
            'INSTRUCTION': 'instruction',
            'BRANCH': 'branch',
            'LINE': 'line',
            'COMPLEXITY': 'complexity',
            'METHOD': 'method',
            'CLASS': 'class'
        }

        # 統計情報
        self.reports_processed = 0
        self.coverage_entries_extracted = 0
        self.errors = []

    def process_coverage_reports(self, coverage_files: List[FileInfo]) -> List[CoverageInfo]:
        """
        カバレッジレポートファイルリストを処理

        Args:
            coverage_files: 処理するカバレッジレポートファイルのリスト

        Returns:
            List[CoverageInfo]: 抽出されたカバレッジ情報のリスト
        """
        all_coverage_data = []

        try:
            self.logger.info(f"カバレッジレポート処理開始: {len(coverage_files)}個のファイル")

            for i, file_info in enumerate(coverage_files):
                try:
                    self.logger.debug(f"処理中: {file_info.file_name} ({i+1}/{len(coverage_files)})")

                    # ファイル拡張子で処理方法を決定
                    if file_info.file_path.lower().endswith('.xml'):
                        coverage_data = self._parse_jacoco_xml_report(file_info)
                    elif file_info.file_path.lower().endswith('.html'):
                        coverage_data = self._parse_jacoco_html_report(file_info)
                    else:
                        self.logger.warning(f"サポートされていないレポート形式: {file_info.file_path}")
                        continue

                    all_coverage_data.extend(coverage_data)
                    self.reports_processed += 1

                except Exception as e:
                    error_msg = f"カバレッジレポート処理エラー: {file_info.file_path} - {str(e)}"
                    self.logger.error(error_msg)
                    self.errors.append(ErrorInfo(
                        error_description=error_msg,
                        error_source="process_coverage_reports",
                        error_severity=ErrorSeverity.ERROR.value
                    ))

            self.logger.info(f"カバレッジレポート処理完了: {len(all_coverage_data)}個のエントリ抽出")

        except Exception as e:
            error_msg = f"カバレッジレポート処理中にエラー: {str(e)}"
            self.logger.error(error_msg)
            raise CoverageParsingError(error_msg)

        return all_coverage_data

    def _parse_jacoco_xml_report(self, file_info: FileInfo) -> List[CoverageInfo]:
        """
        JaCoCoXMLレポートを解析

        Args:
            file_info: XMLレポートファイル情報

        Returns:
            List[CoverageInfo]: 抽出されたカバレッジ情報のリスト
        """
        coverage_data = []

        try:
            # XMLファイル読み込み
            tree = ET.parse(file_info.file_path)
            root = tree.getroot()

            if root.tag != 'report':
                self.logger.warning(f"JaCoCoレポートではありません: {file_info.file_path}")
                return coverage_data

            # パッケージ要素を処理
            for package in root.findall('package'):
                package_name = package.get('name', '')

                # クラス要素を処理
                for class_elem in package.findall('class'):
                    class_name = class_elem.get('name', '')
                    source_file = class_elem.get('sourcefilename', '')

                    # クラスレベルカバレッジ
                    class_coverage = self._extract_coverage_from_element(
                        class_elem, package_name, class_name, source_file, '', file_info
                    )
                    if class_coverage:
                        coverage_data.append(class_coverage)

                    # メソッドレベルカバレッジ
                    for method in class_elem.findall('method'):
                        method_name = method.get('name', '')
                        method_line = int(method.get('line', 0))

                        method_coverage = self._extract_coverage_from_element(
                            method, package_name, class_name, source_file, method_name, file_info
                        )
                        if method_coverage:
                            method_coverage.line_number = method_line
                            coverage_data.append(method_coverage)

        except ET.ParseError as e:
            error_msg = f"XML解析エラー: {file_info.file_path} - {str(e)}"
            self.logger.error(error_msg)
            self.errors.append(ErrorInfo(
                error_description=error_msg,
                error_source="_parse_jacoco_xml_report",
                error_severity=ErrorSeverity.ERROR.value
            ))

        except Exception as e:
            error_msg = f"JaCoCoXML解析エラー: {file_info.file_path} - {str(e)}"
            self.logger.error(error_msg)
            self.errors.append(ErrorInfo(
                error_description=error_msg,
                error_source="_parse_jacoco_xml_report",
                error_severity=ErrorSeverity.ERROR.value
            ))

        return coverage_data

    def _extract_coverage_from_element(self, element: ET.Element, package_name: str,
                                     class_name: str, source_file: str, method_name: str,
                                     file_info: FileInfo) -> Optional[CoverageInfo]:
        """
        XML要素からカバレッジ情報を抽出

        Args:
            element: XML要素
            package_name: パッケージ名
            class_name: クラス名
            source_file: ソースファイル名
            method_name: メソッド名
            file_info: レポートファイル情報

        Returns:
            Optional[CoverageInfo]: 抽出されたカバレッジ情報
        """
        try:
            coverage = CoverageInfo()

            # 基本情報設定
            full_class_name = f"{package_name}.{class_name}" if package_name else class_name
            coverage.class_name = full_class_name.replace('/', '.')
            coverage.method_name = method_name
            coverage.source_file = source_file
            coverage.report_file = file_info.file_path
            coverage.report_type = ReportFormat.XML.value

            # カウンター情報を解析
            counters = {}
            for counter in element.findall('counter'):
                counter_type = counter.get('type', '')
                covered = int(counter.get('covered', 0))
                missed = int(counter.get('missed', 0))

                counters[counter_type] = {
                    'covered': covered,
                    'missed': missed,
                    'total': covered + missed
                }

            # 各カバレッジメトリクスを設定
            self._set_coverage_metrics(coverage, counters)

            coverage.is_valid = True
            self.coverage_entries_extracted += 1

            return coverage

        except Exception as e:
            self.logger.error(f"カバレッジ情報抽出エラー: {str(e)}")
            return None

    def _set_coverage_metrics(self, coverage: CoverageInfo, counters: Dict[str, Dict[str, int]]):
        """
        カウンター情報からカバレッジメトリクスを設定

        Args:
            coverage: 設定対象のCoverageInfo
            counters: カウンター情報辞書
        """
        # 命令カバレッジ
        if 'INSTRUCTION' in counters:
            inst = counters['INSTRUCTION']
            coverage.instructions_covered = inst['covered']
            coverage.instructions_missed = inst['missed']
            coverage.instructions_total = inst['total']

        # ブランチカバレッジ（C1カバレッジ）
        if 'BRANCH' in counters:
            branch = counters['BRANCH']
            coverage.branches_covered = branch['covered']
            coverage.branches_missed = branch['missed']
            coverage.branches_total = branch['total']

            if branch['total'] > 0:
                coverage.branch_coverage = (branch['covered'] / branch['total']) * 100.0

        # ラインカバレッジ
        if 'LINE' in counters:
            line = counters['LINE']
            coverage.lines_covered = line['covered']
            coverage.lines_missed = line['missed']
            coverage.lines_total = line['total']

        # 複雑度カバレッジ
        if 'COMPLEXITY' in counters:
            complexity = counters['COMPLEXITY']
            coverage.complexity_covered = complexity['covered']
            coverage.complexity_missed = complexity['missed']
            coverage.complexity_total = complexity['total']

    def _parse_jacoco_html_report(self, file_info: FileInfo) -> List[CoverageInfo]:
        """
        JaCoCoHTMLレポートを解析（基本機能）

        Args:
            file_info: HTMLレポートファイル情報

        Returns:
            List[CoverageInfo]: 抽出されたカバレッジ情報のリスト
        """
        coverage_data = []

        try:
            # HTMLファイル読み込み
            with open(file_info.file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, 'html.parser')

            # JaCoCoレポートの特徴的なテーブルを検索
            coverage_table = soup.find('table', {'id': 'coveragetable'})
            if not coverage_table:
                # 別のテーブル構造を試行
                coverage_table = soup.find('table')

            if coverage_table:
                # テーブル行を解析してカバレッジ情報を抽出
                rows = coverage_table.find_all('tr')

                for row in rows[1:]:  # ヘッダー行をスキップ
                    cells = row.find_all('td')
                    if len(cells) >= 6:  # 十分な列数があることを確認
                        coverage = self._parse_html_table_row(cells, file_info)
                        if coverage:
                            coverage_data.append(coverage)

        except Exception as e:
            error_msg = f"JaCoCoHTML解析エラー: {file_info.file_path} - {str(e)}"
            self.logger.error(error_msg)
            self.errors.append(ErrorInfo(
                error_description=error_msg,
                error_source="_parse_jacoco_html_report",
                error_severity=ErrorSeverity.ERROR.value
            ))

        return coverage_data

    def _parse_html_table_row(self, cells, file_info: FileInfo) -> Optional[CoverageInfo]:
        """
        HTMLテーブル行からカバレッジ情報を解析

        Args:
            cells: テーブルセルのリスト
            file_info: レポートファイル情報

        Returns:
            Optional[CoverageInfo]: 解析されたカバレッジ情報
        """
        try:
            coverage = CoverageInfo()

            # クラス名/メソッド名を抽出（最初の列）
            name_cell = cells[0].get_text().strip()
            if name_cell:
                coverage.class_name = name_cell

            # カバレッジパーセンテージを抽出（通常は最後の方の列）
            for i, cell in enumerate(cells):
                cell_text = cell.get_text().strip()

                # パーセンテージパターンを検索
                percent_match = re.search(r'(\d+(?:\.\d+)?)%', cell_text)
                if percent_match:
                    coverage.branch_coverage = float(percent_match.group(1))
                    break

                # 分数パターンを検索（例: "140/148"）
                fraction_match = re.search(r'(\d+)/(\d+)', cell_text)
                if fraction_match:
                    covered = int(fraction_match.group(1))
                    total = int(fraction_match.group(2))

                    if i == 1:  # 命令カバレッジと仮定
                        coverage.instructions_covered = covered
                        coverage.instructions_total = total
                        coverage.instructions_missed = total - covered
                    elif i == 2:  # ブランチカバレッジと仮定
                        coverage.branches_covered = covered
                        coverage.branches_total = total
                        coverage.branches_missed = total - covered

                        if total > 0:
                            coverage.branch_coverage = (covered / total) * 100.0

            coverage.report_file = file_info.file_path
            coverage.report_type = ReportFormat.HTML.value
            coverage.is_valid = True

            return coverage

        except Exception as e:
            self.logger.error(f"HTMLテーブル行解析エラー: {str(e)}")
            return None

    def merge_coverage_with_test_cases(self, test_cases: List, coverage_data: List[CoverageInfo]):
        """
        テストケース情報とカバレッジ情報をマージ

        Args:
            test_cases: テストケース情報のリスト
            coverage_data: カバレッジ情報のリスト
        """
        try:
            # クラス名とメソッド名でマッピング辞書を作成
            coverage_map = {}
            for coverage in coverage_data:
                # クラス名の正規化
                normalized_class = coverage.class_name.split('.')[-1]  # パッケージ名を除去

                if coverage.method_name:
                    # メソッドレベルカバレッジ
                    key = f"{normalized_class}.{coverage.method_name}"
                else:
                    # クラスレベルカバレッジ
                    key = normalized_class

                coverage_map[key] = coverage

            # テストケースにカバレッジ情報を適用
            for test_case in test_cases:
                # メソッドレベルマッチングを試行
                method_key = f"{test_case.class_name}.{test_case.method_name}"
                if method_key in coverage_map:
                    coverage = coverage_map[method_key]
                else:
                    # クラスレベルマッチングを試行
                    class_key = test_case.class_name
                    coverage = coverage_map.get(class_key)

                if coverage:
                    # カバレッジ情報をテストケースに設定
                    test_case.coverage_percent = coverage.branch_coverage
                    test_case.branches_covered = coverage.branches_covered
                    test_case.branches_total = coverage.branches_total
                    test_case.instructions_covered = coverage.instructions_covered
                    test_case.instructions_total = coverage.instructions_total

                    self.logger.debug(f"カバレッジマージ: {test_case.class_name}.{test_case.method_name} -> {coverage.branch_coverage}%")

        except Exception as e:
            error_msg = f"カバレッジマージエラー: {str(e)}"
            self.logger.error(error_msg)
            self.errors.append(ErrorInfo(
                error_description=error_msg,
                error_source="merge_coverage_with_test_cases",
                error_severity=ErrorSeverity.ERROR.value
            ))

    def calculate_overall_coverage(self, coverage_data: List[CoverageInfo]) -> Dict[str, float]:
        """
        全体カバレッジ統計を計算

        Args:
            coverage_data: カバレッジ情報のリスト

        Returns:
            Dict[str, float]: 全体カバレッジ統計
        """
        try:
            total_branches = 0
            covered_branches = 0
            total_instructions = 0
            covered_instructions = 0
            total_lines = 0
            covered_lines = 0

            for coverage in coverage_data:
                total_branches += coverage.branches_total
                covered_branches += coverage.branches_covered
                total_instructions += coverage.instructions_total
                covered_instructions += coverage.instructions_covered
                total_lines += coverage.lines_total
                covered_lines += coverage.lines_covered

            stats = {
                'branch_coverage': (covered_branches / total_branches * 100.0) if total_branches > 0 else 0.0,
                'instruction_coverage': (covered_instructions / total_instructions * 100.0) if total_instructions > 0 else 0.0,
                'line_coverage': (covered_lines / total_lines * 100.0) if total_lines > 0 else 0.0,
                'total_branches': total_branches,
                'covered_branches': covered_branches,
                'total_instructions': total_instructions,
                'covered_instructions': covered_instructions
            }

            return stats

        except Exception as e:
            self.logger.error(f"全体カバレッジ計算エラー: {str(e)}")
            return {}

    def get_processing_stats(self) -> Dict[str, int]:
        """
        処理統計情報を取得

        Returns:
            Dict[str, int]: 統計情報
        """
        return {
            'reports_processed': self.reports_processed,
            'coverage_entries_extracted': self.coverage_entries_extracted,
            'error_count': len(self.errors)
        }

    def reset_statistics(self):
        """統計情報をリセット"""
        self.reports_processed = 0
        self.coverage_entries_extracted = 0
        self.errors.clear()

# テスト関数

def test_coverage_report_parser():
    """CoverageReportParserのテスト"""
    print("🔍 CoverageReportParserテスト開始...")

    parser = CoverageReportParser()

    # サンプルカバレッジレポートでテスト
    test_xml = "/root/aws.git/container/claudecode/java-test-specs/sample-java-tests/coverage-reports/jacoco-report.xml"

    if Path(test_xml).exists():
        file_info = FileInfo()
        file_info.file_path = test_xml
        file_info.file_name = "jacoco-report.xml"

        coverage_data = parser._parse_jacoco_xml_report(file_info)

        print(f"✅ カバレッジデータ抽出: {len(coverage_data)}個")
        for coverage in coverage_data[:5]:  # 最初の5個を表示
            print(f"   - {coverage.class_name}")
            if coverage.method_name:
                print(f"     メソッド: {coverage.method_name}")
            print(f"     ブランチカバレッジ: {coverage.branch_coverage:.1f}% ({coverage.branches_covered}/{coverage.branches_total})")
            print()

        # 全体統計計算
        overall_stats = parser.calculate_overall_coverage(coverage_data)
        print(f"✅ 全体統計:")
        print(f"   ブランチカバレッジ: {overall_stats.get('branch_coverage', 0):.1f}%")
        print(f"   総ブランチ: {overall_stats.get('covered_branches', 0)}/{overall_stats.get('total_branches', 0)}")

        stats = parser.get_processing_stats()
        print(f"✅ 処理統計: レポート{stats['reports_processed']}個, エントリ{stats['coverage_entries_extracted']}個")

    else:
        print(f"❌ テストファイルが見つかりません: {test_xml}")

    print("🎉 CoverageReportParserテスト完了!")

if __name__ == "__main__":
    # ログ設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    test_coverage_report_parser()