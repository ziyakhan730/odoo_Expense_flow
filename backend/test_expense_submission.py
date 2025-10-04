#!/usr/bin/env python3
"""
Test script to submit an expense and debug the workflow
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

def test_expense_submission():
    print("🧪 Testing Expense Submission Workflow")
    print("=" * 50)
    
    try:
        # Get company and create rules if needed
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
        
        # Get an admin user
        admin = User.objects.filter(company=company, role='admin').first()
        if not admin:
            print("❌ No admin user found")
            return
        
        print(f"👤 Admin: {admin.username}")
        
        # Get an employee user
        employee = User.objects.filter(company=company, role='employee').first()
        if not employee:
            print("❌ No employee user found")
            return
        
        print(f"👤 Employee: {employee.username}")
        
        # Test expense submission via API
        base_url = "http://localhost:8000"
        
        # Login as employee
        login_data = {
            "username": employee.username,
            "password": "testpass123"  # Assuming this is the password
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
            "title": "Test High Amount Expense",
            "description": "Testing workflow for amount above $6000",
            "amount": 6000,
            "currency": "USD",
            "expense_date": "2024-01-15",
            "category": 1,  # Assuming category exists
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
        
        # Check if expense was created in database
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
            
            print(f"📋 Pending approvals response: {pending_response.status_code}")
            if pending_response.status_code == 200:
                pending_data = pending_response.json()
                print(f"   Found {len(pending_data)} pending approvals")
                for approval in pending_data:
                    print(f"   - {approval['title']}: ${approval['amount']} ({approval['current_stage']})")
            else:
                print(f"❌ Failed to get pending approvals: {pending_response.text}")
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_expense_submission()
