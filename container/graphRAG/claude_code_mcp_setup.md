# Claude Code MCP Registration Guide

## Neo4j RAG Connector を Claude Code MCP として登録する手順

**注意**: このガイドはClaude Code CLI用です（Claude Desktopではありません）

### 1. MCP Server の準備

#### 1.1 MCP Server スクリプトの作成

```bash
# MCP Server ディレクトリを作成
mkdir -p /root/aws.git/container/graphRAG/mcp_server
cd /root/aws.git/container/graphRAG/mcp_server
```

#### 1.2 MCP Server 実装ファイルの作成

**`mcp_server/neo4j_rag_mcp.py`**

```python
#!/usr/bin/env python3
"""
Neo4j RAG MCP Server for Claude Code
Provides GraphRAG query capabilities through MCP protocol
"""

import json
import sys
import asyncio
from typing import Dict, Any, List, Optional
import logging

# MCP Server imports
from mcp import Server, types
from mcp.server import NotificationOptions, InitializationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

# GraphRAG imports
sys.path.append('/root/aws.git/container/graphRAG/app')
from neo4j import GraphDatabase
from langchain_aws import BedrockEmbeddings, ChatBedrock
import boto3

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jRAGMCPServer:
    """MCP Server for Neo4j RAG operations."""
    
    def __init__(self):
        self.server = Server("neo4j-rag")
        self.neo4j_uri = "bolt://neo4jRAG:7687"
        self.neo4j_user = "neo4j"
        self.neo4j_password = "password"
        self.region = "us-east-1"
        self.inference_profile_arn = "arn:aws:bedrock:us-east-1:711387140677:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        
        # Setup handlers
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup MCP handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> List[types.Tool]:
            """List available tools."""
            return [
                types.Tool(
                    name="neo4j_rag_query",
                    description="Query Neo4j RAG database for information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string",
                                "description": "The question to ask the RAG system"
                            }
                        },
                        "required": ["question"]
                    }
                ),
                types.Tool(
                    name="neo4j_rag_health",
                    description="Check Neo4j RAG system health",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="neo4j_rag_stats",
                    description="Get Neo4j RAG database statistics",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls."""
            
            if name == "neo4j_rag_query":
                return await self.handle_rag_query(arguments)
            elif name == "neo4j_rag_health":
                return await self.handle_health_check()
            elif name == "neo4j_rag_stats":
                return await self.handle_stats()
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    async def handle_rag_query(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle RAG query requests."""
        question = arguments.get("question", "")
        
        try:
            # Connect to Neo4j and search for relevant chunks
            driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password)
            )
            
            with driver.session() as session:
                # Search for relevant chunks
                result = session.run("""
                    MATCH (n:Chunk) 
                    WHERE n.text IS NOT NULL 
                    AND n.text <> '' 
                    AND n.text CONTAINS $keyword
                    RETURN n.text as text, n.id as id
                    ORDER BY size(n.text) DESC
                    LIMIT 3
                """, keyword=question.split()[0] if question.split() else "")
                
                chunks = list(result)
                
                if not chunks:
                    return [types.TextContent(
                        type="text",
                        text="関連する情報が見つかりませんでした。"
                    )]
                
                # Collect context
                context_texts = [record["text"] for record in chunks]
                full_context = "\n\n".join(context_texts)
                
            driver.close()
            
            # Generate answer using LLM
            bedrock_runtime = boto3.client("bedrock-runtime", region_name=self.region)
            llm = ChatBedrock(
                client=bedrock_runtime,
                model_id=self.inference_profile_arn,
                provider="anthropic",
                region_name=self.region,
                model_kwargs={"temperature": 0.0, "max_tokens": 1000}
            )
            
            prompt = f"""以下の文脈情報に基づいて、質問に正確に答えてください。

文脈情報:
{full_context}

質問: {question}

回答:"""
            
            response = llm.invoke(prompt)
            
            # Format response
            answer_text = f"質問: {question}\n\n回答:\n{response.content}\n\n情報源: {len(chunks)}個のデータチャンクから回答生成"
            
            return [types.TextContent(
                type="text",
                text=answer_text
            )]
            
        except Exception as e:
            logger.error(f"RAG query error: {e}")
            return [types.TextContent(
                type="text",
                text=f"エラーが発生しました: {str(e)}"
            )]
    
    async def handle_health_check(self) -> List[types.TextContent]:
        """Handle health check requests."""
        try:
            driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password)
            )
            
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                result.single()
                
                # Get basic stats
                node_result = session.run("MATCH (n:Chunk) WHERE n.text IS NOT NULL AND n.text <> '' RETURN count(n) as count")
                node_count = node_result.single()["count"]
            
            driver.close()
            
            health_info = f"""Neo4j RAG Health Check
Status: ✅ Healthy
Database: Connected
Valid Chunks: {node_count}
Timestamp: {import time; time.strftime('%Y-%m-%d %H:%M:%S')}"""
            
            return [types.TextContent(
                type="text",
                text=health_info
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Health Check Failed: {str(e)}"
            )]
    
    async def handle_stats(self) -> List[types.TextContent]:
        """Handle statistics requests."""
        try:
            driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password)
            )
            
            with driver.session() as session:
                # Get various statistics
                total_nodes = session.run("MATCH (n) RETURN count(n) as count").single()["count"]
                chunk_nodes = session.run("MATCH (n:Chunk) RETURN count(n) as count").single()["count"]
                valid_chunks = session.run("MATCH (n:Chunk) WHERE n.text IS NOT NULL AND n.text <> '' RETURN count(n) as count").single()["count"]
                entity_nodes = session.run("MATCH (n:entity) RETURN count(n) as count").single()["count"]
                
            driver.close()
            
            stats_info = f"""Neo4j RAG Database Statistics
================================
Total Nodes: {total_nodes}
Chunk Nodes: {chunk_nodes}
Valid Text Chunks: {valid_chunks}
Entity Nodes: {entity_nodes}
Database URI: {self.neo4j_uri}
Region: {self.region}"""
            
            return [types.TextContent(
                type="text",
                text=stats_info
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Stats Error: {str(e)}"
            )]
    
    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, 
                write_stream,
                InitializationOptions(
                    server_name="neo4j-rag",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )

async def main():
    """Main function."""
    server = Neo4jRAGMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
```

#### 1.3 MCP Server の依存関係定義

**`mcp_server/requirements.txt`**

```txt
mcp>=1.0.0
neo4j>=5.25.0
langchain-aws>=0.2.0
boto3>=1.39.0
```

#### 1.4 実行可能スクリプトの作成

**`mcp_server/run_server.py`**

```python
#!/usr/bin/env python3
"""
Neo4j RAG MCP Server launcher
"""

import subprocess
import sys
import os

def main():
    """Launch MCP Server."""
    # Change to server directory
    server_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(server_dir)
    
    # Run the server
    python_path = sys.executable
    server_script = os.path.join(server_dir, "neo4j_rag_mcp.py")
    
    try:
        subprocess.run([python_path, server_script], check=True)
    except KeyboardInterrupt:
        print("\nMCP Server stopped by user")
    except Exception as e:
        print(f"Error running MCP Server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 2. Claude Code MCP 設定

#### 2.1 Claude Code 設定ファイルの場所

Claude Code の設定ファイルは以下の場所にあります：

**macOS/Linux:**
```
~/.claude-code/claude-code-config.json
```

**Windows:**
```
%APPDATA%\Claude Code\claude-code-config.json
```

#### 2.2 MCP 設定の追加

設定ファイルに以下を追加：

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
        "AWS_ACCESS_KEY_ID": "your_access_key",
        "AWS_SECRET_ACCESS_KEY": "your_secret_key"
      }
    }
  }
}
```

#### 2.3 Claude Code コマンドラインでの設定

または、コマンドラインで直接設定：

```bash
# MCP サーバーを追加
claude-code config add-mcp-server neo4j-rag \
  --command python \
  --args "/root/aws.git/container/graphRAG/mcp_server/neo4j_rag_mcp.py" \
  --env NEO4J_URI=bolt://localhost:7587 \
  --env NEO4J_USER=neo4j \
  --env NEO4J_PASSWORD=password \
  --env AWS_DEFAULT_REGION=us-east-1

# 設定確認
claude-code config list-mcp-servers
```

### 3. セットアップ手順

#### 3.1 前提条件

1. **Docker コンテナが稼働中**
   ```bash
   podman ps | grep neo4jRAG
   ```

2. **Python 依存関係のインストール**
   ```bash
   pip install mcp neo4j langchain-aws boto3
   ```

#### 3.2 MCP Server のテスト

```bash
# MCP Server 単体テスト
cd /root/aws.git/container/graphRAG/mcp_server
python neo4j_rag_mcp.py
```

#### 3.3 Claude Code での確認

1. **MCP サーバー状態確認**
   ```bash
   claude-code mcp status
   ```

2. **利用可能ツール確認**
   ```bash
   claude-code mcp list-tools
   ```

3. **接続テスト**
   ```bash
   claude-code mcp test neo4j-rag
   ```

#### 3.4 使用例

Claude Code セッションで以下のように使用できます：

```bash
# Claude Code 起動
claude-code

# MCPツールの使用
What are Raoh's brothers? (Use the neo4j-rag tool)
ラオウの兄弟は誰ですか？ (neo4j-ragツールを使用)

# または直接ツール呼び出し
claude-code --use-mcp neo4j-rag --query "ラオウの兄弟は誰ですか？"
```

### 4. トラブルシューティング

#### 4.1 よくある問題

**問題1: MCP Server が起動しない**
```bash
# ログを確認
python neo4j_rag_mcp.py 2>&1 | tee server.log
```

**問題2: Neo4j 接続エラー**
```bash
# 接続テスト
python -c "from neo4j import GraphDatabase; print('Neo4j OK')"
```

**問題3: AWS認証エラー**
```bash
# AWS設定確認
aws configure list
```

#### 4.2 デバッグ用コマンド

```bash
# MCP Server 健康チェック
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "neo4j_rag_health", "arguments": {}}}' | python neo4j_rag_mcp.py

# 統計情報取得
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "neo4j_rag_stats", "arguments": {}}}' | python neo4j_rag_mcp.py
```

### 5. 設定の最適化

#### 5.1 パフォーマンス調整

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
        "MAX_CHUNKS": "5",
        "LLM_TEMPERATURE": "0.0",
        "LLM_MAX_TOKENS": "1500"
      }
    }
  }
}
```

#### 5.2 セキュリティ設定

```bash
# 設定ファイルの権限設定
chmod 600 ~/.config/claude-desktop/claude_desktop_config.json

# 環境変数での認証情報管理
export NEO4J_PASSWORD="your_secure_password"
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
```

### 6. 完了確認

1. **MCP Server が正常に起動**
2. **Claude Code でツールが認識される**
3. **Neo4j RAG クエリが実行できる**
4. **適切な回答が返される**

これで Neo4j RAG Connector が Claude Code の MCP として正常に動作します。

---

**注意事項:**
- AWS認証情報は適切に設定してください
- Neo4j コンテナが起動していることを確認してください
- Claude Code の再起動が必要な場合があります
- ログファイルでデバッグ情報を確認してください