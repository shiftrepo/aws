#!/bin/bash

echo "🧪 Admin データ管理API テスト開始"

# ログインしてトークン取得
echo "📋 Admin ログイン中..."
TOKEN=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  http://localhost:8080/api/login | jq -r '.access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
    echo "❌ ログイン失敗"
    exit 1
fi

echo "✅ ログイン成功 (token: ${TOKEN:0:20}...)"

# エクスポートテスト
echo
echo "📤 データエクスポートテスト..."
export_result=$(curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/admin/export)

if echo "$export_result" | jq -e '.export_info.version' >/dev/null 2>&1; then
    echo "✅ エクスポート成功"
    echo "📊 バージョン: $(echo "$export_result" | jq -r '.export_info.version')"
    echo "📊 ユーザー数: $(echo "$export_result" | jq -r '.statistics.total_users')"
    echo "📊 予定数: $(echo "$export_result" | jq -r '.statistics.total_availability_records')"
else
    echo "❌ エクスポート失敗"
    echo "$export_result" | jq '.'
fi

# インポートテスト用のサンプルデータ作成
echo
echo "📥 インポートテスト用データ作成..."
sample_data='{
  "export_info": {
    "timestamp": "'$(date -Iseconds)'",
    "version": "v2.1.24",
    "exported_by": "test"
  },
  "users": [
    {
      "id": 999,
      "username": "testuser",
      "password": "testpass123",
      "start_time": "09:00",
      "end_time": "17:00",
      "created_at": "'$(date -Iseconds)'"
    }
  ],
  "availability": [
    {
      "id": 999,
      "user_id": 999,
      "username": "testuser",
      "day_of_week": "monday",
      "start_time": "10:00",
      "end_time": "12:00",
      "created_at": "'$(date -Iseconds)'"
    }
  ],
  "statistics": {
    "total_users": 1,
    "total_availability_records": 1
  }
}'

# インポートテスト
echo "📥 データインポートテスト..."
import_result=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$sample_data" \
  http://localhost:8080/api/admin/import)

if echo "$import_result" | jq -e '.imported_users' >/dev/null 2>&1; then
    echo "✅ インポート成功"
    echo "📊 インポートユーザー: $(echo "$import_result" | jq -r '.imported_users')"
    echo "📊 インポート予定: $(echo "$import_result" | jq -r '.imported_availability')"

    # インポートしたユーザーの確認
    echo "👤 インポートしたユーザーの確認..."
    users_result=$(curl -s -H "Authorization: Bearer $TOKEN" \
      http://localhost:8080/api/admin/users)
    if echo "$users_result" | jq -e '.users[] | select(.username == "testuser")' >/dev/null 2>&1; then
        echo "✅ testuser が正常にインポートされました"
    else
        echo "❌ testuser が見つかりません"
    fi
else
    echo "❌ インポート失敗"
    echo "$import_result" | jq '.'
fi

echo
echo "🎉 テスト完了"