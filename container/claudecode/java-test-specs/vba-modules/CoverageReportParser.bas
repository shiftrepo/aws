Attribute VB_Name = "CoverageReportParser"
' ============================================================================
' CoverageReportParser.bas
' JaCoCo coverage report parsing module for Test Specification Generator
'
' This module handles parsing of JaCoCo coverage reports to extract:
' 1. Branch coverage information (C1 coverage)
' 2. Instruction coverage metrics
' 3. Line coverage statistics
' 4. Method-level coverage details
'
' Supported formats: JaCoCo XML reports, JaCoCo HTML reports (basic)
'
' Created: 2026-01-07
' Version: 1.0.0
' ============================================================================

Option Explicit

' Constants for coverage report parsing
Private Const JACOCO_XML_ROOT As String = "<report"
Private Const JACOCO_PACKAGE As String = "<package"
Private Const JACOCO_CLASS As String = "<class"
Private Const JACOCO_METHOD As String = "<method"
Private Const JACOCO_COUNTER As String = "<counter"

' Process all coverage report files
Public Function ProcessCoverageReports(coverageFiles As Collection) As Collection
    On Error GoTo ErrorHandler

    Set ProcessCoverageReports = New Collection

    If coverageFiles.Count = 0 Then
        Exit Function
    End If

    Dim i As Long
    Dim filePath As String
    Dim coverageData As Collection

    ' Process each coverage report file
    For i = 1 To coverageFiles.Count
        filePath = coverageFiles(i)

        ' Update progress
        MainController.UpdateProgress "Processing coverage report " & FolderScanner.GetFileNameFromPath(filePath), _
                                    60 + Int((i / coverageFiles.Count) * 10)

        ' Determine report type and parse accordingly
        If LCase(Right(filePath, 4)) = ".xml" Then
            Set coverageData = ParseJaCoCoXMLReport(filePath)
        ElseIf LCase(Right(filePath, 5)) = ".html" Then
            Set coverageData = ParseJaCoCoHTMLReport(filePath)
        Else
            MainController.g_ProcessingErrors.Add "Unsupported coverage report format: " & filePath
            GoTo NextFile
        End If

        ' Add coverage data to main collection
        Dim j As Long
        For j = 1 To coverageData.Count
            ProcessCoverageReports.Add coverageData(j)
        Next j

NextFile:
    Next i

    Exit Function

ErrorHandler:
    If ProcessCoverageReports Is Nothing Then Set ProcessCoverageReports = New Collection
    MainController.g_ProcessingErrors.Add "CoverageReportParser.ProcessCoverageReports: " & Err.Description
End Function

' Parse JaCoCo XML report file
Private Function ParseJaCoCoXMLReport(filePath As String) As Collection
    On Error GoTo ErrorHandler

    Set ParseJaCoCoXMLReport = New Collection

    ' Read XML file content
    Dim xmlContent As String
    xmlContent = ReadFileContent(filePath)

    If Len(xmlContent) = 0 Then
        Exit Function
    End If

    ' Validate that this is a JaCoCo XML report
    If InStr(1, xmlContent, JACOCO_XML_ROOT, vbTextCompare) = 0 Then
        MainController.g_ProcessingErrors.Add "Not a valid JaCoCo XML report: " & filePath
        Exit Function
    End If

    ' Parse packages and classes
    ParseXMLPackages xmlContent, filePath, ParseJaCoCoXMLReport

    Exit Function

ErrorHandler:
    If ParseJaCoCoXMLReport Is Nothing Then Set ParseJaCoCoXMLReport = New Collection
    MainController.g_ProcessingErrors.Add "CoverageReportParser.ParseJaCoCoXMLReport: " & Err.Description & " (File: " & filePath & ")"
End Function

' Parse packages from XML content
Private Sub ParseXMLPackages(xmlContent As String, reportFile As String, coverageCollection As Collection)
    On Error GoTo ErrorHandler

    Dim packageStart As Long
    Dim packageEnd As Long
    Dim searchPos As Long
    Dim packageContent As String
    Dim packageName As String

    searchPos = 1

    ' Find all package elements
    Do
        packageStart = InStr(searchPos, xmlContent, JACOCO_PACKAGE, vbTextCompare)
        If packageStart > 0 Then
            ' Find the end of this package element
            packageEnd = InStr(packageStart, xmlContent, "</package>", vbTextCompare)
            If packageEnd > 0 Then
                packageEnd = packageEnd + 10 ' Include </package>
                packageContent = Mid(xmlContent, packageStart, packageEnd - packageStart)
                packageName = ExtractAttributeValue(packageContent, "name")

                ' Parse classes within this package
                ParseXMLClasses packageContent, packageName, reportFile, coverageCollection

                searchPos = packageEnd
            Else
                Exit Do
            End If
        Else
            Exit Do
        End If
    Loop

    Exit Sub

ErrorHandler:
    MainController.g_ProcessingErrors.Add "CoverageReportParser.ParseXMLPackages: " & Err.Description
End Sub

' Parse classes from XML package content
Private Sub ParseXMLClasses(packageContent As String, packageName As String, reportFile As String, coverageCollection As Collection)
    On Error GoTo ErrorHandler

    Dim classStart As Long
    Dim classEnd As Long
    Dim searchPos As Long
    Dim classContent As String
    Dim className As String
    Dim sourceFile As String

    searchPos = 1

    ' Find all class elements
    Do
        classStart = InStr(searchPos, packageContent, JACOCO_CLASS, vbTextCompare)
        If classStart > 0 Then
            ' Find the end of this class element
            classEnd = InStr(classStart, packageContent, "</class>", vbTextCompare)
            If classEnd > 0 Then
                classEnd = classEnd + 8 ' Include </class>
                classContent = Mid(packageContent, classStart, classEnd - classStart)
                className = ExtractAttributeValue(classContent, "name")
                sourceFile = ExtractAttributeValue(classContent, "sourcefilename")

                ' Parse methods and create coverage records
                ParseXMLMethods classContent, packageName, className, sourceFile, reportFile, coverageCollection

                searchPos = classEnd
            Else
                Exit Do
            End If
        Else
            Exit Do
        End If
    Loop

    Exit Sub

ErrorHandler:
    MainController.g_ProcessingErrors.Add "CoverageReportParser.ParseXMLClasses: " & Err.Description
End Sub

' Parse methods from XML class content
Private Sub ParseXMLMethods(classContent As String, packageName As String, className As String, _
                           sourceFile As String, reportFile As String, coverageCollection As Collection)
    On Error GoTo ErrorHandler

    Dim methodStart As Long
    Dim methodEnd As Long
    Dim searchPos As Long
    Dim methodContent As String
    Dim methodName As String
    Dim lineNumber As String

    searchPos = 1

    ' Find all method elements
    Do
        methodStart = InStr(searchPos, classContent, JACOCO_METHOD, vbTextCompare)
        If methodStart > 0 Then
            ' Find the end of this method element
            methodEnd = InStr(methodStart, classContent, "</method>", vbTextCompare)
            If methodEnd > 0 Then
                methodEnd = methodEnd + 9 ' Include </method>
                methodContent = Mid(classContent, methodStart, methodEnd - methodStart)
                methodName = ExtractAttributeValue(methodContent, "name")
                lineNumber = ExtractAttributeValue(methodContent, "line")

                ' Create coverage record for this method
                Dim coverageInfo As CoverageInfo
                coverageInfo = CreateCoverageRecordFromMethod(methodContent, packageName, className, _
                                                            methodName, sourceFile, lineNumber, reportFile)

                If coverageInfo.IsValid Then
                    coverageCollection.Add coverageInfo
                End If

                searchPos = methodEnd
            Else
                Exit Do
            End If
        Else
            Exit Do
        End If
    Loop

    ' Also create class-level coverage record
    Dim classCoverage As CoverageInfo
    classCoverage = CreateCoverageRecordFromClass(classContent, packageName, className, sourceFile, reportFile)
    If classCoverage.IsValid Then
        coverageCollection.Add classCoverage
    End If

    Exit Sub

ErrorHandler:
    MainController.g_ProcessingErrors.Add "CoverageReportParser.ParseXMLMethods: " & Err.Description
End Sub

' Create coverage record from method XML content
Private Function CreateCoverageRecordFromMethod(methodContent As String, packageName As String, _
                                              className As String, methodName As String, _
                                              sourceFile As String, lineNumber As String, _
                                              reportFile As String) As CoverageInfo
    On Error GoTo ErrorHandler

    Dim coverage As CoverageInfo
    coverage = DataTypes.CreateCoverageInfo()

    ' Set basic information
    coverage.SourceFile = sourceFile
    coverage.ClassName = packageName & "/" & className
    coverage.MethodName = methodName
    coverage.LineNumber = CLng(Val(lineNumber))
    coverage.ReportFile = reportFile
    coverage.ReportType = REPORT_FORMAT_XML

    ' Parse counter elements for this method
    ParseCounterElements methodContent, coverage

    ' Calculate coverage percentages
    CalculateCoveragePercentages coverage

    coverage.IsValid = True
    CreateCoverageRecordFromMethod = coverage

    Exit Function

ErrorHandler:
    coverage.IsValid = False
    coverage.ErrorMessage = Err.Description
    CreateCoverageRecordFromMethod = coverage
End Function

' Create coverage record from class XML content
Private Function CreateCoverageRecordFromClass(classContent As String, packageName As String, _
                                             className As String, sourceFile As String, _
                                             reportFile As String) As CoverageInfo
    On Error GoTo ErrorHandler

    Dim coverage As CoverageInfo
    coverage = DataTypes.CreateCoverageInfo()

    ' Set basic information
    coverage.SourceFile = sourceFile
    coverage.ClassName = packageName & "/" & className
    coverage.MethodName = "[Class Total]"
    coverage.LineNumber = 0
    coverage.ReportFile = reportFile
    coverage.ReportType = REPORT_FORMAT_XML

    ' Parse counter elements for this class
    ParseCounterElements classContent, coverage

    ' Calculate coverage percentages
    CalculateCoveragePercentages coverage

    coverage.IsValid = True
    CreateCoverageRecordFromClass = coverage

    Exit Function

ErrorHandler:
    coverage.IsValid = False
    coverage.ErrorMessage = Err.Description
    CreateCoverageRecordFromClass = coverage
End Function

' Parse counter elements from XML content
Private Sub ParseCounterElements(xmlContent As String, ByRef coverage As CoverageInfo)
    On Error Resume Next

    Dim counterStart As Long
    Dim counterEnd As Long
    Dim searchPos As Long
    Dim counterElement As String
    Dim counterType As String
    Dim missedCount As String
    Dim coveredCount As String

    searchPos = 1

    ' Find all counter elements
    Do
        counterStart = InStr(searchPos, xmlContent, JACOCO_COUNTER, vbTextCompare)
        If counterStart > 0 Then
            counterEnd = InStr(counterStart, xmlContent, "/>", vbTextCompare)
            If counterEnd > 0 Then
                counterEnd = counterEnd + 2
                counterElement = Mid(xmlContent, counterStart, counterEnd - counterStart)

                ' Extract counter type and values
                counterType = ExtractAttributeValue(counterElement, "type")
                missedCount = ExtractAttributeValue(counterElement, "missed")
                coveredCount = ExtractAttributeValue(counterElement, "covered")

                ' Apply values based on counter type
                Select Case UCase(counterType)
                    Case "INSTRUCTION"
                        coverage.InstructionsMissed = CLng(Val(missedCount))
                        coverage.InstructionsCovered = CLng(Val(coveredCount))
                        coverage.InstructionsTotal = coverage.InstructionsMissed + coverage.InstructionsCovered
                    Case "BRANCH"
                        coverage.BranchesMissed = CLng(Val(missedCount))
                        coverage.BranchesCovered = CLng(Val(coveredCount))
                        coverage.BranchesTotal = coverage.BranchesMissed + coverage.BranchesCovered
                    Case "LINE"
                        coverage.LinesMissed = CLng(Val(missedCount))
                        coverage.LinesCovered = CLng(Val(coveredCount))
                        coverage.LinesTotal = coverage.LinesMissed + coverage.LinesCovered
                    Case "COMPLEXITY"
                        coverage.ComplexityMissed = CLng(Val(missedCount))
                        coverage.ComplexityCovered = CLng(Val(coveredCount))
                        coverage.ComplexityTotal = coverage.ComplexityMissed + coverage.ComplexityCovered
                End Select

                searchPos = counterEnd
            Else
                Exit Do
            End If
        Else
            Exit Do
        End If
    Loop
End Sub

' Calculate coverage percentages
Private Sub CalculateCoveragePercentages(ByRef coverage As CoverageInfo)
    On Error Resume Next

    ' Calculate branch coverage (C1 coverage)
    If coverage.BranchesTotal > 0 Then
        coverage.BranchCoverage = (coverage.BranchesCovered / coverage.BranchesTotal) * 100
    Else
        coverage.BranchCoverage = 0
    End If

    ' Round to 2 decimal places
    coverage.BranchCoverage = Round(coverage.BranchCoverage, 2)
End Sub

' Parse JaCoCo HTML report (basic implementation)
Private Function ParseJaCoCoHTMLReport(filePath As String) As Collection
    On Error GoTo ErrorHandler

    Set ParseJaCoCoHTMLReport = New Collection

    ' For now, HTML parsing is simplified
    ' In a full implementation, this would parse the HTML tables
    MainController.g_ProcessingErrors.Add "HTML coverage report parsing not yet implemented: " & filePath

    Exit Function

ErrorHandler:
    If ParseJaCoCoHTMLReport Is Nothing Then Set ParseJaCoCoHTMLReport = New Collection
    MainController.g_ProcessingErrors.Add "CoverageReportParser.ParseJaCoCoHTMLReport: " & Err.Description
End Function

' Utility function to read file content
Private Function ReadFileContent(filePath As String) As String
    On Error GoTo ErrorHandler

    Dim fileNum As Integer
    Dim fileContent As String

    fileNum = FreeFile
    Open filePath For Input As #fileNum
    fileContent = Input(LOF(fileNum), fileNum)
    Close #fileNum

    ReadFileContent = fileContent

    Exit Function

ErrorHandler:
    If fileNum > 0 Then Close #fileNum
    ReadFileContent = ""
    MainController.g_ProcessingErrors.Add "CoverageReportParser.ReadFileContent: " & Err.Description & " (File: " & filePath & ")"
End Function

' Extract attribute value from XML element
Private Function ExtractAttributeValue(xmlElement As String, attributeName As String) As String
    On Error Resume Next

    Dim attrPattern As String
    Dim attrStart As Long
    Dim attrEnd As Long
    Dim quoteStart As Long
    Dim quoteEnd As Long

    attrPattern = attributeName & "="""
    attrStart = InStr(1, xmlElement, attrPattern, vbTextCompare)

    If attrStart > 0 Then
        quoteStart = attrStart + Len(attrPattern)
        quoteEnd = InStr(quoteStart, xmlElement, """")

        If quoteEnd > quoteStart Then
            ExtractAttributeValue = Mid(xmlElement, quoteStart, quoteEnd - quoteStart)
        End If
    End If
End Function

' Get coverage summary statistics
Public Function GetCoverageSummary(coverageData As Collection) As SummaryStats
    On Error GoTo ErrorHandler

    Dim summary As SummaryStats

    ' Initialize summary
    summary.TotalCoverageReports = coverageData.Count
    summary.TotalBranchesCovered = 0
    summary.TotalBranches = 0
    summary.OverallBranchCoverage = 0

    If coverageData.Count = 0 Then
        GetCoverageSummary = summary
        Exit Function
    End If

    ' Calculate totals
    Dim i As Long
    Dim coverage As CoverageInfo

    For i = 1 To coverageData.Count
        coverage = coverageData(i)
        summary.TotalBranchesCovered = summary.TotalBranchesCovered + coverage.BranchesCovered
        summary.TotalBranches = summary.TotalBranches + coverage.BranchesTotal
    Next i

    ' Calculate overall percentage
    If summary.TotalBranches > 0 Then
        summary.OverallBranchCoverage = (summary.TotalBranchesCovered / summary.TotalBranches) * 100
        summary.OverallBranchCoverage = Round(summary.OverallBranchCoverage, 2)
    End If

    GetCoverageSummary = summary

    Exit Function

ErrorHandler:
    MainController.g_ProcessingErrors.Add "CoverageReportParser.GetCoverageSummary: " & Err.Description
    GetCoverageSummary = summary
End Function