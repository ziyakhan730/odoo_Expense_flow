#!/usr/bin/env python3
"""
Test script to verify frontend can create user sets
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000/api"
AUTH_URL = f"{BASE_URL}/auth"

def test_frontend_set_creation():
    """Test that the API works as expected by frontend"""
    print("🧪 Testing Frontend User Set Creation")
    print("=" * 50)
    
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
    
    # Step 2: Test user set creation (as frontend would do)
    print("\n2️⃣ Testing user set creation...")
    set_data = {
        "name": "ERP Cell"  # Same as in the screenshot
    }
    
    try:
        response = requests.post(
            f"{AUTH_URL}/sets/",
            json=set_data,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        print(f"   Response Body: {response.text}")
        
        if response.status_code == 201:
            set_response = response.json()
            print(f"\n✅ User set created successfully!")
            print(f"   Set ID: {set_response.get('id')}")
            print(f"   Set Name: {set_response.get('name')}")
            print(f"   Manager: {set_response.get('manager', 'None')}")
        else:
            print(f"❌ User set creation failed")
            try:
                error_data = response.json()
                print(f"   Error details: {error_data}")
            except:
                print(f"   Raw error: {response.text}")
            
    except Exception as e:
        print(f"❌ User set creation error: {e}")
    
    # Step 3: Test getting user sets
    print("\n3️⃣ Testing get user sets...")
    try:
        response = requests.get(
            f"{AUTH_URL}/sets/",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            sets_data = response.json()
            print(f"✅ Retrieved {len(sets_data)} user sets")
            for set_info in sets_data:
                print(f"   - {set_info.get('name')} (ID: {set_info.get('id')})")
        else:
            print(f"❌ Failed to get user sets: {response.text}")
            
    except Exception as e:
        print(f"❌ Get user sets error: {e}")

if __name__ == "__main__":
    test_frontend_set_creation()
