#!/usr/bin/env python
"""
Fresh registration test to verify the company registration endpoint is working.
"""

import requests
import json
import time

def test_fresh_registration():
    """Test company registration with fresh data"""
    print("🚀 Testing Fresh Company Registration...")
    
    # Use timestamp to ensure unique data
    timestamp = str(int(time.time()))
    
    registration_data = {
        "username": f"admin{timestamp}",
        "email": f"admin{timestamp}@testcompany.com",
        "first_name": "Test",
        "last_name": "Admin",
        "password": "testpassword123",
        "password_confirm": "testpassword123",
        "phone": "+1234567890",
        "role": "admin",
        "company_data": {
            "name": f"Test Company {timestamp}",
            "address": f"123 Test Street {timestamp}, Test City, TC 12345",
            "phone": "+1234567890",
            "email": f"info{timestamp}@testcompany.com",
            "website": f"https://testcompany{timestamp}.com",
            "industry": "technology",
            "size": "11-50",
            "description": f"A test company created at {timestamp}"
        }
    }
    
    try:
        response = requests.post("http://localhost:8000/api/auth/register/company/", json=registration_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ Company registration successful!")
            data = response.json()
            print(f"User: {data['user']['first_name']} {data['user']['last_name']}")
            print(f"Company: {data['user']['company']['name']}")
            print(f"Access Token: {data['access'][:20]}...")
            print(f"Refresh Token: {data['refresh'][:20]}...")
            return True
        else:
            print("❌ Company registration failed!")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure Django is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    success = test_fresh_registration()
    print("=" * 60)
    if success:
        print("✅ Backend is working correctly!")
    else:
        print("❌ Backend has issues!")
