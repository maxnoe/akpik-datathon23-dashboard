from flask_sqlalchemy import SQLAlchemy
import secrets
from importlib.resources import read_text


WORD_LIST = read_text("akpik_datathon_dashboard", "wordlist.txt").splitlines()


db = SQLAlchemy()


def create_token():
    return "-".join(secrets.choice(WORD_LIST) for _ in range(3))


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String, nullable=False)
    filename = db.Column(db.String, nullable=False)
    score = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False)


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    token = db.Column(db.String, nullable=False, default=create_token)
