# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Java Test Specification Generator - A tool that extracts custom annotations from Java test files and generates Excel test specification documents integrated with JaCoCo coverage reports.

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
# Build the project
mvn clean compile

# Run tests and generate JaCoCo coverage report
mvn test

# Package into executable JAR (includes shading dependencies)
mvn package

# Clean, test, and package in one command
mvn clean compile test package

# Run single test class
mvn test -Dtest=BasicCalculatorTest

# Run single test method
mvn test -Dtest=BasicCalculatorTest#testPositiveAddition
```

### Docker/Container-based Development
```bash
# Complete build, test, and specification generation in one command
docker run --rm \
  -v "$(pwd)":/workspace:Z \
  -w /workspace \
  maven:3.9-eclipse-temurin-17 \
  bash -c "mvn clean compile test package && \
           cp -r target/site/jacoco ./coverage-reports && \
           java -jar target/java-test-specification-generator-1.0.0.jar \
           --source-dir /workspace --output test_specification.xlsx && \
           rm -rf coverage-reports"

# Note: Use :Z suffix for SELinux environments, remove for non-SELinux
```

### Running the Application
```bash
# Basic usage
java -jar target/java-test-specification-generator-1.0.0.jar \
  --source-dir /path/to/java/tests \
  --output report.xlsx

# Without coverage processing
java -jar target/java-test-specification-generator-1.0.0.jar \
  --source-dir /path/to/java/tests \
  --output report.xlsx \
  --no-coverage

# Debug mode
java -jar target/java-test-specification-generator-1.0.0.jar \
  --source-dir /path/to/java/tests \
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
- `**/jacoco*.xml` - Primary XML format (preferred)
- `**/*coverage*.xml` - Alternative XML patterns
- `**/index.html`, `**/*coverage*.html` - HTML reports as fallback

Coverage data is parsed to extract:
- Branch coverage (C1 coverage)
- Line coverage
- Method-level metrics
- Package and class hierarchies

### Excel Output Structure

Generated Excel contains 4 sheets:
1. **Test Details** - Complete test case information with Japanese field names:
   - No. (番号)
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
3. **Coverage** - Detailed coverage breakdown by class/method
4. **Configuration** - Processing settings and metadata

## Important Implementation Details

### Annotation Extraction
- Only processes JavaDoc comments (`/** */`), not regular comments
- Supports both class-level and method-level annotations
- Falls back to "Not Specified" for missing annotations

### Coverage Report Handling
- The tool excludes `/target/` directory from coverage search to avoid duplicates
- Workaround: Copy `target/site/jacoco` to temporary `coverage-reports` directory before processing
- XML format preferred over HTML for accuracy

### Test File Detection
- Embedded test classes (inner classes like `BasicCalculator` in `BasicCalculatorTest.java`) are supported
- The sample tests include C1 coverage demonstration with conditional branches

## Maven Configuration

- **Java Version**: 17 (requires JDK 17+)
- **Packaging**: Executable JAR with Maven Shade plugin
- **Main Class**: `com.testspecgenerator.TestSpecificationGeneratorMain`
- **JaCoCo Integration**: Automatic report generation during `test` phase

## File Processing Limits

- Maximum 2000 lines per file read by default
- Lines longer than 2000 characters are truncated
- Excel file size typically 15-25KB for standard projects