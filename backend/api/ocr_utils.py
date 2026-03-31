import io
import re
import os
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

def normalize_pan_format(s):
    """
    Normalizes a 10-character string that is likely a PAN by correcting common OCR misreads.
    Positional logic: AAAAA 9999 A
    """
    if not s or len(s) != 10:
        return s
    
    res = ""
    for i, char in enumerate(s.upper()):
        if 0 <= i <= 4 or i == 9: # Positions that should be Letters
            if char == '0': res += 'O'
            elif char == '1': res += 'I'
            elif char == '2': res += 'Z'
            elif char == '5': res += 'S'
            elif char == '8': res += 'B'
            elif char == '6': res += 'G'
            else: res += char
        else: # Positions that should be Digits
            if char in "OQ": res += "0"
            elif char in "I|L": res += "1"
            elif char == "S": res += "5"
            elif char == "Z": res += "2"
            elif char == "B": res += "8"
            elif char == "G": res += "6"
            else: res += char
    return res

def extract_text_from_image(image_file, target_pan=None, rotations=[0, 180, 90, 270]):
    """
    Extract text from an image using EasyOCR with multiple rotations.
    If target_pan is provided, it attempts to find and return it.
    """
    from django.utils import timezone
    from django.conf import settings
    
    log_file = os.path.join(settings.BASE_DIR, "ocr_debug.txt")
    
    def log(msg):
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timezone.now()}] {msg}\n")
        except:
            pass

    try:
        if isinstance(image_file, (bytes, bytearray)):
            image = Image.open(io.BytesIO(image_file))
        elif isinstance(image_file, Image.Image):
            image = image_file
        elif hasattr(image_file, 'temporary_file_path'):
            image = Image.open(image_file.temporary_file_path())
        elif hasattr(image_file, 'read'):
            image_file.seek(0)
            image = Image.open(io.BytesIO(image_file.read()))
            image_file.seek(0)
        else:
            image = Image.open(image_file)
        
        # Ensure image is in RGB mode for OCR
        if image.mode != "RGB":
            image = image.convert("RGB")
            
        full_log = ""
        pan_pattern = re.compile(r'[A-Z]{5}[0-9]{4}[A-Z]{1}')

        for rotation in rotations:
            try:
                rotated_image = image if rotation == 0 else image.rotate(-rotation, expand=True)
                image_np = np.array(rotated_image)
                reader = _get_reader()
                if not reader:
                    log("EasyOCR reader not available")
                    continue
                
                log(f"Running OCR on rotation {rotation}")
                results = reader.readtext(image_np, detail=0) 
                text = " ".join(results).upper()
                full_log += f" {text}"

                # Direct match
                clean_extracted_text = re.sub(r'[^A-Z0-9]', '', text)
                if target_pan and target_pan in clean_extracted_text:
                    log(f"Direct match found at rotation {rotation}")
                    return text, True
                
                # Robust match (no spaces)
                text_nospaces = text.replace(" ", "")
                if target_pan:
                    if target_pan in text_nospaces:
                        log(f"No-spaces match found at rotation {rotation}")
                        return text, True
                    # Positional fuzzy check on slices
                    for i in range(len(text_nospaces) - 9):
                        if normalize_pan_format(text_nospaces[i:i+10]) == target_pan:
                            log(f"Fuzzy slice match found at rotation {rotation}")
                            return text, True
                
                # Find any PAN if target_pan not explicitly found yet
                match_raw = pan_pattern.search(text_nospaces)
                if match_raw and target_pan and match_raw.group(0) == target_pan:
                    log(f"Regex match found at rotation {rotation}")
                    return match_raw.group(0), True
                
            except Exception as e:
                log(f"Rotation {rotation} failed: {e}")
                continue
        return full_log.strip(), False
    except Exception as e:
        log(f"Image OCR Failed: {e}")
        return f"OCR Failed: {str(e)}", False

def extract_text_from_pdf(pdf_file, target_pan=None):
    """
    Extract text from a PDF. Tries selectable text (with multiple methods) first, 
    then falls back to OCR.
    """
    from django.utils import timezone
    from django.conf import settings
    
    log_file = os.path.join(settings.BASE_DIR, "ocr_debug.txt")
    
    def log(msg):
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timezone.now()}] {msg}\n")
        except:
            pass

    log(f"Starting PDF Extraction for PAN: {target_pan}")
    
    try:
        # Load PDF content reliably
        if hasattr(pdf_file, 'temporary_file_path'):
            doc = fitz.open(pdf_file.temporary_file_path())
            pdf_content = open(pdf_file.temporary_file_path(), 'rb').read()
        elif hasattr(pdf_file, 'read'):
            pdf_file.seek(0)
            pdf_content = pdf_file.read()
            pdf_file.seek(0)
            doc = fitz.open(stream=pdf_content, filetype="pdf")
        else:
            pdf_content = pdf_file
            doc = fitz.open(stream=pdf_content, filetype="pdf")

        full_text_log = ""
        log(f"Opened PDF with {len(doc)} pages")
        
        # Step 1: Try direct text extraction (selectable text)
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Method 1: Simple PyMuPDF text
            text = (page.get_text() or "").upper()
            full_text_log += f" {text}"
            
            # Method 2: Word-based PyMuPDF
            try:
                words = page.get_text("words")
                word_text = " ".join([w[4] for w in words]).upper()
                full_text_log += f" {word_text}"
            except: word_text = ""

            # Method 3: Block-based PyMuPDF
            try:
                blocks = page.get_text("blocks")
                block_text = " ".join([b[4] for b in blocks]).upper()
                full_text_log += f" {block_text}"
            except: block_text = ""

            if target_pan:
                clean_target = re.sub(r'[^A-Z0-9]', '', target_pan)
                if clean_target in re.sub(r'[^A-Z0-9]', '', text) or \
                   clean_target in re.sub(r'[^A-Z0-9]', '', word_text) or \
                   clean_target in re.sub(r'[^A-Z0-9]', '', block_text):
                    log(f"Match found in selectable text on page {page_num}")
                    doc.close()
                    return text + " " + word_text + " " + block_text, True

        # Method 4: pdfplumber fallback
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
                plumber_text = ""
                for page in pdf.pages:
                    p_text = (page.extract_text() or "").upper()
                    plumber_text += " " + p_text
                full_text_log += f" {plumber_text}"
                log("pdfplumber extracted content")
                if target_pan:
                    clean_target = re.sub(r'[^A-Z0-9]', '', target_pan)
                    if clean_target in re.sub(r'[^A-Z0-9]', '', plumber_text):
                        log("Match found via pdfplumber")
                        doc.close()
                        return plumber_text, True
        except Exception as e:
            log(f"pdfplumber skipped: {e}")

        # Method 5: PyPDF2 fallback
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            pypdf2_text = ""
            for i in range(len(reader.pages)):
                p_text = (reader.pages[i].extract_text() or "").upper()
                pypdf2_text += " " + p_text
            full_text_log += f" {pypdf2_text}"
            log("PyPDF2 extracted content")
            if target_pan:
                clean_target = re.sub(r'[^A-Z0-9]', '', target_pan)
                if clean_target in re.sub(r'[^A-Z0-9]', '', pypdf2_text):
                    log("Match found via PyPDF2")
                    doc.close()
                    return pypdf2_text, True
        except Exception as e:
            log(f"PyPDF2 skipped: {e}")

        # Step 2: Fallback to OCR (scanned PDF)
        log("Falling back to OCR step (Scanned PDF)")
        for page_num in range(min(len(doc), 3)):
            try:
                page = doc[page_num]
                # Render at 300 DPI for standard professional OCR
                pix = page.get_pixmap(dpi=300, alpha=False)
                ocr_res, found = extract_text_from_image(pix.tobytes("png"), target_pan=target_pan)
                full_text_log += f" {ocr_res}"
                if found:
                    log(f"Match found via OCR on page {page_num}")
                    doc.close()
                    return ocr_res, True
            except Exception as e:
                log(f"Page {page_num} OCR failed: {e}")
                
        doc.close()
        log("No definitive match found")
        return full_text_log, False
    except Exception as e:
        log(f"Critical PDF Error: {e}")
        return f"PDF Extraction Failed: {str(e)}", False

def extract_text_from_pdf_ocr(file_content):
    """
    Extract text from a scanned/non-selectable PDF using OCR for all pages.
    Used for skills extraction where full content is needed.
    """
    try:
        from django.utils import timezone
        from django.conf import settings
        log_file = os.path.join(settings.BASE_DIR, "ocr_debug.txt")

        def log(msg):
            try:
                with open(log_file, "a", encoding="utf-8") as f:
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
        return ""
