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
    answers = db.relationship("Answer", backref="question")
