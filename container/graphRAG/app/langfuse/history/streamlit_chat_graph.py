import os
import uuid
import logging
import streamlit as st
import boto3
import tenacity

from llama_index.core import PropertyGraphIndex, ChatPromptTemplate, Settings
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.chat_engine import ContextChatEngine
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.llms.bedrock import Bedrock
from llama_index.embeddings.bedrock import BedrockEmbedding
from langfuse.callback import CallbackHandler

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🌐 Langfuse session init
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())[:8]
session_id = st.session_state["session_id"]
logger.info(f"Session ID: {session_id}")

# Langfuse handler
if "langfuse_handler" not in st.session_state:
    logger.info("Initializing Langfuse handler...")
    st.session_state["langfuse_handler"] = CallbackHandler(
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        host=os.getenv("LANGFUSE_HOST"),
        session_id=session_id,
    )
langfuse_handler = st.session_state["langfuse_handler"]

# Bedrock clients
logger.info("Creating boto3 session and bedrock client...")
boto3_session = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)
bedrock_client = boto3_session.client('bedrock-runtime')

# LLM
logger.info("Initializing Bedrock LLM...")
llm = Bedrock(
    model="anthropic.claude-3-haiku-20240307-v1:0",
    client=bedrock_client,
    callbacks=[langfuse_handler]
)

@tenacity.retry(stop=tenacity.stop_after_attempt(3),
                wait=tenacity.wait_fixed(5),
                retry=tenacity.retry_if_exception_type(Exception),
                before_sleep=tenacity.before_sleep_log(logging, logging.WARNING))
def create_embedding_with_retry(client, model_name, request_timeout):
    logger.info("Creating Bedrock embedding model with retry...")
    return BedrockEmbedding(
        model_name=model_name,
        client=client,
        use_async=False,
        request_timeout=request_timeout
    )

embedding = create_embedding_with_retry(
    bedrock_client,
    "amazon.titan-embed-text-v2:0",
    request_timeout=60
)

# Set global settings
logger.info("Setting global LLM and embedding settings...")
Settings.llm = llm
Settings.embed_model = embedding

# Neo4j store
logger.info("Initializing Neo4j property graph store...")
graph_store = Neo4jPropertyGraphStore(
    username="neo4j",
    password="password",
    url="bolt://neo4jRAG:7687",
)

# Index
logger.info("Loading existing PropertyGraphIndex...")
index = PropertyGraphIndex.from_existing(
    embed_model=embedding,
    property_graph_store=graph_store,
    show_progress=True,
)

# Retriever + Chat engine
if "chat_engine" not in st.session_state:
    logger.info("Creating chat engine with retriever and memory...")
    retriever = index.as_retriever(include_text=False)
    memory = ChatMemoryBuffer.from_defaults(token_limit=3000)

    chat_engine = ContextChatEngine.from_defaults(
        retriever=retriever,
        memory=memory,
        llm=llm
    )

    st.session_state["chat_engine"] = chat_engine

chat_engine = st.session_state["chat_engine"]

# Streamlit UI
st.title("Neo4j + Claude Sonnet チャット")

# Display chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

for role, content in st.session_state["chat_history"]:
    with st.chat_message(role):
        st.markdown(content)

# Input
if prompt := st.chat_input("質問を入力してください"):
    logger.info(f"User input received: {prompt}")
    st.session_state["chat_history"].append(("user", prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        logger.info("Generating response from chat engine...")
        response = chat_engine.chat(prompt)
        logger.info(f"Response generated: {response.response}")
        st.markdown(response.response)
        st.session_state["chat_history"].append(("assistant", response.response))

