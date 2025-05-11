# patentDWH MCP 404 Error Fix

このドキュメントは、patentDWH MCPサービスで発生する404エラーの修正方法について説明します。

## 問題の概要

patentDWH-mcp-enhancedサービスは起動しているように見えますが、以下のようなエラーが発生します:

```
[ERROR] 2025-05-11 12:43:10 - MCPサービスの起動確認に失敗しました
2025-05-11 12:42:10,306 - INFO - HTTP Request: POST http://patentdwh-db:5002/api/v1/mcp "HTTP/1.0 404 NOT FOUND"
2025-05-11 12:42:10,426 - INFO - HTTP Request: POST http://patentdwh-db:5002/api/v1/mcp "HTTP/1.0 404 NOT FOUND"
2025-05-11 12:42:10,637 - INFO - HTTP Request: POST http://patentdwh-db:5002/api/v1/mcp "HTTP/1.0 404 NOT FOUND"
```

この問題は、データベースサービス（patentdwh-db）の `/api/v1/mcp` エンドポイントが実装されていないために発生します。

## 修正箇所

以下の修正が行われました：

1. **データベースサービスにMCPエンドポイントを追加**
   - `db/mcp_endpoint_patch.py` ファイルを作成し、MCPエンドポイントを実装
   - `db/patched_entrypoint.sh` スクリプトを作成し、起動時にパッチを適用

2. **ネットワーク設定の修正**
   - `docker-compose.consolidated.patched.yml` ファイルに明示的なネットワーク名を設定
   - コンテナ間の接続問題を解決

3. **LangChainの互換性修正**
   - `app/requirements_enhanced.txt` の依存関係を最新の互換性のあるバージョンに更新
   - import fallbackメカニズムを使用してライブラリの読み込みを安定化

## 適用方法

1. 以下のコマンドで修正スクリプトを実行します:

```bash
cd /root/aws.git/patentDWH
./apply_mcp_fix.sh
```

このスクリプトは以下の処理を行います:
- すべてのサービスを停止
- AWS認証情報の確認
- LangChain要件の更新
- データベースサービスにMCPエンドポイントを追加
- 修正されたdocker-compose設定で全サービスを再起動
- サービスステータスの確認

## 修正内容の詳細説明

### データベースサービスMCPエンドポイント

データベースサービスに新しいエンドポイント `/api/v1/mcp` を追加しました。このエンドポイントは以下のツールをサポートします:

- `get_sql_examples`: データベース別のSQLサンプルを返す
- `get_schema_info`: データベーススキーマ情報を返す
- `execute_sql`: SQLクエリを実行する

### ネットワーク設定

ネットワーク接続の問題を解決するために、`patentdwh_default` という名前の明示的なネットワークを設定しました。これにより、すべてのコンテナが同じネットワーク上で通信できるようになります。

### LangChain互換性

最新バージョンのLangChain（langchain>=0.1.0とlangchain-community>=0.0.13）を使用するように要件を更新しました。また、インポート時のフォールバックメカニズムにより、異なるバージョン間の互換性を保証しています。

## トラブルシューティング

修正後も問題が解決しない場合は、以下の確認を行ってください:

1. ログの確認:
```bash
podman-compose -f docker-compose.consolidated.patched.yml logs -f patentdwh-mcp-enhanced
```

2. データベースサービスのMCPエンドポイントが動作しているか確認:
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"tool_name":"get_schema_info","tool_input":{"db_type":"inpit"}}' \
  http://localhost:5002/api/v1/mcp
```

3. MCPサービスのヘルスステータスを確認:
```bash
curl http://localhost:8080/health
```

4. ネットワーク設定を確認:
```bash
podman network ls
podman network inspect patentdwh_default
```

## 今後の改善点

この修正は一時的な対応策です。将来的には以下の改善を検討できます:

1. データベースサービスの公式MCPエンドポイント実装を開発
2. コンテナ間の依存関係管理の強化
3. より堅牢なヘルスチェックと自動復旧メカニズムの実装
