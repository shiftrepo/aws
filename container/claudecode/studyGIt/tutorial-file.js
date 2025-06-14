/**
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
    return `名前: ${this.name}, メール: ${this.email}, 役割: ${this.role}`;
  }

  // ユーザーの役割を更新する
  updateRole(newRole) {
    this.role = newRole;
    return `役割を${newRole}に更新しました`;
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
};