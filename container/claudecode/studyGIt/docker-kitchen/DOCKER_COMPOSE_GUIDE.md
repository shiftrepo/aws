# Docker Compose ガイド

このドキュメントではDocker Kitchenアプリケーションの`docker-compose.yml`ファイルについて説明します。

## 基本概念

Docker Composeは複数のコンテナアプリケーションを定義・実行するためのツールです。YAMLファイルを使用してサービスを設定し、単一のコマンドですべてのサービスを起動・停止できます。

## docker-compose.ymlの構成

### バージョン指定

```yaml
version: '3.8'
```

使用するDocker Composeファイルフォーマットのバージョンを指定します。これにより特定の機能が利用可能になります。

### サービス定義

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    image: docker-kitchen:latest
    container_name: docker-kitchen
    ports:
      - "3000:80"
    restart: unless-stopped
```

- `app`: サービス名（任意の名前を指定可能）
- `build`: Dockerイメージのビルド設定
  - `context`: ビルドコンテキスト（通常はDockerfileのあるディレクトリ）
  - `dockerfile`: 使用するDockerfileの名前
- `image`: ビルドしたイメージに付ける名前
- `container_name`: 起動するコンテナの名前
- `ports`: ポートマッピング（ホスト:コンテナ）
- `restart`: コンテナの再起動ポリシー

### 開発モード設定

```yaml
# Development mode settings
# volumes:
#   - ./:/app:z,U
#   - /app/node_modules
# command: npm start
```

これらの設定は開発時に便利です：
- `volumes`: ホストのファイルをコンテナにマウント（ホットリロード用）
  - `./:/app:z,U`: カレントディレクトリを `/app` にマウント（SELinuxフラグ付き）
  - `/app/node_modules`: node_modulesをコンテナ内に保持（マウントしない）
- `command`: デフォルトのコマンドを上書き（開発サーバー起動）

### 拡張サービス（コメントアウト）

```yaml
# analytics:
#   image: prom/prometheus:latest
#   container_name: docker-kitchen-analytics
#   ports:
#     - "9090:9090"
#   volumes:
#     - ./prometheus.yml:/etc/prometheus/prometheus.yml
#   depends_on:
#     - app
```

このセクションは複数コンテナ設定のサンプルとして含まれています：
- `depends_on`: サービスの起動順序を指定（analyticsはappの後に起動）

### ボリュームとネットワーク

```yaml
volumes:
  node_modules:

networks:
  default:
    name: docker-kitchen-network
    driver: bridge
```

- `volumes`: 名前付きボリュームの定義
- `networks`: カスタムネットワークの定義
  - `name`: ネットワーク名
  - `driver`: ネットワークドライバー（通常はbridge）

## 使用法

### 基本コマンド

```bash
# 起動
docker-compose up

# バックグラウンドで起動
docker-compose up -d

# ビルドしてから起動
docker-compose up --build

# 停止
docker-compose down

# 停止してボリュームも削除
docker-compose down -v
```

### Podmanでの利用

Podmanを使用する場合は、同等の`podman-compose`コマンドを使用できます：

```bash
podman-compose up --build
podman-compose down
```

## 実践的な活用例

1. **スケーリングのデモ**：
   ```bash
   docker-compose up -d --scale app=3
   ```

2. **ネットワーク検査**：
   ```bash
   docker network inspect docker-kitchen-network
   ```

3. **ボリューム確認**：
   ```bash
   docker volume ls
   ```

4. **個別サービスの再起動**：
   ```bash
   docker-compose restart app
   ```

5. **ログの確認**：
   ```bash
   docker-compose logs -f app
   ```

Docker Composeの詳細については[公式ドキュメント](https://docs.docker.com/compose/)を参照してください。