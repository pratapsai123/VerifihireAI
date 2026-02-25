from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
  {
    "question": "What is the time complexity to access an element in an array by its index?",
    "options": {
      "A": "O(1)",
      "B": "O(n)",
      "C": "O(log n)",
      "D": "O(n^2)"
    },
    "answer": "A"
  },
  {
    "question": "True or False: In a Singly Linked List, you can traverse both forward and backward.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO are advantages of Linked Lists over Arrays?",
    "options": {
      "A": "Dynamic size allocation.",
      "B": "Ease of insertion/deletion at any position.",
      "C": "Direct access to any element using an index.",
      "D": "Lower memory overhead per element."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Arrays are stored in contiguous memory locations.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which structure is best for implementing a 'Circular Buffer'?",
    "options": {
      "A": "Stack",
      "B": "Circular Linked List",
      "C": "Binary Tree",
      "D": "Hash Table"
    },
    "answer": "B"
  },
  {
    "question": "Which principle does a Stack follow?",
    "options": {
      "A": "FIFO (First-In, First-Out)",
      "B": "LIFO (Last-In, First-Out)",
      "C": "LILO (Last-In, Last-Out)",
      "D": "Priority-based"
    },
    "answer": "B"
  },
  {
    "question": "True or False: A Queue follows the FIFO (First-In, First-Out) principle.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO applications of a Stack data structure:",
    "options": {
      "A": "Undo/Redo operations in editors.",
      "B": "Function call management (Recursion).",
      "C": "CPU Task Scheduling.",
      "D": "Breadth-First Search (BFS) traversal."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A 'Deque' (Double-Ended Queue) allows insertion and deletion at both ends.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "In a Priority Queue, how are elements removed?",
    "options": {
      "A": "Based on insertion order.",
      "B": "Based on the associated priority value.",
      "C": "Randomly.",
      "D": "Based on the size of the element."
    },
    "answer": "B"
  },
  {
    "question": "What is the maximum number of children a node in a Binary Tree can have?",
    "options": {
      "A": "1",
      "B": "2",
      "C": "3",
      "D": "Unlimited"
    },
    "answer": "B"
  },
  {
    "question": "True or False: In a Binary Search Tree (BST), the left child is always smaller than the parent node.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are types of balanced Binary Trees?",
    "options": {
      "A": "AVL Tree",
      "B": "Red-Black Tree",
      "C": "Binary Heap",
      "D": "Expression Tree"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A 'Leaf' node is a node that has at least one child.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is the time complexity of searching in a perfectly balanced BST?",
    "options": {
      "A": "O(n)",
      "B": "O(1)",
      "C": "O(log n)",
      "D": "O(n log n)"
    },
    "answer": "C"
  },
  {
    "question": "What is a 'Collision' in a Hash Table?",
    "options": {
      "A": "When the table runs out of memory.",
      "B": "When two different keys produce the same hash value.",
      "C": "When a key is deleted.",
      "D": "When the hash function returns a negative value."
    },
    "answer": "B"
  },
  {
    "question": "True or False: An 'Adjacency Matrix' is a common way to represent a Graph.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO common methods for resolving hash collisions:",
    "options": {
      "A": "Chaining (Linked Lists)",
      "B": "Open Addressing (Probing)",
      "C": "Binary Search",
      "D": "Recursion"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A 'Directed Graph' (Digraph) has edges with a specific direction.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which algorithm is commonly used to find the shortest path in a weighted graph?",
    "options": {
      "A": "Prim's Algorithm",
      "B": "Dijkstra's Algorithm",
      "C": "Kruskal's Algorithm",
      "D": "Huffman Coding"
    },
    "answer": "B"
  },
  {
    "question": "What is the space complexity of an Adjacency Matrix for a graph with V vertices?",
    "options": {
      "A": "O(V)",
      "B": "O(V^2)",
      "C": "O(E)",
      "D": "O(V+E)"
    },
    "answer": "B"
  },
  {
    "question": "True or False: A 'Heap' is a specialized tree-based data structure that satisfies the heap property.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO traversals visit the root node first?",
    "options": {
      "A": "Pre-order Traversal",
      "B": "Level-order Traversal (starting at root)",
      "C": "In-order Traversal",
      "D": "Post-order Traversal"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Post-order traversal of a BST always yields elements in ascending order.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which structure is used to implement a 'Dictionary'?",
    "options": {
      "A": "Stack",
      "B": "Queue",
      "C": "Hash Table",
      "D": "Linked List"
    },
    "answer": "C"
  },
  {
    "question": "Which of the following is a disadvantage of using an Array?",
    "options": {
      "A": "Constant time access",
      "B": "Fixed size (static memory)",
      "C": "Cache friendliness",
      "D": "Low memory overhead"
    },
    "answer": "B"
  },
  {
    "question": "True or False: In a Doubly Linked List, each node contains pointers to both the next and previous nodes.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO operations are the most expensive for a large Array?",
    "options": {
      "A": "Accessing the first element",
      "B": "Inserting an element at the beginning",
      "C": "Deleting an element from the middle",
      "D": "Accessing the last element"
    },
    "answer": ["B", "C"]
  },
  {
    "question": "True or False: A 'Stack Overflow' occurs when you try to remove an element from an empty stack.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is the time complexity to insert an element at the end of a Linked List if you only have a pointer to the Head?",
    "options": {
      "A": "O(1)",
      "B": "O(n)",
      "C": "O(log n)",
      "D": "O(n^2)"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO structures are typically used to implement a Stack?",
    "options": {
      "A": "Arrays",
      "B": "Linked Lists",
      "C": "Hash Tables",
      "D": "Binary Trees"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: In a Circular Queue, the last position is connected back to the first position.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which data structure is used by the compiler to check for balanced parentheses?",
    "options": {
      "A": "Queue",
      "B": "Stack",
      "C": "Tree",
      "D": "Array"
    },
    "answer": "B"
  },
  {
    "question": "True or False: A 'Priority Queue' can be implemented using a sorted array.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO types of Linked Lists:",
    "options": {
      "A": "Singly Linked List",
      "B": "Doubly Linked List",
      "C": "Parallel Linked List",
      "D": "Indexed Linked List"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What happens in an 'Enqueue' operation in a Queue?",
    "options": {
      "A": "An element is removed from the front.",
      "B": "An element is added to the rear.",
      "C": "An element is added to the front.",
      "D": "The queue is deleted."
    },
    "answer": "B"
  },
  {
    "question": "True or False: The time complexity to delete the head of a Singly Linked List is O(1).",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are linear data structures?",
    "options": {
      "A": "Stack",
      "B": "Queue",
      "C": "Binary Tree",
      "D": "Graph"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A 'Sparse Matrix' is a matrix in which most of the elements are zero.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which structure is most efficient for 'Reversing a String'?",
    "options": {
      "A": "Queue",
      "B": "Stack",
      "C": "Hash Table",
      "D": "Heap"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO properties of a dynamic array:",
    "options": {
      "A": "It can grow in size automatically.",
      "B": "It allows O(1) access time by index.",
      "C": "It has no memory overhead.",
      "D": "It is always faster than a Linked List for insertions at the start."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: In a Max-Heap, the root node contains the smallest element.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is the result of an 'In-order Traversal' of a Binary Search Tree?",
    "options": {
      "A": "Elements in random order",
      "B": "Elements in sorted ascending order",
      "C": "Elements in sorted descending order",
      "D": "Only the leaf nodes"
    },
    "answer": "B"
  },
  {
    "question": "True or False: A Graph can have cycles, but a Tree cannot.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are used for Graph Traversal?",
    "options": {
      "A": "Depth First Search (DFS)",
      "B": "Breadth First Search (BFS)",
      "C": "Binary Search",
      "D": "Linear Search"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: An 'Undirected Graph' has edges that do not have a specific direction.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the time complexity of the 'Pop' operation in a Stack?",
    "options": {
      "A": "O(1)",
      "B": "O(n)",
      "C": "O(log n)",
      "D": "O(n^2)"
    },
    "answer": "O(1)"
  },
  {
    "question": "Which TWO are properties of a 'B-Tree'?",
    "options": {
      "A": "All leaf nodes are at the same level.",
      "B": "Nodes can have more than two children.",
      "C": "It is primarily used in main memory only.",
      "D": "It is always a complete binary tree."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A 'Trie' (Prefix Tree) is efficient for searching words in a dictionary.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which data structure is used to implement Breadth-First Search (BFS)?",
    "options": {
      "A": "Stack",
      "B": "Queue",
      "C": "Tree",
      "D": "Heap"
    },
    "answer": "B"
  },
  {
    "question": "What is the average time complexity of the 'Bubble Sort' algorithm?",
    "options": {
      "A": "O(n)",
      "B": "O(n log n)",
      "C": "O(n^2)",
      "D": "O(log n)"
    },
    "answer": "C"
  },
  {
    "question": "True or False: Binary Search can be performed on an unsorted array.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO 'Divide and Conquer' sorting algorithms:",
    "options": {
      "A": "Merge Sort",
      "B": "Quick Sort",
      "C": "Selection Sort",
      "D": "Insertion Sort"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Stable Sorting' means that elements with equal keys maintain their relative order.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which sorting algorithm is the fastest for small or nearly sorted data?",
    "options": {
      "A": "Merge Sort",
      "B": "Insertion Sort",
      "C": "Quick Sort",
      "D": "Heap Sort"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO properties of 'Quick Sort':",
    "options": {
      "A": "It uses a pivot element.",
      "B": "It is an in-place sorting algorithm.",
      "C": "It is always stable.",
      "D": "It has a worst-case of O(n log n)."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Merge Sort requires O(n) extra space to merge the sub-arrays.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the worst-case time complexity of Selection Sort?",
    "options": {
      "A": "O(n)",
      "B": "O(n log n)",
      "C": "O(n^2)",
      "D": "O(1)"
    },
    "answer": "C"
  },
  {
    "question": "Which TWO are 'Linear Time' sorting algorithms under specific conditions?",
    "options": {
      "A": "Counting Sort",
      "B": "Radix Sort",
      "C": "Bubble Sort",
      "D": "Shell Sort"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Linear Search has a time complexity of O(n).",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the best-case complexity of a 'Optimized Bubble Sort'?",
    "options": {
      "A": "O(n)",
      "B": "O(n^2)",
      "C": "O(n log n)",
      "D": "O(1)"
    },
    "answer": "A"
  },
  {
    "question": "True or False: Heap Sort is generally faster than Quick Sort in practice.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO are search algorithms?",
    "options": {
      "A": "Binary Search",
      "B": "Exponential Search",
      "C": "Bucket Sort",
      "D": "Cycle Sort"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: In a Max-Heap, the largest element is always at the root.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which algorithm is used to find the 'Kth smallest element' efficiently?",
    "options": {
      "A": "Quick Select",
      "B": "Binary Search",
      "C": "Bubble Sort",
      "D": "Interpolation Search"
    },
    "answer": "A"
  },
  {
    "question": "What does Big O notation describe?",
    "options": {
      "A": "Exact runtime in seconds.",
      "B": "Upper bound of an algorithm's growth rate.",
      "C": "Brand of computer.",
      "D": "Number of lines of code."
    },
    "answer": "B"
  },
  {
    "question": "True or False: O(1) is considered 'Constant Time.'",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO complexities that are faster than O(n^2):",
    "options": {
      "A": "O(n log n)",
      "B": "O(n)",
      "C": "O(n^3)",
      "D": "O(2^n)"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: O(2^n) represents 'Logarithmic Complexity.'",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is the complexity of nested loops, where both run n times?",
    "options": {
      "A": "O(2n)",
      "B": "O(n^2)",
      "C": "O(n)",
      "D": "O(1)"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO factors that affect Space Complexity:",
    "options": {
      "A": "Input size.",
      "B": "Auxiliary data structures.",
      "C": "CPU speed.",
      "D": "Language version."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: An algorithm with O(n log n) is slower than O(n) for very large n.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which complexity describes 'Binary Search' on a sorted array?",
    "options": {
      "A": "O(n)",
      "B": "O(1)",
      "C": "O(log n)",
      "D": "O(n^2)"
    },
    "answer": "C"
  },
  {
    "question": "True or False: Space complexity includes the space taken by the input itself.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which notation is used to describe the 'Average Case' complexity?",
    "options": {
      "A": "Big O",
      "B": "Big Theta",
      "C": "Big Omega",
      "D": "Little o"
    },
    "answer": "B"
  },
  {
    "question": "In an AVL Tree, what is the maximum allowed 'Balance Factor'?",
    "options": {
      "A": "0",
      "B": "1",
      "C": "2",
      "D": "5"
    },
    "answer": "B"
  },
  {
    "question": "True or False: A 'Spanning Tree' must contain all vertices of the graph.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO properties of a 'Red-Black Tree':",
    "options": {
      "A": "Every node is either red or black.",
      "B": "The root is always black.",
      "C": "It is an N-ary tree.",
      "D": "It is always perfectly balanced."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Prim’s Algorithm' is used to find the Shortest Path.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is the height of a balanced Binary Tree with n nodes?",
    "options": {
      "A": "n",
      "B": "log2 n",
      "C": "n^2",
      "D": "sqrt(n)"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO are used to represent a graph?",
    "options": {
      "A": "Adjacency List",
      "B": "Adjacency Matrix",
      "C": "Hash Table",
      "D": "Stack"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A 'Complete Binary Tree' is filled except possibly the last level.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "In a graph, what is 'Degree of a Vertex'?",
    "options": {
      "A": "Node weight.",
      "B": "Number of connected edges.",
      "C": "Distance from root.",
      "D": "Alphabetical order."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Kruskal’s Algorithm' uses a Greedy approach for MST.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO Graph Traversal techniques:",
    "options": {
      "A": "Breadth-First Search (BFS)",
      "B": "Depth-First Search (DFS)",
      "C": "Linear Search",
      "D": "Interpolation Search"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is 'Open Addressing' in Hashing?",
    "options": {
      "A": "Using Linked Lists.",
      "B": "Finding another slot in the table itself.",
      "C": "Deleting keys.",
      "D": "Resizing tables."
    },
    "answer": "B"
  },
  {
    "question": "True or False: A good hash function should distribute keys uniformly.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO 'Probing' techniques:",
    "options": {
      "A": "Linear Probing",
      "B": "Quadratic Probing",
      "C": "Circular Probing",
      "D": "Binary Probing"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Load Factor' is the ratio of elements to table size.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Double Hashing'?",
    "options": {
      "A": "Hashing twice.",
      "B": "Using a second hash function for step size.",
      "C": "Using two tables.",
      "D": "Squaring results."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO applications of Hashing:",
    "options": {
      "A": "Implementing Sets and Maps.",
      "B": "Password verification.",
      "C": "Sorting in O(n^2).",
      "D": "Managing recursion."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Quadratic Probing' reduces 'Primary Clustering.'",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the average time complexity of Hash Table insertion?",
    "options": {
      "A": "O(1)",
      "B": "O(n)",
      "C": "O(log n)",
      "D": "O(n log n)"
    },
    "answer": "A"
  },
  {
    "question": "True or False: A 'Self-Organizing List' moves accessed elements to the front.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which structure is used in 'Breadth-First Search' (BFS)?",
    "options": {
      "A": "Stack",
      "B": "Queue",
      "C": "Priority Queue",
      "D": "Tree"
    },
    "answer": "B"
  },
  {
    "question": "Which data structure is best for a 'Directory System'?",
    "options": {
      "A": "Queue",
      "B": "Stack",
      "C": "Tree",
      "D": "Linked List"
    },
    "answer": "C"
  },
  {
    "question": "True or False: 'Tail Recursion' is more memory-efficient if optimized.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO properties of a 'B-Tree':",
    "options": {
      "A": "Self-balancing.",
      "B": "Heavy use in databases.",
      "C": "Binary tree.",
      "D": "Leaves at different levels."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A 'Splay Tree' moves the most recently accessed node to the root.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which structure is used for 'Depth-First Search' (DFS)?",
    "options": {
      "A": "Queue",
      "B": "Stack",
      "C": "Hash Table",
      "D": "Circular List"
    },
    "answer": "B"
  },
  
  {
    "question": "What is 'Internal Sorting'?",
    "options": {
      "A": "Sorting that happens inside a function.",
      "B": "Sorting where all data fits in the main memory (RAM).",
      "C": "Sorting that happens on a remote server.",
      "D": "Sorting only private variables."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Radix Sort' depends on the digits of the numbers being sorted.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO 'In-place' sorting algorithms:",
    "options": {
      "A": "Bubble Sort",
      "B": "Heap Sort",
      "C": "Merge Sort",
      "D": "Counting Sort"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A 'Skewed Tree' is a tree where nodes only have one child, effectively becoming a Linked List.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the time complexity of deleting a node from a BST (Average Case)?",
    "options": {
      "A": "O(1)",
      "B": "O(n)",
      "C": "O(log n)",
      "D": "O(n log n)"
    },
    "answer": "C"
  },
  {
    "question": "Identify TWO 'Non-linear' data structures:",
    "options": {
      "A": "Trees",
      "B": "Graphs",
      "C": "Arrays",
      "D": "Stacks"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: An 'Eulerian Path' is a trail in a graph which visits every edge exactly once.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is a 'B+ Tree'?",
    "options": {
      "A": "A tree where all data is stored in the leaf nodes.",
      "B": "A tree with only positive numbers.",
      "C": "A tree that is twice as fast as a B-Tree.",
      "D": "A type of binary heap."
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO applications of Graphs:",
    "options": {
      "A": "Social Networks (connections).",
      "B": "Google Maps (pathfinding).",
      "C": "Undo functionality in Word.",
      "D": "Parentheses matching."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Linear Probing' can lead to primary clustering.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is a 'Threaded Binary Tree'?",
    "options": {
      "A": "A tree that uses multiple CPU threads.",
      "B": "A binary tree where NULL pointers are replaced by pointers to in-order predecessor/successor.",
      "C": "A tree with no leaf nodes.",
      "D": "A tree used only for string matching."
    },
    "answer": "B"
  },
  {
    "question": "True or False: In a Min-Heap, the parent node always has a value less than or equal to its children.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO types of rotations used in an AVL Tree:",
    "options": {
      "A": "Single Left Rotation (LL)",
      "B": "Double Left-Right Rotation (LR)",
      "C": "Triple Pivot Rotation",
      "D": "Circular Shift Rotation"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A 'Full Binary Tree' is a tree where every node has either 0 or 2 children.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which searching algorithm is most efficient for a sorted array where elements are uniformly distributed?",
    "options": {
      "A": "Linear Search",
      "B": "Interpolation Search",
      "C": "Jump Search",
      "D": "Fibonacci Search"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO properties of a 'Red-Black Tree' during insertion:",
    "options": {
      "A": "The new node is initially colored Red.",
      "B": "If a node is Red, its children must be Black.",
      "C": "The root can be any color.",
      "D": "Leaf nodes contain data values."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'External Sorting' is used when the data does not fit into the RAM.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the time complexity of 'Heapsort' in the worst case?",
    "options": {
      "A": "O(n)",
      "B": "O(n^2)",
      "C": "O(n log n)",
      "D": "O(log n)"
    },
    "answer": "C"
  },
  {
    "question": "Which TWO are applications of a 'Trie' (Prefix Tree)?",
    "options": {
      "A": "Autocomplete features.",
      "B": "Spell checkers.",
      "C": "Storing payroll records by ID.",
      "D": "Calculating shortest path between cities."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A 'Forest' in graph theory is a collection of disjoint trees.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the time complexity of 'Dijkstra’s Algorithm' using a Binary Heap?",
    "options": {
      "A": "O(V^2)",
      "B": "O(E log V)",
      "C": "O(V+E)",
      "D": "O(E^2)"
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Breadth-First Search' (BFS) uses a Stack as its primary data structure.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO properties of an 'Adjacency List':",
    "options": {
      "A": "It is space-efficient for sparse graphs.",
      "B": "It allows O(1) time to check if an edge exists.",
      "C": "It uses an array of linked lists.",
      "D": "It always requires O(V^2) space."
    },
    "answer": ["A", "C"]
  },
  {
    "question": "True or False: 'Topological Sort' can only be performed on Directed Acyclic Graphs (DAGs).",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which algorithm is used to find all-pairs shortest paths in a weighted graph?",
    "options": {
      "A": "Bellman-Ford",
      "B": "Floyd-Warshall",
      "C": "Prim’s",
      "D": "Kruskal’s"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Internal Sorting'?",
    "options": {
      "A": "Sorting that happens inside a function.",
      "B": "Sorting where all data fits in the main memory (RAM).",
      "C": "Sorting that happens on a remote server.",
      "D": "Sorting only private variables."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Radix Sort' depends on the digits of the numbers being sorted.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO 'In-place' sorting algorithms:",
    "options": {
      "A": "Bubble Sort",
      "B": "Heap Sort",
      "C": "Merge Sort",
      "D": "Counting Sort"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A 'Skewed Tree' is a tree where nodes only have one child, effectively becoming a Linked List.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the time complexity of deleting a node from a BST (Average Case)?",
    "options": {
      "A": "O(1)",
      "B": "O(n)",
      "C": "O(log n)",
      "D": "O(n log n)"
    },
    "answer": "C"
  },
  {
    "question": "Identify TWO 'Non-linear' data structures:",
    "options": {
      "A": "Trees",
      "B": "Graphs",
      "C": "Arrays",
      "D": "Stacks"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: An 'Eulerian Path' is a trail in a graph which visits every edge exactly once.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is a 'B+ Tree'?",
    "options": {
      "A": "A tree where all data is stored in the leaf nodes.",
      "B": "A tree with only positive numbers.",
      "C": "A tree that is twice as fast as a B-Tree.",
      "D": "A type of binary heap."
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO applications of Graphs:",
    "options": {
      "A": "Social Networks (connections).",
      "B": "Google Maps (pathfinding).",
      "C": "Undo functionality in Word.",
      "D": "Parentheses matching."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Linear Probing' can lead to primary clustering.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is a 'Threaded Binary Tree'?",
    "options": {
      "A": "A tree that uses multiple CPU threads to traverse.",
      "B": "A binary tree where empty child pointers are replaced by pointers to the in-order predecessor/successor.",
      "C": "A tree with no leaf nodes.",
      "D": "A tree used only for string matching."
    },
    "answer": "B"
  },
  {
    "question": "True or False: In a Min-Heap, the parent node always has a value less than or equal to its children.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO types of rotations used in an AVL Tree:",
    "options": {
      "A": "Single Left Rotation (LL)",
      "B": "Double Left-Right Rotation (LR)",
      "C": "Triple Pivot Rotation",
      "D": "Circular Shift Rotation"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A 'Full Binary Tree' is a tree where every node has either 0 or 2 children.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which searching algorithm is most efficient for a sorted array where elements are uniformly distributed?",
    "options": {
      "A": "Linear Search",
      "B": "Interpolation Search",
      "C": "Jump Search",
      "D": "Fibonacci Search"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO properties of a 'Red-Black Tree' during insertion:",
    "options": {
      "A": "The new node is initially colored Red.",
      "B": "If a node is Red, its children must be Black.",
      "C": "The root can be any color.",
      "D": "Leaf nodes contain data values."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'External Sorting' is used when the data to be sorted does not fit into the RAM.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the time complexity of 'Heapsort' in the worst case?",
    "options": {
      "A": "O(n)",
      "B": "O(n^2)",
      "C": "O(n log n)",
      "D": "O(log n)"
    },
    "answer": "C"
  },
  {
    "question": "Which TWO are applications of a 'Trie' (Prefix Tree)?",
    "options": {
      "A": "Autocomplete features in search engines.",
      "B": "Spell checkers.",
      "C": "Storing employee payroll records by ID.",
      "D": "Calculating the shortest path between cities."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A 'Forest' in graph theory is a collection of disjoint trees.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the time complexity of 'Dijkstra’s Algorithm' using a Binary Heap?",
    "options": {
      "A": "O(V^2)",
      "B": "O(E log V)",
      "C": "O(V+E)",
      "D": "O(E^2)"
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Breadth-First Search' (BFS) uses a Stack as its primary data structure.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO properties of an 'Adjacency List':",
    "options": {
      "A": "It is space-efficient for sparse graphs.",
      "B": "It allows O(1) time to check if an edge exists between two nodes.",
      "C": "It uses an array of linked lists.",
      "D": "It always requires O(V^2) space."
    },
    "answer": ["A", "C"]
  },
  {
    "question": "True or False: 'Topological Sort' can only be performed on Directed Acyclic Graphs (DAGs).",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which algorithm is used to find all-pairs shortest paths in a weighted graph?",
    "options": {
      "A": "Bellman-Ford",
      "B": "Floyd-Warshall",
      "C": "Prim’s",
      "D": "Kruskal’s"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO types of edges in a DFS traversal of a graph:",
    "options": {
      "A": "Tree Edge",
      "B": "Back Edge",
      "C": "Side Edge",
      "D": "Jump Edge"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A 'Complete Graph' is one where every pair of distinct vertices is connected by a unique edge.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "In an Adjacency Matrix, if the graph is undirected, the matrix is:",
    "options": {
      "A": "Sparse",
      "B": "Symmetric",
      "C": "Identity",
      "D": "Skew-symmetric"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO are 'Greedy' algorithms?",
    "options": {
      "A": "Huffman Coding",
      "B": "Prim's Algorithm",
      "C": "Merge Sort",
      "D": "Floyd-Warshall"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Bellman-Ford' algorithm can handle graphs with negative edge weights.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the average case complexity of 'Quick Sort'?",
    "options": {
      "A": "O(n)",
      "B": "O(n^2)",
      "C": "O(n log n)",
      "D": "O(1)"
    },
    "answer": "C"
  },
  {
    "question": "True or False: 'Interpolation Search' is faster than Binary Search for a uniformly distributed sorted array.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO disadvantages of 'Linear Probing' in Hashing:",
    "options": {
      "A": "Primary Clustering.",
      "B": "Performance degradation as the load factor increases.",
      "C": "Increased memory usage due to pointers.",
      "D": "Complexity of the hash function."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: The time complexity of accessing an element in a Hash Table with a perfect hash function is O(1).",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which sorting algorithm is 'Stable' by nature?",
    "options": {
      "A": "Quick Sort",
      "B": "Merge Sort",
      "C": "Heap Sort",
      "D": "Selection Sort"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO characteristics of 'Space Complexity':",
    "options": {
      "A": "It measures the extra memory used by the algorithm.",
      "B": "It includes the space required for the input.",
      "C": "It is measured in seconds.",
      "D": "It is independent of the input size."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Shell Sort' is an optimization of Insertion Sort.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the time complexity of 'Building a Heap' from an array of n elements?",
    "options": {
      "A": "O(n)",
      "B": "O(n log n)",
      "C": "O(n^2)",
      "D": "O(log n)"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are search techniques in a Graph?",
    "options": {
      "A": "BFS",
      "B": "DFS",
      "C": "BFS+",
      "D": "Tree Search"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: The 'Load Factor' of a hash table should be kept low to minimize collisions.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the space complexity of 'Merge Sort'?",
    "options": {
      "A": "O(1)",
      "B": "O(n)",
      "C": "O(log n)",
      "D": "O(n^2)"
    },
    "answer": "B"
  },
  {
    "question": "True or False: A 'Priority Queue' can be efficiently implemented using a Binary Heap.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO sorting algorithms with O(n^2) worst-case complexity:",
    "options": {
      "A": "Bubble Sort",
      "B": "Selection Sort",
      "C": "Merge Sort",
      "D": "Quick Sort (best case)"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'In-place' sorting algorithms require O(n) extra space.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which structure is best for a 'Dictionary' with fast lookups?",
    "options": {
      "A": "Array",
      "B": "Hash Map",
      "C": "Linked List",
      "D": "Stack"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Recursive algorithms always use more memory because of the call stack.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO balanced tree types:",
    "options": {
      "A": "AVL Tree",
      "B": "B-Tree",
      "C": "Binary Tree",
      "D": "Skewed Tree"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is the result of 'Post-order Traversal' of: Root(A), Left(B), Right(C)?",
    "options": {
      "A": "A-B-C",
      "B": "B-C-A",
      "C": "C-B-A",
      "D": "B-A-C"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Hashing is used in database indexing.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which is the fastest for searching an item in a sorted array of 1 million items?",
    "options": {
      "A": "Linear Search",
      "B": "Binary Search",
      "C": "Interpolation Search",
      "D": "Bubble Search"
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Cycle Detection' in a graph can be done using DFS.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the complexity of 'Bucket Sort'?",
    "options": {
      "A": "O(n+k)",
      "B": "O(n^2)",
      "C": "O(n log n)",
      "D": "O(1)"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO components of a Node in a Doubly Linked List:",
    "options": {
      "A": "Prev Pointer",
      "B": "Next Pointer",
      "C": "Index",
      "D": "Size"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A 'Clique' in a graph is a subset of vertices where every two distinct vertices are adjacent.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which structure follows the 'LIFO' principle?",
    "options": {
      "A": "Stack",
      "B": "Queue",
      "C": "Deque",
      "D": "Priority Queue"
    },
    "answer": "A"
  },
  {
    "question": "True or False: A 'Circular Linked List' has no NULL pointer.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO search algorithms:",
    "options": {
      "A": "Linear Search",
      "B": "Binary Search",
      "C": "Merge Search",
      "D": "Quick Search"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is the time complexity of 'Insertion Sort' in the best case?",
    "options": {
      "A": "O(1)",
      "B": "O(n)",
      "C": "O(n^2)",
      "D": "O(log n)"
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Big Omega' (Ω) notation represents the lower bound of an algorithm.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which sorting is used in Java's Arrays.sort() for objects?",
    "options": {
      "A": "TimSort",
      "B": "QuickSort",
      "C": "BubbleSort",
      "D": "SelectionSort"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO Graph types:",
    "options": {
      "A": "Directed",
      "B": "Undirected",
      "C": "Sorted",
      "D": "Linear"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A 'Heap' can be stored in an array without using pointers.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Self-balancing' in trees?",
    "options": {
      "A": "Automatically maintaining a minimum height.",
      "B": "Adding nodes in alphabetical order.",
      "C": "Deleting empty nodes.",
      "D": "Using only 2 children."
    },
    "answer": "A"
  },
  {
    "question": "True or False: Counting Sort is efficient if the range of input data (k) is not significantly larger than n.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO types of Queue:",
    "options": {
      "A": "Priority Queue",
      "B": "Circular Queue",
      "C": "Balanced Queue",
      "D": "Static Queue"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: The worst-case complexity of a Hash Table lookup is O(n).",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Collision Resolution'?",
    "options": {
      "A": "Handling two keys hashing to the same index.",
      "B": "Stopping the program if data is duplicate.",
      "C": "Speeding up the hash function.",
      "D": "Deleting the table."
    },
    "answer": "A"
  },
  {
    "question": "True or False: Breadth-First Search finds the shortest path in an unweighted graph.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO stack operations:",
    "options": {
      "A": "Push",
      "B": "Pop",
      "C": "Enqueue",
      "D": "Dequeue"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Binary trees can have at most two children per node.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the complexity of accessing an element in a Linked List?",
    "options": {
      "A": "O(1)",
      "B": "O(n)",
      "C": "O(log n)",
      "D": "O(n^2)"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Arrays have a fixed size after creation.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO tree traversals:",
    "options": {
      "A": "In-order",
      "B": "Pre-order",
      "C": "Side-order",
      "D": "Up-order"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A 'DAG' has no cycles.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which structure is used for 'Backtracking'?",
    "options": {
      "A": "Stack",
      "B": "Queue",
      "C": "Hash Table",
      "D": "Array"
    },
    "answer": "A"
  },
  {
    "question": "True or False: O(n log n) is faster than O(n^2).",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO applications of Hashing:",
    "options": {
      "A": "Hash Maps",
      "B": "Hash Sets",
      "C": "Quick Sorting",
      "D": "Tree Balancing"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is the degree of a leaf node in a tree?",
    "options": {
      "A": "0",
      "B": "1",
      "C": "2",
      "D": "Depends on height"
    },
    "answer": "A"
  },
  {
    "question": "True or False: 'Radix Sort' is a non-comparison based sorting algorithm.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO sorting algorithms that are 'Divide and Conquer':",
    "options": {
      "A": "Merge Sort",
      "B": "Quick Sort",
      "C": "Bubble Sort",
      "D": "Selection Sort"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A 'Spanning Tree' contains all vertices of the graph but only enough edges to stay connected.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the result of In-order traversal of a BST with: 10(Root), 5(Left), 15(Right)?",
    "options": {
      "A": "5, 10, 15",
      "B": "10, 5, 15",
      "C": "15, 10, 5",
      "D": "5, 15, 10"
    },
    "answer": "A"
  },
  {
    "question": "True or False: The time complexity to find an item in a balanced BST is O(log n).",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO types of rotations in AVL Trees:",
    "options": {
      "A": "RR",
      "B": "LR",
      "C": "XL",
      "D": "ZZ"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Dynamic Programming is used to optimize recursive algorithms with overlapping subproblems.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which of the following uses a 'Greedy' approach?",
    "options": {
      "A": "Dijkstra's Algorithm",
      "B": "Merge Sort",
      "C": "Binary Search",
      "D": "Bubble Sort"
    },
    "answer": "A"
  },
  {
    "question": "True or False: A 'Trie' is also called a digital tree or prefix tree.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO characteristics of a Max-Heap:",
    "options": {
      "A": "Root is the largest element.",
      "B": "Parent value >= Child value.",
      "C": "Root is the smallest element.",
      "D": "Only leaf nodes are filled."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Linear Search is faster than Binary Search on large sorted arrays.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Secondary Clustering' in hashing?",
    "options": {
      "A": "Two different keys following the same probe sequence.",
      "B": "Deleting all data.",
      "C": "Using two tables.",
      "D": "Adding nodes to a tree."
    },
    "answer": "A"
  },
  {
    "question": "True or False: In BFS, we use a Queue.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO searching algorithms:",
    "options": {
      "A": "Linear",
      "B": "Binary",
      "C": "Selection",
      "D": "Insertion"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: O(log n) is considered better than O(n).",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which algorithm is used for finding the Minimum Spanning Tree?",
    "options": {
      "A": "Prim's",
      "B": "Dijkstra's",
      "C": "Binary Search",
      "D": "Quick Sort"
    },
    "answer": "A"
  },
  {
    "question": "True or False: Linked lists have better cache locality than arrays.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO types of Linked Lists:",
    "options": {
      "A": "Singly",
      "B": "Doubly",
      "C": "Dynamic",
      "D": "Static"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Amortized Analysis' finds the average performance of an operation over a sequence of operations.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which structure is used for 'LRU Cache' (Least Recently Used) implementation?",
    "options": {
      "A": "Hash Map + Doubly Linked List",
      "B": "Stack + Queue",
      "C": "BST + Array",
      "D": "Graph + Heap"
    },
    "answer": "A"
  },
  {
    "question": "True or False: Binary Search is an O(n) algorithm.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which is the best case complexity for Quick Sort?",
    "options": {
      "A": "O(n)",
      "B": "O(n log n)",
      "C": "O(n^2)",
      "D": "O(1)"
    },
    "answer": "B"
  },
  {
    "question": "True or False: In a Singly Linked List, you can traverse both forward and backward.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  }

]
    
      

def remove_duplicates(questions):
    seen = set()
    unique = []

    for q in questions:
        if q["question"] not in seen:
            seen.add(q["question"])
            unique.append(q)

    return unique


def generate_pdf(skill_name, questions):
    doc = SimpleDocTemplate(
        f"{skill_name}_Question_Bank.pdf",
        pagesize=A4
    )

    elements = []
    styles = getSampleStyleSheet()

    title_style = styles["Heading1"]
    normal_style = styles["Normal"]

    elements.append(Paragraph(f"{skill_name} Question Bank ({len(questions)} Questions)", title_style))
    elements.append(Spacer(1, 0.3 * inch))

    for i, q in enumerate(questions, 1):
        elements.append(Paragraph(f"{i}. {q['question']}", normal_style))
        elements.append(Spacer(1, 0.1 * inch))

        for key, value in q["options"].items():
            elements.append(Paragraph(f"{key}) {value}", normal_style))
            elements.append(Spacer(1, 0.05 * inch))

        elements.append(Paragraph(f"<b>Answer:</b> {q['answer']}", normal_style))
        elements.append(Spacer(1, 0.3 * inch))

    doc.build(elements)
    print(f"✅ PDF Generated with {len(questions)} UNIQUE questions only.")


if __name__ == "__main__":
    skill = "Datastructure"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
