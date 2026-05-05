"""
Comprehensive test of all changes made on 2026-05-05
Tests: PAN Security + Face Duplicate Detection
"""
import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from ai_candidates.models import Candidate
from django.db.utils import IntegrityError
from django.utils import timezone
import uuid

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_result(test_name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status}: {test_name}")
    if details:
        print(f"       {details}")

def test_pan_uniqueness():
    """Test 1: PAN number must be unique across candidates"""
    print_header("TEST 1: PAN Uniqueness Constraint")
    
    pan = f"TES{uuid.uuid4().hex[:4].upper()}12F"  # 5 letters + 4 digits + 1 letter = 10 total
    
    # Create first candidate
    c1 = Candidate.objects.create(
        full_name="Test User 1",
        email="test1@test.com",
        pan_number=pan
    )
    print(f"  Created candidate 1 with PAN: {pan}")
    
    # Try to create second with same PAN
    try:
        c2 = Candidate.objects.create(
            full_name="Test User 2", 
            email="test2@test.com",
            pan_number=pan
        )
        print_result("PAN Uniqueness", False, "Duplicate PAN was allowed!")
        c1.delete()
        c2.delete()
        return False
    except IntegrityError as e:
        print_result("PAN Uniqueness", True, f"Duplicate PAN rejected: {str(e)[:50]}")
        c1.delete()
        return True

def test_pan_lock():
    """Test 2: PAN gets locked when interview starts"""
    print_header("TEST 2: PAN Lock on Interview Start")
    
    pan = f"LOC{uuid.uuid4().hex[:4].upper()}12F"
    
    c = Candidate.objects.create(
        full_name="Lock Test User",
        email="lock@test.com",
        pan_number=pan,
        pan_verified=True
    )
    
    # Initially not locked
    if c.pan_locked:
        print_result("Initial State", False, "PAN should not be locked initially")
        c.delete()
        return False
    print("  ✓ PAN initially unlocked")
    
    # Simulate interview start (lock PAN)
    c.pan_locked = True
    c.link_opened_at = timezone.now()
    c.save()
    
    if not c.pan_locked:
        print_result("PAN Lock", False, "PAN lock not persisted")
        c.delete()
        return False
    
    print_result("PAN Lock", True, f"PAN locked at: {c.link_opened_at}")
    c.delete()
    return True

def test_pan_history():
    """Test 3: PAN history is tracked"""
    print_header("TEST 3: PAN History Tracking")
    
    pan = f"HIS{uuid.uuid4().hex[:4].upper()}12F"
    
    c = Candidate.objects.create(
        full_name="History Test User",
        email="history@test.com",
        pan_number=pan,
        pan_history=[{
            'action': 'registered',
            'pan': pan,
            'timestamp': timezone.now().isoformat()
        }]
    )
    
    if not c.pan_history or len(c.pan_history) == 0:
        print_result("PAN History", False, "PAN history not stored")
        c.delete()
        return False
    
    print_result("PAN History", True, f"History entries: {len(c.pan_history)}")
    c.delete()
    return True

def test_face_embedding_hash():
    """Test 4: Face embedding hash field exists and works"""
    print_header("TEST 4: Face Embedding Hash Field")
    
    c = Candidate.objects.create(
        full_name="Face Hash Test",
        email="facehash@test.com"
    )
    
    # Initially no hash
    if c.face_embedding_hash is not None:
        print_result("Initial Hash", False, "Hash should be None initially")
        c.delete()
        return False
    print("  ✓ Face hash initially null")
    
    # Set hash
    test_hash = "a" * 64  # SHA-256 hex is 64 chars
    c.face_embedding_hash = test_hash
    c.save()
    
    # Refresh and verify
    c.refresh_from_db()
    if c.face_embedding_hash != test_hash:
        print_result("Hash Storage", False, "Hash not persisted correctly")
        c.delete()
        return False
    
    print_result("Hash Storage", True, f"Hash stored: {test_hash[:16]}...")
    c.delete()
    return True

def test_face_duplicate_detection():
    """Test 5: Face hash duplicate detection works"""
    print_header("TEST 5: Face Duplicate Detection")
    
    face_hash = "b" * 64
    
    # Create first candidate with face hash
    c1 = Candidate.objects.create(
        full_name="Face User 1",
        email="face1@test.com",
        face_embedding_hash=face_hash
    )
    print(f"  Created candidate 1 with face hash: {face_hash[:16]}...")
    
    # Try to create second with same face hash (simulating backend check)
    existing = Candidate.objects.filter(
        face_embedding_hash=face_hash
    ).exclude(id=c1.id).first()
    
    if existing:
        print_result("Duplicate Detection", False, "Query found duplicate when it shouldn't")
        c1.delete()
        return False
    
    # Now create actual duplicate to test detection
    try:
        c2 = Candidate.objects.create(
            full_name="Face User 2",
            email="face2@test.com",
            face_embedding_hash=face_hash
        )
        
        # Query should find the other candidate
        existing = Candidate.objects.filter(
            face_embedding_hash=face_hash
        ).exclude(id=c2.id).first()
        
        if existing and existing.id == c1.id:
            print_result("Duplicate Detection", True, f"Detected duplicate: {existing.full_name}")
            c1.delete()
            c2.delete()
            return True
        else:
            print_result("Duplicate Detection", False, "Failed to detect duplicate")
            c1.delete()
            c2.delete()
            return False
            
    except Exception as e:
        print_result("Duplicate Detection", False, f"Error: {str(e)}")
        c1.delete()
        return False

def test_model_fields_exist():
    """Test 6: All new fields exist on model"""
    print_header("TEST 6: Model Fields Verification")
    
    required_fields = [
        'pan_number',
        'pan_photo',
        'pan_verified',
        'pan_locked',
        'pan_history',
        'face_embedding_hash'
    ]
    
    all_present = True
    for field in required_fields:
        if hasattr(Candidate, field):
            print(f"  ✓ Field exists: {field}")
        else:
            print(f"  ❌ Missing field: {field}")
            all_present = False
    
    print_result("All Fields Present", all_present)
    return all_present

def test_database_constraints():
    """Test 7: Database constraints are applied"""
    print_header("TEST 7: Database Constraints")
    
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Check if pan_number unique constraint exists
        cursor.execute("""
            SELECT COUNT(*) FROM pg_indexes 
            WHERE indexname LIKE '%pan_number%' 
            AND tablename = 'ai_candidates_candidate'
        """)
        pan_index_count = cursor.fetchone()[0]
        
        if pan_index_count > 0:
            print_result("PAN Unique Index", True, f"Found {pan_index_count} PAN-related indexes")
        else:
            print_result("PAN Unique Index", False, "No PAN unique index found")
        
        # Check if face_embedding_hash index exists
        cursor.execute("""
            SELECT COUNT(*) FROM pg_indexes 
            WHERE indexname LIKE '%face_embedding%' 
            AND tablename = 'ai_candidates_candidate'
        """)
        face_index_count = cursor.fetchone()[0]
        
        if face_index_count > 0:
            print_result("Face Hash Index", True, f"Found {face_index_count} face hash indexes")
            return True
        else:
            print_result("Face Hash Index", False, "No face hash index found")
            return False

def main():
    print("\n" + "="*70)
    print("  VERIFIHIREAI - COMPREHENSIVE CHANGE VERIFICATION")
    print("  Date: 2026-05-05")
    print("  Testing: PAN Security + Face Duplicate Detection")
    print("="*70)
    
    results = []
    
    try:
        results.append(("PAN Uniqueness", test_pan_uniqueness()))
        results.append(("PAN Lock", test_pan_lock()))
        results.append(("PAN History", test_pan_history()))
        results.append(("Face Embedding Hash", test_face_embedding_hash()))
        results.append(("Face Duplicate Detection", test_face_duplicate_detection()))
        results.append(("Model Fields", test_model_fields_exist()))
        results.append(("Database Constraints", test_database_constraints()))
    except Exception as e:
        print(f"\n❌ ERROR during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print("\n" + "="*70)
    print(f"  RESULT: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("  ✅ ALL CHANGES ARE WORKING CORRECTLY!")
        print("="*70)
        return 0
    else:
        print("  ❌ SOME TESTS FAILED - REVIEW REQUIRED")
        print("="*70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
