from app import db


class Question(db.Model):
    __tablename__ = "questions"

    question_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"),
                        nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey(
        "locations.location_id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey(
        "categories.category_id"), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    # time = can be derived from DateTime value of date?
    body = db.Column(db.Text, nullable=False)

    # Relationships
    author = db.relationship("User", back_populates="questions")
    answers = db.relationship(
        "Answer", back_populates="question", cascade="all, delete")
    category = db.relationship("Category", back_populates="questions")
    location = db.relationship("Location", back_populates="questions")
