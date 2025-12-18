from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # owner / vet

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pet_name = db.Column(db.String(100))
    owner = db.Column(db.String(100))
    date = db.Column(db.String(20))
    reason = db.Column(db.String(200))
    status = db.Column(db.String(20), default="Pending")

class Vaccination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pet_name = db.Column(db.String(100))
    vaccine = db.Column(db.String(100))
    given_date = db.Column(db.String(20))
    next_due = db.Column(db.String(20))