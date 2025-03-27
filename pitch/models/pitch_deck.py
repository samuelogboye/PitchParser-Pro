from sqlalchemy.dialects.postgresql import UUID
from pitch import db
from pitch.models.base import BaseModel
from datetime import datetime

class PitchDeck(BaseModel):
    """Pitch deck model"""
    __tablename__ = 'pitch_decks'
    
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    original_filename = db.Column(db.String(256), nullable=False)
    stored_filename = db.Column(db.String(256), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # 'pdf' or 'pptx'
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    processing_status = db.Column(db.String(20), default='uploaded')  # 'uploaded', 'processing', 'completed', 'failed'
    
    # Relationship to slides
    slides = db.relationship('PitchDeckSlide', backref='pitch_deck', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'original_filename': self.original_filename,
            'upload_date': self.upload_date.isoformat(),
            'processing_status': self.processing_status,
            'file_type': self.file_type
        }
