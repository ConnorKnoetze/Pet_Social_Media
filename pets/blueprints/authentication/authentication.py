from flask import Blueprint, render_template, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from pets.adapters import repository
import pets.blueprints.authentication.services as services
from password_validator import PasswordValidator
from functools import wraps


from pets.blueprints.feed.feed import feed, feed_bp

# from pets.utilities import is_logged_in


authentication_blueprint = Blueprint("authentication_bp", __name__, url_prefix="/auth")


@authentication_blueprint.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    user_name_not_unique = None

    if form.validate_on_submit():
        try:
            services.add_user(
                form.user_name.data,
                form.email.data,
                form.password.data,
            )

            return redirect(url_for("authentication_bp.login"))

        except services.NameNotUniqueException:
            user_name_not_unique = (
                "Your user name is already taken - please supply another"
            )
    return render_template(
        "pages/register.html",
        title="Register",
        form=form,
        user_name_error_message=user_name_not_unique,
        handler_url=url_for("authentication_bp.register"),
    )


@authentication_blueprint.route("/login", methods=["GET", "POST"])
def login():
    repo = repository.repo_instance
    form = LoginForm()
    user_name_not_recognised = None
    password_does_not_match_user_name = None

    if form.validate_on_submit():
        try:
            user = services.get_user(form.user_name.data, repo)

            # Authenticate user
            services.authenticate_user(user["user_name"], form.password.data, repo)

            # Initialise session and redirect the user to the home page
            session.clear()
            session["user_name"] = user["user_name"]
            return redirect(url_for("feed.feed"))

        except services.UnknownUserException:
            user_name_not_recognised = (
                "User name not recognised - please supply another"
            )

        except services.AuthenticationException:
            password_does_not_match_user_name = "Password does not match with the supplied user name - please check and try again"

    return render_template(
        "pages/login.html",
        title="Login",
        form=form,
        user_name_error_message=user_name_not_recognised,
        password_error_message=password_does_not_match_user_name,
        handler_url=url_for("authentication_bp.login"),
    )


@authentication_blueprint.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("feed_bp.feed"))


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if not is_logged_in():
            return redirect(url_for("authentication_bp.login"))
        return view(**kwargs)

    return wrapped_view


class PasswordValid:
    def __init__(self, message=None):
        if not message:
            message = (
                "Your password must be at least 8 characters, and contain an upper case letter,\
            a lower case letter and a digit"
            )
        self.message = message

    def __call__(self, form, field):
        schema = PasswordValidator()
        schema.min(8).has().uppercase().has().lowercase().has().digits()
        if not schema.validate(field.data):
            raise ValidationError(self.message)


class RegistrationForm(FlaskForm):
    user_name = StringField(
        "Username",
        [
            DataRequired(message="Your user name is required"),
            Length(min=3, message="Your user name is too short"),
        ],
    )
    email = StringField(
        "Email",
        [
            DataRequired(message="Your email is required"),
            Length(min=9, message="Your email is too short"),
        ],
    )
    password = PasswordField(
        "Password", [DataRequired(message="Your password is required"), PasswordValid()]
    )
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    user_name = StringField("Username", [DataRequired()])
    password = PasswordField("Password", [DataRequired()])
    submit = SubmitField("Login")
