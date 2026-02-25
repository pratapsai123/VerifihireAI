from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
    {
        "question": "Which of the following is considered a 'Low-level' feature of C++ that distinguishes it from languages like Java?",
        "options": {
            "A": "Garbage Collection",
            "B": "Manual Memory Management via Pointers",
            "C": "Strict Type Checking",
            "D": "Platform Independence"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of a 'Constructor' in a C++ class?",
        "options": {
            "A": "To destroy an object when it goes out of scope",
            "B": "To initialize the data members of an object when it is created",
            "C": "To allocate memory manually",
            "D": "To convert one data type to another"
        },
        "answer": "B"
    },
    {
        "question": "Which operator is used to deallocate memory that was previously allocated with 'new'?",
        "options": {
            "A": "free",
            "B": "delete",
            "C": "remove",
            "D": "destruct"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Encapsulation' in C++?",
        "options": {
            "A": "Inheriting properties from a parent class",
            "B": "Bundling data and the methods that operate on that data into a single unit (class)",
            "C": "Allowing a function to have multiple forms",
            "D": "Hiding the complexity of the hardware"
        },
        "answer": "B"
    },
    {
        "question": "Which access specifier makes class members accessible only within the class and its friends, but not to derived classes?",
        "options": {
            "A": "public",
            "B": "private",
            "C": "protected",
            "D": "internal"
        },
        "answer": "B"
    },
    {
        "question": "What is the size of a 'char' data type in C++ (standard)?",
        "options": {
            "A": "4 bytes",
            "B": "1 byte",
            "C": "2 bytes",
            "D": "8 bytes"
        },
        "answer": "B"
    },
    {
        "question": "In C++, what does the 'virtual' keyword do when applied to a member function?",
        "options": {
            "A": "It makes the function faster",
            "B": "It allows the function to be overridden in derived classes and enables runtime polymorphism",
            "C": "It prevents the function from being modified",
            "D": "It makes the function private"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Pointer' in C++?",
        "options": {
            "A": "A variable that stores a numerical value",
            "B": "A variable that stores the memory address of another variable",
            "C": "A link to a website",
            "D": "A type of loop"
        },
        "answer": "B"
    },
    {
        "question": "Which of the following is the correct way to declare a pointer to an integer?",
        "options": {
            "A": "int p*;",
            "B": "int *p;",
            "C": "pointer <int> p;",
            "D": "int &p;"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Function Overloading'?",
        "options": {
            "A": "Calling a function too many times",
            "B": "Defining multiple functions with the same name but different parameter lists",
            "C": "A function that returns multiple values",
            "D": "A function that calls itself"
        },
        "answer": "B"
    },
    {
        "question": "Which header file is required for input and output operations in C++?",
        "options": {
            "A": "<stdio.h>",
            "B": "<iostream>",
            "C": "<conio.h>",
            "D": "<stdlib.h>"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'this' pointer in C++?",
        "options": {
            "A": "A pointer to the global namespace",
            "B": "A pointer to the current instance of the class",
            "C": "A pointer to the previous object created",
            "D": "A pointer to the main function"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Inheritance'?",
        "options": {
            "A": "Hiding data from the user",
            "B": "The mechanism by which one class acquires the properties and behaviors of another class",
            "C": "Creating multiple objects of the same class",
            "D": "A way to speed up compilation"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Pure Virtual Function'?",
        "options": {
            "A": "A function with no name",
            "B": "A virtual function assigned to 0 (e.g., virtual void func() = 0;), making the class abstract",
            "C": "A function that returns a boolean",
            "D": "A function defined in a header file"
        },
        "answer": "B"
    },
    {
        "question": "Which of these features of C++ is used to handle runtime errors?",
        "options": {
            "A": "Templates",
            "B": "Exception Handling (try-catch blocks)",
            "C": "Pointers",
            "D": "Constructors"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Scope Resolution Operator' in C++?",
        "options": {
            "A": "->",
            "B": "::",
            "C": ".",
            "D": ":"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Namespace' in C++?",
        "options": {
            "A": "To allocate memory",
            "B": "To group code and prevent naming collisions between different libraries",
            "C": "To define the class hierarchy",
            "D": "To manage the hard drive space"
        },
        "answer": "B"
    },
    {
        "question": "What is 'RAII' (Resource Acquisition Is Initialization)?",
        "options": {
            "A": "A way to write comments",
            "B": "A programming idiom where resource management is tied to object lifetime (constructor/destructor)",
            "C": "A type of compiler optimization",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "Which keyword is used to prevent an object from being modified?",
        "options": {
            "A": "static",
            "B": "const",
            "C": "final",
            "D": "volatile"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Friend Class' in C++?",
        "options": {
            "A": "A class that is easy to use",
            "B": "A class that can access the private and protected members of the class in which it is declared as a friend",
            "C": "A class that inherits from another",
            "D": "A class defined in the same file"
        },
        "answer": "B"
    },
    {
        "question": "What is the difference between 'struct' and 'class' in C++?",
        "options": {
            "A": "Structs cannot have methods",
            "B": "Default access for members is public in a struct and private in a class",
            "C": "Structs are stored on the stack only",
            "D": "There is no difference"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Multiple Inheritance'?",
        "options": {
            "A": "Inheriting from the same class twice",
            "B": "A class inheriting from more than one base class",
            "C": "A parent class with multiple children",
            "D": "An object with multiple names"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Diamond Problem' in C++?",
        "options": {
            "A": "A memory leak",
            "B": "Ambiguity that arises when a class inherits from two classes that both inherit from a common base class",
            "C": "A syntax error in loops",
            "D": "A problem with expensive hardware"
        },
        "answer": "B"
    },
    {
        "question": "How do you solve the 'Diamond Problem' in C++?",
        "options": {
            "A": "Using pointers",
            "B": "Using virtual inheritance",
            "C": "Deleting one of the classes",
            "D": "Renaming the functions"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Dynamic Casting'?",
        "options": {
            "A": "Changing data types very fast",
            "B": "A type of cast used at runtime to safely cast a base class pointer/reference to a derived type",
            "C": "Converting a string to an int",
            "D": "A compiler error"
        },
        "answer": "B"
    },
    {
        "question": "Which C++ standard introduced 'Smart Pointers' and 'Auto' keyword?",
        "options": {
            "A": "C++98",
            "B": "C++11",
            "C": "C++17",
            "D": "C++20"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'std::unique_ptr'?",
        "options": {
            "A": "To create a shared object",
            "B": "To own a resource exclusively and ensure it is deleted when the pointer goes out of scope",
            "C": "To count the number of references",
            "D": "To speed up the network"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Polymorphism'?",
        "options": {
            "A": "Writing code in many languages",
            "B": "The ability of a single interface to represent different underlying forms (data types or functions)",
            "C": "A way to encrypt data",
            "D": "Having many constructors"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is 'Compile-time Polymorphism'?",
        "options": {
            "A": "Virtual Functions",
            "B": "Function Overloading and Templates",
            "C": "Inheritance",
            "D": "Dynamic Binding"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Rule of Three' in C++?",
        "options": {
            "A": "Always use three variables",
            "B": "If you define a Destructor, Copy Constructor, or Copy Assignment Operator, you likely need all three",
            "C": "Three classes per file",
            "D": "Maximum three levels of inheritance"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Rule of Five' (C++11 and later)?",
        "options": {
            "A": "Adds Move Constructor and Move Assignment Operator to the Rule of Three",
            "B": "Defines five ways to create an object",
            "C": "A security standard",
            "D": "A database rule"
        },
        "answer": "A"
    },
    {
        "question": "What is a 'Memory Leak' in C++?",
        "options": {
            "A": "The computer running out of RAM",
            "B": "Allocating memory on the heap and failing to deallocate it, making it unavailable to the system",
            "C": "A broken RAM stick",
            "D": "A virus"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'inline' keyword suggest to the compiler?",
        "options": {
            "A": "Make the function private",
            "B": "Replace the function call with the actual function code to reduce overhead",
            "C": "Compile the code in one line",
            "D": "Ignore errors"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Copy Constructor'?",
        "options": {
            "A": "A constructor that copies the file",
            "B": "A constructor that initializes an object using another object of the same class",
            "C": "A constructor that returns a copy",
            "D": "A default constructor"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Deep Copy' vs 'Shallow Copy'?",
        "options": {
            "A": "Deep copy is for integers; Shallow is for strings",
            "B": "Shallow copy copies pointers; Deep copy allocates new memory and copies the actual data",
            "C": "There is no difference",
            "D": "Deep copy is only in C++20"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is a 'Standard Template Library' (STL) container?",
        "options": {
            "A": "int",
            "B": "std::vector",
            "C": "class",
            "D": "pointer"
        },
        "answer": "B"
    },
    {
        "question": "What is an 'Iterator' in STL?",
        "options": {
            "A": "A loop counter",
            "B": "An object that points to an element inside a container and can be used to traverse it",
            "C": "A type of primary key",
            "D": "A sorting algorithm"
        },
        "answer": "B"
    },
    {
        "question": "What is the difference between 'std::vector' and 'std::array'?",
        "options": {
            "A": "Vector is faster",
            "B": "Vector is dynamic (can change size); Array is fixed-size",
            "C": "Array is only for characters",
            "D": "Vector is older"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'std::map' in C++?",
        "options": {
            "A": "To draw a map on the screen",
            "B": "To store key-value pairs where keys are unique and sorted",
            "C": "To store a list of numbers",
            "D": "To manage threads"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Template' in C++?",
        "options": {
            "A": "A sample code file",
            "B": "A way to write generic code that works with any data type",
            "C": "A UI theme",
            "D": "A type of sharding"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Destructor'?",
        "options": {
            "A": "A virus that deletes files",
            "B": "A special member function that is called when an object is destroyed to release resources",
            "C": "The main function",
            "D": "A type of pointer"
        },
        "answer": "B"
    },
    {
        "question": "Which operator is used to access members of a class through a pointer?",
        "options": {
            "A": ".",
            "B": "->",
            "C": "::",
            "D": "*"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Reference' in C++?",
        "options": {
            "A": "A link to a library",
            "B": "An alias for an existing variable",
            "C": "A type of pointer that can be null",
            "D": "A comment"
        },
        "answer": "B"
    },
    {
        "question": "Can a 'Reference' be reassigned to refer to another object after initialization?",
        "options": {
            "A": "Yes",
            "B": "No",
            "C": "Only if it is a const reference",
            "D": "Only in C++20"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Lvalue' vs 'Rvalue'?",
        "options": {
            "A": "Lvalue is Left; Rvalue is Right",
            "B": "Lvalue refers to a persistent object (memory location); Rvalue refers to a temporary value",
            "C": "Lvalue is for strings; Rvalue for ints",
            "D": "There is no difference"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::move' used for?",
        "options": {
            "A": "To move a file",
            "B": "To cast an lvalue to an rvalue to enable move semantics (transferring ownership)",
            "C": "To restart the computer",
            "D": "To sort a vector"
        },
        "answer": "B"
    },
    {
        "question": "What is 'C-style String' vs 'std::string'?",
        "options": {
            "A": "C-style is a null-terminated char array; std::string is a dynamic class",
            "B": "They are identical",
            "C": "std::string is only for Windows",
            "D": "C-style is safer"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of 'std::cout'?",
        "options": {
            "A": "To read input",
            "B": "To print output to the standard console",
            "C": "To count the number of lines",
            "D": "To exit the program"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Abstraction'?",
        "options": {
            "A": "Writing complex code",
            "B": "Hiding internal implementation details and showing only necessary features of an object",
            "C": "A type of sharding",
            "D": "A database index"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 1: Which keyword is used to start a C++ program?",
        "options": {
            "A": "start",
            "B": "main",
            "C": "init",
            "D": "run"
        },
        "answer": "B"
    },
    {
        "question": "What is the time complexity of searching for an element in a 'std::set'?",
        "options": {
            "A": "O(1)",
            "B": "O(log n)",
            "C": "O(n)",
            "D": "O(n log n)"
        },
        "answer": "B"
    },
    {
        "question": "What is the underlying data structure typically used to implement 'std::map'?",
        "options": {
            "A": "Hash Table",
            "B": "Red-Black Tree (Self-balancing BST)",
            "C": "Linked List",
            "D": "Dynamic Array"
        },
        "answer": "B"
    },
    {
        "question": "Which C++11 feature allows a function to accept a variable number of arguments of different types?",
        "options": {
            "A": "Templates",
            "B": "Variadic Templates",
            "C": "Macros",
            "D": "Function Overloading"
        },
        "answer": "B"
    },
    {
        "question": "What does 'RAII' ensure during an exception?",
        "options": {
            "A": "The program runs faster",
            "B": "Resources are automatically released as the stack unwinds and destructors are called",
            "C": "The exception is ignored",
            "D": "The database is backed up"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Lambda Expression' in C++?",
        "options": {
            "A": "A new data type",
            "B": "An anonymous function defined directly inside a block of code",
            "C": "A type of loop",
            "D": "A mathematical constant"
        },
        "answer": "B"
    },
    {
        "question": "In a Lambda [capture](params){body}, what does '[=]' signify?",
        "options": {
            "A": "Capture nothing",
            "B": "Capture all local variables by value",
            "C": "Capture all local variables by reference",
            "D": "Compare two variables"
        },
        "answer": "B"
    },
    {
        "question": "In a Lambda, what does '[&]' signify?",
        "options": {
            "A": "Capture by value",
            "B": "Capture all local variables by reference",
            "C": "Address of the function",
            "D": "Logical AND operation"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::shared_ptr'?",
        "options": {
            "A": "A pointer that can only be used by one object",
            "B": "A smart pointer that maintains a reference count to share ownership of a resource",
            "C": "A pointer to a shared network drive",
            "D": "A pointer that never deletes data"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::weak_ptr' used for?",
        "options": {
            "A": "To create a temporary object",
            "B": "To observe a shared_ptr without increasing its reference count, preventing circular dependencies",
            "C": "To point to deleted memory",
            "D": "To speed up the CPU"
        },
        "answer": "B"
    },
    {
        "question": "Which STL container is best for frequent insertions and deletions at both ends?",
        "options": {
            "A": "std::vector",
            "B": "std::deque",
            "C": "std::set",
            "D": "std::array"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'override' keyword used for in C++11?",
        "options": {
            "A": "To rename a function",
            "B": "To explicitly state that a member function is intended to override a virtual function in a base class",
            "C": "To delete a base class function",
            "D": "To increase function priority"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'final' keyword used for in C++ class definitions?",
        "options": {
            "A": "To mark the end of the file",
            "B": "To prevent a class from being inherited or a virtual function from being overridden",
            "C": "To declare a constant",
            "D": "To close the program"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Move Semantics'?",
        "options": {
            "A": "Moving code to a different file",
            "B": "Transferring resources from a temporary object to a new one instead of copying them",
            "C": "Moving a variable to the cloud",
            "D": "A type of sorting"
        },
        "answer": "B"
    },
    {
        "question": "Which operator is the 'Move Assignment Operator'?",
        "options": {
            "A": "Type& operator=(const Type&)",
            "B": "Type& operator=(Type&&)",
            "C": "Type operator+(Type&)",
            "D": "void operator*()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Template Specialization'?",
        "options": {
            "A": "Deleting a template",
            "B": "Providing a custom implementation of a template for a specific data type",
            "C": "Using a template for numbers only",
            "D": "A security feature"
        },
        "answer": "B"
    },
    {
        "question": "Which STL algorithm is used to sort a range of elements?",
        "options": {
            "A": "std::arrange()",
            "B": "std::sort()",
            "C": "std::order()",
            "D": "std::group()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::unordered_map' based on?",
        "options": {
            "A": "Balanced Tree",
            "B": "Hash Table",
            "C": "Heap",
            "D": "Linked List"
        },
        "answer": "B"
    },
    {
        "question": "What is the average time complexity for insertion in a 'std::unordered_map'?",
        "options": {
            "A": "O(log n)",
            "B": "O(1)",
            "C": "O(n)",
            "D": "O(n^2)"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'constexpr'?",
        "options": {
            "A": "To declare a constant",
            "B": "To indicate that a value or function can be evaluated at compile-time",
            "C": "To speed up internet speed",
            "D": "To manage threads"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Functor' in C++?",
        "options": {
            "A": "A funny function",
            "B": "An object of a class that overloads the operator() so it can be called like a function",
            "C": "A type of loop",
            "D": "A pointer to a class"
        },
        "answer": "B"
    },
    {
        "question": "What is 'ADL' (Argument Dependent Lookup)?",
        "options": {
            "A": "Looking for arguments in a list",
            "B": "A set of rules for finding functions based on the namespaces of their arguments",
            "C": "A database query",
            "D": "A type of sorting"
        },
        "answer": "B"
    },
    {
        "question": "Which C++17 feature allows you to decompose a pair or tuple into individual variables?",
        "options": {
            "A": "Auto variables",
            "B": "Structured Bindings",
            "C": "Template deduction",
            "D": "Variadic expansion"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::optional' (C++17) used for?",
        "options": {
            "A": "To make a function optional",
            "B": "A wrapper that may or may not contain a value, replacing the use of null pointers for results",
            "C": "A type of unit test",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::variant' (C++17)?",
        "options": {
            "A": "A virus",
            "B": "A type-safe union that can hold one value from a set of predefined types",
            "C": "A global variable",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What are 'Concepts' in C++20?",
        "options": {
            "A": "Abstract ideas",
            "B": "Named compile-time predicates used to constrain template arguments",
            "C": "A type of inheritance",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What are 'Coroutines' in C++20?",
        "options": {
            "A": "Functions that run on multiple cores",
            "B": "Functions that can suspend execution to be resumed later, useful for async tasks",
            "C": "A type of loop",
            "D": "A database engine"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::span' (C++20)?",
        "options": {
            "A": "The duration of the program",
            "B": "A non-owning view over a contiguous sequence of objects (like a pointer + length)",
            "C": "A type of sharding",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "What is 'CRTP' (Curiously Recurring Template Pattern)?",
        "options": {
            "A": "A pattern for recurring billing",
            "B": "A C++ idiom where a class derives from a template instantiation of its own name",
            "C": "A bug in the compiler",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "What is 'SFINAE' (Substitution Failure Is Not An Error)?",
        "options": {
            "A": "A programming error",
            "B": "A template metaprogramming principle where invalid template substitutions are ignored during overload resolution",
            "C": "A security scan result",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::async' used for?",
        "options": {
            "A": "To update the system",
            "B": "To run a function asynchronously, potentially in a new thread, and return a std::future",
            "C": "To sync the database",
            "D": "To pause the program"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::future'?",
        "options": {
            "A": "A plan for the app",
            "B": "An object that provides a mechanism to access the result of an asynchronous operation",
            "C": "A time-traveling variable",
            "D": "A type of log"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Race Condition' in multi-threading?",
        "options": {
            "A": "Threads competing for speed",
            "B": "When multiple threads access shared data concurrently and at least one is a write, leading to unpredictable results",
            "C": "A type of sharding",
            "D": "A security attack"
        },
        "answer": "B"
    },
    {
        "question": "Which C++ header provides 'std::mutex' for thread synchronization?",
        "options": {
            "A": "<thread>",
            "B": "<mutex>",
            "C": "<lock>",
            "(D)": "<sync>"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::lock_guard'?",
        "options": {
            "A": "A security guard",
            "B": "A scoped mutex wrapper that automatically unlocks the mutex when it goes out of scope (RAII)",
            "C": "A type of firewall",
            "D": "A database index"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Perfect Forwarding'?",
        "options": {
            "A": "Sending an email correctly",
            "B": "A technique using templates and std::forward to preserve the lvalue/rvalue nature of arguments passed to other functions",
            "C": "A performance report",
            "D": "A type of sharding"
        },
        "answer": "B"
    },
    {
        "question": "Which STL algorithm checks if all elements in a range satisfy a predicate?",
        "options": {
            "A": "std::check_all()",
            "B": "std::all_of()",
            "C": "std::test_all()",
            "D": "std::match_all()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::bind' used for?",
        "options": {
            "A": "To bind a book",
            "B": "To create a new function object by binding arguments to an existing function",
            "C": "To link a database",
            "D": "To secure a network"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Explicit Constructor'?",
        "options": {
            "A": "A constructor with a name",
            "B": "A constructor marked with 'explicit' to prevent implicit type conversions",
            "C": "A constructor that is public",
            "D": "A constructor for strings"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Copy Elision'?",
        "options": {
            "A": "Deleting a copy",
            "B": "A compiler optimization that eliminates unnecessary copying of objects",
            "C": "A memory leak",
            "D": "A type of sharding"
        },
        "answer": "B"
    },
    {
        "question": "What is 'RVO' (Return Value Optimization)?",
        "options": {
            "A": "A type of copy elision where the compiler avoids copying a local object being returned from a function",
            "B": "A database index",
            "C": "A network protocol",
            "D": "A security scan"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of 'std::tuple'?",
        "options": {
            "A": "To store only two values",
            "B": "To store a fixed-size collection of heterogeneous values",
            "C": "To store a list of numbers",
            "D": "To manage threads"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::any' (C++17)?",
        "options": {
            "A": "A variable that can be anything",
            "B": "A type-safe container for single values of any type",
            "C": "A performance report",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::filesystem' library (C++17)?",
        "options": {
            "A": "A database engine",
            "B": "A standard library for performing operations on file systems (paths, directories, files)",
            "C": "A type of sharding",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::string_view' (C++17)?",
        "options": {
            "A": "A way to see strings",
            "B": "A non-owning reference to a string or a portion of a string, optimizing string passing",
            "C": "A type of unit test",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Generic Lambda' (C++14)?",
        "options": {
            "A": "A lambda for all languages",
            "B": "A lambda that uses 'auto' for its parameters, making it a template",
            "C": "A type of loop",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'decltype' keyword used for?",
        "options": {
            "A": "To declare a type",
            "B": "To inspect the declared type of an expression at compile-time",
            "C": "To delete a type",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Initialiser List'?",
        "options": {
            "A": "A list of developers",
            "B": "A mechanism to initialize objects with a list of values using '{}' syntax",
            "C": "A type of sharding",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Type Aliasing' (using keyword)?",
        "options": {
            "A": "Giving a person a nickname",
            "B": "A way to create a new name for an existing type (alternative to typedef)",
            "C": "A type of inheritance",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'NVI' (Non-Virtual Interface) pattern?",
        "options": {
            "A": "A UI theme",
            "B": "A pattern where a public non-virtual function calls a private virtual function to control class behavior",
            "C": "A type of sharding",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 2: Which C++20 feature provides a way to write modular code instead of using header files?",
        "options": {
            "A": "Packages",
            "B": "Modules",
            "C": "Libraries",
            "D": "Components"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Memory Model' in C++11 and later?",
        "options": {
            "A": "The physical layout of RAM sticks",
            "B": "A set of rules defining how multiple threads interact with memory and when changes made by one thread are visible to others",
            "C": "A type of garbage collection",
            "D": "The size of the stack"
        },
        "answer": "B"
    },
    {
        "question": "What is an 'Atomic Operation' in C++?",
        "options": {
            "A": "A very small operation",
            "B": "An operation that is guaranteed to execute as a single, indivisible unit without interruption from other threads",
            "C": "A mathematical calculation",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "Which header provides atomic types like 'std::atomic<int>'?",
        "options": {
            "A": "<mutex>",
            "B": "<atomic>",
            "C": "<thread>",
            "D": "<future>"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Lock-free Programming'?",
        "options": {
            "A": "Programming without a password",
            "B": "A design approach using atomic operations instead of mutexes to ensure multiple threads can make progress without blocking",
            "C": "A type of sharding",
            "D": "A performance bug"
        },
        "answer": "B"
    },
    {
        "question": "What is 'False Sharing' in multi-threaded C++ performance?",
        "options": {
            "A": "Giving the wrong code to a teammate",
            "B": "A performance issue where threads on different cores update independent variables that reside on the same cache line",
            "C": "A type of unit test",
            "D": "A memory leak"
        },
        "answer": "B"
    },
    {
        "question": "Which C++17 attribute can be used to prevent 'False Sharing' by aligning data to cache lines?",
        "options": {
            "A": "[[nodiscard]]",
            "B": "alignas()",
            "C": "[[maybe_unused]]",
            "D": "[[fallthrough]]"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Deadlock'?",
        "options": {
            "A": "A broken lock on the server",
            "B": "A situation where two or more threads are blocked forever, each waiting for the other to release a resource",
            "C": "A security attack",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Which C++17 feature helps avoid deadlocks by locking multiple mutexes simultaneously?",
        "options": {
            "A": "std::lock_guard",
            "B": "std::scoped_lock",
            "C": "std::unique_lock",
            "D": "std::mutex::lock_all"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Strict Aliasing Rule' in C++?",
        "options": {
            "A": "The rule that variables must have unique names",
            "B": "A compiler assumption that pointers of different types do not point to the same memory location (allowing optimizations)",
            "C": "A security policy",
            "D": "A type of inheritance"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Placement New'?",
        "options": {
            "A": "Finding a place for new code",
            "B": "A version of 'new' that allows you to construct an object at a specific, pre-allocated memory address",
            "C": "A type of unit test",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Double-Checked Locking' and why was it problematic before C++11?",
        "options": {
            "A": "Checking the password twice",
            "B": "A pattern to reduce overhead that was unsafe due to lack of a defined memory model and reordering by compilers/CPUs",
            "C": "A type of sharding",
            "D": "A performance bug"
        },
        "answer": "B"
    },
    {
        "question": "Which keyword ensures that a variable is always read from memory and prevents compiler optimizations from caching its value?",
        "options": {
            "A": "static",
            "B": "volatile",
            "C": "const",
            "D": "mutable"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Template Metaprogramming' (TMP)?",
        "options": {
            "A": "Designing UI templates",
            "B": "A technique where the compiler executes code at compile-time to generate source code or perform calculations",
            "C": "A type of unit test",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::enable_if' used for?",
        "options": {
            "A": "To enable a function at runtime",
            "B": "A TMP tool used to conditionally remove functions from the overload set based on type traits (SFINAE)",
            "C": "To style the code",
            "D": "To manage threads"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Type Trait' in C++?",
        "options": {
            "A": "A person's character",
            "B": "A template-based interface used to query or modify properties of types at compile-time (e.g., std::is_integral)",
            "C": "A database index",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Small Object Optimization' (SSO) in std::string?",
        "options": {
            "A": "Deleting small strings",
            "B": "Storing short strings directly inside the string object itself to avoid heap allocation",
            "C": "A type of sharding",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Data Cache Miss'?",
        "options": {
            "A": "The database being offline",
            "B": "When the CPU looks for data in the cache and doesn't find it, forcing a slower access to main RAM",
            "C": "A security scan",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "How does 'Data Locality' improve performance?",
        "options": {
            "A": "By using local variables only",
            "B": "By keeping related data close together in memory to maximize CPU cache hits",
            "C": "By moving to a new office",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Vectorization' (SIMD)?",
        "options": {
            "A": "Using std::vector for everything",
            "B": "Single Instruction, Multiple Data; performing the same operation on multiple data points simultaneously using CPU registers",
            "C": "A type of sharding",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Memory Alignment'?",
        "options": {
            "A": "Aligning the computer on the desk",
            "B": "The requirement that data addresses be multiples of a certain power of two for efficient CPU access",
            "C": "A security certificate",
            "D": "A database design"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Vtable' (Virtual Method Table)?",
        "options": {
            "A": "A table for virtual reality",
            "B": "A mechanism used by C++ to support dynamic dispatch (runtime polymorphism) by storing pointers to virtual functions",
            "C": "A database table",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Vptr' (Virtual Pointer)?",
        "options": {
            "A": "A pointer to a virtual world",
            "B": "A hidden pointer inside an object that points to the class's Vtable",
            "C": "A type of sharding",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is the overhead of a 'Virtual Function' call?",
        "options": {
            "A": "Zero overhead",
            "B": "A small runtime cost due to pointer indirection (looking up the address in the Vtable)",
            "C": "It doubles the memory usage",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Inline Expansion'?",
        "options": {
            "A": "Writing long lines of code",
            "B": "The compiler replacing a function call with the function body to eliminate call overhead",
            "C": "A type of sharding",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Undefined Behavior' (UB) in C++?",
        "options": {
            "A": "A behavior that is not yet defined",
            "B": "Code for which the C++ standard imposes no requirements; the result is completely unpredictable (e.g., out-of-bounds access)",
            "C": "A type of unit test",
            "D": "A security scan result"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Dangling Pointer'?",
        "options": {
            "A": "A pointer that is very long",
            "B": "A pointer that continues to point to a memory location after the storage has been deallocated",
            "C": "A type of unit test",
            "D": "A security vulnerability"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Buffer Overflow'?",
        "options": {
            "A": "The server running out of space",
            "B": "Writing data past the end of an allocated buffer, often leading to crashes or security exploits",
            "C": "A performance report",
            "D": "A database error"
        },
        "answer": "B"
    },
    {
        "question": "Which tool is commonly used to detect memory leaks and memory errors in C++?",
        "options": {
            "A": "Valgrind",
            "B": "Notepad++",
            "C": "Calculator",
            "D": "Excel"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Condition Variable' in multi-threading?",
        "options": {
            "A": "A variable that changes with the weather",
            "B": "A synchronization primitive used to block a thread until another thread notifies it that a condition is met",
            "C": "A type of sharding",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Spurious Wakeup'?",
        "options": {
            "A": "A developer waking up early",
            "B": "A situation where a thread waiting on a condition variable wakes up without any notification (requiring a while-loop check)",
            "C": "A performance report",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Lock Contention'?",
        "options": {
            "A": "A fight over a key",
            "B": "Performance degradation that occurs when multiple threads frequently attempt to acquire the same lock",
            "C": "A type of sharding",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Atomic Read-Modify-Write' (RMW)?",
        "options": {
            "A": "Reading a book while writing",
            "B": "A class of atomic operations that perform a read, a calculation, and a write as a single atomic step (e.g., fetch_add)",
            "C": "A security scan",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Compare-and-Swap' (CAS)?",
        "options": {
            "A": "Comparing two variables and swapping them",
            "B": "An atomic instruction used in multithreading to achieve synchronization; it updates a value only if it matches an expected value",
            "C": "A type of sorting",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Instruction Reordering'?",
        "options": {
            "A": "Moving code to different files",
            "B": "A compiler or CPU optimization where instructions are executed in a different order than written to improve performance",
            "C": "A type of sharding",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Memory Barrier' (Memory Fence)?",
        "options": {
            "A": "A physical wall around the RAM",
            "B": "An instruction that prevents the CPU or compiler from reordering memory operations across the barrier",
            "C": "A type of sharding",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "Which memory order in 'std::atomic' is the strictest (most conservative)?",
        "options": {
            "A": "memory_order_relaxed",
            "B": "memory_order_seq_cst (Sequentially Consistent)",
            "C": "memory_order_acquire",
            "D": "memory_order_release"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Pimpl Idiom' (Pointer to Implementation)?",
        "options": {
            "A": "A funny name for code",
            "B": "A C++ technique used to hide implementation details and reduce compilation dependencies by using a pointer to a private struct",
            "C": "A type of sharding",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Link-Time Optimization' (LTO)?",
        "options": {
            "A": "Optimizing while writing code",
            "B": "A type of compiler optimization that analyzes the entire program across different object files during the linking stage",
            "C": "A performance report",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Dead Code Elimination'?",
        "options": {
            "A": "Deleting code that is old",
            "B": "A compiler optimization that removes code that does not affect the program results",
            "C": "A type of sharding",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Tail Call Optimization' (TCO)?",
        "options": {
            "A": "A way to write shorter code",
            "B": "A compiler optimization where a function call at the end of another function is replaced by a jump to save stack space",
            "C": "A performance report",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Copy-on-Write' (COW) in legacy std::string?",
        "options": {
            "A": "Writing data twice",
            "B": "An optimization where a copy of an object initially shares the same memory as the original and is only copied when modified",
            "C": "A performance report",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'ABI' (Application Binary Interface)?",
        "options": {
            "A": "A type of coding language",
            "B": "The interface between two binary program modules (often at the library or OS level)",
            "C": "A security certificate",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Name Mangling'?",
        "options": {
            "A": "Making code look bad",
            "B": "The process by which C++ compilers encode function and variable names into unique strings to support overloading",
            "C": "A type of sharding",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "Which keyword is used to disable C++ name mangling for a function (making it compatible with C)?",
        "options": {
            "A": "extern \"C\"",
            "B": "static",
            "C": "inline",
            "D": "no_mangle"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Translation Unit'?",
        "options": {
            "A": "A team of translators",
            "B": "The source code file plus all the headers it includes, treated as a single unit by the compiler",
            "C": "A database index",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Static Assertion' (static_assert)?",
        "options": {
            "A": "A regular if-statement",
            "B": "A check performed at compile-time that generates an error if a condition is false",
            "C": "A runtime check",
            "D": "A type of loop"
        },
        "answer": "B"
    },
    {
        "question": "What is 'RTTI' (Run-Time Type Information)?",
        "options": {
            "A": "A type of unit test",
            "B": "A mechanism that exposes information about an object's data type at runtime (e.g., typeid)",
            "C": "A security scanner",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Opaque Pointer'?",
        "options": {
            "A": "A pointer that is hard to see",
            "B": "A pointer to a type that is not fully defined in the header, used to hide implementation details",
            "C": "A type of sharding",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::thread::join()'?",
        "options": {
            "A": "Joining a thread to a group",
            "B": "A command that blocks the calling thread until the specific thread finishes execution",
            "C": "A performance report",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 3: What is 'Stack Overflow' in C++?",
        "options": {
            "A": "A popular website",
            "B": "An error that occurs when a program uses more stack memory than is allocated (often due to deep recursion)",
            "C": "A performance report",
            "D": "A type of sharding"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary advantage of C++20 'Modules' over traditional header files?",
        "options": {
            "A": "They make the code more colorful",
            "B": "Faster compilation times by avoiding repeated parsing of the same header text in every translation unit",
            "C": "They automatically delete unused variables",
            "D": "They allow the use of Python libraries"
        },
        "answer": "B"
    },
    {
        "question": "Which C++20 feature allows for the functional-style composition of algorithms (e.g., filtering and transforming)?",
        "options": {
            "A": "Coroutines",
            "B": "Ranges (std::ranges)",
            "C": "Concepts",
            "D": "Modules"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'std::views::filter' do in a C++20 range expression?",
        "options": {
            "A": "It deletes all elements from a vector",
            "B": "It creates a lazy view containing only elements that satisfy a specific predicate",
            "C": "It sorts the data in reverse",
            "D": "It encrypts the range"
        },
        "answer": "B"
    },
    {
        "question": "In C++20, what is the 'Spaceship Operator' (<=>) used for?",
        "options": {
            "A": "Launching a thread to a new core",
            "B": "Three-way comparison (less, equal, or greater) in a single operation",
            "C": "Moving an object to a new memory address",
            "D": "A type of bitwise shift"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::stop_token' used for in C++20?",
        "options": {
            "A": "To stop the program immediately",
            "B": "To provide a thread-safe way to request that a running thread stop execution",
            "C": "To pause a loop",
            "D": "To manage database tokens"
        },
        "answer": "B"
    },
    {
        "question": "Which C++23 feature provides a standard way to represent a multi-dimensional array view?",
        "options": {
            "A": "std::vector2d",
            "B": "std::mdspan",
            "C": "std::matrix",
            "D": "std::array_view"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::expected' (C++23) used for?",
        "options": {
            "A": "To wait for a user input",
            "B": "A vocabulary type that contains either an expected value or an error code, improving error handling",
            "C": "To predict CPU branch behavior",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Argument-Dependent Lookup' (ADL)?",
        "options": {
            "A": "Looking for arguments in a list",
            "B": "A set of rules for finding a function based on the namespaces of the arguments passed to it",
            "C": "A type of sharding",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'std::variant' over a C-style 'union'?",
        "options": {
            "A": "It is faster",
            "B": "It is type-safe and knows which type it currently holds, calling destructors correctly",
            "C": "It can hold multiple values at once",
            "D": "It is only for strings"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Type Erasure' in C++ (e.g., std::any or std::function)?",
        "options": {
            "A": "Deleting a data type",
            "B": "A technique to store and interact with different types through a single common interface without a common base class",
            "C": "A type of sharding",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is the complexity of 'std::sort'?",
        "options": {
            "A": "O(n)",
            "B": "O(n log n)",
            "C": "O(n^2)",
            "D": "O(log n)"
        },
        "answer": "B"
    },
    {
        "question": "Which algorithm is used to find an element in a 'sorted' range in O(log n) time?",
        "options": {
            "A": "std::find",
            "B": "std::binary_search",
            "C": "std::search",
            "D": "std::match"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::nth_element' used for?",
        "options": {
            "A": "Sorting every n-th element",
            "B": "Partially sorting a range so that the element at the n-th position is the one that would be there if sorted",
            "C": "Deleting the n-th element",
            "D": "Finding the n-th prime number"
        },
        "answer": "B"
    },
    {
        "question": "What is the difference between 'std::set' and 'std::unordered_set'?",
        "options": {
            "A": "std::set is faster",
            "B": "std::set is ordered (Tree); std::unordered_set is unordered (Hash Table)",
            "C": "std::unordered_set uses more disk space",
            "D": "std::set is only for integers"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::accumulate'?",
        "options": {
            "A": "A way to accumulate memory leaks",
            "B": "An algorithm that computes the sum of a range of elements",
            "C": "A type of loop",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Which header file is required for using standard algorithms like sort and find?",
        "options": {
            "A": "<math>",
            "B": "<algorithm>",
            "C": "<utility>",
            "D": "<stl>"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::move_iterator'?",
        "options": {
            "A": "An iterator that moves the cursor",
            "B": "An iterator that converts its dereferenced value into an rvalue (triggering a move instead of a copy)",
            "C": "A type of unit test",
            "D": "A legacy feature"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::fstream' used for?",
        "options": {
            "A": "Managing network streams",
            "B": "Performing both input and output operations on files",
            "C": "Streaming video",
            "D": "Encrypting text"
        },
        "answer": "B"
    },
    {
        "question": "In 'std::fstream', what does 'ios::app' mode do?",
        "options": {
            "A": "Opens an app",
            "B": "Appends all output to the end of the file",
            "C": "Deletes the file",
            "D": "Opens the file in binary mode"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'std::cin.ignore()'?",
        "options": {
            "A": "To ignore the user",
            "B": "To discard characters from the input buffer",
            "C": "To stop reading a file",
            "D": "To speed up the network"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Serialization' in a C++ context?",
        "options": {
            "A": "Adding a serial number to code",
            "B": "The process of converting an object into a byte stream to save to a file or send over a network",
            "C": "Deleting data in order",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "Which keyword is used to ensure a function doesn't throw any exceptions?",
        "options": {
            "A": "throw(none)",
            "B": "noexcept",
            "C": "safe",
            "D": "final"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Exception Guarantee' 'Strong Guarantee'?",
        "options": {
            "A": "The exception is strongly ignored",
            "B": "If an operation fails, the state of the program is rolled back to exactly what it was before",
            "C": "The program never crashes",
            "D": "A database rule"
        },
        "answer": "B"
    },
    {
        "question": "What is 'RAII' applied to Mutexes?",
        "options": {
            "A": "Using std::lock_guard or std::scoped_lock to manage mutex ownership automatically",
            "B": "Locking the master node",
            "C": "Deleting the mutex",
            "D": "A security scan"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Non-owning' reference (like std::string_view)?",
        "options": {
            "A": "A reference to a deleted object",
            "B": "A reference that points to data managed by another object, avoiding expensive copies",
            "C": "A type of pointer",
            "D": "A performance bug"
        },
        "answer": "B"
    },
    {
        "question": "Which C++20 feature is used to define generic requirements for template arguments at compile-time?",
        "options": {
            "A": "Traits",
            "B": "Concepts",
            "C": "Interfaces",
            "D": "Contracts"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::jthread' (C++20)?",
        "options": {
            "A": "A thread for Java",
            "B": "A 'joining' thread that automatically joins upon destruction and supports cooperative interruption",
            "C": "A thread that runs in a loop",
            "D": "A type of sharding"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::atomic_ref'?",
        "options": {
            "A": "A reference to a bomb",
            "B": "A way to perform atomic operations on non-atomic objects",
            "C": "A security certificate",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Which of these represents 'Static Polymorphism'?",
        "options": {
            "A": "Virtual functions",
            "B": "Templates and CRTP",
            "C": "Inheritance",
            "D": "Dynamic casting"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Object Slicing'?",
        "options": {
            "A": "Dividing an object into bits",
            "B": "When a derived class object is assigned to a base class object by value, losing the derived data",
            "C": "A type of unit test",
            "D": "A memory leak"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Internal Linkage' (using 'static' keyword on global variables)?",
        "options": {
            "A": "Connecting two computers",
            "B": "Limiting the visibility of a variable or function to the current translation unit",
            "C": "Storing data on the hard drive",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'ODR' (One Definition Rule)?",
        "options": {
            "A": "A rule that says only one person can code",
            "B": "A requirement that every variable or function has exactly one definition in the entire program",
            "C": "A database index",
            "D": "A type of sharding"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::bit_cast' (C++20)?",
        "options": {
            "A": "Casting a movie",
            "B": "A type-safe way to reinterpret the bits of one object as another type of the same size",
            "C": "A performance report",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Constexpr if' (C++17)?",
        "options": {
            "A": "A regular if-statement",
            "B": "A compile-time if-statement that discards branches that don't match criteria, useful in templates",
            "C": "A type of loop",
            "D": "A database query"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::filesystem::path'?",
        "options": {
            "A": "A drawing of the drive",
            "B": "A class that represents a location in the file system across different operating systems",
            "C": "A security scan result",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Which operator is used for the 'Member Pointer' access?",
        "options": {
            "A": "->*",
            "B": "::",
            "C": ".*",
            "D": "Both A and C"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Universal Character Name' (\\uXXXX)?",
        "options": {
            "A": "The developer's name",
            "B": "A way to represent Unicode characters in C++ source code",
            "C": "A type of primary key",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::unique_lock' advantage over 'std::lock_guard'?",
        "options": {
            "A": "It is faster",
            "B": "It allows for manual locking, unlocking, and moving ownership (more flexible)",
            "C": "It is only for Windows",
            "D": "It deletes the mutex"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Prefetching' in the context of C++ performance optimization?",
        "options": {
            "A": "Fetching data before the user asks",
            "B": "An optimization where the CPU loads data into the cache before it is actually requested by an instruction",
            "C": "A security scan",
            "D": "A memory leak"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Cache Line' size (typically)?",
        "options": {
            "A": "1 byte",
            "B": "64 bytes",
            "C": "1 GB",
            "D": "Unlimited"
        },
        "answer": "B"
    },
    {
        "question": "Which attribute is used to tell the compiler that a switch case is intended to fall through?",
        "options": {
            "A": "[[continue]]",
            "B": "[[fallthrough]]",
            "C": "[[no_break]]",
            "D": "[[next]]"
        },
        "answer": "B"
    },
    {
        "question": "What is 'ADL' (Argument-Dependent Lookup) also known as?",
        "options": {
            "A": "Koenig Lookup",
            "B": "Stroustrup Search",
            "C": "C++ Finding",
            "D": "Global Lookup"
        },
        "answer": "A"
    },
    {
        "question": "What is 'std::bind_front' (C++20)?",
        "options": {
            "A": "Binding the front of a book",
            "B": "A more efficient and simpler replacement for std::bind for binding leading arguments",
            "C": "A type of sharding",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "Which C++20 header provides mathematical constants like std::numbers::pi?",
        "options": {
            "A": "<cmath>",
            "B": "<numbers>",
            "C": "<math_constants>",
            "D": "<utility>"
        },
        "answer": "B"
    },
    {
        "question": "What is 'std::format' (C++20)?",
        "options": {
            "A": "Formatting a hard drive",
            "B": "A type-safe and extensible alternative to printf for string formatting",
            "C": "A styling theme",
            "D": "A database tool"
        },
        "answer": "B"
    },
    {
        "question": "Final question: What is the primary purpose of 'std::source_location' (C++20)?",
        "options": {
            "A": "To find the server location",
            "B": "To capture information about the source code (file name, line number) without using macros",
            "C": "A security certificate",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Explicit template instantiation' used for?",
        "options": {
            "A": "To slow down the compiler",
            "B": "To reduce compilation time by instantiating a template in one object file and reusing it in others",
            "C": "To hide code",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "What is 'User-Defined Literals' (e.g., 10s or 5kg)?",
        "options": {
            "A": "Writing a book",
            "B": "Custom suffixes that allow users to create objects with specific values and units",
            "C": "A security scan",
            "D": "A performance bug"
        },
        "answer": "B"
    },
    {
        "question": "Which tool provides static analysis for C++ code to find bugs and performance issues?",
        "options": {
            "A": "Clang-Tidy",
            "B": "Notepad",
            "C": "Calculator",
            "D": "Web Browser"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Whole Program Optimization'?",
        "options": {
            "A": "Optimizing only the main function",
            "B": "A compiler feature that optimizes across all object files in the entire program at once",
            "C": "Deleting the code",
            "D": "A performance report"
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
    skill = "C++"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
