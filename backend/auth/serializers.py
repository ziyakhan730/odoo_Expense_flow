from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from .models import User, Company, UserSet, Expense, ExpenseCategory, Receipt


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for Company model"""
    
    class Meta:
        model = Company
        fields = ['id', 'name', 'address', 'phone', 'email', 'website', 'industry', 'size', 'description', 'created_at', 'is_active']
        read_only_fields = ['id', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    company_data = CompanySerializer(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm', 'phone', 'role', 'company_data']
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def create(self, validated_data):
        company_data = validated_data.pop('company_data', None)
        password_confirm = validated_data.pop('password_confirm')
        
        # Create company if company_data is provided
        company = None
        if company_data:
            company = Company.objects.create(**company_data)
            validated_data['company'] = company
            validated_data['is_company_admin'] = True
            validated_data['role'] = 'admin'
        
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    company = CompanySerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'company', 'phone', 'is_company_admin', 'created_at']
        read_only_fields = ['id', 'created_at']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer that includes user data and supports email login"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Allow email as username field
        self.fields['username'] = serializers.CharField(required=False)
        self.fields['email'] = serializers.EmailField(required=False)
    
    def validate(self, attrs):
        # Handle both username and email login
        username = attrs.get('username')
        email = attrs.get('email')
        
        if email and not username:
            # Try to find user by email
            try:
                user = User.objects.get(email=email)
                attrs['username'] = user.username
            except User.DoesNotExist:
                raise serializers.ValidationError('No active account found with the given credentials.')
        elif not username:
            raise serializers.ValidationError('Username or email is required.')
        
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include username and password.')
        
        return attrs


class UserSetSerializer(serializers.ModelSerializer):
    """Serializer for UserSet model"""
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True)
    manager_email = serializers.CharField(source='manager.email', read_only=True)
    employees_count = serializers.SerializerMethodField()
    employees = serializers.SerializerMethodField()
    
    class Meta:
        model = UserSet
        fields = ['id', 'name', 'manager', 'manager_name', 'manager_email', 'employees_count', 'employees', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_employees_count(self, obj):
        return obj.users.filter(role='employee').count()
    
    def get_employees(self, obj):
        employees = obj.users.filter(role='employee')
        return UserSerializer(employees, many=True).data


class UserSetCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating UserSet without requiring manager assignment"""
    manager_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = UserSet
        fields = ['id', 'name', 'manager_id', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_manager_id(self, value):
        if value is not None:
            try:
                manager = User.objects.get(id=value)
                if manager.role != 'manager':
                    raise serializers.ValidationError("Selected user is not a manager.")
                if manager.user_set and manager.user_set.manager == manager:
                    raise serializers.ValidationError("This manager is already assigned to another set.")
                return value
            except User.DoesNotExist:
                raise serializers.ValidationError("Manager not found.")
        return value
    
    def create(self, validated_data):
        manager_id = validated_data.pop('manager_id', None)
        
        with transaction.atomic():
            user_set = UserSet.objects.create(**validated_data)
            
            if manager_id:
                manager = User.objects.get(id=manager_id)
                user_set.manager = manager
                user_set.save()
                
                # Assign manager to the set
                manager.user_set = user_set
                manager.save()
        
        # Return the full set data
        return UserSetSerializer(user_set).data


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users and assigning to sets"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    set_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'role', 'set_id', 'phone', 'user_set', 'company', 'is_company_admin', 'created_at']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def validate_set_id(self, value):
        if value is not None:
            try:
                user_set = UserSet.objects.get(id=value)
                return value
            except UserSet.DoesNotExist:
                raise serializers.ValidationError("User set not found.")
        return value
    
    def create(self, validated_data):
        set_id = validated_data.pop('set_id', None)
        
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            if set_id:
                user_set = UserSet.objects.get(id=set_id)
                user.user_set = user_set
                user.company = user_set.company
            else:
                # Assign to the same company as the admin
                user.company = self.context['request'].user.company
            user.save()
        
        # Return the user instance
        return user


class UserRoleUpdateSerializer(serializers.Serializer):
    """Serializer for updating user roles"""
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)
    
    def validate_role(self, value):
        user = self.instance
        current_role = user.role
        new_role = value
        
        # If changing from employee to manager
        if current_role == 'employee' and new_role == 'manager':
            if user.user_set and user.user_set.manager:
                raise serializers.ValidationError("This set already has a manager. Please reassign the current manager first.")
        
        # If changing from manager to employee
        elif current_role == 'manager' and new_role == 'employee':
            if user.user_set:
                # Check if there are other managers in the set
                other_managers = User.objects.filter(user_set=user.user_set, role='manager').exclude(id=user.id)
                if not other_managers.exists():
                    raise serializers.ValidationError("Cannot demote the only manager. Please assign a new manager first.")
        
        return value


class UserSetUpdateSerializer(serializers.Serializer):
    """Serializer for moving users between sets"""
    set_id = serializers.IntegerField()
    
    def validate_set_id(self, value):
        try:
            user_set = UserSet.objects.get(id=value)
            return value
        except UserSet.DoesNotExist:
            raise serializers.ValidationError("User set not found.")
    
    def validate(self, attrs):
        user = self.instance
        new_set_id = attrs['set_id']
        
        # If user is a manager, check if the new set already has a manager
        if user.role == 'manager':
            new_set = UserSet.objects.get(id=new_set_id)
            if new_set.manager and new_set.manager != user:
                raise serializers.ValidationError("The target set already has a manager.")
        
        return attrs


# Expense Management Serializers
class ExpenseCategorySerializer(serializers.ModelSerializer):
    """Serializer for expense categories"""
    class Meta:
        model = ExpenseCategory
        fields = ['id', 'name', 'description', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class ReceiptSerializer(serializers.ModelSerializer):
    """Serializer for receipt information"""
    class Meta:
        model = Receipt
        fields = ['id', 'file', 'file_name', 'file_size', 'file_type', 'ocr_text', 
                 'ocr_confidence', 'merchant_name', 'merchant_address', 'merchant_phone', 
                 'created_at']
        read_only_fields = ['id', 'created_at']


class ExpenseSerializer(serializers.ModelSerializer):
    """Serializer for expense information"""
    category = ExpenseCategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False)
    receipt = ReceiptSerializer(read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = Expense
        fields = ['id', 'title', 'description', 'amount', 'currency', 'exchange_rate', 
                 'base_amount', 'category', 'category_id', 'expense_date', 'status', 
                 'priority', 'approved_by', 'approved_by_name', 'approved_at', 
                 'rejection_reason', 'ocr_extracted_data', 'ai_confidence_score', 
                 'is_ai_filled', 'tags', 'notes', 'user_name', 'receipt', 
                 'submission_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'submission_date', 'created_at', 'updated_at', 
                           'approved_by', 'approved_at', 'exchange_rate', 'base_amount']


class ExpenseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating expenses"""
    category_id = serializers.IntegerField(required=False)
    receipt_file = serializers.FileField(write_only=True, required=False)
    
    class Meta:
        model = Expense
        fields = ['title', 'description', 'amount', 'currency', 'expense_date', 
                 'category_id', 'priority', 'tags', 'notes', 'receipt_file']
    
    def create(self, validated_data):
        receipt_file = validated_data.pop('receipt_file', None)
        category_id = validated_data.pop('category_id', None)
        
        # Set user and company from request context
        user = self.context['request'].user
        validated_data['user'] = user
        validated_data['company'] = user.company
        
        # Set category if provided
        if category_id:
            try:
                category = ExpenseCategory.objects.get(id=category_id, company=user.company)
                validated_data['category'] = category
            except ExpenseCategory.DoesNotExist:
                raise serializers.ValidationError("Invalid category ID")
        
        # Create expense
        expense = Expense.objects.create(**validated_data)
        
        # Handle receipt file if provided
        if receipt_file:
            Receipt.objects.create(
                expense=expense,
                file=receipt_file,
                file_name=receipt_file.name,
                file_size=receipt_file.size,
                file_type=receipt_file.content_type
            )
        
        return expense


class OCRDataSerializer(serializers.Serializer):
    """Serializer for OCR extracted data"""
    text = serializers.CharField()
    confidence = serializers.FloatField()
    extracted_data = serializers.JSONField()
    merchant_info = serializers.JSONField(required=False)
