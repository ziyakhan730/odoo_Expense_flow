"""
Approval workflow engine for expense management system
"""
import requests
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from django.db import transaction, models
from .models import Expense, ApprovalRule, ApprovalRecord, User, Company


def convert_currency(amount, from_currency, to_currency='USD'):
    """
    Convert currency using external API
    """
    try:
        if from_currency == to_currency:
            return float(amount)
        
        # Use exchangerate-api.com for currency conversion
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            rate = data['rates'].get(to_currency)
            if rate:
                converted_amount = float(amount) * rate
                return converted_amount
        
        # Fallback: return original amount if conversion fails
        return float(amount)
    except Exception as e:
        print(f"Currency conversion error: {e}")
        return float(amount)


def get_applicable_rule(amount, company, urgent=False):
    """
    Get the applicable approval rule based on amount and urgency
    """
    try:
        # If urgent and urgent_bypass is enabled, get the rule that skips manager
        if urgent:
            urgent_rule = ApprovalRule.objects.filter(
                company=company,
                is_active=True,
                urgent_bypass=True
            ).first()
            if urgent_rule:
                return urgent_rule
        
        # Find rule based on amount range
        rule = ApprovalRule.objects.filter(
            company=company,
            is_active=True,
            min_amount__lte=amount
        ).filter(
            models.Q(max_amount__gte=amount) | models.Q(max_amount__isnull=True)
        ).order_by('min_amount').first()
        
        return rule
    except Exception as e:
        print(f"Error getting applicable rule: {e}")
        return None


def calculate_approval_percentage(expense):
    """
    Calculate approval percentage for an expense
    """
    try:
        total_approvers = ApprovalRecord.objects.filter(
            expense=expense,
            role__in=['manager', 'admin']
        ).count()
        
        approved_count = ApprovalRecord.objects.filter(
            expense=expense,
            status='approved',
            role__in=['manager', 'admin']
        ).count()
        
        if total_approvers == 0:
            return 0
        
        return (approved_count / total_approvers) * 100
    except Exception as e:
        print(f"Error calculating approval percentage: {e}")
        return 0


def advance_workflow(expense, approver, action, comment=None):
    """
    Advance the workflow based on approval action
    """
    try:
        with transaction.atomic():
            # Create approval record
            approval_record = ApprovalRecord.objects.create(
                expense=expense,
                approver=approver,
                role=approver.role,
                status=action,
                comment=comment,
                approved_at=timezone.now() if action in ['approved', 'rejected'] else None
            )
            
            if action == 'rejected':
                # Reject the expense
                expense.status = 'rejected'
                expense.rejection_reason = comment
                expense.approved_by = approver
                expense.approved_at = timezone.now()
                expense.save()
                return {
                    'expense_id': expense.id,
                    'status': 'Rejected',
                    'current_stage': 'Completed',
                    'next_approver': None,
                    'approval_record_id': approval_record.id
                }
            
            elif action == 'approved':
                # Check if this completes the workflow
                if expense.approval_rule:
                    sequence = expense.approval_rule.sequence
                    current_stage_index = sequence.index(expense.current_stage) if expense.current_stage in sequence else 0
                    
                    # Check if we need to move to next stage
                    if current_stage_index < len(sequence) - 1:
                        next_stage = sequence[current_stage_index + 1]
                        expense.current_stage = next_stage
                        expense.status = 'in_progress'
                        expense.save()
                        
                        return {
                            'expense_id': expense.id,
                            'status': 'In Progress',
                            'current_stage': next_stage,
                            'next_approver': get_next_approver(expense, next_stage),
                            'approval_record_id': approval_record.id
                        }
                    else:
                        # Workflow complete
                        expense.status = 'approved'
                        expense.approved_by = approver
                        expense.approved_at = timezone.now()
                        expense.save()
                        
                        return {
                            'expense_id': expense.id,
                            'status': 'Approved',
                            'current_stage': 'Completed',
                            'next_approver': None,
                            'approval_record_id': approval_record.id
                        }
                else:
                    # No rule, just approve
                    expense.status = 'approved'
                    expense.approved_by = approver
                    expense.approved_at = timezone.now()
                    expense.save()
                    
                    return {
                        'expense_id': expense.id,
                        'status': 'Approved',
                        'current_stage': 'Completed',
                        'next_approver': None,
                        'approval_record_id': approval_record.id
                    }
            
            return {
                'expense_id': expense.id,
                'status': 'Error',
                'current_stage': expense.current_stage,
                'next_approver': None,
                'approval_record_id': approval_record.id
            }
    
    except Exception as e:
        print(f"Error advancing workflow: {e}")
        return {
            'expense_id': expense.id,
            'status': 'Error',
            'current_stage': expense.current_stage,
            'next_approver': None,
            'approval_record_id': None
        }


def get_next_approver(expense, stage):
    """
    Get the next approver for the given stage
    """
    try:
        if stage == 'manager':
            # Get manager from user's set
            if expense.user.user_set and expense.user.user_set.manager:
                return expense.user.user_set.manager.username
            return "Manager (Not Assigned)"
        elif stage == 'admin':
            # Get company admin
            admin = User.objects.filter(
                company=expense.company,
                role='admin',
                is_company_admin=True
            ).first()
            return admin.username if admin else "Admin (Not Found)"
        
        return "Unknown Stage"
    except Exception as e:
        print(f"Error getting next approver: {e}")
        return "Error"


def admin_override(expense_id, action, admin_user, comment=None):
    """
    Admin override functionality
    """
    try:
        expense = Expense.objects.get(id=expense_id)
        
        if admin_user.role != 'admin':
            return {
                'expense_id': expense.id,
                'status': 'Error',
                'message': 'Only admins can override'
            }
        
        with transaction.atomic():
            # Create override record
            approval_record = ApprovalRecord.objects.create(
                expense=expense,
                approver=admin_user,
                role='admin',
                status='overridden',
                comment=comment,
                approved_at=timezone.now()
            )
            
            if action == 'approve':
                expense.status = 'approved'
                expense.approved_by = admin_user
                expense.approved_at = timezone.now()
                expense.current_stage = 'completed'
            elif action == 'reject':
                expense.status = 'rejected'
                expense.rejection_reason = comment
                expense.approved_by = admin_user
                expense.approved_at = timezone.now()
                expense.current_stage = 'completed'
            
            expense.save()
            
            return {
                'expense_id': expense.id,
                'status': 'Overridden',
                'current_stage': 'Completed',
                'next_approver': None,
                'approval_record_id': approval_record.id
            }
    
    except Exception as e:
        print(f"Error in admin override: {e}")
        return {
            'expense_id': expense_id,
            'status': 'Error',
            'message': str(e)
        }


def setup_escalation(expense):
    """
    Setup auto-escalation for expense
    """
    try:
        # Set escalation date to 48 hours from now
        escalation_date = timezone.now() + timedelta(hours=48)
        expense.escalation_date = escalation_date
        expense.save()
        
        return escalation_date
    except Exception as e:
        print(f"Error setting up escalation: {e}")
        return None


def check_escalations():
    """
    Check for expenses that need escalation
    """
    try:
        now = timezone.now()
        expired_expenses = Expense.objects.filter(
            escalation_date__lte=now,
            escalated=False,
            status__in=['pending', 'in_progress']
        )
        
        escalated_count = 0
        for expense in expired_expenses:
            # Escalate to admin
            expense.current_stage = 'admin'
            expense.escalated = True
            expense.status = 'in_progress'
            expense.save()
            escalated_count += 1
        
        return escalated_count
    except Exception as e:
        print(f"Error checking escalations: {e}")
        return 0


def create_default_rules(company):
    """
    Create default approval rules for a company
    """
    try:
        # Rule 1: ≤ 5000 - Manager only
        ApprovalRule.objects.get_or_create(
            company=company,
            min_amount=0,
            max_amount=5000,
            defaults={
                'name': 'Low Amount - Manager Only',
                'sequence': ['manager'],
                'percentage_required': 100,
                'admin_override': True,
                'urgent_bypass': True
            }
        )
        
        # Rule 2: 5001-25000 - Manager → Admin
        ApprovalRule.objects.get_or_create(
            company=company,
            min_amount=5001,
            max_amount=25000,
            defaults={
                'name': 'Medium Amount - Manager to Admin',
                'sequence': ['manager', 'admin'],
                'percentage_required': 100,
                'admin_override': True,
                'urgent_bypass': True
            }
        )
        
        # Rule 3: > 25000 - Manager → Admin (with comment requirement)
        ApprovalRule.objects.get_or_create(
            company=company,
            min_amount=25001,
            defaults={
                'name': 'High Amount - Manager to Admin',
                'sequence': ['manager', 'admin'],
                'percentage_required': 100,
                'admin_override': True,
                'urgent_bypass': True
            }
        )
        
        return True
    except Exception as e:
        print(f"Error creating default rules: {e}")
        return False
