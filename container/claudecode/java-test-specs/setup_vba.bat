@echo off
echo VBA Test Specification Generator Setup
echo =======================================

echo.
echo 1. Opening Excel file...
start "" "TestSpecGenerator_WithMacros.xlsm"

echo.
echo 2. Manual steps required:
echo    - Enable macros when prompted
echo    - Press Alt + F11 to open VBA Editor
echo    - Import VBA modules from vba-modules/ folder in this order:
echo      * DataTypes.bas (FIRST)
echo      * FolderScanner.bas
echo      * JavaAnnotationParser.bas
echo      * CoverageReportParser.bas
echo      * ExcelSheetBuilder.bas
echo      * MainController.bas (LAST)
echo.
echo 3. Set up macro button:
echo    - Right-click the green button on main sheet
echo    - Select "Assign Macro"
echo    - Choose "MainController.GenerateTestSpecification"
echo.
echo 4. Test with sample data in sample-java-tests/
echo.
echo Setup complete! Check the VBA Import Instructions sheet for details.
pause
