import random

class CodingSkeletons:
    """A library of proven coding challenge 'skeletons'. 
    Each skeleton contains:
    - id: Unique identifier
    - title_hint: Context hint for AI
    - logic_desc: Mathematical description for AI
    - difficulty: Easy/Medium/Hard
    - input_schema: Generator configuration
    - gold_solution: 100% Correct Python solution
    - input_generator: Python function to generate random valid text inputs
    """
    
    SKELETONS = [
        {
            "id": "skel_max_overlap",
            "title_hint": "Peak Concurrency / Overlapping Intervals",
            "logic_desc": "Detect the maximum number of intervals that overlap at any given point in time.",
            "difficulty": "Medium",
            "category": "Intervals",
            "input_schema": [{"type": "int", "name": "N", "min": 1, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    starts = [int(x) for x in input_data[1:n+1]]
    ends = [int(x) for x in input_data[n+1:2*n+1]]
    events = []
    # FIX: Correct backward intervals and use +1 for start, -1 for end
    for s, e in zip(starts, ends):
        ts, te = min(s, e), max(s, e)
        events.append((ts, 1))
        events.append((te, -1))
    
    # FIX: Sort by time, then by type DESCENDING (1 before -1)
    # This ensures intervals touching at a point are counted as overlapping.
    events.sort(key=lambda x: (x[0], -x[1]))
    
    max_c = cur_c = 0
    for t, delta in events:
        cur_c += delta
        max_c = max(max_c, cur_c)
    print(max_c)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None # Handled by InputDataGenerator
        },
        {
            "id": "skel_target_sum",
            "title_hint": "Pair Finding / Two Sum Variation",
            "logic_desc": "Find if there exists a pair of integers in an array that sums up to a target value.",
            "difficulty": "Easy",
            "category": "Math",
            "input_schema": [{"type": "int", "name": "Target", "min": 1, "max": 200}, {"type": "int", "name": "N", "min": 1, "max": 30}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    target = int(input_data[0])
    n = int(input_data[1])
    nums = [int(x) for x in input_data[2:]]
    seen = set()
    found = False
    for x in nums:
        if (target - x) in seen:
            found = True
            break
        seen.add(x)
    print("YES" if found else "NO")
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_longest_unique_substr",
            "title_hint": "Unique Data Stream Segment",
            "logic_desc": "Find the length of the longest continuous segment of data that contains no duplicates.",
            "difficulty": "Medium",
            "category": "HashMap",
            "input_schema": [{"type": "string", "name": "S", "min": 1, "max": 50}],
            "gold_solution": """import sys
def main():
    s = sys.stdin.read().strip()
    if not s: return
    char_map = {}
    left = max_len = 0
    for right in range(len(s)):
        if s[right] in char_map and char_map[s[right]] >= left:
            left = char_map[s[right]] + 1
        char_map[s[right]] = right
        max_len = max(max_len, right - left + 1)
    print(max_len)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_frequency_sorting",
            "title_hint": "Priority-Based Processing",
            "logic_desc": "Group elements by frequency and sort them based on how often they occur.",
            "difficulty": "Easy",
            "category": "Sorting",
            "input_schema": [{"type": "int", "name": "N", "min": 1, "max": 30}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 20}}],
            "gold_solution": """import sys
from collections import Counter
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    nums = [int(x) for x in input_data[1:]]
    counts = Counter(nums)
    res = sorted(nums, key=lambda x: (counts[x], x))
    print(" ".join(map(str, res)))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_max_stock_profit",
            "title_hint": "Optimal Transaction Period",
            "logic_desc": "Find the maximum possible profit from a single buy and sell transaction given time-series values.",
            "difficulty": "Easy",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 1, "max": 30}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 500}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    prices = [int(x) for x in input_data[1:]]
    if n < 2:
        print(0)
        return
    min_p = float('inf')
    max_prof = 0
    for p in prices:
        min_p = min(min_p, p)
        max_prof = max(max_prof, p - min_p)
    print(max_prof)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_matrix_rotate",
            "title_hint": "Grid Transformation / Matrix Rotation",
            "logic_desc": "Rotate an N x N matrix of integers 90 degrees clockwise.",
            "difficulty": "Medium",
            "category": "Matrix",
            "input_schema": [{"type": "int", "name": "N", "min": 2, "max": 5}, {"type": "matrix", "rows_ref": "N", "cols_ref": "N", "item": {"type": "int", "min": 0, "max": 9}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    matrix = []
    idx = 1
    for r in range(n):
        matrix.append([int(x) for x in input_data[idx:idx+n]])
        idx += n
    res = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            res[j][n-1-i] = matrix[i][j]
    for r in res:
        print(" ".join(map(str, r)))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_balanced_brackets",
            "title_hint": "Syntax Validation / Balanced Brackets",
            "logic_desc": "Find if a string of brackets (parentheses, square, and curly) is correctly balanced.",
            "difficulty": "Easy",
            "category": "String",
            "input_schema": [{"type": "string", "name": "S", "length": 12}],
            "gold_solution": """import sys
def main():
    s = sys.stdin.read().strip()
    if not s: return
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    balanced = True
    for char in s:
        if char in '({[':
            stack.append(char)
        elif char in mapping:
            if not stack or stack.pop() != mapping[char]:
                balanced = False
                break
        else: continue # Ignore other chars
    print("YES" if balanced and not stack else "NO")
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_merge_intervals",
            "title_hint": "Timeline Consolidation / Merging Intervals",
            "logic_desc": "Merge any overlapping intervals into a set of exclusive continuous ranges.",
            "difficulty": "Medium",
            "category": "Intervals",
            "input_schema": [{"type": "int", "name": "N", "min": 2, "max": 10}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 50}}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 50}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    starts = [int(x) for x in input_data[1:n+1]]
    ends = [int(x) for x in input_data[n+1:2*n+1]]
    intervals = sorted([[min(s,e), max(s,e)] for s,e in zip(starts, ends)])
    merged = []
    for curr in intervals:
        if not merged or curr[0] > merged[-1][1]:
            merged.append(curr)
        else:
            merged[-1][1] = max(merged[-1][1], curr[1])
    for start, end in merged:
        print(f"{start} {end}")
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_single_number",
            "title_hint": "Data Integrity / Unique Element Search",
            "logic_desc": "Find the element that appears exactly once in an array where all other elements appear twice.",
            "difficulty": "Easy",
            "category": "Searching",
            "input_schema": [{"type": "int", "name": "M", "min": 2, "max": 8}, {"type": "array", "name": "distinct", "count_ref": "M", "item": {"type": "int", "min": 1, "max": 99}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    m = int(input_data[0])
    # The system will generate M distinct numbers. To form the pattern (all twice except one thrice)
    # We'll just take the data as provided and find the one that occurs once.
    # Actually, the simple logic is XORing everything.
    nums = [int(x) for x in input_data[1:]]
    # For a real challenge, we expect (2n + 1) inputs. We will simulate this by using all but the last pair.
    # Logic: XOR all input numbers.
    res = 0
    for x in nums:
        res ^= x
    print(res)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_binary_search",
            "title_hint": "Optimized Lookup / First Occurrence",
            "logic_desc": "Perform an efficient search to find the index of the first occurrence of a target in a sorted list.",
            "difficulty": "Medium",
            "category": "Searching",
            "input_schema": [{"type": "int", "name": "Target", "min": 1, "max": 50}, {"type": "int", "name": "N", "min": 5, "max": 15}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    target = int(input_data[0])
    n = int(input_data[1])
    nums = sorted([int(x) for x in input_data[2:]])
    res = -1
    low, high = 0, n - 1
    while low <= high:
        mid = (low + high) // 2
        if nums[mid] == target:
            res = mid
            high = mid - 1
        elif nums[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    print(res)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_regex_matching",
            "title_hint": "Dynamic Evaluation / Regex Matching",
            "logic_desc": "Implement regular expression matching with support for '.' and '*'.",
            "difficulty": "Hard",
            "category": "String",
            "input_schema": [{"type": "string", "name": "s", "length": 10}, {"type": "string", "name": "p", "length": 5}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if len(input_data) < 2: return
    s, p = input_data[0], input_data[1]
    m, n = len(s), len(p)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    for j in range(1, n + 1):
        if p[j - 1] == '*':
            dp[0][j] = dp[0][j - 2]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if p[j - 1] == '.' or p[j - 1] == s[i - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            elif p[j - 1] == '*':
                dp[i][j] = dp[i][j - 2] or (dp[i - 1][j] and (s[i - 1] == p[j - 2] or p[j - 2] == '.'))
    print("true" if dp[m][n] else "false")
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_trapping_rain_water",
            "title_hint": "Topological Capacity / Trapping Water",
            "logic_desc": "Given an elevation map where the width of each bar is 1, compute how much water it can trap after raining.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 2, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 0, "max": 20}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    height = [int(x) for x in input_data[1:]]
    if not height:
        print(0)
        return
    left, right = 0, len(height) - 1
    left_max, right_max = height[left], height[right]
    water = 0
    while left < right:
        if left_max < right_max:
            left += 1
            left_max = max(left_max, height[left])
            water += left_max - height[left]
        else:
            right -= 1
            right_max = max(right_max, height[right])
            water += right_max - height[right]
    print(water)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_edit_distance",
            "title_hint": "String Transformation / Edit Distance",
            "logic_desc": "Find the minimum number of operations required to convert string word1 to string word2.",
            "difficulty": "Hard",
            "category": "String",
            "input_schema": [{"type": "string", "name": "word1", "length": 10}, {"type": "string", "name": "word2", "length": 10}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if len(input_data) < 2: return
    word1, word2 = input_data[0], input_data[1]
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1): dp[i][0] = i
    for j in range(n + 1): dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(dp[i - 1][j - 1], dp[i - 1][j], dp[i][j - 1]) + 1
    print(dp[m][n])
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_sliding_window_max",
            "title_hint": "Stream Processing / Sliding Window Maximum",
            "logic_desc": "Return the maximum in each sliding window of size k moving across an array.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 5, "max": 20}, {"type": "int", "name": "K", "min": 2, "max": 4}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
from collections import deque
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    k = int(input_data[1])
    nums = [int(x) for x in input_data[2:]]
    if k > n: k = n
    q = deque()
    res = []
    for i in range(len(nums)):
        while q and q[0] < i - k + 1:
            q.popleft()
        while q and nums[q[-1]] < nums[i]:
            q.pop()
        q.append(i)
        if i >= k - 1:
            res.append(nums[q[0]])
    print(" ".join(map(str, res)))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_max_subarray_sum",
            "title_hint": "Financial Fluctuation / Max Subarray",
            "logic_desc": "Find the maximum sum of a contiguous subarray within a one-dimensional array of numbers.",
            "difficulty": "Medium",
            "category": "Math",
            "input_schema": [{"type": "int", "name": "N", "min": 1, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": -100, "max": 100}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    nums = [int(x) for x in input_data[1:]]
    max_so_far = float('-inf')
    current_max = 0
    for num in nums:
        current_max += num
        if current_max > max_so_far:
            max_so_far = current_max
        if current_max < 0:
            current_max = 0
    print(max_so_far)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_product_except_self",
            "title_hint": "Data Scaling / Product Except Self",
            "logic_desc": "Return an array where each element is the product of all elements in the input array except itself. You cannot use division.",
            "difficulty": "Medium",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 2, "max": 15}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 10}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    nums = [int(x) for x in input_data[1:]]
    if n == 0: return
    left = [1] * n
    right = [1] * n
    for i in range(1, n):
        left[i] = left[i-1] * nums[i-1]
    for i in range(n-2, -1, -1):
        right[i] = right[i+1] * nums[i+1]
    res = [str(left[i] * right[i]) for i in range(n)]
    print(" ".join(res))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_longest_consecutive_seq",
            "title_hint": "Continuous Segment / Longest Consecutive Sequence",
            "logic_desc": "Given an unsorted array of integers, return the length of the longest consecutive elements sequence.",
            "difficulty": "Medium",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 1, "max": 30}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 200}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    nums = set(int(x) for x in input_data[1:])
    longest_streak = 0
    for num in nums:
        if num - 1 not in nums:
            current_num = num
            current_streak = 1
            while current_num + 1 in nums:
                current_num += 1
                current_streak += 1
            longest_streak = max(longest_streak, current_streak)
    print(longest_streak)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_group_anagrams",
            "title_hint": "Data Categorization / Group Similar Strings",
            "logic_desc": "Given an array of strings, group the anagrams together. Output the number of unique groups.",
            "difficulty": "Medium",
            "category": "String",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 15}, {"type": "array", "count_ref": "N", "item": {"type": "string", "length": 4}}],
            "gold_solution": """import sys
from collections import defaultdict
def main():
    input_data = sys.stdin.read().split()
    if len(input_data) < 2: return
    n = int(input_data[0])
    words = input_data[1:n+1]
    groups = defaultdict(list)
    for w in words:
        s_w = "".join(sorted(w))
        groups[s_w].append(w)
    print(len(groups))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_missing_number",
            "title_hint": "Data Audit / Missing Sequential Identifier",
            "logic_desc": "Given an array containing n distinct numbers taken from 0, 1, 2, ..., n, find the one that is missing from the array.",
            "difficulty": "Easy",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 50}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 0, "max": 50}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    nums = [int(x) for x in input_data[1:]]
    expected_sum = (len(nums) * (len(nums) + 1)) // 2
    actual_sum = sum(nums)
    print(expected_sum - actual_sum)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_valid_palindrome",
            "title_hint": "String Validation / Palindrome Check",
            "logic_desc": "Given a string, determine if it is a palindrome, considering only alphanumeric characters and ignoring cases.",
            "difficulty": "Easy",
            "category": "String",
            "input_schema": [{"type": "string", "name": "S", "length": 25}],
            "gold_solution": """import sys
def main():
    s = sys.stdin.read().strip()
    clean = [c.lower() for c in s if c.isalnum()]
    if clean == clean[::-1]:
        print("true")
    else:
        print("false")
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_majority_element",
            "title_hint": "Consensus Voting / Majority Element",
            "logic_desc": "Given an array of size n, find the majority element. The majority element is the element that appears more than n / 2 times.",
            "difficulty": "Easy",
            "category": "HashMap",
            "input_schema": [{"type": "int", "name": "N", "min": 5, "max": 25}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 10}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if len(input_data) < 2: return
    n = int(input_data[0])
    nums = [int(x) for x in input_data[1:]]
    count = 0
    candidate = None
    for num in nums:
        if count == 0:
            candidate = num
        count += (1 if num == candidate else -1)
    print(candidate)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_contains_duplicate",
            "title_hint": "Data Duplication / Duplicate Check",
            "logic_desc": "Given an integer array nums, return true if any value appears at least twice in the array, and return false if every element is distinct.",
            "difficulty": "Easy",
            "category": "HashMap",
            "input_schema": [{"type": "int", "name": "N", "min": 5, "max": 30}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 50}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if len(input_data) < 2: return
    n = int(input_data[0])
    nums = [int(x) for x in input_data[1:]]
    if len(nums) != len(set(nums)):
        print("true")
    else:
        print("false")
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_valid_anagram",
            "title_hint": "Character Frequency / Anagram Detection",
            "logic_desc": "Given two strings, write a function to determine if they are valid anagrams of each other.",
            "difficulty": "Easy",
            "category": "String",
            "input_schema": [{"type": "string", "name": "S", "length": 15}, {"type": "string", "name": "T", "length": 15}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if len(input_data) < 2: return
    s, t = input_data[0], input_data[1]
    if sorted(s) == sorted(t):
        print("true")
    else:
        print("false")
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_move_zeroes",
            "title_hint": "Array Operation / Move Elements Array",
            "logic_desc": "Given an integer array nums, move all 0s to the end of it while maintaining the relative order of the non-zero elements.",
            "difficulty": "Easy",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 5, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 0, "max": 9}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    nums = [int(x) for x in input_data[1:]]
    non_zero = [x for x in nums if x != 0]
    zeroes = [0] * (len(nums) - len(non_zero))
    res = non_zero + zeroes
    print(" ".join(map(str, res)))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_power_of_two",
            "title_hint": "Bitwise Check / Power of Two Evaluation",
            "logic_desc": "Given an integer, write a function to determine if it is a power of two.",
            "difficulty": "Easy",
            "category": "Math",
            "input_schema": [{"type": "int", "name": "N", "min": 0, "max": 1000}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    if n <= 0:
        print("false")
    elif (n & (n - 1)) == 0:
        print("true")
    else:
        print("false")
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_isomorphic_strings",
            "title_hint": "Character Mapping / Isomorphic Verification",
            "logic_desc": "Determine if two strings are isomorphic. Two strings are isomorphic if the characters in the first can be replaced to get the second.",
            "difficulty": "Easy",
            "category": "String",
            "input_schema": [{"type": "string", "name": "s", "length": 8}, {"type": "string", "name": "t", "length": 8}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if len(input_data) < 2: return
    s, t = input_data[0], input_data[1]
    if len(s) != len(t):
        print("false")
        return
    map_s_t, map_t_s = {}, {}
    for c1, c2 in zip(s, t):
        if (c1 in map_s_t and map_s_t[c1] != c2) or (c2 in map_t_s and map_t_s[c2] != c1):
            print("false")
            return
        map_s_t[c1] = c2
        map_t_s[c2] = c1
    print("true")
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_fizz_buzz",
            "title_hint": "Module Counting / Sequence Rules",
            "logic_desc": "Output a special sequence for numbers 1 to n where multiples of 3 are substituted with Fizz and multiples of 5 with Buzz.",
            "difficulty": "Easy",
            "category": "Math",
            "input_schema": [{"type": "int", "name": "N", "min": 5, "max": 30}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    res = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            res.append("FizzBuzz")
        elif i % 3 == 0:
            res.append("Fizz")
        elif i % 5 == 0:
            res.append("Buzz")
        else:
            res.append(str(i))
    print(" ".join(res))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_reverse_string",
            "title_hint": "String Reversal / Text Inversion",
            "logic_desc": "Reverse a given string segment natively.",
            "difficulty": "Easy",
            "category": "String",
            "input_schema": [{"type": "string", "name": "Word", "length": 20}],
            "gold_solution": """import sys
def main():
    s = sys.stdin.read().strip()
    if s:
        print(s[::-1])
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_climbing_stairs",
            "title_hint": "Path Combinations / Climbing Constraints",
            "logic_desc": "You are climbing a staircase. It takes n steps to reach the top. Each time you can either climb 1 or 2 steps. Find how many distinct ways you can climb.",
            "difficulty": "Easy",
            "category": "Math",
            "input_schema": [{"type": "int", "name": "N", "min": 1, "max": 30}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    if n <= 2:
        print(n)
        return
    a, b = 1, 2
    for _ in range(3, n + 1):
        a, b = b, a + b
    print(b)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_best_time_to_buy_sell_stock_ii",
            "title_hint": "Cumulative Profit / Infinite Transactions",
            "logic_desc": "Find the maximum profit from an array of daily prices, where you may engage in as many transactions as you like.",
            "difficulty": "Easy",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    prices = [int(x) for x in input_data[1:]]
    max_profit = 0
    for i in range(1, len(prices)):
        if prices[i] > prices[i-1]:
            max_profit += prices[i] - prices[i-1]
    print(max_profit)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_check_straight_line",
            "title_hint": "Geometry Verification / Coordinate Linearity",
            "logic_desc": "Determine if an array of coordinates forms a straight line in the XY plane.",
            "difficulty": "Easy",
            "category": "Matrix",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 10}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 10}}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 10}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    x_coords = [int(x) for x in input_data[1:n+1]]
    y_coords = [int(x) for x in input_data[n+1:2*n+1]]
    if n <= 2:
        print("true")
        return
    x0, y0 = x_coords[0], y_coords[0]
    x1, y1 = x_coords[1], y_coords[1]
    for i in range(2, n):
        x, y = x_coords[i], y_coords[i]
        if (y1 - y0) * (x - x0) != (y - y0) * (x1 - x0):
            print("false")
            return
    print("true")
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_first_unique_character",
            "title_hint": "Unique Element Indexing / First Singleton",
            "logic_desc": "In a given string, find the first non-repeating character and return its index. If it does not exist, return -1.",
            "difficulty": "Easy",
            "category": "String",
            "input_schema": [{"type": "string", "name": "Word", "length": 25}],
            "gold_solution": """import sys
from collections import Counter
def main():
    s = sys.stdin.read().strip()
    if not s: return
    counts = Counter(s)
    for i, char in enumerate(s):
        if counts[char] == 1:
            print(i)
            return
    print("-1")
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_intersection_two_arrays",
            "title_hint": "Data Intersection / Set Overlap",
            "logic_desc": "Given two distinct lists of entities, return an array of their unique intersection.",
            "difficulty": "Easy",
            "category": "Intervals",
            "input_schema": [{"type": "int", "name": "N", "min": 2, "max": 15}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 20}}, {"type": "int", "name": "M", "min": 2, "max": 15}, {"type": "array", "count_ref": "M", "item": {"type": "int", "min": 1, "max": 20}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if len(input_data) < 3: return
    n = int(input_data[0])
    arr1 = [int(x) for x in input_data[1:n+1]]
    m = int(input_data[n+1])
    arr2 = [int(x) for x in input_data[n+2:n+2+m]]
    intersection = sorted(list(set(arr1) & set(arr2)))
    print(" ".join(map(str, intersection)))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_first_missing_positive",
            "title_hint": "Data Sanity / Lowest Missing Identifier",
            "logic_desc": "Given an unsorted integer array, return the smallest missing positive integer. You must implement an algorithm that runs in O(n) time and uses constant extra space.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 5, "max": 40}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": -20, "max": 40}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    nums = [int(x) for x in input_data[1:]]
    for i in range(len(nums)):
        while 1 <= nums[i] <= len(nums) and nums[nums[i] - 1] != nums[i]:
            nums[nums[i] - 1], nums[i] = nums[i], nums[nums[i] - 1]
    for i in range(len(nums)):
        if nums[i] != i + 1:
            print(i + 1)
            return
    print(len(nums) + 1)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_largest_rectangle_histogram",
            "title_hint": "Geometric Analytics / Max Area Bounds",
            "logic_desc": "Given an array of integers representing the histogram's bar height where the width of each bar is 1, return the area of the largest rectangle in the histogram.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 5, "max": 30}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 0, "max": 50}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    heights = [int(x) for x in input_data[1:]]
    stack = []
    max_area = 0
    heights.append(0)
    for i, h in enumerate(heights):
        start = i
        while stack and stack[-1][1] > h:
            index, height = stack.pop()
            max_area = max(max_area, height * (i - index))
            start = index
        stack.append((start, h))
    print(max_area)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_candy",
            "title_hint": "Resource Distribution / Rating Allocation",
            "logic_desc": "You are distributing rewards to elements in a sequence based on a rating array. Every element must have at least one reward. Elements with a higher rating get more rewards than their neighbors.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 5, "max": 30}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    ratings = [int(x) for x in input_data[1:]]
    candies = [1] * len(ratings)
    for i in range(1, len(ratings)):
        if ratings[i] > ratings[i-1]:
            candies[i] = candies[i-1] + 1
    for i in range(len(ratings)-2, -1, -1):
        if ratings[i] > ratings[i+1]:
            candies[i] = max(candies[i], candies[i+1] + 1)
    print(sum(candies))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_count_smaller_after_self",
            "title_hint": "Trend Analytics / Inversion Counts",
            "logic_desc": "Given an integer array, return an array where the value at each index is the number of smaller elements to the right of that index.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 5, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": -50, "max": 50}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    nums = [int(x) for x in input_data[1:]]
    from bisect import bisect_left
    sorted_arr = []
    res = []
    for num in reversed(nums):
        idx = bisect_left(sorted_arr, num)
        res.append(idx)
        sorted_arr.insert(idx, num)
    print(" ".join(map(str, res[::-1])))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_reverse_pairs",
            "title_hint": "Statistical Anomalies / Major Inversion Detection",
            "logic_desc": "Given an integer array, return the number of reverse pairs where i < j and nums[i] > 2 * nums[j].",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 5, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": -50, "max": 50}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    nums = [int(x) for x in input_data[1:]]
    res, sorted_arr = 0, []
    from bisect import bisect_right
    res2 = 0
    nnums = nums[:]
    def mergeSort(arr):
        if len(arr) <= 1: return arr
        mid = len(arr) // 2
        left, right = mergeSort(arr[:mid]), mergeSort(arr[mid:])
        nonlocal res2
        j = 0
        for i in range(len(left)):
            while j < len(right) and left[i] > 2 * right[j]:
                j += 1
            res2 += j
        return sorted(left + right)
    mergeSort(nnums)
    print(res2)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_burst_balloons",
            "title_hint": "Destructive Maximization / Boundary Collapses",
            "logic_desc": "Given an array of values, find the maximum coins you can collect by bursting all elements sequentially. Bursting an element yields coins equal to the product of its value and its adjacent unburst bounds.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 10}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 10}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    nums = [int(x) for x in input_data[1:]]
    nums = [1] + nums + [1]
    dp = [[0] * len(nums) for _ in range(len(nums))]
    for length in range(1, len(nums) - 1):
        for left in range(1, len(nums) - length):
            right = left + length - 1
            for i in range(left, right + 1):
                dp[left][right] = max(dp[left][right], dp[left][i - 1] + nums[left - 1] * nums[i] * nums[right + 1] + dp[i + 1][right])
    print(dp[1][len(nums) - 2])
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_russian_doll_envelopes",
            "title_hint": "Dimensional Nesting / Multi-Parameter Subsequence",
            "logic_desc": "Given an array of 2D attributes [width, height], determine the maximum number of items you can Russian doll fit inside one another.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 5, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 20}}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 20}}],
            "gold_solution": """import sys
from bisect import bisect_left
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    ws = [int(x) for x in input_data[1:n+1]]
    hs = [int(x) for x in input_data[n+1:2*n+1]]
    envs = sorted(zip(ws, hs), key=lambda x: (x[0], -x[1]))
    lis = []
    for w, h in envs:
        idx = bisect_left(lis, h)
        if idx == len(lis):
            lis.append(h)
        else:
            lis[idx] = h
    print(len(lis))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_poor_pigs",
            "title_hint": "Information Theory / Exponential Testing Rounds",
            "logic_desc": "Determine the minimum number of parallel tests needed to figure out which of the N identical-looking items is flawed, given a specific testing window ratio.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "Buckets", "min": 50, "max": 1000}, {"type": "int", "name": "MinutesDie", "min": 10, "max": 20}, {"type": "int", "name": "MinutesTest", "min": 30, "max": 60}],
            "gold_solution": """import sys
import math
def main():
    input_data = sys.stdin.read().split()
    if len(input_data) < 3: return
    buckets = int(input_data[0])
    min_die = int(input_data[1])
    min_test = int(input_data[2])
    states = (min_test // min_die) + 1
    pigs = math.ceil(math.log(buckets) / math.log(states))
    print(pigs)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_super_egg_drop",
            "title_hint": "Stress Horizon / Optimal Drop Trials",
            "logic_desc": "You are given k items and n floors. Find the minimum number of attempts needed with certainty to find the threshold floor from which an item breaks.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "K", "min": 2, "max": 5}, {"type": "int", "name": "N", "min": 10, "max": 10000}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if len(input_data) < 2: return
    k = int(input_data[0])
    n = int(input_data[1])
    dp = [0] * (k + 1)
    m = 0
    while dp[k] < n:
        m += 1
        for i in range(k, 0, -1):
            dp[i] = dp[i] + dp[i-1] + 1
    print(m)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_distinct_subsequences",
            "title_hint": "String Evolution / Structural Replicas",
            "logic_desc": "Given two strings s and t, return the number of distinct subsequences of s which equals t.",
            "difficulty": "Hard",
            "category": "String",
            "input_schema": [{"type": "string", "name": "S", "length": 25}, {"type": "string", "name": "T", "length": 5}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if len(input_data) < 2: return
    s, t = input_data[0], input_data[1]
    dp = [[0] * (len(t) + 1) for _ in range(len(s) + 1)]
    for i in range(len(s) + 1):
        dp[i][0] = 1
    for i in range(1, len(s) + 1):
        for j in range(1, len(t) + 1):
            if s[i - 1] == t[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + dp[i - 1][j]
            else:
                dp[i][j] = dp[i - 1][j]
    print(dp[-1][-1])
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_palindrome_partitioning_ii",
            "title_hint": "Data Slicing / Optimal Palindrome Fragments",
            "logic_desc": "Given a string, partition it such that every substring is a palindrome. Return the minimum cuts needed for a palindrome partitioning of the string.",
            "difficulty": "Hard",
            "category": "String",
            "input_schema": [{"type": "string", "name": "S", "length": 15}],
            "gold_solution": """import sys
def main():
    s = sys.stdin.read().strip()
    if not s: return
    n = len(s)
    dp = list(range(-1, n))
    for i in range(n):
        for j in range(n):
            if i - j < 0 or i + j >= n or s[i - j] != s[i + j]:
                break
            dp[i + j + 1] = min(dp[i + j + 1], dp[i - j] + 1)
        for j in range(1, n):
            if i - j + 1 < 0 or i + j >= n or s[i - j + 1] != s[i + j]:
                break
            dp[i + j + 1] = min(dp[i + j + 1], dp[i - j + 1] + 1)
    print(dp[-1])
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_longest_increasing_path_matrix",
            "title_hint": "Topological Climb / Multi-Directional Gradient",
            "logic_desc": "Given an m x n integers matrix, return the length of the longest strictly increasing path.",
            "difficulty": "Hard",
            "category": "Matrix",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 5}, {"type": "matrix", "rows_ref": "N", "cols_ref": "N", "item": {"type": "int", "min": 1, "max": 20}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    idx = 1
    matrix = []
    for r in range(n):
        row = []
        for c in range(n):
            row.append(int(input_data[idx]))
            idx += 1
        matrix.append(row)
    if not matrix: return
    rows, cols = len(matrix), len(matrix[0])
    dp = {}
    def dfs(r, c, prev):
        if r < 0 or r == rows or c < 0 or c == cols or matrix[r][c] <= prev:
            return 0
        if (r, c) in dp:
            return dp[(r, c)]
        res = 1
        res = max(res, 1 + dfs(r + 1, c, matrix[r][c]))
        res = max(res, 1 + dfs(r - 1, c, matrix[r][c]))
        res = max(res, 1 + dfs(r, c + 1, matrix[r][c]))
        res = max(res, 1 + dfs(r, c - 1, matrix[r][c]))
        dp[(r, c)] = res
        return res
    print(max([dfs(r, c, -1) for r in range(rows) for c in range(cols)]))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_split_array_largest_sum",
            "title_hint": "Load Balancing / Min-Max Allocation",
            "logic_desc": "Given an integer array and an integer m, split the array into m non-empty continuous subarrays such that the largest sum among these subarrays is minimized.",
            "difficulty": "Hard",
            "category": "Math",
            "input_schema": [{"type": "int", "name": "N", "min": 5, "max": 15}, {"type": "int", "name": "M", "min": 2, "max": 4}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 20}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if len(input_data) < 3: return
    n = int(input_data[0])
    m = int(input_data[1])
    nums = [int(x) for x in input_data[2:]]
    def canSplit(largest):
        subarrays, cur_sum = 1, 0
        for num in nums:
            cur_sum += num
            if cur_sum > largest:
                subarrays += 1
                cur_sum = num
        return subarrays <= m
    l, r = max(nums), sum(nums)
    res = r
    while l <= r:
        mid = l + ((r - l) // 2)
        if canSplit(mid):
            res = mid
            r = mid - 1
        else:
            l = mid + 1
    print(res)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_kth_smallest_multiplication_table",
            "title_hint": "Matrix Search / Conceptual Coordinate Thresholding",
            "logic_desc": "Given the height m and the length n of a conceptually evaluated m x n Multiplication Table, and a positive integer k, return the kth smallest number in this table.",
            "difficulty": "Hard",
            "category": "Matrix",
            "input_schema": [{"type": "int", "name": "M", "min": 5, "max": 20}, {"type": "int", "name": "N", "min": 5, "max": 20}, {"type": "int", "name": "K", "min": 5, "max": 100}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if len(input_data) < 3: return
    m = int(input_data[0])
    n = int(input_data[1])
    k = int(input_data[2])
    def enough(x):
        count = 0
        for i in range(1, m + 1):
            count += min(x // i, n)
        return count >= k
    low, high = 1, m * n
    while low < high:
        mid = low + (high - low) // 2
        if enough(mid):
            high = mid
        else:
            low = mid + 1
    print(low)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_find_kth_smallest_pair_distance",
            "title_hint": "Distance Analytics / Pair Delta Indexing",
            "logic_desc": "The distance of a pair of integers a and b is defined as the absolute difference between a and b. Given an integer array and an integer k, return the kth smallest distance among all the pairs.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 5, "max": 25}, {"type": "int", "name": "K", "min": 5, "max": 50}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 50}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if len(input_data) < 3: return
    n = int(input_data[0])
    k = int(input_data[1])
    nums = sorted([int(x) for x in input_data[2:]])
    def count(dist):
        res = 0
        left = 0
        for right in range(len(nums)):
            while nums[right] - nums[left] > dist:
                left += 1
            res += right - left
        return res
    low, high = 0, nums[-1] - nums[0]
    while low < high:
        mid = low + (high - low) // 2
        if count(mid) >= k:
            high = mid
        else:
            low = mid + 1
    print(low)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_minimum_window_substring",
            "title_hint": "Data Slicing / Minimal Containing Signature",
            "logic_desc": "Given two strings s and t, return the minimum window substring of s such that every character in t (including duplicates) is included in the window. Produce NONE if unachievable.",
            "difficulty": "Hard",
            "category": "String",
            "input_schema": [{"type": "string", "name": "S", "length": 30}, {"type": "string", "name": "T", "length": 5}],
            "gold_solution": """import sys
from collections import Counter
def main():
    input_data = sys.stdin.read().split()
    if len(input_data) < 2: return
    s, t = input_data[0], input_data[1]
    if t == "": return
    countT, window = Counter(t), {}
    have, need = 0, len(countT)
    res, resLen = [-1, -1], float("infinity")
    l = 0
    for r in range(len(s)):
        c = s[r]
        window[c] = window.get(c, 0) + 1
        if c in countT and window[c] == countT[c]:
            have += 1
        while have == need:
            if (r - l + 1) < resLen:
                res = [l, r]
                resLen = (r - l + 1)
            window[s[l]] -= 1
            if s[l] in countT and window[s[l]] < countT[s[l]]:
                have -= 1
            l += 1
    l, r = res
    print(s[l:r+1] if resLen != float("infinity") else "NONE")
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_container_most_water",
            "title_hint": "Capacity Optimization / Container Analysis",
            "logic_desc": "Given an array of heights, find two lines that together with the x-axis form a container that holds the most water.",
            "difficulty": "Medium",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 5, "max": 30}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    heights = [int(x) for x in input_data[1:]]
    left, right = 0, n - 1
    max_area = 0
    while left < right:
        width = right - left
        h = min(heights[left], heights[right])
        max_area = max(max_area, width * h)
        if heights[left] < heights[right]:
            left += 1
        else:
            right -= 1
    print(max_area)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_coin_change",
            "title_hint": "Resource Allocation / Minimum Denominations",
            "logic_desc": "Given an amount and an array of available coin denominations, compute the fewest number of coins needed to make up that amount. Output -1 if impossible.",
            "difficulty": "Medium",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "Amount", "min": 10, "max": 50}, {"type": "int", "name": "N", "min": 3, "max": 6}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 10}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if len(input_data) < 3: return
    amount = int(input_data[0])
    n = int(input_data[1])
    coins = [int(x) for x in input_data[2:n+2]]
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for coin in coins:
        for x in range(coin, amount + 1):
            dp[x] = min(dp[x], dp[x - coin] + 1)
    print(dp[amount] if dp[amount] != float('inf') else -1)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_house_robber",
            "title_hint": "Asset Security / Non-Adjacent Maximization",
            "logic_desc": "Determine the maximum sum of elements you can extract from an array without selecting any two adjacent elements.",
            "difficulty": "Medium",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 5, "max": 25}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    nums = [int(x) for x in input_data[1:]]
    if not nums:
        print(0)
        return
    if len(nums) <= 2:
        print(max(nums))
        return
    prev1, prev2 = 0, 0
    for num in nums:
        temp = prev1
        prev1 = max(prev2 + num, prev1)
        prev2 = temp
    print(prev1)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_daily_temperatures",
            "title_hint": "Metric Forecasting / Next Greater Element",
            "logic_desc": "Given an array of daily temperatures, return an array such that the answer at the ith day is the number of days you have to wait to get a warmer temperature.",
            "difficulty": "Medium",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 5, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 30, "max": 100}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    temps = [int(x) for x in input_data[1:]]
    res = [0] * n
    stack = []
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            prev_idx = stack.pop()
            res[prev_idx] = i - prev_idx
        stack.append(i)
    print(" ".join(map(str, res)))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_sort_colors",
            "title_hint": "Data Segregation / Three-Tier Sorting",
            "logic_desc": "Sort an array consisting of exactly three distinct categories (represented as 0, 1, and 2) in-place without using native sort functions.",
            "difficulty": "Medium",
            "category": "Sorting",
            "input_schema": [{"type": "int", "name": "N", "min": 5, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 0, "max": 2}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    nums = [int(x) for x in input_data[1:]]
    low, mid, high = 0, 0, n - 1
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:
            nums[high], nums[mid] = nums[mid], nums[high]
            high -= 1
    print(" ".join(map(str, nums)))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_jump_game",
            "title_hint": "Viable Traversal / Jump Reachability",
            "logic_desc": "Given an integer array where each element represents your maximum jump length at that position, return true if you can reach the last index.",
            "difficulty": "Medium",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 5, "max": 15}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 0, "max": 4}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    nums = [int(x) for x in input_data[1:]]
    farthest = 0
    for i in range(n):
        if i > farthest:
            print("false")
            return
        farthest = max(farthest, i + nums[i])
        if farthest >= n - 1:
            print("true")
            return
    print("true")
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_subarray_sum_equals_k",
            "title_hint": "Running Metrics / Continuous Subarrays",
            "logic_desc": "Given an array of integers and an integer k, return the total number of continuous subarrays whose sum equals to k.",
            "difficulty": "Medium",
            "category": "Math",
            "input_schema": [{"type": "int", "name": "K", "min": 5, "max": 20}, {"type": "int", "name": "N", "min": 5, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": -5, "max": 10}}],
            "gold_solution": """import sys
from collections import defaultdict
def main():
    input_data = sys.stdin.read().split()
    if len(input_data) < 3: return
    k = int(input_data[0])
    n = int(input_data[1])
    nums = [int(x) for x in input_data[2:]]
    count = 0
    current_sum = 0
    prefix_sums = defaultdict(int)
    prefix_sums[0] = 1
    for num in nums:
        current_sum += num
        if (current_sum - k) in prefix_sums:
            count += prefix_sums[current_sum - k]
        prefix_sums[current_sum] += 1
    print(count)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_longest_repeat_char_replacement",
            "title_hint": "Data Healing / Character Replacement",
            "logic_desc": "Given a string and an integer k, you can choose any character and replace it up to k times. Return the length of the longest substring containing the same letter.",
            "difficulty": "Medium",
            "category": "String",
            "input_schema": [{"type": "string", "name": "S", "length": 25}, {"type": "int", "name": "K", "min": 1, "max": 4}],
            "gold_solution": """import sys
from collections import defaultdict
def main():
    input_data = sys.stdin.read().split()
    if len(input_data) < 2: return
    s = input_data[0]
    k = int(input_data[1])
    count = defaultdict(int)
    res = 0
    l = 0
    maxf = 0
    for r in range(len(s)):
        count[s[r]] += 1
        maxf = max(maxf, count[s[r]])
        while (r - l + 1) - maxf > k:
            count[s[l]] -= 1
            l += 1
        res = max(res, r - l + 1)
    print(res)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_gas_station",
            "title_hint": "Supply Loop / Circular Traverse Viability",
            "logic_desc": "Given a circular route containing gas nodes and cost edges, find the starting index that guarantees a full continuous loop completion without reaching negative fuel.",
            "difficulty": "Medium",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 10}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 10}}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 10}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    gas = [int(x) for x in input_data[1:n+1]]
    cost = [int(x) for x in input_data[n+1:2*n+1]]
    if sum(gas) < sum(cost):
        print(-1)
        return
    total = 0
    start = 0
    for i in range(n):
        total += (gas[i] - cost[i])
        if total < 0:
            total = 0
            start = i + 1
    print(start)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_rotate_array",
            "title_hint": "Data Shifting / Array Cycle Operations",
            "logic_desc": "Given an integer array, rotate the array to the right by k steps, natively avoiding out of limits indices.",
            "difficulty": "Medium",
            "category": "Matrix",
            "input_schema": [{"type": "int", "name": "K", "min": 1, "max": 10}, {"type": "int", "name": "N", "min": 5, "max": 15}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if len(input_data) < 3: return
    k = int(input_data[0])
    n = int(input_data[1])
    nums = [int(x) for x in input_data[2:]]
    k = k % n
    if k == 0:
        print(" ".join(map(str, nums)))
        return
    nums.reverse()
    nums[:k] = reversed(nums[:k])
    nums[k:] = reversed(nums[k:])
    print(" ".join(map(str, nums)))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_minimum_path_sum",
            "title_hint": "Grid Routing / Min Path Analysis",
            "logic_desc": "Given a m x n grid filled with non-negative numbers, find a path from top left to bottom right, which minimizes the sum of all numbers along its path. Only move down or right.",
            "difficulty": "Medium",
            "category": "Math",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 5}, {"type": "matrix", "rows_ref": "N", "cols_ref": "N", "item": {"type": "int", "min": 0, "max": 9}}],
            "gold_solution": """import sys
def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    n = int(input_data[0])
    # Read matrix
    idx = 1
    grid = []
    for r in range(n):
        row = []
        for c in range(n):
            row.append(int(input_data[idx]))
            idx += 1
        grid.append(row)
        
    for r in range(n):
        for c in range(n):
            if r == 0 and c == 0: continue
            if r == 0: grid[r][c] += grid[r][c-1]
            elif c == 0: grid[r][c] += grid[r-1][c]
            else: grid[r][c] += min(grid[r-1][c], grid[r][c-1])
            
    print(grid[n-1][n-1])
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_sum_of_digits",
            "title_hint": "Digit Analysis / Digit Sum",
            "logic_desc": "Calculate the sum of all digits of a given positive integer.",
            "difficulty": "Easy",
            "category": "Math",
            "input_schema": [{"type": "int", "name": "N", "min": 1, "max": 9999}],
            "gold_solution": """import sys
def main():
    n = int(sys.stdin.read().strip())
    print(sum(int(d) for d in str(abs(n))))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_fibonacci_nth",
            "title_hint": "Sequence Computation / Fibonacci",
            "logic_desc": "Compute the Nth number in the Fibonacci sequence (0-indexed: F(0)=0, F(1)=1).",
            "difficulty": "Easy",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 0, "max": 30}],
            "gold_solution": """import sys
def main():
    n = int(sys.stdin.read().strip())
    if n <= 1:
        print(n)
        return
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    print(b)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_count_even",
            "title_hint": "Data Filtering / Even Count",
            "logic_desc": "Count the number of even integers in a given array.",
            "difficulty": "Easy",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 1, "max": 30}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n+1]]
    print(sum(1 for x in nums if x % 2 == 0))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_array_sum",
            "title_hint": "Data Aggregation / Array Summation",
            "logic_desc": "Calculate the total sum of all elements in an integer array.",
            "difficulty": "Easy",
            "category": "Math",
            "input_schema": [{"type": "int", "name": "N", "min": 1, "max": 30}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n+1]]
    print(sum(nums))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_second_largest",
            "title_hint": "Ranking Analysis / Second Maximum",
            "logic_desc": "Find the second largest distinct element in an array. If no second distinct element exists, return the maximum.",
            "difficulty": "Easy",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n+1]]
    unique = sorted(set(nums), reverse=True)
    print(unique[1] if len(unique) >= 2 else unique[0])
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_count_unique",
            "title_hint": "Data Deduplication / Distinct Count",
            "logic_desc": "Count the number of distinct (unique) elements in an integer array.",
            "difficulty": "Easy",
            "category": "HashMap",
            "input_schema": [{"type": "int", "name": "N", "min": 5, "max": 30}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 20}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n+1]]
    print(len(set(nums)))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_max_consecutive_ones",
            "title_hint": "Signal Processing / Consecutive Streak",
            "logic_desc": "Find the maximum number of consecutive 1s in a binary array.",
            "difficulty": "Easy",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 5, "max": 30}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 0, "max": 1}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n+1]]
    max_c = cur = 0
    for x in nums:
        if x == 1:
            cur += 1
            max_c = max(max_c, cur)
        else:
            cur = 0
    print(max_c)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_running_sum",
            "title_hint": "Cumulative Metrics / Running Sum",
            "logic_desc": "Compute the running sum of a one-dimensional array, where each element becomes the sum of itself and all preceding elements.",
            "difficulty": "Easy",
            "category": "Math",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 50}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n+1]]
    res = []
    s = 0
    for x in nums:
        s += x
        res.append(s)
    print(" ".join(map(str, res)))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_sorted_squares",
            "title_hint": "Data Transformation / Sorted Squares",
            "logic_desc": "Given an array of integers, return a new array of the squares of each number, sorted in non-decreasing order.",
            "difficulty": "Easy",
            "category": "Sorting",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": -50, "max": 50}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n+1]]
    print(" ".join(map(str, sorted(x*x for x in nums))))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_pascal_row",
            "title_hint": "Combinatorial Generation / Pascal Row",
            "logic_desc": "Generate the Nth row (0-indexed) of Pascal's Triangle.",
            "difficulty": "Easy",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 0, "max": 15}],
            "gold_solution": """import sys
def main():
    n = int(sys.stdin.read().strip())
    row = [1]
    for i in range(1, n + 1):
        row.append(row[-1] * (n - i + 1) // i)
    print(" ".join(map(str, row)))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_count_set_bits",
            "title_hint": "Bitwise Analysis / Popcount",
            "logic_desc": "Count the number of 1-bits in the binary representation of a non-negative integer.",
            "difficulty": "Easy",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 0, "max": 1000}],
            "gold_solution": """import sys
def main():
    n = int(sys.stdin.read().strip())
    print(bin(n).count('1'))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_digital_root",
            "title_hint": "Numeric Reduction / Digital Root",
            "logic_desc": "Repeatedly sum the digits of a non-negative integer until a single digit remains.",
            "difficulty": "Easy",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 0, "max": 9999}],
            "gold_solution": """import sys
def main():
    n = int(sys.stdin.read().strip())
    if n == 0:
        print(0)
    else:
        print(1 + (n - 1) % 9)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_plus_one",
            "title_hint": "Large Number Arithmetic / Increment Digits",
            "logic_desc": "Given a number represented as an array of its digits, increment it by one and return the resulting digit array.",
            "difficulty": "Easy",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 1, "max": 10}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 0, "max": 9}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    digits = [int(x) for x in data[1:n+1]]
    num = int("".join(map(str, digits))) + 1
    print(" ".join(list(str(num))))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_find_pivot_index",
            "title_hint": "Balance Point / Equilibrium Index",
            "logic_desc": "Find the index where the sum of elements to the left equals the sum of elements to the right. Return -1 if no such index exists.",
            "difficulty": "Easy",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 15}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 20}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n+1]]
    total = sum(nums)
    left_sum = 0
    for i in range(n):
        if left_sum == total - left_sum - nums[i]:
            print(i)
            return
        left_sum += nums[i]
    print(-1)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_gcd",
            "title_hint": "Number Theory / Greatest Common Divisor",
            "logic_desc": "Compute the Greatest Common Divisor (GCD) of two positive integers.",
            "difficulty": "Easy",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "A", "min": 1, "max": 500}, {"type": "int", "name": "B", "min": 1, "max": 500}],
            "gold_solution": """import sys
import math
def main():
    data = sys.stdin.read().split()
    a, b = int(data[0]), int(data[1])
    print(math.gcd(a, b))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_hamming_distance",
            "title_hint": "Bitwise Comparison / Hamming Distance",
            "logic_desc": "Calculate the Hamming distance between two integers, which is the number of positions at which the corresponding bits differ.",
            "difficulty": "Easy",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "A", "min": 0, "max": 500}, {"type": "int", "name": "B", "min": 0, "max": 500}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    a, b = int(data[0]), int(data[1])
    print(bin(a ^ b).count('1'))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_count_negatives_array",
            "title_hint": "Data Quality / Negative Count",
            "logic_desc": "Count how many negative numbers exist in a given integer array.",
            "difficulty": "Easy",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 5, "max": 25}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": -50, "max": 50}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n+1]]
    print(sum(1 for x in nums if x < 0))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_matrix_diagonal_sum",
            "title_hint": "Matrix Analysis / Diagonal Sum",
            "logic_desc": "Compute the sum of both diagonals of an N x N matrix. If N is odd, subtract the center element once to avoid double counting.",
            "difficulty": "Easy",
            "category": "Math",
            "input_schema": [{"type": "int", "name": "N", "min": 2, "max": 5}, {"type": "matrix", "rows_ref": "N", "cols_ref": "N", "item": {"type": "int", "min": 1, "max": 9}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    idx = 1
    matrix = []
    for r in range(n):
        row = [int(data[idx + c]) for c in range(n)]
        idx += n
        matrix.append(row)
    total = 0
    for i in range(n):
        total += matrix[i][i]
        total += matrix[i][n - 1 - i]
    if n % 2 == 1:
        total -= matrix[n // 2][n // 2]
    print(total)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_third_maximum",
            "title_hint": "Rank Selection / Third Maximum",
            "logic_desc": "Find the third distinct maximum number in an array. If the third maximum does not exist, return the maximum number.",
            "difficulty": "Easy",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 50}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n+1]]
    unique = sorted(set(nums), reverse=True)
    print(unique[2] if len(unique) >= 3 else unique[0])
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_min_diff_pair",
            "title_hint": "Proximity Analysis / Minimum Pair Difference",
            "logic_desc": "Find the minimum absolute difference between any two elements in an integer array.",
            "difficulty": "Easy",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = sorted(int(x) for x in data[1:n+1])
    min_diff = float('inf')
    for i in range(1, len(nums)):
        min_diff = min(min_diff, nums[i] - nums[i-1])
    print(min_diff)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_is_perfect_square",
            "title_hint": "Numeric Validation / Perfect Square",
            "logic_desc": "Determine if a given non-negative integer is a perfect square.",
            "difficulty": "Easy",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 0, "max": 1000}],
            "gold_solution": """import sys
def main():
    n = int(sys.stdin.read().strip())
    if n < 0:
        print("false")
        return
    r = int(n ** 0.5)
    if r * r == n or (r + 1) * (r + 1) == n:
        print("true")
    else:
        print("false")
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_count_primes",
            "title_hint": "Number Theory / Prime Sieve",
            "logic_desc": "Count the number of prime numbers strictly less than a given integer N.",
            "difficulty": "Easy",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 2, "max": 100}],
            "gold_solution": """import sys
def main():
    n = int(sys.stdin.read().strip())
    if n < 2:
        print(0)
        return
    sieve = [True] * n
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n, i):
                sieve[j] = False
    print(sum(sieve))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_reverse_array",
            "title_hint": "Data Reordering / Array Reversal",
            "logic_desc": "Reverse the order of elements in an integer array.",
            "difficulty": "Easy",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n+1]]
    print(" ".join(map(str, nums[::-1])))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_sum_multiples",
            "title_hint": "Divisibility Check / Sum of Multiples",
            "logic_desc": "Find the sum of all natural numbers below N that are multiples of 3 or 5.",
            "difficulty": "Easy",
            "category": "Math",
            "input_schema": [{"type": "int", "name": "N", "min": 1, "max": 100}],
            "gold_solution": """import sys
def main():
    n = int(sys.stdin.read().strip())
    print(sum(i for i in range(n) if i % 3 == 0 or i % 5 == 0))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_kth_smallest",
            "title_hint": "Order Statistics / Kth Smallest",
            "logic_desc": "Find the Kth smallest element in an unsorted integer array.",
            "difficulty": "Easy",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "K", "min": 1, "max": 5}, {"type": "int", "name": "N", "min": 5, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    k = int(data[0])
    n = int(data[1])
    nums = sorted(int(x) for x in data[2:n+2])
    print(nums[min(k - 1, len(nums) - 1)])
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_array_product_mod",
            "title_hint": "Modular Arithmetic / Product Modulo",
            "logic_desc": "Compute the product of all elements in an array modulo 1000000007.",
            "difficulty": "Easy",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 1, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n+1]]
    result = 1
    MOD = 1000000007
    for x in nums:
        result = (result * x) % MOD
    print(result)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_merge_two_sorted",
            "title_hint": "Data Merging / Merge Sorted Arrays",
            "logic_desc": "Merge two sorted integer arrays into a single sorted array.",
            "difficulty": "Easy",
            "category": "Sorting",
            "input_schema": [{"type": "int", "name": "N", "min": 2, "max": 10}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 50}}, {"type": "int", "name": "M", "min": 2, "max": 10}, {"type": "array", "count_ref": "M", "item": {"type": "int", "min": 1, "max": 50}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    arr1 = sorted(int(x) for x in data[1:n+1])
    m = int(data[n+1])
    arr2 = sorted(int(x) for x in data[n+2:n+2+m])
    merged = sorted(arr1 + arr2)
    print(" ".join(map(str, merged)))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_max_min_difference",
            "title_hint": "Range Analysis / Max Min Spread",
            "logic_desc": "Compute the difference between the maximum and minimum elements in an integer array.",
            "difficulty": "Easy",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n+1]]
    print(max(nums) - min(nums))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_count_pairs_with_sum",
            "title_hint": "Pair Analysis / Count Sum Pairs",
            "logic_desc": "Count the number of distinct index pairs (i, j) where i < j and nums[i] + nums[j] equals a given target.",
            "difficulty": "Easy",
            "category": "Math",
            "input_schema": [{"type": "int", "name": "Target", "min": 5, "max": 50}, {"type": "int", "name": "N", "min": 5, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 30}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    target = int(data[0])
    n = int(data[1])
    nums = [int(x) for x in data[2:n+2]]
    count = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                count += 1
    print(count)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_array_leaders",
            "title_hint": "Element Dominance / Array Leaders",
            "logic_desc": "Count the number of leader elements in an array. An element is a leader if it is greater than or equal to all elements to its right.",
            "difficulty": "Easy",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n+1]]
    count = 0
    max_from_right = float('-inf')
    for i in range(len(nums) - 1, -1, -1):
        if nums[i] >= max_from_right:
            count += 1
            max_from_right = nums[i]
    print(count)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_three_sum_closest",
            "title_hint": "Triplet Optimization / Three Sum Closest",
            "logic_desc": "Given an array of integers and a target value, find three integers whose sum is closest to the target. Return the closest sum.",
            "difficulty": "Medium",
            "category": "Math",
            "input_schema": [{"type": "int", "name": "Target", "min": 10, "max": 50}, {"type": "int", "name": "N", "min": 5, "max": 15}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": -20, "max": 20}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    target = int(data[0])
    n = int(data[1])
    nums = sorted(int(x) for x in data[2:n+2])
    closest = float('inf')
    for i in range(n - 2):
        lo, hi = i + 1, n - 1
        while lo < hi:
            s = nums[i] + nums[lo] + nums[hi]
            if abs(s - target) < abs(closest - target):
                closest = s
            if s < target:
                lo += 1
            elif s > target:
                hi -= 1
            else:
                print(target)
                return
    print(closest)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_spiral_matrix_read",
            "title_hint": "Grid Traversal / Spiral Order",
            "logic_desc": "Traverse an N x N matrix in spiral order (right, down, left, up) and output all elements.",
            "difficulty": "Medium",
            "category": "Matrix",
            "input_schema": [{"type": "int", "name": "N", "min": 2, "max": 5}, {"type": "matrix", "rows_ref": "N", "cols_ref": "N", "item": {"type": "int", "min": 1, "max": 99}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    idx = 1
    matrix = []
    for r in range(n):
        row = [int(data[idx + c]) for c in range(n)]
        idx += n
        matrix.append(row)
    res = []
    top, bottom, left, right = 0, n - 1, 0, n - 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            res.append(matrix[top][c])
        top += 1
        for r in range(top, bottom + 1):
            res.append(matrix[r][right])
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                res.append(matrix[bottom][c])
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                res.append(matrix[r][left])
            left += 1
    print(" ".join(map(str, res)))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_longest_palindrome_length",
            "title_hint": "String Analysis / Palindrome Length",
            "logic_desc": "Find the length of the longest palindromic substring in a given string.",
            "difficulty": "Medium",
            "category": "String",
            "input_schema": [{"type": "string", "name": "S", "length": 20}],
            "gold_solution": """import sys
def main():
    s = sys.stdin.read().strip()
    if not s:
        print(0)
        return
    n = len(s)
    max_len = 1
    for i in range(n):
        l, r = i, i
        while l >= 0 and r < n and s[l] == s[r]:
            max_len = max(max_len, r - l + 1)
            l -= 1
            r += 1
        l, r = i, i + 1
        while l >= 0 and r < n and s[l] == s[r]:
            max_len = max(max_len, r - l + 1)
            l -= 1
            r += 1
    print(max_len)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_kth_largest",
            "title_hint": "Order Statistics / Kth Largest Element",
            "logic_desc": "Find the Kth largest element in an unsorted integer array.",
            "difficulty": "Medium",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "K", "min": 1, "max": 5}, {"type": "int", "name": "N", "min": 5, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    k = int(data[0])
    n = int(data[1])
    nums = sorted([int(x) for x in data[2:n+2]], reverse=True)
    print(nums[min(k - 1, len(nums) - 1)])
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_top_k_frequent",
            "title_hint": "Frequency Ranking / Top K Elements",
            "logic_desc": "Given an integer array and an integer K, return the K most frequent elements sorted in ascending order.",
            "difficulty": "Medium",
            "category": "Sorting",
            "input_schema": [{"type": "int", "name": "K", "min": 1, "max": 3}, {"type": "int", "name": "N", "min": 5, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 10}}],
            "gold_solution": """import sys
from collections import Counter
def main():
    data = sys.stdin.read().split()
    k = int(data[0])
    n = int(data[1])
    nums = [int(x) for x in data[2:n+2]]
    counts = Counter(nums)
    top_k = sorted(counts.keys(), key=lambda x: -counts[x])[:k]
    print(" ".join(map(str, sorted(top_k))))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_unique_paths_grid",
            "title_hint": "Grid Navigation / Unique Paths",
            "logic_desc": "Count the number of unique paths from the top-left corner to the bottom-right corner of an M x N grid, moving only right or down.",
            "difficulty": "Medium",
            "category": "HashMap",
            "input_schema": [{"type": "int", "name": "M", "min": 1, "max": 10}, {"type": "int", "name": "N", "min": 1, "max": 10}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    m, n = int(data[0]), int(data[1])
    dp = [1] * n
    for i in range(1, m):
        for j in range(1, n):
            dp[j] += dp[j - 1]
    print(dp[n - 1])
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_lis_length",
            "title_hint": "Subsequence Analysis / Longest Increasing",
            "logic_desc": "Find the length of the longest strictly increasing subsequence in an integer array.",
            "difficulty": "Medium",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 5, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
from bisect import bisect_left
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n+1]]
    tails = []
    for x in nums:
        pos = bisect_left(tails, x)
        if pos == len(tails):
            tails.append(x)
        else:
            tails[pos] = x
    print(len(tails))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_max_product_subarray",
            "title_hint": "Value Optimization / Maximum Product Subarray",
            "logic_desc": "Find the contiguous subarray within an array of integers that has the largest product.",
            "difficulty": "Medium",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 15}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": -5, "max": 5}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n+1]]
    if not nums:
        print(0)
        return
    max_p = min_p = result = nums[0]
    for i in range(1, len(nums)):
        if nums[i] < 0:
            max_p, min_p = min_p, max_p
        max_p = max(nums[i], max_p * nums[i])
        min_p = min(nums[i], min_p * nums[i])
        result = max(result, max_p)
    print(result)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_find_peak",
            "title_hint": "Signal Detection / Peak Element",
            "logic_desc": "Find the index of a peak element in an array. A peak element is one that is strictly greater than its neighbors.",
            "difficulty": "Medium",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 15}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n+1]]
    lo, hi = 0, n - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < nums[mid + 1]:
            lo = mid + 1
        else:
            hi = mid
    print(lo)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_count_inversions",
            "title_hint": "Array Disorder / Inversion Count",
            "logic_desc": "Count the number of inversions in an array: the number of pairs (i, j) where i < j but nums[i] > nums[j].",
            "difficulty": "Medium",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 15}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 50}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n+1]]
    count = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] > nums[j]:
                count += 1
    print(count)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_next_permutation",
            "title_hint": "Combinatorial Sequencing / Next Permutation",
            "logic_desc": "Rearrange the given array of numbers into the lexicographically next greater permutation. If no such permutation exists, return the lowest possible order.",
            "difficulty": "Medium",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 10}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 9}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n+1]]
    i = len(nums) - 2
    while i >= 0 and nums[i] >= nums[i + 1]:
        i -= 1
    if i >= 0:
        j = len(nums) - 1
        while nums[j] <= nums[i]:
            j -= 1
        nums[i], nums[j] = nums[j], nums[i]
    nums[i + 1:] = nums[i + 1:][::-1]
    print(" ".join(map(str, nums)))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_count_islands",
            "title_hint": "Graph Connectivity / Island Count",
            "logic_desc": "Given an N x N binary matrix where 1 represents land and 0 represents water, count the number of connected islands (groups of adjacent 1s).",
            "difficulty": "Medium",
            "category": "Graphs",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 5}, {"type": "matrix", "rows_ref": "N", "cols_ref": "N", "item": {"type": "int", "min": 0, "max": 1}}],
            "gold_solution": """import sys
sys.setrecursionlimit(10000)
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    idx = 1
    grid = []
    for r in range(n):
        row = [int(data[idx + c]) for c in range(n)]
        idx += n
        grid.append(row)
    def dfs(r, c):
        if r < 0 or r >= n or c < 0 or c >= n or grid[r][c] != 1:
            return
        grid[r][c] = 0
        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)
    count = 0
    for r in range(n):
        for c in range(n):
            if grid[r][c] == 1:
                dfs(r, c)
                count += 1
    print(count)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_stock_cooldown",
            "title_hint": "Trading Strategy / Stock With Cooldown",
            "logic_desc": "Find the maximum profit from stock prices where after selling you must wait one day before buying again.",
            "difficulty": "Medium",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    prices = [int(x) for x in data[1:n+1]]
    if n <= 1:
        print(0)
        return
    hold = -prices[0]
    sold = 0
    rest = 0
    for i in range(1, n):
        prev_hold, prev_sold, prev_rest = hold, sold, rest
        hold = max(prev_hold, prev_rest - prices[i])
        sold = prev_hold + prices[i]
        rest = max(prev_rest, prev_sold)
    print(max(sold, rest))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_lcs_length",
            "title_hint": "Sequence Alignment / Longest Common Subsequence",
            "logic_desc": "Find the length of the longest common subsequence between two strings.",
            "difficulty": "Medium",
            "category": "Array",
            "input_schema": [{"type": "string", "name": "S1", "length": 10}, {"type": "string", "name": "S2", "length": 10}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    if len(data) < 2:
        print(0)
        return
    s1, s2 = data[0], data[1]
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    print(dp[m][n])
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_min_cost_stairs",
            "title_hint": "Cost Optimization / Minimum Cost Climbing",
            "logic_desc": "Given an array of costs where cost[i] is the cost of stepping on the ith stair, find the minimum cost to reach the top. You can start from step 0 or step 1, and climb 1 or 2 steps at a time.",
            "difficulty": "Medium",
            "category": "Math",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    cost = [int(x) for x in data[1:n+1]]
    if n <= 1:
        print(0)
        return
    a, b = cost[0], cost[1]
    for i in range(2, n):
        a, b = b, cost[i] + min(a, b)
    print(min(a, b))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_circular_subarray_sum",
            "title_hint": "Circular Analysis / Max Circular Subarray Sum",
            "logic_desc": "Find the maximum sum of a subarray in a circular integer array.",
            "difficulty": "Medium",
            "category": "Math",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 15}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": -20, "max": 20}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n+1]]
    total = sum(nums)
    max_kadane = cur_max = nums[0]
    min_kadane = cur_min = nums[0]
    for i in range(1, n):
        cur_max = max(nums[i], cur_max + nums[i])
        max_kadane = max(max_kadane, cur_max)
        cur_min = min(nums[i], cur_min + nums[i])
        min_kadane = min(min_kadane, cur_min)
    if max_kadane < 0:
        print(max_kadane)
    else:
        print(max(max_kadane, total - min_kadane))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_min_size_subarray_sum",
            "title_hint": "Window Optimization / Minimum Length Subarray",
            "logic_desc": "Given a target sum and an array of positive integers, find the minimum length of a contiguous subarray whose sum is at least the target. Return 0 if no such subarray exists.",
            "difficulty": "Medium",
            "category": "Math",
            "input_schema": [{"type": "int", "name": "Target", "min": 5, "max": 30}, {"type": "int", "name": "N", "min": 5, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 10}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    target = int(data[0])
    n = int(data[1])
    nums = [int(x) for x in data[2:n+2]]
    left = 0
    cur_sum = 0
    min_len = float('inf')
    for right in range(n):
        cur_sum += nums[right]
        while cur_sum >= target:
            min_len = min(min_len, right - left + 1)
            cur_sum -= nums[left]
            left += 1
    print(min_len if min_len != float('inf') else 0)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_wiggle_subsequence",
            "title_hint": "Pattern Detection / Wiggle Subsequence",
            "logic_desc": "Find the length of the longest wiggle subsequence, where differences between successive numbers strictly alternate between positive and negative.",
            "difficulty": "Medium",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n+1]]
    if n < 2:
        print(n)
        return
    up = down = 1
    for i in range(1, n):
        if nums[i] > nums[i - 1]:
            up = down + 1
        elif nums[i] < nums[i - 1]:
            down = up + 1
    print(max(up, down))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_combination_sum_count",
            "title_hint": "Resource Allocation / Combination Sum Count",
            "logic_desc": "Given an amount and an array of coin denominations, count the number of distinct combinations that sum up to the given amount.",
            "difficulty": "Medium",
            "category": "Math",
            "input_schema": [{"type": "int", "name": "Amount", "min": 5, "max": 30}, {"type": "int", "name": "N", "min": 2, "max": 5}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 10}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    amount = int(data[0])
    n = int(data[1])
    coins = [int(x) for x in data[2:n+2]]
    dp = [0] * (amount + 1)
    dp[0] = 1
    for coin in coins:
        for x in range(coin, amount + 1):
            dp[x] += dp[x - coin]
    print(dp[amount])
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_trailing_zeros_factorial",
            "title_hint": "Mathematical Analysis / Factorial Trailing Zeros",
            "logic_desc": "Count the number of trailing zeros in the factorial of a given integer N.",
            "difficulty": "Medium",
            "category": "Math",
            "input_schema": [{"type": "int", "name": "N", "min": 1, "max": 100}],
            "gold_solution": """import sys
def main():
    n = int(sys.stdin.read().strip())
    count = 0
    while n >= 5:
        n //= 5
        count += n
    print(count)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_matrix_transpose",
            "title_hint": "Grid Transformation / Matrix Transpose",
            "logic_desc": "Compute the transpose of an N x N matrix by swapping rows and columns.",
            "difficulty": "Medium",
            "category": "Matrix",
            "input_schema": [{"type": "int", "name": "N", "min": 2, "max": 5}, {"type": "matrix", "rows_ref": "N", "cols_ref": "N", "item": {"type": "int", "min": 1, "max": 99}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    idx = 1
    matrix = []
    for r in range(n):
        row = [int(data[idx + c]) for c in range(n)]
        idx += n
        matrix.append(row)
    for c in range(n):
        print(" ".join(str(matrix[r][c]) for r in range(n)))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_knapsack_01",
            "title_hint": "Resource Optimization / 0-1 Knapsack",
            "logic_desc": "Given N items with weights and values and a knapsack capacity W, determine the maximum total value achievable without exceeding the weight capacity. Each item can be used at most once.",
            "difficulty": "Medium",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "W", "min": 5, "max": 30}, {"type": "int", "name": "N", "min": 3, "max": 8}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 10}}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 15}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    W = int(data[0])
    n = int(data[1])
    weights = [int(x) for x in data[2:n+2]]
    values = [int(x) for x in data[n+2:2*n+2]]
    dp = [0] * (W + 1)
    for i in range(n):
        for w in range(W, weights[i] - 1, -1):
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    print(dp[W])
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_house_robber_circular",
            "title_hint": "Cyclic Optimization / Circular Non-Adjacent Sum",
            "logic_desc": "Determine the maximum sum of elements you can extract from a circular array without selecting any two adjacent elements.",
            "difficulty": "Medium",
            "category": "Math",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n+1]]
    if n == 1:
        print(nums[0])
        return
    def rob_linear(arr):
        prev1, prev2 = 0, 0
        for x in arr:
            prev1, prev2 = max(prev2 + x, prev1), prev1
        return prev1
    print(max(rob_linear(nums[:-1]), rob_linear(nums[1:])))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_count_palindromic_substrings",
            "title_hint": "String Analysis / Palindromic Substrings Count",
            "logic_desc": "Count the total number of palindromic substrings in a given string.",
            "difficulty": "Medium",
            "category": "String",
            "input_schema": [{"type": "string", "name": "S", "length": 20}],
            "gold_solution": """import sys
def main():
    s = sys.stdin.read().strip()
    if not s:
        print(0)
        return
    n = len(s)
    count = 0
    for i in range(n):
        l, r = i, i
        while l >= 0 and r < n and s[l] == s[r]:
            count += 1
            l -= 1
            r += 1
        l, r = i, i + 1
        while l >= 0 and r < n and s[l] == s[r]:
            count += 1
            l -= 1
            r += 1
    print(count)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_max_width_ramp",
            "title_hint": "Index Analysis / Maximum Width Ramp",
            "logic_desc": "Find the maximum difference j - i such that i < j and nums[i] <= nums[j]. Return 0 if no such pair exists.",
            "difficulty": "Medium",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n+1]]
    stack = []
    for i in range(n):
        if not stack or nums[stack[-1]] > nums[i]:
            stack.append(i)
    res = 0
    for j in range(n - 1, -1, -1):
        while stack and nums[stack[-1]] <= nums[j]:
            res = max(res, j - stack.pop())
    print(res)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_minimum_platforms",
            "title_hint": "Scheduling Optimization / Minimum Platforms",
            "logic_desc": "Given arrival and departure times as integer arrays, find the minimum number of platforms required so that no train waits.",
            "difficulty": "Medium",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 10}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 100, "max": 500}}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 500, "max": 999}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    arrivals = sorted(int(x) for x in data[1:n+1])
    departures = sorted(int(x) for x in data[n+1:2*n+1])
    platforms = max_platforms = 0
    i = j = 0
    while i < n and j < n:
        if arrivals[i] <= departures[j]:
            platforms += 1
            max_platforms = max(max_platforms, platforms)
            i += 1
        else:
            platforms -= 1
            j += 1
    print(max_platforms)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_decode_ways",
            "title_hint": "String Decoding / Message Interpretation Count",
            "logic_desc": "Given a string of digits where A=1, B=2, ..., Z=26, count the total number of ways to decode the string.",
            "difficulty": "Medium",
            "category": "String",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 10}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 2}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    digits = [int(x) for x in data[1:n+1]]
    s = "".join(map(str, digits))
    if not s or s[0] == '0':
        print(0)
        return
    dp = [0] * (len(s) + 1)
    dp[0] = 1
    dp[1] = 1
    for i in range(2, len(s) + 1):
        if s[i - 1] != '0':
            dp[i] += dp[i - 1]
        two_digit = int(s[i - 2:i])
        if 10 <= two_digit <= 26:
            dp[i] += dp[i - 2]
    print(dp[len(s)])
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_max_area_island",
            "title_hint": "Graph Exploration / Maximum Island Area",
            "logic_desc": "Given an N x N binary grid, find the area (number of cells) of the largest island (connected group of 1s).",
            "difficulty": "Medium",
            "category": "Graphs",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 5}, {"type": "matrix", "rows_ref": "N", "cols_ref": "N", "item": {"type": "int", "min": 0, "max": 1}}],
            "gold_solution": """import sys
sys.setrecursionlimit(10000)
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    idx = 1
    grid = []
    for r in range(n):
        row = [int(data[idx + c]) for c in range(n)]
        idx += n
        grid.append(row)
    def dfs(r, c):
        if r < 0 or r >= n or c < 0 or c >= n or grid[r][c] != 1:
            return 0
        grid[r][c] = 0
        return 1 + dfs(r+1,c) + dfs(r-1,c) + dfs(r,c+1) + dfs(r,c-1)
    max_area = 0
    for r in range(n):
        for c in range(n):
            if grid[r][c] == 1:
                max_area = max(max_area, dfs(r, c))
    print(max_area)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_maximal_rectangle",
            "title_hint": "Geometric Optimization / Maximal Rectangle",
            "logic_desc": "Given an N x N binary matrix filled with 0s and 1s, find the area of the largest rectangle containing only 1s.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 5}, {"type": "matrix", "rows_ref": "N", "cols_ref": "N", "item": {"type": "int", "min": 0, "max": 1}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    idx = 1
    matrix = []
    for r in range(n):
        row = [int(data[idx + c]) for c in range(n)]
        idx += n
        matrix.append(row)
    def largestRectangleArea(heights):
        stack = []
        max_area = 0
        heights.append(0)
        for i, h in enumerate(heights):
            start = i
            while stack and stack[-1][1] > h:
                index, height = stack.pop()
                max_area = max(max_area, height * (i - index))
                start = index
            stack.append((start, h))
        return max_area
    heights = [0] * n
    max_area = 0
    for r in range(n):
        for c in range(n):
            heights[c] = heights[c] + 1 if matrix[r][c] == 1 else 0
        max_area = max(max_area, largestRectangleArea(heights[:]))
    print(max_area)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_n_queens_count",
            "title_hint": "Constraint Satisfaction / N-Queens Solutions",
            "logic_desc": "Count the number of distinct solutions to the N-Queens puzzle, where N queens must be placed on an N x N chessboard such that no two queens threaten each other.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 4, "max": 9}],
            "gold_solution": """import sys
def main():
    n = int(sys.stdin.read().strip())
    count = 0
    cols = set()
    diag1 = set()
    diag2 = set()
    def backtrack(row):
        nonlocal count
        if row == n:
            count += 1
            return
        for col in range(n):
            if col in cols or (row - col) in diag1 or (row + col) in diag2:
                continue
            cols.add(col)
            diag1.add(row - col)
            diag2.add(row + col)
            backtrack(row + 1)
            cols.remove(col)
            diag1.remove(row - col)
            diag2.remove(row + col)
    backtrack(0)
    print(count)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_longest_valid_parentheses",
            "title_hint": "Syntax Validation / Longest Valid Bracket Sequence",
            "logic_desc": "Given a string containing only '(' and ')' characters, find the length of the longest valid (well-formed) parentheses substring.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "string", "name": "S", "length": 20}],
            "gold_solution": """import sys
def main():
    s = sys.stdin.read().strip()
    if not s:
        print(0)
        return
    stack = [-1]
    max_len = 0
    for i, c in enumerate(s):
        if c == '(':
            stack.append(i)
        else:
            stack.pop()
            if not stack:
                stack.append(i)
            else:
                max_len = max(max_len, i - stack[-1])
    print(max_len)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_median_two_sorted",
            "title_hint": "Statistical Analysis / Median of Sorted Arrays",
            "logic_desc": "Given two sorted integer arrays, find the median of the two combined sorted arrays.",
            "difficulty": "Hard",
            "category": "Sorting",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 10}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 50}}, {"type": "int", "name": "M", "min": 3, "max": 10}, {"type": "array", "count_ref": "M", "item": {"type": "int", "min": 1, "max": 50}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    arr1 = sorted(int(x) for x in data[1:n+1])
    m = int(data[n+1])
    arr2 = sorted(int(x) for x in data[n+2:n+2+m])
    merged = sorted(arr1 + arr2)
    total = len(merged)
    if total % 2 == 1:
        print(merged[total // 2])
    else:
        mid = total // 2
        val = (merged[mid - 1] + merged[mid]) / 2
        print(int(val) if val == int(val) else val)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_wildcard_matching",
            "title_hint": "Pattern Evaluation / Wildcard Matching",
            "logic_desc": "Implement wildcard pattern matching with support for '?' (matches any single character) and '*' (matches any sequence of characters including empty).",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "string", "name": "s", "length": 10}, {"type": "string", "name": "p", "length": 8}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    if len(data) < 2:
        print("false")
        return
    s, p = data[0], data[1]
    m, n = len(s), len(p)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    for j in range(1, n + 1):
        if p[j - 1] == '*':
            dp[0][j] = dp[0][j - 1]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if p[j - 1] == '*':
                dp[i][j] = dp[i - 1][j] or dp[i][j - 1]
            elif p[j - 1] == '?' or s[i - 1] == p[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
    print("true" if dp[m][n] else "false")
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_max_profit_k_transactions",
            "title_hint": "Financial Engineering / K Transaction Profit",
            "logic_desc": "Find the maximum profit from an array of daily prices where you may complete at most K transactions.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "K", "min": 1, "max": 3}, {"type": "int", "name": "N", "min": 5, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    k = int(data[0])
    n = int(data[1])
    prices = [int(x) for x in data[2:n+2]]
    if n <= 1:
        print(0)
        return
    if k >= n // 2:
        profit = sum(max(0, prices[i] - prices[i-1]) for i in range(1, n))
        print(profit)
        return
    dp = [[0] * n for _ in range(k + 1)]
    for i in range(1, k + 1):
        max_diff = -prices[0]
        for j in range(1, n):
            dp[i][j] = max(dp[i][j-1], prices[j] + max_diff)
            max_diff = max(max_diff, dp[i-1][j] - prices[j])
    print(dp[k][n-1])
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_longest_substr_k_distinct",
            "title_hint": "Data Windowing / K Distinct Characters",
            "logic_desc": "Given a string and an integer K, find the length of the longest substring that contains at most K distinct characters.",
            "difficulty": "Hard",
            "category": "String",
            "input_schema": [{"type": "string", "name": "S", "length": 25}, {"type": "int", "name": "K", "min": 1, "max": 5}],
            "gold_solution": """import sys
from collections import defaultdict
def main():
    data = sys.stdin.read().split()
    if len(data) < 2:
        print(0)
        return
    s = data[0]
    k = int(data[1])
    window = defaultdict(int)
    left = 0
    max_len = 0
    for right in range(len(s)):
        window[s[right]] += 1
        while len(window) > k:
            window[s[left]] -= 1
            if window[s[left]] == 0:
                del window[s[left]]
            left += 1
        max_len = max(max_len, right - left + 1)
    print(max_len)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_interleaving_string",
            "title_hint": "Sequence Composition / Interleaving Validation",
            "logic_desc": "Given three strings s1, s2, and s3, determine whether s3 is formed by an interleaving of s1 and s2.",
            "difficulty": "Hard",
            "category": "String",
            "input_schema": [{"type": "string", "name": "s1", "length": 8}, {"type": "string", "name": "s2", "length": 8}, {"type": "string", "name": "s3", "length": 16}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    if len(data) < 3:
        print("false")
        return
    s1, s2, s3 = data[0], data[1], data[2]
    m, n = len(s1), len(s2)
    if m + n != len(s3):
        print("false")
        return
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    for i in range(1, m + 1):
        dp[i][0] = dp[i-1][0] and s1[i-1] == s3[i-1]
    for j in range(1, n + 1):
        dp[0][j] = dp[0][j-1] and s2[j-1] == s3[j-1]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = (dp[i-1][j] and s1[i-1] == s3[i+j-1]) or (dp[i][j-1] and s2[j-1] == s3[i+j-1])
    print("true" if dp[m][n] else "false")
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_longest_palindrome_subseq",
            "title_hint": "Sequence Alignment / Longest Palindromic Subsequence",
            "logic_desc": "Find the length of the longest palindromic subsequence in a given string.",
            "difficulty": "Hard",
            "category": "String",
            "input_schema": [{"type": "string", "name": "S", "length": 20}],
            "gold_solution": """import sys
def main():
    s = sys.stdin.read().strip()
    if not s:
        print(0)
        return
    n = len(s)
    dp = [[0] * n for _ in range(n)]
    for i in range(n):
        dp[i][i] = 1
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j]:
                dp[i][j] = dp[i+1][j-1] + 2
            else:
                dp[i][j] = max(dp[i+1][j], dp[i][j-1])
    print(dp[0][n-1])
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_min_insertions_palindrome",
            "title_hint": "String Engineering / Minimum Palindrome Insertions",
            "logic_desc": "Find the minimum number of character insertions needed to make a given string a palindrome.",
            "difficulty": "Hard",
            "category": "String",
            "input_schema": [{"type": "string", "name": "S", "length": 20}],
            "gold_solution": """import sys
def main():
    s = sys.stdin.read().strip()
    if not s:
        print(0)
        return
    n = len(s)
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j]:
                dp[i][j] = dp[i+1][j-1]
            else:
                dp[i][j] = min(dp[i+1][j], dp[i][j-1]) + 1
    print(dp[0][n-1])
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_max_sum_increasing_subseq",
            "title_hint": "Value Optimization / Max Sum Increasing Subsequence",
            "logic_desc": "Find the maximum sum of a subsequence such that the elements are in strictly increasing order.",
            "difficulty": "Hard",
            "category": "Math",
            "input_schema": [{"type": "int", "name": "N", "min": 5, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n+1]]
    dp = nums[:]
    for i in range(1, n):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + nums[i])
    print(max(dp))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_arithmetic_slices_count",
            "title_hint": "Pattern Analytics / Arithmetic Subsequence Count",
            "logic_desc": "Count the number of arithmetic slices (subarrays of length >= 3 with equal consecutive differences) in an integer array.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 5, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 50}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n+1]]
    total = 0
    curr = 0
    for i in range(2, n):
        if nums[i] - nums[i-1] == nums[i-1] - nums[i-2]:
            curr += 1
            total += curr
        else:
            curr = 0
    print(total)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_min_refueling_stops",
            "title_hint": "Route Planning / Minimum Refueling Stops",
            "logic_desc": "A vehicle starts with a given fuel capacity and must reach a target distance. Given fuel stations at various positions with fuel amounts, find the minimum number of refueling stops needed. Return -1 if impossible.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "Target", "min": 50, "max": 200}, {"type": "int", "name": "StartFuel", "min": 10, "max": 50}, {"type": "int", "name": "N", "min": 3, "max": 8}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 10, "max": 100}}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 5, "max": 50}}],
            "gold_solution": """import sys
import heapq
def main():
    data = sys.stdin.read().split()
    target = int(data[0])
    start_fuel = int(data[1])
    n = int(data[2])
    positions = sorted(int(x) for x in data[3:n+3])
    fuels = [int(x) for x in data[n+3:2*n+3]]
    stations = sorted(zip(positions, fuels))
    fuel = start_fuel
    stops = 0
    heap = []
    prev = 0
    for pos, f in stations:
        fuel -= (pos - prev)
        while heap and fuel < 0:
            fuel += -heapq.heappop(heap)
            stops += 1
        if fuel < 0:
            print(-1)
            return
        heapq.heappush(heap, -f)
        prev = pos
    fuel -= (target - prev)
    while heap and fuel < 0:
        fuel += -heapq.heappop(heap)
        stops += 1
    print(stops if fuel >= 0 else -1)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_stone_game",
            "title_hint": "Game Theory / Stone Game Strategy",
            "logic_desc": "Two players take turns picking stones from either end of a row. Each player plays optimally. Return the maximum score difference (Player 1 score - Player 2 score).",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 4, "max": 12}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 20}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    piles = [int(x) for x in data[1:n+1]]
    dp = [[0] * n for _ in range(n)]
    for i in range(n):
        dp[i][i] = piles[i]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = max(piles[i] - dp[i+1][j], piles[j] - dp[i][j-1])
    print(dp[0][n-1])
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_dungeon_game",
            "title_hint": "Survival Planning / Dungeon Minimum Health",
            "logic_desc": "Given an N x N grid where each cell contains an integer (positive heals, negative damages), find the minimum initial health needed to go from top-left to bottom-right moving only right or down, keeping health above 0 at all times.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 2, "max": 5}, {"type": "matrix", "rows_ref": "N", "cols_ref": "N", "item": {"type": "int", "min": -20, "max": 10}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    idx = 1
    grid = []
    for r in range(n):
        row = [int(data[idx + c]) for c in range(n)]
        idx += n
        grid.append(row)
    dp = [[float('inf')] * (n + 1) for _ in range(n + 1)]
    dp[n-1][n] = dp[n][n-1] = 1
    for i in range(n - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            need = min(dp[i+1][j], dp[i][j+1]) - grid[i][j]
            dp[i][j] = max(need, 1)
    print(dp[0][0])
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_best_time_stock_iii",
            "title_hint": "Financial Analytics / Two Transaction Profit",
            "logic_desc": "Find the maximum profit from an array of daily prices with at most two buy-sell transactions.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 5, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    prices = [int(x) for x in data[1:n+1]]
    if n <= 1:
        print(0)
        return
    buy1 = buy2 = float('inf')
    profit1 = profit2 = 0
    for p in prices:
        buy1 = min(buy1, p)
        profit1 = max(profit1, p - buy1)
        buy2 = min(buy2, p - profit1)
        profit2 = max(profit2, p - buy2)
    print(profit2)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_maximum_gap",
            "title_hint": "Distribution Analysis / Maximum Successive Gap",
            "logic_desc": "Given an unsorted array, find the maximum difference between successive elements in its sorted form. Return 0 if the array has fewer than 2 elements.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 500}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n+1]]
    if n < 2:
        print(0)
        return
    nums.sort()
    max_gap = 0
    for i in range(1, len(nums)):
        max_gap = max(max_gap, nums[i] - nums[i-1])
    print(max_gap)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_nth_ugly_number",
            "title_hint": "Number Generation / Nth Ugly Number",
            "logic_desc": "Find the Nth ugly number. Ugly numbers are positive numbers whose prime factors only include 2, 3, and 5. The sequence starts with 1.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 1, "max": 500}],
            "gold_solution": """import sys
def main():
    n = int(sys.stdin.read().strip())
    ugly = [0] * n
    ugly[0] = 1
    i2 = i3 = i5 = 0
    for i in range(1, n):
        next2, next3, next5 = ugly[i2] * 2, ugly[i3] * 3, ugly[i5] * 5
        ugly[i] = min(next2, next3, next5)
        if ugly[i] == next2: i2 += 1
        if ugly[i] == next3: i3 += 1
        if ugly[i] == next5: i5 += 1
    print(ugly[n-1])
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_count_range_sum",
            "title_hint": "Range Analytics / Count Range Sum",
            "logic_desc": "Given an integer array and two integers lower and upper, return the number of range sums that lie in [lower, upper]. A range sum S(i, j) is the sum of elements between index i and j inclusive.",
            "difficulty": "Hard",
            "category": "Math",
            "input_schema": [{"type": "int", "name": "Lower", "min": -20, "max": 0}, {"type": "int", "name": "Upper", "min": 0, "max": 20}, {"type": "int", "name": "N", "min": 3, "max": 10}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": -10, "max": 10}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    lower = int(data[0])
    upper = int(data[1])
    n = int(data[2])
    nums = [int(x) for x in data[3:n+3]]
    count = 0
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += nums[j]
            if lower <= s <= upper:
                count += 1
    print(count)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_max_sum_rectangle_2d",
            "title_hint": "Matrix Optimization / Maximum Sum Rectangle",
            "logic_desc": "Find the maximum sum of any rectangular submatrix in a given N x N matrix of integers.",
            "difficulty": "Hard",
            "category": "Math",
            "input_schema": [{"type": "int", "name": "N", "min": 2, "max": 5}, {"type": "matrix", "rows_ref": "N", "cols_ref": "N", "item": {"type": "int", "min": -10, "max": 10}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    idx = 1
    matrix = []
    for r in range(n):
        row = [int(data[idx + c]) for c in range(n)]
        idx += n
        matrix.append(row)
    max_sum = float('-inf')
    for left in range(n):
        temp = [0] * n
        for right in range(left, n):
            for i in range(n):
                temp[i] += matrix[i][right]
            cur_max = cur_sum = temp[0]
            for i in range(1, n):
                cur_sum = max(temp[i], cur_sum + temp[i])
                cur_max = max(cur_max, cur_sum)
            max_sum = max(max_sum, cur_max)
    print(max_sum)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_painter_partition",
            "title_hint": "Load Distribution / Painter Partition",
            "logic_desc": "Given an array of board lengths and K painters, each painter paints contiguous boards. Find the minimum time to paint all boards, where each painter takes time proportional to the total length they paint.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "K", "min": 2, "max": 4}, {"type": "int", "name": "N", "min": 5, "max": 15}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 20}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    k = int(data[0])
    n = int(data[1])
    boards = [int(x) for x in data[2:n+2]]
    def canPaint(limit):
        painters, cur_sum = 1, 0
        for b in boards:
            cur_sum += b
            if cur_sum > limit:
                painters += 1
                cur_sum = b
        return painters <= k
    lo, hi = max(boards), sum(boards)
    res = hi
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if canPaint(mid):
            res = mid
            hi = mid - 1
        else:
            lo = mid + 1
    print(res)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_max_coins_path_grid",
            "title_hint": "Grid Optimization / Maximum Coin Collection",
            "logic_desc": "Given an N x N grid of non-negative integers representing coins, find the maximum coins collected traveling from top-left to bottom-right, moving only right or down.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 5}, {"type": "matrix", "rows_ref": "N", "cols_ref": "N", "item": {"type": "int", "min": 0, "max": 20}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    idx = 1
    grid = []
    for r in range(n):
        row = [int(data[idx + c]) for c in range(n)]
        idx += n
        grid.append(row)
    for r in range(n):
        for c in range(n):
            if r == 0 and c == 0:
                continue
            if r == 0:
                grid[r][c] += grid[r][c-1]
            elif c == 0:
                grid[r][c] += grid[r-1][c]
            else:
                grid[r][c] += max(grid[r-1][c], grid[r][c-1])
    print(grid[n-1][n-1])
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_longest_common_substring",
            "title_hint": "Sequence Mining / Longest Common Substring",
            "logic_desc": "Find the length of the longest contiguous substring that appears in both of two given strings.",
            "difficulty": "Hard",
            "category": "String",
            "input_schema": [{"type": "string", "name": "S1", "length": 15}, {"type": "string", "name": "S2", "length": 15}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    if len(data) < 2:
        print(0)
        return
    s1, s2 = data[0], data[1]
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    max_len = 0
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
                max_len = max(max_len, dp[i][j])
    print(max_len)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_count_subarrays_min_max",
            "title_hint": "Range Constraint / Bounded Subarrays",
            "logic_desc": "Count the number of contiguous subarrays where the difference between the maximum and minimum element is less than or equal to a given limit.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "Limit", "min": 5, "max": 20}, {"type": "int", "name": "N", "min": 5, "max": 15}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 50}}],
            "gold_solution": """import sys
from collections import deque
def main():
    data = sys.stdin.read().split()
    limit = int(data[0])
    n = int(data[1])
    nums = [int(x) for x in data[2:n+2]]
    maxd = deque()
    mind = deque()
    left = 0
    count = 0
    for right in range(n):
        while maxd and nums[maxd[-1]] <= nums[right]:
            maxd.pop()
        while mind and nums[mind[-1]] >= nums[right]:
            mind.pop()
        maxd.append(right)
        mind.append(right)
        while nums[maxd[0]] - nums[mind[0]] > limit:
            left += 1
            if maxd[0] < left:
                maxd.popleft()
            if mind[0] < left:
                mind.popleft()
        count += right - left + 1
    print(count)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_shortest_subarray_sum_k",
            "title_hint": "Window Optimization / Shortest Subarray Sum at Least K",
            "logic_desc": "Find the length of the shortest non-empty contiguous subarray with sum at least K. Return -1 if no such subarray exists.",
            "difficulty": "Hard",
            "category": "Math",
            "input_schema": [{"type": "int", "name": "K", "min": 5, "max": 30}, {"type": "int", "name": "N", "min": 5, "max": 15}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 10}}],
            "gold_solution": """import sys
from collections import deque
def main():
    data = sys.stdin.read().split()
    k = int(data[0])
    n = int(data[1])
    nums = [int(x) for x in data[2:n+2]]
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i+1] = prefix[i] + nums[i]
    dq = deque()
    res = float('inf')
    for i in range(n + 1):
        while dq and prefix[i] - prefix[dq[0]] >= k:
            res = min(res, i - dq.popleft())
        while dq and prefix[i] <= prefix[dq[-1]]:
            dq.pop()
        dq.append(i)
    print(res if res != float('inf') else -1)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_word_break_count",
            "title_hint": "Segmentation Counting / Word Break Combinations",
            "logic_desc": "Given a string of lowercase letters, count the number of ways to segment it into substrings where each substring has length between 1 and K.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "string", "name": "S", "length": 15}, {"type": "int", "name": "K", "min": 2, "max": 5}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    if len(data) < 2:
        print(0)
        return
    s = data[0]
    k = int(data[1])
    n = len(s)
    dp = [0] * (n + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        for j in range(1, min(k, i) + 1):
            dp[i] += dp[i - j]
    print(dp[n])
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_min_cost_connect_sticks",
            "title_hint": "Cost Optimization / Connect Sticks Minimum Cost",
            "logic_desc": "Given an array of stick lengths, connect them into one stick by joining two at a time. The cost of joining two sticks is the sum of their lengths. Find the minimum total cost.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 15}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 50}}],
            "gold_solution": """import sys
import heapq
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    sticks = [int(x) for x in data[1:n+1]]
    heapq.heapify(sticks)
    total_cost = 0
    while len(sticks) > 1:
        a = heapq.heappop(sticks)
        b = heapq.heappop(sticks)
        cost = a + b
        total_cost += cost
        heapq.heappush(sticks, cost)
    print(total_cost)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_skyline_max_height",
            "title_hint": "Geometric Analysis / Skyline Maximum Height",
            "logic_desc": "Given an array of building heights, find the maximum height visible from outside when looking at the buildings as a skyline silhouette. This is equivalent to the maximum element in the array.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 5, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 500}}, {"type": "int", "name": "Q", "min": 3, "max": 5}, {"type": "array", "count_ref": "Q", "item": {"type": "int", "min": 0, "max": 19}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    heights = [int(x) for x in data[1:n+1]]
    q = int(data[n+1])
    queries = [int(x) for x in data[n+2:n+2+q]]
    res = []
    for idx in queries:
        idx = min(idx, n - 1)
        res.append(str(max(heights[:idx+1])))
    print(" ".join(res))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_optimal_bst_cost",
            "title_hint": "Tree Optimization / Optimal Search Cost",
            "logic_desc": "Given an array of sorted keys and their corresponding search frequencies, find the minimum cost of a binary search tree where cost is sum of (frequency * depth) for each key.",
            "difficulty": "Hard",
            "category": "Searching",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 8}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 20}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    freq = [int(x) for x in data[1:n+1]]
    dp = [[0] * n for _ in range(n)]
    for i in range(n):
        dp[i][i] = freq[i]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = float('inf')
            fsum = sum(freq[i:j+1])
            for r in range(i, j + 1):
                cost = fsum
                if r > i:
                    cost += dp[i][r-1]
                if r < j:
                    cost += dp[r+1][j]
                dp[i][j] = min(dp[i][j], cost)
    print(dp[0][n-1])
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_longest_repeating_subseq",
            "title_hint": "String Redundancy / Longest Repeating Subsequence",
            "logic_desc": "Find the length of the longest subsequence that occurs at least twice in a string, where no element at the same position is used in both subsequences.",
            "difficulty": "Medium",
            "category": "String",
            "input_schema": [{"type": "string", "name": "S", "length": 15}],
            "gold_solution": """import sys
def main():
    s = sys.stdin.read().strip()
    if not s:
        print(0)
        return
    n = len(s)
    dp = [[0] * (n + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            if s[i-1] == s[j-1] and i != j:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    print(dp[n][n])
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_max_length_pair_chain",
            "title_hint": "Interval Selection / Maximum Pair Chain",
            "logic_desc": "Given pairs of integers where each pair (a, b) has a < b, find the longest chain where for consecutive pairs (c, d) follows (a, b) only if b < c.",
            "difficulty": "Medium",
            "category": "Intervals",
            "input_schema": [{"type": "int", "name": "N", "min": 3, "max": 10}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 50}}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 50, "max": 100}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    a = [int(x) for x in data[1:n+1]]
    b = [int(x) for x in data[n+1:2*n+1]]
    pairs = sorted(zip(a, b), key=lambda x: x[1])
    count = 0
    cur_end = float('-inf')
    for s, e in pairs:
        if s > cur_end:
            count += 1
            cur_end = e
    print(count)
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        },
        {
            "id": "skel_longest_bitonic_subseq",
            "title_hint": "Sequence Analysis / Longest Bitonic Subsequence",
            "logic_desc": "Find the length of the longest bitonic subsequence: a subsequence that first strictly increases then strictly decreases.",
            "difficulty": "Hard",
            "category": "Array",
            "input_schema": [{"type": "int", "name": "N", "min": 5, "max": 20}, {"type": "array", "count_ref": "N", "item": {"type": "int", "min": 1, "max": 100}}],
            "gold_solution": """import sys
def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n+1]]
    lis = [1] * n
    for i in range(1, n):
        for j in range(i):
            if nums[j] < nums[i]:
                lis[i] = max(lis[i], lis[j] + 1)
    lds = [1] * n
    for i in range(n - 2, -1, -1):
        for j in range(i + 1, n):
            if nums[j] < nums[i]:
                lds[i] = max(lds[i], lds[j] + 1)
    print(max(lis[i] + lds[i] - 1 for i in range(n)))
if __name__ == "__main__":
    main()""",
            "input_generator": lambda: None
        }
    ]

    @classmethod
    def get_skeleton(cls, difficulty=None):
        pool = cls.SKELETONS
        if difficulty:
            pool = [s for s in cls.SKELETONS if s["difficulty"].lower() == difficulty.lower()]
        if not pool: pool = cls.SKELETONS
        return random.choice(pool)
