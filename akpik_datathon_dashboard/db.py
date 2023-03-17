from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String, nullable=False)
    filename = db.Column(db.String, nullable=False)
    score = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False)
