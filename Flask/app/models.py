from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    plate = db.Column(db.String(7), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Reserves(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_parking = db.Column(db.Integer, nullable=False)
    id_usuari = db.Column(db.Integer, nullable=False)
    data = db.Column(db.String(50), nullable=False)

class Ocupacions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.Integer, nullable=False)

class ParkingLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String(7), nullable=False)
    accio = db.Column(db.String(50), nullable = False)