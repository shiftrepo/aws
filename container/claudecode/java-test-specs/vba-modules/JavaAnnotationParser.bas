Attribute VB_Name = "JavaAnnotationParser"
' ============================================================================
' JavaAnnotationParser.bas
' Java annotation parsing module for Test Specification Generator
'
' This module handles parsing of custom annotations from Java test files:
' 1. Read Java files and extract JavaDoc comment blocks
' 2. Parse custom annotations (@TestModule, @TestCase, etc.)
' 3. Handle both class-level and method-level annotations
' 4. Merge annotation data with file metadata
'
' Created: 2026-01-07
' Version: 1.0.0
' ============================================================================

Option Explicit

' Constants for annotation processing
Private Const MAX_FILE_SIZE As Long = 10485760 ' 10MB maximum file size
Private Const JAVADOC_START As String = "/**"
Private Const JAVADOC_END As String = "*/"
Private Const ANNOTATION_PREFIX As String = "@"

' Process all Java files and extract test case information
Public Function ProcessJavaFiles(javaFiles As Collection) As Collection
    On Error GoTo ErrorHandler

    Set ProcessJavaFiles = New Collection

    Dim i As Long
    Dim filePath As String
    Dim fileTestCases As Collection

    ' Process each Java file
    For i = 1 To javaFiles.Count
        filePath = javaFiles(i)

        ' Update progress
        MainController.UpdateProgress "Processing " & FolderScanner.GetFileNameFromPath(filePath), _
                                    20 + Int((i / javaFiles.Count) * 20)

        ' Extract test cases from this file
        Set fileTestCases = ExtractTestCasesFromFile(filePath)

        ' Add all test cases from this file to the main collection
        Dim j As Long
        For j = 1 To fileTestCases.Count
            ProcessJavaFiles.Add fileTestCases(j)
        Next j
    Next i

    Exit Function

ErrorHandler:
    If ProcessJavaFiles Is Nothing Then Set ProcessJavaFiles = New Collection
    MainController.g_ProcessingErrors.Add "JavaAnnotationParser.ProcessJavaFiles: " & Err.Description
End Function

' Extract test cases from a single Java file
Private Function ExtractTestCasesFromFile(filePath As String) As Collection
    On Error GoTo ErrorHandler

    Set ExtractTestCasesFromFile = New Collection

    ' Validate file
    If Not FolderScanner.FileExists(filePath) Then
        Exit Function
    End If

    Dim fileInfo As FileInfo
    fileInfo = FolderScanner.GetFileInfo(filePath)

    If Not fileInfo.IsValid Then
        MainController.g_ProcessingErrors.Add "Cannot access file: " & filePath & " - " & fileInfo.ErrorMessage
        Exit Function
    End If

    ' Check file size limit
    If fileInfo.FileSize > MAX_FILE_SIZE Then
        MainController.g_ProcessingErrors.Add "File too large, skipping: " & filePath & " (" & fileInfo.FileSize & " bytes)"
        Exit Function
    End If

    ' Read file content
    Dim fileContent As String
    fileContent = ReadFileContent(filePath)

    If Len(fileContent) = 0 Then
        Exit Function
    End If

    ' Extract class and method annotations
    Dim classAnnotations As Collection
    Dim methodAnnotations As Collection

    Set classAnnotations = ExtractClassAnnotations(fileContent)
    Set methodAnnotations = ExtractMethodAnnotations(fileContent)

    ' Create test case records
    CreateTestCaseRecords filePath, fileInfo, classAnnotations, methodAnnotations, ExtractTestCasesFromFile

    Exit Function

ErrorHandler:
    If ExtractTestCasesFromFile Is Nothing Then Set ExtractTestCasesFromFile = New Collection
    MainController.g_ProcessingErrors.Add "JavaAnnotationParser.ExtractTestCasesFromFile: " & Err.Description & " (File: " & filePath & ")"
End Function

' Read file content into string
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
    MainController.g_ProcessingErrors.Add "JavaAnnotationParser.ReadFileContent: " & Err.Description & " (File: " & filePath & ")"
End Function

' Extract class-level annotations from file content
Private Function ExtractClassAnnotations(fileContent As String) As Collection
    On Error GoTo ErrorHandler

    Set ExtractClassAnnotations = New Collection

    ' Find class declaration and preceding JavaDoc block
    Dim classPattern As String
    classPattern = "public\s+class\s+\w+"

    Dim classPos As Long
    classPos = FindRegexMatch(fileContent, classPattern)

    If classPos > 0 Then
        ' Look for JavaDoc block before class declaration
        Dim javadocBlock As String
        javadocBlock = FindPrecedingJavaDocBlock(fileContent, classPos)

        If Len(javadocBlock) > 0 Then
            ' Parse annotations from JavaDoc block
            ParseAnnotationsFromBlock javadocBlock, ExtractClassAnnotations
        End If
    End If

    Exit Function

ErrorHandler:
    If ExtractClassAnnotations Is Nothing Then Set ExtractClassAnnotations = New Collection
    MainController.g_ProcessingErrors.Add "JavaAnnotationParser.ExtractClassAnnotations: " & Err.Description
End Function

' Extract method-level annotations from file content
Private Function ExtractMethodAnnotations(fileContent As String) As Collection
    On Error GoTo ErrorHandler

    Set ExtractMethodAnnotations = New Collection

    ' Find all test method declarations
    Dim methodPattern As String
    methodPattern = "@Test|@ParameterizedTest"

    Dim searchPos As Long
    Dim methodPos As Long
    searchPos = 1

    Do
        methodPos = FindRegexMatch(Mid(fileContent, searchPos), methodPattern)
        If methodPos > 0 Then
            methodPos = methodPos + searchPos - 1

            ' Find the actual method declaration after the @Test annotation
            Dim methodDeclaration As String
            Dim methodName As String
            methodDeclaration = FindMethodDeclarationAfterAnnotation(fileContent, methodPos)
            methodName = ExtractMethodName(methodDeclaration)

            If Len(methodName) > 0 Then
                ' Look for JavaDoc block before the method
                Dim javadocBlock As String
                javadocBlock = FindPrecedingJavaDocBlock(fileContent, methodPos)

                If Len(javadocBlock) > 0 Then
                    ' Create method annotation record
                    Dim methodRecord As MethodAnnotationRecord
                    methodRecord.MethodName = methodName
                    methodRecord.Annotations = New Collection
                    ParseAnnotationsFromBlock javadocBlock, methodRecord.Annotations

                    ExtractMethodAnnotations.Add methodRecord
                End If
            End If

            searchPos = methodPos + 10 ' Move past this match
        End If
    Loop While methodPos > 0 And searchPos < Len(fileContent)

    Exit Function

ErrorHandler:
    If ExtractMethodAnnotations Is Nothing Then Set ExtractMethodAnnotations = New Collection
    MainController.g_ProcessingErrors.Add "JavaAnnotationParser.ExtractMethodAnnotations: " & Err.Description
End Function

' Find JavaDoc comment block preceding a position in the file
Private Function FindPrecedingJavaDocBlock(fileContent As String, position As Long) As String
    On Error GoTo ErrorHandler

    FindPrecedingJavaDocBlock = ""

    Dim searchText As String
    searchText = Left(fileContent, position - 1)

    ' Find the last occurrence of /** before the position
    Dim startPos As Long
    startPos = InStrRev(searchText, JAVADOC_START)

    If startPos > 0 Then
        ' Find the corresponding */
        Dim endPos As Long
        endPos = InStr(startPos, fileContent, JAVADOC_END)

        If endPos > startPos And endPos < position Then
            FindPrecedingJavaDocBlock = Mid(fileContent, startPos, endPos - startPos + 2)
        End If
    End If

    Exit Function

ErrorHandler:
    FindPrecedingJavaDocBlock = ""
End Function

' Parse annotations from a JavaDoc comment block
Private Sub ParseAnnotationsFromBlock(javadocBlock As String, annotations As Collection)
    On Error GoTo ErrorHandler

    Dim lines() As String
    lines = Split(javadocBlock, vbCrLf)

    Dim i As Long
    Dim line As String
    Dim trimmedLine As String

    For i = 0 To UBound(lines)
        line = lines(i)
        trimmedLine = Trim(line)

        ' Remove comment markers
        If Left(trimmedLine, 1) = "*" Then
            trimmedLine = Trim(Mid(trimmedLine, 2))
        End If

        ' Check if line contains annotation
        If Left(trimmedLine, 1) = ANNOTATION_PREFIX Then
            Dim annotationResult As AnnotationResult
            annotationResult = ParseSingleAnnotation(trimmedLine)

            If annotationResult.IsValid Then
                annotations.Add annotationResult
            End If
        End If
    Next i

    Exit Sub

ErrorHandler:
    MainController.g_ProcessingErrors.Add "JavaAnnotationParser.ParseAnnotationsFromBlock: " & Err.Description
End Sub

' Parse a single annotation line
Private Function ParseSingleAnnotation(annotationLine As String) As AnnotationResult
    On Error GoTo ErrorHandler

    Dim result As AnnotationResult
    result.IsValid = False

    ' Remove leading @ symbol
    If Left(annotationLine, 1) = ANNOTATION_PREFIX Then
        annotationLine = Trim(Mid(annotationLine, 2))
    End If

    ' Find space separator between annotation name and value
    Dim spacePos As Long
    spacePos = InStr(annotationLine, " ")

    If spacePos > 0 Then
        result.AnnotationName = Trim(Left(annotationLine, spacePos - 1))
        result.AnnotationValue = Trim(Mid(annotationLine, spacePos + 1))
    Else
        ' No value specified
        result.AnnotationName = Trim(annotationLine)
        result.AnnotationValue = ""
    End If

    ' Validate annotation name
    If Len(result.AnnotationName) > 0 Then
        result.IsValid = True
    End If

    ParseSingleAnnotation = result

    Exit Function

ErrorHandler:
    result.IsValid = False
    ParseSingleAnnotation = result
End Function

' Create test case records from class and method annotations
Private Sub CreateTestCaseRecords(filePath As String, fileInfo As FileInfo, _
                                 classAnnotations As Collection, methodAnnotations As Collection, _
                                 testCases As Collection)
    On Error GoTo ErrorHandler

    Dim className As String
    className = GetClassNameFromFilePath(filePath)

    ' If no method annotations found, create one record for the class
    If methodAnnotations.Count = 0 Then
        Dim classTestCase As TestCaseInfo
        classTestCase = CreateTestCaseFromAnnotations(filePath, className, "", classAnnotations, Nothing)
        testCases.Add classTestCase
    Else
        ' Create a test case record for each method
        Dim i As Long
        For i = 1 To methodAnnotations.Count
            Dim methodRecord As MethodAnnotationRecord
            methodRecord = methodAnnotations(i)

            Dim methodTestCase As TestCaseInfo
            methodTestCase = CreateTestCaseFromAnnotations(filePath, className, methodRecord.MethodName, _
                                                         classAnnotations, methodRecord.Annotations)
            testCases.Add methodTestCase
        Next i
    End If

    Exit Sub

ErrorHandler:
    MainController.g_ProcessingErrors.Add "JavaAnnotationParser.CreateTestCaseRecords: " & Err.Description
End Sub

' Create a test case info record from annotations
Private Function CreateTestCaseFromAnnotations(filePath As String, className As String, methodName As String, _
                                             classAnnotations As Collection, methodAnnotations As Collection) As TestCaseInfo
    On Error GoTo ErrorHandler

    Dim testCase As TestCaseInfo
    testCase = DataTypes.CreateTestCaseInfo()

    ' Set basic file information
    testCase.FilePath = filePath
    testCase.ClassName = className
    testCase.MethodName = methodName

    ' Apply class-level annotations first
    ApplyAnnotationsToTestCase classAnnotations, testCase

    ' Apply method-level annotations (override class-level)
    If Not methodAnnotations Is Nothing Then
        ApplyAnnotationsToTestCase methodAnnotations, testCase
    End If

    ' Set default values if not specified
    SetDefaultValuesIfMissing testCase

    CreateTestCaseFromAnnotations = testCase

    Exit Function

ErrorHandler:
    testCase.IsValid = False
    testCase.ErrorMessage = Err.Description
    CreateTestCaseFromAnnotations = testCase
End Function

' Apply annotations to test case record
Private Sub ApplyAnnotationsToTestCase(annotations As Collection, ByRef testCase As TestCaseInfo)
    On Error Resume Next

    Dim i As Long
    Dim annotation As AnnotationResult

    For i = 1 To annotations.Count
        annotation = annotations(i)

        Select Case UCase(annotation.AnnotationName)
            Case "TESTMODULE"
                testCase.TestModule = annotation.AnnotationValue
            Case "TESTCASE"
                testCase.TestCase = annotation.AnnotationValue
            Case "BASELINEVERSION"
                testCase.BaselineVersion = annotation.AnnotationValue
            Case "TESTOVERVIEW"
                testCase.TestOverview = annotation.AnnotationValue
            Case "TESTPURPOSE"
                testCase.TestPurpose = annotation.AnnotationValue
            Case "TESTPROCESS"
                testCase.TestProcess = annotation.AnnotationValue
            Case "TESTRESULTS"
                testCase.TestResults = annotation.AnnotationValue
            Case "CREATOR"
                testCase.Creator = annotation.AnnotationValue
            Case "CREATEDDATE"
                testCase.CreatedDate = ParseDateFromString(annotation.AnnotationValue)
            Case "MODIFIER"
                testCase.Modifier = annotation.AnnotationValue
            Case "MODIFIEDDATE"
                testCase.ModifiedDate = ParseDateFromString(annotation.AnnotationValue)
            Case "TESTCATEGORY"
                testCase.TestCategory = annotation.AnnotationValue
            Case "PRIORITY"
                testCase.Priority = annotation.AnnotationValue
            Case "REQUIREMENTS"
                testCase.Requirements = annotation.AnnotationValue
            Case "DEPENDENCIES"
                testCase.Dependencies = annotation.AnnotationValue
        End Select
    Next i
End Sub

' Set default values for missing annotations
Private Sub SetDefaultValuesIfMissing(ByRef testCase As TestCaseInfo)
    If testCase.TestModule = "Not Specified" And Len(testCase.ClassName) > 0 Then
        testCase.TestModule = testCase.ClassName
    End If

    If testCase.TestCase = "Not Specified" And Len(testCase.MethodName) > 0 Then
        testCase.TestCase = testCase.MethodName
    End If

    If testCase.Creator = "Unknown" Then
        testCase.Creator = "Not Specified"
    End If
End Sub

' Utility functions
Private Function GetClassNameFromFilePath(filePath As String) As String
    Dim fileName As String
    fileName = FolderScanner.GetFileNameFromPath(filePath)

    ' Remove .java extension
    If Right(LCase(fileName), 5) = ".java" Then
        GetClassNameFromFilePath = Left(fileName, Len(fileName) - 5)
    Else
        GetClassNameFromFilePath = fileName
    End If
End Function

Private Function ParseDateFromString(dateString As String) As Date
    On Error GoTo ErrorHandler

    If Len(dateString) = 10 And Mid(dateString, 5, 1) = "-" And Mid(dateString, 8, 1) = "-" Then
        ' YYYY-MM-DD format
        ParseDateFromString = DateSerial(CInt(Left(dateString, 4)), _
                                       CInt(Mid(dateString, 6, 2)), _
                                       CInt(Right(dateString, 2)))
    Else
        ParseDateFromString = CDate(dateString)
    End If

    Exit Function

ErrorHandler:
    ParseDateFromString = #1/1/1900#
End Function

Private Function FindRegexMatch(text As String, pattern As String) As Long
    ' Simplified pattern matching (would use RegEx in full implementation)
    FindRegexMatch = InStr(1, text, "@Test", vbTextCompare)
End Function

Private Function FindMethodDeclarationAfterAnnotation(fileContent As String, annotationPos As Long) As String
    ' Find method declaration after @Test annotation
    Dim searchStart As Long
    searchStart = annotationPos

    Dim publicPos As Long
    publicPos = InStr(searchStart, fileContent, "public ")

    If publicPos > 0 Then
        Dim lineEnd As Long
        lineEnd = InStr(publicPos, fileContent, vbCrLf)
        If lineEnd > publicPos Then
            FindMethodDeclarationAfterAnnotation = Mid(fileContent, publicPos, lineEnd - publicPos)
        End If
    End If
End Function

Private Function ExtractMethodName(methodDeclaration As String) As String
    ' Extract method name from declaration like "public void testSomething()"
    Dim words() As String
    words = Split(Trim(methodDeclaration), " ")

    Dim i As Long
    For i = 0 To UBound(words)
        If InStr(words(i), "(") > 0 Then
            ExtractMethodName = Left(words(i), InStr(words(i), "(") - 1)
            Exit Function
        End If
    Next i
End Function

' Method annotation record type (used internally)
Private Type MethodAnnotationRecord
    MethodName As String
    Annotations As Collection
End Type