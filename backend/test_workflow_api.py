#!/usr/bin/env python3
"""
Test the workflow API endpoints to ensure they work correctly
"""
import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def test_workflow_api():
    print("🧪 Testing Workflow API Endpoints")
    print("=" * 50)
    
    try:
        base_url = "http://localhost:8001"
        
        # Test if server is running
        try:
            response = requests.get(f"{base_url}/api/auth/", timeout=5)
            print("✅ Server is running")
        except requests.exceptions.ConnectionError:
            print("❌ Server is not running. Please start the Django server first.")
            print("   Run: python manage.py runserver")
            return
        
        # Login as employee
        employee_login_data = {
            "username": "testemployee",
            "password": "testpass123"
        }
        
        print(f"🔐 Logging in as employee...")
        employee_login_response = requests.post(f"{base_url}/api/auth/login/", json=employee_login_data)
        
        if employee_login_response.status_code != 200:
            print(f"❌ Employee login failed: {employee_login_response.status_code}")
            return
        
        employee_token = employee_login_response.json()['access']
        employee_headers = {'Authorization': f'Bearer {employee_token}'}
        print("✅ Employee logged in successfully")
        
        # Submit expense above $5000 using workflow endpoint
        expense_data = {
            "title": "API Workflow Test Expense",
            "description": "Testing workflow API for amount above $5000",
            "amount": 6000,
            "currency": "USD",
            "expense_date": "2024-01-15",
            "category": 1,  # Assuming category exists
            "priority": "high",
            "urgent": False
        }
        
        print(f"💳 Submitting expense via workflow API: ${expense_data['amount']}")
        expense_response = requests.post(
            f"{base_url}/api/auth/expenses/submit/",
            json=expense_data,
            headers=employee_headers
        )
        
        print(f"📤 Expense submission response: {expense_response.status_code}")
        if expense_response.status_code != 201:
            print(f"❌ Expense submission failed: {expense_response.text}")
            return
        
        expense_result = expense_response.json()
        expense_id = expense_result['expense']['id']
        print(f"✅ Expense created: ID {expense_id}")
        print(f"   Status: {expense_result['expense']['status']}")
        print(f"   Current Stage: {expense_result['expense']['current_stage']}")
        print(f"   Approval Rule: {expense_result['expense']['approval_rule_name']}")
        
        # Login as manager
        manager_login_data = {
            "username": "testmanager",
            "password": "testpass123"
        }
        
        print(f"\n🔐 Logging in as manager...")
        manager_login_response = requests.post(f"{base_url}/api/auth/login/", json=manager_login_data)
        
        if manager_login_response.status_code != 200:
            print(f"❌ Manager login failed: {manager_login_response.status_code}")
            return
        
        manager_token = manager_login_response.json()['access']
        manager_headers = {'Authorization': f'Bearer {manager_token}'}
        print("✅ Manager logged in successfully")
        
        # Check pending approvals for manager
        print(f"\n📋 Checking pending approvals for manager...")
        pending_response = requests.get(
            f"{base_url}/api/auth/expenses/pending/",
            headers=manager_headers
        )
        
        print(f"📤 Manager pending approvals response: {pending_response.status_code}")
        if pending_response.status_code == 200:
            pending_data = pending_response.json()
            print(f"   Found {len(pending_data)} pending approvals for manager")
            for approval in pending_data:
                print(f"   - {approval['title']}: ${approval['amount']} ({approval['current_stage']})")
        else:
            print(f"❌ Failed to get manager pending approvals: {pending_response.text}")
            return
        
        # Manager approves the expense
        print(f"\n👨‍💼 Manager approving expense {expense_id}...")
        approval_data = {
            "comment": "Manager approved the expense"
        }
        
        approve_response = requests.post(
            f"{base_url}/api/auth/expenses/{expense_id}/approve-workflow/",
            json=approval_data,
            headers=manager_headers
        )
        
        print(f"📤 Manager approval response: {approve_response.status_code}")
        if approve_response.status_code == 200:
            approval_result = approve_response.json()
            print(f"✅ Manager approval successful")
            print(f"   Status: {approval_result['status']}")
            print(f"   Current Stage: {approval_result['current_stage']}")
            print(f"   Next Approver: {approval_result['next_approver']}")
        else:
            print(f"❌ Manager approval failed: {approve_response.text}")
            return
        
        # Login as admin
        admin_login_data = {
            "username": "jwtadmin",
            "password": "testpass123"
        }
        
        print(f"\n🔐 Logging in as admin...")
        admin_login_response = requests.post(f"{base_url}/api/auth/login/", json=admin_login_data)
        
        if admin_login_response.status_code != 200:
            print(f"❌ Admin login failed: {admin_login_response.status_code}")
            return
        
        admin_token = admin_login_response.json()['access']
        admin_headers = {'Authorization': f'Bearer {admin_token}'}
        print("✅ Admin logged in successfully")
        
        # Check pending approvals for admin
        print(f"\n📋 Checking pending approvals for admin...")
        admin_pending_response = requests.get(
            f"{base_url}/api/auth/expenses/pending/",
            headers=admin_headers
        )
        
        print(f"📤 Admin pending approvals response: {admin_pending_response.status_code}")
        if admin_pending_response.status_code == 200:
            admin_pending_data = admin_pending_response.json()
            print(f"   Found {len(admin_pending_data)} pending approvals for admin")
            for approval in admin_pending_data:
                print(f"   - {approval['title']}: ${approval['amount']} ({approval['current_stage']})")
        else:
            print(f"❌ Failed to get admin pending approvals: {admin_pending_response.text}")
            return
        
        # Admin approves the expense
        print(f"\n👨‍💻 Admin approving expense {expense_id}...")
        admin_approval_data = {
            "comment": "Admin approved the expense"
        }
        
        admin_approve_response = requests.post(
            f"{base_url}/api/auth/expenses/{expense_id}/approve-workflow/",
            json=admin_approval_data,
            headers=admin_headers
        )
        
        print(f"📤 Admin approval response: {admin_approve_response.status_code}")
        if admin_approve_response.status_code == 200:
            admin_approval_result = admin_approve_response.json()
            print(f"✅ Admin approval successful")
            print(f"   Status: {admin_approval_result['status']}")
            print(f"   Current Stage: {admin_approval_result['current_stage']}")
            print(f"   Next Approver: {admin_approval_result['next_approver']}")
        else:
            print(f"❌ Admin approval failed: {admin_approve_response.text}")
            return
        
        print("\n✅ Workflow API test completed successfully!")
        print("🎉 The workflow is working correctly!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_workflow_api()
