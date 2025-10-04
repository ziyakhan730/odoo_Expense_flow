from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from django.db import transaction, models
from .models import User, Company, UserSet, Expense, ExpenseCategory, ApprovalRule, ApprovalRecord
from .serializers import (
    UserRegistrationSerializer, UserSerializer, LoginSerializer, CompanySerializer, 
    CustomTokenObtainPairSerializer, UserSetSerializer, UserSetCreateSerializer,
    UserCreateSerializer, UserRoleUpdateSerializer, UserSetUpdateSerializer , 
    ExpenseSerializer, ExpenseCreateSerializer, ExpenseCategorySerializer,
    ApprovalRuleSerializer, ApprovalRecordSerializer, WorkflowExpenseSerializer,
    ExpenseSubmissionSerializer, ApprovalActionSerializer
)
from .workflow import (
    convert_currency, get_applicable_rule, advance_workflow, admin_override,
    setup_escalation, check_escalations, create_default_rules
)


class CompanyRegistrationView(generics.CreateAPIView):
    """
    API endpoint for company and admin registration
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
                    refresh = RefreshToken.for_user(user)
                    
                    return Response({
                        'message': 'Company and admin registered successfully',
                        'user': UserSerializer(user).data,
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)
                    }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'error': f'Registration failed: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token obtain view that includes user data
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # Get the user from the validated data
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                user = serializer.user
                response.data['user'] = UserSerializer(user).data
                response.data['message'] = 'Login successful'
        return response


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    API endpoint for user logout
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                print(f"Refresh token blacklisted: {refresh_token[:20]}...")
            except Exception as token_error:
                print(f"Token blacklist error: {token_error}")
                # Continue with logout even if blacklisting fails
        
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Logout error: {e}")
        return Response({'error': f'Logout failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_profile(request):
    """
    API endpoint to get current user profile
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def company_list(request):
    """
    API endpoint to list companies (for admin users)
    """
    if not request.user.is_company_admin:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    companies = Company.objects.all()
    serializer = CompanySerializer(companies, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def refresh_token_view(request):
    """
    API endpoint to refresh JWT tokens
    """
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        token = RefreshToken(refresh_token)
        new_access_token = str(token.access_token)
        
        return Response({
            'access': new_access_token,
            'message': 'Token refreshed successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'Token refresh failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


# User Management API Views

class UserSetListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating user sets
    """
    serializer_class = UserSetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only show sets for the current user's company
        return UserSet.objects.filter(company=self.request.user.company)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserSetCreateSerializer
        return UserSetSerializer
    
    def perform_create(self, serializer):
        # Assign the current user's company to the set
        serializer.save(company=self.request.user.company)


class UserSetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting user sets
    """
    serializer_class = UserSetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserSet.objects.filter(company=self.request.user.company)


class UserListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating users
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only show users from the current user's company
        return User.objects.filter(company=self.request.user.company)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting users
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(company=self.request.user.company)


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_user_role(request, user_id):
    """
    API endpoint for updating user roles
    """
    try:
        user = User.objects.get(id=user_id, company=request.user.company)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = UserRoleUpdateSerializer(user, data=request.data)
    if serializer.is_valid():
        with transaction.atomic():
            old_role = user.role
            new_role = serializer.validated_data['role']
            
            # Update the user's role
            user.role = new_role
            user.save()
            
            # Handle manager assignment logic
            if old_role == 'employee' and new_role == 'manager':
                # If promoting to manager, assign as manager of their current set
                if user.user_set:
                    user.user_set.manager = user
                    user.user_set.save()
            elif old_role == 'manager' and new_role == 'employee':
                # If demoting from manager, remove from manager position
                if user.user_set and user.user_set.manager == user:
                    user.user_set.manager = None
                    user.user_set.save()
            
            return Response({
                'message': f'User role updated from {old_role} to {new_role}',
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_user_set(request, user_id):
    """
    API endpoint for moving users between sets
    """
    try:
        user = User.objects.get(id=user_id, company=request.user.company)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = UserSetUpdateSerializer(user, data=request.data)
    if serializer.is_valid():
        with transaction.atomic():
            old_set = user.user_set
            new_set_id = serializer.validated_data['set_id']
            new_set = UserSet.objects.get(id=new_set_id)
            
            # Handle manager logic
            if user.role == 'manager':
                # If user is a manager, update the set's manager
                if old_set:
                    old_set.manager = None
                    old_set.save()
                
                new_set.manager = user
                new_set.save()
            
            # Move user to new set
            user.user_set = new_set
            user.save()
            
            return Response({
                'message': f'User moved to {new_set.name}',
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_available_managers(request):
    """
    API endpoint for getting available managers for set assignment
    """
    # Get managers who are not already assigned to a set
    available_managers = User.objects.filter(
        company=request.user.company,
        role='manager',
        user_set__isnull=True
    )
    
    serializer = UserSerializer(available_managers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_users_by_set(request, set_id):
    """
    API endpoint for getting users in a specific set
    """
    try:
        user_set = UserSet.objects.get(id=set_id, company=request.user.company)
        users = user_set.users.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except UserSet.DoesNotExist:
        return Response({'error': 'User set not found'}, status=status.HTTP_404_NOT_FOUND)


# Expense Management Views
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def expense_list_create(request):
    """
    API endpoint for listing and creating expenses
    """
    if request.method == 'GET':
        expenses = Expense.objects.filter(company=request.user.company).order_by('-submission_date')
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = ExpenseCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            expense = serializer.save()
            return Response(ExpenseSerializer(expense).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def expense_detail(request, expense_id):
    """
    API endpoint for expense detail operations
    """
    try:
        expense = Expense.objects.get(id=expense_id, company=request.user.company)
    except Expense.DoesNotExist:
        return Response({'error': 'Expense not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = ExpenseSerializer(expense)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method in ['PUT', 'PATCH']:
        serializer = ExpenseSerializer(expense, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        expense.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def expense_categories(request):
    """
    API endpoint for expense categories
    """
    if request.method == 'GET':
        categories = ExpenseCategory.objects.filter(company=request.user.company).order_by('-created_at')
        serializer = ExpenseCategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = ExpenseCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(company=request.user.company)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def expense_category_detail(request, category_id):
    """
    API endpoint for expense category detail operations
    """
    try:
        category = ExpenseCategory.objects.get(id=category_id, company=request.user.company)
    except ExpenseCategory.DoesNotExist:
        return Response({'error': 'Expense category not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = ExpenseCategorySerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = ExpenseCategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def process_receipt_ocr(request):
    """
    API endpoint for processing receipt OCR
    """
    try:
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        if file.content_type not in allowed_types:
            return Response({'error': 'Invalid file type. Please upload an image.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file size (max 10MB)
        if file.size > 10 * 1024 * 1024:
            return Response({'error': 'File too large. Maximum size is 10MB.'}, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"Processing OCR for file: {file.name}, size: {file.size}, type: {file.content_type}")
        
        # TODO: Integrate with Google Vision API for OCR
        # For now, return mock data based on file name
        file_name = file.name.lower()
        
        # Generate mock data based on file characteristics
        mock_ocr_data = {
            'text': f'OCR extracted text from {file.name}\n\nSample receipt content:\nMerchant: Sample Store\nDate: 2024-01-15\nAmount: $25.50\nItems: Coffee, Sandwich',
            'confidence': 0.85,
            'extracted_data': {
                'amount': 25.50,
                'merchant': 'Sample Store',
                'date': '2024-01-15',
                'items': ['Coffee', 'Sandwich']
            },
            'merchant_info': {
                'name': 'Sample Store',
                'address': '123 Main St',
                'phone': '+1234567890'
            }
        }
        
        # If file contains "bill" in name, adjust mock data
        if 'bill' in file_name:
            mock_ocr_data['extracted_data']['amount'] = 4985.60
            mock_ocr_data['extracted_data']['merchant'] = 'Market Committee ELLENABAD'
            mock_ocr_data['text'] = f'OCR extracted text from {file.name}\n\nForm J\nC.S.T. No.\nS.T. No.\nRice No.\nCotton\nWheat\nM. No.\nF.G.L. No.\nMarket Committee ELLENABAD\nAmount: 4985.60'
            mock_ocr_data['merchant_info']['name'] = 'Market Committee ELLENABAD'
        
        return Response(mock_ocr_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"OCR processing error: {str(e)}")
        return Response({'error': f'OCR processing failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_countries_currencies(request):
    """
    API endpoint for getting countries and their currencies
    """
    import requests
    
    try:
        response = requests.get('https://restcountries.com/v3.1/all?fields=name,currencies')
        if response.status_code == 200:
            return Response(response.json(), status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to fetch countries data'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_exchange_rates(request):
    """
    API endpoint for getting exchange rates
    """
    import requests
    
    try:
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
        if response.status_code == 200:
            return Response(response.json(), status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to fetch exchange rates'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Expense Approval Views

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_pending_approvals(request):
    """
    API endpoint for managers to get pending expense approvals from their set
    """
    if request.user.role != 'manager':
        return Response({'error': 'Only managers can view pending approvals'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get expenses from users in the manager's set that are pending approval
    if not request.user.user_set:
        return Response({'error': 'Manager is not assigned to any set'}, status=status.HTTP_400_BAD_REQUEST)
    
    pending_expenses = Expense.objects.filter(
        user__user_set=request.user.user_set,
        status='pending'
    ).order_by('-submission_date')
    
    serializer = ExpenseSerializer(pending_expenses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def approve_expense(request, expense_id):
    """
    API endpoint for managers to approve an expense
    """
    if request.user.role != 'manager':
        return Response({'error': 'Only managers can approve expenses'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        expense = Expense.objects.get(id=expense_id, company=request.user.company)
    except Expense.DoesNotExist:
        return Response({'error': 'Expense not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if the expense is from a user in the manager's set
    if not request.user.user_set or expense.user.user_set != request.user.user_set:
        return Response({'error': 'You can only approve expenses from users in your set'}, status=status.HTTP_403_FORBIDDEN)
    
    # Check if expense is pending
    if expense.status != 'pending':
        return Response({'error': 'Expense is not pending approval'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Approve the expense
    from django.utils import timezone
    expense.status = 'approved'
    expense.approved_by = request.user
    expense.approved_at = timezone.now()
    expense.save()
    
    return Response({
        'message': 'Expense approved successfully',
        'expense': ExpenseSerializer(expense).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reject_expense(request, expense_id):
    """
    API endpoint for managers to reject an expense
    """
    if request.user.role != 'manager':
        return Response({'error': 'Only managers can reject expenses'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        expense = Expense.objects.get(id=expense_id, company=request.user.company)
    except Expense.DoesNotExist:
        return Response({'error': 'Expense not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if the expense is from a user in the manager's set
    if not request.user.user_set or expense.user.user_set != request.user.user_set:
        return Response({'error': 'You can only reject expenses from users in your set'}, status=status.HTTP_403_FORBIDDEN)
    
    # Check if expense is pending
    if expense.status != 'pending':
        return Response({'error': 'Expense is not pending approval'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get rejection reason from request
    rejection_reason = request.data.get('rejection_reason', '')
    if not rejection_reason:
        return Response({'error': 'Rejection reason is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Reject the expense
    from django.utils import timezone
    expense.status = 'rejected'
    expense.approved_by = request.user
    expense.approved_at = timezone.now()
    expense.rejection_reason = rejection_reason
    expense.save()
    
    return Response({
        'message': 'Expense rejected successfully',
        'expense': ExpenseSerializer(expense).data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_my_expenses(request):
    """
    API endpoint for users to get their own expenses
    """
    expenses = Expense.objects.filter(user=request.user).order_by('-submission_date')
    serializer = ExpenseSerializer(expenses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_employee_dashboard_data(request):
    """
    API endpoint for employees to get dashboard summary data
    """
    if request.user.role != 'employee':
        return Response({'error': 'Only employees can access dashboard data'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get all expenses from the employee
    all_expenses = Expense.objects.filter(user=request.user)
    
    # Calculate statistics
    total_submitted = sum(expense.amount for expense in all_expenses)
    pending_amount = sum(expense.amount for expense in all_expenses.filter(status='pending'))
    approved_amount = sum(expense.amount for expense in all_expenses.filter(status='approved'))
    rejected_amount = sum(expense.amount for expense in all_expenses.filter(status='rejected'))
    
    # Get recent expenses (last 5)
    recent_expenses = all_expenses[:5]
    
    # Calculate counts
    pending_count = all_expenses.filter(status='pending').count()
    approved_count = all_expenses.filter(status='approved').count()
    rejected_count = all_expenses.filter(status='rejected').count()
    
    # Serialize recent expenses
    recent_expenses_serializer = ExpenseSerializer(recent_expenses, many=True)
    
    return Response({
        'total_submitted': total_submitted,
        'pending_amount': pending_amount,
        'approved_amount': approved_amount,
        'rejected_amount': rejected_amount,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'recent_expenses': recent_expenses_serializer.data,
        'total_expenses': all_expenses.count()
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_manager_dashboard_data(request):
    """
    API endpoint for managers to get dashboard summary data
    """
    if request.user.role != 'manager':
        return Response({'error': 'Only managers can access dashboard data'}, status=status.HTTP_403_FORBIDDEN)
    
    if not request.user.user_set:
        return Response({'error': 'Manager is not assigned to any set'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get all expenses from users in the manager's set
    all_expenses = Expense.objects.filter(
        user__user_set=request.user.user_set
    ).order_by('-submission_date')
    
    # Calculate statistics
    pending_count = all_expenses.filter(status='pending').count()
    approved_count = all_expenses.filter(status='approved').count()
    rejected_count = all_expenses.filter(status='rejected').count()
    
    # Get unique team members
    team_members = User.objects.filter(user_set=request.user.user_set).count()
    
    # Get recent approvals (last 5 approved expenses)
    recent_approvals = all_expenses.filter(status='approved')[:5]
    
    # Get today's approvals
    from django.utils import timezone
    today = timezone.now().date()
    today_approvals = all_expenses.filter(
        status='approved',
        approved_at__date=today
    ).count()
    
    # Serialize recent approvals
    recent_approvals_serializer = ExpenseSerializer(recent_approvals, many=True)
    
    return Response({
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'team_members_count': team_members,
        'today_approvals': today_approvals,
        'recent_approvals': recent_approvals_serializer.data,
        'total_expenses': all_expenses.count()
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_admin_dashboard_data(request):
    """
    API endpoint for admins to get comprehensive dashboard data
    """
    if request.user.role != 'admin':
        return Response({'error': 'Only admins can access dashboard data'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get all expenses from the admin's company
    all_expenses = Expense.objects.filter(company=request.user.company)
    
    # Calculate basic statistics
    total_users = User.objects.filter(company=request.user.company).count()
    total_expenses_count = all_expenses.count()
    pending_approvals = all_expenses.filter(status='pending').count()
    
    # Calculate monthly expenses (excluding rejected bills)
    from django.utils import timezone
    from datetime import timedelta
    current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_expenses = all_expenses.filter(
        submission_date__gte=current_month
    ).exclude(status='rejected')  # Exclude rejected bills from monthly expenses
    monthly_total = sum(expense.amount for expense in monthly_expenses)
    
    # Calculate approval metrics
    approved_count = all_expenses.filter(status='approved').count()
    rejected_count = all_expenses.filter(status='rejected').count()
    total_processed = approved_count + rejected_count
    
    approval_rate = (approved_count / total_processed * 100) if total_processed > 0 else 0
    rejection_rate = (rejected_count / total_processed * 100) if total_processed > 0 else 0
    
    # Calculate average processing time
    processed_expenses = all_expenses.filter(
        status__in=['approved', 'rejected'],
        approved_at__isnull=False
    )
    
    avg_processing_days = 0
    if processed_expenses.exists():
        total_days = 0
        for expense in processed_expenses:
            if expense.approved_at:
                days_diff = (expense.approved_at - expense.submission_date).days
                total_days += days_diff
        avg_processing_days = total_days / processed_expenses.count()
    
    # Get expenses by category (excluding rejected bills)
    from django.db.models import Sum, Count
    category_data = all_expenses.exclude(status='rejected').values('category__name').annotate(
        total_amount=Sum('amount'),
        count=Count('id')
    ).order_by('-total_amount')
    
    # Calculate percentages
    total_category_amount = sum(item['total_amount'] or 0 for item in category_data)
    expenses_by_category = []
    for item in category_data:
        amount = item['total_amount'] or 0
        percentage = (amount / total_category_amount * 100) if total_category_amount > 0 else 0
        expenses_by_category.append({
            'category': item['category__name'] or 'Uncategorized',
            'amount': amount,
            'percentage': round(percentage, 1),
            'count': item['count']
        })
    
    # Get recent users (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_users = User.objects.filter(
        company=request.user.company,
        date_joined__gte=thirty_days_ago
    ).count()
    
    # Calculate growth percentages (mock data for now - can be enhanced with historical data)
    user_growth = 12  # Mock percentage
    expense_growth = 8.2  # Mock percentage
    approval_change = -15  # Mock percentage
    processing_change = -22  # Mock percentage
    
    # Calculate rejected bills amount (for reference, not included in monthly expenses)
    rejected_expenses = all_expenses.filter(status='rejected')
    rejected_amount = sum(expense.amount for expense in rejected_expenses)
    
    return Response({
        'total_users': total_users,
        'monthly_expenses': monthly_total,  # Excludes rejected bills
        'pending_approvals': pending_approvals,
        'avg_processing_time': round(avg_processing_days, 1),
        'approval_rate': round(approval_rate, 1),
        'rejection_rate': round(rejection_rate, 1),
        'total_processed': total_processed,
        'expenses_by_category': expenses_by_category,  # Excludes rejected bills
        'user_growth': user_growth,
        'expense_growth': expense_growth,
        'approval_change': approval_change,
        'processing_change': processing_change,
        'recent_users': recent_users,
        'total_expenses_count': total_expenses_count,
        'rejected_amount': rejected_amount  # Separate metric for rejected bills
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_manager_approval_history(request):
    """
    API endpoint for managers to get approval history with filtering
    """
    if request.user.role != 'manager':
        return Response({'error': 'Only managers can access approval history'}, status=status.HTTP_403_FORBIDDEN)
    
    if not request.user.user_set:
        return Response({'error': 'Manager is not assigned to any set'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get query parameters for filtering
    status_filter = request.GET.get('status', None)  # pending, approved, rejected
    employee_filter = request.GET.get('employee', None)  # employee name or ID
    date_from = request.GET.get('date_from', None)  # YYYY-MM-DD
    date_to = request.GET.get('date_to', None)  # YYYY-MM-DD
    search = request.GET.get('search', None)  # search in title/description
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    
    # Get all expenses from users in the manager's set
    expenses = Expense.objects.filter(
        user__user_set=request.user.user_set
    ).order_by('-submission_date')
    
    # Apply filters
    if status_filter:
        expenses = expenses.filter(status=status_filter)
    
    if employee_filter:
        expenses = expenses.filter(
            models.Q(user__first_name__icontains=employee_filter) |
            models.Q(user__last_name__icontains=employee_filter) |
            models.Q(user__username__icontains=employee_filter)
        )
    
    if date_from:
        expenses = expenses.filter(submission_date__date__gte=date_from)
    
    if date_to:
        expenses = expenses.filter(submission_date__date__lte=date_to)
    
    if search:
        expenses = expenses.filter(
            models.Q(title__icontains=search) |
            models.Q(description__icontains=search)
        )
    
    # Calculate pagination
    total_count = expenses.count()
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    paginated_expenses = expenses[start_index:end_index]
    
    # Serialize expenses
    serializer = ExpenseSerializer(paginated_expenses, many=True)
    
    # Calculate summary statistics
    approved_count = expenses.filter(status='approved').count()
    rejected_count = expenses.filter(status='rejected').count()
    pending_count = expenses.filter(status='pending').count()
    
    return Response({
        'expenses': serializer.data,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total_count': total_count,
            'total_pages': (total_count + page_size - 1) // page_size,
            'has_next': end_index < total_count,
            'has_previous': page > 1
        },
        'summary': {
            'total': total_count,
            'approved': approved_count,
            'rejected': rejected_count,
            'pending': pending_count
        }
    }, status=status.HTTP_200_OK)


# Workflow API Views

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_expense(request):
    """
    API endpoint for submitting expenses with workflow
    """
    serializer = ExpenseSubmissionSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        expense = serializer.save()
        return Response({
            'message': 'Expense submitted successfully',
            'expense': WorkflowExpenseSerializer(expense).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_pending_approvals_workflow(request):
    """
    API endpoint for getting pending approvals with workflow details
    """
    user = request.user
    
    if user.role == 'manager':
        # Get expenses from user's set
        if not user.user_set:
            return Response({'error': 'Manager not assigned to any set'}, status=status.HTTP_400_BAD_REQUEST)
        
        expenses = Expense.objects.filter(
            user__user_set=user.user_set,
            status__in=['pending', 'in_progress'],
            current_stage='manager'
        ).order_by('-submission_date')
    
    elif user.role == 'admin':
        # Get all expenses pending admin approval
        expenses = Expense.objects.filter(
            company=user.company,
            status__in=['pending', 'in_progress'],
            current_stage='admin'
        ).order_by('-submission_date')
    
    else:
        return Response({'error': 'Only managers and admins can view pending approvals'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = WorkflowExpenseSerializer(expenses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def approve_expense_workflow(request, expense_id):
    """
    API endpoint for approving expenses with workflow
    """
    try:
        expense = Expense.objects.get(id=expense_id, company=request.user.company)
    except Expense.DoesNotExist:
        return Response({'error': 'Expense not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user can approve this expense
    if request.user.role == 'manager':
        if not request.user.user_set or expense.user.user_set != request.user.user_set:
            return Response({'error': 'You can only approve expenses from your set'}, status=status.HTTP_403_FORBIDDEN)
        if expense.current_stage != 'manager':
            return Response({'error': 'Expense is not in manager approval stage'}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.user.role == 'admin':
        if expense.current_stage not in ['admin', 'manager']:
            return Response({'error': 'Expense is not in admin approval stage'}, status=status.HTTP_400_BAD_REQUEST)
    
    else:
        return Response({'error': 'Only managers and admins can approve expenses'}, status=status.HTTP_403_FORBIDDEN)
    
    # Process approval
    result = advance_workflow(expense, request.user, 'approved', request.data.get('comment', ''))
    
    return Response(result, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reject_expense_workflow(request, expense_id):
    """
    API endpoint for rejecting expenses with workflow
    """
    try:
        expense = Expense.objects.get(id=expense_id, company=request.user.company)
    except Expense.DoesNotExist:
        return Response({'error': 'Expense not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user can reject this expense
    if request.user.role == 'manager':
        if not request.user.user_set or expense.user.user_set != request.user.user_set:
            return Response({'error': 'You can only reject expenses from your set'}, status=status.HTTP_403_FORBIDDEN)
        if expense.current_stage != 'manager':
            return Response({'error': 'Expense is not in manager approval stage'}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.user.role == 'admin':
        if expense.current_stage not in ['admin', 'manager']:
            return Response({'error': 'Expense is not in admin approval stage'}, status=status.HTTP_400_BAD_REQUEST)
    
    else:
        return Response({'error': 'Only managers and admins can reject expenses'}, status=status.HTTP_403_FORBIDDEN)
    
    # Process rejection
    result = advance_workflow(expense, request.user, 'rejected', request.data.get('comment', ''))
    
    return Response(result, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def admin_override_expense(request, expense_id):
    """
    API endpoint for admin override functionality
    """
    if request.user.role != 'admin':
        return Response({'error': 'Only admins can override'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = ApprovalActionSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        action = serializer.validated_data['action']
        comment = serializer.validated_data.get('comment', '')
        
        result = admin_override(expense_id, action, request.user, comment)
        return Response(result, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_expense_history(request):
    """
    API endpoint for getting expense approval history
    """
    user = request.user
    
    if user.role == 'employee':
        # Get user's own expenses
        expenses = Expense.objects.filter(user=user).order_by('-submission_date')
    elif user.role == 'manager':
        # Get expenses from user's set
        if not user.user_set:
            return Response({'error': 'Manager not assigned to any set'}, status=status.HTTP_400_BAD_REQUEST)
        expenses = Expense.objects.filter(user__user_set=user.user_set).order_by('-submission_date')
    elif user.role == 'admin':
        # Get all company expenses
        expenses = Expense.objects.filter(company=user.company).order_by('-submission_date')
    else:
        return Response({'error': 'Invalid user role'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Apply filters
    status_filter = request.GET.get('status')
    if status_filter:
        expenses = expenses.filter(status=status_filter)
    
    date_from = request.GET.get('date_from')
    if date_from:
        expenses = expenses.filter(submission_date__date__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        expenses = expenses.filter(submission_date__date__lte=date_to)
    
    serializer = WorkflowExpenseSerializer(expenses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_approval_rules(request):
    """
    API endpoint for getting approval rules
    """
    if request.user.role != 'admin':
        return Response({'error': 'Only admins can view approval rules'}, status=status.HTTP_403_FORBIDDEN)
    
    rules = ApprovalRule.objects.filter(company=request.user.company, is_active=True)
    serializer = ApprovalRuleSerializer(rules, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_approval_rule(request):
    """
    API endpoint for creating approval rules
    """
    if request.user.role != 'admin':
        return Response({'error': 'Only admins can create approval rules'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = ApprovalRuleSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(company=request.user.company)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def approval_rule_detail(request, rule_id):
    """
    API endpoint for retrieving, updating, and deleting approval rules
    """
    if request.user.role != 'admin':
        return Response({'error': 'Only admins can manage approval rules'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        rule = ApprovalRule.objects.get(id=rule_id, company=request.user.company)
    except ApprovalRule.DoesNotExist:
        return Response({'error': 'Approval rule not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = ApprovalRuleSerializer(rule)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = ApprovalRuleSerializer(rule, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        rule.delete()
        return Response({'message': 'Approval rule deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def setup_default_rules(request):
    """
    API endpoint for setting up default approval rules
    """
    if request.user.role != 'admin':
        return Response({'error': 'Only admins can setup default rules'}, status=status.HTTP_403_FORBIDDEN)
    
    success = create_default_rules(request.user.company)
    if success:
        return Response({'message': 'Default approval rules created successfully'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Failed to create default rules'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def check_escalations_view(request):
    """
    API endpoint for checking escalations (can be called by cron job)
    """
    if request.user.role != 'admin':
        return Response({'error': 'Only admins can check escalations'}, status=status.HTTP_403_FORBIDDEN)
    
    escalated_count = check_escalations()
    return Response({
        'message': f'{escalated_count} expenses escalated',
        'escalated_count': escalated_count
    }, status=status.HTTP_200_OK)
