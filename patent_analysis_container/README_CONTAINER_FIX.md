# Patent Analysis MCP Container Fix Guide

## 問題 (Problem)

特許分析MCPコンテナが「Created」の状態で起動せず、実行状態(Running)になりませんでした。
(The patent-analysis-mcp container was stuck in the "Created" state and not transitioning to the "Running" state.)

```
CONTAINER ID  IMAGE                                                           COMMAND               STATUS         PORTS                                              NAMES
c8fc55d4b259  localhost/patent_analysis_container_patent-analysis-mcp:latest  python patent_ana...  Created        0.0.0.0:8000->8000/tcp, 8000/tcp                   patent-analysis-mcp
```

## 原因 (Cause)

主な問題は以下の点でした：
(The main issues were:)

1. ネットワーク構成: 
   - Docker Compose設定ファイルで外部ネットワーク(patentdwh_default)への接続が必須と設定されていたが、該当ネットワークが存在しない場合がありました。
   - `external: true`の設定により、存在しないネットワークにアクセスしようとしてエラーが発生していました。
   (Network configuration: Docker Compose file required connection to external network that might not exist)

2. コンテナランタイム: 
   - システムにはDocker Composeコマンドがなく、Podmanを使用しているため、設定の互換性に問題がありました。
   - Podman環境では外部ネットワークの取り扱いがDocker環境と微妙に異なります。
   (Container runtime: The system didn't have Docker Compose command and was using Podman)

3. エラーメッセージ: 
   ```
   RuntimeError: External network [patentdwh_default] does not exists
   ```

## 解決策 (Solution)

1. `docker-compose.mcp.yml` ファイルを更新し、外部ネットワークへの接続を有効化：
   (Updated the `docker-compose.mcp.yml` file to enable external network connection:)

   ```yaml
   networks:
     patent-network:
       # This lets the container connect to the patentDWH services
       external: true
       name: patentdwh_default
   ```

2. コンテナの再構築と再起動を行う修正スクリプト `fix_mcp_container.sh` を作成し、Docker/Podmanのどちらでも動作するように対応：
   (Created a fix script `fix_mcp_container.sh` for rebuilding and restarting the container, compatible with both Docker and Podman:)

   - コンテナランタイム(Docker/Podman)を自動検出
     (Auto-detects container runtime (Docker/Podman))
   - Compose ツールがない場合はネイティブコマンドを使用
     (Uses native commands if Compose tools are not available)
   - AWS認証情報の自動ロードを試行
     (Attempts to auto-load AWS credentials)
   - コンテナを適切なネットワーク設定で再起動
     (Restarts the container with proper network configuration)

## 使用方法 (Usage)

コンテナに問題が発生した場合は、以下のコマンドで修正スクリプトを実行してください：
(If you encounter issues with the container, run the fix script with the following command:)

```bash
cd /path/to/patent_analysis_container
./fix_mcp_container.sh
```

スクリプトはコンテナをビルドし直し、適切な設定で再起動します。
(The script will rebuild and restart the container with the correct configuration.)

## APIエンドポイント確認 (API Endpoint Verification)

APIが正常に動作していることを確認するには：
(To verify the API is working correctly:)

```bash
curl http://localhost:8000/
```

以下のレスポンスが返ってくれば、サーバーは正常に動作しています：
(The following response indicates the server is running properly:)

```json
{"status":"ok","message":"Patent Analysis MCP Server is running"}
```

## 特許分析の実行 (Running Patent Analysis)

特許分析を実行するには以下のようなcURLコマンドを使用できます：
(To run a patent analysis, you can use a cURL command like this:)

```bash
curl -X POST http://localhost:8000/api/v1/mcp \
  -H 'Content-Type: application/json' \
  -d '{"tool_name":"analyze_patent_trends","tool_input":{"applicant":"トヨタ"}}'
```

## 注意点 (Notes)

- AWS認証情報が正しく設定されていることを確認してください
  (Ensure AWS credentials are properly configured)
- Podmanを使用している場合、ネットワーク設定に注意してください
  (If using Podman, pay attention to network configuration)
- patentdwh_defaultネットワークが存在することが前提です
  (Assumes the patentdwh_default network exists)
