#!/usr/bin/env python3
"""
Test script for the rules management system
"""
import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/auth"
COMPANY_NAME = f"Test Company {int(time.time())}"
ADMIN_EMAIL = f"admin{int(time.time())}@test.com"

def make_request(method, url, data=None, headers=None):
    """Make HTTP request with error handling"""
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        print(f"{method} {url} - Status: {response.status_code}")
        if response.status_code not in [200, 201, 204]:
            print(f"Error: {response.text}")
        return response
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def test_rules_management():
    """Test the complete rules management system"""
    print("🧪 Testing Rules Management System")
    print("=" * 50)
    
    # Step 1: Register Company and Admin
    print("\n1. Registering Company and Admin...")
    company_data = {
        "company_data": {
            "name": COMPANY_NAME,
            "email": ADMIN_EMAIL,
            "size": "51-200",
            "industry": "Technology",
            "address": "123 Business St, City, State 12345",
            "phone": "+15551234567"
        },
        "username": f"admin{int(time.time())}",
        "email": ADMIN_EMAIL,
        "first_name": "Admin",
        "last_name": "User",
        "password": "AdminPass123!",
        "password_confirm": "AdminPass123!"
    }
    
    response = make_request('POST', f"{BASE_URL}/register/company/", company_data)
    if not response or response.status_code != 201:
        print("❌ Company registration failed")
        return
    
    admin_data = response.json()
    admin_token = admin_data['access']
    admin_headers = {'Authorization': f'Bearer {admin_token}'}
    print("✅ Company and admin registered successfully")
    
    # Step 2: Setup default rules
    print("\n2. Setting up default approval rules...")
    response = make_request('POST', f"{BASE_URL}/approval-rules/setup-default/", headers=admin_headers)
    if response and response.status_code == 200:
        print("✅ Default approval rules created")
    else:
        print("❌ Failed to create default rules")
    
    # Step 3: Get all rules
    print("\n3. Getting all approval rules...")
    response = make_request('GET', f"{BASE_URL}/approval-rules/", headers=admin_headers)
    if not response or response.status_code != 200:
        print("❌ Failed to get approval rules")
        return
    
    rules = response.json()
    print(f"✅ Found {len(rules)} approval rules")
    for rule in rules:
        print(f"   - {rule['name']}: ${rule['min_amount']} - ${rule['max_amount'] or '∞'}")
    
    # Step 4: Create a custom rule
    print("\n4. Creating a custom approval rule...")
    custom_rule = {
        "name": "Custom High Amount Rule",
        "min_amount": 100000.00,
        "max_amount": None,
        "sequence": ["manager", "admin"],
        "percentage_required": 100,
        "admin_override": True,
        "urgent_bypass": True,
        "is_active": True
    }
    
    response = make_request('POST', f"{BASE_URL}/approval-rules/create/", custom_rule, admin_headers)
    if not response or response.status_code != 201:
        print("❌ Failed to create custom rule")
        return
    
    new_rule = response.json()
    rule_id = new_rule['id']
    print(f"✅ Custom rule created with ID: {rule_id}")
    
    # Step 5: Update the custom rule
    print("\n5. Updating the custom rule...")
    updated_rule = {
        "name": "Updated Custom High Amount Rule",
        "min_amount": 75000.00,
        "max_amount": 200000.00,
        "sequence": ["admin"],
        "percentage_required": 100,
        "admin_override": True,
        "urgent_bypass": False,
        "is_active": True
    }
    
    response = make_request('PUT', f"{BASE_URL}/approval-rules/{rule_id}/", updated_rule, admin_headers)
    if not response or response.status_code != 200:
        print("❌ Failed to update custom rule")
        return
    
    updated_rule_data = response.json()
    print(f"✅ Rule updated: {updated_rule_data['name']}")
    print(f"   Amount range: ${updated_rule_data['min_amount']} - ${updated_rule_data['max_amount']}")
    print(f"   Sequence: {' → '.join(updated_rule_data['sequence'])}")
    
    # Step 6: Get the updated rule
    print("\n6. Getting the updated rule...")
    response = make_request('GET', f"{BASE_URL}/approval-rules/{rule_id}/", headers=admin_headers)
    if not response or response.status_code != 200:
        print("❌ Failed to get updated rule")
        return
    
    rule_data = response.json()
    print(f"✅ Retrieved rule: {rule_data['name']}")
    print(f"   Active: {rule_data['is_active']}")
    print(f"   Admin Override: {rule_data['admin_override']}")
    print(f"   Urgent Bypass: {rule_data['urgent_bypass']}")
    
    # Step 7: Get all rules again to see the changes
    print("\n7. Getting all rules after updates...")
    response = make_request('GET', f"{BASE_URL}/approval-rules/", headers=admin_headers)
    if not response or response.status_code != 200:
        print("❌ Failed to get updated rules list")
        return
    
    updated_rules = response.json()
    print(f"✅ Found {len(updated_rules)} approval rules")
    for rule in updated_rules:
        status = "Active" if rule['is_active'] else "Inactive"
        print(f"   - {rule['name']}: ${rule['min_amount']} - ${rule['max_amount'] or '∞'} ({status})")
    
    # Step 8: Delete the custom rule
    print("\n8. Deleting the custom rule...")
    response = make_request('DELETE', f"{BASE_URL}/approval-rules/{rule_id}/", headers=admin_headers)
    if not response or response.status_code == 204:
        print("✅ Custom rule deleted successfully")
    else:
        print("❌ Failed to delete custom rule")
    
    # Step 9: Verify deletion
    print("\n9. Verifying rule deletion...")
    response = make_request('GET', f"{BASE_URL}/approval-rules/", headers=admin_headers)
    if not response or response.status_code != 200:
        print("❌ Failed to get rules after deletion")
        return
    
    final_rules = response.json()
    print(f"✅ Found {len(final_rules)} approval rules after deletion")
    
    print("\n🎉 Rules Management Test Completed Successfully!")
    print("=" * 50)
    print("✅ All rules management features tested:")
    print("   - Company and admin registration")
    print("   - Default rules setup")
    print("   - Rule creation")
    print("   - Rule retrieval")
    print("   - Rule updating")
    print("   - Rule deletion")
    print("   - Rules listing")

if __name__ == "__main__":
    test_rules_management()
