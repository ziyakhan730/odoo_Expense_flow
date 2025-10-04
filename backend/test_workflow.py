#!/usr/bin/env python3
"""
Test script for the approval workflow engine
"""
import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api/auth"
COMPANY_NAME = f"Test Company {int(time.time())}"
ADMIN_EMAIL = f"admin{int(time.time())}@test.com"
MANAGER_EMAIL = f"manager{int(time.time())}@test.com"
EMPLOYEE_EMAIL = f"employee{int(time.time())}@test.com"

def make_request(method, url, data=None, headers=None):
    """Make HTTP request with error handling"""
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PATCH':
            response = requests.patch(url, json=data, headers=headers)
        
        print(f"{method} {url} - Status: {response.status_code}")
        if response.status_code not in [200, 201]:
            print(f"Error: {response.text}")
        return response
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def test_workflow():
    """Test the complete approval workflow"""
    print("🚀 Testing Approval Workflow Engine")
    print("=" * 50)
    
    # Step 1: Register Company and Admin
    print("\n1. Registering Company and Admin...")
    company_data = {
        "company_data": {
            "name": COMPANY_NAME,
            "email": ADMIN_EMAIL,
            "size": "51-200",
            "industry": "Technology",
            "address": "123 Business St, City, State 12345",
            "phone": "+15551234567"
        },
        "username": f"admin{int(time.time())}",
        "email": ADMIN_EMAIL,
        "first_name": "Admin",
        "last_name": "User",
        "password": "AdminPass123!",
        "password_confirm": "AdminPass123!"
    }
    
    response = make_request('POST', f"{BASE_URL}/register/company/", company_data)
    if not response or response.status_code != 201:
        print("❌ Company registration failed")
        return
    
    admin_data = response.json()
    admin_token = admin_data['access']
    admin_headers = {'Authorization': f'Bearer {admin_token}'}
    print("✅ Company and admin registered successfully")
    
    # Step 2: Setup default approval rules
    print("\n2. Setting up default approval rules...")
    response = make_request('POST', f"{BASE_URL}/approval-rules/setup-default/", headers=admin_headers)
    if response and response.status_code == 200:
        print("✅ Default approval rules created")
    else:
        print("❌ Failed to create default rules")
    
    # Step 3: Create User Set
    print("\n3. Creating User Set...")
    set_data = {"name": "Engineering Team", "description": "Software engineering team"}
    response = make_request('POST', f"{BASE_URL}/sets/", set_data, admin_headers)
    if not response or response.status_code != 201:
        print("❌ User set creation failed")
        return
    
    set_id = response.json()['id']
    print("✅ User set created successfully")
    
    # Step 4: Create Manager
    print("\n4. Creating Manager...")
    manager_data = {
        "username": f"manager{int(time.time())}",
        "email": MANAGER_EMAIL,
        "first_name": "Manager",
        "last_name": "User",
        "password": "ManagerPass123!",
        "role": "manager",
        "user_set": set_id
    }
    response = make_request('POST', f"{BASE_URL}/users/", manager_data, admin_headers)
    if not response or response.status_code != 201:
        print("❌ Manager creation failed")
        return
    
    manager_id = response.json()['id']
    print("✅ Manager created successfully")
    
    # Step 5: Create Employee
    print("\n5. Creating Employee...")
    employee_data = {
        "username": f"employee{int(time.time())}",
        "email": EMPLOYEE_EMAIL,
        "first_name": "Employee",
        "last_name": "User",
        "password": "EmployeePass123!",
        "role": "employee",
        "user_set": set_id
    }
    response = make_request('POST', f"{BASE_URL}/users/", employee_data, admin_headers)
    if not response or response.status_code != 201:
        print("❌ Employee creation failed")
        return
    
    employee_id = response.json()['id']
    print("✅ Employee created successfully")
    
    # Step 6: Login as Employee
    print("\n6. Logging in as Employee...")
    login_data = {
        "username": employee_data['username'],
        "password": "EmployeePass123!"
    }
    response = make_request('POST', f"{BASE_URL}/login/", login_data)
    if not response or response.status_code != 200:
        print("❌ Employee login failed")
        return
    
    employee_token = response.json()['access']
    employee_headers = {'Authorization': f'Bearer {employee_token}'}
    print("✅ Employee logged in successfully")
    
    # Step 7: Submit Low Amount Expense (≤ 5000)
    print("\n7. Submitting Low Amount Expense (≤ 5000)...")
    expense_data = {
        "title": "Office Supplies",
        "description": "Purchase of office supplies",
        "amount": 2500.00,
        "currency": "USD",
        "expense_date": "2024-01-15",
        "urgent": False
    }
    response = make_request('POST', f"{BASE_URL}/expenses/submit/", expense_data, employee_headers)
    if not response or response.status_code != 201:
        print("❌ Expense submission failed")
        return
    
    expense = response.json()['expense']
    expense_id = expense['id']
    print(f"✅ Low amount expense submitted - ID: {expense_id}")
    print(f"   Current Stage: {expense['current_stage']}")
    print(f"   Next Approver: {expense['next_approver']}")
    
    # Step 8: Login as Manager
    print("\n8. Logging in as Manager...")
    login_data = {
        "username": manager_data['username'],
        "password": "ManagerPass123!"
    }
    response = make_request('POST', f"{BASE_URL}/login/", login_data)
    if not response or response.status_code != 200:
        print("❌ Manager login failed")
        return
    
    manager_token = response.json()['access']
    manager_headers = {'Authorization': f'Bearer {manager_token}'}
    print("✅ Manager logged in successfully")
    
    # Step 9: Get Pending Approvals
    print("\n9. Getting Pending Approvals...")
    response = make_request('GET', f"{BASE_URL}/expenses/pending/", headers=manager_headers)
    if not response or response.status_code != 200:
        print("❌ Failed to get pending approvals")
        return
    
    pending_expenses = response.json()
    print(f"✅ Found {len(pending_expenses)} pending expenses")
    
    # Step 10: Approve Expense
    print("\n10. Approving Expense...")
    approval_data = {"comment": "Approved by manager"}
    response = make_request('POST', f"{BASE_URL}/expenses/{expense_id}/approve-workflow/", approval_data, manager_headers)
    if not response or response.status_code != 200:
        print("❌ Expense approval failed")
        return
    
    approval_result = response.json()
    print(f"✅ Expense approved - Status: {approval_result['status']}")
    print(f"   Current Stage: {approval_result['current_stage']}")
    print(f"   Next Approver: {approval_result['next_approver']}")
    
    # Step 11: Submit High Amount Expense (> 25000)
    print("\n11. Submitting High Amount Expense (> 25000)...")
    high_expense_data = {
        "title": "Software License",
        "description": "Annual software license purchase",
        "amount": 50000.00,
        "currency": "USD",
        "expense_date": "2024-01-15",
        "urgent": False
    }
    response = make_request('POST', f"{BASE_URL}/expenses/submit/", high_expense_data, employee_headers)
    if not response or response.status_code != 201:
        print("❌ High amount expense submission failed")
        return
    
    high_expense = response.json()['expense']
    high_expense_id = high_expense['id']
    print(f"✅ High amount expense submitted - ID: {high_expense_id}")
    print(f"   Current Stage: {high_expense['current_stage']}")
    print(f"   Next Approver: {high_expense['next_approver']}")
    
    # Step 12: Manager Approves High Amount
    print("\n12. Manager Approving High Amount Expense...")
    approval_data = {"comment": "Manager approval for high amount"}
    response = make_request('POST', f"{BASE_URL}/expenses/{high_expense_id}/approve-workflow/", approval_data, manager_headers)
    if not response or response.status_code != 200:
        print("❌ High amount expense approval failed")
        return
    
    approval_result = response.json()
    print(f"✅ High amount expense approved by manager - Status: {approval_result['status']}")
    print(f"   Current Stage: {approval_result['current_stage']}")
    print(f"   Next Approver: {approval_result['next_approver']}")
    
    # Step 13: Admin Approves High Amount
    print("\n13. Admin Approving High Amount Expense...")
    approval_data = {"comment": "Admin final approval for high amount"}
    response = make_request('POST', f"{BASE_URL}/expenses/{high_expense_id}/approve-workflow/", approval_data, admin_headers)
    if not response or response.status_code != 200:
        print("❌ Admin approval failed")
        return
    
    approval_result = response.json()
    print(f"✅ High amount expense approved by admin - Status: {approval_result['status']}")
    print(f"   Current Stage: {approval_result['current_stage']}")
    print(f"   Next Approver: {approval_result['next_approver']}")
    
    # Step 14: Submit Urgent Expense
    print("\n14. Submitting Urgent Expense...")
    urgent_expense_data = {
        "title": "Emergency Travel",
        "description": "Urgent business travel",
        "amount": 15000.00,
        "currency": "USD",
        "expense_date": "2024-01-15",
        "urgent": True
    }
    response = make_request('POST', f"{BASE_URL}/expenses/submit/", urgent_expense_data, employee_headers)
    if not response or response.status_code != 201:
        print("❌ Urgent expense submission failed")
        return
    
    urgent_expense = response.json()['expense']
    urgent_expense_id = urgent_expense['id']
    print(f"✅ Urgent expense submitted - ID: {urgent_expense_id}")
    print(f"   Current Stage: {urgent_expense['current_stage']}")
    print(f"   Next Approver: {urgent_expense['next_approver']}")
    print(f"   Urgent: {urgent_expense['urgent']}")
    
    # Step 15: Admin Approves Urgent Expense
    print("\n15. Admin Approving Urgent Expense...")
    approval_data = {"comment": "Admin approval for urgent expense"}
    response = make_request('POST', f"{BASE_URL}/expenses/{urgent_expense_id}/approve-workflow/", approval_data, admin_headers)
    if not response or response.status_code != 200:
        print("❌ Urgent expense approval failed")
        return
    
    approval_result = response.json()
    print(f"✅ Urgent expense approved by admin - Status: {approval_result['status']}")
    print(f"   Current Stage: {approval_result['current_stage']}")
    print(f"   Next Approver: {approval_result['next_approver']}")
    
    # Step 16: Get Expense History
    print("\n16. Getting Expense History...")
    response = make_request('GET', f"{BASE_URL}/expenses/history/", headers=admin_headers)
    if not response or response.status_code != 200:
        print("❌ Failed to get expense history")
        return
    
    history = response.json()
    print(f"✅ Found {len(history)} expenses in history")
    
    # Step 17: Test Admin Override
    print("\n17. Testing Admin Override...")
    # First submit an expense
    override_expense_data = {
        "title": "Test Override",
        "description": "Testing admin override functionality",
        "amount": 10000.00,
        "currency": "USD",
        "expense_date": "2024-01-15",
        "urgent": False
    }
    response = make_request('POST', f"{BASE_URL}/expenses/submit/", override_expense_data, employee_headers)
    if not response or response.status_code != 201:
        print("❌ Override expense submission failed")
        return
    
    override_expense_id = response.json()['expense']['id']
    
    # Admin overrides directly
    override_data = {
        "action": "approve",
        "comment": "Admin override - direct approval"
    }
    response = make_request('POST', f"{BASE_URL}/expenses/{override_expense_id}/override/", override_data, admin_headers)
    if not response or response.status_code != 200:
        print("❌ Admin override failed")
        return
    
    override_result = response.json()
    print(f"✅ Admin override successful - Status: {override_result['status']}")
    print(f"   Current Stage: {override_result['current_stage']}")
    
    print("\n🎉 Workflow Test Completed Successfully!")
    print("=" * 50)
    print("✅ All workflow features tested:")
    print("   - Company and user registration")
    print("   - Default approval rules setup")
    print("   - Low amount expense (Manager only)")
    print("   - High amount expense (Manager → Admin)")
    print("   - Urgent expense (Admin only)")
    print("   - Admin override functionality")
    print("   - Expense history tracking")

if __name__ == "__main__":
    test_workflow()
