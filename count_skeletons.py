
path = 'backend/ai_assessments/coding_skeletons.py'
with open(path, 'r') as f:
    content = f.read()

easy = content.count('"difficulty": "Easy"')
medium = content.count('"difficulty": "Medium"')
hard = content.count('"difficulty": "Hard"')

print(f"Easy: {easy}")
print(f"Medium: {medium}")
print(f"Hard: {hard}")
print(f"TOTAL: {easy + medium + hard}")

# Count unique IDs
import re
ids = re.findall(r'"id":\s*"(skel_[^"]+)"', content)
print(f"\nUnique skeleton IDs: {len(set(ids))}")
if len(ids) != len(set(ids)):
    from collections import Counter
    dupes = [id for id, count in Counter(ids).items() if count > 1]
    print(f"DUPLICATE IDS: {dupes}")
else:
    print("No duplicate IDs - all unique!")
