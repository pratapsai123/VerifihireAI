from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
  {
    "question": "What is the primary difference between 'val' and 'var' in Scala?",
    "options": {
      "A": "val is for mutable variables; var is for immutable constants.",
      "B": "val is immutable (read-only); var is mutable.",
      "C": "val is only for integers; var is for strings.",
      "D": "val is private; var is public."
    },
    "answer": "B"
  },
  {
    "question": "Which keyword is used to define a function in Scala?",
    "options": {
      "A": "function",
      "B": "func",
      "C": "def",
      "D": "val"
    },
    "answer": "C"
  },
  {
    "question": "Scala is often described as a 'multi-paradigm' language. Which two paradigms does it primarily combine?",
    "options": {
      "A": "Procedural and Logic",
      "B": "Object-Oriented and Functional",
      "C": "Imperative and Low-level Assembly",
      "D": "Scripting and Markup"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Case Class' in Scala primarily used for?",
    "options": {
      "A": "To create GUI components",
      "B": "To model immutable data and enable pattern matching",
      "C": "To handle database connections specifically",
      "D": "To define global constants"
    },
    "answer": "B"
  },
  {
    "question": "What is the result of the following expression: 'val x = List(1, 2, 3); x.map(_ * 2)'?",
    "options": {
      "A": "List(2, 4, 6)",
      "B": "List(1, 2, 3, 1, 2, 3)",
      "C": "6",
      "D": "Error: map is not a function"
    },
    "answer": "A"
  },
  {
    "question": "In Scala, what does 'Unit' represent?",
    "options": {
      "A": "The number 1",
      "B": "A value that indicates the absence of a meaningful value (similar to void in Java)",
      "C": "A single-threaded process",
      "D": "The smallest data type (1 bit)"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Pattern Matching' in Scala most similar to in other languages, but more powerful?",
    "options": {
      "A": "If-Else statements",
      "B": "Switch statements",
      "C": "For loops",
      "D": "Try-Catch blocks"
    },
    "answer": "B"
  },
  {
    "question": "Which of the following describes a 'Trait' in Scala?",
    "options": {
      "A": "A class that cannot be inherited",
      "B": "A unit that encapsulates method and field definitions, which can be reused by mixing them into classes",
      "C": "A specialized function for mathematical operations",
      "D": "A way to define global variables"
    },
    "answer": "B"
  },
  {
    "question": "What is an 'Option' type in Scala used for?",
    "options": {
      "A": "To provide optional command-line arguments",
      "B": "To represent a value that may or may not be present, avoiding NullPointerExceptions",
      "C": "To choose between different compilers",
      "D": "To define optional parameters in a constructor"
    },
    "answer": "B"
  },
  {
    "question": "True or False: In Scala, every value is an object, and every operation is a method call.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Currying' in Scala?",
    "options": {
      "A": "A technique of transforming a function that takes multiple arguments into a chain of functions each taking a single argument",
      "B": "A method for encrypting string data",
      "C": "The process of compiling Scala into JavaScript",
      "D": "An optimization for recursive functions"
    },
    "answer": "A"
  },
  {
    "question": "What is a 'Singleton Object' in Scala defined with the 'object' keyword?",
    "options": {
      "A": "A class that can only have one instance, created automatically",
      "B": "A variable that can only hold one value",
      "C": "An object that only works on a single CPU core",
      "D": "A way to define private classes"
    },
    "answer": "A"
  },
  {
    "question": "Which collection type is immutable by default in Scala?",
    "options": {
      "A": "Array",
      "B": "List",
      "C": "StringBuilder",
      "D": "Buffer"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'yield' keyword do when used with a 'for' comprehension?",
    "options": {
      "A": "Exits the loop immediately",
      "B": "Pauses the execution of the function",
      "C": "Constructs a new collection based on the results of the loop iterations",
      "D": "Returns a value to the caller and terminates the program"
    },
    "answer": "C"
  },
  {
    "question": "What is a 'Pure Function' in functional programming?",
    "options": {
      "A": "A function that has no parameters",
      "B": "A function whose output depends only on its input and has no side effects",
      "C": "A function that only uses the 'Double' data type",
      "D": "A function defined inside a class"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Lazy val'?",
    "options": {
      "A": "To define a variable that never changes",
      "B": "To delay the initialization of a variable until it is accessed for the first time",
      "C": "To create a variable that uses less memory",
      "D": "To allow a variable to be null"
    },
    "answer": "B"
  },
  {
    "question": "How do you define a 'Companion Object' in Scala?",
    "options": {
      "A": "By naming an object differently from its class",
      "B": "By defining an object with the same name as a class in the same source file",
      "C": "By using the 'companion' keyword",
      "D": "By nesting an object inside a class"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Tail Recursion' optimization in Scala?",
    "options": {
      "A": "A way to write loops in reverse",
      "B": "A compiler optimization that prevents stack overflow by reusing the current stack frame for recursive calls",
      "C": "A method to speed up string concatenation",
      "D": "A process to clean up unused memory at the end of a function"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO common subtypes of 'Option' in Scala:",
    "options": {
      "A": "Some",
      "B": "None",
      "C": "Null",
      "D": "Empty"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is 'Implicits' (or 'Using' clauses in Scala 3) primarily used for?",
    "options": {
      "A": "To hide code from other developers",
      "B": "To reduce boilerplate by letting the compiler provide arguments or conversions automatically",
      "C": "To force the program to run faster",
      "D": "To define variables that are implicit in the operating system"
    },
    "answer": "B"
  },
  {
    "question": "Which collection method is used to combine two lists into a list of pairs (tuples)?",
    "options": {
      "A": "combine",
      "B": "zip",
      "C": "merge",
      "D": "pair"
    },
    "answer": "B"
  },
  {
    "question": "In Scala's 'Try' type, which two subclasses represent the result of a computation?",
    "options": {
      "A": "Success and Failure",
      "B": "Some and None",
      "C": "Right and Left",
      "D": "Valid and Invalid"
    },
    "answer": "A"
  },
  {
    "question": "What is the primary benefit of using 'Either[A, B]' for error handling?",
    "options": {
      "A": "It automatically restarts the program on failure.",
      "B": "It allows you to return a specific error value (usually on the Left) instead of just an exception.",
      "C": "It is faster than using Try-Catch blocks.",
      "D": "It only works with integers."
    },
    "answer": "B"
  },
  {
    "question": "True or False: In Scala 3, the 'enum' keyword can be used to define Algebraic Data Types (ADTs) more concisely.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What does the 'foldLeft' operation do on a collection?",
    "options": {
      "A": "It deletes all elements from the left side.",
      "B": "It reduces a collection to a single value by applying a binary operator from left to right, starting with an initial seed.",
      "C": "It sorts the list in descending order.",
      "D": "It splits the list into two halves."
    },
    "answer": "B"
  },
  {
    "question": "Which of the following describes an 'Opaque Type Alias' in Scala 3?",
    "options": {
      "A": "A type that is hidden from the compiler.",
      "B": "A type alias that provides zero-overhead abstraction by hiding its implementation details outside its scope.",
      "C": "A type that can only be used in dark-themed IDEs.",
      "D": "A way to make variables invisible to the debugger."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Referential Transparency'?",
    "options": {
      "A": "The ability to see the memory address of a variable.",
      "B": "The property where an expression can be replaced by its result without changing the program's behavior.",
      "C": "A way to make private fields public.",
      "D": "A type of network transparency in Akka."
    },
    "answer": "B"
  },
  {
    "question": "Which collection is better suited for frequent element lookups by a unique key?",
    "options": {
      "A": "List",
      "B": "Map",
      "C": "Vector",
      "D": "Queue"
    },
    "answer": "B"
  },
  {
    "question": "True or False: A 'Future' in Scala is 'eager', meaning it starts executing as soon as it is defined.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "In Scala 3, what is the purpose of the 'export' keyword?",
    "options": {
      "A": "To save the code to a text file.",
      "B": "To define aliases for members of an object or class, making them available in the current scope.",
      "C": "To send data to a remote API.",
      "D": "To mark a class as public."
    },
    "answer": "B"
  },
  {
    "question": "In Scala 3, what is the 'extension' keyword used for?",
    "options": {
      "A": "To inherit from multiple classes simultaneously.",
      "B": "To add new methods to an existing type without modifying its source code or using inheritance.",
      "C": "To increase the memory limit of a running JVM.",
      "D": "To mark a class as 'open' for external modification."
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Type Class' in Scala?",
    "options": {
      "A": "A special class that only holds types, not values.",
      "B": "A design pattern that allows you to add behavior to types without changing the types themselves, using implicits or givens.",
      "C": "A class that automatically converts strings to integers.",
      "D": "The base class for all Scala collections."
    },
    "answer": "B"
  },
  {
    "question": "What does the 'unapply' method do in a Scala 'object'?",
    "options": {
      "A": "It deletes an instance of a class.",
      "B": "It acts as an 'extractor' that takes an object and tries to give back its arguments, enabling pattern matching.",
      "C": "It reverses a string.",
      "D": "It prevents a class from being instantiated."
    },
    "answer": "B"
  },
  {
    "question": "True or False: A 'Monad' in Scala is any type that implements 'flatMap' and 'unit' (or a constructor) and follows specific algebraic laws.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'Cake Pattern' in Scala primarily used for?",
    "options": {
      "A": "Designing UI layouts.",
      "B": "A dependency injection pattern using traits and self-type annotations.",
      "C": "A way to organize test data.",
      "D": "Formatting JSON responses."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO features of 'Self-Type Annotations' (e.g., 'this: Base =>'):",
    "options": {
      "A": "They allow a trait to require that any class mixing it in must also extend a specific base type.",
      "B": "They provide a way to perform dependency injection.",
      "C": "They automatically make all methods in a trait private.",
      "D": "They prevent a trait from having any methods."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is the 'Nothing' type in Scala?",
    "options": {
      "A": "The same as 'null' in Java.",
      "B": "A bottom type that is a subtype of every other type; it has no instances and is used to signal non-termination or exceptions.",
      "C": "A type used for empty strings.",
      "D": "A synonym for 'Unit'."
    },
    "answer": "B"
  },
  {
    "question": "What is the difference between 'Sequence' (Seq) and 'IndexedSeq' in Scala?",
    "options": {
      "A": "There is no difference.",
      "B": "IndexedSeq provides efficient (usually constant time) random access to elements.",
      "C": "Seq can only hold integers; IndexedSeq can hold any type.",
      "D": "IndexedSeq is always mutable."
    },
    "answer": "B"
  },
  {
    "question": "True or False: Scala 3 'Union Types' (A | B) allow a variable to hold a value that is either of type A or type B.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Invariance' in Scala generics?",
    "options": {
      "A": "When a generic type allows subtyping (e.g., List[String] is a List[Object]).",
      "B": "When a generic type does NOT allow any subtyping relationship (e.g., Container[String] is not a Container[Object]).",
      "C": "When a type cannot be changed once defined.",
      "D": "When a function returns the same value regardless of input."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO common types of variance in Scala:",
    "options": {
      "A": "Covariance (+T)",
      "B": "Contravariance (-T)",
      "C": "Multivariance (*T)",
      "D": "Divariance (/T)"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is a 'Higher-Kinded Type'?",
    "options": {
      "A": "A type that is defined at the top of a file.",
      "B": "A type that takes another type constructor as a parameter (e.g., F[_]).",
      "C": "A type that can only be used by senior developers.",
      "D": "A type that represents a mathematical infinity."
    },
    "answer": "B"
  },
  {
    "question": "True or False: The 'Context Bound' syntax (e.g., [T : Ordering]) is a shorthand for requiring an implicit/given instance of a type class for T.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'AnyVal' class in Scala?",
    "options": {
      "A": "The root of all types.",
      "B": "The parent class for all value types (like Int, Double, Boolean) that are represented as primitives at runtime.",
      "C": "A type used only for validation.",
      "D": "A class used to store any object."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Partial Application' of a function?",
    "options": {
      "A": "When a function only runs half of its code.",
      "B": "Providing only some of the arguments to a function, resulting in a new function that takes the remaining arguments.",
      "C": "Calling a function that has no return value.",
      "D": "A function that is only partially compiled."
    },
    "answer": "B"
  },
  {
    "question": "In Scala 3, what replaces the old 'whitebox' macros for type-level programming?",
    "options": {
      "A": "Reflection API",
      "B": "Inline methods and Quotes/Splices",
      "C": "Annotation processors",
      "D": "Dynamic traits"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary purpose of the 'inline' keyword in Scala 3?",
    "options": {
      "A": "To make the code look prettier.",
      "B": "To ensure that a method's code is inserted at the call site during compilation, enabling compile-time computation.",
      "C": "To force a function to run on the main thread.",
      "D": "To allow a method to be used inside an HTML file."
    },
    "answer": "B"
  },
  {
    "question": "True or False: Scala is binary compatible with Java, meaning you can call Java methods from Scala and vice versa without any extra configuration.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What does the '@tailrec' annotation do?",
    "options": {
      "A": "It automatically makes any function faster.",
      "B": "It instructs the compiler to verify that a function is tail-recursive and fails compilation if it is not.",
      "C": "It marks a function as 'deprecated'.",
      "D": "It allows a function to access the private variables of other classes."
    },
    "answer": "B"
  },
  {
    "question": "In the 'Cats' library, what is a 'Semigroup'?",
    "options": {
      "A": "A group of junior developers.",
      "B": "A type class that provides a way to combine two values of the same type (associative binary operation).",
      "C": "A database connection pool.",
      "D": "A type of collection that can only hold strings."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO features of 'ZIO' (Functional Effect System):",
    "options": {
      "A": "Type-safe, composable asynchronous and concurrent programming.",
      "B": "Built-in dependency injection via the 'ZLayer' system.",
      "C": "It is a replacement for the Scala compiler.",
      "D": "It only works with SQL databases."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is 'Eta Expansion' in Scala?",
    "options": {
      "A": "Converting a method into a function object.",
      "B": "Increasing the memory of the JVM.",
      "C": "A type of string concatenation.",
      "D": "Automatically adding 'null' checks to every variable."
    },
    "answer": "A"
  },
  {
    "question": "True or False: 'Value Classes' (classes extending AnyVal) are used to avoid runtime object allocation for simple wrappers around primitives.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Trampiline' in functional programming?",
    "options": {
      "A": "A way to jump between different servers.",
      "B": "A technique to implement mutual recursion without blowing the stack by using objects to represent pending computations.",
      "C": "A type of fast-access cache.",
      "D": "A specialized data structure for storing trees."
    },
    "answer": "B"
  },
  {
    "question": "Which keyword in Scala 3 allows you to create a type that is a combination of two others (Intersection Types)?",
    "options": {
      "A": "A | B",
      "B": "A & B",
      "C": "A with B",
      "&": "A combine B"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Phantom Types' pattern used for?",
    "options": {
      "A": "Creating objects that don't exist in memory.",
      "B": "Using type parameters that never appear in the constructor to enforce state-related constraints at compile time.",
      "C": "A security technique to hide code.",
      "D": "A way to handle null values."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Quasiquotes' were the primary way to manipulate Scala code in the Scala 2 macro system.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'Magnet Pattern' used for in Scala libraries like Akka HTTP?",
    "options": {
      "A": "To pull data from a database faster.",
      "B": "To solve problems with method overloading and type erasure by using a single method that accepts a 'magnet' object.",
      "C": "To attract more users to the website.",
      "D": "To stick variables to a specific thread."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO common build tools used for Scala projects:",
    "options": {
      "A": "sbt (Scala Build Tool)",
      "B": "Mill",
      "C": "Adobe Creative Cloud",
      "D": "Docker Desktop"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is the role of 'Dotty' in the Scala ecosystem?",
    "options": {
      "A": "It is a specialized library for graphics.",
      "B": "It was the project name for the new compiler that eventually became Scala 3.",
      "C": "It is a tool for cleaning up old code.",
      "D": "It is a replacement for the Java Virtual Machine."
    },
    "answer": "B"
  },
  {
    "question": "What is the primary purpose of 'Opaque Type Aliases' introduced in Scala 3?",
    "options": {
      "A": "To make variables invisible to the debugger.",
      "B": "To provide zero-overhead type abstractions that hide their underlying implementation outside of their defining scope.",
      "C": "To prevent other developers from reading the source code.",
      "D": "To allow multiple types to share the same memory address."
    },
    "answer": "B"
  },
  {
    "question": "In Scala 3 metaprogramming, what is the role of 'Quotes' (e.g., '{ ... }')?",
    "options": {
      "A": "To mark a string as a literal.",
      "B": "To turn code into a data structure (Expr) that can be manipulated at compile time.",
      "C": "To comment out a block of code.",
      "D": "To define a multi-line variable."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Splices' (e.g., '${ ... }') are used inside a quote to evaluate an expression and insert its result back into the quoted code.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What are 'Generalized Algebraic Data Types' (GADTs) in Scala?",
    "options": {
      "A": "Algebra classes used for high-speed math.",
      "B": "Enum or class hierarchies where the type parameters in the result of a constructor can be more specific than the type being defined.",
      "C": "A way to automatically generate unit tests.",
      "D": "A database schema migration tool."
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the '@targetName' annotation in Scala 3?",
    "options": {
      "A": "To specify the name of the developer who wrote the code.",
      "B": "To provide an alternative name for a method or field in the compiled bytecode, useful for Java interoperability.",
      "C": "To target a specific CPU architecture.",
      "D": "To mark a function for deletion in the next version."
    },
    "answer": "B"
  },
  {
    "question": "Which keyword is used in Scala 3 to define an 'extension' that can be imported and used as if it were a method of the type?",
    "options": {
      "A": "implicit",
      "B": "extension",
      "C": "using",
      "D": "extra"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO characteristics of 'ZIO' (Functional Effect System) compared to standard Scala Futures:",
    "options": {
      "A": "ZIO effects are 'lazy' and do not execute until explicitly run.",
      "B": "ZIO provides built-in support for interruption and resource safety (bracket/acquireRelease).",
      "C": "ZIO requires a dedicated hardware processor to run.",
      "D": "ZIO is only compatible with the Java 8 runtime."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: In Scala 3, 'Intersection Types' (A & B) represent a value that is both an instance of A AND an instance of B.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Kind-Projector' functionality used for in Scala (now largely built into Scala 3)?",
    "options": {
      "A": "To project 3D graphics in a browser.",
      "B": "To simplify the syntax for defining partially applied type constructors (Higher-Kinded Types).",
      "C": "To search for bugs in the compiler.",
      "D": "To manage project dependencies."
    },
    "answer": "B"
  },
  {
    "question": "In 'Akka Streams', what is the role of a 'Flow'?",
    "options": {
      "A": "To store the entire dataset in memory.",
      "B": "A processing stage which has exactly one input and one output, used to transform data.",
      "C": "To handle user authentication.",
      "D": "To define the physical network path."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Eta-Expansion' in the Scala compiler?",
    "options": {
      "A": "A process that converts a method into a function value (object).",
      "B": "Increasing the memory of the JVM.",
      "C": "A type of string concatenation.",
      "D": "A way to compress compiled bytecode."
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO common features of 'Cats Effect':",
    "options": {
      "A": "The IO monad for managing synchronous and asynchronous effects.",
      "B": "A rich set of concurrency primitives like Fibers, Ref, and Deferred.",
      "C": "It is a graphical library for drawing cats.",
      "D": "It replaces the standard Scala 'for' comprehension."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Implicit Conversions' are still widely used in Scala 3 as the primary way to implement type classes.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Invariance' mean in a Scala generic type like Container[T]?",
    "options": {
      "A": "Container[Sub] is a subtype of Container[Super].",
      "B": "Container[Super] is a subtype of Container[Sub].",
      "C": "There is no subtyping relationship between Container[Sub] and Container[Super].",
      "D": "The type T can never be changed."
    },
    "answer": "C"
  },
  {
    "question": "What is the purpose of the 'Nothing' type in the Scala hierarchy?",
    "options": {
      "A": "It represents a null reference.",
      "B": "It is the 'bottom type' which is a subtype of every other type; used to signal non-returning functions or exceptions.",
      "C": "It is an alias for Unit.",
      "D": "It is used for variables that have no name."
    },
    "answer": "B"
  },
  {
    "question": "What is the primary purpose of 'Opaque Type Aliases' introduced in Scala 3?",
    "options": {
      "A": "To make variables invisible to the debugger.",
      "B": "To provide zero-overhead type abstractions that hide their underlying implementation outside of their defining scope.",
      "C": "To prevent other developers from reading the source code.",
      "D": "To allow multiple types to share the same memory address."
    },
    "answer": "B"
  },
  {
    "question": "In Scala 3 metaprogramming, what is the role of 'Quotes' (e.g., '{ ... }')?",
    "options": {
      "A": "To mark a string as a literal.",
      "B": "To turn code into a data structure (Expr) that can be manipulated at compile time.",
      "C": "To comment out a block of code.",
      "D": "To define a multi-line variable."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Splices' (e.g., '${ ... }') are used inside a quote to evaluate an expression and insert its result back into the quoted code.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What are 'Generalized Algebraic Data Types' (GADTs) in Scala?",
    "options": {
      "A": "Algebra classes used for high-speed math.",
      "B": "Enum or class hierarchies where the type parameters in the result of a constructor can be more specific than the type being defined.",
      "C": "A way to automatically generate unit tests.",
      "D": "A database schema migration tool."
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the '@targetName' annotation in Scala 3?",
    "options": {
      "A": "To specify the name of the developer who wrote the code.",
      "B": "To provide an alternative name for a method or field in the compiled bytecode, useful for Java interoperability.",
      "C": "To target a specific CPU architecture.",
      "D": "To mark a function for deletion in the next version."
    },
    "answer": "B"
  },
  {
    "question": "Which keyword is used in Scala 3 to define an 'extension' that can be imported and used as if it were a method of the type?",
    "options": {
      "A": "implicit",
      "B": "extension",
      "C": "using",
      "D": "extra"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO characteristics of 'ZIO' (Functional Effect System) compared to standard Scala Futures:",
    "options": {
      "A": "ZIO effects are 'lazy' and do not execute until explicitly run.",
      "B": "ZIO provides built-in support for interruption and resource safety (bracket/acquireRelease).",
      "C": "ZIO requires a dedicated hardware processor to run.",
      "D": "ZIO is only compatible with the Java 8 runtime."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: In Scala 3, 'Intersection Types' (A & B) represent a value that is both an instance of A AND an instance of B.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Kind-Projector' functionality used for in Scala (now largely built into Scala 3)?",
    "options": {
      "A": "To project 3D graphics in a browser.",
      "B": "To simplify the syntax for defining partially applied type constructors (Higher-Kinded Types).",
      "C": "To search for bugs in the compiler.",
      "D": "To manage project dependencies."
    },
    "answer": "B"
  },
  {
    "question": "In 'Akka Streams', what is the role of a 'Flow'?",
    "options": {
      "A": "To store the entire dataset in memory.",
      "B": "A processing stage which has exactly one input and one output, used to transform data.",
      "C": "To handle user authentication.",
      "D": "To define the physical network path."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Eta-Expansion' in the Scala compiler?",
    "options": {
      "A": "A process that converts a method into a function value (object).",
      "B": "Increasing the memory of the JVM.",
      "C": "A type of string concatenation.",
      "D": "A way to compress compiled bytecode."
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO common features of 'Cats Effect':",
    "options": {
      "A": "The IO monad for managing synchronous and asynchronous effects.",
      "B": "A rich set of concurrency primitives like Fibers, Ref, and Deferred.",
      "C": "It is a graphical library for drawing cats.",
      "D": "It replaces the standard Scala 'for' comprehension."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Implicit Conversions' are still widely used in Scala 3 as the primary way to implement type classes.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Invariance' mean in a Scala generic type like Container[T]?",
    "options": {
      "A": "Container[Sub] is a subtype of Container[Super].",
      "B": "Container[Super] is a subtype of Container[Sub].",
      "C": "There is no subtyping relationship between Container[Sub] and Container[Super].",
      "D": "The type T can never be changed."
    },
    "answer": "C"
  },
  {
    "question": "What is the purpose of the 'Nothing' type in the Scala hierarchy?",
    "options": {
      "A": "It represents a null reference.",
      "B": "It is the 'bottom type' which is a subtype of every other type; used to signal non-returning functions or exceptions.",
      "C": "It is an alias for Unit.",
      "D": "It is used for variables that have no name."
    },
    "answer": "B"
  },
  {
    "question": "What is the primary purpose of 'Opaque Type Aliases' introduced in Scala 3?",
    "options": {
      "A": "To make variables invisible to the debugger.",
      "B": "To provide zero-overhead type abstractions that hide their underlying implementation outside of their defining scope.",
      "C": "To prevent other developers from reading the source code.",
      "D": "To allow multiple types to share the same memory address."
    },
    "answer": "B"
  },
  {
    "question": "In Scala 3 metaprogramming, what is the role of 'Quotes' (e.g., '{ ... }')?",
    "options": {
      "A": "To mark a string as a literal.",
      "B": "To turn code into a data structure (Expr) that can be manipulated at compile time.",
      "C": "To comment out a block of code.",
      "D": "To define a multi-line variable."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Splices' (e.g., '${ ... }') are used inside a quote to evaluate an expression and insert its result back into the quoted code.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What are 'Generalized Algebraic Data Types' (GADTs) in Scala?",
    "options": {
      "A": "Algebra classes used for high-speed math.",
      "B": "Enum or class hierarchies where the type parameters in the result of a constructor can be more specific than the type being defined.",
      "C": "A way to automatically generate unit tests.",
      "D": "A database schema migration tool."
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the '@targetName' annotation in Scala 3?",
    "options": {
      "A": "To specify the name of the developer who wrote the code.",
      "B": "To provide an alternative name for a method or field in the compiled bytecode, useful for Java interoperability.",
      "C": "To target a specific CPU architecture.",
      "D": "To mark a function for deletion in the next version."
    },
    "answer": "B"
  },
  {
    "question": "Which keyword is used in Scala 3 to define an 'extension' that can be imported and used as if it were a method of the type?",
    "options": {
      "A": "implicit",
      "B": "extension",
      "C": "using",
      "D": "extra"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO characteristics of 'ZIO' (Functional Effect System) compared to standard Scala Futures:",
    "options": {
      "A": "ZIO effects are 'lazy' and do not execute until explicitly run.",
      "B": "ZIO provides built-in support for interruption and resource safety (bracket/acquireRelease).",
      "C": "ZIO requires a dedicated hardware processor to run.",
      "D": "ZIO is only compatible with the Java 8 runtime."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: In Scala 3, 'Intersection Types' (A & B) represent a value that is both an instance of A AND an instance of B.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Kind-Projector' functionality used for in Scala (now largely built into Scala 3)?",
    "options": {
      "A": "To project 3D graphics in a browser.",
      "B": "To simplify the syntax for defining partially applied type constructors (Higher-Kinded Types).",
      "C": "To search for bugs in the compiler.",
      "D": "To manage project dependencies."
    },
    "answer": "B"
  },
  {
    "question": "In 'Akka Streams', what is the role of a 'Flow'?",
    "options": {
      "A": "To store the entire dataset in memory.",
      "B": "A processing stage which has exactly one input and one output, used to transform data.",
      "C": "To handle user authentication.",
      "D": "To define the physical network path."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Eta-Expansion' in the Scala compiler?",
    "options": {
      "A": "A process that converts a method into a function value (object).",
      "B": "Increasing the memory of the JVM.",
      "C": "A type of string concatenation.",
      "D": "A way to compress compiled bytecode."
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO common features of 'Cats Effect':",
    "options": {
      "A": "The IO monad for managing synchronous and asynchronous effects.",
      "B": "A rich set of concurrency primitives like Fibers, Ref, and Deferred.",
      "C": "It is a graphical library for drawing cats.",
      "D": "It replaces the standard Scala 'for' comprehension."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Implicit Conversions' are still widely used in Scala 3 as the primary way to implement type classes.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Invariance' mean in a Scala generic type like Container[T]?",
    "options": {
      "A": "Container[Sub] is a subtype of Container[Super].",
      "B": "Container[Super] is a subtype of Container[Sub].",
      "C": "There is no subtyping relationship between Container[Sub] and Container[Super].",
      "D": "The type T can never be changed."
    },
    "answer": "C"
  },
  {
    "question": "What is the purpose of the 'Nothing' type in the Scala hierarchy?",
    "options": {
      "A": "It represents a null reference.",
      "B": "It is the 'bottom type' which is a subtype of every other type; used to signal non-returning functions or exceptions.",
      "C": "It is an alias for Unit.",
      "D": "It is used for variables that have no name."
    },
    "answer": "B"
  },
  {
    "question": "What is the primary purpose of 'Opaque Type Aliases' introduced in Scala 3?",
    "options": {
      "A": "To make variables invisible to the debugger.",
      "B": "To provide zero-overhead type abstractions that hide their underlying implementation outside of their defining scope.",
      "C": "To prevent other developers from reading the source code.",
      "D": "To allow multiple types to share the same memory address."
    },
    "answer": "B"
  },
  {
    "question": "In Scala 3 metaprogramming, what is the role of 'Quotes' (e.g., '{ ... }')?",
    "options": {
      "A": "To mark a string as a literal.",
      "B": "To turn code into a data structure (Expr) that can be manipulated at compile time.",
      "C": "To comment out a block of code.",
      "D": "To define a multi-line variable."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Splices' (e.g., '${ ... }') are used inside a quote to evaluate an expression and insert its result back into the quoted code.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What are 'Generalized Algebraic Data Types' (GADTs) in Scala?",
    "options": {
      "A": "Algebra classes used for high-speed math.",
      "B": "Enum or class hierarchies where the type parameters in the result of a constructor can be more specific than the type being defined.",
      "C": "A way to automatically generate unit tests.",
      "D": "A database schema migration tool."
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the '@targetName' annotation in Scala 3?",
    "options": {
      "A": "To specify the name of the developer who wrote the code.",
      "B": "To provide an alternative name for a method or field in the compiled bytecode, useful for Java interoperability.",
      "C": "To target a specific CPU architecture.",
      "D": "To mark a function for deletion in the next version."
    },
    "answer": "B"
  },
  {
    "question": "Which keyword is used in Scala 3 to define an 'extension' that can be imported and used as if it were a method of the type?",
    "options": {
      "A": "implicit",
      "B": "extension",
      "C": "using",
      "D": "extra"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO characteristics of 'ZIO' (Functional Effect System) compared to standard Scala Futures:",
    "options": {
      "A": "ZIO effects are 'lazy' and do not execute until explicitly run.",
      "B": "ZIO provides built-in support for interruption and resource safety (bracket/acquireRelease).",
      "C": "ZIO requires a dedicated hardware processor to run.",
      "D": "ZIO is only compatible with the Java 8 runtime."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: In Scala 3, 'Intersection Types' (A & B) represent a value that is both an instance of A AND an instance of B.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Kind-Projector' functionality used for in Scala (now largely built into Scala 3)?",
    "options": {
      "A": "To project 3D graphics in a browser.",
      "B": "To simplify the syntax for defining partially applied type constructors (Higher-Kinded Types).",
      "C": "To search for bugs in the compiler.",
      "D": "To manage project dependencies."
    },
    "answer": "B"
  },
  {
    "question": "In 'Akka Streams', what is the role of a 'Flow'?",
    "options": {
      "A": "To store the entire dataset in memory.",
      "B": "A processing stage which has exactly one input and one output, used to transform data.",
      "C": "To handle user authentication.",
      "D": "To define the physical network path."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Eta-Expansion' in the Scala compiler?",
    "options": {
      "A": "A process that converts a method into a function value (object).",
      "B": "Increasing the memory of the JVM.",
      "C": "A type of string concatenation.",
      "D": "A way to compress compiled bytecode."
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO common features of 'Cats Effect' IO:",
    "options": {
      "A": "The IO monad for managing synchronous and asynchronous effects.",
      "B": "A rich set of concurrency primitives like Fibers, Ref, and Deferred.",
      "C": "It is a graphical library for drawing cats.",
      "D": "It replaces the standard Scala 'for' comprehension."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Implicit Conversions' are still widely used in Scala 3 as the primary way to implement type classes.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Invariance' mean in a Scala generic type like Container[T]?",
    "options": {
      "A": "Container[Sub] is a subtype of Container[Super].",
      "B": "Container[Super] is a subtype of Container[Sub].",
      "C": "There is no subtyping relationship between Container[Sub] and Container[Super].",
      "D": "The type T can never be changed."
    },
    "answer": "C"
  },
  {
    "question": "What is the purpose of the 'Nothing' type in the Scala hierarchy?",
    "options": {
      "A": "It represents a null reference.",
      "B": "It is the 'bottom type' which is a subtype of every other type; used to signal non-returning functions or exceptions.",
      "C": "It is an alias for Unit.",
      "D": "It is used for variables that have no name."
    },
    "answer": "B"
  },
  {
    "question": "What is the primary purpose of 'Opaque Type Aliases' introduced in Scala 3?",
    "options": {
      "A": "To make variables invisible to the debugger.",
      "B": "To provide zero-overhead type abstractions that hide their underlying implementation outside of their defining scope.",
      "C": "To prevent other developers from reading the source code.",
      "D": "To allow multiple types to share the same memory address."
    },
    "answer": "B"
  },
  {
    "question": "What is 'TASTY' in the context of Scala 3?",
    "options": {
      "A": "A new library for JSON parsing.",
      "B": "The Typed Abstract Syntax Tree format used by the compiler for separate compilation and metaprogramming.",
      "C": "A testing framework for functional code.",
      "D": "A way to optimize memory usage in the JVM."
    },
    "answer": "B"
  },
  {
    "question": "In the 'Doobie' library, what does 'transact' do?",
    "options": {
      "A": "Translates Scala code into SQL strings.",
      "B": "Executes a ConnectionIO program as a single transaction against a database using a Transactor.",
      "C": "Sends a message to an Akka actor.",
      "D": "Converts a List into a Map."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Value Classes' (extending AnyVal) can sometimes be boxed at runtime if they are used as part of an array or passed to a generic function.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Eta-Expansion'?",
    "options": {
      "A": "The process of converting a method into a function value (instance of FunctionN).",
      "B": "Increasing the memory limit of the JVM stack.",
      "C": "A type of string concatenation optimization.",
      "D": "A feature for defining multi-line strings."
    },
    "answer": "A"
  },
  {
    "question": "Which HTTP model does 'Http4s' primarily use?",
    "options": {
      "A": "Blocking I/O with Servlets.",
      "B": "Purely functional, streaming, and built on top of FS2 and Cats Effect.",
      "C": "Actor-based communication using Akka HTTP.",
      "D": "Synchronous request-response using standard Java threads."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO benefits of 'Opaque Types' in Scala 3 compared to 'Value Classes':",
    "options": {
      "A": "They are guaranteed to have zero runtime overhead (no boxing).",
      "B": "They allow for cleaner syntax without the need to extend AnyVal.",
      "C": "They automatically encrypt the data they hold.",
      "D": "They can be used to define new primitive types."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is a 'Type Lambda' in Scala 3 syntax (e.g., [X] =>> List[X])?",
    "options": {
      "A": "A function that runs during compilation.",
      "B": "An anonymous type constructor used to partially apply types.",
      "C": "A way to define variables inside a type definition.",
      "D": "A specialized version of a lambda function."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Structural Types' in Scala 3 use reflection to access members by default, which can impact performance.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the primary role of 'FS2' in the Scala ecosystem?",
    "options": {
      "A": "A file system utility library.",
      "B": "A compositional, streaming library for functional programming in Scala.",
      "C": "A replacement for the Scala Standard Library.",
      "D": "A tool for managing database migrations."
    },
    "answer": "B"
  },
  {
    "question": "What does the '@experimental' annotation do in Scala 3?",
    "options": {
      "A": "Marks code for deletion in the next release.",
      "B": "Enables the use of experimental language features that are not yet part of the stable standard.",
      "C": "Instructs the compiler to run tests automatically.",
      "D": "Prevents the code from being compiled into production builds."
    },
    "answer": "B"
  },
  {
    "question": "Which Scala 3 feature replaces the need for 'Simulacrum' when defining type classes?",
    "options": {
      "A": "Implicit classes.",
      "B": "Extension methods and given instances.",
      "C": "Dynamic traits.",
      "D": "Macro annotations."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO characteristics of 'Tagless Final' pattern in Scala:",
    "options": {
      "A": "It decouples the definition of an algebra from its implementation using context bounds (F[_]).",
      "B": "It allows switching between different effect types (e.g., Option, Future, IO) easily.",
      "C": "It is a way to tag variables for garbage collection.",
      "D": "It requires the use of Akka actors."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: In Scala 3, you can use 'parameterless' methods as if they were values (Uniform Access Principle).",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'Magnet Pattern' used to solve in Scala libraries?",
    "options": {
      "A": "Attracting more users to the site.",
      "B": "Issues with method overloading and type erasure by using a single method that accepts a 'magnet' object.",
      "C": "Memory leaks in long-running processes.",
      "D": "Slow compilation times."
    },
    "answer": "B"
  },
  {
    "question": "Which command is used to run the Scala 3 REPL (Interactive Shell)?",
    "options": {
      "A": "scalac",
      "B": "scala",
      "C": "sbt console",
      "D": "scala-shell"
    },
    "answer": "C"
  },
  {
    "question": "What is the purpose of 'Given Instances' in Scala 3?",
    "options": {
      "A": "To define implicit values that can be automatically provided by the compiler when required.",
      "B": "To create new threads for concurrent execution.",
      "C": "To mark a method as deprecated.",
      "D": "To specify the author of a piece of code."
    },
    "answer": "A"
  },
  {
    "question": "What are 'Literal Types' in Scala 3?",
    "options": {
      "A": "Types that can only be defined in a literal string.",
      "B": "Types that represent a single constant value at the type level (e.g., val x: 42 = 42).",
      "C": "Types used for writing novels and documentation.",
      "D": "A way to automatically convert code into a PDF."
    },
    "answer": "B"
  },
  {
    "question": "In Scala 3, what is a 'Match Type'?",
    "options": {
      "A": "A type that only works with Tinder integration.",
      "B": "A type definition that uses pattern matching to decide the resulting type at compile-time.",
      "C": "A way to compare two different classes for equality.",
      "D": "A specialized version of a case class."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Akka Persistence' allows actors to recover their state after a crash by replaying stored events from a journal.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the primary role of the 'Mirror' type class in Scala 3 generic programming?",
    "options": {
      "A": "To flip the code horizontally for easier reading.",
      "B": "To provide compile-time information about the structure of a class or enum (e.g., its labels and types) for derivation.",
      "C": "To duplicate an object in memory.",
      "D": "To show the developer's reflection in the IDE."
    },
    "answer": "B"
  },
  {
    "question": "Which keyword is used to evaluate a 'Quote' and turn it back into executable code in a Scala 3 macro?",
    "options": {
      "A": "eval",
      "B": "splice ($)",
      "C": "run",
      "D": "compile"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO characteristics of 'Context Functions' (e.g., 'type Contextual[T] = Context ?=> T'):",
    "options": {
      "A": "They abstract away repetitive 'using' parameters in function signatures.",
      "B": "They allow for cleaner DSL (Domain Specific Language) design.",
      "C": "They only work inside the Akka framework.",
      "D": "They force a function to be executed synchronously."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is 'Inlining' in Scala 3 specifically used for in metaprogramming?",
    "options": {
      "A": "To make all code stay on a single line.",
      "B": "To guarantee that code is expanded at the call site to enable compile-time optimizations and macro expansion.",
      "C": "To prevent code from being shared between files.",
      "D": "To reduce the size of the final JAR file."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Multiversal Equality' in Scala 3 requires a 'CanEqual' instance to exist to compare two different types at compile-time.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is a 'Phantom Type' used for?",
    "options": {
      "A": "A type that disappears at runtime and is only used to enforce constraints at compile-time.",
      "B": "A variable that cannot be seen by the debugger.",
      "C": "An object that is automatically deleted by the GC.",
      "D": "A way to handle null pointers."
    },
    "answer": "A"
  },
  {
    "question": "Which Akka component ensures that only one instance of a specific actor is running across a cluster?",
    "options": {
      "A": "ActorSystem",
      "B": "Cluster Singleton",
      "C": "Distributed PubSub",
      "D": "Router"
    },
    "answer": "B"
  },
  {
    "question": "In 'Cats Effect', what does 'Fiber' represent?",
    "options": {
      "A": "A physical network cable.",
      "B": "A lightweight, 'green' thread that represents a running IO computation.",
      "C": "A type of fast-access cache.",
      "D": "A way to compress JSON data."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO common 'Supervision Strategies' in Akka:",
    "options": {
      "A": "Restart",
      "B": "Stop",
      "C": "Wait",
      "D": "Delete"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Generalized Algebraic Data Types' (GADTs) allow you to specify the type parameters of the result type in the constructor.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Polymorphic Function Types' in Scala 3?",
    "options": {
      "A": "Functions that can take multiple names.",
      "B": "Functions that take type parameters just like methods (e.g., [T] => List[T] => T).",
      "C": "A way to make functions return multiple values.",
      "D": "Functions that can be run on different operating systems."
    },
    "answer": "B"
  },
  {
    "question": "What is the primary benefit of 'Opaque Types' over 'Type Aliases'?",
    "options": {
      "A": "They are easier to type.",
      "B": "They provide strict type-safety by hiding the underlying type, preventing accidental mixing (e.g., Id and String).",
      "C": "They make the compiled code smaller.",
      "D": "They allow for faster database lookups."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Backpressure' in the context of Akka Streams?",
    "options": {
      "A": "A security protocol to prevent DDOS attacks.",
      "B": "A mechanism that allows a slow consumer to signal a fast producer to slow down, preventing memory overflow.",
      "C": "The physical air pressure inside a server rack.",
      "D": "A way to reverse the order of elements in a list."
    },
    "answer": "B"
  },
  {
    "question": "In Scala 3, what replaces the 'Aux' pattern often used in Scala 2 type-level programming?",
    "options": {
      "A": "Dependent Function Types",
      "B": "Standard Class inheritance",
      "C": "Macro annotations",
      "D": "Implicit conversions"
    },
    "answer": "A"
  },
  {
    "question": "True or False: 'Value Classes' (extending AnyVal) cannot be used as a 'trait' in Scala.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the primary role of a 'Transactor' in the Doobie library?",
    "options": {
      "A": "To translate Scala into JavaScript.",
      "B": "To bridge the gap between functional code (ConnectionIO) and a physical database connection (JDBC).",
      "C": "To act as a message broker between actors.",
      "D": "To manage the server's file system."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Eta-Expansion' in the Scala compiler?",
    "options": {
      "A": "Converting a method into a function object automatically.",
      "B": "Increasing the memory limit for recursive calls.",
      "C": "A type of string interpolation.",
      "D": "The process of deleting unused variables."
    },
    "answer": "A"
  },
  {
    "question": "Which type class in the 'Cats' library is used to represent a context that can be 'mapped' over, like List or Option?",
    "options": {
      "A": "Monoid",
      "B": "Functor",
      "C": "Semigroup",
      "D": "Order"
    },
    "answer": "B"
  },
  {
    "question": "What does the '@nowarn' annotation do in Scala code?",
    "options": {
      "A": "Increases the severity of compiler warnings.",
      "B": "Suppresses specific compiler warnings for a targeted piece of code.",
      "C": "Turns off the computer's fans to reduce noise.",
      "D": "Prevents the code from being edited."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Intersection Types' in Scala 3 (A & B) are commutative, meaning A & B is identical to B & A.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is a 'Type Lambda' in Scala 3 syntax (e.g., [X] =>> Map[String, X])?",
    "options": {
      "A": "A function that runs on types to produce a new type constructor.",
      "B": "A way to define variables inside a type.",
      "C": "A faster version of a lambda function.",
      "D": "A tool for visualizing the type hierarchy."
    },
    "answer": "A"
  },
  {
    "question": "In 'Tagless Final' design, what does the 'F[_]' parameter typically represent?",
    "options": {
      "A": "A specific value like Integer.",
      "B": "An effect type (like IO, Task, or Future) that the algebra is polymorphic over.",
      "C": "A failure message.",
      "D": "The final version of the code."
    },
    "answer": "B"
  },
  {
    "question": "Which Akka pattern is used to distribute work among a set of identical actor instances?",
    "options": {
      "A": "Router",
      "B": "Supervisor",
      "C": "Singleton",
      "D": "Mailbox"
    },
    "answer": "A"
  },
  {
    "question": "True or False: 'Opaque Types' in Scala 3 are lost at runtime and treated as their underlying type for performance.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Polymorphic Function Types' in Scala 3?",
    "options": {
      "A": "Functions that can take type parameters at the call site (e.g., [T] => List[T] => T).",
      "B": "Functions that can return multiple values.",
      "C": "Functions that work on multiple operating systems.",
      "D": "A way to rename functions."
    },
    "answer": "A"
  },
  {
    "question": "What is 'Materialization' in Akka Streams?",
    "options": {
      "A": "Converting code into a physical circuit.",
      "B": "The process of starting the stream and allocating the necessary resources (actors, buffers).",
      "C": "Saving the stream output to a database.",
      "D": "Deleting the stream configuration."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO features of 'ZIO' ZLayer:",
    "options": {
      "A": "It provides a way to manage dependency injection in a type-safe, functional manner.",
      "B": "It allows for the composition of services and their requirements.",
      "C": "It is a graphical layer for drawing UI elements.",
      "D": "It replaces the Java Garbage Collector."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "In Scala 3, which feature allows you to define a function that depends on a context but doesn't require explicit 'using' parameters at the call site?",
    "options": {
      "A": "Context Functions",
      "B": "Implicit Classes",
      "C": "Extension Methods",
      "D": "Macro Annotations"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Partial Application' of a function in Scala?",
    "options": {
      "A": "A function that is only half compiled.",
      "B": "Passing fewer arguments to a function than it requires, resulting in a new function that accepts the remaining arguments.",
      "C": "A function that returns a 'Partial' type.",
      "D": "A way to run code on only half of the CPU cores."
    },
    "answer": "B"
  },
  {
    "question": "True or False: The 'Nothing' type in Scala is a subtype of every other type, including 'Null'.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which Akka component ensures 'at-most-once' delivery semantics by default?",
    "options": {
      "A": "ActorRef",
      "B": "PersistentActor",
      "C": "ReliableProxy",
      "D": "AtLeastOnceDelivery trait"
    },
    "answer": "A"
  },
  {
    "question": "What is the primary role of 'Kleisli' in functional libraries like Cats?",
    "options": {
      "A": "To act as a database driver.",
      "B": "To represent a function that returns an effectful value (A => F[B]) and allow for their composition.",
      "C": "To handle user authentication.",
      "D": "To sort large lists in parallel."
    },
    "answer": "B"
  },
  {
    "question": "What does the 'unapplySeq' method enable in Scala?",
    "options": {
      "A": "Deleting a sequence from memory.",
      "B": "Pattern matching on sequences of indeterminate length (e.g., matching a List against h :: t).",
      "C": "A way to sort a sequence in reverse.",
      "D": "Encrypting a list of strings."
    },
    "answer": "B"
  },
  {
    "question": "True or False: In Scala 3, 'Structural Types' can be used with a programmatic selection mechanism (Selectable) to avoid using Java Reflection.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Currying' specifically?",
    "options": {
      "A": "A technique of transforming a function that takes multiple arguments into a sequence of functions that each take a single argument.",
      "B": "A method for cleaning up the garbage collector.",
      "C": "A type of syntax highlighting.",
      "D": "A process of converting Scala to C++."
    },
    "answer": "A"
  },
  {
    "question": "In ZIO, what is a 'Fiber'?",
    "options": {
      "A": "A physical network connection.",
      "B": "A lightweight 'green' thread that represents a running computation and can be interrupted or joined.",
      "C": "A way to store data on a hard drive.",
      "D": "A type of fast-access cache."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO common traits of 'Case Classes' in Scala:",
    "options": {
      "A": "They are immutable by default.",
      "B": "They provide built-in implementations of 'equals', 'hashCode', and 'toString'.",
      "C": "They cannot be used in pattern matching.",
      "D": "They must always be defined inside a Singleton Object."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is 'Eta Expansion' used for?",
    "options": {
      "A": "To convert a method into a function object automatically when a function is expected.",
      "B": "To increase the memory limit of the JVM stack.",
      "C": "To expand a string into an array of characters.",
      "D": "To hide private variables from other classes."
    },
    "answer": "A"
  },
  {
    "question": "True or False: 'Self-type' annotations are used to ensure that a trait can only be mixed into a class that also extends a specific other type.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'Magnet Pattern' used to solve in Scala libraries like Akka-HTTP?",
    "options": {
      "A": "Issues with method overloading and type erasure by using a single method that accepts a 'magnet' object to determine the logic.",
      "B": "Attracting more users to a website.",
      "C": "Memory leaks in distributed clusters.",
      "D": "Slow database connection times."
    },
    "answer": "A"
  },
  {
    "question": "Which keyword is used in Scala 3 to import a 'given' instance without importing other members of a package?",
    "options": {
      "A": "import package.given",
      "B": "import package._",
      "C": "import package.implicit",
      "D": "import package.context"
    },
    "answer": "A"
  },
  {
    "question": "In 'Cats Effect', what is the purpose of the 'Resource' type?",
    "options": {
      "A": "To define the URL of a website.",
      "B": "To manage the lifecycle of a resource (like a database connection) ensuring it is closed properly regardless of success or failure.",
      "C": "To store images and CSS files.",
      "D": "To monitor the CPU usage of a process."
    },
    "answer": "B"
  },
  {
    "question": "What does 'TASTy' stand for in the context of the Scala 3 compiler?",
    "options": {
      "A": "Total Abstract Syntax Tree",
      "B": "Typed Abstract Syntax Tree",
      "C": "Technical Analysis of Syntax Trees",
      "D": "Template-based Abstract Syntax Types"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary benefit of the 'TASTy' format for Scala 3 libraries?",
    "options": {
      "A": "It makes the source code unreadable to hackers.",
      "B": "It enables backward and forward compatibility (separate compilation) and powers the Scala 3 reflection API.",
      "C": "It reduces the size of the JVM bytecode by 50%.",
      "D": "It allows Scala code to run directly on the browser without JavaScript."
    },
    "answer": "B"
  },
  {
    "question": "True or False: In Scala 3, 'Match Types' allow for type-level computation by matching on types rather than values.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the role of a 'Shard Region' in Akka Cluster Sharding?",
    "options": {
      "A": "To act as a physical hard drive partition.",
      "B": "To manage the location of entities (actors) and route messages to the correct shard across the cluster.",
      "C": "To encrypt messages between data centers.",
      "D": "To provide a UI for monitoring the cluster."
    },
    "answer": "B"
  },
  {
    "question": "Which type class in 'Cats' provides a 'pure' method to lift a value into a context and a 'flatMap' method to chain computations?",
    "options": {
      "A": "Functor",
      "B": "Monad",
      "C": "Semigroup",
      "D": "Applicative"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Tagless Final' primarily used for in Scala functional architecture?",
    "options": {
      "A": "To remove HTML tags from a string.",
      "B": "To decouple the definition of a DSL from its interpreter, allowing for different implementations (e.g., Production vs Test).",
      "C": "To mark a variable as the final version.",
      "D": "To speed up the compilation of case classes."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Opaque Type Aliases' in Scala 3 are treated as a distinct type outside the defining scope but are identical to the underlying type at runtime.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the purpose of the 'summon' method in Scala 3?",
    "options": {
      "A": "To create a new instance of a class.",
      "B": "To look up an implicit/given value of a specific type in the current scope (replacing 'implicitly').",
      "C": "To call a method from a remote server.",
      "D": "To force a garbage collection cycle."
    },
    "answer": "B"
  },
  {
    "question": "In 'Monad Transformer' patterns, what does 'OptionT[F, A]' allow you to do?",
    "options": {
      "A": "Convert an Option into a Future.",
      "B": "Work with a nested structure like F[Option[A]] as if it were a single Monad.",
      "C": "Delete all None values from a database.",
      "D": "Encrypt an optional string."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Polymorphic Function Types' in Scala 3?",
    "options": {
      "A": "Functions that can change their name at runtime.",
      "B": "Functions that take type parameters, similar to generic methods (e.g., [T] => List[T] => T).",
      "C": "Functions that work on multiple different operating systems.",
      "D": "A way to define multiple return types for a function."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Multiversal Equality' (CanEqual) prevents the comparison of unrelated types (e.g., String == Int) at compile time in Scala 3.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which Akka pattern is used to prevent a fast producer from overwhelming a slow consumer by managing the flow of data?",
    "options": {
      "A": "Backpressure",
      "B": "Circuit Breaker",
      "C": "Dead Letter Queue",
      "D": "Leader Election"
    },
    "answer": "A"
  },
  {
    "question": "What does the 'inline' keyword signify in a Scala 3 macro definition?",
    "options": {
      "A": "The method should be written on a single line.",
      "B": "The method should be expanded at the call site at compile time, providing access to the AST.",
      "C": "The method is a private helper.",
      "D": "The method should be ignored by the compiler."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO common components of an 'MTL' (Monad Transformer Library) style architecture:",
    "options": {
      "A": "MonadReader",
      "B": "MonadState",
      "C": "MonadDelete",
      "D": "MonadPrint"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is 'Invariance' in a generic type like Box[T]?",
    "options": {
      "A": "Box[String] is a subtype of Box[Any].",
      "B": "There is no subtyping relationship between Box[String] and Box[Any], regardless of the relationship between String and Any.",
      "C": "Box[Any] is a subtype of Box[String].",
      "D": "The type T can never be changed once the Box is created."
    },
    "answer": "B"
  },
  {
    "question": "In Scala 3, what is the primary difference between 'given' and 'implicit'?",
    "options": {
      "A": "There is no difference; they are just different words.",
      "B": "'given' provides a more structured way to define contextual values and reduces the ambiguity often associated with Scala 2 'implicit'.",
      "C": "'given' can only be used for integers.",
      "D": "'given' values are not visible to the compiler."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Whitebox' vs 'Blackbox' macros in Scala 2 (historically important for migration)?",
    "options": {
      "A": "Whitebox macros can change the return type based on inputs; Blackbox macros must follow the signature exactly.",
      "B": "Whitebox refers to UI code; Blackbox refers to backend code.",
      "C": "Whitebox macros are faster than Blackbox macros.",
      "D": "Blackbox macros are deprecated in all versions of Scala."
    },
    "answer": "A"
  },
  {
    "question": "What is the 'Aux' pattern used for in type-level programming?",
    "options": {
      "A": "To provide an auxiliary battery for the server.",
      "B": "To capture and 'leak' a dependent type from a type class into a scope where it can be used for further computation.",
      "C": "A way to define private variables in a trait.",
      "D": "A specialized library for audio processing in Scala."
    },
    "answer": "B"
  },
  {
    "question": "True or False: In Scala 3, 'Match Types' allow for the creation of type-level functions that can return different types based on the input type.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which JVM Garbage Collector is generally recommended for low-latency Scala applications like Akka systems?",
    "options": {
      "A": "Serial GC",
      "B": "Parallel GC",
      "C": "G1 GC or ZGC",
      "D": "None (Manual memory management)"
    },
    "answer": "C"
  },
  {
    "question": "What is 'Partial Unification' in the Scala compiler?",
    "options": {
      "A": "A feature that allows the compiler to better infer types for higher-kinded types (like F[A, B]).",
      "B": "A way to merge two different Git branches.",
      "C": "A method for simplifying math equations.",
      "D": "A technique to reduce the size of JAR files."
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO features of 'Opaque Types' compared to 'AnyVal' value classes:",
    "options": {
      "A": "They have absolutely zero runtime overhead.",
      "B": "They allow for a cleaner separation of implementation and interface through 'export'.",
      "C": "They are automatically encrypted.",
      "D": "They only work with the Play Framework."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A 'Context Bound' (e.g., [T : Ordering]) is a shorthand for an implicit parameter of type Ordering[T].",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Inlining' (inline) in Scala 3 specifically designed to facilitate?",
    "options": {
      "A": "Faster string concatenation.",
      "B": "Compile-time code expansion and optimization, acting as a foundation for the new macro system.",
      "C": "Moving all code onto a single line to save space.",
      "D": "Defining CSS styles inside Scala code."
    },
    "answer": "B"
  },
  {
    "question": "What does the '@static' annotation (with the scala-static plugin) achieve?",
    "options": {
      "A": "It marks a variable as never changing.",
      "B": "It allows a member of a Scala object to be compiled as a static field/method in the Java sense.",
      "C": "It stops the program from running.",
      "D": "It renders a static HTML page."
    },
    "answer": "B"
  },
  {
    "question": "Which of the following is NOT a valid way to define a 'given' instance in Scala 3?",
    "options": {
      "A": "given Ordering[Int] with { def compare(x: Int, y: Int) = x - y }",
      "B": "given [T]: Show[T] with { def show(t: T) = t.toString }",
      "C": "given (using Context): Logger with { def log(msg: String) = println(msg) }",
      "D": "given val defaultConfig: Config = Config.load()"
    },
    "answer": "C"
  },
  {
    "question": "In Scala 3, what is the 'Union Type' (A | B)?",
    "options": {
      "A": "A type that represents a value that is both A and B.",
      "B": "A type that represents a value that is either of type A or type B.",
      "C": "A type used only for database join operations.",
      "D": "A way to merge two separate classes into one file."
    },
    "answer": "B"
  },
  {
    "question": "What is the result of the intersection type 'TraitA & TraitB' in Scala 3?",
    "options": {
      "A": "A value that must implement both TraitA and TraitB.",
      "B": "A value that can choose to implement either TraitA or TraitB.",
      "C": "An error, as types cannot be intersected.",
      "D": "A new trait that contains only the overlapping methods."
    },
    "answer": "A"
  },
  {
    "question": "True or False: In Scala 3, Union Types are commutative, meaning 'Int | String' is the same as 'String | Int'.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What does 'Contravariance' (-T) imply in a generic type like 'Output[-T]'?",
    "options": {
      "A": "If String is a subtype of Any, then Output[Any] is a subtype of Output[String].",
      "B": "If String is a subtype of Any, then Output[String] is a subtype of Output[Any].",
      "C": "The type T can never be used as a function parameter.",
      "D": "The type T must be an immutable class."
    },
    "answer": "A"
  },
  {
    "question": "In the ZIO ecosystem, what is a 'Fiber'?",
    "options": {
      "A": "A physical hardware thread.",
      "B": "A lightweight, virtual thread managed by the ZIO runtime for high-concurrency tasks.",
      "C": "A type of data compression algorithm.",
      "D": "A wrapper for legacy Java Future objects."
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Split-Brain Resolver' used for in Akka Clusters?",
    "options": {
      "A": "To optimize the CPU usage of an actor.",
      "B": "To decide which side of a network partition should survive to maintain cluster consistency.",
      "C": "To handle cases where a developer writes conflicting code.",
      "D": "To automatically restart the primary database."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO characteristics of 'Match Types' in Scala 3:",
    "options": {
      "A": "They allow for type-level computation based on pattern matching.",
      "B": "They are resolved at compile-time.",
      "C": "They can only be used with String literals.",
      "D": "They are a runtime feature used for reflection."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: The 'export' keyword in Scala 3 allows an object to define aliases for members of other objects, promoting composition over inheritance.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the primary purpose of 'Polymorphic Function Types' (e.g., [T] => List[T] => T)?",
    "options": {
      "A": "To allow functions to accept type parameters just like methods.",
      "B": "To make functions run faster on multicore systems.",
      "C": "To allow a function to return multiple different types at once.",
      "D": "To convert Scala functions into Java lambdas."
    },
    "answer": "A"
  },
  {
    "question": "In 'Cats Effect', what does the 'IO' monad represent?",
    "options": {
      "A": "A synchronous calculation that cannot fail.",
      "B": "A description of a side-effecting computation that is lazy and can be composed.",
      "C": "A direct connection to a file on disk.",
      "D": "A way to perform input and output operations in the console only."
    },
    "answer": "B"
  },
  {
    "question": "In Scala 3, what is the 'Implicit Selection' rule for 'using' parameters?",
    "options": {
      "A": "The compiler picks the first variable it finds in the file.",
      "B": "The compiler searches for a 'given' instance that matches the required type in the current scope or imported scopes.",
      "C": "The user must manually point to the variable using the @use annotation.",
      "D": "Only variables marked with 'val' can be used."
    },
    "answer": "B"
  },
  {
    "question": "What is the primary role of 'HList' (Heterogeneous List) in type-level programming?",
    "options": {
      "A": "To store different types of data in a way that preserves each element's specific type at compile-time.",
      "B": "To speed up the sorting of standard Lists.",
      "C": "To allow for the deletion of null values from a database.",
      "D": "To create a list that can only hold strings and integers."
    },
    "answer": "A"
  },
  {
    "question": "True or False: In Scala 3, 'Context Bounds' (e.g., [T : Numeric]) are still expanded into implicit parameters, but are now compatible with 'given' and 'using' syntax.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is a 'Phantom Type' and why is it used in Scala API design?",
    "options": {
      "A": "A type that is invisible to the developer.",
      "B": "A type that has no runtime representation and is used purely to enforce state-related constraints at compile-time (e.g., a 'Door' that is 'Closed').",
      "C": "A type used to represent null values in a safe way.",
      "D": "A way to make the compiler ignore certain sections of code."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO features of 'Akka HTTP' Directives:",
    "options": {
      "A": "They are small, building-block components used to construct a routing tree.",
      "B": "They can extract data from a request (like headers or query parameters) and pass it to inner routes.",
      "C": "They are used to physically route cables in a data center.",
      "D": "They replace the need for an SSL certificate."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "Which tool is commonly used to profile the JVM and identify 'hot spots' or memory leaks in a running Scala application?",
    "options": {
      "A": "JVisualVM or JProfiler",
      "B": "Sublime Text",
      "C": "Google Analytics",
      "D": "npm audit"
    },
    "answer": "A"
  },
  {
    "question": "True or False: 'Eta Expansion' occurs when the Scala compiler automatically wraps a method in a function object when a function type is expected.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What does the 'inline' keyword enable in Scala 3 metaprogramming?",
    "options": {
      "A": "It allows the code to be executed directly in a web browser console.",
      "B": "It instructs the compiler to expand the code at the call site, allowing access to compile-time information and reducing runtime overhead.",
      "C": "It forces the entire application to be a single .scala file.",
      "D": "It prevents the use of external libraries."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Partial Unification' in the Scala compiler and why was it traditionally enabled?",
    "options": {
      "A": "To allow the compiler to better infer types for higher-kinded types like F[A, B] when a single-hole type F[_] is expected.",
      "B": "To speed up the connection to the database.",
      "C": "To allow two developers to work on the same file without conflicts.",
      "D": "To partially compile the code to save energy."
    },
    "answer": "A"
  },
  {
    "question": "In 'Cats', what is the difference between a 'Semigroup' and a 'Monoid'?",
    "options": {
      "A": "A Monoid is a Semigroup that also has an 'empty' (identity) element.",
      "B": "A Semigroup is faster than a Monoid.",
      "C": "A Monoid only works with integers, while a Semigroup works with any type.",
      "D": "There is no difference; they are synonyms."
    },
    "answer": "A"
  },
  {
    "question": "In Scala 3, which package contains the fundamental tools for Quote/Splice metaprogramming?",
    "options": {
      "A": "scala.meta",
      "B": "scala.quoted",
      "C": "scala.macros",
      "D": "scala.reflection"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Mirror.SumOf' used for in Scala 3 type class derivation?",
    "options": {
      "A": "To perform mathematical addition on types.",
      "B": "To provide compile-time reflection for Coproducts (Enums or Sealed Traits).",
      "C": "To duplicate an object across a cluster.",
      "D": "To verify that a class has no private methods."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'GraphStage' in Akka Streams allows developers to create custom processing stages with arbitrary numbers of input and output ports.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the primary function of 'Export' clauses in Scala 3?",
    "options": {
      "A": "To save the source code to an external drive.",
      "B": "To project selected members of an object into the current class/object, serving as a formal alternative to 'package object' or inheritance.",
      "C": "To make a private variable public in all child classes.",
      "D": "To convert Scala classes into JSON schema automatically."
    },
    "answer": "B"
  },
  {
    "question": "Which method is used in the 'Cats Effect' IO monad to run two computations in parallel and return their results as a tuple?",
    "options": {
      "A": "flatMap",
      "B": "parMapN (or parZip)",
      "C": "sequence",
      "D": "traverse"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO features of 'Opaque Types' in Scala 3 compared to standard Type Aliases:",
    "options": {
      "A": "They are treated as completely unrelated to the underlying type outside their definition scope.",
      "B": "They incur zero runtime boxing overhead.",
      "C": "They automatically implement 'toString' as the underlying type's name.",
      "D": "They can only be used with numeric types."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is a 'Match Type' in Scala 3 used for?",
    "options": {
      "A": "Checking if a string matches a regex at runtime.",
      "B": "Defining a type-level function that reduces to a specific type based on a pattern match on an input type.",
      "C": "Matching two database rows for equality.",
      "D": "Ensuring a variable name matches its type name."
    },
    "answer": "B"
  },
  {
    "question": "True or False: In Akka, 'At-Least-Once Delivery' requires the receiver to be idempotent to handle potential duplicate messages.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What does the 'inline' modifier guarantee when applied to a parameter in a Scala 3 function?",
    "options": {
      "A": "The parameter will be ignored if it is null.",
      "B": "The argument passed to the function will be expanded as code at the call site, allowing it to be used in macros.",
      "C": "The parameter will be stored in the CPU cache.",
      "D": "The function will execute on a single line of the stack trace."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Kind-Projector' syntax (e.g., Lambda[A => Map[String, A]]) primarily used to solve?",
    "options": {
      "A": "Slow database projection queries.",
      "B": "Complex syntax for defining anonymous Higher-Kinded Type constructors.",
      "C": "Memory leaks in Akka actors.",
      "D": "Type erasure issues in Java reflection."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Type Erasure' and how does it affect Scala troubleshooting on the JVM?",
    "options": {
      "A": "It deletes the source code after compilation.",
      "B": "It is the removal of generic type information at runtime, making it difficult to differentiate between List[Int] and List[String] via reflection.",
      "C": "It is a security feature that hides variable names.",
      "D": "It is a process that speeds up string concatenation."
    },
    "answer": "B"
  },
  {
    "question": "Which compiler option in Scala 3 enables the 'Strict Equality' feature to prevent comparison of unrelated types?",
    "options": {
      "A": "-language:strictEquality",
      "B": "-feature:equality",
      "C": "-Xverify-equality",
      "D": "-strict-types"
    },
    "answer": "A"
  },
  {
    "question": "True or False: In Scala 3, a 'Main' method can be defined using the @main annotation on a top-level function instead of an object.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What does the 'ClassTag' context bound help solve in Scala?",
    "options": {
      "A": "It allows the program to run on older versions of Java.",
      "B": "It preserves runtime information about a generic type, allowing for the creation of generic arrays or type-safe casting.",
      "C": "It acts as a tag for the garbage collector.",
      "D": "It automatically formats JSON strings."
    },
    "answer": "B"
  },
  {
    "question": "Identify the primary purpose of the 'scala-js' compiler:",
    "options": {
      "A": "To run JavaScript code inside a Scala actor.",
      "B": "To compile Scala code into optimized JavaScript for execution in browsers or Node.js.",
      "C": "To convert Scala classes into CSS styles.",
      "D": "To allow Scala to access the browser's cookies directly."
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Contextual Abstraction' in the context of Scala 3?",
    "options": {
      "A": "A way to hide code inside comments.",
      "B": "The unified term for features like 'given', 'using', and 'extension' that handle implicit context.",
      "C": "A type of database abstraction layer.",
      "D": "A method for managing the server's CPU context."
    },
    "answer": "B"
  },
  {
    "question": "True or False: In Scala 3, 'Open' classes must be explicitly marked with the 'open' modifier to allow extension from other files.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the function of 'TypeTest' in Scala 3?",
    "options": {
      "A": "To check the internet speed.",
      "B": "To provide a way to perform type-safe pattern matching on types that are otherwise erased at runtime.",
      "C": "To test if a variable is null.",
      "D": "To verify that the code follows the style guide."
    },
    "answer": "B"
  },
  {
    "question": "Which keyword is used to explicitly call a 'given' instance by its type without using 'summon'?",
    "options": {
      "A": "using",
      "B": "with",
      "C": "valueOf",
      "D": "apply"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Inferred Contextual Argument'?",
    "options": {
      "A": "When the developer guesses what the variable should be.",
      "B": "When the compiler automatically fills in a 'using' parameter based on the available 'given' instances in scope.",
      "C": "A type of error where the context is lost.",
      "D": "A way to speed up the database."
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
    skill = "Scala"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
