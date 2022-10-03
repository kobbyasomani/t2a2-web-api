from app import db


class Category(db.Model):
    __tablename__ = "categories"

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(), nullable=False, unique=True)
    description = db.Column(db.String(), nullable=False)

    # Relationships
    questions = db.relationship("Question", back_populates="category")
