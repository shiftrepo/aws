# JavaScript Test Specification Generator

JavaScript/TypeScript テスト仕様書自動生成ツール - JSDocアノテーションからExcelテスト仕様書を生成

## 概要

このツールは、JavaScript/TypeScriptのテストファイルに記述されたJSDocアノテーションを解析し、Excel形式のテスト仕様書を自動生成します。Jestのカバレッジレポートとの統合により、テストカバレッジ情報も含めた包括的なテスト仕様書を作成できます。

## 主な機能

- ✅ **JSDocアノテーション解析**: JavaScript/TypeScriptテストファイルからテストメタデータを抽出
- ✅ **日本語・英語アノテーション対応**: 日本語アノテーション優先、英語も後方互換サポート
- ✅ **Jestカバレッジ統合**: coverage-final.jsonまたはHTMLレポートからカバレッジデータを取得
- ✅ **メソッドレベルカバレッジ**: ファイルレベルではなく関数/メソッドごとのカバレッジを表示
- ✅ **テスト実行結果統合**: Jest JSON出力からテスト実行ステータス（PASS/FAIL/SKIP）と実行時間を取得
- ✅ **Excel出力**: 4シート構成の専門的なテスト仕様書を生成
  - テスト詳細シート（実行ステータス・実行時間含む）
  - サマリーシート（実行統計含む）
  - カバレッジシート（メソッドレベル・行カバレッジ）
  - 設定情報シート
- ✅ **CSV出力**: Test DetailsとCoverageのCSVエクスポート
- ✅ **マルチモジュール/Monorepo対応**: npm/yarn/lerna workspacesを自動検出し並列処理
- ✅ **構造化ログ**: Winston による詳細なログ出力（DEBUG, INFO, WARN, ERROR）
- ✅ **CLI対応**: コマンドライン from any ディレクトリで実行可能
- ✅ **カラーコーディング**: カバレッジステータスと実行ステータスに応じた視覚的な表現

## 必要要件

- Node.js >= 18.0.0
- npm または yarn

## インストール

### 1. 依存関係のインストール

```bash
npm install
```

### 2. 実行権限の付与（Linuxの場合）

```bash
chmod +x src/index.js
```

## 使用方法

### 基本的な使い方

```bash
# デフォルト設定で実行
node src/index.js

# または
npm start
```

### オプション指定

```bash
# カスタムディレクトリを指定
node src/index.js --source-dir ./src/test --coverage-dir ./coverage --output report.xlsx

# カバレッジ処理をスキップ
node src/index.js --no-coverage

# CSV出力を有効化
node src/index.js --csv-output

# デバッグモード
node src/index.js --log-level DEBUG

# マルチモジュール/Monorepo プロジェクト処理
node src/index.js --project-root . --output-dir ./reports --csv-output

# シングルモジュールとして強制処理（ワークスペース自動検出をスキップ）
node src/index.js --single-module
```

### CLIオプション

#### シングルモジュールオプション

| オプション | 説明 | デフォルト値 |
|----------|------|------------|
| `-s, --source-dir <path>` | テストファイルのソースディレクトリ | `./src/test` |
| `-c, --coverage-dir <path>` | カバレッジレポートディレクトリ | `./coverage` |
| `-o, --output <path>` | 出力Excelファイルパス | `test_specification.xlsx` |
| `--no-coverage` | カバレッジ処理をスキップ | false |
| `--test-results <path>` | Jestテスト実行結果JSONファイル | `test-results.json` |
| `--csv-output` | CSV形式でも出力 | false |
| `--log-level <level>` | ログレベル (DEBUG, INFO, WARN, ERROR) | `INFO` |

#### マルチモジュールオプション

| オプション | 説明 | デフォルト値 |
|----------|------|------------|
| `--project-root <path>` | プロジェクトルートディレクトリ（monorepo） | - |
| `--output-dir <path>` | モジュールごとのレポート出力ディレクトリ | `./reports` |
| `--single-module` | シングルモジュールとして処理（ワークスペース検出スキップ） | false |
| `--csv-output` | CSV形式でも出力 | false |
| `--log-level <level>` | ログレベル | `INFO` |

## JSDocアノテーション

### 日本語アノテーション（推奨）

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
 * @テストケース修正者 開発チーム
 * @テストケース修正日 2026-01-14
 */
test('加算機能のテスト', () => {
  expect(calculator.add(2, 3)).toBe(5);
});
```

### 英語アノテーション（後方互換）

```javascript
/**
 * @TestCase testAddition
 * @TestType Functional
 * @TestObjective Test addition functionality
 * @ExpectedResult Correct addition results
 * @TestModule BasicCalculator
 * @BaselineVersion 1.0.0
 * @Creator Development Team
 * @CreatedDate 2026-01-14
 */
test('addition functionality test', () => {
  expect(calculator.add(2, 3)).toBe(5);
});
```

## プロジェクト構造

```
js-test-specs/
├── src/
│   ├── index.js                     # メインエントリポイント
│   ├── core/                        # コアモジュール
│   │   ├── FolderScanner.js        # ディレクトリスキャン
│   │   ├── AnnotationParser.js      # アノテーション解析
│   │   ├── CoverageReportParser.js  # カバレッジ解析（メソッドレベル対応）
│   │   ├── TestExecutionParser.js   # テスト実行結果解析（NEW）
│   │   ├── ExcelSheetBuilder.js     # Excel生成
│   │   ├── CsvSheetBuilder.js       # CSV生成（NEW）
│   │   ├── WorkspaceDetector.js     # Monorepoワークスペース検出（NEW）
│   │   └── MultiModuleProcessor.js  # マルチモジュール並列処理（NEW）
│   ├── model/                       # データモデル
│   │   ├── TestCaseInfo.js         # テストケース情報（実行情報追加）
│   │   ├── CoverageInfo.js         # カバレッジ情報（メソッド名追加）
│   │   ├── ModuleInfo.js            # モジュール情報（NEW）
│   │   └── ModuleResult.js          # モジュール処理結果（NEW）
│   ├── util/                        # ユーティリティ（NEW）
│   │   └── Logger.js                # Winston ロガー設定
│   ├── workers/                     # Worker Threads（NEW）
│   │   └── moduleProcessor.js       # モジュール処理ワーカー
│   ├── main/                        # サンプル実装
│   │   └── example/
│   │       └── BasicCalculator.js   # サンプル計算機クラス
│   └── test/                        # テストファイル
│       ├── setup.js                # Jest セットアップ
│       └── example/
│           └── BasicCalculator.test.js  # サンプルテスト
├── package.json                     # プロジェクト設定
├── jest.config.js                   # Jest 設定
├── babel.config.cjs                 # Babel 設定
├── vite.config.js                   # Vite 設定
└── README.md                        # このファイル
```

## テストの実行

```bash
# テスト実行
npm test

# カバレッジ付きテスト実行
npm run test:coverage
```

## 出力例

生成されるExcelファイルには以下の4つのシートが含まれます:

1. **テスト詳細**: 各テストケースの詳細情報
   - 番号、ソフトウェア・サービス、項目名、試験内容、確認項目
   - テスト対象モジュール、バージョン、作成者、作成日、修正者、修正日
   - **テスト実行ステータス**（PASS/FAIL/SKIP）と**実行時間**（NEW）
   - カバレッジ率、カバレッジステータス

2. **サマリー**: 全体の統計情報
   - 総テストケース数、ファイル数
   - **テスト実行サマリー**（実行数、成功、失敗、スキップ、成功率）（NEW）
   - ブランチカバレッジ、行カバレッジ、メソッドカバレッジ
   - 処理日時

3. **カバレッジ**: **メソッドレベル**のカバレッジ詳細（NEW）
   - クラス名、**メソッド名**
   - ブランチカバレッジ、カバーされたブランチ数、総ブランチ数
   - **行カバレッジ、カバーされた行数、総行数**（NEW）
   - カバレッジステータス（色分け表示）

4. **設定情報**: ツールの設定とメタデータ
   - ツール名、バージョン
   - 実行日時、Node.jsバージョン、プラットフォーム
   - 機能説明

## CSV出力

`--csv-output` オプションを使用すると、Excel形式に加えてCSV形式でもデータをエクスポートできます。

```bash
node src/index.js --csv-output
```

生成されるCSVファイル:
- `test_specification_test_details.csv`: テスト詳細データ
- `test_specification_coverage.csv`: カバレッジデータ

CSV形式はExcelで開くか、データ分析ツール（Python pandas、R、BIツールなど）で処理できます。UTF-8 BOMエンコーディングでExcelとの互換性を確保しています。

## マルチモジュール/Monorepoサポート

npm/yarn workspaces または lerna を使用するmonorepoプロジェクトを自動検出し、並列処理します。

### 自動検出モード

プロジェクトルートでツールを実行すると、package.jsonの`workspaces`フィールドまたは`lerna.json`を自動検出します。

```bash
cd /path/to/monorepo
node /path/to/js-test-spec-gen --output-dir ./reports --csv-output
```

### 明示的なマルチモジュールモード

```bash
node src/index.js --project-root /path/to/monorepo --output-dir ./reports
```

### 生成される出力

マルチモジュールモードでは以下のファイルが生成されます:

- `combined_test_specification.xlsx`: 全モジュールの統合レポート
- `{module-name}_test_specification.xlsx`: モジュールごとの個別レポート
- CSV出力オプション有効時: 各Excelファイルに対応するCSVファイル

### パフォーマンス

- **並列処理**: 最大4モジュールを同時処理（設定可能）
- **Worker Threads**: 各モジュールは独立したWorkerスレッドで処理
- **タイムアウト**: モジュールごとに5分のタイムアウト（設定可能）

### シングルモジュールとして強制処理

workspaceを含むmonorepoでも、特定のモジュールだけを処理したい場合:

```bash
cd packages/my-module
node /path/to/js-test-spec-gen --single-module
```

## 技術スタック

| カテゴリ | 技術 | バージョン |
|---------|------|----------|
| フレームワーク | React | 18.3.1 |
| ビルドツール | Vite | 5.4.11 |
| テスト | Jest | 29.7.0 |
| テストライブラリ | @testing-library/react | 16.0.1 |
| UI | React Router | 7.1.1 |
| Excel生成 | ExcelJS | 4.4.0 |
| CSV生成 | csv-writer | 1.6.0 |
| ロギング | winston | 3.11.0 |
| CLI | Commander | 12.0.0 |
| ファイル検索 | fast-glob | 3.3.2 |
| XML解析 | fast-xml-parser | 4.3.4 |
| HTML解析 | jsdom | 24.0.0 |

## トラブルシューティング

### テストファイルが見つからない

- `--source-dir` オプションで正しいディレクトリを指定しているか確認
- テストファイルの拡張子が `.test.js`, `.spec.js`, `.test.jsx`, `.spec.jsx` であることを確認

### カバレッジが表示されない

- `npm run test:coverage` を実行してカバレッジレポートを生成
- `--coverage-dir` オプションで正しいディレクトリを指定
- `coverage/coverage-final.json` または `coverage/lcov-report/index.html` が存在することを確認

### テスト実行ステータスが表示されない

- テストを `npm run test:coverage` で実行すると自動的に `test-results.json` が生成されます
- 手動で実行する場合: `jest --json --outputFile=test-results.json`
- `--test-results` オプションで正しいパスを指定

### Excelファイルが生成されない

- 出力ディレクトリの書き込み権限を確認
- `--log-level DEBUG` オプションでエラー詳細を確認
- ログファイル `test_spec_generator.log` を確認

### マルチモジュール処理が失敗する

- 各モジュールに `package.json` が存在することを確認
- 各モジュールのテストディレクトリ構造が正しいか確認
- `--log-level DEBUG` でモジュールごとの処理状況を確認
- タイムアウトが発生する場合、モジュール数が多すぎる可能性あり

## ライセンス

MIT

## 作成者

開発チーム

## バージョン履歴

- **v1.0.0** (2026-01-14): 初版リリース
  - JSDocアノテーション解析機能
  - Jestカバレッジ統合
  - Excel出力機能
  - CLIインターフェース
