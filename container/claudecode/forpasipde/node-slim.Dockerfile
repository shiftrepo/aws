FROM node:18-slim

# GitLab連携やnvm、その他必要なツールのインストール
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    gnupg \
    wget \
    zip \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# nvmのインストール
ENV NVM_DIR /usr/local/nvm
RUN mkdir -p $NVM_DIR
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash

# nvmセットアップのためのシェル設定
RUN echo 'export NVM_DIR="/usr/local/nvm"' >> /etc/profile.d/nvm.sh \
    && echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"' >> /etc/profile.d/nvm.sh

# GitLab CLIのインストール（オプション）
RUN curl -s https://packages.gitlab.com/install/repositories/gitlab/gitlab-ee/script.deb.sh | bash \
    && apt-get update \
    && apt-get install -y gitlab-cli \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /app

# アプリケーションのファイルをコピー
COPY package*.json ./

# 依存関係のインストール
RUN npm install

# 残りのアプリケーションコードをコピー
COPY . .

# アプリケーションのポート公開
EXPOSE 3000

# 起動コマンド
CMD ["npm", "start"]