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
]
