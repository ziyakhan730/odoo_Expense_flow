#!/usr/bin/env python3
"""
Test script to verify user set creation works
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000/api"
AUTH_URL = f"{BASE_URL}/auth"

def test_set_creation():
    """Test user set creation without manager"""
    print("🧪 Testing User Set Creation")
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
    
    # Step 2: Create a user set without manager
    print("\n2️⃣ Creating user set without manager...")
    set_data = {
        "name": f"Test Set {timestamp}"
    }
    
    try:
        response = requests.post(
            f"{AUTH_URL}/sets/",
            json=set_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 201:
            set_response = response.json()
            print(f"\n✅ User set created successfully!")
            print(f"   Set ID: {set_response.get('id', 'NOT FOUND')}")
            print(f"   Set Name: {set_response.get('name', 'NOT FOUND')}")
            print(f"   Available fields: {list(set_response.keys())}")
        else:
            print(f"❌ User set creation failed")
            
    except Exception as e:
        print(f"❌ User set creation error: {e}")

if __name__ == "__main__":
    test_set_creation()
