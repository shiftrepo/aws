#!/usr/bin/env python3
"""
シンプルな固定グリッドロジック
7:00-19:00を30分刻みで区切り、SQLデータを正確にマッピング
"""

def create_time_grid():
    """
    8:00-18:00を30分刻みで固定グリッド作成
    Returns: [(start_time, end_time, grid_index), ...]
    """
    grid = []
    start_hour = 8  # 8:00開始
    end_hour = 18   # 18:00終了

    index = 0
    for hour in range(start_hour, end_hour):
        for minute in [0, 30]:  # 00分と30分の2つのスロット
            start_time = f"{hour:02d}:{minute:02d}"

            if minute == 0:
                end_time = f"{hour:02d}:30"
            else:
                end_time = f"{hour+1:02d}:00"

            grid.append({
                'start': start_time,
                'end': end_time,
                'index': index
            })
            index += 1

    return grid

def time_to_grid_index(time_str):
    """
    時間文字列をグリッドインデックスに変換
    '08:30' -> 3 (7:00=0, 7:30=1, 8:00=2, 8:30=3)
    """
    try:
        hours, minutes = map(int, time_str.split(':'))

        # 8:00を基準とした分数計算
        total_minutes = (hours - 8) * 60 + minutes

        # 30分刻みでのインデックス
        grid_index = total_minutes // 30

        # 範囲外チェック (8:00-18:00 = 0-19)
        if grid_index < 0 or grid_index > 19:
            return None

        return grid_index

    except ValueError:
        return None

def grid_index_to_time(index):
    """
    グリッドインデックスを時間文字列に変換
    3 -> '08:30'
    """
    if index < 0 or index > 19:
        return None

    # インデックスから分数計算
    total_minutes = index * 30
    hours = 8 + (total_minutes // 60)
    minutes = total_minutes % 60

    return f"{hours:02d}:{minutes:02d}"

def check_user_availability_in_slot(user_availability, day, grid_slot):
    """
    ユーザーが指定されたグリッドスロットで利用可能かチェック
    """
    if day not in user_availability:
        return False

    slot_start_minutes = time_to_minutes(grid_slot['start'])
    slot_end_minutes = time_to_minutes(grid_slot['end'])

    for availability in user_availability[day]:
        avail_start_minutes = time_to_minutes(availability['start'])
        avail_end_minutes = time_to_minutes(availability['end'])

        # 完全に重複しているかチェック
        if avail_start_minutes <= slot_start_minutes and avail_end_minutes >= slot_end_minutes:
            return True

    return False

def time_to_minutes(time_str):
    """時間文字列を分数に変換"""
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes

# テスト関数
if __name__ == "__main__":
    print("🕐 固定グリッドテスト")
    print("=" * 40)

    grid = create_time_grid()
    print(f"グリッド数: {len(grid)}")
    print(f"最初のスロット: {grid[0]}")
    print(f"最後のスロット: {grid[-1]}")

    # kenの08:30テスト
    ken_time = "08:30"
    ken_index = time_to_grid_index(ken_time)
    print(f"\nken's {ken_time} -> インデックス {ken_index}")
    print(f"インデックス {ken_index} -> {grid_index_to_time(ken_index)}")

    # グリッドスロット情報
    if ken_index is not None and ken_index < len(grid):
        slot = grid[ken_index]
        print(f"ken's スロット: {slot}")