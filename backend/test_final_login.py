#!/usr/bin/env python
"""
Test the final login functionality with the test user.
"""

import requests
import json

def test_email_login():
    """Test login with email"""
    print("🔐 Testing Email Login...")
    
    login_data = {
        "email": "test@testcompany.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/auth/login/", json=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Email login successful!")
            data = response.json()
            print(f"User: {data['user']['first_name']} {data['user']['last_name']}")
            print(f"Email: {data['user']['email']}")
            print(f"Role: {data['user']['role']}")
            print(f"Company: {data['user']['company']['name']}")
            print(f"Access Token: {data['access'][:20]}...")
            return True
        else:
            print("❌ Email login failed!")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_username_login():
    """Test login with username"""
    print("\n🔐 Testing Username Login...")
    
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/auth/login/", json=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Username login successful!")
            data = response.json()
            print(f"User: {data['user']['first_name']} {data['user']['last_name']}")
            print(f"Username: {data['user']['username']}")
            print(f"Role: {data['user']['role']}")
            print(f"Company: {data['user']['company']['name']}")
            return True
        else:
            print("❌ Username login failed!")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Testing Final Login Authentication")
    print("=" * 60)
    
    email_success = test_email_login()
    username_success = test_username_login()
    
    print("\n" + "=" * 60)
    if email_success and username_success:
        print("✅ Both login methods working!")
        print("📋 Login Test Results:")
        print("  ✅ Email + Password: Working")
        print("  ✅ Username + Password: Working")
        print("\n🎉 Frontend login should now work!")
    elif email_success or username_success:
        print("⚠️  Partial success - one login method working")
    else:
        print("❌ Login still not working - check backend logs")
    print("=" * 60)
