import io
import re
import numpy as np
from PIL import Image
import PyPDF2

# Global variable for the reader
_reader = None

def _get_reader():
    """Lazy initialization of the EasyOCR reader"""
    global _reader
    if _reader is None:
        try:
            import easyocr
            _reader = easyocr.Reader(['en'], gpu=False)
        except Exception as e:
            return None
    return _reader

def extract_text_from_image(image_file, strategies=['Standard'], rotations=[0, 90, 180, 270]):
    """
    Extract text from an image file using EasyOCR with rotation support.
    """
    try:
        # EasyOCR expects file path, bytes, or numpy array. 
        # Since we have an UploadedFile/memory file, we convert to bytes/image.
        image = Image.open(image_file)
        
        extracted_text_log = ""
        
        # PAN pattern to look for
        pan_pattern = re.compile(r'[A-Z]{5}[0-9]{4}[A-Z]{1}')

        for rotation in rotations:
            try:
                # Rotate image
                if rotation == 0:
                    rotated_image = image
                else:
                    rotated_image = image.rotate(-rotation, expand=True)

                # Convert PIL image to bytes or numpy array for EasyOCR
                # EasyOCR works well with numpy arrays
                image_np = np.array(rotated_image)
                
                # Extract text
                # detail=0 returns just the list of strings
                reader = _get_reader()
                if not reader:
                    return extracted_text_log + "\nOCR Reader failed to initialize", False
                    
                results = reader.readtext(image_np, detail=0) 
                text = " ".join(results)
                
                extracted_text_log += f"\n--- Rotation {rotation} ---\n{text}"
                
                # Check for match immediately
                match = pan_pattern.search(text)
                if match:
                    return match.group(0), True # Found valid PAN

                # Also try concatenated text (sometimes spaces break the pattern)
                text_nospaces = text.replace(" ", "")
                match_nospaces = pan_pattern.search(text_nospaces)
                if match_nospaces:
                    return match_nospaces.group(0), True

            except Exception as e:
                continue

        return extracted_text_log, False

    except Exception as overall_e:
        return f"OCR Failed: {str(overall_e)}", False


def extract_text_from_pdf_ocr(file_content):
    """
    Extract text from a scanned/non-selectable PDF using OCR.
    Uses pymupdf (fitz) to render each page as an image, then EasyOCR to read text.
    No external binaries (Poppler) required.
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

        log("Starting PDF OCR via fitz (pymupdf) rendering")

        reader = _get_reader()
        if not reader:
            log("EasyOCR reader failed to initialize")
            return ""

        all_text = ""

        try:
            import fitz  # pymupdf
            doc = fitz.open(stream=file_content, filetype="pdf")
            log(f"fitz opened PDF with {len(doc)} pages")

            for page_num in range(len(doc)):
                try:
                    page = doc[page_num]
                    # Render at 2x zoom (144 DPI) for better OCR accuracy
                    mat = fitz.Matrix(2, 2)
                    pix = page.get_pixmap(matrix=mat)
                    # Convert pixmap to PIL Image
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    image_np = np.array(img)
                    results = reader.readtext(image_np, detail=0)
                    page_text = " ".join(results)
                    log(f"Page {page_num}: {len(page_text)} chars extracted")
                    if page_text.strip():
                        all_text += page_text + "\n"
                except Exception as e:
                    log(f"Error on page {page_num}: {e}")

            doc.close()

        except ImportError:
            log("fitz not available, trying pdf2image fallback")
            try:
                from pdf2image import convert_from_bytes
                pages = convert_from_bytes(file_content, dpi=200)
                log(f"pdf2image rendered {len(pages)} pages")
                for page_num, page_image in enumerate(pages):
                    try:
                        image_np = np.array(page_image.convert('RGB'))
                        results = reader.readtext(image_np, detail=0)
                        page_text = " ".join(results)
                        log(f"Page {page_num}: {len(page_text)} chars via pdf2image")
                        if page_text.strip():
                            all_text += page_text + "\n"
                    except Exception as e:
                        log(f"OCR error on page {page_num}: {e}")
            except Exception as e:
                log(f"pdf2image fallback also failed: {e}")

        log(f"OCR complete. Total chars: {len(all_text)}")
        return all_text.strip()

    except Exception as e:
        try:
            import os, traceback
            err_log = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ocr_error.txt")
            with open(err_log, "a") as f:
                f.write(f"Critical error: {str(e)}\n{traceback.format_exc()}\n")
        except:
            pass
        return ""