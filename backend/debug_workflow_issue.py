#!/usr/bin/env python3
"""
Debug script to test the workflow issue with expenses above $5000
"""
import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from auth.models import Company, User, ApprovalRule, Expense, UserSet, ExpenseCategory
from auth.workflow import get_applicable_rule, create_default_rules, advance_workflow
from django.contrib.auth.hashers import make_password
from django.utils import timezone

def debug_workflow_issue():
    print("🔍 Debugging Workflow Issue for Expenses Above $5000")
    print("=" * 60)
    
    try:
        # Get company and ensure rules exist
        company = Company.objects.first()
        if not company:
            print("❌ No company found")
            return
        
        print(f"📊 Company: {company.name}")
        
        # Check existing rules
        rules = ApprovalRule.objects.filter(company=company, is_active=True).order_by('min_amount')
        print(f"\n📋 Current Approval Rules:")
        for rule in rules:
            print(f"   📝 {rule.name}")
            print(f"      Amount Range: ${rule.min_amount} - ${rule.max_amount or '∞'}")
            print(f"      Sequence: {rule.sequence}")
            print(f"      Urgent Bypass: {rule.urgent_bypass}")
            print()
        
        # Get users
        admin = User.objects.filter(company=company, role='admin').first()
        manager = User.objects.filter(company=company, role='manager').first()
        employee = User.objects.filter(company=company, role='employee').first()
        
        if not all([admin, manager, employee]):
            print("❌ Missing users. Creating test users...")
            # Create users if they don't exist
            admin, _ = User.objects.get_or_create(
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
            
            manager, _ = User.objects.get_or_create(
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
            
            employee, _ = User.objects.get_or_create(
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
        
        print(f"👤 Users: Admin={admin.username}, Manager={manager.username}, Employee={employee.username}")
        
        # Create user set and assign users
        user_set, _ = UserSet.objects.get_or_create(
            name='Test Team',
            company=company,
            defaults={'manager': manager}
        )
        
        employee.user_set = user_set
        employee.save()
        
        # Create expense category
        category, _ = ExpenseCategory.objects.get_or_create(
            name='Test Category',
            company=company,
            defaults={'description': 'Test category for workflow'}
        )
        
        # Test rule matching for $6000
        test_amount = 6000
        print(f"\n🧪 Testing Rule Matching for ${test_amount}")
        print("-" * 40)
        
        applicable_rule = get_applicable_rule(test_amount, company, urgent=False)
        if applicable_rule:
            print(f"✅ Found applicable rule: {applicable_rule.name}")
            print(f"   Amount Range: ${applicable_rule.min_amount} - ${applicable_rule.max_amount or '∞'}")
            print(f"   Sequence: {applicable_rule.sequence}")
            print(f"   Should go to: {applicable_rule.sequence[0] if applicable_rule.sequence else 'Unknown'}")
        else:
            print("❌ No applicable rule found!")
            return
        
        # Create expense directly
        print(f"\n💳 Creating expense directly...")
        expense = Expense.objects.create(
            title="Debug Test High Amount Expense",
            description="Testing workflow for amount above $6000",
            amount=test_amount,
            currency="USD",
            expense_date=timezone.now().date(),
            submission_date=timezone.now(),
            status='pending',
            priority='high',
            urgent=False,
            user=employee,
            company=company,
            category=category,
            approval_rule=applicable_rule,
            current_stage=applicable_rule.sequence[0] if applicable_rule.sequence else 'manager'
        )
        
        print(f"✅ Expense created: ID {expense.id}")
        print(f"   Status: {expense.status}")
        print(f"   Current Stage: {expense.current_stage}")
        print(f"   Approval Rule: {expense.approval_rule.name}")
        print(f"   User: {expense.user.username}")
        
        # Test manager approval
        print(f"\n👨‍💼 Testing Manager Approval...")
        print(f"   Before approval - Status: {expense.status}, Stage: {expense.current_stage}")
        
        result = advance_workflow(expense, manager, 'approved', 'Manager approved the expense')
        print(f"✅ Manager approval result: {result}")
        
        # Check expense status after manager approval
        expense.refresh_from_db()
        print(f"   After manager approval - Status: {expense.status}")
        print(f"   After manager approval - Stage: {expense.current_stage}")
        print(f"   Next approver: {result.get('next_approver', 'None')}")
        
        # Check if expense is now pending admin approval
        if expense.current_stage == 'admin' and expense.status == 'in_progress':
            print("✅ SUCCESS: Expense correctly moved to admin stage after manager approval")
            
            # Test admin approval
            print(f"\n👨‍💻 Testing Admin Approval...")
            result = advance_workflow(expense, admin, 'approved', 'Admin approved the expense')
            print(f"✅ Admin approval result: {result}")
            
            # Check final status
            expense.refresh_from_db()
            print(f"   Final status: {expense.status}")
            print(f"   Final stage: {expense.current_stage}")
            
            if expense.status == 'approved':
                print("✅ SUCCESS: Expense fully approved after admin approval")
            else:
                print("❌ ISSUE: Expense not approved after admin approval")
        else:
            print("❌ ISSUE: Expense did not move to admin stage after manager approval")
            print(f"   Expected: current_stage='admin', status='in_progress'")
            print(f"   Actual: current_stage='{expense.current_stage}', status='{expense.status}'")
        
        # Check approval records
        approval_records = expense.approval_records.all()
        print(f"\n📋 Approval Records ({approval_records.count()}):")
        for record in approval_records:
            print(f"   - {record.approver.username} ({record.role}): {record.status}")
            if record.comment:
                print(f"     Comment: {record.comment}")
        
        print("\n🔧 Debugging Complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_workflow_issue()
