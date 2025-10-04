#!/usr/bin/env python3
"""
Simple test for the approval workflow engine
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from auth.workflow import convert_currency, create_default_rules
from auth.models import Company, User

def test_workflow_basics():
    """Test basic workflow functionality"""
    print("🧪 Testing Workflow Engine Basics")
    print("=" * 40)
    
    # Test currency conversion
    print("\n1. Testing Currency Conversion...")
    try:
        usd_amount = convert_currency(100, 'EUR', 'USD')
        print(f"✅ Currency conversion: 100 EUR = {usd_amount:.2f} USD")
    except Exception as e:
        print(f"❌ Currency conversion failed: {e}")
    
    # Test default rules creation
    print("\n2. Testing Default Rules Creation...")
    try:
        # Create a test company
        company = Company.objects.create(
            name="Test Company",
            email="test@company.com",
            size="51-200",
            industry="Technology",
            address="123 Test St",
            phone="+15551234567"
        )
        print(f"✅ Test company created: {company.name}")
        
        # Create default rules
        success = create_default_rules(company)
        if success:
            print("✅ Default approval rules created successfully")
        else:
            print("❌ Failed to create default rules")
        
        # List created rules
        from auth.models import ApprovalRule
        rules = ApprovalRule.objects.filter(company=company)
        print(f"✅ Found {rules.count()} approval rules:")
        for rule in rules:
            print(f"   - {rule.name}: ${rule.min_amount} - ${rule.max_amount or '∞'}")
        
    except Exception as e:
        print(f"❌ Rules creation failed: {e}")
    
    print("\n🎉 Basic workflow tests completed!")

if __name__ == "__main__":
    test_workflow_basics()
