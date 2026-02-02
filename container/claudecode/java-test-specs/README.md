# 📊 Java Test Specification Generator

**JavaテストファイルからExcelテスト仕様書を自動生成するJavaツール**

## 概要

Java Test Specification Generatorは、Javaテストファイルからカスタムアノテーションを抽出し、JaCoCoカバレッジレポートと統合して、C1（条件判定）カバレッジ分析を含む包括的なExcelテスト仕様書を自動生成するJavaツールです。

> **📋 移行完了**: 2026年1月7日に **PythonとVBA版から完全にJava版に移行** しました。現在はJava実装のみが提供されており、最新のJava 17技術スタックを採用して高性能と拡張性を実現しています。

### 🚀 主な特徴

- **☕ Java 17ベース**: 最新のJava技術で構築された高性能なツール
- **🔍 自動アノテーション解析**: Javaコメントブロックからカスタムアノテーションを抽出
- **📈 C1カバレッジ分析**: JaCoCoカバレッジレポートと統合した条件判定カバレッジメトリクス
- **📊 プロフェッショナルなExcelレポート**: 4シート構成の詳細分析レポート
- **🖥️ コマンドライン対応**: CLI実行と対話モードをサポート
- **🐧 Linuxサポート**: Ubuntu/Debian/CentOS/RHEL/Fedora対応
- **📂 再帰的スキャン**: プロジェクト全体のディレクトリ構造を自動処理
- **🏗️ Maven対応**: 標準的なJavaプロジェクト構造とビルドツール

## ⚡ クイックスタート（Javaコマンドベース） 🎯 推奨

**JARファイル1つで、どこでも実行可能！**

Java 17以上があれば、コンテナ不要で即座に使用開始できます。

### 📦 実行可能JARの準備

#### 方法1: 既存のJARを使用

このリポジトリには実行可能JARが含まれています：

```bash
# JARファイルの場所
target/java-test-specification-generator-1.0.0.jar (24MB)
```

#### 方法2: ソースからビルド（コンテナ不使用）

**前提条件:**
- Java 17以上（JDK）
- Maven 3.6以上

**ビルド手順:**

```bash
# 1. リポジトリをクローン（または既存のディレクトリに移動）
git clone <repository-url>
cd java-test-specs

# 2. Mavenでビルド（テスト実行とJARパッケージング）
mvn clean compile test package

# 3. 実行可能JARが生成されます
ls -lh target/java-test-specification-generator-1.0.0.jar
# -rw-r--r--. 1 user user 24M Jan 14 12:00 target/java-test-specification-generator-1.0.0.jar

# 4. すぐに使用可能
java -jar target/java-test-specification-generator-1.0.0.jar --help
```

**ビルドプロセス:**
- `mvn clean` - 以前のビルド成果物を削除
- `mvn compile` - Javaソースコードをコンパイル
- `mvn test` - JUnitテストを実行し、JaCoCoカバレッジレポートを生成
- `mvn package` - 実行可能JAR（すべての依存関係を含む）を作成

**注意:** Maven初回実行時は依存ライブラリのダウンロードに時間がかかります。

### 🚀 基本的な使い方

#### カバレッジなし（テストケース情報のみ）

```bash
# テスト仕様書を生成（カバレッジなし）
java -jar target/java-test-specification-generator-1.0.0.jar \
  --source-dir . \
  --output test_specification.xlsx \
  --no-coverage

# 出力例:
# ✅ Javaファイル発見: 16個
# ✅ テストケース抽出: 35個
# ✅ テスト仕様書が正常に生成されました: test_specification.xlsx
```

#### カバレッジ統合版（推奨）

**重要**: カバレッジデータを含める場合は以下の手順に従ってください：

```bash
# ステップ1: ビルドとテスト実行（JaCoCoレポート生成）
mvn clean compile test package

# ステップ2: カバレッジレポートを一時コピー（target除外対策）
cp -r target/site/jacoco ./coverage-reports

# ステップ3: テスト仕様書を生成（--source-dirにプロジェクトルートを指定）
java -jar target/java-test-specification-generator-1.0.0.jar \
  --source-dir . \
  --output test_specification.xlsx

# ステップ4: 一時ファイルをクリーンアップ
rm -rf coverage-reports

# 出力例:
# ✅ Javaファイル発見: 16個
# ✅ テストケース抽出: 35個
# ✅ カバレッジデータ取得: 166個
# ✅ テスト仕様書が正常に生成されました: test_specification.xlsx
```

**注意点**:
- `--source-dir` には**プロジェクトルート**（`.` または絶対パス）を指定してください
- `--source-dir ./src/test/java` とすると、カバレッジレポートが見つかりません
- ツールは `/target/` ディレクトリを自動除外するため、一時的に `coverage-reports` にコピーする必要があります

### 📁 サンプル出力結果

このリポジトリには2つの代表的なサンプルファイルが含まれています：

| ファイル | サイズ | 説明 |
|---------|--------|------|
| **test_specification_output.xlsx** | 9.2KB | Javaコマンドベースの出力例（日本語項目） |
| **test_specification_ja.xlsx** | 15KB | カバレッジ統合版の出力例（日本語項目） |

### 🎯 主な特徴

- **単一ファイル**: JARファイル1つで完結
- **依存関係不要**: すべてのライブラリが含まれています
- **環境非依存**: Java 17以上があればどこでも動作
- **柔軟な指定**: ソース、カバレッジ、出力先を自由に指定可能

### 🔧 利用可能なオプション

| オプション | 短縮形 | 説明 | デフォルト |
|-----------|--------|------|-----------|
| `--source-dir` | `-s` | ソースディレクトリ（**プロジェクトルート**を指定）（必須） | - |
| `--output` | `-o` | 出力Excelファイルのパス（必須） | - |
| `--no-coverage` | - | カバレッジ処理をスキップ | false |
| `--log-level` | - | ログレベル（DEBUG/INFO/WARN/ERROR） | INFO |
| `--interactive` | `-i` | 対話モードで実行 | false |
| `--help` | `-h` | ヘルプメッセージを表示 | - |
| `--version` | `-v` | バージョン情報を表示 | - |

**重要な注意点**:
- `--source-dir` には**プロジェクトルート**を指定してください（例: `.` または `/path/to/project`）
- `--source-dir ./src/test/java` のようにテストディレクトリのみを指定すると、カバレッジレポートが見つかりません
- カバレッジを含める場合は、事前に `coverage-reports` ディレクトリを作成してください（上記の例を参照）

詳細は [STANDALONE_USAGE.md](STANDALONE_USAGE.md) を参照してください。

---

## 🐳 Dockerコンテナベース実行（カバレッジ生成含む）

Maven環境がない場合や、ビルドからカバレッジ生成まで一括実行したい場合はDockerを使用できます。

```bash
# 完全版ワンライナー: ビルド → テスト → カバレッジ → Excel生成 → クリーンアップ
docker run --rm \
  -v "$(pwd)":/workspace:Z \
  -w /workspace \
  maven:3.9-eclipse-temurin-17 \
  bash -c "mvn clean compile test package && \
           cp -r target/site/jacoco ./coverage-reports && \
           java -jar target/java-test-specification-generator-1.0.0.jar \
           --source-dir /workspace \
           --output test_specification.xlsx && \
           rm -rf coverage-reports"
```

**注**:
- Docker実行はビルドとテストを含むため時間がかかります（初回は依存関係のダウンロードで数分）
- 既にJARファイルがある場合は、上記のJavaコマンドベースの方が高速です
- SELinux環境では `:Z` オプションが必要です。非SELinux環境では削除してください

---

## 📁 プロジェクト構成

```
java-test-specs/
├── README.md                           # メイン説明書（このファイル）
├── pom.xml                             # Maven設定ファイル
├── .gitignore                          # Git除外設定
│
├── src/                                # Javaソースコード
│   ├── main/java/com/testspecgenerator/
│   │   ├── TestSpecificationGeneratorMain.java  # メインクラス
│   │   ├── model/                      # データモデル
│   │   │   ├── TestCaseInfo.java       # テストケース情報
│   │   │   └── CoverageInfo.java       # カバレッジ情報
│   │   └── core/                       # コア処理
│   │       ├── FolderScanner.java      # ディレクトリスキャン
│   │       ├── JavaAnnotationParser.java  # Javaアノテーション解析
│   │       ├── CoverageReportParser.java   # JaCoCoレポート解析
│   │       └── ExcelSheetBuilder.java  # Excel生成
│   ├── main/resources/
│   │   └── logback.xml                 # ログ設定
│   └── test/java/                      # JUnitテストケース（150アサーション）
│       ├── com/example/                # アノテーション付きテストサンプル
│       │   ├── BasicCalculatorTest.java    # 計算機テスト（C1カバレッジ含む）
│       │   └── StringValidatorTest.java    # 文字列検証テスト（条件分岐含む）
│       ├── com/testspecgenerator/core/
│       │   └── FolderScannerTest.java  # コアロジックテスト
│       └── com/testspecgenerator/
│           └── TestSpecificationGeneratorMainTest.java
│
└── target/                             # Maven生成ディレクトリ（ビルド後）
    ├── java-test-specification-generator-1.0.0.jar  # 実行可能JAR（24MB）
    └── site/jacoco/                    # JaCoCoカバレッジレポート
        ├── jacoco.xml                  # XMLレポート（114KB）⭐ 主要解析対象
        ├── index.html                  # HTMLメインレポート
        └── com.testspecgenerator.*/    # パッケージ別詳細レポート
```

## 🚀 クイックスタートガイド

### 📋 システム要件

- **Java 17以上** (JDK)
- **Apache Maven 3.6以上** (ビルドツール)
- **Javaテストファイル** （カスタムアノテーション付き）
- **JaCoCoカバレッジレポート** （オプション）

### 🔍 **事前環境チェック** ⚠️ **必須**

以下のコマンドで環境を確認してから開始してください：

```bash
# Java環境の確認
java -version
# 期待される出力例:
# openjdk version "17.0.x" 2023-xx-xx
# OpenJDK Runtime Environment (build 17.0.x+xx)
# OpenJDK 64-Bit Server VM (build 17.0.x+xx, mixed mode, sharing)

# Maven環境の確認
mvn --version
# 期待される出力例:
# Apache Maven 3.8.x (xxxxx)
# Maven home: /usr/share/maven
# Java version: 17.0.x, vendor: Eclipse Adoptium, runtime: /usr/lib/jvm/java-17-openjdk
```

#### ❌ **環境が整っていない場合**

**⚠️ 重要**: 以下のエラーが表示される場合は環境セットアップが必要です：

```bash
java -version
# ❌ エラー例:
# bash: java: command not found
# または
# java: command not found

mvn --version
# ❌ エラー例:
# bash: mvn: command not found
# または
# mvn: command not found
```

**📦 環境別インストール手順:**

##### **Ubuntu/Debian系**
```bash
# パッケージリストを更新
sudo apt update

# Java 17とMavenをインストール
sudo apt install openjdk-17-jdk maven

# インストール確認
java -version
mvn --version
```

##### **CentOS/RHEL/Fedora系**
```bash
# Java 17とMavenをインストール
sudo dnf install java-17-openjdk-devel maven

# インストール確認
java -version
mvn --version

# RHEL 8以前の場合
sudo yum install java-17-openjdk-devel maven
```

##### **🐳 Docker環境での実行（推奨・カバレッジレポート込み）**
```bash
# 【完全版】カバレッジ生成→テスト仕様書作成 ワンライナー実行
docker run --rm \
  -v "$(pwd)":/workspace:Z \
  -w /workspace \
  maven:3.9-eclipse-temurin-17 \
  bash -c "mvn clean compile test package && cp -r target/site/jacoco ./coverage-reports && java -jar target/java-test-specification-generator-1.0.0.jar --source-dir /workspace --output test_specification_complete.xlsx && rm -rf coverage-reports"

# またはステップごとに実行する場合:
# 1. ビルド・テスト・カバレッジ生成
docker run --rm \
  -v "$(pwd)":/workspace:Z \
  -w /workspace \
  maven:3.9-eclipse-temurin-17 \
  mvn clean compile test

# 2. 実行可能JAR作成
docker run --rm \
  -v "$(pwd)":/workspace:Z \
  -w /workspace \
  maven:3.9-eclipse-temurin-17 \
  mvn package

# 3. カバレッジレポートを一時コピー（target除外対策）
docker run --rm \
  -v "$(pwd)":/workspace:Z \
  -w /workspace \
  maven:3.9-eclipse-temurin-17 \
  cp -r target/site/jacoco ./coverage-reports

# 4. テスト仕様書生成（カバレッジ212エントリ統合）
docker run --rm \
  -v "$(pwd)":/workspace:Z \
  -w /workspace \
  maven:3.9-eclipse-temurin-17 \
  java -jar target/java-test-specification-generator-1.0.0.jar --source-dir /workspace --output test_specification.xlsx

# 5. 一時ファイル削除
rm -rf coverage-reports

# ⚠️ SELinux無効環境の場合（:Zを削除）
docker run --rm \
  -v "$(pwd)":/workspace \
  -w /workspace \
  maven:3.9-eclipse-temurin-17 \
  bash -c "mvn clean compile test package && cp -r target/site/jacoco ./coverage-reports && java -jar target/java-test-specification-generator-1.0.0.jar --source-dir /workspace --output test_specification.xlsx && rm -rf coverage-reports"
```

##### **🏢 企業環境・制限された環境での対処**
```bash
# 管理者権限がない場合のポータブル版使用

# 1. SDKMANを使用（Linux）
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"
sdk install java 17.0.9-tem
sdk install maven 3.9.6

# 2. 手動インストール（管理者権限不要）
# JDK 17ポータブル版をダウンロードし、JAVA_HOMEを設定
export JAVA_HOME=/path/to/portable/jdk-17
export PATH=$JAVA_HOME/bin:$PATH

# 3. Mavenポータブル版を設定
export M2_HOME=/path/to/portable/maven
export PATH=$M2_HOME/bin:$PATH
```

### ⚡ 5分で開始

#### **💻 ローカル環境での実行**
```bash
# 1. リポジトリをクローン
git clone https://github.com/shiftrepo/aws.git
cd aws/container/claudecode/java-test-specs

# 2. プロジェクトをビルド
mvn clean compile

# 3. JUnitテスト実行（オプション）
mvn test

# 4. 実行可能JARを作成
mvn package

# 5. サンプルデータで実行テスト
java -jar target/java-test-specification-generator-1.0.0.jar \
    --source-dir sample-java-tests \
    --output test_result.xlsx

# 6. 結果確認
ls -la test_result.xlsx
```

#### **🐳 Docker環境での実行（環境構築不要・カバレッジ完全版）**
```bash
# 1. リポジトリをクローン
git clone https://github.com/shiftrepo/aws.git
cd aws/container/claudecode/java-test-specs

# 2. カバレッジレポート生成→テスト仕様書作成 完全ワンライナー
docker run --rm \
  -v "$(pwd)":/workspace:Z \
  -w /workspace \
  maven:3.9-eclipse-temurin-17 \
  bash -c "mvn clean compile test package && cp -r target/site/jacoco ./coverage-reports && java -jar target/java-test-specification-generator-1.0.0.jar --source-dir /workspace --output test_specification_complete.xlsx && rm -rf coverage-reports"

# 3. 結果確認
ls -la test_specification_complete.xlsx
```

**実行結果例:**
```
📊 Java Test Specification Generator 開始
   バージョン: 1.0.0
   ソース: /workspace
   出力: test_specification_verification.xlsx

🔍 Step 1: Javaファイルスキャン開始...
✅ Javaファイル発見: 9個

📝 Step 2: アノテーション解析開始...
✅ テストケース抽出: 10個

📈 Step 3: カバレッジレポート処理開始...
✅ カバレッジデータ取得: 212個

📊 Step 4: Excelレポート生成開始...
✅ Excelレポート生成完了

============================================================
🎉 処理完了サマリー
============================================================
📁 Javaファイル処理: 9個
🧪 テストケース抽出: 10個
📈 カバレッジエントリ: 212個
⏱️ 処理時間: 2.297秒
📊 出力ファイル: test_specification_verification.xlsx
📏 ファイルサイズ: 17,373バイト
============================================================
✅ テスト仕様書が正常に生成されました: test_specification_verification.xlsx
```

## 📖 使用方法

### コマンドライン実行

#### カバレッジ統合版（完全ワークフロー）

```bash
# ステップ1: ビルドとテスト実行
mvn clean compile test package

# ステップ2: カバレッジレポートを一時コピー
cp -r target/site/jacoco ./coverage-reports

# ステップ3: テスト仕様書を生成
java -jar target/java-test-specification-generator-1.0.0.jar \
    --source-dir . \
    --output test_specification.xlsx

# ステップ4: クリーンアップ
rm -rf coverage-reports
```

#### カバレッジなし

```bash
# カバレッジ処理をスキップ
java -jar target/java-test-specification-generator-1.0.0.jar \
    --source-dir . \
    --output test_specification.xlsx \
    --no-coverage
```

#### デバッグモード

```bash
# 詳細ログを出力
java -jar target/java-test-specification-generator-1.0.0.jar \
    --source-dir . \
    --output test_specification.xlsx \
    --log-level DEBUG
```

#### その他のコマンド

```bash
# 対話モード
java -jar target/java-test-specification-generator-1.0.0.jar --interactive

# ヘルプ表示
java -jar target/java-test-specification-generator-1.0.0.jar --help

# バージョン表示
java -jar target/java-test-specification-generator-1.0.0.jar --version
```

### スタンドアロン実行（別環境への移行）

JARファイルを別環境にコピーして独立実行できます。詳細は [STANDALONE_USAGE.md](STANDALONE_USAGE.md) を参照してください。

```bash
# JARファイルをコピー
cp target/java-test-specification-generator-1.0.0.jar /path/to/target/environment/

# 別環境で実行（カバレッジ統合版）
cd /path/to/target/project

# ステップ1: カバレッジレポートを一時コピー
cp -r target/site/jacoco ./coverage-reports

# ステップ2: テスト仕様書を生成
java -jar /path/to/target/environment/java-test-specification-generator-1.0.0.jar \
    --source-dir . \
    --output test_specification.xlsx

# ステップ3: クリーンアップ
rm -rf coverage-reports

# カバレッジなしで実行
java -jar /path/to/target/environment/java-test-specification-generator-1.0.0.jar \
    --source-dir . \
    --output test_specification.xlsx \
    --no-coverage
```

### Mavenライフサイクル

```bash
# プロジェクトのクリーン
mvn clean

# ソースコンパイル
mvn compile

# テスト実行
mvn test

# パッケージ作成（JAR生成）
mvn package

# JaCoCoカバレッジレポート生成（testと同時実行）
mvn clean compile test

# カバレッジレポート確認
ls -la target/site/jacoco/jacoco.xml

# 依存関係確認
mvn dependency:tree
```

### 対話モード実行

```bash
java -jar target/java-test-specification-generator-1.0.0.jar --interactive
```

対話モードでは以下を入力：
1. ソースディレクトリのパス
2. 出力Excelファイルのパス
3. カバレッジレポート処理の有無

## 📝 サポートされるアノテーション

JavaDocコメント内で以下のカスタムアノテーションを認識します。日本語アノテーションと英語アノテーションの両方をサポートしています。

### 日本語アノテーション（推奨）

```java
/**
 * @ソフトウェア・サービス 計算サービス
 * @項目名 条件分岐加算テスト
 * @試験内容 様々なパラメータで条件分岐を含む加算処理をテスト実行
 * @確認項目 すべての条件が検証チェックをパスすること
 * @テスト対象モジュール名 BasicCalculator
 * @テスト実施ベースラインバージョン 1.0.0
 * @テストケース作成者 開発者名
 * @テストケース作成日 2026-01-14
 * @テストケース修正者 レビュー担当者名
 * @テストケース修正日 2026-01-14
 */
@Test
public void testConditionalCalculation() {
    // C1 Coverage: 条件判定カバレッジ
    if (value > 0) {
        // 正の値の場合
        assertTrue(result > value);
    } else if (value < 0) {
        // 負の値の場合
        assertTrue(result > value);
    } else {
        // ゼロの場合
        assertEquals(1, result);
    }
}
```

### 英語アノテーション（後方互換性）

```java
/**
 * @TestModule CalculatorModule
 * @TestCase ConditionalAdditionTest
 * @BaselineVersion 1.0.0
 * @TestOverview Test addition with conditional branching
 * @TestPurpose Ensure proper handling of different input types
 * @TestProcess Execute tests with various parameters
 * @TestResults All conditions should pass validation checks
 * @Creator DeveloperName
 * @CreatedDate 2026-01-07
 * @Modifier ReviewerName
 * @ModifiedDate 2026-01-07
 * @TestCategory Unit
 * @Priority High
 * @Requirements REQ-001, REQ-002
 * @Dependencies Calculator.class
 */
```

**注意**: 日本語アノテーションが優先されます。英語アノテーションは後方互換性のために維持されています。

## 📈 カバレッジレポート対応

### 📍 JaCoCoカバレッジレポート生成場所

JaCoCoカバレッジレポートは以下の場所に自動生成されます：

```bash
# Maven test実行でJaCoCoレポートを生成
mvn clean compile test

# 生成されるカバレッジレポートファイル:
target/site/jacoco/
├── jacoco.xml                    # XMLレポート（114KB）⭐ メイン解析対象
├── jacoco.csv                    # CSVフォーマット
├── index.html                    # HTMLメインレポート
├── jacoco-sessions.html          # セッション情報（195KB）
└── com.testspecgenerator.*/      # パッケージ別詳細レポート
    ├── FolderScanner.java.html   # クラス別カバレッジ詳細
    └── JavaAnnotationParser.java.html
```

**🔍 重要**: 本ツールは `target/site/jacoco/jacoco.xml` を解析対象とし、212個のカバレッジエントリを自動統合します。

### JaCoCoXMLレポートサンプル

```xml
<?xml version="1.0" encoding="UTF-8"?>
<report name="JaCoCo Coverage Report">
  <package name="com.testspecgenerator.core">
    <class name="com/testspecgenerator/core/FolderScanner">
      <method name="scanForJavaFiles" line="25">
        <counter type="INSTRUCTION" missed="42" covered="717"/>
        <counter type="BRANCH" missed="8" covered="140"/>
        <counter type="LINE" missed="12" covered="88"/>
      </method>
    </class>
  </package>
</report>
```

### JaCoCoHTMLレポート

- `index.html` (メインレポート)
- `*coverage*.html` (カバレッジサマリー)

### Maven JaCoCo統合

```xml
<!-- pom.xmlに既に含まれている設定 -->
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.11</version>
    <executions>
        <execution>
            <goals>
                <goal>prepare-agent</goal>
            </goals>
        </execution>
        <execution>
            <id>report</id>
            <phase>test</phase>
            <goals>
                <goal>report</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

## 📊 出力Excelフォーマット

生成されるExcelファイルは4つのシートで構成：

### 1. Test Details シート

**列構成（12列）:**

| No. | FQCN (完全修飾クラス名) | ソフトウェア・サービス | 項目名 | 試験内容 | 確認項目 | テスト対象モジュール名 | テスト実施ベースラインバージョン | テストケース作成者 | テストケース作成日 | テストケース修正者 | テストケース修正日 |
|-----|----------------------|---------------------|--------|---------|---------|---------------------|--------------------------|-----------------|-----------------|-----------------|-----------------|
| 1 | com.example.BasicCalculatorTest.testAddition | 計算サービス | 加算テスト | 加算処理をテスト | 正常動作確認 | BasicCalculator | 1.0.0 | 開発者 | 2026-01-14 | レビュー担当 | 2026-01-14 |
| 2 | com.example.BasicCalculatorTest.testSubtraction | 計算サービス | 減算テスト | 減算処理をテスト | 正常動作確認 | BasicCalculator | 1.0.0 | 開発者 | 2026-01-14 | レビュー担当 | 2026-01-14 |

**特徴:**
- **FQCN列（2列目）**: 完全修飾クラス名（パッケージ名.クラス名.メソッド名）でテストケースを一意に識別
- **日本語項目**: ソフトウェア・サービス、項目名、試験内容、確認項目など
- **トレーサビリティ**: 作成者、作成日、修正者、修正日を記録

### 2. Summary シート
- 処理ファイル数: 16個
- テストケース数: 35個
- 全体C1カバレッジ: 97.8%
- カバー済みブランチ: 528/540
- 処理時間: 4.707秒
- カバレッジエントリ: 166個

### 3. Coverage シート

**列構成（17列）:**

| No. | Package | Class Name | Method Name | Source File | Test Class (テストクラス) | Branch Coverage % | Branch (Covered/Total) | ... |
|-----|---------|------------|-------------|-------------|------------------------|-------------------|------------------------|-----|
| 1 | com/example | BasicCalculator | add | BasicCalculator.java | com.example.BasicCalculatorTest | 100.0% | 2/2 | ... |
| 2 | com/example | DataStructures$MinHeap | bubbleUp | DataStructures.java | com.example.DataStructuresTest | 100.0% | 8/8 | ... |
| 3 | com/example | StringValidator | isValidEmail | StringValidator.java | com.example.StringValidatorTest | 95.8% | 23/24 | ... |

**特徴:**
- **Test Class列（6列目）**: テスト対象コードを検証しているテストクラスを表示
- **クラスレベルマッピング**: JaCoCoレポートに基づく正確なテストカバレッジ追跡
- **メソッドレベル詳細**: 各メソッドのブランチカバレッジ、命令カバレッジ、行カバレッジを表示
- **ステータス評価**: Excellent（95%以上）、Good（80-95%）、Fair（60-80%）、Poor（60%未満）

### 4. Configuration シート
- 処理設定とシステム情報
- Java版バージョン情報
- 実行パラメータ
- カバレッジファイルパス
- 処理タイムスタンプ

## 🏗️ 開発者向け情報

### Maven依存関係

- **Apache POI 5.2.5**: Excel操作
- **Jackson 2.16.1**: JSON/XML処理
- **JSoup 1.17.2**: HTMLパース
- **Commons CLI 1.6.0**: コマンドライン引数処理
- **SLF4J + Logback**: ログ処理
- **JUnit 5.10.1**: テストフレームワーク

### アーキテクチャ

```
TestSpecificationGeneratorMain (エントリーポイント)
├── FolderScanner (ファイルスキャン)
├── JavaAnnotationParser (アノテーション解析)
├── CoverageReportParser (カバレッジ解析)
└── ExcelSheetBuilder (Excel生成)
```

### カスタマイズ

プロジェクト設定は `pom.xml` で管理されており、以下をカスタマイズ可能：

- Javaバージョン（現在: Java 17）
- 依存ライブラリバージョン
- プラグイン設定
- ビルド設定

## 🛠️ トラブルシューティング

### 🚨 環境関連の問題

#### ❌ **問題1: Java環境が見つからない**

**エラーメッセージ:**
```bash
java -version
# bash: java: command not found
# または
# java: No such file or directory
```

**解決手順:**
```bash
# Step 1: 現在のシステム確認
uname -a
cat /etc/os-release

# Step 2: Javaの検索
which java
whereis java
ls /usr/lib/jvm/

# Step 3: 環境別インストール（前述の「環境が整っていない場合」を参照）

# Step 4: 環境変数の確認と設定
echo $JAVA_HOME
echo $PATH

# 手動設定が必要な場合
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

# 永続化（.bashrcまたは.profileに追加）
echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> ~/.bashrc
echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

#### ❌ **問題2: Maven環境が見つからない**

**エラーメッセージ:**
```bash
mvn --version
# bash: mvn: command not found
# または
# mvn: No such file or directory
```

**解決手順:**
```bash
# Step 1: Mavenの検索
which mvn
whereis maven
ls /usr/share/maven/

# Step 2: 手動インストール（管理者権限がない場合）
cd /tmp
wget https://archive.apache.org/dist/maven/maven-3/3.9.6/binaries/apache-maven-3.9.6-bin.tar.gz
tar xzf apache-maven-3.9.6-bin.tar.gz
sudo mv apache-maven-3.9.6 /opt/maven

# Step 3: 環境変数設定
export M2_HOME=/opt/maven
export MAVEN_HOME=/opt/maven
export PATH=$M2_HOME/bin:$PATH

# Step 4: 永続化
echo 'export M2_HOME=/opt/maven' >> ~/.bashrc
echo 'export PATH=$M2_HOME/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# Step 5: 確認
mvn --version
```

### 🔧 ビルドとコンパイル関連の問題

#### ❌ **問題3: ビルドエラー**

**エラー1**: `JAVA_HOME is not set`
```bash
# 解決方法
java -version  # Javaは動作する
echo $JAVA_HOME  # 空の場合は設定が必要

# JAVA_HOMEを正しく設定
export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))
echo $JAVA_HOME
```

**エラー2**: `Project build error: Non-resolvable parent POM`
```bash
# 解決方法: pom.xmlの確認と修正
mvn clean
mvn validate  # pom.xmlの構文チェック
mvn help:effective-pom  # 実効POMの確認
```

**エラー3**: `Failed to execute goal org.apache.maven.plugins:maven-compiler-plugin`
```bash
# 解決方法: Javaバージョンの確認
java -version  # Java 17が必要
javac -version  # コンパイラの確認

# pom.xmlでJavaバージョンを確認
grep -A5 -B5 "maven.compiler" pom.xml
```

#### ❌ **問題4: 依存関係エラー**

**エラー**: `Could not resolve dependencies`
```bash
# Step 1: ローカルリポジトリのクリア
rm -rf ~/.m2/repository
mvn clean

# Step 2: 依存関係の強制更新
mvn clean compile -U

# Step 3: オフラインモードの確認
mvn dependency:resolve
mvn dependency:tree

# Step 4: プロキシ設定が必要な環境
# ~/.m2/settings.xmlを作成
mkdir -p ~/.m2
cat > ~/.m2/settings.xml << EOF
<?xml version="1.0" encoding="UTF-8"?>
<settings>
    <proxies>
        <proxy>
            <id>http-proxy</id>
            <active>true</active>
            <protocol>http</protocol>
            <host>proxy.example.com</host>
            <port>8080</port>
        </proxy>
    </proxies>
</settings>
EOF
```

### 📂 実行時の問題

#### ❌ **問題5: ファイルアクセスエラー**

**エラー**: `java.nio.file.AccessDeniedException`
```bash
# 解決方法1: ファイルロック確認
lsof test_result.xlsx  # Linuxの場合
# Excelなどで開かれているファイルを閉じる

# 解決方法2: 権限確認
ls -la test_result.xlsx
chmod 644 test_result.xlsx

# 解決方法3: 別ディレクトリで実行
mkdir -p /tmp/testgen
cd /tmp/testgen
java -jar /path/to/java-test-specification-generator-1.0.0.jar \
    --source-dir /path/to/sample-java-tests \
    --output test_result.xlsx
```

#### ❌ **問題6: メモリエラー**

**エラー**: `java.lang.OutOfMemoryError: Java heap space`
```bash
# 解決方法: JVMメモリ設定を増加
java -Xmx4g -jar target/java-test-specification-generator-1.0.0.jar \
    --source-dir sample-java-tests \
    --output test_result.xlsx

# 大規模プロジェクトの場合
java -Xms2g -Xmx8g -jar target/java-test-specification-generator-1.0.0.jar \
    --source-dir large-project \
    --output large_result.xlsx
```

### 📝 データ処理の問題

#### ❌ **問題7: アノテーションが認識されない**

**問題**: 「Not Specified」として表示される

**解決手順:**
```java
// ❌ 間違った形式
// @TestModule MyModule  <- スラッシュ2つのコメントは認識されない

/* @TestModule MyModule */  // <- ブロックコメントも認識されない

// ✅ 正しい形式（JavaDocコメント）
/**
 * @TestModule MyModule
 * @TestCase MyTestCase
 * @TestOverview このテストの概要説明
 */
@Test
public void testMethod() {
    // テスト実装
}
```

**確認方法:**
```bash
# アノテーション抽出のデバッグ
java -jar target/java-test-specification-generator-1.0.0.jar \
    --source-dir sample-java-tests \
    --output debug.xlsx \
    --log-level DEBUG

# ログファイルでアノテーション抽出状況を確認
grep "annotation" test_spec_generator.log
```

#### ❌ **問題8: カバレッジレポートが見つからない**

**エラー**: `Coverage files found: 0`

**解決手順:**
```bash
# Step 1: JaCoCoレポートファイルの確認
find . -name "*.xml" -path "*/jacoco*" 2>/dev/null
find . -name "*coverage*.xml" 2>/dev/null
find . -name "*coverage*.html" 2>/dev/null

# Step 2: JaCoCoレポートを生成（推奨方法）
mvn clean compile test

# Step 3: 生成されたファイルを確認
ls -la target/site/jacoco/jacoco.xml
# 期待される出力: -rw-r--r--. 1 user group 114443 Jan  7 06:43 target/site/jacoco/jacoco.xml

# Step 4: カバレッジ統合でテスト仕様書生成
# target除外対策として一時コピーしてから実行
cp -r target/site/jacoco ./coverage-reports
java -jar target/java-test-specification-generator-1.0.0.jar \
    --source-dir /path/to/project \
    --output test_result.xlsx
rm -rf coverage-reports
```

### 🏢 特殊環境での問題

#### ❌ **問題9: 企業プロキシ環境**

**エラー**: `Could not transfer artifact`
```bash
# 解決方法: Maven用プロキシ設定
mkdir -p ~/.m2
cat > ~/.m2/settings.xml << 'EOF'
<settings>
    <proxies>
        <proxy>
            <id>corporate-proxy</id>
            <active>true</active>
            <protocol>http</protocol>
            <host>proxy.company.com</host>
            <port>8080</port>
            <username>your-username</username>
            <password>your-password</password>
        </proxy>
    </proxies>
</settings>
EOF

# SSL証明書の問題がある場合
mvn clean compile -Dmaven.wagon.http.ssl.insecure=true -Dmaven.wagon.http.ssl.allowall=true
```

#### ❌ **問題10: コンテナ環境での実行**

**問題**: `Permission denied` や `ls: cannot open directory '.':`

**解決方法:**
```bash
# 1. SELinux環境での解決（:Z オプション追加）
docker run --rm \
  -v "$(pwd)":/workspace:Z \
  -w /workspace \
  maven:3.9-eclipse-temurin-17 \
  mvn clean package -DskipTests

# 2. SELinux状態の確認
getenforce
# Enforcingの場合は:Zオプションが必要

# 3. 権限問題の解決（ファイルアクセス）
chmod -R 755 .
docker run --rm \
  -v "$(pwd)":/workspace:Z \
  -w /workspace \
  maven:3.9-eclipse-temurin-17 \
  java -jar target/java-test-specification-generator-1.0.0.jar --source-dir sample-java-tests --output test_result.xlsx

# 4. 出力ファイル権限の修正
sudo chown $(id -u):$(id -g) test_result.xlsx
```

**TTYエラーが出る場合:**
```bash
# -itオプションを削除して実行
docker run --rm \
  -v "$(pwd)":/workspace:Z \
  -w /workspace \
  maven:3.9-eclipse-temurin-17 \
  bash -c "echo 'コンテナ内で実行中' && mvn --version"
```

### 📊 出力とログの問題

#### ❌ **問題11: Excel出力が正しくない**

**問題**: 空のExcelファイルや文字化け

**解決方法:**
```bash
# Step 1: Javaエンコーディング確認
java -Dfile.encoding=UTF-8 -jar target/java-test-specification-generator-1.0.0.jar \
    --source-dir sample-java-tests \
    --output test_result.xlsx

# Step 2: ファイル内容の確認
file test_result.xlsx
hexdump -C test_result.xlsx | head

# Step 3: ログでエラー詳細確認
tail -50 test_spec_generator.log
```

### 🔍 診断コマンド集

**包括的な環境診断:**
```bash
#!/bin/bash
echo "=== Java Test Spec Generator 環境診断 ==="
echo "日時: $(date)"
echo ""

echo "--- システム情報 ---"
uname -a
cat /etc/os-release 2>/dev/null || sw_vers 2>/dev/null || ver 2>/dev/null

echo ""
echo "--- Java環境 ---"
which java && java -version || echo "Java not found"
echo "JAVA_HOME: $JAVA_HOME"

echo ""
echo "--- Maven環境 ---"
which mvn && mvn --version || echo "Maven not found"
echo "M2_HOME: $M2_HOME"

echo ""
echo "--- ディスク容量 ---"
df -h .

echo ""
echo "--- 権限 ---"
ls -la .
whoami
id

echo ""
echo "--- ネットワーク（Maven用） ---"
ping -c 1 repo1.maven.org 2>/dev/null || echo "Maven repository unreachable"
```

### ログの確認

詳細なログファイル `test_spec_generator.log` が生成されます：

```bash
# ログファイルの確認
tail -f test_spec_generator.log

# デバッグモードでの実行
java -jar target/java-test-specification-generator-1.0.0.jar \
    --source-dir sample-java-tests \
    --output debug.xlsx \
    --log-level DEBUG
```

## 🔧 設定オプション

### 環境変数での設定

```bash
export TSG_SOURCE_DIR="/path/to/your/tests"
export TSG_OUTPUT_FILE="/path/to/output.xlsx"
export TSG_LOG_LEVEL="INFO"

java -jar target/java-test-specification-generator-1.0.0.jar  # 環境変数の設定が自動適用
```

### JVMオプション

```bash
# メモリ設定
java -Xmx2g -jar target/java-test-specification-generator-1.0.0.jar \
    --source-dir sample-java-tests \
    --output large_project.xlsx

# ログ設定のカスタマイズ
java -Dlogback.configurationFile=custom-logback.xml \
    -jar target/java-test-specification-generator-1.0.0.jar \
    --source-dir sample-java-tests \
    --output custom.xlsx
```

## ⚡ パフォーマンス

### ベンチマーク結果

| 項目 | Java版 | 特徴 |
|------|--------|------|
| **処理時間** | 0.3秒 | 高速処理 |
| **ファイル処理** | 2ファイル/0.3秒 | 並列処理対応 |
| **メモリ使用量** | 効率的 | JVM最適化 |
| **セットアップ** | mvn package のみ | 簡単ビルド |
| **拡張性** | 高い | Javaエコシステム |

## 🎯 対応フォーマット

### Javaアノテーション
```java
@TestModule, @TestCase, @BaselineVersion, @TestOverview,
@TestPurpose, @TestProcess, @TestResults, @Creator,
@CreatedDate, @Modifier, @ModifiedDate, @TestCategory,
@Priority, @Requirements, @Dependencies
```

### カバレッジフォーマット
- **JaCoCo XML**: `jacoco*.xml`, `*coverage*.xml`
- **JaCoCo HTML**: `index.html`, `*coverage*.html`
- **C1カバレッジ**: 条件判定カバレッジ分析
- **メソッドレベル**: 詳細分析サポート

## 🔄 バージョン情報

### Version 1.0.0 (Java版) - 2026-01-07 ⭐ **現在のバージョン**
- ✅ **完全Java実装**: 最新のJava 17技術スタック
- ⚡ **高速処理**: 0.3秒での処理実現
- 🖥️ **CLI対応**: コマンドライン実行サポート
- 🐧 **Linuxサポート**: Ubuntu/Debian/CentOS/RHEL/Fedora対応
- 🏗️ **Maven統合**: 標準的なJavaプロジェクト構造
- 📊 **同等のExcel生成**: 4シート構成の詳細レポート
- 🧪 **JUnitテスト**: 包括的なテストカバレッジ
- 🔄 **PythonとVBA版からの完全移行**: 統一されたJava実装

### 📜 移行履歴

#### 🗂️ 廃止されたバージョン（2026年1月7日まで）
- **Python版 2.0.0**: 0.1秒での高速処理を実現したが、Javaエコシステムとの統合性向上のため廃止
- **VBA版 1.0.0**: Excel環境での直接実行を提供したが、クロスプラットフォーム対応のため廃止

#### 🎯 移行理由
- **統一性**: 単一のJava実装による一貫した開発・保守
- **拡張性**: Javaエコシステムを活用した機能拡張
- **保守性**: 標準的なMavenプロジェクト構造による長期サポート
- **パフォーマンス**: JVM最適化による安定した高速処理

---

## 📞 サポート・連絡先

### サポートリソース
- **Issue報告**: [GitHub Issues](https://github.com/shiftrepo/aws/issues)
- **使用方法質問**: README.mdの詳細ガイドを参照
- **機能要望**: 具体的な使用ケースと共に提案

### バグレポートに含める情報
- エラーメッセージとログファイル
- 実行コマンドと引数
- サンプルJavaファイル（可能であれば）
- システム情報（Java版、Maven版、OS）

---

*Java Test Specification Generator は、Javaテストケースからの自動テスト仕様書生成に実用的なソリューションを提供します。Java実装により高速処理とクロスプラットフォーム対応を実現し、JaCoCoカバレッジ分析統合でテストドキュメント自動化の包括的な機能を提供します。*