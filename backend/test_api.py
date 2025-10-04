#!/usr/bin/env python
"""
Simple test script to verify the API endpoints are working correctly.
Run this after starting the Django server.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/auth"

def test_company_registration():
    """Test the company registration endpoint"""
    print("Testing company registration...")
    
    registration_data = {
        "username": "testadmin",
        "email": "admin@testcompany.com",
        "first_name": "Test",
        "last_name": "Admin",
        "password": "testpassword123",
        "password_confirm": "testpassword123",
        "phone": "+1234567890",
        "role": "admin",
        "company_data": {
            "name": "Test Company Inc",
            "address": "123 Test Street, Test City, TC 12345",
            "phone": "+1234567890",
            "email": "info@testcompany.com",
            "website": "https://testcompany.com",
            "industry": "technology",
            "size": "11-50",
            "description": "A test company for demonstration purposes"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register/company/", json=registration_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ Company registration successful!")
            data = response.json()
            print(f"User ID: {data['user']['id']}")
            print(f"Company: {data['user']['company']['name']}")
            print(f"Token: {data['token'][:20]}...")
            return data['token']
        else:
            print("❌ Company registration failed!")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure Django is running on localhost:8000")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_login():
    """Test the login endpoint"""
    print("\nTesting login...")
    
    login_data = {
        "username": "admin@testcompany.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login/", json=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            data = response.json()
            print(f"User: {data['user']['first_name']} {data['user']['last_name']}")
            print(f"Role: {data['user']['role']}")
            return data['token']
        else:
            print("❌ Login failed!")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_profile(token):
    """Test the profile endpoint"""
    print("\nTesting profile...")
    
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/profile/", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Profile retrieval successful!")
            data = response.json()
            print(f"User: {data['first_name']} {data['last_name']}")
            print(f"Company: {data['company']['name']}")
        else:
            print("❌ Profile retrieval failed!")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Testing ExpenseFlow API Endpoints")
    print("=" * 50)
    
    # Test company registration
    token = test_company_registration()
    
    if token:
        # Test login
        login_token = test_login()
        
        # Test profile
        test_profile(token)
    
    print("\n" + "=" * 50)
    print("✅ API testing completed!")
