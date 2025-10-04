#!/usr/bin/env python3
"""
Test script to simulate what the frontend sends when creating a user
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000/api"
AUTH_URL = f"{BASE_URL}/auth"

def test_frontend_user_creation():
    """Test user creation with data that frontend might send"""
    print("🧪 Testing Frontend User Creation")
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
    
    # Step 2: Create a user set
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
    
    # Step 3: Test user creation with data that might cause 400 error
    print("\n3️⃣ Testing user creation with various data formats...")
    
    # Test cases that might cause 400 errors
    test_cases = [
        {
            "name": "Empty set_id",
            "data": {
                "username": f"employee1_{timestamp}",
                "email": f"employee1_{timestamp}@test.com",
                "first_name": "Employee1",
                "last_name": "User",
                "password": "employeepass123",
                "role": "employee",
                "set_id": ""
            }
        },
        {
            "name": "Invalid set_id",
            "data": {
                "username": f"employee2_{timestamp}",
                "email": f"employee2_{timestamp}@test.com",
                "first_name": "Employee2",
                "last_name": "User",
                "password": "employeepass123",
                "role": "employee",
                "set_id": 99999
            }
        },
        {
            "name": "Missing required fields",
            "data": {
                "username": f"employee3_{timestamp}",
                "email": f"employee3_{timestamp}@test.com",
                "password": "employeepass123",
                "role": "employee",
                "set_id": set_id
            }
        },
        {
            "name": "Valid data",
            "data": {
                "username": f"employee4_{timestamp}",
                "email": f"employee4_{timestamp}@test.com",
                "first_name": "Employee4",
                "last_name": "User",
                "password": "employeepass123",
                "role": "employee",
                "set_id": set_id
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n   Test {i+1} - {test_case['name']}:")
        print(f"   Data: {json.dumps(test_case['data'], indent=2)}")
        
        try:
            response = requests.post(
                f"{AUTH_URL}/users/",
                json=test_case['data'],
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
    test_frontend_user_creation()
