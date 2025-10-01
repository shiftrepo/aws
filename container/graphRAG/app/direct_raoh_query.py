"""
Direct query for Raoh brothers information using Neo4j database query.
"""

import boto3
from neo4j import GraphDatabase
from langchain_aws import BedrockEmbeddings, ChatBedrock

# Neo4j RAG connection
NEO4J_URI_RAG = "bolt://neo4jRAG:7687"
NEO4J_USER_RAG = "neo4j"
NEO4J_PASS_RAG = "password"

# AWS configuration
region = "us-east-1"
bedrock_runtime = boto3.client("bedrock-runtime", region_name=region)
inference_profile_arn = "arn:aws:bedrock:us-east-1:711387140677:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0"

def direct_raoh_query():
    """Direct query for Raoh brothers information."""
    question = "ラオウの兄弟は誰ですか？"
    
    print(f"🎯 Direct Neo4j Query for Raoh Brothers")
    print(f"Question: {question}")
    print("=" * 60)
    
    try:
        # Connect to Neo4j directly
        driver = GraphDatabase.driver(
            NEO4J_URI_RAG,
            auth=(NEO4J_USER_RAG, NEO4J_PASS_RAG)
        )
        
        print("1. Connecting to Neo4j...")
        
        with driver.session() as session:
            print("2. Searching for Raoh-related chunks...")
            
            # Search for chunks containing brother information
            result = session.run("""
                MATCH (n:Chunk) 
                WHERE n.text IS NOT NULL 
                AND n.text <> '' 
                AND (n.text CONTAINS 'ラオウ' OR n.text CONTAINS 'ラオウ')
                AND (n.text CONTAINS '兄弟' OR n.text CONTAINS '兄' OR n.text CONTAINS '弟')
                RETURN n.text as text, n.id as id
                ORDER BY size(n.text) DESC
                LIMIT 3
            """)
            
            chunks = list(result)
            print(f"   ✓ Found {len(chunks)} relevant chunks")
            
            if not chunks:
                print("❌ No relevant chunks found")
                return False
            
            # Collect context
            context_texts = []
            print(f"\n📚 Retrieved Context:")
            print("-" * 40)
            
            for i, record in enumerate(chunks, 1):
                text = record["text"]
                chunk_id = record["id"]
                
                print(f"\n【Chunk {i}】(ID: {chunk_id[:8]}...)")
                print(f"Content: {text[:300]}...")
                
                context_texts.append(text)
                
                # Extract brother information
                if "兄弟" in text:
                    sentences = text.split('。')
                    for sentence in sentences:
                        if "兄弟" in sentence or any(word in sentence for word in ["長兄", "実兄", "義兄", "実弟"]):
                            print(f"🔍 Brother info: {sentence}。")
        
        driver.close()
        
        # Now use LLM to generate answer
        print(f"\n3. Setting up LLM for answer generation...")
        
        llm = ChatBedrock(
            client=bedrock_runtime,
            model_id=inference_profile_arn,
            provider="anthropic",
            region_name=region,
            model_kwargs={"temperature": 0.0, "max_tokens": 1000}
        )
        
        # Create context
        full_context = "\n\n".join(context_texts)
        
        prompt = f"""以下の文脈情報に基づいて、質問に正確に答えてください。

文脈情報:
{full_context}

質問: {question}

文脈情報から、ラオウの兄弟関係について具体的に答えてください。"""

        print(f"4. Generating answer with LLM...")
        print("⏳ Processing...")
        
        response = llm.invoke(prompt)
        
        print(f"\n" + "🎯 FINAL ANSWER:")
        print("=" * 60)
        print(response.content)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Direct Raoh Brothers Query")
    print("=" * 60)
    
    success = direct_raoh_query()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Query completed successfully!")
    else:
        print("❌ Query failed!")
    print("=" * 60)