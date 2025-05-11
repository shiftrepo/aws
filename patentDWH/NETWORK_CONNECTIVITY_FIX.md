# patentDWH Network Connectivity Fix

## 問題の説明 (Problem Description)

patentDWH のセットアップ中に発生したエラーは、コンテナ間のネットワーク接続の問題によるものです。具体的には、patentdwh-mcp コンテナが patentdwh-db コンテナに接続できずにいます。

ログを見ると、次のようなエラーが繰り返し表示されています：
```
Could not connect to database server, retrying in 3 seconds...
```

この問題は、コンテナ間での名前解決が適切に動作していないために発生しています。

## 解決策 (Solution)

問題を解決するために、次の修正を行いました：

1. 明示的な Docker/Podman ネットワーク定義を含む修正済みの docker-compose ファイルを作成
2. すべてのコンテナが同じネットワーク（`patent-network`）上で稼働するように設定
3. コンテナ間の通信を確実にするための設定を追加

この修正により、patentdwh-mcp サービスは patentdwh-db サービスに正常に接続できるようになります。

## 修正スクリプトの使用方法 (How to Use the Fix)

修正スクリプト `fix_setup.sh` を実行することで、問題を自動的に解決できます：

```bash
cd patentDWH
./fix_setup.sh
```

このスクリプトは以下のステップを実行します：

1. 実行中のコンテナをすべて停止・削除
2. 修正済みの docker-compose ファイルを作成
3. コンテナを再ビルドして起動
4. サービスの初期化待機
5. サービスの状態確認

正常に完了すると、以下のサービスにアクセスできるようになります：

- データベース UI: http://localhost:5002/
- MCP API: http://localhost:8080/

## ログの確認方法 (How to Check Logs)

サービスが正常に動作しているか確認するには、以下のコマンドでログを確認できます：

```bash
# すべてのサービスのログを確認
cd patentDWH
podman-compose -f docker-compose.patched.yml logs -f

# 特定のサービスのログを確認
cd patentDWH
podman-compose -f docker-compose.patched.yml logs -f patentdwh-db
podman-compose -f docker-compose.patched.yml logs -f patentdwh-mcp
```

## 技術的解説 (Technical Explanation)

この問題は Docker/Podman のネットワークアーキテクチャに関連しています。デフォルトでは、各コンテナは独自のネットワーク名前空間を持ち、明示的にネットワークを定義しない限り、他のコンテナにホスト名でアクセスすることができません。

修正した `docker-compose.patched.yml` では：

1. 共有ネットワーク `patent-network` を定義
2. すべてのサービスがこのネットワークに接続するよう設定
3. サービス間の通信が `http://patentdwh-db:5002` のような形式で適切に機能するよう保証

この修正により、DNS 名前解決が正しく機能し、サービス間の通信が可能になります。
