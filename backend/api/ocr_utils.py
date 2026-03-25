import io
import re
import numpy as np
import fitz  # PyMuPDF
from PIL import Image

# Global variable for the reader
_reader = None

def _get_reader():
    global _reader
    if _reader is None:
        try:
            import easyocr
            _reader = easyocr.Reader(['en'], gpu=False)
        except:
            return None
    return _reader

def extract_text_from_image(image_file, target_pan=None, rotations=[0, 180, 90, 270]):
    """
    Extract text from an image using EasyOCR with multiple rotations.
    If target_pan is provided, it attempts to find and return it.
    """
    try:
        if isinstance(image_file, (bytes, bytearray)):
            image = Image.open(io.BytesIO(image_file))
        elif isinstance(image_file, Image.Image):
            image = image_file
        else:
            image = Image.open(image_file)
        
        full_log = ""
        pan_pattern = re.compile(r'[A-Z]{5}[0-9]{4}[A-Z]{1}')

        for rotation in rotations:
            try:
                rotated_image = image if rotation == 0 else image.rotate(-rotation, expand=True)
                image_np = np.array(rotated_image)
                reader = _get_reader()
                if not reader:
                    continue
                results = reader.readtext(image_np, detail=0) 
                text = " ".join(results).upper()
                full_log += f" {text}"

                # Direct match
                if target_pan and target_pan in re.sub(r'[^A-Z0-9]', '', text):
                    return text, True
                
                # Robust match (no spaces)
                text_nospaces = text.replace(" ", "")
                if target_pan and target_pan in text_nospaces:
                    return text, True
                
                # Find any PAN if target_pan not explicitly found yet
                match_nospaces = pan_pattern.search(text_nospaces)
                if match_nospaces and target_pan and match_nospaces.group(0) == target_pan:
                    return match_nospaces.group(0), True
                
            except:
                continue
        return full_log, False
    except Exception as e:
        return f"OCR Failed: {str(e)}", False

def extract_text_from_pdf(pdf_file, target_pan=None):
    """
    Extract text from a PDF. Tries selectable text first, then falls back to OCR.
    Used for PAN verification and general extraction.
    """
    try:
        if hasattr(pdf_file, 'read'):
            pdf_content = pdf_file.read()
            pdf_file.seek(0)
        else:
            pdf_content = pdf_file

        doc = fitz.open(stream=pdf_content, filetype="pdf")
        full_text_log = ""
        
        # Step 1: Try direct text extraction (selectable text)
        for page_num in range(len(doc)):
            text = doc[page_num].get_text().upper()
            full_text_log += f" {text}"
            if target_pan and target_pan in re.sub(r'[^A-Z0-9]', '', text):
                doc.close()
                return text, True
        
        # Step 2: Fallback to OCR (scanned PDF) for first few pages or if target not found
        for page_num in range(min(len(doc), 3)):
            page = doc[page_num]
            zoom = 4.0 
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
            ocr_res, found = extract_text_from_image(pix.tobytes("png"), target_pan=target_pan)
            full_text_log += f" {ocr_res}"
            if found:
                doc.close()
                return ocr_res, True
                
        doc.close()
        return full_text_log, False
    except Exception as e:
        return f"PDF Extraction Failed: {str(e)}", False

def extract_text_from_pdf_ocr(file_content):
    """
    Extract text from a scanned/non-selectable PDF using OCR for all pages.
    Used for skills extraction where full content is needed.
    """
    try:
        import os
        from django.utils import timezone
        debug_log = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ocr_debug_log.txt")

        def log(msg):
            try:
                with open(debug_log, "a", encoding="utf-8") as f:
                    f.write(f"[{timezone.now()}] {msg}\n")
            except:
                pass

        log("Starting Full PDF OCR (Skills Extraction)")

        reader = _get_reader()
        if not reader:
            log("EasyOCR reader failed to initialize")
            return ""

        all_text = ""
        doc = fitz.open(stream=file_content, filetype="pdf")
        log(f"fitz opened PDF with {len(doc)} pages")

        for page_num in range(len(doc)):
            try:
                page = doc[page_num]
                # Render at 2x zoom for skills OCR
                mat = fitz.Matrix(2, 2)
                pix = page.get_pixmap(matrix=mat)
                image_np = np.array(Image.open(io.BytesIO(pix.tobytes("png"))))
                results = reader.readtext(image_np, detail=0)
                page_text = " ".join(results)
                log(f"Page {page_num}: {len(page_text)} chars extracted")
                if page_text.strip():
                    all_text += page_text + "\n"
            except Exception as e:
                log(f"Error on page {page_num}: {e}")

        doc.close()
        log(f"OCR complete. Total chars: {len(all_text)}")
        return all_text.strip()

    except Exception as e:
        try:
            import traceback
            err_log = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ocr_error.txt")
            with open(err_log, "a") as f:
                f.write(f"Critical OCR error: {str(e)}\n{traceback.format_exc()}\n")
        except:
            pass
        return ""
