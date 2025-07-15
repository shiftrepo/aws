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

# 必要なツールのインストール
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    sudo \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --break-system-packages pytest black flake8 mypy && \
    npm install -g uv

# タイムゾーンのAsia/Tokyo設定
RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime && \
    echo "Asia/Tokyo" > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata

# sudo権限を付与
RUN echo "claudeuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Claude Codeと必要なMCPサーバーパッケージをグローバルインストール
RUN npm install -g @anthropic-ai/claude-code \
    && npm install -g @modelcontextprotocol/server-gitlab \
    && npm install -g @modelcontextprotocol/server-filesystem \
    && npm install -g @modelcontextprotocol/server-sequential-thinking \
    && npm install -g mcp-server-sqlite-npx \
    && npm install -g @cyanheads/git-mcp-server

# MCPサーバーパッケージが正しくインストールされたか確認
RUN npx @modelcontextprotocol/server-gitlab --version || echo "GitLab MCP server package installed" && \
    npx @modelcontextprotocol/server-filesystem --version || echo "Filesystem MCP server package installed" && \
    npx @modelcontextprotocol/server-sequential-thinking --version || echo "Sequential Thinking MCP server package installed" && \
    npx mcp-server-sqlite-npx --version || echo "SQLite MCP server package installed" && \
    npx @cyanheads/git-mcp-server --version || echo "Git MCP server package installed"

# MCPサーバー登録スクリプトをコンテナ内にコピー
COPY setup_mcp_servers.sh /app/setup_mcp_servers.sh

# ディレクトリの所有者を変更
RUN chown -R claudeuser:claudeuser /app && chmod +x /app/setup_mcp_servers.sh

# Claude Code用のユーザーに切り替え
USER claudeuser

# 環境変数の設定
ENV NODE_ENV=production
ENV CLAUDE_CODE_USE_BEDROCK=1

# ホスト名設定（GitLab連携用）
ENV GITLAB_HOST=gitlab.local

# MCPサーバー関連の環境変数設定（実行時に上書き可能）
ENV GITLAB_API_TOKEN=""
ENV GITLAB_PERSONAL_ACCESS_TOKEN=""
ENV MCP_FILESYSTEM_ENABLED=1
ENV MCP_SEQUENTIAL_THINKING_ENABLED=1
ENV MCP_SQLITE_ENABLED=1
ENV MCP_GIT_ENABLED=1
ENV TZ=Asia/Tokyo

# 永続化のためにボリュームマウントポイントを作成
VOLUME ["/app/workdir"]

# Claudeユーザーのホームディレクトリに環境設定を追加
RUN echo 'export PATH=$PATH:/usr/local/bin' >> ~/.bashrc

# glabコマンドが利用可能か確認するスクリプトを作成
RUN echo '#!/bin/bash\necho "GitLab CLI (glab) version:"\nglab --version\necho "\nTo configure GitLab CLI with your token, run:\nglab auth login --token YOUR_GITLAB_TOKEN"' > /app/check_glab.sh \
    && chmod +x /app/check_glab.sh

# 起動時にインタラクティブシェルを維持
CMD ["/bin/bash"]