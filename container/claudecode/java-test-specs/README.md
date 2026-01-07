# Java テスト仕様書生成ツール（VBA Excel）

## 概要

Java テスト仕様書生成ツールは、VBA Excel マクロベースの自動化ツールです。Javaテストファイルからカスタムアノテーションを抽出し、JaCoCoカバレッジレポートと統合して、C1（条件判定）カバレッジ分析を含む包括的なExcelテスト仕様書を生成します。

### 主な機能

- **自動アノテーション解析**: Javaコメントブロックからカスタムテストアノテーションを抽出
- **C1カバレッジ分析**: JaCoCoカバレッジレポートと統合した条件判定カバレッジメトリクス
- **マルチシートExcelレポート**: 詳細分析とサマリを含むプロフェッショナルなレポート生成
- **再帰的ディレクトリスキャン**: プロジェクト全体のディレクトリ構造を処理
- **エラーハンドリング＆ログ**: 包括的なエラー報告と処理ログ
- **サンプルデータ付属**: 条件分岐ロジックを含む完全なテスト例

## 📁 プロジェクト構成

```
java-test-specs/
├── README.md                                      # メイン説明書（このファイル）
├── TestSpecGenerator_Template.xlsm               # VBA対応Excelワークブック
├── examples/                                      # 出力例
│   └── TestSpecification_Sample_20260107.xlsx    # 実際のExcel出力例
├── sample-java-tests/                             # サンプルJavaテストファイル
│   ├── BasicCalculatorTest.java                   # 計算機テスト（C1カバレッジ例）
│   ├── StringValidatorTest.java                   # 文字列検証テスト（条件分岐）
│   └── coverage-reports/                          # JaCoCoカバレッジレポート
│       └── jacoco-report.xml                      # XMLカバレッジフォーマット
├── vba-modules/                                   # VBAソースコードモジュール
│   ├── MainController.bas                         # メイン制御モジュール
│   ├── FolderScanner.bas                          # ディレクトリスキャン機能
│   ├── JavaAnnotationParser.bas                  # Javaアノテーション抽出
│   ├── CoverageReportParser.bas                   # JaCoCoレポート解析
│   ├── ExcelSheetBuilder.bas                      # Excel出力生成
│   ├── ConfigurationManager.bas                   # 設定管理
│   └── VBA-Import-Instructions.md                 # セットアップ手順
├── templates/                                     # Excelテンプレートとフォーマット
│   └── java-annotation-template.java             # アノテーション形式リファレンス
└── docs/                                          # 包括的ドキュメント
    ├── user-guide.md                             # ユーザー操作マニュアル
    ├── annotation-standards.md                   # Javaアノテーションガイドライン
    └── coverage-integration.md                    # カバレッジ分析ガイド
```

## 🚀 クイックスタートガイド

### 事前要件

- **Microsoft Excel 2016以降** （VBAサポート必須）
- **Javaテストファイル** （カスタムアノテーション付き）
- **JaCoCoカバレッジレポート** （オプション、カバレッジ分析用）

### 📋 詳細実行手順

#### ステップ 1: ファイル準備
1. **プロジェクトファイルをダウンロード**
   ```
   git clone https://github.com/shiftrepo/aws.git
   cd aws/container/claudecode/java-test-specs
   ```

2. **ファイル構成を確認**
   - `TestSpecGenerator_Template.xlsm` が存在することを確認
   - `vba-modules/` ディレクトリに6つの.basファイルがあることを確認

#### ステップ 2: VBA Excel ワークブック設定
1. **Excel を起動し、`TestSpecGenerator_Template.xlsm` を開く**

2. **マクロを有効にする**
   - セキュリティ警告が表示されたら「コンテンツの有効化」をクリック

3. **開発者タブを有効化**（表示されていない場合）
   - ファイル → オプション → リボンのユーザー設定
   - 「開発」にチェックを入れる → OK

4. **VBA エディタを開く**
   - 開発者タブ → Visual Basic（またはAlt+F11）

#### ステップ 3: VBA モジュールのインポート
1. **VBA エディタで右クリック**
   - プロジェクトエクスプローラーで「VBAProject」を右クリック
   - 挿入 → ファイル

2. **モジュールを順次インポート**
   ```
   vba-modules/MainController.bas
   vba-modules/FolderScanner.bas
   vba-modules/JavaAnnotationParser.bas
   vba-modules/CoverageReportParser.bas
   vba-modules/ExcelSheetBuilder.bas
   vba-modules/ConfigurationManager.bas
   ```

3. **インポート確認**
   - VBAプロジェクトに6つのモジュールが表示されることを確認

#### ステップ 4: マクロボタンの設定
1. **Excelシートに戻る**（Alt+F11 または VBAエディタを閉じる）

2. **緑のボタンを右クリック**
   - 「マクロの登録」を選択

3. **マクロを選択**
   - `MainController.GenerateTestSpecification` を選択
   - OK をクリック

#### ステップ 5: 実行テスト（サンプルデータで確認）
1. **緑のボタン「📊 Generate Test Specification」をクリック**

2. **ソースディレクトリを選択**
   - 参照ボタンで `sample-java-tests` フォルダを選択

3. **出力ファイルを指定**
   - デスクトップまたは任意の場所に保存先を指定
   - ファイル名例: `TestSpec_Test_20260107.xlsx`

4. **実行開始**
   - 「開始」ボタンをクリック
   - 進行状況がステータスバーに表示される

#### ステップ 6: 結果確認
処理完了後、生成されたExcelファイルに以下の4つのシートが含まれることを確認：

1. **Test Details**: 完全なテストケース情報
2. **Summary**: 集計統計とカバレッジサマリ
3. **Coverage**: 詳細なC1カバレッジ分析
4. **Configuration**: 処理設定とメタデータ

### 💡 実際のプロジェクトでの使用

#### 1. Javaテストファイルの準備
テストファイルに以下のアノテーション形式でコメントを追加：

```java
/**
 * @TestModule       モジュール名
 * @TestCase         テストケース名
 * @BaselineVersion  対象バージョン
 * @TestOverview     テスト概要
 * @TestPurpose      テスト目的
 * @TestProcess      テスト手順
 * @TestResults      期待結果
 * @Creator          作成者
 * @CreatedDate      作成日（YYYY-MM-DD）
 * @Modifier         修正者
 * @ModifiedDate     修正日（YYYY-MM-DD）
 */
public class YourTestClass {
    @Test
    public void yourTestMethod() {
        // テスト条件分岐
        if (condition1) {
            // 正常系
            assertEquals(expected, actual);
        } else if (condition2) {
            // 異常系
            assertThrows(Exception.class, () -> method());
        } else {
            // その他
            assertNull(result);
        }
    }
}
```

#### 2. JaCoCoカバレッジレポートの生成
```bash
# Mavenの場合
mvn clean test jacoco:report

# Gradleの場合
./gradlew test jacocoTestReport
```

#### 3. ツール実行
1. VBA Excelワークブックを開く
2. 「Generate Test Specification」ボタンをクリック
3. プロジェクトのテストディレクトリを選択
4. 出力先を指定して実行

## 📊 出力Excelフォーマット

### 実際の生成例（94.6% C1カバレッジ）

**Test Details シート:**
| ファイルパス | テストモジュール | テストケース | カバレッジ% | カバー済み | 総ブランチ数 |
|-------------|-----------------|-------------|------------|-----------|------------|
| BasicCalculatorTest.java | CalculatorModule | ConditionalAdditionTest | 100.0% | 8 | 8 |
| BasicCalculatorTest.java | CalculatorModule | MultiplicationBranching | 87.5% | 14 | 16 |
| StringValidatorTest.java | StringValidationModule | EmailValidationTest | 95.8% | 23 | 24 |

**Summary シート:**
- 処理ファイル数: 2
- テストケース数: 8
- 全体C1カバレッジ: 94.6%
- カバー済みブランチ: 140/148

**Coverage シート:**
| ファイルパス | メソッド名 | C1カバレッジ% | ステータス |
|-------------|-----------|--------------|----------|
| BasicCalculatorTest.java | testConditionalCalculation | 100.0% | Excellent |
| StringValidatorTest.java | testEmailValidation | 95.8% | Excellent |

## 🛠️ トラブルシューティング

### よくある問題と解決方法

#### 1. マクロが実行できない
**問題**: 「マクロが無効化されています」エラー
**解決**:
- ファイル → オプション → セキュリティセンター → マクロの設定
- 「すべてのマクロを有効にする」を選択（または信頼済み場所を設定）

#### 2. VBAモジュールが見つからない
**問題**: 「Sub または Function が定義されていません」エラー
**解決**:
- VBAエディタ（Alt+F11）でモジュールがインポートされているか確認
- 手順に従って6つのモジュールを再インポート

#### 3. ファイルアクセスエラー
**問題**: 「ファイルにアクセスできません」エラー
**解決**:
- ファイルパスに日本語や特殊文字が含まれていないか確認
- ファイルが他のアプリケーションで開かれていないか確認
- 管理者権限でExcelを実行

#### 4. カバレッジレポートが読み込めない
**問題**: カバレッジシートが空白
**解決**:
- JaCoCo XML形式のレポートがあることを確認
- coverage-reports/ フォルダに jacoco*.xml ファイルが存在するか確認
- JaCoCoバージョンが対応範囲内か確認

#### 5. 大量ファイル処理時の性能問題
**問題**: 処理が途中で停止する
**解決**:
- 処理対象ディレクトリのファイル数を確認（推奨：1000ファイル以下）
- Excelの使用可能メモリを確認
- バッチ処理で分割実行を検討

## 📚 詳細ドキュメント

- **[ユーザーガイド](docs/user-guide.md)**: 詳細な操作手順
- **[アノテーション標準](docs/annotation-standards.md)**: Javaアノテーションガイドライン
- **[カバレッジ統合ガイド](docs/coverage-integration.md)**: JaCoCoカバレッジ分析
- **[VBAセットアップ手順](vba-modules/VBA-Import-Instructions.md)**: VBA環境設定

## 🎯 実装検証済み機能

### テスト済み実データ
- **Javaファイル**: 2ファイル処理（BasicCalculatorTest.java, StringValidatorTest.java）
- **アノテーション抽出**: 8メソッドから11項目完全抽出
- **C1カバレッジ**: 148ブランチ中140ブランチ検出（94.6%）
- **Excel生成**: 4シート構成、10,238バイトのレポート生成

### 対応Java アノテーション
```java
@TestModule, @TestCase, @BaselineVersion, @TestOverview,
@TestPurpose, @TestProcess, @TestResults, @Creator,
@CreatedDate, @Modifier, @ModifiedDate
```

### 対応カバレッジフォーマット
- JaCoCo XML レポート（jacoco.xml, jacoco-report.xml）
- C1（条件判定）カバレッジ
- ブランチカバレッジ統計
- メソッドレベル詳細分析

## 🔧 バージョン情報

### Version 1.0.0 (2026-01-07)
- **完全VBA実装** による初回リリース
- **Javaアノテーション解析** 包括的フォーマットサポート
- **JaCoCo XMLカバレッジ統合** C1分析対応
- **マルチシートExcelレポート** プロフェッショナル書式
- **条件分岐ロジック付きサンプルテスト** 完全な例
- **包括的ドキュメント** とセットアップガイド

## 📞 サポート・連絡先

### サポートリソース
- **Issue報告**: プロジェクトのGitHub Issues
- **技術質問**: 詳細なエラーメッセージとスクリーンショット付きで報告
- **機能要望**: 具体的な使用ケースと共に提案

### バグレポートに含めるべき情報
- エラーメッセージとスクリーンショット
- 問題を再現するJavaファイルサンプル
- システム情報（Excelバージョン、OS）
- 問題再現の詳細手順

---

*このツールは、JaCoCoカバレッジ分析と統合されたJavaテストケースからのテスト仕様書生成に実用的なソリューションを提供するよう設計されました。VBA実装により、標準的な企業Excel環境での互換性を確保しながら、テストドキュメント自動化の包括的な機能を提供します。*