#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py - Java Test Specification Generator Python版メインエントリーポイント

VBAのMainController.basから移植されたメイン制御機能
コマンドライン引数による実行とVBAと同等の完全なワークフローを提供:

1. 設定とユーザー入力処理
2. Javaファイルスキャン
3. アノテーション解析
4. カバレッジレポート処理
5. Excelレポート生成
6. エラーハンドリングとログ出力

Usage:
    python main.py --source-dir /path/to/java/tests --output /path/to/report.xlsx
    python main.py --interactive  # 対話モード

Created: 2026-01-07 (Pythonに移植)
Version: 2.0.0
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.data_types import ConfigurationSettings, ValidationResult, ProgressInfo
from src.folder_scanner import FolderScanner
from src.java_annotation_parser import JavaAnnotationParser
from src.coverage_report_parser import CoverageReportParser
from src.excel_sheet_builder import ExcelSheetBuilder

class JavaTestSpecificationGenerator:
    """Java Test Specification Generator メインクラス"""

    APP_NAME = "Java Test Specification Generator (Python版)"
    APP_VERSION = "2.0.0"

    def __init__(self):
        """初期化"""
        self.logger = logging.getLogger(__name__)
        self.config = ConfigurationSettings()

        # 処理統計
        self.processing_start_time = None
        self.processing_end_time = None
        self.total_errors = 0
        self.total_warnings = 0

        # コンポーネント初期化
        self.folder_scanner = FolderScanner(self.config)
        self.annotation_parser = JavaAnnotationParser()
        self.coverage_parser = CoverageReportParser()
        self.excel_builder = ExcelSheetBuilder(self.config)

    def generate_test_specification(self, source_directory: str, output_file: str,
                                  include_coverage: bool = True, interactive: bool = False) -> bool:
        """
        テスト仕様書生成のメインワークフロー

        Args:
            source_directory: ソースディレクトリパス
            output_file: 出力Excelファイルパス
            include_coverage: カバレッジレポート処理を含めるかどうか
            interactive: 対話モードかどうか

        Returns:
            bool: 処理成功の場合True
        """
        try:
            self.processing_start_time = datetime.now()

            self.logger.info(f"📊 {self.APP_NAME} 開始")
            self.logger.info(f"   バージョン: {self.APP_VERSION}")
            self.logger.info(f"   ソース: {source_directory}")
            self.logger.info(f"   出力: {output_file}")

            # 設定更新
            self.config.source_directory = source_directory
            self.config.output_file_path = output_file
            self.config.process_coverage_reports = include_coverage

            # 入力検証
            if not self._validate_inputs():
                return False

            if interactive:
                self._show_interactive_confirmation()

            # Step 1: Javaファイルスキャン
            self.logger.info("🔍 Step 1: Javaファイルスキャン開始...")
            java_files = self.folder_scanner.scan_for_java_files(
                source_directory, self.config.include_subdirectories
            )

            if not java_files:
                self.logger.error("❌ Javaファイルが見つかりません")
                return False

            self.logger.info(f"✅ Javaファイル発見: {len(java_files)}個")

            # Step 2: アノテーション解析
            self.logger.info("📝 Step 2: アノテーション解析開始...")
            test_cases = self.annotation_parser.process_java_files(java_files)

            if not test_cases:
                self.logger.error("❌ テストケースが見つかりません")
                return False

            self.logger.info(f"✅ テストケース抽出: {len(test_cases)}個")

            # Step 3: カバレッジレポート処理
            coverage_data = []
            if include_coverage:
                self.logger.info("📈 Step 3: カバレッジレポート処理開始...")
                coverage_files = self.folder_scanner.scan_for_coverage_reports(
                    source_directory, self.config.include_subdirectories
                )

                if coverage_files:
                    coverage_data = self.coverage_parser.process_coverage_reports(coverage_files)
                    self.logger.info(f"✅ カバレッジデータ取得: {len(coverage_data)}個")

                    # カバレッジ情報をテストケースにマージ
                    self.coverage_parser.merge_coverage_with_test_cases(test_cases, coverage_data)
                else:
                    self.logger.warning("⚠️ カバレッジレポートが見つかりません")

            # Step 4: Excelレポート生成
            self.logger.info("📊 Step 4: Excelレポート生成開始...")
            success = self.excel_builder.generate_test_specification_report(
                output_file, test_cases, coverage_data
            )

            if not success:
                self.logger.error("❌ Excelレポート生成失敗")
                return False

            # 処理完了
            self.processing_end_time = datetime.now()
            self._show_completion_summary(len(java_files), len(test_cases), len(coverage_data), output_file)

            return True

        except Exception as e:
            self.logger.error(f"❌ 処理中にエラーが発生: {str(e)}")
            return False

    def _validate_inputs(self) -> bool:
        """入力パラメータの検証"""
        # ソースディレクトリ検証
        if not self.folder_scanner.directory_exists(self.config.source_directory):
            self.logger.error(f"❌ ソースディレクトリが存在しません: {self.config.source_directory}")
            return False

        # 出力ディレクトリ検証
        output_dir = Path(self.config.output_file_path).parent
        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"📁 出力ディレクトリ作成: {output_dir}")
            except Exception as e:
                self.logger.error(f"❌ 出力ディレクトリ作成失敗: {str(e)}")
                return False

        return True

    def _show_interactive_confirmation(self):
        """対話モードでの設定確認"""
        print("\n" + "="*60)
        print(f"🚀 {self.APP_NAME}")
        print("="*60)
        print(f"ソースディレクトリ: {self.config.source_directory}")
        print(f"出力ファイル: {self.config.output_file_path}")
        print(f"サブディレクトリ含む: {'はい' if self.config.include_subdirectories else 'いいえ'}")
        print(f"カバレッジレポート処理: {'はい' if self.config.process_coverage_reports else 'いいえ'}")
        print("="*60)

        response = input("処理を続行しますか? [Y/n]: ").strip().lower()
        if response in ['n', 'no', 'いいえ']:
            print("❌ 処理がキャンセルされました")
            sys.exit(0)

        print("✅ 処理を開始します...\n")

    def _show_completion_summary(self, java_files: int, test_cases: int, coverage_entries: int, output_file: str):
        """処理完了サマリーの表示"""
        duration = self.processing_end_time - self.processing_start_time
        file_size = Path(output_file).stat().st_size

        print("\n" + "="*60)
        print("🎉 処理完了サマリー")
        print("="*60)
        print(f"📁 Javaファイル処理: {java_files}個")
        print(f"🧪 テストケース抽出: {test_cases}個")
        print(f"📈 カバレッジエントリ: {coverage_entries}個")
        print(f"⏱️ 処理時間: {duration}")
        print(f"📊 出力ファイル: {output_file}")
        print(f"📏 ファイルサイズ: {file_size:,}バイト")

        # 全体カバレッジ統計
        if coverage_entries > 0:
            overall_stats = self.coverage_parser.calculate_overall_coverage(
                self.coverage_parser.process_coverage_reports([])
            )
            if overall_stats:
                print(f"🎯 全体ブランチカバレッジ: {overall_stats.get('branch_coverage', 0):.1f}%")

        print("="*60)
        print(f"✅ テスト仕様書が正常に生成されました: {output_file}")

def setup_logging(level: str = "INFO"):
    """ログ設定のセットアップ"""
    log_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('test_spec_generator.log', encoding='utf-8')
        ]
    )

def parse_arguments():
    """コマンドライン引数の解析"""
    parser = argparse.ArgumentParser(
        description='Java Test Specification Generator (Python版)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python main.py --source-dir /path/to/java/tests --output report.xlsx
  python main.py --source-dir ./sample-java-tests --output result.xlsx --no-coverage
  python main.py --interactive
        """
    )

    parser.add_argument(
        '--source-dir', '-s',
        type=str,
        help='Javaテストファイルのソースディレクトリ'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        help='出力Excelファイルのパス'
    )

    parser.add_argument(
        '--no-coverage',
        action='store_true',
        help='カバレッジレポート処理をスキップ'
    )

    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='対話モードで実行'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='ログレベル (デフォルト: INFO)'
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'Java Test Specification Generator {JavaTestSpecificationGenerator.APP_VERSION}'
    )

    return parser.parse_args()

def interactive_mode():
    """対話モードの実行"""
    print(f"\n🚀 {JavaTestSpecificationGenerator.APP_NAME}")
    print(f"バージョン: {JavaTestSpecificationGenerator.APP_VERSION}")
    print("\n対話モードで設定を入力してください:")

    # ソースディレクトリ入力
    while True:
        source_dir = input("ソースディレクトリのパス: ").strip()
        if source_dir and Path(source_dir).exists():
            break
        print("❌ ディレクトリが見つかりません。正しいパスを入力してください。")

    # 出力ファイル入力
    while True:
        output_file = input("出力Excelファイルのパス: ").strip()
        if output_file:
            if not output_file.endswith('.xlsx'):
                output_file += '.xlsx'
            break
        print("❌ ファイルパスを入力してください。")

    # カバレッジ処理確認
    coverage_input = input("カバレッジレポートを処理しますか? [Y/n]: ").strip().lower()
    include_coverage = coverage_input not in ['n', 'no', 'いいえ']

    return source_dir, output_file, include_coverage

def main():
    """メイン関数"""
    args = parse_arguments()

    # ログ設定
    setup_logging(args.log_level)

    try:
        generator = JavaTestSpecificationGenerator()

        if args.interactive:
            # 対話モード
            source_dir, output_file, include_coverage = interactive_mode()
        else:
            # コマンドライン引数モード
            if not args.source_dir or not args.output:
                print("❌ エラー: --source-dir と --output の両方を指定してください")
                print("または --interactive オプションを使用してください")
                sys.exit(1)

            source_dir = args.source_dir
            output_file = args.output
            include_coverage = not args.no_coverage

        # テスト仕様書生成実行
        success = generator.generate_test_specification(
            source_dir, output_file, include_coverage, args.interactive
        )

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n❌ 処理が中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 予期しないエラーが発生: {str(e)}")
        logging.error(f"予期しないエラー: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()