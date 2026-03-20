"""
Script to convert domain URLs back to localhost URLs (http://localhost:3000)
Run this to revert to local development settings
"""

import os
from pathlib import Path

# Define files to modify
FILES_TO_MODIFY = [
    "backend/VerifiHireAI_backend/settings.py",
    "backend/ai_candidates/views.py",
    "backend/api/views.py",
    "backend/ai_assessments/views.py",
    "backend/README.md",
    "README.md",
    "frontend/README.md",
]

# Conversion mappings (reverse)
REPLACEMENTS = [
    ("https://verifihireai.com", "http://localhost:3000"),
]

def convert_files():
    """Convert domain URLs back to localhost URLs"""
    base_dir = Path(__file__).parent
    
    for file_path in FILES_TO_MODIFY:
        full_path = base_dir / file_path
        
        if not full_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply all replacements
            for old, new in REPLACEMENTS:
                content = content.replace(old, new)
            
            # Write back if changes were made
            if content != original_content:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Reverted: {file_path}")
            else:
                print(f"ℹ️  No changes needed: {file_path}")
                
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

if __name__ == "__main__":
    print("🔄 Reverting domain URLs to: http://localhost:3000\n")
    convert_files()
    print("\n✨ Reversion complete!")
