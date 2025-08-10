from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Group, Membership, GroupInvitation, User
from app.groups.forms import CreateGroupForm
from app.groups.fsm import GroupStateMachine

# Create blueprint
groups_bp = Blueprint('groups', __name__, url_prefix='/groups')


@groups_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_group():
    """Create a new Susu group"""
    form = CreateGroupForm()
    if form.validate_on_submit():
        group = Group(
            name=form.name.data,
            description=form.description.data,
            created_by=current_user.id,
            cycle_size=form.cycle_size.data,
            weekly_amount=form.weekly_amount.data
        )
        
        db.session.add(group)
        db.session.commit()
        
        # Add creator as first member
        membership = Membership(
            user_id=current_user.id,
            group_id=group.id,
            payout_order=1  # Creator is first in line
        )
        
        db.session.add(membership)
        db.session.commit()
        
        flash(f'Group "{group.name}" created successfully!', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('create_group.html', form=form)


@groups_bp.route('/join/<int:group_id>', methods=['GET', 'POST'])
@login_required
def join_group(group_id):
    """Join an existing Susu group"""
    group = Group.query.get_or_404(group_id)
    
    # Check if user is already a member
    existing_membership = Membership.query.filter_by(
        user_id=current_user.id,
        group_id=group.id
    ).first()
    
    if existing_membership:
        flash('You are already a member of this group.', 'info')
        return redirect(url_for('dashboard.index'))
    
    # Check if group is in a state that allows joining
    if not GroupStateMachine.can_join(group.status):
        flash('This group is no longer accepting new members.', 'error')
        return redirect(url_for('dashboard.index'))
    
    # Check if group has available slots
    if group.is_full:
        flash('This group is already full.', 'error')
        return redirect(url_for('dashboard.index'))
    
    # Add user to group
    next_position = group.memberships.count() + 1
    membership = Membership(
        user_id=current_user.id,
        group_id=group.id,
        payout_order=next_position
    )
    
    db.session.add(membership)
    db.session.commit()
    
    flash(f'You have successfully joined {group.name}!', 'success')
    
    # Check if group is now full and can start
    if GroupStateMachine.can_start(group.status, group.memberships.count(), group.cycle_size):
        group.status = 'collecting'
        db.session.commit()
        flash(f'Group {group.name} is now complete and has started collecting contributions!', 'info')
    
    return redirect(url_for('dashboard.index'))


@groups_bp.route('/view/<int:group_id>')
@login_required
def view_group(group_id):
    """View details of a specific group"""
    group = Group.query.get_or_404(group_id)
    
    # Check if user is a member
    membership = Membership.query.filter_by(
        user_id=current_user.id,
        group_id=group.id
    ).first()
    
    if not membership and group.created_by != current_user.id:
        flash('You are not a member of this group.', 'error')
        return redirect(url_for('dashboard.index'))
    
    # Get all members
    memberships = Membership.query.filter_by(group_id=group.id).all()
    
    return render_template(
        'view_group.html',
        group=group,
        membership=membership,
        memberships=memberships
    )


@groups_bp.route('/view/<int:group_id>/delete', methods=['POST'])
@login_required
def delete_group_from_view(group_id):
    """Delete a group from the view page (admin only)"""
    group = Group.query.get_or_404(group_id)
    
    # Check if user is the group creator (admin)
    if group.created_by != current_user.id:
        flash('Only the group creator can delete this group.', 'error')
        return redirect(url_for('groups.view_group', group_id=group.id))
    
    # Check if group is in forming status (can't delete active groups)
    if group.status != 'forming':
        flash('Cannot delete a group that has already started. Groups can only be deleted while forming.', 'error')
        return redirect(url_for('groups.view_group', group_id=group.id))
    
    try:
        # Delete all memberships
        Membership.query.filter_by(group_id=group.id).delete()
        
        # Delete all invitations
        GroupInvitation.query.filter_by(group_id=group.id).delete()
        
        # Delete the group
        db.session.delete(group)
        db.session.commit()
        
        flash(f'Group "{group.name}" has been deleted successfully.', 'success')
        return redirect(url_for('dashboard.index'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting group: {str(e)}', 'error')
        return redirect(url_for('groups.view_group', group_id=group.id))


@groups_bp.route('/view/<int:group_id>/leave', methods=['POST'])
@login_required
def leave_group_from_view(group_id):
    """Leave a group from the view page (regular members only)"""
    group = Group.query.get_or_404(group_id)
    
    # Check if user is a member
    membership = Membership.query.filter_by(
        user_id=current_user.id,
        group_id=group.id
    ).first()
    
    if not membership:
        flash('You are not a member of this group.', 'error')
        return redirect(url_for('groups.view_group', group_id=group.id))
    
    # Check if user is the creator (creators can't leave, they must delete)
    if group.created_by == current_user.id:
        flash('Group creators cannot leave their own group. Use the delete option instead.', 'error')
        return redirect(url_for('groups.view_group', group_id=group.id))
    
    # Check if group has started (can't leave active groups)
    if group.status != 'forming':
        flash('Cannot leave a group that has already started.', 'error')
        return redirect(url_for('groups.view_group', group_id=group.id))
    
    try:
        # Delete the membership
        db.session.delete(membership)
        db.session.commit()
        
        flash(f'You have left the group "{group.name}".', 'success')
        return redirect(url_for('dashboard.index'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error leaving group: {str(e)}', 'error')
        return redirect(url_for('groups.view_group', group_id=group.id))


@groups_bp.route('/view/<int:group_id>/remove-member/<int:member_id>', methods=['POST'])
@login_required
def remove_member_from_view(group_id, member_id):
    """Remove a member from a group from the view page (admin only)"""
    group = Group.query.get_or_404(group_id)
    
    # Check if user is the group creator (admin)
    if group.created_by != current_user.id:
        flash('Only the group creator can remove members.', 'error')
        return redirect(url_for('groups.view_group', group_id=group.id))
    
    # Get the membership to remove
    membership = Membership.query.filter_by(
        user_id=member_id,
        group_id=group.id
    ).first()
    
    if not membership:
        flash('Member not found in this group.', 'error')
        return redirect(url_for('groups.view_group', group_id=group.id))
    
    # Check if trying to remove the creator
    if member_id == group.created_by:
        flash('Cannot remove the group creator. Use the delete group option instead.', 'error')
        return redirect(url_for('groups.view_group', group_id=group.id))
    
    # Check if group has started (can't remove members from active groups)
    if group.status != 'forming':
        flash('Cannot remove members from a group that has already started.', 'error')
        return redirect(url_for('groups.view_group', group_id=group.id))
    
    try:
        # Get member name for flash message
        member_name = membership.user.full_name
        
        # Delete the membership
        db.session.delete(membership)
        db.session.commit()
        
        flash(f'Member "{member_name}" has been removed from the group.', 'success')
        return redirect(url_for('groups.view_group', group_id=group.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error removing member: {str(e)}', 'error')
        return redirect(url_for('groups.view_group', group_id=group.id))


@groups_bp.route('/my-groups')
@login_required
def my_groups():
    """View all groups the user is a member of"""
    user_memberships = current_user.memberships.all()
    user_groups = []
    
    for membership in user_memberships:
        group = membership.group
        # Calculate additional group info
        group.current_cycle = membership.payout_order
        group.total_cycles = group.cycle_size
        group.user_position = membership.payout_order
        group.next_payout_date = "Week " + str(membership.payout_order) if membership.payout_order <= group.cycle_size else "Completed"
        user_groups.append(group)
    
    # Sort groups by status (forming first, then active)
    user_groups.sort(key=lambda x: (x.status != 'forming', x.name))
    
    return render_template('my_groups.html', groups=user_groups)


@groups_bp.route('/debug/groups')
@login_required
def debug_groups():
    """Debug route to check all groups and their status"""
    all_groups = Group.query.all()
    user_memberships = current_user.memberships.all()
    
    debug_info = {
        'total_groups': len(all_groups),
        'user_memberships': len(user_memberships),
        'groups': []
    }
    
    for group in all_groups:
        group_info = {
            'id': group.id,
            'name': group.name,
            'status': group.status,
            'cycle_size': group.cycle_size,
            'current_members': group.memberships.count(),
            'is_full': group.is_full,
            'created_by': group.created_by,
            'user_is_member': group.id in [m.group_id for m in user_memberships],
            'user_is_creator': group.created_by == current_user.id
        }
        debug_info['groups'].append(group_info)
    
    return jsonify(debug_info)


# New invitation routes
@groups_bp.route('/invite/<int:group_id>', methods=['GET', 'POST'])
@login_required
def invite_members(group_id):
    """Invite members to join a group"""
    group = Group.query.get_or_404(group_id)
    
    # Check if user is the group creator or a member
    membership = Membership.query.filter_by(
        user_id=current_user.id,
        group_id=group.id
    ).first()
    
    if not membership and group.created_by != current_user.id:
        flash('You are not authorized to invite members to this group.', 'error')
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        invited_email = request.form.get('invited_email')
        invited_phone = request.form.get('invited_phone')
        invited_name = request.form.get('invited_name')
        
        if not invited_email and not invited_phone:
            flash('Please provide either an email or phone number.', 'error')
            return redirect(url_for('groups.invite_members', group_id=group_id))
        
        try:
            # Create invitation
            invitation = GroupInvitation.create_invitation(
                group_id=group.id,
                invited_by=current_user.id,
                invited_email=invited_email,
                invited_phone=invited_phone,
                invited_name=invited_name
            )
            
            db.session.add(invitation)
            db.session.commit()
            
            flash(f'Invitation sent successfully! Code: {invitation.invitation_code}', 'success')
            return redirect(url_for('groups.view_invitations', group_id=group_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating invitation: {str(e)}', 'error')
            return redirect(url_for('groups.invite_members', group_id=group_id))
    
    return render_template('invite_members.html', group=group)


@groups_bp.route('/join/invitation/<invitation_code>', methods=['GET', 'POST'])
def join_via_invitation(invitation_code):
    """Join a group using an invitation code"""
    invitation = GroupInvitation.query.filter_by(invitation_code=invitation_code).first()
    
    if not invitation:
        flash('Invalid invitation code.', 'error')
        return redirect(url_for('main.index'))
    
    if not invitation.is_valid:
        if invitation.is_expired:
            flash('This invitation has expired.', 'error')
        else:
            flash('This invitation is no longer valid.', 'error')
        return redirect(url_for('main.index'))
    
    group = invitation.group
    
    # If user is not logged in, redirect to login
    if not current_user.is_authenticated:
        flash('Please log in to accept this invitation.', 'info')
        return redirect(url_for('auth.login', next=request.url))
    
    # Check if user is already a member
    existing_membership = Membership.query.filter_by(
        user_id=current_user.id,
        group_id=group.id
    ).first()
    
    # Check if group is full
    if group.is_full:
        flash('This group is already full.', 'error')
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        # If user is already a member, just redirect to dashboard
        if existing_membership:
            flash('You are already a member of this group.', 'info')
            return redirect(url_for('dashboard.index'))
        
        try:
            # Add user to group
            next_position = group.memberships.count() + 1
            membership = Membership(
                user_id=current_user.id,
                group_id=group.id,
                payout_order=next_position
            )
            
            # Accept the invitation
            invitation.accept(current_user.id)
            
            db.session.add(membership)
            db.session.commit()
            
            flash(f'You have successfully joined {group.name}!', 'success')
            
            # Check if group is now full and can start
            if GroupStateMachine.can_start(group.status, group.memberships.count(), group.cycle_size):
                group.status = 'collecting'
                db.session.commit()
                flash(f'Group {group.name} is now complete and has started collecting contributions!', 'info')
            
            return redirect(url_for('dashboard.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error joining group: {str(e)}', 'error')
            return redirect(url_for('main.index'))
    
    return render_template('join_via_invitation.html', invitation=invitation, group=group, existing_membership=existing_membership)


@groups_bp.route('/invitations/<int:group_id>')
@login_required
def view_invitations(group_id):
    """View all invitations for a group"""
    group = Group.query.get_or_404(group_id)
    
    # Check if user is the group creator or a member
    membership = Membership.query.filter_by(
        user_id=current_user.id,
        group_id=group.id
    ).first()
    
    if not membership and group.created_by != current_user.id:
        flash('You are not authorized to view invitations for this group.', 'error')
        return redirect(url_for('dashboard.index'))
    
    invitations = GroupInvitation.query.filter_by(group_id=group_id).order_by(GroupInvitation.created_at.desc()).all()
    
    return render_template('view_invitations.html', group=group, invitations=invitations)


@groups_bp.route('/invitation/<int:invitation_id>/cancel', methods=['POST'])
@login_required
def cancel_invitation(invitation_id):
    """Cancel an invitation"""
    invitation = GroupInvitation.query.get_or_404(invitation_id)
    
    # Check if user is the inviter or group creator
    if invitation.invited_by != current_user.id and invitation.group.created_by != current_user.id:
        flash('You are not authorized to cancel this invitation.', 'error')
        return redirect(url_for('groups.view_invitations', group_id=invitation.group_id))
    
    invitation.status = 'cancelled'
    db.session.commit()
    
    flash('Invitation cancelled successfully.', 'success')
    return redirect(url_for('groups.view_invitations', group_id=invitation.group_id))


