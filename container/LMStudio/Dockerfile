# Dockerfile (True Final Version)

FROM debian:12-slim

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    wget libfuse2 ca-certificates libglib2.0-0 libnspr4 libnss3 \
    libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libgbm1 libgtk-3-0 \
    libasound2 libxss1 libxtst6 libxshmfence1 xvfb xauth net-tools curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN wget "https://installers.lmstudio.ai/linux/x64/0.3.20-4/LM-Studio-0.3.20-4-x64.AppImage" -O lmstudio.AppImage && \
    chmod +x lmstudio.AppImage

RUN ./lmstudio.AppImage --appimage-extract

# 起動スクリプトをコンテナにコピーして実行権限を付与
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# 起動スクリプトを実行する
ENTRYPOINT ["/app/entrypoint.sh"]

EXPOSE 1234
