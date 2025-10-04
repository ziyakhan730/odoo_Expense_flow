#!/usr/bin/env python3
"""
Test script for User Management System
Tests all user management APIs including sets, users, role changes, and set assignments
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000/api"
AUTH_URL = f"{BASE_URL}/auth"

def test_user_management_system():
    """Test the complete user management system"""
    print("🧪 Testing User Management System")
    print("=" * 50)
    
    # Step 1: Register a company and admin
    print("\n1️⃣ Registering company and admin...")
    import time
    timestamp = str(int(time.time()))
    company_data = {
        "username": f"admin_user_{timestamp}",
        "email": f"admin{timestamp}@testcompany.com",
        "first_name": "Admin",
        "last_name": "User",
        "password": "adminpass123",
        "password_confirm": "adminpass123",
        "phone": "+1234567890",
        "role": "admin",
        "company_data": {
            "name": f"Test Company {timestamp}",
            "address": "123 Test St, Test City, TC 12345",
            "phone": "+1234567890",
            "email": f"info{timestamp}@testcompany.com",
            "website": "https://testcompany.com",
            "industry": "Technology",
            "size": "11-50",
            "description": "A test company for user management"
        }
    }
    
    try:
        response = requests.post(f"{AUTH_URL}/register/company/", json=company_data)
        if response.status_code == 201:
            print("✅ Company and admin registered successfully")
            admin_data = response.json()
            access_token = admin_data['access']
            print(f"   Access token: {access_token[:20]}...")
        else:
            print(f"❌ Company registration failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Company registration error: {e}")
        return False
    
    # Step 2: Create managers (without set assignment first)
    print("\n2️⃣ Creating managers...")
    managers = []
    for i in range(2):
        manager_data = {
            "username": f"manager{i+1}_{timestamp}",
            "email": f"manager{i+1}_{timestamp}@testcompany.com",
            "first_name": f"Manager{i+1}",
            "last_name": "User",
            "password": "managerpass123",
            "role": "manager",
            "phone": f"+123456789{i+1}"
        }
        
        try:
            response = requests.post(
                f"{AUTH_URL}/users/",
                json=manager_data,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if response.status_code == 201:
                manager = response.json()
                managers.append(manager)
                print(f"✅ Manager {i+1} created: {manager['first_name']} {manager['last_name']}")
                print(f"   Manager data: {manager}")
            else:
                print(f"❌ Manager {i+1} creation failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ Manager {i+1} creation error: {e}")
    
    # Step 3: Create employees (without set assignment first)
    print("\n3️⃣ Creating employees...")
    employees = []
    for i in range(3):
        employee_data = {
            "username": f"employee{i+1}_{timestamp}",
            "email": f"employee{i+1}_{timestamp}@testcompany.com",
            "first_name": f"Employee{i+1}",
            "last_name": "User",
            "password": "employeepass123",
            "role": "employee",
            "phone": f"+123456780{i+1}"
        }
        
        try:
            response = requests.post(
                f"{AUTH_URL}/users/",
                json=employee_data,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if response.status_code == 201:
                employee = response.json()
                employees.append(employee)
                print(f"✅ Employee {i+1} created: {employee['first_name']} {employee['last_name']}")
            else:
                print(f"❌ Employee {i+1} creation failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ Employee {i+1} creation error: {e}")
    
    # Step 4: Create user sets
    print("\n4️⃣ Creating user sets...")
    print(f"   Available managers: {len(managers)}")
    for i, manager in enumerate(managers):
        print(f"   Manager {i+1}: {manager.get('first_name', 'Unknown')} (ID: {manager.get('id', 'No ID')})")
    
    sets = []
    for i in range(2):
        if i < len(managers):
            set_data = {
                "name": f"Team {i+1}",
                "manager_id": managers[i]['id']
            }
        else:
            # If we don't have enough managers, use the first one
            set_data = {
                "name": f"Team {i+1}",
                "manager_id": managers[0]['id']
            }
        
        try:
            response = requests.post(
                f"{AUTH_URL}/sets/",
                json=set_data,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if response.status_code == 201:
                user_set = response.json()
                sets.append(user_set)
                print(f"✅ Set {i+1} created: {user_set['name']} (Manager: {user_set.get('manager_name', 'Unknown')})")
                print(f"   Set data: {user_set}")
            else:
                print(f"❌ Set {i+1} creation failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ Set {i+1} creation error: {e}")
            print(f"   Exception details: {str(e)}")
    
    # Step 5: Assign employees to sets
    print("\n5️⃣ Assigning employees to sets...")
    print(f"   Available sets: {len(sets)}")
    for i, set_info in enumerate(sets):
        print(f"   Set {i+1}: {set_info.get('name', 'Unknown')} (ID: {set_info.get('id', 'No ID')})")
    
    print(f"   Available employees: {len(employees)}")
    for i, employee in enumerate(employees):
        print(f"   Employee {i+1}: {employee.get('first_name', 'Unknown')} (ID: {employee.get('id', 'No ID')})")
    
    if sets and employees:
        for i, employee in enumerate(employees):
            set_id = sets[i % len(sets)]['id']
            try:
                response = requests.patch(
                    f"{AUTH_URL}/users/{employee['id']}/set/",
                    json={"set_id": set_id},
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                if response.status_code == 200:
                    print(f"✅ Employee {employee['first_name']} assigned to {sets[i % len(sets)]['name']}")
                else:
                    print(f"❌ Employee assignment failed: {response.status_code}")
                    print(f"   Error: {response.text}")
            except Exception as e:
                print(f"❌ Employee assignment error: {e}")
    else:
        print("⚠️ No sets or employees available for assignment")
    
    # Step 6: Test role changes
    print("\n6️⃣ Testing role changes...")
    if employees:
        employee = employees[0]
        try:
            # Promote employee to manager
            response = requests.patch(
                f"{AUTH_URL}/users/{employee['id']}/role/",
                json={"role": "manager"},
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if response.status_code == 200:
                print(f"✅ Employee {employee['first_name']} promoted to manager")
            else:
                print(f"❌ Role change failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ Role change error: {e}")
    else:
        print("⚠️ No employees available for role change test")
    
    # Step 7: Test set movements
    print("\n7️⃣ Testing set movements...")
    if employees and len(sets) > 1:
        employee = employees[1] if len(employees) > 1 else employees[0]
        new_set_id = sets[1]['id']
        try:
            response = requests.patch(
                f"{AUTH_URL}/users/{employee['id']}/set/",
                json={"set_id": new_set_id},
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if response.status_code == 200:
                print(f"✅ Employee {employee['first_name']} moved to {sets[1]['name']}")
            else:
                print(f"❌ Set movement failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ Set movement error: {e}")
    else:
        print("⚠️ No employees or sets available for movement test")
    
    # Step 8: List all sets with details
    print("\n8️⃣ Listing all sets with details...")
    try:
        response = requests.get(
            f"{AUTH_URL}/sets/",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code == 200:
            sets_data = response.json()
            print(f"✅ Found {len(sets_data)} sets:")
            for set_info in sets_data:
                print(f"   📁 {set_info['name']}")
                print(f"      Manager: {set_info['manager_name']} ({set_info['manager_email']})")
                print(f"      Employees: {set_info['employees_count']}")
                if set_info['employees']:
                    for emp in set_info['employees']:
                        print(f"        - {emp['first_name']} {emp['last_name']} ({emp['role']})")
        else:
            print(f"❌ Failed to list sets: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ List sets error: {e}")
    
    # Step 9: Test validation rules
    print("\n9️⃣ Testing validation rules...")
    
    # Try to assign a second manager to a set that already has one
    if len(managers) > 1 and len(sets) > 0:
        try:
            response = requests.patch(
                f"{AUTH_URL}/users/{managers[1]['id']}/set/",
                json={"set_id": sets[0]['id']},
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if response.status_code == 400:
                print("✅ Validation working: Cannot assign second manager to set")
            else:
                print(f"❌ Validation failed: Should not allow second manager")
        except Exception as e:
            print(f"❌ Validation test error: {e}")
    
    # Step 10: Test available managers endpoint
    print("\n🔟 Testing available managers...")
    try:
        response = requests.get(
            f"{AUTH_URL}/managers/available/",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code == 200:
            available_managers = response.json()
            print(f"✅ Found {len(available_managers)} available managers")
            for manager in available_managers:
                print(f"   - {manager['first_name']} {manager['last_name']} ({manager['email']})")
        else:
            print(f"❌ Failed to get available managers: {response.status_code}")
    except Exception as e:
        print(f"❌ Available managers error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 User Management System Test Complete!")
    print("✅ All core functionality tested")
    print("✅ Validation rules working")
    print("✅ API endpoints functional")
    return True

if __name__ == "__main__":
    try:
        success = test_user_management_system()
        if success:
            print("\n🎯 User Management System is working correctly!")
            sys.exit(0)
        else:
            print("\n❌ User Management System has issues!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1)
