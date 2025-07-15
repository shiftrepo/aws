FROM ubuntu:22.04 as builder

# 環境変数の設定
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Tokyo

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg2 \
    apt-transport-https \
    ca-certificates \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Mattermostのバージョンと環境設定
ENV MATTERMOST_VERSION=9.5.1
ENV MATTERMOST_HOME=/opt/mattermost
WORKDIR /opt

# Mattermostのダウンロードと展開
RUN wget -q https://releases.mattermost.com/${MATTERMOST_VERSION}/mattermost-${MATTERMOST_VERSION}-linux-amd64.tar.gz \
    && tar -xzf mattermost-${MATTERMOST_VERSION}-linux-amd64.tar.gz \
    && rm mattermost-${MATTERMOST_VERSION}-linux-amd64.tar.gz \
    && mkdir -p ${MATTERMOST_HOME}/data \
    && mkdir -p ${MATTERMOST_HOME}/plugins \
    && mkdir -p ${MATTERMOST_HOME}/client/plugins \
    && mkdir -p ${MATTERMOST_HOME}/config

# メインイメージ
FROM ubuntu:22.04

# 環境変数の設定
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Tokyo
ENV MATTERMOST_HOME=/opt/mattermost
ENV PATH=${MATTERMOST_HOME}/bin:${PATH}
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    postgresql-client \
    jq \
    git \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Mattermostのファイルをビルダーステージからコピー
COPY --from=builder /opt/mattermost /opt/mattermost

# ユーザー作成と権限設定
RUN adduser --disabled-password --gecos "" mattermost \
    && chown -R mattermost:mattermost ${MATTERMOST_HOME} \
    && chmod -R 755 ${MATTERMOST_HOME}

# 設定ファイルの準備
WORKDIR ${MATTERMOST_HOME}
RUN mkdir -p ${MATTERMOST_HOME}/config-init
COPY config.json ${MATTERMOST_HOME}/config-init/

# root権限の起動スクリプトを作成
COPY root-entrypoint.sh /root-entrypoint.sh
RUN chmod +x /root-entrypoint.sh

# コンテナ起動時の設定
EXPOSE 8065
VOLUME ["${MATTERMOST_HOME}/data", "${MATTERMOST_HOME}/logs", "${MATTERMOST_HOME}/config"]

# Mattermostサーバーの起動
ENTRYPOINT ["/root-entrypoint.sh"]