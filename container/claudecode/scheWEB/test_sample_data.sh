#!/bin/bash

echo "🧪 サンプルデータ動作確認テスト"

# ログイン
TOKEN=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  http://localhost:8080/api/login | jq -r '.access_token')

echo "📊 基本統計情報:"
echo "👥 総ユーザー数: $(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/admin/users | jq '.users | length')"

echo
echo "📅 グリッドスケジュール確認:"
grid_result=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/grid-schedule)
echo "総ユーザー: $(echo "$grid_result" | jq '.total_users')"
echo "月曜日の会議候補: $(echo "$grid_result" | jq '.grid_schedule.monday | length // 0')"
echo "火曜日の会議候補: $(echo "$grid_result" | jq '.grid_schedule.tuesday | length // 0')"

echo
echo "🤖 LLM分析テスト:"
llm_result=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/llm-analysis)
if echo "$llm_result" | jq -e '.success' >/dev/null 2>&1; then
    echo "✅ LLM分析成功"
    echo "📊 会議候補数: $(echo "$llm_result" | jq '.total_candidates')"
    echo "👥 分析対象ユーザー: $(echo "$llm_result" | jq '.total_users')"
    echo "🥇 TOP候補: $(echo "$llm_result" | jq -r '.top_candidates[0].day + " " + .top_candidates[0].start + "-" + .top_candidates[0].end + " (" + (.top_candidates[0].participant_count | tostring) + "人)"')"
else
    echo "❌ LLM分析エラー"
    echo "$llm_result" | jq '.error'
fi

echo
echo "📤 エクスポート機能確認:"
export_result=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/admin/export)
if echo "$export_result" | jq -e '.export_info.version' >/dev/null 2>&1; then
    echo "✅ エクスポート成功"
    echo "📊 エクスポートユーザー: $(echo "$export_result" | jq '.statistics.total_users')"
    echo "📊 エクスポート予定: $(echo "$export_result" | jq '.statistics.total_availability_records')"
else
    echo "❌ エクスポートエラー"
fi

echo
echo "🎉 サンプルデータ動作確認完了"