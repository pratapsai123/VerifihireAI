"""
Script to convert localhost URLs to domain URLs (https://verifyhire.duckdns.org)
Run this before deploying to production
"""

import os
import re
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

# Conversion mappings
REPLACEMENTS = [
    ("http://localhost:3000", "https://verifyhire.duckdns.org"),
    ("http://127.0.0.1:3000", "https://verifyhire.duckdns.org"),
    ("http://localhost:3001", "https://verifyhire.duckdns.org"),
    ("http://127.0.0.1:3001", "https://verifyhire.duckdns.org"),
    ("http://192.168.1.22:3001", "https://verifyhire.duckdns.org"),
]

def convert_files():
    """Convert all localhost URLs to domain URLs"""
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
                
                # Count replacements
                count = sum(content.count(new) - original_content.count(new) for old, new in REPLACEMENTS)
                print(f"✅ Updated: {file_path}")
            else:
                print(f"ℹ️  No changes needed: {file_path}")
                
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

if __name__ == "__main__":
    print("🔄 Converting localhost URLs to: https://verifyhire.duckdns.org\n")
    convert_files()
    print("\n✨ Conversion complete!")
