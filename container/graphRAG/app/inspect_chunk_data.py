"""
Inspect the actual structure of Chunk nodes in Neo4j RAG database.
"""

from neo4j import GraphDatabase

# Neo4j RAG connection
NEO4J_URI_RAG = "bolt://neo4jRAG:7687"
NEO4J_USER_RAG = "neo4j"
NEO4J_PASS_RAG = "password"

def inspect_chunk_data():
    """Inspect Chunk node structure."""
    try:
        driver = GraphDatabase.driver(
            NEO4J_URI_RAG,
            auth=(NEO4J_USER_RAG, NEO4J_PASS_RAG)
        )
        
        with driver.session() as session:
            print("Inspecting Chunk Node Structure")
            print("=" * 40)
            
            # Get sample Chunk nodes
            result = session.run("MATCH (n:Chunk) RETURN n LIMIT 5")
            chunks = list(result)
            
            print(f"Found {len(chunks)} Chunk samples:")
            for i, record in enumerate(chunks, 1):
                node = record["n"]
                properties = dict(node)
                print(f"\nChunk {i}:")
                for key, value in properties.items():
                    value_str = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                    print(f"  {key}: {value_str}")
            
            # Check all property names in Chunk nodes
            print(f"\nAll property names in Chunk nodes:")
            result = session.run("MATCH (n:Chunk) UNWIND keys(n) as key RETURN DISTINCT key")
            keys = [record["key"] for record in result]
            print(f"Properties: {keys}")
            
            # Check for text-like properties
            text_properties = [k for k in keys if 'text' in k.lower() or 'content' in k.lower() or 'description' in k.lower()]
            print(f"Text-like properties: {text_properties}")
            
            # Check entity nodes too
            print(f"\nInspecting entity nodes:")
            result = session.run("MATCH (n:entity) RETURN n LIMIT 3")
            entities = list(result)
            
            print(f"Found {len(entities)} entity samples:")
            for i, record in enumerate(entities, 1):
                node = record["n"]
                properties = dict(node)
                print(f"\nEntity {i}:")
                for key, value in properties.items():
                    value_str = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                    print(f"  {key}: {value_str}")
            
            # Check entity property names
            print(f"\nAll property names in entity nodes:")
            result = session.run("MATCH (n:entity) UNWIND keys(n) as key RETURN DISTINCT key")
            entity_keys = [record["key"] for record in result]
            print(f"Properties: {entity_keys}")
            
            # Search for any nodes with "ラオウ" in any property
            print(f"\nSearching for nodes containing 'ラオウ':")
            result = session.run("""
                MATCH (n) 
                WHERE any(prop in keys(n) WHERE toString(n[prop]) CONTAINS 'ラオウ')
                RETURN n, labels(n) as labels
                LIMIT 5
            """)
            
            raoh_nodes = list(result)
            print(f"Found {len(raoh_nodes)} nodes containing 'ラオウ':")
            for i, record in enumerate(raoh_nodes, 1):
                node = record["n"]
                labels = record["labels"]
                properties = dict(node)
                print(f"\nNode {i} (labels: {labels}):")
                for key, value in properties.items():
                    if 'ラオウ' in str(value):
                        value_str = str(value)[:200] + "..." if len(str(value)) > 200 else str(value)
                        print(f"  {key}: {value_str}")
            
        driver.close()
        
    except Exception as e:
        print(f"Error inspecting data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_chunk_data()