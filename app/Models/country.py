from app import db


class Country(db.Model):
    __tablename__ = "countries"

    country_code = db.Column(db.String(2), primary_key=True)
    country = db.Column(db.String(), nullable=False)

    # Relationships
    locations = db.relationship("Location", back_populates="country")