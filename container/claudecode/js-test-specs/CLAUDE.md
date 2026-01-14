# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

JavaScript Test Specification Generator - Generates Excel test specification documents from JSDoc annotations in test files, integrated with Jest coverage reports. This is a complete JavaScript port of the Java version located at `/root/aws.git/container/claudecode/java-test-specs`.

**Key Principle**: All data is dynamically generated from actual test files and coverage reports. No mocks or fixed values are used.

## Common Commands

### Development
```bash
# Install dependencies (required before first run)
npm install

# Run tests with coverage (required before generating specifications)
npm run test:coverage

# Run tests only
npm test

# Run specific test file
npm test -- BasicCalculator.test.js

# Lint code
npm run lint

# Format code
npm run format
```

### Main Tool Execution
```bash
# Generate test specification (basic usage)
node src/index.js --source-dir ./src/test --coverage-dir ./coverage --output test_specification.xlsx

# Quick run with defaults
npm start

# Skip coverage integration
node src/index.js --no-coverage

# Debug mode
node src/index.js --log-level DEBUG
```

### Data Verification
```bash
# Verify data generation process (proves no mocks used)
node verify-data.js

# Verify Excel output content
node verify-excel.js
```

## Architecture

### Data Flow (4 Steps)

1. **FolderScanner** (`src/core/FolderScanner.js`)
   - Uses `fast-glob` to find test files matching patterns: `**/*.test.js`, `**/*.spec.js`, etc.
   - Excludes: node_modules, .git, dist, coverage, target

2. **AnnotationParser** (`src/core/AnnotationParser.js`)
   - Extracts JSDoc comments using regex: `/\/\*\*\s*\n([\s\S]*?)\*\/\s*(?:test|it)\s*\(\s*['"\`](.*?)['"\`]/g`
   - Prioritizes Japanese annotations (`@ソフトウェア・サービス`) over English (`@TestModule`)
   - Creates `TestCaseInfo` objects for each test method

3. **CoverageReportParser** (`src/core/CoverageReportParser.js`)
   - Parses `coverage/coverage-final.json` (JSON format from Jest)
   - Calculates branch, line, and method coverage dynamically
   - Creates `CoverageInfo` objects per class

4. **ExcelSheetBuilder** (`src/core/ExcelSheetBuilder.js`)
   - Integrates TestCaseInfo + CoverageInfo via `testCase.setCoverageInfo(covered, total)`
   - Generates 4-sheet Excel workbook using ExcelJS:
     - Sheet 1: テスト詳細 (Test Details) - all test cases with annotations
     - Sheet 2: サマリー (Summary) - overall statistics
     - Sheet 3: カバレッジ (Coverage) - coverage per class/method with color coding
     - Sheet 4: 設定情報 (Configuration) - tool metadata

### Key Data Models

**TestCaseInfo** (`src/model/TestCaseInfo.js`)
- Stores annotation data: softwareService, testItemName, testContent, confirmationItem, etc.
- Method: `setCoverageInfo(covered, total)` - integrates coverage data
- Method: `updateCoverageStatus()` - determines status: 優秀 (90-100%), 良好 (70-89%), 普通 (50-69%), 要改善 (<50%)

**CoverageInfo** (`src/model/CoverageInfo.js`)
- Stores: branchCovered/Total, lineCovered/Total, methodCovered/Total
- Methods: `getBranchCoveragePercent()`, `getLineCoveragePercent()`, `getCoverageStatus()`

### JSDoc Annotation Formats

**Japanese (Preferred)**:
```javascript
/**
 * @ソフトウェア・サービス 計算サービス
 * @項目名 加算機能テスト
 * @試験内容 正の数、負の数、ゼロを含む加算演算を実行
 * @確認項目 すべての加算結果が数学的に正しいことを確認
 * @テスト対象モジュール名 BasicCalculator
 * @テスト実施ベースラインバージョン 1.0.0
 * @テストケース作成者 開発チーム
 * @テストケース作成日 2026-01-14
 */
test('加算機能のテスト', () => { /* ... */ });
```

**English (Backward Compatible)**:
```javascript
/**
 * @TestModule BasicCalculator
 * @TestCase Addition Test
 * @TestObjective Test addition functionality
 * @ExpectedResult Results are mathematically correct
 * @BaselineVersion 1.0.0
 * @Creator Development Team
 * @CreatedDate 2026-01-14
 */
test('addition test', () => { /* ... */ });
```

## Important Technical Details

### ES6 Modules
- Project uses `"type": "module"` in package.json
- All imports use `.js` extensions: `import { X } from './X.js'`
- Config files use `.cjs` when CommonJS is required (babel.config.cjs, .eslintrc.cjs)

### Jest Configuration
- Requires `NODE_OPTIONS=--experimental-vm-modules` for ES module support
- Environment: jsdom (for React testing)
- Coverage output: `coverage/coverage-final.json` and HTML reports

### Technology Stack (Exact Versions)
These versions are **strictly enforced** per project requirements:
- React: 18.3.1
- Vite: 5.4.11
- Jest: 29.7.0
- @testing-library/react: 16.0.1
- React Router: 7.1.1

### Color Coding in Excel
Coverage status determines cell background color:
- 優秀 (90-100%): Green (90EE90)
- 良好 (70-89%): Yellow (FFFF99)
- 普通 (50-69%): Light Gray (D3D3D3)
- 要改善 (<50%): Light Red (FFB6C1)

## Sample Implementation

`src/main/example/BasicCalculator.js` - Sample class with 15 methods
`src/test/example/BasicCalculator.test.js` - 14 test cases with full annotations

**Test Results**: 14/14 passed, 100% coverage on BasicCalculator

## Data Verification

The project includes verification scripts that prove data is dynamically generated:
- `verify-data.js` - Re-runs the data extraction process
- `verify-excel.js` - Parses generated Excel and displays contents
- `VERIFICATION_REPORT.md` - Comprehensive verification documentation

## File Exclusions

`.gitignore` includes:
- `node_modules/`, `coverage/`, `dist/`, `build/`
- **Exception**: `test_specification.xlsx` is tracked (sample output for documentation)

## Java Version Comparison

This is a direct port from Java version. Key differences:
- Files.walk → fast-glob
- Apache POI → ExcelJS
- Commons CLI → Commander.js
- JaCoCo XML/HTML → Jest JSON/HTML
- Regex patterns preserved for compatibility
