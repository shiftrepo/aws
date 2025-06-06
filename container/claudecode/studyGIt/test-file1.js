/**
 * 簡単な計算機能
 */

// 足し算
function add(a, b) {
  return a + b;
}

// 引き算
function subtract(a, b) {
  return a - b;
}

// 掛け算
function multiply(a, b) {
  return a * b;
}

// 割り算
function divide(a, b) {
  if (b === 0) {
    throw new Error("0で割ることはできません");
  }
  return a / b;
}

// モジュールのエクスポート
module.exports = {
  add,
  subtract,
  multiply,
  divide
};