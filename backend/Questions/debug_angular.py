import sys
sys.path.insert(0, '.')

# Load QUESTIONS from Angular.py
with open('Angular.py', 'r') as f:
    content = f.read()
    exec_content = content.split('if __name__')[0]
    exec(exec_content)

print('Total questions:', len(QUESTIONS))
broken = [q for q in QUESTIONS if 'answer' not in q]
print('Questions without answer:', len(broken))
for i, b in enumerate(broken):
    print(f'  {i+1}. Q: {b.get("question", "NO QUESTION")}')
