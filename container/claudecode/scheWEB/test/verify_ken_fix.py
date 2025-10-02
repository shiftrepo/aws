#!/usr/bin/env python3

import requests
import json
import sys

def test_ken_08_30_fix():
    """Test that ken's 08:30-09:00 slot appears in the corrected API response"""

    print("🔧 Testing corrected meeting-compatibility API...")
    print("=" * 50)

    # Login and get token
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

        # Get meeting compatibility data
        print("📊 Calling /api/meeting-compatibility...")
        response = requests.get("http://localhost:5000/api/meeting-compatibility", headers=headers)

        if response.status_code != 200:
            print(f"❌ API call failed: {response.text}")
            return False

        data = response.json()

        print(f"📋 Response keys: {list(data.keys())}")

        # Check for ken's 08:30 slot in different categories
        found_08_30 = False
        found_in_category = None

        # 1. Check meeting_slots (all slots including 1-person)
        monday_slots = data.get('meeting_slots', {}).get('monday', [])
        print(f"\n📅 Monday meeting_slots ({len(monday_slots)} slots):")

        for slot in monday_slots:
            print(f"  {slot['start']}-{slot['end']}: {slot['participant_count']} people {slot['available_users']}")
            if slot['start'] == '08:30' and slot['end'] == '09:00':
                found_08_30 = True
                found_in_category = 'meeting_slots'
                print(f"  🎯 FOUND KEN'S 08:30 SLOT! (Category: meeting_slots)")

        # 2. Check single_availability (new category for 1-person slots)
        if 'single_availability' in data:
            single_monday = data.get('single_availability', {}).get('monday', [])
            print(f"\n👤 Monday single_availability ({len(single_monday)} slots):")

            for slot in single_monday:
                print(f"  {slot['start']}-{slot['end']}: {slot['participant_count']} people {slot['available_users']}")
                if slot['start'] == '08:30' and slot['end'] == '09:00':
                    found_08_30 = True
                    found_in_category = 'single_availability'
                    print(f"  🎯 FOUND KEN'S 08:30 SLOT! (Category: single_availability)")
        else:
            print("\n❌ No 'single_availability' field found in response")

        # 3. Check partial_availability (2+ but not all people)
        partial_monday = data.get('partial_availability', {}).get('monday', [])
        print(f"\n👥 Monday partial_availability ({len(partial_monday)} slots):")
        for slot in partial_monday:
            print(f"  {slot['start']}-{slot['end']}: {slot['participant_count']} people {slot['available_users']}")

        # 4. Check full_availability (all people)
        full_monday = data.get('full_availability', {}).get('monday', [])
        print(f"\n🏢 Monday full_availability ({len(full_monday)} slots):")
        for slot in full_monday:
            print(f"  {slot['start']}-{slot['end']}: {slot['participant_count']} people {slot['available_users']}")

        # Summary
        print(f"\n🔍 VERIFICATION RESULTS:")
        print("=" * 30)

        if found_08_30:
            print(f"✅ SUCCESS: Ken's 08:30-09:00 slot found in '{found_in_category}' category!")
            print("✅ The backend API fix is working correctly!")
            return True
        else:
            print("❌ FAILURE: Ken's 08:30-09:00 slot is still missing")
            print("💡 The backend logic may still need adjustment")

            # Show ken's raw availability for comparison
            print("\n🔍 Let's check ken's raw availability...")
            all_avail_response = requests.get("http://localhost:5000/api/availability/all", headers=headers)
            if all_avail_response.status_code == 200:
                all_users = all_avail_response.json()
                for user in all_users:
                    if user['username'] == 'ken':
                        monday_avail = user['availability'].get('monday', [])
                        print(f"📍 Ken's Monday availability: {monday_avail}")
                        for slot in monday_avail:
                            if slot['start'] == '08:30':
                                print(f"✅ Ken DOES have 08:30 availability: {slot['start']}-{slot['end']}")
                                break
                        break

            return False

    except Exception as e:
        print(f"💥 Error during test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_ken_08_30_fix()
    sys.exit(0 if success else 1)