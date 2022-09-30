from app import db


class Answer(db.Model):
    __tablename__ = "answers"

    answer_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        "users.user_id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey(
        "questions.question_id"), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey(
        "answers.answer_id"), nullable=True)
    date_time = db.Column(db.DateTime, nullable=False)
    # time = can be derived from DateTime value of date?
    body = db.Column(db.Text, nullable=False)
    replies = db.relationship("Answer",
                            backref=db.backref("parent", remote_side=[answer_id]))
    recommendations = db.relationship("Recommendation", backref="answer")
