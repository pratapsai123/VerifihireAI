import re
import os

file_path = os.path.join(os.path.dirname(__file__), 'coding_skeletons.py')

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

categories = [
    ('overlap', 'Intervals'), ('interval', 'Intervals'),
    ('regex', 'String'), ('string', 'String'), ('palindrome', 'String'), ('anagram', 'String'), ('character', 'String'), ('brackets', 'String'),
    ('sum', 'Math'), ('math', 'Math'), ('fizz', 'Math'), ('power', 'Math'), ('stair', 'Math'),
    ('matrix', 'Matrix'), ('rotate', 'Matrix'), ('straight', 'Matrix'),
    ('sort', 'Sorting'), ('search', 'Searching'), ('frequency', 'Sorting'),
    ('tree', 'Trees'), ('graph', 'Graphs'),
    ('duplicate', 'HashMap'), ('intersection', 'HashMap'), ('unique', 'HashMap'), ('majority', 'HashMap'),
]

new_lines = []
current_id = ''

for line in lines:
    if '"id":' in line:
        current_id = line.lower()
    if '"title_hint":' in line:
        current_id += line.lower()
    
    if '"difficulty":' in line:
        # Determine category based on current_id buffer
        assigned = 'Array'
        for kw, cat in categories:
            if kw in current_id:
                assigned = cat
                break
        
        new_lines.append(line)
        new_lines.append(f'            "category": "{assigned}",\n')
    elif '"category":' not in line:
        new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Categories intelligently applied!")
