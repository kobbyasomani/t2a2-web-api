from app import db


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), nullable=False, unique=True)
    email = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)
    questions = db.relationship("Question", backref="author")
    answers = db.relationship("Answer", backref="author")
    recommendations = db.relationship("Recommendation", backref="user")
