from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

user_wallets = db.Table('user_wallets',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('wallet_id', db.Integer, db.ForeignKey('wallets.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'  # Explicitly set the table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    wallets = db.relationship('Wallet', secondary=user_wallets, back_populates='users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Wallet(db.Model):
    __tablename__ = 'wallets'  # Explicitly set the table name
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(44), index=True)  # Removed unique=True
    balance = db.Column(db.Float, default=0.0)
    users = db.relationship('User', secondary=user_wallets, back_populates='wallets')

    def __repr__(self):
        return f'<Wallet {self.address}>'

def init_app(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
