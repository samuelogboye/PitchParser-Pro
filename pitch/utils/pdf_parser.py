import PyPDF2

def parse_pdf(filepath):
    slides = []
    with open(filepath, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for i, page in enumerate(reader.pages):
            slides.append({
                "slide_number": i + 1,
                "title": f"Slide {i + 1}",
                "content": page.extract_text()
            })
    return slides