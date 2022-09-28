from app import db


class Recommendation(db.Model):
    __tablename__ = "recommendations"

    vote_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        "user.user_id"), nullable=False)
    answer_id = db.Column(db.Integer, db.ForeignKey(
        "answers.answer_id"), nullable=False)
