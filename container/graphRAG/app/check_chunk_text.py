"""
Check Chunk nodes for empty or missing text properties.
"""

from neo4j import GraphDatabase

# Neo4j RAG connection
NEO4J_URI_RAG = "bolt://neo4jRAG:7687"
NEO4J_USER_RAG = "neo4j"
NEO4J_PASS_RAG = "password"

def check_chunk_text_properties():
    """Check text properties in Chunk nodes."""
    try:
        driver = GraphDatabase.driver(
            NEO4J_URI_RAG,
            auth=(NEO4J_USER_RAG, NEO4J_PASS_RAG)
        )
        
        with driver.session() as session:
            print("Checking Chunk node text properties")
            print("=" * 40)
            
            # Count total chunks
            result = session.run("MATCH (n:Chunk) RETURN count(n) as total")
            total = result.single()["total"]
            print(f"Total Chunk nodes: {total}")
            
            # Count chunks with text property
            result = session.run("MATCH (n:Chunk) WHERE n.text IS NOT NULL RETURN count(n) as with_text")
            with_text = result.single()["with_text"]
            print(f"Chunks with text property: {with_text}")
            
            # Count chunks with non-empty text
            result = session.run("MATCH (n:Chunk) WHERE n.text IS NOT NULL AND n.text <> '' RETURN count(n) as non_empty")
            non_empty = result.single()["non_empty"]
            print(f"Chunks with non-empty text: {non_empty}")
            
            # Find empty or missing text chunks
            result = session.run("MATCH (n:Chunk) WHERE n.text IS NULL OR n.text = '' RETURN n LIMIT 3")
            empty_chunks = list(result)
            print(f"Chunks with empty/missing text: {len(empty_chunks)}")
            
            for i, record in enumerate(empty_chunks, 1):
                node = record["n"]
                props = dict(node)
                print(f"\nEmpty chunk {i}:")
                for key, value in props.items():
                    if key != 'embedding':  # Skip large embedding array
                        print(f"  {key}: {value}")
            
            # Check chunks with actual text content
            print(f"\nSample chunks with text content:")
            result = session.run("MATCH (n:Chunk) WHERE n.text IS NOT NULL AND n.text <> '' RETURN n.text as text LIMIT 3")
            for i, record in enumerate(result, 1):
                text = record["text"]
                print(f"\nText sample {i}: {text[:200]}...")
            
            # Try to find a working configuration by checking different approaches
            print(f"\nTrying to find working vector configuration...")
            
            # Option 1: Use only chunks with non-empty text
            result = session.run("""
                MATCH (n:Chunk) 
                WHERE n.text IS NOT NULL AND n.text <> '' AND n.text CONTAINS 'ラオウ'
                RETURN n.text as text, n.id as id
                LIMIT 2
            """)
            
            raoh_chunks = list(result)
            print(f"Found {len(raoh_chunks)} chunks containing 'ラオウ':")
            for i, record in enumerate(raoh_chunks, 1):
                text = record["text"]
                chunk_id = record["id"]
                print(f"\nRaoh chunk {i} (ID: {chunk_id}):")
                print(f"Content: {text[:300]}...")
        
        driver.close()
        
    except Exception as e:
        print(f"Error checking chunks: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_chunk_text_properties()