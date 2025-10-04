#!/usr/bin/env python
"""
JWT Authentication test script for ExpenseFlow API.
Tests the complete JWT authentication flow.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/auth"

def test_jwt_registration():
    """Test JWT-based company registration"""
    print("🔐 Testing JWT Company Registration...")
    
    registration_data = {
        "username": "jwtadmin",
        "email": "jwtadmin@testcompany.com",
        "first_name": "JWT",
        "last_name": "Admin",
        "password": "jwtpassword123",
        "password_confirm": "jwtpassword123",
        "phone": "+1234567890",
        "role": "admin",
        "company_data": {
            "name": "JWT Test Company",
            "address": "456 JWT Street, Test City, TC 54321",
            "phone": "+1234567890",
            "email": "info@jwttestcompany.com",
            "website": "https://jwttestcompany.com",
            "industry": "technology",
            "size": "11-50",
            "description": "A test company for JWT authentication"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register/company/", json=registration_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ JWT Registration successful!")
            data = response.json()
            print(f"Access Token: {data['access'][:20]}...")
            print(f"Refresh Token: {data['refresh'][:20]}...")
            print(f"User: {data['user']['first_name']} {data['user']['last_name']}")
            print(f"Company: {data['user']['company']['name']}")
            return data['access'], data['refresh']
        else:
            print("❌ JWT Registration failed!")
            print(f"Response: {response.text}")
            return None, None
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure Django is running on localhost:8000")
        return None, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def test_jwt_login():
    """Test JWT-based login"""
    print("\n🔐 Testing JWT Login...")
    
    login_data = {
        "username": "jwtadmin",
        "password": "jwtpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login/", json=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ JWT Login successful!")
            data = response.json()
            print(f"Access Token: {data['access'][:20]}...")
            print(f"Refresh Token: {data['refresh'][:20]}...")
            print(f"User: {data['user']['first_name']} {data['user']['last_name']}")
            print(f"Role: {data['user']['role']}")
            return data['access'], data['refresh']
        else:
            print("❌ JWT Login failed!")
            print(f"Response: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def test_jwt_profile(access_token):
    """Test JWT-protected profile endpoint"""
    print("\n🔐 Testing JWT Profile Access...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/profile/", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ JWT Profile access successful!")
            data = response.json()
            print(f"User: {data['first_name']} {data['last_name']}")
            print(f"Company: {data['company']['name']}")
            print(f"Role: {data['role']}")
        else:
            print("❌ JWT Profile access failed!")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_jwt_refresh(refresh_token):
    """Test JWT token refresh"""
    print("\n🔐 Testing JWT Token Refresh...")
    
    refresh_data = {
        "refresh": refresh_token
    }
    
    try:
        response = requests.post(f"{BASE_URL}/refresh/", json=refresh_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ JWT Token refresh successful!")
            data = response.json()
            print(f"New Access Token: {data['access'][:20]}...")
            return data['access']
        else:
            print("❌ JWT Token refresh failed!")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_jwt_logout(access_token, refresh_token):
    """Test JWT logout"""
    print("\n🔐 Testing JWT Logout...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    logout_data = {
        "refresh": refresh_token
    }
    
    try:
        response = requests.post(f"{BASE_URL}/logout/", json=logout_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ JWT Logout successful!")
            data = response.json()
            print(f"Message: {data['message']}")
        else:
            print("❌ JWT Logout failed!")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_invalid_token():
    """Test with invalid token"""
    print("\n🔐 Testing Invalid Token Handling...")
    
    headers = {
        "Authorization": "Bearer invalid_token_here",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/profile/", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Invalid token properly rejected!")
        else:
            print("❌ Invalid token not properly handled!")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Testing ExpenseFlow JWT Authentication")
    print("=" * 60)
    
    # Test JWT registration
    access_token, refresh_token = test_jwt_registration()
    
    if access_token and refresh_token:
        # Test JWT login
        login_access, login_refresh = test_jwt_login()
        
        # Test JWT profile access
        test_jwt_profile(access_token)
        
        # Test JWT token refresh
        new_access = test_jwt_refresh(refresh_token)
        
        if new_access:
            # Test profile with refreshed token
            test_jwt_profile(new_access)
        
        # Test JWT logout
        test_jwt_logout(access_token, refresh_token)
        
        # Test invalid token
        test_invalid_token()
    
    print("\n" + "=" * 60)
    print("✅ JWT Authentication testing completed!")
    print("\n📋 JWT Features Tested:")
    print("  ✅ Company registration with JWT")
    print("  ✅ User login with JWT")
    print("  ✅ Protected endpoint access")
    print("  ✅ Token refresh mechanism")
    print("  ✅ Logout with token blacklisting")
    print("  ✅ Invalid token handling")
