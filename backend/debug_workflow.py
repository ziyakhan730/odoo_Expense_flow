#!/usr/bin/env python3
"""
Debug script to test the approval workflow for expenses above $6000
"""
import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from auth.models import Company, User, ApprovalRule, Expense, UserSet
from auth.workflow import get_applicable_rule, create_default_rules, convert_currency
from django.utils import timezone

def debug_workflow():
    print("🔍 Debugging Approval Workflow for $6000+ Expenses")
    print("=" * 60)
    
    # Get the first company (assuming it exists)
    try:
        company = Company.objects.first()
        if not company:
            print("❌ No company found. Please create a company first.")
            return
        
        print(f"📊 Company: {company.name}")
        print(f"   ID: {company.id}")
        print()
        
        # Check existing rules
        print("📋 Current Approval Rules:")
        rules = ApprovalRule.objects.filter(company=company, is_active=True).order_by('min_amount')
        
        if not rules.exists():
            print("   ⚠️  No rules found. Creating default rules...")
            success = create_default_rules(company)
            if success:
                print("   ✅ Default rules created successfully")
                rules = ApprovalRule.objects.filter(company=company, is_active=True).order_by('min_amount')
            else:
                print("   ❌ Failed to create default rules")
                return
        else:
            print("   ✅ Found existing rules")
        
        # Display rules
        for rule in rules:
            print(f"   📝 {rule.name}")
            print(f"      Amount Range: ${rule.min_amount} - ${rule.max_amount or '∞'}")
            print(f"      Sequence: {rule.sequence}")
            print(f"      Urgent Bypass: {rule.urgent_bypass}")
            print(f"      Admin Override: {rule.admin_override}")
            print()
        
        # Test rule matching for $6000
        test_amount = 6000
        print(f"🧪 Testing Rule Matching for ${test_amount}")
        print("-" * 40)
        
        # Test currency conversion
        print(f"💰 Currency Conversion Test:")
        converted_amount = convert_currency(test_amount, 'USD', 'USD')
        print(f"   Original: ${test_amount}")
        print(f"   Converted: ${converted_amount}")
        print()
        
        # Test rule matching
        applicable_rule = get_applicable_rule(converted_amount, company, urgent=False)
        if applicable_rule:
            print(f"✅ Found applicable rule: {applicable_rule.name}")
            print(f"   Amount Range: ${applicable_rule.min_amount} - ${applicable_rule.max_amount or '∞'}")
            print(f"   Sequence: {applicable_rule.sequence}")
            print(f"   Should go to: {applicable_rule.sequence[0] if applicable_rule.sequence else 'Unknown'}")
        else:
            print("❌ No applicable rule found!")
            print("   This means the expense won't be routed properly.")
        
        print()
        
        # Check for existing expenses
        print("📊 Existing Expenses:")
        expenses = Expense.objects.filter(company=company).order_by('-submission_date')[:5]
        
        if expenses.exists():
            for expense in expenses:
                print(f"   💳 {expense.title}")
                print(f"      Amount: ${expense.amount} {expense.currency}")
                print(f"      Status: {expense.status}")
                print(f"      Current Stage: {expense.current_stage}")
                print(f"      Approval Rule: {expense.approval_rule.name if expense.approval_rule else 'None'}")
                print(f"      User: {expense.user.username}")
                print()
        else:
            print("   📝 No expenses found")
        
        # Test urgent workflow
        print("🚨 Testing Urgent Workflow:")
        urgent_rule = get_applicable_rule(converted_amount, company, urgent=True)
        if urgent_rule:
            print(f"✅ Urgent rule found: {urgent_rule.name}")
            print(f"   Sequence: {urgent_rule.sequence}")
        else:
            print("❌ No urgent rule found")
        
        print()
        print("🔧 Debugging Complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_workflow()
