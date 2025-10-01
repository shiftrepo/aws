"""
Example usage of Neo4j RAG connector.
Simple example showing how to connect to and query the neo4jRAG container.
"""

import sys
import logging
from services import rag_connector

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main example function."""
    print("Neo4j RAG Connector Example")
    print("=" * 30)
    
    # Health check
    print("\n1. Checking system health...")
    health = rag_connector.health_check()
    print(f"Health status: {health['status']}")
    if health['status'] == 'unhealthy':
        print(f"Error: {health['error']}")
        return
    
    # Database statistics
    print("\n2. Getting database statistics...")
    stats = rag_connector.get_stats()
    if 'error' in stats:
        print(f"Error getting stats: {stats['error']}")
    else:
        print(f"Total nodes: {stats['total_nodes']}")
        print(f"Total relationships: {stats['total_relationships']}")
        print(f"GraphRAG chunks: {stats['graphrag_chunks']}")
    
    # Query example
    if len(sys.argv) > 1:
        question = sys.argv[1]
    else:
        question = "機械学習とは何ですか？"
    
    print(f"\n3. Querying: {question}")
    result = rag_connector.query(question)
    
    print(f"\nAnswer: {result.answer}")
    print(f"Processing time: {result.processing_time:.2f}s")
    print(f"Sources found: {len(result.sources)}")
    
    # Show sources
    if result.sources:
        print("\nSources:")
        for i, source in enumerate(result.sources, 1):
            print(f"{i}. {source['content'][:100]}...")
            if source['metadata']:
                print(f"   Metadata: {source['metadata']}")
    
    # Similarity search example
    print(f"\n4. Similarity search for: {question}")
    documents = rag_connector.similarity_search(question, k=3)
    print(f"Found {len(documents)} similar documents")
    
    for i, doc in enumerate(documents, 1):
        print(f"{i}. {doc.page_content[:100]}...")
    
    # Cleanup
    rag_connector.disconnect()
    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()