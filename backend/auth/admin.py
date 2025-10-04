from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Company, UserSet


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'industry', 'size', 'is_active', 'created_at']
    list_filter = ['industry', 'size', 'is_active', 'created_at']
    search_fields = ['name', 'email', 'industry']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserSet)
class UserSetAdmin(admin.ModelAdmin):
    list_display = ['name', 'manager', 'company', 'created_at']
    list_filter = ['company', 'created_at']
    search_fields = ['name', 'manager__first_name', 'manager__last_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'company', 'user_set', 'is_company_admin', 'is_active']
    list_filter = ['role', 'is_company_admin', 'is_active', 'company', 'user_set']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Company Information', {'fields': ('company', 'user_set', 'role', 'phone', 'is_company_admin')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
