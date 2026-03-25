import re
import io
import numpy as np
import fitz  # PyMuPDF
from PIL import Image

_reader = None

def _get_reader():
    global _reader
    if _reader is None:
        try:
            import easyocr
            _reader = easyocr.Reader(['en'], gpu=False)
        except: return None
    return _reader

def extract_text_from_image(image_file, target_pan=None, rotations=[0, 180, 90, 270]):
    try:
        if isinstance(image_file, (bytes, bytearray)): image = Image.open(io.BytesIO(image_file))
        elif isinstance(image_file, Image.Image): image = image_file
        else: image = Image.open(image_file)
        
        full_log = ""
        for rotation in rotations:
            try:
                rotated_image = image if rotation == 0 else image.rotate(-rotation, expand=True)
                image_np = np.array(rotated_image)
                reader = _get_reader()
                if not reader: continue
                results = reader.readtext(image_np, detail=0) 
                text = " ".join(results).upper()
                full_log += f" {text}"
                if target_pan and target_pan in re.sub(r'[^A-Z0-9]', '', text): return text, True
            except: continue
        return full_log, False
    except: return "", False

def extract_text_from_pdf(pdf_file, target_pan=None):
    try:
        pdf_content = pdf_file.read()
        pdf_file.seek(0)
        doc = fitz.open(stream=pdf_content, filetype="pdf")
        full_text_log = ""
        for page_num in range(len(doc)):
            text = doc[page_num].get_text().upper()
            full_text_log += f" {text}"
            if target_pan and target_pan in re.sub(r'[^A-Z0-9]', '', text):
                doc.close(); return text, True
        for page_num in range(min(len(doc), 3)):
            page = doc[page_num]
            zoom = 4.0 
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
            ocr_res, found = extract_text_from_image(pix.tobytes("png"), target_pan=target_pan)
            full_text_log += f" {ocr_res}"
            if found: doc.close(); return ocr_res, True
        doc.close(); return full_text_log, False
    except: return "", False