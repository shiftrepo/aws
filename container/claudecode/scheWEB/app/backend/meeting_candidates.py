#!/usr/bin/env python3
"""
会議候補時間分析ツール
予定の合う時間帯を俯瞰グリッドで表示し、上位4つの候補をピックアップ
LLM（Bedrock）を使用してより高度な分析を実行
"""

import sqlite3
import sys
import os
import json
import boto3
from datetime import datetime, timedelta
from collections import defaultdict

class MeetingCandidateAnalyzer:
    def __init__(self, db_path=None):
        # 環境変数からデータベースパスを取得、デフォルトは/app/data/scheduler.db
        self.db_path = db_path or os.getenv('DATABASE_PATH', '/app/data/scheduler.db')
        self.time_slots = self.generate_time_slots()

        # Bedrock設定（環境変数から取得）
        self.setup_bedrock_client()

    def setup_bedrock_client(self):
        """Bedrock クライアントを環境変数から設定"""
        try:
            # 環境変数からAWS設定を取得
            aws_region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
            aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
            aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

            if aws_access_key and aws_secret_key:
                self.bedrock_client = boto3.client(
                    'bedrock-runtime',
                    region_name=aws_region,
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key
                )
                self.llm_available = True
                print(f"✅ Bedrock クライアント初期化完了 (リージョン: {aws_region})")
            else:
                self.bedrock_client = None
                self.llm_available = False
                print("⚠️  AWS認証情報が見つかりません。LLM分析は無効化されます。")

        except Exception as e:
            self.bedrock_client = None
            self.llm_available = False
            print(f"❌ Bedrock クライアント初期化エラー: {e}")

    def analyze_with_llm(self, candidates, all_users):
        """LLM（Bedrock）を使用して会議候補を詳細分析"""
        if not self.llm_available:
            print("⚠️ LLM分析がスキップされました（Bedrock利用不可）")
            return self.get_top_candidates(candidates)

        try:
            # 分析用データを準備
            analysis_data = {
                'total_users': len(all_users),
                'users': list(all_users.values()),
                'candidates': candidates[:10],  # 上位10候補をLLMに送信
                'context': {
                    'working_hours': '7:00-19:00',
                    'slot_duration': '30 minutes',
                    'analysis_goal': 'Find optimal meeting times prioritizing participant count and duration'
                }
            }

            # LLMプロンプトを構築
            prompt = self.build_analysis_prompt(analysis_data)

            # Bedrock APIを呼び出し
            response = self.call_bedrock_llm(prompt)

            # LLMレスポンスを解析
            llm_analysis = self.parse_llm_response(response)

            # LLMの推奨を既存候補と組み合わせ
            enhanced_candidates = self.enhance_candidates_with_llm(candidates, llm_analysis)

            return enhanced_candidates[:4]  # 上位4つを返却

        except Exception as e:
            print(f"❌ LLM分析エラー: {e}")
            # フォールバックとして従来の分析を返却
            return self.get_top_candidates(candidates)

    def build_analysis_prompt(self, data):
        """LLM分析用プロンプトを構築"""
        prompt = f"""
あなたはチームスケジューリングの専門家です。以下のデータに基づいて最適な会議時間を分析してください。

## チーム情報
- 総メンバー数: {data['total_users']}人
- メンバー: {', '.join(data['users'])}

## 会議候補データ
以下は予定の合う時間帯の候補です：

"""
        for i, candidate in enumerate(data['candidates'], 1):
            prompt += f"""
{i}. {candidate['day_japanese']} {candidate['start']}-{candidate['end']}
   - 参加者: {candidate['participant_count']}人/{candidate['total_users']}人 ({candidate['availability_percentage']}%)
   - 参加可能: {', '.join(candidate['available_users'])}
   - 参加不可: {', '.join(candidate['unavailable_users']) if candidate['unavailable_users'] else 'なし'}
   - 時間長: {candidate['duration']}分
"""

        prompt += """

## 分析要求
上記の候補から最適な会議時間を4つ選んで、以下の形式でJSONレスポンスを生成してください：

1. **参加人数を重視**（より多くの人が参加できる時間を優先）
2. **時間の長さを考慮**（長い時間確保できる方を優先）
3. **時間帯の実用性**（午前中や昼食後など、会議に適した時間）
4. **チーム全体のバランス**（特定の人だけが常に参加できない状況を避ける）

レスポンス形式：
{
  "analysis_summary": "分析の要約（日本語）",
  "recommendations": [
    {
      "rank": 1,
      "day": "monday",
      "start": "11:00",
      "end": "12:00",
      "reasoning": "選択理由（日本語）",
      "priority_score": 95
    }
  ],
  "insights": [
    "チームスケジュールに関する洞察1",
    "チームスケジュールに関する洞察2"
  ]
}

JSONのみを返してください。追加の説明は不要です。
"""
        return prompt

    def call_bedrock_llm(self, prompt):
        """Bedrock LLMを呼び出し"""
        try:
            # Claude 3 Sonnetを使用
            model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3
            }

            response = self.bedrock_client.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body),
                contentType='application/json'
            )

            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']

        except Exception as e:
            print(f"❌ Bedrock API呼び出しエラー: {e}")
            raise e

    def parse_llm_response(self, response_text):
        """LLMレスポンスを解析"""
        try:
            # JSONブロックを抽出
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                return json.loads(json_text)
            else:
                print("❌ LLMレスポンスでJSONが見つかりませんでした")
                return None

        except json.JSONDecodeError as e:
            print(f"❌ LLMレスポンスのJSON解析エラー: {e}")
            return None

    def enhance_candidates_with_llm(self, candidates, llm_analysis):
        """LLM分析結果で候補を強化"""
        if not llm_analysis or 'recommendations' not in llm_analysis:
            return self.get_top_candidates(candidates)

        enhanced = []

        # LLMの推奨順に候補を並べ直し
        for rec in llm_analysis['recommendations']:
            # 既存候補から対応するものを検索
            matching_candidate = None
            for candidate in candidates:
                if (candidate['day'] == rec.get('day') and
                    candidate['start'] == rec.get('start') and
                    candidate['end'] == rec.get('end')):
                    matching_candidate = candidate.copy()
                    break

            if matching_candidate:
                # LLM分析結果を追加
                matching_candidate['llm_rank'] = rec.get('rank', 999)
                matching_candidate['llm_reasoning'] = rec.get('reasoning', '')
                matching_candidate['llm_priority_score'] = rec.get('priority_score', 0)
                enhanced.append(matching_candidate)

        # LLMで見つからなかった場合は従来のロジックでフォールバック
        if len(enhanced) < 4:
            fallback_candidates = self.get_top_candidates(candidates)
            for candidate in fallback_candidates:
                if candidate not in enhanced and len(enhanced) < 4:
                    enhanced.append(candidate)

        # LLM分析サマリーを追加
        if len(enhanced) > 0 and 'analysis_summary' in llm_analysis:
            enhanced[0]['llm_analysis_summary'] = llm_analysis['analysis_summary']

        if 'insights' in llm_analysis:
            enhanced[0]['llm_insights'] = llm_analysis['insights']

        return enhanced[:4]

    def generate_time_slots(self):
        """7:00-19:00を30分間隔で生成"""
        slots = []
        for hour in range(7, 19):
            for minute in [0, 30]:
                start_time = f"{hour:02d}:{minute:02d}"
                if minute == 0:
                    end_time = f"{hour:02d}:30"
                else:
                    end_time = f"{hour+1:02d}:00"

                slots.append({
                    'index': len(slots),
                    'start': start_time,
                    'end': end_time,
                    'duration': 30  # minutes
                })
        return slots

    def get_all_availability(self):
        """全ユーザーのavailabilityを取得"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        query = '''
            SELECT u.id, u.username, a.day_of_week, a.start_time, a.end_time
            FROM users u
            LEFT JOIN availability a ON u.id = a.user_id
            ORDER BY u.username, a.day_of_week, a.start_time
        '''

        rows = conn.execute(query).fetchall()

        # Get all users for reference
        all_users_query = 'SELECT id, username FROM users ORDER BY username'
        all_users = {row['id']: row['username'] for row in conn.execute(all_users_query).fetchall()}

        conn.close()

        return rows, all_users

    def time_to_minutes(self, time_str):
        """時間文字列を分数に変換"""
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes

    def check_user_availability_in_slot(self, user_availability, day, grid_slot):
        """ユーザーが指定されたグリッドスロットで利用可能かチェック"""
        if day not in user_availability:
            return False

        slot_start_minutes = self.time_to_minutes(grid_slot['start'])
        slot_end_minutes = self.time_to_minutes(grid_slot['end'])

        for availability in user_availability[day]:
            avail_start_minutes = self.time_to_minutes(availability['start'])
            avail_end_minutes = self.time_to_minutes(availability['end'])

            # 完全に重複しているかチェック
            if avail_start_minutes <= slot_start_minutes and avail_end_minutes >= slot_end_minutes:
                return True

        return False

    def analyze_meeting_candidates(self):
        """会議候補時間を分析"""
        rows, all_users = self.get_all_availability()

        # ユーザーごとのavailabilityを整理
        user_availability = {}
        for row in rows:
            user_id = row['id']
            username = row['username']

            if user_id not in user_availability:
                user_availability[user_id] = {'username': username, 'days': {}}

            if row['day_of_week']:
                day = row['day_of_week']
                if day not in user_availability[user_id]['days']:
                    user_availability[user_id]['days'][day] = []

                user_availability[user_id]['days'][day].append({
                    'start': row['start_time'],
                    'end': row['end_time']
                })

        # 各曜日の各時間スロットでの参加可能者を計算
        DAYS_OF_WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']

        meeting_candidates = []

        for day in DAYS_OF_WEEK:
            for grid_slot in self.time_slots:
                available_users = []

                # 各ユーザーがこのスロットで利用可能かチェック
                for user_id, user_data in user_availability.items():
                    if self.check_user_availability_in_slot(user_data['days'], day, grid_slot):
                        available_users.append(user_data['username'])

                # 2人以上が参加可能な時間帯のみを候補とする
                if len(available_users) >= 2:
                    unavailable_users = [username for uid, username in all_users.items()
                                       if username not in available_users]

                    candidate = {
                        'day': day,
                        'day_japanese': self.get_japanese_day(day),
                        'grid_index': grid_slot['index'],
                        'start': grid_slot['start'],
                        'end': grid_slot['end'],
                        'duration': grid_slot['duration'],
                        'participant_count': len(available_users),
                        'available_users': sorted(available_users),
                        'unavailable_users': sorted(unavailable_users),
                        'availability_percentage': round((len(available_users) / len(all_users)) * 100, 1),
                        'total_users': len(all_users)
                    }

                    meeting_candidates.append(candidate)

        return meeting_candidates, all_users

    def get_japanese_day(self, day):
        """英語の曜日を日本語に変換"""
        day_map = {
            'monday': '月曜日',
            'tuesday': '火曜日',
            'wednesday': '水曜日',
            'thursday': '木曜日',
            'friday': '金曜日'
        }
        return day_map.get(day, day)

    def get_top_candidates(self, candidates, top_n=4):
        """優先順位で上位N個の候補を選択"""
        # 優先順位:
        # 1. 参加人数が多い
        # 2. 時間の長さ（連続した時間帯を重視）
        # 3. より早い時間帯を優先

        # まず参加人数でソート（降順）、次に時間でソート（昇順）
        sorted_candidates = sorted(candidates,
                                 key=lambda x: (-x['participant_count'],
                                              x['grid_index']))

        # 連続する時間帯をグループ化して長い時間帯を優先
        grouped_candidates = self.group_consecutive_slots(sorted_candidates)

        return grouped_candidates[:top_n]

    def group_consecutive_slots(self, candidates):
        """連続する時間帯をグループ化"""
        # 日付・参加者でグループ化
        groups = defaultdict(list)

        for candidate in candidates:
            # 同じ日付・同じ参加者の組み合わせでグループ化
            key = (candidate['day'], tuple(candidate['available_users']))
            groups[key].append(candidate)

        # 各グループで連続する時間帯を統合
        merged_candidates = []

        for (day, users), group in groups.items():
            # グリッドインデックスでソート
            group.sort(key=lambda x: x['grid_index'])

            i = 0
            while i < len(group):
                current = group[i]
                consecutive_slots = [current]

                # 連続する次のスロットを探す
                j = i + 1
                while j < len(group) and group[j]['grid_index'] == group[j-1]['grid_index'] + 1:
                    consecutive_slots.append(group[j])
                    j += 1

                # 連続する時間帯をマージ
                if len(consecutive_slots) > 1:
                    merged = {
                        'day': current['day'],
                        'day_japanese': current['day_japanese'],
                        'grid_index': current['grid_index'],
                        'start': consecutive_slots[0]['start'],
                        'end': consecutive_slots[-1]['end'],
                        'duration': len(consecutive_slots) * 30,
                        'participant_count': current['participant_count'],
                        'available_users': current['available_users'],
                        'unavailable_users': current['unavailable_users'],
                        'availability_percentage': current['availability_percentage'],
                        'total_users': current['total_users'],
                        'consecutive_slots': len(consecutive_slots)
                    }
                    merged_candidates.append(merged)
                else:
                    current['consecutive_slots'] = 1
                    merged_candidates.append(current)

                i = j

        # 再ソート: 参加人数、連続時間長さ、早い時間順
        merged_candidates.sort(key=lambda x: (-x['participant_count'],
                                            -x['consecutive_slots'],
                                            x['grid_index']))

        return merged_candidates

    def create_grid_display(self, candidates, all_users, top_candidates):
        """俯瞰グリッド表示を生成"""
        print("\n" + "="*80)
        print("📅 会議時間候補　俯瞰グリッド")
        print("="*80)

        # ヘッダー
        print("\n🕐 時間グリッド (7:00-19:00, 30分間隔)")
        print("-" * 60)

        # 曜日ごとの表示
        DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        day_names = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日']

        for day, day_name in zip(DAYS, day_names):
            print(f"\n【{day_name}】")
            day_candidates = [c for c in candidates if c['day'] == day]

            if day_candidates:
                # 時間順でソート
                day_candidates.sort(key=lambda x: x['grid_index'])

                for candidate in day_candidates:
                    participants = ", ".join(candidate['available_users'])
                    unavailable = ", ".join(candidate['unavailable_users']) if candidate['unavailable_users'] else "なし"

                    print(f"  {candidate['start']}-{candidate['end']} "
                          f"({candidate['participant_count']}人/{candidate['total_users']}人 "
                          f"{candidate['availability_percentage']}%)")
                    print(f"    ✅ 参加可能: {participants}")
                    print(f"    ❌ 参加不可: {unavailable}")
                    print()
            else:
                print("  会議可能な時間帯なし")
                print()

    def display_top_candidates(self, top_candidates):
        """上位4つの候補を表示"""
        print("\n" + "🎯" + "="*78)
        print("🏆 おすすめ会議時間候補 TOP 4")
        print("="*80)

        for i, candidate in enumerate(top_candidates, 1):
            duration_text = f"{candidate['duration']}分"
            if candidate.get('consecutive_slots', 1) > 1:
                duration_text += f" (連続{candidate['consecutive_slots']}スロット)"

            print(f"\n【第{i}位】 {candidate['day_japanese']} {candidate['start']}-{candidate['end']} ({duration_text})")
            print(f"  参加者: {candidate['participant_count']}人/{candidate['total_users']}人 ({candidate['availability_percentage']}%)")
            print(f"  ✅ 参加可能: {', '.join(candidate['available_users'])}")

            if candidate['unavailable_users']:
                print(f"  ❌ 参加不可: {', '.join(candidate['unavailable_users'])}")

            # 優先度の理由
            reasons = []
            if candidate['participant_count'] >= candidate['total_users'] * 0.75:
                reasons.append("高参加率")
            if candidate.get('consecutive_slots', 1) > 1:
                reasons.append("長時間確保")
            if candidate['grid_index'] < 8:  # 午前中
                reasons.append("午前中")

            if reasons:
                print(f"  🎯 選出理由: {', '.join(reasons)}")

            print("-" * 60)

def main():
    analyzer = MeetingCandidateAnalyzer()

    try:
        print("📊 会議候補時間分析を開始...")
        candidates, all_users = analyzer.analyze_meeting_candidates()

        if not candidates:
            print("❌ 2人以上が参加可能な時間帯が見つかりませんでした。")
            return

        print(f"✅ {len(candidates)}個の会議可能時間帯を発見")

        # 俯瞰グリッド表示
        top_candidates = analyzer.get_top_candidates(candidates)
        analyzer.create_grid_display(candidates, all_users, top_candidates)

        # トップ4候補表示
        analyzer.display_top_candidates(top_candidates)

        print(f"\n📈 総合統計:")
        print(f"  - 登録ユーザー数: {len(all_users)}人")
        print(f"  - 会議可能時間帯: {len(candidates)}個")
        print(f"  - 最高参加率: {max(c['availability_percentage'] for c in candidates)}%")
        print(f"  - 平均参加率: {sum(c['availability_percentage'] for c in candidates) / len(candidates):.1f}%")

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()