# 使用方法ガイド

## クイックスタート

### 1. セットアップ

```bash
# 依存関係のインストール
npm install

# テスト実行（カバレッジ付き）
npm run test:coverage
```

### 2. テスト仕様書の生成

```bash
# 基本的な実行
node src/index.js

# カスタムオプション指定
node src/index.js \
  --source-dir ./src/test \
  --coverage-dir ./coverage \
  --output my_test_spec.xlsx
```

### 3. 出力の確認

生成された `test_specification.xlsx` を開くと、以下の4つのシートが含まれています：

1. **テスト詳細**: 全テストケースの詳細情報
2. **サマリー**: 統計情報とカバレッジサマリー
3. **カバレッジ**: クラス・メソッド別のカバレッジ詳細
4. **設定情報**: ツールのメタデータ

## コマンドラインオプション

```bash
node src/index.js [options]

オプション:
  -s, --source-dir <path>     テストファイルのディレクトリ (デフォルト: "./src/test")
  -c, --coverage-dir <path>   カバレッジディレクトリ (デフォルト: "./coverage")
  -o, --output <path>         出力ファイルパス (デフォルト: "test_specification.xlsx")
  --no-coverage              カバレッジ処理をスキップ
  --log-level <level>        ログレベル: DEBUG, INFO, WARN, ERROR (デフォルト: "INFO")
  -i, --interactive          インタラクティブモードで実行
  -h, --help                 ヘルプを表示
  -V, --version              バージョンを表示
```

## JSDocアノテーションの書き方

### ファイルレベルのアノテーション

```javascript
/**
 * @ソフトウェア・サービス 計算サービス
 * @項目名 基本演算機能テスト
 * @試験内容 加減乗除、絶対値、最大値/最小値の各機能を検証
 * @確認項目 各演算が正しく実行され、エッジケースも適切に処理されることを確認
 * @テスト対象モジュール名 BasicCalculator
 * @テスト実施ベースラインバージョン 1.0.0
 * @テストケース作成者 開発チーム
 * @テストケース作成日 2026-01-14
 * @テストケース修正者 開発チーム
 * @テストケース修正日 2026-01-14
 */
describe('BasicCalculator テストスイート', () => {
  // テストケース
});
```

### テストケースレベルのアノテーション

```javascript
/**
 * @項目名 加算機能テスト
 * @試験内容 正の数、負の数、ゼロを含む加算演算を実行
 * @確認項目 すべての加算結果が数学的に正しいことを確認
 */
test('加算機能のテスト', () => {
  expect(calculator.add(2, 3)).toBe(5);
});
```

## サポートされているアノテーション

### 日本語アノテーション（推奨）

- `@ソフトウェア・サービス` - ソフトウェアまたはサービス名
- `@項目名` - テスト項目名
- `@試験内容` - テストの内容説明
- `@確認項目` - 確認する項目
- `@テスト対象モジュール名` - テスト対象のモジュール名
- `@テスト実施ベースラインバージョン` - ベースラインバージョン
- `@テストケース作成者` - 作成者名
- `@テストケース作成日` - 作成日
- `@テストケース修正者` - 修正者名
- `@テストケース修正日` - 修正日

### 英語アノテーション（後方互換）

- `@TestModule` - Test module name
- `@TestCase` - Test case name
- `@BaselineVersion` - Baseline version
- `@TestOverview` / `@TestObjective` - Test overview
- `@Verification` / `@ExpectedResult` - Expected result
- `@Creator` - Creator name
- `@CreatedDate` - Creation date
- `@Modifier` - Modifier name
- `@ModifiedDate` - Modification date

## 実行例

### 例1: 基本的な実行

```bash
$ node src/index.js
========================================
JavaScript Test Specification Generator
バージョン: 1.0.0
========================================

【ステップ1】ディレクトリスキャン開始...
検出されたテストファイル数: 1

【ステップ2】アノテーション解析開始...
抽出されたテストケース数: 14

【ステップ3】カバレッジ解析開始...
ブランチカバレッジ: 25.48%

【ステップ4】Excel生成開始...
Excel生成完了: test_specification.xlsx

✓ テスト仕様書の生成が完了しました
```

### 例2: カバレッジなしで実行

```bash
$ node src/index.js --no-coverage
========================================
JavaScript Test Specification Generator
バージョン: 1.0.0
========================================

【ステップ1】ディレクトリスキャン開始...
検出されたテストファイル数: 1

【ステップ2】アノテーション解析開始...
抽出されたテストケース数: 14

【ステップ3】カバレッジ処理をスキップ

【ステップ4】Excel生成開始...
Excel生成完了: test_specification.xlsx

✓ テスト仕様書の生成が完了しました
```

### 例3: デバッグモードで実行

```bash
$ node src/index.js --log-level DEBUG
# 詳細なログ出力が表示されます
```

## トラブルシューティング

### Q: テストファイルが検出されない

**A:** 以下を確認してください：
- テストファイルの拡張子が `.test.js`, `.spec.js`, `.test.jsx`, `.spec.jsx` であること
- `--source-dir` オプションで正しいディレクトリを指定していること
- ファイルが除外ディレクトリ（node_modules, dist, coverage等）に含まれていないこと

### Q: カバレッジが表示されない

**A:** 以下を確認してください：
- `npm run test:coverage` でカバレッジレポートを生成済みであること
- `coverage/coverage-final.json` または `coverage/lcov-report/index.html` が存在すること
- `--coverage-dir` オプションで正しいディレクトリを指定していること

### Q: Excelファイルが生成されない

**A:** 以下を確認してください：
- 出力ディレクトリの書き込み権限があること
- ディスク容量が十分にあること
- `--log-level DEBUG` でエラーの詳細を確認すること

### Q: アノテーションが抽出されない

**A:** 以下を確認してください：
- JSDocコメントの形式が正しいこと（`/**` で開始、`*/` で終了）
- アノテーションが `@` で始まっていること
- ファイルのエンコーディングが UTF-8 であること

## Docker を使用した実行

```bash
# Dockerイメージのビルド
docker build -t js-test-spec-gen .

# コンテナで実行
docker run --rm \
  -v "$(pwd)":/workspace \
  -w /workspace \
  js-test-spec-gen \
  node src/index.js --source-dir ./src/test --output report.xlsx
```

## CI/CD統合

### GitHub Actions

```yaml
name: Generate Test Specification

on:
  push:
    branches: [main]

jobs:
  generate-spec:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run test:coverage
      - run: node src/index.js
      - uses: actions/upload-artifact@v3
        with:
          name: test-specification
          path: test_specification.xlsx
```

## よくある質問

### Q: 大規模プロジェクトで実行が遅い場合は？

**A:** 以下の最適化を試してください：
- テストファイルを特定のディレクトリに絞る
- `--no-coverage` オプションでカバレッジ処理をスキップ
- 除外ディレクトリを `.gitignore` に追加

### Q: カスタムアノテーションを追加できますか？

**A:** はい、`src/core/AnnotationParser.js` の `japaneseAnnotations` または `englishAnnotations` オブジェクトに追加することで対応できます。

### Q: 複数のプロジェクトで使用できますか？

**A:** はい、グローバルインストールするか、各プロジェクトに依存関係として追加してください。

## サポート

問題が発生した場合は、以下の情報とともにIssueを作成してください：
- Node.jsバージョン (`node --version`)
- npm/yarnバージョン
- エラーメッセージ全文
- 実行コマンド
- プロジェクト構造（可能な範囲で）
