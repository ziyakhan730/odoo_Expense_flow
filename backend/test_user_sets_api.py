#!/usr/bin/env python3
"""
Test script to verify user sets API and see what data is returned
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000/api"
AUTH_URL = f"{BASE_URL}/auth"

def test_user_sets_api():
    """Test user sets API to see what data is returned"""
    print("🧪 Testing User Sets API")
    print("=" * 40)
    
    timestamp = str(int(time.time()))
    
    # Step 1: Register a company and get admin token
    print("\n1️⃣ Setting up admin user...")
    company_data = {
        "username": f"admin_{timestamp}",
        "email": f"admin_{timestamp}@test.com",
        "first_name": "Admin",
        "last_name": "User",
        "password": "adminpass123",
        "password_confirm": "adminpass123",
        "phone": "+1234567890",
        "role": "admin",
        "company_data": {
            "name": f"Test Company {timestamp}",
            "address": "123 Test St",
            "phone": "+1234567890",
            "email": f"info_{timestamp}@test.com",
            "industry": "Technology",
            "size": "11-50"
        }
    }
    
    try:
        response = requests.post(f"{AUTH_URL}/register/company/", json=company_data)
        if response.status_code == 201:
            admin_data = response.json()
            access_token = admin_data['access']
            print("✅ Admin user created successfully")
        else:
            print(f"❌ Admin creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return
    except Exception as e:
        print(f"❌ Admin creation error: {e}")
        return
    
    # Step 2: Create some user sets
    print("\n2️⃣ Creating user sets...")
    sets_to_create = [
        "Development Team",
        "Marketing Team", 
        "Sales Team"
    ]
    
    created_sets = []
    for set_name in sets_to_create:
        try:
            response = requests.post(
                f"{AUTH_URL}/sets/",
                json={"name": set_name},
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 201:
                set_data = response.json()
                created_sets.append(set_data)
                print(f"✅ Created set: {set_data['name']} (ID: {set_data['id']})")
            else:
                print(f"❌ Failed to create set '{set_name}': {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error creating set '{set_name}': {e}")
    
    # Step 3: Test getting user sets (what frontend will receive)
    print("\n3️⃣ Testing GET /auth/sets/ (what frontend receives)...")
    try:
        response = requests.get(
            f"{AUTH_URL}/sets/",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            sets_data = response.json()
            print(f"✅ Retrieved {len(sets_data)} user sets")
            print(f"   Raw response: {json.dumps(sets_data, indent=2)}")
            
            for i, set_info in enumerate(sets_data):
                print(f"\n   Set {i+1}:")
                print(f"     ID: {set_info.get('id')}")
                print(f"     Name: {set_info.get('name')}")
                print(f"     Manager: {set_info.get('manager')}")
                print(f"     Manager Name: {set_info.get('manager_name')}")
                print(f"     Manager Email: {set_info.get('manager_email')}")
                print(f"     Employees Count: {set_info.get('employees_count')}")
                print(f"     Employees: {set_info.get('employees')}")
                print(f"     Created At: {set_info.get('created_at')}")
        else:
            print(f"❌ Failed to get user sets: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Get user sets error: {e}")

if __name__ == "__main__":
    test_user_sets_api()
