#!/usr/bin/env python
"""
Test the fixed login functionality with email-based authentication.
"""

import requests
import json

def test_email_login():
    """Test login with email instead of username"""
    print("🔐 Testing Email-based Login...")
    
    # Test with an existing user from the Django admin
    login_data = {
        "email": "bcan1ca24093@itmuniversity.ac.in",
        "password": "your_password_here"  # You'll need to set the actual password
    }
    
    try:
        response = requests.post("http://localhost:8000/api/auth/login/", json=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Email-based login successful!")
            data = response.json()
            print(f"User: {data['user']['first_name']} {data['user']['last_name']}")
            print(f"Email: {data['user']['email']}")
            print(f"Role: {data['user']['role']}")
            print(f"Access Token: {data['access'][:20]}...")
            return True
        else:
            print("❌ Email-based login failed!")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_username_login():
    """Test login with username (should still work)"""
    print("\n🔐 Testing Username-based Login...")
    
    login_data = {
        "username": "admin",
        "password": "admin123"  # Default admin password
    }
    
    try:
        response = requests.post("http://localhost:8000/api/auth/login/", json=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Username-based login successful!")
            data = response.json()
            print(f"User: {data['user']['first_name']} {data['user']['last_name']}")
            print(f"Username: {data['user']['username']}")
            print(f"Role: {data['user']['role']}")
            return True
        else:
            print("❌ Username-based login failed!")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Testing Fixed Login Authentication")
    print("=" * 60)
    
    # Test username login first (should work)
    username_success = test_username_login()
    
    # Test email login (new functionality)
    email_success = test_email_login()
    
    print("\n" + "=" * 60)
    if username_success or email_success:
        print("✅ Login authentication is working!")
        print("📋 Supported login methods:")
        if username_success:
            print("  ✅ Username + Password")
        if email_success:
            print("  ✅ Email + Password")
    else:
        print("❌ Login authentication needs further fixes!")
    print("=" * 60)
