/**
 * 初期表示用のデフォルトファイル定義
 * アプリケーション起動時に自動的にリポジトリに追加される
 */

// チュートリアル用ファイル
const tutorialFile = `/**
 * Gitチュートリアル用のサンプルファイル
 * このファイルを使ってコンフリクトの解決方法を学びます
 */

// ユーザー情報クラス
class UserProfile {
  constructor(name, email, role) {
    this.name = name;
    this.email = email;
    this.role = role;
    this.createdAt = new Date();
  }

  // ユーザー情報を表示する
  displayInfo() {
    return \`名前: \${this.name}, メール: \${this.email}, 役割: \${this.role}\`;
  }

  // ユーザーの役割を更新する
  updateRole(newRole) {
    this.role = newRole;
    return \`役割を\${newRole}に更新しました\`;
  }
}

// 設定オプション
const CONFIG = {
  darkMode: false,
  language: 'ja',
  notifications: true,
  autoSave: true
};

// アプリケーション初期化関数
function initializeApp() {
  console.log('アプリケーションを初期化しています...');
  loadUserPreferences();
  return 'アプリケーションの初期化が完了しました';
}

// ユーザー設定読み込み関数
function loadUserPreferences() {
  console.log('ユーザー設定を読み込んでいます...');
  // ここに設定読み込みのコードが入ります
}

module.exports = {
  UserProfile,
  CONFIG,
  initializeApp
};`;

// テストファイル1 - 計算機能
const testFile1 = `/**
 * 簡単な計算機能
 */

// 2つの数値を足し算する
function add(a, b) {
  return a + b;
}

// 2つの数値を引き算する
function subtract(a, b) {
  return a - b;
}

// 2つの数値を掛け算する
function multiply(a, b) {
  return a * b;
}

// 2つの数値を割り算する
function divide(a, b) {
  if (b === 0) {
    throw new Error('0で割ることはできません');
  }
  return a / b;
}

// モジュールのエクスポート
module.exports = {
  add,
  subtract,
  multiply,
  divide
};`;

// テストファイル2 - 文字列操作
const testFile2 = `/**
 * 簡単な文字列操作機能
 */

// 文字列の反転
function reverseString(str) {
  return str.split('').reverse().join('');
}

// 大文字に変換
function toUpperCase(str) {
  return str.toUpperCase();
}

// 小文字に変換
function toLowerCase(str) {
  return str.toLowerCase();
}

// 文字数をカウント
function countCharacters(str) {
  return str.length;
}

// モジュールのエクスポート
module.exports = {
  reverseString,
  toUpperCase,
  toLowerCase,
  countCharacters
};`;

// ファイル名とその内容をマッピング
const DEFAULT_FILES = {
  'tutorial-file.js': tutorialFile,
  'test-file1.js': testFile1,
  'test-file2.js': testFile2
};

export default DEFAULT_FILES;