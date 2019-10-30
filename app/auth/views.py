from flask import render_template, redirect, request, url_for, flash, \
    current_app
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import auth
from ..models.users import User
from ..email import send_email
from .forms import LoginForm, RegistrationForm, ChangePasswordForm,\
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm
import logging


logger = logging.getLogger(__name__)


@auth.before_app_request
def before_request():
    logger.debug('current_user is: %s', current_user)
    if current_user.is_authenticated:
        if not current_user.confirmed and current_app.config['EMAIL_CONFIRMATION_ENABLED'] \
                and request.endpoint \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('admin.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            logging.debug('Used found in DB: %s', user.username)
            login_user(user, form.remember_me.data)
            next_page = request.args.get('next')
            if next_page is None or not next_page.startswith('/'):
                next_page = url_for('admin.index')
            return redirect(next_page)
        flash('Invalid email or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('admin.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data)
        user.password = form.password.data
        user.save()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('admin.index'))
    if current_user.confirm(token):
        current_user.save()
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('admin.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('admin.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            current_user.save()
            flash('Your password has been updated.')
            return redirect(url_for('admin.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('admin.index'))
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


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('admin.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('admin.index'))
    return render_template('auth/reset_password.html', form=form)


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
            return redirect(url_for('admin.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('admin.index'))
