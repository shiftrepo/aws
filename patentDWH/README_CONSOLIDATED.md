# patentDWH 統合設定ガイド

このドキュメントでは、patentDWHの複数のdocker-composeファイルを統合し、ローカルホスト専用サービスを削除した新しい設定について説明します。

## 概要

以前のpatentDWHでは、複数のdocker-composeファイル（docker-compose.enhanced.yml、podman-compose.yml）やpatent_analysis_container内の設定ファイルが混在していました。また、ローカルホスト専用のUIサービスも含まれていました。

今回の統合により：

1. すべてのサービスを1つの設定ファイル（`docker-compose.consolidated.yml`）に統合
2. ローカルホスト専用サービス（WebUI）を削除
3. 必要な核心的なサービスのみを維持
4. 統合された設定ファイル用の新しいセットアップスクリプト（`setup_consolidated.sh`）を作成

## 含まれるサービス

統合された設定には、以下の必要不可欠なサービスのみが含まれています：

1. **patentdwh-db**: 特許データベースサービス（WebUIなし）
2. **patentdwh-mcp-enhanced**: 拡張MCP（Model Context Protocol）サービス（LangChain機能付き）
3. **patent-analysis**: 特許分析サービス（patent_analysis_containerからのもの）

## ローカルホスト専用サービスの削除

削除されたサービスとコンポーネント：

- データベースWebインターフェース（UIのみ、データベース自体は維持）
- MCPサーバーWebインターフェース（APIは維持）
- その他のローカルホスト専用コンポーネント

## 使い方

### セットアップ

1. 統合されたセットアップスクリプトを実行します：
   ```bash
   cd patentDWH
   ./setup_consolidated.sh
   ```

2. スクリプトは以下を行います：
   - 必要なコンテナをビルド
   - patentdwh-dbとpatentdwh-mcp-enhancedサービスを起動
   - サービスの健全性を確認
   - 使用方法の情報を表示

### 特許分析の実行

特許分析を実行するには：

```bash
# patentDWHディレクトリから
docker-compose -f docker-compose.consolidated.yml run patent-analysis "トヨタ" inpit
# または
podman-compose -f docker-compose.consolidated.yml run patent-analysis "トヨタ" inpit
```

### その他の便利なコマンド

```bash
# ログの表示
docker-compose -f docker-compose.consolidated.yml logs -f

# 特定のサービスのログを表示
docker-compose -f docker-compose.consolidated.yml logs -f patentdwh-db

# サービスの停止
docker-compose -f docker-compose.consolidated.yml down

# サービスの再起動
docker-compose -f docker-compose.consolidated.yml restart
```

## AWS認証情報

以下の環境変数を設定してAWS認証情報を提供してください：

```bash
export AWS_ACCESS_KEY_ID=あなたのアクセスキー
export AWS_SECRET_ACCESS_KEY=あなたのシークレットキー
export AWS_REGION=us-east-1  # または適切なリージョン
```

## MCPサーバーへの接続

Claudeなどのアシスタントをサーバーに接続する際は、以下の設定を使用します：

```json
{
  "serverName": "patentDWH",
  "description": "Enhanced Patent DWH MCP Server with LangChain",
  "url": "http://localhost:8080/api/v1/mcp"
}
```

## 注意点

- WebUIは削除されたため、すべての操作はAPIまたはCLIを通じて行う必要があります
- ローカルホストアクセスを必要としないヘッドレスシステムとして実行できます
- AWS認証情報はすべて環境変数を通じて提供され、設定ファイルには保存されません
