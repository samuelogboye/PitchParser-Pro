''' Tasks related to our celery functions '''
import os
from pitch.models.pitch_deck import PitchDeck
from pitch.models.pitch_deck_slide import PitchDeckSlide
from pitch.utils.pdf_parser import parse_pdf
from pitch.utils.pptx_parser import parse_pptx
from pitch.utils.logger import log_error, log_success, log_warning
# from pitch import db, create_app  # Import create_app from your application
from pitch.extensions import celery, db
from celery.result import AsyncResult
from uuid import UUID
from PIL import Image

def get_task(task_id):
    '''
    To be called from web app.
    The job ID is passed and the celery job is returned.
    '''
    return AsyncResult(task_id, app=celery)

@celery.task(bind=True)
def process_pitchdeck(self, filepath: str, filename: str, user_id):
    """Process pitch deck file and store in database"""
    from pitch import create_app  # Lazy import to avoid circular imports
    app = create_app()
    
    with app.app_context():  # Ensure Flask app context
        log_success("process_pitchdeck", f'Processing pitch deck: {filename}')
        
        try:
            # Validate inputs
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"File not found: {filepath}")
                
            file_size = os.path.getsize(filepath)
            if file_size == 0:
                raise ValueError("Empty file provided")
                
            file_type = 'pdf' if filename.lower().endswith('.pdf') else 'pptx'
            
            # Convert user_id if it's a string
            try:
                if isinstance(user_id, str):
                    user_id = UUID(user_id)
            except ValueError as e:
                raise ValueError(f"Invalid user_id format: {user_id}") from e

            # Create pitch deck record
            pitch_deck = PitchDeck(
                user_id=user_id,
                original_filename=filename,
                stored_filename=os.path.basename(filepath),
                file_size=file_size,
                file_type=file_type,
                processing_status='processing'
            )
            pitch_deck.insert()
            
            try:
                # Parse the file
                slides = parse_pdf(filepath) if file_type == 'pdf' else []
                
                # Store slides in database
                for slide in slides:
                    slide_db = PitchDeckSlide(
                        deck_id=pitch_deck.id,
                        slide_number=slide.number,
                        title=slide.title,
                        content={
                            'headings': slide.content.headings,
                            'paragraphs': slide.content.paragraphs,
                            'bullet_points': slide.content.bullet_points,
                            'key_metrics': slide.content.key_metrics,
                            'images': slide.content.images
                        },
                        meta_data=slide.meta
                    )
                    db.session.add(slide_db)
                
                # Update status
                pitch_deck.processing_status = 'completed'
                db.session.commit()
                
                log_success("process_pitchdeck", 
                          f'Successfully processed {filename} with {len(slides)} slides')
                return {
                    'status': 'success',
                    'pitch_deck_id': str(pitch_deck.id),
                    'slide_count': len(slides)
                }
                
            except Exception as parse_error:
                pitch_deck.processing_status = 'failed'
                db.session.commit()
                log_error("process_pitchdeck", 
                         f'Parse failed for {filename}: {str(parse_error)}')
                raise parse_error
                
        except Exception as e:
            log_error("process_pitchdeck", 
                     f'Failed to process {filename}: {str(e)}')
            if 'pitch_deck' in locals():
                db.session.rollback()
            raise e
        finally:
            # Clean up the file
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception as e:
                log_warning("process_pitchdeck", 
                          f'Failed to cleanup file {filepath}: {str(e)}')