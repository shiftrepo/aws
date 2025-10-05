#!/bin/bash

echo "🗑️ 削除機能テスト"

# ログイン
TOKEN=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  http://localhost:8080/api/login | jq -r '.access_token')

echo "📊 削除前のユーザー数確認..."
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/admin/users | jq '.users | length'

echo "🗑️ 全データ削除実行..."
curl -s -X DELETE -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/admin/delete-all | jq '.'

echo "📊 削除後のユーザー数確認..."
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/admin/users | jq '.users | length'

echo "✅ 削除テスト完了"