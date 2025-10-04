#!/usr/bin/env python
"""
Test CORS configuration to ensure frontend can access the backend.
"""

import requests

def test_cors():
    """Test CORS headers"""
    print("🌐 Testing CORS Configuration...")
    
    try:
        # Test OPTIONS request (preflight)
        response = requests.options(
            "http://localhost:8000/api/auth/register/company/",
            headers={
                "Origin": "http://localhost:8080",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"CORS Headers:")
        for header, value in response.headers.items():
            if 'access-control' in header.lower():
                print(f"  {header}: {value}")
        
        if response.status_code == 200:
            print("✅ CORS preflight request successful!")
            return True
        else:
            print("❌ CORS preflight request failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing CORS: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    test_cors()
    print("=" * 50)
