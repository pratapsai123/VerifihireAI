"""
Enhanced PAN Validation for AI Assessment
Includes: Face detection, PDF support, Fuzzy matching, Identity fraud detection
"""
import re
import cv2
import numpy as np
from PIL import Image
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import logging

logger = logging.getLogger(__name__)


class EnhancedPanValidationView(APIView):
    """
    Validates PAN card photo using OCR and compares with entered PAN number.
    Includes advanced features: face detection, PDF support, fuzzy matching, identity fraud detection.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        try:
            pan_photo = request.FILES.get('pan_photo')
            entered_pan_raw = request.data.get('pan_number', '').strip().upper()
            candidate_email = request.data.get('email', '').strip().lower()
            
            # Clean the input PAN
            entered_pan = re.sub(r'[^A-Z0-9]', '', entered_pan_raw)
            if len(entered_pan) == 10:
                entered_pan = self._normalize_pan_format(entered_pan)

            if not pan_photo:
                return Response({'error': 'PAN photo is required'}, status=status.HTTP_400_BAD_REQUEST)

            if not entered_pan:
                return Response({'error': 'PAN number is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Validate PAN format (5 letters + 4 digits + 1 letter)
            pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
            if not re.match(pan_pattern, entered_pan):
                return Response({
                    'error': 'Invalid PAN format. Expected format: ABCDE1234F',
                    'is_verified': False
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check file type
            is_pdf = pan_photo.content_type == 'application/pdf' or pan_photo.name.lower().endswith('.pdf')
            is_image = pan_photo.content_type.startswith('image/')
            
            if not (is_image or is_pdf):
                return Response({'error': 'File must be an image or PDF'}, status=status.HTTP_400_BAD_REQUEST)

            # 1. Face Detection Check (Mandatory)
            face_check_file = pan_photo
            if is_pdf:
                from api.ocr_utils import pdf_page_to_png_bytes
                if hasattr(pan_photo, 'temporary_file_path'):
                    with open(pan_photo.temporary_file_path(), 'rb') as f:
                        pdf_content = f.read()
                else:
                    pan_photo.seek(0)
                    pdf_content = pan_photo.read()
                    pan_photo.seek(0)
                
                face_check_file = pdf_page_to_png_bytes(pdf_content, page_num=0)
                if not face_check_file:
                    return Response({
                        'success': True,
                        'is_verified': False,
                        'reason': 'no_face',
                        'message': 'Invalid Document: Could not process PDF for face detection.'
                    }, status=status.HTTP_200_OK)

            face_detected, face_count = self._detect_face_in_image(face_check_file)
            if not face_detected:
                return Response({
                    'success': True,
                    'is_verified': False,
                    'reason': 'no_face',
                    'message': 'Invalid Document: No human face detected in the PAN card. Please upload a clear image of your original PAN card showing your face photograph.'
                }, status=status.HTTP_200_OK)

            # 2. Perform OCR / Extraction
            if is_pdf:
                from api.ocr_utils import extract_text_from_pdf
                extracted_text, success = extract_text_from_pdf(pan_photo, target_pan=entered_pan)
            else:
                extracted_text, success = self._extract_text_from_image(pan_photo, target_pan=entered_pan)
            
            clean_extracted = re.sub(r'[^A-Z0-9]', '', (extracted_text or "").upper())
            
            # 3. Identity Fraud Detection (if email provided)
            if candidate_email:
                fraud_check = self._check_identity_fraud(candidate_email, entered_pan, pan_photo)
                if fraud_check:
                    return fraud_check

            # 4. Find ALL potential PANs on the document
            loose_pattern = re.compile(r'[A-Z0-9]{5}[0-9A-Z]{4}[A-Z0-9]{1}')
            raw_matches = re.findall(loose_pattern, clean_extracted)
            all_potential_pans = [self._normalize_pan_format(m) for m in raw_matches]

            # Step 1: Direct containment check
            if entered_pan in clean_extracted:
                self._save_identity_link(candidate_email, entered_pan, pan_photo)
                return Response({
                    'success': True,
                    'is_verified': True,
                    'message': 'PAN verification successful',
                    'extracted_pan': entered_pan,
                    'face_detected': True
                }, status=status.HTTP_200_OK)

            # Step 2: Advanced Fuzzy Window Search
            found_fuzzy = self._fuzzy_pan_search(clean_extracted, entered_pan)
            
            if found_fuzzy:
                self._save_identity_link(candidate_email, entered_pan, pan_photo)
                return Response({
                    'success': True,
                    'is_verified': True,
                    'message': 'PAN verification successful (Fuzzy)',
                    'extracted_pan': entered_pan,
                    'face_detected': True
                }, status=status.HTTP_200_OK)

            # Step 3: Determine failure reason
            pan_keywords = ["INCOME", "TAX", "PERMANENT", "ACCOUNT", "NUMBER", "GOVT", "INDIA", "DEPT", "DOB", "HOLDER"]
            is_likely_pan = any(kw in clean_extracted for kw in pan_keywords)

            if len(all_potential_pans) > 0:
                reason = 'mismatch'
                if is_likely_pan:
                    msg = "Mismatch: The PAN number on the document does not match your entry."
                else:
                    msg = "Incorrect Document: This document seems to have a PAN-like number but is not a valid PAN card."
            else:
                reason = 'unclear'
                if is_likely_pan:
                    msg = "Could not find your PAN number on the card. Please upload a clear image."
                else:
                    msg = "Invalid Document: We could not find any PAN markers. Please upload a clear image of your PAN card."

            return Response({
                'success': True,
                'is_verified': False,
                'reason': reason,
                'message': msg,
                'extracted_pan': all_potential_pans[0] if all_potential_pans else None,
                'face_detected': True
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"PAN validation error: {str(e)}", exc_info=True)
            return Response({
                'error': f'Failed to validate PAN: {str(e)}',
                'is_verified': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _normalize_pan_format(self, pan):
        """Normalize PAN format handling common OCR errors."""
        result = ""
        for i, char in enumerate(pan):
            if 5 <= i <= 8:  # Numeric section
                if char in "OQ": result += "0"
                elif char in "I|L": result += "1"
                elif char == "S": result += "5"
                elif char == "Z": result += "2"
                elif char == "B": result += "8"
                elif char == "G": result += "6"
                else: result += char
            else: result += char
        return result

    def _detect_face_in_image(self, image_file):
        """Detect face in image using OpenCV."""
        try:
            if isinstance(image_file, bytes):
                nparr = np.frombuffer(image_file, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            else:
                image_file.seek(0)
                nparr = np.frombuffer(image_file.read(), np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return False, 0
            
            # Use OpenCV face detection
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            return len(faces) > 0, len(faces)
        except Exception as e:
            logger.warning(f"Face detection failed: {str(e)}")
            return True, 1  # Allow if detection fails

    def _extract_text_from_image(self, image_file, target_pan=None):
        """Extract text from image using EasyOCR or Groq Vision."""
        try:
            import io
            import os
            image = Image.open(image_file)
            extracted_text = ""
            
            # Try EasyOCR
            try:
                import easyocr
                reader = easyocr.Reader(['en'])
                img_array = np.array(image)
                result = reader.readtext(img_array, detail=0)
                extracted_text = ' '.join(result)
                logger.info(f"EasyOCR extracted: {extracted_text}")
            except Exception as ocr_error:
                logger.warning(f"EasyOCR failed: {str(ocr_error)}")
            
            # Try Groq Vision as fallback
            if not extracted_text:
                try:
                    from ai_assessments.llm_client import create_llm_client, get_default_model
                    import base64
                    llm_client = create_llm_client()
                    
                    buffered = io.BytesIO()
                    image.save(buffered, format="JPEG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode()
                    
                    response = llm_client.chat.completions.create(
                        model=get_default_model(),
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Extract the PAN number from this PAN card image. The PAN number is 10 characters: 5 letters, 4 digits, 1 letter. Return ONLY the PAN number."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                            ]
                        }],
                        max_tokens=20
                    )
                    extracted_text = response.choices[0].message.content.upper().strip()
                    logger.info(f"DeepSeek extracted: {extracted_text}")
                except Exception as ds_error:
                    logger.warning(f"DeepSeek failed: {str(ds_error)}")
            
            return extracted_text, bool(extracted_text)
        except Exception as e:
            logger.error(f"Image extraction failed: {str(e)}")
            return "", False

    def _fuzzy_pan_search(self, clean_text, target_pan):
        """Advanced fuzzy search for PAN in extracted text."""
        potential_matches = [clean_text[i:i+10] for i in range(len(clean_text) - 9)]
        
        for p in potential_matches:
            norm = ""
            for i, char in enumerate(p):
                if 5 <= i <= 8:
                    if char in "OQ": norm += "0"
                    elif char in "I|L": norm += "1"
                    elif char == "S": norm += "5"
                    elif char == "Z": norm += "2"
                    elif char == "B": norm += "8"
                    elif char == "G": norm += "6"
                    else: norm += char
                else: norm += char
            
            if norm == target_pan:
                return True
        return False

    def _check_identity_fraud(self, email, pan, photo):
        """Check for identity fraud - email/PAN consistency."""
        try:
            from api.models import IdentityLink
            
            norm_email = email.lower().strip()
            norm_pan = pan.strip().upper()
            
            # Check if email already registered with different PAN
            existing_by_email = IdentityLink.objects.filter(email=norm_email).first()
            if existing_by_email and existing_by_email.pan_number != norm_pan:
                self._save_violation_screenshot(photo, f"Fraud: {email} with different PAN")
                return Response({
                    'error': 'Identity Fraud Detected: This email is already registered with a different PAN card.',
                    'is_verified': False,
                    'reason': 'identity_fraud'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Check if PAN already registered with different email
            existing_by_pan = IdentityLink.objects.filter(pan_number=norm_pan).first()
            if existing_by_pan and existing_by_pan.email != norm_email:
                self._save_violation_screenshot(photo, f"Fraud: PAN {pan} with different email")
                return Response({
                    'error': 'Identity Fraud Detected: This PAN card is already linked to another identity.',
                    'is_verified': False,
                    'reason': 'identity_fraud'
                }, status=status.HTTP_403_FORBIDDEN)
            
            return None  # No fraud detected
        except Exception as e:
            logger.warning(f"Identity fraud check failed: {str(e)}")
            return None  # Allow if check fails

    def _save_identity_link(self, email, pan, photo):
        """Save email-PAN binding for future fraud detection."""
        try:
            from api.models import IdentityLink
            if email:
                IdentityLink.objects.update_or_create(
                    email=email.lower().strip(),
                    defaults={'pan_number': pan.strip().upper()}
                )
        except Exception as e:
            logger.warning(f"Failed to save identity link: {str(e)}")

    def _save_violation_screenshot(self, photo, reason):
        """Save screenshot of violation attempt."""
        try:
            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile
            from datetime import datetime
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"violations/pan_fraud_{timestamp}_{reason[:50]}.jpg"
            
            if hasattr(photo, 'temporary_file_path'):
                with open(photo.temporary_file_path(), 'rb') as f:
                    default_storage.save(filename, ContentFile(f.read()))
            else:
                photo.seek(0)
                default_storage.save(filename, ContentFile(photo.read()))
                photo.seek(0)
        except Exception as e:
            logger.error(f"Failed to save violation screenshot: {str(e)}")
