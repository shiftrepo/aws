"""
Simple Neo4j RAG configuration for existing container.
Connects to the running neo4jRAG container on port 7587.
"""

import os
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Neo4jRAGConfig:
    """Configuration for Neo4j RAG container connection."""
    uri: str = "bolt://localhost:7587"
    user: str = "neo4j" 
    password: str = "password"
    database: str = "neo4j"
    
    @classmethod
    def from_env(cls) -> 'Neo4jRAGConfig':
        """Create config from environment variables."""
        return cls(
            uri=os.environ.get("NEO4J_RAG_URI", "bolt://localhost:7587"),
            user=os.environ.get("NEO4J_RAG_USER", "neo4j"),
            password=os.environ.get("NEO4J_RAG_PASSWORD", "password"),
            database=os.environ.get("NEO4J_RAG_DATABASE", "neo4j")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excluding password)."""
        return {
            "uri": self.uri,
            "user": self.user,
            "database": self.database
        }


# Default instance for easy import
neo4j_rag_config = Neo4jRAGConfig.from_env()