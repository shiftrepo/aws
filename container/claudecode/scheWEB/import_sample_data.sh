#!/bin/bash

echo "📥 サンプルデータのインポート開始"

# ログイン
TOKEN=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  http://localhost:8080/api/login | jq -r '.access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
    echo "❌ ログイン失敗"
    exit 1
fi

echo "✅ adminでログイン成功"

# サンプルデータをインポート
echo "📋 サンプルデータをインポート中..."
import_result=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @sample_data.json \
  http://localhost:8080/api/admin/import)

echo "📊 インポート結果:"
echo "$import_result" | jq '.'

# インポート後のユーザー確認
echo
echo "👥 インポート後のユーザーリスト:"
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/admin/users | jq '.users[] | {username, start_time, end_time}'

echo
echo "📈 インポート統計:"
user_count=$(curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/admin/users | jq '.users | length')
echo "ユーザー数: $user_count人"

echo "✅ サンプルデータインポート完了"