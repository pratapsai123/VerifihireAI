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
    "backend/.env",
]
 
# Conversion mappings (Local -> Domain)
REPLACEMENTS = [
    ("http://localhost:3000", "https://verifihireai.com"),
    ("http://127.0.0.1:3000", "https://verifihireai.com"),
    ("http://localhost:3001", "https://verifihireai.com"),
    ("http://127.0.0.1:3001", "https://verifihireai.com"),
    ("http://192.168.1.22:3001", "https://verifihireai.com"),
    ("http://localhost:5173", "https://verifihireai.com"),
    ("http://localhost:5174", "https://verifihireai.com"),
]
 
def update_env_file(full_path, to_local):
    """Special handling for .env file to ensure specific variables are set correctly"""
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        new_lines = []
        for line in lines:
            if line.startswith("DJANGO_DEBUG="):
                new_lines.append(f"DJANGO_DEBUG={'True' if to_local else 'False'}\n")
            elif line.startswith("FRONTEND_BASE_URL="):
                new_lines.append(f"FRONTEND_BASE_URL={'http://localhost:3000' if to_local else 'https://verifihireai.com'}\n")
            elif line.startswith("ALLOWED_HOSTS="):
                new_lines.append(f"ALLOWED_HOSTS={'localhost,127.0.0.1' if to_local else 'verifihireai.com,api.verifihireai.com'}\n")
            elif line.startswith("CORS_ALLOWED_ORIGINS="):
                new_lines.append(f"CORS_ALLOWED_ORIGINS={'http://localhost:3000' if to_local else 'https://verifihireai.com'}\n")
            elif line.startswith("CSRF_TRUSTED_ORIGINS="):
                new_lines.append(f"CSRF_TRUSTED_ORIGINS={'http://localhost:3000' if to_local else 'https://verifihireai.com'}\n")
            else:
                # Apply general replacements to other lines in .env if any
                processed_line = line
                replacements = REPLACEMENTS
                if to_local:
                    replacements = [(new, old) for old, new in REPLACEMENTS]
                
                for old, new in replacements:
                    processed_line = processed_line.replace(old, new)
                new_lines.append(processed_line)
        
        content = "".join(new_lines)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated (Special): {full_path.name}")
        
    except Exception as e:
        print(f"Error updating .env file: {e}")
 
def convert_files(to_local=False):
    """Convert URLs between localhost and domain"""
    base_dir = Path(__file__).parent
    
    # Define replacements based on mode
    replacements = REPLACEMENTS
    if to_local:
        # Reverse replacements for local mode
        # We use a set to avoid duplicate reversals if any
        unique_replacements = []
        seen = set()
        for old, new in REPLACEMENTS:
            if (new, old) not in seen:
                unique_replacements.append((new, old))
                seen.add((new, old))
        replacements = unique_replacements
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
            for ext in ['*.py', '*.md', '*.js', '*.env']:
                for p in full_path.rglob(ext):
                    all_files.append(p.relative_to(base_dir).as_posix())
        else:
            all_files.append(file_path)
    
    # Remove duplicates
    all_files = sorted(list(set(all_files)))
    
    for file_path in all_files:
        full_path = base_dir / file_path
        
        # Special handling for .env
        if full_path.name == ".env":
            update_env_file(full_path, to_local)
            continue
            
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