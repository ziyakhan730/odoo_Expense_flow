#!/usr/bin/env python3
"""
Debug script to test user creation API response
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api"
AUTH_URL = f"{BASE_URL}/auth"

def debug_user_creation():
    """Debug user creation API response"""
    print("🔍 Debugging User Creation API Response")
    print("=" * 50)
    
    # First, get an access token by logging in as admin
    login_data = {
        "email": "admin@testcompany.com",  # Use existing admin
        "password": "adminpass123"
    }
    
    try:
        response = requests.post(f"{AUTH_URL}/login/", json=login_data)
        if response.status_code == 200:
            data = response.json()
            access_token = data['access']
            print(f"✅ Login successful, token: {access_token[:20]}...")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Now try to create a user
    user_data = {
        "username": "test_user_debug",
        "email": "test_debug@testcompany.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "testpass123",
        "role": "manager",
        "phone": "+1234567890"
    }
    
    try:
        response = requests.post(
            f"{AUTH_URL}/users/",
            json=user_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        print(f"\n📊 User Creation Response:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        print(f"   Response Body: {response.text}")
        
        if response.status_code == 201:
            user_data = response.json()
            print(f"\n✅ User created successfully!")
            print(f"   Full response data: {json.dumps(user_data, indent=2)}")
            print(f"   User ID: {user_data.get('id', 'NOT FOUND')}")
            print(f"   Available fields: {list(user_data.keys())}")
        else:
            print(f"❌ User creation failed")
            
    except Exception as e:
        print(f"❌ User creation error: {e}")

if __name__ == "__main__":
    debug_user_creation()
