from app import db


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), nullable=False, unique=True)
    email = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)

    # Relationships
    questions = db.relationship(
        "Question", back_populates="author", cascade="all, delete")
    answers = db.relationship(
        "Answer", back_populates="author", cascade="all, delete")
    recommendations = db.relationship(
        "Recommendation", back_populates="user", cascade="all, delete")
