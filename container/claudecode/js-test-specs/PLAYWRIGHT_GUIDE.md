# Playwright テストガイド

このドキュメントでは、Playwright E2Eテストをテスト仕様書生成ツールで活用する方法を説明します。

## 📋 概要

このツールは **Playwright** のテストファイルを自動認識し、JSDocアノテーションからテスト仕様書（Excel/CSV）を生成します。

### サポートされているファイルパターン
- `**/*.spec.js`
- `**/*.spec.ts`
- `**/*.test.js`
- `**/*.test.ts`
- `**/*.spec.jsx`
- `**/*.spec.tsx`

## 🚀 セットアップ

### 1. Playwrightのインストール

```bash
npm install -D @playwright/test
```

### 2. Playwright設定ファイルの作成

`playwright.config.js` を作成：

```javascript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.js',
  reporter: [
    ['html'],
    ['json', { outputFile: 'playwright-results.json' }]
  ],
  use: {
    baseURL: 'https://example.com',
    trace: 'on-first-retry',
  },
});
```

## 📝 JSDocアノテーションの書き方

Playwrightテストの前に、JSDocコメントでアノテーションを記述します。

### 基本構文

```javascript
import { test, expect } from '@playwright/test';

/**
 * @ソフトウェア・サービス Webアプリケーション名
 * @項目名 テスト項目名
 * @試験内容 テストの目的・内容
 * @確認項目 確認すべき項目
 * @テスト対象モジュール名 テスト対象のモジュール
 * @テスト実施ベースラインバージョン 1.0.0
 * @テストケース作成者 作成者名
 * @テストケース作成日 2026-02-12
 */
test('テストケース名', async ({ page }) => {
  // テストコード
  await page.goto('https://example.com');
  await expect(page.locator('h1')).toContainText('Welcome');
});
```

### 英語アノテーション（後方互換性）

```javascript
/**
 * @TestModule LoginPage
 * @TestCase Login functionality test
 * @TestObjective Verify login with valid credentials
 * @ExpectedResult User is redirected to dashboard
 * @BaselineVersion 1.0.0
 * @Creator QA Team
 * @CreatedDate 2026-02-12
 */
test('successful login', async ({ page }) => {
  // Test code
});
```

## 📂 サンプルファイル

このプロジェクトには2つのPlaywrightサンプルが含まれています：

### 1. LoginPage.spec.js
- ログイン機能の正常系・異常系テスト
- バリデーションテスト
- ログアウト機能テスト
- パスワード表示切り替えテスト

場所: `src/test/example/LoginPage.spec.js`

### 2. ShoppingCart.spec.js
- 商品追加機能テスト
- 数量変更機能テスト
- 商品削除機能テスト
- 複数商品追加テスト
- チェックアウト遷移テスト
- カート永続化テスト

場所: `src/test/example/ShoppingCart.spec.js`

## 🔧 テスト仕様書の生成

### 基本的な使い方

```bash
# Playwrightテストを含むディレクトリを指定
node src/index.js \
  --source-dir ./tests \
  --output ./test_specification.xlsx \
  --no-coverage
```

### Playwrightテスト結果との統合

Playwrightのテスト結果JSONを統合する場合：

```bash
# 1. Playwrightテストを実行（JSON出力）
npx playwright test --reporter=json

# 2. テスト仕様書を生成
node src/index.js \
  --source-dir ./tests \
  --test-results ./playwright-results.json \
  --output ./test_specification.xlsx \
  --csv-output
```

## 📊 生成される出力

### Excel（テスト詳細シート）

19列のテスト仕様書が生成されます：

| 列名 | 内容 |
|------|------|
| FQN | テストファイルのフルパス |
| ソフトウェア・サービス | JSDocから取得 |
| 項目名 | JSDocから取得 |
| 試験内容 | JSDocから取得 |
| 確認項目 | JSDocから取得 |
| テスト実施実績日 | テスト実行日 |
| テスト結果 | OK/NG |
| テスト実施者 | CI |
| テスト検証者 | （空欄） |
| 申し送り有無 | （空欄） |
| 申し送りテスト実施タイミング | （空欄） |
| 申し送りテスト実施時期(予定) | （空欄） |
| 備考 | （空欄） |
| テスト対象モジュール名 | JSDocから取得 |
| テスト実施ベースラインバージョン | JSDocから取得 |
| テストケース作成者 | JSDocから取得 |
| テストケース作成日 | JSDocから取得 |
| テストケース修正者 | JSDocから取得 |
| テストケース修正日 | JSDocから取得 |

### CSV出力

2つのCSVファイルが生成されます：
- `*_test_details.csv` - テスト詳細
- `*_coverage.csv` - カバレッジ情報（オプション）

## 🎯 Playwrightテストのベストプラクティス

### 1. JSDocアノテーションを必ず記述

すべての`test()`の前にJSDocコメントを記述してください。

### 2. テストケース名は明確に

```javascript
// 良い例
test('ログイン機能 - 正常系', async ({ page }) => { ... });

// 悪い例
test('test1', async ({ page }) => { ... });
```

### 3. describe()でグループ化

関連するテストは`test.describe()`でグループ化できます：

```javascript
import { test, expect } from '@playwright/test';

test.describe('ログイン機能', () => {
  /**
   * @ソフトウェア・サービス 認証システム
   * @項目名 正常ログイン
   * ...
   */
  test('正常系', async ({ page }) => { ... });

  /**
   * @ソフトウェア・サービス 認証システム
   * @項目名 無効な認証情報
   * ...
   */
  test('異常系', async ({ page }) => { ... });
});
```

### 4. Page Objectパターンの使用

複雑なテストではPage Objectパターンを使用してください：

```javascript
// pages/LoginPage.js
export class LoginPage {
  constructor(page) {
    this.page = page;
  }

  async login(username, password) {
    await this.page.fill('[data-testid="username"]', username);
    await this.page.fill('[data-testid="password"]', password);
    await this.page.click('[data-testid="login-button"]');
  }
}

// tests/login.spec.js
import { test } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';

/**
 * @ソフトウェア・サービス 認証システム
 * @項目名 ログイン機能
 * ...
 */
test('ログインテスト', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.login('user', 'pass');
});
```

## 🔍 トラブルシューティング

### Playwrightテストが認識されない

- ファイル名が `*.spec.js` または `*.test.js` のパターンになっているか確認
- `--source-dir` オプションで正しいディレクトリを指定しているか確認

### JSDocアノテーションが読み込まれない

- JSDocコメントが `test()` または `it()` の直前に配置されているか確認
- `/**` で開始し `*/` で終了しているか確認（`//` や `/*` ではない）

### テスト結果が統合されない

- Playwrightのレポーター設定でJSON出力を有効にしているか確認
- `--test-results` オプションで正しいJSONファイルパスを指定しているか確認

## 📚 参考情報

- [Playwright公式ドキュメント](https://playwright.dev/)
- [Playwrightテスト作成ガイド](https://playwright.dev/docs/writing-tests)
- [Playwrightベストプラクティス](https://playwright.dev/docs/best-practices)

## 💡 追加機能

### Playwrightカバレッジの取得

Playwrightでカバレッジを取得する場合は、以下の設定を追加してください：

```javascript
// playwright.config.js
export default defineConfig({
  use: {
    // カバレッジ取得を有効化
    coverage: {
      enabled: true,
      include: ['src/**/*.js'],
      exclude: ['tests/**/*.spec.js'],
    },
  },
});
```

### CI/CDとの統合

GitHub Actionsの例：

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npx playwright test --reporter=json
      - run: node src/index.js --source-dir ./tests --test-results ./playwright-results.json --output ./test_specification.xlsx
      - uses: actions/upload-artifact@v3
        with:
          name: test-specification
          path: test_specification.xlsx
```

---

**質問やフィードバックがあれば、Issueを作成してください！**
