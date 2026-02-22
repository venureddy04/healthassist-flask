import PyPDF2
import easyocr
from PIL import Image
import numpy as np

def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def extract_text_from_image(image_file):
    try:
        reader = easyocr.Reader(['en'], gpu=False)
        image = Image.open(image_file)
        image_np = np.array(image)
        results = reader.readtext(image_np, detail=0)
        text = "\n".join(results)
        return text.strip() if text else "No text detected"
    except Exception as e:
        return f"Error: {str(e)}"