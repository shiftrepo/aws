# VBA モジュールインポート手順

## 概要
このドキュメントは、VBAモジュールをExcelにインポートしてTestSpecGenerator.xlsmファイルを作成するためのステップバイステップ手順を提供します。

## 事前要件
- Microsoft Excel 2016以降
- VBA（Visual Basic for Applications）有効化
- Excel リボンの開発者タブ有効化

## 開発者タブの有効化（表示されていない場合）
1. Excelを開く
2. **ファイル** → **オプション** → **リボンのユーザー設定** に移動
3. 右パネルで**開発**にチェックを入れる
4. **OK**をクリック

## TestSpecGenerator.xlsmファイルの作成

### ステップ 1: 新しいマクロ有効ワークブックの作成
1. Excelを開く
2. 新しい空白のワークブックを作成
3. **TestSpecGenerator.xlsm**として保存（Excel マクロ有効ワークブック形式）
4. 場所を選択: `/container/claudecode/java-test-specs/`

### ステップ 2: VBAエディタを開く
1. **Alt + F11**を押すか、**開発者** → **Visual Basic**をクリック
2. VBAエディタウィンドウが開きます

### ステップ 3: VBAモジュールのインポート
各`.bas`ファイルを以下の順序でインポート：

#### 3.1 DataTypes.basのインポート
1. VBAエディタで: **ファイル** → **ファイルのインポート**
2. `/container/claudecode/java-test-specs/vba-modules/`に移動
3. **DataTypes.bas**を選択
4. **開く**をクリック

#### 3.2 FolderScanner.basのインポート
1. **ファイル** → **ファイルのインポート**
2. **FolderScanner.bas**を選択
3. **開く**をクリック

#### 3.3 JavaAnnotationParser.basのインポート
1. **ファイル** → **ファイルのインポート**
2. **JavaAnnotationParser.bas**を選択
3. **開く**をクリック

#### 3.4 CoverageReportParser.basのインポート
1. **ファイル** → **ファイルのインポート**
2. **CoverageReportParser.bas**を選択
3. **開く**をクリック

#### 3.5 ExcelSheetBuilder.basのインポート
1. **ファイル** → **ファイルのインポート**
2. **ExcelSheetBuilder.bas**を選択
3. **開く**をクリック

#### 3.6 MainController.basのインポート
1. **ファイル** → **ファイルのインポート**
2. **MainController.bas**を選択
3. **開く**をクリック

### ステップ 4: モジュールインポートの確認
すべてのモジュールをインポート後、VBAプロジェクトエクスプローラーに以下が表示される必要があります：
```
VBAProject (TestSpecGenerator.xlsm)
├── Microsoft Excel Objects
│   ├── Sheet1 (Sheet1)
│   ├── Sheet2 (Sheet2)
│   ├── Sheet3 (Sheet3)
│   └── ThisWorkbook
└── Modules
    ├── DataTypes
    ├── FolderScanner
    ├── JavaAnnotationParser
    ├── CoverageReportParser
    ├── ExcelSheetBuilder
    └── MainController
```

### ステップ 5: ユーザーインターフェース作成（オプション）
#### 5.1 リボンボタンの追加
1. Excelでリボンを右クリック
2. **リボンのユーザー設定**を選択
3. 新しいグループまたはタブを作成
4. `MainController.GenerateTestSpecification`にリンクするボタンを追加

#### 5.2 図形ボタンの追加（代替方法）
1. **挿入** → **図形**に移動
2. 四角形またはボタン図形を挿入
3. 図形を右クリック → **マクロの登録**
4. `MainController.GenerateTestSpecification`を選択
5. ボタンに「Generate Test Specification」のテキストを設定

### ステップ 6: マクロセキュリティの設定
1. **ファイル** → **オプション** → **セキュリティセンター** → **セキュリティセンターの設定**に移動
2. **マクロの設定**を選択
3. **すべてのマクロを有効にする**（開発用）または**警告を表示してすべてのマクロを無効にする**（本番使用）を選択
4. **OK**をクリック

### ステップ 7: アプリケーションのテスト
1. VBAエディタを閉じる
2. ワークブックを保存（**Ctrl + S**）
3. ボタンをクリックするか、VBAエディタから`MainController.GenerateTestSpecification`を実行
4. `/sample-java-tests/`のサンプルJavaファイルでテスト

## 使用方法

### ツールの実行
1. **TestSpecGenerator.xlsm**を開く
2. プロンプトが表示されたらマクロを有効化
3. 「Generate Test Specification」ボタンをクリックするか：
   - **Alt + F11**を押してVBAエディタを開く
   - **F5**を押すか**実行** → **Sub/ユーザーフォームの実行**をクリック
   - `MainController.GenerateTestSpecification`を選択

### 入力要件
- **ソースディレクトリ**: Javaテストファイルを含むパス
  - 例: `C:\Projects\MyProject\src\test\java`
- **出力ファイル**: 生成されるExcelレポートのパス
  - 例: `C:\Reports\TestSpec_20260107.xlsx`

### 期待される出力
ツールは4つのシートを持つExcelファイルを生成します：
1. **Test Details** - 完全なテストケース情報
2. **Summary** - 集計統計
3. **Coverage** - カバレッジ分析結果
4. **Configuration** - 処理メタデータ

## トラブルシューティング

### よくある問題

#### 「コンパイルエラー: ユーザー定義型が定義されていません」
- **解決策**: DataTypes.basが最初にインポートされていることを確認

#### スキャン中の「ファイルが見つかりません」エラー
- **解決策**: ソースディレクトリパスが存在し、Javaファイルが含まれていることを確認

#### 出力ファイル保存時の「アクセスが拒否されました」
- **解決策**: 出力ディレクトリが存在し、書き込み可能であることを確認

#### マクロセキュリティ警告
- **解決策**: マクロを有効化するか、ファイルを信頼できる場所に追加

### エラーログ
アプリケーションは以下にエラーをログに記録：
- `MainController.g_ProcessingErrors`コレクション
- デバッグ出力については VBA イミディエイトウィンドウ（**Ctrl + G**）をチェック

## 性能に関する考慮事項

### 大規模プロジェクト
多数のファイル（Javaファイル1000個以上）を持つプロジェクトの場合：
- 処理時間5-10分を予想
- オフピーク時間中の実行を検討
- 出力ファイル用の十分なディスク容量を確保

### メモリ使用量
- 大きなファイル（10MB以上）は自動的にスキップされます
- メモリ使用量は見つかったテストケース数に応じてスケール
- メモリ問題が発生した場合は他のアプリケーションを閉じる

## セットアップ後のファイル構造
```
/container/claudecode/java-test-specs/
├── TestSpecGenerator.xlsm          # メインアプリケーションファイル
├── sample-java-tests/              # サンプルテストファイル
├── vba-modules/                    # VBAソースコード
├── templates/                      # Excelテンプレート
├── docs/                          # ドキュメント
└── examples/                      # サンプル出力
```

## バージョン情報
- **VBAアプリケーションバージョン**: 1.0.0
- **Excel互換性**: 2016以降
- **ファイル形式**: .xlsm（Excel マクロ有効ワークブック）
- **作成日**: 2026-01-07

## セキュリティ注意事項
- アプリケーションはJavaファイルとカバレッジレポートのみを読み取ります
- システム変更や外部ネットワーク接続はありません
- すべてのファイル操作はユーザー指定ディレクトリ内で行われます
- マクロセキュリティは組織のポリシーに従って設定する必要があります

## サポート
問題や質問がある場合：
1. アプリケーションのエラーメッセージを確認
2. ファイルパスと権限を確認
3. すべてのVBAモジュールが適切にインポートされていることを確認
4. 適切なアノテーション形式についてサンプルJavaファイルをレビュー

## 🚨 重要な実行順序

### VBAモジュールインポート順序（必須）
以下の順序で**必ず**インポートしてください：

1. **DataTypes.bas** ← 最初に必須（他のモジュールが依存）
2. **FolderScanner.bas**
3. **JavaAnnotationParser.bas**
4. **CoverageReportParser.bas**
5. **ExcelSheetBuilder.bas**
6. **MainController.bas** ← 最後にインポート

### 依存関係エラーの回避
- DataTypes.basを最初にインポートしないと「ユーザー定義型が定義されていません」エラーが発生
- MainController.basは他の全モジュールに依存するため最後にインポート

### 実行前チェックリスト
- [ ] 6つのモジュールがすべてVBAプロジェクトエクスプローラーに表示されている
- [ ] コンパイルエラーがない（VBAエディタでF5を押してテスト）
- [ ] マクロセキュリティが適切に設定されている
- [ ] sample-java-testsディレクトリでテスト実行が成功する