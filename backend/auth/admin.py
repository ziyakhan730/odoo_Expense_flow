from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Company, UserSet, Expense, ExpenseCategory, Receipt


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


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'is_active', 'created_at']
    list_filter = ['company', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'amount', 'currency', 'status', 'expense_date', 'submission_date']
    list_filter = ['status', 'priority', 'currency', 'company', 'expense_date', 'submission_date']
    search_fields = ['title', 'description', 'user__first_name', 'user__last_name']
    readonly_fields = ['submission_date', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {'fields': ('user', 'company', 'title', 'description')}),
        ('Financial Information', {'fields': ('amount', 'currency', 'exchange_rate', 'base_amount')}),
        ('Categorization', {'fields': ('category', 'expense_date')}),
        ('Status and Approval', {'fields': ('status', 'priority', 'approved_by', 'approved_at', 'rejection_reason')}),
        ('AI Information', {'fields': ('ocr_extracted_data', 'ai_confidence_score', 'is_ai_filled')}),
        ('Additional Information', {'fields': ('tags', 'notes')}),
        ('Timestamps', {'fields': ('submission_date', 'created_at', 'updated_at')}),
    )


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ['expense', 'file_name', 'file_size', 'merchant_name', 'created_at']
    list_filter = ['file_type', 'created_at']
    search_fields = ['file_name', 'merchant_name', 'merchant_address']
    readonly_fields = ['created_at', 'updated_at']
