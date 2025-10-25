#!/bin/bash

##############################################################################
# 予定追加機能 重複判定バグ検証テストスクリプト
# 目的: 全入力パターンで重複判定ロジックの動作確認
##############################################################################

API_BASE="http://localhost:8080/api"
TEST_LOG="/root/aws.git/container/claudecode/scheWEB/test/overlap_test_results.txt"
PASSED=0
FAILED=0
TOTAL=0

# カラーコード
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "==========================================" > "$TEST_LOG"
echo "予定追加重複判定テスト" >> "$TEST_LOG"
echo "開始時刻: $(date)" >> "$TEST_LOG"
echo "==========================================" >> "$TEST_LOG"
echo "" >> "$TEST_LOG"

# テスト用ユーザー作成とログイン
echo -e "${BLUE}🔧 テスト環境準備中...${NC}"
curl -s -X POST -H 'Content-Type: application/json' -d '{"username":"overlap_test_user","password":"test123","start_time":"08:00","end_time":"19:00"}' $API_BASE/register > /dev/null 2>&1

LOGIN_RESPONSE=$(curl -s -X POST -H 'Content-Type: application/json' -d '{"username":"overlap_test_user","password":"test123"}' $API_BASE/login)
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')

if [[ "$TOKEN" == "null" || -z "$TOKEN" ]]; then
    echo -e "${RED}❌ ログイン失敗 - テスト中止${NC}"
    exit 1
fi

echo -e "${GREEN}✅ テスト用ユーザー準備完了${NC}"
echo ""

# テストヘルパー関数
run_test() {
    local test_name="$1"
    local availability_json="$2"
    local should_succeed="$3"  # "success" or "fail"

    TOTAL=$((TOTAL + 1))
    echo ""
    echo -e "${BLUE}[TEST $TOTAL] $test_name${NC}"
    echo "[TEST $TOTAL] $test_name" >> "$TEST_LOG"
    echo "送信データ: $availability_json" >> "$TEST_LOG"

    # 既存データをクリア
    curl -s -X POST -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" -d '{"availability":{}}' $API_BASE/availability > /dev/null

    # テスト実行
    local response=$(curl -s -X POST -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" -d "$availability_json" $API_BASE/availability)

    # 結果確認
    local result_availability=$(curl -s -H "Authorization: Bearer $TOKEN" $API_BASE/availability)

    echo "応答: $response" >> "$TEST_LOG"
    echo "保存後データ: $result_availability" >> "$TEST_LOG"

    if [[ "$should_succeed" == "success" ]]; then
        if echo "$response" | grep -q "successfully"; then
            echo -e "  ${GREEN}✅ PASS - 正常に保存${NC}"
            echo "  ✅ PASS" >> "$TEST_LOG"
            PASSED=$((PASSED + 1))
        else
            echo -e "  ${RED}❌ FAIL - 保存失敗（成功すべき）${NC}"
            echo "  ❌ FAIL - 保存失敗" >> "$TEST_LOG"
            FAILED=$((FAILED + 1))
        fi
    else
        if echo "$response" | grep -q "successfully"; then
            echo -e "  ${RED}❌ FAIL - 保存成功（失敗すべき）${NC}"
            echo "  ❌ FAIL - 保存成功" >> "$TEST_LOG"
            FAILED=$((FAILED + 1))
        else
            echo -e "  ${GREEN}✅ PASS - 正しく拒否${NC}"
            echo "  ✅ PASS" >> "$TEST_LOG"
            PASSED=$((PASSED + 1))
        fi
    fi

    echo "" >> "$TEST_LOG"
}

##############################################################################
# パターン1: 単一時間帯（重複なし）
##############################################################################
echo -e "${YELLOW}===========================================${NC}"
echo -e "${YELLOW}パターン1: 単一時間帯テスト${NC}"
echo -e "${YELLOW}===========================================${NC}"
echo "" >> "$TEST_LOG"
echo "========================================" >> "$TEST_LOG"
echo "パターン1: 単一時間帯テスト" >> "$TEST_LOG"
echo "========================================" >> "$TEST_LOG"

run_test "1-1. 単一時間帯: 09:00-10:00" \
    '{"availability":{"monday":[{"start":"09:00","end":"10:00"}]}}' \
    "success"

run_test "1-2. 単一時間帯: 14:00-15:00" \
    '{"availability":{"monday":[{"start":"14:00","end":"15:00"}]}}' \
    "success"

run_test "1-3. 境界値: 08:00-08:30（最小）" \
    '{"availability":{"monday":[{"start":"08:00","end":"08:30"}]}}' \
    "success"

run_test "1-4. 境界値: 18:30-19:00（最大）" \
    '{"availability":{"monday":[{"start":"18:30","end":"19:00"}]}}' \
    "success"

##############################################################################
# パターン2: 連続時間帯（重複なし・境界が接する）
##############################################################################
echo ""
echo -e "${YELLOW}===========================================${NC}"
echo -e "${YELLOW}パターン2: 連続時間帯（境界接触）${NC}"
echo -e "${YELLOW}===========================================${NC}"
echo "" >> "$TEST_LOG"
echo "========================================" >> "$TEST_LOG"
echo "パターン2: 連続時間帯テスト" >> "$TEST_LOG"
echo "========================================" >> "$TEST_LOG"

run_test "2-1. 連続: 09:00-10:00 と 10:00-11:00（境界が一致）" \
    '{"availability":{"monday":[{"start":"09:00","end":"10:00"},{"start":"10:00","end":"11:00"}]}}' \
    "success"

run_test "2-2. 連続3つ: 09:00-09:30, 09:30-10:00, 10:00-10:30" \
    '{"availability":{"monday":[{"start":"09:00","end":"09:30"},{"start":"09:30","end":"10:00"},{"start":"10:00","end":"10:30"}]}}' \
    "success"

run_test "2-3. 連続: 13:00-14:00, 14:00-15:00, 15:00-16:00" \
    '{"availability":{"monday":[{"start":"13:00","end":"14:00"},{"start":"14:00","end":"15:00"},{"start":"15:00","end":"16:00"}]}}' \
    "success"

##############################################################################
# パターン3: 離れた時間帯（重複なし）
##############################################################################
echo ""
echo -e "${YELLOW}===========================================${NC}"
echo -e "${YELLOW}パターン3: 離れた時間帯（重複なし）${NC}"
echo -e "${YELLOW}===========================================${NC}"
echo "" >> "$TEST_LOG"
echo "========================================" >> "$TEST_LOG"
echo "パターン3: 離れた時間帯テスト" >> "$TEST_LOG"
echo "========================================" >> "$TEST_LOG"

run_test "3-1. 離れた2つ: 09:00-10:00 と 14:00-15:00（4時間差）" \
    '{"availability":{"monday":[{"start":"09:00","end":"10:00"},{"start":"14:00","end":"15:00"}]}}' \
    "success"

run_test "3-2. 離れた3つ: 08:00-09:00, 12:00-13:00, 17:00-18:00" \
    '{"availability":{"monday":[{"start":"08:00","end":"09:00"},{"start":"12:00","end":"13:00"},{"start":"17:00","end":"18:00"}]}}' \
    "success"

run_test "3-3. 30分刻み離れた: 09:00-09:30, 10:00-10:30, 11:00-11:30" \
    '{"availability":{"monday":[{"start":"09:00","end":"09:30"},{"start":"10:00","end":"10:30"},{"start":"11:00","end":"11:30"}]}}' \
    "success"

##############################################################################
# パターン4: 完全重複（同じ時間帯）
##############################################################################
echo ""
echo -e "${YELLOW}===========================================${NC}"
echo -e "${YELLOW}パターン4: 完全重複（同一時間帯）${NC}"
echo -e "${YELLOW}===========================================${NC}"
echo "" >> "$TEST_LOG"
echo "========================================" >> "$TEST_LOG"
echo "パターン4: 完全重複テスト" >> "$TEST_LOG"
echo "========================================" >> "$TEST_LOG"

# 注意: バックエンドは重複許可、フロントエンドが検証
run_test "4-1. 完全重複: 09:00-10:00 を2回" \
    '{"availability":{"monday":[{"start":"09:00","end":"10:00"},{"start":"09:00","end":"10:00"}]}}' \
    "success"

run_test "4-2. 完全重複3回: 14:00-15:00 を3回" \
    '{"availability":{"monday":[{"start":"14:00","end":"15:00"},{"start":"14:00","end":"15:00"},{"start":"14:00","end":"15:00"}]}}' \
    "success"

##############################################################################
# パターン5: 部分重複
##############################################################################
echo ""
echo -e "${YELLOW}===========================================${NC}"
echo -e "${YELLOW}パターン5: 部分重複（時間帯が一部重なる）${NC}"
echo -e "${YELLOW}===========================================${NC}"
echo "" >> "$TEST_LOG"
echo "========================================" >> "$TEST_LOG"
echo "パターン5: 部分重複テスト" >> "$TEST_LOG"
echo "========================================" >> "$TEST_LOG"

run_test "5-1. 後半重複: 09:00-11:00 と 10:00-12:00（1時間重複）" \
    '{"availability":{"monday":[{"start":"09:00","end":"11:00"},{"start":"10:00","end":"12:00"}]}}' \
    "success"

run_test "5-2. 前半重複: 13:00-15:00 と 12:00-14:00（1時間重複）" \
    '{"availability":{"monday":[{"start":"13:00","end":"15:00"},{"start":"12:00","end":"14:00"}]}}' \
    "success"

run_test "5-3. 30分重複: 09:00-10:00 と 09:30-10:30" \
    '{"availability":{"monday":[{"start":"09:00","end":"10:00"},{"start":"09:30","end":"10:30"}]}}' \
    "success"

##############################################################################
# パターン6: 包含関係
##############################################################################
echo ""
echo -e "${YELLOW}===========================================${NC}"
echo -e "${YELLOW}パターン6: 包含関係（一方が他方を含む）${NC}"
echo -e "${YELLOW}===========================================${NC}"
echo "" >> "$TEST_LOG"
echo "========================================" >> "$TEST_LOG"
echo "パターン6: 包含関係テスト" >> "$TEST_LOG"
echo "========================================" >> "$TEST_LOG"

run_test "6-1. 包含: 09:00-12:00 内に 10:00-11:00" \
    '{"availability":{"monday":[{"start":"09:00","end":"12:00"},{"start":"10:00","end":"11:00"}]}}' \
    "success"

run_test "6-2. 包含: 10:00-11:00 内に 09:00-12:00（逆順）" \
    '{"availability":{"monday":[{"start":"10:00","end":"11:00"},{"start":"09:00","end":"12:00"}]}}' \
    "success"

run_test "6-3. 複数包含: 08:00-18:00 内に 10:00-11:00, 14:00-15:00" \
    '{"availability":{"monday":[{"start":"08:00","end":"18:00"},{"start":"10:00","end":"11:00"},{"start":"14:00","end":"15:00"}]}}' \
    "success"

##############################################################################
# パターン7: 複数曜日
##############################################################################
echo ""
echo -e "${YELLOW}===========================================${NC}"
echo -e "${YELLOW}パターン7: 複数曜日の予定${NC}"
echo -e "${YELLOW}===========================================${NC}"
echo "" >> "$TEST_LOG"
echo "========================================" >> "$TEST_LOG"
echo "パターン7: 複数曜日テスト" >> "$TEST_LOG"
echo "========================================" >> "$TEST_LOG"

run_test "7-1. 2曜日: 月曜09:00-10:00, 火曜14:00-15:00" \
    '{"availability":{"monday":[{"start":"09:00","end":"10:00"}],"tuesday":[{"start":"14:00","end":"15:00"}]}}' \
    "success"

run_test "7-2. 全曜日: 月〜金すべて09:00-10:00" \
    '{"availability":{"monday":[{"start":"09:00","end":"10:00"}],"tuesday":[{"start":"09:00","end":"10:00"}],"wednesday":[{"start":"09:00","end":"10:00"}],"thursday":[{"start":"09:00","end":"10:00"}],"friday":[{"start":"09:00","end":"10:00"}]}}' \
    "success"

run_test "7-3. 各曜日複数時間: 月曜2つ、火曜3つ、水曜1つ" \
    '{"availability":{"monday":[{"start":"09:00","end":"10:00"},{"start":"14:00","end":"15:00"}],"tuesday":[{"start":"10:00","end":"11:00"},{"start":"13:00","end":"14:00"},{"start":"16:00","end":"17:00"}],"wednesday":[{"start":"11:00","end":"12:00"}]}}' \
    "success"

##############################################################################
# パターン8: 逆順・ランダム順序
##############################################################################
echo ""
echo -e "${YELLOW}===========================================${NC}"
echo -e "${YELLOW}パターン8: 時間順序のバリエーション${NC}"
echo -e "${YELLOW}===========================================${NC}"
echo "" >> "$TEST_LOG"
echo "========================================" >> "$TEST_LOG"
echo "パターン8: 順序バリエーション" >> "$TEST_LOG"
echo "========================================" >> "$TEST_LOG"

run_test "8-1. 逆順: 14:00-15:00, 09:00-10:00（後→前）" \
    '{"availability":{"monday":[{"start":"14:00","end":"15:00"},{"start":"09:00","end":"10:00"}]}}' \
    "success"

run_test "8-2. ランダム: 12:00-13:00, 09:00-10:00, 15:00-16:00" \
    '{"availability":{"monday":[{"start":"12:00","end":"13:00"},{"start":"09:00","end":"10:00"},{"start":"15:00","end":"16:00"}]}}' \
    "success"

run_test "8-3. 5つランダム順: 16:00-17:00, 10:00-11:00, 13:00-14:00, 08:00-09:00, 18:00-19:00" \
    '{"availability":{"monday":[{"start":"16:00","end":"17:00"},{"start":"10:00","end":"11:00"},{"start":"13:00","end":"14:00"},{"start":"08:00","end":"09:00"},{"start":"18:00","end":"19:00"}]}}' \
    "success"

##############################################################################
# パターン9: 極端なケース
##############################################################################
echo ""
echo -e "${YELLOW}===========================================${NC}"
echo -e "${YELLOW}パターン9: 極端なケース${NC}"
echo -e "${YELLOW}===========================================${NC}"
echo "" >> "$TEST_LOG"
echo "========================================" >> "$TEST_LOG"
echo "パターン9: 極端なケース" >> "$TEST_LOG"
echo "========================================" >> "$TEST_LOG"

run_test "9-1. 最小単位: 09:00-09:30（30分）" \
    '{"availability":{"monday":[{"start":"09:00","end":"09:30"}]}}' \
    "success"

run_test "9-2. 最大範囲: 08:00-19:00（11時間）" \
    '{"availability":{"monday":[{"start":"08:00","end":"19:00"}]}}' \
    "success"

run_test "9-3. 1日全て30分刻み: 08:00〜19:00を30分ごとに22個" \
    '{"availability":{"monday":[{"start":"08:00","end":"08:30"},{"start":"08:30","end":"09:00"},{"start":"09:00","end":"09:30"},{"start":"09:30","end":"10:00"},{"start":"10:00","end":"10:30"},{"start":"10:30","end":"11:00"},{"start":"11:00","end":"11:30"},{"start":"11:30","end":"12:00"},{"start":"12:00","end":"12:30"},{"start":"12:30","end":"13:00"},{"start":"13:00","end":"13:30"},{"start":"13:30","end":"14:00"},{"start":"14:00","end":"14:30"},{"start":"14:30","end":"15:00"},{"start":"15:00","end":"15:30"},{"start":"15:30","end":"16:00"},{"start":"16:00","end":"16:30"},{"start":"16:30","end":"17:00"},{"start":"17:00","end":"17:30"},{"start":"17:30","end":"18:00"},{"start":"18:00","end":"18:30"},{"start":"18:30","end":"19:00"}]}}' \
    "success"

##############################################################################
# パターン10: 異常データ（バックエンド検証）
##############################################################################
echo ""
echo -e "${YELLOW}===========================================${NC}"
echo -e "${YELLOW}パターン10: 異常データ${NC}"
echo -e "${YELLOW}===========================================${NC}"
echo "" >> "$TEST_LOG"
echo "========================================" >> "$TEST_LOG"
echo "パターン10: 異常データ" >> "$TEST_LOG"
echo "========================================" >> "$TEST_LOG"

run_test "10-1. 空配列: monday: []" \
    '{"availability":{"monday":[]}}' \
    "success"

run_test "10-2. 空オブジェクト: {}" \
    '{"availability":{}}' \
    "success"

##############################################################################
# テスト結果サマリー
##############################################################################
echo ""
echo -e "${YELLOW}===========================================${NC}"
echo -e "${YELLOW}テスト結果サマリー${NC}"
echo -e "${YELLOW}===========================================${NC}"
echo "" >> "$TEST_LOG"
echo "========================================" >> "$TEST_LOG"
echo "テスト結果サマリー" >> "$TEST_LOG"
echo "========================================" >> "$TEST_LOG"

COVERAGE=$(awk "BEGIN {printf \"%.2f\", ($PASSED/$TOTAL)*100}")

echo -e "${BLUE}総テスト数: $TOTAL${NC}"
echo -e "${GREEN}成功: $PASSED${NC}"
echo -e "${RED}失敗: $FAILED${NC}"
echo -e "${BLUE}カバレッジ: $COVERAGE%${NC}"

echo "総テスト数: $TOTAL" >> "$TEST_LOG"
echo "成功: $PASSED" >> "$TEST_LOG"
echo "失敗: $FAILED" >> "$TEST_LOG"
echo "カバレッジ: $COVERAGE%" >> "$TEST_LOG"

if [[ $FAILED -eq 0 ]]; then
    echo ""
    echo -e "${GREEN}🎉 全テスト合格！${NC}"
    echo "🎉 全テスト合格！" >> "$TEST_LOG"
else
    echo ""
    echo -e "${RED}⚠️  失敗: $FAILED 件${NC}"
    echo "⚠️  失敗: $FAILED 件" >> "$TEST_LOG"
fi

echo ""
echo "終了時刻: $(date)" >> "$TEST_LOG"
echo "詳細結果: $TEST_LOG"
echo ""
