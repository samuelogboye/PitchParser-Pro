'''ParserService with business logic for document parsing routes'''
import os
from werkzeug.utils import secure_filename
from pitch.utils.file_utils import allowed_file, get_upload_folder, sanitize_pdf_data, prepare_slide_content
from pitch.models.pitch_deck import PitchDeck
from pitch.models.pitch_deck_slide import PitchDeckSlide
from pitch.models.user import User
from pitch.utils.logger import log_error, log_success, log_warning
from pitch.tasks import process_pitchdeck, get_task
from pitch.utils.pdf_parser import parse_pdf
# from pitch.utils.pptx_parser import parse_pptx
from pitch import db
import json

class ParserService:
    '''Contains business logic for document parsing'''

    @staticmethod
    def upload_file(file, user_id):
        '''Handles file upload and initiates processing'''
        if not user_id:
            return {'error': 'User authentication required'}, 401
        
        if not file:
            log_error('upload_file', 'No file uploaded')
            return {'error': 'No file uploaded'}, 400

        if not allowed_file(file.filename):
            log_error('upload_file', 'Unsupported file type')
            return {'error': 'Unsupported file type'}, 400
        
        # confirm is user exists
        user = User.query.get(user_id)
        if not user:
            log_error('upload_file', 'User not found')
            return {'error': 'User not found'}, 404
        
        try:
            filename = secure_filename(file.filename)
            upload_folder = get_upload_folder()
            filepath = os.path.join(upload_folder, filename)
           
            log_success('upload_file', f'Uploading {filename}')
           
            file.save(filepath)
           
            task = process_pitchdeck.delay(filepath, filename, user_id)
            log_success('upload_file', f'File uploaded successfully, task created: {task.id}')
            return {
                'message': 'File uploaded successfully',
                'task_id': task.id
            }, 202
        except Exception as e:
            log_error('upload_file', str(e))
            return {'error': 'File upload failed'}, 500

    @staticmethod
    def get_progress(task_id):
        '''Retrieves the progress of a task'''
        task = get_task(task_id)
        if task.state == 'PROGRESS':
            return json.dumps(dict(
                state=task.state,
                progress=task.result['current'],
            ))
        elif task.state == 'SUCCESS':
            return json.dumps(dict(
                state=task.state,
                progress=1.0,
            ))
        return '{}'
    
    @staticmethod
    def get_pitch_deck(pitch_deck_id):
        '''Retrieves a pitch deck by ID'''
        pitch_deck = PitchDeck.query.get(pitch_deck_id)
        if not pitch_deck:
            return {'error': 'Pitch deck not found'}, 404
        
        return pitch_deck.to_dict(), 200

    @staticmethod
    def get_slides(pitch_deck_id):
        '''Retrieves all slides for a pitch deck'''
        # slides = PitchDeckSlide.query.filter_by(deck_id=pitch_deck_id).all()
        slides = PitchDeckSlide.query.filter_by(deck_id=pitch_deck_id)\
                      .order_by(PitchDeckSlide.slide_number).all()
        return [slide.to_dict() for slide in slides], 200
    
    # get all pictch decks
    @staticmethod
    def get_pitch_decks(user_id=None):
        '''Retrieve all pitch decks (optionally filtered by user)'''
        query = PitchDeck.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        pitch_decks = query.order_by(PitchDeck.upload_date.desc()).all()
        return [deck.to_dict() for deck in pitch_decks], 200