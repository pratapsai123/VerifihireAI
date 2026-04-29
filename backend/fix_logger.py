# Script to fix the logger definition
import re

# Read the views.py file
with open('ai_candidates/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the incorrect logger definition
content = content.replace(
    "logger = logging.getLogger(__name__)",
    "logger = logging.getLogger(__name__)"
)

# Write back the corrected content
with open('ai_candidates/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed logger definition in views.py")
