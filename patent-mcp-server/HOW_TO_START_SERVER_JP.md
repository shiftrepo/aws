# Patent MCPサーバーの起動方法

Patent MCPサーバーを起動するには、以下の2つの方法があります：

## 方法1：Dockerを使用する方法（推奨）

Dockerは、すべての依存関係があらかじめインストールされた隔離環境を提供します。この方法が推奨されています。

```bash
# patent-mcp-serverディレクトリに移動
cd patent-mcp-server

# Docker Composeでサーバーを起動
docker-compose up
```

サーバーは http://localhost:8000 で利用可能になります。

バックグラウンドモード（デタッチモード）で実行するには：

```bash
docker-compose up -d
```

サーバーを停止するには：

```bash
docker-compose down
```

## 方法2：直接実行する方法

Dockerを使用したくない場合は、サーバーを直接実行できます。必要な依存関係がすべてインストールされていることを確認してください（requirements.txtを参照）。

```bash
# patent-mcp-serverディレクトリに移動
cd patent-mcp-server

# 起動スクリプトを使用
./start_server.sh
```

または手動で：

```bash
# サーバーディレクトリに移動
cd patent-mcp-server

# 親ディレクトリをPythonパスに含める
export PYTHONPATH=$PYTHONPATH:$(dirname $(pwd))

# appディレクトリに移動してサーバーを起動
cd app
python3 server.py
```

## サーバーが実行中であることを確認

起動後、サーバーが実行中であることを確認するには：

```bash
# サーバーが応答しているか確認
curl http://localhost:8000
```

以下のような出力が表示されるはずです：

```json
{"status":"ok","message":"Patent MCP Server is running"}
```

## 日本語の出願人名でテストする

日本語の出願人名（例：「テック株式会社」）でテストする場合は、名前をURLエンコードすることを忘れないでください：

```bash
# エンコードされたURLを生成するヘルパースクリプトを使用
cd patent-mcp-server/app
./curl_examples.sh "テック株式会社"

# またはエンコードされたURLで直接テスト
curl "http://localhost:8000/applicant/%E3%83%86%E3%83%83%E3%82%AF%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE"
```

URLエンコーディングに関する詳細は、[handling_non_ascii_characters.md](./docs/handling_non_ascii_characters.md)を参照してください。
