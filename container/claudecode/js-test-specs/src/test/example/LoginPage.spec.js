/**
 * @file Playwright E2Eテストサンプル - ログインページ
 *
 * このファイルはPlaywrightを使用したE2Eテストの例です。
 * JSDocアノテーションを使用してテスト仕様を記述します。
 */

import { test, expect } from '@playwright/test';

/**
 * @ソフトウェア・サービス Webアプリケーション認証システム
 * @項目名 ログイン機能 - 正常系
 * @試験内容 有効なユーザー名とパスワードでログインし、ダッシュボードに遷移することを確認
 * @確認項目 ログイン成功後、ダッシュボードページが表示され、ユーザー名が表示されること
 * @テスト対象モジュール名 LoginPage
 * @テスト実施ベースラインバージョン 2.0.0
 * @テストケース作成者 QAチーム
 * @テストケース作成日 2026-02-12
 */
test('正常なログイン処理', async ({ page }) => {
  // ログインページに遷移
  await page.goto('https://example.com/login');

  // ユーザー名とパスワードを入力
  await page.fill('[data-testid="username"]', 'testuser');
  await page.fill('[data-testid="password"]', 'password123');

  // ログインボタンをクリック
  await page.click('[data-testid="login-button"]');

  // ダッシュボードページへの遷移を確認
  await expect(page).toHaveURL(/.*dashboard/);

  // ユーザー名が表示されることを確認
  await expect(page.locator('[data-testid="user-name"]')).toContainText('testuser');
});

/**
 * @ソフトウェア・サービス Webアプリケーション認証システム
 * @項目名 ログイン機能 - 異常系（無効な認証情報）
 * @試験内容 無効なユーザー名またはパスワードでログインを試み、エラーメッセージが表示されることを確認
 * @確認項目 エラーメッセージ「ユーザー名またはパスワードが正しくありません」が表示されること
 * @テスト対象モジュール名 LoginPage
 * @テスト実施ベースラインバージョン 2.0.0
 * @テストケース作成者 QAチーム
 * @テストケース作成日 2026-02-12
 */
test('無効な認証情報でのログイン試行', async ({ page }) => {
  // ログインページに遷移
  await page.goto('https://example.com/login');

  // 無効なユーザー名とパスワードを入力
  await page.fill('[data-testid="username"]', 'invaliduser');
  await page.fill('[data-testid="password"]', 'wrongpassword');

  // ログインボタンをクリック
  await page.click('[data-testid="login-button"]');

  // エラーメッセージが表示されることを確認
  await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
  await expect(page.locator('[data-testid="error-message"]')).toContainText(
    'ユーザー名またはパスワードが正しくありません'
  );

  // ログインページに留まることを確認
  await expect(page).toHaveURL(/.*login/);
});

/**
 * @ソフトウェア・サービス Webアプリケーション認証システム
 * @項目名 ログイン機能 - バリデーション（必須項目）
 * @試験内容 ユーザー名またはパスワードが空の状態でログインボタンをクリックし、バリデーションエラーが表示されることを確認
 * @確認項目 ユーザー名とパスワードの両方が必須項目であることを示すエラーメッセージが表示されること
 * @テスト対象モジュール名 LoginPage
 * @テスト実施ベースラインバージョン 2.0.0
 * @テストケース作成者 QAチーム
 * @テストケース作成日 2026-02-12
 */
test('必須項目のバリデーション', async ({ page }) => {
  // ログインページに遷移
  await page.goto('https://example.com/login');

  // 何も入力せずにログインボタンをクリック
  await page.click('[data-testid="login-button"]');

  // バリデーションエラーが表示されることを確認
  await expect(page.locator('[data-testid="username-error"]')).toBeVisible();
  await expect(page.locator('[data-testid="username-error"]')).toContainText('ユーザー名は必須です');

  await expect(page.locator('[data-testid="password-error"]')).toBeVisible();
  await expect(page.locator('[data-testid="password-error"]')).toContainText('パスワードは必須です');
});

/**
 * @ソフトウェア・サービス Webアプリケーション認証システム
 * @項目名 ログアウト機能
 * @試験内容 ログイン後、ログアウトボタンをクリックし、ログインページに戻ることを確認
 * @確認項目 ログアウト後、ログインページにリダイレクトされ、認証が必要なページにアクセスできないこと
 * @テスト対象モジュール名 LoginPage
 * @テスト実施ベースラインバージョン 2.0.0
 * @テストケース作成者 QAチーム
 * @テストケース作成日 2026-02-12
 */
test('ログアウト処理', async ({ page }) => {
  // ログイン
  await page.goto('https://example.com/login');
  await page.fill('[data-testid="username"]', 'testuser');
  await page.fill('[data-testid="password"]', 'password123');
  await page.click('[data-testid="login-button"]');

  // ダッシュボードページへの遷移を確認
  await expect(page).toHaveURL(/.*dashboard/);

  // ログアウトボタンをクリック
  await page.click('[data-testid="logout-button"]');

  // ログインページにリダイレクトされることを確認
  await expect(page).toHaveURL(/.*login/);

  // ダッシュボードに直接アクセスしようとすると、ログインページにリダイレクトされることを確認
  await page.goto('https://example.com/dashboard');
  await expect(page).toHaveURL(/.*login/);
});

/**
 * @ソフトウェア・サービス Webアプリケーション認証システム
 * @項目名 パスワード表示/非表示切り替え
 * @試験内容 パスワード入力欄の表示/非表示切り替えボタンが正常に動作することを確認
 * @確認項目 切り替えボタンをクリックするとパスワードがプレーンテキストとして表示され、再度クリックすると隠されること
 * @テスト対象モジュール名 LoginPage
 * @テスト実施ベースラインバージョン 2.0.0
 * @テストケース作成者 QAチーム
 * @テストケース作成日 2026-02-12
 */
test('パスワード表示切り替え', async ({ page }) => {
  // ログインページに遷移
  await page.goto('https://example.com/login');

  // パスワードを入力
  await page.fill('[data-testid="password"]', 'mypassword');

  // 初期状態でパスワードが隠されていることを確認
  await expect(page.locator('[data-testid="password"]')).toHaveAttribute('type', 'password');

  // 表示切り替えボタンをクリック
  await page.click('[data-testid="toggle-password"]');

  // パスワードがプレーンテキストとして表示されることを確認
  await expect(page.locator('[data-testid="password"]')).toHaveAttribute('type', 'text');

  // 再度切り替えボタンをクリック
  await page.click('[data-testid="toggle-password"]');

  // パスワードが再び隠されることを確認
  await expect(page.locator('[data-testid="password"]')).toHaveAttribute('type', 'password');
});
