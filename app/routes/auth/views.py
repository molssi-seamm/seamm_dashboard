import logging

from flask import (
    render_template,
    flash,
    make_response,
    request,
    redirect
)

from flask_jwt_extended import (
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
    create_access_token,
    get_current_user,

)

from .forms import (
    LoginForm,
    ConfirmLogin
)

from app.models import User, UserSchema

from . import auth

from app import jwt
from app.models import User
from app.routes.api.auth import create_tokens

logger = logging.getLogger(__name__)


@auth.route("/login", methods=["GET", "POST"])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).one_or_none()

        if user is not None and user.verify_password(form.password.data):
            # redirect to blank login page which will set local storage to
            # reload all tabs (as logged in user)
            response = make_response(render_template("login_script.html"))

            # Add cookies to response
            access_token, refresh_token = create_tokens(user)
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)

            return response
        flash("Invalid username or password.")

    return render_template("auth/login.html", form=form)

@jwt.needs_fresh_token_loader
@auth.route("/confirm_login", methods=["GET", "POST"])
def fresh_login():

    form = ConfirmLogin()
    user = get_current_user()

    if form.validate_on_submit():

        if user.verify_password(form.password.data):
            user_schema = UserSchema(many=False)
            user = user_schema.dump(user)
            response = redirect(request.referrer)

            # Add cookies to response
            access_token = create_access_token(identity=user, fresh=True)
            set_access_cookies(response, access_token)

            return response
        flash("Invalid username or password.")

    return render_template("auth/confirm_login.html", form=form)


# Login required.
@auth.route("/logout")
def logout():
    """
    Direct to blank page which sets local storage to log out all other tabs and redirects to main
    """
    flash("You have been logged out.")
    response = make_response(render_template("logout.html"))
    unset_jwt_cookies(response)
    return response
