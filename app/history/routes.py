from flask import Blueprint, render_template
from flask_login import login_required, current_user

# Create blueprint
history_bp = Blueprint('history', __name__, url_prefix='/history')


@history_bp.route('/')
@login_required
def index():
    """History dashboard showing payment history and past groups"""
    # Mock data for demonstration
    payment_history = [
        {
            'group_name': 'Akwaaba Savings',
            'amount': '₵200',
            'date': '2024-01-08',
            'type': 'contribution'
        },
        {
            'group_name': 'Family Circle',
            'amount': '₵150',
            'date': '2024-01-01',
            'type': 'contribution'
        },
        {
            'group_name': 'Work Colleagues',
            'amount': '₵300',
            'date': '2023-12-25',
            'type': 'contribution'
        },
        {
            'group_name': 'Akwaaba Savings',
            'amount': '₵1,000',
            'date': '2023-12-18',
            'type': 'payout'
        }
    ]
    
    past_groups = [
        {
            'name': 'Work Colleagues',
            'total_contributed': '₵3,600',
            'total_received': '₵3,600',
            'start_date': '2023-01-15',
            'end_date': '2023-12-15',
            'status': 'completed'
        },
        {
            'name': 'University Friends',
            'total_contributed': '₵2,400',
            'total_received': '₵2,400',
            'start_date': '2022-06-01',
            'end_date': '2023-05-31',
            'status': 'completed'
        },
        {
            'name': 'Neighborhood Group',
            'total_contributed': '₵1,800',
            'total_received': '₵1,800',
            'start_date': '2022-01-01',
            'end_date': '2022-12-31',
            'status': 'completed'
        }
    ]
    
    return render_template('history/index.html', 
                         payment_history=payment_history,
                         past_groups=past_groups) 