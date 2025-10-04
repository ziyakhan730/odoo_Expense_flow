from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Authentication endpoints
    path('register/company/', views.CompanyRegistrationView.as_view(), name='company-registration'),
    path('login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('refresh/', views.refresh_token_view, name='refresh-token'),
    path('profile/', views.user_profile, name='user-profile'),
    path('companies/', views.company_list, name='company-list'),
    
    # User Management endpoints
    path('sets/', views.UserSetListCreateView.as_view(), name='user-set-list-create'),
    path('sets/<int:pk>/', views.UserSetDetailView.as_view(), name='user-set-detail'),
    path('users/', views.UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/<int:user_id>/role/', views.update_user_role, name='update-user-role'),
    path('users/<int:user_id>/set/', views.update_user_set, name='update-user-set'),
    path('managers/available/', views.get_available_managers, name='available-managers'),
    path('sets/<int:set_id>/users/', views.get_users_by_set, name='users-by-set'),
    
    # Expense Management endpoints
    path('expenses/', views.expense_list_create, name='expense-list-create'),
    path('expenses/<int:expense_id>/', views.expense_detail, name='expense-detail'),
    path('expense-categories/', views.expense_categories, name='expense-categories'),
    path('expense-categories/<int:category_id>/', views.expense_category_detail, name='expense-category-detail'),
    path('receipts/ocr/', views.process_receipt_ocr, name='process-receipt-ocr'),
    path('countries-currencies/', views.get_countries_currencies, name='countries-currencies'),
    path('exchange-rates/', views.get_exchange_rates, name='exchange-rates'),
    
    # Expense Approval endpoints
    path('pending-approvals/', views.get_pending_approvals, name='pending-approvals'),
    path('expenses/<int:expense_id>/approve/', views.approve_expense, name='approve-expense'),
    path('expenses/<int:expense_id>/reject/', views.reject_expense, name='reject-expense'),
    path('my-expenses/', views.get_my_expenses, name='my-expenses'),
    path('manager-dashboard/', views.get_manager_dashboard_data, name='manager-dashboard'),
    path('manager-history/', views.get_manager_approval_history, name='manager-history'),
    path('admin-dashboard/', views.get_admin_dashboard_data, name='admin-dashboard'),
    
    # Workflow API endpoints
    path('expenses/submit/', views.submit_expense, name='submit-expense'),
    path('expenses/pending/', views.get_pending_approvals_workflow, name='pending-approvals-workflow'),
    path('expenses/<int:expense_id>/approve-workflow/', views.approve_expense_workflow, name='approve-expense-workflow'),
    path('expenses/<int:expense_id>/reject-workflow/', views.reject_expense_workflow, name='reject-expense-workflow'),
    path('expenses/<int:expense_id>/override/', views.admin_override_expense, name='admin-override-expense'),
    path('expenses/history/', views.get_expense_history, name='expense-history'),
    path('approval-rules/', views.get_approval_rules, name='approval-rules'),
    path('approval-rules/create/', views.create_approval_rule, name='create-approval-rule'),
    path('approval-rules/<int:rule_id>/', views.approval_rule_detail, name='approval-rule-detail'),
    path('approval-rules/setup-default/', views.setup_default_rules, name='setup-default-rules'),
    path('escalations/check/', views.check_escalations_view, name='check-escalations'),
]
