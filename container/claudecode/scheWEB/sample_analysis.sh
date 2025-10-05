#!/bin/bash

echo "📊 サンプルデータ詳細分析レポート"
echo "=========================================="

# ログイン
TOKEN=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  http://localhost:8080/api/login | jq -r '.access_token')

echo
echo "👥 ユーザー詳細情報:"
echo "--------------------"
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/admin/users | jq -r '.users[] |
  "🏢 \(.username) | 勤務時間: \(.start_time)-\(.end_time)"'

echo
echo "📅 各曜日の会議候補数:"
echo "----------------------"
grid_result=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/grid-schedule)

for day in monday tuesday wednesday thursday friday; do
    count=$(echo "$grid_result" | jq ".grid_schedule.$day | length // 0")
    day_jp=$(echo "$day" | sed 's/monday/月曜日/;s/tuesday/火曜日/;s/wednesday/水曜日/;s/thursday/木曜日/;s/friday/金曜日/')
    echo "$day_jp: ${count}個の時間帯"
done

echo
echo "🤖 LLM分析による TOP 5 推奨時間:"
echo "----------------------------------"
llm_result=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/llm-analysis)
echo "$llm_result" | jq -r '.top_candidates[0:5][] |
  "🏆 \(.day | sub("monday";"月曜") | sub("tuesday";"火曜") | sub("wednesday";"水曜") | sub("thursday";"木曜") | sub("friday";"金曜")) \(.start)-\(.end) | \(.participant_count)/\(.total_users)人参加 (\(.availability_percentage)%)"'

echo
echo "📈 会議参加率分析:"
echo "------------------"
echo "🎯 最高参加率: $(echo "$llm_result" | jq -r '.statistics.max_participation_rate')%"
echo "📊 平均参加率: $(echo "$llm_result" | jq -r '.statistics.avg_participation_rate | . * 100 | floor / 100')%"
echo "📋 総候補数: $(echo "$llm_result" | jq '.total_candidates')"

echo
echo "💾 データ管理統計:"
echo "------------------"
export_result=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/admin/export)
echo "👤 総ユーザー数: $(echo "$export_result" | jq '.statistics.total_users')人"
echo "📅 総予定数: $(echo "$export_result" | jq '.statistics.total_availability_records')件"
echo "📊 平均予定数/人: $(echo "scale=1; $(echo "$export_result" | jq '.statistics.total_availability_records') / $(echo "$export_result" | jq '.statistics.total_users')" | bc)"

echo
echo "=========================================="
echo "🎉 サンプルデータ分析完了"
echo
echo "🌐 Web UI確認方法:"
echo "http://localhost:8080/ でadmin/admin123 でログインして確認してください"