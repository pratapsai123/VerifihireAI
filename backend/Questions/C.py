from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
    {
        "question": "What is the index of the first element in a C array?",
        "options": {
            "A": "-1",
            "B": "0",
            "C": "1",
            "D": "Depends on the array size"
        },
        "answer": "B"
    },
    {
        "question": "How do you declare an array of 5 integers named 'arr'?",
        "options": {
            "A": "int arr[5];",
            "B": "arr int[5];",
            "C": "int arr = {5};",
            "D": "array int arr[5];"
        },
        "answer": "A"
    },
    {
        "question": "Which character is automatically added at the end of a string in C?",
        "options": {
            "A": "\\n",
            "B": "\\0",
            "C": "\\t",
            "D": ";"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'strlen()' function?",
        "options": {
            "A": "To copy a string",
            "B": "To find the length of a string (excluding the null character)",
            "C": "To concatenate two strings",
            "D": "To compare two strings"
        },
        "answer": "B"
    },
    {
        "question": "Which header file is required to use string functions like 'strcpy' and 'strcat'?",
        "options": {
            "A": "<stdio.h>",
            "B": "<string.h>",
            "C": "<stdlib.h>",
            "D": "<ctype.h>"
        },
        "answer": "B"
    },
    {
        "question": "What happens if you try to access 'arr[10]' in an array declared as 'int arr[10];'?",
        "options": {
            "A": "It accesses the last element",
            "B": "It results in an 'Array Index Out of Bounds' error at compile-time",
            "C": "It accesses out-of-bounds memory (Undefined Behavior)",
            "D": "It returns 0"
        },
        "answer": "C"
    },
    {
        "question": "Which function is used to compare two strings in C?",
        "options": {
            "A": "strcp()",
            "B": "strcmp()",
            "C": "strcm()",
            "D": "strcompare()"
        },
        "answer": "B"
    },
    {
        "question": "A function that calls itself is known as:",
        "options": {
            "A": "Self-function",
            "B": "Recursive function",
            "C": "Nested function",
            "D": "Loop function"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Global Variable'?",
        "options": {
            "A": "A variable declared inside a function",
            "B": "A variable declared outside of all functions",
            "C": "A variable that can be accessed globally by other programs",
            "D": "A variable stored in a global header"
        },
        "answer": "B"
    },
    {
        "question": "Which keyword is used to preserve the value of a local variable even after the function finishes execution?",
        "options": {
            "A": "volatile",
            "B": "static",
            "C": "extern",
            "D": "auto"
        },
        "answer": "B"
    },
    {
        "question": "What does 'Call by Value' mean?",
        "options": {
            "A": "Passing the memory address of a variable to a function",
            "B": "Passing a copy of the variable's value to the function",
            "C": "Calling a function using its return value",
            "D": "Updating the original variable directly"
        },
        "answer": "B"
    },
    {
        "question": "What does 'Call by Reference' involve in C?",
        "options": {
            "A": "Using the 'ref' keyword",
            "B": "Passing the address of a variable using pointers",
            "C": "Passing the variable name as a string",
            "D": "There is no call by reference in C"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to concatenate two strings?",
        "options": {
            "A": "strjoin()",
            "B": "strcat()",
            "C": "stradd()",
            "D": "strcpy()"
        },
        "answer": "B"
    },
    {
        "question": "What is the return type of 'strcmp()' if the two strings are identical?",
        "options": {
            "A": "1",
            "B": "0",
            "C": "-1",
            "D": "True"
        },
        "answer": "B"
    },
    {
        "question": "How do you declare a 2D array of integers with 3 rows and 4 columns?",
        "options": {
            "A": "int arr[3,4];",
            "B": "int arr[3][4];",
            "C": "int arr[4][3];",
            "D": "2d_int arr[3][4];"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of a 'Function Prototype'?",
        "options": {
            "A": "To define the body of the function",
            "B": "To inform the compiler about the function's name, return type, and parameters before its use",
            "C": "To call the function",
            "D": "To allocate memory for the function"
        },
        "answer": "B"
    },
    {
        "question": "Variables declared inside a function are called:",
        "options": {
            "A": "Local variables",
            "B": "Private variables",
            "C": "Internal variables",
            "D": "Static variables"
        },
        "answer": "A"
    },
    {
        "question": "Which storage class has the fastest access speed?",
        "options": {
            "A": "auto",
            "B": "static",
            "C": "register",
            "D": "extern"
        },
        "answer": "C"
    },
    {
        "question": "What is the default storage class for local variables?",
        "options": {
            "A": "static",
            "B": "extern",
            "C": "auto",
            "D": "register"
        },
        "answer": "C"
    },
    {
        "question": "Which keyword is used to access a global variable declared in another file?",
        "options": {
            "A": "global",
            "B": "extern",
            "C": "import",
            "D": "static"
        },
        "answer": "B"
    },
    {
        "question": "What is the maximum number of values a C function can return using the 'return' statement?",
        "options": {
            "A": "0",
            "B": "1",
            "C": "2",
            "D": "Unlimited"
        },
        "answer": "B"
    },
    {
        "question": "What is the output of 'sizeof(arr)' if 'int arr[10];' (assuming int is 4 bytes)?",
        "options": {
            "A": "10",
            "B": "40",
            "C": "4",
            "D": "1"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to copy one string to another?",
        "options": {
            "A": "strfill()",
            "B": "strcpy()",
            "C": "strmove()",
            "D": "strset()"
        },
        "answer": "B"
    },
    {
        "question": "In a 2D array 'arr[2][3]', how many total elements are there?",
        "options": {
            "A": "2",
            "B": "3",
            "C": "5",
            "D": "6"
        },
        "answer": "D"
    },
    {
        "question": "What is the base address of an array?",
        "options": {
            "A": "The address of the last element",
            "B": "The address of the first element (index 0)",
            "C": "The total size of the array",
            "D": "The middle index address"
        },
        "answer": "B"
    },
    {
        "question": "Which of the following is an example of an actual parameter?",
        "options": {
            "A": "The parameter defined in the function signature",
            "B": "The value passed to the function during a function call",
            "C": "The return value",
            "D": "The local variable inside the function"
        },
        "answer": "B"
    },
    {
        "question": "What is the life of a 'static' local variable?",
        "options": {
            "A": "Only while the function is executing",
            "B": "Throughout the entire lifetime of the program",
            "C": "Until the variable is reset to zero",
            "D": "Depends on the CPU"
        },
        "answer": "B"
    },
    {
        "question": "What is 'gets()' function used for?",
        "options": {
            "A": "To output a string",
            "B": "To read a string from the user (including spaces)",
            "C": "To get the size of a file",
            "D": "To get a single character"
        },
        "answer": "B"
    },
    {
        "question": "Why is 'fgets()' preferred over 'gets()'?",
        "options": {
            "A": "It is faster",
            "B": "It prevents buffer overflow by specifying a maximum buffer size",
            "C": "It can read integers",
            "D": "It doesn't require a header file"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'string' in C?",
        "options": {
            "A": "A built-in data type",
            "B": "A 1D array of characters terminated by a null character",
            "C": "A pointer to a character only",
            "D": "A class in the standard library"
        },
        "answer": "B"
    },
    {
        "question": "Which function converts a string to an integer?",
        "options": {
            "A": "itoa()",
            "B": "atoi()",
            "C": "strint()",
            "D": "toInt()"
        },
        "answer": "B"
    },
    {
        "question": "What is the result of '1 + \"A\"' in C?",
        "options": {
            "A": "66",
            "B": "B",
            "C": "It adds 1 to the memory address of the string constant \"A\"",
            "D": "Error"
        },
        "answer": "C"
    },
    {
        "question": "A function that does not return any value must have a return type of:",
        "options": {
            "A": "null",
            "B": "void",
            "C": "int",
            "D": "empty"
        },
        "answer": "B"
    },
    {
        "question": "How do you pass an entire array to a function?",
        "options": {
            "A": "Pass the name of the array",
            "B": "Pass every element using a loop",
            "C": "Arrays cannot be passed to functions",
            "D": "Pass the size of the array only"
        },
        "answer": "A"
    },
    {
        "question": "When an array is passed to a function, what is actually being passed?",
        "options": {
            "A": "A copy of all elements",
            "B": "The address of the first element",
            "C": "The size of the array",
            "D": "The last element's value"
        },
        "answer": "B"
    },
    {
        "question": "Which library contains 'atoi()'?",
        "options": {
            "A": "<stdio.h>",
            "B": "<stdlib.h>",
            "C": "<string.h>",
            "D": "<math.h>"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Recursive Base Case'?",
        "options": {
            "A": "The start of the recursion",
            "B": "The condition that stops the recursion",
            "C": "The most complex part of the function",
            "D": "A memory error"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Scope' of a variable?",
        "options": {
            "A": "The memory size of the variable",
            "B": "The region of the program where a variable is accessible",
            "C": "The data type of the variable",
            "D": "The value of the variable"
        },
        "answer": "B"
    },
    {
        "question": "Which of the following can be used as an array size in C (C89)?",
        "options": {
            "A": "A variable",
            "B": "A constant integer expression",
            "C": "A floating point number",
            "D": "A string"
        },
        "answer": "B"
    },
    {
        "question": "What is 'puts()' used for?",
        "options": {
            "A": "To read a string",
            "B": "To print a string to the console and add a newline",
            "C": "To concatenate strings",
            "D": "To delete a string"
        },
        "answer": "B"
    },
    {
        "question": "What is the output of 'strcmp(\"abc\", \"abc\")'?",
        "options": {
            "A": "1",
            "B": "0",
            "C": "true",
            "D": "-1"
        },
        "answer": "B"
    },
    {
        "question": "Can two functions in the same program have the same name?",
        "options": {
            "A": "Yes, always",
            "B": "No (unless they are in different files and static)",
            "C": "Yes, if they have different parameters",
            "D": "Only if they return void"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Modular Programming'?",
        "options": {
            "A": "Using only while loops",
            "B": "Breaking a large program into smaller, manageable functions/modules",
            "C": "Programming in binary",
            "D": "A type of database design"
        },
        "answer": "B"
    },
    {
        "question": "What is the storage class of a variable declared outside 'main()'?",
        "options": {
            "A": "auto",
            "B": "static",
            "C": "extern (Global)",
            "D": "register"
        },
        "answer": "C"
    },
    {
        "question": "How is a string literal stored in memory?",
        "options": {
            "A": "In the stack",
            "B": "In the read-only data segment",
            "C": "In the heap",
            "D": "In the CPU registers"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to reverse a string in some C compilers (non-standard)?",
        "options": {
            "A": "strrev()",
            "B": "revstr()",
            "C": "reverse()",
            "D": "strinv()"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Array Initialization'?",
        "options": {
            "A": "Deleting an array",
            "B": "Assigning values to an array at the time of declaration",
            "C": "Finding the size of an array",
            "D": "Sorting an array"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Pass by Address'?",
        "options": {
            "A": "Another name for 'Call by Value'",
            "B": "Another name for 'Call by Reference' using pointers",
            "C": "Passing the home address of the user",
            "D": "An error in the compiler"
        },
        "answer": "B"
    },
    {
        "question": "What is the index of the last element in 'int a[n]'?",
        "options": {
            "A": "n",
            "B": "n - 1",
            "C": "n + 1",
            "D": "0"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 2: What is the main disadvantage of 'register' storage class?",
        "options": {
            "A": "It is slow",
            "B": "The address of a register variable cannot be taken using the '&' operator",
            "C": "It uses too much RAM",
            "D": "It can only store strings"
        },
        "answer": "B"
    },
    {
        "question": "What is a pointer in C?",
        "options": {
            "A": "A variable that stores a value",
            "B": "A variable that stores the memory address of another variable",
            "C": "A symbol used to point to errors",
            "D": "A type of loop"
        },
        "answer": "B"
    },
    {
        "question": "Which operator is used to get the address of a variable?",
        "options": {
            "A": "*",
            "B": "&",
            "C": "->",
            "D": "address()"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'NULL' pointer?",
        "options": {
            "A": "A pointer that points to the middle of memory",
            "B": "A pointer that does not point to any valid memory location",
            "C": "A pointer that has been deleted",
            "D": "An integer variable set to zero"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'malloc()' function?",
        "options": {
            "A": "To free memory",
            "B": "To allocate a block of memory dynamically on the heap",
            "C": "To calculate the size of a variable",
            "D": "To copy memory contents"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to deallocate memory that was previously allocated by malloc?",
        "options": {
            "A": "delete()",
            "B": "free()",
            "C": "remove()",
            "D": "clear()"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Dangling Pointer'?",
        "options": {
            "A": "A pointer that points to a memory location that has been freed",
            "B": "A pointer that is not initialized",
            "C": "A pointer used in a loop",
            "D": "A pointer that points to itself"
        },
        "answer": "A"
    },
    {
        "question": "What is a 'Wild Pointer'?",
        "options": {
            "A": "A pointer that points to a random location",
            "B": "A pointer that has not been initialized to anything",
            "C": "A pointer that points to a constant",
            "D": "A pointer that cannot be deleted"
        },
        "answer": "B"
    },
    {
        "question": "Which keyword is used to define a user-defined data type that can hold multiple variables of different types?",
        "options": {
            "A": "union",
            "B": "struct",
            "C": "enum",
            "D": "typedef"
        },
        "answer": "B"
    },
    {
        "question": "What is the difference between a 'struct' and a 'union'?",
        "options": {
            "A": "Structs are faster than unions",
            "B": "In a struct, every member has its own memory; in a union, all members share the same memory",
            "C": "Unions can only hold integers",
            "D": "There is no difference"
        },
        "answer": "B"
    },
    {
        "question": "Which operator is used to access members of a structure using a structure variable?",
        "options": {
            "A": "->",
            "B": ".",
            "C": "*",
            "D": "&"
        },
        "answer": "B"
    },
    {
        "question": "Which operator is used to access members of a structure using a pointer to that structure?",
        "options": {
            "A": ".",
            "B": "->",
            "C": "*",
            "D": "&"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'calloc()'?",
        "options": {
            "A": "To call a function",
            "B": "To allocate multiple blocks of memory and initialize them to zero",
            "C": "To reallocate memory",
            "D": "To free memory"
        },
        "answer": "B"
    },
    {
        "question": "What does 'realloc()' do?",
        "options": {
            "A": "Allocates memory for the first time",
            "B": "Changes the size of a previously allocated memory block",
            "C": "Deletes memory",
            "D": "Initializes memory to one"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Void Pointer' (void *)?",
        "options": {
            "A": "A pointer that has no value",
            "B": "A generic pointer that can point to any data type",
            "C": "A pointer that causes a crash",
            "D": "A pointer to a function"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Memory Leak' in C?",
        "options": {
            "A": "The CPU running out of power",
            "B": "Failure to free dynamically allocated memory, leading to wasted system resources",
            "C": "A hard drive failure",
            "D": "Accessing an array out of bounds"
        },
        "answer": "B"
    },
    {
        "question": "What is the output of 'printf(\"%d\", sizeof(ptr))' assuming a 64-bit system?",
        "options": {
            "A": "4",
            "B": "8",
            "C": "Depends on the data type the pointer points to",
            "D": "1"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Typedef' used for?",
        "options": {
            "A": "To create a new data type",
            "B": "To create an alias or nickname for an existing data type",
            "C": "To define a constant",
            "D": "To perform type casting"
        },
        "answer": "B"
    },
    {
        "question": "How do you access the value of a pointer 'p'?",
        "options": {
            "A": "&p",
            "B": "*p",
            "C": "p->value",
            "D": "val(p)"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Self-Referential Structure'?",
        "options": {
            "A": "A structure that has no members",
            "B": "A structure that contains a pointer to a structure of the same type (used in Linked Lists)",
            "C": "A structure that is constant",
            "D": "An error in structure definition"
        },
        "answer": "B"
    },
    {
        "question": "Which function returns a pointer to the first byte of the allocated memory block?",
        "options": {
            "A": "malloc()",
            "B": "calloc()",
            "C": "realloc()",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "What is the result of 'p + 1' if 'p' is a pointer to an integer (4 bytes) at address 1000?",
        "options": {
            "A": "1001",
            "B": "1004",
            "C": "1000",
            "D": "Undefined"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Pointer to Pointer'?",
        "options": {
            "A": "A variable that stores the address of another pointer",
            "B": "An error in C",
            "C": "Two pointers pointing to the same variable",
            "D": "A pointer that points to a function"
        },
        "answer": "A"
    },
    {
        "question": "Which of the following correctly defines a pointer to an array of 10 integers?",
        "options": {
            "A": "int *ptr[10];",
            "B": "int (*ptr)[10];",
            "C": "int ptr[*10];",
            "D": "int (*ptr)10;"
        },
        "answer": "B"
    },
    {
        "question": "What is the return type of malloc()?",
        "options": {
            "A": "int *",
            "B": "void *",
            "C": "char *",
            "D": "float *"
        },
        "answer": "B"
    },
    {
        "question": "In a union of an int (4 bytes) and a char (1 byte), what is the total size of the union?",
        "options": {
            "A": "1 byte",
            "B": "4 bytes",
            "C": "5 bytes",
            "D": "8 bytes"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Function Pointer'?",
        "options": {
            "A": "A pointer that points to the first line of a function",
            "B": "A pointer that stores the starting address of a function",
            "C": "A function that returns a pointer",
            "D": "A pointer used as a parameter"
        },
        "answer": "B"
    },
    {
        "question": "How do you declare a function pointer named 'f' that points to a function returning void?",
        "options": {
            "A": "void *f();",
            "B": "void (*f)();",
            "C": "void f*();",
            "D": "f = void(*)();"
        },
        "answer": "B"
    },
    {
        "question": "Which area of memory is used for dynamic memory allocation?",
        "options": {
            "A": "Stack",
            "B": "Heap",
            "C": "Data Segment",
            "D": "Register"
        },
        "answer": "B"
    },
    {
        "question": "What happens if malloc() cannot find enough memory to allocate?",
        "options": {
            "A": "It crashes the program",
            "B": "It returns a NULL pointer",
            "C": "It restarts the computer",
            "D": "It returns a random address"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Pointer Arithmetic'?",
        "options": {
            "A": "Adding two pointers together",
            "B": "Performing operations like addition or subtraction on a pointer to navigate memory",
            "C": "Calculating the value of a pointer",
            "D": "Dividing a pointer by an integer"
        },
        "answer": "B"
    },
    {
        "question": "Which of the following is NOT a valid pointer operation?",
        "options": {
            "A": "Adding an integer to a pointer",
            "B": "Adding two pointers",
            "C": "Subtracting an integer from a pointer",
            "D": "Subtracting one pointer from another (of the same type)"
        },
        "answer": "B"
    },
    {
        "question": "What is the size of an empty structure in C?",
        "options": {
            "A": "0",
            "B": "1",
            "C": "Undefined / Compiler dependent",
            "D": "4"
        },
        "answer": "C"
    },
    {
        "question": "What is 'Structure Padding'?",
        "options": {
            "A": "Adding comments to a structure",
            "B": "Adding extra bytes between structure members to align them with memory boundaries for faster access",
            "C": "A way to delete structure members",
            "D": "Filling a structure with zeros"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'free(ptr)' call?",
        "options": {
            "A": "To set the pointer to NULL",
            "B": "To mark the allocated memory block as available for future use",
            "C": "To delete the variable ptr",
            "D": "To clear the screen"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Bit Field' in a structure?",
        "options": {
            "A": "A field used for bitwise operations",
            "B": "A structure member that allows you to specify the exact number of bits it occupies",
            "C": "A field that only stores zeros",
            "D": "A hidden member"
        },
        "answer": "B"
    },
    {
        "question": "Which of the following is used for bit-field declaration?",
        "options": {
            "A": "int a : 4;",
            "B": "int a (4);",
            "C": "int a [4];",
            "D": "int a {4};"
        },
        "answer": "A"
    },
    {
        "question": "What is an 'Enumeration' (enum)?",
        "options": {
            "A": "A type of loop",
            "B": "A user-defined data type that consists of named integer constants",
            "C": "A list of strings",
            "D": "A security feature"
        },
        "answer": "B"
    },
    {
        "question": "What is the default value of the first member of an 'enum' if not specified?",
        "options": {
            "A": "1",
            "B": "0",
            "C": "-1",
            "D": "NULL"
        },
        "answer": "B"
    },
    {
        "question": "What is the output of 'printf(\"%d\", ptr1 - ptr2)' if both point to elements of the same array?",
        "options": {
            "A": "The difference in their addresses in bytes",
            "B": "The number of elements between the two pointers",
            "C": "0",
            "D": "Undefined"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Double Free' error?",
        "options": {
            "A": "Freeing two different pointers",
            "B": "Attempting to call free() on the same memory address twice",
            "C": "Freeing memory and then using it",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Which function initializes the newly allocated memory with zero values?",
        "options": {
            "A": "malloc()",
            "B": "calloc()",
            "C": "realloc()",
            "D": "init()"
        },
        "answer": "B"
    },
    {
        "question": "How do you define a structure 'Point' with x and y coordinates?",
        "options": {
            "A": "struct Point { int x, y; };",
            "B": "Point struct { int x, y; };",
            "C": "struct { int x, y; } Point;",
            "D": "define struct Point (x, y);"
        },
        "answer": "A"
    },
    {
        "question": "Can a structure contain another structure as its member?",
        "options": {
            "A": "No",
            "B": "Yes (Nested Structure)",
            "C": "Only if they are of the same name",
            "D": "Only if it is a union"
        },
        "answer": "B"
    },
    {
        "question": "What is the size of 'char *ptr' on a 32-bit system?",
        "options": {
            "A": "1 byte",
            "B": "4 bytes",
            "C": "8 bytes",
            "D": "Depends on the system"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is the correct way to free a pointer 'p'?",
        "options": {
            "A": "free(p);",
            "B": "free(*p);",
            "C": "free(&p);",
            "D": "delete p;"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Segmentation Fault' typically caused by?",
        "options": {
            "A": "Accessing invalid or restricted memory (e.g., dereferencing a NULL pointer)",
            "B": "Running out of disk space",
            "C": "A syntax error",
            "D": "A infinite loop"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of 'typedef struct'?",
        "options": {
            "A": "To create a constant structure",
            "B": "To allow creating structure variables without using the 'struct' keyword every time",
            "C": "To delete the structure",
            "D": "To speed up compilation"
        },
        "answer": "B"
    },
    {
        "question": "What is the relationship between an array name and a pointer?",
        "options": {
            "A": "There is no relationship",
            "B": "An array name acts as a constant pointer to the first element of the array",
            "C": "A pointer can hold multiple arrays",
            "D": "An array name is a pointer to the middle element"
        },
        "answer": "B"
    },
    {
        "question": "Which operator is used for indirection or dereferencing?",
        "options": {
            "A": "&",
            "B": "*",
            "C": "->",
            "D": "[]"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 3: What is 'Pass by Pointer' used for in function calls?",
        "options": {
            "A": "To make the program harder to read",
            "B": "To allow a function to modify the actual value of a variable in the calling function",
            "C": "To save memory on the stack",
            "D": "To return multiple values"
        },
        "answer": "B"
    },
    {
        "question": "Which data type is used to represent a file pointer in C?",
        "options": {
            "A": "file *",
            "B": "FILE *",
            "C": "struct FILE",
            "D": "int"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to open a file in C?",
        "options": {
            "A": "open()",
            "B": "fopen()",
            "C": "file_open()",
            "D": "load()"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'w' mode in fopen() do?",
        "options": {
            "A": "Opens a file for reading",
            "B": "Opens a file for writing (creates if not exists, overwrites if it does)",
            "C": "Opens a file for appending",
            "D": "Opens a binary file"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'a' mode in fopen() do?",
        "options": {
            "A": "Opens for reading only",
            "B": "Opens for writing at the end of the file (appending)",
            "C": "Opens for all-purpose access",
            "D": "Deletes the file contents"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to close a file?",
        "options": {
            "A": "close()",
            "B": "fclose()",
            "C": "file_close()",
            "D": "end()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'EOF' in C file handling?",
        "options": {
            "A": "Error of File",
            "B": "End of File",
            "C": "Equal of Function",
            "D": "Execute only File"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to read a single character from a file?",
        "options": {
            "A": "scanf()",
            "B": "fgetc()",
            "C": "getch()",
            "D": "read()"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to write a single character to a file?",
        "options": {
            "A": "printf()",
            "B": "fputc()",
            "C": "write()",
            "D": "putch()"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'rewind()' function?",
        "options": {
            "A": "To delete a file",
            "B": "To set the file position indicator to the beginning of the file",
            "C": "To reverse the characters in a file",
            "D": "To close and reopen a file"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to read formatted data from a file?",
        "options": {
            "A": "scanf()",
            "B": "fscanf()",
            "C": "readf()",
            "D": "sscanf()"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to write formatted data to a file?",
        "options": {
            "A": "printf()",
            "B": "fprintf()",
            "C": "writef()",
            "D": "sprintf()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'fseek()' used for?",
        "options": {
            "A": "To find a string in a file",
            "B": "To set the file position indicator to a specific offset",
            "C": "To search for a file on disk",
            "D": "To check for errors"
        },
        "answer": "B"
    },
    {
        "question": "Which constant is used with fseek() to represent the current position in the file?",
        "options": {
            "A": "SEEK_SET",
            "B": "SEEK_CUR",
            "C": "SEEK_END",
            "D": "SEEK_NOW"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Preprocessor Directive' in C?",
        "options": {
            "A": "A command that starts with # and is processed before compilation",
            "B": "A function that runs before main()",
            "C": "A type of loop",
            "D": "A post-compilation cleanup tool"
        },
        "answer": "A"
    },
    {
        "question": "Which directive is used to define a macro?",
        "options": {
            "A": "#include",
            "B": "#define",
            "C": "#macro",
            "D": "#const"
        },
        "answer": "B"
    },
    {
        "question": "What does '#include <filename>' do?",
        "options": {
            "A": "Searches for the file in the standard system directories",
            "B": "Searches for the file in the current project directory only",
            "C": "Compiles the specified file",
            "D": "Creates a new header file"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of '#ifdef'?",
        "options": {
            "A": "To define a function",
            "B": "Conditional compilation; checks if a macro is defined",
            "C": "To include a file if it exists",
            "D": "To declare a variable"
        },
        "answer": "B"
    },
    {
        "question": "What are 'Command Line Arguments' in C?",
        "options": {
            "A": "Arguments passed to a function",
            "B": "Parameters passed to the main() function from the shell or terminal",
            "C": "Errors displayed in the terminal",
            "D": "Directives used by the linker"
        },
        "answer": "B"
    },
    {
        "question": "In 'int main(int argc, char *argv[])', what does 'argc' represent?",
        "options": {
            "A": "Argument Characters",
            "B": "Argument Count (number of parameters passed)",
            "C": "Array of command lines",
            "D": "Active code"
        },
        "answer": "B"
    },
    {
        "question": "What is 'argv[0]' in a C program?",
        "options": {
            "A": "The first user argument",
            "B": "The name of the program itself",
            "C": "The number of arguments",
            "D": "A null pointer"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to convert a string argument from the command line into an integer?",
        "options": {
            "A": "strint()",
            "B": "atoi()",
            "C": "toInt()",
            "D": "scanf()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'ftell()' used for?",
        "options": {
            "A": "To tell the name of the file",
            "B": "To return the current position (offset) of the file pointer",
            "C": "To check if a file is empty",
            "D": "To set the file pointer"
        },
        "answer": "B"
    },
    {
        "question": "Which header file is needed for 'exit()' and dynamic memory functions?",
        "options": {
            "A": "<stdio.h>",
            "B": "<stdlib.h>",
            "C": "<string.h>",
            "D": "<time.h>"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Macro' in C?",
        "options": {
            "A": "A large function",
            "B": "A fragment of code which has been given a name for text replacement",
            "C": "A type of global variable",
            "D": "A security feature"
        },
        "answer": "B"
    },
    {
        "question": "Which directive is used to undefine a macro?",
        "options": {
            "A": "#del",
            "B": "#undef",
            "C": "#remove",
            "D": "#ifdef"
        },
        "answer": "B"
    },
    {
        "question": "What is 'perror()' used for?",
        "options": {
            "A": "To ignore errors",
            "B": "To print a descriptive error message to stderr based on 'errno'",
            "C": "To calculate math errors",
            "D": "To exit the program"
        },
        "answer": "B"
    },
    {
        "question": "Which variable stores the error number of the last system call error?",
        "options": {
            "A": "error",
            "B": "errno",
            "C": "err_code",
            "D": "status"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Binary Mode' in file handling ('rb', 'wb')?",
        "options": {
            "A": "Writing only 0s and 1s",
            "B": "Opening a file as-is without translating newline characters",
            "C": "Encrypting the file",
            "D": "A faster reading mode"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to read a whole line or string from a file?",
        "options": {
            "A": "fgetc()",
            "B": "fgets()",
            "C": "gets()",
            "D": "fscanf()"
        },
        "answer": "B"
    },
    {
        "question": "What is the result of '#include \"myfile.h\"'?",
        "options": {
            "A": "Compiler searches the current directory first",
            "B": "Compiler only searches system libraries",
            "C": "It creates a new file",
            "D": "It throws an error"
        },
        "answer": "A"
    },
    {
        "question": "What is a 'Pragma' directive?",
        "options": {
            "A": "A way to define variables",
            "B": "Compiler-specific instructions to the preprocessor",
            "C": "A comment type",
            "D": "A return statement"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to detect the end of a file stream?",
        "options": {
            "A": "check_end()",
            "B": "feof()",
            "C": "end()",
            "D": "file_limit()"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'fflush()'?",
        "options": {
            "A": "To close a file",
            "B": "To clear or 'flush' the output buffer of a stream",
            "C": "To delete file contents",
            "D": "To speed up reading"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Enum' size in C?",
        "options": {
            "A": "1 byte",
            "B": "Size of an integer (usually 4 bytes)",
            "C": "Size of a char",
            "D": "Depends on the number of elements"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is used to define a 'Type' name for a struct?",
        "options": {
            "A": "typedef",
            "B": "typename",
            "C": "define",
            "D": "alias"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Conditional Compilation' used for?",
        "options": {
            "A": "To make code run faster",
            "B": "To compile only specific parts of code based on certain conditions (e.g., OS version)",
            "C": "To test for if-else statements",
            "D": "To avoid using loops"
        },
        "answer": "B"
    },
    {
        "question": "Which directive ends an #if or #ifdef block?",
        "options": {
            "A": "#done",
            "B": "#endif",
            "C": "#stop",
            "D": "#exit"
        },
        "answer": "B"
    },
    {
        "question": "What does 'volatile' keyword tell the compiler?",
        "options": {
            "A": "The variable's value may change at any time without action from the code (e.g., hardware)",
            "B": "The variable is constant",
            "C": "The variable is stored in a register",
            "D": "The variable is empty"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of 'setjmp' and 'longjmp'?",
        "options": {
            "A": "To perform loops",
            "B": "To perform non-local jumps (often used for error handling/exceptions)",
            "C": "To sort an array",
            "D": "To clear the memory"
        },
        "answer": "B"
    },
    {
        "question": "Which function removes a file from the disk?",
        "options": {
            "A": "delete()",
            "B": "remove()",
            "C": "unlink()",
            "D": "Both B and C"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Buffer Overflow'?",
        "options": {
            "A": "Writing more data to a buffer than it can hold",
            "B": "Using too much RAM",
            "C": "A network speed issue",
            "D": "A database error"
        },
        "answer": "A"
    },
    {
        "question": "Which function is used to rename a file?",
        "options": {
            "A": "mv()",
            "B": "rename()",
            "C": "name()",
            "D": "change_name()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Standard Error' (stderr)?",
        "options": {
            "A": "A typo in the code",
            "B": "The default stream for outputting error messages (distinct from stdout)",
            "C": "A type of exception",
            "D": "A log file"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'const' pointer 'int * const ptr'?",
        "options": {
            "A": "The value pointed to is constant",
            "B": "The address stored in the pointer is constant (cannot point elsewhere)",
            "C": "Both are constant",
            "D": "It is a standard pointer"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Static Linking'?",
        "options": {
            "A": "Linking code during runtime",
            "B": "Copying all library modules into the executable at compile time",
            "C": "A type of sharding",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Dynamic Linking'?",
        "options": {
            "A": "Linking library code at the time the program is executed (e.g., .dll or .so)",
            "B": "Linking using pointers",
            "C": "A type of unit test",
            "D": "A performance report"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Memory Alignment'?",
        "options": {
            "A": "Putting data in alphabetical order",
            "B": "Arranging data in memory to match the word size of the processor",
            "C": "A type of sharding",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "Which of the following is used to include a standard math library?",
        "options": {
            "A": "#include <math.h>",
            "B": "#include <m.h>",
            "C": "import math",
            "D": "using math"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Type Casting'?",
        "options": {
            "A": "Deleting a data type",
            "B": "Explicitly converting a variable from one data type to another",
            "C": "Creating a new class",
            "D": "A type of sharding"
        },
        "answer": "B"
    },
    {
        "question": "Final question: C is often called a ______ level language.",
        "options": {
            "A": "High",
            "B": "Low",
            "C": "Middle",
            "D": "Very High"
        },
        "answer": "C"
    },
    {
        "question": "Which notation is used to describe the upper bound of an algorithm's running time?",
        "options": {
            "A": "Omega (Ω)",
            "B": "Big O (O)",
            "C": "Theta (Θ)",
            "D": "Little o (o)"
        },
        "answer": "B"
    },
    {
        "question": "What is the time complexity of accessing an element in an array by its index?",
        "options": {
            "A": "O(1)",
            "B": "O(n)",
            "C": "O(log n)",
            "D": "O(n^2)"
        },
        "answer": "A"
    },
    {
        "question": "In a Singly Linked List, what is the time complexity to delete a node given a pointer to it (not the previous node)?",
        "options": {
            "A": "O(1)",
            "B": "O(n)",
            "C": "O(log n)",
            "D": "O(n^2)"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary disadvantage of a Linked List compared to an Array?",
        "options": {
            "A": "Dynamic size",
            "B": "Ease of insertion/deletion",
            "C": "No random access (must traverse from head)",
            "D": "Wasted memory in null pointers"
        },
        "answer": "C"
    },
    {
        "question": "Which data structure follows the Last-In-First-Out (LIFO) principle?",
        "options": {
            "A": "Queue",
            "B": "Stack",
            "C": "Linked List",
            "D": "Tree"
        },
        "answer": "B"
    },
    {
        "question": "Which data structure follows the First-In-First-Out (FIFO) principle?",
        "options": {
            "A": "Stack",
            "B": "Queue",
            "C": "Priority Queue",
            "D": "Graph"
        },
        "answer": "B"
    },
    {
        "question": "What is the time complexity of a Binary Search algorithm?",
        "options": {
            "A": "O(n)",
            "B": "O(log n)",
            "C": "O(n log n)",
            "D": "O(1)"
        },
        "answer": "B"
    },
    {
        "question": "Which of the following is required for Binary Search to work correctly?",
        "options": {
            "A": "A Linked List",
            "B": "A sorted array",
            "C": "A balanced tree",
            "D": "An unsorted array"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'worst-case' time complexity of Bubble Sort?",
        "options": {
            "A": "O(n log n)",
            "B": "O(n^2)",
            "C": "O(n)",
            "D": "O(2^n)"
        },
        "answer": "B"
    },
    {
        "question": "Which node in a Doubly Linked List has a NULL 'prev' pointer?",
        "options": {
            "A": "The Tail node",
            "B": "The Head node",
            "C": "The middle node",
            "D": "Every node"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Circular Linked List'?",
        "options": {
            "A": "A list with only one node",
            "B": "A list where the last node points back to the first node",
            "C": "A list shaped like a circle",
            "D": "A list that stores circular data"
        },
        "answer": "B"
    },
    {
        "question": "What is the time complexity to insert an element at the beginning of a Singly Linked List?",
        "options": {
            "A": "O(n)",
            "B": "O(1)",
            "C": "O(log n)",
            "D": "O(n log n)"
        },
        "answer": "B"
    },
    {
        "question": "Which operation is used to add an element to a Stack?",
        "options": {
            "A": "Pop",
            "B": "Enqueue",
            "C": "Push",
            "D": "Peek"
        },
        "answer": "C"
    },
    {
        "question": "Which operation is used to remove an element from a Queue?",
        "options": {
            "A": "Dequeue",
            "B": "Pop",
            "C": "Push",
            "D": "Delete"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Overflow' in the context of data structures?",
        "options": {
            "A": "A program running too fast",
            "B": "Attempting to add an element to a data structure that is already full",
            "C": "Accessing an index that is too small",
            "D": "A memory leak"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Underflow'?",
        "options": {
            "A": "A slow algorithm",
            "B": "Attempting to remove an element from an empty data structure",
            "C": "A type of subquery",
            "D": "A hardware failure"
        },
        "answer": "B"
    },
    {
        "question": "What is the space complexity of an algorithm that creates an array of size 'n'?",
        "options": {
            "A": "O(1)",
            "B": "O(n)",
            "C": "O(n^2)",
            "D": "O(log n)"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is a non-linear data structure?",
        "options": {
            "A": "Stack",
            "B": "Graph",
            "C": "Array",
            "D": "Queue"
        },
        "answer": "B"
    },
    {
        "question": "What is the time complexity of searching for an element in an unsorted array of size n?",
        "options": {
            "A": "O(1)",
            "B": "O(n)",
            "C": "O(log n)",
            "D": "O(n log n)"
        },
        "answer": "B"
    },
    {
        "question": "Which data structure is typically used to implement Function Calls (Recursion) in a compiler?",
        "options": {
            "A": "Queue",
            "B": "Stack",
            "C": "Heap",
            "D": "Hash Table"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Priority Queue'?",
        "options": {
            "A": "A queue where elements are served based on priority instead of FIFO",
            "B": "A queue for VIP users",
            "C": "A queue that is faster than normal",
            "D": "A stack with two ends"
        },
        "answer": "A"
    },
    {
        "question": "What is the time complexity of Selection Sort in the best case?",
        "options": {
            "A": "O(n)",
            "B": "O(n^2)",
            "C": "O(n log n)",
            "D": "O(1)"
        },
        "answer": "B"
    },
    {
        "question": "Which sorting algorithm is known as 'Divide and Conquer'?",
        "options": {
            "A": "Bubble Sort",
            "B": "Merge Sort",
            "C": "Selection Sort",
            "D": "Insertion Sort"
        },
        "answer": "B"
    },
    {
        "question": "What is the time complexity of Merge Sort?",
        "options": {
            "A": "O(n^2)",
            "B": "O(n log n)",
            "C": "O(n)",
            "D": "O(log n)"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Internal Sorting'?",
        "options": {
            "A": "Sorting data that fits entirely in the main memory (RAM)",
            "B": "Sorting data within a class",
            "C": "Sorting hidden data",
            "D": "Sorting on a hard drive"
        },
        "answer": "A"
    },
    {
        "question": "Which sorting algorithm has a worst-case complexity of O(n^2) but an average case of O(n log n)?",
        "options": {
            "A": "Merge Sort",
            "B": "Quick Sort",
            "C": "Heap Sort",
            "D": "Counting Sort"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Pivot' in Quick Sort?",
        "options": {
            "A": "The largest element",
            "B": "An element used to partition the array into two sub-arrays",
            "C": "The first element only",
            "D": "A loop counter"
        },
        "answer": "B"
    },
    {
        "question": "Which data structure is used to implement a 'Breadth-First Search' (BFS) on a graph?",
        "options": {
            "A": "Stack",
            "B": "Queue",
            "C": "Tree",
            "D": "Array"
        },
        "answer": "B"
    },
    {
        "question": "Which data structure is used to implement a 'Depth-First Search' (DFS) on a graph?",
        "options": {
            "A": "Queue",
            "B": "Stack",
            "C": "Linked List",
            "D": "Priority Queue"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Space Complexity'?",
        "options": {
            "A": "The amount of disk space used",
            "B": "The total amount of memory an algorithm needs relative to the input size",
            "C": "The space between characters",
            "D": "The number of lines of code"
        },
        "answer": "B"
    },
    {
        "question": "What is the Big O complexity of O(3n^2 + 5n + 10)?",
        "options": {
            "A": "O(n)",
            "B": "O(n^2)",
            "C": "O(1)",
            "D": "O(3n^2)"
        },
        "answer": "B"
    },
    {
        "question": "A Linked List where each node has a pointer to the next and the previous node is called:",
        "options": {
            "A": "Circular Linked List",
            "B": "Doubly Linked List",
            "C": "Dual Linked List",
            "D": "Binary List"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Deque' (Double Ended Queue)?",
        "options": {
            "A": "A queue that can only be accessed from the front",
            "B": "A queue where insertion and deletion can occur at both ends",
            "C": "A queue for strings",
            "D": "A legacy data structure"
        },
        "answer": "B"
    },
    {
        "question": "What is the time complexity of removing the tail element from a Doubly Linked List?",
        "options": {
            "A": "O(n)",
            "B": "O(1)",
            "C": "O(log n)",
            "D": "O(n log n)"
        },
        "answer": "B"
    },
    {
        "question": "Which data structure is ideal for checking balanced parentheses in an expression?",
        "options": {
            "A": "Queue",
            "B": "Stack",
            "C": "Array",
            "D": "Tree"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Amortized Analysis'?",
        "options": {
            "A": "Calculating the cost per user",
            "B": "Finding the average cost of an operation over a sequence of operations",
            "C": "A type of security scan",
            "D": "A memory leak test"
        },
        "answer": "B"
    },
    {
        "question": "What is the time complexity of adding an element to a 'Dynamic Array' (like ArrayList) when it needs to resize?",
        "options": {
            "A": "O(1)",
            "B": "O(n)",
            "C": "O(log n)",
            "D": "O(n^2)"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Best Case' time complexity of Insertion Sort?",
        "options": {
            "A": "O(n log n)",
            "B": "O(n)",
            "C": "O(n^2)",
            "D": "O(1)"
        },
        "answer": "B"
    },
    {
        "question": "Which sorting algorithm is 'Stable'?",
        "options": {
            "A": "Quick Sort",
            "B": "Merge Sort",
            "C": "Heap Sort",
            "D": "Selection Sort"
        },
        "answer": "B"
    },
    {
        "question": "What does 'Stability' in sorting algorithms mean?",
        "options": {
            "A": "The algorithm never crashes",
            "B": "Records with equal keys retain their relative order after sorting",
            "C": "The algorithm uses constant space",
            "D": "The algorithm is fast"
        },
        "answer": "B"
    },
    {
        "question": "What is 'In-place' sorting?",
        "options": {
            "A": "Sorting only in one location",
            "B": "An algorithm that sorts the input without requiring extra storage space (O(1) extra space)",
            "C": "Sorting data inside a database",
            "D": "Sorting with constant time"
        },
        "answer": "B"
    },
    {
        "question": "Which notation represents the 'tight' bound of an algorithm?",
        "options": {
            "A": "O",
            "B": "Θ (Theta)",
            "C": "Ω",
            "D": "ω"
        },
        "answer": "B"
    },
    {
        "question": "What is the time complexity of Linear Search?",
        "options": {
            "A": "O(1)",
            "B": "O(n)",
            "C": "O(log n)",
            "D": "O(n^2)"
        },
        "answer": "B"
    },
    {
        "question": "How many pointers does a node in a Singly Linked List have?",
        "options": {
            "A": "0",
            "B": "1",
            "C": "2",
            "D": "3"
        },
        "answer": "B"
    },
    {
        "question": "Which structure is used to represent the 'Undo' operation in software?",
        "options": {
            "A": "Queue",
            "B": "Stack",
            "C": "Graph",
            "D": "Tree"
        },
        "answer": "B"
    },
    {
        "question": "Which structure is used for 'Printer Spooling'?",
        "options": {
            "A": "Stack",
            "B": "Queue",
            "C": "Tree",
            "D": "Array"
        },
        "answer": "B"
    },
    {
        "question": "What is the Big O complexity of O(log n + n)?",
        "options": {
            "A": "O(log n)",
            "B": "O(n)",
            "C": "O(n log n)",
            "D": "O(1)"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Sentinel Node' in a Linked List?",
        "options": {
            "A": "A node with secret data",
            "B": "A dummy node used to simplify boundary conditions like head/tail insertion",
            "C": "The middle node",
            "D": "A node that has been deleted"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Time-Space Tradeoff'?",
        "options": {
            "A": "Buying more RAM to save time",
            "B": "Increasing memory usage to reduce execution time, or vice-versa",
            "C": "The cost of building a server",
            "D": "The time it takes to move data"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 1: Which data structure allows for O(1) time complexity for both Enqueue and Dequeue?",
        "options": {
            "A": "Array-based Queue (with front/rear pointers)",
            "B": "Linked List-based Queue",
            "C": "Sorted Array",
            "D": "Both A and B"
        },
        "answer": "D"
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
    skill = "C"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
