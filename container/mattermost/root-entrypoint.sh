#!/bin/bash
set -e

# デバッグ情報の表示
echo "Debug: PATH=$PATH"
echo "Debug: MATTERMOST_HOME=$MATTERMOST_HOME"
ls -la /opt/mattermost/bin/

# 設定ファイルのパーミッション設定
rm -rf /opt/mattermost/config/*
mkdir -p /opt/mattermost/config
chown -R mattermost:mattermost /opt/mattermost
chmod -R 777 /opt/mattermost/config
chmod -R 777 /opt/mattermost/logs
chmod -R 777 /opt/mattermost/data
chmod -R 777 /opt/mattermost/client
chmod -R 777 /opt/mattermost/plugins

# 設定ファイルをコピー
cp /opt/mattermost/config-init/config.json /opt/mattermost/config/config.json

# 設定ファイルのパーミッション設定
chmod 666 /opt/mattermost/config/config.json
chown mattermost:mattermost /opt/mattermost/config/config.json

# PATHを明示的に設定
export PATH="/opt/mattermost/bin:$PATH"

# mattermostユーザーとしてサーバーを起動
exec su -c "export PATH=/opt/mattermost/bin:\$PATH && exec /opt/mattermost/bin/mattermost" mattermost