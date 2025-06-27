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

cat <<EOF >> /home/ec2-user/.bashrc
# Claude codee 
# Bedrockを使う設定
export CLAUDE_CODE_USE_BEDROCK=1

# Amazon Bedrock (モデルIDを使用)
export ANTHROPIC_MODEL=us.anthropic.claude-3-7-sonnet-20250219-v1:0
#export ANTHROPIC_MODEL=us.anthropic.claude-sonnet-4-20250514-v1:0
export ANTHROPIC_SMALL_FAST_MODEL=us.anthropic.claude-3-5-haiku-20241022-v1:0
. /home/ec2-user/.nvm/nvm.sh
EOF

. ~/.bashrc
envsubst < add_mcp.json > add_token_github_mcp.json
claude mcp add-json github-org "$(cat add_token_github_mcp.json)" --verbose
rm -f add_token_github_mcp.json
