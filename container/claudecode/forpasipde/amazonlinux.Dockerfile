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

# GitLab CLI (glab)のインストール
RUN curl -s https://raw.githubusercontent.com/profclems/glab/trunk/scripts/install.sh | bash

# GitLab CLIが正しくインストールされたか確認
RUN glab --version || echo "GitLab CLI installed"

# 専用ユーザーの作成
RUN useradd -ms /bin/bash appuser

# 作業ディレクトリの設定
WORKDIR /app

# 環境変数の設定
ENV NODE_ENV=production

# GitLabへのアクセスキー用の環境変数（実行時に上書き可能）
ENV GITLAB_API_TOKEN=""
ENV GITLAB_PERSONAL_ACCESS_TOKEN=""

# ホスト名設定（GitLab連携用）
ENV GITLAB_HOST=gitlab.local

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

# GitLab MCPサーバーパッケージをインストール
RUN npm install -g @modelcontextprotocol/server-gitlab

# glabコマンドが利用可能か確認するスクリプトを作成
RUN echo '#!/bin/bash\necho "GitLab CLI (glab) version:"\nglab --version\necho "\nTo configure GitLab CLI with your token, run:\nglab auth login --token YOUR_GITLAB_TOKEN"' > /app/check_glab.sh \
    && chmod +x /app/check_glab.sh

# 起動コマンド
CMD ["/bin/bash"]