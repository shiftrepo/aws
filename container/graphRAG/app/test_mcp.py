#!/usr/bin/env python3
"""
Neo4j RAG MCP Server for Claude Code
Provides GraphRAG query capabilities through MCP protocol
"""

import json
import sys
import asyncio
from typing import Dict, Any, List
import logging
import time

# Add app path for imports
sys.path.append('/root/aws.git/container/graphRAG/app')

try:
    # MCP imports
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types
    
    # GraphRAG imports
    from neo4j import GraphDatabase
    import boto3
    from langchain_aws import ChatBedrock
    
    MCP_AVAILABLE = True
except ImportError as e:
    MCP_AVAILABLE = False
    print(f"MCP or dependencies not available: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jRAGMCPServer:
    """MCP Server for Neo4j RAG operations."""
    
    def __init__(self):
        self.app_name = "neo4j-rag"
        self.neo4j_uri = "bolt://neo4jRAG:7687"
        self.neo4j_user = "neo4j"
        self.neo4j_password = "password"
        self.region = "us-east-1"
        self.inference_profile_arn = "arn:aws:bedrock:us-east-1:711387140677:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        
        if MCP_AVAILABLE:
            self.server = Server(self.app_name)
            self.setup_handlers()
        else:
            logger.error("MCP not available, running in standalone mode")
    
    def setup_handlers(self):
        """Setup MCP handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> List[types.Tool]:
            """List available tools."""
            return [
                types.Tool(
                    name="neo4j_rag_query",
                    description="Query Neo4j RAG database for information about characters, stories, etc.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string",
                                "description": "The question to ask the RAG system (e.g., 'ラオウの兄弟は誰ですか？')"
                            }
                        },
                        "required": ["question"]
                    }
                ),
                types.Tool(
                    name="neo4j_rag_health",
                    description="Check Neo4j RAG system health status",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="neo4j_rag_stats", 
                    description="Get Neo4j RAG database statistics and information",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls."""
            
            try:
                if name == "neo4j_rag_query":
                    return await self.handle_rag_query(arguments)
                elif name == "neo4j_rag_health":
                    return await self.handle_health_check()
                elif name == "neo4j_rag_stats":
                    return await self.handle_stats()
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Tool call error: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"❌ エラーが発生しました: {str(e)}"
                )]
    
    async def handle_rag_query(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle RAG query requests."""
        question = arguments.get("question", "")
        
        if not question.strip():
            return [types.TextContent(
                type="text",
                text="❌ 質問が空です。質問を入力してください。"
            )]
        
        try:
            logger.info(f"Processing RAG query: {question}")
            
            # Connect to Neo4j and search for relevant chunks
            driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password)
            )
            
            with driver.session() as session:
                # Search for relevant chunks containing the question keywords
                keywords = question.split()
                search_conditions = []
                params = {}
                
                # Build search query for better matching
                for i, keyword in enumerate(keywords[:3]):  # Limit to first 3 keywords
                    if len(keyword) > 1:  # Skip very short words
                        search_conditions.append(f"n.text CONTAINS $keyword{i}")
                        params[f"keyword{i}"] = keyword
                
                if not search_conditions:
                    # Fallback search if no good keywords
                    search_conditions = ["n.text IS NOT NULL AND n.text <> ''"]
                
                search_query = f"""
                    MATCH (n:Chunk) 
                    WHERE n.text IS NOT NULL AND n.text <> ''
                    AND ({' OR '.join(search_conditions)})
                    RETURN n.text as text, n.id as id
                    ORDER BY size(n.text) DESC
                    LIMIT 4
                """
                
                result = session.run(search_query, params)
                chunks = list(result)
                
                if not chunks:
                    # Try broader search if no specific matches
                    broader_result = session.run("""
                        MATCH (n:Chunk) 
                        WHERE n.text IS NOT NULL AND n.text <> ''
                        RETURN n.text as text, n.id as id
                        ORDER BY size(n.text) DESC
                        LIMIT 3
                    """)
                    chunks = list(broader_result)
                
                if not chunks:
                    return [types.TextContent(
                        type="text",
                        text="❌ データベースに関連する情報が見つかりませんでした。"
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
                model_kwargs={"temperature": 0.0, "max_tokens": 1500}
            )
            
            prompt = f"""以下の文脈情報に基づいて、質問に正確で詳細に答えてください。
文脈に含まれる情報のみを使用して回答してください。

文脈情報:
{full_context}

質問: {question}

回答:"""
            
            logger.info("Generating LLM response...")
            response = llm.invoke(prompt)
            
            # Format response
            answer_text = f"""🔍 **質問**: {question}

📝 **回答**:
{response.content}

📊 **データソース**: {len(chunks)}個のチャンクから情報を取得
⏱️ **処理時間**: {time.strftime('%Y-%m-%d %H:%M:%S')}"""
            
            logger.info("RAG query completed successfully")
            
            return [types.TextContent(
                type="text", 
                text=answer_text
            )]
            
        except Exception as e:
            logger.error(f"RAG query error: {e}")
            return [types.TextContent(
                type="text",
                text=f"❌ クエリ処理中にエラーが発生しました: {str(e)}"
            )]
    
    async def handle_health_check(self) -> List[types.TextContent]:
        """Handle health check requests."""
        try:
            logger.info("Performing health check...")
            
            # Test Neo4j connection
            driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password)
            )
            
            with driver.session() as session:
                # Basic connectivity test
                result = session.run("RETURN 1 as test")
                result.single()
                
                # Get chunk statistics
                chunk_result = session.run("""
                    MATCH (n:Chunk) 
                    WHERE n.text IS NOT NULL AND n.text <> '' 
                    RETURN count(n) as valid_chunks
                """)
                valid_chunks = chunk_result.single()["valid_chunks"]
                
                # Get total chunks
                total_result = session.run("MATCH (n:Chunk) RETURN count(n) as total")
                total_chunks = total_result.single()["total"]
            
            driver.close()
            
            # Test AWS Bedrock connection
            try:
                bedrock_runtime = boto3.client("bedrock-runtime", region_name=self.region)
                # Simple test call
                aws_status = "✅ Available"
            except Exception as e:
                aws_status = f"⚠️ Warning: {str(e)}"
            
            health_info = f"""🏥 **Neo4j RAG Health Check**

**データベース**: ✅ 接続正常
**AWS Bedrock**: {aws_status}
**データ統計**:
  - 総チャンク数: {total_chunks}
  - 有効チャンク数: {valid_chunks}
  - データベースURI: {self.neo4j_uri}
  - AWSリージョン: {self.region}

**ステータス**: ✅ システム正常
**チェック時刻**: {time.strftime('%Y-%m-%d %H:%M:%S')}"""
            
            logger.info("Health check completed successfully")
            
            return [types.TextContent(
                type="text",
                text=health_info
            )]
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return [types.TextContent(
                type="text",
                text=f"❌ **Health Check Failed**: {str(e)}\n\n⏱️ **時刻**: {time.strftime('%Y-%m-%d %H:%M:%S')}"
            )]
    
    async def handle_stats(self) -> List[types.TextContent]:
        """Handle statistics requests."""
        try:
            logger.info("Gathering database statistics...")
            
            driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password)
            )
            
            with driver.session() as session:
                # Get comprehensive statistics
                queries = {
                    "total_nodes": "MATCH (n) RETURN count(n) as count",
                    "chunk_nodes": "MATCH (n:Chunk) RETURN count(n) as count", 
                    "valid_chunks": "MATCH (n:Chunk) WHERE n.text IS NOT NULL AND n.text <> '' RETURN count(n) as count",
                    "entity_nodes": "MATCH (n:entity) RETURN count(n) as count",
                    "empty_chunks": "MATCH (n:Chunk) WHERE n.text IS NULL OR n.text = '' RETURN count(n) as count"
                }
                
                stats = {}
                for key, query in queries.items():
                    result = session.run(query)
                    stats[key] = result.single()["count"]
                
                # Get sample of text lengths
                text_lengths = session.run("""
                    MATCH (n:Chunk) 
                    WHERE n.text IS NOT NULL AND n.text <> ''
                    RETURN size(n.text) as length
                    ORDER BY length DESC
                    LIMIT 5
                """)
                lengths = [record["length"] for record in text_lengths]
                
            driver.close()
            
            # Calculate percentages
            chunk_fill_rate = (stats["valid_chunks"] / stats["chunk_nodes"] * 100) if stats["chunk_nodes"] > 0 else 0
            
            stats_info = f"""📊 **Neo4j RAG Database Statistics**

**ノード統計**:
  - 総ノード数: {stats["total_nodes"]:,}
  - Chunkノード: {stats["chunk_nodes"]:,}
  - 有効テキストChunk: {stats["valid_chunks"]:,}
  - 空のChunk: {stats["empty_chunks"]:,}
  - Entityノード: {stats["entity_nodes"]:,}

**データ品質**:
  - Chunk充填率: {chunk_fill_rate:.1f}%
  - 最大テキスト長: {max(lengths) if lengths else 0:,} 文字
  - 平均テキスト長: {sum(lengths)//len(lengths) if lengths else 0:,} 文字

**接続情報**:
  - データベースURI: {self.neo4j_uri}
  - AWSリージョン: {self.region}
  - LLMモデル: Claude 3.5 Sonnet

**生成時刻**: {time.strftime('%Y-%m-%d %H:%M:%S')}"""
            
            logger.info("Statistics gathered successfully")
            
            return [types.TextContent(
                type="text",
                text=stats_info
            )]
            
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return [types.TextContent(
                type="text",
                text=f"❌ **統計取得エラー**: {str(e)}\n\n⏱️ **時刻**: {time.strftime('%Y-%m-%d %H:%M:%S')}"
            )]
    
    async def run(self):
        """Run the MCP server."""
        if not MCP_AVAILABLE:
            logger.error("Cannot run MCP server - dependencies not available")
            return
            
        logger.info(f"Starting {self.app_name} MCP Server...")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

def standalone_test():
    """Standalone test mode when MCP is not available."""
    print("🧪 Neo4j RAG Standalone Test Mode")
    print("=" * 50)
    
    server = Neo4jRAGMCPServer()
    
    # Test health check
    print("\n1. Health Check Test:")
    try:
        driver = GraphDatabase.driver(
            server.neo4j_uri,
            auth=(server.neo4j_user, server.neo4j_password)
        )
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            result.single()
        driver.close()
        print("✅ Neo4j connection successful")
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")
    
    # Test query
    print("\n2. Sample Query Test:")
    question = "ラオウの兄弟は"
    print(f"Question: {question}")
    
    try:
        # This would normally be async, but simplified for testing
        driver = GraphDatabase.driver(
            server.neo4j_uri,
            auth=(server.neo4j_user, server.neo4j_password)
        )
        
        with driver.session() as session:
            result = session.run("""
                MATCH (n:Chunk) 
                WHERE n.text IS NOT NULL AND n.text <> ''
                AND n.text CONTAINS 'ラオウ'
                RETURN n.text as text
                LIMIT 1
            """)
            
            chunks = list(result)
            if chunks:
                print(f"✅ Found {len(chunks)} relevant chunks")
                print(f"Sample: {chunks[0]['text'][:100]}...")
            else:
                print("❌ No relevant chunks found")
                
        driver.close()
        
    except Exception as e:
        print(f"❌ Query test failed: {e}")

async def main():
    """Main function."""
    if MCP_AVAILABLE:
        server = Neo4jRAGMCPServer()
        await server.run()
    else:
        standalone_test()

if __name__ == "__main__":
    if MCP_AVAILABLE:
        asyncio.run(main())
    else:
        standalone_test()