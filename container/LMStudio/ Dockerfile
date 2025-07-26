# ベースイメージとして軽量なDebian 12 Slimを選択
FROM debian:12-slim

# セキュリティアップデートを含めてパッケージを最新化
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    wget \
    libfuse2 \
    vim \
    ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# アプリケーションを格納するディレクトリを作成
WORKDIR /app

# LM Studioの公式AppImageをダウンロードして実行権限を付与
# 注意: このURLは将来変更される可能性があります
RUN wget "https://releases.lmstudio.ai/linux/latest/LM-Studio-0.2.29-x86_64.AppImage" -O lmstudio.AppImage && \
    chmod +x lmstudio.AppImage

# コンテナ起動時にLM Studioのサーバーを起動
# 0.0.0.0で待ち受けることで、コンテナ外部からのアクセスを許可
CMD ["/app/lmstudio.AppImage", "lms", "server", "start", "--host", "0.0.0.0", "--port", "1234"]

# サーバーが使用するポートを公開
EXPOSE 1234