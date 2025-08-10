from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db, login_manager
import secrets
import string


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    """User model for authentication and profile information"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    groups_created = db.relationship('Group', backref='creator', lazy='dynamic')
    memberships = db.relationship('Membership', backref='user', lazy='dynamic')
    invitations_sent = db.relationship('GroupInvitation', backref='inviter', lazy='dynamic', foreign_keys='GroupInvitation.invited_by')
    
    @property
    def password(self):
        """Prevent password from being accessed"""
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        """Set password to a hashed password"""
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """Check if password matches the hashed password"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.full_name}>'


class Group(db.Model):
    """Group model for Susu savings groups"""
    __tablename__ = 'groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    cycle_size = db.Column(db.Integer, nullable=False)  # Number of members
    weekly_amount = db.Column(db.Numeric(10, 2), nullable=False)  # Amount per week
    status = db.Column(db.String(20), default='forming')  # FSM state
    current_cycle = db.Column(db.Integer, default=0)  # Current payment cycle
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    memberships = db.relationship('Membership', backref='group', lazy='dynamic')
    invitations = db.relationship('GroupInvitation', backref='group', lazy='dynamic')
    
    def __repr__(self):
        return f'<Group {self.name}>'
    
    @property
    def is_full(self):
        """Check if the group has reached its member limit"""
        return self.memberships.count() >= self.cycle_size
    
    @property
    def available_slots(self):
        """Get the number of available slots in the group"""
        return self.cycle_size - self.memberships.count()
    
    @property
    def total_amount(self):
        """Calculate the total amount to be collected in each cycle"""
        return self.weekly_amount * self.cycle_size
    
    @property
    def admin(self):
        """Get the admin (creator) of the group"""
        return User.query.get(self.created_by)
    
    def is_admin(self, user_id):
        """Check if a user is the admin of this group"""
        return self.created_by == user_id
    
    def can_delete(self, user_id):
        """Check if a user can delete this group"""
        return self.is_admin(user_id) and self.status == 'forming'
    
    def can_remove_member(self, user_id, member_id):
        """Check if a user can remove a member from this group"""
        return (self.is_admin(user_id) and 
                member_id != self.created_by and 
                self.status == 'forming')


class GroupInvitation(db.Model):
    """Invitation model for inviting users to join groups"""
    __tablename__ = 'group_invitations'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    invited_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    invitation_code = db.Column(db.String(32), unique=True, nullable=False)
    invited_email = db.Column(db.String(120))  # Optional
    invited_phone = db.Column(db.String(20))   # Optional
    invited_name = db.Column(db.String(100))   # Optional
    status = db.Column(db.String(20), default='pending')  # pending, accepted, expired, cancelled
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    accepted_at = db.Column(db.DateTime)
    accepted_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # Who accepted the invitation
    
    def __repr__(self):
        return f'<GroupInvitation {self.invitation_code}>'
    
    @classmethod
    def generate_invitation_code(cls):
        """Generate a unique invitation code"""
        while True:
            # Generate 8-character alphanumeric code
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            # Check if code already exists
            if not cls.query.filter_by(invitation_code=code).first():
                return code
    
    @classmethod
    def create_invitation(cls, group_id, invited_by, invited_email=None, invited_phone=None, invited_name=None, expires_in_hours=48):
        """Create a new invitation"""
        invitation = cls(
            group_id=group_id,
            invited_by=invited_by,
            invitation_code=cls.generate_invitation_code(),
            invited_email=invited_email,
            invited_phone=invited_phone,
            invited_name=invited_name,
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours)
        )
        return invitation
    
    @property
    def is_expired(self):
        """Check if the invitation has expired"""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if the invitation is valid and can be used"""
        return self.status == 'pending' and not self.is_expired
    
    def accept(self, user_id):
        """Accept the invitation"""
        self.status = 'accepted'
        self.accepted_at = datetime.utcnow()
        self.accepted_by = user_id


class Membership(db.Model):
    """Membership model for user participation in groups"""
    __tablename__ = 'memberships'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    payout_order = db.Column(db.Integer, nullable=False)  # Position in rotation
    has_paid_this_cycle = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='membership', lazy='dynamic')
    
    def __repr__(self):
        return f'<Membership User:{self.user_id} Group:{self.group_id}>'
    
    @property
    def is_current_recipient(self):
        """Check if this member is the current recipient in the rotation"""
        return self.payout_order == self.group.current_cycle


class Transaction(db.Model):
    """Transaction model for contributions and payouts"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    membership_id = db.Column(db.Integer, db.ForeignKey('memberships.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    tx_type = db.Column(db.String(20), nullable=False)  # 'contribution' or 'payout'
    reference = db.Column(db.String(100))  # Payment reference
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Transaction {self.tx_type} {self.amount}>'