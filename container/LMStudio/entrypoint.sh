#!/bin/bash
set -e

LMS_CLI="/root/.cache/lm-studio/bin/lms"
LM_STUDIO_APP="/app/squashfs-root/lm-studio"

# 専用CLIツールが存在しない場合（初回起動時）のみ、GUIアプリを一度実行してツールを抽出させる
if [ ! -f "$LMS_CLI" ]; then
  echo "LM Studio CLI not found. Performing one-time extraction..."
  # --version のような、すぐに終了するコマンドを実行して抽出だけを促す
  xvfb-run $LM_STUDIO_APP --no-sandbox --disable-gpu --version > /dev/null 2>&1 || true
fi

# 抽出された専用CLIツールを使ってサーバーを起動する
echo "Starting LM Studio server using the dedicated CLI..."
$LMS_CLI server start --host 0.0.0.0 --port 1234
