# Docling Container for Document Processing
FROM python:3.11-slim

# 作業ディレクトリの設定
WORKDIR /app

# システムの依存関係をインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-jpn \
    libreoffice \
    pandoc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Pythonの依存関係をインストール
RUN pip install --no-cache-dir \
    docling \
    docling-core \
    docling-ibm-models \
    fastapi \
    uvicorn \
    python-multipart \
    onnxruntime

# 共有ディレクトリを作成
RUN mkdir -p /shared/input /shared/output /shared/config

# 処理スクリプトをコピー
COPY process_documents.py /app/

# 環境変数の設定
ENV PYTHONPATH=/app
ENV DOCLING_CACHE_DIR=/shared/cache

# デフォルトのエントリーポイント（コンテナを常に実行状態に保つ）
CMD ["tail", "-f", "/dev/null"]