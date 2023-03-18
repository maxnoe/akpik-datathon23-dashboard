from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, ValidationError
from flask_login import login_required
from werkzeug.utils import secure_filename
from wtforms import StringField
from wtforms.validators import DataRequired
import numpy as np
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from .db import Submission, Group, db
from .tasks import score_submission


dashboard = Blueprint("dashboard", __name__)



class SubmissionForm(FlaskForm):
    token = StringField("Submission Token", [DataRequired()])
    submission = FileField("Training Indices Numpy File", validators=[FileRequired()])

    def validate_token(self, token: StringField):
        group = db.session.query(Group).filter_by(token=token.data).first()
        if group is None:
            raise ValidationError("Invalid Submission Token")

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
        " Only upload the <em>indices</em> of the training set"
        ", stored with the <code>export_submission</code> function."
        " The expected filesize is 80kB.",
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
    tz = ZoneInfo(current_app.config["TIMEZONE"])
    return render_template("index.html", submissions=submissions, timezone=tz, utc=timezone.utc)


@dashboard.route("/submission/", methods=["GET", "POST"])
def submission():
    form = SubmissionForm()
    if form.validate_on_submit():
        file_storage = form.submission.data

        group = db.session.query(Group).filter_by(token=form.token.data).one()

        group_name = group.name

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
