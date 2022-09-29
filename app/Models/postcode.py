from app import db


class Postcode(db.Model):
    __tablename__ = "postcodes"

    postcode = db.Column(db.String(), primary_key=True)
    country_id = db.Column(db.String(), db.ForeignKey(
        "countries.country_id"), primary_key=True)
    state = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(), nullable=False)
    locations = db.relationship("Location", backref="postcode")
