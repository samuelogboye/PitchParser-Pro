from pptx import Presentation

def parse_pptx(filepath):
    slides = []
    prs = Presentation(filepath)
    for i, slide in enumerate(prs.slides):
        content = "\n".join([shape.text for shape in slide.shapes if hasattr(shape, "text")])
        slides.append({
            "slide_number": i + 1,
            "title": f"Slide {i + 1}",
            "content": content
        })
    return slides