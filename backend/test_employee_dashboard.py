#!/usr/bin/env python3
"""
Test script to verify employee dashboard functionality
"""
import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def test_employee_dashboard():
    print("🧪 Testing Employee Dashboard API")
    print("=" * 50)
    
    try:
        base_url = "http://localhost:8000"
        
        # Test if server is running
        try:
            response = requests.get(f"{base_url}/api/auth/", timeout=5)
            print("✅ Server is running")
        except requests.exceptions.ConnectionError:
            print("❌ Server is not running. Please start the Django server first.")
            print("   Run: python manage.py runserver")
            return
        
        # Login as employee
        login_data = {
            "username": "testemployee",
            "password": "testpass123"
        }
        
        print(f"🔐 Logging in as employee...")
        login_response = requests.post(f"{base_url}/api/auth/login/", json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return
        
        login_data = login_response.json()
        access_token = login_data['access']
        headers = {'Authorization': f'Bearer {access_token}'}
        
        print("✅ Employee logged in successfully")
        
        # Test employee dashboard endpoint
        print(f"\n📊 Testing employee dashboard endpoint...")
        dashboard_response = requests.get(
            f"{base_url}/api/auth/employee-dashboard/",
            headers=headers
        )
        
        print(f"📤 Dashboard response: {dashboard_response.status_code}")
        if dashboard_response.status_code == 200:
            dashboard_data = dashboard_response.json()
            print("✅ Dashboard data retrieved successfully")
            print(f"   Total Submitted: ${dashboard_data.get('total_submitted', 0)}")
            print(f"   Pending Amount: ${dashboard_data.get('pending_amount', 0)}")
            print(f"   Approved Amount: ${dashboard_data.get('approved_amount', 0)}")
            print(f"   Rejected Amount: ${dashboard_data.get('rejected_amount', 0)}")
            print(f"   Recent Expenses: {len(dashboard_data.get('recent_expenses', []))}")
            print(f"   Total Expenses: {dashboard_data.get('total_expenses', 0)}")
        else:
            print(f"❌ Dashboard request failed: {dashboard_response.text}")
        
        # Test my expenses endpoint
        print(f"\n📋 Testing my expenses endpoint...")
        expenses_response = requests.get(
            f"{base_url}/api/auth/my-expenses/",
            headers=headers
        )
        
        print(f"📤 My expenses response: {expenses_response.status_code}")
        if expenses_response.status_code == 200:
            expenses_data = expenses_response.json()
            print(f"✅ My expenses retrieved: {len(expenses_data)} expenses")
            for expense in expenses_data[:3]:  # Show first 3
                print(f"   - {expense.get('title', 'N/A')}: ${expense.get('amount', 0)} ({expense.get('status', 'N/A')})")
        else:
            print(f"❌ My expenses request failed: {expenses_response.text}")
        
        print("\n✅ Employee dashboard test completed!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_employee_dashboard()
