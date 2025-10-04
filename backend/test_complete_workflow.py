#!/usr/bin/env python3
"""
Complete workflow test - create users and test expense submission
"""
import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from auth.models import Company, User, ApprovalRule, Expense, UserSet
from auth.workflow import create_default_rules
from django.contrib.auth.hashers import make_password

def test_complete_workflow():
    print("🧪 Complete Workflow Test")
    print("=" * 50)
    
    try:
        # Get or create company
        company = Company.objects.first()
        if not company:
            print("❌ No company found")
            return
        
        print(f"📊 Company: {company.name}")
        
        # Ensure rules exist
        rules = ApprovalRule.objects.filter(company=company, is_active=True)
        if not rules.exists():
            print("📋 Creating default rules...")
            create_default_rules(company)
            print("✅ Rules created")
        
        # Create admin user if not exists
        admin, created = User.objects.get_or_create(
            username='testadmin',
            defaults={
                'email': 'admin@test.com',
                'first_name': 'Test',
                'last_name': 'Admin',
                'role': 'admin',
                'company': company,
                'is_active': True,
                'password': make_password('testpass123')
            }
        )
        if created:
            print("✅ Created admin user")
        else:
            print("✅ Admin user exists")
        
        # Create manager user
        manager, created = User.objects.get_or_create(
            username='testmanager',
            defaults={
                'email': 'manager@test.com',
                'first_name': 'Test',
                'last_name': 'Manager',
                'role': 'manager',
                'company': company,
                'is_active': True,
                'password': make_password('testpass123')
            }
        )
        if created:
            print("✅ Created manager user")
        else:
            print("✅ Manager user exists")
        
        # Create employee user
        employee, created = User.objects.get_or_create(
            username='testemployee',
            defaults={
                'email': 'employee@test.com',
                'first_name': 'Test',
                'last_name': 'Employee',
                'role': 'employee',
                'company': company,
                'is_active': True,
                'password': make_password('testpass123')
            }
        )
        if created:
            print("✅ Created employee user")
        else:
            print("✅ Employee user exists")
        
        # Create user set and assign manager and employee
        user_set, created = UserSet.objects.get_or_create(
            name='Test Team',
            company=company,
            defaults={'manager': manager}
        )
        if created:
            print("✅ Created user set")
        else:
            print("✅ User set exists")
        
        # Assign employee to user set
        employee.user_set = user_set
        employee.save()
        print("✅ Assigned employee to user set")
        
        # Create expense category
        from auth.models import ExpenseCategory
        category, created = ExpenseCategory.objects.get_or_create(
            name='Test Category',
            company=company,
            defaults={'description': 'Test category for workflow'}
        )
        if created:
            print("✅ Created expense category")
        else:
            print("✅ Expense category exists")
        
        print("\n🧪 Testing Expense Submission")
        print("-" * 30)
        
        # Test expense submission via API
        base_url = "http://localhost:8000"
        
        # Login as employee
        login_data = {
            "username": employee.username,
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
        
        # Submit expense above $6000
        expense_data = {
            "title": "High Amount Test Expense",
            "description": "Testing workflow for amount above $6000",
            "amount": 6000,
            "currency": "USD",
            "expense_date": "2024-01-15",
            "category": category.id,
            "priority": "high",
            "urgent": False
        }
        
        print(f"💳 Submitting expense: ${expense_data['amount']}")
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
        print(f"✅ Expense created: ID {expense_result['expense']['id']}")
        print(f"   Status: {expense_result['expense']['status']}")
        print(f"   Current Stage: {expense_result['expense']['current_stage']}")
        print(f"   Approval Rule: {expense_result['expense']['approval_rule_name']}")
        
        # Check database
        expense_id = expense_result['expense']['id']
        expense = Expense.objects.get(id=expense_id)
        print(f"\n📊 Database Check:")
        print(f"   Expense ID: {expense.id}")
        print(f"   Amount: ${expense.amount}")
        print(f"   Status: {expense.status}")
        print(f"   Current Stage: {expense.current_stage}")
        print(f"   Approval Rule: {expense.approval_rule.name if expense.approval_rule else 'None'}")
        print(f"   User: {expense.user.username}")
        print(f"   Company: {expense.company.name}")
        
        # Check pending approvals for manager
        print(f"\n🔍 Checking pending approvals for manager...")
        manager_login_data = {
            "username": manager.username,
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
            "username": admin.username,
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
        
        print("\n✅ Complete workflow test finished!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_workflow()
