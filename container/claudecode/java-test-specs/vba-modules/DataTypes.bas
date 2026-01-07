Attribute VB_Name = "DataTypes"
' ============================================================================
' DataTypes.bas
' Data type definitions for Java Test Specification Generator
'
' This module contains all custom data types and structures used throughout
' the VBA application for consistent data handling.
'
' Created: 2026-01-07
' Version: 1.0.0
' ============================================================================

Option Explicit

' Test case information structure
Public Type TestCaseInfo
    FilePath As String              ' Full path to the Java test file
    ClassName As String             ' Name of the test class
    MethodName As String            ' Name of the test method
    TestModule As String            ' @TestModule annotation value
    TestCase As String              ' @TestCase annotation value
    BaselineVersion As String       ' @BaselineVersion annotation value
    TestOverview As String          ' @TestOverview annotation value
    TestPurpose As String           ' @TestPurpose annotation value
    TestProcess As String           ' @TestProcess annotation value
    TestResults As String           ' @TestResults annotation value
    Creator As String               ' @Creator annotation value
    CreatedDate As Date             ' @CreatedDate annotation value
    Modifier As String              ' @Modifier annotation value
    ModifiedDate As Date            ' @ModifiedDate annotation value
    TestCategory As String          ' @TestCategory annotation value (optional)
    Priority As String              ' @Priority annotation value (optional)
    Requirements As String          ' @Requirements annotation value (optional)
    Dependencies As String          ' @Dependencies annotation value (optional)

    ' Coverage information (populated from coverage reports)
    CoveragePercent As Double       ' Branch coverage percentage
    BranchesCovered As Long         ' Number of branches covered
    BranchesTotal As Long           ' Total number of branches
    InstructionsCovered As Long     ' Number of instructions covered
    InstructionsTotal As Long       ' Total number of instructions

    ' Processing metadata
    IsValid As Boolean              ' Whether parsing was successful
    ErrorMessage As String          ' Error message if parsing failed
    ProcessedDate As Date           ' When this record was processed
End Type

' Coverage information from JaCoCo reports
Public Type CoverageInfo
    SourceFile As String            ' Source file path
    ClassName As String             ' Fully qualified class name
    MethodName As String            ' Method name
    LineNumber As Long              ' Starting line number

    ' Instruction coverage
    InstructionsCovered As Long     ' Instructions covered
    InstructionsMissed As Long      ' Instructions missed
    InstructionsTotal As Long       ' Total instructions

    ' Branch coverage (C1 coverage)
    BranchesCovered As Long         ' Branches covered
    BranchesMissed As Long          ' Branches missed
    BranchesTotal As Long           ' Total branches
    BranchCoverage As Double        ' Branch coverage percentage

    ' Line coverage
    LinesCovered As Long            ' Lines covered
    LinesMissed As Long             ' Lines missed
    LinesTotal As Long              ' Total lines

    ' Complexity coverage
    ComplexityCovered As Long       ' Complexity covered
    ComplexityMissed As Long        ' Complexity missed
    ComplexityTotal As Long         ' Total complexity

    ' Processing metadata
    ReportFile As String            ' Source coverage report file
    ReportType As String            ' Type of report (XML, HTML)
    IsValid As Boolean              ' Whether parsing was successful
    ErrorMessage As String          ' Error message if parsing failed
End Type

' File information structure
Public Type FileInfo
    FilePath As String              ' Full file path
    FileName As String              ' File name only
    FileSize As Long                ' File size in bytes
    ModifiedDate As Date            ' Last modification date
    IsValid As Boolean              ' Whether file access was successful
    ErrorMessage As String          ' Error message if access failed
End Type

' Directory statistics
Public Type DirectoryStats
    TotalFiles As Long              ' Total number of files
    TotalSize As Long               ' Total size in bytes
    IsValid As Boolean              ' Whether calculation was successful
    ErrorMessage As String          ' Error message if calculation failed
End Type

' Annotation parsing result
Public Type AnnotationResult
    AnnotationName As String        ' Name of the annotation (e.g., "TestModule")
    AnnotationValue As String       ' Value of the annotation
    LineNumber As Long              ' Line number where found
    IsValid As Boolean              ' Whether parsing was successful
End Type

' Summary statistics
Public Type SummaryStats
    TotalJavaFiles As Long          ' Total Java files processed
    TotalTestClasses As Long        ' Total test classes found
    TotalTestMethods As Long        ' Total test methods found
    TotalCoverageReports As Long    ' Total coverage reports found

    OverallBranchCoverage As Double ' Overall branch coverage percentage
    TotalBranchesCovered As Long    ' Total branches covered
    TotalBranches As Long           ' Total branches

    ProcessingStartTime As Date     ' When processing started
    ProcessingEndTime As Date       ' When processing completed
    ProcessingDuration As String    ' Formatted duration string

    ErrorCount As Long              ' Number of errors encountered
    WarningCount As Long            ' Number of warnings encountered
End Type

' Module coverage summary
Public Type ModuleCoverageStats
    ModuleName As String            ' Name of the module
    TestCaseCount As Long           ' Number of test cases in module
    BranchCoverage As Double        ' Branch coverage percentage
    Status As String                ' Coverage status (Excellent, Good, Poor)
    Color As Long                   ' Color code for Excel formatting
End Type

' Excel formatting information
Public Type ExcelFormatting
    HeaderBackgroundColor As Long   ' Background color for headers
    HeaderFontColor As Long         ' Font color for headers
    DataFontSize As Long            ' Font size for data rows
    IsBold As Boolean               ' Whether text is bold
    HasBorders As Boolean           ' Whether to apply borders
    TextWrap As Boolean             ' Whether to wrap text
    NumberFormat As String          ' Number format string
End Type

' Configuration settings
Public Type ConfigurationSettings
    SourceDirectory As String       ' Source directory path
    OutputFilePath As String        ' Output Excel file path
    IncludeSubdirectories As Boolean ' Whether to scan subdirectories
    ProcessCoverageReports As Boolean ' Whether to process coverage reports
    GenerateSummary As Boolean      ' Whether to generate summary sheet
    ApplyFormatting As Boolean      ' Whether to apply Excel formatting

    ' File filtering options
    IncludeTestFiles As Boolean     ' Include files with "Test" in name
    IncludeITFiles As Boolean       ' Include integration test files (IT)
    ExcludeAbstractClasses As Boolean ' Exclude abstract test classes

    ' Processing options
    MaxFileSize As Long             ' Maximum file size to process (bytes)
    TimeoutSeconds As Long          ' Processing timeout per file (seconds)
    LogDetailLevel As String        ' Logging detail level (Basic, Detailed, Verbose)
End Type

' Progress information
Public Type ProgressInfo
    CurrentStep As String           ' Description of current step
    PercentComplete As Long         ' Percentage complete (0-100)
    FilesProcessed As Long          ' Number of files processed so far
    TotalFiles As Long              ' Total number of files to process
    EstimatedTimeRemaining As String ' Estimated time remaining
    CurrentFileName As String       ' Name of file currently being processed
End Type

' Error information
Public Type ErrorInfo
    ErrorNumber As Long             ' VBA error number
    ErrorDescription As String      ' Error description
    ErrorSource As String           ' Function/module where error occurred
    ErrorTime As Date               ' When error occurred
    ErrorSeverity As String         ' Severity level (Warning, Error, Critical)
    AdditionalInfo As String        ' Additional context information
End Type

' Validation result
Public Type ValidationResult
    IsValid As Boolean              ' Whether validation passed
    ErrorMessage As String          ' Error message if validation failed
    WarningMessage As String        ' Warning message if applicable
    SuggestionMessage As String     ' Suggestion for fixing issues
End Type

' Coverage status enumeration values (as constants since VBA doesn't have enums)
Public Const COVERAGE_EXCELLENT As String = "Excellent"
Public Const COVERAGE_GOOD As String = "Good"
Public Const COVERAGE_FAIR As String = "Fair"
Public Const COVERAGE_POOR As String = "Poor"
Public Const COVERAGE_UNKNOWN As String = "Unknown"

' Priority level constants
Public Const PRIORITY_HIGH As String = "High"
Public Const PRIORITY_MEDIUM As String = "Medium"
Public Const PRIORITY_LOW As String = "Low"

' Test category constants
Public Const CATEGORY_UNIT As String = "Unit"
Public Const CATEGORY_INTEGRATION As String = "Integration"
Public Const CATEGORY_SYSTEM As String = "System"
Public Const CATEGORY_ACCEPTANCE As String = "Acceptance"
Public Const CATEGORY_PERFORMANCE As String = "Performance"
Public Const CATEGORY_SECURITY As String = "Security"

' Error severity constants
Public Const SEVERITY_WARNING As String = "Warning"
Public Const SEVERITY_ERROR As String = "Error"
Public Const SEVERITY_CRITICAL As String = "Critical"

' Report format constants
Public Const REPORT_FORMAT_XML As String = "XML"
Public Const REPORT_FORMAT_HTML As String = "HTML"
Public Const REPORT_FORMAT_JSON As String = "JSON"

' Excel color constants (RGB values converted to Long)
Public Const COLOR_HEADER_BLUE As Long = 5287936        ' RGB(79, 129, 189)
Public Const COLOR_LIGHT_BLUE As Long = 15389428        ' RGB(184, 204, 228)
Public Const COLOR_HEADER_GREEN As Long = 5296146       ' RGB(146, 208, 80)
Public Const COLOR_HEADER_YELLOW As Long = 10092543     ' RGB(255, 230, 153)
Public Const COLOR_WHITE As Long = 16777215             ' RGB(255, 255, 255)
Public Const COLOR_BLACK As Long = 0                    ' RGB(0, 0, 0)
Public Const COLOR_RED As Long = 255                    ' RGB(255, 0, 0)
Public Const COLOR_GREEN As Long = 65280                ' RGB(0, 255, 0)
Public Const COLOR_ORANGE As Long = 65535               ' RGB(255, 255, 0)

' Utility functions for working with data types
Public Function CreateTestCaseInfo() As TestCaseInfo
    Dim testCase As TestCaseInfo

    ' Initialize with default values
    testCase.FilePath = ""
    testCase.ClassName = ""
    testCase.MethodName = ""
    testCase.TestModule = "Not Specified"
    testCase.TestCase = "Not Specified"
    testCase.BaselineVersion = "Not Specified"
    testCase.TestOverview = "Not Specified"
    testCase.TestPurpose = "Not Specified"
    testCase.TestProcess = "Not Specified"
    testCase.TestResults = "Not Specified"
    testCase.Creator = "Unknown"
    testCase.CreatedDate = #1/1/1900#
    testCase.Modifier = ""
    testCase.ModifiedDate = #1/1/1900#
    testCase.TestCategory = ""
    testCase.Priority = ""
    testCase.Requirements = ""
    testCase.Dependencies = ""

    testCase.CoveragePercent = 0
    testCase.BranchesCovered = 0
    testCase.BranchesTotal = 0
    testCase.InstructionsCovered = 0
    testCase.InstructionsTotal = 0

    testCase.IsValid = True
    testCase.ErrorMessage = ""
    testCase.ProcessedDate = Now

    CreateTestCaseInfo = testCase
End Function

Public Function CreateCoverageInfo() As CoverageInfo
    Dim coverage As CoverageInfo

    ' Initialize with default values
    coverage.SourceFile = ""
    coverage.ClassName = ""
    coverage.MethodName = ""
    coverage.LineNumber = 0

    coverage.InstructionsCovered = 0
    coverage.InstructionsMissed = 0
    coverage.InstructionsTotal = 0

    coverage.BranchesCovered = 0
    coverage.BranchesMissed = 0
    coverage.BranchesTotal = 0
    coverage.BranchCoverage = 0

    coverage.LinesCovered = 0
    coverage.LinesMissed = 0
    coverage.LinesTotal = 0

    coverage.ComplexityCovered = 0
    coverage.ComplexityMissed = 0
    coverage.ComplexityTotal = 0

    coverage.ReportFile = ""
    coverage.ReportType = ""
    coverage.IsValid = True
    coverage.ErrorMessage = ""

    CreateCoverageInfo = coverage
End Function