from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
  {
    "question": "What is the primary relationship between TypeScript and JavaScript?",
    "options": {
      "A": "TypeScript is a separate language that competes with JavaScript",
      "B": "TypeScript is a strict syntactical superset of JavaScript that adds static typing",
      "C": "TypeScript is a specialized version of JavaScript for mobile apps only",
      "D": "TypeScript is older than JavaScript"
    },
    "answer": "B"
  },
  {
    "question": "Which command-line tool is used to compile TypeScript files into JavaScript?",
    "options": {
      "A": "ts-run",
      "B": "tsc",
      "C": "node-ts",
      "D": "typescript-build"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'any' type represent in TypeScript?",
    "options": {
      "A": "A type that can only be a string",
      "B": "A type that bypasses type-checking, allowing any value to be assigned",
      "C": "A type that is automatically detected as a number",
      "D": "A type used only for arrays"
    },
    "answer": "B"
  },
  {
    "question": "What is the benefit of the 'unknown' type over the 'any' type?",
    "options": {
      "A": "It is faster",
      "B": "It is type-safe; you must perform some type checking before performing operations on an unknown value",
      "C": "It can only store numbers",
      "D": "It is deprecated"
    },
    "answer": "B"
  },
  {
    "question": "Which keyword is used to define a blueprint for an object's structure in TypeScript?",
    "options": {
      "A": "blueprint",
      "B": "interface",
      "C": "struct",
      "D": "contract"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Type Inference' in TypeScript?",
    "options": {
      "A": "When the developer manually defines every type",
      "B": "The compiler's ability to automatically deduce the type of a variable based on its value",
      "C": "A type of network error",
      "D": "A way to convert strings to numbers"
    },
    "answer": "B"
  },
  {
    "question": "How do you define an optional property in an interface?",
    "options": {
      "A": "Using the 'optional' keyword",
      "B": "Adding a question mark (?) after the property name",
      "C": "Using a null value",
      "D": "Adding a 'maybe' prefix"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Tuple' in TypeScript?",
    "options": {
      "A": "A type of loop",
      "B": "An array with a fixed number of elements where each element has a known type",
      "C": "A database record",
      "D": "A mathematical formula"
    },
    "answer": "B"
  },
  {
    "question": "Which keyword is used to create a new name for a type?",
    "options": {
      "A": "rename",
      "B": "type",
      "C": "alias",
      "D": "define"
    },
    "answer": "B"
  },
  {
    "question": "What is the difference between an 'interface' and a 'type' alias regarding extension?",
    "options": {
      "A": "Types cannot be extended",
      "B": "Interfaces can be re-opened to add new properties (declaration merging); types cannot",
      "C": "Interfaces are only for classes",
      "D": "Types are faster to compile"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'void' type indicate for a function?",
    "options": {
      "A": "The function returns a null value",
      "B": "The function does not return a value",
      "C": "The function is empty",
      "D": "The function is asynchronous"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'never' type used for?",
    "options": {
      "A": "To indicate a variable that is never used",
      "B": "To represent values that will never occur (e.g., a function that always throws an error)",
      "C": "To replace the 'any' type",
      "D": "To mark a property as deleted"
    },
    "answer": "B"
  },
  {
    "question": "How do you define an array of strings in TypeScript?",
    "options": {
      "A": "string[]",
      "B": "Array<string>",
      "C": "Both A and B",
      "D": "List<string>"
    },
    "answer": "C"
  },
  {
    "question": "What is a 'Union Type'?",
    "options": {
      "A": "A type that combines two objects into one",
      "B": "A type that allows a value to be one of several types (e.g., string | number)",
      "C": "A type used for database joins",
      "D": "A global variable"
    },
    "answer": "B"
  },
  {
    "question": "What is an 'Intersection Type'?",
    "options": {
      "A": "A type that allows a value to be one of two types",
      "B": "A type that combines multiple types into one (e.g., TypeA & TypeB)",
      "C": "A type used for routing",
      "D": "A type that excludes properties"
    },
    "answer": "B"
  },
  {
    "question": "Which keyword is used to check the type of a variable at runtime in a 'Type Guard'?",
    "options": {
      "A": "isType",
      "B": "typeof",
      "C": "check",
      "D": "kindof"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'readonly' modifier used for?",
    "options": {
      "A": "To make a function private",
      "B": "To prevent a property from being modified after it is initialized",
      "C": "To hide a variable from the debugger",
      "D": "To mark a file as read-only"
    },
    "answer": "B"
  },
  {
    "question": "What is an 'Enum' in TypeScript?",
    "options": {
      "A": "A type of mathematical calculation",
      "B": "A way to define a set of named constants (numeric or string)",
      "C": "A type of loop",
      "D": "A database connection string"
    },
    "answer": "B"
  },
  {
    "question": "What is the default value of the first member in a numeric Enum if not specified?",
    "options": {
      "A": "1",
      "B": "0",
      "C": "-1",
      "D": "null"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Strict Null Checking' in TypeScript?",
    "options": {
      "A": "A mode where null and undefined are not allowed in the project",
      "B": "A mode where null and undefined are not assignable to other types unless explicitly allowed",
      "C": "A tool to delete null values",
      "D": "A way to speed up the app"
    },
    "answer": "B"
  },
  {
    "question": "Which configuration file is used to manage TypeScript project settings?",
    "options": {
      "A": "package.json",
      "B": "tsconfig.json",
      "C": "ts-config.xml",
      "D": "settings.ts"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'as' keyword do in TypeScript?",
    "options": {
      "A": "It renames a variable",
      "B": "It performs a type assertion, telling the compiler to treat a value as a specific type",
      "C": "It imports a module",
      "D": "It creates a loop"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Literal Type' in TypeScript?",
    "options": {
      "A": "A type that can be any string",
      "B": "A type that represents a specific exact value (e.g., 'Success' | 'Error')",
      "C": "A type for reading books",
      "D": "A type for numbers only"
    },
    "answer": "B"
  },
  {
    "question": "Which keyword is used to inherit from an interface?",
    "options": {
      "A": "implements",
      "B": "extends",
      "C": "inherits",
      "D": "with"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Class' in TypeScript compared to JavaScript?",
    "options": {
      "A": "It is completely different",
      "B": "It follows ES6 class syntax but adds access modifiers (public, private, protected)",
      "C": "It is used only for data storage",
      "D": "It doesn't support constructors"
    },
    "answer": "B"
  },
  {
    "question": "What is the default access modifier for class members in TypeScript?",
    "options": {
      "A": "private",
      "B": "public",
      "C": "protected",
      "D": "internal"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'protected' modifier used for in a class?",
    "options": {
      "A": "To make a member visible only within the class",
      "B": "To make a member visible within the class and its subclasses",
      "C": "To make a member visible to everyone",
      "D": "To encrypt the member"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Constructor' in a TypeScript class?",
    "options": {
      "A": "A tool to build the app",
      "B": "A special method for creating and initializing an object instance of that class",
      "C": "A type of static method",
      "D": "A way to delete an object"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Abstract Class'?",
    "options": {
      "A": "A class that cannot be instantiated and is used as a base for other classes",
      "B": "A class with no methods",
      "C": "A class that is hidden from the user",
      "D": "A class used only for math"
    },
    "answer": "A"
  },
  {
    "question": "How do you define a function type in an interface?",
    "options": {
      "A": "function: name();",
      "B": "(arg: type) => returnType;",
      "C": "name: Function;",
      "D": "meth: void;"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Non-Null Assertion Operator' (!)?",
    "options": {
      "A": "A way to check for nulls",
      "B": "Telling the compiler that a value is definitely not null or undefined, even if the type suggests otherwise",
      "C": "Deleting a null value",
      "D": "A mathematical operator"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Structural Typing' (Duck Typing) in TypeScript?",
    "options": {
      "A": "Typing like a duck",
      "B": "A system where type compatibility is determined by the shape/structure of the data rather than explicit names",
      "C": "A rigid type system",
      "D": "A type of network call"
    },
    "answer": "B"
  },
  {
    "question": "Which keyword is used to declare a variable that is only available within a specific block?",
    "options": {
      "A": "var",
      "B": "let",
      "C": "const",
      "D": "Both B and C"
    },
    "answer": "D"
  },
  {
    "question": "What is 'Generics' in TypeScript?",
    "options": {
      "A": "Types that are generic and non-specific",
      "B": "A tool for creating reusable components that work with a variety of types while maintaining type safety",
      "C": "A way to delete types",
      "D": "A type of network protocol"
    },
    "answer": "B"
  },
  {
    "question": "What is the common naming convention for a generic type parameter?",
    "options": {
      "A": "G",
      "B": "T",
      "C": "Type",
      "D": "X"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Type Guard' function return type?",
    "options": {
      "A": "boolean",
      "B": "arg is Type",
      "C": "Type",
      "D": "void"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Target' in tsconfig.json?",
    "options": {
      "A": "To choose which developer is working on the project",
      "B": "To specify which version of JavaScript the TypeScript code should be compiled into (e.g., ES5, ES6)",
      "C": "To set the app's goals",
      "D": "To choose the device type"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Lib' in tsconfig.json used for?",
    "options": {
      "A": "To import libraries",
      "B": "To specify the environment's built-in type definitions (e.g., DOM, ESNext) the compiler should include",
      "C": "To store the app's history",
      "D": "To manage project IDs"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Declaration Files' (.d.ts)?",
    "options": {
      "A": "Files that describe the project's goals",
      "B": "Files that provide type information for JavaScript libraries that don't have built-in types",
      "C": "Files that store the user's data",
      "D": "Files for CSS only"
    },
    "answer": "B"
  },
  {
    "question": "How do you define a type that is a string OR a number in a single variable?",
    "options": {
      "A": "string | number",
      "B": "string & number",
      "C": "string, number",
      "D": "Mixed<string, number>"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Ambient Declaration' (declare keyword)?",
    "options": {
      "A": "A way to make the code sound better",
      "B": "Telling TypeScript that a variable or module exists globally but is defined outside of the TypeScript files",
      "C": "A type of network call",
      "D": "A way to hide code"
    },
    "answer": "B"
  },
  {
    "question": "Which flag in tsconfig.json prevents the compiler from outputting files if any errors are found?",
    "options": {
      "A": "noEmitOnError",
      "B": "stopOnError",
      "C": "strict",
      "D": "failFast"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Module' in TypeScript?",
    "options": {
      "A": "A small app",
      "B": "A self-contained piece of code that exports variables, functions, or classes for use in other files",
      "C": "A type of UI theme",
      "D": "A database table"
    },
    "answer": "B"
  },
  {
    "question": "Which keyword is used to make a member of a module available in other files?",
    "options": {
      "A": "public",
      "B": "export",
      "C": "provide",
      "D": "share"
    },
    "answer": "B"
  },
  {
    "question": "Which keyword is used to bring an exported member from another module into the current file?",
    "options": {
      "A": "import",
      "B": "fetch",
      "C": "include",
      "D": "get"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Optional Chaining' (?.) in TypeScript?",
    "options": {
      "A": "A way to chain multiple apps",
      "B": "An operator that allows reading the value of a property deep within a chain of objects without checking each level for null",
      "C": "A network tool",
      "D": "A database feature"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Nullish Coalescing' (??) operator?",
    "options": {
      "A": "A way to combine two null values",
      "B": "An operator that returns the right-hand side value if the left-hand side is null or undefined (but not 0 or false)",
      "C": "A mathematical operator",
      "D": "A type of loop"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Parameter Properties' in a constructor?",
    "options": {
      "A": "Properties that change with parameters",
      "B": "A shorthand to declare and initialize a class member directly in the constructor arguments (using public/private/protected)",
      "C": "A way to name variables",
      "D": "A network protocol"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Decorators' in TypeScript?",
    "options": {
      "A": "Tools to design the UI",
      "B": "A special kind of declaration that can be attached to a class, method, or property to modify its behavior (experimental)",
      "C": "A type of loop",
      "D": "A database tool"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Function Overloading'?",
    "options": {
      "A": "Calling a function too many times",
      "B": "Providing multiple function signatures for a single implementation to support different types of arguments",
      "C": "A bug in the code",
      "D": "A network timeout"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary advantage of using Generics in a function?",
    "options": {
      "A": "It makes the function run faster in the browser",
      "B": "It allows the function to work with any type while still capturing the specific type for safety",
      "C": "It removes the need for the 'return' keyword",
      "D": "It automatically converts strings to numbers"
    },
    "answer": "B"
  },
  {
    "question": "Which Utility Type makes all properties of an interface optional?",
    "options": {
      "A": "Readonly<T>",
      "B": "Partial<T>",
      "C": "Pick<T, K>",
      "D": "Omit<T, K>"
    },
    "answer": "B"
  },
  {
    "question": "Which Utility Type creates a type by selecting a set of properties 'K' from type 'T'?",
    "options": {
      "A": "Exclude<T, U>",
      "B": "Pick<T, K>",
      "C": "Extract<T, U>",
      "D": "Record<K, T>"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'keyof' operator do?",
    "options": {
      "A": "It returns the value of a key in an object",
      "B": "It takes an object type and produces a string or numeric literal union of its keys",
      "C": "It checks if a key exists in a database",
      "D": "It deletes a key from an interface"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'typeof' operator do when used in a type context?",
    "options": {
      "A": "It returns the JavaScript type of a variable at runtime",
      "B": "It extracts the TypeScript type of a variable or property",
      "C": "It converts a type to a string",
      "D": "It creates a new class"
    },
    "answer": "B"
  },
  {
    "question": "Which Utility Type constructs a type with all properties of 'T' set to required?",
    "options": {
      "A": "Required<T>",
      "B": "NonNullable<T>",
      "C": "Record<T, K>",
      "D": "Partial<T>"
    },
    "answer": "A"
  },
  {
    "question": "What is a 'Mapped Type' in TypeScript?",
    "options": {
      "A": "A type used for GPS navigation",
      "B": "A way to create new types based on the properties of an existing type by iterating over keys",
      "C": "A type that only works with Google Maps API",
      "D": "A list of all types in a project"
    },
    "answer": "B"
  },
  {
    "question": "Which Utility Type constructs a type by picking all properties from 'T' and then removing 'K'?",
    "options": {
      "A": "Exclude<T, K>",
      "B": "Omit<T, K>",
      "C": "Pick<T, K>",
      "D": "Extract<T, K>"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Record<K, T>' utility type used for?",
    "options": {
      "A": "To record audio in the app",
      "B": "To create an object type where keys are of type 'K' and values are of type 'T'",
      "C": "To store database records only",
      "D": "To track the history of state changes"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Generic Constraint' (using the extends keyword) do?",
    "options": {
      "A": "It allows a generic to be any type",
      "B": "It limits the types that can be passed to a generic parameter",
      "C": "It makes a class inherit from another class",
      "D": "It speeds up compilation"
    },
    "answer": "B"
  },
  {
    "question": "Which keyword is used to describe an 'Index Signature' in an interface?",
    "options": {
      "A": "[key: string]: any;",
      "B": "index: string;",
      "C": "keys: string[];",
      "D": "signature: type;"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Type Alias' vs 'Interface' regarding Unions?",
    "options": {
      "A": "Interfaces can define unions; type aliases cannot",
      "B": "Type aliases can define unions; interfaces cannot",
      "C": "Both can define unions equally",
      "D": "Unions are not allowed in TypeScript"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Declaration Merging' in TypeScript?",
    "options": {
      "A": "Merging two different apps",
      "B": "When the compiler merges two or more separate declarations with the same name into a single definition",
      "C": "Combining two variables into one",
      "D": "Deleting duplicate code"
    },
    "answer": "B"
  },
  {
    "question": "Which access modifier allows a member to be accessed only within its own class?",
    "options": {
      "A": "public",
      "B": "private",
      "C": "protected",
      "D": "readonly"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Namespace' in TypeScript?",
    "options": {
      "A": "A way to name the user's computer",
      "B": "A TypeScript-specific way to organize code and avoid global scope pollution (internal modules)",
      "C": "A database schema",
      "D": "A type of variable"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'InstanceType<T>' utility type?",
    "options": {
      "A": "To check the type of a variable",
      "B": "To obtain the instance type of a constructor function type",
      "C": "To create a new instance of a class",
      "D": "To delete a class instance"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Conditional Type'?",
    "options": {
      "A": "A type that only works in 'if' statements",
      "B": "A type that chooses one of two possible types based on a condition expressed as a ternary",
      "C": "A type that changes at runtime",
      "D": "A way to handle errors"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'infer' keyword used for in conditional types?",
    "options": {
      "A": "To guess the type of a variable",
      "B": "To declare a type variable that is 'inferred' from a type being matched in a condition",
      "C": "To import a library",
      "D": "To rename a type"
    },
    "answer": "B"
  },
  {
    "question": "Which Utility Type excludes from 'T' all properties that are assignable to 'U'?",
    "options": {
      "A": "Omit<T, U>",
      "B": "Exclude<T, U>",
      "C": "Extract<T, U>",
      "D": "NonNullable<T>"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'ReturnType<T>' utility type?",
    "options": {
      "A": "To force a function to return a value",
      "B": "To obtain the return type of a function type",
      "C": "To change the return value of a function",
      "D": "To check if a function returns anything"
    },
    "answer": "B"
  },
  {
    "question": "How do you define a 'ReadOnly' array that cannot be modified?",
    "options": {
      "A": "const arr = []",
      "B": "ReadonlyArray<string> or readonly string[]",
      "C": "Array.freeze([])",
      "D": "FixedArray<string>"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Const Assertion' (as const)?",
    "options": {
      "A": "A way to declare a constant",
      "B": "Telling the compiler to treat an object as deeply readonly and its literal values as types",
      "C": "A type of network security",
      "D": "A way to speed up the loop"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'Parameters<T>' utility type?",
    "options": {
      "A": "To set the arguments for a function",
      "B": "To obtain the types of the parameters of a function type as a tuple",
      "C": "To count how many parameters a function has",
      "D": "To delete parameters"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Type Narrowing'?",
    "options": {
      "A": "Reducing the size of the font",
      "B": "The process of moving from a less specific type to a more specific type using logic (guards)",
      "C": "Deleting unused types",
      "D": "A way to handle small numbers"
    },
    "answer": "B"
  },
  {
    "question": "Which keyword is used to declare a member that belongs to the class itself rather than instances?",
    "options": {
      "A": "global",
      "B": "static",
      "C": "const",
      "D": "shared"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Discriminated Union' pattern?",
    "options": {
      "A": "A union that is not allowed",
      "B": "Using a common literal property (like 'kind' or 'type') in a union of objects to allow for easy narrowing",
      "C": "A type of database join",
      "D": "A security vulnerability"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Awaited<T>' utility type?",
    "options": {
      "A": "To wait for a function to finish",
      "B": "To model operations like 'await' in async functions or the '.then()' method on Promises",
      "C": "To pause the app",
      "D": "To handle network timeouts"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Module Augmentation'?",
    "options": {
      "A": "Adding more memory to a module",
      "B": "Adding new declarations to an existing module from outside of it",
      "C": "Renaming a module",
      "D": "Deleting a module"
    },
    "answer": "B"
  },
  {
    "question": "Which flag in tsconfig.json allows for interoperability between CommonJS and ES Modules?",
    "options": {
      "A": "strict",
      "B": "esModuleInterop",
      "C": "allowJs",
      "D": "moduleResolution"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Template Literal Type'?",
    "options": {
      "A": "A type for writing emails",
      "B": "A type that allows building new types by manipulating strings via template literal syntax",
      "C": "A type for UI templates",
      "D": "A type that converts code to HTML"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Definite Assignment Assertion' (!)?",
    "options": {
      "A": "A way to check for errors",
      "B": "Telling the compiler that a variable will definitely be assigned a value before use, even if TS can't prove it",
      "C": "Deleting a variable",
      "D": "A type of loop"
    },
    "answer": "B"
  },
  {
    "question": "Which keyword is used in a class to implement an interface?",
    "options": {
      "A": "extends",
      "B": "implements",
      "C": "uses",
      "D": "with"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Exhaustiveness Checking' in a switch statement?",
    "options": {
      "A": "Checking if the computer is tired",
      "B": "Ensuring that every possible case of a union type is handled, often using the 'never' type in the default case",
      "C": "Deleting unused cases",
      "D": "A performance test"
    },
    "answer": "B"
  },
  {
    "question": "What is the difference between 'null' and 'undefined' in TypeScript?",
    "options": {
      "A": "They are identical",
      "B": "Undefined means a value hasn't been initialized; Null means a value is intentionally empty",
      "C": "Null is for strings; Undefined is for numbers",
      "D": "TypeScript does not support 'null'"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Partial<T>' implementation internally?",
    "options": {
      "A": "A mapped type that adds '?' to every key",
      "B": "A loop that deletes keys",
      "C": "A hardcoded list of types",
      "D": "A network protocol"
    },
    "answer": "A"
  },
  {
    "question": "What is 'NonNullable<T>' used for?",
    "options": {
      "A": "To make all properties required",
      "B": "To create a type by excluding null and undefined from T",
      "C": "To check if a database is empty",
      "D": "To hide code"
    },
    "answer": "B"
  },
  {
    "question": "What is 'ConstructorParameters<T>'?",
    "options": {
      "A": "A tool to build classes",
      "B": "A utility type that extracts the parameter types of a class constructor",
      "C": "A way to name variables",
      "D": "A type for database queries"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Key Remapping' in Mapped Types?",
    "options": {
      "A": "Changing the keys on a keyboard",
      "B": "Using the 'as' clause in a mapped type to transform the names of the keys",
      "C": "Deleting keys from a database",
      "D": "A type of UI layout"
    },
    "answer": "B"
  },
  {
    "question": "Which flag in tsconfig.json enables the use of Decorators?",
    "options": {
      "A": "strict",
      "B": "experimentalDecorators",
      "C": "emitDecoratorMetadata",
      "D": "Both B and C"
    },
    "answer": "D"
  },
  {
    "question": "What is 'Unknown' vs 'Any' regarding operations?",
    "options": {
      "A": "You can call any method on 'unknown'; you cannot on 'any'",
      "B": "You can call any method on 'any'; you must narrow 'unknown' before calling methods",
      "C": "They are the same",
      "D": "Unknown is for strings only"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Type Assertion' vs 'Type Casting'?",
    "options": {
      "A": "TypeScript uses Assertions (as type) to inform the compiler; Casting implies a runtime conversion which TS doesn't do",
      "B": "They are the same",
      "C": "Casting is for mobile; Assertion is for web",
      "D": "Assertions are older"
    },
    "answer": "A"
  },
  {
    "question": "What is 'ThisType<T>'?",
    "options": {
      "A": "A type for the current user",
      "B": "A marker utility type used to control the type of 'this' within an object literal",
      "C": "A type for the current date",
      "D": "A database reference"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Self-Referencing' Type?",
    "options": {
      "A": "A type that talks about itself",
      "B": "A recursive type definition where a type refers to itself (common for tree structures)",
      "C": "A type that deletes itself",
      "D": "A global variable"
    },
    "answer": "B"
  },
  {
    "question": "What is 'String Enums' advantage over Numeric Enums?",
    "options": {
      "A": "They are faster",
      "B": "They provide better readability during debugging because the values are meaningful strings",
      "C": "They use less memory",
      "D": "They don't require values"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Literal Inference' problem with objects?",
    "options": {
      "A": "Objects are too large",
      "B": "TypeScript normally infers properties as 'string' rather than specific literals unless 'as const' is used",
      "C": "Objects cannot have types",
      "D": "A network error"
    },
    "answer": "B"
  },
  {
    "question": "Which keyword is used to access the parent class's constructor or methods?",
    "options": {
      "A": "this",
      "B": "super",
      "C": "parent",
      "D": "base"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Intersection Type' (&) usage?",
    "options": {
      "A": "To combine multiple interfaces into one single type requirement",
      "B": "To choose between two types",
      "C": "To delete properties",
      "D": "To handle errors"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Readonly<T>' internal implementation?",
    "options": {
      "A": "A loop that adds 'readonly' modifier to every property of T",
      "B": "A tool that deletes keys",
      "C": "A database setting",
      "D": "A network protocol"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Type Compatibility' based on in TypeScript?",
    "options": {
      "A": "Variable names",
      "B": "Structural subtyping (the shape of the data)",
      "C": "The file name",
      "D": "The compiler version"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Final Rule' of TypeScript assessment?",
    "options": {
      "A": "Always use 'any'",
      "B": "Static types are for compile-time safety and vanish once the code is compiled to JavaScript",
      "C": "TypeScript runs in the browser directly",
      "D": "Never use interfaces"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary function of a 'Decorator' in TypeScript?",
    "options": {
      "A": "To add visual styles to the UI",
      "B": "To provide a way to add both annotations and a meta-programming syntax for class declarations and members",
      "C": "To decrease the file size of the compiled JavaScript",
      "D": "To replace the need for interfaces"
    },
    "answer": "B"
  },
  {
    "question": "Which specific decorator type can be applied to a class constructor?",
    "options": {
      "A": "Method Decorator",
      "B": "Class Decorator",
      "C": "Property Decorator",
      "D": "Parameter Decorator"
    },
    "answer": "B"
  },
  {
    "question": "In TypeScript, what is a 'Mixin'?",
    "options": {
      "A": "A type of database join",
      "B": "A pattern for building classes from reusable components by combining multiple simpler partial classes",
      "C": "A tool to mix different programming languages",
      "D": "A way to encrypt source code"
    },
    "answer": "B"
  },
  {
    "question": "Which tsconfig.json option is used to enable the generation of source maps for debugging?",
    "options": {
      "A": "debug: true",
      "B": "sourceMap: true",
      "C": "generateMap: true",
      "D": "mapRoot: './maps'"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'moduleResolution' setting in tsconfig.json determine?",
    "options": {
      "A": "The screen resolution of the app",
      "B": "The strategy the compiler uses to figure out what an import refers to",
      "C": "The version of Node.js used",
      "D": "The compression level of the module"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'exclude' property in tsconfig.json?",
    "options": {
      "A": "To hide code from the user",
      "B": "To specify a list of files or folders that should not be included in the compilation",
      "C": "To remove private variables",
      "D": "To ignore specific type errors"
    },
    "answer": "B"
  },
  {
    "question": "When using TypeScript with React, which file extension is required for files containing JSX?",
    "options": {
      "A": ".ts",
      "B": ".tsx",
      "C": ".react.ts",
      "D": ".jsx.ts"
    },
    "answer": "B"
  },
  {
    "question": "How do you define the types for React component props in TypeScript?",
    "options": {
      "A": "Using an interface or type alias",
      "B": "Props are automatically typed as 'any'",
      "C": "Using a special @props decorator",
      "D": "In the CSS file"
    },
    "answer": "A"
  },
  {
    "question": "What is 'React.FC' (or React.FunctionComponent)?",
    "options": {
      "A": "A new version of React",
      "B": "A generic type for defining functional components that provides automatic typing for children and return types",
      "C": "A database for React",
      "D": "A CSS framework"
    },
    "answer": "B"
  },
  {
    "question": "Which hook is often typed as 'useRef<HTMLInputElement>(null)' when accessing a DOM element?",
    "options": {
      "A": "useState",
      "B": "useRef",
      "C": "useEffect",
      "D": "useMemo"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Global Augmentation'?",
    "options": {
      "A": "Adding more memory to the server",
      "B": "A way to add declarations to the global scope from within a module",
      "C": "Changing the app's location",
      "D": "Updating the TypeScript version"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'triple-slash directive' (/// <reference path='...' />) do?",
    "options": {
      "A": "It is a comment only",
      "B": "It acts as a single-line XML tag containing instructions for the compiler about file dependencies",
      "C": "It deletes three lines of code",
      "D": "It creates a new branch in Git"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Downlevel Iteration' (downlevelIteration) in tsconfig.json?",
    "options": {
      "A": "A way to slow down loops",
      "B": "A flag that enables full support for ES6 iterables (like Map and Set) when targeting older JS versions like ES5",
      "C": "A type of recursive function",
      "D": "A tool to delete old variables"
    },
    "answer": "B"
  },
  {
    "question": "Which utility type constructs a type with all properties of 'T' set to 'readonly', meaning they cannot be reassigned?",
    "options": {
      "A": "Locked<T>",
      "B": "Readonly<T>",
      "C": "Constant<T>",
      "D": "Private<T>"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Const Enum'?",
    "options": {
      "A": "An enum that is hidden",
      "B": "An enum that is completely removed during compilation and replaced by literal values for performance",
      "C": "A global enum",
      "D": "A type of constant variable"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Type Branding' (or Opaque Types) in TypeScript?",
    "options": {
      "A": "Designing a logo for a type",
      "B": "A technique to create unique types from the same base type (like string) to prevent accidental misuse (e.g., UserId vs PostId)",
      "C": "A security feature",
      "D": "A way to name classes"
    },
    "answer": "B"
  },
  {
    "question": "Which flag ensures that 'this' is not implicitly treated as 'any'?",
    "options": {
      "A": "strict",
      "B": "noImplicitThis",
      "C": "checkThis",
      "D": "strictPropertyInitialization"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Project References' in a monorepo setup?",
    "options": {
      "A": "To list the names of other developers",
      "B": "To allow a TypeScript project to depend on other TypeScript projects, improving build times by sharing outputs",
      "C": "To store API keys",
      "D": "To manage Git branches"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Path Mapping' in tsconfig.json?",
    "options": {
      "A": "A GPS feature",
      "B": "The 'paths' property which allows you to define aliases for long or complex import paths",
      "C": "A way to organize folders",
      "D": "A network protocol"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Declaration Maps' (declarationMap) used for?",
    "options": {
      "A": "To draw a map of the app",
      "B": "To create source maps that link .d.ts files back to the original .ts source files for better IDE navigation",
      "C": "To store types in a database",
      "D": "To track module history"
    },
    "answer": "B"
  },
  {
    "question": "How do you define a type that is a 'String' but specifically matches a certain pattern (e.g., a URL or Email) in TS (conceptually)?",
    "options": {
      "A": "Using Regex types (not natively supported as of 2026)",
      "B": "Template Literal Types combined with custom brands",
      "C": "By using the 'pattern' keyword",
      "D": "In the HTML file"
    },
    "answer": "B"
  },
  {
    "question": "Which decorator is used to observe or modify a parameter of a method?",
    "options": {
      "A": "Class Decorator",
      "B": "Parameter Decorator",
      "C": "Property Decorator",
      "D": "Method Decorator"
    },
    "answer": "B"
  },
  {
    "question": "What is the result of using 'readonly' on a class property in the constructor?",
    "options": {
      "A": "It can never be set",
      "B": "It can be set inside the constructor but nowhere else",
      "C": "It is automatically private",
      "D": "It is automatically public"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Polymorphic this'?",
    "options": {
      "A": "A type for many users",
      "B": "Using 'this' as a return type to enable fluent interface patterns (method chaining) that work with inheritance",
      "C": "A way to hide variables",
      "D": "A database feature"
    },
    "answer": "B"
  },
  {
    "question": "Which tsconfig option prevents 'strict' checking for files in the node_modules folder?",
    "options": {
      "A": "skipLibCheck",
      "B": "ignoreModules",
      "C": "noCheckNode",
      "D": "moduleIgnore"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Type-Only Imports' (import type ...)?",
    "options": {
      "A": "Imports that are faster",
      "B": "A syntax that ensures the imported code is only used for type checking and is removed from the final JavaScript",
      "C": "Imports for CSS only",
      "D": "A type of network call"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Namespace Merging'?",
    "options": {
      "A": "Combining two different apps",
      "B": "Merging a namespace with a class or function to add extra static properties",
      "C": "Deleting duplicate namespaces",
      "D": "A network tool"
    },
    "answer": "B"
  },
  {
    "question": "Which React hook returns a tuple containing [state, dispatch] in a TypeScript project?",
    "options": {
      "A": "useState",
      "B": "useReducer",
      "C": "useContext",
      "D": "useEffect"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Strict Function Types' flag?",
    "options": {
      "A": "Makes all functions private",
      "B": "Ensures that function parameters are checked contravariantly rather than bivariantly",
      "C": "Deletes unused functions",
      "D": "A performance test"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Partial Re-export' in TypeScript?",
    "options": {
      "A": "Exporting only half a file",
      "B": "Exporting specific members from another module using 'export { x } from './file''",
      "C": "Deleting old exports",
      "D": "A UI layout"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Symbol' type in TypeScript used for?",
    "options": {
      "A": "To draw icons",
      "B": "To create unique, immutable identifiers often used as keys for object properties",
      "C": "To encrypt data",
      "D": "A type of math"
    },
    "answer": "B"
  },
  {
    "question": "Which flag in tsconfig.json allows for the use of the 'experimental' metadata API?",
    "options": {
      "A": "strict",
      "B": "emitDecoratorMetadata",
      "C": "sourceMap",
      "D": "checkJs"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Variance' (Covariance, Contravariance) in TypeScript types?",
    "options": {
      "A": "Different versions of a type",
      "B": "Rules that govern how complex types (like functions or lists) are compatible based on their sub-types",
      "C": "A network protocol",
      "D": "A type of animation"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Unknown' type vs 'Any' in a try-catch block?",
    "options": {
      "A": "Catch clauses now default to 'unknown' (or any) for better safety",
      "B": "They are the same",
      "C": "Unknown is not allowed in catch",
      "D": "Any is faster"
    },
    "answer": "A"
  },
  {
    "question": "Which utility type extracts the type of the 'this' parameter from a function type?",
    "options": {
      "A": "ThisParameterType<T>",
      "B": "GetThis<T>",
      "C": "InstanceType<T>",
      "D": "OmitThisParameter<T>"
    },
    "answer": "A"
  },
  {
    "question": "What does 'noImplicitReturns' flag do?",
    "options": {
      "A": "Deletes the return keyword",
      "B": "Ensures that all code paths in a function return a value explicitly",
      "C": "Speeds up the CPU",
      "D": "A security setting"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Assertion Function' in TypeScript?",
    "options": {
      "A": "A function that makes the user agree",
      "B": "A function that throws an error if a condition isn't met, helping the compiler narrow types (asserts condition)",
      "C": "A type of math",
      "D": "A database query"
    },
    "answer": "B"
  },
  {
    "question": "In React, what is the type for a 'Ref' pointing to a <div> element?",
    "options": {
      "A": "useRef<HTMLDivElement>(null)",
      "B": "useRef<Div>(null)",
      "C": "useRef<Element>(null)",
      "D": "useRef<JSX.Element>(null)"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Module Augmentation' use case?",
    "options": {
      "A": "Adding a new method to an existing external library's interface",
      "B": "Renaming a file",
      "C": "Deleting a module",
      "D": "A type of user login"
    },
    "answer": "A"
  },
  {
    "question": "Which keyword is used to provide an implementation for a static method in an abstract class?",
    "options": {
      "A": "static",
      "B": "override",
      "C": "virtual",
      "D": "concrete"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Literal Type' widening?",
    "options": {
      "A": "Making the text larger",
      "B": "When a literal value (like 'Red') is inferred as its broader type (like string) during assignment",
      "C": "A network error",
      "D": "A database feature"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'OmitThisParameter<T>' utility type?",
    "options": {
      "A": "To remove 'this' from a function signature",
      "B": "To delete a parameter",
      "C": "To rename a function",
      "D": "To hide a variable"
    },
    "answer": "A"
  },
  {
    "question": "Which flag ensures that class properties are actually initialized in the constructor?",
    "options": {
      "A": "strict",
      "B": "strictPropertyInitialization",
      "C": "noUninitialized",
      "D": "checkInit"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Declaration Emitting' (declaration: true)?",
    "options": {
      "A": "Telling the user the app is ready",
      "B": "Automatically generating .d.ts files for your project during build",
      "C": "A network protocol",
      "D": "A way to hide code"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Bivariant' parameter checking?",
    "options": {
      "A": "Checking two variants",
      "B": "A legacy behavior where function parameters could be checked as either super-types or sub-types (now restricted by strictFunctionTypes)",
      "C": "A type of mathematical proof",
      "D": "A performance test"
    },
    "answer": "B"
  },
  {
    "question": "What is 'VerifiHire AI's' focus for TypeScript candidates?",
    "options": {
      "A": "Writing shorter code",
      "B": "Ensuring enterprise-grade type safety, modularity, and predictable codebases",
      "C": "Avoiding JavaScript entirely",
      "D": "Only using the 'any' type"
    },
    "answer": "B"
  },
  {
    "question": "Which operator is used to extract the type of an element in an array?",
    "options": {
      "A": "typeof arr[0]",
      "B": "arr[number]",
      "C": "ElementOf<arr>",
      "D": "Both A and B"
    },
    "answer": "D"
  },
  {
    "question": "What is 'Non-Null Assertion' risk?",
    "options": {
      "A": "It can lead to runtime 'Cannot read property of null' errors if the developer is wrong",
      "B": "It makes the code run slow",
      "C": "It is not allowed by Google",
      "D": "It changes the UI theme"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'root' configuration for multiple tsconfig files in one project?",
    "options": {
      "A": "tsconfig.base.json and the 'extends' property",
      "B": "Multiple package.json files",
      "C": "One giant file",
      "D": "None; it is not possible"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Strict Bind Call Apply' flag?",
    "options": {
      "A": "Ensures the built-in bind, call, and apply methods are invoked with correct arguments",
      "B": "A tool to bind code together",
      "C": "A network security setting",
      "D": "A database tool"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Contravariance' in the context of TypeScript function parameters?",
    "options": {
      "A": "Parameters can be more specific than the expected type",
      "B": "Parameters must be the same or less specific (broader) than the expected type to ensure safety",
      "C": "Parameters are ignored by the compiler",
      "D": "It only applies to return types"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Recursive Type' in TypeScript?",
    "options": {
      "A": "A type that repeats itself in a loop",
      "B": "A type that references itself in its own definition, commonly used for tree or JSON structures",
      "C": "A type that deletes itself",
      "D": "A type used only for recursive functions"
    },
    "answer": "B"
  },
  {
    "question": "Which flag in tsconfig.json is used to improve performance by allowing TypeScript to skip type checking of declaration files (.d.ts)?",
    "options": {
      "A": "skipLibCheck",
      "B": "fastCompile",
      "C": "ignoreDts",
      "D": "noCheck"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Type Branding' (or Nominally-typed flavors) used to prevent?",
    "options": {
      "A": "Styling errors in CSS",
      "B": "Logic errors where two structurally identical types (like two different strings) are swapped by mistake",
      "C": "Network timeouts",
      "D": "Database injection"
    },
    "answer": "B"
  },
  {
    "question": "How do you implement a 'Brand' in TypeScript technically?",
    "options": {
      "A": "By using the @brand decorator",
      "B": "By intersecting a base type with an object containing a unique private property (e.g., string & { __brand: 'Id' })",
      "C": "By using the 'branded' keyword",
      "D": "In the package.json file"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Distributive Conditional Types' behavior?",
    "options": {
      "A": "Distributing the code to multiple servers",
      "B": "When a conditional type is applied to a union, it acts on each member of the union individually",
      "C": "Deleting members of a union",
      "D": "A way to handle math in types"
    },
    "answer": "B"
  },
  {
    "question": "How can you prevent a conditional type from being distributive?",
    "options": {
      "A": "By using the 'fixed' keyword",
      "B": "By wrapping the checked types in square brackets (e.g., [T] extends [any])",
      "C": "By using an interface instead",
      "D": "It is not possible to stop distribution"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Incremental' compilation (incremental flag)?",
    "options": {
      "A": "Compiling only on weekends",
      "B": "Saving information about the project graph from the last compilation to only re-compile changed files",
      "C": "Making the app larger over time",
      "D": "A network protocol"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'Object.is' comparison in TypeScript's internal state checking?",
    "options": {
      "A": "To check if the user is a human",
      "B": "To perform a precise equality check that handles NaN and -0/+0 correctly for type narrowing",
      "C": "To create a new object",
      "D": "To delete an object"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Type-Only' import/export (import type)?",
    "options": {
      "A": "A way to import CSS",
      "B": "Ensuring that the imported item is used only as a type and is completely removed during JavaScript emission",
      "C": "An import that is faster",
      "D": "A database tool"
    },
    "answer": "B"
  },
  {
    "question": "Which utility type converts all string literal properties of an object to uppercase?",
    "options": {
      "A": "ToUpper<T>",
      "B": "Uppercase<T> (Intrinsic string manipulation type)",
      "C": "Caps<T>",
      "D": "Strict<T>"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'satisfies' operator (introduced in TS 4.9)?",
    "options": {
      "A": "To check if the user is satisfied with the app",
      "B": "To validate that an expression matches a type without losing the most specific type inference",
      "C": "To replace the 'as' keyword",
      "D": "A database query"
    },
    "answer": "B"
  },
  {
    "question": "What is the risk of using 'any' in a high-scale enterprise TypeScript project?",
    "options": {
      "A": "It makes the code look bad",
      "B": "It creates 'type holes' where errors are not caught until runtime, defeating the purpose of TypeScript",
      "C": "It increases the build time",
      "D": "It is not allowed by the browser"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Opaque Types' in TypeScript?",
    "options": {
      "A": "Types that are invisible",
      "B": "Types that are intentionally restricted so they cannot be assigned to their underlying primitive without a cast",
      "C": "A type of UI theme",
      "D": "A security vulnerability"
    },
    "answer": "B"
  },
  {
    "question": "Which flag ensures that every property of a class is initialized in the constructor or has a default value?",
    "options": {
      "A": "strict",
      "B": "strictPropertyInitialization",
      "C": "checkClass",
      "D": "noEmitOnError"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Type Intersection' performance cost?",
    "options": {
      "A": "It has no cost",
      "B": "Extremely large or complex intersections can slow down the compiler's type-checking speed significantly",
      "C": "It costs money to use",
      "D": "It uses more GPU memory"
    },
    "answer": "B"
  },
  {
    "question": "In a monorepo, what does 'composite: true' in tsconfig.json enable?",
    "options": {
      "A": "3D graphics",
      "B": "Project References, allowing for faster builds and better modularity across packages",
      "C": "Multiple languages in one file",
      "D": "Automatic database syncing"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Mapped Type' key remapping (as keyword)?",
    "options": {
      "A": "Changing the values of an object",
      "B": "Transforming the property names of a type during the mapping process (e.g., adding a 'get' prefix)",
      "C": "Renaming the file",
      "D": "A network tool"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'NoImplicitAny'?",
    "options": {
      "A": "To force developers to write longer code",
      "B": "To raise an error on expressions and declarations with an implied 'any' type",
      "C": "To speed up the app",
      "D": "To allow null values"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Covariance' in function return types?",
    "options": {
      "A": "The return type must be broader than expected",
      "B": "The return type can be the same or more specific than the expected type",
      "C": "The return type is ignored",
      "D": "It is not supported in TS"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Intrinsic' type in TypeScript?",
    "options": {
      "A": "A type for the internal CPU",
      "B": "Built-in types provided by the compiler (like Uppercase, Lowercase) that are not defined in source code",
      "C": "A private type",
      "D": "A type of network call"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Template Literal Types' recursion limit?",
    "options": {
      "A": "5 levels",
      "B": "Roughly 50-100 levels depending on the TS version; used to prevent compiler crashes",
      "C": "Unlimited",
      "D": "1 level"
    },
    "answer": "B"
  },
  {
    "question": "Which keyword is used to provide a default type for a generic parameter?",
    "options": {
      "A": "default",
      "B": "using the assignment operator (=) (e.g., <T = string>)",
      "C": "extends",
      "D": "as"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Ambiguous' type check in Overloads?",
    "options": {
      "A": "When the compiler cannot determine which function signature to use based on the arguments",
      "B": "When the code is hard to read",
      "C": "A network error",
      "D": "A database timeout"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Module Resolution: NodeNext'?",
    "options": {
      "A": "A new version of Node.js",
      "B": "A strategy that matches modern Node.js ESM/CJS resolution patterns exactly",
      "C": "A way to hide modules",
      "D": "A type of CSS index"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Partial<Record<K, T>>' pattern?",
    "options": {
      "A": "To create a map where every key is required",
      "B": "To create a map where all possible keys exist but their values are optional",
      "C": "To delete a record",
      "D": "To track changes"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Assertion Function' signature?",
    "options": {
      "A": "function(x: any): x is Type",
      "B": "asserts condition",
      "C": "asserts x is Type",
      "D": "Both B and C"
    },
    "answer": "D"
  },
  {
    "question": "In React, what is the type for 'children' in a modern functional component?",
    "options": {
      "A": "React.ReactNode",
      "B": "JSX.Element",
      "C": "any",
      "D": "string"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Type Inference' from the 'in' operator?",
    "options": {
      "A": "Checking if a property exists in an object to narrow the type to one that contains that property",
      "B": "A type of loop",
      "C": "A network tool",
      "D": "A way to name classes"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Const' modifier on type parameters (TS 5.0)?",
    "options": {
      "A": "Making a variable constant",
      "B": "Ensuring that the inferred type of a generic parameter defaults to a 'const' (literal) inference",
      "C": "A way to hide code",
      "D": "A database key"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Declaration emit' performance bottleneck?",
    "options": {
      "A": "Generating thousands of .d.ts files can significantly increase build times",
      "B": "It uses too much internet",
      "C": "It is not allowed by Apple",
      "D": "It deletes source code"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Unknown' vs '{}' (Empty Object type)?",
    "options": {
      "A": "'{}' can be anything except null/undefined; 'unknown' can be truly anything",
      "B": "They are identical",
      "C": "Unknown is for arrays only",
      "D": "{} is for numbers"
    },
    "answer": "A"
  },
  {
    "question": "What is the purpose of 'PreserveValueDeclaration' flag?",
    "options": {
      "A": "To keep the user's data",
      "B": "An internal flag that controls how variables are emitted in certain module formats",
      "C": "To speed up the app",
      "D": "To manage project IDs"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Indexed Access Type' T[K]?",
    "options": {
      "A": "Accessing a file on disk",
      "B": "Looking up the type of a property on another type using its key",
      "C": "A type of loop",
      "D": "A database join"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Variadic Tuple Types'?",
    "options": {
      "A": "Tuples that change colors",
      "B": "Tuples that can use the spread operator (...) to represent an unknown number of elements of a certain type",
      "C": "Tuples used for audio",
      "D": "A network protocol"
    },
    "answer": "B"
  },
  {
    "question": "Which flag enables checking of 'JavaScript' files in a TypeScript project?",
    "options": {
      "A": "checkJs",
      "B": "allowJs",
      "C": "both A and B (allowJs must be true for checkJs to work)",
      "D": "noJsErrors"
    },
    "answer": "C"
  },
  {
    "question": "What is 'Type Widening' in an object literal?",
    "options": {
      "A": "Making the object larger",
      "B": "When a specific literal (like 'red') is inferred as its general type (string) during assignment",
      "C": "A network error",
      "D": "A database feature"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Decorator Metadata' dependency?",
    "options": {
      "A": "The 'reflect-metadata' library",
      "B": "The browser version",
      "C": "The user's account",
      "D": "A CSS file"
    },
    "answer": "A"
  },
  {
    "question": "What is 'TypeScript's' final goal in a project?",
    "options": {
      "A": "To provide a zero-bug guarantee",
      "B": "To catch type-related errors early and provide a better development experience through tooling and safety",
      "C": "To replace JavaScript entirely",
      "D": "To run faster in production"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'never' type in a conditional type used for?",
    "options": {
      "A": "To throw an error",
      "B": "To 'filter out' members from a union (since unioning with never results in the other members)",
      "C": "To stop the function",
      "D": "To hide a variable"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Module Augmentation' limitation?",
    "options": {
      "A": "It can only add members, not remove them",
      "B": "It only works on Tuesdays",
      "C": "It is not allowed in production",
      "D": "It deletes the module"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Self-Referencing' generic constraint?",
    "options": {
      "A": "<T extends T>",
      "B": "<T extends Base<T>> (F-Bounded Polymorphism)",
      "C": "A loop error",
      "D": "A private generic"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Strict Null Checks' impact on Optional properties?",
    "options": {
      "A": "It makes them required",
      "B": "It ensures that an optional property 'prop?: string' is treated as 'string | undefined'",
      "C": "It deletes optional properties",
      "D": "It has no impact"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Ambient' module definition?",
    "options": {
      "A": "A module that makes noise",
      "B": "A way to declare the structure of a module in a .d.ts file without an implementation",
      "C": "A network protocol",
      "D": "A UI theme"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Exhaustive Switch' implementation using 'never'?",
    "options": {
      "A": "case default: const _exhaustiveCheck: never = val; return _exhaustiveCheck;",
      "B": "case default: throw Error();",
      "C": "case default: return null;",
      "D": "There is no way to do this"
    },
    "answer": "A"
  },
  {
    "question": "What is 'VerifiHire AI's' final TypeScript question?",
    "options": {
      "A": "This one!",
      "B": "The first one",
      "C": "There is no final question",
      "D": "A network protocol"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'keyof any' type equivalent to?",
    "options": {
      "A": "string | number | symbol",
      "B": "any",
      "C": "object",
      "D": "unknown"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Mapped Type' modifier prefix (+ or -)?",
    "options": {
      "A": "Adding or subtracting numbers",
      "B": "Explicitly adding or removing modifiers like 'readonly' or '?' during mapping",
      "C": "A type of mathematical operator",
      "D": "A database tool"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Type Alias' vs 'Interface' for Primitive types?",
    "options": {
      "A": "Interfaces can define primitive aliases; types cannot",
      "B": "Type aliases can define primitive aliases (e.g. type MyStr = string); interfaces cannot",
      "C": "Both can do it",
      "D": "Neither can do it"
    },
    "answer": "B"
  },
  {
    "question": "What is 'TypeScript' runtime presence?",
    "options": {
      "A": "It is exactly like JavaScript at runtime; all types are erased",
      "B": "It provides extra security at runtime",
      "C": "It checks types while the app is running",
      "D": "It makes the app slower"
    },
    "answer": "A"
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
    skill = "Typescript"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
