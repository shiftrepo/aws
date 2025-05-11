# Comprehensive MCP Service Fix Documentation

このドキュメントでは、patentDWHシステムのMCPサービスで発生する一般的な問題に対する包括的な修正方法について説明します。

## 問題概要 / Problem Summary

patentDWH MCPサービス（patentdwh-mcp-enhanced）に関連して以下の問題が発生することがあります：

1. **サービス起動の失敗**: MCPサービスがUvicornで起動するものの、ヘルスチェックが失敗する
2. **データベース接続エラー**: DB接続に関する "Connection refused" エラー
3. **LangChain互換性の問題**: LangChainとLangChain Communityパッケージのバージョン不一致
4. **コンテナ間通信の問題**: コンテナ間で相互に通信できない（特にネットワーク設定の問題）
5. **AWS認証情報の不足**: 自然言語処理機能のためのAWS認証情報が正しく設定されていない

## 包括的修正スクリプト / Comprehensive Fix Script

これらの問題をすべて解決するために、包括的修正スクリプト `fix_all_mcp_issues.sh` を提供しています。このスクリプトは以下の機能を実行します：

### 1. コンテナランタイムの検出と設定

- DockerまたはPodmanのどちらを使用しているかを自動検出
- 適切なcomposeコマンド（docker-compose または podman-compose）の決定

### 2. ネットワーク問題の修正

- `patentdwh_default` ネットワークの存在確認と作成
- コンテナが同じネットワーク上で通信できるように設定

### 3. LangChain互換性の修正

- `requirements_enhanced.txt` ファイルの更新
- 互換性のあるLangChainバージョンに修正（langchain>=0.1.0、langchain-community>=0.0.13）
- インポートフォールバックメカニズムの追加

### 4. AWS認証情報の設定

- 環境変数から、または `~/.aws/credentials` ファイルからAWS認証情報の読み込み
- `AWS_DEFAULT_REGION` が設定されていない場合はデフォルト値の設定

### 5. サービス再構築と起動

- patentdwh-mcp-enhancedサービスの再構築
- データベースサービスとMCPサービスの順番に沿った起動
- サービスの状態確認とヘルスチェック

### 6. Patent Analysis MCPコンテナの修正

- Patent Analysis MCPコンテナの再構築と起動
- 適切なネットワーク設定の適用

### 7. 接続性のテスト

- コンテナ間の接続テスト実行
- 問題が解決されたことの確認

## 使用方法 / Usage

1. スクリプトを実行可能にする:
```bash
chmod +x fix_all_mcp_issues.sh
```

2. スクリプトを実行する:
```bash
./fix_all_mcp_issues.sh
```

## 修正後の確認方法 / Verification

スクリプト実行後、以下のURLでサービスが正常に動作していることを確認できます：

1. MCP サービス: http://localhost:8080/
2. Patent Analysis MCP API: http://localhost:8000/

## 注意事項 / Notes

- このスクリプトを実行する前に、すべてのサービスが停止していることを確認してください
- AWS認証情報が正しく設定されていない場合、自然言語処理機能は正常に動作しませんが、他の機能は使用可能です
- コンテナエンジン（DockerまたはPodman）がインストールされ、正しく設定されている必要があります

## トラブルシューティング / Troubleshooting

スクリプト実行後も問題が解決しない場合は、以下を確認してください：

1. コンテナのログを確認:
```bash
podman logs patentdwh-mcp-enhanced
# または
docker logs patentdwh-mcp-enhanced
```

2. ネットワーク設定を確認:
```bash
podman network ls
# または
docker network ls
```

3. コンテナの状態を確認:
```bash
podman ps -a
# または
docker ps -a
```

4. AWS認証情報が正しく設定されているか確認:
```bash
curl http://localhost:8080/api/aws-status
```

5. サービス間の接続を確認:
```bash
cd /root/aws.git/patent_analysis_container
./test_container_connectivity.sh
```
