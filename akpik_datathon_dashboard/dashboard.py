from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, ValidationError
from werkzeug.utils import secure_filename
from wtforms import StringField
from wtforms.validators import DataRequired
import numpy as np
from datetime import datetime, timezone

from .db import Submission, db
from .tasks import score_submission


dashboard = Blueprint("dashboard", __name__)



class SubmissionForm(FlaskForm):
    group_name = StringField("Group Name", [DataRequired()])
    submission = FileField("Training Indices Numpy File", validators=[FileRequired()])

    def validate_submission(self, submission: FileField):
        file_storage = submission.data
        magic_bytes = file_storage.read(6)
        file_storage.seek(0)
        if magic_bytes != b'\x93NUMPY':
            raise ValidationError("You must upload a file created with numpy.save")

        try:
            data = np.load(file_storage)
            # seek back to start, otherwise stored file will be empty
            file_storage.seek(0)
        except Exception as e:
            raise ValidationError(f"Error loading data: {e}")

        if data.dtype != int:
            raise ValidationError(f"Data has dtype {data.dtype}, must be int")

        if data.shape != (10000, ):
            raise ValidationError(f"Data must have shape (10000, ), got {data.shape}")


@dashboard.errorhandler(413)
def request_entity_too_large(error):
    flash(
        "Your upload is too large."
        "Only upload the *indices* stored with the <pre>export_submission</pre> function",
        category="danger",
    )
    return redirect(url_for("dashboard.submission"))


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

        base = current_app.config['DATA_PATH']

        name = secure_filename(f"submission_{group_name}_{timestamp}.npy")
        path = base / "submissions" / secure_filename(group_name) / name

        path.parent.mkdir(exist_ok=True, parents=True)
        file_storage.save(path)

        submission = Submission(
            group_name=group_name,
            filename=str(path.relative_to(base)),
            timestamp=now,
        )
        db.session.add(submission)
        db.session.commit()

        score_submission.delay(submission.id)

        flash("Submission added!", category="success")
        return redirect(url_for("dashboard.index"))
    return render_template("submission.html", form=form)
