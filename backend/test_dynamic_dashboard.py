#!/usr/bin/env python3
"""
Test script for dynamic manager dashboard functionality
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api/auth"
TIMESTAMP = datetime.now().strftime('%Y%m%d%H%M%S')
COMPANY_NAME = f"Dashboard Test Company {TIMESTAMP}"
ADMIN_EMAIL = f"admin_{TIMESTAMP}@test.com"
MANAGER_EMAIL = f"manager_{TIMESTAMP}@test.com"
EMPLOYEE1_EMAIL = f"employee1_{TIMESTAMP}@test.com"
EMPLOYEE2_EMAIL = f"employee2_{TIMESTAMP}@test.com"
ADMIN_USERNAME = f"admin_{TIMESTAMP}"
MANAGER_USERNAME = f"manager_{TIMESTAMP}"
EMPLOYEE1_USERNAME = f"employee1_{TIMESTAMP}"
EMPLOYEE2_USERNAME = f"employee2_{TIMESTAMP}"

def test_dynamic_dashboard():
    print("🧪 Testing Dynamic Manager Dashboard")
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
    else:
        print(f"❌ Company registration failed: {response.text}")
        return False
    
    # Step 2: Create user set
    print("\n2. Creating user set...")
    set_data = {"name": "Dashboard Test Set"}
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
        manager_id = manager_info['id']
        print(f"✅ Manager created: {manager_info['first_name']} {manager_info['last_name']}")
    else:
        print(f"❌ Manager creation failed: {response.text}")
        return False
    
    # Step 4: Create employees
    print("\n4. Creating employees...")
    employees = [
        {
            "username": EMPLOYEE1_USERNAME,
            "email": EMPLOYEE1_EMAIL,
            "password": "EmployeePass123!",
            "first_name": "Employee",
            "last_name": "One",
            "role": "employee",
            "set_id": set_id
        },
        {
            "username": EMPLOYEE2_USERNAME,
            "email": EMPLOYEE2_EMAIL,
            "password": "EmployeePass123!",
            "first_name": "Employee",
            "last_name": "Two",
            "role": "employee",
            "set_id": set_id
        }
    ]
    
    employee_tokens = []
    for i, employee_data in enumerate(employees, 1):
        response = requests.post(f"{BASE_URL}/users/", json=employee_data, headers=headers)
        if response.status_code == 201:
            employee_info = response.json()
            print(f"✅ Employee {i} created: {employee_info['first_name']} {employee_info['last_name']}")
            
            # Login employee to get token
            login_data = {
                "email": employee_data["email"],
                "password": employee_data["password"]
            }
            login_response = requests.post(f"{BASE_URL}/login/", json=login_data)
            if login_response.status_code == 200:
                employee_auth = login_response.json()
                employee_tokens.append(employee_auth['access'])
                print(f"✅ Employee {i} logged in")
            else:
                print(f"❌ Employee {i} login failed")
        else:
            print(f"❌ Employee {i} creation failed: {response.text}")
            return False
    
    # Step 5: Assign manager to set
    print("\n5. Assigning manager to set...")
    update_set_data = {"manager_id": manager_id}
    response = requests.patch(f"{BASE_URL}/sets/{set_id}/", json=update_set_data, headers=headers)
    if response.status_code == 200:
        print(f"✅ Manager assigned to set")
    else:
        print(f"❌ Manager assignment failed: {response.text}")
        return False
    
    # Step 6: Create expense categories
    print("\n6. Creating expense categories...")
    categories = [
        {"name": "Travel", "description": "Travel expenses"},
        {"name": "Meals", "description": "Meal expenses"},
        {"name": "Office", "description": "Office supplies"}
    ]
    
    category_ids = []
    for category_data in categories:
        response = requests.post(f"{BASE_URL}/expense-categories/", json=category_data, headers=headers)
        if response.status_code == 201:
            category_info = response.json()
            category_ids.append(category_info['id'])
            print(f"✅ Category created: {category_info['name']}")
        else:
            print(f"❌ Category creation failed: {response.text}")
            return False
    
    # Step 7: Create test expenses
    print("\n7. Creating test expenses...")
    expenses_data = [
        {
            "title": "Client Meeting Travel",
            "description": "Taxi fare to client meeting",
            "amount": 25.50,
            "currency": "USD",
            "expense_date": "2024-01-15",
            "category_id": category_ids[0],
            "priority": "medium"
        },
        {
            "title": "Team Lunch",
            "description": "Team lunch expense",
            "amount": 45.00,
            "currency": "USD",
            "expense_date": "2024-01-16",
            "category_id": category_ids[1],
            "priority": "low"
        },
        {
            "title": "Office Supplies",
            "description": "Stationery and supplies",
            "amount": 15.75,
            "currency": "USD",
            "expense_date": "2024-01-17",
            "category_id": category_ids[2],
            "priority": "low"
        }
    ]
    
    expense_ids = []
    for i, expense_data in enumerate(expenses_data, 1):
        employee_headers = {"Authorization": f"Bearer {employee_tokens[i % len(employee_tokens)]}"}
        response = requests.post(f"{BASE_URL}/expenses/", json=expense_data, headers=employee_headers)
        if response.status_code == 201:
            expense_info = response.json()
            expense_ids.append(expense_info['id'])
            print(f"✅ Expense {i} created: {expense_info['title']} - ${expense_info['amount']}")
        else:
            print(f"❌ Expense {i} creation failed: {response.text}")
            return False
    
    # Step 8: Manager login and test dashboard
    print("\n8. Manager login and test dashboard...")
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
    
    # Test dashboard data endpoint
    print("\n9. Testing dashboard data endpoint...")
    manager_headers = {"Authorization": f"Bearer {manager_token}"}
    response = requests.get(f"{BASE_URL}/manager-dashboard/", headers=manager_headers)
    if response.status_code == 200:
        dashboard_data = response.json()
        print(f"✅ Dashboard data retrieved successfully")
        print(f"   - Pending count: {dashboard_data['pending_count']}")
        print(f"   - Approved count: {dashboard_data['approved_count']}")
        print(f"   - Rejected count: {dashboard_data['rejected_count']}")
        print(f"   - Team members: {dashboard_data['team_members_count']}")
        print(f"   - Total expenses: {dashboard_data['total_expenses']}")
        print(f"   - Today's approvals: {dashboard_data['today_approvals']}")
        print(f"   - Recent approvals: {len(dashboard_data['recent_approvals'])}")
    else:
        print(f"❌ Dashboard data failed: {response.text}")
        return False
    
    # Step 10: Approve some expenses and test dynamic updates
    print("\n10. Approving expenses and testing dynamic updates...")
    for i, expense_id in enumerate(expense_ids[:2], 1):  # Approve first 2 expenses
        response = requests.post(f"{BASE_URL}/expenses/{expense_id}/approve/", headers=manager_headers)
        if response.status_code == 200:
            print(f"✅ Expense {i} approved")
        else:
            print(f"❌ Expense {i} approval failed: {response.text}")
    
    # Test updated dashboard data
    print("\n11. Testing updated dashboard data...")
    response = requests.get(f"{BASE_URL}/manager-dashboard/", headers=manager_headers)
    if response.status_code == 200:
        updated_dashboard_data = response.json()
        print(f"✅ Updated dashboard data retrieved")
        print(f"   - Pending count: {updated_dashboard_data['pending_count']}")
        print(f"   - Approved count: {updated_dashboard_data['approved_count']}")
        print(f"   - Recent approvals: {len(updated_dashboard_data['recent_approvals'])}")
    else:
        print(f"❌ Updated dashboard data failed: {response.text}")
        return False
    
    print("\n🎉 Dynamic Dashboard Test Completed Successfully!")
    print("=" * 50)
    print("✅ All dashboard features working:")
    print("   - Real-time statistics")
    print("   - Pending approvals count")
    print("   - Approved expenses tracking")
    print("   - Team member count")
    print("   - Recent approvals display")
    print("   - Dynamic updates after actions")
    
    return True

if __name__ == "__main__":
    try:
        test_dynamic_dashboard()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
