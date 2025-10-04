#!/usr/bin/env python3
"""
Test script for expense approval functionality
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api/auth"
TIMESTAMP = datetime.now().strftime('%Y%m%d%H%M%S')
COMPANY_NAME = f"Test Company {TIMESTAMP}"
ADMIN_EMAIL = f"admin_{TIMESTAMP}@test.com"
MANAGER_EMAIL = f"manager_{TIMESTAMP}@test.com"
EMPLOYEE_EMAIL = f"employee_{TIMESTAMP}@test.com"
ADMIN_USERNAME = f"admin_{TIMESTAMP}"
MANAGER_USERNAME = f"manager_{TIMESTAMP}"
EMPLOYEE_USERNAME = f"employee_{TIMESTAMP}"

def test_expense_approval_workflow():
    print("🧪 Testing Expense Approval Workflow")
    print("=" * 50)
    
    # Step 1: Register company and admin
    print("\n1. Registering company and admin...")
    company_data = {
        "company_name": COMPANY_NAME,
        "company_domain": "test.com",
        "username": ADMIN_USERNAME,
        "email": ADMIN_EMAIL,
        "password": "AdminPass123!",
        "password_confirm": "AdminPass123!",
        "first_name": "Admin",
        "last_name": "User"
    }
    
    response = requests.post(f"{BASE_URL}/register/company/", json=company_data)
    if response.status_code == 201:
        admin_data = response.json()
        admin_token = admin_data['access']
        print(f"✅ Company registered: {COMPANY_NAME}")
        print(f"✅ Admin token obtained")
    else:
        print(f"❌ Company registration failed: {response.text}")
        return False
    
    # Step 2: Create user set
    print("\n2. Creating user set...")
    set_data = {
        "name": "Test Set"
    }
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.post(f"{BASE_URL}/sets/", json=set_data, headers=headers)
    if response.status_code == 201:
        set_info = response.json()
        set_id = set_info['id']
        print(f"✅ User set created: {set_info['name']} (ID: {set_id})")
    else:
        print(f"❌ Set creation failed: {response.text}")
        return False
    
    # Step 3: Create manager
    print("\n3. Creating manager...")
    manager_data = {
        "username": MANAGER_USERNAME,
        "email": MANAGER_EMAIL,
        "password": "ManagerPass123!",
        "first_name": "Manager",
        "last_name": "User",
        "role": "manager",
        "set_id": set_id
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=manager_data, headers=headers)
    if response.status_code == 201:
        manager_info = response.json()
        print(f"✅ Manager created: {manager_info['first_name']} {manager_info['last_name']}")
    else:
        print(f"❌ Manager creation failed: {response.text}")
        return False
    
    # Step 4: Create employee
    print("\n4. Creating employee...")
    employee_data = {
        "username": EMPLOYEE_USERNAME,
        "email": EMPLOYEE_EMAIL,
        "password": "EmployeePass123!",
        "first_name": "Employee",
        "last_name": "User",
        "role": "employee",
        "set_id": set_id
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=employee_data, headers=headers)
    if response.status_code == 201:
        employee_info = response.json()
        print(f"✅ Employee created: {employee_info['first_name']} {employee_info['last_name']}")
    else:
        print(f"❌ Employee creation failed: {response.text}")
        return False
    
    # Step 5: Assign manager to set
    print("\n5. Assigning manager to set...")
    manager_id = manager_info['id']
    update_set_data = {
        "manager_id": manager_id
    }
    
    response = requests.patch(f"{BASE_URL}/sets/{set_id}/", json=update_set_data, headers=headers)
    if response.status_code == 200:
        print(f"✅ Manager assigned to set")
    else:
        print(f"❌ Manager assignment failed: {response.text}")
        return False
    
    # Step 6: Employee login and create expense
    print("\n6. Employee login and create expense...")
    employee_login_data = {
        "email": EMPLOYEE_EMAIL,
        "password": "EmployeePass123!"
    }
    
    response = requests.post(f"{BASE_URL}/login/", json=employee_login_data)
    if response.status_code == 200:
        employee_auth = response.json()
        employee_token = employee_auth['access']
        print(f"✅ Employee logged in")
    else:
        print(f"❌ Employee login failed: {response.text}")
        return False
    
    # Create expense category first
    print("\n7. Creating expense category...")
    category_data = {
        "name": "Travel",
        "description": "Travel expenses"
    }
    
    employee_headers = {"Authorization": f"Bearer {employee_token}"}
    response = requests.post(f"{BASE_URL}/expense-categories/", json=category_data, headers=employee_headers)
    if response.status_code == 201:
        category_info = response.json()
        category_id = category_info['id']
        print(f"✅ Category created: {category_info['name']}")
    else:
        print(f"❌ Category creation failed: {response.text}")
        return False
    
    # Create expense
    print("\n8. Creating expense...")
    expense_data = {
        "title": "Client Meeting Travel",
        "description": "Taxi fare to client meeting",
        "amount": 25.50,
        "currency": "USD",
        "expense_date": "2024-01-15",
        "category_id": category_id,
        "priority": "medium"
    }
    
    response = requests.post(f"{BASE_URL}/expenses/", json=expense_data, headers=employee_headers)
    if response.status_code == 201:
        expense_info = response.json()
        expense_id = expense_info['id']
        print(f"✅ Expense created: {expense_info['title']} - ${expense_info['amount']}")
        print(f"✅ Expense status: {expense_info['status']}")
    else:
        print(f"❌ Expense creation failed: {response.text}")
        return False
    
    # Step 7: Manager login and check pending approvals
    print("\n9. Manager login and check pending approvals...")
    manager_login_data = {
        "email": MANAGER_EMAIL,
        "password": "ManagerPass123!"
    }
    
    response = requests.post(f"{BASE_URL}/login/", json=manager_login_data)
    if response.status_code == 200:
        manager_auth = response.json()
        manager_token = manager_auth['access']
        print(f"✅ Manager logged in")
    else:
        print(f"❌ Manager login failed: {response.text}")
        return False
    
    # Get pending approvals
    manager_headers = {"Authorization": f"Bearer {manager_token}"}
    response = requests.get(f"{BASE_URL}/pending-approvals/", headers=manager_headers)
    if response.status_code == 200:
        pending_expenses = response.json()
        print(f"✅ Found {len(pending_expenses)} pending approvals")
        if pending_expenses:
            expense = pending_expenses[0]
            print(f"   - {expense['title']} by {expense['user_name']} - ${expense['amount']}")
    else:
        print(f"❌ Failed to get pending approvals: {response.text}")
        return False
    
    # Step 8: Manager approves expense
    print("\n10. Manager approving expense...")
    response = requests.post(f"{BASE_URL}/expenses/{expense_id}/approve/", headers=manager_headers)
    if response.status_code == 200:
        approval_result = response.json()
        print(f"✅ Expense approved: {approval_result['message']}")
        print(f"✅ New status: {approval_result['expense']['status']}")
    else:
        print(f"❌ Expense approval failed: {response.text}")
        return False
    
    # Step 9: Employee checks expense status
    print("\n11. Employee checking expense status...")
    response = requests.get(f"{BASE_URL}/my-expenses/", headers=employee_headers)
    if response.status_code == 200:
        employee_expenses = response.json()
        print(f"✅ Employee has {len(employee_expenses)} expenses")
        if employee_expenses:
            expense = employee_expenses[0]
            print(f"   - {expense['title']} - Status: {expense['status']}")
            if expense['status'] == 'approved':
                print(f"   - Approved by: {expense.get('approved_by_name', 'N/A')}")
                print(f"   - Approved at: {expense.get('approved_at', 'N/A')}")
    else:
        print(f"❌ Failed to get employee expenses: {response.text}")
        return False
    
    # Step 10: Test rejection workflow
    print("\n12. Testing rejection workflow...")
    
    # Create another expense
    expense_data_2 = {
        "title": "Personal Lunch",
        "description": "Personal lunch expense",
        "amount": 15.00,
        "currency": "USD",
        "expense_date": "2024-01-16",
        "category_id": category_id,
        "priority": "low"
    }
    
    response = requests.post(f"{BASE_URL}/expenses/", json=expense_data_2, headers=employee_headers)
    if response.status_code == 201:
        expense_info_2 = response.json()
        expense_id_2 = expense_info_2['id']
        print(f"✅ Second expense created: {expense_info_2['title']}")
    else:
        print(f"❌ Second expense creation failed: {response.text}")
        return False
    
    # Manager rejects expense
    rejection_data = {
        "rejection_reason": "Personal expenses are not reimbursable"
    }
    
    response = requests.post(f"{BASE_URL}/expenses/{expense_id_2}/reject/", json=rejection_data, headers=manager_headers)
    if response.status_code == 200:
        rejection_result = response.json()
        print(f"✅ Expense rejected: {rejection_result['message']}")
        print(f"✅ Rejection reason: {rejection_result['expense']['rejection_reason']}")
    else:
        print(f"❌ Expense rejection failed: {response.text}")
        return False
    
    print("\n🎉 Expense Approval Workflow Test Completed Successfully!")
    print("=" * 50)
    print("✅ All steps completed:")
    print("   - Company and admin registration")
    print("   - User set creation")
    print("   - Manager and employee creation")
    print("   - Manager assignment to set")
    print("   - Employee expense submission")
    print("   - Manager approval workflow")
    print("   - Employee status tracking")
    print("   - Rejection workflow")
    
    return True

if __name__ == "__main__":
    try:
        test_expense_approval_workflow()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
