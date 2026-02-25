from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
  {
    "question": "What is the core concept of RxJS?",
    "options": {
      "A": "A new type of HTML element",
      "B": "Managing asynchronous data streams using Observables",
      "C": "A replacement for the Redux store",
      "D": "A tool for physical hardware networking"
    },
    "answer": "B"
  },
  {
    "question": "What is an 'Observable' in RxJS?",
    "options": {
      "A": "A function that runs only once",
      "B": "An invokable collection of future values or events",
      "C": "A type of database record",
      "D": "A synchronous variable"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used to start receiving data from an Observable?",
    "options": {
      "A": "listen()",
      "B": "subscribe()",
      "C": "fetch()",
      "D": "start()"
    },
    "answer": "B"
  },
  {
    "question": "What are the three callbacks an 'Observer' can receive?",
    "options": {
      "A": "start, stop, error",
      "B": "next, error, complete",
      "C": "data, failure, finish",
      "D": "load, update, delete"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Cold Observable'?",
    "options": {
      "A": "An observable that runs in the background",
      "B": "An observable that starts its execution only when a subscriber is attached",
      "C": "An observable that has failed",
      "D": "An observable that returns only numbers"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Hot Observable'?",
    "options": {
      "A": "An observable that runs very fast",
      "B": "An observable that produces values even if no one is subscribed (like a mouse click stream)",
      "C": "An observable that uses a lot of CPU",
      "D": "A synchronous observable"
    },
    "answer": "B"
  },
  {
    "question": "Which operator is used to create an Observable from an array, promise, or iterable?",
    "options": {
      "A": "of()",
      "B": "from()",
      "C": "create()",
      "D": "just()"
    },
    "answer": "B"
  },
  {
    "question": "What is the difference between 'of()' and 'from()'?",
    "options": {
      "A": "of() is for strings; from() is for numbers",
      "B": "of() emits arguments as a sequence; from() flattens an array or promise into a sequence",
      "C": "from() is faster than of()",
      "D": "There is no difference"
    },
    "answer": "B"
  },
  {
    "question": "What does a 'Subscription' represent in RxJS?",
    "options": {
      "A": "A payment for the library",
      "B": "An object that represents the execution of an Observable, primarily used to cancel it",
      "C": "The total number of users",
      "D": "A type of database connection"
    },
    "answer": "B"
  },
  {
    "question": "Which operator is used to emit a sequence of numbers in a range?",
    "options": {
      "A": "interval()",
      "B": "range()",
      "C": "timer()",
      "D": "sequence()"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'pipe()' method?",
    "options": {
      "A": "To output data to the console",
      "B": "To chain multiple operators together to transform a stream",
      "C": "To close the observable",
      "D": "To manage app memory"
    },
    "answer": "B"
  },
  {
    "question": "What happens when an Observable encounters an 'error'?",
    "options": {
      "A": "It restarts automatically",
      "B": "It immediately terminates and stops emitting further values",
      "C": "It skips the error and continues",
      "D": "It deletes the subscriber"
    },
    "answer": "B"
  },
  {
    "question": "Which creation operator emits a value every fixed time interval?",
    "options": {
      "A": "timer()",
      "B": "interval()",
      "C": "delay()",
      "D": "repeat()"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Subscription.unsubscribe()' method used for?",
    "options": {
      "A": "To pause the observable",
      "B": "To stop the execution and prevent memory leaks",
      "C": "To delete the variable",
      "D": "To refresh the page"
    },
    "answer": "B"
  },
  {
    "question": "Which operator turns an event (like a DOM button click) into an Observable?",
    "options": {
      "A": "fromEvent()",
      "B": "observeEvent()",
      "C": "onClick()",
      "D": "eventStream()"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Reactive Programming'?",
    "options": {
      "A": "Programming that reacts to user feedback",
      "B": "A declarative paradigm concerned with data streams and the propagation of change",
      "C": "Programming with only React.js",
      "D": "Programming that is very fast"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Observer' in RxJS?",
    "options": {
      "A": "A person watching the screen",
      "B": "A consumer of values delivered by an Observable (an object with next, error, complete methods)",
      "C": "A type of database index",
      "D": "A network monitor"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Pull' vs 'Push' system in programming?",
    "options": {
      "A": "Pull is for data; Push is for UI",
      "B": "In Pull, the Consumer decides when to receive data (Functions); in Push, the Producer decides (Observables)",
      "C": "Push is faster than Pull",
      "D": "Pull is for mobile; Push is for web"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Teardown' logic in an Observable?",
    "options": {
      "A": "Logic to delete the app",
      "B": "A function returned by the observable to clean up resources (like clearing a timeout) upon unsubscription",
      "C": "An error message",
      "D": "The end of a loop"
    },
    "answer": "B"
  },
  {
    "question": "Which operator creates an Observable that emits nothing and then completes?",
    "options": {
      "A": "never()",
      "B": "empty() (now replaced by EMPTY constants)",
      "C": "throwError()",
      "D": "null()"
    },
    "answer": "B"
  },
  {
    "question": "Which operator creates an Observable that emits nothing and never completes?",
    "options": {
      "A": "empty()",
      "B": "NEVER",
      "C": "null()",
      "D": "stop()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Stream' in RxJS?",
    "options": {
      "A": "A video on YouTube",
      "B": "A sequence of data elements made available over time",
      "C": "A network connection",
      "D": "A type of variable"
    },
    "answer": "B"
  },
  {
    "question": "Which creation operator emits a single value after a delay?",
    "options": {
      "A": "interval()",
      "B": "timer()",
      "C": "delay()",
      "D": "once()"
    },
    "answer": "B"
  },
  {
    "question": "How do you handle a 'Complete' notification in a subscription?",
    "options": {
      "A": "Using the error callback",
      "B": "Using the third callback argument in the subscribe method",
      "C": "Using the finish() method",
      "D": "By deleting the subscription"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Producer' in RxJS?",
    "options": {
      "A": "The developer",
      "B": "The Observable that generates the data",
      "C": "The browser",
      "D": "The server"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Multicasting'?",
    "options": {
      "A": "Sending data to many servers",
      "B": "Sharing a single Observable execution among multiple subscribers",
      "C": "Playing audio in the app",
      "D": "A type of UI theme"
    },
    "answer": "B"
  },
  {
    "question": "Which creation operator emits a value and then completes immediately?",
    "options": {
      "A": "just() (generic term) / of() in RxJS",
      "B": "one()",
      "C": "single()",
      "D": "fast()"
    },
    "answer": "A"
  },
  {
    "question": "What happens if an Observable emits values before a subscriber joins?",
    "options": {
      "A": "The values are saved forever",
      "B": "In Cold Observables, they are never emitted until a subscriber joins; in Hot, they may be lost if not buffered",
      "C": "The app crashes",
      "D": "The subscriber is blocked"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Functional Programming' influence on RxJS?",
    "options": {
      "A": "It has no influence",
      "B": "RxJS uses pure functions (operators) to transform streams without changing the original data",
      "C": "It makes RxJS only for math",
      "D": "It requires using 'class' keywords"
    },
    "answer": "B"
  },
  {
    "question": "Which creation operator creates an Observable from a variable number of arguments?",
    "options": {
      "A": "from()",
      "B": "of()",
      "C": "concat()",
      "D": "list()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Declarative' vs 'Imperative' in RxJS?",
    "options": {
      "A": "Declarative is 'how'; Imperative is 'what'",
      "B": "RxJS is Declarative (defining what the stream should look like via operators) rather than Imperative (looping and modifying)",
      "C": "They are the same",
      "D": "Imperative is for mobile"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Laziness' in RxJS Observables?",
    "options": {
      "A": "The library is slow",
      "B": "Observables don't do anything until you subscribe to them",
      "C": "The developer doesn't write code",
      "D": "A database tool"
    },
    "answer": "B"
  },
  {
    "question": "Which creation operator turns a promise into an observable?",
    "options": {
      "A": "from()",
      "B": "of()",
      "C": "promise()",
      "D": "async()"
    },
    "answer": "A"
  },
  {
    "question": "How do you emit multiple values manually in a custom Observable?",
    "options": {
      "A": "Using return statements",
      "B": "Using subscriber.next(value) multiple times",
      "C": "By restarting the subscription",
      "D": "Using a global variable"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Subscription.add()' method?",
    "options": {
      "A": "Adding more data",
      "B": "Adding a child subscription to a parent, so unsubscribing from the parent cancels both",
      "C": "A mathematical operator",
      "D": "A network protocol"
    },
    "answer": "B"
  },
  {
    "question": "Which operator generates a stream that throws an error immediately upon subscription?",
    "options": {
      "A": "error()",
      "B": "throwError()",
      "C": "fail()",
      "D": "crash()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Memory Leak' risk in RxJS?",
    "options": {
      "A": "The app uses too much internet",
      "B": "Failing to unsubscribe from long-lived observables when a component is destroyed",
      "C": "A database error",
      "D": "A type of loop"
    },
    "answer": "B"
  },
  {
    "question": "In RxJS, 'Observables' are similar to which pattern?",
    "options": {
      "A": "Singleton",
      "B": "Observer Pattern",
      "C": "Factory Pattern",
      "D": "Prototype"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Asynchronous' data in RxJS?",
    "options": {
      "A": "Data that arrives all at once",
      "B": "Data that arrives at unpredictable intervals (like clicks, API responses)",
      "C": "Data only from the server",
      "D": "Data for mobile apps"
    },
    "answer": "B"
  },
  {
    "question": "Which method on the subscriber is called when there is no more data to emit?",
    "options": {
      "A": "finish()",
      "B": "complete()",
      "C": "stop()",
      "D": "close()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'AjaxObservable'?",
    "options": {
      "A": "A tool to wash the computer",
      "B": "A specialized observable for making HTTP requests (ajax())",
      "C": "A type of UI theme",
      "D": "A network protocol"
    },
    "answer": "B"
  },
  {
    "question": "What is 'defer()' operator used for?",
    "options": {
      "A": "To pause the stream",
      "B": "To create an observable only when a subscriber joins, ensuring fresh data for each subscriber",
      "C": "To delete a stream",
      "D": "A security setting"
    },
    "answer": "B"
  },
  {
    "question": "Can an Observable emit values after calling 'complete()'?",
    "options": {
      "A": "Yes",
      "B": "No, once complete is called, the stream is finished and won't emit again",
      "C": "Only if there is an error",
      "D": "Only in development"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Unicast' in Observables?",
    "options": {
      "A": "The default behavior where each subscriber gets their own independent execution of the observable",
      "B": "Sending data to one user",
      "C": "Using one language",
      "D": "A type of network call"
    },
    "answer": "A"
  },
  {
    "question": "Which operator is the building block for all other operators in RxJS internally?",
    "options": {
      "A": "map()",
      "B": "lift() (Note: mostly internal usage)",
      "C": "subscribe()",
      "D": "pipe()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Subscriber' interface?",
    "options": {
      "A": "The person using the app",
      "B": "The object that implements Observer and Subscription to handle the internal data flow",
      "C": "A database table",
      "D": "A UI component"
    },
    "answer": "B"
  },
  {
    "question": "What is the return type of the 'subscribe()' method?",
    "options": {
      "A": "void",
      "B": "Subscription",
      "C": "Observable",
      "D": "Promise"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Scheduling' in RxJS?",
    "options": {
      "A": "Setting a meeting",
      "B": "Controlling the timing and context of when notifications are delivered (e.g., asap, async, queue)",
      "C": "Managing project dates",
      "D": "A network protocol"
    },
    "answer": "B"
  },
  {
    "question": "What is 'VerifiHire AI's' focus for RxJS candidates?",
    "options": {
      "A": "Writing loops",
      "B": "Ensuring high-quality management of complex asynchronous data streams and event logic",
      "C": "Avoiding JavaScript",
      "D": "Only using React state"
    },
    "answer": "B"
  },
  {
    "question": "Which creation operator combines multiple Observables and emits only when all of them complete?",
    "options": {
      "A": "forkJoin()",
      "B": "concat()",
      "C": "merge()",
      "D": "zip()"
    },
    "answer": "A"
  },
  {
    "question": "Which operator is used to apply a projection function to each value emitted by the source Observable?",
    "options": {
      "A": "filter()",
      "B": "map()",
      "C": "scan()",
      "D": "tap()"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary purpose of the 'filter()' operator?",
    "options": {
      "A": "To change the values in the stream",
      "B": "To only emit values from the source that pass a specific predicate test",
      "C": "To stop the stream after 5 seconds",
      "D": "To log data to the console"
    },
    "answer": "B"
  },
  {
    "question": "Which operator emits only the first 'n' values emitted by the source?",
    "options": {
      "A": "first()",
      "B": "take()",
      "C": "limit()",
      "D": "skip()"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'debounceTime()' operator do?",
    "options": {
      "A": "It slows down the CPU",
      "B": "It only emits a value from the source if a particular time span has passed without another source emission",
      "C": "It repeats the value multiple times",
      "D": "It adds a delay to every single emission"
    },
    "answer": "B"
  },
  {
    "question": "Which operator is best for handling a search input to avoid making an API call for every keystroke?",
    "options": {
      "A": "throttleTime()",
      "B": "debounceTime()",
      "C": "delay()",
      "D": "buffer()"
    },
    "answer": "B"
  },
  {
    "question": "What is the difference between 'map()' and 'pluck()' (Note: pluck is deprecated in RxJS 7+)?",
    "options": {
      "A": "map() is for numbers; pluck() is for objects",
      "B": "map() takes a function; pluck() takes a string property name to extract a value from an object",
      "C": "pluck() is faster than map()",
      "D": "There is no difference"
    },
    "answer": "B"
  },
  {
    "question": "Which operator is useful for side effects, like logging, without affecting the stream itself?",
    "options": {
      "A": "map()",
      "B": "tap()",
      "C": "subscribe()",
      "D": "scan()"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'scan()' operator equivalent to in standard JavaScript?",
    "options": {
      "A": "Array.prototype.map()",
      "B": "Array.prototype.reduce() (but it emits the intermediate totals)",
      "C": "Array.prototype.filter()",
      "D": "Array.prototype.forEach()"
    },
    "answer": "B"
  },
  {
    "question": "Which operator emits only the last value emitted by the source before it completes?",
    "options": {
      "A": "last()",
      "B": "takeLast(1)",
      "C": "Both A and B",
      "D": "end()"
    },
    "answer": "C"
  },
  {
    "question": "What does 'distinctUntilChanged()' do?",
    "options": {
      "A": "It only emits values that are different from the previous value",
      "B": "It makes sure all values in the stream are unique",
      "C": "It renames the values",
      "D": "It clears the stream cache"
    },
    "answer": "A"
  },
  {
    "question": "Which operator ignores the first 'n' values emitted by the source?",
    "options": {
      "A": "take()",
      "B": "skip()",
      "C": "ignore()",
      "D": "drop()"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'throttleTime()'?",
    "options": {
      "A": "To speed up the network",
      "B": "To emit a value, then ignore subsequent values for a duration, then repeat the process",
      "C": "To stop the app from running",
      "D": "To encrypt the data stream"
    },
    "answer": "B"
  },
  {
    "question": "Which operator collects values into an array and emits that array when it reaches a certain size?",
    "options": {
      "A": "group()",
      "B": "bufferCount()",
      "C": "toArray()",
      "D": "collect()"
    },
    "answer": "B"
  },
  {
    "question": "What is the difference between 'scan()' and 'reduce()' in RxJS?",
    "options": {
      "A": "scan() is for numbers only",
      "B": "scan() emits every intermediate state; reduce() only emits the final result upon completion",
      "C": "reduce() is faster",
      "D": "scan() is deprecated"
    },
    "answer": "B"
  },
  {
    "question": "Which operator emits values only when a second Observable emits?",
    "options": {
      "A": "takeUntil()",
      "B": "sample()",
      "C": "audit()",
      "D": "watch()"
    },
    "answer": "B"
  },
  {
    "question": "What does 'takeUntil()' do?",
    "options": {
      "A": "It takes values until the user clicks a button",
      "B": "It emits values from the source until a notifier Observable emits a value",
      "C": "It limits the stream to 10 seconds",
      "D": "It waits for a promise to resolve"
    },
    "answer": "B"
  },
  {
    "question": "Which operator transforms each value into a constant value?",
    "options": {
      "A": "mapTo() (Note: deprecated in favor of map(() => value))",
      "B": "const()",
      "C": "fix()",
      "D": "static()"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'auditTime()' operator?",
    "options": {
      "A": "A tool to check for bugs",
      "B": "It ignores values for a duration, then emits the most recent value, then repeats",
      "C": "It logs the time of each emission",
      "D": "It checks user permissions"
    },
    "answer": "B"
  },
  {
    "question": "Which operator emits only the first value that passes a condition and then completes?",
    "options": {
      "A": "take(1)",
      "B": "find()",
      "C": "first()",
      "D": "All of the above"
    },
    "answer": "D"
  },
  {
    "question": "What does 'skipWhile()' do?",
    "options": {
      "A": "It skips values as long as a condition is true, then emits everything thereafter",
      "B": "It skips only every second value",
      "C": "It skips values until a timer ends",
      "D": "It stops the observable"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'map' operator's marble diagram representation?",
    "options": {
      "A": "A circle turning into a square based on a function",
      "B": "A line being cut in half",
      "C": "Two lines merging",
      "D": "A circle disappearing"
    },
    "answer": "A"
  },
  {
    "question": "Which operator is used to 'flatten' an Observable of Observables?",
    "options": {
      "A": "map()",
      "B": "mergeMap()",
      "C": "flatten()",
      "D": "reduce()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'distinct()'?",
    "options": {
      "A": "It emits only values that haven't been seen before in the entire lifetime of the stream",
      "B": "It emits only strings",
      "C": "It removes null values",
      "D": "It renames the observable"
    },
    "answer": "A"
  },
  {
    "question": "Which operator emits the most recent value from the source since the previous sampling?",
    "options": {
      "A": "sampleTime()",
      "B": "throttleTime()",
      "C": "debounceTime()",
      "D": "delay()"
    },
    "answer": "A"
  },
  {
    "question": "What happens if 'first()' is called on a stream that completes without emitting any values?",
    "options": {
      "A": "It returns null",
      "B": "It throws an EmptyError",
      "C": "It stays pending forever",
      "D": "It returns undefined"
    },
    "answer": "B"
  },
  {
    "question": "What is the difference between 'throttleTime()' and 'debounceTime()'?",
    "options": {
      "A": "Throttle emits the first value; Debounce waits for a pause to emit the last value",
      "B": "Throttle is for mobile; Debounce is for web",
      "C": "Debounce is faster",
      "D": "They are the same"
    },
    "answer": "A"
  },
  {
    "question": "Which operator is used to 'peek' at the stream for debugging without changing the data?",
    "options": {
      "A": "log()",
      "B": "tap()",
      "C": "spy()",
      "D": "watch()"
    },
    "answer": "B"
  },
  {
    "question": "What does 'single()' do?",
    "options": {
      "A": "Emits only one value ever",
      "B": "Emits the single value that matches a predicate and errors if more than one matches",
      "C": "Converts the stream to a promise",
      "D": "Makes the stream run on one thread"
    },
    "answer": "B"
  },
  {
    "question": "Which operator skips values from the source until a second Observable emits?",
    "options": {
      "A": "skipUntil()",
      "B": "wait()",
      "C": "delay()",
      "D": "ignoreUntil()"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'bufferTime()' operator?",
    "options": {
      "A": "It slows down the stream",
      "B": "It collects values for a specific time window and emits them as an array",
      "C": "It adds a delay to the whole app",
      "D": "It manages memory cache"
    },
    "answer": "B"
  },
  {
    "question": "Which operator converts a stream of values into a stream of 'Notification' objects (next, error, complete)?",
    "options": {
      "A": "notify()",
      "B": "materialize()",
      "C": "objectify()",
      "D": "wrap()"
    },
    "answer": "B"
  },
  {
    "question": "What does 'takeWhile()' do?",
    "options": {
      "A": "Emits values as long as they pass a condition, then completes the stream immediately when one fails",
      "B": "Takes values while the user is active",
      "C": "Takes values while the network is up",
      "D": "A loop that never ends"
    },
    "answer": "A"
  },
  {
    "question": "What is 'ignoreElements()'?",
    "options": {
      "A": "Deletes all elements in the app",
      "B": "Ignores all 'next' emissions and only passes through 'error' or 'complete' notifications",
      "C": "Hides the UI",
      "D": "Speeds up the CPU"
    },
    "answer": "B"
  },
  {
    "question": "Which operator emits a value from the source, then ignores for a duration, then emits the *last* value that arrived during that duration?",
    "options": {
      "A": "throttleTime(duration, { trailing: true })",
      "B": "debounceTime()",
      "C": "sampleTime()",
      "D": "auditTime()"
    },
    "answer": "A"
  },
  {
    "question": "In 'map(x => x * 10)', if the source emits 1, 2, 3, what is the output?",
    "options": {
      "A": "1, 2, 3",
      "B": "10, 20, 30",
      "C": "[10, 20, 30]",
      "D": "60"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'elementAt(i)'?",
    "options": {
      "A": "To find all elements with index i",
      "B": "To emit only the value at a specific index in the sequence",
      "C": "To count the elements",
      "D": "To delete an element"
    },
    "answer": "B"
  },
  {
    "question": "Which operator emits a notification when the source Observable completes?",
    "options": {
      "A": "onComplete()",
      "B": "tap({ complete: () => ... })",
      "C": "finalize()",
      "D": "Both B and C"
    },
    "answer": "D"
  },
  {
    "question": "What is 'pairwise()'?",
    "options": {
      "A": "It groups values into pairs of [previous, current] and emits them as an array",
      "B": "It only allows two subscribers",
      "C": "It doubles every value",
      "D": "It renames the observable"
    },
    "answer": "A"
  },
  {
    "question": "Which operator is best for ensuring a value is only emitted after the user has stopped typing for 300ms?",
    "options": {
      "A": "throttleTime(300)",
      "B": "debounceTime(300)",
      "C": "delay(300)",
      "D": "sampleTime(300)"
    },
    "answer": "B"
  },
  {
    "question": "What does 'every()' do in RxJS?",
    "options": {
      "A": "Emits every value in the stream",
      "B": "Returns an Observable of a boolean indicating if all emitted values pass a condition",
      "C": "Runs a function on every value",
      "D": "A loop that never ends"
    },
    "answer": "B"
  },
  {
    "question": "Which operator emits only the values from the source that are not 'null' or 'undefined'?",
    "options": {
      "A": "clean()",
      "B": "filter(val => val != null)",
      "C": "compact()",
      "D": "real()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'buffer()'?",
    "options": {
      "A": "A tool to wash the stream",
      "B": "Collects values into an array until a provided 'closing' Observable emits",
      "C": "Adds a delay",
      "D": "A type of UI theme"
    },
    "answer": "B"
  },
  {
    "question": "What is 'dematerialize()'?",
    "options": {
      "A": "Deletes the observable",
      "B": "Converts a stream of Notification objects back into a stream of actual values",
      "C": "Hides the UI",
      "D": "Speeds up the CPU"
    },
    "answer": "B"
  },
  {
    "question": "Which operator is used to 'summarize' the entire stream into a single value once it completes?",
    "options": {
      "A": "scan()",
      "B": "reduce()",
      "C": "map()",
      "D": "sum()"
    },
    "answer": "B"
  },
  {
    "question": "What happens if 'last()' is called and the stream never completes?",
    "options": {
      "A": "It returns the most recent value",
      "B": "It never emits a value",
      "C": "It throws an error immediately",
      "D": "It returns null"
    },
    "answer": "B"
  },
  {
    "question": "What is 'pluck('name')' equivalent to in modern RxJS?",
    "options": {
      "A": "map(x => x.name)",
      "B": "filter(x => x.name)",
      "C": "tap(x => x.name)",
      "D": "select('name')"
    },
    "answer": "A"
  },
  {
    "question": "Which operator 'starts' the stream with a specific value before any source values are emitted?",
    "options": {
      "A": "init()",
      "B": "startWith()",
      "C": "prefix()",
      "D": "prepend()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'toArray()'?",
    "options": {
      "A": "Converts every value to an array",
      "B": "Collects all values from a stream and emits them as a single array when the stream completes",
      "C": "A type of variable",
      "D": "A database query"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'defaultIfEmpty(value)'?",
    "options": {
      "A": "To set the default UI theme",
      "B": "To emit a specific value if the source completes without emitting anything",
      "C": "To handle errors",
      "D": "To restart the stream"
    },
    "answer": "B"
  },
  {
    "question": "What is 'RxJS' final goal for stream transformation?",
    "options": {
      "A": "To make data static",
      "B": "To provide a powerful, functional way to shape asynchronous data exactly as the UI needs it",
      "C": "To write more code",
      "D": "To avoid using functions"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Flattening Operator' in RxJS?",
    "options": {
      "A": "An operator that reduces the size of a JSON object",
      "B": "An operator that maps each value to an inner Observable and then flattens the result into a single stream",
      "C": "A tool to delete nested arrays",
      "D": "A way to compress the application's memory"
    },
    "answer": "B"
  },
  {
    "question": "Which flattening operator is best for search-as-you-type because it cancels the previous inner Observable when a new value arrives?",
    "options": {
      "A": "mergeMap",
      "B": "switchMap",
      "C": "concatMap",
      "D": "exhaustMap"
    },
    "answer": "B"
  },
  {
    "question": "What is the behavior of 'mergeMap' (also known as flatMap)?",
    "options": {
      "A": "It processes inner Observables in parallel as they arrive",
      "B": "It waits for the first one to finish before starting the next",
      "C": "It cancels the previous one immediately",
      "D": "It ignores all new values until the current one finishes"
    },
    "answer": "A"
  },
  {
    "question": "Which operator ensures that inner Observables are executed in strict sequential order?",
    "options": {
      "A": "mergeMap",
      "B": "concatMap",
      "C": "switchMap",
      "D": "exhaustMap"
    },
    "answer": "B"
  },
  {
    "question": "What does 'exhaustMap' do when a new value arrives while an inner Observable is still running?",
    "options": {
      "A": "It queues the value",
      "B": "It ignores (drops) the new value until the current inner Observable completes",
      "C": "It cancels the current one",
      "D": "It runs them in parallel"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Subject' in RxJS?",
    "options": {
      "A": "A topic for discussion",
      "B": "A special type of Observable that allows values to be multicasted to many Observers (it is both an Observable and an Observer)",
      "C": "A private variable",
      "D": "A network protocol"
    },
    "answer": "B"
  },
  {
    "question": "What is the key difference between a regular Observable and a Subject?",
    "options": {
      "A": "Observables are faster",
      "B": "Observables are unicast (each subscriber gets a new execution); Subjects are multicast",
      "C": "Subjects can only emit strings",
      "D": "Observables cannot be canceled"
    },
    "answer": "B"
  },
  {
    "question": "Which type of Subject requires an initial value and emits its current value to new subscribers immediately?",
    "options": {
      "A": "Subject",
      "B": "BehaviorSubject",
      "C": "ReplaySubject",
      "D": "AsyncSubject"
    },
    "answer": "B"
  },
  {
    "question": "What does 'ReplaySubject(3)' do?",
    "options": {
      "A": "It plays the stream 3 times",
      "B": "It records the last 3 emitted values and replays them to any new subscriber",
      "C": "It waits for 3 subscribers before starting",
      "D": "It deletes the first 3 values"
    },
    "answer": "B"
  },
  {
    "question": "When does 'AsyncSubject' emit values to its subscribers?",
    "options": {
      "A": "Immediately as they arrive",
      "B": "Only when the execution completes, and it only emits the last value",
      "C": "Every 5 seconds",
      "D": "Only if there is an error"
    },
    "answer": "B"
  },
  {
    "question": "How do you manually push a new value into a Subject?",
    "options": {
      "A": "subject.push(value)",
      "B": "subject.next(value)",
      "C": "subject.emit(value)",
      "D": "subject.send(value)"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Cold to Hot' conversion in RxJS?",
    "options": {
      "A": "Upgrading the library",
      "B": "Converting a unicast observable into a multicast one, typically using the 'share()' operator",
      "C": "A way to speed up the CPU",
      "D": "A network security tool"
    },
    "answer": "B"
  },
  {
    "question": "Which operator is a combination of 'tap', 'map', and 'multicast' to share a side-effecting execution?",
    "options": {
      "A": "share()",
      "B": "connect()",
      "C": "publish()",
      "D": "group()"
    },
    "answer": "A"
  },
  {
    "question": "What happens to a Subject once 'complete()' is called?",
    "options": {
      "A": "It restarts",
      "B": "It will no longer emit any values and will notify all current and future subscribers that it is complete",
      "C": "It throws an error",
      "D": "It deletes all subscribers"
    },
    "answer": "B"
  },
  {
    "question": "Which operator is best for a 'Login' button to prevent multiple clicks from triggering multiple API calls simultaneously?",
    "options": {
      "A": "mergeMap",
      "B": "exhaustMap",
      "C": "switchMap",
      "D": "concatMap"
    },
    "answer": "B"
  },
  {
    "question": "What is the risk of using 'mergeMap' with an infinite inner Observable?",
    "options": {
      "A": "The app will run faster",
      "B": "It can lead to a memory leak as more and more inner Observables are created and never completed",
      "C": "The first one will be cancelled",
      "D": "It is not allowed"
    },
    "answer": "B"
  },
  {
    "question": "How can you access the current value of a 'BehaviorSubject' without subscribing?",
    "options": {
      "A": "subject.current",
      "B": "subject.getValue()",
      "C": "subject.value",
      "D": "Both B and C"
    },
    "answer": "D"
  },
  {
    "question": "Which operator is used to 'wait' for multiple Observables to emit and then combine their last values into an array?",
    "options": {
      "A": "combineLatest",
      "B": "withLatestFrom",
      "C": "zip",
      "D": "merge"
    },
    "answer": "A"
  },
  {
    "question": "What is the difference between 'combineLatest' and 'zip'?",
    "options": {
      "A": "combineLatest is for strings",
      "B": "zip combines values based on index (1st with 1st); combineLatest combines the latest values whenever any source emits",
      "C": "zip is faster",
      "D": "They are the same"
    },
    "answer": "B"
  },
  {
    "question": "Which operator is used to 'merge' multiple Observables into one, emitting values from all of them as they arrive?",
    "options": {
      "A": "concat",
      "B": "merge",
      "C": "race",
      "D": "forkJoin"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'race()' operator do?",
    "options": {
      "A": "It speeds up the app",
      "B": "It subscribes to multiple Observables and only keeps the one that emits first, canceling the others",
      "C": "A competition between developers",
      "D": "A database tool"
    },
    "answer": "B"
  },
  {
    "question": "Which operator works like 'combineLatest' but is used as a pipeable operator on a source stream?",
    "options": {
      "A": "withLatestFrom",
      "B": "mergeWith",
      "C": "concatWith",
      "D": "zipWith"
    },
    "answer": "A"
  },
  {
    "question": "What is the purpose of 'forkJoin'?",
    "options": {
      "A": "To split a stream in two",
      "B": "To wait for all provided Observables to complete and then emit their final values as an array (similar to Promise.all)",
      "C": "To restart the app",
      "D": "A type of UI theme"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Higher-order Observable'?",
    "options": {
      "A": "An observable with a lot of code",
      "B": "An Observable that emits other Observables",
      "C": "A private observable",
      "D": "A network protocol"
    },
    "answer": "B"
  },
  {
    "question": "Which operator would you use to 'retry' an Observable execution a specific number of times if it fails?",
    "options": {
      "A": "repeat()",
      "B": "retry()",
      "C": "recover()",
      "D": "backoff()"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'catchError()'?",
    "options": {
      "A": "To stop the app from crashing",
      "B": "To intercept an error in a stream and return a new Observable or re-throw the error",
      "C": "To log the error only",
      "D": "To delete the stream"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Void' Subject usage?",
    "options": {
      "A": "A Subject that doesn't emit data, used purely as a signal that an event happened",
      "B": "An empty subject",
      "C": "A type of error",
      "D": "A database key"
    },
    "answer": "A"
  },
  {
    "question": "In RxJS, what is a 'Marble Diagram'?",
    "options": {
      "A": "A game for developers",
      "B": "A visual representation of how operators transform data over time",
      "C": "A type of database schema",
      "D": "A CSS layout"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Backpressure' in stream processing?",
    "options": {
      "A": "The server being too slow",
      "B": "When the producer generates data faster than the consumer can process it",
      "C": "A network error",
      "D": "A UI lag"
    },
    "answer": "B"
  },
  {
    "question": "Which operator can help manage backpressure by 'ignoring' values for a duration?",
    "options": {
      "A": "map",
      "B": "throttleTime",
      "C": "mergeMap",
      "D": "startWith"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Inner Subscription'?",
    "options": {
      "A": "A subscription inside a function",
      "B": "The subscription created by a flattening operator (like switchMap) to an inner Observable",
      "C": "A private subscriber",
      "D": "A network protocol"
    },
    "answer": "B"
  },
  {
    "question": "What does 'concat' do with multiple Observables?",
    "options": {
      "A": "It runs them all at once",
      "B": "It subscribes to them one by one, waiting for the previous one to complete before starting the next",
      "C": "It merges their values",
      "D": "It chooses the fastest one"
    },
    "answer": "B"
  },
  {
    "question": "What is 'ReplaySubject' windowTime parameter?",
    "options": {
      "A": "How long the app stays open",
      "B": "The maximum age of recorded values that the subject will keep and replay",
      "C": "The time between emissions",
      "D": "A database setting"
    },
    "answer": "B"
  },
  {
    "question": "Which operator allows you to 'switch' to a new Observable based on the value of a previous one?",
    "options": {
      "A": "map",
      "B": "switchMap",
      "C": "concat",
      "D": "merge"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'delayWhen()'?",
    "options": {
      "A": "To delay the app",
      "B": "To delay the emission of values based on a second Observable's signal",
      "C": "To handle network errors",
      "D": "A security setting"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Subject.asObservable()' used for?",
    "options": {
      "A": "To hide the Subject's 'next' and 'error' methods from consumers, exposing only the stream",
      "B": "To convert a Subject to a Promise",
      "C": "To speed up the connection",
      "D": "To rename the Subject"
    },
    "answer": "A"
  },
  {
    "question": "Which operator is best for 'Saving' data to a database where order matters and you don't want to overlap requests?",
    "options": {
      "A": "mergeMap",
      "B": "concatMap",
      "C": "switchMap",
      "D": "exhaustMap"
    },
    "answer": "B"
  },
  {
    "question": "What is 'ConnectableObservable'?",
    "options": {
      "A": "An observable that needs a manual 'connect()' call to start emitting to its subscribers",
      "B": "A type of network cable",
      "C": "A database link",
      "D": "A type of UI theme"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'shareReplay()' operator common use case?",
    "options": {
      "A": "Caching an API response so multiple subscribers get the same cached data without making extra network calls",
      "B": "Sharing files",
      "C": "Repeating an animation",
      "D": "Deleting data"
    },
    "answer": "A"
  },
  {
    "question": "What happens if 'forkJoin' is used on an Observable that never completes?",
    "options": {
      "A": "It emits the last value",
      "B": "It will never emit a value or complete",
      "C": "It throws an error",
      "D": "It returns null"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Scheduler.async'?",
    "options": {
      "A": "A tool to schedule meetings",
      "B": "A scheduler that uses setInterval or setTimeout to run tasks asynchronously in the next event loop",
      "C": "A type of variable",
      "D": "A database tool"
    },
    "answer": "B"
  },
  {
    "question": "Which operator allows you to 'perform' a task when an Observable is subscribed to?",
    "options": {
      "A": "tap()",
      "B": "defer()",
      "C": "finalize()",
      "D": "onSubscribe() (Note: not a standard operator, use defer or tap)"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Subject' statefulness?",
    "options": {
      "A": "Subject is stateless; BehaviorSubject is stateful (it remembers the current value)",
      "B": "All subjects are stateful",
      "C": "No subjects are stateful",
      "D": "Subjects are for mobile"
    },
    "answer": "A"
  },
  {
    "question": "Which operator 'flattens' by always subscribing to the most recent inner Observable and unsubscribing from the previous one?",
    "options": {
      "A": "mergeMap",
      "B": "concatMap",
      "C": "switchMap",
      "D": "exhaustMap"
    },
    "answer": "C"
  },
  {
    "question": "What is the result of 'of(1, 2).pipe(mergeMap(x => of(x, x*10)))'?",
    "options": {
      "A": "1, 2",
      "B": "1, 10, 2, 20",
      "C": "11, 22",
      "D": "[1, 10, 2, 20]"
    },
    "answer": "B"
  },
  {
    "question": "Which operator is best for 'Upload' progress tracking where you want to see every update in order?",
    "options": {
      "A": "mergeMap",
      "B": "concatMap",
      "C": "switchMap",
      "D": "exhaustMap"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Multicasted' Observable lifetime?",
    "options": {
      "A": "It lasts forever",
      "B": "It typically lasts as long as there is at least one subscriber (if using refCount)",
      "C": "It lasts 5 minutes",
      "D": "It depends on the server"
    },
    "answer": "B"
  },
  {
    "question": "What is 'RxJS' final goal for stream combination?",
    "options": {
      "A": "To make data separate",
      "B": "To provide a highly flexible way to coordinate and merge multiple data sources into a single logical flow",
      "C": "To write more code",
      "D": "To avoid using classes"
    },
    "answer": "B"
  },
  {
    "question": "What is 'exhaustAll()'?",
    "options": {
      "A": "Deletes all observables",
      "B": "A flattening operator that applies to a higher-order Observable, ignoring new inner Observables until the current one finishes",
      "C": "Hides the UI",
      "D": "Speeds up the CPU"
    },
    "answer": "B"
  },
  {
    "question": "In RxJS, what is 'The Big Four' of flattening?",
    "options": {
      "A": "Map, Filter, Scan, Tap",
      "B": "switchMap, mergeMap, concatMap, exhaustMap",
      "C": "Of, From, Interval, Timer",
      "D": "Subject, BehaviorSubject, ReplaySubject, AsyncSubject"
    },
    "answer": "B"
  },
  {
    "question": "Which operator is used to intercept an error and provide a fallback Observable to continue the stream?",
    "options": {
      "A": "retry()",
      "B": "catchError()",
      "C": "onErrorResumeNext()",
      "D": "throwError()"
    },
    "answer": "B"
  },
  {
    "question": "In RxJS Marble Testing, what does the 'dash' (-) character represent?",
    "options": {
      "A": "An error",
      "B": "A frame of virtual time passing (usually 1ms or 10ms)",
      "C": "A value emission",
      "D": "The end of the stream"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary difference between 'retry' and 'repeat'?",
    "options": {
      "A": "Retry happens on error; Repeat happens on completion",
      "B": "Repeat is for mobile; Retry is for web",
      "C": "Retry is faster",
      "D": "There is no difference"
    },
    "answer": "A"
  },
  {
    "question": "In a Marble string, what does the '#' character signify?",
    "options": {
      "A": "A successful emission",
      "B": "An error notification",
      "C": "The subscription start",
      "D": "A grouping of values"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Virtual Time Scheduler' used for in testing?",
    "options": {
      "A": "To speed up the computer",
      "B": "To simulate the passage of time without actually waiting, making async tests synchronous",
      "C": "To tell the real time",
      "D": "To manage server dates"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'EMPTY' constant in RxJS?",
    "options": {
      "A": "A stream that errors immediately",
      "B": "An Observable that emits no items and immediately completes",
      "C": "A variable with no value",
      "D": "A database tool"
    },
    "answer": "B"
  },
  {
    "question": "Which operator allows you to perform complex retry logic like 'Exponential Backoff'?",
    "options": {
      "A": "retry()",
      "B": "retryWhen() (or retry with a delay config)",
      "C": "repeat()",
      "D": "delay()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Tearing' in RxJS streams?",
    "options": {
      "A": "When the UI flickers",
      "B": "An inconsistency where two subscribers see different values from the same synchronous source",
      "C": "A network crash",
      "D": "Deleting a subscriber"
    },
    "answer": "B"
  },
  {
    "question": "In a Marble string, what do parentheses '()' represent?",
    "options": {
      "A": "A comment",
      "B": "Values that occur synchronously in the same frame",
      "C": "An error",
      "D": "A hidden value"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'finalize' operator used for?",
    "options": {
      "A": "To finish the app",
      "B": "To call a function when the Observable terminates (either complete or error), similar to a finally block",
      "C": "To delete the database",
      "D": "To encrypt the stream"
    },
    "answer": "B"
  },
  {
    "question": "Which tool is commonly used to visualize and test RxJS operators in a browser sandbox?",
    "options": {
      "A": "RxViz",
      "B": "Postman",
      "C": "Chrome DevTools",
      "D": "Android Studio"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Schedulers.asap' used for?",
    "options": {
      "A": "To run a task as soon as possible via a microtask",
      "B": "To run a task next year",
      "C": "To delete a task",
      "D": "A network protocol"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'Materialize' operator?",
    "options": {
      "A": "Turning code into hardware",
      "B": "Wrapping emissions into 'Notification' objects so you can handle next, error, and complete as data",
      "C": "Making the UI look better",
      "D": "Saving to disk"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Subscribing' to an error-only stream called?",
    "options": {
      "A": "Listening to the crash",
      "B": "Handling the error notification",
      "C": "A void subscription",
      "D": "A bad connection"
    },
    "answer": "B"
  },
  {
    "question": "How do you 're-throw' an error in a catchError operator?",
    "options": {
      "A": "return throwError(() => new Error())",
      "B": "return null",
      "C": "break",
      "D": "throw Error()"
    },
    "answer": "A"
  },
  {
    "question": "In RxJS, what is 'The pipeable operator' pattern?",
    "options": {
      "A": "A function that takes an Observable and returns a new Observable",
      "B": "A way to fix plumbing",
      "C": "A type of variable",
      "D": "A network cable"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'timeout' operator used for?",
    "options": {
      "A": "To pause the app",
      "B": "To emit an error if the source does not emit a value within a specified time span",
      "C": "To set the clock",
      "D": "A security setting"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Multicasting' using 'ConnectableObservable'?",
    "options": {
      "A": "Sharing a single execution with multiple subscribers by calling .connect() manually",
      "B": "Sending data to a TV",
      "C": "A type of UI theme",
      "D": "A database tool"
    },
    "answer": "A"
  },
  {
    "question": "In 'retry(3)', how many times will the observable be re-subscribed to if it keeps failing?",
    "options": {
      "A": "1 time",
      "B": "3 times",
      "C": "Infinite times",
      "D": "0 times"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Marble Testing' expectObservable()?",
    "options": {
      "A": "Telling the compiler to expect a value",
      "B": "Asserting that a specific Observable matches a marble string during a test",
      "C": "Waiting for a user click",
      "D": "A network speed test"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'SubscriptionLog'?",
    "options": {
      "A": "A list of people who paid for the app",
      "B": "A record of exactly when a subscription started and ended in virtual time",
      "C": "A console log",
      "D": "A database table"
    },
    "answer": "B"
  },
  {
    "question": "Which operator is used to 'combine' an error stream and a success stream into one handled flow?",
    "options": {
      "A": "merge()",
      "B": "catchError()",
      "C": "concat()",
      "D": "zip()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Schedulers.queue'?",
    "options": {
      "A": "A scheduler that executes tasks synchronously by putting them in a queue",
      "B": "A line at the store",
      "C": "A network protocol",
      "D": "A database tool"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Custom Operator' structure?",
    "options": {
      "A": "A function that takes a source Observable and returns a result Observable",
      "B": "A new library",
      "C": "A CSS style",
      "D": "A database query"
    },
    "answer": "A"
  },
  {
    "question": "What does 'retryWhen' take as its argument?",
    "options": {
      "A": "A number",
      "B": "A function that returns an Observable of 'notifications' that triggers the retry",
      "C": "A string",
      "D": "A boolean"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Race' condition in mergeMap?",
    "options": {
      "A": "A fast network",
      "B": "When multiple parallel inner observables complete in an order different from how they started",
      "C": "A type of loop",
      "D": "A database error"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Cold to Hot' with share()?",
    "options": {
      "A": "Making the app run hot",
      "B": "Allowing a cold observable to be shared among multiple subscribers using a Subject internally",
      "C": "A network security tool",
      "D": "Updating the version"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Subject' completion side-effect?",
    "options": {
      "A": "It can never be used again once complete() is called",
      "B": "It clears the memory",
      "C": "It restarts the app",
      "D": "It notifies the server"
    },
    "answer": "A"
  },
  {
    "question": "In 'of(1, 2).pipe(delay(1000))', when is '2' emitted?",
    "options": {
      "A": "Immediately",
      "B": "1000ms after the first value",
      "C": "At the same time as 1 (after 1000ms)",
      "D": "Never"
    },
    "answer": "C"
  },
  {
    "question": "What is the purpose of 'observeOn'?",
    "options": {
      "A": "To watch the user",
      "B": "To change the Scheduler on which the observers receive notifications",
      "C": "To start a network call",
      "D": "To manage app themes"
    },
    "answer": "B"
  },
  {
    "question": "What is 'subscribeOn'?",
    "options": {
      "A": "To change the Scheduler on which the subscription itself starts",
      "B": "To login to the app",
      "C": "A database tool",
      "D": "A type of variable"
    },
    "answer": "A"
  },
  {
    "question": "What is 'VerifiHire AI's' requirement for RxJS testing?",
    "options": {
      "A": "Manual testing only",
      "B": "Ensuring asynchronous logic is 100% predictable and verified via marble tests or similar tools",
      "C": "Writing code without tests",
      "D": "Using only console logs"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Result Selector' in older RxJS operators?",
    "options": {
      "A": "A way to pick the winner",
      "B": "An optional second function to shape the output of a combination operator (now deprecated)",
      "C": "A UI component",
      "D": "A network tool"
    },
    "answer": "B"
  },
  {
    "question": "Which operator is used to 'flatten' and ignore values if the previous inner Observable is still active?",
    "options": {
      "A": "mergeMap",
      "B": "switchMap",
      "C": "exhaustMap",
      "D": "concatMap"
    },
    "answer": "C"
  },
  {
    "question": "What is 'Marble' syntax for completion?",
    "options": {
      "A": "|",
      "B": "#",
      "C": "-",
      "D": "!"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'TestScheduler.run()' method?",
    "options": {
      "A": "To run the app",
      "B": "A helper that provides 'helpers' like cold(), hot(), and expectObservable() for cleaner tests",
      "C": "A type of loop",
      "D": "A database query"
    },
    "answer": "B"
  },
  {
    "question": "Which operator provides the 'Index' of the emission as a second argument to the map function?",
    "options": {
      "A": "map( (val, i) => ... )",
      "B": "indexMap()",
      "C": "count()",
      "D": "pluck()"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Unicast' vs 'Multicast'?",
    "options": {
      "A": "Unicast is one-to-one; Multicast is one-to-many",
      "B": "Unicast is for mobile; Multicast is for web",
      "C": "Multicast is faster",
      "D": "They are the same"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Internal State' of an operator?",
    "options": {
      "A": "The code inside the operator",
      "B": "Variables held by an operator (like 'scan' or 'debounce') to track data across emissions",
      "C": "The user's account state",
      "D": "A database table"
    },
    "answer": "B"
  },
  {
    "question": "What is 'BehaviorSubject' initial value importance?",
    "options": {
      "A": "It ensures that the stream always has a 'current' value for new subscribers immediately",
      "B": "It speeds up the app",
      "C": "It is not important",
      "D": "It is a security key"
    },
    "answer": "A"
  },
  {
    "question": "What is 'RxJS' final goal for error handling?",
    "options": {
      "A": "To hide all errors",
      "B": "To make asynchronous error recovery predictable, resilient, and declarative",
      "C": "To crash the app cleanly",
      "D": "To avoid using try-catch"
    },
    "answer": "B"
  },
  {
    "question": "Which operator will 'exhaust' all inner observables once they complete?",
    "options": {
      "A": "exhaustMap()",
      "B": "exhaustAll()",
      "C": "concat()",
      "D": "merge()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Marble' caret (^) symbol?",
    "options": {
      "A": "The end of the stream",
      "B": "The point in time where a subscription starts in a hot observable test",
      "C": "A value of zero",
      "D": "An error"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Schedulers.animationFrame'?",
    "options": {
      "A": "To animate a movie",
      "B": "A scheduler that uses requestAnimationFrame to perform tasks before the next browser paint",
      "C": "A database tool",
      "D": "A network protocol"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Operator' purity?",
    "options": {
      "A": "Operators should not modify original data but return new streams",
      "B": "Operators have no bugs",
      "C": "Operators are written in C++",
      "D": "Operators are private"
    },
    "answer": "A"
  },
  {
    "question": "What is 'ReplaySubject' buffer size?",
    "options": {
      "A": "The number of previous values the subject stores to play back to new subscribers",
      "B": "The size of the app",
      "C": "The internet speed",
      "D": "The database storage"
    },
    "answer": "A"
  },
  {
    "question": "In 'retryWhen', what happens if the notifier observable errors?",
    "options": {
      "A": "The app restarts",
      "B": "The whole stream errors and stops",
      "C": "The error is ignored",
      "D": "The stream is reset"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Custom Pipeable Operator' return value?",
    "options": {
      "A": "A new Observable",
      "B": "A function that takes an Observable and returns an Observable",
      "C": "A subscription",
      "D": "A promise"
    },
    "answer": "B"
  },
  {
    "question": "What is 'VerifiHire AI's' final RxJS milestone?",
    "options": {
      "A": "This final question!",
      "B": "The first 50 questions",
      "C": "The logo design",
      "D": "The database export"
    },
    "answer": "A"
  },
  {
    "question": "What is 'RxJS' version 7+ focus?",
    "options": {
      "A": "Performance, smaller bundle sizes, and better TypeScript support",
      "B": "Adding more operators",
      "C": "Changing the logo",
      "D": "Supporting only mobile"
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
    skill = "RxJs"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
