Attribute VB_Name = "ExcelSheetBuilder"
' ============================================================================
' ExcelSheetBuilder.bas
' Excel sheet generation module for Test Specification Generator
'
' This module handles creation of the final Excel report with:
' 1. Test Details sheet - Complete test case information
' 2. Summary sheet - Aggregated statistics and metrics
' 3. Coverage sheet - Detailed coverage analysis
' 4. Configuration sheet - Processing settings and metadata
'
' Created: 2026-01-07
' Version: 1.0.0
' ============================================================================

Option Explicit

' Generate the complete test specification report
Public Sub GenerateTestSpecificationReport(outputFile As String, mergedData As Collection, _
                                         testCaseData As Collection, coverageData As Collection)
    On Error GoTo ErrorHandler

    ' Create new workbook
    Dim wb As Workbook
    Set wb = Workbooks.Add

    ' Disable screen updating for performance
    Application.ScreenUpdating = False
    Application.Calculation = xlCalculationManual

    ' Create all sheets
    CreateTestDetailsSheet wb, mergedData
    CreateSummarySheet wb, testCaseData, coverageData
    CreateCoverageSheet wb, coverageData
    CreateConfigurationSheet wb

    ' Remove default sheets
    RemoveDefaultSheets wb

    ' Save the workbook
    wb.SaveAs outputFile, xlOpenXMLWorkbook

    ' Re-enable screen updating
    Application.ScreenUpdating = True
    Application.Calculation = xlCalculationAutomatic

    ' Close the workbook (user will open it separately if desired)
    wb.Close SaveChanges:=False

    Exit Sub

ErrorHandler:
    Application.ScreenUpdating = True
    Application.Calculation = xlCalculationAutomatic
    MainController.g_ProcessingErrors.Add "ExcelSheetBuilder.GenerateTestSpecificationReport: " & Err.Description

    ' Try to clean up workbook if it was created
    On Error Resume Next
    If Not wb Is Nothing Then wb.Close SaveChanges:=False
End Sub

' Create the Test Details sheet
Private Sub CreateTestDetailsSheet(wb As Workbook, testCaseData As Collection)
    On Error GoTo ErrorHandler

    Dim ws As Worksheet
    Set ws = wb.Worksheets.Add
    ws.Name = "Test Details"

    ' Create header section
    CreateTestDetailsHeaders ws

    ' Populate data rows
    PopulateTestDetailsData ws, testCaseData

    ' Apply formatting
    FormatTestDetailsSheet ws, testCaseData.Count

    Exit Sub

ErrorHandler:
    MainController.g_ProcessingErrors.Add "ExcelSheetBuilder.CreateTestDetailsSheet: " & Err.Description
End Sub

' Create headers for Test Details sheet
Private Sub CreateTestDetailsHeaders(ws As Worksheet)
    On Error Resume Next

    With ws
        ' Title and metadata
        .Cells(1, 1).Value = "Test Specification Report"
        .Cells(2, 1).Value = "Generated on: " & Format(Now, "yyyy-mm-dd hh:mm:ss")
        .Cells(3, 1).Value = "Source Directory: " & MainController.g_SourceDirectory
        .Cells(4, 1).Value = ""

        ' Column headers
        .Cells(5, 1).Value = "File Path"
        .Cells(5, 2).Value = "Test Module"
        .Cells(5, 3).Value = "Test Case"
        .Cells(5, 4).Value = "Baseline Version"
        .Cells(5, 5).Value = "Test Overview"
        .Cells(5, 6).Value = "Test Purpose"
        .Cells(5, 7).Value = "Test Process"
        .Cells(5, 8).Value = "Test Results"
        .Cells(5, 9).Value = "Creator"
        .Cells(5, 10).Value = "Created Date"
        .Cells(5, 11).Value = "Modifier"
        .Cells(5, 12).Value = "Modified Date"
        .Cells(5, 13).Value = "Coverage %"
        .Cells(5, 14).Value = "Branches Covered"
        .Cells(5, 15).Value = "Branches Total"
    End With
End Sub

' Populate data rows for Test Details sheet
Private Sub PopulateTestDetailsData(ws As Worksheet, testCaseData As Collection)
    On Error Resume Next

    Dim i As Long
    Dim testCase As TestCaseInfo
    Dim row As Long

    For i = 1 To testCaseData.Count
        testCase = testCaseData(i)
        row = 5 + i ' Start after header row

        With ws
            .Cells(row, 1).Value = testCase.FilePath
            .Cells(row, 2).Value = testCase.TestModule
            .Cells(row, 3).Value = testCase.TestCase
            .Cells(row, 4).Value = testCase.BaselineVersion
            .Cells(row, 5).Value = testCase.TestOverview
            .Cells(row, 6).Value = testCase.TestPurpose
            .Cells(row, 7).Value = testCase.TestProcess
            .Cells(row, 8).Value = testCase.TestResults
            .Cells(row, 9).Value = testCase.Creator
            .Cells(row, 10).Value = testCase.CreatedDate
            .Cells(row, 11).Value = testCase.Modifier
            .Cells(row, 12).Value = testCase.ModifiedDate
            .Cells(row, 13).Value = testCase.CoveragePercent / 100 ' Convert to percentage
            .Cells(row, 14).Value = testCase.BranchesCovered
            .Cells(row, 15).Value = testCase.BranchesTotal
        End With
    Next i
End Sub

' Format the Test Details sheet
Private Sub FormatTestDetailsSheet(ws As Worksheet, dataRows As Long)
    On Error Resume Next

    With ws
        ' Title formatting
        .Range("A1:O1").Merge
        .Range("A1").Font.Size = 16
        .Range("A1").Font.Bold = True
        .Range("A1").HorizontalAlignment = xlCenter

        ' Metadata formatting
        .Range("A2:A3").Font.Bold = True

        ' Header formatting
        .Range("A5:O5").Interior.Color = DataTypes.COLOR_HEADER_BLUE
        .Range("A5:O5").Font.Color = DataTypes.COLOR_WHITE
        .Range("A5:O5").Font.Bold = True

        ' Column widths
        .Columns("A:A").ColumnWidth = 40 ' File Path
        .Columns("B:D").ColumnWidth = 15 ' Module, Case, Version
        .Columns("E:H").ColumnWidth = 25 ' Description fields
        .Columns("I:L").ColumnWidth = 12 ' People and dates
        .Columns("M:O").ColumnWidth = 10 ' Coverage numbers

        ' Text wrapping for description columns
        .Columns("E:H").WrapText = True

        ' Date formatting
        If dataRows > 0 Then
            .Range("J6:J" & (5 + dataRows)).NumberFormat = "yyyy-mm-dd"
            .Range("L6:L" & (5 + dataRows)).NumberFormat = "yyyy-mm-dd"
            .Range("M6:M" & (5 + dataRows)).NumberFormat = "0.00%"
        End If

        ' Add borders
        If dataRows > 0 Then
            .Range("A5:O" & (5 + dataRows)).Borders.LineStyle = xlContinuous
        End If
    End With
End Sub

' Create the Summary sheet
Private Sub CreateSummarySheet(wb As Workbook, testCaseData As Collection, coverageData As Collection)
    On Error GoTo ErrorHandler

    Dim ws As Worksheet
    Set ws = wb.Worksheets.Add
    ws.Name = "Summary"

    ' Create summary statistics
    CreateSummaryStatistics ws, testCaseData, coverageData

    ' Create module breakdown
    CreateModuleBreakdown ws, testCaseData

    ' Apply formatting
    FormatSummarySheet ws

    Exit Sub

ErrorHandler:
    MainController.g_ProcessingErrors.Add "ExcelSheetBuilder.CreateSummarySheet: " & Err.Description
End Sub

' Create summary statistics section
Private Sub CreateSummaryStatistics(ws As Worksheet, testCaseData As Collection, coverageData As Collection)
    On Error Resume Next

    Dim summary As SummaryStats
    summary = CalculateSummaryStatistics(testCaseData, coverageData)

    With ws
        ' Title
        .Cells(1, 1).Value = "Test Summary Report"

        ' Basic statistics
        .Cells(3, 1).Value = "Total Test Files:"
        .Cells(3, 2).Value = MainController.g_TotalFilesProcessed
        .Cells(4, 1).Value = "Total Test Cases:"
        .Cells(4, 2).Value = testCaseData.Count
        .Cells(5, 1).Value = "Total Test Methods:"
        .Cells(5, 2).Value = CountTestMethods(testCaseData)

        ' Coverage statistics
        .Cells(7, 1).Value = "Coverage Statistics"
        .Cells(8, 1).Value = "Overall Branch Coverage:"
        .Cells(8, 2).Value = summary.OverallBranchCoverage / 100 ' Convert to percentage
        .Cells(9, 1).Value = "Branches Covered:"
        .Cells(9, 2).Value = summary.TotalBranchesCovered
        .Cells(10, 1).Value = "Total Branches:"
        .Cells(10, 2).Value = summary.TotalBranches
        .Cells(11, 1).Value = "Missing Coverage:"
        .Cells(11, 2).Value = summary.TotalBranches - summary.TotalBranchesCovered

        ' Processing information
        .Cells(13, 1).Value = "Processing Information"
        .Cells(14, 1).Value = "Processing Time:"
        .Cells(14, 2).Value = Format(Now - MainController.g_ProcessingStartTime, "hh:mm:ss")
        .Cells(15, 1).Value = "Coverage Reports Found:"
        .Cells(15, 2).Value = MainController.g_TotalCoverageReportsFound
    End With
End Sub

' Create module coverage breakdown
Private Sub CreateModuleBreakdown(ws As Worksheet, testCaseData As Collection)
    On Error Resume Next

    With ws
        ' Section title
        .Cells(17, 1).Value = "Module Coverage Breakdown"

        ' Headers
        .Cells(18, 1).Value = "Module Name"
        .Cells(18, 2).Value = "Test Cases"
        .Cells(18, 3).Value = "Coverage %"
        .Cells(18, 4).Value = "Status"

        ' Get module statistics
        Dim moduleStats As Collection
        Set moduleStats = CalculateModuleStatistics(testCaseData)

        ' Populate module data
        Dim i As Long
        Dim moduleData As ModuleCoverageStats
        For i = 1 To moduleStats.Count
            moduleData = moduleStats(i)
            .Cells(18 + i, 1).Value = moduleData.ModuleName
            .Cells(18 + i, 2).Value = moduleData.TestCaseCount
            .Cells(18 + i, 3).Value = moduleData.BranchCoverage / 100 ' Convert to percentage
            .Cells(18 + i, 4).Value = moduleData.Status
        Next i
    End With
End Sub

' Format the Summary sheet
Private Sub FormatSummarySheet(ws As Worksheet)
    On Error Resume Next

    With ws
        ' Title formatting
        .Range("A1").Font.Size = 16
        .Range("A1").Font.Bold = True

        ' Section headers
        .Range("A7").Font.Size = 14
        .Range("A7").Font.Bold = True
        .Range("A13").Font.Size = 14
        .Range("A13").Font.Bold = True
        .Range("A17").Font.Size = 14
        .Range("A17").Font.Bold = True

        ' Labels in bold
        .Range("A3:A5,A8:A11,A14:A15").Font.Bold = True

        ' Module breakdown headers
        .Range("A18:D18").Interior.Color = DataTypes.COLOR_LIGHT_BLUE
        .Range("A18:D18").Font.Bold = True

        ' Percentage formatting
        .Range("B8").NumberFormat = "0.00%"

        ' Column widths
        .Columns("A:A").ColumnWidth = 25
        .Columns("B:D").ColumnWidth = 15
    End With
End Sub

' Create the Coverage sheet
Private Sub CreateCoverageSheet(wb As Workbook, coverageData As Collection)
    On Error GoTo ErrorHandler

    Dim ws As Worksheet
    Set ws = wb.Worksheets.Add
    ws.Name = "Coverage"

    ' Create headers
    CreateCoverageHeaders ws

    ' Populate coverage data
    PopulateCoverageData ws, coverageData

    ' Apply formatting
    FormatCoverageSheet ws, coverageData.Count

    Exit Sub

ErrorHandler:
    MainController.g_ProcessingErrors.Add "ExcelSheetBuilder.CreateCoverageSheet: " & Err.Description
End Sub

' Create headers for Coverage sheet
Private Sub CreateCoverageHeaders(ws As Worksheet)
    On Error Resume Next

    With ws
        .Cells(1, 1).Value = "Coverage Analysis Report"
        .Cells(3, 1).Value = "File Path"
        .Cells(3, 2).Value = "Method Name"
        .Cells(3, 3).Value = "Instructions Covered"
        .Cells(3, 4).Value = "Instructions Missed"
        .Cells(3, 5).Value = "Branches Covered"
        .Cells(3, 6).Value = "Branches Missed"
        .Cells(3, 7).Value = "C1 Coverage %"
        .Cells(3, 8).Value = "Coverage Status"
    End With
End Sub

' Populate Coverage sheet data
Private Sub PopulateCoverageData(ws As Worksheet, coverageData As Collection)
    On Error Resume Next

    Dim i As Long
    Dim coverage As CoverageInfo
    Dim row As Long

    For i = 1 To coverageData.Count
        coverage = coverageData(i)
        row = 3 + i ' Start after header row

        With ws
            .Cells(row, 1).Value = coverage.SourceFile
            .Cells(row, 2).Value = coverage.MethodName
            .Cells(row, 3).Value = coverage.InstructionsCovered
            .Cells(row, 4).Value = coverage.InstructionsMissed
            .Cells(row, 5).Value = coverage.BranchesCovered
            .Cells(row, 6).Value = coverage.BranchesMissed
            .Cells(row, 7).Value = coverage.BranchCoverage / 100 ' Convert to percentage
            .Cells(row, 8).Value = GetCoverageStatus(coverage.BranchCoverage)
        Next i
    End With
End Sub

' Format the Coverage sheet
Private Sub FormatCoverageSheet(ws As Worksheet, dataRows As Long)
    On Error Resume Next

    With ws
        ' Title formatting
        .Range("A1").Font.Size = 16
        .Range("A1").Font.Bold = True

        ' Header formatting
        .Range("A3:H3").Interior.Color = DataTypes.COLOR_HEADER_GREEN
        .Range("A3:H3").Font.Bold = True

        ' Column widths
        .Columns("A:A").ColumnWidth = 30 ' File Path
        .Columns("B:B").ColumnWidth = 20 ' Method Name
        .Columns("C:H").ColumnWidth = 15 ' Numbers and status

        ' Percentage formatting
        If dataRows > 0 Then
            .Range("G4:G" & (3 + dataRows)).NumberFormat = "0.00%"
        End If

        ' Add borders
        If dataRows > 0 Then
            .Range("A3:H" & (3 + dataRows)).Borders.LineStyle = xlContinuous
        End If
    End With
End Sub

' Create the Configuration sheet
Private Sub CreateConfigurationSheet(wb As Workbook)
    On Error GoTo ErrorHandler

    Dim ws As Worksheet
    Set ws = wb.Worksheets.Add
    ws.Name = "Configuration"

    CreateConfigurationContent ws
    FormatConfigurationSheet ws

    Exit Sub

ErrorHandler:
    MainController.g_ProcessingErrors.Add "ExcelSheetBuilder.CreateConfigurationSheet: " & Err.Description
End Sub

' Create Configuration sheet content
Private Sub CreateConfigurationContent(ws As Worksheet)
    On Error Resume Next

    With ws
        ' Title
        .Cells(1, 1).Value = "Processing Configuration"

        ' Headers
        .Cells(3, 1).Value = "Configuration Parameter"
        .Cells(3, 2).Value = "Value"
        .Cells(3, 3).Value = "Description"

        ' Configuration data
        .Cells(4, 1).Value = "Source Directory"
        .Cells(4, 2).Value = MainController.g_SourceDirectory
        .Cells(4, 3).Value = "Directory containing Java test files"

        .Cells(5, 1).Value = "Output File"
        .Cells(5, 2).Value = MainController.g_OutputFile
        .Cells(5, 3).Value = "Generated Excel report location"

        .Cells(6, 1).Value = "Processing Date"
        .Cells(6, 2).Value = Format(Now, "yyyy-mm-dd hh:mm:ss")
        .Cells(6, 3).Value = "When the report was generated"

        .Cells(7, 1).Value = "Files Processed"
        .Cells(7, 2).Value = MainController.g_TotalFilesProcessed
        .Cells(7, 3).Value = "Total number of Java files analyzed"

        .Cells(8, 1).Value = "Test Cases Found"
        .Cells(8, 2).Value = MainController.g_TotalTestCasesFound
        .Cells(8, 3).Value = "Total number of test cases extracted"

        .Cells(9, 1).Value = "Coverage Reports Found"
        .Cells(9, 2).Value = MainController.g_TotalCoverageReportsFound
        .Cells(9, 3).Value = "Number of JaCoCo reports processed"

        .Cells(10, 1).Value = "Processing Duration"
        .Cells(10, 2).Value = Format(Now - MainController.g_ProcessingStartTime, "hh:mm:ss")
        .Cells(10, 3).Value = "Time taken to generate this report"

        .Cells(11, 1).Value = "Application Version"
        .Cells(11, 2).Value = MainController.APP_VERSION
        .Cells(11, 3).Value = "Version of the VBA application used"
    End With
End Sub

' Format the Configuration sheet
Private Sub FormatConfigurationSheet(ws As Worksheet)
    On Error Resume Next

    With ws
        ' Title formatting
        .Range("A1").Font.Size = 16
        .Range("A1").Font.Bold = True

        ' Header formatting
        .Range("A3:C3").Interior.Color = DataTypes.COLOR_HEADER_YELLOW
        .Range("A3:C3").Font.Bold = True

        ' Labels in bold
        .Range("A4:A11").Font.Bold = True

        ' Column widths
        .Columns("A:A").ColumnWidth = 25 ' Parameter
        .Columns("B:B").ColumnWidth = 40 ' Value
        .Columns("C:C").ColumnWidth = 35 ' Description

        ' Add borders
        .Range("A3:C11").Borders.LineStyle = xlContinuous
    End With
End Sub

' Remove default Excel sheets
Private Sub RemoveDefaultSheets(wb As Workbook)
    On Error Resume Next

    Application.DisplayAlerts = False

    Dim ws As Worksheet
    For Each ws In wb.Worksheets
        If ws.Name Like "Sheet*" Then
            ws.Delete
        End If
    Next ws

    Application.DisplayAlerts = True
End Sub

' Utility functions
Private Function CalculateSummaryStatistics(testCaseData As Collection, coverageData As Collection) As SummaryStats
    Dim summary As SummaryStats

    summary.TotalTestMethods = testCaseData.Count
    summary.TotalBranches = 0
    summary.TotalBranchesCovered = 0

    Dim i As Long
    Dim testCase As TestCaseInfo

    For i = 1 To testCaseData.Count
        testCase = testCaseData(i)
        summary.TotalBranches = summary.TotalBranches + testCase.BranchesTotal
        summary.TotalBranchesCovered = summary.TotalBranchesCovered + testCase.BranchesCovered
    Next i

    If summary.TotalBranches > 0 Then
        summary.OverallBranchCoverage = (summary.TotalBranchesCovered / summary.TotalBranches) * 100
    End If

    CalculateSummaryStatistics = summary
End Function

Private Function CountTestMethods(testCaseData As Collection) As Long
    Dim count As Long
    Dim i As Long
    Dim testCase As TestCaseInfo

    For i = 1 To testCaseData.Count
        testCase = testCaseData(i)
        If Len(testCase.MethodName) > 0 Then
            count = count + 1
        End If
    Next i

    CountTestMethods = count
End Function

Private Function CalculateModuleStatistics(testCaseData As Collection) As Collection
    Set CalculateModuleStatistics = New Collection

    ' This would group by module and calculate statistics
    ' Simplified implementation for now
    Dim moduleData As ModuleCoverageStats
    moduleData.ModuleName = "All Modules"
    moduleData.TestCaseCount = testCaseData.Count
    moduleData.BranchCoverage = 95 ' Placeholder
    moduleData.Status = DataTypes.COVERAGE_EXCELLENT

    CalculateModuleStatistics.Add moduleData
End Function

Private Function GetCoverageStatus(coveragePercent As Double) As String
    If coveragePercent >= 90 Then
        GetCoverageStatus = DataTypes.COVERAGE_EXCELLENT
    ElseIf coveragePercent >= 70 Then
        GetCoverageStatus = DataTypes.COVERAGE_GOOD
    ElseIf coveragePercent >= 50 Then
        GetCoverageStatus = DataTypes.COVERAGE_FAIR
    Else
        GetCoverageStatus = DataTypes.COVERAGE_POOR
    End If
End Function