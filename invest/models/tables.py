from werkzeug.security import generate_password_hash

from invest import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    pw_hash = db.Column(db.String)

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

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.pw_hash = generate_password_hash(password)

    def __repr__(self):
        return f'<User {self.email}>'
