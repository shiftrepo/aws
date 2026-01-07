# 📊 Java Test Specification Generator

**JavaテストファイルからExcelテスト仕様書を自動生成するJavaツール**

## 概要

Java Test Specification Generatorは、Javaテストファイルからカスタムアノテーションを抽出し、JaCoCoカバレッジレポートと統合して、C1（条件判定）カバレッジ分析を含む包括的なExcelテスト仕様書を自動生成するJavaツールです。

### 🚀 主な特徴

- **☕ Java 17ベース**: 最新のJava技術で構築された高性能なツール
- **🔍 自動アノテーション解析**: Javaコメントブロックからカスタムアノテーションを抽出
- **📈 C1カバレッジ分析**: JaCoCoカバレッジレポートと統合した条件判定カバレッジメトリクス
- **📊 プロフェッショナルなExcelレポート**: 4シート構成の詳細分析レポート
- **🖥️ コマンドライン対応**: CLI実行と対話モードをサポート
- **🌐 クロスプラットフォーム**: Windows/Linux/macOS対応
- **📂 再帰的スキャン**: プロジェクト全体のディレクトリ構造を自動処理
- **🏗️ Maven対応**: 標準的なJavaプロジェクト構造とビルドツール

## 📁 プロジェクト構成

```
java-test-specs/
├── README.md                           # メイン説明書（このファイル）
├── pom.xml                             # Maven設定ファイル
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
│   └── test/java/                      # JUnitテストケース
│
├── sample-java-tests/                  # サンプルデータ
│   ├── BasicCalculatorTest.java        # 計算機テスト（C1カバレッジ例）
│   ├── StringValidatorTest.java        # 文字列検証テスト
│   └── coverage-reports/               # JaCoCoカバレッジレポート
│       ├── jacoco-report.xml           # XMLフォーマット
│       └── coverage-summary.html       # HTMLフォーマット
│
├── examples/                           # 出力例
│   └── TestSpecification_Sample.xlsx  # 実際のExcel出力例
│
├── templates/                          # テンプレート
│   └── java-annotation-template.java  # アノテーション形式リファレンス
│
└── docs/                              # ドキュメント
    ├── user-guide.md                  # ユーザーガイド
    ├── annotation-standards.md        # アノテーション標準
    └── coverage-integration.md        # カバレッジ統合ガイド
```

## 🚀 クイックスタートガイド

### 📋 システム要件

- **Java 17以上** (JDK)
- **Apache Maven 3.6以上** (ビルドツール)
- **Javaテストファイル** （カスタムアノテーション付き）
- **JaCoCoカバレッジレポート** （オプション）

### ⚡ 5分で開始

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

**実行結果例:**
```
📊 Java Test Specification Generator 開始
   バージョン: 1.0.0
   ソース: sample-java-tests
   出力: test_result.xlsx

🔍 Step 1: Javaファイルスキャン開始...
✅ Javaファイル発見: 2個

📝 Step 2: アノテーション解析開始...
✅ テストケース抽出: 6個

📈 Step 3: カバレッジレポート処理開始...
✅ カバレッジデータ取得: 58個

📊 Step 4: Excelレポート生成開始...
✅ Excelレポート生成完了

🎉 処理完了サマリー
============================================================
📁 Javaファイル処理: 2個
🧪 テストケース抽出: 6個
📈 カバレッジエントリ: 58個
⏱️ 処理時間: 0.312秒
📊 出力ファイル: test_result.xlsx
📏 ファイルサイズ: 11,154バイト
🎯 全体ブランチカバレッジ: 94.6%
============================================================
```

## 📖 使用方法

### コマンドライン実行

```bash
# 基本的な使用方法
java -jar target/java-test-specification-generator-1.0.0.jar \
    --source-dir /path/to/java/tests \
    --output report.xlsx

# カバレッジ処理なし
java -jar target/java-test-specification-generator-1.0.0.jar \
    --source-dir sample-java-tests \
    --output report.xlsx \
    --no-coverage

# デバッグモード
java -jar target/java-test-specification-generator-1.0.0.jar \
    --source-dir sample-java-tests \
    --output report.xlsx \
    --log-level DEBUG

# 対話モード
java -jar target/java-test-specification-generator-1.0.0.jar --interactive

# ヘルプ表示
java -jar target/java-test-specification-generator-1.0.0.jar --help
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

# JaCoCoカバレッジレポート生成
mvn test jacoco:report

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

JavaDocコメント内で以下のカスタムアノテーションを認識します：

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

## 📈 カバレッジレポート対応

### JaCoCoXMLレポート

```xml
<?xml version="1.0" encoding="UTF-8"?>
<report name="JaCoCo Coverage Report">
  <package name="com.example.calculator">
    <class name="com/example/calculator/BasicCalculatorTest">
      <method name="testConditionalCalculation" line="25">
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
| No. | Class Name | Method Name | Test Module | Test Case | Coverage % | Branches (Covered/Total) |
|-----|------------|-------------|-------------|-----------|------------|---------------------------|
| 1 | BasicCalculatorTest | testConditionalCalculation | CalculatorModule | ConditionalAdditionTest | 100.0% | 8/8 |
| 2 | BasicCalculatorTest | testMultiplicationBranching | CalculatorModule | MultiplicationTest | 87.5% | 14/16 |

### 2. Summary シート
- 処理ファイル数: 2個
- テストケース数: 6個
- 全体C1カバレッジ: 94.6%
- カバー済みブランチ: 140/148
- 処理時間: 0.312秒

### 3. Coverage シート
| Class Name | Method Name | Branch Coverage % | Status |
|------------|-------------|-------------------|--------|
| BasicCalculatorTest | testConditionalCalculation | 100.0% | Excellent |
| StringValidatorTest | testEmailValidation | 95.8% | Excellent |

### 4. Configuration シート
- 処理設定とシステム情報
- Java版バージョン情報
- 実行パラメータ

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

### よくある問題と解決方法

#### 1. ビルドエラー

**エラー**: `JAVA_HOME is not set`
```bash
# 解決方法: Java環境を確認
java -version
echo $JAVA_HOME

# Java 17をインストール（Ubuntu/Debian）
sudo apt update
sudo apt install openjdk-17-jdk

# JAVA_HOMEを設定
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
```

#### 2. Maven依存関係エラー

**エラー**: 依存関係の解決に失敗
```bash
# 解決方法
mvn clean
mvn dependency:resolve
mvn compile
```

#### 3. ファイルアクセスエラー

**問題**: `PermissionError: [Errno 13] Permission denied`
```bash
# 解決方法
# 出力ファイルが他のアプリで開かれていないか確認
# または別のファイル名で実行
java -jar target/java-test-specification-generator-1.0.0.jar \
    --source-dir sample-java-tests \
    --output report2.xlsx
```

#### 4. アノテーションが認識されない

**問題**: テストケースは見つかるがアノテーション情報が「Not Specified」
```java
// 解決方法: JavaDocコメント形式を使用
/**
 * @TestModule YourModule
 * @TestCase YourTestCase
 */
@Test
public void yourTestMethod() { ... }
```

#### 5. カバレッジレポートが見つからない

**問題**: カバレッジデータが0個
```bash
# 解決方法: JaCoCoレポートファイルの確認
ls target/site/jacoco/jacoco.xml
# または
find . -name "*coverage*.xml"

# JaCoCoレポートを生成
mvn test jacoco:report
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

### Version 1.0.0 (Java版) - 2026-01-07
- ✅ **完全Java実装**: 最新のJava 17技術スタック
- ⚡ **高速処理**: 0.3秒での処理実現
- 🖥️ **CLI対応**: コマンドライン実行サポート
- 🌐 **クロスプラットフォーム**: Windows/Linux/macOS対応
- 🏗️ **Maven統合**: 標準的なJavaプロジェクト構造
- 📊 **同等のExcel生成**: 4シート構成の詳細レポート
- 🧪 **JUnitテスト**: 包括的なテストカバレッジ

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