from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False) 

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pet_name = db.Column(db.String(100), nullable=False)
    owner = db.Column(db.String(80), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    appt_type = db.Column(db.String(20), default="General") 
    status = db.Column(db.String(20), default="Pending")