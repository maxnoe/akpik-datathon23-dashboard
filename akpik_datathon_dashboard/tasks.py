from flask import Flask, current_app
from celery import Celery, Task, shared_task
import random
import numpy as np
import tensorflow as tf

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


def _evaluate(X_trn, y_trn, X_tst, y_tst, n_trials=10):
    """Evaluate a fixed model with given training and testing sets.
    
    The participants of the Datathon are provided with precisely the same function,
    but not with the true testing labels. Hence, the evaluation pipeline is transparent
    but they cannot simply optimize the actual testing performance.
    """

    performances = np.zeros(n_trials)
    for i in range(n_trials):
        model = tf.keras.Sequential([
            tf.keras.layers.Flatten(input_shape=(28, 28)),
            tf.keras.layers.Dense(256, activation="relu"),
            tf.keras.layers.Dense(10)
        ])
        model.compile(
            optimizer = "adam",
            loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
            metrics = ["accuracy"]
        )
        model.fit(X_trn, y_trn, epochs=10, validation_split=.1, verbose=0)
        performances[i] = model.evaluate(X_tst, y_tst, verbose=0)[1]
        print(f"Score {i:02d}: {performances[i]}")

    return performances


@shared_task()
def score_submission(submission_id):
    submission = db.session.get(Submission, submission_id)

    data_path = current_app.config["DATA_PATH"] 
    path = data_path / submission.filename
    train_indices = np.load(str(path))

    X_trn = np.load(data_path / "X_trn.npy")
    X_tst = np.load(data_path / "X_tst.npy")
    y_trn = np.load(data_path / "y_trn.npy")
    y_tst = np.load(data_path / "y_tst.npy")

    np.random.seed(current_app.config["RANDOM_SEED"])
    tf.random.set_seed(current_app.config["RANDOM_SEED"])
    scores = _evaluate(
        X_trn[train_indices],
        y_trn[train_indices],
        X_tst,
        y_tst
    )
    score = np.mean(scores)
    std = np.std(scores)

    print(f"Final score for submission {submission.id}: {score:.4f} (± {std:.4f})")

    submission.score = score
    db.session.add(submission)
    db.session.commit()
