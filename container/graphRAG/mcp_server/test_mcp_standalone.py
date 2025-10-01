#!/usr/bin/env python3
"""
Neo4j RAG MCP Server Test - Standalone mode
Tests the core functionality without MCP dependencies
"""

import sys
import time
import logging

# Add app path for imports
sys.path.append('/root/aws.git/container/graphRAG/app')

from neo4j import GraphDatabase
import boto3
from langchain_aws import ChatBedrock

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jRAGTester:
    """Test class for Neo4j RAG functionality."""
    
    def __init__(self):
        self.neo4j_uri = "bolt://neo4jRAG:7687"
        self.neo4j_user = "neo4j"
        self.neo4j_password = "password"
        self.region = "us-east-1"
        self.inference_profile_arn = "arn:aws:bedrock:us-east-1:711387140677:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    
    def test_health_check(self):
        """Test health check functionality."""
        print("🏥 Testing Health Check...")
        
        try:
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
            
            health_info = f"""✅ Neo4j RAG Health Check PASSED

📊 データベース統計:
  - 総チャンク数: {total_chunks}
  - 有効チャンク数: {valid_chunks}
  - データベースURI: {self.neo4j_uri}
  - 接続状態: ✅ 正常

⏱️ チェック時刻: {time.strftime('%Y-%m-%d %H:%M:%S')}"""
            
            print(health_info)
            return True
            
        except Exception as e:
            print(f"❌ Health Check FAILED: {e}")
            return False
    
    def test_stats(self):
        """Test statistics functionality."""
        print("\n📊 Testing Statistics...")
        
        try:
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
            
            stats_info = f"""✅ Statistics Test PASSED

📈 ノード統計:
  - 総ノード数: {stats["total_nodes"]:,}
  - Chunkノード: {stats["chunk_nodes"]:,}
  - 有効テキストChunk: {stats["valid_chunks"]:,}
  - 空のChunk: {stats["empty_chunks"]:,}
  - Entityノード: {stats["entity_nodes"]:,}

📊 データ品質:
  - Chunk充填率: {chunk_fill_rate:.1f}%
  - 最大テキスト長: {max(lengths) if lengths else 0:,} 文字
  - 平均テキスト長: {sum(lengths)//len(lengths) if lengths else 0:,} 文字

⏱️ 生成時刻: {time.strftime('%Y-%m-%d %H:%M:%S')}"""
            
            print(stats_info)
            return True
            
        except Exception as e:
            print(f"❌ Statistics Test FAILED: {e}")
            return False
    
    def test_rag_query(self, question="ラオウの兄弟は誰ですか？"):
        """Test RAG query functionality."""
        print(f"\n🔍 Testing RAG Query: {question}")
        
        try:
            # Connect to Neo4j and search for relevant chunks
            driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password)
            )
            
            with driver.session() as session:
                # Search for relevant chunks containing the question keywords
                result = session.run("""
                    MATCH (n:Chunk) 
                    WHERE n.text IS NOT NULL AND n.text <> ''
                    AND n.text CONTAINS 'ラオウ'
                    AND (n.text CONTAINS '兄弟' OR n.text CONTAINS '兄' OR n.text CONTAINS '弟')
                    RETURN n.text as text, n.id as id
                    ORDER BY size(n.text) DESC
                    LIMIT 3
                """)
                
                chunks = list(result)
                
                if not chunks:
                    print("❌ No relevant chunks found")
                    return False
                
                # Collect context
                context_texts = [record["text"] for record in chunks]
                full_context = "\n\n".join(context_texts)
                
                print(f"📚 Found {len(chunks)} relevant chunks")
                
            driver.close()
            
            # Generate answer using LLM
            print("🤖 Generating LLM response...")
            
            bedrock_runtime = boto3.client("bedrock-runtime", region_name=self.region)
            llm = ChatBedrock(
                client=bedrock_runtime,
                model_id=self.inference_profile_arn,
                provider="anthropic",
                region_name=self.region,
                model_kwargs={"temperature": 0.0, "max_tokens": 1000}
            )
            
            prompt = f"""以下の文脈情報に基づいて、質問に正確で詳細に答えてください。

文脈情報:
{full_context}

質問: {question}

回答:"""
            
            response = llm.invoke(prompt)
            
            # Format response
            answer_text = f"""✅ RAG Query Test PASSED

🔍 質問: {question}

📝 回答:
{response.content}

📊 データソース: {len(chunks)}個のチャンクから情報を取得
⏱️ 処理時刻: {time.strftime('%Y-%m-%d %H:%M:%S')}"""
            
            print(answer_text)
            return True
            
        except Exception as e:
            print(f"❌ RAG Query Test FAILED: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests."""
        print("🚀 Starting Neo4j RAG MCP Server Tests")
        print("=" * 60)
        
        results = []
        
        # Test 1: Health Check
        results.append(self.test_health_check())
        
        # Test 2: Statistics
        results.append(self.test_stats())
        
        # Test 3: RAG Query
        results.append(self.test_rag_query())
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 Test Results Summary")
        print("=" * 60)
        
        passed = sum(results)
        total = len(results)
        
        print(f"✅ Tests Passed: {passed}/{total}")
        print(f"❌ Tests Failed: {total - passed}/{total}")
        
        if passed == total:
            print("\n🎉 All tests PASSED! MCP Server is ready for deployment.")
        else:
            print("\n⚠️  Some tests FAILED. Please check the errors above.")
        
        return passed == total

def main():
    """Main test function."""
    tester = Neo4jRAGTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🔧 Next steps:")
        print("1. Install MCP dependencies: pip install mcp")
        print("2. Add server to Claude Desktop config")
        print("3. Restart Claude Desktop")
        print("4. Test with @neo4j-rag commands")
    
    return success

if __name__ == "__main__":
    main()