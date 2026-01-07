#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
data_types.py - Python版データ構造定義

VBAのDataTypes.basから移植されたデータ構造
JavaテストspecificationジェネレータでやVBAの全てのデータ型を
Pythonのdataclassesとenumで再現

Created: 2026-01-07 (Pythonで移植)
Version: 2.0.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pathlib import Path

# 列挙型の定義

class CoverageStatus(Enum):
    """カバレッジステータス"""
    EXCELLENT = "Excellent"
    GOOD = "Good"
    FAIR = "Fair"
    POOR = "Poor"
    UNKNOWN = "Unknown"

class Priority(Enum):
    """優先度レベル"""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class TestCategory(Enum):
    """テストカテゴリ"""
    UNIT = "Unit"
    INTEGRATION = "Integration"
    SYSTEM = "System"
    ACCEPTANCE = "Acceptance"
    PERFORMANCE = "Performance"
    SECURITY = "Security"

class ErrorSeverity(Enum):
    """エラー深刻度"""
    WARNING = "Warning"
    ERROR = "Error"
    CRITICAL = "Critical"

class ReportFormat(Enum):
    """レポート形式"""
    XML = "XML"
    HTML = "HTML"
    JSON = "JSON"

# Excel色定数クラス
class ExcelColors:
    """Excelカラー定数（RGB値をLongに変換）"""
    HEADER_BLUE = 5287936        # RGB(79, 129, 189)
    LIGHT_BLUE = 15389428        # RGB(184, 204, 228)
    HEADER_GREEN = 5296146       # RGB(146, 208, 80)
    HEADER_YELLOW = 10092543     # RGB(255, 230, 153)
    WHITE = 16777215             # RGB(255, 255, 255)
    BLACK = 0                    # RGB(0, 0, 0)
    RED = 255                    # RGB(255, 0, 0)
    GREEN = 65280                # RGB(0, 255, 0)
    ORANGE = 65535               # RGB(255, 255, 0)

# メインデータ構造

@dataclass
class TestCaseInfo:
    """テストケース情報構造体"""
    # ファイル情報
    file_path: str = ""
    class_name: str = ""
    method_name: str = ""

    # アノテーション情報
    test_module: str = "Not Specified"
    test_case: str = "Not Specified"
    baseline_version: str = "Not Specified"
    test_overview: str = "Not Specified"
    test_purpose: str = "Not Specified"
    test_process: str = "Not Specified"
    test_results: str = "Not Specified"
    creator: str = "Unknown"
    created_date: Optional[datetime] = None
    modifier: str = ""
    modified_date: Optional[datetime] = None
    test_category: str = ""
    priority: str = ""
    requirements: str = ""
    dependencies: str = ""

    # カバレッジ情報
    coverage_percent: float = 0.0
    branches_covered: int = 0
    branches_total: int = 0
    instructions_covered: int = 0
    instructions_total: int = 0

    # 処理メタデータ
    is_valid: bool = True
    error_message: str = ""
    processed_date: datetime = field(default_factory=datetime.now)

@dataclass
class CoverageInfo:
    """JaCoCoカバレッジ情報構造体"""
    # ソース情報
    source_file: str = ""
    class_name: str = ""
    method_name: str = ""
    line_number: int = 0

    # 命令カバレッジ
    instructions_covered: int = 0
    instructions_missed: int = 0
    instructions_total: int = 0

    # ブランチカバレッジ (C1カバレッジ)
    branches_covered: int = 0
    branches_missed: int = 0
    branches_total: int = 0
    branch_coverage: float = 0.0

    # ラインカバレッジ
    lines_covered: int = 0
    lines_missed: int = 0
    lines_total: int = 0

    # 複雑度カバレッジ
    complexity_covered: int = 0
    complexity_missed: int = 0
    complexity_total: int = 0

    # 処理メタデータ
    report_file: str = ""
    report_type: str = ""
    is_valid: bool = True
    error_message: str = ""

@dataclass
class FileInfo:
    """ファイル情報構造体"""
    file_path: str = ""
    file_name: str = ""
    file_size: int = 0
    modified_date: Optional[datetime] = None
    is_valid: bool = True
    error_message: str = ""

@dataclass
class DirectoryStats:
    """ディレクトリ統計構造体"""
    total_files: int = 0
    total_size: int = 0
    is_valid: bool = True
    error_message: str = ""

@dataclass
class AnnotationResult:
    """アノテーション解析結果構造体"""
    annotation_name: str = ""
    annotation_value: str = ""
    line_number: int = 0
    is_valid: bool = True

@dataclass
class SummaryStats:
    """統計情報構造体"""
    # ファイル統計
    total_java_files: int = 0
    total_test_classes: int = 0
    total_test_methods: int = 0
    total_coverage_reports: int = 0

    # カバレッジ統計
    overall_branch_coverage: float = 0.0
    total_branches_covered: int = 0
    total_branches: int = 0

    # 処理時間統計
    processing_start_time: Optional[datetime] = None
    processing_end_time: Optional[datetime] = None
    processing_duration: str = ""

    # エラー統計
    error_count: int = 0
    warning_count: int = 0

@dataclass
class ModuleCoverageStats:
    """モジュールカバレッジ統計構造体"""
    module_name: str = ""
    test_case_count: int = 0
    branch_coverage: float = 0.0
    status: str = CoverageStatus.UNKNOWN.value
    color: int = ExcelColors.WHITE

@dataclass
class ExcelFormatting:
    """Excel書式設定構造体"""
    header_background_color: int = ExcelColors.HEADER_BLUE
    header_font_color: int = ExcelColors.WHITE
    data_font_size: int = 11
    is_bold: bool = False
    has_borders: bool = True
    text_wrap: bool = True
    number_format: str = "General"

@dataclass
class ConfigurationSettings:
    """設定構造体"""
    # パス設定
    source_directory: str = ""
    output_file_path: str = ""
    include_subdirectories: bool = True
    process_coverage_reports: bool = True
    generate_summary: bool = True
    apply_formatting: bool = True

    # ファイルフィルタリングオプション
    include_test_files: bool = True
    include_it_files: bool = True
    exclude_abstract_classes: bool = True

    # 処理オプション
    max_file_size: int = 10485760  # 10MB
    timeout_seconds: int = 30
    log_detail_level: str = "Detailed"

@dataclass
class ProgressInfo:
    """進捗情報構造体"""
    current_step: str = ""
    percent_complete: int = 0
    files_processed: int = 0
    total_files: int = 0
    estimated_time_remaining: str = ""
    current_file_name: str = ""

@dataclass
class ErrorInfo:
    """エラー情報構造体"""
    error_number: int = 0
    error_description: str = ""
    error_source: str = ""
    error_time: datetime = field(default_factory=datetime.now)
    error_severity: str = ErrorSeverity.ERROR.value
    additional_info: str = ""

@dataclass
class ValidationResult:
    """検証結果構造体"""
    is_valid: bool = True
    error_message: str = ""
    warning_message: str = ""
    suggestion_message: str = ""

# ユーティリティ関数

def create_test_case_info() -> TestCaseInfo:
    """デフォルト値で初期化されたTestCaseInfoを作成"""
    return TestCaseInfo(
        created_date=datetime(1900, 1, 1),
        modified_date=datetime(1900, 1, 1),
        processed_date=datetime.now()
    )

def create_coverage_info() -> CoverageInfo:
    """デフォルト値で初期化されたCoverageInfoを作成"""
    return CoverageInfo()

def get_coverage_status(coverage_percent: float) -> CoverageStatus:
    """カバレッジ率からステータスを判定"""
    if coverage_percent >= 90.0:
        return CoverageStatus.EXCELLENT
    elif coverage_percent >= 80.0:
        return CoverageStatus.GOOD
    elif coverage_percent >= 60.0:
        return CoverageStatus.FAIR
    elif coverage_percent > 0.0:
        return CoverageStatus.POOR
    else:
        return CoverageStatus.UNKNOWN

def get_coverage_color(status: CoverageStatus) -> int:
    """カバレッジステータスから表示色を取得"""
    color_map = {
        CoverageStatus.EXCELLENT: ExcelColors.HEADER_GREEN,
        CoverageStatus.GOOD: ExcelColors.LIGHT_BLUE,
        CoverageStatus.FAIR: ExcelColors.HEADER_YELLOW,
        CoverageStatus.POOR: ExcelColors.RED,
        CoverageStatus.UNKNOWN: ExcelColors.WHITE
    }
    return color_map.get(status, ExcelColors.WHITE)

def format_duration(start_time: datetime, end_time: datetime) -> str:
    """処理時間を読みやすい形式でフォーマット"""
    if not start_time or not end_time:
        return "00:00:00"

    duration = end_time - start_time
    hours, remainder = divmod(duration.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

def validate_file_path(file_path: str) -> ValidationResult:
    """ファイルパスの有効性を検証"""
    result = ValidationResult()

    if not file_path:
        result.is_valid = False
        result.error_message = "ファイルパスが指定されていません"
        return result

    try:
        path = Path(file_path)
        if not path.exists():
            result.is_valid = False
            result.error_message = f"指定されたファイルが存在しません: {file_path}"
            result.suggestion_message = "パスが正しいか確認してください"
        elif not path.is_file():
            result.is_valid = False
            result.error_message = f"指定されたパスはファイルではありません: {file_path}"
    except Exception as e:
        result.is_valid = False
        result.error_message = f"ファイルパスの検証中にエラーが発生: {str(e)}"

    return result

# カスタム例外クラス

class TestSpecificationError(Exception):
    """テスト仕様書生成エラー"""
    pass

class AnnotationParsingError(TestSpecificationError):
    """アノテーション解析エラー"""
    pass

class CoverageParsingError(TestSpecificationError):
    """カバレッジ解析エラー"""
    pass

class ExcelGenerationError(TestSpecificationError):
    """Excel生成エラー"""
    pass

if __name__ == "__main__":
    # データ構造のテスト
    print("🔍 Python版データ構造テスト開始...")

    # TestCaseInfoのテスト
    test_case = create_test_case_info()
    test_case.class_name = "BasicCalculatorTest"
    test_case.method_name = "testConditionalCalculation"
    test_case.test_module = "CalculatorModule"
    test_case.coverage_percent = 94.6
    test_case.branches_covered = 140
    test_case.branches_total = 148

    print(f"✅ TestCaseInfo作成: {test_case.class_name}.{test_case.method_name}")
    print(f"   カバレッジ: {test_case.coverage_percent}% ({test_case.branches_covered}/{test_case.branches_total})")

    # CoverageInfoのテスト
    coverage = create_coverage_info()
    coverage.class_name = "BasicCalculatorTest"
    coverage.branch_coverage = 94.6
    coverage.branches_covered = 140
    coverage.branches_total = 148

    # カバレッジステータステスト
    status = get_coverage_status(coverage.branch_coverage)
    color = get_coverage_color(status)

    print(f"✅ CoverageInfo作成: {coverage.class_name}")
    print(f"   ステータス: {status.value}, カラー: {color}")

    # ValidationResultのテスト
    validation = validate_file_path("/nonexistent/file.java")
    if not validation.is_valid:
        print(f"✅ ファイル検証テスト: {validation.error_message}")

    print("🎉 Python版データ構造テスト完了!")