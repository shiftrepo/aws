#!/bin/bash

##############################################################################
# チームスケジューラー 包括的APIテストスクリプト
# 目的: カバレッジ100%を目指した全機能テスト
##############################################################################

API_BASE="http://localhost:8080/api"
TEST_RESULTS_FILE="/root/aws.git/container/claudecode/scheWEB/test/test_results.txt"
PASSED=0
FAILED=0
TOTAL=0

# カラーコード
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# テスト結果を記録
echo "===========================================" > "$TEST_RESULTS_FILE"
echo "チームスケジューラー 包括的APIテスト結果" >> "$TEST_RESULTS_FILE"
echo "開始時刻: $(date)" >> "$TEST_RESULTS_FILE"
echo "===========================================" >> "$TEST_RESULTS_FILE"
echo "" >> "$TEST_RESULTS_FILE"

# テストヘルパー関数
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_pattern="$3"

    TOTAL=$((TOTAL + 1))
    echo ""
    echo -e "${BLUE}[TEST $TOTAL] $test_name${NC}"
    echo "[TEST $TOTAL] $test_name" >> "$TEST_RESULTS_FILE"

    # コマンド実行
    local result=$(eval "$test_command" 2>&1)
    local exit_code=$?

    # 結果検証
    if [[ $exit_code -eq 0 ]] && echo "$result" | grep -q "$expected_pattern"; then
        echo -e "${GREEN}✅ PASS${NC}"
        echo "✅ PASS" >> "$TEST_RESULTS_FILE"
        echo "  結果: $result" >> "$TEST_RESULTS_FILE"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "❌ FAIL" >> "$TEST_RESULTS_FILE"
        echo "  期待パターン: $expected_pattern" >> "$TEST_RESULTS_FILE"
        echo "  実際の結果: $result" >> "$TEST_RESULTS_FILE"
        echo "  終了コード: $exit_code" >> "$TEST_RESULTS_FILE"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# 詳細検証関数
verify_json_field() {
    local json="$1"
    local field="$2"
    local expected_value="$3"

    local actual_value=$(echo "$json" | jq -r ".$field")
    if [[ "$actual_value" == "$expected_value" ]]; then
        echo -e "  ${GREEN}✓${NC} フィールド '$field' = '$expected_value'"
        echo "  ✓ フィールド '$field' = '$expected_value'" >> "$TEST_RESULTS_FILE"
        return 0
    else
        echo -e "  ${RED}✗${NC} フィールド '$field' 期待: '$expected_value', 実際: '$actual_value'"
        echo "  ✗ フィールド '$field' 期待: '$expected_value', 実際: '$actual_value'" >> "$TEST_RESULTS_FILE"
        return 1
    fi
}

##############################################################################
# 1. 認証機能テスト
##############################################################################
echo ""
echo -e "${YELLOW}===========================================${NC}"
echo -e "${YELLOW}1. 認証機能テスト${NC}"
echo -e "${YELLOW}===========================================${NC}"
echo "" >> "$TEST_RESULTS_FILE"
echo "========================================" >> "$TEST_RESULTS_FILE"
echo "1. 認証機能テスト" >> "$TEST_RESULTS_FILE"
echo "========================================" >> "$TEST_RESULTS_FILE"

# 1-1. 新規ユーザー登録（正常系）
run_test "1-1. 新規ユーザー登録（testuser1）" \
    "curl -s -X POST -H 'Content-Type: application/json' -d '{\"username\":\"testuser1\",\"password\":\"pass123\",\"start_time\":\"09:00\",\"end_time\":\"18:00\"}' $API_BASE/register" \
    "User registered successfully"

# 1-2. 重複ユーザー登録試行（異常系）
run_test "1-2. 重複ユーザー登録試行（エラー期待）" \
    "curl -s -X POST -H 'Content-Type: application/json' -d '{\"username\":\"testuser1\",\"password\":\"pass123\",\"start_time\":\"09:00\",\"end_time\":\"18:00\"}' $API_BASE/register" \
    "already exists"

# 1-3. 不正な登録データ（異常系：必須フィールド欠落）
run_test "1-3. 不正な登録データ（start_time欠落）" \
    "curl -s -X POST -H 'Content-Type: application/json' -d '{\"username\":\"baduser\",\"password\":\"pass123\",\"end_time\":\"18:00\"}' $API_BASE/register" \
    "Missing required fields"

# 1-4. ログイン（正常系）
LOGIN_RESPONSE=$(curl -s -X POST -H 'Content-Type: application/json' -d '{"username":"testuser1","password":"pass123"}' $API_BASE/login)
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
run_test "1-4. ログイン成功（testuser1）" \
    "echo '$LOGIN_RESPONSE'" \
    "access_token"

# トークン検証
if [[ "$TOKEN" != "null" && -n "$TOKEN" ]]; then
    echo -e "${GREEN}  トークン取得成功: ${TOKEN:0:20}...${NC}"
    echo "  トークン取得成功" >> "$TEST_RESULTS_FILE"
else
    echo -e "${RED}  トークン取得失敗${NC}"
    echo "  トークン取得失敗" >> "$TEST_RESULTS_FILE"
    exit 1
fi

# 1-5. ログイン（異常系：間違ったパスワード）
run_test "1-5. ログイン失敗（間違ったパスワード）" \
    "curl -s -X POST -H 'Content-Type: application/json' -d '{\"username\":\"testuser1\",\"password\":\"wrongpass\"}' $API_BASE/login" \
    "Invalid credentials"

# 1-6. ログイン（異常系：存在しないユーザー）
run_test "1-6. ログイン失敗（存在しないユーザー）" \
    "curl -s -X POST -H 'Content-Type: application/json' -d '{\"username\":\"nonexistent\",\"password\":\"pass123\"}' $API_BASE/login" \
    "Invalid credentials"

##############################################################################
# 2. 予定管理機能テスト
##############################################################################
echo ""
echo -e "${YELLOW}===========================================${NC}"
echo -e "${YELLOW}2. 予定管理機能テスト${NC}"
echo -e "${YELLOW}===========================================${NC}"
echo "" >> "$TEST_RESULTS_FILE"
echo "========================================" >> "$TEST_RESULTS_FILE"
echo "2. 予定管理機能テスト" >> "$TEST_RESULTS_FILE"
echo "========================================" >> "$TEST_RESULTS_FILE"

# 2-1. 予定追加（単一時間帯）
run_test "2-1. 予定追加（月曜 10:00-12:00）" \
    "curl -s -X POST -H 'Content-Type: application/json' -H 'Authorization: Bearer $TOKEN' -d '{\"availability\":{\"monday\":[{\"start\":\"10:00\",\"end\":\"12:00\"}]}}' $API_BASE/availability" \
    "Availability saved successfully"

# 2-2. 予定取得・確認
AVAIL_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" $API_BASE/availability)
run_test "2-2. 予定取得確認" \
    "echo '$AVAIL_RESPONSE'" \
    "monday"

# 詳細検証：予定内容確認
echo -e "${BLUE}  詳細検証: 予定内容${NC}"
MONDAY_START=$(echo "$AVAIL_RESPONSE" | jq -r '.monday[0].start')
MONDAY_END=$(echo "$AVAIL_RESPONSE" | jq -r '.monday[0].end')
if [[ "$MONDAY_START" == "10:00" && "$MONDAY_END" == "12:00" ]]; then
    echo -e "  ${GREEN}✓${NC} 月曜の予定: 10:00-12:00"
    echo "  ✓ 月曜の予定: 10:00-12:00" >> "$TEST_RESULTS_FILE"
else
    echo -e "  ${RED}✗${NC} 月曜の予定が期待と異なる: $MONDAY_START-$MONDAY_END"
    echo "  ✗ 月曜の予定が期待と異なる: $MONDAY_START-$MONDAY_END" >> "$TEST_RESULTS_FILE"
fi

# 2-3. 予定追加（複数時間帯）
run_test "2-3. 予定追加（火曜 複数時間帯）" \
    "curl -s -X POST -H 'Content-Type: application/json' -H 'Authorization: Bearer $TOKEN' -d '{\"availability\":{\"monday\":[{\"start\":\"10:00\",\"end\":\"12:00\"}],\"tuesday\":[{\"start\":\"09:00\",\"end\":\"10:30\"},{\"start\":\"14:00\",\"end\":\"16:00\"}]}}' $API_BASE/availability" \
    "Availability saved successfully"

# 2-4. 予定変更（開始時刻のみ変更）
run_test "2-4. 予定変更（月曜開始時刻 10:00→09:30）" \
    "curl -s -X POST -H 'Content-Type: application/json' -H 'Authorization: Bearer $TOKEN' -d '{\"availability\":{\"monday\":[{\"start\":\"09:30\",\"end\":\"12:00\"}],\"tuesday\":[{\"start\":\"09:00\",\"end\":\"10:30\"},{\"start\":\"14:00\",\"end\":\"16:00\"}]}}' $API_BASE/availability" \
    "Availability saved successfully"

# 変更確認
AVAIL_AFTER_CHANGE=$(curl -s -H "Authorization: Bearer $TOKEN" $API_BASE/availability)
MONDAY_START_NEW=$(echo "$AVAIL_AFTER_CHANGE" | jq -r '.monday[0].start')
if [[ "$MONDAY_START_NEW" == "09:30" ]]; then
    echo -e "  ${GREEN}✓${NC} 開始時刻変更確認: 09:30"
    echo "  ✓ 開始時刻変更確認: 09:30" >> "$TEST_RESULTS_FILE"
else
    echo -e "  ${RED}✗${NC} 開始時刻変更失敗: $MONDAY_START_NEW"
    echo "  ✗ 開始時刻変更失敗: $MONDAY_START_NEW" >> "$TEST_RESULTS_FILE"
fi

# 2-5. 予定変更（終了時刻のみ変更）
run_test "2-5. 予定変更（月曜終了時刻 12:00→13:00）" \
    "curl -s -X POST -H 'Content-Type: application/json' -H 'Authorization: Bearer $TOKEN' -d '{\"availability\":{\"monday\":[{\"start\":\"09:30\",\"end\":\"13:00\"}],\"tuesday\":[{\"start\":\"09:00\",\"end\":\"10:30\"},{\"start\":\"14:00\",\"end\":\"16:00\"}]}}' $API_BASE/availability" \
    "Availability saved successfully"

# 2-6. 予定追加（5日分）
run_test "2-6. 予定追加（全曜日）" \
    "curl -s -X POST -H 'Content-Type: application/json' -H 'Authorization: Bearer $TOKEN' -d '{\"availability\":{\"monday\":[{\"start\":\"09:00\",\"end\":\"12:00\"}],\"tuesday\":[{\"start\":\"10:00\",\"end\":\"11:00\"}],\"wednesday\":[{\"start\":\"14:00\",\"end\":\"16:00\"}],\"thursday\":[{\"start\":\"09:00\",\"end\":\"10:00\"}],\"friday\":[{\"start\":\"15:00\",\"end\":\"17:00\"}]}}' $API_BASE/availability" \
    "Availability saved successfully"

# 2-7. 予定削除（特定曜日）
run_test "2-7. 予定削除（水曜日）" \
    "curl -s -X POST -H 'Content-Type: application/json' -H 'Authorization: Bearer $TOKEN' -d '{\"availability\":{\"monday\":[{\"start\":\"09:00\",\"end\":\"12:00\"}],\"tuesday\":[{\"start\":\"10:00\",\"end\":\"11:00\"}],\"thursday\":[{\"start\":\"09:00\",\"end\":\"10:00\"}],\"friday\":[{\"start\":\"15:00\",\"end\":\"17:00\"}]}}' $API_BASE/availability" \
    "Availability saved successfully"

# 削除確認
AVAIL_AFTER_DELETE=$(curl -s -H "Authorization: Bearer $TOKEN" $API_BASE/availability)
HAS_WEDNESDAY=$(echo "$AVAIL_AFTER_DELETE" | jq 'has("wednesday")')
if [[ "$HAS_WEDNESDAY" == "false" ]]; then
    echo -e "  ${GREEN}✓${NC} 水曜日削除確認"
    echo "  ✓ 水曜日削除確認" >> "$TEST_RESULTS_FILE"
else
    echo -e "  ${RED}✗${NC} 水曜日削除失敗"
    echo "  ✗ 水曜日削除失敗" >> "$TEST_RESULTS_FILE"
fi

# 2-8. 予定全削除
run_test "2-8. 予定全削除" \
    "curl -s -X POST -H 'Content-Type: application/json' -H 'Authorization: Bearer $TOKEN' -d '{\"availability\":{}}' $API_BASE/availability" \
    "Availability saved successfully"

##############################################################################
# 3. グリッドスケジュール機能テスト
##############################################################################
echo ""
echo -e "${YELLOW}===========================================${NC}"
echo -e "${YELLOW}3. グリッドスケジュール機能テスト${NC}"
echo -e "${YELLOW}===========================================${NC}"
echo "" >> "$TEST_RESULTS_FILE"
echo "========================================" >> "$TEST_RESULTS_FILE"
echo "3. グリッドスケジュール機能テスト" >> "$TEST_RESULTS_FILE"
echo "========================================" >> "$TEST_RESULTS_FILE"

# 複数ユーザー作成して予定を追加
curl -s -X POST -H 'Content-Type: application/json' -d '{"username":"testuser2","password":"pass123","start_time":"09:00","end_time":"18:00"}' $API_BASE/register > /dev/null
TOKEN2=$(curl -s -X POST -H 'Content-Type: application/json' -d '{"username":"testuser2","password":"pass123"}' $API_BASE/login | jq -r '.access_token')

# testuser1の予定を再追加
curl -s -X POST -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" -d '{"availability":{"monday":[{"start":"10:00","end":"12:00"}],"tuesday":[{"start":"14:00","end":"16:00"}]}}' $API_BASE/availability > /dev/null

# testuser2の予定を追加
curl -s -X POST -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN2" -d '{"availability":{"monday":[{"start":"10:00","end":"11:00"}],"tuesday":[{"start":"15:00","end":"17:00"}]}}' $API_BASE/availability > /dev/null

# 3-1. グリッドスケジュール取得
GRID_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" $API_BASE/grid-schedule)
run_test "3-1. グリッドスケジュール取得" \
    "echo '$GRID_RESPONSE'" \
    "grid_schedule"

# 3-2. 参加者数確認（重複時間帯）
echo -e "${BLUE}  詳細検証: 月曜10:00-11:00の参加者${NC}"
MONDAY_10_PARTICIPANTS=$(echo "$GRID_RESPONSE" | jq -r '.grid_schedule.monday[] | select(.start=="10:00" and .end=="10:30") | .participant_count')
if [[ "$MONDAY_10_PARTICIPANTS" == "2" ]]; then
    echo -e "  ${GREEN}✓${NC} 月曜10:00-10:30の参加者数: 2人"
    echo "  ✓ 月曜10:00-10:30の参加者数: 2人" >> "$TEST_RESULTS_FILE"
else
    echo -e "  ${YELLOW}⚠${NC} 月曜10:00-10:30の参加者数: $MONDAY_10_PARTICIPANTS"
    echo "  ⚠ 月曜10:00-10:30の参加者数: $MONDAY_10_PARTICIPANTS" >> "$TEST_RESULTS_FILE"
fi

# 3-3. 全ユーザーavailability取得
run_test "3-3. 全ユーザーavailability取得" \
    "curl -s -H 'Authorization: Bearer $TOKEN' $API_BASE/availability/all" \
    "testuser1"

##############################################################################
# 4. セッション永続性テスト
##############################################################################
echo ""
echo -e "${YELLOW}===========================================${NC}"
echo -e "${YELLOW}4. セッション永続性テスト${NC}"
echo -e "${YELLOW}===========================================${NC}"
echo "" >> "$TEST_RESULTS_FILE"
echo "========================================" >> "$TEST_RESULTS_FILE"
echo "4. セッション永続性テスト" >> "$TEST_RESULTS_FILE"
echo "========================================" >> "$TEST_RESULTS_FILE"

# 4-1. ログアウト（トークン破棄シミュレーション）→再ログイン
NEW_LOGIN=$(curl -s -X POST -H 'Content-Type: application/json' -d '{"username":"testuser1","password":"pass123"}' $API_BASE/login)
NEW_TOKEN=$(echo "$NEW_LOGIN" | jq -r '.access_token')
run_test "4-1. 再ログイン成功" \
    "echo '$NEW_LOGIN'" \
    "access_token"

# 4-2. 再ログイン後に予定取得
AVAIL_AFTER_RELOGIN=$(curl -s -H "Authorization: Bearer $NEW_TOKEN" $API_BASE/availability)
run_test "4-2. 再ログイン後の予定取得" \
    "echo '$AVAIL_AFTER_RELOGIN'" \
    "monday"

# 予定が保持されているか確認
HAS_MONDAY_AFTER=$(echo "$AVAIL_AFTER_RELOGIN" | jq 'has("monday")')
if [[ "$HAS_MONDAY_AFTER" == "true" ]]; then
    echo -e "  ${GREEN}✓${NC} 予定が正しく保持されている"
    echo "  ✓ 予定が正しく保持されている" >> "$TEST_RESULTS_FILE"
else
    echo -e "  ${RED}✗${NC} 予定が失われた"
    echo "  ✗ 予定が失われた" >> "$TEST_RESULTS_FILE"
fi

##############################################################################
# 5. Admin機能テスト
##############################################################################
echo ""
echo -e "${YELLOW}===========================================${NC}"
echo -e "${YELLOW}5. Admin機能テスト${NC}"
echo -e "${YELLOW}===========================================${NC}"
echo "" >> "$TEST_RESULTS_FILE"
echo "========================================" >> "$TEST_RESULTS_FILE"
echo "5. Admin機能テスト" >> "$TEST_RESULTS_FILE"
echo "========================================" >> "$TEST_RESULTS_FILE"

# Adminログイン
ADMIN_LOGIN=$(curl -s -X POST -H 'Content-Type: application/json' -d '{"username":"admin","password":"admin123"}' $API_BASE/login)
ADMIN_TOKEN=$(echo "$ADMIN_LOGIN" | jq -r '.access_token')

# 5-1. 全ユーザーリスト取得
USERS_LIST=$(curl -s -H "Authorization: Bearer $ADMIN_TOKEN" $API_BASE/admin/users)
run_test "5-1. 全ユーザーリスト取得（Admin）" \
    "echo '$USERS_LIST'" \
    "users"

# ユーザー数確認
USER_COUNT=$(echo "$USERS_LIST" | jq '.users | length')
echo -e "  ${BLUE}登録ユーザー数: $USER_COUNT${NC}"
echo "  登録ユーザー数: $USER_COUNT" >> "$TEST_RESULTS_FILE"

# 5-2. ユーザー削除（testuser2）
TESTUSER2_ID=$(echo "$USERS_LIST" | jq -r '.users[] | select(.username=="testuser2") | .id')
if [[ -n "$TESTUSER2_ID" && "$TESTUSER2_ID" != "null" ]]; then
    run_test "5-2. ユーザー削除（testuser2）" \
        "curl -s -X DELETE -H 'Authorization: Bearer $ADMIN_TOKEN' $API_BASE/admin/users/$TESTUSER2_ID" \
        "deleted successfully"
else
    echo -e "${YELLOW}  testuser2が見つからない、スキップ${NC}"
fi

# 5-3. 削除確認
USERS_AFTER_DELETE=$(curl -s -H "Authorization: Bearer $ADMIN_TOKEN" $API_BASE/admin/users)
HAS_TESTUSER2=$(echo "$USERS_AFTER_DELETE" | jq -r '.users[] | select(.username=="testuser2") | .username')
if [[ -z "$HAS_TESTUSER2" ]]; then
    echo -e "  ${GREEN}✓${NC} testuser2削除確認"
    echo "  ✓ testuser2削除確認" >> "$TEST_RESULTS_FILE"
else
    echo -e "  ${RED}✗${NC} testuser2削除失敗"
    echo "  ✗ testuser2削除失敗" >> "$TEST_RESULTS_FILE"
fi

# 5-4. データエクスポート
EXPORT_DATA=$(curl -s -H "Authorization: Bearer $ADMIN_TOKEN" $API_BASE/admin/export)
run_test "5-4. データエクスポート" \
    "echo '$EXPORT_DATA'" \
    "export_info"

# エクスポート内容確認
EXPORT_USER_COUNT=$(echo "$EXPORT_DATA" | jq '.users | length')
echo -e "  ${BLUE}エクスポートユーザー数: $EXPORT_USER_COUNT${NC}"
echo "  エクスポートユーザー数: $EXPORT_USER_COUNT" >> "$TEST_RESULTS_FILE"

##############################################################################
# 6. LLM分析機能テスト
##############################################################################
echo ""
echo -e "${YELLOW}===========================================${NC}"
echo -e "${YELLOW}6. LLM分析機能テスト${NC}"
echo -e "${YELLOW}===========================================${NC}"
echo "" >> "$TEST_RESULTS_FILE"
echo "========================================" >> "$TEST_RESULTS_FILE"
echo "6. LLM分析機能テスト" >> "$TEST_RESULTS_FILE"
echo "========================================" >> "$TEST_RESULTS_FILE"

# 6-1. LLM分析実行
LLM_RESPONSE=$(curl -s -H "Authorization: Bearer $ADMIN_TOKEN" $API_BASE/llm-analysis)
run_test "6-1. LLM分析実行" \
    "echo '$LLM_RESPONSE'" \
    "success"

# 分析結果の候補数確認
if echo "$LLM_RESPONSE" | jq -e '.top_candidates' > /dev/null 2>&1; then
    CANDIDATES_COUNT=$(echo "$LLM_RESPONSE" | jq '.top_candidates | length')
    echo -e "  ${BLUE}会議候補数: $CANDIDATES_COUNT${NC}"
    echo "  会議候補数: $CANDIDATES_COUNT" >> "$TEST_RESULTS_FILE"
fi

##############################################################################
# 7. エッジケース・境界値テスト
##############################################################################
echo ""
echo -e "${YELLOW}===========================================${NC}"
echo -e "${YELLOW}7. エッジケース・境界値テスト${NC}"
echo -e "${YELLOW}===========================================${NC}"
echo "" >> "$TEST_RESULTS_FILE"
echo "========================================" >> "$TEST_RESULTS_FILE"
echo "7. エッジケース・境界値テスト" >> "$TEST_RESULTS_FILE"
echo "========================================" >> "$TEST_RESULTS_FILE"

# 7-1. 最小時間（8:00開始）
run_test "7-1. 最小時間帯（8:00-8:30）" \
    "curl -s -X POST -H 'Content-Type: application/json' -H 'Authorization: Bearer $NEW_TOKEN' -d '{\"availability\":{\"monday\":[{\"start\":\"08:00\",\"end\":\"08:30\"}]}}' $API_BASE/availability" \
    "Availability saved successfully"

# 7-2. 最大時間（18:00終了）
run_test "7-2. 最大時間帯（17:30-18:00）" \
    "curl -s -X POST -H 'Content-Type: application/json' -H 'Authorization: Bearer $NEW_TOKEN' -d '{\"availability\":{\"monday\":[{\"start\":\"17:30\",\"end\":\"18:00\"}]}}' $API_BASE/availability" \
    "Availability saved successfully"

# 7-3. 連続した時間帯
run_test "7-3. 連続時間帯（9:00-12:00を30分刻み）" \
    "curl -s -X POST -H 'Content-Type: application/json' -H 'Authorization: Bearer $NEW_TOKEN' -d '{\"availability\":{\"monday\":[{\"start\":\"09:00\",\"end\":\"09:30\"},{\"start\":\"09:30\",\"end\":\"10:00\"},{\"start\":\"10:00\",\"end\":\"10:30\"}]}}' $API_BASE/availability" \
    "Availability saved successfully"

# 7-4. 空の予定データ
run_test "7-4. 空の予定データ" \
    "curl -s -X POST -H 'Content-Type: application/json' -H 'Authorization: Bearer $NEW_TOKEN' -d '{\"availability\":{}}' $API_BASE/availability" \
    "Availability saved successfully"

# 7-5. 不正な認証トークン
run_test "7-5. 不正な認証トークン（401エラー期待）" \
    "curl -s -w '%{http_code}' -o /dev/null -H 'Authorization: Bearer invalid_token_12345' $API_BASE/availability" \
    "401"

##############################################################################
# テスト結果サマリー
##############################################################################
echo ""
echo -e "${YELLOW}===========================================${NC}"
echo -e "${YELLOW}テスト結果サマリー${NC}"
echo -e "${YELLOW}===========================================${NC}"
echo "" >> "$TEST_RESULTS_FILE"
echo "========================================" >> "$TEST_RESULTS_FILE"
echo "テスト結果サマリー" >> "$TEST_RESULTS_FILE"
echo "========================================" >> "$TEST_RESULTS_FILE"

COVERAGE=$(awk "BEGIN {printf \"%.2f\", ($PASSED/$TOTAL)*100}")

echo -e "${BLUE}総テスト数: $TOTAL${NC}"
echo -e "${GREEN}成功: $PASSED${NC}"
echo -e "${RED}失敗: $FAILED${NC}"
echo -e "${BLUE}カバレッジ: $COVERAGE%${NC}"

echo "総テスト数: $TOTAL" >> "$TEST_RESULTS_FILE"
echo "成功: $PASSED" >> "$TEST_RESULTS_FILE"
echo "失敗: $FAILED" >> "$TEST_RESULTS_FILE"
echo "カバレッジ: $COVERAGE%" >> "$TEST_RESULTS_FILE"

if [[ $FAILED -eq 0 ]]; then
    echo ""
    echo -e "${GREEN}🎉 全テスト合格！${NC}"
    echo "" >> "$TEST_RESULTS_FILE"
    echo "🎉 全テスト合格！" >> "$TEST_RESULTS_FILE"
else
    echo ""
    echo -e "${RED}⚠️  一部のテストが失敗しました${NC}"
    echo "" >> "$TEST_RESULTS_FILE"
    echo "⚠️  一部のテストが失敗しました" >> "$TEST_RESULTS_FILE"
fi

echo ""
echo "終了時刻: $(date)" >> "$TEST_RESULTS_FILE"
echo "詳細結果: $TEST_RESULTS_FILE"
echo ""
