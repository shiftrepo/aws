# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Docker Environment Setup
```bash
# Start all services (Neo4j databases, PostgreSQL, Python container)
docker-compose up -d

# Access the Python container for development
docker exec -it python-aws bash

# Stop all services
docker-compose down
```

### Dependencies Installation
```bash
# Install basic requirements
pip install -r app/requierment.txt

# Install Langfuse-specific requirements
pip install -r app/langfuse/requirements.txt

# Install Streamlit requirements
pip install -r app/langfuse/streamlit_requirements.txt
```

### Running Applications
```bash
# Run Streamlit chat interface with Langfuse integration
cd app/langfuse
streamlit run streamlit_chat_pdtlan.py --server.port 8501

# Run GraphRAG query with command line arguments
cd app/4pdtlan
python query_graphRAGsonet35v2.py "your question here"

# Process PDF documents for GraphRAG
cd app
python pdf_arg_bigdoc_graphRAG.py --input path/to/document.pdf
```

### Environment Configuration
```bash
# Set Langfuse environment variables
cd app/langfuse
./env.bash "your_secret_key" "your_public_key" "your_host_url"

# Required AWS environment variables:
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_DEFAULT_REGION="us-east-1"
```

## Architecture Overview

### Core Components

**Graph Database Layer**
- Two Neo4j instances: `neo4j` (port 7474/7687) for source data, `neo4jRAG` (port 7575/7587) for RAG-processed data
- PostgreSQL database for structured data storage
- Graph migration utilities in `neo4j2GraphRAG.py`

**Document Processing Pipeline**
- PDF document ingestion via `pdf_arg_bigdoc_graphRAG.py`
- Wikipedia content loading through LlamaIndex readers
- Text chunking and embedding generation using AWS Bedrock Titan embeddings
- Property graph construction and storage in Neo4j

**RAG Query System**
- `graph2graphRAG.py`: Core RAG functionality using LangChain and Neo4j vector store
- `query_graphRAGsonet35v2.py`: Command-line interface for GraphRAG queries
- Integration with AWS Bedrock Claude 3.5 Sonnet via inference profiles

**Web Interface**
- Streamlit-based chat interface in `app/langfuse/streamlit_chat_pdtlan.py`
- Langfuse integration for conversation tracking and analytics
- Session management and proxy support

### Key Libraries and Frameworks
- **LlamaIndex**: Document processing, graph construction, and RAG implementation
- **LangChain**: RAG chains, document loaders, and vector stores
- **Neo4j**: Graph database for knowledge representation
- **AWS Bedrock**: LLM inference (Claude 3.5 Sonnet) and embeddings (Titan)
- **Streamlit**: Web interface for chat functionality
- **Langfuse**: Conversation tracking and observability

### Data Flow
1. Documents are processed through PDF loaders or Wikipedia readers
2. Content is chunked and embedded using Bedrock Titan embeddings
3. Knowledge graphs are constructed and stored in Neo4j
4. RAG queries retrieve relevant graph nodes and generate responses using Claude 3.5 Sonnet
5. Conversations are tracked through Langfuse for analytics

### Development Structure
- `app/4pdtlan/`: Core GraphRAG implementation and query interfaces
- `app/langfuse/`: Streamlit UI and conversation tracking
- `app/prototype/`: Experimental and development versions
- `doc/`: Sample documents for testing