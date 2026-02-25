from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
  {
    "question": "Which of the following is the correct definition of the C++ STL?",
    "options": {
      "A": "A library for building graphical user interfaces",
      "B": "A powerful set of C++ template classes to provide common data structures and algorithms",
      "C": "A database management system for C++",
      "D": "A hardware driver interface for C++"
    },
    "answer": "B"
  },
  {
    "question": "Which STL container is implemented as a dynamic array that can grow in one direction?",
    "options": {
      "A": "std::list",
      "B": "std::vector",
      "C": "std::deque",
      "D": "std::set"
    },
    "answer": "B"
  },
  {
    "question": "What is the time complexity for inserting an element at the end of a std::vector, assuming no reallocation?",
    "options": {
      "A": "O(log n)",
      "B": "O(1)",
      "C": "O(n)",
      "D": "O(n log n)"
    },
    "answer": "B"
  },
  {
    "question": "Which container would be most efficient for frequent insertions and deletions at both the front and the back?",
    "options": {
      "A": "std::vector",
      "B": "std::deque",
      "C": "std::stack",
      "D": "std::set"
    },
    "answer": "B"
  },
  {
    "question": "Which STL container is implemented as a doubly linked list?",
    "options": {
      "A": "std::vector",
      "B": "std::list",
      "    C": "std::forward_list",
      "D": "std::deque"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary difference between std::set and std::unordered_set?",
    "options": {
      "A": "std::set is faster",
      "B": "std::set is ordered (usually Red-Black Tree), while std::unordered_set is unordered (Hash Table)",
      "C": "std::set allows duplicate keys",
      "D": "std::unordered_set uses less memory"
    },
    "answer": "B"
  },
  {
    "question": "Which iterator type allows both incrementing and decrementing and can access any element in O(1)?",
    "options": {
      "A": "Forward Iterator",
      "B": "Random Access Iterator",
      "C": "Bidirectional Iterator",
      "D": "Input Iterator"
    },
    "answer": "B"
  },
  {
    "question": "What is the time complexity of searching for an element in a std::map?",
    "options": {
      "A": "O(1)",
      "B": "O(log n)",
      "C": "O(n)",
      "D": "O(n log n)"
    },
    "answer": "B"
  },
  {
    "question": "Which function is used to add an element to the end of a std::vector?",
    "options": {
      "A": "add_back()",
      "B": "push_back()",
      "C": "insert_end()",
      "D": "append()"
    },
    "answer": "B"
  },
  {
    "question": "What happens if you access a std::vector index out of bounds using the [] operator?",
    "options": {
      "A": "An exception is thrown",
      "B": "Undefined behavior occurs",
      "C": "The program exits with error code 1",
      "D": "The vector automatically grows"
    },
    "answer": "B"
  },
  {
    "question": "Which header file is required to use the std::sort algorithm?",
    "options": {
      "A": "<vector>",
      "B": "<algorithm>",
      "C": "<numeric>",
      "D": "<utility>"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of std::priority_queue?",
    "options": {
      "A": "To store elements in the order they were inserted",
      "B": "To provide constant time access to the largest (or smallest) element",
      "C": "To prevent duplicate elements",
      "D": "To sort a list in reverse"
    },
    "answer": "B"
  },
  {
    "question": "Which of these is NOT a member of the STL 'Big Three' components?",
    "options": {
      "A": "Containers",
      "B": "Pointers",
      "C": "Algorithms",
      "D": "Iterators"
    },
    "answer": "B"
  },
  {
    "question": "Which function in std::vector returns the number of elements the container can hold before needing to reallocate?",
    "options": {
      "A": "size()",
      "B": "capacity()",
      "C": "max_size()",
      "D": "length()"
    },
    "answer": "B"
  },
  {
    "question": "Which STL container does not allow duplicate keys and keeps them in sorted order?",
    "options": {
      "A": "std::multimap",
      "B": "std::set",
      "C": "std::unordered_set",
      "D": "std::vector"
    },
    "answer": "B"
  },
  {
    "question": "What does the std::vector::reserve() function do?",
    "options": {
      "A": "It changes the number of elements currently in the vector",
      "B": "It allocates memory for a specified number of elements without initializing them",
      "C": "It sorts the vector",
      "D": "It prevents the vector from being modified"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm can be used to find the first occurrence of a value in a range?",
    "options": {
      "A": "std::search()",
      "B": "std::find()",
      "C": "std::locate()",
      "D": "std::match()"
    },
    "answer": "B"
  },
  {
    "question": "What is the return type of the std::map::insert() function?",
    "options": {
      "A": "bool",
      "B": "A pair containing an iterator and a boolean",
      "C": "void",
      "D": "iterator"
    },
    "answer": "B"
  },
  {
    "question": "Which function is used to remove all elements from an STL container?",
    "options": {
      "A": "empty()",
      "B": "clear()",
      "C": "erase_all()",
      "D": "reset()"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm is used to count the number of elements that satisfy a specific condition?",
    "options": {
      "A": "std::count()",
      "B": "std::count_if()",
      "C": "std::sum_if()",
      "D": "std::check()"
    },
    "answer": "B"
  },
  {
    "question": "Which header file contains algorithms like std::accumulate and std::inner_product?",
    "options": {
      "A": "<algorithm>",
      "B": "<numeric>",
      "C": "<functional>",
      "D": "<utility>"
    },
    "answer": "B"
  },
  {
    "question": "What is the complexity of std::sort in the average case?",
    "options": {
      "A": "O(n)",
      "B": "O(n log n)",
      "C": "O(n^2)",
      "D": "O(log n)"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm is used to reorder elements such that all elements satisfying a predicate come before those that do not?",
    "options": {
      "A": "std::sort",
      "B": "std::partition",
      "C": "std::move",
      "D": "std::swap"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Functor' in C++ STL?",
    "options": {
      "A": "A built-in keyword for functions",
      "B": "An object of a class that overloads the function call operator ()",
      "C": "A pointer to a virtual function",
      "D": "A specific type of iterator"
    },
    "answer": "B"
  },
  {
    "question": "Which container adapter follows the LIFO (Last-In, First-Out) principle?",
    "options": {
      "A": "std::queue",
      "B": "std::stack",
      "C": "std::priority_queue",
      "D": "std::deque"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used to access the top element of a std::stack without removing it?",
    "options": {
      "A": "front()",
      "B": "top()",
      "C": "peek()",
      "D": "pop()"
    },
    "answer": "B"
  },
  {
    "question": "What is the difference between std::copy and std::copy_if?",
    "options": {
      "A": "std::copy_if only works with vectors",
      "B": "std::copy_if copies only elements that satisfy a specific condition (predicate)",
      "C": "std::copy is faster than std::copy_if",
      "D": "There is no functional difference"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm transforms a range by applying a specific operation to every element?",
    "options": {
      "A": "std::for_each",
      "B": "std::transform",
      "C": "std::replace",
      "D": "std::mutate"
    },
    "answer": "B"
  },
  {
    "question": "What is the underlying default container for std::stack?",
    "options": {
      "A": "std::vector",
      "B": "std::deque",
      "C": "std::list",
      "D": "std::array"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm is used to find the maximum element in a range?",
    "options": {
      "A": "std::max()",
      "B": "std::max_element()",
      "C": "std::top_element()",
      "D": "std::largest()"
    },
    "answer": "B"
  },
  {
    "question": "What does the std::unique algorithm do in a sorted range?",
    "options": {
      "A": "Deletes all duplicate elements from the container",
      "B": "Removes consecutive duplicate elements and returns an iterator to the new end",
      "C": "Sorts the elements uniquely",
      "D": "Checks if the container has duplicates"
    },
    "answer": "B"
  },
  {
    "question": "Which function is used to add an element to a std::priority_queue?",
    "options": {
      "A": "enqueue()",
      "B": "push()",
      "C": "insert()",
      "D": "add()"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm is used to merge two sorted ranges into a single sorted range?",
    "options": {
      "A": "std::combine",
      "B": "std::merge",
      "C": "std::union",
      "D": "std::concat"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of std::binary_search?",
    "options": {
      "A": "To find the index of an element in O(log n)",
      "B": "To return a boolean indicating if an element exists in a sorted range",
      "C": "To sort a range using binary logic",
      "D": "To find the frequency of an element"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm fills a range with a sequence of values starting from a given value and incrementing it?",
    "options": {
      "A": "std::fill",
      "B": "std::iota",
      "C": "std::generate",
      "D": "std::sequence"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Predicate' in the context of STL algorithms?",
    "options": {
      "A": "A function or functor that returns a boolean value",
      "B": "A variable that stores the size of a container",
      "C": "A keyword used to define templates",
      "D": "The first element of a list"
    },
    "answer": "A"
  },
  {
    "question": "Which algorithm reverses the order of elements in a range?",
    "options": {
      "A": "std::invert",
      "B": "std::reverse",
      "C": "std::flip",
      "D": "std::backwards"
    },
    "answer": "B"
  },
  {
    "question": "What does std::lower_bound return in a sorted range?",
    "options": {
      "A": "The smallest value in the range",
      "B": "An iterator to the first element not less than the given value",
      "C": "An iterator to the last element smaller than the given value",
      "D": "The index of the value"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm is used to exchange the values of two objects?",
    "options": {
      "A": "std::change",
      "B": "std::swap",
      "C": "std::replace",
      "D": "std::rotate"
    },
    "answer": "B"
  },
  {
    "question": "What is the complexity of std::for_each?",
    "options": {
      "A": "O(1)",
      "B": "O(n)",
      "C": "O(log n)",
      "D": "O(n log n)"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm returns an iterator to the first element greater than the given value in a sorted range?",
    "options": {
      "A": "std::lower_bound",
      "B": "std::upper_bound",
      "C": "std::find_greater",
      "D": "std::next_element"
    },
    "answer": "B"
  },
  {
    "question": "What is the default sorting order of std::priority_queue?",
    "options": {
      "A": "Ascending (min-heap)",
      "B": "Descending (max-heap)",
      "C": "The order of insertion",
      "D": "Random"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm is used to replace all occurrences of a specific value with another value?",
    "options": {
      "A": "std::set_value",
      "B": "std::replace",
      "C": "std::update",
      "D": "std::fill"
    },
    "answer": "B"
  },
  {
    "question": "What does std::equal_range return?",
    "options": {
      "A": "A boolean indicating if two ranges are equal",
      "B": "A pair of iterators representing the range of elements equal to a value",
      "C": "The sum of the range",
      "D": "The distance between two iterators"
    },
    "answer": "B"
  },
  {
    "question": "Which function object in <functional> performs addition?",
    "options": {
      "A": "std::sum",
      "B": "std::plus",
      "C": "std::add",
      "D": "std::accumulate"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm is used to copy a range of elements in reverse order?",
    "options": {
      "A": "std::reverse_copy",
      "B": "std::copy_backward",
      "C": "std::move_backward",
      "D": "std::back_copy"
    },
    "answer": "A"
  },
  {
    "question": "What is the complexity of std::nth_element?",
    "options": {
      "A": "O(log n)",
      "B": "O(n) on average",
      "C": "O(n^2)",
      "D": "O(n log n)"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm rotates the elements in a range such that a specific element becomes the first?",
    "options": {
      "A": "std::shift",
      "B": "std::rotate",
      "C": "std::spin",
      "D": "std::reorder"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm checks if a range is sorted?",
    "options": {
      "A": "std::check_sort",
      "B": "std::is_sorted",
      "C": "std::test_order",
      "D": "std::sorted"
    },
    "answer": "B"
  },
  {
    "question": "What is the return type of std::distance?",
    "options": {
      "A": "int",
      "B": "The difference between two iterators (usually ptrdiff_t)",
      "C": "void",
      "D": "size_t"
    },
    "answer": "B"
  },
  {
    "question": "Which header file contains predefined functors like std::less and std::greater?",
    "options": {
      "A": "<algorithm>",
      "B": "<functional>",
      "C": "<utility>",
      "D": "<numeric>"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of std::back_inserter?",
    "options": {
      "A": "To delete elements from the back of a container",
      "B": "To create an insert iterator that appends elements to the end of a container",
      "C": "To reverse the container",
      "D": "To access the back of the container"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm randomly shuffles the elements in a range?",
    "options": {
      "A": "std::mix",
      "B": "std::shuffle (or random_shuffle in older versions)",
      "C": "std::rearrange",
      "D": "std::randomize"
    },
    "answer": "B"
  },
  {
    "question": "What does std::mismatch return?",
    "options": {
      "A": "A boolean value",
      "B": "A pair of iterators to the first unequal elements in two ranges",
      "C": "The number of unequal elements",
      "D": "The index of the first error"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm is used to find the minimum and maximum elements in a range simultaneously?",
    "options": {
      "A": "std::min_max",
      "B": "std::minmax_element",
      "C": "std::find_bounds",
      "D": "std::extreme_elements"
    },
    "answer": "B"
  },
  {
    "question": "What is the complexity of std::binary_search?",
    "options": {
      "A": "O(1)",
      "B": "O(log n)",
      "C": "O(n)",
      "D": "O(n log n)"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm is used to fill a container with values generated by a function?",
    "options": {
      "A": "std::fill",
      "B": "std::generate",
      "C": "std::produce",
      "D": "std::make_range"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Stable' sort?",
    "options": {
      "A": "A sort that is faster than others",
      "B": "A sort that preserves the relative order of elements with equal keys",
      "C": "A sort that uses less memory",
      "D": "A sort that works with strings"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm performs a stable sort in the STL?",
    "options": {
      "A": "std::sort",
      "B": "std::stable_sort",
      "C": "std::fix_sort",
      "D": "std::partial_sort"
    },
    "answer": "B"
  },
  {
    "question": "Which function object performs a logical AND operation?",
    "options": {
      "A": "std::and",
      "B": "std::logical_and",
      "C": "std::bit_and",
      "D": "std::all_of"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of std::lexicographical_compare?",
    "options": {
      "A": "To check if two ranges have the same elements",
      "B": "To compare two ranges to see which is 'dictionary-order' smaller",
      "C": "To sort strings alphabetically",
      "D": "To count words in a range"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm can be used to perform a set union of two sorted ranges?",
    "options": {
      "A": "std::merge",
      "B": "std::set_union",
      "C": "std::combine_sorted",
      "D": "std::join"
    },
    "answer": "B"
  },
  {
    "question": "What is the return value of std::includes?",
    "options": {
      "A": "An iterator",
      "B": "A boolean indicating if one sorted range is a subset of another",
      "C": "The count of matching elements",
      "D": "void"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm finds the first pair of neighboring elements that are equal?",
    "options": {
      "A": "std::find_duplicate",
      "B": "std::adjacent_find",
      "C": "std::neighbor_search",
      "D": "std::equal_next"
    },
    "answer": "B"
  },
  {
    "question": "What does std::partial_sort do?",
    "options": {
      "A": "Sorts only even elements",
      "B": "Rearranges the range such that the first N elements are sorted and are the smallest in the range",
      "C": "Sorts the first half of the range",
      "D": "Sorts without using a comparator"
    },
    "answer": "B"
  },
  {
    "question": "Which function in <numeric> calculates the sum of a range and an initial value?",
    "options": {
      "A": "std::sum",
      "B": "std::accumulate",
      "C": "std::total",
      "D": "std::add_range"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm checks if all elements in a range satisfy a condition?",
    "options": {
      "A": "std::is_all",
      "B": "std::all_of",
      "C": "std::every_one",
      "D": "std::none_of"
    },
    "answer": "B"
  },
  {
    "question": "What does std::none_of return if the range is empty?",
    "options": {
      "A": "false",
      "B": "true",
      "C": "An error",
      "D": "0"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm is used to compute the difference between two sorted ranges?",
    "options": {
      "A": "std::set_difference",
      "B": "std::subtract_ranges",
      "C": "std::minus_elements",
      "D": "std::exclude"
    },
    "answer": "A"
  },
  {
    "question": "Which algorithm replaces elements that satisfy a predicate with a new value?",
    "options": {
      "A": "std::replace",
      "B": "std::replace_if",
      "C": "std::update_if",
      "D": "std::fill_if"
    },
    "answer": "B"
  },
  {
    "question": "Which iterator category is the most restricted, allowing only one-pass read-only access?",
    "options": {
      "A": "Forward Iterator",
      "B": "Input Iterator",
      "C": "Output Iterator",
      "D": "Bidirectional Iterator"
    },
    "answer": "B"
  },
  {
    "question": "Which of the following STL containers provides 'Random Access Iterators'?",
    "options": {
      "A": "std::list",
      "B": "std::deque",
      "C": "std::forward_list",
      "D": "std::map"
    },
    "answer": "B"
  },
  {
    "question": "What is the return type of the 'std::string::find()' function if the substring is not found?",
    "options": {
      "A": "-1",
      "B": "std::string::npos",
      "C": "0",
      "D": "std::string::end"
    },
    "answer": "B"
  },
  {
    "question": "Which iterator adapter is used to iterate over a container in the opposite direction?",
    "options": {
      "A": "std::back_iterator",
      "B": "std::reverse_iterator",
      "C": "std::flip_iterator",
      "D": "std::invert_iterator"
    },
    "answer": "B"
  },
  {
    "question": "What is the complexity of the 'std::distance()' function when applied to a std::list iterator?",
    "options": {
      "A": "O(1)",
      "B": "O(n)",
      "C": "O(log n)",
      "D": "O(n log n)"
    },
    "answer": "B"
  },
  {
    "question": "Which function is used to convert a std::string to a C-style string (char*)?",
    "options": {
      "A": "to_char()",
      "B": "c_str()",
      "C": "str()",
      "D": "data_ptr()"
    },
    "answer": "B"
  },
  {
    "question": "Which header provides the 'std::pair' and 'std::make_pair' utilities?",
    "options": {
      "A": "<pair>",
      "B": "<utility>",
      "C": "<tuple>",
      "D": "<algorithm>"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'std::advance()' function do?",
    "options": {
      "A": "It returns a new iterator at a specified distance",
      "B": "It increments a given iterator by a specified distance",
      "C": "It moves an element to a new container",
      "D": "It sorts the container"
    },
    "answer": "B"
  },
  {
    "question": "Which iterator category is used by std::forward_list?",
    "options": {
      "A": "Bidirectional Iterator",
      "B": "Forward Iterator",
      "C": "Random Access Iterator",
      "D": "Input Iterator"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used to obtain an iterator to the first element of a container?",
    "options": {
      "A": "front()",
      "B": "begin()",
      "C": "start()",
      "D": "first()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'std::back_inserter' an example of?",
    "options": {
      "A": "A container adapter",
      "B": "An insert iterator",
      "C": "A function object",
      "D": "A sequence container"
    },
    "answer": "B"
  },
  {
    "question": "Which member function of std::string removes all characters from the string?",
    "options": {
      "A": "reset()",
      "B": "clear()",
      "C": "erase_all()",
      "D": "empty()"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'std::prev()'?",
    "options": {
      "A": "To delete the previous element",
      "B": "To get an iterator to the n-th predecessor of a given iterator",
      "C": "To check if an iterator has a predecessor",
      "D": "To move an iterator to the beginning"
    },
    "answer": "B"
  },
  {
    "question": "Which of these is a valid way to create a 'std::pair' of an int and a string?",
    "options": {
      "A": "std::pair p(1, 'test');",
      "B": "std::make_pair(1, std::string('test'));",
      "C": "new pair(1, 'test');",
      "D": "std::pair.create(1, 'test');"
    },
    "answer": "B"
  },
  {
    "question": "Which iterator category allows for 'it1 - it2' to find the number of elements between them in O(1)?",
    "options": {
      "A": "Bidirectional Iterator",
      "B": "Random Access Iterator",
      "C": "Forward Iterator",
      "D": "Output Iterator"
    },
    "answer": "B"
  },
  {
    "question": "What does 'std::string::substr(5, 3)' return?",
    "options": {
      "A": "A string starting at index 5 with 3 characters",
      "B": "A string from index 5 to index 3",
      "C": "A string from the end of index 5",
      "D": "An error"
    },
    "answer": "A"
  },
  {
    "question": "Which utility is used to tie multiple values together into a single object in C++11 and later?",
    "options": {
      "A": "std::pair",
      "B": "std::tuple",
      "C": "std::group",
      "D": "std::collection"
    },
    "answer": "B"
  },
  {
    "question": "Which iterator category is required for the 'std::sort()' algorithm?",
    "options": {
      "A": "Bidirectional Iterator",
      "B": "Random Access Iterator",
      "C": "Forward Iterator",
      "D": "Input Iterator"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'std::next()'?",
    "options": {
      "A": "To increment a pointer",
      "B": "To get an iterator to the n-th successor of a given iterator",
      "C": "To move to the next container",
      "D": "To find the next largest value"
    },
    "answer": "B"
  },
  {
    "question": "How do you access the first element of a std::pair named 'p'?",
    "options": {
      "A": "p[0]",
      "B": "p.first",
      "C": "p.get(0)",
      "D": "p.left"
    },
    "answer": "B"
  },
  {
    "question": "Which of the following is NOT a valid iterator category?",
    "options": {
      "A": "Forward Iterator",
      "B": "Backward Iterator",
      "C": "Bidirectional Iterator",
      "D": "Random Access Iterator"
    },
    "answer": "B"
  },
  {
    "question": "What does 'std::string::append()' do?",
    "options": {
      "A": "Inserts a character at the beginning",
      "B": "Adds characters to the end of the string",
      "C": "Sorts the string alphabetically",
      "D": "Replaces the string content"
    },
    "answer": "B"
  },
  {
    "question": "Which iterator is used to read data directly from an input stream?",
    "options": {
      "A": "std::ostream_iterator",
      "B": "std::istream_iterator",
      "C": "std::stream_reader",
      "D": "std::input_stream_iterator"
    },
    "answer": "B"
  },
  {
    "question": "What is the size of an empty std::string object?",
    "options": {
      "A": "0",
      "B": "Implementation dependent (size of the string control block)",
      "C": "1 byte",
      "D": "Pointer size only"
    },
    "answer": "B"
  },
  {
    "question": "Which member function checks if a std::string is empty?",
    "options": {
      "A": "is_null()",
      "B": "empty()",
      "C": "size_zero()",
      "D": "has_content()"
    },
    "answer": "B"
  },
  {
    "question": "What is the result of 'std::string('abc') + 'def''?",
    "options": {
      "A": "A new string 'abcdef'",
      "B": "A compiler error",
      "C": "A pointer to a char array",
      "D": "'abc' with 'def' added to the original memory"
    },
    "answer": "A"
  },
  {
    "question": "Which iterator type is used by std::list?",
    "options": {
      "A": "Forward Iterator",
      "B": "Bidirectional Iterator",
      "C": "Random Access Iterator",
      "D": "Input Iterator"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'std::string::resize()'?",
    "options": {
      "A": "To change the allocated capacity only",
      "B": "To change the actual number of characters in the string",
      "C": "To sort the string",
      "D": "To compress the string"
    },
    "answer": "B"
  },
  {
    "question": "Which function allows you to get an element from a std::tuple by index?",
    "options": {
      "A": "tuple.at(i)",
      "B": "std::get<i>(tuple)",
      "C": "tuple[i]",
      "D": "tuple.first"
    },
    "answer": "B"
  },
  {
    "question": "What is the difference between 'begin()' and 'cbegin()' in C++11?",
    "options": {
      "A": "cbegin() is for C-style arrays",
      "B": "cbegin() always returns a const_iterator",
      "C": "cbegin() is faster",
      "D": "begin() is only for vectors"
    },
    "answer": "B"
  },
  {
    "question": "Which operator is used to access the element an iterator points to?",
    "options": {
      "A": "&",
      "B": "*",
      "C": "->",
      "D": "Both B and C"
    },
    "answer": "D"
  },
  {
    "question": "What is 'std::ostream_iterator' used for?",
    "options": {
      "A": "Reading from a file",
      "B": "Writing elements directly to an output stream",
      "C": "Iterating through an array",
      "D": "Managing memory streams"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used to insert a string into another at a specific position?",
    "options": {
      "A": "add()",
      "B": "insert()",
      "C": "put()",
      "D": "inject()"
    },
    "answer": "B"
  },
  {
    "question": "What does 'std::string::push_back('a')' do?",
    "options": {
      "A": "Adds the character 'a' to the front",
      "B": "Adds the character 'a' to the end",
      "C": "Replaces the last character with 'a'",
      "D": "Removes 'a' from the string"
    },
    "answer": "B"
  },
  {
    "question": "Which iterator category is used for write-only access in one pass?",
    "options": {
      "A": "Input Iterator",
      "B": "Output Iterator",
      "C": "Forward Iterator",
      "D": "Random Access Iterator"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'std::string::reserve()' function?",
    "options": {
      "A": "To change the string size",
      "B": "To pre-allocate memory to avoid multiple reallocations during growth",
      "C": "To make the string read-only",
      "D": "To clear the string"
    },
    "answer": "B"
  },
  {
    "question": "Which function in <string> converts a string to an integer?",
    "options": {
      "A": "atoi()",
      "B": "std::stoi()",
      "C": "str_to_int()",
      "D": "std::convert()"
    },
    "answer": "B"
  },
  {
    "question": "What is the complexity of accessing a character in std::string using the [] operator?",
    "options": {
      "A": "O(log n)",
      "B": "O(1)",
      "C": "O(n)",
      "D": "O(n log n)"
    },
    "answer": "B"
  },
  {
    "question": "Which function template returns the number of elements between two iterators?",
    "options": {
      "A": "std::count()",
      "B": "std::distance()",
      "C": "std::gap()",
      "D": "std::length()"
    },
    "answer": "B"
  },
  {
    "question": "How do you obtain a 'reverse_iterator' to the last element of a container?",
    "options": {
      "A": "end()",
      "B": "rbegin()",
      "C": "back()",
      "D": "rend()"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm is used to find the first character in a string that is part of a specific set?",
    "options": {
      "A": "find()",
      "B": "find_first_of()",
      "C": "search()",
      "D": "match_any()"
    },
    "answer": "B"
  },
  {
    "question": "What is the result of 'std::string::pop_back()'?",
    "options": {
      "A": "Returns the last character and removes it",
      "B": "Removes the last character (void return)",
      "C": "Removes the first character",
      "D": "Clears the string"
    },
    "answer": "B"
  },
  {
    "question": "Which iterator category is required by the 'std::reverse()' algorithm?",
    "options": {
      "A": "Forward Iterator",
      "B": "Bidirectional Iterator",
      "C": "Random Access Iterator",
      "D": "Output Iterator"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'std::string::capacity()'?",
    "options": {
      "A": "To get the current number of characters",
      "B": "To get the total number of characters the string can hold without reallocating",
      "C": "To get the maximum possible string size",
      "D": "To get the memory size in bytes"
    },
    "answer": "B"
  },
  {
    "question": "Which function converts a numeric value to a std::string?",
    "options": {
      "A": "std::to_string()",
      "B": "std::itos()",
      "C": "std::str()",
      "D": "std::convert_to_string()"
    },
    "answer": "A"
  },
  {
    "question": "What is an 'Invalidated Iterator'?",
    "options": {
      "A": "An iterator that was never initialized",
      "B": "An iterator that points to memory that is no longer valid due to container modification",
      "C": "A null pointer",
      "D": "A const iterator"
    },
    "answer": "B"
  },
  {
    "question": "Which of these is a sequence of characters that is NOT null-terminated inside std::string?",
    "options": {
      "A": "The result of data()",
      "B": "std::string contents (it may contain '\\0' as a valid character)",
      "C": "c_str()",
      "D": "None of the above"
    },
    "answer": "B"
  },
  {
    "question": "Which iterator adapter allows you to treat a range as a set of elements to be moved rather than copied?",
    "options": {
      "A": "std::back_iterator",
      "B": "std::move_iterator",
      "C": "std::transfer_iterator",
      "D": "std::shift_iterator"
    },
    "answer": "B"
  },
  {
    "question": "What does 'std::string::compare()' return if the strings are equal?",
    "options": {
      "A": "true",
      "B": "0",
      "C": "false",
      "D": "1"
    },
    "answer": "B"
  },
  {
    "question": "Which function in <iterator> returns the size of a container or array?",
    "options": {
      "A": "std::length()",
      "B": "std::size()",
      "C": "std::count()",
      "D": "std::capacity()"
    },
    "answer": "B"
  },
  {
    "question": "Which C++20 component provides a thread-safe way to wait for a specific number of threads to arrive before proceeding?",
    "options": {
      "A": "std::mutex",
      "B": "std::barrier",
      "C": "std::condition_variable",
      "D": "std::stop_token"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary purpose of the <type_traits> header in STL?",
    "options": {
      "A": "To provide mathematical constants",
      "B": "To allow compile-time inspection and manipulation of type properties",
      "C": "To handle string conversions",
      "D": "To manage thread priorities"
    },
    "answer": "B"
  },
  {
    "question": "Which C++20 class template is a thread-safe counter used to synchronize threads?",
    "options": {
      "A": "std::atomic_int",
      "B": "std::latch",
      "C": "std::thread_count",
      "D": "std::semaphore"
    },
    "answer": "B"
  },
  {
    "question": "What does 'std::is_same<T, U>::value' return?",
    "options": {
      "A": "A pointer to T",
      "B": "A boolean indicating if types T and U are identical at compile time",
      "C": "The size of the larger type",
      "D": "The memory address of U"
    },
    "answer": "B"
  },
  {
    "question": "Which STL utility introduced in C++11 is used to capture a function and its arguments for later execution?",
    "options": {
      "A": "std::call",
      "B": "std::bind",
      "C": "std::execute",
      "D": "std::capture"
    },
    "answer": "B"
  },
  {
    "question": "What is the complexity of 'std::set::count()'?",
    "options": {
      "A": "O(1)",
      "B": "O(log n)",
      "C": "O(n)",
      "D": "O(n log n)"
    },
    "answer": "B"
  },
  {
    "question": "In C++20, which header provides 'std::semaphore' for signaling between threads?",
    "options": {
      "A": "<thread>",
      "B": "<semaphore>",
      "C": "<mutex>",
      "D": "<condition_variable>"
    },
    "answer": "B"
  },
  {
    "question": "Which member function of 'std::shared_ptr' returns the number of shared_ptr instances managing the same object?",
    "options": {
      "A": "count()",
      "B": "use_count()",
      "C": "ref_count()",
      "D": "owners()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'SFINAE' in the context of STL template development?",
    "options": {
      "A": "A type of smart pointer",
      "B": "Substitution Failure Is Not An Error",
      "C": "Standard Functional Interface for Node Applications",
      "D": "Simple Fast Iteration over Native Elements"
    },
    "answer": "B"
  },
  {
    "question": "Which C++14 feature allows using 'auto' in lambda parameter lists?",
    "options": {
      "A": "Standard Lambdas",
      "B": "Generic Lambdas",
      "C": "Variadic Lambdas",
      "D": "Template Lambdas"
    },
    "answer": "B"
  },
  {
    "question": "What does 'std::decay_t<T>' do?",
    "options": {
      "A": "Slowly deletes an object",
      "B": "Applies array-to-pointer and function-to-pointer conversions and removes const/volatile qualifiers",
      "C": "Converts a type to its bitwise representation",
      "D": "Identifies if a type is a primitive"
    },
    "answer": "B"
  },
  {
    "question": "Which container is most suitable for a scenario where you need a sorted collection that allows multiple identical keys?",
    "options": {
      "A": "std::set",
      "B": "std::multiset",
      "C": "std::unordered_set",
      "D": "std::vector"
    },
    "answer": "B"
  },
  {
    "question": "Which C++17 algorithm allows for the application of an operation to a range in parallel using an execution policy?",
    "options": {
      "A": "std::for_each",
      "B": "std::transform",
      "C": "std::reduce",
      "D": "All of the above"
    },
    "answer": "D"
  },
  {
    "question": "What is the purpose of 'std::scoped_lock' introduced in C++17?",
    "options": {
      "A": "To lock a single mutex",
      "B": "To lock multiple mutexes simultaneously using a deadlock-avoidance algorithm",
      "C": "To prevent a thread from ever finishing",
      "D": "To limit the scope of a variable"
    },
    "answer": "B"
  },
  {
    "question": "Which C++20 feature allows you to restrict template arguments to those that satisfy specific requirements?",
    "options": {
      "A": "Modules",
      "B": "Concepts",
      "C": "Coroutines",
      "D": "Ranges"
    },
    "answer": "B"
  },
  {
    "question": "What is the underlying data structure of 'std::priority_queue' by default?",
    "options": {
      "A": "Linked List",
      "B": "Binary Heap",
      "C": "AVL Tree",
      "D": "Hash Table"
    },
    "answer": "B"
  },
  {
    "question": "Which header provides 'std::source_location' in C++20 for better logging?",
    "options": {
      "A": "<iostream>",
      "B": "<source_location>",
      "C": "<utility>",
      "D": "<debug>"
    },
    "answer": "B"
  },
  {
    "question": "What is 'std::enable_if' typically used for?",
    "options": {
      "A": "To enable hardware acceleration",
      "B": "To conditionally remove a function from overload resolution based on a compile-time condition",
      "C": "To turn on compiler optimizations",
      "D": "To check if a file exists"
    },
    "answer": "B"
  },
  {
    "question": "Which C++20 feature is used for pausing and resuming function execution?",
    "options": {
      "A": "Ranges",
      "B": "Coroutines",
      "C": "Concepts",
      "D": "Atomic Wait"
    },
    "answer": "B"
  },
  {
    "question": "What is the return type of 'std::unique_ptr::release()'?",
    "options": {
      "A": "void",
      "B": "A raw pointer to the managed object (and ownership is relinquished)",
      "C": "A shared_ptr",
      "D": "The object itself"
    },
    "answer": "B"
  },
  {
    "question": "Which header file contains 'std::invoke'?",
    "options": {
      "A": "<algorithm>",
      "B": "<functional>",
      "C": "<utility>",
      "D": "<memory>"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'std::string::data()' function return in C++17 and later?",
    "options": {
      "A": "A copy of the string",
      "B": "A pointer to the first character of the string (can be non-const)",
      "C": "The size of the string",
      "D": "The number of bits"
    },
    "answer": "B"
  },
  {
    "question": "Which smart pointer should be used in a parent-child relationship to prevent a circular reference that causes memory leaks?",
    "options": {
      "A": "std::shared_ptr for both",
      "B": "std::shared_ptr for parent, std::weak_ptr for child",
      "C": "std::unique_ptr for both",
      "D": "Raw pointers"
    },
    "answer": "B"
  },
  {
    "question": "What is 'std::void_t' used for in template metaprogramming?",
    "options": {
      "A": "To return nothing from a function",
      "B": "A utility to detect valid member types or expressions via SFINAE",
      "C": "To clear the memory of a template",
      "D": "To declare a void pointer"
    },
    "answer": "B"
  },
  {
    "question": "Which container adapter does NOT have an iterator?",
    "options": {
      "A": "std::stack",
      "B": "std::queue",
      "C": "std::priority_queue",
      "D": "All of the above"
    },
    "answer": "D"
  },
  {
    "question": "In C++20, which synchronization primitive allows threads to wait until a value changes?",
    "options": {
      "A": "std::atomic::wait()",
      "B": "std::mutex::wait()",
      "C": "std::thread::join()",
      "D": "std::signal()"
    },
    "answer": "A"
  },
  {
    "question": "What is the complexity of 'std::unordered_map::insert()' in the worst case?",
    "options": {
      "A": "O(1)",
      "B": "O(n)",
      "C": "O(log n)",
      "D": "O(1) amortized"
    },
    "answer": "B"
  },
  {
    "question": "Which C++17 utility represents the result of an operation that can either be a value or an error?",
    "options": {
      "A": "std::variant",
      "B": "std::expected (Standardized in C++23, often used via libraries in 17)",
      "C": "std::optional",
      "D": "std::result"
    },
    "answer": "C"
  },
  {
    "question": "Which header provides 'std::make_unique'?",
    "options": {
      "A": "<utility>",
      "B": "<memory>",
      "C": "<unique>",
      "D": "<algorithm>"
    },
    "answer": "B"
  },
  {
    "question": "What is the effect of 'std::move_if_noexcept'?",
    "options": {
      "A": "Moves an object only if its move constructor is marked noexcept; otherwise, it copies",
      "B": "Deletes the object if it throws an error",
      "C": "Moves the object and catches all exceptions",
      "D": "Moves the object only for primitive types"
    },
    "answer": "A"
  },
  {
    "question": "Which header provides atomic types for thread-safe operations without explicit mutex locking?",
    "options": {
      "A": "<mutex>",
      "B": "<atomic>",
      "C": "<thread>",
      "D": "<condition_variable>"
    },
    "answer": "B"
  },
  {
    "question": "What is the default memory order used by atomic operations in C++?",
    "options": {
      "A": "std::memory_order_relaxed",
      "B": "std::memory_order_seq_cst (Sequentially Consistent)",
      "C": "std::memory_order_acquire",
      "D": "std::memory_order_release"
    },
    "answer": "B"
  },
  {
    "question": "Which C++20 feature allows you to specify that a template parameter must be a 'floating point' or 'integral' type at compile time?",
    "options": {
      "A": "Traits",
      "B": "Concepts",
      "C": "SFINAE",
      "D": "Static Assert"
    },
    "answer": "B"
  },
  {
    "question": "What does 'std::atomic_flag' guarantee that 'std::atomic<bool>' does not?",
    "options": {
      "A": "It is faster",
      "B": "It is guaranteed to be lock-free on all platforms",
      "C": "It can store multiple values",
      "D": "It uses more memory"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm is used to find the first element in a range such that the range is partitioned according to a predicate?",
    "options": {
      "A": "std::partition",
      "B": "std::partition_point",
      "C": "std::find_if",
      "D": "std::split_point"
    },
    "answer": "B"
  },
  {
    "question": "What is 'std::uninitialized_copy' used for?",
    "options": {
      "A": "To copy elements into a container that already has data",
      "B": "To copy elements into a range of uninitialized raw memory, constructing objects as it goes",
      "C": "To delete elements without calling destructors",
      "D": "To move elements between threads"
    },
    "answer": "B"
  },
  {
    "question": "Which C++20 header introduces 'std::jthread'?",
    "options": {
      "A": "<thread>",
      "B": "<jthread>",
      "C": "<stop_token>",
      "D": "<utility>"
    },
    "answer": "A"
  },
  {
    "question": "What is the primary advantage of 'std::jthread' over 'std::thread'?",
    "options": {
      "A": "It supports cooperative cancellation and automatically joins on destruction",
      "B": "It is much faster to start",
      "C": "It can run on the GPU",
      "D": "It does not require a function to start"
    },
    "answer": "A"
  },
  {
    "question": "Which STL component is used to manage the lifetime of an object by 'counting' how many pointers refer to it?",
    "options": {
      "A": "std::unique_ptr",
      "B": "std::shared_ptr",
      "C": "std::counting_ptr",
      "D": "std::weak_ptr"
    },
    "answer": "B"
  },
  {
    "question": "In C++20, which view can be used to skip the first N elements of a range?",
    "options": {
      "A": "std::views::filter",
      "B": "std::views::drop",
      "C": "std::views::take",
      "D": "std::views::reverse"
    },
    "answer": "B"
  },
  {
    "question": "What is 'std::scoped_allocator_adaptor' used for?",
    "options": {
      "A": "To speed up small allocations",
      "B": "To allow multi-level containers (like a vector of strings) to share the same allocator",
      "C": "To prevent memory leaks in global variables",
      "D": "To allocate memory on the stack only"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm performs an 'Exclusive Prefix Sum'?",
    "options": {
      "A": "std::accumulate",
      "B": "std::exclusive_scan",
      "C": "std::partial_sum",
      "D": "std::total_scan"
    },
    "answer": "B"
  },
  {
    "question": "What is the complexity of 'std::list::sort()'?",
    "options": {
      "A": "O(n^2)",
      "B": "O(n log n)",
      "C": "O(n)",
      "D": "O(log n)"
    },
    "answer": "B"
  },
  {
    "question": "Which smart pointer casting operator is used to cast a shared_ptr of a base class to a shared_ptr of a derived class?",
    "options": {
      "A": "std::static_pointer_cast",
      "B": "std::dynamic_pointer_cast",
      "C": "std::reinterpret_pointer_cast",
      "D": "std::const_pointer_cast"
    },
    "answer": "B"
  },
  {
    "question": "What does 'std::atomic::compare_exchange_weak' return?",
    "options": {
      "A": "The current value",
      "B": "A boolean indicating if the exchange was successful",
      "C": "void",
      "D": "The new value"
    },
    "answer": "B"
  },
  {
    "question": "Which C++20 header provides 'std::endian' to check the byte order of the platform?",
    "options": {
      "A": "<utility>",
      "B": "<bit>",
      "C": "<memory>",
      "D": "<type_traits>"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm is used to shift elements in a range left or right, filling the empty spots with default values?",
    "options": {
      "A": "std::rotate",
      "B": "std::shift_left / std::shift_right",
      "C": "std::move",
      "D": "std::slide"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Transparent Comparator' in STL associative containers?",
    "options": {
      "A": "A comparator that allows comparison between different types (e.g., searching a set of strings with a string_view) without conversion",
      "B": "A comparator that is invisible to the user",
      "C": "A comparator that always returns true",
      "D": "A comparator for smart pointers"
    },
    "answer": "A"
  },
  {
    "question": "Which C++23 feature (available in some 2026 compilers) allows for a multi-dimensional array view?",
    "options": {
      "A": "std::span",
      "B": "std::mdspan",
      "C": "std::matrix",
      "D": "std::grid"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'std::destroy_at'?",
    "options": {
      "A": "To delete all objects in a container",
      "B": "To manually call the destructor of an object at a specific memory address without deallocating the memory",
      "C": "To turn off the computer",
      "D": "To clear a smart pointer"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm is used to find the smallest element in a range that is not less than a given value in a sorted container?",
    "options": {
      "A": "std::upper_bound",
      "B": "std::lower_bound",
      "C": "std::binary_search",
      "D": "std::equal_range"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary function of 'std::stop_token' in C++20?",
    "options": {
      "A": "To pause a loop",
      "B": "To provide a way to request asynchronous cancellation of a task or thread",
      "C": "To delete a pointer safely",
      "D": "To stop a container from growing"
    },
    "answer": "B"
  },
  {
    "question": "Which numeric algorithm computes the difference between adjacent elements in a range?",
    "options": {
      "A": "std::partial_sum",
      "B": "std::adjacent_difference",
      "C": "std::inner_product",
      "D": "std::accumulate"
    },
    "answer": "B"
  },
  {
    "question": "What does 'std::atomic_ref' (C++20) allow you to do?",
    "options": {
      "A": "Convert a shared_ptr to a weak_ptr",
      "B": "Perform atomic operations on a non-atomic object during its lifetime",
      "C": "Create a reference to a thread",
      "D": "Speed up memory allocation"
    },
    "answer": "B"
  },
  {
    "question": "Which C++20 container adapter provides a way to coordinate multiple threads by waiting for a count to reach zero?",
    "options": {
      "A": "std::barrier",
      "B": "std::latch",
      "C": "std::mutex",
      "D": "std::semaphore"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'std::midpoint' introduced in C++20?",
    "options": {
      "A": "To find the middle element of a vector",
      "B": "To safely compute the average of two numbers without overflow",
      "C": "To find the median of a range",
      "D": "To split a string into two"
    },
    "answer": "B"
  },
  {
    "question": "Which header file is required to use the 'std::reduce' algorithm for parallel summation?",
    "options": {
      "A": "<algorithm>",
      "B": "<numeric>",
      "C": "<execution>",
      "D": "<functional>"
    },
    "answer": "B"
  },
  {
    "question": "What is the difference between 'std::accumulate' and 'std::reduce'?",
    "options": {
      "A": "std::reduce is faster only for integers",
      "B": "std::accumulate is strictly sequential; std::reduce allows for out-of-order execution (parallelism)",
      "C": "std::reduce returns a double",
      "D": "std::accumulate does not take a custom operation"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm finds the first sequence of two identical elements in a range?",
    "options": {
      "A": "std::find",
      "B": "std::adjacent_find",
      "C": "std::search_n",
      "D": "std::unique"
    },
    "answer": "B"
  },
  {
    "question": "What is 'std::aligned_alloc' used for?",
    "options": {
      "A": "To align text in a string",
      "B": "To allocate memory with a specified alignment requirement",
      "C": "To sort data into columns",
      "D": "To fix memory leaks"
    },
    "answer": "B"
  },
  {
    "question": "In C++20, what is a 'View' in the context of the Ranges library?",
    "options": {
      "A": "A graphical representation of data",
      "B": "A range that is cheap to copy and performs lazy evaluation",
      "C": "A read-only copy of a container",
      "D": "A pointer to a vector"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm is used to determine if all elements in a range are less than a specific value?",
    "options": {
      "A": "std::none_of",
      "B": "std::all_of",
      "C": "std::any_of",
      "D": "std::count_if"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'std::make_move_iterator'?",
    "options": {
      "A": "To move an iterator to the end of a list",
      "B": "To convert an iterator into one that moves elements instead of copying them",
      "C": "To delete elements as they are iterated",
      "D": "To sort elements in reverse"
    },
    "answer": "B"
  },
  {
    "question": "Which function allows for 'In-place' construction of a std::pair within a map?",
    "options": {
      "A": "insert()",
      "B": "emplace()",
      "C": "add()",
      "D": "push()"
    },
    "answer": "B"
  },
  {
    "question": "What is the complexity of 'std::unordered_set::bucket_count()'?",
    "options": {
      "A": "O(n)",
      "B": "O(1)",
      "C": "O(log n)",
      "D": "O(n log n)"
    },
    "answer": "B"
  },
  {
    "question": "Which smart pointer casting operator should be used to remove the 'const' qualifier from a shared_ptr?",
    "options": {
      "A": "std::static_pointer_cast",
      "B": "std::const_pointer_cast",
      "C": "std::dynamic_pointer_cast",
      "D": "std::reinterpret_pointer_cast"
    },
    "answer": "B"
  },
  {
    "question": "What does 'std::atomic::is_lock_free()' return?",
    "options": {
      "A": "The current value of the atomic",
      "B": "A boolean indicating if the atomic operations are performed without using internal locks",
      "C": "The memory address",
      "D": "True if the thread is finished"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm can be used to rotate a range such that the element at 'middle' becomes the first element?",
    "options": {
      "A": "std::shift",
      "B": "std::rotate",
      "C": "std::reorder",
      "D": "std::partition"
    },
    "answer": "B"
  },
  {
    "question": "In C++20, which range adapter is used to transform elements lazily?",
    "options": {
      "A": "std::views::filter",
      "B": "std::views::transform",
      "C": "std::views::take",
      "D": "std::views::drop"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'std::tuple_element' trait?",
    "options": {
      "A": "To get the value of an element",
      "B": "To get the type of a tuple element at a specific index at compile time",
      "C": "To delete an element",
      "D": "To resize a tuple"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm is used to find the first position where a value could be inserted while maintaining sorted order?",
    "options": {
      "A": "std::upper_bound",
      "B": "std::lower_bound",
      "C": "std::find",
      "D": "std::binary_search"
    },
    "answer": "B"
  },
  {
    "question": "What is 'std::identity' (C++20) used for?",
    "options": {
      "A": "To store user login data",
      "B": "As a function object that returns its argument unchanged, often used as a default projection",
      "C": "To check if two pointers are the same",
      "D": "To verify the system clock"
    },
    "answer": "B"
  },
  {
    "question": "Which C++20 utility allows for the easy comparison of two objects using a single operator (<=>)?",
    "options": {
      "A": "The Equality Operator",
      "B": "The Spaceship Operator (Three-way comparison)",
      "C": "The Lambda Operator",
      "D": "The Logical AND"
    },
    "answer": "B"
  },
  {
    "question": "What is 'std::to_address' (C++20) used for?",
    "options": {
      "A": "To convert a string to an IP address",
      "B": "To obtain the raw pointer from a pointer-like object (like an iterator or smart pointer)",
      "C": "To find the home directory",
      "D": "To send a network packet"
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm performs an 'In-place' merge of two consecutive sorted ranges?",
    "options": {
      "A": "std::merge",
      "B": "std::inplace_merge",
      "C": "std::combine",
      "D": "std::join"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary use of 'std::as_const'?",
    "options": {
      "A": "To make a variable unchangeable forever",
      "B": "To obtain a const reference to an existing object",
      "C": "To speed up code execution",
      "D": "To hide data from threads"
    },
    "answer": "B"
  },
  {
    "question": "Which header file is required to use 'std::optional'?",
    "options": {
      "A": "<utility>",
      "B": "<optional>",
      "C": "<memory>",
      "D": "<any>"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'std::string::shrink_to_fit()'?",
    "options": {
      "A": "To delete all spaces",
      "B": "To request the removal of unused capacity from the string",
      "C": "To shorten the string to 10 characters",
      "D": "To compress the string using GZIP"
    },
    "answer": "B"
  },
  {
    "question": "Which C++20 algorithm returns the number of bits set to 1 in an integer?",
    "options": {
      "A": "std::bit_count",
      "B": "std::popcount",
      "C": "std::countl_zero",
      "D": "std::has_single_bit"
    },
    "answer": "B"
  },
  {
    "question": "What is the return type of 'std::vector::begin()'?",
    "options": {
      "A": "A raw pointer",
      "B": "An iterator to the first element",
      "C": "The value of the first element",
      "D": "void"
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
            # Escape any unclosed HTML tags in value
            safe_value = value.replace('<', '&lt;').replace('>', '&gt;')
            elements.append(Paragraph(f"{key}) {safe_value}", normal_style))
            elements.append(Spacer(1, 0.05 * inch))

        elements.append(Paragraph(f"<b>Answer:</b> {q['answer']}", normal_style))
        elements.append(Spacer(1, 0.3 * inch))

    doc.build(elements)
    print(f"✅ PDF Generated with {len(questions)} UNIQUE questions only.")


if __name__ == "__main__":
    skill = "STL"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
