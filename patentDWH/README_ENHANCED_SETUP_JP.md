# patentDWH 強化版セットアップガイド（コンテナ版）

このドキュメントでは、通常の patentDWH セットアップと強化版コンテナセットアップの違いについて説明します。

## セットアップスクリプトの違い

patentDWH には2種類のセットアップ方法があります：

### 1. 標準セットアップ (`setup.sh`)

`setup.sh` は以下の特徴を持ちます：

- **コンテナベースのデプロイ**: Docker または Podman を使用してコンテナ化されたサービスを起動します
- **自動ビルドと起動**: データベースサービス (`patentdwh-db`) と MCP サービス (`patentdwh-mcp`) を自動的にビルドして起動します
- **データダウンロード**: 必要なデータを自動的にダウンロードして、データベースを準備します
- **ヘルスチェック**: サービスが正常に起動しているかをチェックします
- **ポートチェック**: 必要なポート (5002, 8080) が使用可能かをチェックします

通常、標準セットアップでは以下のコンポーネントが起動します：
1. データベースサービス (SQLite、ポート 5002)
2. MCP サービス (patentDWH MCP API、ポート 8080)

### 2. 強化版セットアップ (`setup_enhanced_container.sh`)

`setup_enhanced_container.sh` は以下の特徴を持ちます：

- **コンテナベースのデプロイ**: Docker または Podman を使用してコンテナ化されたサービスを起動します
- **カスタム Dockerfile**: 強化版の `Dockerfile.enhanced` を使用してLangChainやその他の依存関係を含めた強化版MCPサービスをビルド
- **AWS 認証情報の確認**: AWS Bedrock サービスを利用するための認証情報をチェックします
- **別の docker-compose ファイル**: LangChain 対応の強化版MCPサービス用に `docker-compose.enhanced.yml` を生成して使用

強化版セットアップでは、以下のような構成になります：
1. データベースサービス (標準セットアップと同じ、ポート 5002) - コンテナ化
2. 強化版 MCP サービス (コンテナ名 `patentdwh-mcp-enhanced`、ポート 8080) - コンテナ化

## 主な違い

| 機能 | 標準セットアップ (`setup.sh`) | 強化版セットアップ (`setup_enhanced_container.sh`) |
|------|------------------------|---------------------------|
| 実行環境 | コンテナ（Docker/Podman） | コンテナ（Docker/Podman） |
| MCP サービス | 標準MCP（コンテナ） | 強化版MCP（コンテナ） |
| LangChain サポート | なし | あり（優先的に使用可能） |
| 自然言語クエリ方法 | Bedrock API のみ | Bedrock API + LangChain |
| フォールバック機構 | Bedrock フォールバック | 3段階（オリジナル→Bedrock→LangChain） |
| AWS 依存度 | 高い（必須） | 高い（必須） |
| リソース使用量 | 中（標準コンテナ） | 中〜高（LangChain含むコンテナ） |

## 起動方法の違い

### 標準セットアップの起動

```bash
# 1. セットアップスクリプトを実行（初回のみ）
./patentDWH/setup.sh

# サービスが自動的に起動します

# コンテナを停止する場合
cd patentDWH
podman-compose down  # または docker compose down
```

### 強化版コンテナセットアップの起動

```bash
# 1. AWS認証情報を設定（未設定の場合）
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1

# 2. 強化版セットアップスクリプトを実行（すべてを自動でセットアップ）
./patentDWH/setup_enhanced_container.sh

# サービスが自動的に起動します

# コンテナを停止する場合
cd patentDWH
podman-compose -f docker-compose.enhanced.yml down  # または docker compose -f docker-compose.enhanced.yml down
```

## 使用上の注意点

1. **ポートの競合**: 標準セットアップと強化版セットアップの両方で同じポート（5002, 8080）を使用するため、同時に実行することはできません。

2. **AWS 認証情報**: 両方のセットアップで AWS 認証情報（AWS_ACCESS_KEY_ID、AWS_SECRET_ACCESS_KEY、AWS_REGION）が必要です。

3. **データ互換性**: 両方のセットアップは同じデータベースファイルを使用するため、データの互換性に問題はありません。ただし、一方のセットアップから他方に切り替える際は、先に実行していたコンテナを停止する必要があります。

4. **リソース使用量**: 強化版セットアップはLangChainや追加の依存関係を含むため、標準セットアップよりも若干多くのメモリを使用する可能性があります。

## どちらを使うべきか？

- **標準セットアップ**: シンプルな自然言語クエリ処理で十分な場合
- **強化版セットアップ**: より柔軟な自然言語クエリ処理が必要な場合や、LangChainの機能を活用したい場合

## 完全なワークフロー例

### 標準セットアップから強化版セットアップへの切り替え

```bash
# 1. 標準セットアップのコンテナを停止
cd patentDWH
podman-compose down  # または docker compose down

# 2. AWS認証情報を設定（未設定の場合）
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1

# 3. 強化版コンテナセットアップを実行
./patentDWH/setup_enhanced_container.sh
```

この構成で、データベースサービスは `http://localhost:5002` で、強化版MCP APIは `http://localhost:8080` で利用可能になります。

強化版のAPIを使用してLangChainを優先的に使用するクエリ例：

```bash
curl -X POST http://localhost:8080/api/nl-query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "2020年以降に出願された人工知能に関する特許で、外国企業が出願人になっているものを教えてください",
    "db_type": "inpit",
    "use_langchain_first": true
  }' | jq
```

## ログの確認

強化版コンテナのログを確認するには：

```bash
# 全体のログを確認
cd patentDWH
podman-compose -f docker-compose.enhanced.yml logs -f

# データベースサービスのログのみを確認
podman-compose -f docker-compose.enhanced.yml logs -f patentdwh-db

# 強化版MCPサービスのログのみを確認
podman-compose -f docker-compose.enhanced.yml logs -f patentdwh-mcp-enhanced
```

## トラブルシューティング

1. **コンテナが起動しない場合**：
   - AWS認証情報が正しく設定されていることを確認
   - ポートが他のプロセスによって使用されていないことを確認
   - セットアップスクリプト内のエラーメッセージを確認

2. **データベース接続エラー**：
   - データベースサービスが実行中であることを確認
   - `docker-compose.enhanced.yml`の設定を確認

3. **LangChainが機能しない場合**：
   - コンテナのログを確認して詳細なエラーメッセージを取得
   - AWS Bedrock APIへのアクセス権があることを確認
