from datetime import datetime
from werkzeug.security import generate_password_hash
from app.models import db, User, Pilot, Drone

DRONES = [
    {"call_sign": "9J-XDR", "model": "DJI PHANTOM 4 RTK",     "serial_number": "0V2DG7A0A30046",     "is_active": True},
    {"call_sign": "9J-XEJ", "model": "DJI PHANTOM 4 PRO",     "serial_number": "0AXCE8Q0A30417",     "is_active": True},
    {"call_sign": "9J-XGF", "model": "T- DRONE M1200",        "serial_number": "CU11J20701878",      "is_active": True},
    {"call_sign": "9J-XIX", "model": "DJI M300 RTK",          "serial_number": "1ZN3K8W00SVOCS",     "is_active": True},
    {"call_sign": "9J-XJR", "model": "DJI MAVIC 3 PRO CINE",  "serial_number": "1581F6MKD233U0240538", "is_active": True},
    {"call_sign": "9J-XLC", "model": "DJI MAVIC 3 PRO CINE",  "serial_number": "1581F6MKC234MO2404F2", "is_active": True},
    {"call_sign": "9J-XMM", "model": "DJI MAVIC 3 THERMAL",   "serial_number": "1581F5FJC246300DY3K6", "is_active": True},
    {"call_sign": "9J-XOC", "model": "DJI MATRICE 350 RTK",   "serial_number": "1581F6GKX254700404V5", "is_active": True},
    {"call_sign": "9J-XOK", "model": "DJI MATRICE 350 RTK",   "serial_number": "1581F6GKB24CN0040DP4", "is_active": True},
    {"call_sign": "9J-XON", "model": "DJI MATRICE 400",       "serial_number": "1581F8DBW255D00A2LU3", "is_active": True},
    {"call_sign": "9J-X00", "model": "DJI MATRICE 400",       "serial_number": "1581F8DBW257C00A2S64", "is_active": True},
]

PILOTS = [
    {"name": "Chamunorlwa Masiye",               "email": "", "phone_number": "", "license_number": "15",  "license_expiry_date": "13/06/2020", "license_type": "MR", "license_rating": "VLOS", "is_active": False},
    {"name": "Toni Zeravica",                    "email": "", "phone_number": "", "license_number": "17",  "license_expiry_date": "27/08/2027", "license_type": "MR", "license_rating": "VLOS", "is_active": True},
    {"name": "Percy Musiane Chilombo Chikwenda", "email": "", "phone_number": "", "license_number": "70",  "license_expiry_date": "",          "license_type": "MR", "license_rating": "VLOS", "is_active": False},
    {"name": "Ismail Riyaz",                     "email": "", "phone_number": "", "license_number": "71",  "license_expiry_date": "",          "license_type": "MR", "license_rating": "VLOS", "is_active": False},
    {"name": "Sylvester Mwale",                  "email": "", "phone_number": "", "license_number": "109", "license_expiry_date": "18/10/2027", "license_type": "MR", "license_rating": "VLOS", "is_active": True},
    {"name": "Matthew Blair",                    "email": "", "phone_number": "", "license_number": "141", "license_expiry_date": "",          "license_type": "MR", "license_rating": "VLOS", "is_active": False},
    {"name": "Onijah Zami",                      "email": "", "phone_number": "", "license_number": "142", "license_expiry_date": "",          "license_type": "MR", "license_rating": "VLOS", "is_active": False},
    {"name": "Lawrence Twaambo",                 "email": "", "phone_number": "", "license_number": "361", "license_expiry_date": "",          "license_type": "MR", "license_rating": "VLOS", "is_active": True},
]

def _parse_date(value):
    """'13/06/2020' -> date, '' -> None (stored as NULL)."""
    return datetime.strptime(value, "%d/%m/%Y").date() if value else None

def seed_db():
    # Each table is seeded independently, so adding data later
    # won't re-insert what's already there.
    if Drone.query.count() == 0:
        db.session.add_all([Drone(**d) for d in DRONES])

    if Pilot.query.count() == 0:
        db.session.add_all([
            Pilot(
                name=p["name"],
                email=p["email"] or None,
                phone_number=p["phone_number"] or None,
                license_number=p["license_number"],
                license_expiration_date=_parse_date(p["license_expiry_date"]),
                license_type=p["license_type"],
                license_rating=p["license_rating"],
                is_active=p["is_active"],
            )
            for p in PILOTS
        ])

    # Checked by email rather than count, so the admin comes back
    # even if other users exist.
    if User.query.filter_by(email="admin@terravia.africa").first() is None:
        db.session.add(User(
            name="Admin",
            email="admin@terravia.africa",
            password_hash=generate_password_hash("123456", method="pbkdf2:sha256"),
            role="admin",
        ))

    db.session.commit()