#!/usr/bin/env python3

import requests
import json

def test_grid_api():
    """新しいグリッドAPIでken's 08:30スロットをテスト"""

    print("🎯 新しいグリッドAPIテスト - ken's 08:30確認")
    print("=" * 50)

    # Login
    login_data = {"username": "admin", "password": "admin123"}

    try:
        print("🔑 Logging in...")
        login_response = requests.post("http://localhost:5000/api/login", json=login_data)

        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return False

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful")

        # Test new grid API
        print("📊 Testing /api/grid-schedule...")
        response = requests.get("http://localhost:5000/api/grid-schedule", headers=headers)

        if response.status_code != 200:
            print(f"❌ Grid API failed: {response.text}")
            return False

        data = response.json()

        print(f"📋 Response keys: {list(data.keys())}")
        print(f"🕐 Grid info: {data['time_grid_info']}")

        # Check Monday schedule
        monday_schedule = data.get('grid_schedule', {}).get('monday', [])
        print(f"\n📅 Monday slots found: {len(monday_schedule)}")

        ken_0830_found = False

        for slot in monday_schedule:
            print(f"  Index {slot['grid_index']:2d}: {slot['start']}-{slot['end']} | {slot['participant_count']} people | {slot['available_users']}")

            if slot['start'] == '08:30' and 'ken' in slot['available_users']:
                ken_0830_found = True
                print(f"  🎯 SUCCESS: ken's 08:30-09:00 slot found at grid index {slot['grid_index']}!")

        # Verification
        print(f"\n🔍 VERIFICATION:")
        print("=" * 30)

        if ken_0830_found:
            print("✅ SUCCESS: ken's 08:30-09:00 slot is correctly positioned!")
            print("✅ Fixed grid system is working!")
            return True
        else:
            print("❌ FAILURE: ken's 08:30-09:00 slot not found")

            # Debug info
            print("\nDebugging - Grid mapping:")
            for i, grid_slot in enumerate(data['grid_mapping'][:10]):  # Show first 10
                print(f"  Index {i}: {grid_slot}")

            return False

    except Exception as e:
        print(f"💥 Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_grid_api()