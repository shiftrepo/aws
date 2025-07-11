FROM node:22-slim

# Claude Code実行に必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    gnupg \
    wget \
    zip \
    unzip \
    procps \
    && rm -rf /var/lib/apt/lists/*

# 専用ユーザーの作成
RUN useradd -ms /bin/bash claudeuser

# 作業ディレクトリの設定
WORKDIR /app

# Node.jsバージョン確認（デバッグ用）
RUN node --version && npm --version

# Claude Codeと必要なMCPサーバーパッケージをグローバルインストール
RUN npm install -g @anthropic-ai/claude-code \
    && npm install -g @modelcontextprotocol/server-gitlab

# ディレクトリの所有者を変更
RUN chown -R claudeuser:claudeuser /app

# Claude Code用のユーザーに切り替え
USER claudeuser

# 環境変数の設定
ENV NODE_ENV=production
ENV CLAUDE_CODE_USE_BEDROCK=1

# ホスト名設定（GitLab連携用）  
ENV GITLAB_HOST=gitlab.local

# 永続化のためにボリュームマウントポイントを作成
VOLUME ["/app/workdir"]

# Claudeユーザーのホームディレクトリに環境設定を追加
RUN echo 'export PATH=$PATH:/usr/local/bin' >> ~/.bashrc

# 起動時にインタラクティブシェルを維持
CMD ["/bin/bash"]