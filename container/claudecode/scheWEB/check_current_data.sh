#!/bin/bash

echo "📊 現在のデータベース状況確認"

# ログイン
TOKEN=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  http://localhost:8080/api/login | jq -r '.access_token')

echo "👥 現在のユーザー数:"
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/admin/users | jq '.users | length'

echo "📋 現在のユーザーリスト:"
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/admin/users | jq '.users[] | {username, start_time, end_time}'