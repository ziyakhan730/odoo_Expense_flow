#!/usr/bin/env python3
"""
Simple test to verify the workflow is working correctly
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from auth.models import Company, User, ApprovalRule, Expense, UserSet, ExpenseCategory
from auth.workflow import get_applicable_rule, advance_workflow, create_default_rules
from django.contrib.auth.hashers import make_password
from django.utils import timezone

def test_workflow_simple():
    print("🧪 Simple Workflow Test")
    print("=" * 40)
    
    try:
        # Get or create company
        company = Company.objects.first()
        if not company:
            print("❌ No company found")
            return
        
        print(f"📊 Company: {company.name}")
        
        # Ensure default rules exist
        rules = ApprovalRule.objects.filter(company=company, is_active=True)
        if not rules.exists():
            print("📋 Creating default rules...")
            create_default_rules(company)
            rules = ApprovalRule.objects.filter(company=company, is_active=True)
        
        print(f"📋 Found {rules.count()} approval rules")
        for rule in rules:
            print(f"   - {rule.name}: ${rule.min_amount} - ${rule.max_amount or '∞'}")
        
        # Get users
        admin = User.objects.filter(company=company, role='admin').first()
        manager = User.objects.filter(company=company, role='manager').first()
        employee = User.objects.filter(company=company, role='employee').first()
        
        if not all([admin, manager, employee]):
            print("❌ Missing users")
            return
        
        print(f"👤 Users: Admin={admin.username}, Manager={manager.username}, Employee={employee.username}")
        
        # Test rule matching for $6000
        test_amount = 6000
        print(f"\n🧪 Testing Rule Matching for ${test_amount}")
        
        applicable_rule = get_applicable_rule(test_amount, company, urgent=False)
        if applicable_rule:
            print(f"✅ Found rule: {applicable_rule.name}")
            print(f"   Sequence: {applicable_rule.sequence}")
        else:
            print("❌ No applicable rule found!")
            return
        
        # Create expense
        category, _ = ExpenseCategory.objects.get_or_create(
            name='Test Category',
            company=company,
            defaults={'description': 'Test category'}
        )
        
        expense = Expense.objects.create(
            title="Simple Workflow Test",
            description="Testing workflow for $6000",
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
        
        # Test manager approval
        print(f"\n👨‍💼 Manager Approval Test...")
        result = advance_workflow(expense, manager, 'approved', 'Manager approved')
        print(f"✅ Manager approval result: {result}")
        
        # Check status after manager approval
        expense.refresh_from_db()
        print(f"   After manager approval:")
        print(f"   - Status: {expense.status}")
        print(f"   - Stage: {expense.current_stage}")
        print(f"   - Next Approver: {result.get('next_approver', 'None')}")
        
        # Check if it moved to admin stage
        if expense.current_stage == 'admin' and expense.status == 'in_progress':
            print("✅ SUCCESS: Expense correctly moved to admin stage!")
            
            # Test admin approval
            print(f"\n👨‍💻 Admin Approval Test...")
            result = advance_workflow(expense, admin, 'approved', 'Admin approved')
            print(f"✅ Admin approval result: {result}")
            
            # Check final status
            expense.refresh_from_db()
            print(f"   Final status: {expense.status}")
            print(f"   Final stage: {expense.current_stage}")
            
            if expense.status == 'approved':
                print("🎉 SUCCESS: Workflow completed correctly!")
            else:
                print("❌ ISSUE: Expense not approved after admin approval")
        else:
            print("❌ ISSUE: Expense did not move to admin stage")
            print(f"   Expected: current_stage='admin', status='in_progress'")
            print(f"   Actual: current_stage='{expense.current_stage}', status='{expense.status}'")
        
        # Show approval records
        records = expense.approval_records.all()
        print(f"\n📋 Approval Records ({records.count()}):")
        for record in records:
            print(f"   - {record.approver.username} ({record.role}): {record.status}")
        
        print("\n✅ Simple workflow test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_workflow_simple()
