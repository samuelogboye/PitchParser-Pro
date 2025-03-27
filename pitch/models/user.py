from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import generate_password_hash, check_password_hash
from pitch.models.base import BaseModel
from time import time

db = SQLAlchemy()

class User(BaseModel):
    """User model for authentication"""
    __tablename__ = 'users'

    updated_at = None
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(512))
    refresh_tokens = db.relationship('RefreshToken', backref='user', lazy=True)
    
    # Relationship to pitch decks
    pitch_decks = db.relationship('PitchDeck', backref='owner', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        db.session.commit()
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def format(self):
        '''Return a dictionary representation of the user object'''
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    

class RefreshToken(BaseModel):
    '''Refresh Token Table'''
    __tablename__ = 'refreshtokens'

    token = db.Column(db.String(512), unique=True, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        '''Return a string representation of the refresh token object'''
        return f"RefreshToken('{self.token}', '{self.user_id}', '{self.expires_at}')"

    def format(self):
        '''Return a dictionary representation of the refresh token object'''
        return {
            'token': self.token,
            'user_id': self.user_id,
            'used': self.used,
            'expires_at': self.expires_at
        }