# Node.js 18 LTS
FROM node:18-alpine

# 作業ディレクトリ設定
WORKDIR /workspace

# パッケージファイルをコピー
COPY package*.json ./

# 依存関係インストール
RUN npm ci --only=production

# ソースコードをコピー
COPY . .

# デフォルトコマンド
CMD ["node", "src/index.js", "--help"]
