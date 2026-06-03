import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from deepface import DeepFace

def verify_stored_identities():
    print("=== Verification of Stored Identity Images ===")
    identities_dir = "media/identities"
    
    if not os.path.exists(identities_dir):
        print(f"Error: Directory '{identities_dir}' does not exist.")
        return
        
    # Gather all canonical face image paths dynamically
    image_records = []
    for candidate_dir in os.listdir(identities_dir):
        full_dir_path = os.path.join(identities_dir, candidate_dir)
        if os.path.isdir(full_dir_path):
            canonical_path = os.path.join(full_dir_path, "canonical.jpg")
            if os.path.exists(canonical_path):
                image_records.append({
                    'id': candidate_dir,
                    'path': canonical_path
                })
            else:
                print(f"Warning: No canonical.jpg found for candidate ID '{candidate_dir}'")

    if len(image_records) < 2:
        print(f"Error: Found only {len(image_records)} valid canonical images. Need at least 2 to compare.")
        return

    print(f"Successfully loaded {len(image_records)} candidate identity records to compare.\n")

    # Compare every unique image pair
    comparisons_run = 0
    failures = 0
    
    for i in range(len(image_records)):
        for j in range(i + 1, len(image_records)):
            rec1 = image_records[i]
            rec2 = image_records[j]
            
            p1, p2 = rec1['path'], rec2['path']
            id1, id2 = rec1['id'], rec2['id']
            
            print(f"Comparing Identity '{id1}' vs '{id2}'...")
            try:
                # Perform biometric verification using ArcFace + RetinaFace with strict face detection
                res = DeepFace.verify(
                    img1_path=p1,
                    img2_path=p2,
                    model_name="ArcFace",
                    detector_backend="retinaface",
                    enforce_detection=True,
                    align=True
                )
                
                verified = res.get('verified', False)
                distance = res.get('distance', 1.0)
                threshold = res.get('threshold', 0.68)
                
                print(f"  > Verification Result: {'[MATCH - Same Person]' if verified else '[MISMATCH - Different Persons]'}")
                print(f"  > Distance Score: {distance:.4f} (Threshold: {threshold})")
                print(f"  > Verification Success: {verified}\n")
                comparisons_run += 1
                
            except Exception as e:
                print(f"  > [ERROR] Comparison failed between '{id1}' and '{id2}': {e}\n")
                failures += 1
                
    print(f"=== Verification Complete ===")
    print(f"Total successful comparisons run: {comparisons_run}")
    print(f"Total failed comparisons: {failures}")

if __name__ == '__main__':
    verify_stored_identities()
