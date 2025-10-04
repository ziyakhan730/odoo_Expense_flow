#!/usr/bin/env python3
"""
Direct workflow test without API calls
"""
import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from auth.models import Company, User, ApprovalRule, Expense, UserSet, ExpenseCategory
from auth.workflow import get_applicable_rule, create_default_rules, convert_currency, advance_workflow
from django.contrib.auth.hashers import make_password
from django.utils import timezone

def test_workflow_direct():
    print("🧪 Direct Workflow Test")
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
        
        # Create users
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
        
        # Create user set
        user_set, created = UserSet.objects.get_or_create(
            name='Test Team',
            company=company,
            defaults={'manager': manager}
        )
        
        # Assign employee to user set
        employee.user_set = user_set
        employee.save()
        
        # Create expense category
        category, created = ExpenseCategory.objects.get_or_create(
            name='Test Category',
            company=company,
            defaults={'description': 'Test category for workflow'}
        )
        
        print("✅ Users and setup created")
        
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
            title="Test High Amount Expense",
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
        result = advance_workflow(expense, manager, 'approved', 'Manager approved the expense')
        print(f"✅ Manager approval result: {result}")
        
        # Check expense status after manager approval
        expense.refresh_from_db()
        print(f"   Status after manager approval: {expense.status}")
        print(f"   Current stage: {expense.current_stage}")
        
        # Test admin approval
        print(f"\n👨‍💻 Testing Admin Approval...")
        result = advance_workflow(expense, admin, 'approved', 'Admin approved the expense')
        print(f"✅ Admin approval result: {result}")
        
        # Check final status
        expense.refresh_from_db()
        print(f"   Final status: {expense.status}")
        print(f"   Final stage: {expense.current_stage}")
        
        # Check approval records
        approval_records = expense.approval_records.all()
        print(f"\n📋 Approval Records ({approval_records.count()}):")
        for record in approval_records:
            print(f"   - {record.approver.username} ({record.role}): {record.status}")
            if record.comment:
                print(f"     Comment: {record.comment}")
        
        print("\n✅ Direct workflow test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_workflow_direct()
