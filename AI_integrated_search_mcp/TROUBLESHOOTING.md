# AI Integrated Search MCP Troubleshooting Guide

このドキュメントでは、AI Integrated Search MCPシステムの一般的な問題に対する解決策を提供します。

## コンテナの起動問題

ヘルスチェックスクリプトでコンテナが実行されていないと報告された場合は、以下の手順で解決できます。

### スクリプトの改良点

メインの`start_services.sh`スクリプトには、以下の自動修復機能が組み込まれています：

- 既存の同名コンテナの自動クリーンアップ
- データベースファイルの存在確認と適切な権限設定
- 専用のコンテナネットワーク作成による接続問題解決
- 各コンテナを個別に起動することによる依存関係の問題回避
- コンテナ間通信の最適化
- 起動時の自動ヘルスチェック

### 解決手順

1. AWS認証情報を準備します
2. 起動スクリプトを実行します：
   ```bash
   cd AI_integrated_search_mcp
   ./scripts/start_services.sh
   ```
3. AWS認証情報の入力を求められた場合は、入力してください
4. 出力エラーがないか監視します

スクリプトは自動的に一般的な問題（ポート競合、ネットワーク接続、データベースの不足など）を検出して修正します。

## データベースファイルの問題

データベースファイルが見つからない、または破損している場合：

1. ダウンロードスクリプトを実行します：
   ```bash
   cd AI_integrated_search_mcp
   ./scripts/download_databases.sh
   ```
2. データベースファイルに適切な権限を設定します：
   ```bash
   chmod 644 ./db/data/*.db
   ```

## ネットワーク接続の問題

コンテナ同士が通信できない場合：

1. コンテナに`--network=host`パラメータを使用します（これはstart_services.shスクリプトに組み込まれています）
2. または、専用のネットワークを作成します：
   ```bash
   podman network create mcp-network
   ```
   その後、このネットワークをpodman-compose.ymlファイルで使用します。

## 権限の問題

権限の問題が発生した場合：

1. `--user "$(id -u):$(id -g)"`を使ってコンテナをユーザーIDとグループIDに合わせて実行します
2. データベースファイルが適切な権限（644）を持っていることを確認します
3. ボリュームマウントでSELinuxコンテキスト用に`:Z`サフィックスを使用します（例：`-v ./db/data:/app/data:Z`）

## AWS認証情報の問題

AWS認証情報に問題がある場合：

1. スクリプトを実行する前に次の環境変数を設定します：
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key_id
   export AWS_SECRET_ACCESS_KEY=your_secret_access_key
   export AWS_DEFAULT_REGION=your_aws_region
   ```

## 一般的なエラーメッセージ

### "no container with name or ID X found"
これは通常、コンテナが存在しないことを意味します。start_services.shスクリプトを使用して作成してください。

### "permission denied"エラー
適切なユーザー権限で実行していることと、ファイルの権限が正しく設定されていることを確認してください。

### AWS認証情報エラー
AWS_ACCESS_KEY_ID、AWS_SECRET_ACCESS_KEY、AWS_DEFAULT_REGIONが適切に設定されていることを確認してください。

## その他のヘルプ

これらのトラブルシューティング手順で問題が解決しない場合：

1. コンテナのログを確認します：
   ```bash
   podman logs sqlite-db
   podman logs nl-query-service
   podman logs web-ui
   ```
2. コンテナの設定を調べます：
   ```bash
   podman inspect sqlite-db
   ```
3. サービスのステータスを手動でcurlを使って確認します：
   ```bash
   curl http://localhost:5003/health
   curl http://localhost:5004/health
   curl http://localhost:5002
   ```
