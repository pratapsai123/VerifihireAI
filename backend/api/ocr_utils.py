import easyocr
from PIL import Image
import io
import re
import numpy as np

# Initialize reader globally to avoid reloading model on every request
# 'en' for English. gpu=False by default to be safe, or True if available.
# We'll set gpu=False for compatibility unless we know otherwise.
reader = easyocr.Reader(['en'], gpu=False)

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
                print(f"Error extracting text at rotation {rotation}: {e}")
                continue

        return extracted_text_log, False

    except Exception as overall_e:
        return f"OCR Failed: {str(overall_e)}", False