from datetime import timedelta
from werkzeug.security import generate_password_hash

from invest import db


class User(db.Model):
    __tablename__ = 'users'
    # __table_args__ = {'schema': 'invest'}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    pw_hash = db.Column(db.String, nullable=False)
    registration_date = db.Column(db.DateTime, nullable=False)
    activation_date = db.Column(db.DateTime, nullable=False)
    access_expiration_date = db.Column(db.DateTime, nullable=False)
    role = db.Column(db.String(16), nullable=False)

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
        return str(self.id)

    def __init__(
            self, name, email, password, registration_date, activation_date,
            expiration_date=None, role='user'
            ):
        self.name = name
        self.email = email
        self.pw_hash = generate_password_hash(password)
        self.registration_date = registration_date
        self.activation_date = activation_date
        if expiration_date is None:
            self.access_expiration_date = activation_date + timedelta(days=365)
        else:
            self.access_expiration_date = expiration_date
        self.role = role

    def __repr__(self):
        return f'<User {self.email}>'


class Asset(db.Model):
    __tablename__ = 'assets'
    # __table_args__ = {'schema': 'invest'}

    id = db.Column(db.Integer, primary_key=True)
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


class Wallet(db.Model):
    __tablename__ = 'wallets'
    # __table_args__ = {'schema': 'invest'}

    id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(db.Integer, db.ForeignKey('invest.users.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(db.DateTime, nullable=False)
    wallet = db.Column(db.Text, nullable=False)

    user = db.relationship('User', foreign_keys=user_id)

    def __init__(self, user_id, date, wallet):
        self.user_id = user_id
        self.date = date
        self.wallet = wallet


# class Wallet(db.Model):
#     __tablename__ = 'wallets'
#     __table_args__ = {'schema': 'invest'}

#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('invest.users.id'))
#     asset_id = db.Column(db.Integer, db.ForeignKey('invest.assets.id'))
#     quantity = db.Column(db.Float, nullable=False)
#     cost = db.Column(db.Float, nullable=False)
#     value = db.Column(db.Float, nullable=False)
#     institution = db.Column(db.String(128), nullable=False)
#     date = db.Column(db.DateTime, nullable=False)

#     user = db.relationship('User', foreign_keys=user_id)
#     asset = db.relationship('Asset', foreign_keys=asset_id)

#     def __init__(self, user_id, asset_id, quantity, cost, value, institution, date):
#         self.user_id = user_id
#         self.asset_id = asset_id
#         self.quantity = quantity
#         self.cost = cost
#         self.value = value
#         self.institution = institution
#         self.date = date
