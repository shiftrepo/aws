#!/bin/bash

# .envファイルが存在するか確認
if [ ! -f .env ]; then
  echo "エラー: .envファイルが見つかりません。.env.exampleをコピーして必要な値を設定してください。"
  echo "cp .env.example .env"
  exit 1
fi

# コンテナ起動
docker-compose up -d