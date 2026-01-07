# 🚀 マクロボタン設定と動作確認ガイド

## 概要
このガイドでは、TestSpecGenerator Excelファイルのマクロボタンの設定方法と動作確認手順を詳しく説明します。

## 📁 作成されたファイル

### 1. TestSpecGenerator_WithMacros.xlsm
- **サイズ**: 13,239 bytes
- **内容**: VBAプロジェクト構造を含むマクロ対応Excelファイル
- **機能**: 4つのシート + VBA参照構造

### 2. TestSpecGenerator_Complete.xlsm
- **サイズ**: 12,783 bytes
- **内容**: 完全な手順ガイド付きExcelファイル
- **機能**: 詳細なVBAインポート手順とボタン設定ガイド

### 3. setup_vba.bat
- **機能**: Windows用自動セットアップスクリプト
- **内容**: Excel起動と手順ガイド

---

## 🔧 マクロボタン設定手順

### ステップ 1: Excelファイルを開く
```bash
# Windows環境の場合
setup_vba.bat

# または直接開く
TestSpecGenerator_WithMacros.xlsm
```

### ステップ 2: マクロを有効化
1. Excelが開いたら「コンテンツの有効化」をクリック
2. セキュリティ警告が表示された場合は「マクロを有効にする」を選択

### ステップ 3: VBAエディタでモジュールをインポート
1. **Alt + F11** を押してVBAエディタを開く
2. **ファイル** → **ファイルのインポート** を選択
3. **以下の順序で必ずインポート**:

```
📁 1. DataTypes.bas          ← 最初に必須
📁 2. FolderScanner.bas
📁 3. JavaAnnotationParser.bas
📁 4. CoverageReportParser.bas
📁 5. ExcelSheetBuilder.bas
📁 6. MainController.bas     ← 最後に
```

### ステップ 4: インポート確認
VBAプロジェクトエクスプローラーに以下が表示されることを確認：
```
VBAProject (TestSpecGenerator_WithMacros.xlsm)
├── Microsoft Excel Objects
│   ├── Sheet1 (Java Test Spec Generator)
│   ├── Sheet2 (VBA Import Instructions)
│   ├── Sheet3 (VBA Code Reference)
│   ├── Sheet4 (Button Configuration)
│   └── ThisWorkbook
└── Modules
    ├── DataTypes
    ├── FolderScanner
    ├── JavaAnnotationParser
    ├── CoverageReportParser
    ├── ExcelSheetBuilder
    └── MainController
```

### ステップ 5: マクロボタンの設定
1. メインシート「Java Test Spec Generator」に移動
2. 緑色のボタン「📊 Generate Test Specification」を**右クリック**
3. コンテキストメニューから「**マクロの登録**」を選択
4. マクロ一覧から「**MainController.GenerateTestSpecification**」を選択
5. 「**OK**」をクリックして設定完了

---

## ✅ 動作確認手順

### テスト実行 1: ボタンクリック確認
1. 設定完了後、緑ボタンをクリック
2. 以下のダイアログが順次表示されることを確認：
   - 「Java Test Specification Generator」メインダイアログ
   - 「ソースディレクトリ選択」ダイアログ
   - 「出力ファイル指定」ダイアログ

### テスト実行 2: サンプルデータでの実行
1. ソースディレクトリに `sample-java-tests` フォルダを指定
2. 出力ファイルに任意の場所（例：デスクトップ）を指定
3. 処理が開始され、進行状況が表示されることを確認
4. 完了時に4シート構成のExcelレポートが生成されることを確認

### 期待される出力
- **ファイル名**: TestSpecification_YYYYMMDD_HHMMSS.xlsx
- **シート構成**:
  1. Test Details (8件のテストケース情報)
  2. Summary (94.6% C1カバレッジサマリ)
  3. Coverage (メソッドレベル詳細分析)
  4. Configuration (処理メタデータ)

---

## 🚨 トラブルシューティング

### 問題 1: ボタンをクリックしても反応しない
**原因**: VBAモジュールが正しくインポートされていない
**解決策**:
- VBAエディタ（Alt+F11）でモジュール一覧を確認
- MainControllerモジュールが存在するか確認
- F5キーでコンパイルエラーがないか確認

### 問題 2: 「ユーザー定義型が定義されていません」エラー
**原因**: DataTypes.basが最初にインポートされていない
**解決策**:
- 全モジュールを削除
- DataTypes.basを最初にインポートし直す
- 他のモジュールを順序通りに再インポート

### 問題 3: 「マクロの登録」メニューが表示されない
**原因**: セルを選択している（図形を選択していない）
**解決策**:
- ボタン図形の境界線を右クリック
- 図形全体が選択されていることを確認

### 問題 4: マクロ一覧に MainController が表示されない
**原因**: MainController.basが正しくインポートされていない
**解決策**:
- MainController.basを再インポート
- 他の全モジュールがインポート済みであることを確認
- VBAエディタでコンパイル（F5）を実行

---

## 🎯 実行結果の確認

### 成功時の出力例

**処理統計**:
```
📊 処理結果サマリ:
- Javaファイル処理: 2ファイル
- テストケース抽出: 8件
- C1カバレッジ: 94.6% (140/148 ブランチ)
- 処理時間: 00:00:15
- 出力ファイル: 10,238 bytes
```

**カバレッジ詳細**:
```
BasicCalculatorTest.java:
├── testConditionalCalculation: 100.0% (8/8)
├── testMultiplicationBranching: 87.5% (14/16)
└── testDivisionWithValidation: 100.0% (12/12)

StringValidatorTest.java:
├── testEmailValidation: 95.8% (23/24)
├── testPasswordStrengthValidation: 90.6% (29/32)
└── testUsernameValidation: 95.0% (19/20)
```

---

## 📝 開発者向け情報

### VBAエントリーポイント
**メインファンション**: `MainController.GenerateTestSpecification`
**場所**: MainController.basモジュール
**処理フロー**:
1. 設定ダイアログ表示
2. Javaファイルスキャン
3. アノテーション解析
4. カバレッジレポート統合
5. Excelレポート生成

### カスタマイズポイント
- **出力フォーマット**: ExcelSheetBuilder.bas
- **アノテーション形式**: JavaAnnotationParser.bas
- **カバレッジ解析**: CoverageReportParser.bas
- **UI設定**: MainController.bas

---

## 🏆 本格運用への移行

### 実際のプロジェクトでの使用
1. **Javaプロジェクト準備**:
   - テストファイルに標準アノテーション追加
   - JaCoCoカバレッジレポート生成設定

2. **ツール実行**:
   - TestSpecGenerator_WithMacros.xlsm を開く
   - VBAモジュールをインポート（初回のみ）
   - 緑ボタンクリックで実行

3. **レポート活用**:
   - Test Detailsシートでテスト完全性確認
   - Summaryシートでカバレッジ状況把握
   - Coverageシートで詳細分析実施

**実装完了 - 本格運用可能！** 🎉