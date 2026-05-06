"""
Script to convert localhost URLs to domain URLs (https://verifihireai.com)
Run this before deploying to production
"""
 
import os
import re
from pathlib import Path
 
# Define files to modify
TARGET_FILES = [
    "README.md",
    "backend/README.md",
    "backend/VerifiHireAI_backend/settings.py",
    "backend/ai_assessments/views.py",
    "backend/ai_candidates/views.py",
    "backend/api/pipeline.py",
    "backend/api/tasks.py",
    "backend/api/views/candidate_assessment_views.py",
    "backend/api/views/live_interview_views.py",
    "backend/api/views/user_views.py",
    "frontend/README.md",
    "frontend/src/pages/SecurePrecheck.js",
]
 
# Conversion mappings
REPLACEMENTS = [
    ("http://localhost:3000", "https://verifihireai.com"),
    ("http://127.0.0.1:3000", "https://verifihireai.com"),
    ("http://localhost:3001", "https://verifihireai.com"),
    ("http://127.0.0.1:3001", "https://verifihireai.com"),
    ("http://192.168.1.22:3001", "https://verifihireai.com"),
    # Handle www variant
    ("http://localhost:3000", "https://www.verifihireai.com"),
    # Download URLs
    ("http://localhost:3000", "https://downloads.verifihireai.com"),
    ("http://localhost:3000", "https://downloads.local"),
]
 
def convert_files(to_local=False):
    """Convert URLs between localhost and domain"""
    base_dir = Path(__file__).parent
    
    # Define replacements based on mode
    replacements = REPLACEMENTS
    if to_local:
        replacements = [(new, old) for old, new in REPLACEMENTS]
        target_desc = "localhost"
    else:
        target_desc = "https://verifihireai.com"
        
    print(f"Converting URLs to: {target_desc}\n")
    
    # Expand directories if any
    all_files = []
    for file_path in TARGET_FILES:
        full_path = base_dir / file_path
        if not full_path.exists():
            print(f"File/Directory not found: {file_path}")
            continue
            
        if full_path.is_dir():
            # Include .py, .md and .js files in the directory recursively
            for ext in ['*.py', '*.md', '*.js']:
                for p in full_path.rglob(ext):
                    all_files.append(p.relative_to(base_dir).as_posix())
        else:
            all_files.append(file_path)
    
    # Remove duplicates
    all_files = sorted(list(set(all_files)))
    
    for file_path in all_files:
        full_path = base_dir / file_path
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply all replacements
            for old, new in replacements:
                content = content.replace(old, new)
            
            # Write back if changes were made
            if content != original_content:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Updated: {file_path}")
            else:
                print(f"No changes needed: {file_path}")
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
 
if __name__ == "__main__":
    import sys
    to_local = "--local" in sys.argv
    convert_files(to_local=to_local)
    print("\nConversion complete!")