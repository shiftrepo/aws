"""
Simple Neo4j RAG connector for existing container.
Connects to neo4jRAG container on port 7587 and provides basic query functionality.
"""

import time
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from neo4j import GraphDatabase, Driver
from langchain_community.vectorstores import Neo4jVector
from langchain_aws import BedrockEmbeddings, BedrockLLM
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document

from ..config.neo4j_rag_config import neo4j_rag_config


logger = logging.getLogger(__name__)


@dataclass
class RAGQueryResult:
    """Result from RAG query."""
    answer: str
    sources: List[Dict[str, Any]]
    processing_time: float
    error: Optional[str] = None


class Neo4jRAGConnector:
    """Simple connector for Neo4j RAG operations."""
    
    def __init__(self):
        self.config = neo4j_rag_config
        self._driver = None
        self._vector_store = None
        self._llm = None
        self._qa_chain = None
        
    def connect(self) -> bool:
        """Connect to Neo4j RAG database."""
        try:
            self._driver = GraphDatabase.driver(
                self.config.uri,
                auth=(self.config.user, self.config.password)
            )
            
            # Test connection
            with self._driver.session() as session:
                result = session.run("RETURN 1 as test")
                result.single()
            
            logger.info(f"Connected to Neo4j RAG at {self.config.uri}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j RAG: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Neo4j RAG database."""
        if self._driver:
            self._driver.close()
            self._driver = None
            logger.info("Disconnected from Neo4j RAG")
    
    def get_vector_store(self):
        """Get or create vector store instance."""
        if self._vector_store is None:
            # Initialize embedding model
            embeddings = BedrockEmbeddings(
                model_id="amazon.titan-embed-text-v2:0",
                region_name="us-east-1"
            )
            
            # Create vector store
            self._vector_store = Neo4jVector(
                embedding=embeddings,
                url=self.config.uri,
                username=self.config.user,
                password=self.config.password,
                index_name="graphrag_index",
                node_label="GraphRAGChunk",
                text_node_property="text"
            )
        
        return self._vector_store
    
    def get_llm(self):
        """Get or create LLM instance."""
        if self._llm is None:
            self._llm = BedrockLLM(
                model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
                region_name="us-east-1",
                model_kwargs={
                    "max_tokens": 3000,
                    "temperature": 0.1
                }
            )
        return self._llm
    
    def get_qa_chain(self):
        """Get or create QA chain."""
        if self._qa_chain is None:
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
            
            self._qa_chain = RetrievalQA.from_chain_type(
                llm=self.get_llm(),
                chain_type="stuff",
                retriever=self.get_vector_store().as_retriever(search_kwargs={"k": 4}),
                chain_type_kwargs={"prompt": prompt},
                return_source_documents=True
            )
        
        return self._qa_chain
    
    def query(self, question: str) -> RAGQueryResult:
        """Execute RAG query."""
        start_time = time.time()
        
        try:
            if not self.connect():
                return RAGQueryResult(
                    answer="データベースに接続できませんでした。",
                    sources=[],
                    processing_time=time.time() - start_time,
                    error="Connection failed"
                )
            
            # Execute query
            qa_chain = self.get_qa_chain()
            result = qa_chain.invoke({"query": question})
            
            # Extract answer and sources
            answer = result.get("result", "")
            source_documents = result.get("source_documents", [])
            
            # Format sources
            sources = []
            for doc in source_documents:
                sources.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })
            
            processing_time = time.time() - start_time
            
            return RAGQueryResult(
                answer=answer,
                sources=sources,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"RAG query failed: {e}")
            
            return RAGQueryResult(
                answer=f"エラーが発生しました: {str(e)}",
                sources=[],
                processing_time=processing_time,
                error=str(e)
            )
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Perform similarity search."""
        try:
            vector_store = self.get_vector_store()
            return vector_store.similarity_search(query, k=k)
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            if not self.connect():
                return {"error": "Cannot connect to database"}
            
            with self._driver.session() as session:
                # Count nodes
                node_result = session.run("MATCH (n) RETURN count(n) as count")
                node_count = node_result.single()["count"]
                
                # Count relationships
                rel_result = session.run("MATCH ()-[r]-() RETURN count(r) as count")
                rel_count = rel_result.single()["count"]
                
                # Count GraphRAG chunks
                chunk_result = session.run("MATCH (n:GraphRAGChunk) RETURN count(n) as count")
                chunk_count = chunk_result.single()["count"]
                
                return {
                    "total_nodes": node_count,
                    "total_relationships": rel_count,
                    "graphrag_chunks": chunk_count,
                    "database_uri": self.config.uri
                }
                
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Check system health."""
        try:
            if not self.connect():
                return {
                    "status": "unhealthy",
                    "error": "Cannot connect to Neo4j RAG database"
                }
            
            # Test vector store
            vector_store = self.get_vector_store()
            vector_store.similarity_search("test", k=1)
            
            # Test LLM
            llm = self.get_llm()
            llm.invoke("Hello")
            
            return {
                "status": "healthy",
                "neo4j_connection": "ok",
                "vector_store": "ok",
                "llm": "ok",
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }


# Global instance for easy import
rag_connector = Neo4jRAGConnector()