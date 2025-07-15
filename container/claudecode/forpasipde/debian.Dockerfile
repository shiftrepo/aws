FROM debian:11-slim

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    curl \
    git \
    gnupg \
    wget \
    ca-certificates \
    zip \
    unzip \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Node.jsのインストール
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get update \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# GitLab CLI (glab)のインストール
RUN curl -s https://raw.githubusercontent.com/profclems/glab/trunk/scripts/install.sh | bash

# GitLab CLIが正しくインストールされたか確認
RUN glab --version || echo "GitLab CLI installed"

# 専用ユーザーの作成
RUN useradd -ms /bin/bash claudeuser

# 作業ディレクトリの設定
WORKDIR /app

# Node.jsバージョン確認（デバッグ用）
RUN node --version && npm --version

# Claude Codeと必要なMCPサーバーパッケージをグローバルインストール
RUN npm install -g @anthropic-ai/claude-code \
    && npm install -g @modelcontextprotocol/server-gitlab

# GitLab MCPサーバーパッケージが正しくインストールされたか確認
RUN npx @modelcontextprotocol/server-gitlab --version || echo "GitLab MCP server package installed"

# ディレクトリの所有者を変更
RUN chown -R claudeuser:claudeuser /app

# Claude Code用のユーザーに切り替え
USER claudeuser

# 環境変数の設定
ENV NODE_ENV=production
ENV CLAUDE_CODE_USE_BEDROCK=1

# ホスト名設定（GitLab連携用）
ENV GITLAB_HOST=gitlab.local

# GitLabへのアクセスキー用の環境変数（実行時に上書き可能）
ENV GITLAB_API_TOKEN=""
ENV GITLAB_PERSONAL_ACCESS_TOKEN=""

# 永続化のためにボリュームマウントポイントを作成
VOLUME ["/app/workdir"]

# Claudeユーザーのホームディレクトリに環境設定を追加
RUN echo 'export PATH=$PATH:/usr/local/bin' >> ~/.bashrc

# glabコマンドが利用可能か確認するスクリプトを作成
RUN echo '#!/bin/bash\necho "GitLab CLI (glab) version:"\nglab --version\necho "\nTo configure GitLab CLI with your token, run:\nglab auth login --token YOUR_GITLAB_TOKEN"' > /app/check_glab.sh \
    && chmod +x /app/check_glab.sh

# 起動時にインタラクティブシェルを維持
CMD ["/bin/bash"]