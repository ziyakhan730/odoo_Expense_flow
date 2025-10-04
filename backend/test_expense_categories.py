#!/usr/bin/env python3
"""
Test script to verify expense categories functionality
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000/api"
AUTH_URL = f"{BASE_URL}/auth"

def test_expense_categories():
    """Test expense categories functionality"""
    print("🧪 Testing Expense Categories Functionality")
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
    
    # Step 2: Test getting categories (should be empty initially)
    print("\n2️⃣ Testing initial categories list...")
    try:
        response = requests.get(
            f"{AUTH_URL}/expense-categories/",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Categories API working - {len(categories)} categories found")
        else:
            print(f"❌ Categories API failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Categories API error: {e}")
    
    # Step 3: Create expense categories
    print("\n3️⃣ Creating expense categories...")
    test_categories = [
        {"name": f"Travel {timestamp}", "description": "Travel and transportation expenses"},
        {"name": f"Meals {timestamp}", "description": "Food and dining expenses"},
        {"name": f"Office Supplies {timestamp}", "description": "Office equipment and supplies"},
        {"name": f"Entertainment {timestamp}", "description": "Client entertainment and events"}
    ]
    
    created_categories = []
    for i, category_data in enumerate(test_categories):
        try:
            response = requests.post(
                f"{AUTH_URL}/expense-categories/",
                json=category_data,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if response.status_code == 201:
                category = response.json()
                created_categories.append(category)
                print(f"✅ Category {i+1} created: {category['name']}")
            else:
                print(f"❌ Category {i+1} creation failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ Category {i+1} creation error: {e}")
    
    # Step 4: Test getting all categories
    print("\n4️⃣ Testing categories list after creation...")
    try:
        response = requests.get(
            f"{AUTH_URL}/expense-categories/",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Categories list working - {len(categories)} categories found")
            for category in categories:
                print(f"   - {category['name']} ({'Active' if category['is_active'] else 'Inactive'})")
        else:
            print(f"❌ Categories list failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Categories list error: {e}")
    
    # Step 5: Test updating a category
    if created_categories:
        print("\n5️⃣ Testing category update...")
        category_to_update = created_categories[0]
        update_data = {
            "name": f"Updated {category_to_update['name']}",
            "description": "Updated description",
            "is_active": True
        }
        
        try:
            response = requests.put(
                f"{AUTH_URL}/expense-categories/{category_to_update['id']}/",
                json=update_data,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if response.status_code == 200:
                updated_category = response.json()
                print(f"✅ Category updated: {updated_category['name']}")
            else:
                print(f"❌ Category update failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ Category update error: {e}")
    
    # Step 6: Test deactivating a category
    if len(created_categories) > 1:
        print("\n6️⃣ Testing category deactivation...")
        category_to_deactivate = created_categories[1]
        deactivate_data = {
            "name": category_to_deactivate['name'],
            "description": category_to_deactivate.get('description', ''),
            "is_active": False
        }
        
        try:
            response = requests.put(
                f"{AUTH_URL}/expense-categories/{category_to_deactivate['id']}/",
                json=deactivate_data,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if response.status_code == 200:
                deactivated_category = response.json()
                print(f"✅ Category deactivated: {deactivated_category['name']} (Active: {deactivated_category['is_active']})")
            else:
                print(f"❌ Category deactivation failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Category deactivation error: {e}")
    
    # Step 7: Test deleting a category
    if len(created_categories) > 2:
        print("\n7️⃣ Testing category deletion...")
        category_to_delete = created_categories[2]
        
        try:
            response = requests.delete(
                f"{AUTH_URL}/expense-categories/{category_to_delete['id']}/",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if response.status_code == 204:
                print(f"✅ Category deleted: {category_to_delete['name']}")
            else:
                print(f"❌ Category deletion failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Category deletion error: {e}")
    
    # Step 8: Final categories list
    print("\n8️⃣ Final categories list...")
    try:
        response = requests.get(
            f"{AUTH_URL}/expense-categories/",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Final categories count: {len(categories)}")
            for category in categories:
                status = "Active" if category['is_active'] else "Inactive"
                print(f"   - {category['name']} ({status})")
        else:
            print(f"❌ Final categories list failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Final categories list error: {e}")
    
    print("\n🎉 Expense Categories testing completed!")

if __name__ == "__main__":
    test_expense_categories()
