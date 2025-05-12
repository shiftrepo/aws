# Podman-Compose による特許分析コンテナ使用ガイド

このガイドでは、podman-composeを使用して特許分析MCPコンテナを管理する方法について説明します。

## 前提条件

以下のソフトウェアがインストールされている必要があります：

- podman
- podman-compose

## 変更点

Dockerfile.mcpには以下のネットワークユーティリティが追加されています：
- curl - HTTPリクエストを送信するためのツール
- iputils-ping - ネットワーク接続テスト用
- net-tools - ネットワーク設定確認用
- dnsutils - DNS解決のテスト用

## 基本的な使い方

### 1. サービスの起動

```bash
cd /root/aws.git/patent_analysis_container
podman-compose -f docker-compose.mcp.yml up -d
```

### 2. コンテナの接続性テスト

更新された`test_container_connectivity.sh`スクリプトを使用して、コンテナ間の接続をテストできます：

```bash
cd /root/aws.git/patent_analysis_container
./test_container_connectivity.sh
```

このスクリプトは以下をチェックします：
- patentdwh-dbへの接続
- patentdwh-mcp-enhancedへの接続
- API経由でのDB接続
- ネットワーク設定の確認
- podman-composeの設定確認

### 3. ネットワーク問題のトラブルシューティング

ネットワーク接続に問題がある場合は、以下の手順を試してください：

1. すべてのユーティリティが含まれているイメージを再ビルドします：
   ```bash
   cd /root/aws.git/patent_analysis_container
   podman-compose -f podman-compose.yml build
   ```

2. patentdwh_defaultネットワークが存在するか確認：
   ```bash
   podman network ls | grep patentdwh_default
   ```

3. 存在しない場合は作成：
   ```bash
   podman network create patentdwh_default
   ```

4. サービスを再起動：
   ```bash
   cd /root/aws.git/patent_analysis_container
   podman-compose -f podman-compose.yml down
   podman-compose -f podman-compose.yml up -d
   ```

### 4. サービスの停止

```bash
cd /root/aws.git/patent_analysis_container
podman-compose -f docker-compose.mcp.yml down
```

## AWS認証情報の設定

コンテナは環境変数からAWS認証情報を取得します。以下のように設定してください：

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=your_region  # Optional, defaults to us-east-1
```

**注意**: AWS認証情報をスクリプトやDockerfile内にハードコードしないでください。常に環境変数を使用してください。

## APIエンドポイント

サービスが起動すると、以下のエンドポイントが利用可能になります：

- ヘルスチェック: http://localhost:8000/
- Swagger API ドキュメント: http://localhost:8000/docs
- OpenAPI スキーマ（Dify統合用）: http://localhost:8000/openapi.json
- MCP互換エンドポイント: http://localhost:8000/api/v1/mcp (POST)
- Dify互換エンドポイント: http://localhost:8000/api/tools/execute (POST)
- 特許トレンド分析: http://localhost:8000/api/analyze (POST)
- レポート取得（Markdown）: http://localhost:8000/api/report/{applicant_name} (GET)
- レポート取得（ZIP）: http://localhost:8000/api/report/{applicant_name}/zip (GET)

## 既知の問題と解決策

1. **コンテナ間通信の問題**
   - 外部ネットワーク `patentdwh_default` が正しく設定されているか確認してください
   - ネットワーク設定のトラブルシューティングには `test_container_connectivity.sh` を使用

2. **パフォーマンスの問題**
   - podmanはDockerよりも若干遅い場合があります
   - 大量のコンテナを同時に実行する際はリソース使用量に注意してください
