from flask import Blueprint, current_app, redirect, render_template, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, ValidationError
from werkzeug.utils import secure_filename
from wtforms import StringField
from wtforms.validators import DataRequired
import numpy as np
from datetime import datetime, timezone

from .db import Submission, db


dashboard = Blueprint("dashboard", __name__)


class SubmissionForm(FlaskForm):
    group_name = StringField("Group Name", [DataRequired()])
    submission = FileField("Training Indices Numpy File", validators=[FileRequired()])

    def validate_submission(self, submission: FileField):
        file_storage = submission.data
        try:
            data = np.load(file_storage)
        except Exception as e:
            raise ValidationError(f"Error loading data: {e}")

        if data.dtype != int:
            raise ValidationError(f"Data has dtype {data.dtype}, must be int")

        if data.shape != (10000, ):
            raise ValidationError(f"Data must have shape (10000, ), got {data.shape}")



@dashboard.route("/")
def index():
    submissions = (
        db.session.query(Submission)
        .order_by(Submission.score.desc(), Submission.timestamp)
        .limit(50)
    )
    return render_template("index.html", submissions=submissions)


@dashboard.route("/submission", methods=["GET", "POST"])
def submission():
    form = SubmissionForm()
    if form.validate_on_submit():
        file_storage = form.submission.data
        group_name = form.group_name.data

        now = datetime.now(timezone.utc)
        timestamp = now.isoformat()

        base = current_app.config['UPLOAD_PATH']

        name = secure_filename(f"submission_{group_name}_{timestamp}.npy")
        path = base / secure_filename(group_name) / name

        path.parent.mkdir(exist_ok=True, parents=True)
        file_storage.save(path)

        submission = Submission(
            group_name=group_name,
            filename=str(path.relative_to(base)),
            timestamp=now,
        )
        db.session.add(submission)
        db.session.commit()

        return redirect(url_for("dashboard.index"))
    return render_template("submission.html", form=form)