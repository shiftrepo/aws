"""
Check Neo4j RAG database status and available data.
"""

import sys
from neo4j import GraphDatabase

# Neo4j RAG connection
NEO4J_URI_RAG = "bolt://neo4jRAG:7687"
NEO4J_USER_RAG = "neo4j"
NEO4J_PASS_RAG = "password"

def check_database_status():
    """Check Neo4j RAG database status."""
    try:
        driver = GraphDatabase.driver(
            NEO4J_URI_RAG,
            auth=(NEO4J_USER_RAG, NEO4J_PASS_RAG)
        )
        
        with driver.session() as session:
            print("Neo4j RAG Database Status Check")
            print("=" * 40)
            
            # Check connection
            result = session.run("RETURN 'Connected successfully' as status")
            status = result.single()["status"]
            print(f"Connection: {status}")
            
            # Count total nodes
            result = session.run("MATCH (n) RETURN count(n) as total_nodes")
            total_nodes = result.single()["total_nodes"]
            print(f"Total nodes: {total_nodes}")
            
            # Check node labels
            result = session.run("CALL db.labels()")
            labels = [record["label"] for record in result]
            print(f"Available labels: {labels}")
            
            # Check for GraphRAGChunk nodes
            result = session.run("MATCH (n:GraphRAGChunk) RETURN count(n) as chunk_count")
            chunk_count = result.single()["chunk_count"]
            print(f"GraphRAGChunk nodes: {chunk_count}")
            
            # Check indexes
            result = session.run("SHOW INDEXES")
            indexes = []
            for record in result:
                indexes.append({
                    "name": record.get("name"),
                    "type": record.get("type"),
                    "state": record.get("state"),
                    "labels": record.get("labelsOrTypes")
                })
            
            print(f"\nAvailable indexes ({len(indexes)}):")
            for idx in indexes:
                print(f"  - {idx['name']}: {idx['type']} ({idx['state']})")
            
            # Check for vector indexes specifically
            result = session.run("CALL db.indexes() YIELD name, type WHERE type CONTAINS 'VECTOR'")
            vector_indexes = [record["name"] for record in result]
            print(f"Vector indexes: {vector_indexes}")
            
            # Sample some data if GraphRAGChunk exists
            if chunk_count > 0:
                print(f"\nSample GraphRAGChunk data:")
                result = session.run("MATCH (n:GraphRAGChunk) RETURN n LIMIT 3")
                for i, record in enumerate(result, 1):
                    node = record["n"]
                    print(f"  Sample {i}: {dict(node)}")
            
            # Check relationships
            result = session.run("MATCH ()-[r]-() RETURN count(r) as total_relationships")
            total_rels = result.single()["total_relationships"]
            print(f"\nTotal relationships: {total_rels}")
            
        driver.close()
        return True
        
    except Exception as e:
        print(f"Error checking database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_database_status()