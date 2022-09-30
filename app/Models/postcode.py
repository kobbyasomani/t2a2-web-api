from app import db


class Postcode(db.Model):
    __tablename__ = "postcodes"

    code = db.Column(db.String())
    country_id = db.Column(db.String(), db.ForeignKey(
        "countries.country_id"))
    state = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(), nullable=False)
    locations = db.relationship("Location", backref="postcode")

    # Define postcode_id and country_id as composite primary key
    __table_args__ = (db.PrimaryKeyConstraint("code", "country_id"), )
