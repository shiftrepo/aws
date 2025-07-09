FROM node:18-alpine

# 必要なパッケージのインストール
RUN apk add --no-cache \
    git \
    curl \
    bash \
    ca-certificates \
    wget \
    tar \
    zip \
    unzip \
    shadow

# nvmのインストール (Alpineでは特別な設定が必要)
ENV NVM_DIR /usr/local/nvm
RUN mkdir -p $NVM_DIR
RUN apk add --no-cache --virtual .build-deps \
    build-base \
    python3 \
    && curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash \
    && apk del .build-deps

# nvmセットアップのためのシェル設定
RUN echo 'export NVM_DIR="/usr/local/nvm"' >> /etc/profile.d/nvm.sh \
    && echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"' >> /etc/profile.d/nvm.sh

# GitLab CLIのインストール (Alpine用にバイナリをダウンロード)
RUN wget -O /usr/local/bin/gitlab-cli https://gitlab.com/gitlab-org/cli/releases/download/v1.30.0/gitlab-cli-linux-amd64 \
    && chmod +x /usr/local/bin/gitlab-cli

# 専用ユーザーの作成
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# 作業ディレクトリの設定
WORKDIR /app

# アプリケーションのファイルをコピー
COPY package*.json ./

# 依存関係のインストール
RUN npm install

# 残りのアプリケーションコードをコピー
COPY . .

# アプリケーションディレクトリの所有者を変更
RUN chown -R appuser:appgroup /app

# アプリケーションユーザーに切り替え
USER appuser

# アプリケーションのポート公開
EXPOSE 3000

# 起動コマンド
CMD ["npm", "start"]