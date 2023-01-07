from datetime import timedelta
from werkzeug.security import generate_password_hash

from invest import db


class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'invest'}

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    pw_hash = db.Column(db.String, nullable=False)
    registration_date = db.Column(db.DateTime, nullable=False)
    activation_date = db.Column(db.DateTime, nullable=False)
    access_expiration_date = db.Column(db.DateTime, nullable=False)
    persona = db.Column(db.String(16), nullable=False)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return self.is_active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.user_id)

    def __init__(
            self, name, email, password, registration_date, activation_date,
            persona='user'
            ):
        self.name = name
        self.email = email
        self.pw_hash = generate_password_hash(password)
        self.registration_date = registration_date
        self.activation_date = activation_date
        self.access_expiration_date = activation_date + timedelta(days=365)
        self.persona = persona

    def __repr__(self):
        return f'<User {self.email}>'


class Asset(db.Model):
    __tablename__ = 'assets'
    __table_args__ = {'schema': 'invest'}

    asset_id = db.Column(db.Integer, primary_key=True)
    asset_name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(128), nullable=False)
    market = db.Column(db.String(128), nullable=False)
    asset_type = db.Column(db.String(128), nullable=False)
    asset_group = db.Column(db.String(128), nullable=False)
    asset_expiration_date = db.Column(db.DateTime, nullable=False)

    def __init__(self, name, description, market, asset_type, group, expiration_date):
        self.asset_name = name
        self.description = description
        self.market = market
        self.asset_type = asset_type
        self.asset_group = group
        self.asset_expiration_date = expiration_date

    def __repr__(self):
        return f'<Asset {self.asset_name}>'


# class Wallet(db.Model):
#     __tablename__ = 'wallets'
#     __table_args__ = {'schema': 'invest'}
