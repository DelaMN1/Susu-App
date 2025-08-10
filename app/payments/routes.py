from flask import Blueprint, render_template
from flask_login import login_required, current_user

# Create blueprint
payments_bp = Blueprint('payments', __name__, url_prefix='/payments')


@payments_bp.route('/')
@login_required
def index():
    """Payments dashboard showing past and upcoming payments"""
    # Mock data for demonstration
    upcoming_payments = [
        {
            'group_name': 'Akwaaba Savings',
            'amount': '₵200',
            'due_date': '2024-01-15',
            'status': 'pending'
        },
        {
            'group_name': 'Family Circle',
            'amount': '₵150',
            'due_date': '2024-01-20',
            'status': 'pending'
        }
    ]
    
    past_payments = [
        {
            'group_name': 'Akwaaba Savings',
            'amount': '₵200',
            'date': '2024-01-08',
            'status': 'completed'
        },
        {
            'group_name': 'Family Circle',
            'amount': '₵150',
            'date': '2024-01-01',
            'status': 'completed'
        },
        {
            'group_name': 'Work Colleagues',
            'amount': '₵300',
            'date': '2023-12-25',
            'status': 'completed'
        }
    ]
    
    return render_template('payments/index.html', 
                         upcoming_payments=upcoming_payments,
                         past_payments=past_payments) 