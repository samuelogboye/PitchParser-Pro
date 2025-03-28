# import PyPDF2
# import re
# from typing import List, Dict
# from pitch.utils.logger import log_error, log_success
# import pdfplumber  # Additional PDF parsing library
# from PIL import Image
# import io
# import pytesseract  # OCR for image-based text
# from concurrent.futures import ThreadPoolExecutor


# def extract_structured_content(text: str) -> Dict:
#     """Extract structured content from slide text"""
#     content = {
#         'headings': [],
#         'paragraphs': [],
#         'bullet_points': [],
#         'key_metrics': []
#     }
    
#     lines = [line.strip() for line in text.split('\n') if line.strip()]
    
#     for line in lines:
#         # Detect headings (usually first line or marked with #)
#         if line.startswith('#') or (not content['headings'] and len(line) < 50):
#             content['headings'].append(line.replace('#', '').strip())
#         # Detect bullet points
#         elif line.startswith('- ') or line.startswith('* '):
#             content['bullet_points'].append(line[2:].strip())
#         # Detect key metrics (patterns like $X.XB or XX%)
#         elif re.search(r'\$\d+\.?\d*[BMK]|\d+%', line):
#             content['key_metrics'].append(line)
#         else:
#             content['paragraphs'].append(line)
    
#     return content

# def extract_text_with_ocr(page) -> str:
#     """Extract text using OCR if needed"""
#     text = page.extract_text()
#     if text and len(text.split()) > 5:  # Minimum word count threshold
#         return text
        
#     # Fallback to OCR if text extraction fails
#     images = page.images
#     if images:
#         ocr_text = []
#         for img in images:
#             try:
#                 img_data = img["stream"].get_data()
#                 img_obj = Image.open(io.BytesIO(img_data))
#                 ocr_text.append(pytesseract.image_to_string(img_obj))
#             except Exception as e:
#                 logger.warning(f"OCR failed for image: {str(e)}")
#         return "\n".join(ocr_text)
        
#     return ""

# def parse_pdf_page(page, page_num: int) -> Optional[Slide]:
#     """Parse a single PDF page with enhanced text extraction"""
#     try:
#         with pdfplumber.open(page) as pdf_page:
#             # Try multiple extraction methods
#             text = pdf_page.extract_text()
#             if not text or len(text.split()) < 5:
#                 text = extract_text_with_ocr(pdf_page)
                
#             if not text:
#                 return None
                
#             structured_content = extract_structured_content(text)
            
#             # Get images metadata
#             images = []
#             if pdf_page.images:
#                 images = [{"size": img["width"] * img["height"], "type": img["name"]} 
#                          for img in pdf_page.images]
            
#             # Determine title (first heading or default)
#             title = (
#                 structured_content.headings[0] 
#                 if structured_content.headings 
#                 else f"Slide {page_num}"
#             )
            
#             return Slide(
#                 number=page_num,
#                 title=title,
#                 content=structured_content,
#                 meta={
#                     "page_size": [float(x) for x in pdf_page.width, pdf_page.height]],
#                     "has_images": bool(pdf_page.images),
#                     "word_count": len(text.split()),
#                     "images": images
#                 }
#             )
#     except Exception as e:
#         log_error("parse_pdf_page", f"Error parsing page {page_num}: {str(e)}")
#         return None
    
# # def _parse_pdf_raw(filepath: str) -> List[Dict]:
# #     """Parse PDF file into structured slides data"""
# #     slides = []
    
# #     try:
# #         with open(filepath, 'rb') as file:
# #             reader = PyPDF2.PdfReader(file)
# #             log_success("reader.pages", reader.pages)
            
# #             for i, page in enumerate(reader.pages):
# #                 raw_text = page.extract_text() or ''
# #                 log_success("raw_text", raw_text)
# #                 structured_content = extract_structured_content(raw_text)
                
# #                 # Determine title (first heading or default)
# #                 title = (
# #                     structured_content['headings'][0] 
# #                     if structured_content['headings'] 
# #                     else f"Slide {i + 1}"
# #                 )
                
# #                 slides.append({
# #                     "slide_number": i + 1,
# #                     "title": title,
# #                     "content": structured_content,
# #                     "meta": {
# #                         "page_size": page.mediabox,
# #                         "has_images": '/XObject' in page.get('/Resources', {}),
# #                         "word_count": len(raw_text.split())
# #                     }
# #                 })
                
# #     except Exception as e:
# #         raise ValueError(f"Failed to parse PDF: {str(e)}")
    
# #     return slides

# def parse_pdf(filepath: str) -> List[Slide]:
#     """Parse PDF with parallel processing and enhanced extraction"""
#     slides = []
    
#     try:
#         with open(filepath, 'rb') as file:
#             # Use PyPDF2 for initial document structure
#             pdf_reader = PyPDF2.PdfReader(file)
            
#             # Use pdfplumber for better content extraction
#             with pdfplumber.open(filepath) as pdf:
#                 # Process pages in parallel for better performance
#                 with ThreadPoolExecutor() as executor:
#                     futures = [
#                         executor.submit(parse_pdf_page, pdf.pages[i], i+1)
#                         for i in range(len(pdf.pages))
#                     ]
                    
#                     for future in futures:
#                         slide = future.result()
#                         if slide:
#                             slides.append(slide)
                            
#     except Exception as e:
#         log_error("parse_pdf", f"Failed to parse PDF: {str(e)}")
#         raise ValueError(f"PDF parsing failed: {str(e)}")
    
#     # Post-processing to improve title detection
#     for i, slide in enumerate(slides):
#         # If title is generic, try to find better title from content
#         if slide.title.startswith("Slide ") and slide.content.headings:
#             slide.title = slide.content.headings[0]
            
#     return slides

# # def parse_pdf(filepath):
# #     """Parse PDF and return clean slide data"""
# #     raw_slides = _parse_pdf_raw(filepath)  
# #     log_success("parse_pdf", raw_slides)
    
# #     slides = []
# #     for i, slide in enumerate(raw_slides, 1):
# #         slides.append({
# #             'slide_number': i,
# #             'title': slide.get('title', f'Slide {i}'),
# #             'content': {
# #                 'headings': list(slide.get('headings', [])),
# #                 'paragraphs': list(slide.get('paragraphs', [])),
# #                 'bullet_points': list(slide.get('bullet_points', [])),
# #                 'key_metrics': [str(m) for m in slide.get('key_metrics', [])]
# #             },
# #             'meta': {
# #                 'page_size': list(map(float, slide.get('page_size', [0, 0]))),
# #                 'has_images': bool(slide.get('has_images')),
# #                 'word_count': int(slide.get('word_count', 0))
# #             }
# #         })
# #     return slides

# def parse_pdf_to_dict(filepath: str) -> List[Dict]:
#     """Parse PDF and return as list of dictionaries"""
#     slides = parse_pdf(filepath)
#     return [
#         {
#             "slide_number": slide.number,
#             "title": slide.title,
#             "content": {
#                 "headings": slide.content.headings,
#                 "paragraphs": slide.content.paragraphs,
#                 "bullet_points": slide.content.bullet_points,
#                 "key_metrics": slide.content.key_metrics,
#                 "images": slide.content.images
#             },
#             "meta": slide.meta
#         }
#         for slide in slides
#     ]

from dataclasses import dataclass
from typing import List, Dict, Optional
import logging
from concurrent.futures import ThreadPoolExecutor
# import PyPDF2
import pdfplumber
from PIL import Image
import io
import pytesseract
import re
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SlideContent:
    headings: List[str]
    paragraphs: List[str]
    bullet_points: List[str]
    key_metrics: List[str]
    images: List[Dict]

@dataclass
class Slide:
    number: int
    title: str
    content: SlideContent
    meta: Dict

def extract_structured_content(text: str) -> SlideContent:
    """Extract structured content from slide text"""
    headings = []
    paragraphs = []
    bullet_points = []
    key_metrics = []
    
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    for line in lines:
        # Detect headings (first line, marked with #, or ALL CAPS)
        if (line.startswith('#') or 
            (not headings and len(line) < 100) or
            re.match(r'^[A-Z][A-Z0-9 ]+$', line)):
            headings.append(re.sub(r'^#+\s*', '', line))
        # Detect bullet points
        elif re.match(r'^[\-\*•›]\s', line):
            bullet_points.append(re.sub(r'^[\-\*•›]\s*', '', line))
        # Detect key metrics
        elif re.search(r'(?:\$|€|£)\d+(?:\.\d+)?[BMK]?|\d+\%|\d+x', line, re.IGNORECASE):
            key_metrics.append(line)
        # Longer text blocks as paragraphs
        elif len(line) > 60:
            paragraphs.append(line)
    
    return SlideContent(
        headings=headings,
        paragraphs=paragraphs,
        bullet_points=bullet_points,
        key_metrics=key_metrics,
        images=[]
    )

def extract_text_with_ocr(page) -> str:
    """Extract text using OCR if needed"""
    text = page.extract_text()
    if text and len(text.split()) > 5:  # Minimum word count threshold
        return text
        
    # Fallback to OCR if text extraction fails
    if hasattr(page, 'images') and page.images:
        ocr_text = []
        for img in page.images:
            try:
                img_data = img["stream"].get_data()
                img_obj = Image.open(io.BytesIO(img_data))
                ocr_text.append(pytesseract.image_to_string(img_obj))
            except Exception as e:
                logger.warning(f"OCR failed for image: {str(e)}")
        return "\n".join(ocr_text)
        
    return ""

def parse_pdf_page(pdf_page, page_num: int) -> Optional[Slide]:
    """Parse a single PDF page with enhanced text extraction"""
    try:
        # Try multiple extraction methods
        text = pdf_page.extract_text()
        if not text or len(text.split()) < 5:
            text = extract_text_with_ocr(pdf_page)
            
        if not text:
            return None
            
        structured_content = extract_structured_content(text)
        
        # Get images metadata
        images = []
        if hasattr(pdf_page, 'images') and pdf_page.images:
            images = [{
                "size": img["width"] * img["height"], 
                "type": img.get("name", "unknown")
            } for img in pdf_page.images]
        
        # Determine title (first heading or default)
        title = (
            structured_content.headings[0] 
            if structured_content.headings 
            else f"Slide {page_num}"
        )
        
        return Slide(
            number=page_num,
            title=title,
            content=SlideContent(
                headings=structured_content.headings,
                paragraphs=structured_content.paragraphs,
                bullet_points=structured_content.bullet_points,
                key_metrics=structured_content.key_metrics,
                images=images
            ),
            meta={
                "page_size": [float(pdf_page.width), float(pdf_page.height)],
                "has_images": bool(images),
                "word_count": len(text.split())
            }
        )
    except Exception as e:
        logger.error(f"Error parsing page {page_num}: {str(e)}")
        return None

def parse_pdf(filepath: str) -> List[Slide]:
    """Parse PDF with parallel processing and enhanced extraction"""
    slides = []
    
    try:
        with open(filepath, 'rb') as file:
            # Use pdfplumber for better content extraction
            with pdfplumber.open(filepath) as pdf:
                # Process pages in parallel for better performance
                with ThreadPoolExecutor() as executor:
                    futures = [
                        executor.submit(parse_pdf_page, pdf.pages[i], i+1)
                        for i in range(len(pdf.pages))
                    ]
                    
                    for future in futures:
                        slide = future.result()
                        if slide:
                            slides.append(slide)
                            
    except Exception as e:
        logger.error(f"Failed to parse PDF: {str(e)}")
        raise ValueError(f"PDF parsing failed: {str(e)}")
    
    # Post-processing to improve title detection
    for slide in slides:
        if slide.title.startswith("Slide ") and slide.content.headings:
            slide.title = slide.content.headings[0]
            
    return slides