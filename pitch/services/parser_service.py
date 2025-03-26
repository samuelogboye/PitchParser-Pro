'''ParserService with business logic for document parsing routes'''
import os
from pitch import db
from pitch.celery.celery import celery
from pitch.utils.pdf_parser import parse_pdf
from pitch.utils.pptx_parser import parse_pptx
from pitch.utils.file_utils import allowed_file, get_upload_folder
from pitch.models.pitch_deck import PitchDeck
from pitch.models.pitch_deck_slide import PitchDeckSlide
from pitch.utils.logger import log_error, log_success
from werkzeug.utils import secure_filename
from pitch.celery.tasks import process_pitchdeck

class ParserService:
    '''Contains business logic for document parsing'''

    @staticmethod
    def upload_file(file):
        '''Handles file upload and initiates processing'''
        if not file:
            return {'error': 'No file uploaded'}, 400

        if not allowed_file(file.filename):
            return {'error': 'Unsupported file type'}, 400

        filename = secure_filename(file.filename)
        upload_folder = get_upload_folder()
        filepath = os.path.join(upload_folder, filename)
        
        try:
            file.save(filepath)
            task = process_pitchdeck.delay(filepath, filename)
            return {
                'message': 'File uploaded successfully',
                'task_id': task.id
            }, 202
        except Exception as e:
            log_error('upload_file', str(e))
            return {'error': 'File upload failed'}, 500

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
        slides = PitchDeckSlide.query.filter_by(deck_id=pitch_deck_id).all()
        return [slide.to_dict() for slide in slides], 200
    
    # get all pictch decks
    @staticmethod
    def get_pitch_decks():
        pitch_decks = PitchDeck.query.all()
        return [pitch_deck.to_dict() for pitch_deck in pitch_decks], 200

    # # Celery Task (internal)
    # @staticmethod
    # @celery.task(bind=True)
    # def _process_pitchdeck(self, filepath, filename):
    #     '''Background task for processing pitch decks'''
    #     try:
    #         # Create pitch deck record
    #         pitch_deck = PitchDeck(
    #             original_filename=filename,
    #             stored_filename=os.path.basename(filepath),
    #             file_size=os.path.getsize(filepath),
    #             file_type='pdf' if filepath.endswith('.pdf') else 'pptx',
    #             processing_status='processing'
    #         )
    #         pitch_deck.insert()

    #         # Parse document
    #         if filepath.endswith('.pdf'):
    #             slides_data = parse_pdf(filepath)
    #         elif filepath.endswith('.pptx'):
    #             slides_data = parse_pptx(filepath)

    #         # Save slides
    #         for slide_data in slides_data:
    #             slide = PitchDeckSlide(
    #                 deck_id=pitch_deck.id,
    #                 slide_number=slide_data['slide_number'],
    #                 title=slide_data.get('title', f'Slide {slide_data["slide_number"]}'),
    #                 content=slide_data.get('content', ''),
    #                 meta_data=slide_data.get('meta', {})
    #             )
    #             db.session.add(slide)

    #         # Update status
    #         pitch_deck.processing_status = 'completed'
    #         db.session.commit()

    #         log_success('_process_pitchdeck', f'Successfully processed {filename}')
    #         return {
    #             'status': 'success',
    #             'pitch_deck_id': pitch_deck.id
    #         }

    #     except Exception as e:
    #         log_error('_process_pitchdeck', str(e))
    #         if 'pitch_deck' in locals():
    #             pitch_deck.processing_status = 'failed'
    #             db.session.commit()
    #         raise  # Celery will handle retries