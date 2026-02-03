# 🏗️ Java Test Specification Generator - マルチモジュール対応実行ガイド

## 概要

Java Test Specification Generatorは、Mavenマルチモジュールプロジェクトに対応し、各モジュール個別のレポートと全体統合レポートの両方を自動生成できます。

## ✅ 前提条件

- Java 17以上
- Maven 3.6以上
- マルチモジュール構造のMavenプロジェクト
- 各モジュールにpom.xmlが存在

## 🏛️ マルチモジュールプロジェクト構造例

```
my-multimodule-project/          # プロジェクトルート
├── pom.xml                      # 親POM（<modules>要素を含む）
├── module-a/
│   ├── pom.xml
│   └── src/
│       ├── main/java/
│       └── test/java/           # テストファイルここにあり
├── module-b/
│   ├── pom.xml
│   └── src/
│       ├── main/java/
│       └── test/java/
└── services/
    └── user-service/
        ├── pom.xml
        └── src/
            ├── main/java/
            └── test/java/
```

**親pom.xml例:**
```xml
<project>
    <modules>
        <module>module-a</module>
        <module>module-b</module>
        <module>services/user-service</module>
    </modules>
</project>
```

## 🚀 基本的な実行方法

### 1. **完全ワンライナー実行（推奨）**

```bash
# マルチモジュール処理（カバレッジ生成込み）
java -jar target/java-test-specification-generator-1.0.0.jar \
  --project-root /path/to/multimodule-project \
  --output-dir /path/to/output-reports
```

### 2. **CSV出力込み**

```bash
# Excel + CSV両方生成
java -jar target/java-test-specification-generator-1.0.0.jar \
  --project-root /path/to/multimodule-project \
  --output-dir /path/to/output-reports \
  --csv-output
```

### 3. **デバッグモード**

```bash
# 詳細ログ出力
java -jar target/java-test-specification-generator-1.0.0.jar \
  --project-root /path/to/multimodule-project \
  --output-dir /path/to/output-reports \
  --log-level DEBUG
```

## 📁 出力構造

マルチモジュール実行時の出力ディレクトリ構造：

```
output-reports/
├── combined-report.xlsx              # 🎯 統合レポート（全モジュール）
├── combined-report_test_details.csv
├── combined-report_coverage.csv
├── module-a/                         # モジュール個別レポート
│   ├── report.xlsx
│   ├── report_test_details.csv
│   └── report_coverage.csv
├── module-b/
│   ├── report.xlsx
│   ├── report_test_details.csv
│   └── report_coverage.csv
├── user-service/                     # ネストモジュール（services/user-service → user-service）
│   ├── report.xlsx
│   ├── report_test_details.csv
│   └── report_coverage.csv
└── modules-summary.json              # 📊 処理サマリー
```

### **統合レポート（combined-report.xlsx）の特徴**

1. **Test Details シート**: 全モジュールのテスト + `Module Name`列
2. **Coverage シート**: 全モジュールのカバレッジ + `Module Name`列
3. **Summary シート**: 全体統計 + モジュール別統計
4. **Modules シート**: モジュール一覧と処理結果
5. **Configuration シート**: 実行設定情報

## 🔧 コマンドラインオプション

| オプション | 説明 | 必須 | 例 |
|-----------|------|------|-----|
| `--project-root` | マルチモジュールプロジェクトのルートディレクトリ | ✅ | `/path/to/project` |
| `--output-dir` | 出力ディレクトリ（サブフォルダが自動作成） | ✅ | `./reports` |
| `--csv-output` | CSV形式での出力も生成 | ❌ | - |
| `--log-level` | ログレベル（DEBUG/INFO/WARN/ERROR） | ❌ | `DEBUG` |

## 🎯 実行パターン別ガイド

### **パターン1: 現在のディレクトリがマルチモジュールルート**

```bash
# プロジェクトルートで実行
java -jar target/java-test-specification-generator-1.0.0.jar \
  --project-root . \
  --output-dir ./test-reports
```

### **パターン2: 別の場所にあるマルチモジュールプロジェクト**

```bash
# 絶対パス指定
java -jar target/java-test-specification-generator-1.0.0.jar \
  --project-root /home/user/projects/my-multimodule \
  --output-dir /home/user/reports/multimodule-analysis
```

### **パターン3: Docker環境での実行**

```bash
# Docker完全ワンライナー
docker run --rm \
  -v "/path/to/multimodule-project:/workspace:Z" \
  -v "/path/to/output:/output:Z" \
  maven:3.9-eclipse-temurin-17 \
  bash -c "cd /workspace && \
           mvn clean compile test jacoco:report package && \
           java -jar target/java-test-specification-generator-1.0.0.jar \
           --project-root . --output-dir /output"
```

## 🔍 マルチモジュール自動検出

ツールは以下の方法でマルチモジュールプロジェクトを自動検出します：

1. **pom.xml存在確認**: `--project-root`で指定されたディレクトリにpom.xmlがあるか
2. **モジュール要素検索**: `<project><modules><module>` 要素が存在するか
3. **モジュール構造検証**: 各モジュールディレクトリとpom.xmlが存在するか

## ⚠️ 重要な注意事項

### **1. カバレッジレポート生成**

マルチモジュールでカバレッジを含める場合：

```bash
# 各モジュールでカバレッジ生成が必要
mvn clean compile test jacoco:report

# または、ルートから一括実行
mvn clean compile test jacoco:report -P all-modules
```

### **2. パス指定について**

- `--project-root`: 親pom.xmlがある**ルートディレクトリ**を指定
- `--output-dir`: 出力先**ディレクトリ**を指定（ファイル名ではない）

### **3. 後方互換性**

既存の単一モジュールモードは完全に維持：

```bash
# 従来通りの単一モジュール実行
java -jar target/java-test-specification-generator-1.0.0.jar \
  --source-dir ./src/test/java \
  --output single-module-report.xlsx
```

## 🐛 トラブルシューティング

### **問題1: "not a Maven multi-module project"エラー**

**原因**: pom.xmlに`<modules>`要素がない、またはモジュールディレクトリが存在しない

**解決策**:
```bash
# pom.xmlの構造確認
grep -A 5 -B 5 "<modules>" pom.xml

# モジュールディレクトリの存在確認
ls -la module-a/ module-b/
```

### **問題2: カバレッジデータが0**

**原因**: 各モジュールでJaCoCoレポートが生成されていない

**解決策**:
```bash
# 各モジュールでカバレッジ生成
mvn clean compile test jacoco:report

# XMLレポート確認
find . -name "jacoco.xml" -path "*/target/site/jacoco/*"
```

### **問題3: 出力ディレクトリ権限エラー**

**原因**: 出力ディレクトリの作成/書き込み権限がない

**解決策**:
```bash
# ディレクトリ作成と権限設定
mkdir -p /path/to/output-reports
chmod 755 /path/to/output-reports
```

## 💡 ベストプラクティス

### **1. 推奨実行フロー**

```bash
# ステップ1: プロジェクトルートに移動
cd /path/to/multimodule-project

# ステップ2: 全モジュールビルドとカバレッジ生成
mvn clean compile test jacoco:report

# ステップ3: テスト仕様書生成
java -jar target/java-test-specification-generator-1.0.0.jar \
  --project-root . \
  --output-dir ./test-reports \
  --csv-output

# ステップ4: 結果確認
ls -la test-reports/
ls -la test-reports/*/
```

### **2. CI/CD統合例**

```yaml
# GitHub Actions例
- name: Generate Multi-Module Test Specification
  run: |
    mvn clean compile test jacoco:report
    java -jar target/java-test-specification-generator-1.0.0.jar \
      --project-root . \
      --output-dir ./test-reports \
      --csv-output

- name: Upload Test Reports
  uses: actions/upload-artifact@v3
  with:
    name: test-specifications
    path: test-reports/
```

### **3. レポート活用**

- **統合レポート**: プロジェクト全体のテスト状況把握
- **個別モジュールレポート**: モジュール固有の問題分析
- **CSV出力**: 外部ツールでの分析やGraphQL等への取り込み

## 🚀 パフォーマンス

- **並列処理**: 各モジュールが並列で処理される
- **メモリ効率**: モジュールごとの独立処理でメモリ使用量を最適化
- **処理時間**: 単一モジュールの約1.2-1.5倍（統合処理含む）

マルチモジュール機能により、大規模なMavenプロジェクトでも効率的にテスト仕様書を生成できます！