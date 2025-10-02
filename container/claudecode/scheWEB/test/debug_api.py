#!/usr/bin/env python3

import requests
import json

# Login and get token
login_data = {
    "username": "admin",
    "password": "admin123"
}

print("🔑 Logging in...")
login_response = requests.post("http://localhost:5000/api/login", json=login_data)
token = login_response.json()["access_token"]
print("✅ Login successful")

# Get meeting compatibility data
headers = {"Authorization": f"Bearer {token}"}
print("\n📊 Getting meeting compatibility data...")

response = requests.get("http://localhost:5000/api/meeting-compatibility", headers=headers)
data = response.json()

print("\n🔍 ANALYSIS:")
print("=============")

print(f"Total users: {data['total_users']}")
print(f"Users with availability: {data['users_with_availability']}")

print("\n📅 Meeting slots by day:")
for day, slots in data.get('meeting_slots', {}).items():
    print(f"\n{day.upper()}:")
    for slot in slots:
        print(f"  {slot['start']}-{slot['end']}: {slot['participant_count']} people ({slot['available_users']})")

print("\n🕐 Looking for ken's 08:30-09:00 slot...")
monday_slots = data.get('meeting_slots', {}).get('monday', [])
ken_0830_found = any(
    slot['start'] == '08:30' and slot['end'] == '09:00'
    for slot in monday_slots
)

print(f"Ken's 08:30-09:00 in meeting_slots: {'✅ Found' if ken_0830_found else '❌ NOT Found'}")

# Also check all availability to see raw data
print("\n📋 Getting all availability...")
all_avail_response = requests.get("http://localhost:5000/api/availability/all", headers=headers)
all_users = all_avail_response.json()

print(f"\nFound {len(all_users)} users:")
for user in all_users:
    if user['username'] == 'ken':
        print(f"📍 KEN's data: {json.dumps(user['availability'], indent=2)}")

        # Check if ken has monday 08:30 slot
        monday_avail = user['availability'].get('monday', [])
        has_0830 = any(
            slot['start'] == '08:30' for slot in monday_avail
        )
        print(f"Ken has 08:30 monday slot: {'✅ Yes' if has_0830 else '❌ No'}")

print("\n🎯 CONCLUSION:")
print("==============")
if ken_0830_found:
    print("✅ Ken's 08:30-09:00 slot is included in meeting compatibility")
else:
    print("❌ Ken's 08:30-09:00 slot is MISSING from meeting compatibility")
    print("💡 This confirms the bug: 1-person slots are excluded from meeting_slots!")