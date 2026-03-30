import re

# Mock the logic from views.py
_label_pattern = re.compile(
    r'\b(?:JD|RESUME[- ]?SKILL|PROJECT|SCENARIO|SYNTAX|INTRO)\b[- ]?Q?\d*[:\.\-—]*\s*',
    re.IGNORECASE
)

test_cases = [
    ("Based on your INTROduction, you have a solid background.", "Based on your INTROduction, you have a solid background."),
    ("I noticed your projects involve React.", "I noticed your projects involve React."),
    ("In your scenarios, how do you handle scale?", "In your scenarios, how do you handle scale?"),
    ("PROJECT-Q5: Tell me about Java.", "Tell me about Java."),
    ("JD: Must have SQL skills.", "Must have SQL skills."),
    ("yours is a great answer.", "yours is a great answer."),
    ("INTRO: Welcome to the team.", "Welcome to the team.")
]

print("Verifying Typo Fix (Regex Word Boundary):")
failed = False
for original, expected in test_cases:
    result = _label_pattern.sub('', original).strip()
    if result == expected:
        print(f"PASS: '{original}' -> '{result}'")
    else:
        print(f"FAIL: '{original}' -> EXPECTED '{expected}' BUT GOT '{result}'")
        failed = True

if not failed:
    print("\nSUCCESS: All typo test cases passed!")
else:
    print("\nFAILURE: Some test cases failed.")
