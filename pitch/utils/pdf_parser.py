from dataclasses import dataclass
from typing import List, Dict, Optional
import logging
from concurrent.futures import ThreadPoolExecutor
# import PyPDF2
from pitch.utils.logger import log_error, log_success, log_warning
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
                log_warning("extract_text_with_ocr", f"OCR failed for image: {str(e)}")

                # Try alternative image extraction
                try:
                    log_warning("extract_text_with_ocr", f"Trying alternative image extraction for image: {str(e)}")
                    if hasattr(page, 'to_image'):
                        pil_image = page.to_image(resolution=150).original
                        ocr_text.append(pytesseract.image_to_string(pil_image))
                        log_success("extract_text_with_ocr", f"Alternative image extraction succeeded for image: {str(e)}")
                except Exception as fallback_e:
                    log_warning("extract_text_with_ocr", f"Fallback OCR failed: {str(fallback_e)}")
        
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