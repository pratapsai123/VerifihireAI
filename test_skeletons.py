import sys
sys.path.insert(0, 'backend')
from ai_assessments.coding_skeletons import CodingSkeletons

easy = [s for s in CodingSkeletons.SKELETONS if s['difficulty'] == 'Easy']
med = [s for s in CodingSkeletons.SKELETONS if s['difficulty'] == 'Medium']
hard = [s for s in CodingSkeletons.SKELETONS if s['difficulty'] == 'Hard']

print(f"Easy: {len(easy)}, Medium: {len(med)}, Hard: {len(hard)}")
print(f"Total skeletons loaded: {len(CodingSkeletons.SKELETONS)}")

s = CodingSkeletons.get_skeleton('Easy')
print(f"Random Easy: {s['id']} - {s['title_hint']}")

s = CodingSkeletons.get_skeleton('Medium')
print(f"Random Medium: {s['id']} - {s['title_hint']}")

s = CodingSkeletons.get_skeleton('Hard')
print(f"Random Hard: {s['id']} - {s['title_hint']}")

print("\nAll skeletons loaded and working correctly!")
