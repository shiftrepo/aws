# JARコマンド実行例の修正サマリー

## 修正日時
2026-02-02

## 問題点

README及びSTANDALONE_USAGE.mdのjarコマンド実行例に**重大な誤り**がありました：

### 問題のあった例（修正前）
```bash
# ❌ 問題あり: テストファイルのみ処理
java -jar target/java-test-specification-generator-1.0.0.jar \
  --source-dir ./src/test/java \
  --output test_specification.xlsx

# ❌ 存在しないオプション
java -jar target/java-test-specification-generator-1.0.0.jar \
  --source-dir ./src/test/java \
  --coverage-dir ./target/site/jacoco \
  --output test_specification.xlsx
```

### 問題点
1. `--source-dir ./src/test/java` - テストディレクトリのみを指定
   - カバレッジレポート（coverage-reports/jacoco.xml）が見つからない
   - Coverageシートにデータが出力されない
   - テストファイルの情報のみ処理される

2. `--coverage-dir` オプション - **存在しません**
   - ツールはこのオプションをサポートしていない
   - 使用しても効果なし

## 正しい実行方法

### カバレッジ統合版（推奨）
```bash
# ステップ1: ビルドとテスト実行
mvn clean compile test package

# ステップ2: カバレッジレポートを一時コピー
cp -r target/site/jacoco ./coverage-reports

# ステップ3: テスト仕様書を生成（プロジェクトルートを指定）
java -jar target/java-test-specification-generator-1.0.0.jar \
  --source-dir . \
  --output test_specification.xlsx

# ステップ4: クリーンアップ
rm -rf coverage-reports
```

### CSV出力付き
```bash
java -jar target/java-test-specification-generator-1.0.0.jar \
  --source-dir . \
  --output test_specification.xlsx \
  --csv-output
```

## 重要なポイント

### 1. --source-dir にはプロジェクトルートを指定
- ✅ 正: `--source-dir .`
- ✅ 正: `--source-dir /path/to/project`
- ❌ 誤: `--source-dir ./src/test/java`
- ❌ 誤: `--source-dir src/test/java`

### 2. target除外対策
ツールは `/target/` ディレクトリを自動除外するため：
- カバレッジレポートを `coverage-reports` に一時コピー
- 処理後に `coverage-reports` を削除

### 3. --coverage-dir オプションは存在しない
- このオプションはサポートされていません
- カバレッジレポートは自動検索されます

## 修正されたファイル

### 1. README.md
**修正箇所**:
- 🚀 基本的な使い方セクション
- コマンドライン実行セクション
- スタンドアロン実行セクション
- 利用可能なオプション表
- Dockerコンテナベース実行セクション

**主な変更**:
- `--source-dir` の正しい使用方法を明記
- カバレッジ統合版の完全なワークフローを追加
- `--coverage-dir` オプションを削除
- 重要な注意点を追加

### 2. STANDALONE_USAGE.md
**修正箇所**:
- 基本的な実行セクション
- カバレッジ統合版セクション
- 完全なワークフロー例
- 別環境への移行セクション
- コマンドラインオプション一覧
- 実行例（例1、例2）
- 出力されるExcelファイルの内容

**主な変更**:
- 全ての実行例を修正
- ステップバイステップのワークフローを追加
- `--coverage-dir` オプションを削除
- 正しい出力例を記載

## 検証結果

実際に以下のコマンドで動作確認済み：

```bash
# ビルド
mvn clean compile test package

# カバレッジレポートコピー
cp -r target/site/jacoco ./coverage-reports

# 実行
java -jar target/java-test-specification-generator-1.0.0.jar \
  --source-dir . \
  --output test_specification_mvn_build.xlsx

# クリーンアップ
rm -rf coverage-reports
```

**結果**:
- ✅ Javaファイル処理: 16個
- ✅ テストケース抽出: 35個
- ✅ カバレッジエントリ: 166個
- ✅ ファイルサイズ: 20,913バイト
- ✅ Test Detailsシート: 12列、36行
- ✅ Coverageシート: 17列、167行

## ユーザーへの影響

### 既存ユーザー
誤った実行例に従っていた場合：
- カバレッジデータが0個と表示されていた
- Coverageシートにヘッダーのみが出力されていた
- 本来の機能を利用できていなかった

### 修正後
- 正しい手順でカバレッジデータを統合可能
- 完全なExcelレポートが生成される
- 166個のカバレッジエントリが正しく出力される

---
修正者: Claude Sonnet 4.5
検証日: 2026-02-02
