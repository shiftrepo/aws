/**
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
};