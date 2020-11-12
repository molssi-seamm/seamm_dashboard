
import logging

from flask import render_template, redirect, request, url_for, flash, jsonify

# Still importing for un-rewritten routes (leaving for reference)
from flask_login import login_required, current_user

from flask_jwt_extended import (get_jwt_identity, jwt_optional, get_current_user,
                                set_access_cookies, set_refresh_cookies)
from ..email import send_email
from .forms import LoginForm, CreateUserForm, ChangePasswordForm,\
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm

from . import auth

from app import db
from app.models import User
from app.routes.api.auth import create_tokens


logger = logging.getLogger(__name__)

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@jwt_optional
@auth.route('/login', methods=['GET', 'POST'])
def login():

    # If current user is logged in, redirect them to the main page.
    if get_current_user():
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).one_or_none()

        if user is not None and user.verify_password(form.password.data):
            next_page = request.args.get('next')

            if next_page is None or not next_page.startswith('/'):
                next_page = url_for('main.index')
                response = redirect(next_page)

            # Add cookies to response
            access_token, refresh_token = create_tokens(user)
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
           
            return response
        flash('Invalid email or password.')

    return render_template('auth/login.html', form=form, current_user=get_current_user)

# Login required.
@auth.route('/logout')
def logout():
    # Logout using token TODO
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/create_user', methods=['GET', 'POST'])
def create_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data)
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        #token = user.generate_confirmation_token()
        #send_email(user.email, 'SEAMM Dashboard - Confirm Your Account',
        #           'auth/email/confirm', user=user, token=token)
        flash(F'The user {user.username} has been created')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

# Hasn't been rewritten
@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            current_user.save()
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)

# Hasn't been rewritten
@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

# Hasn't been rewritten
@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)

# Hasn't been rewritten
@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_email.html", form=form)

# Hasn't been rewritten
@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))
