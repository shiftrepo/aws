# スタンドアロン実行ガイド

このドキュメントでは、コンテナを使わずに実行可能JARファイルを使って、Java Test Specification Generatorをスタンドアロンで実行する方法を説明します。

## 必要な環境

- **Java 17以上** (JDK)
- 実行可能JARファイル: `java-test-specification-generator-1.0.0.jar`

## JARファイルの取得

### 方法1: リポジトリから取得

```bash
# リポジトリをクローン
git clone <repository-url>
cd java-test-specs

# ビルド（Maven必要）
mvn clean compile test package

# JARファイルの場所
# target/java-test-specification-generator-1.0.0.jar
```

### 方法2: ビルド済みJARを直接取得

```bash
# リポジトリのtarget/ディレクトリから
# java-test-specification-generator-1.0.0.jar をコピー
```

## 基本的な使用方法

### 1. ヘルプの表示

```bash
java -jar java-test-specification-generator-1.0.0.jar --help
```

### 2. CSV出力付き

```bash
java -jar java-test-specification-generator-1.0.0.jar \
  --source-dir . \
  --output test_specification.xlsx \
  --csv-output
```

**説明:**
- `--source-dir` : **プロジェクトルート**を指定（`.` または絶対パス）
- `--output` : 生成するExcelファイルのパス
- `--csv-output` : Excelに加えてCSVファイルも生成

### 3. カバレッジ統合版（推奨）

```bash
# ステップ1: カバレッジレポートを一時コピー
cp -r target/site/jacoco ./coverage-reports

# ステップ2: テスト仕様書を生成
java -jar java-test-specification-generator-1.0.0.jar \
  --source-dir . \
  --output test_specification.xlsx

# ステップ3: クリーンアップ
rm -rf coverage-reports
```

**説明:**
- ツールは `/target/` ディレクトリを自動除外するため、一時的に `coverage-reports` にコピー
- `--source-dir` には**プロジェクトルート**を指定（カバレッジレポートを検索するため）

### 4. デバッグモード

```bash
java -jar java-test-specification-generator-1.0.0.jar \
  --source-dir . \
  --output test_specification.xlsx \
  --log-level DEBUG
```

### 5. 対話モード

```bash
java -jar java-test-specification-generator-1.0.0.jar --interactive
```

対話的にパラメータを入力できます。

## 完全なワークフロー例

### ステップ1: ビルドとテスト実行（JaCoCoレポート生成）

```bash
# Mavenでビルド、テスト実行、JAR作成
mvn clean compile test package

# JaCoCoレポートの確認
ls -lh target/site/jacoco/jacoco.xml
```

### ステップ2: カバレッジレポートを一時コピー

```bash
# target除外対策として一時ディレクトリにコピー
cp -r target/site/jacoco ./coverage-reports

# 確認
ls -lh coverage-reports/jacoco.xml
```

### ステップ3: テスト仕様書の生成

```bash
# プロジェクトルートを指定して実行
java -jar target/java-test-specification-generator-1.0.0.jar \
  --source-dir . \
  --output test_specification.xlsx

# 期待される出力:
# ✅ Javaファイル発見: 16個
# ✅ テストケース抽出: 35個
# ✅ カバレッジデータ取得: 166個
# ✅ テスト仕様書が正常に生成されました
```

### ステップ4: 生成されたExcelファイルの確認

```bash
# ファイルサイズと内容を確認
ls -lh test_specification.xlsx
# 期待されるサイズ: 約20-21KB
```

### ステップ5: クリーンアップ

```bash
# 一時ファイルを削除
rm -rf coverage-reports
```

## 別環境への移行

### 1. 必要なファイル

以下のファイルを別環境にコピーします：

```
java-test-specification-generator-1.0.0.jar  # 実行可能JAR
```

### 2. 別環境での実行

```bash
# Java 17以上がインストールされていることを確認
java -version

# 対象プロジェクトに移動
cd /path/to/target/project

# 標準的な実行（カバレッジ統合版）
cp -r target/site/jacoco ./coverage-reports
java -jar /path/to/jar/java-test-specification-generator-1.0.0.jar \
  --source-dir . \
  --output test_specification.xlsx
rm -rf coverage-reports

# CSV出力も含む版
cp -r target/site/jacoco ./coverage-reports
java -jar /path/to/jar/java-test-specification-generator-1.0.0.jar \
  --source-dir . \
  --output test_specification.xlsx \
  --csv-output
rm -rf coverage-reports
```

## コマンドラインオプション一覧

| オプション | 短縮形 | 引数 | 説明 |
|-----------|--------|------|------|
| `--source-dir` | `-s` | directory | **プロジェクトルート**のディレクトリ（必須）<br>例: `.` または `/path/to/project` |
| `--output` | `-o` | file | 出力Excelファイルのパス（必須） |
| `--csv-output` | - | - | CSV形式でのテスト仕様書も生成（Excel出力に追加） |
| `--log-level` | - | level | ログレベル (DEBUG/INFO/WARN/ERROR) |
| `--interactive` | `-i` | - | 対話モードで実行 |
| `--help` | `-h` | - | ヘルプメッセージを表示 |
| `--version` | `-v` | - | バージョン情報を表示 |

**重要**:
- **標準的な使用法**: `--source-dir .` でテスト + カバレッジ + 実行結果を取得
- **CSV出力付き**: `--source-dir . --csv-output` でExcelとCSV両方を生成
- カバレッジデータを含む完全な処理のため、必ずプロジェクトルートを指定してください

## トラブルシューティング

### エラー: Java version が古い

```bash
# Javaバージョンを確認
java -version

# Java 17以上が必要です
```

### エラー: カバレッジレポートが見つからない

```bash
# JaCoCoレポートが存在するか確認
ls -lh target/site/jacoco/jacoco.xml

# 存在しない場合はテストを実行
mvn clean test
```

### エラー: Javaファイルが見つからない

```bash
# プロジェクトルートにいることを確認
pwd
ls -lh src/test/java/

# プロジェクトルート（カレントディレクトリ）を指定
java -jar java-test-specification-generator-1.0.0.jar \
  --source-dir . \
  --output test_specification.xlsx

# または絶対パスでプロジェクトルートを指定
java -jar java-test-specification-generator-1.0.0.jar \
  --source-dir /absolute/path/to/project \
  --output test_specification.xlsx
```

## 実行例

### 例1: 基本的な使用（完全なデータ）

```bash
$ java -jar java-test-specification-generator-1.0.0.jar \
    --source-dir . \
    --output my_test_spec.xlsx

📊 Java Test Specification Generator 開始
   バージョン: 1.0.0
   ソース: .
   出力: my_test_spec.xlsx
🔍 Step 1: Javaファイルスキャン開始...
✅ Javaファイル発見: 16個
📝 Step 2: アノテーション解析開始...
✅ テストケース抽出: 35個
📊 Step 4: Excelレポート生成開始...
✅ Excelレポート生成完了
============================================================
🎉 処理完了サマリー
============================================================
📁 Javaファイル処理: 16個
🧪 テストケース抽出: 35個
📈 カバレッジエントリ: 0個
⏱️ 処理時間: 2.765秒
📊 出力ファイル: my_test_spec.xlsx
📏 ファイルサイズ: 9,807バイト
============================================================
✅ テスト仕様書が正常に生成されました: my_test_spec.xlsx
```

### 例2: カバレッジ統合版（推奨）

```bash
# ステップ1: ビルドとテスト実行
$ mvn clean compile test package

# ステップ2: カバレッジレポートを一時コピー
$ cp -r target/site/jacoco ./coverage-reports

# ステップ3: テスト仕様書を生成
$ java -jar target/java-test-specification-generator-1.0.0.jar \
    --source-dir . \
    --output test_spec_with_coverage.xlsx

📊 Java Test Specification Generator 開始
   バージョン: 1.0.0
   ソース: .
   出力: test_spec_with_coverage.xlsx
🔍 Step 1: Javaファイルスキャン開始...
✅ Javaファイル発見: 16個
📝 Step 2: アノテーション解析開始...
✅ テストケース抽出: 35個
📈 Step 3: カバレッジレポート処理開始...
✅ カバレッジデータ取得: 166個
📊 Step 4: Excelレポート生成開始...
✅ Excelレポート生成完了
============================================================
🎉 処理完了サマリー
============================================================
📁 Javaファイル処理: 16個
🧪 テストケース抽出: 35個
📈 カバレッジエントリ: 166個
⏱️ 処理時間: 4.707秒
📊 出力ファイル: test_spec_with_coverage.xlsx
📏 ファイルサイズ: 20,913バイト
============================================================
✅ テスト仕様書が正常に生成されました: test_spec_with_coverage.xlsx

# ステップ4: クリーンアップ
$ rm -rf coverage-reports
```

## 出力されるExcelファイルの内容

生成されるExcelファイルには以下の情報が含まれます：

### Test Detailsシート（12列）
1. No. (番号)
2. **FQCN (完全修飾クラス名)** - package.ClassName.methodName形式
3. ソフトウェア・サービス
4. 項目名
5. 試験内容
6. 確認項目
7. テスト対象モジュール名
8. テスト実施ベースラインバージョン
9. テストケース作成者
10. テストケース作成日
11. テストケース修正者
12. テストケース修正日

### Summaryシート
- 処理統計（ファイル数、テストケース数）
- カバレッジ統計（全体カバレッジ率、ブランチカバレッジ）
- テスト実行結果
- 品質指標

### Coverageシート（17列）
- パッケージ、クラス、メソッド別のカバレッジ詳細
- **Test Class (テストクラス)** - テスト対象コードをカバーするテストクラス
- Branch、Instruction、Line、Method各カバレッジ
- C1カバレッジ（条件判定カバレッジ）
- カバレッジステータス（Excellent/Good/Fair/Poor）

### Configurationシート
- システム情報（Java版、OS、実行環境）
- 処理設定（ソースディレクトリ、出力ファイル）
- 処理タイムスタンプ

## よくある質問

### Q: JARファイルのサイズが大きい（約24MB）のはなぜですか？

A: すべての依存ライブラリ（Apache POI、JaCoCo解析など）が含まれた実行可能JARです。単一ファイルでどこでも実行できる利点があります。

### Q: CSV形式でも出力できますか？

A: はい、`--csv-output` オプションを使用してExcelとCSV両方を生成できます。

### Q: Windowsで実行できますか？

A: はい、Java 17以上がインストールされていれば実行できます。パスの区切り文字は `\` を使用してください。

### Q: 複数のプロジェクトを一度に処理できますか？

A: 各プロジェクトごとに個別に実行してください。

## サポート

問題が発生した場合は、`--log-level DEBUG` オプションで詳細ログを確認してください。

```bash
# デバッグモードでの実行例（完全なデータを取得）
java -jar java-test-specification-generator-1.0.0.jar \
  --source-dir . \
  --output test_spec.xlsx \
  --log-level DEBUG

# CSV出力も含めてデバッグ
java -jar java-test-specification-generator-1.0.0.jar \
  --source-dir . \
  --output test_spec.xlsx \
  --csv-output \
  --log-level DEBUG
```
