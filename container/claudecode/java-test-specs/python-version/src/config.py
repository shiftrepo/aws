#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
config.py - Python版設定管理

Java Test Specification Generator の設定管理機能
デフォルト値、環境変数、設定ファイルのサポート

Created: 2026-01-07 (Pythonに移植)
Version: 2.0.0
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from .data_types import ConfigurationSettings

class ConfigManager:
    """設定管理クラス"""

    def __init__(self, config_file: Optional[str] = None):
        """
        初期化

        Args:
            config_file: 設定ファイルパス（オプション）
        """
        self.logger = logging.getLogger(__name__)
        self.config_file = config_file or "test_spec_generator_config.json"
        self._config = ConfigurationSettings()

    def load_config(self, config_file: Optional[str] = None) -> ConfigurationSettings:
        """
        設定を読み込み

        Args:
            config_file: 設定ファイルパス（オプション）

        Returns:
            ConfigurationSettings: 読み込まれた設定
        """
        if config_file:
            self.config_file = config_file

        try:
            # 設定ファイルが存在する場合は読み込み
            if Path(self.config_file).exists():
                self._load_from_file()

            # 環境変数から設定を上書き
            self._load_from_environment()

        except Exception as e:
            self.logger.warning(f"設定読み込みエラー: {str(e)}")

        return self._config

    def save_config(self, config: ConfigurationSettings, config_file: Optional[str] = None):
        """
        設定をファイルに保存

        Args:
            config: 保存する設定
            config_file: 設定ファイルパス（オプション）
        """
        if config_file:
            self.config_file = config_file

        try:
            config_data = {
                # パス設定
                "source_directory": config.source_directory,
                "output_file_path": config.output_file_path,
                "include_subdirectories": config.include_subdirectories,
                "process_coverage_reports": config.process_coverage_reports,
                "generate_summary": config.generate_summary,
                "apply_formatting": config.apply_formatting,

                # ファイルフィルタリング
                "include_test_files": config.include_test_files,
                "include_it_files": config.include_it_files,
                "exclude_abstract_classes": config.exclude_abstract_classes,

                # 処理オプション
                "max_file_size": config.max_file_size,
                "timeout_seconds": config.timeout_seconds,
                "log_detail_level": config.log_detail_level
            }

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"設定をファイルに保存: {self.config_file}")

        except Exception as e:
            self.logger.error(f"設定保存エラー: {str(e)}")

    def _load_from_file(self):
        """設定ファイルから読み込み"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            # 各設定項目を適用
            if "source_directory" in config_data:
                self._config.source_directory = config_data["source_directory"]
            if "output_file_path" in config_data:
                self._config.output_file_path = config_data["output_file_path"]
            if "include_subdirectories" in config_data:
                self._config.include_subdirectories = config_data["include_subdirectories"]
            if "process_coverage_reports" in config_data:
                self._config.process_coverage_reports = config_data["process_coverage_reports"]
            if "generate_summary" in config_data:
                self._config.generate_summary = config_data["generate_summary"]
            if "apply_formatting" in config_data:
                self._config.apply_formatting = config_data["apply_formatting"]
            if "include_test_files" in config_data:
                self._config.include_test_files = config_data["include_test_files"]
            if "include_it_files" in config_data:
                self._config.include_it_files = config_data["include_it_files"]
            if "exclude_abstract_classes" in config_data:
                self._config.exclude_abstract_classes = config_data["exclude_abstract_classes"]
            if "max_file_size" in config_data:
                self._config.max_file_size = config_data["max_file_size"]
            if "timeout_seconds" in config_data:
                self._config.timeout_seconds = config_data["timeout_seconds"]
            if "log_detail_level" in config_data:
                self._config.log_detail_level = config_data["log_detail_level"]

            self.logger.info(f"設定ファイルから読み込み: {self.config_file}")

        except Exception as e:
            self.logger.warning(f"設定ファイル読み込みエラー: {str(e)}")

    def _load_from_environment(self):
        """環境変数から設定を読み込み"""
        try:
            # 環境変数のマッピング
            env_mapping = {
                "TSG_SOURCE_DIR": "source_directory",
                "TSG_OUTPUT_FILE": "output_file_path",
                "TSG_INCLUDE_SUBDIRS": "include_subdirectories",
                "TSG_PROCESS_COVERAGE": "process_coverage_reports",
                "TSG_INCLUDE_TEST_FILES": "include_test_files",
                "TSG_INCLUDE_IT_FILES": "include_it_files",
                "TSG_EXCLUDE_ABSTRACT": "exclude_abstract_classes",
                "TSG_MAX_FILE_SIZE": "max_file_size",
                "TSG_TIMEOUT": "timeout_seconds",
                "TSG_LOG_LEVEL": "log_detail_level"
            }

            for env_var, config_attr in env_mapping.items():
                env_value = os.environ.get(env_var)
                if env_value:
                    # 型変換
                    if config_attr in ["include_subdirectories", "process_coverage_reports",
                                     "include_test_files", "include_it_files", "exclude_abstract_classes"]:
                        # ブール値
                        setattr(self._config, config_attr, env_value.lower() in ['true', '1', 'yes', 'on'])
                    elif config_attr in ["max_file_size", "timeout_seconds"]:
                        # 整数値
                        setattr(self._config, config_attr, int(env_value))
                    else:
                        # 文字列値
                        setattr(self._config, config_attr, env_value)

            # 環境変数が設定されている場合はログ出力
            env_vars_found = [var for var in env_mapping.keys() if os.environ.get(var)]
            if env_vars_found:
                self.logger.info(f"環境変数から設定読み込み: {', '.join(env_vars_found)}")

        except Exception as e:
            self.logger.warning(f"環境変数読み込みエラー: {str(e)}")

    def get_default_config(self) -> ConfigurationSettings:
        """
        デフォルト設定を取得

        Returns:
            ConfigurationSettings: デフォルト設定
        """
        return ConfigurationSettings()

    def validate_config(self, config: ConfigurationSettings) -> Dict[str, str]:
        """
        設定の妥当性をチェック

        Args:
            config: チェックする設定

        Returns:
            Dict[str, str]: 検証エラーの辞書（キー：項目名、値：エラーメッセージ）
        """
        errors = {}

        # ソースディレクトリのチェック
        if config.source_directory and not Path(config.source_directory).exists():
            errors["source_directory"] = f"ソースディレクトリが存在しません: {config.source_directory}"

        # 出力ファイルのディレクトリチェック
        if config.output_file_path:
            output_dir = Path(config.output_file_path).parent
            if not output_dir.exists():
                try:
                    output_dir.mkdir(parents=True, exist_ok=True)
                except Exception:
                    errors["output_file_path"] = f"出力ディレクトリを作成できません: {output_dir}"

        # ファイルサイズのチェック
        if config.max_file_size < 1024:  # 1KB未満
            errors["max_file_size"] = "最大ファイルサイズが小さすぎます（1KB以上）"

        # タイムアウトのチェック
        if config.timeout_seconds < 1:
            errors["timeout_seconds"] = "タイムアウト時間が短すぎます（1秒以上）"

        return errors

# デフォルト設定インスタンス
_default_config_manager = ConfigManager()

def get_config(config_file: Optional[str] = None) -> ConfigurationSettings:
    """
    設定を取得する便利関数

    Args:
        config_file: 設定ファイルパス（オプション）

    Returns:
        ConfigurationSettings: 設定オブジェクト
    """
    return _default_config_manager.load_config(config_file)

def save_config(config: ConfigurationSettings, config_file: Optional[str] = None):
    """
    設定を保存する便利関数

    Args:
        config: 保存する設定
        config_file: 設定ファイルパス（オプション）
    """
    _default_config_manager.save_config(config, config_file)

# 設定ファイルのサンプル生成
def create_sample_config_file(file_path: str = "test_spec_generator_config.json"):
    """
    サンプル設定ファイルを作成

    Args:
        file_path: 作成するファイルパス
    """
    sample_config = {
        "source_directory": "./sample-java-tests",
        "output_file_path": "./test_specification.xlsx",
        "include_subdirectories": True,
        "process_coverage_reports": True,
        "generate_summary": True,
        "apply_formatting": True,

        "include_test_files": True,
        "include_it_files": True,
        "exclude_abstract_classes": True,

        "max_file_size": 10485760,
        "timeout_seconds": 30,
        "log_detail_level": "Detailed"
    }

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, indent=2, ensure_ascii=False)

        print(f"✅ サンプル設定ファイル作成: {file_path}")

    except Exception as e:
        print(f"❌ サンプル設定ファイル作成エラー: {str(e)}")

if __name__ == "__main__":
    # サンプル設定ファイル作成
    create_sample_config_file()

    # 設定管理テスト
    print("🔧 設定管理テスト開始...")

    config_manager = ConfigManager()
    config = config_manager.get_default_config()

    print(f"✅ デフォルト設定:")
    print(f"   最大ファイルサイズ: {config.max_file_size:,}バイト")
    print(f"   タイムアウト: {config.timeout_seconds}秒")
    print(f"   ログレベル: {config.log_detail_level}")

    # 設定検証テスト
    errors = config_manager.validate_config(config)
    if errors:
        print(f"⚠️ 設定エラー: {errors}")
    else:
        print("✅ 設定検証OK")

    print("🎉 設定管理テスト完了!")