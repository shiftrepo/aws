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


echo "=== Please source ==="
echo ". /home/ec2-user/.nvm/nvm.sh"

echo "envsubst < add_mcp.json > add_token_github_mcp.json#
echo "mcp add-json github-org "$(cat add_token_github_mcp.json)" --verbose"
