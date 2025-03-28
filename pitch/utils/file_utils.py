import os 
import json
from PyPDF2.generic import FloatObject, RectangleObject

ALLOWED_EXTENSIONS = {'pdf', 'pptx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_upload_folder():
    upload_folder = os.getenv('UPLOAD_FOLDER')
    # Check if the directory exists, if not, create it
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    return upload_folder

def sanitize_pdf_data(data):
    """Convert PDF-specific objects to serializable formats"""
    if isinstance(data, (FloatObject, RectangleObject)):
        return float(data)
    elif isinstance(data, dict):
        return {k: sanitize_pdf_data(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple)):
        return [sanitize_pdf_data(item) for item in data]
    return data

def prepare_slide_content(content):
    """Prepare slide content for database storage"""
    if not content:
        return {}
    
    # Ensure all content is JSON serializable
    return {
        'headings': list(content.get('headings', [])),
        'paragraphs': list(content.get('paragraphs', [])),
        'bullet_points': list(content.get('bullet_points', [])),
        'key_metrics': [str(m) for m in content.get('key_metrics', [])]
    }