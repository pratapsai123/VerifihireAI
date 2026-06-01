import re
import os
import io
import numpy as np
import fitz  # PyMuPDF
import logging
import traceback
import cv2
import requests
import base64
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
                # We use detail=1 to get bounding boxes, which might help in name extraction
                results_with_detail = reader.readtext(image_np)
                results = [res[1] for res in results_with_detail]
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

def detect_face_in_image(image_file):
    """
    Detects human face in the given image file.
    Accepts file path, bytes, or PIL Image.
    Returns (bool, int) -> (is_face_detected, face_count)
    """
    import cv2
    import numpy as np
    from PIL import Image
    import io

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

        # Convert to BGR for OpenCV
        if image.mode != "RGB":
            image = image.convert("RGB")
        image_np = np.array(image)
        image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

        # Load Haar Cascade
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(50, 50) # Increased minSize to ensure face is clear
        )

        if len(faces) > 0:
            return True, len(faces)
        return False, 0
    except Exception as e:
        print(f"Face Detection Error: {e}")
        return False, 0

def register_face_with_deepface(person_id, image_data):
    """
    Registers a face with DeepFace DIRECTLY in the backend (no microservice needed).
    """
    try:
        from deepface import DeepFace
        from django.conf import settings
        import shutil

        # Setup directory for identity storage
        identities_dir = os.path.join(settings.MEDIA_ROOT, 'identities', person_id)
        if os.path.exists(identities_dir):
            shutil.rmtree(identities_dir)
        os.makedirs(identities_dir, exist_ok=True)

        # Process image data
        if hasattr(image_data, 'read'):
            image_data.seek(0)
            img_bytes = image_data.read()
            image_data.seek(0)
            img_path = os.path.join(identities_dir, "canonical.jpg")
            with open(img_path, "wb") as f:
                f.write(img_bytes)
        elif isinstance(image_data, str) and image_data.startswith('data:image'):
            img_b64 = image_data.split(',', 1)[1]
            img_bytes = base64.b64decode(img_b64)
            img_path = os.path.join(identities_dir, "canonical.jpg")
            with open(img_path, "wb") as f:
                f.write(img_bytes)
        else:
            # Assume it's a file path or bytes
            img_path = image_data

        # We don't actually need to "register" in a DB here, just ensure a face exists
        # and we can use it as a reference later.
        objs = DeepFace.extract_faces(
            img_path = img_path, 
            detector_backend = 'retinaface',
            enforce_detection = True,
            align = True
        )
        
        if not objs:
            return {"success": False, "message": "No face detected in the image."}

        return {"success": True, "message": "Face identity established internally."}
    except Exception as e:
        print(f"Internal DeepFace Registration Error: {e}")
        return {"success": False, "message": str(e)}

def verify_face_with_deepface(person_id, snapshot_base64):
    """
    Verifies a snapshot against a registered identity DIRECTLY in the backend.
    """
    try:
        from deepface import DeepFace
        from django.conf import settings
        
        # Reference image path
        ref_path = os.path.join(settings.MEDIA_ROOT, 'identities', person_id, "canonical.jpg")
        if not os.path.exists(ref_path):
            return {"verified": False, "message": "No registered identity found for this person."}

        # Current snapshot
        if ',' in snapshot_base64:
            snapshot_base64 = snapshot_base64.split(',', 1)[1]
        
        snapshot_bytes = base64.b64decode(snapshot_base64)
        
        # Save temp snapshot for DeepFace
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        temp_snap_path = os.path.join(temp_dir, f"snap_{person_id}.jpg")
        with open(temp_snap_path, "wb") as f:
            f.write(snapshot_bytes)

        # Verification using ArcFace (High accuracy)
        result = DeepFace.verify(
            img1_path = ref_path,
            img2_path = temp_snap_path,
            model_name = "ArcFace",
            detector_backend = "retinaface",
            enforce_detection = True,
            align = True
        )
        
        # Cleanup temp file
        if os.path.exists(temp_snap_path):
            os.remove(temp_snap_path)

        return {
            "verified": result["verified"],
            "distance": result["distance"],
            "threshold": result["threshold"],
            "model": result["model"],
            "detector": result["detector_backend"]
        }
    except Exception as e:
        print(f"Internal DeepFace Verification Error: {e}")
        return {"verified": False, "message": str(e)}

def extract_name_from_text(text):
    """
    Heuristic to extract name from PAN card text.
    PAN text usually follows:
    INCOME TAX DEPARTMENT
    NAME
    FATHER'S NAME
    DOB
    PAN
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines:
        lines = [line.strip() for line in text.split(' ') if line.strip()]

    # Look for keywords and try to find the line after them
    keywords = ["INCOME", "TAX", "DEPARTMENT", "GOVT", "INDIA"]
    
    # Filter out lines that are just keywords
    potential_names = []
    for line in lines:
        is_keyword = any(kw in line for kw in keywords)
        is_pan = bool(re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', line.replace(" ", "")))
        is_dob = bool(re.search(r'\d{2}/\d{2}/\d{4}', line))
        
        if not is_keyword and not is_pan and not is_dob and len(line) > 3:
            potential_names.append(line)

    if potential_names:
        # Usually the first non-keyword line is the name
        return potential_names[0]
    return "Unknown"

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
                # Render at 4x zoom for standard professional OCR
                mat = fitz.Matrix(4, 4)
                pix = page.get_pixmap(matrix=mat, alpha=False)
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

def pdf_page_to_png_bytes(pdf_content, page_num=0, zoom=2.0):
    """
    Convert a specific page of a PDF to PNG bytes for reporting, with auto-cropping.
    """
    try:
        doc = fitz.open(stream=pdf_content, filetype="pdf")
        if page_num >= len(doc):
            doc.close()
            return None
            
        page = doc[page_num]
        
        # Auto-crop logic: Find the bounding box of all content (text and images)
        # We use page.get_text("dict") which includes both text and image blocks
        text_dict = page.get_text("dict")
        all_blocks = text_dict.get("blocks", [])
        
        # Also check for images explicitly if blocks seem empty
        if not all_blocks:
            image_info = page.get_image_info()
            if image_info:
                all_blocks = [img for img in image_info if "bbox" in img]

        if all_blocks:
            # Initialize with first block
            first_bbox = all_blocks[0].get("bbox", (0, 0, 0, 0))
            if not any(first_bbox): # Handle cases where bbox might be (0,0,0,0)
                 x0, y0, x1, y1 = page.rect
            else:
                 x0, y0, x1, y1 = first_bbox

            for b in all_blocks:
                b_bbox = b.get("bbox", (x0, y0, x1, y1))
                x0 = min(x0, b_bbox[0])
                y0 = min(y0, b_bbox[1])
                x1 = max(x1, b_bbox[2])
                y1 = max(y1, b_bbox[3])
            
            # Add some padding (15 pts) for a better visual look
            padding = 15
            x0 = max(0, x0 - padding)
            y0 = max(0, y0 - padding)
            x1 = min(page.rect.width, x1 + padding)
            y1 = min(page.rect.height, y1 + padding)
            
            bbox = fitz.Rect(x0, y0, x1, y1)
        else:
            bbox = page.rect
        
        # If the resulting bbox is essentially the whole page, we might still have white space
        # but at least we tried to crop based on PDF objects.
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=bbox)
        png_bytes = pix.tobytes("png")
        doc.close()
        
        # Secondary Crop using PIL to remove any remaining white space at the bitmap level
        # This handles cases where the PDF objects themselves have white margins
        try:
            from PIL import Image as PILImage, ImageChops
            img = PILImage.open(io.BytesIO(png_bytes))
            
            # Convert to RGB if not already
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            # Find the bbox of non-white content
            # We use a threshold to be safe against slightly off-white pixels
            bg = PILImage.new(img.mode, img.size, (255, 255, 255))
            diff = ImageChops.difference(img, bg)
            # Thresholding 
            # diff = diff.convert('L').point(lambda x: 0 if x < 5 else 255, '1')
            
            bbox_pil = diff.getbbox()
            if bbox_pil:
                # Add a small margin of 2 pixels
                w, h = img.size
                bbox_pil = (
                    max(0, bbox_pil[0] - 2),
                    max(0, bbox_pil[1] - 2),
                    min(w, bbox_pil[2] + 2),
                    min(h, bbox_pil[3] + 2)
                )
                img = img.crop(bbox_pil)
                
            output = io.BytesIO()
            img.save(output, format='PNG')
            return output.getvalue()
        except Exception as e:
            print(f"Bitmap crop failed, returning original pixmap: {e}")
            return png_bytes
    except Exception as e:
        print(f"Error converting PDF to PNG: {e}")
        traceback.print_exc()
        if 'doc' in locals() and doc:
            try: doc.close()
            except: pass
        return None

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

def extract_text_from_docx_ocr(file_content):
    """
    Extract text from a DOCX file by iterating through its internal images and running OCR.
    Useful for DOCX files that consist mainly of scanned images.
    """
    try:
        from docx import Document
        from django.utils import timezone
        from django.conf import settings
        log_file = os.path.join(settings.BASE_DIR, "ocr_debug.txt")

        def log(msg):
            try:
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"[{timezone.now()}] {msg}\n")
            except:
                pass

        log("Starting DOCX OCR (Skills Extraction)")

        reader = _get_reader()
        if not reader:
            log("EasyOCR reader failed to initialize")
            return ""

        all_text = ""
        doc = Document(io.BytesIO(file_content))
        
        # Iterate through all relations in the document to find images
        image_count = 0
        for rel in doc.part.rels.values():
            if "image" in rel.target_ref:
                try:
                    image_count += 1
                    image_data = rel.target_part.blob
                    image_np = np.array(Image.open(io.BytesIO(image_data)))
                    
                    # Run OCR on the image
                    results = reader.readtext(image_np, detail=0)
                    image_text = " ".join(results)
                    
                    log(f"Image {image_count}: {len(image_text)} chars extracted")
                    if image_text.strip():
                        all_text += image_text + "\n"
                except Exception as e:
                    log(f"Error extracting/OCR-ing image {image_count}: {e}")

        log(f"DOCX OCR complete. Processed {image_count} images. Total chars: {len(all_text)}")
        return all_text.strip()

    except Exception as e:
        print(f"DOCX OCR Error: {e}")
        return ""


def verify_face_against_pan_card(pan_image_file, snapshot_base64):
    """
    Compares the face in the webcam snapshot with the face in the uploaded PAN card image.
    """
    temp_pan_path = None
    temp_snap_path = None
    try:
        from deepface import DeepFace
        from django.conf import settings
        import uuid
        import os
        import base64
        import shutil

        # Setup directory for temp files
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        unique_id = uuid.uuid4().hex

        temp_pan_path = os.path.join(temp_dir, f"pan_{unique_id}.jpg")
        temp_snap_path = os.path.join(temp_dir, f"snap_{unique_id}.jpg")

        # Process PAN card image
        if hasattr(pan_image_file, 'temporary_file_path'):
            shutil.copy(pan_image_file.temporary_file_path(), temp_pan_path)
        elif hasattr(pan_image_file, 'read'):
            pan_image_file.seek(0)
            with open(temp_pan_path, "wb") as f:
                f.write(pan_image_file.read())
            pan_image_file.seek(0)
        else:
            # Assume it is bytes or a file path
            if isinstance(pan_image_file, (bytes, bytearray)):
                with open(temp_pan_path, "wb") as f:
                    f.write(pan_image_file)
            else:
                shutil.copy(pan_image_file, temp_pan_path)

        # Process webcam snapshot
        if ',' in snapshot_base64:
            snapshot_base64 = snapshot_base64.split(',', 1)[1]
        snapshot_bytes = base64.b64decode(snapshot_base64)
        with open(temp_snap_path, "wb") as f:
            f.write(snapshot_bytes)

        # Compare faces using ArcFace and RetinaFace
        result = DeepFace.verify(
            img1_path = temp_pan_path,
            img2_path = temp_snap_path,
            model_name = "ArcFace",
            detector_backend = "retinaface",
            enforce_detection = True,
            align = True
        )

        return {
            "verified": result.get("verified", False),
            "distance": result.get("distance", 1.0),
            "threshold": result.get("threshold", 0.6)
        }
    except Exception as e:
        print(f"Error in verify_face_against_pan_card: {e}")
        return {"verified": False, "message": str(e)}
    finally:
        # Securely cleanup temp files
        for path in [temp_pan_path, temp_snap_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as ex:
                    print(f"Failed to remove temp face file {path}: {ex}")


