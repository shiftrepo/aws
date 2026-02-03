# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Java Test Specification Generator - A comprehensive Java tool that extracts custom annotations from Java test files and generates Excel test specification documents integrated with JaCoCo coverage reports. This tool supports both single-module and multi-module Maven projects, providing ASCII-only output for international compatibility.

### Latest Version: 1.0.0 (February 2026)
- **68% Code Coverage**: Achieved through comprehensive unit testing
- **ASCII Output**: Full Linux/English environment compatibility
- **Multi-Module Support**: Handles Maven multi-module projects (in development)
- **Enhanced Coverage Integration**: Robust XML-based JaCoCo report processing
- **Comprehensive Testing**: 150+ test assertions across all core components

## Verification Guidelines

**IMPORTANT**: When verifying functionality or testing changes in this codebase, always execute the actual commands and observe real outputs. Do not rely on mocks, stubs, or fixed/hardcoded data for verification. Every verification must be performed through actual execution to ensure accuracy and identify real-world issues.

### Verification Practices
- Always run the actual Maven commands to verify build and test results
- Execute the JAR file with real test files to verify annotation extraction
- Generate actual Excel reports and verify their contents
- Run Docker commands completely to ensure container-based workflows function correctly
- Check actual file outputs (Excel files, coverage reports) rather than assuming their contents
- Verify coverage percentages by running real tests, not by using predetermined values

## Build and Test Commands

### Local Development
```bash
# Complete workflow (recommended for coverage integration)
mvn clean compile test jacoco:report package

# Individual steps:
# Build the project
mvn clean compile

# Run tests and generate JaCoCo coverage report
mvn test jacoco:report

# Package into executable JAR (includes shading dependencies)
mvn package

# Verify coverage report generation (should be ~300KB XML file)
ls -la target/site/jacoco/jacoco.xml
file target/site/jacoco/jacoco.xml  # Should show: XML 1.0 document

# Run single test class
mvn test -Dtest=BasicCalculatorTest

# Run single test method
mvn test -Dtest=BasicCalculatorTest#testPositiveAddition

# Debug failing tests with verbose output
mvn test -Dtest=FailingTestClass -X
```

### Docker/Container-based Development
```bash
# Complete build, test, and specification generation in one command
docker run --rm \
  -v "$(pwd)":/workspace:Z \
  -w /workspace \
  maven:3.9-eclipse-temurin-17 \
  bash -c "mvn clean compile test jacoco:report package && \
           cp -r target/site/jacoco ./coverage-reports && \
           java -jar target/java-test-specification-generator-1.0.0.jar \
           --source-dir /workspace --output test_specification.xlsx && \
           rm -rf coverage-reports"

# Note: Use :Z suffix for SELinux environments, remove for non-SELinux
```

### Running the Application
```bash
# Basic usage (complete data: tests + coverage + execution results)
java -jar target/java-test-specification-generator-1.0.0.jar \
  --source-dir . \
  --output report.xlsx

# With CSV output (Excel + CSV files)
java -jar target/java-test-specification-generator-1.0.0.jar \
  --source-dir . \
  --output report.xlsx \
  --csv-output

# Complete workflow with coverage data
java -jar target/java-test-specification-generator-1.0.0.jar \
  --source-dir . \
  --output report.xlsx

# Debug mode
java -jar target/java-test-specification-generator-1.0.0.jar \
  --source-dir . \
  --output report.xlsx \
  --log-level DEBUG

# Interactive mode
java -jar target/java-test-specification-generator-1.0.0.jar --interactive
```

## Architecture and Processing Flow

### Core Components

1. **TestSpecificationGeneratorMain** - Entry point and orchestrator
   - Handles CLI arguments via Apache Commons CLI
   - Coordinates the 4-step processing pipeline
   - Manages logging and error handling

2. **Processing Pipeline**:
   ```
   FolderScanner → JavaAnnotationParser → CoverageReportParser → ExcelSheetBuilder
   ```
   - **FolderScanner**: Recursively finds Java test files and coverage XML/HTML files
   - **JavaAnnotationParser**: Extracts custom annotations from JavaDoc comments
   - **CoverageReportParser**: Parses JaCoCo XML reports and HTML files for coverage metrics
   - **ExcelSheetBuilder**: Creates 4-sheet Excel report with POI

### Custom Annotation System

The tool recognizes JavaDoc-style custom annotations in test files. It supports both **Japanese** and English annotations.

#### Japanese Annotations (推奨)

```java
/**
 * @ソフトウェア・サービス サービス名
 * @項目名 テストケース名
 * @試験内容 テスト処理の説明
 * @確認項目 期待される結果
 * @テスト対象モジュール名 モジュール名
 * @テスト実施ベースラインバージョン 1.0.0
 * @テストケース作成者 作成者名
 * @テストケース作成日 2026-01-14
 * @テストケース修正者 修正者名
 * @テストケース修正日 2026-01-14
 */
```

#### English Annotations (Backward Compatibility)

```java
/**
 * @TestModule ModuleName
 * @TestCase TestCaseName
 * @BaselineVersion 1.0.0
 * @TestOverview Overview text
 * @TestPurpose Purpose description
 * @TestProcess Process description
 * @TestResults Expected results
 * @Creator CreatorName
 * @CreatedDate 2026-01-07
 * @Modifier ModifierName
 * @ModifiedDate 2026-01-07
 * @TestCategory Unit
 * @Priority High
 * @Requirements REQ-001, REQ-002
 * @Dependencies ClassName.class
 */
```

**Note**: Japanese annotations take priority when both are present. The English annotations are maintained for backward compatibility.

### Coverage Integration

The tool automatically searches for JaCoCo coverage reports in these patterns:
- `**/jacoco*.xml` - Primary XML format (preferred and required)
- `**/*coverage*.xml` - Alternative XML patterns

**Critical**: The tool processes **XML reports only**. HTML reports (`index.html`) are not processed for coverage data extraction.

Coverage data is parsed to extract:
- Branch coverage (C1 coverage) - conditional logic analysis
- Instruction coverage - bytecode-level metrics
- Line coverage - source code line analysis
- Method-level metrics - individual method coverage
- Package and class hierarchies - organizational coverage mapping

#### Coverage Troubleshooting

**Problem**: "Coverage data: 0 entries" or "All coverage entries were filtered out"

**Root Cause**: Missing XML reports (tool only processes `jacoco.xml`, not HTML files)

**Solution**:
```bash
# Step 1: Generate XML coverage reports explicitly
mvn clean compile test jacoco:report

# Step 2: Verify XML report exists and has content
ls -la target/site/jacoco/jacoco.xml
# Expected: ~300-500KB XML file

# Step 3: Check XML content
head -10 target/site/jacoco/jacoco.xml
# Expected: <?xml version="1.0" encoding="UTF-8"?><report name="JaCoCo Coverage Report">

# Step 4: Run tool with project root (not just test directory)
java -jar target/java-test-specification-generator-1.0.0.jar \
  --source-dir . \
  --output report.xlsx

# Common issue: Using --source-dir ./src/test/java (incorrect)
# Correct: Using --source-dir . (project root)
```

**Package Filtering**: Tool uses dynamic package detection from test files. Default exclusion: only `com.testspecgenerator` (tool's own packages).

### Excel Output Structure

Generated Excel contains 4 sheets:
1. **Test Details** - Complete test case information with Japanese field names (12 columns):
   - No. (番号)
   - **FQCN (完全修飾クラス名)** - Fully Qualified Class Name (package.ClassName.methodName)
   - ソフトウェア・サービス (Software/Service)
   - 項目名 (Item Name)
   - 試験内容 (Test Content)
   - 確認項目 (Confirmation Items)
   - テスト対象モジュール名 (Test Target Module Name)
   - テスト実施ベースラインバージョン (Baseline Version)
   - テストケース作成者 (Creator)
   - テストケース作成日 (Created Date)
   - テストケース修正者 (Modifier)
   - テストケース修正日 (Modified Date)
2. **Summary** - Overall statistics and metrics
3. **Coverage** - Detailed coverage breakdown by class/method (17 columns):
   - Includes **Test Class (テストクラス)** column showing which test class covers each target code method
   - Class-level mapping based on JaCoCo reports (e.g., BasicCalculator → com.example.BasicCalculatorTest)
   - Branch coverage, instruction coverage, line coverage, and method coverage metrics
4. **Configuration** - Processing settings and metadata

## Important Implementation Details

### Annotation Extraction
- Only processes JavaDoc comments (`/** */`), not regular comments
- Supports both class-level and method-level annotations
- Falls back to "Not Specified" for missing annotations

### Coverage Report Handling
- The tool excludes `/target/` directory from coverage search to avoid duplicates
- Workaround: Copy `target/site/jacoco` to temporary `coverage-reports` directory before processing
- **XML format required**: Tool processes only XML reports (`jacoco.xml`), not HTML reports
- Use `mvn test jacoco:report` to generate XML reports if they don't exist
- Typical XML report size: ~300KB for standard projects

### Test File Detection
- Embedded test classes (inner classes like `BasicCalculator` in `BasicCalculatorTest.java`) are supported
- The sample tests include C1 coverage demonstration with conditional branches

### Multi-Module Project Support

The tool includes experimental support for Maven multi-module projects:

#### Multi-Module Project Detection
- Automatically detects `pom.xml` with `<modules>` sections
- Processes each module independently for comprehensive coverage
- Generates both combined reports and individual module reports

#### Multi-Module Execution (Experimental)
```bash
# For multi-module projects (when implemented):
java -jar target/java-test-specification-generator-1.0.0.jar \
  --project-root /path/to/multimodule/project \
  --output-dir ./reports

# Expected output structure:
# reports/
# ├── combined-report.xlsx          # Integrated report
# ├── combined-report_coverage.csv
# ├── module-a/report.xlsx          # Individual module reports
# ├── module-b/report.xlsx
# └── modules-summary.json
```

**Current Status**: Single-module projects are fully supported. Multi-module functionality is under development based on the implementation plan.

### International Compatibility
- **ASCII Output**: All console output and log messages use ASCII characters only
- **Linux/English Environment**: Fully compatible with non-Japanese environments
- **No Emoji/Unicode**: Status indicators use [OK]/[ERROR] instead of ✅/❌
- **Machine-Independent**: Avoids 2-byte characters and machine-dependent symbols
- **Locale Independence**: Consistent behavior across different system locales

## Maven Configuration

- **Java Version**: 17 (requires JDK 17+)
- **Packaging**: Executable JAR with Maven Shade plugin
- **Main Class**: `com.testspecgenerator.TestSpecificationGeneratorMain`
- **JaCoCo Integration**: Automatic report generation during `test` phase

## Code Quality Metrics

- **Test Coverage**: 68% instruction coverage achieved through comprehensive unit tests
- **Test Classes**: 150+ test assertions covering core functionality
- **Coverage Analysis**: C1 (branch) coverage analysis with real-world test scenarios
- **Quality Assurance**: All components verified with actual execution testing

## File Processing Limits

- Maximum 2000 lines per file read by default
- Lines longer than 2000 characters are truncated
- Excel file size typically 15-25KB for standard projects

## Best Practices

### Complete Development Workflow
```bash
# 1. Clean build with comprehensive testing and coverage
mvn clean compile test jacoco:report package

# 2. Verify all components are working
ls -la target/java-test-specification-generator-1.0.0.jar  # ~24MB JAR file
ls -la target/site/jacoco/jacoco.xml  # ~300KB XML coverage report

# 3. Verify XML content is valid
head -5 target/site/jacoco/jacoco.xml
# Expected: <?xml version="1.0" encoding="UTF-8"?>

# 4. Generate comprehensive test specification
java -jar target/java-test-specification-generator-1.0.0.jar \
  --source-dir . \
  --output test_specification.xlsx \
  --csv-output

# 5. Verify output quality
ls -la test_specification*.xlsx test_specification*csv
file test_specification.xlsx  # Should show Microsoft Excel format
```

### Testing and Verification Standards
```bash
# Run all tests with coverage analysis
mvn clean test jacoco:report

# Verify 68%+ code coverage achievement
grep -A 20 "Coverage Summary" target/site/jacoco/index.html

# Run specific test classes for focused testing
mvn test -Dtest=EnhancedJavaDocBuilderTest
mvn test -Dtest=SurefireReportParserTest
mvn test -Dtest=CoverageReportParserTest

# Debug test failures with full output
mvn test -Dtest=FailingTest -X -e
```

### Coverage Report Generation Best Practices
```bash
# Recommended complete workflow
mvn clean compile test jacoco:report package

# Alternative: Step-by-step verification
mvn clean compile
mvn test          # Generates coverage data
mvn jacoco:report # Creates XML reports
mvn package       # Builds final JAR

# Verify XML report generation
ls -la target/site/jacoco/jacoco.xml
file target/site/jacoco/jacoco.xml  # Should show: XML 1.0 document, UTF-8 Unicode text

# Complete workflow with coverage integration (if needed)
cp -r target/site/jacoco ./coverage-reports
java -jar target/java-test-specification-generator-1.0.0.jar \
  --source-dir . --output report.xlsx
rm -rf coverage-reports
```

### Common Issues and Solutions

#### Coverage Data Issues
- **"Coverage data: 0 entries"**:
  - Root cause: XML reports missing or not found
  - Solution: Run `mvn clean compile test jacoco:report`
  - Verify: `ls -la target/site/jacoco/jacoco.xml` should exist (~300KB)

#### Build Issues
- **Compilation failures**: Ensure Java 17+ and Maven 3.6+
- **Dependency resolution**: Clear `~/.m2/repository` and rebuild
- **Permission errors**: Check file permissions and SELinux context (`:Z` flag for containers)

#### Output Issues
- **Empty Excel files**: Check Java encoding with `-Dfile.encoding=UTF-8`
- **Character encoding problems**: All output uses ASCII-only characters
- **File locking**: Ensure Excel files are not open in other applications

#### Performance Optimization
- **Memory for large projects**: Use `-Xmx4g` JVM flag
- **Parallel test execution**: Maven Surefire plugin configured for optimal performance
- **Coverage analysis**: JaCoCo optimized for minimal overhead during test execution