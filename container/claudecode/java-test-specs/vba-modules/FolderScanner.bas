Attribute VB_Name = "FolderScanner"
' ============================================================================
' FolderScanner.bas
' Folder scanning module for Java Test Specification Generator
'
' This module handles recursive directory scanning to find:
' 1. Java test files (.java)
' 2. JaCoCo coverage reports (.xml, .html)
' 3. Directory validation and file filtering
'
' Created: 2026-01-07
' Version: 1.0.0
' ============================================================================

Option Explicit

' File system constants
Private Const MAX_PATH As Long = 260
Private Const INVALID_HANDLE_VALUE As Long = -1

' API declarations for efficient file operations
#If VBA7 Then
    Private Declare PtrSafe Function FindFirstFile Lib "kernel32" Alias "FindFirstFileA" (ByVal lpFileName As String, lpFindFileData As WIN32_FIND_DATA) As LongPtr
    Private Declare PtrSafe Function FindNextFile Lib "kernel32" Alias "FindNextFileA" (ByVal hFindFile As LongPtr, lpFindFileData As WIN32_FIND_DATA) As Long
    Private Declare PtrSafe Function FindClose Lib "kernel32" (ByVal hFindFile As LongPtr) As Long
    Private Type WIN32_FIND_DATA
        dwFileAttributes As Long
        ftCreationTime As Currency
        ftLastAccessTime As Currency
        ftLastWriteTime As Currency
        nFileSizeHigh As Long
        nFileSizeLow As Long
        dwReserved0 As Long
        dwReserved1 As Long
        cFileName As String * MAX_PATH
        cAlternateFileName As String * 14
    End Type
#Else
    Private Declare Function FindFirstFile Lib "kernel32" Alias "FindFirstFileA" (ByVal lpFileName As String, lpFindFileData As WIN32_FIND_DATA) As Long
    Private Declare Function FindNextFile Lib "kernel32" Alias "FindNextFileA" (ByVal hFindFile As Long, lpFindFileData As WIN32_FIND_DATA) As Long
    Private Declare Function FindClose Lib "kernel32" (ByVal hFindFile As Long) As Long
    Private Type WIN32_FIND_DATA
        dwFileAttributes As Long
        ftCreationTime As Currency
        ftLastAccessTime As Currency
        ftLastWriteTime As Currency
        nFileSizeHigh As Long
        nFileSizeLow As Long
        dwReserved0 As Long
        dwReserved1 As Long
        cFileName As String * MAX_PATH
        cAlternateFileName As String * 14
    End Type
#End If

' File attribute constants
Private Const FILE_ATTRIBUTE_DIRECTORY As Long = &H10
Private Const FILE_ATTRIBUTE_HIDDEN As Long = &H2
Private Const FILE_ATTRIBUTE_SYSTEM As Long = &H4

' Scan for Java files in the specified directory and subdirectories
Public Function ScanForJavaFiles(rootDirectory As String) As Collection
    On Error GoTo ErrorHandler

    Set ScanForJavaFiles = New Collection

    If Not DirectoryExists(rootDirectory) Then
        Err.Raise vbObjectError + 1001, "FolderScanner.ScanForJavaFiles", "Root directory does not exist: " & rootDirectory
    End If

    ' Normalize directory path
    Dim normalizedPath As String
    normalizedPath = NormalizePath(rootDirectory)

    ' Recursively scan for Java files
    ScanDirectoryForFiles normalizedPath, "*.java", ScanForJavaFiles, True

    Exit Function

ErrorHandler:
    If ScanForJavaFiles Is Nothing Then Set ScanForJavaFiles = New Collection
    MainController.g_ProcessingErrors.Add "FolderScanner.ScanForJavaFiles: " & Err.Description
End Function

' Scan for coverage report files (XML and HTML)
Public Function ScanForCoverageReports(rootDirectory As String) As Collection
    On Error GoTo ErrorHandler

    Set ScanForCoverageReports = New Collection

    If Not DirectoryExists(rootDirectory) Then
        Exit Function
    End If

    ' Normalize directory path
    Dim normalizedPath As String
    normalizedPath = NormalizePath(rootDirectory)

    ' Scan for various coverage report formats
    Dim xmlReports As Collection
    Dim htmlReports As Collection

    Set xmlReports = New Collection
    Set htmlReports = New Collection

    ' Scan for JaCoCo XML reports (usually named jacoco*.xml or *coverage*.xml)
    ScanDirectoryForFiles normalizedPath, "jacoco*.xml", xmlReports, True
    ScanDirectoryForFiles normalizedPath, "*coverage*.xml", xmlReports, True

    ' Scan for JaCoCo HTML reports (usually index.html in coverage directories)
    ScanDirectoryForFiles normalizedPath, "index.html", htmlReports, True
    ScanDirectoryForFiles normalizedPath, "*coverage*.html", htmlReports, True

    ' Combine all coverage reports
    Dim i As Long
    For i = 1 To xmlReports.Count
        ScanForCoverageReports.Add xmlReports(i)
    Next i

    For i = 1 To htmlReports.Count
        ScanForCoverageReports.Add htmlReports(i)
    Next i

    Exit Function

ErrorHandler:
    If ScanForCoverageReports Is Nothing Then Set ScanForCoverageReports = New Collection
    MainController.g_ProcessingErrors.Add "FolderScanner.ScanForCoverageReports: " & Err.Description
End Function

' Check if a directory exists
Public Function DirectoryExists(directoryPath As String) As Boolean
    On Error GoTo ErrorHandler

    DirectoryExists = False

    If Len(directoryPath) = 0 Then Exit Function

    ' Remove trailing backslash if present
    Dim path As String
    path = directoryPath
    If Right(path, 1) = "\" And Len(path) > 3 Then
        path = Left(path, Len(path) - 1)
    End If

    ' Check if path exists and is a directory
    Dim attr As Long
    attr = GetAttr(path)
    DirectoryExists = ((attr And FILE_ATTRIBUTE_DIRECTORY) = FILE_ATTRIBUTE_DIRECTORY)

    Exit Function

ErrorHandler:
    DirectoryExists = False
End Function

' Check if a file exists
Public Function FileExists(filePath As String) As Boolean
    On Error GoTo ErrorHandler

    FileExists = (Len(Dir(filePath)) > 0)

    Exit Function

ErrorHandler:
    FileExists = False
End Function

' Get file information including size and modification date
Public Function GetFileInfo(filePath As String) As FileInfo
    On Error GoTo ErrorHandler

    Dim info As FileInfo
    info.FilePath = filePath
    info.FileName = GetFileNameFromPath(filePath)
    info.FileSize = FileLen(filePath)
    info.ModifiedDate = FileDateTime(filePath)
    info.IsValid = True

    GetFileInfo = info

    Exit Function

ErrorHandler:
    info.IsValid = False
    info.ErrorMessage = Err.Description
    GetFileInfo = info
End Function

' Normalize directory path (handle forward/back slashes, trailing slashes)
Private Function NormalizePath(path As String) As String
    On Error Resume Next

    NormalizePath = path

    ' Replace forward slashes with backslashes (Windows standard)
    NormalizePath = Replace(NormalizePath, "/", "\")

    ' Ensure path ends with backslash for directory operations
    If Right(NormalizePath, 1) <> "\" Then
        NormalizePath = NormalizePath & "\"
    End If

    ' Remove double backslashes
    Do While InStr(NormalizePath, "\\") > 0
        NormalizePath = Replace(NormalizePath, "\\", "\")
    Loop
End Function

' Extract filename from full path
Private Function GetFileNameFromPath(filePath As String) As String
    On Error Resume Next

    Dim pos As Long
    pos = InStrRev(filePath, "\")
    If pos > 0 Then
        GetFileNameFromPath = Mid(filePath, pos + 1)
    Else
        GetFileNameFromPath = filePath
    End If
End Function

' Recursively scan directory for files matching pattern
Private Sub ScanDirectoryForFiles(directoryPath As String, pattern As String, results As Collection, includeSubdirectories As Boolean)
    On Error GoTo ErrorHandler

#If VBA7 Then
    Dim hFind As LongPtr
#Else
    Dim hFind As Long
#End If

    Dim findData As WIN32_FIND_DATA
    Dim searchPath As String
    Dim fileName As String
    Dim fullPath As String

    ' Search for files matching the pattern
    searchPath = directoryPath & pattern
    hFind = FindFirstFile(searchPath, findData)

    If hFind <> INVALID_HANDLE_VALUE Then
        Do
            fileName = Left(findData.cFileName, InStr(findData.cFileName, Chr(0)) - 1)
            If Len(fileName) > 0 And fileName <> "." And fileName <> ".." Then
                If (findData.dwFileAttributes And FILE_ATTRIBUTE_DIRECTORY) = 0 Then
                    ' This is a file, add it to results
                    fullPath = directoryPath & fileName
                    results.Add fullPath
                End If
            End If
        Loop While FindNextFile(hFind, findData) <> 0
        FindClose hFind
    End If

    ' If including subdirectories, scan them recursively
    If includeSubdirectories Then
        searchPath = directoryPath & "*"
        hFind = FindFirstFile(searchPath, findData)

        If hFind <> INVALID_HANDLE_VALUE Then
            Do
                fileName = Left(findData.cFileName, InStr(findData.cFileName, Chr(0)) - 1)
                If Len(fileName) > 0 And fileName <> "." And fileName <> ".." Then
                    If (findData.dwFileAttributes And FILE_ATTRIBUTE_DIRECTORY) = FILE_ATTRIBUTE_DIRECTORY Then
                        ' This is a subdirectory, scan it recursively
                        If (findData.dwFileAttributes And FILE_ATTRIBUTE_HIDDEN) = 0 And _
                           (findData.dwFileAttributes And FILE_ATTRIBUTE_SYSTEM) = 0 Then
                            fullPath = directoryPath & fileName & "\"
                            ScanDirectoryForFiles fullPath, pattern, results, True
                        End If
                    End If
                End If
            Loop While FindNextFile(hFind, findData) <> 0
            FindClose hFind
        End If
    End If

    Exit Sub

ErrorHandler:
    If hFind <> INVALID_HANDLE_VALUE Then FindClose hFind
    MainController.g_ProcessingErrors.Add "FolderScanner.ScanDirectoryForFiles: " & Err.Description & " (Path: " & directoryPath & ")"
End Sub

' Get directory size and file count (for progress estimation)
Public Function GetDirectoryStats(directoryPath As String) As DirectoryStats
    On Error GoTo ErrorHandler

    Dim stats As DirectoryStats
    stats.TotalFiles = 0
    stats.TotalSize = 0
    stats.IsValid = True

    If Not DirectoryExists(directoryPath) Then
        stats.IsValid = False
        stats.ErrorMessage = "Directory does not exist"
        GetDirectoryStats = stats
        Exit Function
    End If

    CalculateDirectoryStats NormalizePath(directoryPath), stats

    GetDirectoryStats = stats

    Exit Function

ErrorHandler:
    stats.IsValid = False
    stats.ErrorMessage = Err.Description
    GetDirectoryStats = stats
End Function

' Recursively calculate directory statistics
Private Sub CalculateDirectoryStats(directoryPath As String, ByRef stats As DirectoryStats)
    On Error GoTo ErrorHandler

#If VBA7 Then
    Dim hFind As LongPtr
#Else
    Dim hFind As Long
#End If

    Dim findData As WIN32_FIND_DATA
    Dim searchPath As String
    Dim fileName As String
    Dim fullPath As String

    searchPath = directoryPath & "*"
    hFind = FindFirstFile(searchPath, findData)

    If hFind <> INVALID_HANDLE_VALUE Then
        Do
            fileName = Left(findData.cFileName, InStr(findData.cFileName, Chr(0)) - 1)
            If Len(fileName) > 0 And fileName <> "." And fileName <> ".." Then
                fullPath = directoryPath & fileName

                If (findData.dwFileAttributes And FILE_ATTRIBUTE_DIRECTORY) = FILE_ATTRIBUTE_DIRECTORY Then
                    ' Subdirectory - recurse
                    If (findData.dwFileAttributes And FILE_ATTRIBUTE_HIDDEN) = 0 And _
                       (findData.dwFileAttributes And FILE_ATTRIBUTE_SYSTEM) = 0 Then
                        CalculateDirectoryStats fullPath & "\", stats
                    End If
                Else
                    ' File - add to statistics
                    stats.TotalFiles = stats.TotalFiles + 1
                    stats.TotalSize = stats.TotalSize + ((findData.nFileSizeHigh * (2 ^ 32)) + findData.nFileSizeLow)
                End If
            End If
        Loop While FindNextFile(hFind, findData) <> 0
        FindClose hFind
    End If

    Exit Sub

ErrorHandler:
    If hFind <> INVALID_HANDLE_VALUE Then FindClose hFind
    MainController.g_ProcessingErrors.Add "FolderScanner.CalculateDirectoryStats: " & Err.Description
End Sub