import os
from pitch.celery.celery import celery_app 
from pitch.models.pitch_deck import PitchDeck
from pitch.models.pitch_deck_slide import PitchDeckSlide
from pitch.utils.pdf_parser import parse_pdf
from pitch.utils.pptx_parser import parse_pptx
from pitch.utils.logger import log_error, log_success
from pitch import db

@celery_app.task(bind=True, name='process_pitchdeck')
def process_pitchdeck(self, filepath, filename):
    log_success('process_pitchdeck', f'Processing {filename}')
    """Process pitch deck file and extract structured content"""
    log_context = f'{filename} ({os.path.basename(filepath)})'

    try:
        # Validate file exists and is accessible
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
            
        file_size = os.path.getsize(filepath)
        if file_size == 0:
            raise ValueError("Empty file provided")
            
        file_type = 'pdf' if filepath.lower().endswith('.pdf') else 'pptx'

        # Create pitch deck record
        pitch_deck = PitchDeck(
            original_filename=filename,
            stored_filename=os.path.basename(filepath),
            file_size=file_size,
            file_type=file_type,
            processing_status='processing'
        )
        pitch_deck.insert()
        log_success('process_pitchdeck', f'Created pitch deck {pitch_deck.id} for {log_context}')

        try:
            # Parse file based on type
            parser = parse_pdf if file_type == 'pdf' else parse_pptx
            slides_data = parser(filepath)
            log_success('process_pitchdeck', f'Parsed {len(slides_data)} slides from {log_context}')

            for slide_data in slides_data:
                slide = PitchDeckSlide(
                    deck_id=pitch_deck.id,
                    slide_number=slide_data['slide_number'],
                    title=slide_data.get('title', f'Slide {slide_data["slide_number"]}'),
                    content=slide_data.get('content', ''),
                    meta_data=slide_data.get('meta', {})
                )
                db.session.add(slide)

            pitch_deck.processing_status = 'completed'
            db.session.commit()
            log_success('process_pitchdeck', f'Successfully processed {log_context}')
            
            # Clean up file after processing
            try:
                os.remove(filepath)
                log_success('process_pitchdeck',  f'Cleaned up file {filepath}')
            except OSError as e:
                log_error('process_pitchdeck', f'Failed to cleanup file {filepath}: {str(e)}')

            return {
                'status': 'success', 
                'pitch_deck_id': pitch_deck.id,
                'slide_count': len(slides_data)
            }
        except Exception as parse_error:
            pitch_deck.processing_status = 'failed'
            db.session.commit()
            log_error('process_pitchdeck', f'Parse failed for {log_context}: {str(parse_error)}')
            raise
    except Exception as task_error:
        log_error('process_pitchdeck', f'Task failed for {log_context}: {str(task_error)}')
        self.retry(exc=task_error, countdown=60, max_retries=3)