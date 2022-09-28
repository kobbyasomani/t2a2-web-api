from app import db


class Country(db.Model):
    __tablename__ = "countries"

    country_id = db.Column(db.String(2), primary_key=True)
    name = db.Column(db.String(), nullable=False)
    description = db.Column(db.String(), nullable=False)