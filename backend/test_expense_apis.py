#!/usr/bin/env python3
"""
Test script to verify expense management APIs
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000/api"
AUTH_URL = f"{BASE_URL}/auth"

def test_expense_apis():
    """Test expense management APIs"""
    print("🧪 Testing Expense Management APIs")
    print("=" * 50)
    
    timestamp = str(int(time.time()))
    
    # Step 1: Register a company and get admin token
    print("\n1️⃣ Setting up admin user...")
    company_data = {
        "username": f"admin_{timestamp}",
        "email": f"admin_{timestamp}@test.com",
        "first_name": "Admin",
        "last_name": "User",
        "password": "adminpass123",
        "password_confirm": "adminpass123",
        "phone": "+1234567890",
        "role": "admin",
        "company_data": {
            "name": f"Test Company {timestamp}",
            "address": "123 Test St",
            "phone": "+1234567890",
            "email": f"info_{timestamp}@test.com",
            "industry": "Technology",
            "size": "11-50"
        }
    }
    
    try:
        response = requests.post(f"{AUTH_URL}/register/company/", json=company_data)
        if response.status_code == 201:
            admin_data = response.json()
            access_token = admin_data['access']
            print("✅ Admin user created successfully")
        else:
            print(f"❌ Admin creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return
    except Exception as e:
        print(f"❌ Admin creation error: {e}")
        return
    
    # Step 2: Test currency APIs
    print("\n2️⃣ Testing currency APIs...")
    
    # Test countries and currencies
    try:
        response = requests.get(
            f"{AUTH_URL}/countries-currencies/",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code == 200:
            countries_data = response.json()
            print(f"✅ Countries API working - {len(countries_data)} countries")
            # Show first few currencies
            currencies_found = set()
            for country in countries_data[:5]:
                for code, currency in country.get('currencies', {}).items():
                    currencies_found.add(f"{code} - {currency.get('name', 'Unknown')}")
            print(f"   Sample currencies: {', '.join(list(currencies_found)[:5])}")
        else:
            print(f"❌ Countries API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Countries API error: {e}")
    
    # Test exchange rates
    try:
        response = requests.get(
            f"{AUTH_URL}/exchange-rates/",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code == 200:
            rates_data = response.json()
            print(f"✅ Exchange rates API working - Base: {rates_data.get('base', 'Unknown')}")
            print(f"   Sample rates: USD={rates_data.get('rates', {}).get('USD', 'N/A')}, EUR={rates_data.get('rates', {}).get('EUR', 'N/A')}")
        else:
            print(f"❌ Exchange rates API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Exchange rates API error: {e}")
    
    # Step 3: Test expense categories
    print("\n3️⃣ Testing expense categories...")
    try:
        response = requests.get(
            f"{AUTH_URL}/expense-categories/",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Expense categories API working - {len(categories)} categories")
        else:
            print(f"❌ Expense categories API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Expense categories API error: {e}")
    
    # Step 4: Create an expense category
    print("\n4️⃣ Creating expense category...")
    try:
        category_data = {
            "name": f"Test Category {timestamp}",
            "description": "Test category for API testing"
        }
        response = requests.post(
            f"{AUTH_URL}/expense-categories/",
            json=category_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code == 201:
            category = response.json()
            print(f"✅ Expense category created: {category['name']}")
            category_id = category['id']
        else:
            print(f"❌ Category creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            category_id = None
    except Exception as e:
        print(f"❌ Category creation error: {e}")
        category_id = None
    
    # Step 5: Test expense creation
    print("\n5️⃣ Testing expense creation...")
    try:
        expense_data = {
            "title": f"Test Expense {timestamp}",
            "description": "Test expense for API testing",
            "amount": 25.50,
            "currency": "USD",
            "expense_date": "2024-01-15",
            "priority": "medium",
            "tags": ["test", "api"],
            "notes": "Test expense notes"
        }
        
        if category_id:
            expense_data["category_id"] = category_id
        
        response = requests.post(
            f"{AUTH_URL}/expenses/",
            json=expense_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code == 201:
            expense = response.json()
            print(f"✅ Expense created: {expense['title']} - ${expense['amount']} {expense['currency']}")
            expense_id = expense['id']
        else:
            print(f"❌ Expense creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            expense_id = None
    except Exception as e:
        print(f"❌ Expense creation error: {e}")
        expense_id = None
    
    # Step 6: Test expense listing
    print("\n6️⃣ Testing expense listing...")
    try:
        response = requests.get(
            f"{AUTH_URL}/expenses/",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code == 200:
            expenses = response.json()
            print(f"✅ Expenses listing working - {len(expenses)} expenses")
            if expenses:
                latest = expenses[0]
                print(f"   Latest expense: {latest['title']} - ${latest['amount']} {latest['currency']}")
        else:
            print(f"❌ Expenses listing failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Expenses listing error: {e}")
    
    # Step 7: Test OCR endpoint (mock)
    print("\n7️⃣ Testing OCR endpoint...")
    try:
        # Create a dummy file for testing
        dummy_file_content = b"dummy receipt content"
        files = {'file': ('test_receipt.txt', dummy_file_content, 'text/plain')}
        
        response = requests.post(
            f"{AUTH_URL}/receipts/ocr/",
            files=files,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code == 200:
            ocr_data = response.json()
            print(f"✅ OCR API working - Confidence: {ocr_data.get('confidence', 'N/A')}")
            print(f"   Extracted amount: {ocr_data.get('extracted_data', {}).get('amount', 'N/A')}")
        else:
            print(f"❌ OCR API failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ OCR API error: {e}")
    
    print("\n🎉 Expense API testing completed!")

if __name__ == "__main__":
    test_expense_apis()
