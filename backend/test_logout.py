#!/usr/bin/env python
"""
Test the logout functionality to ensure it works correctly.
"""

import requests
import json

def test_logout():
    """Test logout functionality"""
    print("🚪 Testing Logout Functionality...")
    
    # First, login to get tokens
    login_data = {
        "email": "test@testcompany.com",
        "password": "testpassword123"
    }
    
    try:
        # Login first
        login_response = requests.post("http://localhost:8000/api/auth/login/", json=login_data)
        print(f"Login Status Code: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print("❌ Login failed - cannot test logout")
            return False
        
        login_data = login_response.json()
        access_token = login_data['access']
        refresh_token = login_data['refresh']
        
        print("✅ Login successful - got tokens")
        print(f"Access Token: {access_token[:20]}...")
        print(f"Refresh Token: {refresh_token[:20]}...")
        
        # Test logout
        logout_data = {
            "refresh": refresh_token
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        logout_response = requests.post("http://localhost:8000/api/auth/logout/", json=logout_data, headers=headers)
        print(f"Logout Status Code: {logout_response.status_code}")
        
        if logout_response.status_code == 200:
            print("✅ Logout successful!")
            logout_result = logout_response.json()
            print(f"Message: {logout_result.get('message', 'No message')}")
            
            # Test that the token is now blacklisted
            print("\n🔒 Testing token blacklisting...")
            test_response = requests.get("http://localhost:8000/api/auth/profile/", headers=headers)
            print(f"Profile Access Status Code: {test_response.status_code}")
            
            if test_response.status_code == 401:
                print("✅ Token successfully blacklisted!")
                return True
            else:
                print("❌ Token not properly blacklisted")
                return False
        else:
            print("❌ Logout failed!")
            print(f"Response: {logout_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Testing Logout Functionality")
    print("=" * 60)
    
    success = test_logout()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Logout functionality is working correctly!")
        print("📋 Logout Test Results:")
        print("  ✅ Login successful")
        print("  ✅ Logout API call successful")
        print("  ✅ Token blacklisting working")
        print("  ✅ Protected endpoints properly secured")
    else:
        print("❌ Logout functionality has issues!")
    print("=" * 60)
