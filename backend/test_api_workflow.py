#!/usr/bin/env python3
"""
Test API workflow endpoints
"""
import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def test_api_workflow():
    print("🧪 API Workflow Test")
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
        
        # Submit expense above $6000 using the workflow endpoint
        expense_data = {
            "title": "API Test High Amount Expense",
            "description": "Testing API workflow for amount above $6000",
            "amount": 6000,
            "currency": "USD",
            "expense_date": "2024-01-15",
            "category": 1,  # Assuming category exists
            "priority": "high",
            "urgent": False
        }
        
        print(f"💳 Submitting expense via API: ${expense_data['amount']}")
        expense_response = requests.post(
            f"{base_url}/api/auth/expenses/submit/",
            json=expense_data,
            headers=headers
        )
        
        print(f"📤 Expense submission response: {expense_response.status_code}")
        if expense_response.status_code != 201:
            print(f"❌ Expense submission failed: {expense_response.text}")
            return
        
        expense_result = expense_response.json()
        print(f"✅ Expense created via API: ID {expense_result['expense']['id']}")
        print(f"   Status: {expense_result['expense']['status']}")
        print(f"   Current Stage: {expense_result['expense']['current_stage']}")
        print(f"   Approval Rule: {expense_result['expense']['approval_rule_name']}")
        
        # Check pending approvals for manager
        print(f"\n🔍 Checking pending approvals for manager...")
        manager_login_data = {
            "username": "testmanager",
            "password": "testpass123"
        }
        
        manager_login_response = requests.post(f"{base_url}/api/auth/login/", json=manager_login_data)
        if manager_login_response.status_code == 200:
            manager_token = manager_login_response.json()['access']
            manager_headers = {'Authorization': f'Bearer {manager_token}'}
            
            pending_response = requests.get(
                f"{base_url}/api/auth/expenses/pending/",
                headers=manager_headers
            )
            
            print(f"📋 Manager pending approvals response: {pending_response.status_code}")
            if pending_response.status_code == 200:
                pending_data = pending_response.json()
                print(f"   Found {len(pending_data)} pending approvals for manager")
                for approval in pending_data:
                    print(f"   - {approval['title']}: ${approval['amount']} ({approval['current_stage']})")
            else:
                print(f"❌ Failed to get manager pending approvals: {pending_response.text}")
        
        # Check pending approvals for admin
        print(f"\n🔍 Checking pending approvals for admin...")
        admin_login_data = {
            "username": "testadmin",
            "password": "testpass123"
        }
        
        admin_login_response = requests.post(f"{base_url}/api/auth/login/", json=admin_login_data)
        if admin_login_response.status_code == 200:
            admin_token = admin_login_response.json()['access']
            admin_headers = {'Authorization': f'Bearer {admin_token}'}
            
            pending_response = requests.get(
                f"{base_url}/api/auth/expenses/pending/",
                headers=admin_headers
            )
            
            print(f"📋 Admin pending approvals response: {pending_response.status_code}")
            if pending_response.status_code == 200:
                pending_data = pending_response.json()
                print(f"   Found {len(pending_data)} pending approvals for admin")
                for approval in pending_data:
                    print(f"   - {approval['title']}: ${approval['amount']} ({approval['current_stage']})")
            else:
                print(f"❌ Failed to get admin pending approvals: {pending_response.text}")
        
        print("\n✅ API workflow test completed!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_workflow()
