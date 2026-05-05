import sys

with open('backend/ai_candidates/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line in CandidatePublicDetailView where candidate.save(update_fields=['link_opened_at']) is
for i, line in enumerate(lines):
    if "candidate.save(update_fields=['link_opened_at'])" in line:
        print(f'Found save at line {i+1}')
        # Replace this line with PAN lock logic
        indent = '            '
        lines[i] = indent + "# Lock PAN when interview starts - prevents PAN swapping\n"
        lines.insert(i+1, indent + "candidate.pan_locked = True\n")
        lines.insert(i+2, indent + "candidate.save(update_fields=['link_opened_at', 'pan_locked'])\n")
        break

with open('backend/ai_candidates/views.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('SUCCESS: PAN lock added to CandidatePublicDetailView')
