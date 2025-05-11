# 特許分析MCPコンテナのネットワーク接続問題解決ガイド

## 問題概要

特許分析MCPコンテナが `Created` 状態のままになり、他のコンテナ（patentdwh-db、patentdwh-mcp-enhanced）と通信できない場合があります。これは主に以下の原因で発生します：

1. **ネットワークが存在しない**：`patentdwh_default` ネットワークが存在せず、エラー `External network [patentdwh_default] does not exists` が発生
2. **ネットワーク設定の互換性**：podman-compose と Docker Compose の間でネットワーク設定の扱いが異なる
3. **コンテナ間の通信エラー**：コンテナが起動しても、適切なネットワーク上に配置されていないと通信できない

## 解決方法

1. **ネットワークの事前確認と作成**  
   スクリプト実行前に `patentdwh_default` ネットワークの存在を確認し、存在しない場合は自動的に作成します。

   ```bash
   # ネットワークを確認・作成
   if ! podman network exists patentdwh_default; then
     podman network create patentdwh_default
   fi
   ```

2. **Docker Compose 設定ファイルの修正**  
   `docker-compose.mcp.yml` ファイルで、外部ネットワークへの接続設定を調整します。

   ```yaml
   networks:
     patent-network:
       external: true
       name: patentdwh_default
   ```

3. **コンテナの接続性テスト**  
   提供している `test_container_connectivity.sh` スクリプトを使用して、コンテナ間の接続性をテストします。

   ```bash
   ./test_container_connectivity.sh
   ```

## コンテナ間通信の確保

特許分析MCPコンテナとpatentDWHサービス間の通信には、以下の点が重要です：

1. **同一ネットワーク上にあること**  
   すべてのコンテナが同じネットワーク（`patentdwh_default`）上に存在する必要があります。

2. **DNS解決の確認**  
   コンテナ名による相互DNSルックアップが機能していること。例えば、patent-analysis-mcpコンテナから 
   `patentdwh-db` や `patentdwh-mcp-enhanced` の名前で接続できる必要があります。

3. **ポートの公開**  
   各サービスが必要なポートを適切に公開していること：
   - patentdwh-db: 5002
   - patentdwh-mcp-enhanced: 8080
   - patent-analysis-mcp: 8000

## トラブルシューティングの手順

コンテナが正しく起動しても通信に問題がある場合は、以下の手順を試してください：

1. **すべてのサービスを停止**:
   ```bash
   cd /root/aws.git/patentDWH
   ./stop_all_services.sh
   ```

2. **ネットワークを再作成**:
   ```bash
   podman network rm patentdwh_default
   podman network create patentdwh_default
   ```

3. **すべてのサービスを再起動**:
   ```bash
   ./start_all_services.sh
   ```

4. **コンテナの状態確認**:
   ```bash
   podman ps -a
   ```

5. **コンテナ間の接続性テスト**:
   ```bash
   cd /root/aws.git/patent_analysis_container
   ./test_container_connectivity.sh
   ```

## 修正後のテスト方法

1. **API 接続テスト**:
   ```bash
   curl http://localhost:8000/
   ```
   
   期待される出力:
   ```json
   {"status":"ok","message":"Patent Analysis MCP Server is running"}
   ```

2. **特許分析機能テスト**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/mcp \
     -H 'Content-Type: application/json' \
     -d '{"tool_name":"analyze_patent_trends","tool_input":{"applicant":"トヨタ"}}'
   ```
   
   このコマンドが成功すると、トヨタの特許出願分析結果が返されます。
   
## 注意事項

- Podman環境ではネットワーク関連のコマンドに sudo 権限が必要な場合があります
- コンテナが正しく起動しても他のサービスとの接続に問題がある場合は、ログを確認してください
- AWS認証情報が正しく設定されていることを確認してください
