from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user
from flask import abort, current_app, Blueprint, flash, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired

login_manager = LoginManager()
auth = Blueprint("auth", __name__)


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class User(UserMixin):
    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return 'User(username={})'.format(self.username)

    def get_id(self):
        return self.username


@login_manager.user_loader
def load_user(user_id):
    if user_id == current_app.config["ADMIN_USER"]:
        return User(current_app.config["ADMIN_USER"])
    return None


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.is_submitted():
        if form.validate_on_submit():
            user = load_user(form.username.data)

            if user is None or not form.password.data == current_app.config["ADMIN_PASSWORD"]:
                flash("Invalid user or password", "danger")
                abort(401)

            login_user(user)
            return redirect(request.args.get("next") or url_for("admin.admin_page"))

        else:
            # if form was posted but is not valid we abort with 401
            abort(401)

    return render_template("login.html", form=form)


@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect('/')

