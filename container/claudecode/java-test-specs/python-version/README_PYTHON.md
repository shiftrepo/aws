# 📊 Java Test Specification Generator (Python版)

**VBAマクロからPythonに移植されたテスト仕様書生成ツール**

## 概要

JavaテストファイルからカスタムアノテーションとJaCoCoカバレッジ情報を自動抽出し、包括的なExcelテスト仕様書を生成するPython版ツールです。VBAマクロ版と同等の機能を提供しながら、より高速で柔軟な処理を実現しています。

## ✨ 特徴

- **🔍 自動スキャン**: 指定ディレクトリからJavaテストファイルを再帰的に検索
- **📝 アノテーション抽出**: カスタムアノテーション（@TestModule, @TestCase等）を解析
- **📈 カバレッジ統合**: JaCoCoレポート（XML/HTML）からC1カバレッジを取得
- **📊 Excel生成**: プロフェッショナルな4シート構成のレポート作成
- **🖥️ CLI & 対話モード**: コマンドライン実行と対話型設定の両方をサポート
- **🚀 高速処理**: VBAよりも高速なファイル処理とパフォーマンス

## 📁 生成されるExcelレポート構成

| シート名 | 内容 |
|----------|------|
| **Test Details** | テストケースの詳細情報（アノテーション、カバレッジ、メタデータ） |
| **Summary** | 全体統計、処理時間、カバレッジサマリー |
| **Coverage** | メソッドレベルの詳細カバレッジ分析 |
| **Configuration** | 処理設定、システム情報、実行パラメータ |

## 🛠️ インストール

### 1. 依存関係のインストール

```bash
# 必要なPythonライブラリをインストール
pip install -r requirements.txt
```

### 2. 主要依存関係

- **openpyxl**: Excelファイル生成
- **beautifulsoup4**: HTMLカバレッジレポート解析
- **lxml**: XML処理の高速化

## 🚀 使用方法

### コマンドライン実行

```bash
# 基本的な使用方法
python main.py --source-dir /path/to/java/tests --output report.xlsx

# サンプルデータで実行
python main.py --source-dir ../sample-java-tests --output test_result.xlsx

# カバレッジ処理なしで実行
python main.py --source-dir ./tests --output report.xlsx --no-coverage

# デバッグモードで実行
python main.py --source-dir ./tests --output report.xlsx --log-level DEBUG
```

### 対話モード実行

```bash
# 対話型設定で実行
python main.py --interactive
```

対話モードでは以下を入力します：
1. ソースディレクトリのパス
2. 出力Excelファイルのパス
3. カバレッジレポート処理の有無

### コマンドライン引数

| 引数 | 短縮形 | 説明 | 例 |
|------|--------|------|-----|
| `--source-dir` | `-s` | Javaテストファイルのソースディレクトリ | `--source-dir /path/to/tests` |
| `--output` | `-o` | 出力Excelファイルのパス | `--output report.xlsx` |
| `--no-coverage` | - | カバレッジレポート処理をスキップ | `--no-coverage` |
| `--interactive` | `-i` | 対話モードで実行 | `--interactive` |
| `--log-level` | - | ログレベル (DEBUG/INFO/WARNING/ERROR) | `--log-level DEBUG` |
| `--version` | - | バージョン情報を表示 | `--version` |

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
public void testConditionalCalculation(int value) {
    // テストロジック
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

## 🎯 実行例

### 1. サンプルデータでの実行

```bash
cd python-version
python main.py --source-dir ../sample-java-tests --output sample_result.xlsx
```

**期待される出力:**
```
📊 Java Test Specification Generator (Python版) 開始
   バージョン: 2.0.0
   ソース: ../sample-java-tests
   出力: sample_result.xlsx

🔍 Step 1: Javaファイルスキャン開始...
✅ Javaファイル発見: 2個

📝 Step 2: アノテーション解析開始...
✅ テストケース抽出: 8個

📈 Step 3: カバレッジレポート処理開始...
✅ カバレッジデータ取得: 140個

📊 Step 4: Excelレポート生成開始...
✅ Excelレポート生成完了

🎉 処理完了サマリー
==========================================
📁 Javaファイル処理: 2個
🧪 テストケース抽出: 8個
📈 カバレッジエントリ: 140個
⏱️ 処理時間: 0:00:15
📊 出力ファイル: sample_result.xlsx
📏 ファイルサイズ: 12,543バイト
🎯 全体ブランチカバレッジ: 94.6%
==========================================
```

### 2. カスタムプロジェクトでの実行

```bash
# 実際のJavaプロジェクトで実行
python main.py \
  --source-dir /path/to/your/java/project/src/test/java \
  --output project_test_spec.xlsx \
  --log-level INFO
```

## 🔧 設定カスタマイズ

### 設定項目

プログラム内で以下の設定を調整できます：

```python
# src/data_types.py の ConfigurationSettings
class ConfigurationSettings:
    # パス設定
    source_directory: str = ""
    output_file_path: str = ""
    include_subdirectories: bool = True
    process_coverage_reports: bool = True

    # ファイルフィルタリング
    include_test_files: bool = True
    include_it_files: bool = True  # Integration Test
    exclude_abstract_classes: bool = True

    # 処理制限
    max_file_size: int = 10485760  # 10MB
    timeout_seconds: int = 30
    log_detail_level: str = "Detailed"
```

## 🐛 トラブルシューティング

### よくある問題と解決方法

#### 1. ファイル読み込みエラー

**エラー**: `UnicodeDecodeError`
**解決**: ファイルエンコーディングの自動検出を実装済み（UTF-8 → Shift_JIS → CP932）

#### 2. カバレッジレポートが見つからない

**エラー**: カバレッジデータが0個
**解決**:
- JaCoCoレポートファイルが正しい場所にあることを確認
- ファイル名パターン: `jacoco*.xml`, `*coverage*.xml`, `index.html`

#### 3. アノテーションが認識されない

**エラー**: テストケースは見つかるがアノテーション情報が「Not Specified」
**解決**:
- JavaDocコメント形式 `/** ... */` を使用
- アノテーション前に `@` を付ける
- サポートされるアノテーション名を確認

#### 4. Excel生成失敗

**エラー**: `ExcelGenerationError`
**解決**:
- 出力ディレクトリの書き込み権限を確認
- ファイルが他のアプリで開かれていないことを確認
- 十分なディスク容量があることを確認

### ログファイル確認

```bash
# 詳細ログを確認
tail -f test_spec_generator.log

# デバッグモードで実行
python main.py --source-dir ./tests --output debug.xlsx --log-level DEBUG
```

## 🆚 VBA版との比較

| 特徴 | VBA版 | Python版 |
|------|-------|----------|
| **実行環境** | Windows + Excel | クロスプラットフォーム |
| **処理速度** | 中程度 | 高速 |
| **セットアップ** | VBAモジュールインポート必要 | pip install のみ |
| **自動実行** | 手動ボタンクリック | コマンドライン/バッチ処理対応 |
| **エラーハンドリング** | 基本的 | 詳細なログとエラー追跡 |
| **拡張性** | 限定的 | 高い（Pythonエコシステム） |
| **出力品質** | Excel形式 | 同等のExcel形式 |

## 🔄 VBA版からの移行

### 1. 既存データの互換性
- 同じアノテーション形式をサポート
- 同じExcelシート構成を生成
- 同じJaCoCoレポート形式に対応

### 2. 移行手順
1. Python環境のセットアップ
2. 依存関係のインストール
3. 既存のJavaファイルとカバレッジレポートをそのまま使用
4. Python版で実行してExcelファイル生成

## 📋 開発者情報

- **Version**: 2.0.0 (Python版)
- **移植元**: VBA版 1.0.0
- **作成日**: 2026-01-07
- **対応言語**: Python 3.8+
- **ライセンス**: VBA版と同等

## 🤝 サポート

問題や質問がある場合は、以下の情報と共にお問い合わせください：

1. 実行コマンド
2. エラーメッセージ
3. ログファイル (`test_spec_generator.log`)
4. サンプルJavaファイル（可能であれば）

---

**🎉 VBA版と同等の機能をPythonで実現したテスト仕様書生成ツールをお楽しみください！**