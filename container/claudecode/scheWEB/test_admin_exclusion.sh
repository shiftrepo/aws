#!/bin/bash

echo "🧪 admin除外修正後のLLM分析テスト"
echo "======================================="

# ログイン
TOKEN=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  http://localhost:8080/api/login | jq -r '.access_token')

echo "🤖 LLM分析実行中..."
llm_result=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/llm-analysis)

if echo "$llm_result" | jq -e '.success' >/dev/null 2>&1; then
    echo "✅ LLM分析成功"
    echo
    echo "📊 基本統計:"
    echo "・総候補数: $(echo "$llm_result" | jq '.total_candidates')"
    echo "・分析対象ユーザー数: $(echo "$llm_result" | jq '.total_users')"
    echo
    echo "🏆 TOP候補詳細:"

    # TOP候補を詳細表示
    for i in {0..3}; do
        candidate=$(echo "$llm_result" | jq ".top_candidates[$i]")
        if [ "$candidate" != "null" ]; then
            day=$(echo "$candidate" | jq -r '.day')
            start=$(echo "$candidate" | jq -r '.start')
            end=$(echo "$candidate" | jq -r '.end')
            duration=$(echo "$candidate" | jq -r '.duration')
            count=$(echo "$candidate" | jq -r '.participant_count')
            total=$(echo "$candidate" | jq -r '.total_users')
            percentage=$(echo "$candidate" | jq -r '.availability_percentage')
            users=$(echo "$candidate" | jq -r '.available_users | join(", ")')

            day_jp=$(echo "$day" | sed 's/monday/月曜日/;s/tuesday/火曜日/;s/wednesday/水曜日/;s/thursday/木曜日/;s/friday/金曜日/')

            echo
            echo "【第$((i+1))位】 $day_jp $start-$end ($duration分)"
            echo "✅ 参加可能: $users ($count人/$total人 - $percentage%)"

            # adminが含まれているかチェック
            if echo "$users" | grep -q "admin"; then
                echo "❌ ERROR: adminが含まれています！"
            else
                echo "✅ OK: adminは除外されています"
            fi
        fi
    done
else
    echo "❌ LLM分析失敗"
    echo "$llm_result" | jq '.error'
fi

echo
echo "📅 グリッドスケジュールも確認..."
grid_result=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/grid-schedule)
total_grid_users=$(echo "$grid_result" | jq '.total_users')
echo "グリッド対象ユーザー数: $total_grid_users人"

if [ "$total_grid_users" -eq 6 ]; then
    echo "✅ OK: グリッドでもadmin除外済み（6人 = adminを除くユーザー数）"
else
    echo "❌ WARNING: グリッドにadminが含まれている可能性"
fi

echo
echo "🎉 admin除外テスト完了"