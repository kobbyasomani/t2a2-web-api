from app import db


class Location(db.Model):
    __tablename__ = "locations"

    location_id = db.Column(db.Integer, primary_key=True)
    country_code = db.Column(db.String(2), db.ForeignKey(
        "countries.country_code"), nullable=False)
    state = db.Column(db.String(), nullable=False)
    postcode = db.Column(db.String(), nullable=False)
    suburb = db.Column(db.String(), nullable=False)

    # Relationships
    country = db.relationship("Country", back_populates="locations")
    questions = db.relationship("Question", back_populates="location")
