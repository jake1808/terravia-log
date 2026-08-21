from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash=db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(80), nullable=False)
    
    def to_dict(self):
        return{
               "id":self.id, 
               "name":self.name, 
               "email":self.email, 
               'role':self.role
               }

class Pilot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    license_number = db.Column(db.String(100), unique=True, nullable=False)
    license_expiration_date = db.Column(db.Date, nullable=False)
    license_type = db.Column(db.String(50), nullable=False)
    license_rating = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def to_dict(self):
        return {
                "id": self.id, 
                "user_id": self.user_id, 
                "license_number": self.license_number, 
                "license_expiration_date": self.license_expiration_date, 
                "license_type": self.license_type, 
                "license_rating": self.license_rating, 
                "is_active": self.is_active, 
                }

class Drone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    call_sign = db.Column(db.String(100), unique=True, nullable=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    max_flight_time = db.Column(db.Integer, nullable=False)  # in minutes
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "call_sign": self.call_sign,
            "serial_number": self.serial_number,
            "max_flight_time": self.max_flight_time,
            "is_active": self.is_active
        }

class MissionLogs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pilot_id = db.Column(db.Integer, db.ForeignKey('pilot.id'), nullable=False)
    drone_id = db.Column(db.Integer, db.ForeignKey('drone.id'), nullable=False)
    location = db.Column(Geometry(geometry_type='POINT', srid=4326))
    clearance_code=db.Column(db.String(100))
    active=db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)