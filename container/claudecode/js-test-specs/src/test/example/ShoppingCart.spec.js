/**
 * @file Playwright E2Eテストサンプル - ショッピングカート
 *
 * このファイルはE-Commerceサイトのショッピングカート機能をテストします。
 */

import { test, expect } from '@playwright/test';

/**
 * @ソフトウェア・サービス E-Commerce Webアプリケーション
 * @項目名 商品追加機能
 * @試験内容 商品詳細ページから商品をカートに追加し、カート内に正しく表示されることを確認
 * @確認項目 カートアイコンのバッジ数が増加し、カート内に追加した商品が表示されること
 * @テスト対象モジュール名 ShoppingCart
 * @テスト実施ベースラインバージョン 3.1.0
 * @テストケース作成者 E2Eテストチーム
 * @テストケース作成日 2026-02-12
 */
test('商品をカートに追加', async ({ page }) => {
  // 商品一覧ページに遷移
  await page.goto('https://example.com/products');

  // 商品をクリックして詳細ページに遷移
  await page.click('[data-testid="product-item-1"]');

  // 商品詳細ページであることを確認
  await expect(page).toHaveURL(/.*\/product\/1/);

  // カートに追加ボタンをクリック
  await page.click('[data-testid="add-to-cart"]');

  // カートバッジの数が1になることを確認
  await expect(page.locator('[data-testid="cart-badge"]')).toHaveText('1');

  // カートアイコンをクリック
  await page.click('[data-testid="cart-icon"]');

  // カートページに遷移
  await expect(page).toHaveURL(/.*\/cart/);

  // 追加した商品がカートに表示されることを確認
  await expect(page.locator('[data-testid="cart-item"]')).toBeVisible();
  await expect(page.locator('[data-testid="cart-item-name"]')).toContainText('商品名1');
});

/**
 * @ソフトウェア・サービス E-Commerce Webアプリケーション
 * @項目名 商品数量変更機能
 * @試験内容 カート内の商品数量を増減し、合計金額が正しく更新されることを確認
 * @確認項目 数量を増やすと合計金額が増加し、減らすと減少すること
 * @テスト対象モジュール名 ShoppingCart
 * @テスト実施ベースラインバージョン 3.1.0
 * @テストケース作成者 E2Eテストチーム
 * @テストケース作成日 2026-02-12
 */
test('カート内の商品数量を変更', async ({ page }) => {
  // 商品をカートに追加（準備）
  await page.goto('https://example.com/products');
  await page.click('[data-testid="product-item-1"]');
  await page.click('[data-testid="add-to-cart"]');

  // カートページに遷移
  await page.click('[data-testid="cart-icon"]');

  // 初期数量と金額を確認
  await expect(page.locator('[data-testid="item-quantity"]')).toHaveText('1');
  const initialPrice = await page.locator('[data-testid="total-price"]').textContent();

  // 数量を増やす
  await page.click('[data-testid="increase-quantity"]');

  // 数量が2になることを確認
  await expect(page.locator('[data-testid="item-quantity"]')).toHaveText('2');

  // 合計金額が2倍になることを確認（簡易チェック）
  const updatedPrice = await page.locator('[data-testid="total-price"]').textContent();
  expect(updatedPrice).not.toBe(initialPrice);

  // 数量を減らす
  await page.click('[data-testid="decrease-quantity"]');

  // 数量が1に戻ることを確認
  await expect(page.locator('[data-testid="item-quantity"]')).toHaveText('1');

  // 合計金額が元に戻ることを確認
  await expect(page.locator('[data-testid="total-price"]')).toHaveText(initialPrice);
});

/**
 * @ソフトウェア・サービス E-Commerce Webアプリケーション
 * @項目名 商品削除機能
 * @試験内容 カート内の商品を削除し、カートから正しく削除されることを確認
 * @確認項目 削除ボタンをクリックすると商品がカートから削除され、カートバッジの数が減少すること
 * @テスト対象モジュール名 ShoppingCart
 * @テスト実施ベースラインバージョン 3.1.0
 * @テストケース作成者 E2Eテストチーム
 * @テストケース作成日 2026-02-12
 */
test('カートから商品を削除', async ({ page }) => {
  // 商品をカートに追加（準備）
  await page.goto('https://example.com/products');
  await page.click('[data-testid="product-item-1"]');
  await page.click('[data-testid="add-to-cart"]');

  // カートページに遷移
  await page.click('[data-testid="cart-icon"]');

  // 商品が1つあることを確認
  await expect(page.locator('[data-testid="cart-item"]')).toBeVisible();
  await expect(page.locator('[data-testid="cart-badge"]')).toHaveText('1');

  // 削除ボタンをクリック
  await page.click('[data-testid="remove-item"]');

  // 確認ダイアログで「はい」をクリック
  page.on('dialog', dialog => dialog.accept());

  // カートが空になることを確認
  await expect(page.locator('[data-testid="cart-empty-message"]')).toBeVisible();
  await expect(page.locator('[data-testid="cart-empty-message"]')).toContainText('カートは空です');

  // カートバッジが非表示になるか、0になることを確認
  await expect(page.locator('[data-testid="cart-badge"]')).not.toBeVisible();
});

/**
 * @ソフトウェア・サービス E-Commerce Webアプリケーション
 * @項目名 複数商品追加機能
 * @試験内容 異なる複数の商品をカートに追加し、すべて正しく表示されることを確認
 * @確認項目 カート内に追加したすべての商品が表示され、合計金額が正しく計算されること
 * @テスト対象モジュール名 ShoppingCart
 * @テスト実施ベースラインバージョン 3.1.0
 * @テストケース作成者 E2Eテストチーム
 * @テストケース作成日 2026-02-12
 */
test('複数の商品をカートに追加', async ({ page }) => {
  // 商品一覧ページに遷移
  await page.goto('https://example.com/products');

  // 1つ目の商品を追加
  await page.click('[data-testid="product-item-1"]');
  await page.click('[data-testid="add-to-cart"]');
  await page.goBack();

  // 2つ目の商品を追加
  await page.click('[data-testid="product-item-2"]');
  await page.click('[data-testid="add-to-cart"]');
  await page.goBack();

  // 3つ目の商品を追加
  await page.click('[data-testid="product-item-3"]');
  await page.click('[data-testid="add-to-cart"]');

  // カートバッジが3になることを確認
  await expect(page.locator('[data-testid="cart-badge"]')).toHaveText('3');

  // カートページに遷移
  await page.click('[data-testid="cart-icon"]');

  // 3つの商品がすべて表示されることを確認
  const cartItems = page.locator('[data-testid="cart-item"]');
  await expect(cartItems).toHaveCount(3);

  // 合計金額が表示されることを確認
  await expect(page.locator('[data-testid="total-price"]')).toBeVisible();
});

/**
 * @ソフトウェア・サービス E-Commerce Webアプリケーション
 * @項目名 チェックアウト遷移機能
 * @試験内容 カート内に商品がある状態でチェックアウトボタンをクリックし、チェックアウトページに遷移することを確認
 * @確認項目 チェックアウトページに遷移し、カート内の商品情報が表示されること
 * @テスト対象モジュール名 ShoppingCart
 * @テスト実施ベースラインバージョン 3.1.0
 * @テストケース作成者 E2Eテストチーム
 * @テストケース作成日 2026-02-12
 */
test('チェックアウトページへの遷移', async ({ page }) => {
  // 商品をカートに追加（準備）
  await page.goto('https://example.com/products');
  await page.click('[data-testid="product-item-1"]');
  await page.click('[data-testid="add-to-cart"]');

  // カートページに遷移
  await page.click('[data-testid="cart-icon"]');

  // チェックアウトボタンをクリック
  await page.click('[data-testid="checkout-button"]');

  // チェックアウトページに遷移することを確認
  await expect(page).toHaveURL(/.*\/checkout/);

  // 注文サマリーが表示されることを確認
  await expect(page.locator('[data-testid="order-summary"]')).toBeVisible();

  // カート内の商品情報が表示されることを確認
  await expect(page.locator('[data-testid="checkout-item"]')).toBeVisible();
});

/**
 * @ソフトウェア・サービス E-Commerce Webアプリケーション
 * @項目名 カート永続化機能
 * @試験内容 商品をカートに追加後、ページをリロードしても商品が残っていることを確認
 * @確認項目 ページリロード後もカート内の商品が保持されていること
 * @テスト対象モジュール名 ShoppingCart
 * @テスト実施ベースラインバージョン 3.1.0
 * @テストケース作成者 E2Eテストチーム
 * @テストケース作成日 2026-02-12
 */
test('カートの永続化（リロード後も保持）', async ({ page }) => {
  // 商品をカートに追加
  await page.goto('https://example.com/products');
  await page.click('[data-testid="product-item-1"]');
  await page.click('[data-testid="add-to-cart"]');

  // カートバッジが1になることを確認
  await expect(page.locator('[data-testid="cart-badge"]')).toHaveText('1');

  // ページをリロード
  await page.reload();

  // リロード後もカートバッジが1のままであることを確認
  await expect(page.locator('[data-testid="cart-badge"]')).toHaveText('1');

  // カートページに遷移
  await page.click('[data-testid="cart-icon"]');

  // 商品がまだカートに残っていることを確認
  await expect(page.locator('[data-testid="cart-item"]')).toBeVisible();
  await expect(page.locator('[data-testid="cart-item-name"]')).toContainText('商品名1');
});
