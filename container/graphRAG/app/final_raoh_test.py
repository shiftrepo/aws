"""
Final test for Raoh brothers query using correct Chunk configuration.
"""

import boto3
from langchain_community.vectorstores import Neo4jVector
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
    question = "ラオウの兄弟は"
    
    print(f"=== Neo4j RAG Query Test ===")
    print(f"Question: {question}")
    print("=" * 50)
    
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
            model_kwargs={"temperature": 0.1, "max_tokens": 2000}
        )

        print("3. Connecting to Neo4j vector store...")
        # Use the correct configuration based on our inspection
        vectorstore = Neo4jVector(
            embedding=embedding,
            url=NEO4J_URI_RAG,
            username=NEO4J_USER_RAG,
            password=NEO4J_PASS_RAG,
            index_name="entity",  # This index exists and is online
            node_label="Chunk",   # Chunk nodes contain the text data
            text_node_property="text"  # text property contains the content
        )

        print("4. Testing similarity search first...")
        test_results = vectorstore.similarity_search("ラオウ 兄弟", k=3)
        print(f"   Found {len(test_results)} similar documents")
        for i, doc in enumerate(test_results, 1):
            print(f"   {i}. {doc.page_content[:100]}...")

        print("5. Setting up retriever...")
        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

        print("6. Creating prompt template...")
        prompt_template = PromptTemplate.from_template(
            """以下の情報に基づいて質問に答えてください。
            可能な限り詳細で正確な情報を提供してください。

            参考情報:
            {context}

            質問: {question}
            
            回答:"""
        )

        print("7. Building QA chain...")
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt_template}
        )

        print(f"8. Executing query: {question}")
        print("-" * 50)
        
        response = qa_chain.invoke({"query": question})

        print("\n" + "="*60)
        print("📝 ANSWER:")
        print("="*60)
        
        answer = response.get("result", "No result found")
        print(answer)
        
        source_docs = response.get("source_documents", [])
        print(f"\n📚 Source Documents ({len(source_docs)}):")
        print("="*60)
        
        if source_docs:
            for i, doc in enumerate(source_docs, 1):
                print(f"\n【Source {i}】")
                content = doc.page_content
                # Show first 500 characters
                if len(content) > 500:
                    print(f"{content[:500]}...")
                else:
                    print(content)
                    
                if hasattr(doc, 'metadata') and doc.metadata:
                    print(f"Metadata: {doc.metadata}")
                print("-" * 40)
        else:
            print("No source documents found.")
            
        return True

    except Exception as e:
        print(f"❌ Error during query execution: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_raoh_brothers_query()
    
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")
        
    print("\n" + "="*60)
    print("Test finished.")
    print("="*60)