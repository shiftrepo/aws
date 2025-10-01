"""
Test script to query about Raoh's brothers using existing Neo4j RAG setup.
Based on the existing graph2graphRAG.py structure.
"""

import sys
import os

# Add paths
sys.path.append('/root/aws.git/container/graphRAG/app')

try:
    import boto3
    from langchain_community.vectorstores import Neo4jVector
    from langchain_aws import BedrockEmbeddings, ChatBedrock
    from langchain.chains import RetrievalQA
    from langchain.prompts import PromptTemplate
    print("All required libraries imported successfully!")

    # Neo4j RAG connection info (based on container network)
    NEO4J_URI_RAG = "bolt://neo4jRAG:7687"  # Container network address
    NEO4J_USER_RAG = "neo4j"
    NEO4J_PASS_RAG = "password"

    # AWS configuration
    region = "us-east-1"
    bedrock_runtime = boto3.client("bedrock-runtime", region_name=region)

    # Inference profile ARN
    inference_profile_arn = "arn:aws:bedrock:us-east-1:711387140677:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0"

    def test_raoh_query(question="ラオウの兄弟は"):
        """Test RAG query about Raoh's brothers."""
        print(f"Testing query: {question}")
        print("=" * 50)
        
        try:
            print("1. Initializing embedding model...")
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
                model_kwargs={"temperature": 0.5, "max_tokens": 1024}
            )

            print("3. Connecting to Neo4j vector store...")
            vectorstore = Neo4jVector(
                embedding=embedding,
                url=NEO4J_URI_RAG,
                username=NEO4J_USER_RAG,
                password=NEO4J_PASS_RAG,
                index_name="graphrag_index",
                node_label="GraphRAGChunk",
                text_node_property="text"
            )

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
                    print(f"Content: {doc.page_content[:300]}...")
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

    def test_connection():
        """Test basic connectivity to Neo4j RAG."""
        try:
            print("Testing basic Neo4j connectivity...")
            
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
                index_name="graphrag_index",
                node_label="GraphRAGChunk",
                text_node_property="text"
            )
            
            # Test similarity search
            results = vectorstore.similarity_search("test", k=1)
            print(f"Connection successful! Found {len(results)} documents in similarity search.")
            return True
            
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False

    if __name__ == "__main__":
        print("Neo4j RAG Query Test")
        print("=" * 30)
        
        # Test connection first
        if test_connection():
            # Run the actual query
            question = sys.argv[1] if len(sys.argv) > 1 else "ラオウの兄弟は"
            test_raoh_query(question)
        else:
            print("Connection test failed. Cannot proceed with query.")

except ImportError as e:
    print(f"Import error: {e}")
    print("Required libraries not available.")
    
    # Test network connectivity at least
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        
        # Try connecting to neo4jRAG container
        result = sock.connect_ex(('neo4jRAG', 7687))
        if result == 0:
            print("✓ Network connection to neo4jRAG:7687 successful")
        else:
            print("✗ Cannot connect to neo4jRAG:7687")
            
        sock.close()
        
    except Exception as e:
        print(f"Network test failed: {e}")

except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()