#!/usr/bin/env python3
"""
Debug script to test user creation and see what's causing the 400 error
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000/api"
AUTH_URL = f"{BASE_URL}/auth"

def debug_user_creation():
    """Debug user creation to see what's causing 400 error"""
    print("🔍 Debugging User Creation 400 Error")
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
    
    # Step 2: Create a user set first
    print("\n2️⃣ Creating a user set...")
    try:
        set_response = requests.post(
            f"{AUTH_URL}/sets/",
            json={"name": f"Test Set {timestamp}"},
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )
        
        if set_response.status_code == 201:
            set_data = set_response.json()
            set_id = set_data['id']
            print(f"✅ User set created: {set_data['name']} (ID: {set_id})")
        else:
            print(f"❌ Set creation failed: {set_response.status_code}")
            print(f"   Error: {set_response.text}")
            return
    except Exception as e:
        print(f"❌ Set creation error: {e}")
        return
    
    # Step 3: Test user creation with different data formats
    print("\n3️⃣ Testing user creation...")
    
    # Test 1: Minimal user data (what frontend might send)
    user_data_1 = {
        "username": f"employee_{timestamp}",
        "email": f"employee_{timestamp}@test.com",
        "first_name": "Employee",
        "last_name": "User",
        "password": "employeepass123",
        "role": "employee",
        "set_id": set_id
    }
    
    print(f"\n   Test 1 - Minimal data:")
    print(f"   Data: {json.dumps(user_data_1, indent=2)}")
    
    try:
        response = requests.post(
            f"{AUTH_URL}/users/",
            json=user_data_1,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ User created successfully!")
        else:
            print("❌ User creation failed")
            try:
                error_data = response.json()
                print(f"   Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Raw error: {response.text}")
                
    except Exception as e:
        print(f"❌ User creation error: {e}")
    
    # Test 2: User data without set_id
    print(f"\n   Test 2 - Without set_id:")
    user_data_2 = {
        "username": f"employee2_{timestamp}",
        "email": f"employee2_{timestamp}@test.com",
        "first_name": "Employee2",
        "last_name": "User",
        "password": "employeepass123",
        "role": "employee"
    }
    
    print(f"   Data: {json.dumps(user_data_2, indent=2)}")
    
    try:
        response = requests.post(
            f"{AUTH_URL}/users/",
            json=user_data_2,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ User created successfully!")
        else:
            print("❌ User creation failed")
            try:
                error_data = response.json()
                print(f"   Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Raw error: {response.text}")
                
    except Exception as e:
        print(f"❌ User creation error: {e}")

if __name__ == "__main__":
    debug_user_creation()
