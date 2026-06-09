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

def calculate_sha256(image_input):
    """
    Calculates SHA256 hash of an image.
    Accepts file path, bytes, base64 string, or Django File field.
    """
    import hashlib
    import base64
    import os
    
    if not image_input:
        return None
        
    try:
        # If it's a Django file field with a path
        if hasattr(image_input, 'path') and os.path.exists(image_input.path):
            with open(image_input.path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
                
        # If it's a file field/bytes-like that we can read
        if hasattr(image_input, 'read'):
            try:
                image_input.seek(0)
                data = image_input.read()
                image_input.seek(0)
                return hashlib.sha256(data).hexdigest()
            except Exception:
                pass
                
        # If it's a file path
        if isinstance(image_input, str) and os.path.exists(image_input):
            with open(image_input, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
                
        # If it's a base64 string
        if isinstance(image_input, str) and (image_input.startswith("data:image") or len(image_input) > 200):
            clean_b64 = image_input
            if ',' in clean_b64:
                clean_b64 = clean_b64.split(',', 1)[1]
            # remove formatting
            clean_b64 = clean_b64.replace('\n', '').replace('\r', '').replace(' ', '')
            padding = 4 - len(clean_b64) % 4
            if padding != 4:
                clean_b64 += '=' * padding
            try:
                data = base64.b64decode(clean_b64)
                return hashlib.sha256(data).hexdigest()
            except Exception:
                pass
                
        # Fallback to string encoding if it's some other string path that doesn't exist
        if isinstance(image_input, str):
            from django.conf import settings
            full_path = os.path.join(settings.MEDIA_ROOT, image_input.lstrip('/'))
            if os.path.exists(full_path):
                with open(full_path, 'rb') as f:
                    return hashlib.sha256(f.read()).hexdigest()
                    
    except Exception as e:
        print(f"Error calculating SHA256: {e}")
        
    return None


def write_audit_log(candidate_id, email, pan, img1_path, img2_path, img1_hash, img2_hash, face_details, verify_res, final_decision):
    """
    Appends verification details to backend/face_verification_audit.log
    """
    import os
    import json
    from datetime import datetime
    from django.conf import settings
    
    log_path = os.path.join(settings.BASE_DIR, 'face_verification_audit.log')
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "candidate_id": candidate_id,
        "email": email,
        "pan": pan,
        "original_path": img1_path,
        "captured_path": img2_path,
        "original_hash": img1_hash,
        "captured_hash": img2_hash,
        "face_detection_details": face_details,
        "verification_result": {
            "verified": verify_res.get("verified"),
            "distance": verify_res.get("distance"),
            "threshold": verify_res.get("threshold"),
            "model": verify_res.get("model"),
            "detector": verify_res.get("detector"),
            "no_face_detected": verify_res.get("no_face_detected"),
            "image_source_mismatch": verify_res.get("image_source_mismatch"),
            "report_original_hash": verify_res.get("report_original_hash"),
            "report_captured_hash": verify_res.get("report_captured_hash"),
        },
        "final_decision": final_decision
    }
    
    try:
        with open(log_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        print(f"Error writing face verification audit log: {e}")


def run_standard_deepface_verification(
    img1_path,
    img2_path,
    candidate_id=None,
    email=None,
    pan=None
):
    """
    Standardized DeepFace verification pipeline using ArcFace and RetinaFace.
    """
    import os
    import time
    import shutil
    import hashlib
    from datetime import datetime
    from django.conf import settings
    from deepface import DeepFace
    from PIL import Image

    start_time = time.time()
    
    # 1. Pre-verification Image Validation
    img1_exists = os.path.exists(img1_path) if img1_path else False
    img2_exists = os.path.exists(img2_path) if img2_path else False
    
    print(f"[DeepFace Verification] Candidate ID: {candidate_id}, Email: {email}, PAN: {pan}")
    print(f"[DeepFace Verification] Original Path: {img1_path} (Exists: {img1_exists})")
    print(f"[DeepFace Verification] Captured Path: {img2_path} (Exists: {img2_exists})")

    # Generate SHA256 hashes
    original_image_hash = calculate_sha256(img1_path)
    captured_image_hash = calculate_sha256(img2_path)

    # Resolve report images and calculate report hashes
    report_original_hash = None
    report_captured_hash = None
    image_source_mismatch = False

    try:
        from api.models import CandidateDetails, IdentityLink
        import re
        
        detail = None
        if candidate_id:
            detail = CandidateDetails.objects.filter(id=candidate_id).first()
        if not detail and email:
            detail = CandidateDetails.objects.filter(email=email).first()
        if not detail and pan:
            detail = CandidateDetails.objects.filter(pan_number=pan).first()
            
        if detail:
            # Check photo update approved status
            photo_approved = getattr(detail, 'photo_update_approved', False)
            snap_sources = []
            if photo_approved:
                norm_pan = re.sub(r'[^A-Z0-9]', '', detail.pan_number.strip().upper())
                link = IdentityLink.objects.filter(pan_number=norm_pan).first()
                if not link and detail.email:
                    link = IdentityLink.objects.filter(email__iexact=detail.email.strip()).first()
                if link and link.snapshot_image:
                    snap_sources.append(link.snapshot_image)
            if detail.snapshot:
                snap_sources.append(detail.snapshot)
                
            if snap_sources:
                report_original_hash = calculate_sha256(snap_sources[0])
            report_captured_hash = captured_image_hash # Normally reports render the webcam snapshot
    except Exception as e:
        print(f"Error resolving report hashes: {e}")

    if report_original_hash is None:
        report_original_hash = original_image_hash
    if report_captured_hash is None:
        report_captured_hash = captured_image_hash

    image_source_mismatch = (original_image_hash != report_original_hash) or (captured_image_hash != report_captured_hash)

    # Get image widths, heights, sizes, and timestamps
    def get_img_meta(path):
        if not path or not os.path.exists(path):
            return 0, 0, 0, None
        try:
            with Image.open(path) as img:
                w, h = img.size
            size = os.path.getsize(path)
            mtime = datetime.fromtimestamp(os.path.getmtime(path)).isoformat()
            return w, h, size, mtime
        except Exception:
            return 0, 0, 0, None

    img1_w, img1_h, img1_size, img1_mtime = get_img_meta(img1_path)
    img2_w, img2_h, img2_size, img2_mtime = get_img_meta(img2_path)

    # Save copies of images being compared to media/debug_face_verification/
    debug_dir = os.path.join(settings.MEDIA_ROOT, 'debug_face_verification')
    os.makedirs(debug_dir, exist_ok=True)
    c_id = candidate_id if candidate_id else "unknown"
    
    debug_orig_path = os.path.join(debug_dir, f"candidate_{c_id}_original.jpg")
    debug_cap_path = os.path.join(debug_dir, f"candidate_{c_id}_captured.jpg")
    
    if img1_exists:
        try:
            shutil.copy(img1_path, debug_orig_path)
        except Exception as e:
            print(f"Error copying original debug image: {e}")
            
    if img2_exists:
        try:
            shutil.copy(img2_path, debug_cap_path)
        except Exception as e:
            print(f"Error copying captured debug image: {e}")

    # Check file exists status
    if not img1_exists or not img2_exists:
        print("[DeepFace Verification] File missing. Setting to Manual Review.")
        result = {
            "verified": False,
            "distance": None,
            "threshold": 0.68, # Default ArcFace cosine threshold is 0.68
            "model": "ArcFace",
            "detector": "retinaface",
            "no_face_detected": True,
            "identity_mismatch_detected": False,
            "status": "Manual Review",
            "reason": "Missing comparison image files.",
            "original_image_path": img1_path,
            "captured_image_path": img2_path,
            "original_image_hash": original_image_hash,
            "captured_image_hash": captured_image_hash,
            "report_original_hash": report_original_hash,
            "report_captured_hash": report_captured_hash,
            "image_source_mismatch": image_source_mismatch
        }
        write_audit_log(candidate_id, email, pan, img1_path, img2_path, original_image_hash, captured_image_hash, "File Missing", result, "Manual Review")
        return result

    # Phase 2: Face Detection
    faces_detected = True
    face_detection_details = []
    
    # Check img1 face detection
    try:
        objs1 = DeepFace.extract_faces(
            img_path=img1_path,
            detector_backend="retinaface",
            enforce_detection=True
        )
        face_detection_details.append({
            "image": "original",
            "count": len(objs1),
            "bbox": objs1[0]["facial_area"],
            "confidence": objs1[0]["confidence"],
            "status": "success"
        })
    except Exception as e:
        faces_detected = False
        face_detection_details.append({
            "image": "original",
            "count": 0,
            "bbox": {},
            "confidence": 0.0,
            "status": f"failed: {str(e)}"
        })

    # Check img2 face detection
    try:
        objs2 = DeepFace.extract_faces(
            img_path=img2_path,
            detector_backend="retinaface",
            enforce_detection=True
        )
        face_detection_details.append({
            "image": "captured",
            "count": len(objs2),
            "bbox": objs2[0]["facial_area"],
            "confidence": objs2[0]["confidence"],
            "status": "success"
        })
    except Exception as e:
        faces_detected = False
        face_detection_details.append({
            "image": "captured",
            "count": 0,
            "bbox": {},
            "confidence": 0.0,
            "status": f"failed: {str(e)}"
        })

    if not faces_detected:
        print("[DeepFace Verification] Face extraction failed. Setting to Manual Review.")
        result = {
            "verified": False,
            "distance": None,
            "threshold": 0.68,
            "model": "ArcFace",
            "detector": "retinaface",
            "no_face_detected": True,
            "identity_mismatch_detected": False,
            "status": "Manual Review",
            "reason": "Face detection failed during verification.",
            "original_image_path": img1_path,
            "captured_image_path": img2_path,
            "original_image_hash": original_image_hash,
            "captured_image_hash": captured_image_hash,
            "report_original_hash": report_original_hash,
            "report_captured_hash": report_captured_hash,
            "image_source_mismatch": image_source_mismatch
        }
        write_audit_log(candidate_id, email, pan, img1_path, img2_path, original_image_hash, captured_image_hash, face_detection_details, result, "Manual Review")
        return result

    # Phase 3 & 4: DeepFace Verification (ArcFace, RetinaFace)
    try:
        verify_res = DeepFace.verify(
            img1_path=img1_path,
            img2_path=img2_path,
            model_name="ArcFace",
            detector_backend="retinaface",
            align=True,
            enforce_detection=True
        )
        
        verified = verify_res.get("verified", False)
        distance = verify_res.get("distance", 1.0)
        threshold = verify_res.get("threshold", 0.68)
        
        execution_time = time.time() - start_time
        print(f"[DeepFace Verification] Done in {execution_time:.2f}s. Verified: {verified}, Distance: {distance:.4f}, Threshold: {threshold}")
        
        # Phase 5: Decision Logic
        identity_mismatch_detected = False
        
        # Relax the strict threshold slightly to reduce false positives for the same person
        # ArcFace default is 0.68. We relax it to 0.80 to account for lighting/webcam quality changes.
        relaxed_threshold = threshold if threshold > 0.75 else 0.80
        
        if distance > relaxed_threshold:
            identity_mismatch_detected = True

        result = {
            "verified": verified,
            "distance": distance,
            "threshold": threshold,
            "model": "ArcFace",
            "detector": "retinaface",
            "no_face_detected": False,
            "identity_mismatch_detected": identity_mismatch_detected,
            "status": "Identity Face Mismatch" if identity_mismatch_detected else "Verified",
            "original_image_path": img1_path,
            "captured_image_path": img2_path,
            "original_image_hash": original_image_hash,
            "captured_image_hash": captured_image_hash,
            "report_original_hash": report_original_hash,
            "report_captured_hash": report_captured_hash,
            "image_source_mismatch": image_source_mismatch,
            "execution_time": execution_time
        }
        write_audit_log(candidate_id, email, pan, img1_path, img2_path, original_image_hash, captured_image_hash, face_detection_details, result, "Identity Mismatch" if identity_mismatch_detected else "Success")
        return result

    except Exception as e:
        print(f"[DeepFace Verification] Verification exception: {e}")
        result = {
            "verified": False,
            "distance": None,
            "threshold": 0.68,
            "model": "ArcFace",
            "detector": "retinaface",
            "no_face_detected": False,
            "identity_mismatch_detected": False,
            "status": "Manual Review",
            "reason": f"Verification system exception: {str(e)}",
            "original_image_path": img1_path,
            "captured_image_path": img2_path,
            "original_image_hash": original_image_hash,
            "captured_image_hash": captured_image_hash,
            "report_original_hash": report_original_hash,
            "report_captured_hash": report_captured_hash,
            "image_source_mismatch": image_source_mismatch
        }
        write_audit_log(candidate_id, email, pan, img1_path, img2_path, original_image_hash, captured_image_hash, "Exception", result, "Manual Review")
        return result


def detect_face_in_image(image_file):
    """
    Detects human face in the given image file using RetinaFace.
    Returns (bool, int) -> (is_face_detected, face_count)
    """
    import os
    import uuid
    import base64
    from django.conf import settings
    from PIL import Image
    import io
    from deepface import DeepFace

    temp_path = None
    try:
        # Setup temp path
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, f"detect_{uuid.uuid4().hex}.jpg")

        # Save image_file to temp_path
        if isinstance(image_file, (bytes, bytearray)):
            with open(temp_path, 'wb') as f:
                f.write(image_file)
        elif isinstance(image_file, str) and os.path.exists(image_file):
            temp_path = image_file
        elif hasattr(image_file, 'temporary_file_path'):
            import shutil
            shutil.copy(image_file.temporary_file_path(), temp_path)
        elif hasattr(image_file, 'read'):
            image_file.seek(0)
            data = image_file.read()
            image_file.seek(0)
            with open(temp_path, 'wb') as f:
                f.write(data)
        else:
            # Assume it's a PIL Image or similar
            image_file.save(temp_path)

        # Run DeepFace face extraction
        objs = DeepFace.extract_faces(
            img_path=temp_path,
            detector_backend="retinaface",
            enforce_detection=True
        )
        return len(objs) > 0, len(objs)
    except Exception as e:
        # DeepFace raises ValueError when no face is detected
        print(f"RetinaFace Face Detection: No face detected or error: {e}")
        return False, 0
    finally:
        # Cleanup temp file if created
        if temp_path and temp_path != image_file and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

def register_face_with_deepface(person_id, image_data):
    """
    Register a face via the DeepFace microservice (unified flow).

    Accepts the same argument shapes as the legacy local implementation so that
    all existing callers (candidate_assessment_views, workflow_views) continue to
    work without modification.

    Raises DeepFaceServiceError if the microservice is unreachable (hard-fail policy).
    """
    from api.deepface_client import df_register, DeepFaceServiceError  # noqa: F401

    # Normalise image_data to a base64 string
    if hasattr(image_data, 'read'):
        # Django UploadedFile / InMemoryUploadedFile
        image_data.seek(0)
        raw = image_data.read()
        image_data.seek(0)
        image_b64 = base64.b64encode(raw).decode('ascii')
    elif isinstance(image_data, (bytes, bytearray)):
        image_b64 = base64.b64encode(image_data).decode('ascii')
    elif isinstance(image_data, str):
        # Already a base64 string or data-URL — pass through; df_register strips the prefix
        image_b64 = image_data
    else:
        return {"success": False, "message": f"Unsupported image_data type: {type(image_data)}"}

    try:
        result = df_register(person_id, image_b64, overwrite=True)
        return result
    except DeepFaceServiceError as exc:
        print(f"[DeepFace] register_face_with_deepface({person_id}) failed: {exc}")
        raise

def verify_face_with_deepface(person_id, snapshot_base64, candidate_id=None, email=None):
    """
    Verify a snapshot against the registered identity for person_id via the
    DeepFace microservice (unified flow).

    Recovery logic: if the microservice reports that the person is not yet
    registered (e.g., first-time or after a data wipe), this function attempts
    to restore the face from CandidateDetails or IdentityLink and re-registers
    it with the microservice before verifying.

    Returns a dict compatible with the legacy run_standard_deepface_verification
    shape so all callers continue to work unchanged.

    Raises DeepFaceServiceError if the microservice is unreachable.
    """
    from api.deepface_client import df_verify, df_is_registered, df_register, DeepFaceServiceError
    from api.models import CandidateDetails, IdentityLink

    try:
        # ── Recovery: if not yet registered in the microservice, restore from DB ──
        try:
            already_registered = df_is_registered(person_id)
        except DeepFaceServiceError:
            raise  # Hard-fail immediately if microservice is down

        if not already_registered:
            print(f"[DeepFace Recovery] {person_id} not in microservice — attempting restore from DB.")
            restored = False

            # Priority 1: Latest admin-approved CandidateDetails snapshot
            detail = CandidateDetails.objects.filter(
                pan_number=person_id,
                photo_update_status='approved'
            ).order_by('-id').first()

            if not detail and email:
                detail = CandidateDetails.objects.filter(
                    email=email,
                    photo_update_status='approved'
                ).order_by('-id').first()

            # Priority 2: Earliest verified (no mismatch) baseline
            if not detail:
                detail = CandidateDetails.objects.filter(
                    pan_number=person_id,
                    identity_mismatch_detected=False
                ).exclude(snapshot='').order_by('id').first()

            if not detail and email:
                detail = CandidateDetails.objects.filter(
                    email=email,
                    identity_mismatch_detected=False
                ).exclude(snapshot='').order_by('id').first()

            # Priority 3: Any snapshot for this PAN
            if not detail:
                detail = CandidateDetails.objects.filter(
                    pan_number=person_id
                ).exclude(snapshot='').order_by('id').first()

            if not detail and email:
                detail = CandidateDetails.objects.filter(
                    email=email
                ).exclude(snapshot='').order_by('id').first()

            if detail and detail.snapshot:
                snap_b64 = detail.snapshot
                try:
                    df_register(person_id, snap_b64, overwrite=False)
                    print(f"[DeepFace Recovery] Re-registered {person_id} from CandidateDetails (ID: {detail.id}).")
                    restored = True
                except DeepFaceServiceError:
                    raise
                except Exception as reg_err:
                    print(f"[DeepFace Recovery] Re-register from CandidateDetails failed: {reg_err}")

            # Priority 4: IdentityLink snapshot_image
            if not restored:
                identity_link = IdentityLink.objects.filter(pan_number=person_id).first()
                if not identity_link and email:
                    identity_link = IdentityLink.objects.filter(email=email).first()
                if identity_link and identity_link.snapshot_image:
                    try:
                        identity_link.snapshot_image.seek(0)
                        raw = identity_link.snapshot_image.read()
                        link_b64 = base64.b64encode(raw).decode('ascii')
                        df_register(person_id, link_b64, overwrite=False)
                        print(f"[DeepFace Recovery] Re-registered {person_id} from IdentityLink snapshot.")
                        restored = True
                    except DeepFaceServiceError:
                        raise
                    except Exception as reg_err:
                        print(f"[DeepFace Recovery] Re-register from IdentityLink failed: {reg_err}")

            if not restored:
                # No source found — return a 'not registered' result so caller
                # can fall through to first-time registration.
                return {
                    "verified": False,
                    "distance": None,
                    "threshold": 0.75,
                    "model": "ArcFace",
                    "detector": "opencv",
                    "no_face_detected": False,
                    "identity_mismatch_detected": False,
                    "message": "No registered identity found for this person_id.",
                }

        # ── Actual verification via microservice ──
        result = df_verify(person_id, snapshot_base64)

        # Normalise to the shape that all callers expect (same keys as
        # run_standard_deepface_verification output).
        verified   = result.get('verified', False)
        distance   = result.get('distance')
        threshold  = result.get('threshold')
        model      = result.get('model', 'ArcFace')
        detector   = result.get('detector', 'opencv')

        # Relax the strict threshold slightly to reduce false positives for the same person
        # ArcFace default is 0.68. We relax it to 0.80.
        relaxed_threshold = threshold if threshold and threshold > 0.75 else 0.80

        identity_mismatch_detected = (
            not verified
            and distance is not None
            and threshold is not None
            and distance > relaxed_threshold
        )

        return {
            'verified': verified,
            'distance': distance,
            'threshold': threshold,
            'model': model,
            'detector': detector,
            'no_face_detected': result.get('no_face_detected', False),
            'identity_mismatch_detected': identity_mismatch_detected,
            'status': 'Verified' if verified else 'Identity Face Mismatch',
            # Paths/hashes are not applicable for microservice verification;
            # keep keys present with None so callers don't KeyError.
            'original_image_path': None,
            'captured_image_path': None,
            'original_image_hash': None,
            'captured_image_hash': None,
            'report_original_hash': None,
            'report_captured_hash': None,
            'image_source_mismatch': False,
        }

    except DeepFaceServiceError:
        raise  # Propagate hard-fail to caller
    except Exception as exc:
        print(f"[DeepFace] verify_face_with_deepface({person_id}) unexpected error: {exc}")
        return {"verified": False, "message": str(exc)}

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


def verify_face_against_pan_card(pan_image_file, snapshot_base64, candidate_id=None, email=None, pan=None):
    """
    Compares the face in the webcam snapshot with the face in the uploaded PAN card image.
    """
    temp_pan_path = None
    temp_snap_path = None
    try:
        from django.conf import settings
        import uuid
        import os
        import base64
        
        # Setup directory for temp files
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        unique_id = uuid.uuid4().hex
        
        temp_pan_path = os.path.join(temp_dir, f"pan_{unique_id}.jpg")
        temp_snap_path = os.path.join(temp_dir, f"snap_{unique_id}.jpg")
        
        # Process PAN card image
        if hasattr(pan_image_file, 'temporary_file_path'):
            import shutil
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
                import shutil
                shutil.copy(pan_image_file, temp_pan_path)
                
        # Process webcam snapshot
        if ',' in snapshot_base64:
            snapshot_base64 = snapshot_base64.split(',', 1)[1]
        snapshot_bytes = base64.b64decode(snapshot_base64)
        with open(temp_snap_path, "wb") as f:
            f.write(snapshot_bytes)
            
        result = run_standard_deepface_verification(
            img1_path=temp_pan_path,
            img2_path=temp_snap_path,
            candidate_id=candidate_id,
            email=email,
            pan=pan
        )
        return result
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


def verify_two_faces_with_deepface(img1_data, img2_data, candidate_id=None, email=None, pan=None):
    """
    Compares two faces using local DeepFace.
    """
    temp_files = []
    
    def get_local_path(img_input, prefix):
        from django.conf import settings
        import base64
        import uuid
        
        # 1. If it's a local file path and exists
        if isinstance(img_input, str) and os.path.exists(img_input):
            return img_input
            
        # 2. Setup temp directory
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        unique_id = uuid.uuid4().hex
        temp_path = os.path.join(temp_dir, f"{prefix}_{unique_id}.jpg")
        
        # 3. If it's a base64 string
        if isinstance(img_input, str) and (img_input.startswith("data:image") or len(img_input) > 200):
            clean_b64 = img_input
            if ',' in clean_b64:
                clean_b64 = clean_b64.split(',', 1)[1]
            try:
                img_bytes = base64.b64decode(clean_b64)
                with open(temp_path, "wb") as f:
                    f.write(img_bytes)
                temp_files.append(temp_path)
                return temp_path
            except Exception as e:
                print(f"Error decoding base64 for {prefix}: {e}")
                return None
                
        # 4. If it's a Django file/image field or has a read method
        if img_input and hasattr(img_input, 'read'):
            try:
                if hasattr(img_input, 'path') and os.path.exists(img_input.path):
                    return img_input.path
                    
                img_input.seek(0)
                img_bytes = img_input.read()
                img_input.seek(0)
                with open(temp_path, "wb") as f:
                    f.write(img_bytes)
                temp_files.append(temp_path)
                return temp_path
            except Exception as e:
                print(f"Error reading Django file for {prefix}: {e}")
                return None
                
        return None

    try:
        temp_path1 = get_local_path(img1_data, "face1")
        temp_path2 = get_local_path(img2_data, "face2")
        
        if not temp_path1 or not temp_path2:
            return {"verified": False, "message": "Failed to resolve one or both face images."}
            
        result = run_standard_deepface_verification(
            img1_path=temp_path1,
            img2_path=temp_path2,
            candidate_id=candidate_id,
            email=email,
            pan=pan
        )
        return result
    except Exception as e:
        print(f"Error in verify_two_faces_with_deepface: {e}")
        return {"verified": False, "message": str(e)}
    finally:
        for path in temp_files:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as ex:
                    print(f"Failed to remove temp file {path}: {ex}")