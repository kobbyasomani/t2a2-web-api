from app import db


class Location(db.Model):
    __tablename__ = "locations"

    location_id = db.Column(db.Integer, primary_key=True)
    postcode = db.Column(db.String(), nullable=False)
    country_id = db.Column(db.String(2), nullable=False)
    suburb = db.Column(db.String(), nullable=False)
    questions = db.relationship("Question", backref="location")

    # Define postcode and country_id as a composite foreign key
    __tableargs__ = db.ForeignKeyConstraint(
        ["postcode", "country_id"],
        ["postcodes.postcode", "country.country_id"])