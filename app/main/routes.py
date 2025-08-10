from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    # Pass current year to the template for footer copyright
    now = datetime.datetime.now()
    return render_template('index.html', now=now)


@main_bp.route('/favicon.ico')
def favicon():
    """Handle favicon requests"""
    return '', 204  # No content response