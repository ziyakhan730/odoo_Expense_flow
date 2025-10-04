#!/usr/bin/env python
"""
Create a test user with known credentials for testing login.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from auth.models import User, Company

def create_test_user():
    """Create a test user with known credentials"""
    print("👤 Creating test user...")
    
    try:
        # Create or get a test company
        company, created = Company.objects.get_or_create(
            name="Test Company",
            defaults={
                'address': '123 Test Street, Test City, TC 12345',
                'phone': '+1234567890',
                'email': 'test@testcompany.com',
                'website': 'https://testcompany.com',
                'industry': 'technology',
                'size': '11-50',
                'description': 'A test company for login testing'
            }
        )
        
        if created:
            print(f"✅ Created company: {company.name}")
        else:
            print(f"✅ Using existing company: {company.name}")
        
        # Create or update test user
        user, created = User.objects.get_or_create(
            email='test@testcompany.com',
            defaults={
                'username': 'testuser',
                'first_name': 'Test',
                'last_name': 'User',
                'is_active': True,
                'is_company_admin': True,
                'role': 'admin',
                'company': company
            }
        )
        
        if created:
            print(f"✅ Created user: {user.username}")
        else:
            print(f"✅ Using existing user: {user.username}")
            user.is_active = True
            user.save()
        
        # Set password (this will hash it properly)
        user.set_password('testpassword123')
        user.save()
        
        print(f"✅ User created/updated successfully!")
        print(f"   Email: {user.email}")
        print(f"   Username: {user.username}")
        print(f"   Password: testpassword123")
        print(f"   Active: {user.is_active}")
        print(f"   Company: {user.company.name if user.company else 'None'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    success = create_test_user()
    print("=" * 50)
    if success:
        print("✅ Test user ready for login testing!")
    else:
        print("❌ Failed to create test user!")
