from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.validators import MinValueValidator
from decimal import Decimal


class Company(models.Model):
    """Company model for storing company information"""
    name = models.CharField(max_length=200, unique=True)
    address = models.TextField()
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    email = models.EmailField(unique=True)
    website = models.URLField(blank=True, null=True)
    industry = models.CharField(max_length=100)
    size = models.CharField(
        max_length=20,
        choices=[
            ('1-10', '1-10 employees'),
            ('11-50', '11-50 employees'),
            ('51-200', '51-200 employees'),
            ('201-500', '201-500 employees'),
            ('500+', '500+ employees'),
        ]
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Companies"


class UserSet(models.Model):
    """User Set model for grouping users with managers and employees"""
    name = models.CharField(max_length=200)
    manager = models.ForeignKey('User', on_delete=models.CASCADE, related_name='managed_sets', null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='user_sets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (Manager: {self.manager})"

    class Meta:
        verbose_name = "User Set"
        verbose_name_plural = "User Sets"


class User(AbstractUser):
    """Extended User model with company relationship and user sets"""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('employee', 'Employee'),
    ]
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    user_set = models.ForeignKey(UserSet, on_delete=models.SET_NULL, related_name='users', null=True, blank=True)
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    is_company_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class ExpenseCategory(models.Model):
    """Expense category model"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='expense_categories')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Expense Category"
        verbose_name_plural = "Expense Categories"


class Expense(models.Model):
    """Expense model for storing expense information"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('under_review', 'Under Review'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Basic Information
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='expenses')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Financial Information
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    currency = models.CharField(max_length=3, default='USD')  # ISO currency code
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    base_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Amount in company's base currency
    
    # Categorization
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    
    # Dates
    expense_date = models.DateField()
    submission_date = models.DateTimeField(auto_now_add=True)
    
    # Status and Approval
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Workflow fields
    urgent = models.BooleanField(default=False)
    current_stage = models.CharField(max_length=20, default='manager', help_text="Current approval stage")
    approval_rule = models.ForeignKey('ApprovalRule', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Auto-escalation fields
    escalation_date = models.DateTimeField(null=True, blank=True, help_text="When to escalate if not approved")
    escalated = models.BooleanField(default=False)
    
    # Approval Information
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_expenses')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # OCR and AI Information
    ocr_extracted_data = models.JSONField(null=True, blank=True)  # Store OCR extracted data
    ai_confidence_score = models.FloatField(null=True, blank=True)  # AI confidence score
    is_ai_filled = models.BooleanField(default=False)  # Whether data was auto-filled by AI
    
    # Additional Information
    tags = models.JSONField(default=list, blank=True)  # Store tags as JSON array
    notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.amount} {self.currency}"
    
    class Meta:
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"
        ordering = ['-submission_date']


class Receipt(models.Model):
    """Receipt model for storing receipt information and files"""
    expense = models.OneToOneField(Expense, on_delete=models.CASCADE, related_name='receipt')
    
    # File Information
    file = models.FileField(upload_to='receipts/%Y/%m/%d/')
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()  # Size in bytes
    file_type = models.CharField(max_length=100)  # MIME type
    
    # OCR Information
    ocr_text = models.TextField(blank=True, null=True)  # Raw OCR text
    ocr_confidence = models.FloatField(null=True, blank=True)  # OCR confidence score
    ocr_processed_at = models.DateTimeField(null=True, blank=True)
    
    # Extracted Information
    merchant_name = models.CharField(max_length=200, blank=True, null=True)
    merchant_address = models.TextField(blank=True, null=True)
    merchant_phone = models.CharField(max_length=50, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Receipt for {self.expense.title}"
    
    class Meta:
        verbose_name = "Receipt"
        verbose_name_plural = "Receipts"


class ApprovalRule(models.Model):
    """Approval rule model for defining approval workflows"""
    name = models.CharField(max_length=200)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sequence = models.JSONField(help_text="List of approval roles in sequence")
    percentage_required = models.IntegerField(default=100, help_text="Percentage of approvers required")
    admin_override = models.BooleanField(default=True)
    urgent_bypass = models.BooleanField(default=True, help_text="Skip manager for urgent expenses")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='approval_rules')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.min_amount}-{self.max_amount or '∞'})"

    class Meta:
        ordering = ['min_amount']


class ApprovalRecord(models.Model):
    """Approval record model for tracking approval history"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('overridden', 'Overridden'),
    ]
    
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='approval_records')
    approver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approval_records')
    role = models.CharField(max_length=20, choices=User.ROLE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    comment = models.TextField(blank=True, null=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.approver.username} - {self.expense.title} - {self.status}"

    class Meta:
        ordering = ['-created_at']
