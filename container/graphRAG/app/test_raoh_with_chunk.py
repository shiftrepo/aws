"""
Test RAG query using existing Chunk nodes and entity vector index.
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

def test_raoh_query_with_chunk(question="ラオウの兄弟は"):
    """Test RAG query using Chunk nodes."""
    print(f"Testing RAG query: {question}")
    print("=" * 50)
    
    try:
        print("1. Setting up embedding model...")
        embedding = BedrockEmbeddings(
            client=bedrock_runtime,
            model_id="amazon.titan-embed-text-v2:0",
            region_name=region
        )

        print("2. Setting up LLM...")
        llm = ChatBedrock(
            client=bedrock_runtime,
            model_id=inference_profile_arn,
            provider="anthropic",
            region_name=region,
            model_kwargs={"temperature": 0.1, "max_tokens": 2000}
        )

        print("3. Connecting to Neo4j with Chunk label...")
        # Try different configurations
        configs_to_try = [
            {
                "index_name": "entity",
                "node_label": "Chunk", 
                "text_property": "text"
            },
            {
                "index_name": "entity",
                "node_label": "__Entity__",
                "text_property": "id"
            },
            {
                "index_name": "entity", 
                "node_label": "__Node__",
                "text_property": "text"
            }
        ]
        
        vectorstore = None
        for config in configs_to_try:
            try:
                print(f"  Trying config: {config}")
                vectorstore = Neo4jVector(
                    embedding=embedding,
                    url=NEO4J_URI_RAG,
                    username=NEO4J_USER_RAG,
                    password=NEO4J_PASS_RAG,
                    index_name=config["index_name"],
                    node_label=config["node_label"],
                    text_node_property=config["text_property"]
                )
                
                # Test similarity search
                test_results = vectorstore.similarity_search("test", k=1)
                print(f"  ✓ Success with {config}")
                break
                
            except Exception as e:
                print(f"  ✗ Failed with {config}: {e}")
                continue
        
        if not vectorstore:
            print("Could not establish vector store connection with any configuration")
            return False

        print("4. Setting up retriever...")
        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

        print("5. Creating prompt template...")
        prompt_template = PromptTemplate.from_template(
            """以下の情報に基づいて質問に答えてください。
            情報に含まれていない場合は、「提供された情報では答えられません」と回答してください。

            {context}

            質問: {question}
            回答:"""
        )

        print("6. Building QA chain...")
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt_template}
        )

        print(f"7. Executing query: {question}")
        response = qa_chain.invoke({"query": question})

        print("\n" + "="*60)
        print("RESULT:")
        print("="*60)
        
        answer = response.get("result", "No result found")
        print(f"Answer:\n{answer}")
        
        source_docs = response.get("source_documents", [])
        print(f"\nNumber of source documents: {len(source_docs)}")
        
        if source_docs:
            print("\nSource Documents:")
            print("-" * 40)
            for i, doc in enumerate(source_docs, 1):
                print(f"\nSource {i}:")
                print(f"Content: {doc.page_content}")
                if hasattr(doc, 'metadata') and doc.metadata:
                    print(f"Metadata: {doc.metadata}")
        else:
            print("\nNo source documents found.")
            
        return True

    except Exception as e:
        print(f"Error during query execution: {e}")
        import traceback
        traceback.print_exc()
        return False

def simple_similarity_search(question="ラオウ"):
    """Simple similarity search test."""
    print(f"\nTesting simple similarity search: {question}")
    print("-" * 30)
    
    try:
        embedding = BedrockEmbeddings(
            client=bedrock_runtime,
            model_id="amazon.titan-embed-text-v2:0",
            region_name=region
        )
        
        vectorstore = Neo4jVector(
            embedding=embedding,
            url=NEO4J_URI_RAG,
            username=NEO4J_USER_RAG,
            password=NEO4J_PASS_RAG,
            index_name="entity",
            node_label="Chunk",
            text_node_property="text"
        )
        
        results = vectorstore.similarity_search(question, k=5)
        print(f"Found {len(results)} similar documents:")
        
        for i, doc in enumerate(results, 1):
            print(f"\n{i}. {doc.page_content[:200]}...")
            if hasattr(doc, 'metadata'):
                print(f"   Metadata: {doc.metadata}")
                
        return True
        
    except Exception as e:
        print(f"Similarity search failed: {e}")
        return False

if __name__ == "__main__":
    import sys
    question = sys.argv[1] if len(sys.argv) > 1 else "ラオウの兄弟は"
    
    print("Neo4j RAG Query Test with Chunk nodes")
    print("=" * 50)
    
    # First try similarity search
    if simple_similarity_search(question):
        # Then try full RAG query
        test_raoh_query_with_chunk(question)