# Claude Code MCP 導入手順

## Neo4j RAG システムを Claude Code で利用するための完全ガイド

### 概要
このガイドでは、Neo4j RAG（Retrieval-Augmented Generation）システムをClaude Code のMCP（Model Context Protocol）として登録し、対話的にGraphRAGクエリを実行する方法を説明します。

---

## 1. 前提条件の確認

### 1.1 必要なサービスの起動確認
```bash
# Neo4j RAGコンテナが起動していることを確認
podman ps | grep neo4jRAG

# 期待する出力例:
# neo4jRAG  neo4j:latest  Up 2 hours  0.0.0.0:7575->7474/tcp, 0.0.0.0:7587->7687/tcp
```

### 1.2 Python環境の確認
```bash
# Python 3.8以上が必要
python3 --version

# pip が利用可能であることを確認
pip --version
```

---

## 2. MCPサーバーのセットアップ

### 2.1 必要なライブラリのインストール
```bash
# プロジェクトディレクトリに移動
cd /root/aws.git/container/graphRAG

# MCP関連の依存関係をインストール
pip install -r mcp_server/requirements.txt
```

### 2.2 AWS認証情報の設定
```bash
# AWS認証情報を環境変数として設定
export AWS_ACCESS_KEY_ID="your_access_key_here"
export AWS_SECRET_ACCESS_KEY="your_secret_key_here"
export AWS_DEFAULT_REGION="us-east-1"

# 設定の確認
aws configure list
```

### 2.3 MCPサーバーの動作テスト
```bash
# スタンドアロンモードでテスト実行
cd /root/aws.git/container/graphRAG/mcp_server
python test_mcp_standalone.py

# 期待する出力:
# ✅ Neo4j RAG Health Check PASSED
# ✅ Statistics Test PASSED  
# ✅ RAG Query Test PASSED
```

---

## 3. Claude Code の設定

### 3.1 設定ファイルの場所確認
```bash
# Claude Code の設定ディレクトリを作成（存在しない場合）
mkdir -p ~/.claude-code

# 設定ファイルの場所
# Linux/macOS: ~/.claude-code/claude-code-config.json
# Windows: %APPDATA%\Claude Code\claude-code-config.json
```

### 3.2 MCP設定の追加

**方法1: 設定ファイルを直接編集**
```bash
# 設定ファイルを作成/編集
nano ~/.claude-code/claude-code-config.json
```

以下の内容を追加:
```json
{
  "mcpServers": {
    "neo4j-rag": {
      "command": "python",
      "args": ["/root/aws.git/container/graphRAG/mcp_server/neo4j_rag_mcp.py"],
      "env": {
        "NEO4J_URI": "bolt://localhost:7587",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "password",
        "AWS_DEFAULT_REGION": "us-east-1",
        "PYTHONPATH": "/root/aws.git/container/graphRAG/app"
      }
    }
  }
}
```

**方法2: コマンドラインで設定**
```bash
# MCPサーバーを追加
claude-code config add-mcp-server neo4j-rag \
  --command python \
  --args "/root/aws.git/container/graphRAG/mcp_server/neo4j_rag_mcp.py" \
  --env NEO4J_URI=bolt://localhost:7587 \
  --env NEO4J_USER=neo4j \
  --env NEO4J_PASSWORD=password \
  --env AWS_DEFAULT_REGION=us-east-1 \
  --env PYTHONPATH=/root/aws.git/container/graphRAG/app
```

### 3.3 設定の確認
```bash
# 設定されたMCPサーバーを確認
claude-code config list-mcp-servers

# 期待する出力:
# neo4j-rag: python /root/aws.git/container/graphRAG/mcp_server/neo4j_rag_mcp.py
```

---

## 4. 動作確認とテスト

### 4.1 Claude Code の起動とMCP接続確認
```bash
# Claude Code を起動
claude-code

# MCPサーバーの状態確認
claude-code mcp status

# 利用可能なツールの確認
claude-code mcp list-tools
```

### 4.2 基本的な使用方法

**Claude Code セッション内での使用例:**

```
# 健康チェック
Claude Code で「neo4j_rag_health ツールを使用してシステムの状態を確認してください」と入力

# データベース統計情報
Claude Code で「neo4j_rag_stats ツールを使用してデータベースの統計を表示してください」と入力

# RAGクエリの実行
Claude Code で「neo4j_rag_query ツールを使用して『ラオウの兄弟は誰ですか？』という質問に答えてください」と入力
```

### 4.3 サンプルクエリ
```
# 基本的なクエリ例
- 「ラオウの兄弟は誰ですか？」
- 「ケンシロウについて教えてください」
- 「北斗の拳の登場人物について説明してください」
```

---

## 5. トラブルシューティング

### 5.1 よくある問題と解決方法

**問題1: MCPサーバーが起動しない**
```bash
# ログを確認
python /root/aws.git/container/graphRAG/mcp_server/neo4j_rag_mcp.py 2>&1 | tee server.log

# 依存関係を再インストール
pip install --upgrade mcp neo4j langchain-aws boto3
```

**問題2: Neo4j接続エラー**
```bash
# Neo4jコンテナの状態確認
podman ps | grep neo4j

# 接続テスト
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7587', auth=('neo4j', 'password'))
with driver.session() as session:
    result = session.run('RETURN 1')
    print('Neo4j接続成功:', result.single()[0])
driver.close()
"
```

**問題3: AWS Bedrock認証エラー**
```bash
# AWS認証情報の確認
aws sts get-caller-identity

# 認証情報の再設定
aws configure
```

**問題4: Claude Code でツールが認識されない**
```bash
# Claude Code の再起動
# 設定ファイルの権限確認
ls -la ~/.claude-code/claude-code-config.json

# 設定ファイルの構文確認
python -c "import json; print(json.load(open('~/.claude-code/claude-code-config.json')))"
```

### 5.2 デバッグ用コマンド
```bash
# MCPサーバーの健康チェック（JSON-RPC形式）
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "neo4j_rag_health", "arguments": {}}}' | \
python /root/aws.git/container/graphRAG/mcp_server/neo4j_rag_mcp.py

# データベース統計の取得
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "neo4j_rag_stats", "arguments": {}}}' | \
python /root/aws.git/container/graphRAG/mcp_server/neo4j_rag_mcp.py
```

---

## 6. 高度な設定

### 6.1 パフォーマンス最適化
```json
{
  "mcpServers": {
    "neo4j-rag": {
      "command": "python",
      "args": ["/root/aws.git/container/graphRAG/mcp_server/neo4j_rag_mcp.py"],
      "env": {
        "NEO4J_URI": "bolt://localhost:7587",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "password",
        "AWS_DEFAULT_REGION": "us-east-1",
        "PYTHONPATH": "/root/aws.git/container/graphRAG/app",
        "MAX_CHUNKS": "5",
        "LLM_TEMPERATURE": "0.0",
        "LLM_MAX_TOKENS": "2000"
      }
    }
  }
}
```

### 6.2 セキュリティ設定
```bash
# 設定ファイルの権限を制限
chmod 600 ~/.claude-code/claude-code-config.json

# 環境変数ファイルの作成（オプション）
cat > ~/.claude-code/neo4j-rag.env << EOF
NEO4J_PASSWORD=your_secure_password
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
EOF

chmod 600 ~/.claude-code/neo4j-rag.env
```

---

## 7. 完了確認チェックリスト

- [ ] Neo4j RAGコンテナが起動している
- [ ] 必要なPythonライブラリがインストールされている
- [ ] AWS認証情報が正しく設定されている
- [ ] MCPサーバーのスタンドアローンテストが成功している
- [ ] Claude Code の設定ファイルが正しく作成されている
- [ ] `claude-code mcp list-tools` でツールが認識されている
- [ ] RAGクエリが正常に実行できる
- [ ] 適切な回答が返される

---

## 8. 使用例とベストプラクティス

### 8.1 効果的なクエリの書き方
```
# 良い例
「ラオウの兄弟について詳しく教えてください」
「ケンシロウの必殺技について説明してください」
「北斗の拳の世界観について教えてください」

# 改善が必要な例
「何？」「教えて」「情報は？」
```

### 8.2 定期的なメンテナンス
```bash
# 月次メンテナンス
# 1. Neo4jコンテナの再起動
podman restart neo4jRAG

# 2. 依存関係の更新
pip install --upgrade mcp neo4j langchain-aws boto3

# 3. データベースの健康チェック
python /root/aws.git/container/graphRAG/mcp_server/test_mcp_standalone.py
```

---

## 9. サポートとヘルプ

### 9.1 ログの確認方法
```bash
# MCPサーバーのログ
tail -f /var/log/claude-code-mcp.log

# システムログの確認
journalctl -u claude-code -f
```

### 9.2 問題報告時に含める情報
- システム情報（OS、Python バージョン）
- エラーメッセージの全文
- 設定ファイルの内容（パスワード等は除く）
- 実行したコマンドとその出力

---

これで Neo4j RAG システムが Claude Code のMCPとして正常に動作し、対話的にGraphRAGクエリを実行できるようになります。

**重要な注意事項:**
- AWS認証情報は適切に管理してください
- Neo4jのパスワードは本番環境では変更してください
- 定期的にシステムの健康チェックを実行してください