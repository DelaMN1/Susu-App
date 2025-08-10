from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Group, Membership, Transaction

# Create blueprint
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
@login_required
def index():
    """Display user dashboard with groups and transactions"""
    # Get user's memberships and associated groups
    memberships = Membership.query.filter_by(user_id=current_user.id).all()
    
    # Get recent transactions for the user
    transactions = []
    for membership in memberships:
        membership_transactions = Transaction.query.filter_by(membership_id=membership.id).order_by(Transaction.timestamp.desc()).all()
        transactions.extend(membership_transactions)
    
    # Sort transactions by timestamp (most recent first) and limit to 10
    transactions = sorted(transactions, key=lambda x: x.timestamp, reverse=True)[:10]
    
    # Prepare data for the template
    user_groups = []
    total_savings = 0
    next_payout_date = None
    
    for membership in memberships:
        group = membership.group
        
        # Calculate user's contribution in this group
        contributions = Transaction.query.filter_by(
            membership_id=membership.id,
            tx_type='contribution'
        ).all()
        
        group_contribution = sum(float(tx.amount) for tx in contributions)
        total_savings += group_contribution
        
        # Format group data for template
        group_data = {
            'id': group.id,
            'name': group.name,
            'description': group.description or '',
            'status': group.status,
            'contribution_amount': float(group.weekly_amount),
            'frequency': 'weekly',  # Hardcoded for now
            'member_count': group.memberships.count(),
            'user_position': membership.payout_order,
            'current_cycle': group.current_cycle,
            'total_cycles': group.cycle_size,
            'next_payment_date': '2023-08-15'  # Placeholder - would be calculated in real app
        }
        
        user_groups.append(group_data)
    
    # For demo purposes, use a placeholder for next payout date and amount
    next_payout = None
    if user_groups:
        next_payment_date = min(group['next_payment_date'] for group in user_groups)
        # Find the group with the earliest payment date
        for group in user_groups:
            if group['next_payment_date'] == next_payment_date:
                next_payout = {
                    'amount': group['contribution_amount'],
                    'date': next_payment_date
                }
                break
    
    return render_template(
        'dashboard.html',
        user_groups=user_groups,
        total_savings=total_savings,
        next_payout=next_payout,
        active_groups_count=len(user_groups),
        transactions=transactions
    )