'''ParserService with business logic for document parsing routes'''
import os
from werkzeug.utils import secure_filename
from pitch import db
from pitch.utils.file_utils import allowed_file, get_upload_folder, sanitize_pdf_data, prepare_slide_content
from pitch.models.pitch_deck import PitchDeck
from pitch.models.pitch_deck_slide import PitchDeckSlide
from pitch.utils.logger import log_error, log_success, log_warning
# from pitch.celery.celery import celery_app
# from pitch.celery.tasks.pitchdeck import process_pitchdeck
from pitch.tasks import process_pitchdeck, get_task

from pitch.utils.pdf_parser import parse_pdf
# from pitch.utils.pptx_parser import parse_pptx

from pitch import db
from pitch.models.pitch_deck import PitchDeck
from pitch.models.pitch_deck_slide import PitchDeckSlide
from datetime import datetime
import json
from uuid import UUID

# def process_pitchdeck(filepath: str, filename: str, user_id: UUID):
#     """Process pitch deck file and store in database"""
#     log_success("process_pitchdeck", f'Processing pitch deck: {filename}')
    
#     try:
#         # Validate inputs
#         if not os.path.exists(filepath):
#             raise FileNotFoundError(f"File not found: {filepath}")
            
#         file_size = os.path.getsize(filepath)
#         if file_size == 0:
#             raise ValueError("Empty file provided")
            
#         file_type = 'pdf' if filename.lower().endswith('.pdf') else 'pptx'
#         # Convert user_id if it's a string
#         if isinstance(user_id, str):
#             user_id = UUID(user_id)

#         # Create pitch deck record
#         pitch_deck = PitchDeck(
#             user_id=user_id,
#             original_filename=filename,
#             stored_filename=os.path.basename(filepath),
#             file_size=file_size,
#             file_type=file_type,
#             processing_status='processing'
#         )
#         # db.session.add(pitch_deck)
#         # db.session.commit()
#         pitch_deck.insert()
        
#         try:
#             # Parse the file
#             if file_type == 'pdf':
#                 slides = parse_pdf(filepath)
#             else:
#                 # You would add PPTX parsing here
#                 raise ValueError("PPTX parsing not implemented yet")
            
#             # Store slides in database
#             for slide in slides:
#                 slide_db = PitchDeckSlide(
#                     deck_id=pitch_deck.id,
#                     slide_number=slide.number,
#                     title=slide.title,
#                     content={
#                         'headings': slide.content.headings,
#                         'paragraphs': slide.content.paragraphs,
#                         'bullet_points': slide.content.bullet_points,
#                         'key_metrics': slide.content.key_metrics,
#                         'images': slide.content.images
#                     },
#                     meta_data=slide.meta
#                 )
#                 db.session.add(slide_db)
            
#             # Update status
#             pitch_deck.processing_status = 'completed'
#             db.session.commit()
            
#             log_success("process_pitchdeck", f'Successfully processed {filename} with {len(slides)} slides')
#             return {
#                 'status': 'success',
#                 'pitch_deck_id': str(pitch_deck.id),
#                 'slide_count': len(slides)
#             }
            
#         except Exception as parse_error:
#             pitch_deck.processing_status = 'failed'
#             db.session.commit()
#             log_error("process_pitchdeck", f'Parse failed for {filename}: {str(parse_error)}')
#             raise
            
#     except Exception as e:
#         log_error("process_pitchdeck", f'Failed to process {filename}: {str(e)}')
#         if 'pitch_deck' in locals():
#             db.session.rollback()
#         raise
#     finally:
#         # Clean up the file
#         try:
#             if os.path.exists(filepath):
#                 os.remove(filepath)
#         except Exception as e:
#             log_warning("process_pitchdeck", f'Failed to cleanup file {filepath}: {str(e)}')

# def process_pitchdeck(filepath, filename, user_id=None):
#         log_success('process_pitchdeck', f'Processing {filename}')
#         """Process pitch deck file and extract structured content"""
#         log_context = f'{filename} ({os.path.basename(filepath)})'

#         try:
#             # Validate user_id if required
#             if user_id is None:
#                 raise ValueError("User ID is required for pitch deck creation")
            
#             # Validate file exists and is accessible
#             if not os.path.exists(filepath):
#                 raise FileNotFoundError(f"File not found: {filepath}")
                
#             file_size = os.path.getsize(filepath)
#             if file_size == 0:
#                 raise ValueError("Empty file provided")
                
#             file_type = 'pdf' if filepath.lower().endswith('.pdf') else 'pptx'

#             # Initialize a new database session
#             db.session.begin()
#             # user_id = 

#             # Create pitch deck record
#             pitch_deck = PitchDeck(
#                 user_id=user_id,
#                 original_filename=filename,
#                 stored_filename=os.path.basename(filepath),
#                 file_size=file_size,
#                 file_type=file_type,
#                 processing_status='processing'
#             )
#             pitch_deck.insert()
#             log_success('process_pitchdeck', f'Created pitch deck {pitch_deck.id} for {log_context}')

#             try:
#                 # Parse file based on type
#                 parser = parse_pdf_to_dict if file_type == 'pdf' else parse_pptx
#                 slides_data = parser(filepath)
#                 log_success("slides_data", slides_data)
#                 log_success('process_pitchdeck', f'Parsed {len(slides_data)} slides from {log_context}')

#                 # for slide_data in slides_data:
#                 #     slide = PitchDeckSlide(
#                 #         deck_id=pitch_deck.id,
#                 #         slide_number=slide_data['slide_number'],
#                 #         title=slide_data.get('title', f'Slide {slide_data["slide_number"]}'),
#                 #         content=prepare_slide_content(slide_data.get('content', {})),
#                 #         # content=slide_data.get('content', ''),
#                 #         notes=slide_data.get('notes'),
#                 #         image_path=slide_data.get('image_path'),
#                 #         meta_data=sanitize_pdf_data(slide_data.get('meta', {}))
#                 #     )
#                 #     db.session.add(slide)

#                 pitch_deck.processing_status = 'completed'
#                 db.session.commit()
#                 log_success('process_pitchdeck', f'Successfully processed {log_context}')
                
#                 # Clean up file after processing
#                 try:
#                     os.remove(filepath)
#                     log_success('process_pitchdeck',  f'Cleaned up file {filepath}')
#                 except OSError as e:
#                     log_error('process_pitchdeck', f'Failed to cleanup file {filepath}: {str(e)}')

#                 return {
#                     'status': 'success', 
#                     'pitch_deck_id': pitch_deck.id,
#                     'slide_count': len(slides_data)
#                 }
#             except Exception as parse_error:
#                 pitch_deck.processing_status = 'failed'
#                 db.session.commit()
#                 log_error('process_pitchdeck', f'Parse failed for {log_context}: {str(parse_error)}')
#                 raise
#         except Exception as task_error:
#             pitch_deck.processing_status = 'failed'
#             db.session.commit()
#             log_error('process_pitchdeck', f'Task failed for {log_context}: {str(task_error)}')
#             raise
#             # self.retry(exc=task_error, countdown=60, max_retries=3)

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
        
        try:
            filename = secure_filename(file.filename)
            upload_folder = get_upload_folder()
            filepath = os.path.join(upload_folder, filename)
           
            log_success('upload_file', f'Uploading {filename}')
           
            file.save(filepath)
           
            # result = process_pitchdeck(filepath, filename, user_id)
            task = process_pitchdeck(filepath, filename, user_id)
            # task = process_pitchdeck.delay(filepath, filename)
            log_success('upload_file', 'File uploaded successfully')
            return {
                'message': 'File uploaded successfully',
                'task_id': task.id
                # 'pitch_deck_id': result['pitch_deck_id']
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
