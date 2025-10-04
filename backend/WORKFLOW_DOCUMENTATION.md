# Approval Workflow Engine Documentation

## Overview

The Approval Workflow Engine is a comprehensive system for managing expense approvals in the Expense Reimbursement Management System. It supports dynamic rule-based approvals, currency conversion, auto-escalation, and role-based access control.

## 🏗️ Architecture

### Core Components

1. **Models**
   - `ApprovalRule`: Defines approval workflows based on amount thresholds
   - `ApprovalRecord`: Tracks approval history and decisions
   - `Expense`: Enhanced with workflow fields (urgent, current_stage, escalation_date)

2. **Workflow Engine** (`auth/workflow.py`)
   - Currency conversion utilities
   - Rule evaluation logic
   - Workflow advancement functions
   - Auto-escalation system

3. **API Endpoints**
   - Expense submission with workflow
   - Approval/rejection actions
   - History and reporting
   - Admin override functionality

## 📋 Approval Rules

### Default Rules

| Rule ID | Amount Range | Approval Sequence | Description |
|---------|--------------|-------------------|-------------|
| R1 | ≤ $5,000 | Manager only | Low amount expenses |
| R2 | $5,001 - $25,000 | Manager → Admin | Medium amount expenses |
| R3 | > $25,000 | Manager → Admin | High amount expenses |

### Conditional Rules

- **Urgent Expenses**: Bypass manager, go directly to Admin
- **Multiple Managers**: Require 70% approval (configurable)
- **Admin Override**: Admins can approve/reject any expense

## 🔄 Workflow Process

### 1. Expense Submission
```
Employee submits expense → Currency conversion → Rule matching → Workflow initiation
```

### 2. Approval Stages
```
Manager Stage → Admin Stage (if required) → Final Approval
```

### 3. Status Transitions
- `pending` → `in_progress` → `approved`/`rejected`

## 🛠️ API Endpoints

### Expense Submission
```http
POST /api/auth/expenses/submit/
Content-Type: application/json

{
  "title": "Office Supplies",
  "description": "Purchase of office supplies",
  "amount": 2500.00,
  "currency": "USD",
  "expense_date": "2024-01-15",
  "urgent": false
}
```

### Get Pending Approvals
```http
GET /api/auth/expenses/pending/
Authorization: Bearer <token>
```

### Approve Expense
```http
POST /api/auth/expenses/{expense_id}/approve-workflow/
Content-Type: application/json
Authorization: Bearer <token>

{
  "comment": "Approved by manager"
}
```

### Reject Expense
```http
POST /api/auth/expenses/{expense_id}/reject-workflow/
Content-Type: application/json
Authorization: Bearer <token>

{
  "comment": "Insufficient documentation"
}
```

### Admin Override
```http
POST /api/auth/expenses/{expense_id}/override/
Content-Type: application/json
Authorization: Bearer <token>

{
  "action": "approve",
  "comment": "Admin override - urgent business need"
}
```

### Get Expense History
```http
GET /api/auth/expenses/history/?status=approved&date_from=2024-01-01
Authorization: Bearer <token>
```

## 💱 Currency Conversion

The system automatically converts expenses to the company's default currency using the ExchangeRate API:

```python
# Example conversion
amount_usd = convert_currency(1000, 'EUR', 'USD')
# Returns: 1085.50 (approximate)
```

### Supported Features
- Real-time exchange rates
- Fallback to original amount if conversion fails
- Automatic conversion on expense submission

## ⏰ Auto-Escalation

### Escalation Rules
- **Time Limit**: 48 hours for manager approval
- **Auto-Escalation**: Moves to admin if manager doesn't act
- **Cron Job**: Runs every hour to check escalations

### Setup Cron Job
```bash
# Add to crontab (runs every hour)
0 * * * * cd /path/to/project && python manage.py check_escalations
```

### Manual Escalation Check
```http
POST /api/auth/escalations/check/
Authorization: Bearer <admin_token>
```

## 🎯 Usage Examples

### 1. Low Amount Expense (≤ $5,000)
```python
# Employee submits
expense_data = {
    "title": "Office Supplies",
    "amount": 2500.00,
    "currency": "USD",
    "urgent": False
}

# Workflow: Employee → Manager → Approved
# No admin approval required
```

### 2. High Amount Expense (> $25,000)
```python
# Employee submits
expense_data = {
    "title": "Software License",
    "amount": 50000.00,
    "currency": "USD",
    "urgent": False
}

# Workflow: Employee → Manager → Admin → Approved
# Requires both manager and admin approval
```

### 3. Urgent Expense
```python
# Employee submits
expense_data = {
    "title": "Emergency Travel",
    "amount": 15000.00,
    "currency": "USD",
    "urgent": True
}

# Workflow: Employee → Admin → Approved
# Bypasses manager approval
```

## 📊 Response Format

### Approval Response
```json
{
  "expense_id": 123,
  "status": "Approved",
  "current_stage": "Completed",
  "next_approver": null,
  "approval_record_id": 456
}
```

### Workflow Status
```json
{
  "expense_id": 123,
  "status": "In Progress",
  "current_stage": "admin",
  "next_approver": "admin@company.com",
  "approval_percentage": 50.0
}
```

## 🔧 Configuration

### Setting Up Default Rules
```http
POST /api/auth/approval-rules/setup-default/
Authorization: Bearer <admin_token>
```

### Creating Custom Rules
```http
POST /api/auth/approval-rules/create/
Content-Type: application/json
Authorization: Bearer <admin_token>

{
  "name": "Custom Rule",
  "min_amount": 10000.00,
  "max_amount": 50000.00,
  "sequence": ["manager", "admin"],
  "percentage_required": 100,
  "admin_override": true,
  "urgent_bypass": true
}
```

## 🧪 Testing

### Run Test Script
```bash
python test_workflow.py
```

### Test Scenarios
1. ✅ Company and user registration
2. ✅ Default approval rules setup
3. ✅ Low amount expense (Manager only)
4. ✅ High amount expense (Manager → Admin)
5. ✅ Urgent expense (Admin only)
6. ✅ Admin override functionality
7. ✅ Expense history tracking

## 📈 Monitoring

### Key Metrics
- Approval rates by role
- Average processing time
- Escalation frequency
- Currency conversion success rate

### Dashboard Integration
The workflow system integrates with existing dashboards:
- Manager Dashboard: Shows pending approvals
- Admin Dashboard: Shows all company expenses
- Employee Dashboard: Shows personal expense history

## 🔒 Security

### Role-Based Access
- **Employees**: Can submit expenses, view own history
- **Managers**: Can approve expenses from their set
- **Admins**: Can approve any expense, override decisions

### Validation
- Amount thresholds enforced
- Currency conversion validated
- User permissions checked
- Audit trail maintained

## 🚀 Deployment

### Prerequisites
1. Django 4.0+
2. PostgreSQL (recommended)
3. Redis (for caching, optional)
4. Celery (for background tasks, optional)

### Environment Variables
```bash
# Currency conversion API
EXCHANGE_RATE_API_URL=https://api.exchangerate-api.com/v4/latest/

# Escalation settings
ESCALATION_HOURS=48
ESCALATION_CHECK_INTERVAL=3600  # seconds
```

### Database Setup
```bash
python manage.py migrate
python manage.py setup_default_rules  # Optional: setup via API
```

## 📝 Best Practices

### 1. Rule Design
- Keep rules simple and clear
- Test with various amount ranges
- Consider business requirements
- Document custom rules

### 2. Performance
- Use database indexes on amount fields
- Cache exchange rates
- Monitor escalation queries
- Optimize approval queries

### 3. Monitoring
- Track approval times
- Monitor escalation rates
- Alert on failed conversions
- Regular rule review

## 🐛 Troubleshooting

### Common Issues

1. **Currency Conversion Fails**
   - Check API connectivity
   - Verify currency codes
   - Review fallback logic

2. **Escalation Not Working**
   - Verify cron job setup
   - Check escalation_date field
   - Review timezone settings

3. **Approval Rules Not Applied**
   - Check rule configuration
   - Verify amount ranges
   - Review rule priority

### Debug Commands
```bash
# Check escalations manually
python manage.py check_escalations

# View approval rules
python manage.py shell
>>> from auth.models import ApprovalRule
>>> ApprovalRule.objects.all()
```

## 🔄 Future Enhancements

### Planned Features
1. **Multi-Currency Support**: Enhanced currency handling
2. **Advanced Rules**: Conditional logic, custom fields
3. **Notifications**: Email/SMS alerts for approvals
4. **Analytics**: Advanced reporting and insights
5. **Mobile API**: Optimized for mobile applications

### Integration Points
- **ERP Systems**: SAP, Oracle integration
- **Accounting Software**: QuickBooks, Xero
- **Payment Systems**: Stripe, PayPal
- **Document Management**: SharePoint, Google Drive

---

## 📞 Support

For technical support or feature requests, please contact the development team or create an issue in the project repository.

**Version**: 1.0.0  
**Last Updated**: January 2024  
**Maintainer**: Development Team
