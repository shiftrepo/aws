FROM amazonlinux:2023

# 必要なパッケージのインストール
RUN dnf update -y \
    && dnf install -y \
    nodejs \
    npm \
    git \
    curl \
    wget \
    tar \
    gzip \
    unzip \
    which \
    procps \
    shadow-utils \
    && dnf clean all

# nvmのインストール
ENV NVM_DIR /usr/local/nvm
RUN mkdir -p $NVM_DIR
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash

# nvmセットアップのためのシェル設定
RUN echo 'export NVM_DIR="/usr/local/nvm"' >> /etc/profile.d/nvm.sh \
    && echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"' >> /etc/profile.d/nvm.sh

# GitLab CLIのインストール（オプション）
RUN curl -s https://packages.gitlab.com/install/repositories/gitlab/gitlab-ee/script.rpm.sh | bash \
    && dnf install -y gitlab-cli \
    && dnf clean all

# 専用ユーザーの作成
RUN useradd -ms /bin/bash appuser

# 作業ディレクトリの設定
WORKDIR /app

# アプリケーションのファイルをコピー
COPY package*.json ./

# 依存関係のインストール
RUN npm install

# 残りのアプリケーションコードをコピー
COPY . .

# アプリケーションディレクトリの所有者を変更
RUN chown -R appuser:appuser /app

# アプリケーションユーザーに切り替え
USER appuser

# アプリケーションのポート公開
EXPOSE 3000

# 起動コマンド
CMD ["npm", "start"]