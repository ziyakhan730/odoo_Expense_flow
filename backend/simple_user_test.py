#!/usr/bin/env python3
"""
Simple test to debug user creation
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000/api"
AUTH_URL = f"{BASE_URL}/auth"

def simple_user_test():
    """Simple test for user creation"""
    print("🧪 Simple User Creation Test")
    print("=" * 40)
    
    timestamp = str(int(time.time()))
    
    # Step 1: Register a company
    print("\n1️⃣ Registering company...")
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
            print("✅ Company registered successfully")
        else:
            print(f"❌ Company registration failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return
    except Exception as e:
        print(f"❌ Company registration error: {e}")
        return
    
    # Step 2: Create a user
    print("\n2️⃣ Creating a user...")
    user_data = {
        "username": f"testuser_{timestamp}",
        "email": f"testuser_{timestamp}@test.com",
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
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 201:
            user_response = response.json()
            print(f"\n✅ User created successfully!")
            print(f"   User ID: {user_response.get('id', 'NOT FOUND')}")
            print(f"   Available fields: {list(user_response.keys())}")
            
            # Check if we can access the id
            if 'id' in user_response:
                print(f"   ✅ ID field found: {user_response['id']}")
            else:
                print(f"   ❌ ID field missing!")
                print(f"   Full response: {json.dumps(user_response, indent=2)}")
        else:
            print(f"❌ User creation failed")
            
    except Exception as e:
        print(f"❌ User creation error: {e}")

if __name__ == "__main__":
    simple_user_test()
