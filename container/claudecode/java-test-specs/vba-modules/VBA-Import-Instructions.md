# VBA Module Import Instructions

## Overview
This document provides step-by-step instructions for importing the VBA modules into Excel to create the TestSpecGenerator.xlsm file.

## Prerequisites
- Microsoft Excel 2016 or later
- VBA (Visual Basic for Applications) enabled
- Developer tab enabled in Excel ribbon

## Enabling Developer Tab (if not visible)
1. Open Excel
2. Go to **File** → **Options** → **Customize Ribbon**
3. Check **Developer** in the right panel
4. Click **OK**

## Creating the TestSpecGenerator.xlsm File

### Step 1: Create New Macro-Enabled Workbook
1. Open Excel
2. Create a new blank workbook
3. Save as **TestSpecGenerator.xlsm** (Excel Macro-Enabled Workbook format)
4. Choose the location: `/container/claudecode/java-test-specs/`

### Step 2: Open VBA Editor
1. Press **Alt + F11** or click **Developer** → **Visual Basic**
2. The VBA Editor window will open

### Step 3: Import VBA Modules
Import each `.bas` file in the following order:

#### 3.1 Import DataTypes.bas
1. In VBA Editor: **File** → **Import File**
2. Navigate to `/container/claudecode/java-test-specs/vba-modules/`
3. Select **DataTypes.bas**
4. Click **Open**

#### 3.2 Import FolderScanner.bas
1. **File** → **Import File**
2. Select **FolderScanner.bas**
3. Click **Open**

#### 3.3 Import JavaAnnotationParser.bas
1. **File** → **Import File**
2. Select **JavaAnnotationParser.bas**
3. Click **Open**

#### 3.4 Import CoverageReportParser.bas
1. **File** → **Import File**
2. Select **CoverageReportParser.bas**
3. Click **Open**

#### 3.5 Import ExcelSheetBuilder.bas
1. **File** → **Import File**
2. Select **ExcelSheetBuilder.bas**
3. Click **Open**

#### 3.6 Import MainController.bas
1. **File** → **Import File**
2. Select **MainController.bas**
3. Click **Open**

### Step 4: Verify Module Import
After importing all modules, the VBA Project Explorer should show:
```
VBAProject (TestSpecGenerator.xlsm)
├── Microsoft Excel Objects
│   ├── Sheet1 (Sheet1)
│   ├── Sheet2 (Sheet2)
│   ├── Sheet3 (Sheet3)
│   └── ThisWorkbook
└── Modules
    ├── DataTypes
    ├── FolderScanner
    ├── JavaAnnotationParser
    ├── CoverageReportParser
    ├── ExcelSheetBuilder
    └── MainController
```

### Step 5: Create User Interface (Optional)
#### 5.1 Add Ribbon Button
1. In Excel, right-click on the ribbon
2. Select **Customize the Ribbon**
3. Create a new group or tab
4. Add a button linked to `MainController.GenerateTestSpecification`

#### 5.2 Add Shape Button (Alternative)
1. Go to **Insert** → **Shapes**
2. Insert a rectangle or button shape
3. Right-click the shape → **Assign Macro**
4. Select `MainController.GenerateTestSpecification`
5. Format the button with text "Generate Test Specification"

### Step 6: Configure Macro Security
1. Go to **File** → **Options** → **Trust Center** → **Trust Center Settings**
2. Select **Macro Settings**
3. Choose **Enable all macros** (for development) or **Disable all macros with notification** (for production use)
4. Click **OK**

### Step 7: Test the Application
1. Close VBA Editor
2. Save the workbook (**Ctrl + S**)
3. Click your button or run `MainController.GenerateTestSpecification` from VBA Editor
4. Test with the sample Java files in `/sample-java-tests/`

## Usage Instructions

### Running the Tool
1. Open **TestSpecGenerator.xlsm**
2. Enable macros when prompted
3. Click the "Generate Test Specification" button or:
   - Press **Alt + F11** to open VBA Editor
   - Press **F5** or click **Run** → **Run Sub/UserForm**
   - Select `MainController.GenerateTestSpecification`

### Input Requirements
- **Source Directory**: Path containing Java test files
  - Example: `C:\Projects\MyProject\src\test\java`
- **Output File**: Path for generated Excel report
  - Example: `C:\Reports\TestSpec_20260107.xlsx`

### Expected Output
The tool will generate an Excel file with 4 sheets:
1. **Test Details** - Complete test case information
2. **Summary** - Aggregated statistics
3. **Coverage** - Coverage analysis results
4. **Configuration** - Processing metadata

## Troubleshooting

### Common Issues

#### "Compile Error: User-defined type not defined"
- **Solution**: Ensure DataTypes.bas is imported first

#### "File not found" errors during scanning
- **Solution**: Verify source directory path exists and contains Java files

#### "Permission denied" when saving output file
- **Solution**: Ensure output directory exists and is writable

#### Macro security warnings
- **Solution**: Enable macros or add file to trusted locations

### Error Logging
The application logs errors to:
- `MainController.g_ProcessingErrors` collection
- Check VBA Immediate Window (**Ctrl + G**) for debug output

## Performance Considerations

### Large Projects
For projects with many files (>1000 Java files):
- Expect processing time of 5-10 minutes
- Consider running during off-peak hours
- Ensure sufficient disk space for output file

### Memory Usage
- Large files (>10MB) are skipped automatically
- Memory usage scales with number of test cases found
- Close other applications if memory issues occur

## File Structure After Setup
```
/container/claudecode/java-test-specs/
├── TestSpecGenerator.xlsm          # Main application file
├── sample-java-tests/              # Example test files
├── vba-modules/                    # VBA source code
├── templates/                      # Excel templates
├── docs/                          # Documentation
└── examples/                      # Sample outputs
```

## Version Information
- **VBA Application Version**: 1.0.0
- **Excel Compatibility**: 2016 or later
- **File Format**: .xlsm (Excel Macro-Enabled Workbook)
- **Created**: 2026-01-07

## Security Notes
- The application only reads Java files and coverage reports
- No system modifications or external network connections
- All file operations are within user-specified directories
- Macro security should be configured according to organizational policies

## Support
For issues or questions:
1. Check error messages in the application
2. Verify file paths and permissions
3. Ensure all VBA modules are properly imported
4. Review sample Java files for proper annotation format