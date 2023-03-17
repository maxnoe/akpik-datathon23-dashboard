from flask import Flask
from celery import Celery, Task, shared_task
import random

from .db import Submission, db


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.conf.broker_url = app.config["REDIS_URL"]
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


@shared_task()
def score_submission(submission_id):
    submission = db.session.get(Submission, submission_id)

    # yes, we just draw a random number ;) Fair
    submission.score = random.random()

    db.session.add(submission)
    db.session.commit()
