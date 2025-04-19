#!/bin/bash

# コマンドライン引数から環境変数を設定
export LANGFUSE_SECRET_KEY="$1"
export LANGFUSE_PUBLIC_KEY="$2"
export LANGFUSE_HOST="$3"

echo "環境変数を設定しました。"
echo "LANGFUSE_SECRET_KEY=${LANGFUSE_SECRET_KEY}"
echo "LANGFUSE_PUBLIC_KEY=${LANGFUSE_PUBLIC_KEY}"
echo "LANGFUSE_HOST=${LANGFUSE_HOST}"