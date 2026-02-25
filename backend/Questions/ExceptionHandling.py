from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
    {
        "question": "Which class is the root of the entire exception hierarchy in Java?",
        "options": {
            "A": "Exception",
            "B": "Throwable",
            "C": "Error",
            "D": "RuntimeException"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary difference between an 'Error' and an 'Exception' in Java?",
        "options": {
            "A": "Exceptions are fatal; Errors are not",
            "B": "Errors represent serious problems that applications usually should not try to catch (e.g., OutOfMemoryError)",
            "C": "Errors are checked; Exceptions are unchecked",
            "D": "There is no difference"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is a 'Checked' exception?",
        "options": {
            "A": "NullPointerException",
            "B": "IOException",
            "C": "ArithmeticException",
            "D": "ArrayIndexOutOfBoundsException"
        },
        "answer": "B"
    },
    {
        "question": "What is the requirement for handling 'Checked' exceptions in Java?",
        "options": {
            "A": "They must be either caught or declared in the method's 'throws' clause",
            "B": "They are handled automatically by the JVM",
            "C": "They must be logged to a file",
            "D": "They can only be handled in the main method"
        },
        "answer": "A"
    },
    {
        "question": "Which block is used to enclose code that might throw an exception?",
        "options": {
            "A": "catch",
            "B": "try",
            "C": "finally",
            "D": "throw"
        },
        "answer": "B"
    },
    {
        "question": "Which block always executes, regardless of whether an exception was thrown or caught?",
        "options": {
            "A": "try",
            "B": "catch",
            "C": "finally",
            "D": "throws"
        },
        "answer": "C"
    },
    {
        "question": "What is the purpose of the 'throw' keyword?",
        "options": {
            "A": "To declare an exception in a method signature",
            "B": "To explicitly throw a specific exception instance from code",
            "C": "To ignore an exception",
            "D": "To catch an exception"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'throws' keyword?",
        "options": {
            "A": "To throw an exception",
            "B": "To declare that a method may throw one or more specific exceptions",
            "C": "To handle an exception",
            "D": "To log an error"
        },
        "answer": "B"
    },
    {
        "question": "Which exception is thrown when you try to divide a number by zero?",
        "options": {
            "A": "NullPointerException",
            "B": "ArithmeticException",
            "C": "NumberFormatException",
            "D": "IllegalArgumentException"
        },
        "answer": "B"
    },
    {
        "question": "Which exception is thrown when an application attempts to use 'null' in a case where an object is required?",
        "options": {
            "A": "ClassNotFoundException",
            "B": "NullPointerException",
            "C": "IllegalStateException",
            "D": "ClassCastException"
        },
        "answer": "B"
    },
    {
        "question": "Can you have a 'try' block without a 'catch' block?",
        "options": {
            "A": "No, it's a compile-time error",
            "B": "Yes, but only if it is followed by a 'finally' block",
            "C": "Yes, always",
            "D": "No, it causes a memory leak"
        },
        "answer": "B"
    },
    {
        "question": "What happens if an exception occurs in a 'try' block and there is no matching 'catch' block?",
        "options": {
            "A": "The program ignores it and continues",
            "B": "The program terminates after executing the 'finally' block (if present)",
            "C": "The JVM restarts",
            "D": "The compiler fixes it"
        },
        "answer": "B"
    },
    {
        "question": "Which class is the parent of all 'Unchecked' (Runtime) exceptions?",
        "options": {
            "A": "Exception",
            "B": "RuntimeException",
            "C": "Error",
            "D": "Throwable"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Multi-catch' (introduced in Java 7)?",
        "options": {
            "A": "Catching exceptions from multiple threads",
            "B": "Catching multiple exception types in a single catch block using the pipe (|) operator",
            "C": "Using multiple try blocks",
            "D": "Throwing multiple exceptions at once"
        },
        "answer": "B"
    },
    {
        "question": "When using multiple 'catch' blocks, what is the rule regarding the order of exceptions?",
        "options": {
            "A": "Subclasses must be caught before parent classes",
            "B": "Parent classes must be caught before subclasses",
            "C": "Order does not matter",
            "D": "Alphabetical order is required"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Try-with-resources' (introduced in Java 7)?",
        "options": {
            "A": "A try block that automatically closes resources (like files or streams) that implement AutoCloseable",
            "B": "A try block that uses more CPU",
            "C": "A way to catch Errors",
            "D": "A replacement for the catch block"
        },
        "answer": "A"
    },
    {
        "question": "Which exception is thrown when a string cannot be converted into a numeric format?",
        "options": {
            "A": "ArithmeticException",
            "B": "NumberFormatException",
            "C": "ClassCastException",
            "D": "StringIndexOutOfBoundsException"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'printStackTrace()' method do?",
        "options": {
            "A": "Deletes the error log",
            "B": "Prints the exception name, description, and the sequence of method calls (stack trace) to the console",
            "C": "Prints the whole source code",
            "D": "Restarts the program"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Custom Exception'?",
        "options": {
            "A": "An exception provided by the Java Standard Library",
            "B": "A user-defined class that extends Exception or RuntimeException",
            "C": "An error in the hardware",
            "D": "A security vulnerability"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to get the detailed description of an exception?",
        "options": {
            "A": "getMessage()",
            "B": "toString()",
            "C": "getDescription()",
            "D": "trace()"
        },
        "answer": "A"
    },
    {
        "question": "Can a method override a parent method and throw a 'broader' checked exception?",
        "options": {
            "A": "Yes",
            "B": "No, it can only throw the same or a narrower checked exception",
            "C": "Only if it's a runtime exception",
            "D": "Only in Java 8+"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Chained Exception' in Java?",
        "options": {
            "A": "Linking multiple try blocks",
            "B": "Associating one exception as the cause of another exception using the 'initCause' method or constructor",
            "C": "A loop that throws exceptions",
            "D": "Handling exceptions in a chain of catch blocks"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is NOT a checked exception?",
        "options": {
            "A": "FileNotFoundException",
            "B": "SQLException",
            "C": "IllegalArgumentException",
            "D": "ClassNotFoundException"
        },
        "answer": "C"
    },
    {
        "question": "What is the result of executing 'System.exit(0)' inside a 'try' block?",
        "options": {
            "A": "The 'finally' block executes first",
            "B": "The program terminates immediately and the 'finally' block does NOT execute",
            "C": "The program crashes",
            "D": "The JVM ignores the command"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Unchecked' exception also known as?",
        "options": {
            "A": "Compile-time exception",
            "B": "Runtime exception",
            "C": "Syntax error",
            "D": "Logic error"
        },
        "answer": "B"
    },
    {
        "question": "Which keyword is used in a method signature to indicate that the method might throw an exception?",
        "options": {
            "A": "throw",
            "B": "throws",
            "C": "try",
            "D": "catch"
        },
        "answer": "B"
    },
    {
        "question": "Can you throw a checked exception from a static block?",
        "options": {
            "A": "Yes",
            "B": "No, because there is no method signature to declare 'throws'",
            "C": "Only if it's a FileNotFoundException",
            "D": "Only if it's caught within the block"
        },
        "answer": "D"
    },
    {
        "question": "What is the base class of 'Error' and 'Exception'?",
        "options": {
            "A": "Object",
            "B": "Throwable",
            "C": "RuntimeException",
            "D": "System"
        },
        "answer": "B"
    },
    {
        "question": "Which of these errors indicates that the JVM has run out of memory?",
        "options": {
            "A": "StackOverflowError",
            "B": "OutOfMemoryError",
            "C": "NoClassDefFoundError",
            "D": "InternalError"
        },
        "answer": "B"
    },
    {
        "question": "Which of these errors indicates an infinite recursion has occurred?",
        "options": {
            "A": "OutOfMemoryError",
            "B": "StackOverflowError",
            "C": "ThreadDeath",
            "D": "VirtualMachineError"
        },
        "answer": "B"
    },
    {
        "question": "How many 'finally' blocks can follow a single 'try' block?",
        "options": {
            "A": "Zero or one",
            "B": "As many as you want",
            "C": "One for each catch block",
            "D": "None"
        },
        "answer": "A"
    },
    {
        "question": "What happens if a 'finally' block contains a 'return' statement?",
        "options": {
            "A": "It is ignored",
            "B": "It overrides any return statement in the try or catch blocks",
            "C": "It causes a compilation error",
            "D": "It only executes if there was no exception"
        },
        "answer": "B"
    },
    {
        "question": "Which exception is thrown if you try to access an index of an array that doesn't exist?",
        "options": {
            "A": "NullPointerException",
            "B": "ArrayIndexOutOfBoundsException",
            "C": "IndexOutOfBoundsException",
            "D": "Both B and C (B is a subclass of C)"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Rethrowing' an exception?",
        "options": {
            "A": "Catching an exception and throwing it again (or throwing a new one) to be handled by the caller",
            "B": "Throwing the same exception twice in one block",
            "C": "Ignoring the error",
            "D": "Cleaning the stack trace"
        },
        "answer": "A"
    },
    {
        "question": "Which of the following can be thrown?",
        "options": {
            "A": "Only classes that extend Exception",
            "B": "Only classes that extend Error",
            "C": "Any class that extends Throwable",
            "D": "Any Java class"
        },
        "answer": "C"
    },
    {
        "question": "In 'Try-with-resources', what interface must a resource implement to be closed automatically?",
        "options": {
            "A": "Serializable",
            "B": "Cloneable",
            "C": "AutoCloseable (or its sub-interface Closeable)",
            "D": "Runnable"
        },
        "answer": "C"
    },
    {
        "question": "What is the difference between 'final', 'finally', and 'finalize'?",
        "options": {
            "A": "final is a keyword, finally is a block, finalize is a method (for GC cleanup)",
            "B": "They are the same",
            "C": "They are all blocks",
            "D": "final is for exceptions only"
        },
        "answer": "A"
    },
    {
        "question": "Is it possible to catch a checked exception that is never thrown in the try block?",
        "options": {
            "A": "Yes",
            "B": "No, it will result in a compilation error",
            "C": "Only if it's a generic Exception",
            "D": "Only in Java 17+"
        },
        "answer": "B"
    },
    {
        "question": "Which of the following is an example of an Error?",
        "options": {
            "A": "SQLException",
            "B": "VirtualMachineError",
            "C": "NullPointerException",
            "D": "ClassNotFoundException"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'getStackTrace()' method return type?",
        "options": {
            "A": "String",
            "B": "StackTraceElement[]",
            "C": "List<String>",
            "D": "Void"
        },
        "answer": "B"
    },
    {
        "question": "Which exception is thrown when an object is cast to a subclass of which it is not an instance?",
        "options": {
            "A": "ClassCastException",
            "B": "ClassNotFoundException",
            "C": "InstantiationException",
            "D": "IllegalAccessException"
        },
        "answer": "A"
    },
    {
        "question": "What is a 'Suppressed Exception'?",
        "options": {
            "A": "An exception that is caught but not logged",
            "B": "An exception that occurs while closing a resource in a try-with-resources block when another exception is already active",
            "C": "An exception that is ignored by the JVM",
            "D": "A custom error"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to retrieve suppressed exceptions?",
        "options": {
            "A": "getSuppressed()",
            "B": "getCause()",
            "C": "getMessages()",
            "D": "getHidden()"
        },
        "answer": "A"
    },
    {
        "question": "Can you have a try block without any catch or finally block?",
        "options": {
            "A": "Yes, if it's a try-with-resources block",
            "B": "No, never",
            "C": "Only if it throws an error",
            "D": "Only in static methods"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of 'Exception Handling'?",
        "options": {
            "A": "To fix bugs automatically",
            "B": "To maintain the normal flow of the application in the event of runtime errors",
            "C": "To make the program run faster",
            "D": "To prevent users from seeing code"
        },
        "answer": "B"
    },
    {
        "question": "Which exception is thrown when a requested class is not found during runtime?",
        "options": {
            "A": "NoClassDefFoundError",
            "B": "ClassNotFoundException",
            "C": "NoSuchMethodException",
            "D": "InstantiationException"
        },
        "answer": "B"
    },
    {
        "question": "What is the difference between 'throws' and 'throw'?",
        "options": {
            "A": "throws is used in method signature; throw is used in method body",
            "B": "throw is for multiple exceptions; throws for one",
            "C": "They are interchangeable",
            "D": "throws is for runtime exceptions only"
        },
        "answer": "A"
    },
    {
        "question": "Which of these is a subclass of RuntimeException?",
        "options": {
            "A": "SQLException",
            "B": "FileNotFoundException",
            "C": "NumberFormatException",
            "D": "InterruptedException"
        },
        "answer": "C"
    },
    {
        "question": "What happens if a 'finally' block throws an exception?",
        "options": {
            "A": "The previous exception is lost and the new exception from finally is propagated",
            "B": "The program stops instantly without propagation",
            "C": "The JVM catches it automatically",
            "D": "It is suppressed"
        },
        "answer": "A"
    },
    {
        "question": "Final question of Batch 1: Checked exceptions are checked at _______?",
        "options": {
            "A": "Runtime",
            "B": "Compile-time",
            "C": "Link-time",
            "D": "Deployment-time"
        },
        "answer": "B"
    },
    {
        "question": "When creating a Custom Exception, which class should you extend to make it a 'Checked' exception?",
        "options": {
            "A": "RuntimeException",
            "B": "Exception",
            "C": "Throwable",
            "D": "Error"
        },
        "answer": "B"
    },
    {
        "question": "Which of the following is considered a 'Best Practice' for exception handling?",
        "options": {
            "A": "Catch the generic 'Exception' class for everything",
            "B": "Catch specific exceptions to provide meaningful handling for different error types",
            "C": "Leave catch blocks empty to keep the program running",
            "D": "Always use printStackTrace() in production logs"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Exception Swallowing'?",
        "options": {
            "A": "Handling an exception and resolving the issue",
            "B": "Catching an exception but neither logging it nor rethrowing it, making the error 'invisible'",
            "C": "A type of memory leak",
            "D": "Throwing an exception to the parent class"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'initCause(Throwable cause)' method do?",
        "options": {
            "A": "Initializes the JVM",
            "B": "Associates a specific cause with an exception for chained exception handling",
            "C": "Resets the stack trace",
            "D": "Clears the error message"
        },
        "answer": "B"
    },
    {
        "question": "Why should you avoid catching the 'Throwable' class directly?",
        "options": {
            "A": "It is a compilation error",
            "B": "It will catch 'Errors' (like OutOfMemoryError) which the application shouldn't attempt to handle",
            "C": "It makes the code run slower",
            "D": "Throwable is a private class"
        },
        "answer": "B"
    },
    {
        "question": "What is the result of a 'finally' block throwing an exception while another exception is being thrown from the 'try' block?",
        "options": {
            "A": "The try-block exception is preserved",
            "B": "The try-block exception is suppressed/lost, and the finally-block exception propagates",
            "C": "Both exceptions are combined into a list",
            "D": "The program enters a deadlock"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is a valid 'Multi-catch' syntax?",
        "options": {
            "A": "catch (IOException e, SQLException e)",
            "B": "catch (IOException | SQLException e)",
            "C": "catch (IOException & SQLException e)",
            "D": "catch (IOException || SQLException e)"
        },
        "answer": "B"
    },
    {
        "question": "In a multi-catch block, what is the implicit modifier of the exception variable 'e'?",
        "options": {
            "A": "static",
            "B": "final",
            "C": "volatile",
            "D": "transient"
        },
        "answer": "B"
    },
    {
        "question": "Which error is thrown if the JVM cannot find the definition of a class that was available during compilation?",
        "options": {
            "A": "ClassNotFoundException",
            "B": "NoClassDefFoundError",
            "C": "NoSuchMethodError",
            "D": "LinkageError"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Loss of Exception'?",
        "options": {
            "A": "Deleting the log file",
            "B": "When a 'return' or 'throw' in a finally block accidentally discards an exception from the try block",
            "C": "Using a generic exception handler",
            "D": "A memory management error"
        },
        "answer": "B"
    },
    {
        "question": "Which of the following is an Unchecked Exception?",
        "options": {
            "A": "InterruptedException",
            "B": "IllegalStateException",
            "C": "MalformedURLException",
            "D": "RemoteException"
        },
        "answer": "B"
    },
    {
        "question": "What happens if you try to catch a Checked Exception that the 'try' block cannot possibly throw?",
        "options": {
            "A": "The code runs normally",
            "B": "A compile-time error occurs (Unreachable catch block)",
            "C": "The JVM ignores the catch block",
            "D": "A RuntimeException is thrown"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to get the original cause of a chained exception?",
        "options": {
            "A": "getReason()",
            "B": "getCause()",
            "C": "getSource()",
            "D": "getRoot()"
        },
        "answer": "B"
    },
    {
        "question": "Can a 'finally' block be used to close a database connection if the 'try' block fails?",
        "options": {
            "A": "No, it only runs if the try succeeds",
            "B": "Yes, it is the standard location for resource cleanup to ensure it runs regardless of error",
            "C": "Only if the database supports it",
            "D": "Only if there is no catch block"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'AssertionError'?",
        "options": {
            "A": "To handle user input errors",
            "B": "To indicate that a programmer's 'assert' statement has failed (logic verification)",
            "C": "To handle network failures",
            "D": "To check database connections"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Liskov Substitution Principle' relevance to 'throws' clause?",
        "options": {
            "A": "A subclass method cannot throw more/broader checked exceptions than the parent method",
            "B": "A subclass must throw the exact same exception",
            "C": "Exceptions have nothing to do with inheritance",
            "D": "Checked exceptions must be converted to Unchecked"
        },
        "answer": "A"
    },
    {
        "question": "Which of these should usually NOT be caught in application code?",
        "options": {
            "A": "NullPointerException",
            "B": "StackOverflowError",
            "C": "FileNotFoundException",
            "D": "ParseException"
        },
        "answer": "B"
    },
    {
        "question": "What does 'fillInStackTrace()' do?",
        "options": {
            "A": "Deletes the current stack trace",
            "B": "Re-initializes the stack trace of an exception to the current point in execution",
            "C": "Adds comments to the trace",
            "D": "Prints the trace to a file"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Checked' exception primarily used for?",
        "options": {
            "A": "Programming errors",
            "B": "Contingencies or recoverable conditions that the caller is expected to handle",
            "C": "JVM failure",
            "D": "Hardware bugs"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Exception Propagation'?",
        "options": {
            "A": "Copying an exception to a list",
            "B": "The process where an uncaught exception is dropped down the call stack until a handler is found",
            "C": "Logging the exception at every level",
            "D": "Automatically fixing the error"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is a RuntimeException?",
        "options": {
            "A": "NoSuchMethodException",
            "B": "NegativeArraySizeException",
            "C": "IllegalAccessException",
            "D": "NoSuchFieldException"
        },
        "answer": "B"
    },
    {
        "question": "Can an 'Interface' method declare a 'throws' clause?",
        "options": {
            "A": "No, interfaces cannot have exceptions",
            "B": "Yes, to force implementing classes to handle or declare those exceptions",
            "C": "Only for RuntimeExceptions",
            "D": "Only if the interface is public"
        },
        "answer": "B"
    },
    {
        "question": "Which exception is thrown by 'Thread.sleep()'?",
        "options": {
            "A": "TimeoutException",
            "B": "InterruptedException",
            "C": "RuntimeException",
            "D": "ExecutionException"
        },
        "answer": "B"
    },
    {
        "question": "What is the effect of 'catch (Exception e)' on code quality?",
        "options": {
            "A": "It is highly recommended",
            "B": "It is generally discouraged because it catches both expected and unexpected exceptions",
            "C": "It is a syntax error",
            "D": "It speeds up the program"
        },
        "answer": "B"
    },
    {
        "question": "What happens when a 'Daemon' thread throws an uncaught exception?",
        "options": {
            "A": "The whole application crashes",
            "B": "The thread terminates, but the JVM continues running (unless it's the last thread)",
            "C": "The JVM restarts the thread",
            "D": "A system alert is shown"
        },
        "answer": "B"
    },
    {
        "question": "Which error is thrown if an application attempts to create an instance of a class but has no access to its constructor?",
        "options": {
            "A": "IllegalAccessException",
            "B": "IllegalAccessError",
            "C": "SecurityException",
            "D": "InstantiationError"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'UncaughtExceptionHandler'?",
        "options": {
            "A": "To prevent exceptions from occurring",
            "B": "To define a custom action when a thread terminates due to an uncaught exception",
            "C": "To catch all errors at compile time",
            "D": "To restart the computer"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is a Checked Exception?",
        "options": {
            "A": "EnumConstantNotPresentException",
            "B": "CloneNotSupportedException",
            "C": "ArrayStoreException",
            "D": "SecurityException"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Defensive Programming' in the context of exceptions?",
        "options": {
            "A": "Catching every possible exception",
            "B": "Checking for nulls or invalid state before performing operations to avoid exceptions (e.g., NullPointerException)",
            "C": "Encryption of error logs",
            "D": "Using try-catch in every method"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Fail-Fast' behavior?",
        "options": {
            "A": "Ignoring errors to finish quickly",
            "B": "Immediately throwing an exception as soon as an unexpected condition is detected to avoid hidden corruption",
            "C": "A performance metric",
            "D": "A type of database optimization"
        },
        "answer": "B"
    },
    {
        "question": "Which exception is thrown if you try to modify a list while iterating over it with a for-each loop?",
        "options": {
            "A": "ConcurrentModificationException",
            "B": "UnsupportedOperationException",
            "C": "IllegalStateException",
            "D": "ArrayIndexOutOfBoundsException"
        },
        "answer": "A"
    },
    {
        "question": "What is the 'getLocalizedMessage()' method for?",
        "options": {
            "A": "To get the message in a specific language (if overridden)",
            "B": "To get the name of the file",
            "C": "To get the IP address of the server",
            "D": "To encrypt the message"
        },
        "answer": "A"
    },
    {
        "question": "Which of these occurs if a class extends another class that has a different version during runtime?",
        "options": {
            "A": "IncompatibleClassChangeError",
            "B": "AbstractMethodError",
            "C": "ClassCastException",
            "D": "VerifyError"
        },
        "answer": "A"
    },
    {
        "question": "Can you 'throw' an instance of a class that extends Error?",
        "options": {
            "A": "Yes, but it is rarely done",
            "B": "No, Errors are only thrown by the JVM",
            "C": "Only in static blocks",
            "D": "Only if the class is final"
        },
        "answer": "A"
    },
    {
        "question": "What is the 'Exception-per-method' anti-pattern?",
        "options": {
            "A": "Defining a unique exception for every single method in a project",
            "B": "Using only one exception for the whole app",
            "C": "Not using any exceptions",
            "D": "Logging errors only in the main method"
        },
        "answer": "A"
    },
    {
        "question": "Which block is executed if an exception is rethrown inside a catch block?",
        "options": {
            "A": "The current 'finally' block executes before the exception propagates up the stack",
            "B": "No other block executes",
            "C": "The next catch block in the same try-catch structure",
            "D": "The JVM immediately terminates"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Try-with-resources' effect on 'finally' block execution?",
        "options": {
            "A": "Resources are closed BEFORE any catch or finally blocks are executed",
            "B": "Resources are closed AFTER the finally block",
            "C": "Finally block is not allowed with try-with-resources",
            "D": "It has no effect"
        },
        "answer": "A"
    },
    {
        "question": "Which class is the parent of 'FileNotFoundException'?",
        "options": {
            "A": "IOException",
            "B": "Exception",
            "C": "RuntimeException",
            "D": "Throwable"
        },
        "answer": "A"
    },
    {
        "question": "In Java 9+, can you use an 'already opened' resource in a try-with-resources block?",
        "options": {
            "A": "Yes, if the variable is effectively final",
            "B": "No, it must be declared inside the try parentheses",
            "C": "Only if it is a File object",
            "D": "Only in the main method"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Standardizing' exception handling?",
        "options": {
            "A": "Using a central global handler or specific logging framework across the whole team",
            "B": "Naming all exceptions 'Error'",
            "C": "Only using checked exceptions",
            "D": "Deleting the stack trace"
        },
        "answer": "A"
    },
    {
        "question": "Which of these is a Checked Exception?",
        "options": {
            "A": "UnsupportedEncodingException",
            "B": "ArrayStoreException",
            "C": "EmptyStackException",
            "D": "NoSuchElementException"
        },
        "answer": "A"
    },
    {
        "question": "What happens if a 'catch' block throws a different exception than the one it caught?",
        "options": {
            "A": "The new exception is propagated, and the original is lost (unless chained)",
            "B": "Both exceptions are sent to the user",
            "C": "The program crashes immediately",
            "D": "The compiler prevents it"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Lazy Exception' handling?",
        "options": {
            "A": "Not catching the error until it's absolutely necessary",
            "B": "Catching Exception and doing nothing (swallowing)",
            "C": "Logging the error and moving on",
            "D": "A type of performance optimization"
        },
        "answer": "B"
    },
    {
        "question": "Can you 'return' a value from a catch block?",
        "options": {
            "A": "Yes, it is common in methods that need to return a default value on error",
            "B": "No, a catch block must throw something",
            "C": "Only if the method return type is void",
            "D": "Only if the finally block is missing"
        },
        "answer": "A"
    },
    {
        "question": "Which exception is thrown if you attempt to call a method on a proxy that is not valid?",
        "options": {
            "A": "UndeclaredThrowableException",
            "B": "ProxyError",
            "C": "InvocationTargetException",
            "D": "ReflectiveOperationException"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of 'Exception.setStackTrace(StackTraceElement[] stackTrace)'?",
        "options": {
            "A": "To programmatically modify or mock the stack trace of an exception",
            "B": "To print the trace",
            "C": "To clear the memory",
            "D": "To restart the program"
        },
        "answer": "A"
    },
    {
        "question": "Which of these is thrown when a thread is waiting, sleeping, or otherwise occupied, and the thread is interrupted?",
        "options": {
            "A": "InterruptedException",
            "B": "TimeoutException",
            "C": "IllegalThreadStateException",
            "D": "ThreadDeath"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Resource Leak'?",
        "options": {
            "A": "Failing to close files or connections in a finally block or try-with-resources",
            "B": "Throwing too many exceptions",
            "C": "Logging too much data",
            "D": "A type of memory corruption"
        },
        "answer": "A"
    },
    {
        "question": "Can a 'constructor' throw an exception?",
        "options": {
            "A": "Yes, and the object creation will fail",
            "B": "No, constructors must be error-free",
            "C": "Only RuntimeExceptions",
            "D": "Only if it is a private constructor"
        },
        "answer": "A"
    },
    {
        "question": "Final question of Batch 2: What is the most important rule when rethrowing an exception?",
        "options": {
            "A": "Always include the original exception as the 'cause' to preserve the stack trace",
            "B": "Always change the message",
            "C": "Always log it before throwing",
            "D": "Never rethrow checked exceptions"
        },
        "answer": "A"
    },
    {
        "question": "Which logging level is typically used for exceptions that do not stop the application but require investigation?",
        "options": {
            "A": "INFO",
            "B": "ERROR",
            "C": "WARN",
            "D": "DEBUG"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary disadvantage of using 'e.printStackTrace()' in a production enterprise application?",
        "options": {
            "A": "It only works in IDEs",
            "B": "It sends the stack trace to standard error (System.err), making it difficult to manage, filter, and store compared to a logging framework",
            "C": "It crashes the JVM",
            "D": "It deletes previous logs"
        },
        "answer": "B"
    },
    {
        "question": "In Java 8 Lambda expressions, how must 'Checked' exceptions be handled?",
        "options": {
            "A": "They are automatically converted to RuntimeExceptions",
            "B": "They must be caught within the lambda body or the functional interface must be custom-defined to throw them",
            "C": "Lambdas cannot throw exceptions",
            "D": "They are ignored by the compiler"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'sneaky throws' technique (often used in Lombok)?",
        "options": {
            "A": "Ignoring an exception entirely",
            "B": "A way to throw checked exceptions without declaring them in the 'throws' clause by tricking the compiler",
            "C": "A type of security attack",
            "D": "Automatically catching all errors"
        },
        "answer": "B"
    },
    {
        "question": "Which Spring Framework annotation is used to handle exceptions globally across all Controllers?",
        "options": {
            "A": "@ExceptionHandler",
            "B": "@ControllerAdvice",
            "C": "@ErrorConfig",
            "D": "@GlobalHandler"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Exception Translation' in Hibernate or Spring Data?",
        "options": {
            "A": "Translating error messages into different languages",
            "B": "Converting low-level technology-specific exceptions (like SQLException) into high-level, consistent DataAccessExceptions",
            "C": "Changing the stack trace format",
            "D": "Encrypting the error logs"
        },
        "answer": "B"
    },
    {
        "question": "Which JVM error is thrown when the 'Permanent Generation' or 'Metaspace' is full?",
        "options": {
            "A": "StackOverflowError",
            "B": "OutOfMemoryError: Metaspace",
            "C": "MemoryLeakError",
            "D": "ClassFormatError"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'SLF4J' in enterprise exception logging?",
        "options": {
            "A": "It is a log storage database",
            "B": "A logging facade that allows you to plug in various logging frameworks (Logback, Log4j) without changing code",
            "C": "A tool to find bugs",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Business Exception' vs a 'Technical Exception'?",
        "options": {
            "A": "There is no difference",
            "B": "Business exceptions represent violations of domain rules (e.g., InsufficientFunds); Technical exceptions represent infrastructure failures",
            "C": "Technical exceptions are always checked",
            "D": "Business exceptions are thrown by the CEO"
        },
        "answer": "B"
    },
    {
        "question": "Which class should you extend for an exception that represents a 'Logic Error' (e.g., passing an invalid argument)?",
        "options": {
            "A": "Exception",
            "B": "RuntimeException",
            "C": "Error",
            "D": "Throwable"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Try' type in functional libraries like Vavr?",
        "options": {
            "A": "A replacement for the try-catch block that represents a computation that may either result in an exception or a value",
            "B": "A type of unit test",
            "C": "A loop structure",
            "D": "A database connection"
        },
        "answer": "A"
    },
    {
        "question": "Which exception is thrown if you attempt to use an Optional.get() when no value is present?",
        "options": {
            "A": "NullPointerException",
            "B": "NoSuchElementException",
            "C": "IllegalStateException",
            "D": "OptionalEmptyException"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'MDC' (Mapped Diagnostic Context) in logging exceptions?",
        "options": {
            "A": "To speed up the logs",
            "B": "To add contextual information (like UserID or TransactionID) to every log entry automatically",
            "C": "To encrypt the logs",
            "D": "To delete old logs"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Fatal' error logging?",
        "options": {
            "A": "Logging every minor bug",
            "B": "The highest logging level, indicating a failure that prevents the application (or a major component) from continuing",
            "C": "Logging to a physical printer",
            "D": "A security scan result"
        },
        "answer": "B"
    },
    {
        "question": "Which Spring annotation handles an exception within a 'single' Controller class?",
        "options": {
            "A": "@ControllerAdvice",
            "B": "@ExceptionHandler",
            "C": "@Catch",
            "D": "@ResponseStatus"
        },
        "answer": "B"
    },
    {
        "question": "What does 'ResponseStatusException' provide in Spring Boot?",
        "options": {
            "A": "A way to restart the server",
            "B": "A programmatic way to return specific HTTP status codes and reasons when an error occurs",
            "C": "A performance report",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is the benefit of 'Log Aggregation' (e.g., ELK Stack) for exception handling?",
        "options": {
            "A": "It makes the code run faster",
            "B": "It centralizes logs from many microservices into one searchable dashboard to find errors quickly",
            "C": "It fixes the bugs automatically",
            "D": "It reduces the size of the application"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is a typical 'Infrastructure' exception?",
        "options": {
            "A": "UserNotFoundException",
            "B": "ConnectException",
            "C": "InvalidOrderException",
            "D": "AccessDeniedException"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Bulkhead' pattern in resilience engineering (Hystrix/Resilience4j)?",
        "options": {
            "A": "Adding more memory to the server",
            "B": "Isolating elements of an application into pools so that if one fails, the others continue to function",
            "C": "A type of database sharding",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Circuit Breaker' state 'Open'?",
        "options": {
            "A": "The application is running normally",
            "B": "The application is failing, and the breaker is 'tripped'—immediately failing requests to prevent system overload",
            "C": "The database is open for business",
            "D": "A performance test result"
        },
        "answer": "B"
    },
    {
        "question": "Which Java 8 feature can be used to avoid NullPointerExceptions by design?",
        "options": {
            "A": "Streams",
            "B": "Optional<T>",
            "C": "Default Methods",
            "D": "Method References"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Throwable.getSuppressed()' specifically used for?",
        "options": {
            "A": "To get ignored errors",
            "B": "To retrieve exceptions that were suppressed during a try-with-resources auto-close",
            "C": "To find hidden bugs",
            "D": "To get the cause of the error"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is a common 'Reflection' related checked exception?",
        "options": {
            "A": "NullPointerException",
            "B": "NoSuchMethodException",
            "C": "ArithmeticException",
            "D": "ClassCastException"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Exception masking'?",
        "options": {
            "A": "Hiding the error from the developer",
            "B": "When an exception in a catch or finally block is thrown, hiding the original exception that occurred in the try block",
            "C": "A type of encryption",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Error Boundaries' in modern UI frameworks (relevant for VerifiHire UI)?",
        "options": {
            "A": "To stop the user from typing",
            "B": "To catch JavaScript errors in the component tree and display a fallback UI instead of crashing the whole app",
            "C": "To check for syntax errors",
            "D": "To manage the database"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Structured Logging'?",
        "options": {
            "A": "Logging in a straight line",
            "B": "Logging data in a machine-readable format (like JSON) so it can be easily parsed by analytics tools",
            "C": "A type of unit test",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "Which exception is thrown by the JVM if the 'main' method is not found?",
        "options": {
            "A": "NoSuchMethodError",
            "B": "ClassNotFoundException",
            "C": "MainNotFoundException",
            "D": "RuntimeException"
        },
        "answer": "A"
    },
    {
        "question": "What is the 'Global Exception Handler' in a Spring Boot application?",
        "options": {
            "A": "A single class annotated with @ControllerAdvice to handle all app-wide exceptions in one place",
            "B": "A person in charge of bugs",
            "C": "A cloud service",
            "D": "A type of sharding"
        },
        "answer": "A"
    },
    {
        "question": "How do you handle an InterruptedException correctly?",
        "options": {
            "A": "Ignore it",
            "B": "Catch it, and optionally restore the interrupted status by calling Thread.currentThread().interrupt()",
            "C": "Throw a RuntimeException",
            "D": "Stop the whole application"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Error code' mapping?",
        "options": {
            "A": "Associating every exception with a unique code (e.g., ERR-102) for easier troubleshooting and documentation",
            "B": "A type of encryption",
            "C": "A performance metric",
            "D": "A security scan"
        },
        "answer": "A"
    },
    {
        "question": "Which of these is a typical 'Database' checked exception?",
        "options": {
            "A": "SQLException",
            "B": "NullPointerException",
            "C": "ArrayIndexOutOfBoundsException",
            "D": "IllegalArgumentException"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Log rotation'?",
        "options": {
            "A": "Turning the logs upside down",
            "B": "The practice of archiving old log files and starting new ones to prevent disk space issues",
            "C": "A type of sharding",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Async' exception handling?",
        "options": {
            "A": "Handling errors that occur in background threads or CompletableFutures",
            "B": "Handling errors faster",
            "C": "A type of sharding",
            "D": "A security scanner"
        },
        "answer": "A"
    },
    {
        "question": "Which method in CompletableFuture is used to handle exceptions in a pipeline?",
        "options": {
            "A": "exceptionally()",
            "B": "handle()",
            "C": "Both A and B",
            "D": "catchError()"
        },
        "answer": "C"
    },
    {
        "question": "What is the purpose of 'Thread.setUncaughtExceptionHandler()'?",
        "options": {
            "A": "To prevent threads from failing",
            "B": "To set a custom handler that runs whenever a specific thread dies due to an uncaught exception",
            "C": "To log the thread name",
            "D": "To restart the thread"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Correlation ID'?",
        "options": {
            "A": "A unique ID passed through microservices to track a single request's journey and its associated logs/errors",
            "B": "A type of sharding",
            "C": "A security key",
            "D": "A performance metric"
        },
        "answer": "A"
    },
    {
        "question": "Which logging framework is the successor to Log4j 1.x and is natively integrated with SLF4J?",
        "options": {
            "A": "Logback",
            "B": "Console",
            "C": "System.out",
            "D": "PrintStream"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Exception Sanitization'?",
        "options": {
            "A": "Cleaning the logs",
            "B": "Stripping sensitive info (passwords, PII) from exceptions before they are sent to the client or logs",
            "C": "Fixing the code",
            "D": "A performance test"
        },
        "answer": "B"
    },
    {
        "question": "Which exception is thrown if you try to use an invalid URI?",
        "options": {
            "A": "URISyntaxException",
            "B": "IOException",
            "C": "NetworkException",
            "D": "MalformedURLException"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Retrying' as a resilience strategy?",
        "options": {
            "A": "Deleting the error and trying again",
            "B": "Automatically attempting a failed operation (like a network call) again after a brief delay",
            "C": "Asking the user to try again",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "Which Spring Data exception occurs when you try to save an object with a duplicate primary key?",
        "options": {
            "A": "DataIntegrityViolationException",
            "B": "SQLException",
            "C": "NullPointerException",
            "D": "DatabaseError"
        },
        "answer": "A"
    },
    {
        "question": "What is the 'Fail-Safe' pattern?",
        "options": {
            "A": "Ensuring the application continues with reduced functionality instead of crashing on error",
            "B": "Ensuring the app never fails",
            "C": "A type of sharding",
            "D": "A security scanner"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Idempotency' in the context of retrying after an exception?",
        "options": {
            "A": "Ensuring that performing the same operation multiple times has the same effect as doing it once (critical for safe retries)",
            "B": "The speed of the retry",
            "C": "The frequency of the error",
            "D": "A type of sharding"
        },
        "answer": "A"
    },
    {
        "question": "Which exception is thrown when a security violation is detected by the SecurityManager?",
        "options": {
            "A": "SecurityException",
            "B": "AccessDeniedException",
            "C": "IllegalAccessException",
            "D": "RuntimeException"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Backoff' strategy in retries?",
        "options": {
            "A": "Giving up immediately",
            "B": "Increasing the wait time between successive retry attempts (e.g., Exponential Backoff)",
            "C": "A performance test",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Jitter' in a retry strategy?",
        "options": {
            "A": "Randomly varying the backoff time to prevent many clients from retrying at the exact same moment (Thundering Herd)",
            "B": "A bug in the timer",
            "C": "A type of sharding",
            "D": "A performance metric"
        },
        "answer": "A"
    },
    {
        "question": "Which interface in Spring is used to customize the error page (like 404/500)?",
        "options": {
            "A": "ErrorController",
            "B": "ViewController",
            "C": "ExceptionHandler",
            "D": "PageMapper"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Log Injection' security vulnerability?",
        "options": {
            "A": "Injecting data into the logs to confuse or exploit log-parsing tools",
            "B": "Injecting code into the app via logs",
            "C": "A performance metric",
            "D": "A type of sharding"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of 'Throwable.getStackTrace()?'",
        "options": {
            "A": "To get the error message",
            "B": "To access the array of stack frames programmatically for logging or analysis",
            "C": "To print the code",
            "D": "To delete the history"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 3: Exception handling should prioritize _____ over _____.",
        "options": {
            "A": "Clarity over silence",
            "B": "Speed over safety",
            "C": "Silence over clarity",
            "D": "Complexity over simplicity"
        },
        "answer": "A"
    },
    {
        "question": "What happens if an exception is thrown inside a 'static initializer' block?",
        "options": {
            "A": "The class fails to load, and ExceptionInInitializerError is thrown",
            "B": "The program ignores it",
            "C": "The JVM restarts",
            "D": "The static block is skipped"
        },
        "answer": "A"
    },
    {
        "question": "Which of the following is an example of the 'Destructive Wrapping' anti-pattern?",
        "options": {
            "A": "Catching an exception and throwing a new one without passing the original as a cause",
            "B": "Catching every exception",
            "C": "Logging the exception twice",
            "D": "Using a custom exception class"
        },
        "answer": "A"
    },
    {
        "question": "What is the danger of 'Log and Throw' (Catching, logging, and then rethrowing the same exception)?",
        "options": {
            "A": "It causes a memory leak",
            "B": "It results in duplicate log entries for a single error as it moves up the call stack",
            "C": "The exception disappears",
            "D": "The program runs slower"
        },
        "answer": "B"
    },
    {
        "question": "Which exception is thrown when an application tries to access a field or call a method of an object that no longer exists in a thread-safe way?",
        "options": {
            "A": "IllegalMonitorStateException",
            "B": "ConcurrentModificationException",
            "C": "NullPointerException",
            "D": "StaleObjectStateException"
        },
        "answer": "A"
    },
    {
        "question": "What is the 'Exception Shielding' pattern used for in Web Services?",
        "options": {
            "A": "To block all errors",
            "B": "To prevent internal technical details (like stack traces) from being exposed to the client by sanitizing them",
            "C": "To encrypt the server",
            "D": "To speed up the network"
        },
        "answer": "B"
    },
    {
        "question": "In a 'ScheduledExecutorService', what happens if a task throws an uncaught exception?",
        "options": {
            "A": "The executor stops",
            "B": "The specific task stops executing and won't run again, but the executor stays alive",
            "C": "The JVM crashes",
            "D": "The exception is printed to System.out automatically"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Partial Success' exception handling?",
        "options": {
            "A": "When some items in a batch process succeed but others fail, requiring a custom result object instead of a single exception",
            "B": "Failing half-way through a method",
            "C": "Ignoring errors in the UI",
            "D": "A type of unit test"
        },
        "answer": "A"
    },
    {
        "question": "Which error occurs when the JVM attempts to load a class but its bytecode is malformed or invalid?",
        "options": {
            "A": "ClassFormatError",
            "B": "VerifyError",
            "C": "NoClassDefFoundError",
            "D": "UnsupportedClassVersionError"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Softening' an exception?",
        "options": {
            "A": "Logging it gently",
            "B": "Catching a Checked exception and rethrowing it as an Unchecked exception to simplify method signatures",
            "C": "Deleting the error message",
            "D": "Reducing the priority of the error"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is a typical symptom of 'Thread Leak' caused by poor exception handling?",
        "options": {
            "A": "High CPU usage",
            "B": "OutOfMemoryError: unable to create new native thread",
            "C": "Database deadlock",
            "D": "Slow disk I/O"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Exception-Driven Development' anti-pattern?",
        "options": {
            "A": "Writing tests before code",
            "B": "Using exceptions for normal control flow logic (e.g., using a catch block to detect if a record exists)",
            "C": "Using only custom exceptions",
            "D": "Logging errors in JSON format"
        },
        "answer": "B"
    },
    {
        "question": "How does 'CompletableFuture.allOf()' handle exceptions from multiple futures?",
        "options": {
            "A": "It waits for all and returns a list of errors",
            "B": "It completes exceptionally as soon as any one of the futures fails",
            "C": "It ignores all failures",
            "D": "It restarts the failed futures"
        },
        "answer": "B"
    },
    {
        "question": "Which class in the 'java.lang.reflect' package wraps an exception thrown by an invoked method?",
        "options": {
            "A": "InvocationTargetException",
            "B": "ReflectionException",
            "C": "TargetException",
            "D": "UndeclaredThrowableException"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of the 'ThreadDeath' error?",
        "options": {
            "A": "To indicate the computer is off",
            "B": "A silent error thrown when Thread.stop() is called (now deprecated) to allow cleanup",
            "C": "To handle thread sleep",
            "D": "A security scan result"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Hierarchical Exception' design?",
        "options": {
            "A": "Creating a tree of domain-specific exceptions (e.g., PaymentException -> CreditCardException)",
            "B": "Catching only the Throwable class",
            "C": "Sorting exceptions by size",
            "D": "A type of database schema"
        },
        "answer": "A"
    },
    {
        "question": "Which error is thrown if the JVM cannot find the 'main' method or a static initializer fails?",
        "options": {
            "A": "NoSuchMethodError",
            "B": "ExceptionInInitializerError",
            "C": "LinkageError",
            "D": "VerifyError"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Exception masking' in the context of return values?",
        "options": {
            "A": "Using a return statement in a finally block, which can cause any exception thrown in try/catch to be ignored",
            "B": "Encrypting the return value",
            "C": "Returning a null on error",
            "D": "A performance metric"
        },
        "answer": "A"
    },
    {
        "question": "Which of these is a valid way to 'ignore' a specific exception type using Java 8 Streams?",
        "options": {
            "A": "There is no built-in way; you must use a try-catch inside the map function",
            "B": "stream.ignore(Exception.class)",
            "C": "stream.catch(e -> ...)",
            "D": "stream.filter(Objects::nonNull)"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Double-Logging'?",
        "options": {
            "A": "Logging to two files",
            "B": "Logging an exception at the point it is thrown AND at the point it is caught",
            "C": "A security feature",
            "D": "Logging in two languages"
        },
        "answer": "B"
    },
    {
        "question": "Which exception is thrown when an application attempts to access a member of a class but the class has changed incompatibly?",
        "options": {
            "A": "IncompatibleClassChangeError",
            "B": "NoSuchFieldError",
            "C": "AbstractMethodError",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "What is the 'Global Error Handler' for a React application (VerifiHire UI)?",
        "options": {
            "A": "window.onerror",
            "B": "Error Boundaries",
            "C": "try-catch on every function",
            "D": "Redux logger"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Backpressure' handling in the context of high-volume error streams?",
        "options": {
            "A": "Ignoring errors to keep speed",
            "B": "Slowing down the source of data when the error handling system is overwhelmed",
            "C": "Increasing CPU speed",
            "D": "A type of sharding"
        },
        "answer": "B"
    },
    {
        "question": "Which error is thrown if a thread tries to wait on an object's monitor without owning it?",
        "options": {
            "A": "IllegalMonitorStateException",
            "B": "IllegalThreadStateException",
            "C": "InterruptedException",
            "D": "SynchronizationError"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Exception bloating'?",
        "options": {
            "A": "Exceptions that are too large in size",
            "B": "An anti-pattern where too much irrelevant data is added to the exception message or context",
            "C": "Having too many catch blocks",
            "D": "A memory management error"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Sentinel Value' pattern as an alternative to exceptions?",
        "options": {
            "A": "Returning a special value (like -1 or null) to indicate an error instead of throwing an exception",
            "B": "Using a guard dog",
            "C": "A security scan",
            "D": "A type of sharding"
        },
        "answer": "A"
    },
    {
        "question": "Which Spring exception is the parent of all data-related exceptions?",
        "options": {
            "A": "DataAccessException",
            "B": "PersistenceException",
            "C": "DatabaseError",
            "D": "SQLException"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Checked-to-Unchecked' wrapping?",
        "options": {
            "A": "Wrapping a checked exception inside a RuntimeException to avoid mandatory 'throws' declarations",
            "B": "The opposite of softening",
            "C": "A security attack",
            "D": "A performance metric"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Log Forging'?",
        "options": {
            "A": "Making fake logs",
            "B": "A vulnerability where unvalidated user input is written to logs, allowing attackers to inject fake entries",
            "C": "A performance test",
            "D": "A type of sharding"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Exception.getOurStackTrace()' (private method)?",
        "options": {
            "A": "To get the stack trace for the current thread specifically",
            "B": "To hide the stack trace",
            "C": "To print the trace",
            "D": "To delete the trace"
        },
        "answer": "A"
    },
    {
        "question": "Which of these is a symptom of a 'Recursive Exception' (Exception in exception handling)?",
        "options": {
            "A": "StackOverflowError",
            "B": "The program hangs indefinitely",
            "C": "Multiple identical error logs",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Error-free' programming philosophy?",
        "options": {
            "A": "Writing code without bugs",
            "B": "Designing systems to be robust enough that errors are handled at the lowest possible level without user impact",
            "C": "A type of sharding",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Checked Exception' debate in modern Java?",
        "options": {
            "A": "Whether they should be replaced by Unchecked exceptions for cleaner code",
            "B": "Whether they should be faster",
            "C": "Whether they should be private",
            "D": "Whether they should use more memory"
        },
        "answer": "A"
    },
    {
        "question": "Which exception is thrown when an operation is performed on a closed resource?",
        "options": {
            "A": "IllegalStateException",
            "B": "IOException",
            "C": "ResourceClosedException",
            "D": "Both A and B (context dependent)"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Contextual' exception handling?",
        "options": {
            "A": "Passing extra metadata (like current state) within the exception object for better debugging",
            "B": "A type of sharding",
            "C": "A security scan",
            "D": "A performance report"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Exception density'?",
        "options": {
            "A": "The number of exceptions per line of code",
            "B": "How heavy the error is",
            "C": "A performance metric",
            "D": "A type of sharding"
        },
        "answer": "A"
    },
    {
        "question": "Which of these is a common 'Reflection' related unchecked exception?",
        "options": {
            "A": "MalformedParametersException",
            "B": "NoSuchMethodException",
            "C": "ClassNotFoundException",
            "D": "IllegalAccessException"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Exception tunneling'?",
        "options": {
            "A": "Passing an exception through a layer that doesn't expect it (e.g., using a RuntimeException to bypass an interface restriction)",
            "B": "A type of VPN",
            "C": "A security attack",
            "D": "A performance metric"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Exception locality'?",
        "options": {
            "A": "Handling the exception as close to the source as possible",
            "B": "A type of database sharding",
            "C": "A security scan",
            "D": "A performance report"
        },
        "answer": "A"
    },
    {
        "question": "Which error is thrown when the JVM is broken or has run out of resources necessary for it to continue operating?",
        "options": {
            "A": "VirtualMachineError",
            "B": "InternalError",
            "C": "UnknownError",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Exception Silencing'?",
        "options": {
            "A": "Catching and doing nothing (Swallowing)",
            "B": "Muting the computer",
            "C": "Deleting the logs",
            "D": "A performance metric"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Exception reification'?",
        "options": {
            "A": "Making the exception real",
            "B": "Turning an exceptional condition into a first-class data object (common in functional programming)",
            "C": "A type of sharding",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is a typical 'Concurrency' related runtime exception?",
        "options": {
            "A": "RejectedExecutionException",
            "B": "InterruptedException",
            "C": "ExecutionException",
            "D": "CancellationException"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Exception enrichment'?",
        "options": {
            "A": "Adding more data to an exception as it bubles up through different layers",
            "B": "Making the error sound better",
            "C": "A performance test",
            "D": "A type of unit test"
        },
        "answer": "A"
    },
    {
        "question": "Which exception is thrown when an operation is requested that is not supported by the object?",
        "options": {
            "A": "UnsupportedOperationException",
            "B": "IllegalStateException",
            "C": "NotImplementedException",
            "D": "RuntimeException"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Exception pruning'?",
        "options": {
            "A": "Reducing the size of the stack trace to only show relevant frames",
            "B": "Deleting old exceptions",
            "C": "A performance metric",
            "D": "A security scan"
        },
        "answer": "A"
    },
    {
        "question": "Which error is thrown when a thread is not in an appropriate state for the requested operation?",
        "options": {
            "A": "IllegalThreadStateException",
            "B": "ThreadDeath",
            "C": "InterruptedException",
            "D": "IllegalStateException"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Exception filtering' in logging?",
        "options": {
            "A": "Removing sensitive or redundant errors from the log stream",
            "B": "A security scan",
            "C": "A type of sharding",
            "D": "A performance metric"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Exception bubbling'?",
        "options": {
            "A": "The process of an exception moving up the call stack to find a handler",
            "B": "An error in the UI",
            "C": "A type of memory leak",
            "D": "A performance test"
        },
        "answer": "A"
    },
    {
        "question": "Which of these is a Checked Exception?",
        "options": {
            "A": "BrokenBarrierException",
            "B": "RejectedExecutionException",
            "C": "CancellationException",
            "D": "CompletionException"
        },
        "answer": "A"
    },
    {
        "question": "Final question: What is the primary purpose of Exception Handling in the VerifiHire AI platform?",
        "options": {
            "A": "To ensure candidates have a seamless experience even when unexpected system errors occur",
            "B": "To make the platform faster",
            "C": "To hide bugs from the team",
            "D": "To replace the database"
        },
        "answer": "A",

    },
    {
        "question": "In a Microservices architecture, which pattern is used to prevent a cascade of 'TimeoutExceptions' when a downstream service is struggling?",
        "options": {
            "A": "Circuit Breaker",
            "B": "Bulkhead",
            "C": "Retry with Exponential Backoff",
            "D": "Sidecar Proxy"
        },
        "answer": "A"
    },
    {
        "question": "When designing a REST API for VerifiHire AI, what is the best practice for communicating a 'ValidationException' to the client?",
        "options": {
            "A": "Return a 500 Internal Server Error with the full stack trace",
            "B": "Return a 400 Bad Request with a structured JSON body detailing the specific field errors",
            "C": "Return a 200 OK but with an 'error' flag in the body",
            "D": "Close the connection immediately"
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
    skill = "ExceptionHandling"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
