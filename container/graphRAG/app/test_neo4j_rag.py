"""
Simple test script to connect to neo4jRAG container and test query.
Uses existing dependencies in the environment.
"""

import sys
import os

# Add current directory to path
sys.path.append('/root/aws.git/container/graphRAG/app')

try:
    # Try to import existing modules
    from langchain_community.vectorstores import Neo4jVector
    from langchain_aws import BedrockEmbeddings, BedrockLLM
    from langchain.chains import RetrievalQA
    from langchain.prompts import PromptTemplate
    
    def test_neo4j_rag_query(question="ラオウの兄弟は"):
        """Test RAG query with neo4jRAG container."""
        print(f"Testing Neo4j RAG with question: {question}")
        print("=" * 50)
        
        try:
            # Neo4j RAG configuration (port 7587)
            NEO4J_URI_RAG = "bolt://localhost:7587"
            NEO4J_USER_RAG = "neo4j" 
            NEO4J_PASS_RAG = "password"
            
            print("1. Initializing embedding model...")
            embedding = BedrockEmbeddings(
                model_id="amazon.titan-embed-text-v2:0",
                region_name="us-east-1"
            )
            
            print("2. Connecting to Neo4j vector store...")
            vectorstore = Neo4jVector(
                embedding=embedding,
                url=NEO4J_URI_RAG,
                username=NEO4J_USER_RAG,
                password=NEO4J_PASS_RAG,
                index_name="graphrag_index",
                node_label="GraphRAGChunk",
                text_node_property="text"
            )
            
            print("3. Initializing LLM...")
            llm = BedrockLLM(
                model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
                region_name="us-east-1",
                model_kwargs={
                    "max_tokens": 3000,
                    "temperature": 0.1
                }
            )
            
            print("4. Setting up QA chain...")
            prompt_template = """
            以下の文脈情報を使用して質問に答えてください。
            文脈に基づいて正確で詳細な回答を提供してください。
            文脈に答えがない場合は、「提供された情報では答えられません」と回答してください。

            文脈: {context}

            質問: {question}

            回答:
            """
            
            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
                chain_type_kwargs={"prompt": prompt},
                return_source_documents=True
            )
            
            print(f"5. Executing query: {question}")
            result = qa_chain.invoke({"query": question})
            
            print("\n" + "="*50)
            print("RESULT:")
            print("="*50)
            print(f"Answer: {result.get('result', '')}")
            
            source_documents = result.get('source_documents', [])
            print(f"\nSource documents found: {len(source_documents)}")
            
            for i, doc in enumerate(source_documents, 1):
                print(f"\n--- Source {i} ---")
                print(f"Content: {doc.page_content[:200]}...")
                print(f"Metadata: {doc.metadata}")
            
            return True
            
        except Exception as e:
            print(f"Error during RAG query: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    if __name__ == "__main__":
        question = sys.argv[1] if len(sys.argv) > 1 else "ラオウの兄弟は"
        test_neo4j_rag_query(question)
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Required libraries are not available in the current environment.")
    
    # Try basic Neo4j connection test
    print("\nTrying basic connection test...")
    try:
        import socket
        
        def test_neo4j_connection():
            """Test basic network connection to Neo4j RAG."""
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex(('localhost', 7587))
                sock.close()
                
                if result == 0:
                    print("✓ Neo4j RAG container is reachable on port 7587")
                    return True
                else:
                    print("✗ Cannot connect to Neo4j RAG container on port 7587")
                    return False
            except Exception as e:
                print(f"Connection test failed: {e}")
                return False
        
        test_neo4j_connection()
        
    except Exception as e:
        print(f"Even basic connection test failed: {e}")