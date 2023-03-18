from flask import Blueprint, render_template, url_for
from flask_login import login_required
from flask_login.login_manager import redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired

from .db import Group, db


admin = Blueprint("admin", __name__)


class GroupCreationForm(FlaskForm):
    group_name = StringField("Name", [DataRequired()])
    submit = SubmitField("Create Group")

    def validate_group_name(self, group_name):
        group = db.session.query(Group).filter_by(name=group_name.data).first()
        if group is not None:
            raise ValidationError(f"Group {group_name.data} already exists")


@admin.route("/admin/", methods=["GET", "POST"])
@login_required
def admin_page():
    form = GroupCreationForm()
    if form.validate_on_submit():
        group = Group(name=form.group_name.data)
        db.session.add(group)
        db.session.commit()
        return redirect(url_for("admin.admin_page"))

    groups = db.session.query(Group)
    return render_template("admin.html", groups=groups, form=form)
