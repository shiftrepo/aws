# 特許DWH MCPサービスの循環インポート問題修正

本ドキュメントでは、特許DWHのMCPサービス内で発生していた循環インポート（circular import）の問題について説明し、その修正方法を解説します。

## 問題の概要

MCPサービスの起動時に以下のエラーが発生していました：

```
ImportError: cannot import name 'NLQueryProcessor' from partially initialized module 'nl_query_processor' (most likely due to a circular import) (/app/nl_query_processor.py)
```

これは「循環インポート」（circular import）と呼ばれる問題です。モジュールA がモジュールB をインポートし、同時にモジュールB がモジュールA をインポートするような構造になっていると、Pythonはこれを正しく解決できずにエラーとなります。

## 循環インポートの原因

我々のコードでは以下のような循環インポート構造が発生していました：

1. `patched_nl_query_processor.py` が `nl_query_processor.py` からクラスをインポート
2. `nl_query_processor.py` が `base_nl_query_processor.py` からインポート
3. `enhanced_nl_query_processor.py` が `patched_nl_query_processor.py` からインポート 
4. `server_with_enhanced_nl.py` が `enhanced_nl_query_processor.py` からインポート

この構造により、モジュールの初期化時に循環参照が発生し、特に `nl_query_processor.py` と `patched_nl_query_processor.py` の間で問題が起きていました。

## 修正方法

循環インポートを解決するため、以下の変更を行いました：

1. `patched_nl_query_processor.py` の修正:
   - `nl_query_processor` からのインポートを削除
   - 代わりに `base_nl_query_processor` から直接基底クラスをインポート

2. `nl_query_processor.py` の修正:
   - コメント修正によるファイルの目的の明確化
   - 循環参照を避けるためのインポート構造の最適化

## クラス階層の明確化

修正後のクラス階層は以下のようになります：

```
BaseNLQueryProcessor (base_nl_query_processor.py)
    ↓
NLQueryProcessor (nl_query_processor.py)
    ↓
NLQueryProcessor (patched_nl_query_processor.py)
    ↓
EnhancedNLQueryProcessor (enhanced_nl_query_processor.py)
```

それぞれのファイルは上位のファイルのみを参照するようになり、循環参照が解消されました。

## 修正ファイル

以下のファイルが修正されています：

- `patched_nl_query_processor.py` - インポート構造の変更
- `nl_query_processor.py` - インポート参照の適正化

## 修正の適用方法

修正を適用するには、提供されているスクリプト `fix_mcp_circular_import.sh` を実行します：

```bash
chmod +x patentDWH/fix_mcp_circular_import.sh
./patentDWH/fix_mcp_circular_import.sh
```

このスクリプトは以下の動作を行います：

1. 修正されたPythonファイルが存在することを確認
2. すでに実行中のMCPコンテナがある場合は、修正ファイルを適用してコンテナを再起動
3. コンテナが実行されていない場合は、docker-compose で起動
4. サービスのヘルスチェックを実行して起動確認

## 注意点

- この修正はコードの動作を変更するものではなく、モジュールのインポート構造のみを最適化しています
- AWS認証情報の管理方法は変更されていません（AWS_DEFAULT_REGIONを使用）
- NLQueryProcessorクラスの機能は全て維持されています

## 確認方法

修正適用後、以下のコマンドで動作を確認できます：

```bash
curl http://localhost:8080/health
```

正常に動作していれば、以下のようなレスポンスが返ります：

```json
{"status": "healthy", "service": "patentDWH-MCP", "database_connected": true, "aws_configured": true}
