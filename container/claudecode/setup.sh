# Download and install nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash

# in lieu of restarting the shell
\. "$HOME/.nvm/nvm.sh"

# Download and install Node.js:
nvm install 22

# Verify the Node.js version:
node -v # Should print "v22.16.0".
nvm current # Should print "v22.16.0".

# Verify npm version:
npm -v # Should print "10.9.2".

npm install -g @anthropic-ai/claude-code
npm install -g @modelcontextprotocol/server-github

# MCP設定ファイルをグローバル設定に移行し、環境変数を使うようにするスクリプト
# 設定ディレクトリの確認
CONFIG_DIR="$HOME/.config/mcp"
if [ ! -d "$CONFIG_DIR" ]; then
  mkdir -p "$CONFIG_DIR"
  echo "Created config directory: $CONFIG_DIR"
fi

# .mcp.jsonテンプレートファイルを作成
cat > "$CONFIG_DIR/config.json" <<EOL
{
  "mcpServers": {
    "github-org": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "\${GITHUB_SHIFTREPO_PAT}"
      }
    }
  }
}
EOL

echo "=== Please source ==="
echo ". /home/ec2-user/.nvm/nvm.sh"
