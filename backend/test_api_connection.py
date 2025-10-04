#!/usr/bin/env python3
"""
Test script to verify API connection and user management endpoints
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api"
AUTH_URL = f"{BASE_URL}/auth"

def test_api_connection():
    """Test API connection and endpoints"""
    print("🔍 Testing API Connection")
    print("=" * 40)
    
    # Test 1: Check if server is running
    print("\n1️⃣ Testing server connection...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Server is running (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running! Please start the Django server with: python manage.py runserver")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    # Test 2: Check auth endpoints
    print("\n2️⃣ Testing auth endpoints...")
    try:
        # Test login endpoint
        response = requests.post(f"{AUTH_URL}/login/", json={"email": "test", "password": "test"})
        print(f"✅ Login endpoint accessible (Status: {response.status_code})")
        
        # Test user sets endpoint (should require auth)
        response = requests.get(f"{AUTH_URL}/sets/")
        print(f"✅ User sets endpoint accessible (Status: {response.status_code})")
        
        # Test users endpoint (should require auth)
        response = requests.get(f"{AUTH_URL}/users/")
        print(f"✅ Users endpoint accessible (Status: {response.status_code})")
        
    except Exception as e:
        print(f"❌ Auth endpoints error: {e}")
        return False
    
    print("\n✅ API connection test completed successfully!")
    print("💡 If you're still seeing errors in the frontend, check:")
    print("   1. Make sure you're logged in as an admin")
    print("   2. Check browser console for CORS errors")
    print("   3. Verify JWT tokens are being sent correctly")
    
    return True

if __name__ == "__main__":
    test_api_connection()
