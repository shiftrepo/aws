# Excel Template Creation Instructions

## Overview
This document provides step-by-step instructions for creating the Excel template (`test-spec-template.xlsx`) that will be used by the VBA macro to generate test specification reports.

## Template Structure

The Excel template should contain 4 worksheets with the following structure:

### 1. Test Details Sheet

**Purpose:** Display detailed information for each test case found in Java files.

**Layout:**
- **Row 1:** Title "Test Specification Report" (Bold, Size 16, Centered across columns A-O)
- **Row 2:** "Generated on: [DATE]" (Bold, Size 12)
- **Row 3:** "Source Directory: [PATH]" (Bold, Size 12)
- **Row 4:** Empty spacer row
- **Row 5:** Headers with blue background (RGB: 79, 129, 189), white bold text:
  - A: File Path
  - B: Test Module
  - C: Test Case
  - D: Baseline Version
  - E: Test Overview (width: 25)
  - F: Test Purpose (width: 25)
  - G: Test Process (width: 30)
  - H: Test Results (width: 25)
  - I: Creator
  - J: Created Date
  - K: Modifier
  - L: Modified Date
  - M: Coverage %
  - N: Branches Covered
  - O: Branches Total

**Column Widths:**
- A: 40, B-D: 15, E-H: 25-30, I-L: 12, M-O: 10

**Data Formatting:**
- Columns E-H: Wrap text enabled
- Columns J, L: Date format (yyyy-mm-dd)
- Column M: Percentage format
- Columns N, O: Number format

### 2. Summary Sheet

**Purpose:** Provide aggregated statistics and overview information.

**Layout:**
- **Row 1:** Title "Test Summary Report" (Bold, Size 16, Centered)
- **Row 3-5:** Statistics section:
  - Total Test Files: [Number]
  - Total Test Cases: [Number]
  - Total Test Methods: [Number]
- **Row 7:** Subtitle "Coverage Statistics" (Bold, Size 14)
- **Row 8-11:** Coverage metrics:
  - Overall Branch Coverage: [Percentage]
  - Branches Covered: [Number]
  - Total Branches: [Number]
  - Missing Coverage: [Number]
- **Row 13:** Subtitle "Module Coverage Breakdown" (Bold, Size 14)
- **Row 14:** Headers with light blue background:
  - A: Module Name
  - B: Test Cases
  - C: Coverage %
  - D: Status

**Conditional Formatting for Status Column:**
- Green: >= 90% coverage
- Yellow: 70-89% coverage
- Red: < 70% coverage

### 3. Coverage Sheet

**Purpose:** Display detailed coverage information from JaCoCo reports.

**Layout:**
- **Row 1:** Title "Coverage Analysis Report" (Bold, Size 16, Centered)
- **Row 3:** Headers with green background (RGB: 146, 208, 80), black bold text:
  - A: File Path
  - B: Method Name
  - C: Instructions Covered
  - D: Instructions Missed
  - E: Branches Covered
  - F: Branches Missed
  - G: C1 Coverage %
  - H: Coverage Status

**Data Formatting:**
- Columns C-F: Number format
- Column G: Percentage format
- Column H: Conditional formatting (same as Summary sheet)

### 4. Configuration Sheet

**Purpose:** Store processing configuration and metadata.

**Layout:**
- **Row 1:** Title "Processing Configuration" (Bold, Size 16, Centered)
- **Row 3:** Headers with yellow background (RGB: 255, 230, 153):
  - A: Configuration Parameter
  - B: Value
  - C: Description
- **Rows 4-9:** Configuration entries:
  - Source Directory
  - Output File
  - Processing Date
  - Files Processed
  - Coverage Reports Found
  - Processing Duration

## Formatting Guidelines

### Colors
- **Title backgrounds:** No fill, just bold formatting
- **Primary headers:** Blue (RGB: 79, 129, 189) with white text
- **Secondary headers:** Light blue (RGB: 184, 204, 228) with black text
- **Coverage headers:** Green (RGB: 146, 208, 80) with black text
- **Config headers:** Yellow (RGB: 255, 230, 153) with black text

### Fonts
- **All text:** Arial, Size 10 (except titles and subtitles)
- **Titles:** Arial, Size 16, Bold
- **Subtitles:** Arial, Size 14, Bold
- **Headers:** Arial, Size 10, Bold

### Borders
- Add thin borders around all header rows
- Add thin borders around data sections

## Cell Naming

For VBA macro integration, define the following named ranges:

### Test Details Sheet
- `TestDetails_StartRow` = A6 (first data row)
- `TestDetails_Headers` = A5:O5

### Summary Sheet
- `Summary_TotalFiles` = B3
- `Summary_TotalCases` = B4
- `Summary_TotalMethods` = B5
- `Summary_Coverage` = B8
- `Summary_ModuleStart` = A15 (first module data row)

### Coverage Sheet
- `Coverage_StartRow` = A4 (first data row)
- `Coverage_Headers` = A3:H3

### Configuration Sheet
- `Config_StartRow` = A4 (first config row)

## Creating the Template

1. **Create new Excel workbook** with 4 sheets renamed as specified
2. **Apply formatting** as described above for each sheet
3. **Set column widths** according to specifications
4. **Add conditional formatting** for status columns
5. **Define named ranges** as specified
6. **Save as Excel Template** (.xltx) or regular workbook (.xlsx)
7. **Test the template** by manually entering sample data

## Notes for VBA Integration

- The VBA macro will look for specific cell positions and named ranges
- Leave data rows empty - they will be populated by the macro
- Placeholder text in brackets (e.g., [DATE]) will be replaced by actual values
- Ensure all formatting is applied to template cells for consistent output

## Validation Checklist

- [ ] All 4 sheets created and properly named
- [ ] Headers formatted with correct colors and fonts
- [ ] Column widths set appropriately
- [ ] Conditional formatting applied to status columns
- [ ] Named ranges defined for VBA integration
- [ ] Data rows left empty for macro population
- [ ] Template saved in correct format