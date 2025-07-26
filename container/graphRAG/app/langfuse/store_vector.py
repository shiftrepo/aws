from langchain_community.embeddings.bedrock import BedrockEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import HTMLHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_core.documents import Document

headers_to_split_on = [
    ("h1", "Header 1"),
    ("h2", "Header 2"),
]

url = (
    "https://www.apple.com/newsroom/2023/09/apple-debuts-iphone-15-and-iphone-15-plus/"
)

html_splitter = HTMLHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
docs_with_headers = html_splitter.split_text_from_url(url)

# ヘッダー情報を除いたテキスト部分をさらに分割
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # チャンクの最大文字数
    chunk_overlap=100, # チャンク間の重複文字数
    separators=["\n\n", "\n", " ", ""],
)
docs = []
for doc in docs_with_headers:
    chunks = text_splitter.split_text(doc.page_content)
    for chunk in chunks:
        docs.append(Document(page_content=chunk, metadata=doc.metadata))

embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0")
db = FAISS.from_documents(docs, embeddings)

db.save_local("faiss_index")
