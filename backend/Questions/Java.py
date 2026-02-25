from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
  {
    "question": "Which of the following is the entry point for a Java application?",
    "options": {
      "A": "public void start()",
      "B": "public static void main(String[] args)",
      "C": "public void main(String args)",
      "D": "static run()"
    },
    "answer": "B"
  },
  {
    "question": "True or False: A Java source file must have the same name as the public class it contains.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the size of the int data type in Java?",
    "options": {
      "A": "16-bit",
      "B": "32-bit",
      "C": "64-bit",
      "D": "8-bit"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO valid ways to declare an array in Java:",
    "options": {
      "A": "int arr[] = new int[5];",
      "B": "int arr = new int[5];",
      "C": "int[] arr = {1, 2, 3};",
      "D": "array int arr = [1, 2, 3];"
    },
    "answer": "A, C"
  },
  {
    "question": "Which component is responsible for running Java bytecode?",
    "options": {
      "A": "JDK",
      "B": "JRE",
      "C": "JVM",
      "D": "JIT"
    },
    "answer": "C"
  },
  {
    "question": "Which keyword prevents a class from being inherited?",
    "options": {
      "A": "static",
      "B": "abstract",
      "C": "final",
      "D": "private"
    },
    "answer": "C"
  },
  {
    "question": "Which operator compares two objects for equality in content?",
    "options": {
      "A": "==",
      "B": "is",
      "C": ".equals()",
      "D": "==="
    },
    "answer": "C"
  },
  {
    "question": "Which collection class allows unique elements and does NOT maintain order?",
    "options": {
      "A": "ArrayList",
      "B": "LinkedList",
      "C": "HashSet",
      "D": "TreeMap"
    },
    "answer": "C"
  },
  {
    "question": "Which exception is thrown when an array is accessed with an invalid index?",
    "options": {
      "A": "IndexNotFoundException",
      "B": "ArrayIndexOutOfBoundsException",
      "C": "ArrayInvalidException",
      "D": "NullPointerException"
    },
    "answer": "B"
  },
  {
    "question": "Which design pattern ensures a class has only one instance?",
    "options": {
      "A": "Factory",
      "B": "Singleton",
      "C": "Observer",
      "D": "Strategy"
    },
    "answer": "B"
  },
  {
    "question": "What is the result of 1.0 / 0.0 in Java?",
    "options": {
      "A": "ArithmeticException",
      "B": "Infinity",
      "C": "NaN",
      "D": "0.0"
    },
    "answer": "B"
  },
  {
    "question": "Which keyword is used to prevent a variable from being serialized?",
    "options": {
      "A": "volatile",
      "B": "transient",
      "C": "final",
      "D": "static"
    },
    "answer": "B"
  },
  {
    "question": "Which interface is used for a function that takes one argument and returns a result?",
    "options": {
      "A": "Consumer",
      "B": "Supplier",
      "C": "Function",
      "D": "Predicate"
    },
    "answer": "C"
  },
  {
    "question": "True or False: Java supports 'Pass-by-Reference' for objects.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which collection should be used if you need to maintain elements in their natural sorted order?",
    "options": {
      "A": "HashSet",
      "B": "LinkedHashSet",
      "C": "TreeSet",
      "D": "ArrayList"
    },
    "answer": "C"
  },
  {
    "question": "Which keyword is used to prevent a variable from being serialized?",
    "options": {
      "A": "volatile",
      "B": "transient",
      "C": "final",
      "D": "static"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Inner classes can access private members of the outer class.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO methods are used to control thread execution?",
    "options": {
      "A": "sleep()",
      "B": "yield()",
      "C": "stop()",
      "D": "exit()"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: The super() call must be the first statement in a constructor.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO interfaces are used for sorting objects?",
    "options": {
      "A": "Comparable",
      "B": "Comparator",
      "C": "Sortable",
      "D": "Ordered"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: In Java 8, interfaces can have static methods.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are valid types for a switch statement expression?",
    "options": {
      "A": "String",
      "B": "float",
      "C": "enum",
      "D": "long"
    },
    "answer": "A, C"
  },
  {
    "question": "True or False: Anonymous inner classes can have a constructor.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO are valid ways to create a Thread?",
    "options": {
      "A": "Extending Thread class",
      "B": "Implementing Runnable interface",
      "C": "Implementing Callable interface",
      "D": "Extending Process class"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: Garbage collection happens in the Stack memory.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO are used to implement abstraction?",
    "options": {
      "A": "Interface",
      "B": "Abstract Class",
      "C": "Encapsulation",
      "D": "Inheritance"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: You can overload the main method.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are part of the java.lang package?",
    "options": {
      "A": "String",
      "B": "Math",
      "C": "ArrayList",
      "D": "Scanner"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: this() and super() can be used together in the same constructor.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO are features of the JVM?",
    "options": {
      "A": "Garbage Collection",
      "B": "Platform Independence",
      "C": "Code Compilation to Machine Code",
      "D": "Visual GUI Design"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: A class declared as final cannot be instantiated.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO methods are used in the Iterator interface?",
    "options": {
      "A": "hasNext()",
      "B": "next()",
      "C": "get()",
      "D": "size()"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: The finalize() method is guaranteed to be called before an object is garbage collected.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO can be used to handle multiple conditions in Java?",
    "options": {
      "A": "if-else if",
      "B": "switch",
      "C": "for",
      "D": "while"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: Java is a strictly 'Compiled' language, never interpreted.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which of these is a thread-safe implementation of Map that allows concurrent access?",
    "options": {
      "A": "HashMap",
      "B": "ConcurrentHashMap",
      "C": "TreeMap",
      "D": "Hashtable"
    },
    "answer": "B"
  },
  {
    "question": "True or False: The 'PermGen' space was replaced by 'Metaspace' in Java 8.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are used to measure the execution time of a code snippet?",
    "options": {
      "A": "System.currentTimeMillis()",
      "B": "System.nanoTime()",
      "C": "System.getClock()",
      "D": "System.time()"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: A WeakHashMap entry is automatically removed when its key is no longer in ordinary use.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO methods are part of the Deque interface?",
    "options": {
      "A": "push()",
      "B": "pop()",
      "C": "enqueue()",
      "D": "dequeue()"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: String.intern() returns a canonical representation for the string object.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are valid types of Garbage Collectors in Java?",
    "options": {
      "A": "G1 (Garbage First)",
      "B": "ZGC",
      "C": "ABC",
      "D": "XGC"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: In Java, an array is an object.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the result of 1.0 / 0.0 in Java?",
    "options": {
      "A": "ArithmeticException",
      "B": "Infinity",
      "C": "NaN",
      "D": "0.0"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO keywords are used for writing thread-safe code without using synchronized?",
    "options": {
      "A": "volatile",
      "B": "atomic (via Classes)",
      "C": "static",
      "D": "native"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: The PriorityQueue allows null elements.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO are part of the java.util.concurrent package?",
    "options": {
      "A": "ExecutorService",
      "B": "CountDownLatch",
      "C": "ArrayList",
      "D": "HashSet"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: A static nested class can access non-static members of the outer class.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which interface is used to make a class 'sortable' by a custom attribute?",
    "options": {
      "A": "Comparable",
      "B": "Comparator",
      "C": "Sortable",
      "D": "List"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Double.NaN == Double.NaN evaluates to true.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO are primitive types?",
    "options": {
      "A": "byte",
      "B": "short",
      "C": "String",
      "D": "Integer"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: The default constructor is only provided if no other constructor is defined.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO methods are used to prevent a thread from running for a specific period?",
    "options": {
      "A": "sleep()",
      "B": "wait()",
      "C": "stop()",
      "D": "interrupt()"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: Enumeration is faster than Iterator but lacks the remove() method.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO describe the behavior of a HashSet?",
    "options": {
      "A": "It permits one null element.",
      "B": "It maintains insertion order.",
      "C": "It uses a HashMap internally.",
      "D": "It is synchronized."
    },
    "answer": "A, C"
  },
  {
    "question": "True or False: Local Variable Type Inference (var) can be used for method parameters.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO classes are used for reading text files efficiently?",
    "options": {
      "A": "BufferedReader",
      "B": "Scanner",
      "C": "FileOutputStream",
      "D": "DataOutputStream"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: System.exit(0) will prevent the finally block from executing.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are types of nested classes?",
    "options": {
      "A": "Inner Class",
      "B": "Static Nested Class",
      "C": "External Class",
      "D": "Side Class"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: A Lambda expression can access non-final variables in the enclosing scope.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which class is the superclass of all classes that represent an input stream of bytes?",
    "options": {
      "A": "Reader",
      "B": "InputStream",
      "C": "File",
      "D": "Filter"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Serializable is a marker interface with no methods.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are used for character-based I/O?",
    "options": {
      "A": "Reader",
      "B": "Writer",
      "C": "InputStream",
      "D": "OutputStream"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: The Socket class is used to implement a server-side connection.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO are advantages of using NIO (New I/O)?",
    "options": {
      "A": "Non-blocking I/O",
      "B": "Buffers and Channels",
      "C": "Simpler code than standard I/O",
      "D": "Automatic file compression"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: 'Composition over Inheritance' suggests using objects with defined behaviors rather than inheriting from a base class.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are 'Creational' patterns?",
    "options": {
      "A": "Prototype",
      "B": "Abstract Factory",
      "C": "Flyweight",
      "D": "Decorator"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: The 'Dependency Inversion' principle suggests that high-level modules should depend on low-level modules.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which pattern is used to attach additional responsibilities to an object dynamically?",
    "options": {
      "A": "Facade",
      "B": "Decorator",
      "C": "Bridge",
      "D": "Proxy"
    },
    "answer": "B"
  },
  {
    "question": "True or False: A 'Sealed' class can be used to implement a restricted class hierarchy.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are common types of Dependency Injection?",
    "options": {
      "A": "Constructor Injection",
      "B": "Setter Injection",
      "C": "Variable Extraction",
      "D": "Method Extension"
    },
    "answer": "A, B"
  },
  {
    "question": "Which class wraps an OutputStream to write primitive Java data types in a portable way?",
    "options": {
      "A": "DataOutputStream",
      "B": "BufferedOutputStream",
      "C": "PrintStream",
      "D": "PrintWriter"
    },
    "answer": "A"
  },
  {
    "question": "True or False: The serialVersionUID is used during deserialization to verify class compatibility.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are methods of the File class?",
    "options": {
      "A": "exists()",
      "B": "createNewFile()",
      "C": "open()",
      "D": "read()"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: BufferedWriter is generally faster than FileWriter for large amounts of text.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO classes handle compressed data in the java.util.zip package?",
    "options": {
      "A": "ZipInputStream",
      "B": "ZipOutputStream",
      "C": "GzipReader",
      "D": "CompressStream"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: In Java, the Socket class uses a connectionless protocol (UDP) by default.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which method of the Scanner class checks if there is another line of input?",
    "options": {
      "A": "hasNext()",
      "B": "hasNextLine()",
      "C": "isNext()",
      "D": "checkNext()"
    },
    "answer": "B"
  },
  {
    "question": "True or False: The transient keyword can be applied to methods.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO are valid constructors for FileOutputStream?",
    "options": {
      "A": "FileOutputStream(String name)",
      "B": "FileOutputStream(File file, boolean append)",
      "C": "FileOutputStream(int bufferSize)",
      "D": "FileOutputStream(URL url)"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: A Pipe in Java NIO allows for two-way communication between two threads.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which class is best for reading a single character at a time from the console?",
    "options": {
      "A": "InputStreamReader",
      "B": "BufferedReader",
      "C": "DataInputStream",
      "D": "ObjectInputStream"
    },
    "answer": "A"
  },
  {
    "question": "True or False: The InetAddress class is used to represent an IP address.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are standard Streams provided by the System class?",
    "options": {
      "A": "System.in",
      "B": "System.err",
      "C": "System.log",
      "D": "System.input"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: Externalizable gives the programmer full control over the serialization process.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the primary purpose of the 'False Sharing' prevention in Java 8+ using the @Contended annotation?",
    "options": {
      "A": "To prevent multiple threads from accessing the same object.",
      "B": "To ensure variables reside on different cache lines to improve multi-core performance.",
      "C": "To force a variable to stay in the Stack memory.",
      "D": "To reduce the frequency of Minor GC cycles."
    },
    "answer": "B"
  },
  {
    "question": "In the context of Java Memory Model, what does 'Happens-Before' relationship guarantee?",
    "options": {
      "A": "That a thread will always execute before another.",
      "B": "Memory visibility of write operations to other read operations.",
      "C": "That the code will not throw a NullPointerException.",
      "D": "That the Garbage Collector will prioritize certain objects."
    },
    "answer": "B"
  },
  {
    "question": "Which Garbage Collector is designed for multi-terabyte heaps with pause times consistently under 1ms?",
    "options": {
      "A": "Parallel GC",
      "B": "CMS",
      "C": "ZGC",
      "D": "G1GC"
    },
    "answer": "C"
  },
  {
    "question": "True or False: A 'Strongly Reachable' object is eligible for garbage collection if the system runs out of memory.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO are functional interfaces introduced to handle primitive types specifically to avoid boxing/unboxing overhead?",
    "options": {
      "A": "IntPredicate",
      "B": "DoubleFunction",
      "C": "PrimitiveConsumer",
      "D": "NumberSupplier"
    },
    "answer": "A, B"
  },
  {
    "question": "What is the result of applying 'flatMap' on a Stream of Streams?",
    "options": {
      "A": "It returns a Stream of Lists.",
      "B": "It flattens the nested structure into a single linear Stream.",
      "C": "It filters out null streams.",
      "D": "It executes the streams in parallel."
    },
    "answer": "B"
  },
  {
    "question": "True or False: In Java 21, Virtual Threads are managed by the Operating System scheduler directly.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO methods in the Thread class are considered 'Deadly' and are deprecated because they can leave monitors in an inconsistent state?",
    "options": {
      "A": "stop()",
      "B": "suspend()",
      "C": "interrupt()",
      "D": "join()"
    },
    "answer": "A, B"
  },
  {
    "question": "What is the 'Diamond Problem' in Java, and how is it resolved?",
    "options": {
      "A": "Ambiguity in multiple inheritance of classes; resolved by private constructors.",
      "B": "Ambiguity in multiple inheritance of default methods in interfaces; resolved by overriding the method.",
      "C": "Conflict between static and instance variables; resolved by the 'this' keyword.",
      "D": "Memory leak in nested loops; resolved by the JIT compiler."
    },
    "answer": "B"
  },
  {
    "question": "Which TWO are valid use cases for the 'VarHandle' API introduced in Java 9?",
    "options": {
      "A": "Atomic updates to fields without using AtomicFieldUpdater.",
      "B": "Low-level memory fencing operations.",
      "C": "Direct hardware register access.",
      "D": "Replacing all 'public' modifiers."
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: The 'finally' block will execute even if the thread is killed via 'System.exit(0)'.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'SoftReference' class in Java?",
    "options": {
      "A": "To prevent an object from ever being collected.",
      "B": "To keep an object in memory until the JVM absolutely needs memory for other tasks.",
      "C": "To speed up the hashing of the object.",
      "D": "To allow multiple threads to edit a string."
    },
    "answer": "B"
  },
  {
    "question": "Which TWO properties define a 'Race Condition'?",
    "options": {
      "A": "Multiple threads accessing shared data.",
      "B": "At least one thread performing a write operation.",
      "C": "The use of the 'volatile' keyword.",
      "D": "The presence of a 'finally' block."
    },
    "answer": "A, B"
  },
  {
    "question": "What does 'T' represent in the signature 'List<? super T>'?",
    "options": {
      "A": "The list can hold T or any subclass of T.",
      "B": "The list can hold T or any superclass of T.",
      "C": "The list is read-only.",
      "D": "The list can only hold Object types."
    },
    "answer": "B"
  },
  {
    "question": "True or False: An 'EnumMap' is generally faster than a 'HashMap' when the keys are enum constants.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO of these are 'Lock-Free' data structures in the concurrent package?",
    "options": {
      "A": "ConcurrentLinkedQueue",
      "B": "ConcurrentSkipListMap",
      "C": "Collections.synchronizedList",
      "D": "LinkedBlockingQueue"
    },
    "answer": "A, B"
  },
  {
    "question": "What is 'Escape Analysis' performed by the JIT compiler?",
    "options": {
      "A": "A check to see if a thread can exit a loop safely.",
      "B": "Determining if an object's scope is limited to a method, allowing for stack allocation instead of heap.",
      "C": "Identifying code that can be bypassed during execution.",
      "D": "A security scan for SQL injection."
    },
    "answer": "B"
  },
  {
    "question": "Which keyword is used in Java 21 Pattern Matching to add a boolean condition to a 'case' label?",
    "options": {
      "A": "where",
      "B": "when",
      "C": "if",
      "D": "and"
    },
    "answer": "B"
  },
  {
    "question": "True or False: CyclicBarrier can be reused after the waiting threads are released, while CountDownLatch cannot.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO methods are required to implement a custom 'Spliterator' for a Stream?",
    "options": {
      "A": "tryAdvance()",
      "B": "trySplit()",
      "C": "parallelize()",
      "D": "merge()"
    },
    "answer": "A, B"
  },
  {
    "question": "Which JVM optimization technique replaces a method call with the actual body of the method to eliminate call overhead?",
    "options": {
      "A": "Loop Unrolling",
      "B": "Method Inlining",
      "C": "Dead Code Elimination",
      "D": "On-Stack Replacement"
    },
    "answer": "B"
  },
  {
    "question": "True or False: In Java 21, the 'Foreign Function & Memory API' allows Java code to interoperate with native code without using JNI headers.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the specific purpose of the 'Phaser' class in java.util.concurrent?",
    "options": {
      "A": "To handle encryption phases in networking.",
      "B": "To provide a reusable synchronization barrier that supports a variable number of parties.",
      "C": "To measure the execution time of different threads.",
      "D": "To replace the synchronized keyword in loops."
    },
    "answer": "B"
  },
  {
    "question": "Which TWO factors can trigger a 'Full GC' in the G1 Garbage Collector?",
    "options": {
      "A": "Humongous Allocation failures.",
      "B": "Metaspace exhaustion.",
      "C": "The Young Generation reaching 10% capacity.",
      "D": "Calling System.out.println()."
    },
    "answer": "A, B"
  },
  {
    "question": "What does 'Biased Locking' (deprecated in recent Java versions) attempt to optimize?",
    "options": {
      "A": "Locking contention between multiple CPUs.",
      "B": "Uncontended synchronization by assuming a monitor is acquired by the same thread repeatedly.",
      "C": "Recursive method calls.",
      "D": "String concatenation speed."
    },
    "answer": "B"
  },
  {
    "question": "True or False: A 'Record' component can be declared with an instance field that is not part of the record header.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO are features of the Java 'Vector API' (Incubating)?",
    "options": {
      "A": "Expressing vector computations that compile to optimal SIMD instructions.",
      "B": "Providing a thread-safe replacement for ArrayList.",
      "C": "Hardware-accelerated performance for data-parallel operations.",
      "D": "Automatic resizing of underlying arrays."
    },
    "answer": "A, C"
  },
  {
    "question": "What is the 'Stop-the-World' (STW) phase in Garbage Collection?",
    "options": {
      "A": "A phase where the JVM stops all application threads to safely perform GC operations.",
      "B": "A crash state that requires a server reboot.",
      "C": "The time it takes for the JIT compiler to warm up.",
      "D": "A security protocol for blocking network traffic."
    },
    "answer": "A"
  },
  {
    "question": "Which TWO interfaces must be implemented to create a custom 'Collector' for the Stream API?",
    "options": {
      "A": "Supplier",
      "B": "BiConsumer (as an accumulator)",
      "C": "Predicate",
      "D": "Comparator"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: Using 'volatile' on a reference object ensures the visibility of the object's internal fields to other threads.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is the role of a 'ServiceLoader' in Java Modules?",
    "options": {
      "A": "To automatically download JAR files from Maven.",
      "B": "To discover and load implementations of a specific interface at runtime without tight coupling.",
      "C": "To manage database connection pools.",
      "D": "To verify digital signatures of classes."
    },
    "answer": "B"
  },
  {
    "question": "Which command-line flag is used to enable 'Preview' features (like Scoped Values) in the JDK?",
    "options": {
      "A": "--enable-preview",
      "B": "-XX:PreviewFeatures=on",
      "C": "--allow-experimental",
      "D": "-Djava.preview=true"
    },
    "answer": "A"
  },
  {
    "question": "True or False: In the Java memory model, 'Final' fields can be modified via Reflection even after the constructor has finished.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are benefits of 'On-Stack Replacement' (OSR)?",
    "options": {
      "A": "Optimizing long-running loops while they are still executing.",
      "B": "Allowing the JVM to switch from interpreted to compiled code mid-execution.",
      "C": "Preventing StackOverflowErrors.",
      "D": "Storing large objects in the thread stack."
    },
    "answer": "A, B"
  },
  {
    "question": "What is the difference between 'CompletableFuture.supplyAsync()' and 'runAsync()'?",
    "options": {
      "A": "supplyAsync returns a value; runAsync returns Void.",
      "B": "supplyAsync is synchronous; runAsync is asynchronous.",
      "C": "runAsync uses a custom thread pool; supplyAsync does not.",
      "D": "There is no difference."
    },
    "answer": "A"
  },
  {
    "question": "Which TWO properties describe 'ThreadLocal' variables?",
    "options": {
      "A": "They provide a separate copy of a variable for each thread.",
      "B": "They can cause memory leaks if not properly removed after use.",
      "C": "They are shared across all threads in the same process.",
      "D": "They are only available in Virtual Threads."
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: A 'Default Method' in an interface can be overridden by a subclass.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'String Deduplication' in G1GC?",
    "options": {
      "A": "A process that combines identical String values in the heap to point to a single byte array.",
      "B": "A compiler optimization that removes duplicate variables.",
      "C": "A method to delete empty strings.",
      "D": "A database synchronization tool."
    },
    "answer": "A"
  },
  {
    "question": "Which TWO conditions are necessary for a 'Deadlock' to occur?",
    "options": {
      "A": "Mutual Exclusion",
      "B": "Circular Wait",
      "C": "Garbage Collection",
      "D": "High CPU usage"
    },
    "answer": "A, B"
  },
  {
    "question": "What is the primary benefit of using 'Scoped Values' (Java 21) over 'ThreadLocal'?",
    "options": {
      "A": "Immutable data sharing with less memory overhead, especially for millions of Virtual Threads.",
      "B": "They can be modified by any thread at any time.",
      "C": "They support primitive types directly.",
      "D": "They are faster for single-threaded applications."
    },
    "answer": "A"
  },
  {
    "question": "Which specific JVM area stores the runtime constant pool, field, and method data?",
    "options": {
      "A": "Stack",
      "B": "Heap",
      "C": "Method Area (Metaspace)",
      "D": "PC Register"
    },
    "answer": "C"
  },
  {
    "question": "True or False: In Java 21, a thread can be 'unmounted' from its carrier thread when it performs a blocking I/O operation.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are key characteristics of 'Atomic' variables in java.util.concurrent.atomic?",
    "options": {
      "A": "They use Compare-And-Swap (CAS) instructions.",
      "B": "They are always faster than synchronized blocks.",
      "C": "They provide lock-free thread safety for single variables.",
      "D": "They prevent all garbage collection of the wrapped value."
    },
    "answer": "A, C"
  },
  {
    "question": "What is the 'ABA problem' in lock-free programming, and how is it typically solved in Java?",
    "options": {
      "A": "A thread reads a value twice; solved by AtomicStampedReference.",
      "B": "A memory leak in loops; solved by System.gc().",
      "C": "An error in string concatenation; solved by StringBuilder.",
      "D": "A deadlock scenario; solved by reordering code."
    },
    "answer": "A"
  },
  {
    "question": "True or False: The 'double-checked locking' pattern for Singletons works correctly in Java 5+ only if the instance variable is marked 'volatile'.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO methods are part of the 'Flow' API introduced in Java 9 for Reactive Streams?",
    "options": {
      "A": "Publisher.subscribe()",
      "B": "Subscriber.onNext()",
      "C": "Processor.start()",
      "D": "Subscription.cancelAll()"
    },
    "answer": "A, B"
  },
  {
    "question": "What does the 'Native Memory Tracking' (NMT) tool help developers monitor?",
    "options": {
      "A": "Memory used by the JVM itself outside of the Java Heap.",
      "B": "The size of local variables on the Stack.",
      "C": "The number of active SQL connections.",
      "D": "The percentage of CPU utilized by Lambda expressions."
    },
    "answer": "A"
  },
  {
    "question": "Which TWO describe 'False Sharing' in high-concurrency Java applications?",
    "options": {
      "A": "When two threads update variables that reside on the same CPU cache line.",
      "B": "It results in significant performance degradation due to cache coherency traffic.",
      "C": "It occurs when two threads share the same 'this' reference.",
      "D": "It is a type of deadlock that only happens in Virtual Threads."
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: Using 'parallelStream()' always results in faster execution than a standard sequential stream.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary function of 'Compressed OOPs' (Ordinary Object Pointers) in a 64-bit JVM?",
    "options": {
      "A": "To represent 64-bit pointers as 32-bit offsets to save memory.",
      "B": "To compress the source code before execution.",
      "C": "To encrypt sensitive data in the Heap.",
      "D": "To reduce the size of the bytecode file."
    },
    "answer": "A"
  },
  {
    "question": "Which TWO annotations are used with 'Project Panama' for binding Java to native libraries?",
    "options": {
      "A": "@NativeType",
      "B": "@C",
      "C": "None (it uses programmatic Lookup/Linker APIs)",
      "D": "@FFI"
    },
    "answer": "C"
  },
  {
    "question": "What is 'JIT Recompilation'?",
    "options": {
      "A": "The process where the JVM promotes code from Level 1 to Level 4 (C2) optimization as it becomes 'hot'.",
      "B": "Restarting the app to clear the cache.",
      "C": "Compiling Java code to JavaScript.",
      "D": "Translating bytecode back into Java source code."
    },
    "answer": "A"
  },
  {
    "question": "True or False: An 'IdentityHashMap' compares keys using '==' instead of '.equals()'.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are benefits of 'AOT' (Ahead-of-Time) compilation in GraalVM?",
    "options": {
      "A": "Faster startup times.",
      "B": "Lower memory footprint at runtime.",
      "C": "Dynamic class loading support.",
      "D": "Better peak performance than C2 JIT."
    },
    "answer": "A, B"
  },
  {
    "question": "What does the 'invokedynamic' instruction (introduced in Java 7) primarily support?",
    "options": {
      "A": "Dynamic language implementation and Lambda expressions.",
      "B": "Direct hardware access.",
      "C": "Memory management for large arrays.",
      "D": "Faster integer arithmetic."
    },
    "answer": "A"
  },
  {
    "question": "True or False: A 'PhantomReference' is automatically cleared by the GC before it is added to the ReferenceQueue.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO are common causes of 'Memory Leaks' in Java?",
    "options": {
      "A": "Static collections that keep growing.",
      "B": "Unclosed Resources (Streams/Connections) in long-running apps.",
      "C": "Using 'final' variables.",
      "D": "Frequent Minor GC cycles."
    },
    "answer": "A, B"
  },
  {
    "question": "What is 'Biased Locking'?",
    "options": {
      "A": "An optimization for uncontended locks; now deprecated.",
      "B": "A way to prioritize certain threads in a pool.",
      "C": "A security feature for private fields.",
      "D": "A method of sorting objects in a TreeMap."
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are properties of 'Structured Concurrency' (Java 21)?",
    "options": {
      "A": "Treating groups of related tasks as a single unit of work.",
      "B": "Ensuring subtasks are finished before the parent task completes.",
      "C": "Replacing the need for any synchronization keywords.",
      "D": "Automatically migrating threads between different JVMs."
    },
    "answer": "A, B"
  },
  {
    "question": "What happens during 'Stack Walking' in Java 9+?",
    "options": {
      "A": "Programmatic access to stack traces to filter or skip frames efficiently.",
      "B": "The JVM checks for stack overflow errors.",
      "C": "Threads are moved from the stack to the heap.",
      "D": "The Garbage Collector scans local variables."
    },
    "answer": "A"
  },
  {
    "question": "Which area of JVM memory is used for storing class metadata, method data, and the runtime constant pool?",
    "options": {
      "A": "Heap",
      "B": "Stack",
      "C": "Metaspace",
      "D": "Code Cache"
    },
    "answer": "C"
  },
  {
    "question": "True or False: In Java 21, Virtual Threads are preemptively scheduled by the Operating System like Platform Threads.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary function of the 'G1' Garbage Collector's 'Humongous Allocation' handling?",
    "options": {
      "A": "To move large objects to the stack memory.",
      "B": "To allocate objects that are larger than 50% of a G1 region directly into the old generation.",
      "C": "To prevent the JVM from ever reaching OutOfMemoryError.",
      "D": "To compress string literals."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO valid methods provided by the 'CompletableFuture' class to handle exceptions in an asynchronous chain:",
    "options": {
      "A": "exceptionally()",
      "B": "handle()",
      "C": "catchError()",
      "D": "trap()"
    },
    "answer": "A, B"
  },
  {
    "question": "What does the 'volatile' keyword guarantee in the Java Memory Model?",
    "options": {
      "A": "Atomicity for long and double types.",
      "B": "Visibility of changes and prevention of instruction reordering for that variable.",
      "C": "Thread-safe increments (like i++).",
      "D": "Automatic locking of the object."
    },
    "answer": "B"
  },
  {
    "question": "True or False: A 'Strongly Reachable' object is protected from Garbage Collection even if the JVM is about to throw an OutOfMemoryError.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are functional interfaces introduced in Java 8 to support primitive types and avoid auto-boxing overhead?",
    "options": {
      "A": "IntPredicate",
      "B": "DoubleFunction",
      "C": "PrimitiveConsumer",
      "D": "NumSupplier"
    },
    "answer": "A, B"
  },
  {
    "question": "What is the purpose of 'Escape Analysis' performed by the JIT compiler?",
    "options": {
      "A": "To identify if a thread can exit a loop prematurely.",
      "B": "To determine if an object's scope is restricted to a method, allowing it to be allocated on the stack instead of the heap.",
      "C": "To find security vulnerabilities in the bytecode.",
      "D": "To optimize database connection strings."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Sealed Classes' (introduced in Java 17) allow a class to specify exactly which other classes can extend it.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO components make up the 'Happens-Before' relationship in concurrent Java code?",
    "options": {
      "A": "Synchronized blocks",
      "B": "Volatile writes/reads",
      "C": "Local variable declarations",
      "D": "Static method calls"
    },
    "answer": "A, B"
  },
  {
    "question": "Which JVM optimization technique replaces a constant value with the result of a calculation at compile time rather than runtime?",
    "options": {
      "A": "Dead Code Elimination",
      "B": "Constant Folding",
      "C": "Loop Unrolling",
      "D": "Inlining"
    },
    "answer": "B"
  },
  {
    "question": "True or False: In a 64-bit JVM, 'Compressed OOPs' are used to reduce the size of object pointers from 64-bit to 32-bit to save memory.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are functional interfaces designed to work with the 'Optional' class for providing fallback values?",
    "options": {
      "A": "Supplier",
      "B": "Runnable",
      "C": "Predicate",
      "D": "Consumer"
    },
    "answer": "A, B"
  },
  {
    "question": "What is the primary benefit of the 'Phaser' class over 'CyclicBarrier' in concurrent programming?",
    "options": {
      "A": "It is faster for single-core machines.",
      "B": "It allows for a dynamic number of registered parties (threads) that can change over time.",
      "C": "It prevents memory leaks in stashed objects.",
      "D": "It automatically handles InterruptedException."
    },
    "answer": "B"
  },
  {
    "question": "True or False: The 'yield' keyword in a switch expression (Java 14+) can be used inside a standard switch statement that does not return a value.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO JVM flags are essential for tuning the G1 Garbage Collector's pause time goals?",
    "options": {
      "A": "-XX:MaxGCPauseMillis",
      "B": "-XX:G1HeapRegionSize",
      "C": "-Xmx",
      "D": "-XX:+UseParallelGC"
    },
    "answer": "A, B"
  },
  {
    "question": "What does the 'invokedynamic' instruction support in the JVM?",
    "options": {
      "A": "Direct access to OS system calls.",
      "B": "Efficient implementation of dynamic languages and Lambda expressions by delaying method binding until runtime.",
      "C": "Automatic encryption of Heap memory.",
      "D": "Multi-threaded array sorting."
    },
    "answer": "B"
  },
  {
    "question": "Which TWO are properties of a 'SoftReference' in Java?",
    "options": {
      "A": "It is cleared only when the JVM is under high memory pressure.",
      "B": "It is used primarily for implementing memory-sensitive caches.",
      "C": "It is cleared immediately during the first Minor GC cycle.",
      "D": "It prevents the object from being finalized."
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: The 'Vector API' (Java 16+) allows developers to write platform-agnostic code that compiles to SIMD (Single Instruction, Multiple Data) hardware instructions.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which class is used to prevent 'False Sharing' by adding padding around a field to ensure it sits on its own cache line?",
    "options": {
      "A": "AtomicLong",
      "B": "@Contended",
      "C": "LongAdder",
      "D": "Volatile"
    },
    "answer": "B"
  },
  {
    "question": "What is the result of applying 'flatMap' to a stream of Optional objects?",
    "options": {
      "A": "A Stream of Lists.",
      "B": "A Stream of values where empty Optionals are removed and present values are unwrapped.",
      "C": "A compilation error.",
      "D": "A nested Optional structure."
    },
    "answer": "B"
  },
  {
    "question": "True or False: In a 'Structured Concurrency' scope, if one subtask fails, all other subtasks in that scope are automatically cancelled.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO methods are used to perform 'Compare-And-Swap' (CAS) operations using the VarHandle API?",
    "options": {
      "A": "compareAndSet()",
      "B": "getAndAdd()",
      "C": "volatileCast()",
      "D": "atomicUpdate()"
    },
    "answer": "A, B"
  },
  {
    "question": "What is the function of the 'Code Cache' area in the JVM?",
    "options": {
      "A": "To store the original .java source files.",
      "B": "To store the native code generated by the JIT (Just-In-Time) compiler.",
      "C": "To cache database query results.",
      "D": "To store static variables."
    },
    "answer": "B"
  },
  {
    "question": "True or False: A 'Default Method' in an interface can call other private or static methods within the same interface.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO collection types are 'Fail-Safe' (do not throw ConcurrentModificationException while iterating)?",
    "options": {
      "A": "CopyOnWriteArrayList",
      "B": "ConcurrentHashMap",
      "C": "ArrayList",
      "D": "TreeMap"
    },
    "answer": "A, B"
  },
  {
    "question": "What does 'T' represent in the wildcard 'List<? extends T>'?",
    "options": {
      "A": "T or any of its subclasses (Covariance).",
      "B": "T or any of its superclasses (Contravariance).",
      "C": "Only the Object class.",
      "D": "Only interface types."
    },
    "answer": "A"
  },
  {
    "question": "True or False: The 'StampedLock' provided in java.util.concurrent is reentrant.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO describe the 'Foreign Function & Memory API' (Project Panama)?",
    "options": {
      "A": "Safe access to off-heap memory.",
      "B": "Calling native C libraries without JNI.",
      "C": "Translating Java to Python.",
      "D": "Managing Docker containers from Java."
    },
    "answer": "A, B"
  },
  {
    "question": "What is 'On-Stack Replacement' (OSR) in the context of the JIT compiler?",
    "options": {
      "A": "Moving objects from the heap back to the stack.",
      "B": "Switching from interpreted to compiled code while a long-running loop is currently executing.",
      "C": "Replacing a local variable with a constant.",
      "D": "Allocating arrays on the thread stack."
    },
    "answer": "B"
  },
  {
    "question": "What is the primary purpose of the 'ForkJoinPool' introduced in Java 7?",
    "options": {
      "A": "To handle blocking I/O operations efficiently.",
      "B": "To implement a work-stealing algorithm for parallelizable, recursive tasks.",
      "C": "To replace the standard ThreadPoolExecutor.",
      "D": "To manage database connection pools."
    },
    "answer": "B"
  },
  {
    "question": "True or False: The 'volatile' keyword provides atomicity for composite operations like 'count++'.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO garbage collectors use a 'Regional' heap layout rather than the traditional 'Generational' layout (Eden, Survivor, Old)?",
    "options": {
      "A": "G1 (Garbage First)",
      "B": "ZGC",
      "C": "Parallel GC",
      "D": "Serial GC"
    },
    "answer": "A, B"
  },
  {
    "question": "What does the '@Inherited' annotation do when applied to a custom Java annotation?",
    "options": {
      "A": "It allows the annotation to be used on interface methods.",
      "B": "It causes the annotation to be automatically inherited by subclasses of the annotated class.",
      "C": "It enables the annotation to be read by the Garbage Collector.",
      "D": "It forces the compiler to check for method overriding."
    },
    "answer": "B"
  },
  {
    "question": "True or False: In Java 21, the ScopedValue API is intended to be a more lightweight and safer alternative to ThreadLocal for Virtual Threads.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO methods are used in the 'ReentrantReadWriteLock' to allow multiple readers but only one writer?",
    "options": {
      "A": "readLock()",
      "B": "writeLock()",
      "C": "sharedLock()",
      "D": "exclusiveLock()"
    },
    "answer": "A, B"
  },
  {
    "question": "What is the function of the 'TAPC' (Thread Local Allocation Buffer) in JVM memory management?",
    "options": {
      "A": "To store the stack traces of all active threads.",
      "B": "To allow threads to allocate objects in the Eden space without global locking, improving performance.",
      "C": "To manage the pool of Virtual Threads.",
      "D": "To cache frequently accessed static variables."
    },
    "answer": "B"
  },
  {
    "question": "True or False: A 'Method Reference' (e.g., System.out::println) can always be converted back into an equivalent Lambda expression.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO conditions are required for 'Deadlock' to occur in a multithreaded Java application?",
    "options": {
      "A": "Circular Wait",
      "B": "Hold and Wait",
      "C": "Garbage Collection",
      "D": "Instruction Reordering"
    },
    "answer": "A, B"
  },
  {
    "question": "What is the 'ABA problem' in lock-free algorithms, and which class helps solve it in Java?",
    "options": {
      "A": "A memory leak issue; solved by WeakReference.",
      "B": "A synchronization failure where a value changes from A to B and back to A; solved by AtomicStampedReference.",
      "C": "A compilation error; solved by the 'final' keyword.",
      "D": "A performance bottleneck; solved by LongAdder."
    },
    "answer": "B"
  },
  {
    "question": "True or False: The 'transient' keyword prevents a field from being included in a JSON string when using common libraries like Jackson or GSON without extra config.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B (The keyword applies to Java Serialization; JSON libraries often require @JsonIgnore)"
  },
  {
    "question": "Which TWO are parts of the 'LMAX Disruptor' pattern often used in high-frequency trading apps with Java?",
    "options": {
      "A": "Ring Buffer",
      "B": "Sequence Barrier",
      "C": "BlockingQueue",
      "D": "ThreadPoolExecutor"
    },
    "answer": "A, B"
  },
  {
    "question": "What does the 'Xss' JVM parameter control?",
    "options": {
      "A": "The maximum size of the Heap.",
      "B": "The size of the thread stack.",
      "C": "The size of the Metaspace.",
      "D": "The number of garbage collection threads."
    },
    "answer": "B"
  },
  {
    "question": "True or False: A 'Static Nested Class' does not have a reference to the instance of its Outer class.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO describe the 'Vector API' (JEP 448)?",
    "options": {
      "A": "It is a replacement for the legacy Vector class.",
      "B": "It allows expressing vector computations that reliably compile to SIMD instructions.",
      "C": "It provides performance benefits for data-parallel tasks.",
      "D": "It is used for managing network vectors."
    },
    "answer": "B, C"
  },
  {
    "question": "What is the purpose of the 'ReferenceQueue' in Java's memory management?",
    "options": {
      "A": "To prioritize objects for garbage collection.",
      "B": "To allow the program to be notified when the garbage collector determines that an object has become reachable/unreachable.",
      "C": "To store all active references in the JVM.",
      "D": "To manage database connection references."
    },
    "answer": "B"
  },
  {
    "question": "True or False: The 'invokedynamic' instruction was specifically added to the JVM to support the efficient execution of dynamic languages and Java Lambdas.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO functional interfaces are used for transforming data in the Stream API?",
    "options": {
      "A": "Function",
      "B": "UnaryOperator",
      "C": "Predicate",
      "D": "Supplier"
    },
    "answer": "A, B"
  },
  {
    "question": "What is the benefit of 'Compressed OOPs' (Ordinary Object Pointers)?",
    "options": {
      "A": "It encrypts object data for security.",
      "B": "It allows 64-bit JVMs to use 32-bit pointers for objects, saving significant memory.",
      "C": "It speeds up the JIT compiler.",
      "D": "It reduces the size of the Stack."
    },
    "answer": "B"
  },
  {
    "question": "True or False: In Java 17+, you can use the 'permits' keyword without a 'sealed' class.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which JVM optimization technique involves the compiler proving that an object's lifetime is restricted to a single thread or method, allowing for Stack Allocation?",
    "options": {
      "A": "Dead Code Elimination",
      "B": "Escape Analysis",
      "C": "Loop Unrolling",
      "D": "Constant Folding"
    },
    "answer": "B"
  },
  {
    "question": "True or False: In the Java Memory Model, a 'volatile' write 'happens-before' every subsequent 'volatile' read of the same variable.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the primary purpose of the 'LongAdder' class compared to 'AtomicLong' in high-concurrency environments?",
    "options": {
      "A": "It supports floating-point additions.",
      "B": "It reduces contention by maintaining a set of variables that grow dynamically to distribute the updates.",
      "C": "It is less memory-intensive for single-threaded apps.",
      "D": "It prevents the ABA problem automatically."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO specific characteristics of the Z Garbage Collector (ZGC):",
    "options": {
      "A": "It is a concurrent, non-generational collector.",
      "B": "Pause times do not exceed 1ms regardless of heap size.",
      "C": "It is the default collector for Java 8.",
      "D": "It uses a single-threaded 'Stop-the-World' approach."
    },
    "answer": "A, B"
  },
  {
    "question": "What does the 'invokedynamic' (indy) instruction facilitate in the JVM?",
    "options": {
      "A": "Direct hardware access for GPU processing.",
      "B": "Delaying the binding of a method call until the first time the instruction is executed at runtime.",
      "C": "Automatic encryption of class files.",
      "D": "Forced garbage collection of local variables."
    },
    "answer": "B"
  },
  {
    "question": "True or False: A 'StrongReference' object will be collected by the Garbage Collector if the JVM runs out of memory and needs to avoid an OutOfMemoryError.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO properties define the behavior of the 'StampedLock' introduced in Java 8?",
    "options": {
      "A": "It is fully reentrant like ReentrantLock.",
      "B": "It provides an 'Optimistic Read' mode to minimize synchronization overhead.",
      "C": "It can be converted from a read lock to a write lock.",
      "D": "It does not support conditional waiting (Condition)."
    },
    "answer": "B, D"
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
    skill = "Java"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
