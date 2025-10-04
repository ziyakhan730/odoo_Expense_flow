from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from django.db import transaction
from .models import User, Company, UserSet, Expense, ExpenseCategory
from .serializers import (
    UserRegistrationSerializer, UserSerializer, LoginSerializer, CompanySerializer, 
    CustomTokenObtainPairSerializer, UserSetSerializer, UserSetCreateSerializer,
    UserCreateSerializer, UserRoleUpdateSerializer, UserSetUpdateSerializer , 
    ExpenseSerializer, ExpenseCreateSerializer, ExpenseCategorySerializer
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
