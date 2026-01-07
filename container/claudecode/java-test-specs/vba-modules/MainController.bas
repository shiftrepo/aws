Attribute VB_Name = "MainController"
' ============================================================================
' MainController.bas
' Main controller module for Java Test Specification Generator
'
' This module orchestrates the entire test specification generation process:
' 1. User interface and configuration
' 2. File scanning coordination
' 3. Annotation parsing coordination
' 4. Coverage report processing
' 5. Excel output generation
'
' Created: 2026-01-07
' Version: 1.0.0
' ============================================================================

Option Explicit

' Public constants for application configuration
Public Const APP_NAME As String = "Java Test Specification Generator"
Public Const APP_VERSION As String = "1.0.0"
Public Const SUPPORTED_JAVA_EXTENSIONS As String = "*.java"
Public Const SUPPORTED_COVERAGE_EXTENSIONS As String = "*.xml;*.html"

' Public variables for global state
Public g_SourceDirectory As String
Public g_OutputFile As String
Public g_ProcessingStartTime As Date
Public g_TotalFilesProcessed As Long
Public g_TotalTestCasesFound As Long
Public g_TotalCoverageReportsFound As Long
Public g_ProcessingErrors As Collection

' Main entry point - called from Excel ribbon or button
Public Sub GenerateTestSpecification()
    On Error GoTo ErrorHandler

    ' Initialize application
    InitializeApplication

    ' Show configuration dialog
    If Not ShowConfigurationDialog() Then
        MsgBox "Test specification generation cancelled by user.", vbInformation, APP_NAME
        Exit Sub
    End If

    ' Validate configuration
    If Not ValidateConfiguration() Then
        Exit Sub
    End If

    ' Start processing
    g_ProcessingStartTime = Now
    ShowProgressForm

    ' Execute main processing workflow
    ExecuteMainWorkflow

    ' Show completion message
    ShowCompletionMessage

    Exit Sub

ErrorHandler:
    HandleFatalError "MainController.GenerateTestSpecification", Err.Number, Err.Description
End Sub

' Initialize application state and error handling
Private Sub InitializeApplication()
    On Error GoTo ErrorHandler

    ' Initialize global variables
    g_SourceDirectory = ""
    g_OutputFile = ""
    g_TotalFilesProcessed = 0
    g_TotalTestCasesFound = 0
    g_TotalCoverageReportsFound = 0

    ' Initialize error collection
    Set g_ProcessingErrors = New Collection

    ' Enable calculation and screen updating
    Application.Calculation = xlCalculationAutomatic
    Application.ScreenUpdating = True

    Exit Sub

ErrorHandler:
    MsgBox "Failed to initialize application: " & Err.Description, vbCritical, APP_NAME
End Sub

' Show configuration dialog and get user inputs
Private Function ShowConfigurationDialog() As Boolean
    On Error GoTo ErrorHandler

    Dim configForm As Object
    Dim dialogResult As VbMsgBoxResult

    ' Create simple input dialogs (can be replaced with custom UserForm)
    g_SourceDirectory = InputBox("Enter the source directory containing Java test files:", _
                                APP_NAME & " - Configuration", _
                                "C:\Projects\MyProject\src\test\java")

    If g_SourceDirectory = "" Then
        ShowConfigurationDialog = False
        Exit Function
    End If

    g_OutputFile = InputBox("Enter the output file path for the Excel report:", _
                           APP_NAME & " - Configuration", _
                           "C:\Reports\TestSpecification_" & Format(Now, "yyyymmdd_hhmmss") & ".xlsx")

    If g_OutputFile = "" Then
        ShowConfigurationDialog = False
        Exit Function
    End If

    ' Confirm configuration
    Dim confirmMsg As String
    confirmMsg = "Configuration Summary:" & vbCrLf & vbCrLf & _
                "Source Directory: " & g_SourceDirectory & vbCrLf & _
                "Output File: " & g_OutputFile & vbCrLf & vbCrLf & _
                "Proceed with test specification generation?"

    dialogResult = MsgBox(confirmMsg, vbYesNo + vbQuestion, APP_NAME & " - Confirm Configuration")
    ShowConfigurationDialog = (dialogResult = vbYes)

    Exit Function

ErrorHandler:
    MsgBox "Configuration dialog error: " & Err.Description, vbCritical, APP_NAME
    ShowConfigurationDialog = False
End Function

' Validate user configuration inputs
Private Function ValidateConfiguration() As Boolean
    On Error GoTo ErrorHandler

    ValidateConfiguration = True

    ' Validate source directory
    If Not FolderScanner.DirectoryExists(g_SourceDirectory) Then
        MsgBox "Source directory does not exist: " & g_SourceDirectory, vbCritical, APP_NAME
        ValidateConfiguration = False
        Exit Function
    End If

    ' Validate output file directory
    Dim outputDir As String
    outputDir = Left(g_OutputFile, InStrRev(g_OutputFile, "\") - 1)
    If Not FolderScanner.DirectoryExists(outputDir) Then
        MsgBox "Output directory does not exist: " & outputDir, vbCritical, APP_NAME
        ValidateConfiguration = False
        Exit Function
    End If

    ' Check for existing output file
    If Dir(g_OutputFile) <> "" Then
        Dim overwriteResult As VbMsgBoxResult
        overwriteResult = MsgBox("Output file already exists. Overwrite?", vbYesNo + vbQuestion, APP_NAME)
        If overwriteResult = vbNo Then
            ValidateConfiguration = False
            Exit Function
        End If
    End If

    Exit Function

ErrorHandler:
    MsgBox "Configuration validation error: " & Err.Description, vbCritical, APP_NAME
    ValidateConfiguration = False
End Function

' Execute the main workflow
Private Sub ExecuteMainWorkflow()
    On Error GoTo ErrorHandler

    UpdateProgress "Scanning for Java test files...", 10

    ' Step 1: Scan for Java files
    Dim javaFiles As Collection
    Set javaFiles = FolderScanner.ScanForJavaFiles(g_SourceDirectory)
    g_TotalFilesProcessed = javaFiles.Count

    UpdateProgress "Found " & javaFiles.Count & " Java files. Processing annotations...", 20

    ' Step 2: Process Java annotations
    Dim testCaseData As Collection
    Set testCaseData = JavaAnnotationParser.ProcessJavaFiles(javaFiles)
    g_TotalTestCasesFound = testCaseData.Count

    UpdateProgress "Found " & testCaseData.Count & " test cases. Scanning for coverage reports...", 40

    ' Step 3: Scan for coverage reports
    Dim coverageFiles As Collection
    Set coverageFiles = FolderScanner.ScanForCoverageReports(g_SourceDirectory)
    g_TotalCoverageReportsFound = coverageFiles.Count

    UpdateProgress "Found " & coverageFiles.Count & " coverage reports. Processing coverage data...", 60

    ' Step 4: Process coverage reports
    Dim coverageData As Collection
    Set coverageData = CoverageReportParser.ProcessCoverageReports(coverageFiles)

    UpdateProgress "Merging test and coverage data...", 70

    ' Step 5: Merge test case and coverage data
    Dim mergedData As Collection
    Set mergedData = MergeTestAndCoverageData(testCaseData, coverageData)

    UpdateProgress "Generating Excel report...", 80

    ' Step 6: Generate Excel output
    ExcelSheetBuilder.GenerateTestSpecificationReport g_OutputFile, mergedData, testCaseData, coverageData

    UpdateProgress "Test specification generation completed!", 100

    Exit Sub

ErrorHandler:
    g_ProcessingErrors.Add "MainController.ExecuteMainWorkflow: " & Err.Description
    HandleProcessingError "ExecuteMainWorkflow", Err.Number, Err.Description
End Sub

' Merge test case data with coverage data
Private Function MergeTestAndCoverageData(testCases As Collection, coverage As Collection) As Collection
    On Error GoTo ErrorHandler

    Set MergeTestAndCoverageData = New Collection

    Dim testCase As TestCaseInfo
    Dim coverageInfo As CoverageInfo
    Dim i As Long, j As Long

    ' For each test case, find matching coverage data
    For i = 1 To testCases.Count
        Set testCase = testCases(i)

        ' Look for matching coverage data by file path
        For j = 1 To coverage.Count
            Set coverageInfo = coverage(j)
            If InStr(LCase(testCase.FilePath), LCase(coverageInfo.SourceFile)) > 0 Then
                ' Found matching coverage data
                testCase.CoveragePercent = coverageInfo.BranchCoverage
                testCase.BranchesCovered = coverageInfo.BranchesCovered
                testCase.BranchesTotal = coverageInfo.BranchesTotal
                Exit For
            End If
        Next j

        MergeTestAndCoverageData.Add testCase
    Next i

    Exit Function

ErrorHandler:
    g_ProcessingErrors.Add "MainController.MergeTestAndCoverageData: " & Err.Description
    Set MergeTestAndCoverageData = testCases ' Return original data if merge fails
End Function

' Show progress form (placeholder - implement custom UserForm)
Private Sub ShowProgressForm()
    ' This would show a custom progress UserForm
    ' For now, use status bar
    Application.StatusBar = "Java Test Specification Generator - Starting..."
End Sub

' Update progress display
Private Sub UpdateProgress(message As String, percent As Long)
    Application.StatusBar = APP_NAME & " - " & message & " (" & percent & "%)"
    DoEvents ' Allow UI to update
End Sub

' Show completion message
Private Sub ShowCompletionMessage()
    On Error GoTo ErrorHandler

    Dim processingTime As String
    processingTime = Format(Now - g_ProcessingStartTime, "hh:mm:ss")

    Dim summaryMsg As String
    summaryMsg = "Test Specification Generation Completed!" & vbCrLf & vbCrLf & _
                "Processing Summary:" & vbCrLf & _
                "- Java files processed: " & g_TotalFilesProcessed & vbCrLf & _
                "- Test cases found: " & g_TotalTestCasesFound & vbCrLf & _
                "- Coverage reports found: " & g_TotalCoverageReportsFound & vbCrLf & _
                "- Processing time: " & processingTime & vbCrLf & _
                "- Output file: " & g_OutputFile

    If g_ProcessingErrors.Count > 0 Then
        summaryMsg = summaryMsg & vbCrLf & vbCrLf & _
                    "Warnings/Errors: " & g_ProcessingErrors.Count & " (see log for details)"
    End If

    summaryMsg = summaryMsg & vbCrLf & vbCrLf & "Open the generated report now?"

    Dim openResult As VbMsgBoxResult
    openResult = MsgBox(summaryMsg, vbYesNo + vbInformation, APP_NAME & " - Generation Complete")

    If openResult = vbYes Then
        OpenGeneratedReport
    End If

    Application.StatusBar = False ' Clear status bar

    Exit Sub

ErrorHandler:
    MsgBox "Error showing completion message: " & Err.Description, vbExclamation, APP_NAME
    Application.StatusBar = False
End Sub

' Open the generated Excel report
Private Sub OpenGeneratedReport()
    On Error GoTo ErrorHandler

    If Dir(g_OutputFile) <> "" Then
        Workbooks.Open g_OutputFile
    Else
        MsgBox "Generated report file not found: " & g_OutputFile, vbExclamation, APP_NAME
    End If

    Exit Sub

ErrorHandler:
    MsgBox "Failed to open generated report: " & Err.Description, vbExclamation, APP_NAME
End Sub

' Handle processing errors (non-fatal)
Private Sub HandleProcessingError(functionName As String, errorNumber As Long, errorDescription As String)
    Dim errorMsg As String
    errorMsg = "Error in " & functionName & ": " & errorDescription & " (Error #" & errorNumber & ")"

    ' Log error but continue processing
    g_ProcessingErrors.Add errorMsg

    ' Show error dialog with option to continue
    Dim continueResult As VbMsgBoxResult
    continueResult = MsgBox(errorMsg & vbCrLf & vbCrLf & _
                           "Continue processing?", _
                           vbYesNo + vbExclamation, APP_NAME & " - Processing Error")

    If continueResult = vbNo Then
        End ' Stop execution
    End If
End Sub

' Handle fatal errors
Private Sub HandleFatalError(functionName As String, errorNumber As Long, errorDescription As String)
    Dim errorMsg As String
    errorMsg = "Fatal error in " & functionName & ": " & errorDescription & " (Error #" & errorNumber & ")"

    MsgBox errorMsg & vbCrLf & vbCrLf & _
           "Test specification generation will be terminated.", _
           vbCritical, APP_NAME & " - Fatal Error"

    Application.StatusBar = False
    End ' Stop execution
End Sub

' Clean up resources
Private Sub CleanupResources()
    Set g_ProcessingErrors = Nothing
    Application.StatusBar = False
End Sub