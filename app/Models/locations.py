from app import db


class Location(db.Model):
    __tablename__ = "locations"

    location_id = db.Column(db.Integer, primary_key=True)
    postcode = db.Column(db.String(), db.ForeignKey(
        "postcodes.postcode"), nullable=False)
    country_id = db.Column(db.String(2), db.ForeignKey(
        "postcodes.country_id"), nullable=False)
    suburb = db.Column(db.String(), nullable=False)