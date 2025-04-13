import uuid

import streamlit as st
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.chat_models.bedrock import BedrockChat
from langchain_community.embeddings.bedrock import BedrockEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory


st.title("Bedrock Claude Haiku チャット")

if "retriever" not in st.session_state:
    embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0")
    db = FAISS.load_local(
        "faiss_index", embeddings, allow_dangerous_deserialization=True
    )
    retriever = db.as_retriever()
    st.session_state["retriever"] = retriever
retriever = st.session_state["retriever"]

if "llm" not in st.session_state:
    st.session_state["llm"] = BedrockChat(
            model_id="anthropic.claude-3-5-haiku-20241022-v1:0"
    )
llm = st.session_state["llm"]

if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())[:8]
session_id = st.session_state["session_id"]

if "history" not in st.session_state:
    st.session_state["history"] = ChatMessageHistory()
history = st.session_state["history"]


def get_session_history(session_id: str):
    return history


def create_chain():

    ### Contextualize question ###
    contextualize_q_system_prompt = """Given a chat history and the latest user question     which might reference context in the chat history, formulate a standalone question     which can be understood without the chat history. Do NOT answer the question,     just reformulate it if needed and otherwise return it as is."""
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    ### Answer question ###
    qa_system_prompt = """You are an assistant for question-answering tasks.     Use the following pieces of retrieved context to answer the question.     If you don't know the answer, just say that you don't know.     Use three sentences maximum and keep the answer concise.
    {context}"""
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    return conversational_rag_chain


if "chain" not in st.session_state:
    st.session_state["chain"] = create_chain()

chain = st.session_state["chain"]

for h in history:
    for message in h[1]:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.write(message.content)
        if isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.write(message.content)


if prompt := st.chat_input("質問を入力"):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = chain.stream(
            {"input": prompt},
            config={
                "configurable": {"session_id": session_id},
            },
        )

        def s():
            for chunk in stream:
                if "answer" in chunk:
                    yield chunk["answer"]

        st.write_stream(s)


