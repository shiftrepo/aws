# Claude Codeのためのベースイメージ使用ガイド

このドキュメントでは、Claude Codeアプリケーション用に作成された各ベースイメージの使い方とカスタマイズ方法について説明します。

## 提供されるDockerfile

以下の4つのDockerfileを用意しています：

1. `node-slim.Dockerfile` - Debian slimベースのNode.jsイメージ
2. `node-alpine.Dockerfile` - Alpineベースの軽量Node.jsイメージ
3. `amazonlinux.Dockerfile` - Amazon Linux 2023ベースのイメージ
4. `ubuntu.Dockerfile` - Ubuntu 22.04ベースのイメージ

## ビルド方法

各Dockerfileをビルドするには、以下のコマンドを使用します：

```bash
# Node.js (Debian slim) イメージのビルド
docker build -t claudecode:node-slim -f node-slim.Dockerfile .

# Node.js (Alpine) イメージのビルド
docker build -t claudecode:alpine -f node-alpine.Dockerfile .

# Amazon Linux イメージのビルド
docker build -t claudecode:amazonlinux -f amazonlinux.Dockerfile .

# Ubuntu イメージのビルド
docker build -t claudecode:ubuntu -f ubuntu.Dockerfile .
```

## イメージの選択ガイド

各イメージの使用シナリオとメリットを以下に示します：

### 1. Node.js (Debian slim)
- **適したシナリオ**: 本番環境、バランスの取れたパフォーマンスと機能性が必要な場合
- **メリット**: 
  - 比較的小さいイメージサイズ
  - 必要十分なツールセット
  - 安定性と互換性のバランスが良い
- **推奨環境**: 一般的な本番環境、CI/CDパイプライン

### 2. Node.js (Alpine)
- **適したシナリオ**: リソースが限られた環境、最小限のイメージサイズが必要な場合
- **メリット**:
  - 非常に小さいイメージサイズ
  - 起動時間の短縮
  - セキュリティ面の利点（攻撃対象領域の削減）
- **推奨環境**: Kubernetesクラスタ、マイクロサービス環境、IoTデバイス

### 3. Amazon Linux 2023
- **適したシナリオ**: AWS環境での運用、AWSサービスとの深い連携
- **メリット**:
  - AWSサービスとの互換性
  - 長期サポート (2029年まで)
  - AWSツールチェーンとの統合が容易
- **推奨環境**: AWS ECS、AWS EKS、EC2インスタンス

### 4. Ubuntu 22.04
- **適したシナリオ**: 開発環境、広いエコシステムが必要な場合
- **メリット**:
  - 豊富なドキュメントとコミュニティサポート
  - 広い互換性
  - 開発ツールの充実
- **推奨環境**: 開発環境、テスト環境

## カスタマイズ方法

### Node.jsバージョンのカスタマイズ

ベースイメージのNode.jsバージョンを変更する場合は、Dockerfileの最初の行を変更します：

```dockerfile
# 例: Node.js 20 を使用したい場合
FROM node:20-slim
# または
FROM node:20-alpine
```

### nvmを使用したNode.jsバージョン管理

nvmを使ってNode.jsのバージョンを切り替える場合：

```bash
# コンテナ内で特定のNode.jsバージョンをインストール
source /etc/profile.d/nvm.sh
nvm install 16
nvm use 16
```

Dockerfileでこれを自動化する場合：

```dockerfile
# 特定のNode.jsバージョンを自動的にインストール
RUN source $NVM_DIR/nvm.sh \
    && nvm install 16 \
    && nvm alias default 16 \
    && nvm use default
```

### 追加パッケージのインストール

#### Debian/Ubuntu系

```dockerfile
RUN apt-get update && apt-get install -y \
    package1 \
    package2 \
    && rm -rf /var/lib/apt/lists/*
```

#### Alpine系

```dockerfile
RUN apk add --no-cache \
    package1 \
    package2
```

#### Amazon Linux系

```dockerfile
RUN dnf install -y \
    package1 \
    package2 \
    && dnf clean all
```

### GitLab連携のカスタマイズ

GitLabとの連携を強化したい場合、以下の設定を追加できます：

```dockerfile
# GitLab Runner のインストール
RUN curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | bash \
    && apt-get update \
    && apt-get install -y gitlab-runner \
    && rm -rf /var/lib/apt/lists/*

# GitLab CI 環境変数の設定
ENV CI_SERVER_URL="https://gitlab.example.com"
ENV CI_REGISTRY="registry.example.com"
```

## セキュリティ対策

セキュリティを強化するためのベストプラクティス：

1. **非rootユーザーの使用**: 既にDockerfileに含まれています
2. **最小権限の原則**: 必要なアクセス権のみを付与
3. **マルチステージビルド**: 本番イメージを小さく保つ

マルチステージビルドの例：

```dockerfile
# ビルドステージ
FROM node:18-slim as builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 本番ステージ
FROM node:18-slim
WORKDIR /app
COPY --from=builder /app/build ./build
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./
USER appuser
CMD ["npm", "start"]
```

## トラブルシューティング

一般的な問題と解決策：

1. **nvmコマンドが見つからない**:
   ```bash
   source /etc/profile.d/nvm.sh
   ```

2. **パッケージのインストールエラー**:
   - Debianベース: `apt-get update`の実行
   - Alpine: 必要なビルドツールの追加 `apk add --no-cache build-base python3`
   - Amazon Linux: `dnf update`の実行

3. **パーミッションエラー**:
   ```bash
   chown -R appuser:appuser /問題のディレクトリ
   ```

## 結論

Claude Codeの要件に基づいて、本番環境には`node-slim.Dockerfile`または`node-alpine.Dockerfile`をお勧めします。AWS環境では`amazonlinux.Dockerfile`、開発環境では`ubuntu.Dockerfile`が最適です。

特定のニーズに合わせてこれらのDockerfileをカスタマイズし、必要に応じて追加のツールや設定を組み込んでください。