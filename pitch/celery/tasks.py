import os
from .celery import celery
from pitch.models.pitch_deck import PitchDeck
from pitch.models.pitch_deck_slide import PitchDeckSlide
from pitch.utils.pdf_parser import parse_pdf
from pitch.utils.pptx_parser import parse_pptx
from pitch.utils.logger import log_error, log_success
from pitch import db

@celery.task(bind=True)
def process_pitchdeck(self, filepath, filename):
    try:
        pitch_deck = PitchDeck(
            original_filename=filename,
            stored_filename=os.path.basename(filepath),
            file_size=os.path.getsize(filepath),
            file_type='pdf' if filepath.endswith('.pdf') else 'pptx',
            processing_status='processing'
        )
        pitch_deck.insert()

        try:
            if filepath.endswith('.pdf'):
                slides_data = parse_pdf(filepath)
            elif filepath.endswith('.pptx'):
                slides_data = parse_pptx(filepath)

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
            log_success('process_pitchdeck', f'Successfully processed {filename}')
            
            # Clean up file after processing
            try:
                os.remove(filepath)
            except OSError as e:
                log_error('process_pitchdeck', f'Failed to remove file {filepath}: {str(e)}')

            return {'status': 'success', 'pitch_deck_id': pitch_deck.id}
        except Exception as e:
            pitch_deck.processing_status = 'failed'
            db.session.commit()
            raise
    except Exception as e:
        log_error('process_pitchdeck', str(e))
        raise