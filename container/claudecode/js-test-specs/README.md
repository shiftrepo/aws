# JavaScript Test Specification Generator

JavaScript/TypeScript テスト仕様書自動生成ツール - JSDocアノテーションからExcelテスト仕様書を生成

## 概要

このツールは、JavaScript/TypeScriptのテストファイルに記述されたJSDocアノテーションを解析し、Excel形式のテスト仕様書を自動生成します。Jestのカバレッジレポートとの統合により、テストカバレッジ情報も含めた包括的なテスト仕様書を作成できます。

## 主な機能

- ✅ **JSDocアノテーション解析**: JavaScript/TypeScriptテストファイルからテストメタデータを抽出
- ✅ **日本語・英語アノテーション対応**: 日本語アノテーション優先、英語も後方互換サポート
- ✅ **Jestカバレッジ統合**: coverage-final.jsonまたはHTMLレポートからカバレッジデータを取得
- ✅ **Excel出力**: 4シート構成の専門的なテスト仕様書を生成
  - テスト詳細シート
  - サマリーシート
  - カバレッジシート
  - 設定情報シート
- ✅ **CLI対応**: コマンドライン from any ディレクトリで実行可能
- ✅ **カラーコーディング**: カバレッジステータスに応じた視覚的な表現

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

# デバッグモード
node src/index.js --log-level DEBUG
```

### CLIオプション

| オプション | 説明 | デフォルト値 |
|----------|------|------------|
| `-s, --source-dir <path>` | テストファイルのソースディレクトリ | `./src/test` |
| `-c, --coverage-dir <path>` | カバレッジレポートディレクトリ | `./coverage` |
| `-o, --output <path>` | 出力Excelファイルパス | `test_specification.xlsx` |
| `--no-coverage` | カバレッジ処理をスキップ | false |
| `--log-level <level>` | ログレベル (DEBUG, INFO, WARN, ERROR) | `INFO` |
| `-i, --interactive` | インタラクティブモードで実行 | false |

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
│   │   ├── CoverageReportParser.js  # カバレッジ解析
│   │   └── ExcelSheetBuilder.js     # Excel生成
│   ├── model/                       # データモデル
│   │   ├── TestCaseInfo.js         # テストケース情報
│   │   ├── CoverageInfo.js         # カバレッジ情報
│   │   └── TestExecutionInfo.js     # テスト実行情報
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
   - カバレッジ率、カバレッジステータス

2. **サマリー**: 全体の統計情報
   - 総テストケース数、ファイル数
   - ブランチカバレッジ、行カバレッジ、メソッドカバレッジ
   - 処理日時

3. **カバレッジ**: クラス・メソッド別のカバレッジ詳細
   - クラス名、メソッド名
   - ブランチカバレッジ、カバーされたブランチ数、総ブランチ数
   - カバレッジステータス（色分け表示）

4. **設定情報**: ツールの設定とメタデータ
   - ツール名、バージョン
   - 実行日時、Node.jsバージョン、プラットフォーム
   - 機能説明

## 技術スタック

| カテゴリ | 技術 | バージョン |
|---------|------|----------|
| フレームワーク | React | 18.3.1 |
| ビルドツール | Vite | 5.4.11 |
| テスト | Jest | 29.7.0 |
| テストライブラリ | @testing-library/react | 16.0.1 |
| UI | React Router | 7.1.1 |
| Excel生成 | ExcelJS | 4.4.0 |
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

### Excelファイルが生成されない

- 出力ディレクトリの書き込み権限を確認
- `--log-level DEBUG` オプションでエラー詳細を確認

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
