from pitch import db
from pitch.models.base import BaseModel

class PitchDeckSlide(BaseModel):
    """Individual slide model from a pitch deck"""
    __tablename__ = 'pitch_deck_slides'
    
    id = db.Column(db.Integer, primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('pitch_decks.id'), nullable=False)
    slide_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(256))
    content = db.Column(db.Text)
    notes = db.Column(db.Text)
    image_path = db.Column(db.String(256))  # Path to extracted slide image if needed
    meta_data = db.Column(db.JSON)  # Store any additional metadata as JSON

    def to_dict(self):
        return {
            'id': self.id,
            'slide_number': self.slide_number,
            'title': self.title,
            'content': self.content,
            'meta_data': self.meta_data
        }
