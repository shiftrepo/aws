#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
folder_scanner.py - Python版フォルダスキャナー

VBAのFolderScanner.basから移植されたディレクトリ走査機能
以下の機能を提供:
1. Javaテストファイルの再帰的検索
2. JaCoCoカバレッジレポートの検索
3. ディレクトリとファイルの検証
4. ファイルフィルタリング

Created: 2026-01-07 (Pythonに移植)
Version: 2.0.0
"""

import os
import logging
from pathlib import Path
from typing import List, Optional, Set, Tuple
from fnmatch import fnmatch
from datetime import datetime

from .data_types import (
    FileInfo, DirectoryStats, ValidationResult, ConfigurationSettings,
    ProgressInfo, ErrorInfo, ErrorSeverity
)

class FolderScanner:
    """フォルダスキャナークラス - ディレクトリの再帰的走査機能"""

    def __init__(self, config: Optional[ConfigurationSettings] = None):
        """
        初期化

        Args:
            config: 設定情報（オプション）
        """
        self.config = config or ConfigurationSettings()
        self.logger = logging.getLogger(__name__)

        # 統計情報
        self.total_files_scanned = 0
        self.total_directories_scanned = 0
        self.errors = []

        # サポートされるファイル拡張子
        self.java_extensions = {'.java'}
        self.coverage_extensions = {'.xml', '.html'}

        # カバレッジレポートのファイル名パターン
        self.coverage_patterns = [
            'jacoco*.xml',
            '*coverage*.xml',
            'index.html',
            '*coverage*.html',
            'jacoco-report.xml',
            'coverage-summary.html'
        ]

    def scan_for_java_files(self, directory_path: str, include_subdirs: bool = True) -> List[FileInfo]:
        """
        Javaファイルを再帰的にスキャン

        Args:
            directory_path: スキャン対象ディレクトリパス
            include_subdirs: サブディレクトリを含むかどうか

        Returns:
            List[FileInfo]: 見つかったJavaファイルのリスト
        """
        java_files = []

        try:
            validation = self._validate_directory(directory_path)
            if not validation.is_valid:
                self.logger.error(f"ディレクトリ検証失敗: {validation.error_message}")
                return java_files

            directory = Path(directory_path)
            self.logger.info(f"Javaファイルスキャン開始: {directory}")

            # 再帰的または非再帰的スキャンパターンを決定
            pattern = "**/*.java" if include_subdirs else "*.java"

            for java_file in directory.glob(pattern):
                if java_file.is_file():
                    # ファイルフィルタリング適用
                    if self._should_include_java_file(java_file):
                        file_info = self._create_file_info(java_file)
                        if file_info.is_valid:
                            java_files.append(file_info)
                            self.total_files_scanned += 1

            self.logger.info(f"Javaファイルスキャン完了: {len(java_files)}個のファイルを発見")

        except Exception as e:
            error_msg = f"Javaファイルスキャン中にエラー: {str(e)}"
            self.logger.error(error_msg)
            self.errors.append(ErrorInfo(
                error_description=error_msg,
                error_source="scan_for_java_files",
                error_severity=ErrorSeverity.ERROR.value
            ))

        return java_files

    def scan_for_coverage_reports(self, directory_path: str, include_subdirs: bool = True) -> List[FileInfo]:
        """
        カバレッジレポートファイルを再帰的にスキャン

        Args:
            directory_path: スキャン対象ディレクトリパス
            include_subdirs: サブディレクトリを含むかどうか

        Returns:
            List[FileInfo]: 見つかったカバレッジレポートファイルのリスト
        """
        coverage_files = []

        try:
            validation = self._validate_directory(directory_path)
            if not validation.is_valid:
                self.logger.error(f"ディレクトリ検証失敗: {validation.error_message}")
                return coverage_files

            directory = Path(directory_path)
            self.logger.info(f"カバレッジレポートスキャン開始: {directory}")

            # 各パターンでファイルを検索
            for pattern in self.coverage_patterns:
                search_pattern = f"**/{pattern}" if include_subdirs else pattern

                for report_file in directory.glob(search_pattern):
                    if report_file.is_file() and self._is_coverage_report(report_file):
                        file_info = self._create_file_info(report_file)
                        if file_info.is_valid:
                            coverage_files.append(file_info)

            self.logger.info(f"カバレッジレポートスキャン完了: {len(coverage_files)}個のファイルを発見")

        except Exception as e:
            error_msg = f"カバレッジレポートスキャン中にエラー: {str(e)}"
            self.logger.error(error_msg)
            self.errors.append(ErrorInfo(
                error_description=error_msg,
                error_source="scan_for_coverage_reports",
                error_severity=ErrorSeverity.ERROR.value
            ))

        return coverage_files

    def get_directory_stats(self, directory_path: str) -> DirectoryStats:
        """
        ディレクトリの統計情報を取得

        Args:
            directory_path: 対象ディレクトリパス

        Returns:
            DirectoryStats: ディレクトリ統計情報
        """
        stats = DirectoryStats()

        try:
            validation = self._validate_directory(directory_path)
            if not validation.is_valid:
                stats.is_valid = False
                stats.error_message = validation.error_message
                return stats

            directory = Path(directory_path)
            total_files = 0
            total_size = 0

            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    try:
                        file_size = file_path.stat().st_size
                        total_files += 1
                        total_size += file_size
                    except OSError as e:
                        self.logger.warning(f"ファイル統計取得失敗: {file_path} - {str(e)}")

            stats.total_files = total_files
            stats.total_size = total_size
            stats.is_valid = True

            self.logger.info(f"ディレクトリ統計: {total_files}ファイル, {total_size:,}バイト")

        except Exception as e:
            stats.is_valid = False
            stats.error_message = f"ディレクトリ統計取得中にエラー: {str(e)}"
            self.logger.error(stats.error_message)

        return stats

    def directory_exists(self, directory_path: str) -> bool:
        """
        ディレクトリの存在確認

        Args:
            directory_path: 確認するディレクトリパス

        Returns:
            bool: ディレクトリが存在する場合True
        """
        try:
            if not directory_path:
                return False

            path = Path(directory_path)
            return path.exists() and path.is_dir()

        except Exception as e:
            self.logger.error(f"ディレクトリ存在確認エラー: {str(e)}")
            return False

    def _validate_directory(self, directory_path: str) -> ValidationResult:
        """
        ディレクトリパスの検証

        Args:
            directory_path: 検証するディレクトリパス

        Returns:
            ValidationResult: 検証結果
        """
        result = ValidationResult()

        if not directory_path:
            result.is_valid = False
            result.error_message = "ディレクトリパスが指定されていません"
            return result

        try:
            path = Path(directory_path)

            if not path.exists():
                result.is_valid = False
                result.error_message = f"指定されたディレクトリが存在しません: {directory_path}"
                result.suggestion_message = "パスが正しいか確認してください"
            elif not path.is_dir():
                result.is_valid = False
                result.error_message = f"指定されたパスはディレクトリではありません: {directory_path}"
            elif not os.access(path, os.R_OK):
                result.is_valid = False
                result.error_message = f"ディレクトリへの読み取り権限がありません: {directory_path}"
                result.suggestion_message = "ディレクトリのアクセス権限を確認してください"

        except Exception as e:
            result.is_valid = False
            result.error_message = f"ディレクトリパス検証中にエラー: {str(e)}"

        return result

    def _should_include_java_file(self, file_path: Path) -> bool:
        """
        Javaファイルを含めるべきかどうかを判定

        Args:
            file_path: 判定するファイルパス

        Returns:
            bool: ファイルを含める場合True
        """
        try:
            file_name = file_path.name.lower()

            # ファイルサイズチェック
            if file_path.stat().st_size > self.config.max_file_size:
                self.logger.warning(f"ファイルサイズが上限を超過（スキップ）: {file_path}")
                return False

            # テストファイル判定
            if self.config.include_test_files:
                if 'test' in file_name:
                    return True

            # ITファイル判定
            if self.config.include_it_files:
                if file_name.startswith('it') or 'integration' in file_name:
                    return True

            # 抽象クラス除外
            if self.config.exclude_abstract_classes:
                if 'abstract' in file_name:
                    return False

            # デフォルトでJavaファイルは含める
            return file_path.suffix.lower() == '.java'

        except Exception as e:
            self.logger.warning(f"ファイル判定エラー: {file_path} - {str(e)}")
            return False

    def _is_coverage_report(self, file_path: Path) -> bool:
        """
        カバレッジレポートファイルかどうかを判定

        Args:
            file_path: 判定するファイルパス

        Returns:
            bool: カバレッジレポートファイルの場合True
        """
        try:
            file_name = file_path.name.lower()

            # 拡張子チェック
            if file_path.suffix.lower() not in self.coverage_extensions:
                return False

            # XMLファイルの場合
            if file_path.suffix.lower() == '.xml':
                return ('jacoco' in file_name or
                        'coverage' in file_name or
                        file_name == 'jacoco-report.xml')

            # HTMLファイルの場合
            if file_path.suffix.lower() == '.html':
                return ('coverage' in file_name or
                        file_name == 'index.html')

            return False

        except Exception as e:
            self.logger.warning(f"カバレッジレポート判定エラー: {file_path} - {str(e)}")
            return False

    def _create_file_info(self, file_path: Path) -> FileInfo:
        """
        ファイル情報オブジェクトを作成

        Args:
            file_path: ファイルパス

        Returns:
            FileInfo: ファイル情報オブジェクト
        """
        file_info = FileInfo()

        try:
            stat = file_path.stat()

            file_info.file_path = str(file_path.absolute())
            file_info.file_name = file_path.name
            file_info.file_size = stat.st_size
            file_info.modified_date = datetime.fromtimestamp(stat.st_mtime)
            file_info.is_valid = True

        except Exception as e:
            file_info.is_valid = False
            file_info.error_message = f"ファイル情報取得エラー: {str(e)}"
            self.logger.error(f"ファイル情報作成エラー: {file_path} - {str(e)}")

        return file_info

    def get_scan_progress(self) -> ProgressInfo:
        """
        スキャン進捗情報を取得

        Returns:
            ProgressInfo: 進捗情報
        """
        progress = ProgressInfo()
        progress.files_processed = self.total_files_scanned
        progress.current_step = f"ファイルスキャン中... ({self.total_files_scanned}個処理済み)"

        return progress

    def reset_statistics(self):
        """統計情報をリセット"""
        self.total_files_scanned = 0
        self.total_directories_scanned = 0
        self.errors.clear()

# テスト関数

def test_folder_scanner():
    """フォルダスキャナーのテスト"""
    print("🔍 FolderScannerテスト開始...")

    # テスト設定
    config = ConfigurationSettings()
    config.max_file_size = 1048576  # 1MB
    config.include_test_files = True
    config.include_it_files = True
    config.exclude_abstract_classes = True

    scanner = FolderScanner(config)

    # サンプルディレクトリでテスト
    test_dir = "/root/aws.git/container/claudecode/java-test-specs/sample-java-tests"

    if scanner.directory_exists(test_dir):
        print(f"✅ ディレクトリ存在確認: {test_dir}")

        # ディレクトリ統計
        stats = scanner.get_directory_stats(test_dir)
        if stats.is_valid:
            print(f"✅ ディレクトリ統計: {stats.total_files}ファイル, {stats.total_size:,}バイト")

        # Javaファイルスキャン
        java_files = scanner.scan_for_java_files(test_dir)
        print(f"✅ Javaファイル検出: {len(java_files)}個")
        for file_info in java_files:
            print(f"   - {file_info.file_name} ({file_info.file_size:,}バイト)")

        # カバレッジレポートスキャン
        coverage_files = scanner.scan_for_coverage_reports(test_dir)
        print(f"✅ カバレッジレポート検出: {len(coverage_files)}個")
        for file_info in coverage_files:
            print(f"   - {file_info.file_name} ({file_info.file_size:,}バイト)")

    else:
        print(f"❌ テストディレクトリが見つかりません: {test_dir}")

    print("🎉 FolderScannerテスト完了!")

if __name__ == "__main__":
    # ログ設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    test_folder_scanner()