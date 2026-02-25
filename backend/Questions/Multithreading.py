from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
    {
        "question": "Which of the following is the two ways to create a thread in Java?",
        "options": {
            "A": "By extending Thread class and implementing Runnable interface",
            "B": "By extending Process class and implementing Callable",
            "C": "By using the newThread() method only",
            "D": "By implementing the Main interface"
        },
        "answer": "A"
    },
    {
        "question": "What is the primary difference between a 'Process' and a 'Thread'?",
        "options": {
            "A": "Processes share memory; Threads do not",
            "B": "A Process is an independent execution unit with its own memory; a Thread is a subset of a process sharing memory",
            "C": "Threads are managed by the hardware only",
            "D": "There is no difference"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to start the execution of a thread?",
        "options": {
            "A": "run()",
            "B": "start()",
            "C": "execute()",
            "D": "launch()"
        },
        "answer": "B"
    },
    {
        "question": "What happens if you call the run() method directly instead of start()?",
        "options": {
            "A": "A new thread is created",
            "B": "The code executes in the current thread like a normal method call",
            "C": "The JVM crashes",
            "D": "It throws a ThreadStateException"
        },
        "answer": "B"
    },
    {
        "question": "Which state is a thread in after the start() method is called but before the scheduler picks it?",
        "options": {
            "A": "Running",
            "B": "Runnable",
            "C": "Blocked",
            "D": "Waiting"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'synchronized' keyword in Java?",
        "options": {
            "A": "To make the code run faster",
            "B": "To ensure that only one thread can access a block of code or method at a time",
            "C": "To allow multiple threads to access a variable simultaneously",
            "D": "To stop a thread"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Race Condition'?",
        "options": {
            "A": "A competition to see which thread finishes first",
            "B": "A situation where the outcome depends on the unpredictable timing of thread execution",
            "C": "A performance metric",
            "D": "A type of deadlock"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Deadlock'?",
        "options": {
            "A": "A thread that has finished execution",
            "B": "A situation where two or more threads are blocked forever, waiting for each other to release locks",
            "C": "A security feature",
            "D": "When a thread sleeps for too long"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to pause the execution of the current thread for a specified time?",
        "options": {
            "A": "wait()",
            "B": "sleep()",
            "C": "stop()",
            "D": "yield()"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'join()' method?",
        "options": {
            "A": "To join two strings",
            "B": "To wait for a specific thread to finish its execution before the current thread continues",
            "C": "To combine two threads into one",
            "D": "To start a thread"
        },
        "answer": "B"
    },
    {
        "question": "Which class/interface was introduced in Java 5 to return a result from a thread?",
        "options": {
            "A": "Runnable",
            "B": "Callable",
            "C": "Returnable",
            "D": "ThreadResult"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'volatile' keyword used for?",
        "options": {
            "A": "To ensure thread-safety for complex operations",
            "B": "To ensure that a variable's value is always read from and written to main memory, ensuring visibility across threads",
            "C": "To create a constant",
            "D": "To lock an object"
        },
        "answer": "B"
    },
    {
        "question": "Which method of the Object class is used for inter-thread communication?",
        "options": {
            "A": "wait()",
            "B": "notify()",
            "C": "notifyAll()",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "What must a thread hold before it can call wait() or notify() on an object?",
        "options": {
            "A": "A reference to the object",
            "B": "The monitor (lock) of that object",
            "C": "A CPU license",
            "D": "A priority of 10"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Thread Priority' range in Java?",
        "options": {
            "A": "0 to 100",
            "B": "1 to 10",
            "C": "A to Z",
            "D": "Low to High"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Daemon' thread?",
        "options": {
            "A": "A high-priority thread",
            "B": "A background thread that provides services to user threads and is terminated by the JVM when all user threads finish",
            "C": "A thread that causes errors",
            "D": "A thread that never stops"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to set a thread as a daemon?",
        "options": {
            "A": "setDaemon(true)",
            "B": "makeDaemon()",
            "C": "runInBackground()",
            "D": "setPriority(0)"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Livelock'?",
        "options": {
            "A": "A type of lock that is always active",
            "B": "A situation where threads keep changing their state in response to each other but make no progress",
            "C": "The opposite of deadlock",
            "D": "A performance optimization"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Starvation' in multithreading?",
        "options": {
            "A": "The CPU running out of power",
            "B": "When a thread is perpetually denied access to resources because other 'greedy' threads keep the resources occupied",
            "C": "A memory leak",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'ThreadLocal' class?",
        "options": {
            "A": "To share data between all threads",
            "B": "To provide variables that are local to a specific thread, ensuring each thread has its own independent copy",
            "C": "To locate a thread in memory",
            "D": "To count the number of threads"
        },
        "answer": "B"
    },
    {
        "question": "What is the default priority of a thread in Java?",
        "options": {
            "A": "1",
            "B": "5 (NORM_PRIORITY)",
            "C": "10",
            "D": "0"
        },
        "answer": "B"
    },
    {
        "question": "Which method can be used to check if a thread is still running?",
        "options": {
            "A": "isAlive()",
            "B": "isRunning()",
            "C": "active()",
            "D": "exists()"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Mutual Exclusion'?",
        "options": {
            "A": "Two threads working together",
            "B": "The property of ensuring that only one thread can access a resource at a given time",
            "C": "A type of deadlock",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "Which keyword is used to prevent an instruction from being reordered by the compiler/JVM?",
        "options": {
            "A": "synchronized",
            "B": "volatile",
            "C": "final",
            "D": "static"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Context Switching'?",
        "options": {
            "A": "Changing the code of a thread",
            "B": "The process of storing the state of a thread and restoring it later to resume execution",
            "C": "Moving a thread to a different server",
            "D": "A security attack"
        },
        "answer": "B"
    },
    {
        "question": "Which method is called when a thread is interrupted?",
        "options": {
            "A": "stop()",
            "B": "interrupt()",
            "C": "break()",
            "D": "pause()"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'yield()' method suggest to the thread scheduler?",
        "options": {
            "A": "Stop the thread immediately",
            "B": "The current thread is willing to give up its current use of a processor",
            "C": "Increase the thread priority",
            "D": "Ignore all other threads"
        },
        "answer": "B"
    },
    {
        "question": "Can we restart a dead thread?",
        "options": {
            "A": "Yes, by calling start() again",
            "B": "No, once a thread finishes execution it cannot be started again",
            "C": "Only if it is a daemon thread",
            "D": "Only in Java 17+"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Thread Pool'?",
        "options": {
            "A": "A place where threads go to swim",
            "B": "A collection of pre-initialized threads that are ready to perform tasks",
            "C": "A memory segment",
            "D": "A type of database"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Intrinsic Lock'?",
        "options": {
            "A": "A lock on a file",
            "B": "The built-in lock associated with every object instance in Java",
            "C": "A lock that cannot be opened",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "Which class provides atomic operations for integers?",
        "options": {
            "A": "AtomicInteger",
            "B": "SafeInteger",
            "C": "VolatileInt",
            "D": "SyncInt"
        },
        "answer": "A"
    },
    {
        "question": "What is the benefit of using 'Atomic' classes over 'synchronized' for simple counters?",
        "options": {
            "A": "They use fewer lines of code",
            "B": "They use non-blocking algorithms (CAS) which are generally faster for simple operations",
            "C": "They are more secure",
            "D": "They prevent all deadlocks"
        },
        "answer": "B"
    },
    {
        "question": "What does CAS stand for in concurrency?",
        "options": {
            "A": "Compare And Swap",
            "B": "Check And Stop",
            "C": "Copy And Send",
            "D": "Calculate And Save"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Wait-free' algorithm?",
        "options": {
            "A": "An algorithm that never waits for user input",
            "B": "An algorithm that guarantees every thread will complete its operation in a finite number of steps",
            "C": "A performance metric",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "Which interface is the root of the Java Concurrency framework?",
        "options": {
            "A": "Thread",
            "B": "Executor",
            "C": "Runnable",
            "D": "Lock"
        },
        "answer": "B"
    },
    {
        "question": "What is 'ReentrantLock'?",
        "options": {
            "A": "A lock that can be used only once",
            "B": "A lock that allows the same thread to acquire it multiple times without deadlocking itself",
            "C": "A security scan result",
            "D": "A type of sharding"
        },
        "answer": "B"
    },
    {
        "question": "What is 'ReadWriteLock'?",
        "options": {
            "A": "A lock that only works for files",
            "B": "A lock that allows multiple threads to read but only one to write",
            "C": "A lock for a database only",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to release a lock in ReentrantLock?",
        "options": {
            "A": "close()",
            "B": "unlock()",
            "C": "release()",
            "D": "free()"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Green Thread' in early Java history?",
        "options": {
            "A": "Threads that are eco-friendly",
            "B": "Threads scheduled by a virtual machine instead of natively by the OS",
            "C": "A performance metric",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "Which exception is thrown if a thread is interrupted while waiting?",
        "options": {
            "A": "ThreadException",
            "B": "InterruptedException",
            "C": "WaitException",
            "D": "RuntimeException"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Thread Group'?",
        "options": {
            "A": "A group of people working on threads",
            "B": "A mechanism to manage multiple threads as a single unit (now largely legacy)",
            "C": "A type of database",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "What is the result of 'wait()' without a timeout?",
        "options": {
            "A": "The thread waits for 1 second",
            "B": "The thread waits indefinitely until notified",
            "C": "The thread stops immediately",
            "D": "An error is thrown"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Spurious Wakeup'?",
        "options": {
            "A": "When a developer wakes up early",
            "B": "A situation where a thread wakes up from wait() even without a notify() signal",
            "C": "A performance report",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "How should wait() be called to handle spurious wakeups?",
        "options": {
            "A": "In an if-block",
            "B": "In a while-loop checking the condition",
            "C": "Only in the main thread",
            "D": "Inside a finally block"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Semaphore'?",
        "options": {
            "A": "To count the number of threads",
            "B": "To control access to a shared resource using a set of permits",
            "C": "To encrypt the code",
            "D": "To speed up the network"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to acquire a permit from a Semaphore?",
        "options": {
            "A": "get()",
            "B": "acquire()",
            "C": "take()",
            "D": "lock()"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'CountDownLatch'?",
        "options": {
            "A": "A clock on the screen",
            "B": "A synchronization aid that allows one or more threads to wait until a set of operations are performed",
            "C": "A type of sharding",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'CyclicBarrier'?",
        "options": {
            "A": "A barrier that moves in circles",
            "B": "A synchronization aid that allows a set of threads to all wait for each other to reach a common barrier point",
            "C": "A security firewall",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "What is the difference between 'CountDownLatch' and 'CyclicBarrier'?",
        "options": {
            "A": "They are identical",
            "B": "CountDownLatch cannot be reset; CyclicBarrier can be reused",
            "C": "CyclicBarrier is faster",
            "D": "CountDownLatch is only for the UI"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 1: Which class is used to create and manage thread pools?",
        "options": {
            "A": "ThreadManager",
            "B": "Executors",
            "C": "PoolFactory",
            "D": "ProcessBuilder"
        },
        "answer": "B"
    },
    {
        "question": "Which interface in the java.util.concurrent package provides a way to decouple task submission from task execution?",
        "options": {
            "A": "Runnable",
            "B": "Executor",
            "C": "ThreadManager",
            "D": "TaskQueue"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary difference between Executor and ExecutorService?",
        "options": {
            "A": "They are identical",
            "B": "ExecutorService extends Executor and adds methods for lifecycle management (shutdown) and task tracking (submit)",
            "C": "Executor is for mobile; ExecutorService for desktop",
            "D": "ExecutorService is deprecated"
        },
        "answer": "B"
    },
    {
        "question": "Which method of ExecutorService is used to submit a Callable task and get a result back?",
        "options": {
            "A": "execute()",
            "B": "submit()",
            "C": "run()",
            "D": "get()"
        },
        "answer": "B"
    },
    {
        "question": "What does a 'Future' object represent in Java concurrency?",
        "options": {
            "A": "A prediction of the code's success",
            "B": "The result of an asynchronous computation that may not be available yet",
            "C": "A backup thread",
            "D": "A time-stamped log"
        },
        "answer": "B"
    },
    {
        "question": "What happens when you call Future.get() if the task is not yet complete?",
        "options": {
            "A": "It returns null immediately",
            "B": "It blocks (waits) until the task is complete and then returns the result",
            "C": "It throws a RuntimeException",
            "D": "It cancels the task"
        },
        "answer": "B"
    },
    {
        "question": "Which Executors method creates a thread pool that reuses a fixed number of threads?",
        "options": {
            "A": "newCachedThreadPool()",
            "B": "newFixedThreadPool(int n)",
            "C": "newSingleThreadExecutor()",
            "D": "newScheduledThreadPool()"
        },
        "answer": "B"
    },
    {
        "question": "What is the behavior of a 'CachedThreadPool'?",
        "options": {
            "A": "It keeps exactly 5 threads active",
            "B": "It creates new threads as needed but reuses idle threads when they are available",
            "C": "It stores thread data in a database",
            "D": "It never terminates"
        },
        "answer": "B"
    },
    {
        "question": "Which class allows you to implement a custom thread pool with specific core and max sizes?",
        "options": {
            "A": "ThreadPoolExecutor",
            "B": "CustomExecutor",
            "C": "ThreadFactory",
            "D": "PoolManager"
        },
        "answer": "A"
    },
    {
        "question": "In ThreadPoolExecutor, what is the 'corePoolSize'?",
        "options": {
            "A": "The maximum threads allowed",
            "B": "The number of threads to keep in the pool, even if they are idle",
            "C": "The size of the task queue",
            "D": "The priority of the threads"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'keepAliveTime' parameter in ThreadPoolExecutor?",
        "options": {
            "A": "To keep the JVM running",
            "B": "The maximum time that excess idle threads will wait for new tasks before terminating",
            "C": "The duration of a task",
            "D": "The interval between health checks"
        },
        "answer": "B"
    },
    {
        "question": "Which queue is typically used by a FixedThreadPool to store pending tasks?",
        "options": {
            "A": "SynchronousQueue",
            "B": "LinkedBlockingQueue",
            "C": "PriorityBlockingQueue",
            "D": "DelayQueue"
        },
        "answer": "B"
    },
    {
        "question": "What does 'ScheduledExecutorService' allow you to do?",
        "options": {
            "A": "Schedule meetings for developers",
            "B": "Execute tasks after a delay or periodically (fixed-rate or fixed-delay)",
            "C": "Optimize the OS schedule",
            "D": "Check the weather"
        },
        "answer": "B"
    },
    {
        "question": "What is the difference between scheduleAtFixedRate() and scheduleWithFixedDelay()?",
        "options": {
            "A": "They are identical",
            "B": "FixedRate starts tasks at constant intervals; FixedDelay starts the interval after the previous task finishes",
            "C": "FixedRate is only for single threads",
            "D": "FixedDelay is more accurate"
        },
        "answer": "B"
    },
    {
        "question": "Which interface should you use for tasks that don't return a value but might throw a checked exception?",
        "options": {
            "A": "Runnable",
            "B": "Callable (though you must return null or use Void)",
            "C": "Executor",
            "D": "There is no such interface"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Fork/Join' framework primarily used for?",
        "options": {
            "A": "Handling user input",
            "B": "Parallelizing recursive, divide-and-conquer tasks to utilize multiple processors",
            "C": "Joining strings in a list",
            "D": "Managing database forks"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Work-Stealing' in the context of ForkJoinPool?",
        "options": {
            "A": "Threads taking tasks from each other's code",
            "B": "Idle threads 'stealing' tasks from the back of the deques of busy threads to balance load",
            "C": "A security vulnerability",
            "D": "A performance bug"
        },
        "answer": "B"
    },
    {
        "question": "Which Concurrent collection is a thread-safe alternative to HashMap?",
        "options": {
            "A": "Hashtable",
            "B": "ConcurrentHashMap",
            "C": "SynchronizedMap",
            "D": "LinkedHashMap"
        },
        "answer": "B"
    },
    {
        "question": "How does ConcurrentHashMap achieve high concurrency compared to Hashtable?",
        "options": {
            "A": "By locking the whole map for every operation",
            "B": "By using lock striping or CAS operations to allow multiple threads to access different segments/buckets simultaneously",
            "C": "By running on a GPU",
            "D": "By disabling updates during reads"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'CopyOnWriteArrayList' best used for?",
        "options": {
            "A": "Frequent write operations",
            "B": "Scenarios with frequent reads and very rare writes (since every write creates a new copy of the array)",
            "C": "Infinite loops",
            "D": "Sorting large datasets"
        },
        "answer": "B"
    },
    {
        "question": "What happens if a thread tries to put an element into a full 'ArrayBlockingQueue'?",
        "options": {
            "A": "It returns null",
            "B": "It blocks (waits) until space becomes available if using the put() method",
            "C": "It throws an IndexOutOfBoundsException",
            "D": "It overwrites the oldest element"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'CompletableFuture' introduced in Java 8?",
        "options": {
            "A": "To replace all threads",
            "B": "To allow for non-blocking, asynchronous programming and pipelining of multiple tasks",
            "C": "To handle database transactions",
            "D": "To visualize thread states"
        },
        "answer": "B"
    },
    {
        "question": "Which method in CompletableFuture is used to chain a task that depends on the previous task's result?",
        "options": {
            "A": "thenApply()",
            "B": "thenAccept()",
            "C": "thenRun()",
            "D": "handle()"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of the 'Exchanger' synchronization aid?",
        "options": {
            "A": "To exchange currencies",
            "B": "To allow two threads to exchange data at a common synchronization point",
            "C": "To move a thread to another CPU",
            "D": "To change the thread's name"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Phaser' in Java Concurrency?",
        "options": {
            "A": "A weapon from a sci-fi movie",
            "B": "A more flexible, reusable synchronization barrier that supports dynamic registration of parties",
            "C": "A type of unit test",
            "D": "A memory segment"
        },
        "answer": "B"
    },
    {
        "question": "Which class is the base for implementing your own custom locks or synchronizers?",
        "options": {
            "A": "AbstractQueuedSynchronizer (AQS)",
            "B": "LockManager",
            "C": "SyncBase",
            "D": "ThreadLock"
        },
        "answer": "A"
    },
    {
        "question": "What does the 'shutdown()' method of ExecutorService do?",
        "options": {
            "A": "Terminates the JVM",
            "B": "Initiates an orderly shutdown where previously submitted tasks are executed, but no new tasks are accepted",
            "C": "Stops all tasks immediately",
            "D": "Deletes the thread pool"
        },
        "answer": "B"
    },
    {
        "question": "What is the difference between shutdown() and shutdownNow()?",
        "options": {
            "A": "shutdownNow() waits for tasks to finish; shutdown() does not",
            "B": "shutdownNow() attempts to stop all actively executing tasks and halts the processing of waiting tasks",
            "C": "There is no difference",
            "D": "shutdownNow() is only for mobile apps"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Thread Leak'?",
        "options": {
            "A": "Threads running too fast",
            "B": "A situation where threads are created but never terminated or returned to a pool, eventually exhausting system resources",
            "C": "A security leak of thread names",
            "D": "A type of memory corruption"
        },
        "answer": "B"
    },
    {
        "question": "Which interface represents a task that can be executed and returned a result, and can throw a checked exception?",
        "options": {
            "A": "Runnable",
            "B": "Callable<V>",
            "C": "Future<V>",
            "D": "Supplier<V>"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Double-Checked Locking' pattern used for?",
        "options": {
            "A": "Locking the database twice",
            "B": "Reducing the overhead of acquiring a lock by first testing the locking criterion without actually acquiring the lock (often used in Singletons)",
            "C": "A security attack",
            "D": "Testing thread speed"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'ABA Problem' in lock-free programming?",
        "options": {
            "A": "A problem with the alphabet",
            "B": "When a value changes from A to B and back to A, causing a CAS operation to succeed even though the state changed",
            "C": "A type of deadlock",
            "D": "A performance bottleneck"
        },
        "answer": "B"
    },
    {
        "question": "Which class is used to solve the ABA problem by using a 'stamp' or 'version'?",
        "options": {
            "A": "AtomicStampedReference",
            "B": "AtomicInteger",
            "C": "VolatileReference",
            "D": "VersionedLock"
        },
        "answer": "A"
    },
    {
        "question": "What is 'False Sharing' in multithreaded systems?",
        "options": {
            "A": "Threads lying to each other",
            "B": "When different threads modify variables that reside on the same CPU cache line, causing unnecessary cache invalidations",
            "C": "A security vulnerability",
            "D": "A type of memory leak"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation was introduced in Java 8 to help combat False Sharing?",
        "options": {
            "A": "@ThreadSafe",
            "B": "@Contended",
            "C": "@CachePadding",
            "D": "@Atomic"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'BlockingQueue'?",
        "options": {
            "A": "A queue that blocks users",
            "B": "A queue that supports operations that wait for the queue to become non-empty when retrieving or non-full when storing",
            "C": "A type of firewall",
            "D": "A legacy collection"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to retrieve and remove the head of a queue, waiting if necessary?",
        "options": {
            "A": "poll()",
            "B": "take()",
            "C": "remove()",
            "D": "peek()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'SynchronousQueue'?",
        "options": {
            "A": "A queue that stores infinite items",
            "B": "A blocking queue in which each insert operation must wait for a corresponding remove operation by another thread",
            "C": "A queue for strings only",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "What is 'DelayQueue' used for?",
        "options": {
            "A": "To delay the program start",
            "B": "To store elements until a certain delay has expired",
            "C": "To slow down the database",
            "D": "To monitor network latency"
        },
        "answer": "B"
    },
    {
        "question": "Which class provides a scalable thread-safe 'Long' adder that is better than AtomicLong under high contention?",
        "options": {
            "A": "LongAdder",
            "B": "AtomicLongFieldUpdater",
            "C": "FastLong",
            "D": "SyncLong"
        },
        "answer": "A"
    },
    {
        "question": "What is 'RecursiveTask' in Fork/Join?",
        "options": {
            "A": "A task that never ends",
            "B": "A subclass of ForkJoinTask that returns a result",
            "C": "A type of unit test",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'RecursiveAction' in Fork/Join?",
        "options": {
            "A": "A task that does not return a result",
            "B": "A type of database trigger",
            "C": "A performance report",
            "D": "A security scanner"
        },
        "answer": "A"
    },
    {
        "question": "Which method is used in Fork/Join to submit a subtask for parallel execution?",
        "options": {
            "A": "split()",
            "B": "fork()",
            "C": "spawn()",
            "D": "run()"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'join()' method do in a ForkJoinTask?",
        "options": {
            "A": "Joins two strings",
            "B": "Blocks until the task is complete and returns the result",
            "C": "Merges two threads",
            "D": "Restarts the task"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'ThreadFactory'?",
        "options": {
            "A": "To manufacture CPU chips",
            "B": "An object that creates new threads on demand, allowing customization of name, priority, and daemon status",
            "C": "To manage the JVM",
            "D": "To visualize threads"
        },
        "answer": "B"
    },
    {
        "question": "What is 'PriorityBlockingQueue'?",
        "options": {
            "A": "A queue that prioritizes the developer",
            "B": "An unbounded blocking queue that uses the same ordering rules as PriorityQueue",
            "C": "A security scan result",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'StampedLock' introduced in Java 8?",
        "options": {
            "A": "A lock for letters",
            "B": "A lock that provides optimistic read mode to improve performance in read-heavy scenarios",
            "C": "A type of database lock",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Optimistic Read' in StampedLock?",
        "options": {
            "A": "Hoping the data is correct",
            "B": "Reading data without a full lock and then validating if a write occurred during the read",
            "C": "Reading only from the cache",
            "D": "A performance test"
        },
        "answer": "B"
    },
    {
        "question": "Which class can be used to coordinate between a fixed number of threads, which must all wait for each other at a point?",
        "options": {
            "A": "Semaphore",
            "B": "CyclicBarrier",
            "C": "CountDownLatch",
            "D": "Exchanger"
        },
        "answer": "B"
    },
    {
        "question": "What is 'ExecutionException' in the context of Futures?",
        "options": {
            "A": "An exception during code writing",
            "B": "An exception thrown by Future.get() when the underlying task threw an exception",
            "C": "A type of sharding",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 2: Which method in CompletableFuture is used to handle results from 'either' of two stages?",
        "options": {
            "A": "thenCombine()",
            "B": "acceptEither()",
            "C": "runAfterBoth()",
            "D": "allOf()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Lock Contention'?",
        "options": {
            "A": "The speed of acquiring a lock",
            "B": "A state where one thread attempts to acquire a lock held by another thread",
            "C": "A type of deadlock",
            "D": "The number of locks in a program"
        },
        "answer": "B"
    },
    {
        "question": "Which class is a thread-safe, array-based implementation of the List interface where all mutative operations are implemented by making a fresh copy?",
        "options": {
            "A": "Vector",
            "B": "CopyOnWriteArrayList",
            "C": "SynchronizedList",
            "D": "ConcurrentArrayList"
        },
        "answer": "B"
    },
    {
        "question": "What does 'CPU Cache Locality' refer to in multithreading performance?",
        "options": {
            "A": "Storing threads on a local disk",
            "B": "Organizing data so that related data items are stored near each other in memory to improve cache hit rates",
            "C": "The physical location of the CPU",
            "D": "Limiting the CPU temperature"
        },
        "answer": "B"
    },
    {
        "question": "What is 'False Sharing' and how does it affect performance?",
        "options": {
            "A": "Threads sharing too much data",
            "B": "When multiple processors modify variables on the same cache line, forcing unnecessary cache updates and slowing down the system",
            "C": "A security vulnerability",
            "D": "A memory leak"
        },
        "answer": "B"
    },
    {
        "question": "Which Java annotation is used to prevent 'False Sharing' by adding padding around a variable?",
        "options": {
            "A": "@ThreadSafe",
            "B": "@jdk.internal.vm.annotation.Contended",
            "C": "@CachePadding",
            "D": "@Atomic"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'StampedLock' introduced in Java 8?",
        "options": {
            "A": "To add a time stamp to every lock",
            "B": "To provide an 'Optimistic Read' mode that allows for better performance in read-heavy scenarios",
            "C": "To replace ReentrantLock entirely",
            "D": "To lock files on disk"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Optimistic Reading' in the context of StampedLock?",
        "options": {
            "A": "Hoping the thread finishes fast",
            "B": "Acquiring a 'non-exclusive' view of the data and validating that no write occurred before using it",
            "C": "Reading data without checking for errors",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Thread Local Storage' (TLS) primarily used for?",
        "options": {
            "A": "To share global state",
            "B": "To store data that is unique to a single thread, such as a database connection or a user session",
            "C": "To store the thread's name",
            "D": "To monitor the thread's RAM usage"
        },
        "answer": "B"
    },
    {
        "question": "Which Concurrent collection uses 'Lock Striping' internally to manage concurrency?",
        "options": {
            "A": "Hashtable",
            "B": "ConcurrentHashMap",
            "C": "Collections.synchronizedMap()",
            "D": "TreeMap"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Wait-Free' synchronization?",
        "options": {
            "A": "A thread never has to wait for user input",
            "B": "An algorithm where every thread makes progress regardless of the speed or status of other threads",
            "C": "A type of unit test",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Lock-Free' synchronization?",
        "options": {
            "A": "A system without any locks",
            "B": "An algorithm where at least one thread is guaranteed to make progress even if others fail",
            "C": "A security scan",
            "D": "A type of sharding"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Obstruction-Free' synchronization?",
        "options": {
            "A": "The weakest non-blocking guarantee; progress is made only if a thread is not interfered with by others",
            "B": "No barriers on the network",
            "C": "A type of unit test",
            "D": "A performance report"
        },
        "answer": "A"
    },
    {
        "question": "Which class is a highly scalable alternative to AtomicLong for high-contention counters?",
        "options": {
            "A": "LongAdder",
            "B": "VolatileLong",
            "C": "SynchronizedLong",
            "D": "SafeLong"
        },
        "answer": "A"
    },
    {
        "question": "What makes 'LongAdder' faster than 'AtomicLong' under high contention?",
        "options": {
            "A": "It uses more threads",
            "B": "It maintains a set of variables that are summed only when the value is requested, reducing contention on a single point",
            "C": "It runs on the GPU",
            "D": "It skips error checking"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Fork/Join' pool's default parallelism level?",
        "options": {
            "A": "1",
            "B": "The number of available processors on the system",
            "C": "10",
            "D": "Unlimited"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'ABA Problem' solution in Java?",
        "options": {
            "A": "Using a synchronized block",
            "B": "Using AtomicStampedReference or AtomicMarkableReference",
            "C": "Using the volatile keyword",
            "D": "It is unsolvable in Java"
        },
        "answer": "B"
    },
    {
        "question": "What does 'ManagedBlocker' do in a ForkJoinPool?",
        "options": {
            "A": "Blocks unwanted threads",
            "B": "Allows the pool to temporarily create more threads to maintain parallelism while a task is blocked on I/O",
            "C": "A type of firewall",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Instruction Reordering' in JMM?",
        "options": {
            "A": "Sorting code alphabetically",
            "B": "A performance optimization where the CPU/Compiler changes the order of operations as long as it doesn't change the single-threaded result",
            "C": "A security attack",
            "D": "A memory leak"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is a 'Memory Barrier' (Fence)?",
        "options": {
            "A": "A hardware barrier",
            "B": "A CPU instruction that forces the completion of previous memory operations before following ones can begin",
            "C": "A security wall",
            "D": "A type of sharding"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Visibility' in multithreading?",
        "options": {
            "A": "Seeing the code on screen",
            "B": "Ensuring that changes made to a variable by one thread are seen by other threads",
            "C": "Public vs private access",
            "D": "A type of log level"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Atomicity'?",
        "options": {
            "A": "The speed of the CPU",
            "B": "Ensuring that a sequence of operations appears to happen as a single, indivisible unit",
            "C": "The number of atoms in the memory",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Non-blocking' algorithm?",
        "options": {
            "A": "An algorithm that doesn't use the network",
            "B": "An algorithm where the failure or suspension of any thread cannot cause the failure or suspension of another thread",
            "C": "A fast algorithm",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Safe Publication'?",
        "options": {
            "A": "Publishing code to GitHub",
            "B": "The practice of making an object reference visible to other threads while ensuring its state is fully consistent",
            "C": "Encrypting data",
            "D": "A type of logging"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is a way to achieve 'Safe Publication'?",
        "options": {
            "A": "Using 'static' initializer",
            "B": "Using 'volatile' or 'final' keywords",
            "C": "Using 'synchronized' blocks",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Check-Then-Act' race condition?",
        "options": {
            "A": "Checking the time before acting",
            "B": "A condition where a value is checked and then used, but the value might change between the check and the act",
            "C": "A type of unit test",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'AtomicReference'?",
        "options": {
            "A": "To create an atomic string",
            "B": "To provide thread-safe, lock-free updates on an object reference",
            "C": "To store a list of threads",
            "D": "To monitor memory addresses"
        },
        "answer": "B"
    },
    {
        "question": "Which Concurrent collection is best for implementing a 'Message Queue' with high-performance requirements?",
        "options": {
            "A": "ConcurrentLinkedQueue",
            "B": "ArrayBlockingQueue",
            "C": "PriorityQueue",
            "D": "LinkedList"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Unbounded' queue risk?",
        "options": {
            "A": "It can grow indefinitely and cause OutOfMemoryError if consumers are slower than producers",
            "B": "It is too slow",
            "C": "It is not thread-safe",
            "D": "It deletes items"
        },
        "answer": "A"
    },
    {
        "question": "Which class is used to exchange a single piece of data between two threads in a blocking manner?",
        "options": {
            "A": "Exchanger",
            "B": "Semaphore",
            "C": "CyclicBarrier",
            "D": "Phaser"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Thread Interruption' policy?",
        "options": {
            "A": "Interrupting every thread",
            "B": "A defined strategy for how a thread should respond when it receives an interrupt signal",
            "C": "A security scan",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Interrupted' status?",
        "options": {
            "A": "A boolean flag on the Thread object indicating if it has been interrupted",
            "B": "The name of the thread",
            "C": "A type of error",
            "D": "The priority of the thread"
        },
        "answer": "A"
    },
    {
        "question": "Which method 'clears' the interrupted status of a thread?",
        "options": {
            "A": "Thread.interrupted()",
            "B": "thread.isInterrupted()",
            "C": "thread.stop()",
            "D": "thread.reset()"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Fairness' in ReentrantLock?",
        "options": {
            "A": "Everyone gets a turn",
            "B": "An optional setting that favors granting access to the thread that has been waiting the longest",
            "C": "A type of unit test",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is the cost of 'Fairness' in locks?",
        "options": {
            "A": "It is free",
            "B": "Significant decrease in throughput because it requires more context switching and bookkeeping",
            "C": "It makes the code longer",
            "D": "It requires more RAM"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Read-Write Lock' starvation risk?",
        "options": {
            "A": "Writers can be starved if there is a constant stream of readers",
            "B": "Readers are always slower",
            "C": "Threads run out of power",
            "D": "A performance report"
        },
        "answer": "A"
    },
    {
        "question": "What is 'AtomicReferenceFieldUpdater'?",
        "options": {
            "A": "A tool to update fields in a database",
            "B": "A reflection-based utility that enables atomic updates to designated volatile fields of a class",
            "C": "A security scan",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Which Concurrent collection is a thread-safe, navigable skip-list implementation?",
        "options": {
            "A": "ConcurrentSkipListMap",
            "B": "ConcurrentHashMap",
            "C": "TreeMap",
            "D": "NavigableMap"
        },
        "answer": "A"
    },
    {
        "question": "What is the 'Double-Checked Locking' prerequisite in Java 5+?",
        "options": {
            "A": "The singleton variable MUST be declared as 'volatile'",
            "B": "The method must be static",
            "C": "The lock must be a String",
            "D": "There is no requirement"
        },
        "answer": "A"
    },
    {
        "question": "What is the 'Thread Pool' saturation policy?",
        "options": {
            "A": "Adding water to the pool",
            "B": "A strategy for what to do when the pool and queue are both full (e.g., Abort, CallerRuns, Discard)",
            "C": "A security scan",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 3: What is the main benefit of 'Lock-Free' data structures?",
        "options": {
            "A": "They are easier to write",
            "B": "They avoid the overhead of thread suspension and context switching, and are immune to deadlock",
            "C": "They use less memory",
            "D": "They work on all hardware"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary goal of 'Virtual Threads' (Project Loom) introduced in Java 19/21?",
        "options": {
            "A": "To make threads run on a GPU",
            "B": "To provide lightweight, user-mode threads that allow scaling to millions of concurrent tasks with low overhead",
            "C": "To replace the synchronized keyword",
            "D": "To encrypt thread communication"
        },
        "answer": "B"
    },
    {
        "question": "What is the difference between a 'Platform Thread' and a 'Virtual Thread'?",
        "options": {
            "A": "Platform threads are mapped 1:1 to OS threads; Virtual threads are managed by the Java runtime and mounted on carrier threads",
            "B": "Virtual threads are only for Windows",
            "C": "Platform threads use less memory",
            "D": "There is no difference"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Pinning' in the context of Virtual Threads?",
        "options": {
            "A": "Setting a thread to high priority",
            "B": "A state where a virtual thread cannot be unmounted from its carrier thread (e.g., inside a synchronized block or native call)",
            "C": "Locking a thread to a specific CPU core",
            "D": "A security feature"
        },
        "answer": "B"
    },
    {
        "question": "Which class is used to create a Virtual Thread in Java 21?",
        "options": {
            "A": "Thread.ofVirtual()",
            "B": "new VirtualThread()",
            "C": "Executors.newLightweightThread()",
            "D": "Thread.startVirtual()"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Structured Concurrency' intended to solve?",
        "options": {
            "A": "Slow database queries",
            "B": "Managing the lifetime and cancellation of groups of related asynchronous tasks as a single unit",
            "C": "Sorting threads by name",
            "D": "Memory leaks in static variables"
        },
        "answer": "B"
    },
    {
        "question": "Which interface provides the 'Scope' for Structured Concurrency in Java?",
        "options": {
            "A": "StructuredTaskScope",
            "B": "ThreadScope",
            "C": "ExecutorScope",
            "D": "TaskGroup"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Scoped Values' (JEP 429) an alternative to?",
        "options": {
            "A": "ThreadLocal",
            "B": "Volatile variables",
            "C": "AtomicInteger",
            "D": "Static constants"
        },
        "answer": "A"
    },
    {
        "question": "What is the main advantage of Scoped Values over ThreadLocal?",
        "options": {
            "A": "They are faster to read",
            "B": "They are immutable and have a bounded lifetime, making them safer and more memory-efficient for thousands of threads",
            "C": "They can be changed by any thread",
            "D": "They don't require a JVM"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Spin-waiting' (Busy-waiting)?",
        "options": {
            "A": "A thread sleeping for a long time",
            "B": "A thread repeatedly checking a condition in a loop without yielding the CPU",
            "C": "A type of deadlock",
            "D": "A performance optimization for slow I/O"
        },
        "answer": "B"
    },
    {
        "question": "When is 'Spin-waiting' actually beneficial?",
        "options": {
            "A": "For long-running I/O tasks",
            "B": "When the expected wait time is extremely short (shorter than the cost of a context switch)",
            "C": "When the CPU has no other tasks",
            "D": "In mobile applications to save battery"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Thread Dumping'?",
        "options": {
            "A": "Deleting all threads",
            "B": "A snapshot of the state of all active threads in a JVM, used for diagnosing deadlocks or performance issues",
            "C": "A type of memory corruption",
            "D": "A backup of the database"
        },
        "answer": "B"
    },
    {
        "question": "Which command line tool is used to generate a thread dump of a Java process?",
        "options": {
            "A": "jstack",
            "B": "jmap",
            "C": "jcmd",
            "D": "Both A and C"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Lock Coarsening'?",
        "options": {
            "A": "Making a lock stronger",
            "B": "A JVM optimization where multiple adjacent synchronized blocks on the same object are merged into one",
            "C": "Removing locks entirely",
            "D": "A type of security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Biased Locking'?",
        "options": {
            "A": "A lock that prefers certain threads",
            "B": "An optimization where a lock 'biases' toward the first thread that acquires it, reducing the cost of subsequent acquisitions by that same thread",
            "C": "A type of deadlock",
            "D": "A performance bug"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Barrier Action' in a CyclicBarrier?",
        "options": {
            "A": "A security alert",
            "B": "A Runnable task that is executed once after the last thread arrives at the barrier but before any threads are released",
            "C": "Stopping the program",
            "D": "A type of memory flush"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Thread-Safe Singleton' via Initialization-on-demand holder idiom?",
        "options": {
            "A": "Using a synchronized method",
            "B": "Using a static inner class to hold the instance, leveraging JVM class-loading guarantees for thread safety",
            "C": "Using the volatile keyword",
            "D": "Using an Enum"
        },
        "answer": "B"
    },
    {
        "question": "Which Concurrent collection is best for implementing a 'First-In-First-Out' (FIFO) buffer with multiple producers and consumers?",
        "options": {
            "A": "LinkedBlockingQueue",
            "B": "Stack",
            "C": "PriorityQueue",
            "D": "DelayQueue"
        },
        "answer": "A"
    },
    {
        "question": "What is the 'Producer-Consumer' pattern?",
        "options": {
            "A": "A business model",
            "B": "A design pattern where one set of threads generates data and another set processes it, coordinated by a shared queue",
            "C": "A type of deadlock",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "In 'Producer-Consumer', what is the role of the 'BlockingQueue'?",
        "options": {
            "A": "To block the internet",
            "B": "To act as a buffer that manages the flow and provides synchronization between producers and consumers",
            "C": "To store the thread names",
            "D": "To monitor CPU usage"
        },
        "answer": "B"
    },
    {
        "question": "What is 'AtomicIntegerFieldUpdater' used for?",
        "options": {
            "A": "To update a database field",
            "B": "To perform atomic updates on a volatile 'int' field of a class without the memory overhead of an AtomicInteger object",
            "C": "A type of sharding",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Diamond Problem' in the context of Default Methods and Multiple Inheritance (relevant for thread-safe interface design)?",
        "options": {
            "A": "A problem with a diamond mine",
            "B": "Ambiguity that arises when a class implements two interfaces that both provide a default implementation of the same method",
            "C": "A type of deadlock",
            "D": "A performance bottleneck"
        },
        "answer": "B"
    },
    {
        "question": "Which class is used to implement a 'Latch' that can be opened only once?",
        "options": {
            "A": "CountDownLatch",
            "B": "CyclicBarrier",
            "C": "Semaphore",
            "D": "Phaser"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Thread Leak' detection?",
        "options": {
            "A": "Monitoring the total thread count and identifying threads that stay alive longer than expected",
            "B": "A type of water leak",
            "C": "A security scan",
            "D": "A performance metric"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Recursive Task' in Fork/Join framework?",
        "options": {
            "A": "A task that calls itself",
            "B": "A task that returns a result",
            "C": "A task that never ends",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Task Granularity'?",
        "options": {
            "A": "The size of the task; if too small, overhead outweighs benefits; if too large, parallelism is wasted",
            "B": "The color of the code",
            "C": "A type of deadlock",
            "D": "A security certificate"
        },
        "answer": "A"
    },
    {
        "question": "Which of these is a 'Synchronizer' aid?",
        "options": {
            "A": "Semaphore",
            "B": "CountDownLatch",
            "C": "CyclicBarrier",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Monitor' in Java?",
        "options": {
            "A": "A computer screen",
            "B": "The synchronization mechanism associated with an object that manages thread entry and exit for synchronized blocks",
            "C": "A type of log file",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Thread.onSpinWait()' introduced in Java 9?",
        "options": {
            "A": "To stop the thread",
            "B": "To hint to the CPU that the current thread is in a spin-loop, allowing for better power management and performance",
            "C": "To start a timer",
            "D": "To refresh the cache"
        },
        "answer": "B"
    },
    {
        "question": "What is 'CompletableFuture.supplyAsync()?'",
        "options": {
            "A": "A way to supply electricity",
            "B": "Static method to run a task that returns a value asynchronously in a separate thread",
            "C": "A type of sharding",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "Which thread pool is used by default for CompletableFuture operations?",
        "options": {
            "A": "ForkJoinPool.commonPool()",
            "B": "newCachedThreadPool()",
            "C": "newFixedThreadPool()",
            "D": "Main thread"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Lock Elision'?",
        "options": {
            "A": "A security attack",
            "B": "A JVM optimization that removes a lock if it determines that the object being locked is never shared across threads",
            "C": "Adding more locks",
            "D": "A type of memory corruption"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'UncaughtExceptionHandler' interface used for?",
        "options": {
            "A": "To prevent all errors",
            "B": "To handle exceptions that are not caught by any try-catch block within a thread",
            "C": "To log method names",
            "D": "To restart the computer"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is an Atomic variable class?",
        "options": {
            "A": "AtomicBoolean",
            "B": "AtomicLong",
            "C": "AtomicReference",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Thread Starvation'?",
        "options": {
            "A": "When a thread has no data to process",
            "B": "When a thread is unable to gain regular access to shared resources and is unable to make progress",
            "C": "A memory leak",
            "D": "A security scan result"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Livelock' vs 'Deadlock'?",
        "options": {
            "A": "Livelock threads are not blocked but keep responding to each other without making progress; Deadlock threads are stuck",
            "B": "Deadlock is faster",
            "C": "They are the same",
            "D": "Livelock only happens on Linux"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Thread Local' overhead?",
        "options": {
            "A": "The extra memory used by each thread to store its own copy of a variable",
            "B": "The time it takes to create a thread",
            "C": "A performance metric",
            "D": "A type of sharding"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Copy-on-Write' strategy?",
        "options": {
            "A": "Writing data twice",
            "B": "An optimization where the system copies the entire underlying data structure only when a write operation occurs",
            "C": "A type of sharding",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "Which class implements a thread-safe, array-based implementation of a deque (double-ended queue)?",
        "options": {
            "A": "ConcurrentLinkedDeque",
            "B": "ArrayDeque (it is NOT thread-safe)",
            "C": "LinkedBlockingDeque",
            "D": "Both A and C"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Instruction Pipelining' in CPU?",
        "options": {
            "A": "A hardware technique where multiple instructions are overlapped in execution",
            "B": "A type of code sorting",
            "C": "A security attack",
            "D": "A performance report"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Cache Line'?",
        "options": {
            "A": "A phone line for data",
            "B": "The basic unit of data transfer between the main memory and the CPU cache",
            "C": "A type of sharding",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Memory Visibility' problem?",
        "options": {
            "A": "When a thread cannot see the RAM",
            "B": "When a change made to memory by one CPU is not immediately visible to other CPUs due to local caching",
            "C": "A type of unit test",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "Which class is the root for building custom synchronizers by managing an internal 'state' integer?",
        "options": {
            "A": "AbstractQueuedSynchronizer (AQS)",
            "B": "SynchronizerBase",
            "C": "LockSupport",
            "D": "StateLock"
        },
        "answer": "A"
    },
    {
        "question": "What is the 'Condition' interface used for?",
        "options": {
            "A": "To check the weather",
            "B": "To provide a way for a thread to suspend execution until notified by another thread (replaces wait/notify for Lock objects)",
            "C": "To set the thread priority",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Park' and 'Unpark' in LockSupport?",
        "options": {
            "A": "Parking a car",
            "B": "Low-level thread blocking and unblocking primitives used to build high-level synchronizers",
            "C": "Stopping the computer",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Heavyweight Lock' in JVM?",
        "options": {
            "A": "A lock that uses a lot of memory",
            "B": "A lock that involves the OS-level mutex and context switching (occurs after contention is detected)",
            "C": "A security scan result",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Lightweight Lock' in JVM?",
        "options": {
            "A": "A lock for small programs",
            "B": "An optimization for locks that are not contended, usually involving simple CAS operations on the object header",
            "C": "A performance report",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'ABA' problem specifically related to?",
        "options": {
            "A": "Atomic operations like Compare-And-Swap (CAS)",
            "B": "Synchronized blocks",
            "C": "Volatile variables",
            "D": "Thread priorities"
        },
        "answer": "A"
    },
    {
        "question": "Which class is used to execute a set of tasks and wait for the 'first' one to complete?",
        "options": {
            "A": "ExecutorService.invokeAny()",
            "B": "ExecutorService.invokeAll()",
            "C": "CompletableFuture.anyOf()",
            "D": "Both A and C"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Thread Group' (deprecated concept)?",
        "options": {
            "A": "A way to organize threads into a hierarchy (no longer recommended)",
            "B": "A team of developers",
            "C": "A type of sharding",
            "D": "A security scan result"
        },
        "answer": "A"
    },
    {
        "question": "Final Expert Question: In Project Loom, virtual threads are 'mounted' on ______ threads.",
        "options": {
            "A": "Carrier",
            "B": "Master",
            "C": "Parent",
            "D": "Global"
        },
        "answer": "A"
    },
    {
        "question": "What is the 'Lost Update' problem in multithreading?",
        "options": {
            "A": "When a thread deletes a file by mistake",
            "B": "When two threads read, increment, and write back a value, but one update overwrites the other due to lack of atomicity",
            "C": "When the JVM fails to log an error",
            "D": "A memory leak in the thread pool"
        },
        "answer": "B"
    },
    {
        "question": "Which JVM optimization moves a 'synchronized' lock from an object header to the thread's stack when no contention is detected?",
        "options": {
            "A": "Biased Locking",
            "B": "Lightweight Locking",
            "C": "Lock Coarsening",
            "D": "Heavyweight Locking"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'MESI Protocol' in the context of CPU cache coherence?",
        "options": {
            "A": "A protocol for sending emails",
            "B": "A hardware protocol (Modified, Exclusive, Shared, Invalid) used to maintain consistency between local caches of different CPU cores",
            "C": "A type of unit test",
            "D": "A security encryption method"
        },
        "answer": "B"
    },
    {
        "question": "In Java 21+, what happens to a 'Virtual Thread' when it performs a blocking I/O operation?",
        "options": {
            "A": "The OS thread is blocked",
            "B": "The virtual thread is 'unmounted' from its carrier thread, allowing the carrier to execute other virtual threads",
            "C": "The JVM terminates the thread",
            "D": "The operation is converted to a non-blocking call automatically"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'VarHandle' introduced in Java 9?",
        "options": {
            "A": "To handle variables in JavaScript",
            "B": "A safer and more efficient alternative to 'java.util.concurrent.atomic' and 'sun.misc.Unsafe' for fine-grained variable access",
            "C": "To create variable-sized arrays",
            "D": "A type of sharding"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Lock Elision'?",
        "options": {
            "A": "Adding extra locks for safety",
            "B": "The compiler optimization of removing a lock when it can prove that the object is only accessible by a single thread",
            "C": "A type of deadlock",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Thread-Safe Leak'?",
        "options": {
            "A": "A thread that is too safe",
            "B": "When a ThreadLocal variable is not removed after use, preventing the value (and the thread's ClassLoader) from being garbage collected",
            "C": "A type of sharding",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Which method in a 'Phaser' allows a thread to arrive and leave without waiting for others?",
        "options": {
            "A": "arriveAndDeregister()",
            "B": "arriveAndAwaitAdvance()",
            "C": "arrive()",
            "D": "leave()"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Pipeline Parallelism'?",
        "options": {
            "A": "Parallelizing tasks by breaking them into stages where each stage is handled by a different thread",
            "B": "Running tests on Jenkins",
            "C": "A type of sharding",
            "D": "A security scan"
        },
        "answer": "A"
    },
    {
        "question": "Final Question: Which memory effect ensures that a 'final' field is seen as fully initialized by all threads after the constructor finishes?",
        "options": {
            "A": "Freeze Guarantee",
            "B": "Volatile Guarantee",
            "C": "Atomic Guarantee",
            "D": "Wait Guarantee"
        },
        "answer": "A"
    },
    {
        "question": "When designing a high-throughput monitoring system for VerifiHire AI, why would you choose 'LongAdder' over 'AtomicLong' for a global request counter?",
        "options": {
            "A": "LongAdder uses a synchronized block internally for better safety",
            "B": "LongAdder reduces CPU cache contention (lock stripping) by maintaining a cellular array of variables that are summed only when needed",
            "C": "AtomicLong does not support increments in a multithreaded environment",
            "D": "LongAdder requires significantly less memory than AtomicLong"
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
    skill = "Multithreading"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
