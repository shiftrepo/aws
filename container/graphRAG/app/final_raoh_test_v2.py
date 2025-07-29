"""
Final test for Raoh brothers query using updated langchain-neo4j.
"""

import boto3
from langchain_neo4j import Neo4jVector
from langchain_aws import BedrockEmbeddings, ChatBedrock
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Neo4j RAG connection
NEO4J_URI_RAG = "bolt://neo4jRAG:7687"
NEO4J_USER_RAG = "neo4j"
NEO4J_PASS_RAG = "password"

# AWS configuration
region = "us-east-1"
bedrock_runtime = boto3.client("bedrock-runtime", region_name=region)
inference_profile_arn = "arn:aws:bedrock:us-east-1:711387140677:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0"

def test_raoh_brothers_query():
    """Test the specific question about Raoh's brothers."""
    question = "ラオウの兄弟は誰ですか？"
    
    print(f"🔍 Neo4j RAG Query Test")
    print(f"Question: {question}")
    print("=" * 60)
    
    try:
        print("1. Setting up embedding model...")
        embedding = BedrockEmbeddings(
            client=bedrock_runtime,
            model_id="amazon.titan-embed-text-v2:0",
            region_name=region
        )

        print("2. Setting up ChatBedrock LLM...")
        llm = ChatBedrock(
            client=bedrock_runtime,
            model_id=inference_profile_arn,
            provider="anthropic",
            region_name=region,
            model_kwargs={"temperature": 0.0, "max_tokens": 1500}
        )

        print("3. Connecting to Neo4j vector store...")
        vectorstore = Neo4jVector.from_existing_index(
            embedding=embedding,
            url=NEO4J_URI_RAG,
            username=NEO4J_USER_RAG,
            password=NEO4J_PASS_RAG,
            index_name="entity",
            node_label="Chunk",
            text_node_property="text",
            embedding_node_property="embedding"
        )

        print("4. Testing similarity search...")
        test_results = vectorstore.similarity_search("ラオウ 兄弟", k=2)
        print(f"   ✓ Found {len(test_results)} similar documents")

        print("5. Setting up retriever...")
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

        print("6. Creating optimized prompt template...")
        prompt_template = PromptTemplate.from_template(
            """以下の文脈情報を使用して質問に正確に答えてください。

文脈情報:
{context}

質問: {question}

回答: """
        )

        print("7. Building QA chain...")
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt_template}
        )

        print(f"8. Executing query...")
        print("⏳ Processing...")
        
        response = qa_chain.invoke({"query": question})

        print("\n" + "🎯 RESULT:")
        print("=" * 60)
        
        answer = response.get("result", "")
        print(f"📝 Answer:\n{answer}")
        
        source_docs = response.get("source_documents", [])
        print(f"\n📚 Source Documents ({len(source_docs)}):")
        print("-" * 40)
        
        for i, doc in enumerate(source_docs, 1):
            content = doc.page_content
            print(f"\n【Source {i}】")
            # Show key parts that mention brothers
            if "兄弟" in content or "兄" in content or "弟" in content:
                # Find the sentence with brother information
                sentences = content.split('。')
                for sentence in sentences:
                    if any(word in sentence for word in ["兄弟", "長兄", "実兄", "義兄", "実弟"]):
                        print(f"🔍 Key info: {sentence}。")
                        
            # Show first part of content
            print(f"📄 Content: {content[:200]}...")
            
            if hasattr(doc, 'metadata') and doc.metadata:
                print(f"📊 Metadata: {doc.metadata}")
            print("-" * 40)
            
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Raoh Brothers Query Test")
    print("=" * 60)
    
    success = test_raoh_brothers_query()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed!")
    print("=" * 60)