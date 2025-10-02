#!/usr/bin/env python3

import requests
import json

def setup_ken_availability():
    """Set up ken's availability with the critical 08:30-11:00 Monday slot"""

    print("🔧 Setting up ken's availability data...")

    # Login as ken
    login_data = {"username": "ken", "password": "ken"}

    try:
        print("🔑 Logging in as ken...")
        login_response = requests.post("http://localhost:5000/api/login", json=login_data)

        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return False

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful")

        # Set ken's availability
        availability_data = {
            "availability": {
                "monday": [{"start": "08:30", "end": "11:00"}],
                "friday": [{"start": "09:00", "end": "10:00"}],
                "thursday": [
                    {"start": "09:00", "end": "10:00"},
                    {"start": "10:00", "end": "11:00"},
                    {"start": "11:00", "end": "12:00"},
                    {"start": "12:00", "end": "13:00"}
                ],
                "tuesday": [
                    {"start": "09:00", "end": "10:00"},
                    {"start": "10:00", "end": "11:00"},
                    {"start": "11:00", "end": "12:00"},
                    {"start": "12:00", "end": "13:00"}
                ]
            }
        }

        print("📊 Setting ken's availability (including 08:30-11:00 Monday)...")
        response = requests.post("http://localhost:5000/api/availability",
                               headers=headers,
                               json=availability_data)

        if response.status_code == 200:
            print("✅ Ken's availability set successfully!")

            # Verify by checking meeting-compatibility
            print("🔍 Verifying meeting-compatibility response...")
            compat_response = requests.get("http://localhost:5000/api/meeting-compatibility", headers=headers)

            if compat_response.status_code == 200:
                data = compat_response.json()

                if 'single_availability' in data:
                    monday_single = data.get('single_availability', {}).get('monday', [])
                    print(f"📅 Monday single_availability slots: {len(monday_single)}")

                    for slot in monday_single:
                        if slot['start'] == '08:30':
                            print(f"🎯 SUCCESS: Found ken's 08:30 slot: {slot}")
                            return True

                    print("❌ Ken's 08:30 slot not found in single_availability")
                    print(f"Available Monday slots: {monday_single}")
                else:
                    print("❌ No single_availability field in response")

            else:
                print(f"❌ Meeting compatibility check failed: {compat_response.text}")

        else:
            print(f"❌ Failed to set availability: {response.text}")

    except Exception as e:
        print(f"💥 Error: {str(e)}")

    return False

if __name__ == "__main__":
    setup_ken_availability()