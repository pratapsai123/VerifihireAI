from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
  {
    "question": "What does CLR stand for in the .NET framework?",
    "options": {
      "A": "Common Language Runtime",
      "B": "Central Library Resource",
      "C": "Core Logging Repository",
      "D": "Common Local Runtime"
    },
    "answer": "A"
  },
  {
    "question": "Which component is responsible for converting MSIL code into machine-specific code?",
    "options": {
      "A": "Garbage Collector",
      "B": "JIT (Just-In-Time) Compiler",
      "C": "Class Loader",
      "D": "Assembly Linker"
    },
    "answer": "B"
  },
  {
    "question": "What is the base class from which all types in .NET are directly or indirectly derived?",
    "options": {
      "A": "System.Type",
      "B": "System.Object",
      "C": "System.Root",
      "D": "System.Base"
    },
    "answer": "B"
  },
  {
    "question": "Which keyword is used to prevent a class from being inherited in C#?",
    "options": {
      "A": "static",
      "B": "sealed",
      "C": "final",
      "D": "private"
    },
    "answer": "B"
  },
  {
    "question": "What is the difference between 'Value Types' and 'Reference Types' regarding memory?",
    "options": {
      "A": "Value types are stored on the Heap; Reference types on the Stack",
      "B": "Value types are stored on the Stack; Reference types on the Heap",
      "C": "Both are stored on the Heap",
      "D": "Both are stored on the Stack"
    },
    "answer": "B"
  },
  {
    "question": "Which of the following is a 'Reference Type' in C#?",
    "options": {
      "A": "int",
      "B": "string",
      "C": "bool",
      "D": "struct"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Managed Code' in .NET?",
    "options": {
      "A": "Code written in C++",
      "B": "Code that is executed by the CLR and provided with services like Garbage Collection",
      "C": "Code that directly manages CPU registers",
      "D": "Code that doesn't require a compiler"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'using' statement in C# when working with IDisposable objects?",
    "options": {
      "A": "To include a namespace",
      "B": "To ensure that the object's Dispose method is called automatically to release resources",
      "C": "To create a global variable",
      "D": "To speed up code execution"
    },
    "answer": "B"
  },
  {
    "question": "Which collection type stores key-value pairs and is optimized for fast lookups by key?",
    "options": {
      "A": "List<T>",
      "B": "Dictionary<TKey, TValue>",
      "C": "Queue<T>",
      "D": "Stack<T>"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Boxing' in .NET?",
    "options": {
      "A": "Converting a reference type to a value type",
      "B": "Converting a value type to a reference type (object)",
      "C": "Enclosing code in a try-catch block",
      "D": "Packing an assembly into a DLL"
    },
    "answer": "B"
  },
  {
    "question": "Which access modifier makes a member accessible only within the same assembly?",
    "options": {
      "A": "protected",
      "B": "internal",
      "C": "private",
      "D": "public"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Delegate' in C#?",
    "options": {
      "A": "A special type of class",
      "B": "A type-safe function pointer that holds references to methods",
      "C": "A database connection string",
      "D": "A replacement for an interface"
    },
    "answer": "B"
  },
  {
    "question": "Which keyword allows a method to be overridden in a derived class?",
    "options": {
      "A": "abstract",
      "B": "virtual",
      "C": "new",
      "D": "override"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Global Assembly Cache' (GAC) used for?",
    "options": {
      "A": "Storing temporary internet files",
      "B": "Storing assemblies that are meant to be shared across multiple applications on a machine",
      "C": "Caching database queries",
      "D": "Storing user profile data"
    },
    "answer": "B"
  },
  {
    "question": "In .NET, what is the role of the 'Garbage Collector'?",
    "options": {
      "A": "To optimize the CPU",
      "B": "To automatically reclaim memory occupied by objects that are no longer in use",
      "C": "To delete old files from the hard drive",
      "D": "To manage thread priorities"
    },
    "answer": "B"
  },
  {
    "question": "What is the difference between 'String' and 'StringBuilder'?",
    "options": {
      "A": "String is mutable; StringBuilder is immutable",
      "B": "String is immutable; StringBuilder is mutable and more efficient for repeated modifications",
      "C": "String is a value type; StringBuilder is a reference type",
      "D": "There is no difference"
    },
    "answer": "B"
  },
  {
    "question": "Which LINQ method is used to filter a sequence based on a predicate?",
    "options": {
      "A": "Select",
      "B": "Where",
      "C": "OrderBy",
      "D": "GroupBy"
    },
    "answer": "B"
  },
  {
    "question": "What is an 'Interface' in C#?",
    "options": {
      "A": "A class that can be instantiated",
      "B": "A contract that defines a set of methods and properties that a class must implement",
      "C": "A way to store static data",
      "D": "A graphical user interface component"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'async' keyword indicate in C#?",
    "options": {
      "A": "The method runs in a separate process",
      "B": "The method contains asynchronous operations and can use the 'await' keyword",
      "C": "The method is private",
      "D": "The method is thread-safe"
    },
    "answer": "B"
  },
  {
    "question": "Which property of an Exception object provides information about the sequence of method calls leading to the error?",
    "options": {
      "A": "Message",
      "B": "StackTrace",
      "C": "Source",
      "D": "HelpLink"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary role of 'Middleware' in ASP.NET Core?",
    "options": {
      "A": "To design the database schema",
      "B": "To handle requests and responses in the application's request pipeline",
      "C": "To compile C# code into HTML",
      "D": "To manage server hardware"
    },
    "answer": "B"
  },
  {
    "question": "Which file is the entry point of an ASP.NET Core application where the WebApplication is built?",
    "options": {
      "A": "Startup.cs",
      "B": "Program.cs",
      "C": "App.config",
      "D": "Web.config"
    },
    "answer": "B"
  },
  {
    "question": "In Dependency Injection, which lifetime creates a new instance for every single request?",
    "options": {
      "A": "Singleton",
      "B": "Scoped",
      "C": "Transient",
      "D": "Static"
    },
    "answer": "B"
  },
  {
    "question": "In Dependency Injection, which lifetime creates a single instance that is shared throughout the application's lifetime?",
    "options": {
      "A": "Transient",
      "B": "Singleton",
      "C": "Scoped",
      "D": "Persistent"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'Kestrel' server represent in ASP.NET Core?",
    "options": {
      "A": "A database engine",
      "B": "A cross-platform, open-source web server for ASP.NET Core",
      "C": "A cloud storage provider",
      "D": "A debugging tool in Visual Studio"
    },
    "answer": "B"
  },
  {
    "question": "Which attribute is used in ASP.NET Core Web API to define the route for a controller?",
    "options": {
      "A": "[Path]",
      "B": "[Route]",
      "C": "[Url]",
      "D": "[Endpoint]"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'appsettings.json' in an ASP.NET Core project?",
    "options": {
      "A": "To store CSS styles",
      "B": "To store configuration settings like connection strings",
      "C": "To write C# logic",
      "D": "To manage NuGet packages"
    },
    "answer": "B"
  },
  {
    "question": "Which method in the Program.cs file is used to add services to the DI container?",
    "options": {
      "A": "app.UseMiddleware()",
      "B": "builder.Services.Add...",
      "C": "app.MapControllers()",
      "D": "builder.Configuration.Get()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Content Negotiation' in ASP.NET Core Web API?",
    "options": {
      "A": "Negotiating the price of the server",
      "B": "The process of selecting the best representation (JSON, XML) for a response based on request headers",
      "C": "Merging two different databases",
      "D": "Validating user passwords"
    },
    "answer": "B"
  },
  {
    "question": "Which filter type in ASP.NET Core runs first after an action is selected but before any other filters?",
    "options": {
      "A": "Action Filter",
      "B": "Authorization Filter",
      "C": "Resource Filter",
      "D": "Exception Filter"
    },
    "answer": "B"
  },
  {
    "question": "What does the [ApiController] attribute provide to a controller class?",
    "options": {
      "A": "Enables automatic 400 responses for validation errors",
      "B": "Requires all methods to return strings",
      "C": "Deletes the controller from memory",
      "D": "Connects the controller to SQL Server"
    },
    "answer": "A"
  },
  {
    "question": "How do you access the value of a route parameter named 'id' in an action method?",
    "options": {
      "A": "Request.Query['id']",
      "B": "The parameter must be defined in the method signature: public IActionResult Get(int id)",
      "C": "Request.Headers['id']",
      "D": "Session['id']"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'wwwroot' folder used for in ASP.NET Core?",
    "options": {
      "A": "Storing C# source files",
      "B": "Storing static files like HTML, CSS, and JavaScript",
      "C": "Storing database migration files",
      "D": "Storing private server keys"
    },
    "answer": "B"
  },
  {
    "question": "Which status code is returned by default when 'CreatedAtAction' is called successfully?",
    "options": {
      "A": "200 OK",
      "B": "201 Created",
      "C": "204 No Content",
      "D": "302 Found"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Model Binding' in ASP.NET Core?",
    "options": {
      "A": "Connecting a view to a stylesheet",
      "B": "The process of mapping data from HTTP requests to action method parameters",
      "C": "Storing a model in a database",
      "D": "Validating the schema of a JSON file"
    },
    "answer": "B"
  },
  {
    "question": "Which tool is commonly used to generate interactive documentation (UI) for .NET Web APIs?",
    "options": {
      "A": "Postman",
      "B": "Swagger (Swashbuckle)",
      "C": "Fiddler",
      "D": "Wireshark"
    },
    "answer": "B"
  },
  {
    "question": "What does 'In-Process' hosting in IIS mean for an ASP.NET Core app?",
    "options": {
      "A": "The app runs in a separate process from IIS",
      "B": "The app runs inside the IIS worker process (w3wp.exe) for better performance",
      "C": "The app runs without a process",
      "D": "The app is always in a 'pending' state"
    },
    "answer": "B"
  },
  {
    "question": "Which interface is used to access configuration data in an ASP.NET Core application?",
    "options": {
      "A": "ISetting",
      "B": "IConfiguration",
      "C": "IConfig",
      "D": "IOptions"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Attribute Routing'?",
    "options": {
      "A": "Defining routes in the Program.cs file",
      "B": "Using attributes like [HttpGet('items/{id}')] directly on controllers and actions to define URLs",
      "C": "A way to route traffic to different servers",
      "D": "A legacy feature from .NET 1.0"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used in Program.cs to enable the serving of static files?",
    "options": {
      "A": "app.MapStatic()",
      "B": "app.UseStaticFiles()",
      "C": "app.AddFiles()",
      "D": "app.ServeHtml()"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Options Pattern' in ASP.NET Core?",
    "options": {
      "A": "To provide more options in a dropdown",
      "B": "To provide strongly-typed access to groups of related settings",
      "C": "To give users multiple login methods",
      "D": "To select the database type"
    },
    "answer": "B"
  },
  {
    "question": "Which interface allows you to perform cleanup tasks when the application is shutting down?",
    "options": {
      "A": "IAppEnd",
      "B": "IHostApplicationLifetime",
      "C": "IShutdown",
      "D": "IExit"
    },
    "answer": "B"
  },
  {
    "question": "What does 'CORS' stand for and why is it needed in Web APIs?",
    "options": {
      "A": "Centralized Object Response System; for speed",
      "B": "Cross-Origin Resource Sharing; to allow/restrict web apps on different domains from calling the API",
      "C": "Core Object Runtime Security; for encryption",
      "D": "Connected Origin Request Service; for load balancing"
    },
    "answer": "B"
  },
  {
    "question": "What is the role of 'IHttpClientFactory' in .NET?",
    "options": {
      "A": "To create database connections",
      "B": "To manage the lifecycle and configuration of HttpClient instances efficiently",
      "C": "To create new web servers",
      "D": "To download files from the internet"
    },
    "answer": "B"
  },
  {
    "question": "Which middleware is used to catch exceptions and return a friendly error page or response?",
    "options": {
      "A": "app.UseLogging()",
      "B": "app.UseExceptionHandler()",
      "C": "app.UseErrorHandling()",
      "D": "app.UseDebug()"
    },
    "answer": "B"
  },
  {
    "question": "What is Entity Framework Core (EF Core)?",
    "options": {
      "A": "A new C# compiler",
      "B": "A lightweight, extensible, open-source, and cross-platform version of the Entity Framework data access technology",
      "C": "A tool for designing HTML forms",
      "D": "A library for building mobile games"
    },
    "answer": "B"
  },
  {
    "question": "Which class in EF Core acts as the primary session with the database and allows you to query and save data?",
    "options": {
      "A": "DbSet",
      "B": "DbContext",
      "C": "DbSession",
      "D": "DbConnection"
    },
    "answer": "B"
  },
  {
    "question": "In EF Core, what does a 'DbSet<TEntity>' property represent?",
    "options": {
      "A": "A specific database column",
      "B": "A collection of entities that can be queried from the database (usually mapping to a table)",
      "C": "A connection string",
      "D": "A SQL stored procedure"
    },
    "answer": "B"
  },
  {
    "question": "Which EF Core approach involves creating your C# classes first and then generating the database from them?",
    "options": {
      "A": "Database-First",
      "B": "Code-First",
      "C": "Model-First",
      "D": "Schema-First"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Migrations' in EF Core?",
    "options": {
      "A": "To move data from Excel to SQL",
      "B": "To incrementally update the database schema to keep it in sync with the application's data model",
      "C": "To backup the database to the cloud",
      "D": "To translate C# into different languages"
    },
    "answer": "B"
  },
  {
    "question": "Which CLI command is used to create a new migration in EF Core?",
    "options": {
      "A": "dotnet ef database update",
      "B": "dotnet ef migrations add <Name>",
      "C": "dotnet ef schema create",
      "D": "dotnet build migration"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Lazy Loading' in EF Core?",
    "options": {
      "A": "Loading data only when the user is idle",
      "B": "The process of loading related data from the database only when the navigation property is first accessed",
      "C": "A performance bug that stops the server",
      "D": "Loading all tables at once"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Eager Loading' in EF Core?",
    "options": {
      "A": "Loading data before the app starts",
      "B": "The process of loading related data as part of the initial query using the .Include() method",
      "C": "Loading data into the browser cache",
      "D": "A fast way to delete records"
    },
    "answer": "B"
  },
  {
    "question": "Which LINQ method is used to return only the first element of a sequence, or a default value if no element is found?",
    "options": {
      "A": "First()",
      "B": "FirstOrDefault()",
      "C": "Single()",
      "D": "ElementAt()"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'N+1 Query Problem'?",
    "options": {
      "A": "A math formula for database growth",
      "B": "A performance issue where the app makes one query to fetch parent data and N additional queries for related child data",
      "C": "A security vulnerability in SQL",
      "D": "A limit on the number of tables"
    },
    "answer": "B"
  },
  {
    "question": "Which method on the DbContext is used to apply all pending changes to the database?",
    "options": {
      "A": "UpdateChanges()",
      "B": "SaveChangesAsync()",
      "C": "Commit()",
      "D": "PushData()"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'Fluent API' in EF Core allow you to do?",
    "options": {
      "A": "Write code in multiple languages",
      "B": "Configure the model using code in the OnModelCreating method instead of using data attributes",
      "C": "Write SQL queries as strings",
      "D": "Design the UI of the database"
    },
    "answer": "B"
  },
  {
    "question": "Which attribute is used to specify that a property is the Primary Key of a table?",
    "options": {
      "A": "[Main]",
      "B": "[Key]",
      "C": "[PrimaryKey]",
      "D": "[Id]"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of '.AsNoTracking()' in an EF Core query?",
    "options": {
      "A": "To hide the query from logs",
      "B": "To improve performance by telling EF not to track the returned entities in the change tracker",
      "C": "To prevent others from reading the data",
      "D": "To disable the database firewall"
    },
    "answer": "B"
  },
  {
    "question": "In LINQ, what is the difference between 'IEnumerable' and 'IQueryable'?",
    "options": {
      "A": "There is no difference",
      "B": "IEnumerable executes in memory; IQueryable executes on the database side (provider-specific)",
      "C": "IQueryable is for mobile apps; IEnumerable is for web",
      "D": "IEnumerable is faster for SQL queries"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Shadow Property' in EF Core?",
    "options": {
      "A": "A property that is hidden in the UI",
      "B": "A property that is defined in the EF Core model but not in the physical C# entity class",
      "C": "A backup of a property",
      "D": "An encrypted field"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used to execute a raw SQL query that returns entities in EF Core?",
    "options": {
      "A": "ExecuteSqlRaw()",
      "B": "FromSqlRaw()",
      "C": "QuerySql()",
      "D": "GetEntitiesFromSql()"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Deferred Execution' mean in LINQ?",
    "options": {
      "A": "The query is never executed",
      "B": "The query is not executed when it is defined, but only when the data is actually iterated over",
      "C": "The query is executed in a background thread",
      "D": "The query is executed before the app starts"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'HasData' method in OnModelCreating?",
    "options": {
      "A": "To check if the database is empty",
      "B": "To seed the database with initial data",
      "C": "To delete all data",
      "D": "To encrypt existing data"
    },
    "answer": "B"
  },
  {
    "question": "Which status indicates that an entity is being tracked by the DbContext but does not yet exist in the database?",
    "options": {
      "A": "Unchanged",
      "B": "Added",
      "C": "Modified",
      "D": "Detached"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Concurrency Token' used for in EF Core?",
    "options": {
      "A": "To speed up multiple users",
      "B": "To handle optimistic concurrency conflicts by ensuring the data hasn't changed since it was read",
      "C": "To generate random IDs",
      "D": "To limit the number of users"
    },
    "answer": "B"
  },
  {
    "question": "Which LINQ operator is used to project each element of a sequence into a new form?",
    "options": {
      "A": "Where",
      "B": "Select",
      "C": "Take",
      "D": "Skip"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Backing Field' feature in EF Core?",
    "options": {
      "A": "A backup of the database",
      "B": "Allowing EF Core to read from or write to a private field rather than a public property",
      "C": "A field used for background tasks",
      "D": "A way to hide data from the developer"
    },
    "answer": "B"
  },
  {
    "question": "How do you define a Many-to-Many relationship in EF Core 5.0 and later without an explicit join entity?",
    "options": {
      "A": "It is not possible",
      "B": "By including collection navigation properties in both entity classes",
      "C": "By using a string array of IDs",
      "D": "By creating a separate SQL file"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Transaction' in EF Core?",
    "options": {
      "A": "To charge users money",
      "B": "To ensure that a group of database operations either all succeed or all fail as a single unit",
      "C": "To track user movements",
      "D": "To connect two different databases"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Reflection' in .NET?",
    "options": {
      "A": "A way to see the screen in the code",
      "B": "The ability to inspect and interact with metadata and code at runtime",
      "C": "A method to reverse a string",
      "D": "A database backup technique"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'Task Parallel Library' (TPL) in .NET?",
    "options": {
      "A": "To manage a list of tasks for developers",
      "B": "To simplify the process of adding parallelism and concurrency to applications",
      "C": "To create a user interface",
      "D": "To connect to multiple databases"
    },
    "answer": "B"
  },
  {
    "question": "Which keyword is used to access the base class members from within a derived class?",
    "options": {
      "A": "this",
      "B": "base",
      "C": "parent",
      "D": "super"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Expression Trees' in LINQ?",
    "options": {
      "A": "A way to draw trees in C#",
      "B": "A data structure that represents code in a tree-like format, allowing for dynamic query building",
      "C": "A method for sorting arrays",
      "D": "A type of database index"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'lock' keyword used for in C# multithreading?",
    "options": {
      "A": "To lock the computer screen",
      "B": "To ensure that only one thread can access a specific block of code at a time",
      "C": "To prevent a file from being deleted",
      "D": "To encrypt a string"
    },
    "answer": "B"
  },
  {
    "question": "In .NET, what is an 'Attribute'?",
    "options": {
      "A": "A private variable",
      "B": "Declarative tags that provide metadata about code elements (classes, methods, etc.)",
      "C": "A property of an HTML tag",
      "D": "A method to calculate values"
    },
    "answer": "B"
  },
  {
    "question": "What is the difference between 'Task.Run' and 'Task.Factory.StartNew'?",
    "options": {
      "A": "Task.Run is a newer, simpler shortcut for the most common scenarios",
      "B": "Task.Run only works on mobile",
      "C": "StartNew is faster",
      "D": "There is no difference"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Middleware' in the context of an API Gateway in Microservices?",
    "options": {
      "A": "Code that handles cross-cutting concerns like authentication and logging for all services",
      "B": "A tool to design the UI",
      "C": "A separate database for each service",
      "D": "A way to write code in the browser"
    },
    "answer": "A"
  },
  {
    "question": "What is 'JWT' commonly used for in .NET Microservices?",
    "options": {
      "A": "Database storage",
      "B": "Securely transmitting information between parties as a JSON object (Authentication/Authorization)",
      "C": "Image compression",
      "D": "Sorting lists"
    },
    "answer": "B"
  },
  {
    "question": "Which C# feature allows you to add new methods to existing types without modifying the original type?",
    "options": {
      "A": "Inheritance",
      "B": "Extension Methods",
      "C": "Interfaces",
      "D": "Partial Classes"
    },
    "answer": "B"
  },
  {
    "question": "What is 'gRPC' in the .NET ecosystem?",
    "options": {
      "A": "A graphics rendering library",
      "B": "A high-performance, open-source universal RPC framework used for microservices",
      "C": "A type of SQL database",
      "D": "A frontend framework"
    },
    "answer": "B"
  },
  {
    "question": "What does 'IDistributedCache' provide in ASP.NET Core?",
    "options": {
      "A": "A way to cache data locally on the user's phone",
      "B": "A common interface for interacting with different distributed cache providers like Redis or SQL Server",
      "C": "A backup for the main database",
      "D": "A tool to minify CSS"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Lazy<T>' used for in C#?",
    "options": {
      "A": "To create a thread that runs slowly",
      "B": "To defer the creation of a large object until it is actually needed",
      "C": "To skip a part of a loop",
      "D": "To automatically delete unused variables"
    },
    "answer": "B"
  },
  {
    "question": "What is 'CancellationToken' used for in asynchronous programming?",
    "options": {
      "A": "To delete a token",
      "B": "To signal that an operation should be stopped or cancelled",
      "C": "To generate a new password",
      "D": "To increase the timeout of a request"
    },
    "answer": "B"
  },
  {
    "question": "Which collection is thread-safe for concurrent additions and removals in .NET?",
    "options": {
      "A": "List<T>",
      "B": "ConcurrentBag<T>",
      "C": "ArrayList",
      "D": "Dictionary<TKey, TValue>"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'yield' keyword used for in C#?",
    "options": {
      "A": "To stop the execution of a program",
      "B": "To indicate that a method is an iterator, returning elements one by one without creating a full list in memory",
      "C": "To wait for a thread to finish",
      "D": "To declare a constant"
    },
    "answer": "B"
  },
  {
    "question": "What is 'AutoMapper' in the context of a .NET project?",
    "options": {
      "A": "A tool to automatically map routes to controllers",
      "B": "A library used to map data between different object types (e.g., Entity to DTO)",
      "C": "A way to automatically generate SQL",
      "D": "A system to map user IPs"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Polly' in the .NET ecosystem?",
    "options": {
      "A": "A tool for UI testing",
      "B": "A resilience and transient-fault-handling library (Retries, Circuit Breakers)",
      "C": "A database migration tool",
      "D": "A chat bot framework"
    },
    "answer": "B"
  },
  {
    "question": "Which keyword is used to pass an argument by reference in C#?",
    "options": {
      "A": "val",
      "B": "ref",
      "C": "link",
      "D": "ptr"
    },
    "answer": "B"
  },
  {
    "question": "What is the difference between 'readonly' and 'const' in C#?",
    "options": {
      "A": "const is evaluated at runtime; readonly at compile-time",
      "B": "const is evaluated at compile-time; readonly at runtime and can be set in a constructor",
      "C": "There is no difference",
      "D": "readonly only works with integers"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary purpose of 'xUnit' or 'NUnit' in a .NET project?",
    "options": {
      "A": "To design the database",
      "B": "To provide a framework for writing and running automated unit tests",
      "C": "To compile the application for Linux",
      "D": "To manage NuGet packages"
    },
    "answer": "B"
  },
  {
    "question": "In Unit Testing, what is 'Mocking'?",
    "options": {
      "A": "Making fun of the code",
      "B": "Creating fake objects that simulate the behavior of real dependencies (like a database or API)",
      "C": "Copying code from another project",
      "D": "Running tests in a loop"
    },
    "answer": "B"
  },
  {
    "question": "Which C# feature introduced in recent versions allows for more concise constructor definitions in classes and structs?",
    "options": {
      "A": "Primary Constructors",
      "B": "Auto-Constructors",
      "C": "Quick Constructors",
      "D": "Simple Constructors"
    },
    "answer": "A"
  },
  {
    "question": "What does 'ASP.NET Core Identity' provide?",
    "options": {
      "A": "A way to identify the server location",
      "B": "A complete membership system that handles login, registration, and roles",
      "C": "A unique ID for every HTML tag",
      "D": "A tool to track server performance"
    },
    "answer": "B"
  },
  {
    "question": "What is 'HSTS' in an ASP.NET Core application?",
    "options": {
      "A": "A high-speed transport system",
      "B": "HTTP Strict Transport Security, which tells browsers to only use HTTPS",
      "C": "A method for caching strings",
      "D": "A database indexing strategy"
    },
    "answer": "B"
  },
  {
    "question": "Which tool allows you to run .NET applications in isolated containers across different environments?",
    "options": {
      "A": "NuGet",
      "B": "Docker",
      "C": "IIS",
      "D": "Kestrel"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'IIdentity' and 'IPrincipal' interfaces?",
    "options": {
      "A": "To manage database migrations",
      "B": "To represent the identity and security context of the current user",
      "C": "To define the main entry point of the app",
      "D": "To handle file uploads"
    },
    "answer": "B"
  },
  {
    "question": "What is 'In-Memory Database Provider' used for in EF Core?",
    "options": {
      "A": "To store production data permanently",
      "B": "To simulate a database in RAM for fast unit testing without a physical SQL server",
      "C": "To backup data to a flash drive",
      "D": "To speed up video rendering"
    },
    "answer": "B"
  },
  {
    "question": "Which C# keyword is used to define a type that is a 'Record'?",
    "options": {
      "A": "data",
      "B": "record",
      "C": "struct",
      "D": "entity"
    },
    "answer": "B"
  },
  {
    "question": "What is the main benefit of using 'Records' in C#?",
    "options": {
      "A": "They are faster than classes",
      "B": "They provide built-in functionality for value-based equality and immutability",
      "C": "They can only be used with SQL",
      "D": "They don't require memory"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Data Protection API' (DPAPI) in ASP.NET Core used for?",
    "options": {
      "A": "To prevent users from deleting files",
      "B": "To provide a simple cryptographic API for protecting data like cookies or tokens",
      "C": "To hide code from competitors",
      "D": "To manage firewalls"
    },
    "answer": "B"
  },
  {
    "question": "Which component is used in Azure to store .NET configuration and feature flags centrally?",
    "options": {
      "A": "Azure SQL",
      "B": "Azure App Configuration",
      "C": "Azure Blob Storage",
      "D": "Azure Active Directory"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'SignalR' library used for?",
    "options": {
      "A": "To send radio signals",
      "B": "To add real-time web functionality (pushing content from server to client)",
      "C": "To compress JSON files",
      "D": "To manage background email tasks"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Global Using Directive' in C#?",
    "options": {
      "A": "A using statement that applies to the whole world",
      "B": "A directive that allows you to define a namespace once for the entire project",
      "C": "A way to use variables from other projects",
      "D": "A method to include CSS globally"
    },
    "answer": "B"
  },
  {
    "question": "Which HTTP header is commonly used to send a JWT to a .NET Web API?",
    "options": {
      "A": "Authentication",
      "B": "Authorization",
      "C": "Token",
      "D": "X-JWT-Key"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Role-Based Authorization'?",
    "options": {
      "A": "Giving users a random name",
      "B": "Restricting access to resources based on the group or role the user belongs to",
      "C": "Rotating the server every hour",
      "D": "Deleting users who don't log in"
    },
    "answer": "B"
  },
  {
    "question": "In EF Core, what is 'Shadow State'?",
    "options": {
      "A": "A hidden database",
      "B": "When data is stored in the change tracker but not in the entity class itself",
      "C": "A backup of a database row",
      "D": "A private variable in the DbContext"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Self-Contained Deployment' for a .NET app?",
    "options": {
      "A": "The app only runs on the developer's machine",
      "B": "The deployment includes the .NET runtime, so it doesn't need to be installed on the target machine",
      "C": "The app doesn't use any libraries",
      "D": "The app is compressed into a .zip file"
    },
    "answer": "B"
  },
  {
    "question": "Which C# operator is used to check if an object is of a certain type and cast it simultaneously?",
    "options": {
      "A": "as",
      "B": "is (with pattern matching)",
      "C": "cast",
      "D": "check"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Managed Identity' in Azure .NET development?",
    "options": {
      "A": "A user who is managed by an admin",
      "B": "A feature that provides an identity for applications to use when connecting to resources that support Microsoft Entra ID",
      "C": "A password manager for developers",
      "D": "A way to log in with a fingerprint"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary purpose of 'Span<T>' in .NET?",
    "options": {
      "A": "To increase the length of a string",
      "B": "To provide a type-safe and memory-safe view into a contiguous region of arbitrary memory without allocation",
      "C": "To create a delay in a loop",
      "D": "To manage multiple databases at once"
    },
    "answer": "B"
  },
  {
    "question": "Which C# feature allows you to define 'default' values for parameters in a Lambda expression?",
    "options": {
      "A": "C# 12 Default Lambda Parameters",
      "B": "C# 7 Local Functions",
      "C": "Optional Attribute",
      "D": "This is not supported in C#"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Deadlock' in a multithreaded .NET application?",
    "options": {
      "A": "A thread that is finished",
      "B": "A situation where two or more threads are blocked forever, each waiting on the other",
      "C": "A database error",
      "D": "A system crash due to heat"
    },
    "answer": "B"
  },
  {
    "question": "What is 'MassTransit' or 'Rebus' used for in .NET Microservices?",
    "options": {
      "A": "Designing the CSS of the app",
      "B": "Message bus abstractions for distributed systems (RabbitMQ, Azure Service Bus)",
      "C": "Compressing images",
      "D": "Writing SQL queries"
    },
    "answer": "B"
  },
  {
    "question": "Which C# 12 feature simplifies the initialization of arrays, spans, and lists using a square bracket syntax [ ]?",
    "options": {
      "A": "List Patterns",
      "B": "Collection Expressions",
      "C": "Array Initializers",
      "D": "Raw Strings"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Source Generators' in the .NET compiler (Roslyn)?",
    "options": {
      "A": "A tool to generate documentation",
      "B": "A feature that lets developers inspect user code and generate new C# source files during compilation",
      "C": "A way to download code from GitHub",
      "D": "A visual code designer"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Saga Pattern' used for in distributed .NET systems?",
    "options": {
      "A": "To tell a story in the code",
      "B": "To manage data consistency across multiple microservices in long-running business transactions",
      "C": "To backup the server every day",
      "D": "To encrypt user passwords"
    },
    "answer": "B"
  },
  {
    "question": "Which status code should a Web API return if a request is valid but the user does not have the required permissions?",
    "options": {
      "A": "401 Unauthorized",
      "B": "403 Forbidden",
      "C": "404 Not Found",
      "D": "400 Bad Request"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Outbox Pattern'?",
    "options": {
      "A": "Sending emails from the server",
      "B": "Ensuring that a message is sent to a bus only if the local database transaction succeeds",
      "C": "A type of UI layout",
      "D": "Deleting data after 30 days"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Native AOT' (Ahead-Of-Time) compilation in .NET?",
    "options": {
      "A": "Compiling code while the user is typing",
      "B": "Compiling .NET apps into a self-contained native executable for faster startup and lower memory footprint",
      "C": "A legacy way to compile C++",
      "D": "Compiling code into a browser plugin"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Idempotency' in the context of an API?",
    "options": {
      "A": "The speed of the API",
      "B": "The property where making the same request multiple times has the same effect as making it once",
      "C": "An error in the code",
      "D": "A way to hide data"
    },
    "answer": "B"
  },
  {
    "question": "Which .NET tool is used to profile memory leaks and CPU usage?",
    "options": {
      "A": "dotMemory / dotTrace",
      "B": "Postman",
      "C": "NuGet",
      "D": "MSBuild"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Vertical Slice Architecture'?",
    "options": {
      "A": "Designing the database vertically",
      "B": "An architectural style where code is organized by features (slices) rather than layers (Clean Architecture)",
      "C": "A way to cut the server costs",
      "D": "A UI pattern for mobile apps"
    },
    "answer": "B"
  },
  {
    "question": "Which keyword is used in C# to define 'interceptors' (experimental in C# 12)?",
    "options": {
      "A": "intercept",
      "B": "InterceptsLocation",
      "C": "hook",
      "D": "override"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Distributed Tracing' (OpenTelemetry) used for?",
    "options": {
      "A": "Tracing the physical location of the server",
      "B": "Monitoring and troubleshooting requests as they flow through multiple microservices",
      "C": "Drawing a map of the database",
      "D": "Tracing the history of a variable"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Health Checks' in ASP.NET Core?",
    "options": {
      "A": "Checking the health of the developers",
      "B": "Middleware that exposes an endpoint to report the status of the app and its dependencies",
      "C": "A virus scanner",
      "D": "A tool to fix bugs automatically"
    },
    "answer": "B"
  },
  {
    "question": "Which attribute is used to prevent a property from being serialized into JSON?",
    "options": {
      "A": "[JsonIgnore]",
      "B": "[NoSerialize]",
      "C": "[Hide]",
      "D": "[Private]"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Rate Limiting' in an API?",
    "options": {
      "A": "Limiting the price of the API",
      "B": "Controlling the number of requests a client can make in a given time period",
      "C": "Speeding up the database",
      "D": "Limiting the number of users"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'ValueTask<T>'?",
    "options": {
      "A": "A faster way to create tasks",
      "B": "A value-type alternative to Task<T> that reduces allocations when an operation completes synchronously",
      "C": "A way to store numbers in a task",
      "D": "A tool for UI tasks"
    },
    "answer": "B"
  },
  {
    "question": "What is 'BenchmarkDotNet' used for?",
    "options": {
      "A": "To create a logo for the app",
      "B": "A library for professional benchmarking of .NET code performance",
      "C": "To test the internet speed",
      "D": "To check the hardware specifications"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Memory Marshal' used for in high-performance .NET code?",
    "options": {
      "A": "To secure the RAM from viruses",
      "B": "To perform unsafe conversions between Spans and ReadOnlySpans or different pointer types",
      "C": "To backup memory to the disk",
      "D": "To increase the size of the Garbage Collector"
    },
    "answer": "B"
  },
  {
    "question": "Which C# keyword is used to ensure a block of code is not interrupted by the Garbage Collector moving memory (pinning)?",
    "options": {
      "A": "lock",
      "B": "fixed",
      "C": "unsafe",
      "D": "static"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'LOH' (Large Object Heap) in .NET memory management?",
    "options": {
      "A": "A heap for storing very small integers",
      "B": "A specific area of the heap for objects larger than 85,000 bytes, which are handled differently by the GC",
      "C": "A database for large files",
      "D": "A cache for web images"
    },
    "answer": "B"
  },
  {
    "question": "What is 'SIMD' (Single Instruction, Multiple Data) in .NET?",
    "options": {
      "A": "A way to send one email to many people",
      "B": "Hardware acceleration that allows the CPU to perform the same operation on multiple data points simultaneously",
      "C": "A type of database join",
      "D": "A networking protocol"
    },
    "answer": "B"
  },
  {
    "question": "Which namespace contains classes for creating code at runtime via 'IL Emit'?",
    "options": {
      "A": "System.Reflection",
      "B": "System.Reflection.Emit",
      "C": "System.CodeDom",
      "D": "System.Runtime.Loader"
    },
    "answer": "B"
  },
  {
    "question": "What does 'ArrayPool<T>' provide in .NET?",
    "options": {
      "A": "A way to share arrays on social media",
      "B": "A resource pool that allows for the reuse of array instances to reduce Garbage Collection pressure",
      "C": "A backup of all arrays",
      "D": "A way to sort arrays faster"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Curiously Recurring Template Pattern' (CRTP) in C#?",
    "options": {
      "A": "A loop that never ends",
      "B": "A pattern where a class derives from a generic base class using itself as the type argument",
      "C": "A way to write recursive functions",
      "D": "A bug in the compiler"
    },
    "answer": "B"
  },
  {
    "question": "Which status code is most appropriate for an API that is 'Rate Limited'?",
    "options": {
      "A": "401 Unauthorized",
      "B": "429 Too Many Requests",
      "C": "503 Service Unavailable",
      "D": "403 Forbidden"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Object Pooling'?",
    "options": {
      "A": "Storing objects in a database",
      "B": "Keeping a set of initialized objects ready for use rather than creating and destroying them on demand",
      "C": "Grouping objects by their size",
      "D": "A way to delete objects"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Background Garbage Collection'?",
    "options": {
      "A": "Cleaning the office while the server is running",
      "B": "A GC mode that allows ephemeral generations (0 and 1) to be collected while a Generation 2 collection is in progress",
      "C": "Deleting files in the background",
      "D": "A setting that disables the GC"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Pinned Object Heap' (POH) introduced in .NET 5?",
    "options": {
      "A": "A heap for objects that the developer 'pins' so the GC cannot move them",
      "B": "A heap for passwords",
      "C": "A heap that is deleted every hour",
      "D": "A heap for static strings"
    },
    "answer": "A"
  },
  {
    "question": "Which C# keyword allows you to call a method that is defined in a DLL written in C or C++?",
    "options": {
      "A": "using",
      "B": "extern",
      "C": "native",
      "D": "import"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Memory<T>' compared to 'Span<T>'?",
    "options": {
      "A": "Memory<T> can be stored on the heap (e.g., in a class field), whereas Span<T> is a stack-only ref struct",
      "B": "Memory<T> is for integers only",
      "C": "Span<T> is slower",
      "D": "There is no difference"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Strongly Typed Id' pattern?",
    "options": {
      "A": "Using 'int' for all IDs",
      "B": "Wrapping primitive IDs (like Guid or int) in a custom record or struct to prevent passing a 'ProductId' where a 'UserId' is expected",
      "C": "Naming IDs with capital letters",
      "D": "Storing IDs in a separate database"
    },
    "answer": "B"
  },
  {
    "question": "Which C# 13 feature (latest) allows for improved 'params' support with collections other than arrays?",
    "options": {
      "A": "Params Collections",
      "B": "List Parameters",
      "C": "Collection Expressions in Params",
      "D": "Universal Params"
    },
    "answer": "A"
  },
  {
    "question": "What is the primary purpose of 'Roslyn' in the .NET ecosystem?",
    "options": {
      "A": "A new database engine",
      "B": "The open-source C# and Visual Basic compiler platform that provides rich code analysis APIs",
      "C": "A graphical designer for Windows Forms",
      "D": "A tool for compressing DLL files"
    },
    "answer": "B"
  },
  {
    "question": "In high-performance .NET, what is a 'Pinned Object'?",
    "options": {
      "A": "An object that cannot be deleted",
      "B": "An object whose memory address is fixed so the Garbage Collector cannot move it during compaction",
      "C": "An object shared between multiple servers",
      "D": "An object that is always stored on the stack"
    },
    "answer": "B"
  },
  {
    "question": "Which namespace provides 'Hardware Intrinsics' to access CPU-specific instructions like AVX2 or SSE?",
    "options": {
      "A": "System.Runtime.Intrinsics",
      "B": "System.Hardware.Optimize",
      "C": "System.CPU.Instructions",
      "D": "System.Runtime.Accelerate"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Workstation GC' vs 'Server GC' in .NET?",
    "options": {
      "A": "Workstation is for desktop; Server is for cloud",
      "B": "Workstation uses one GC thread; Server uses multiple GC threads (one per logical CPU) for higher throughput",
      "C": "Workstation is free; Server requires a license",
      "D": "Workstation deletes data faster"
    },
    "answer": "B"
  },
  {
    "question": "Which C# 13 feature (experimental/latest) allows for 'Ref Structs' to implement interfaces under specific conditions?",
    "options": {
      "A": "Interface Structs",
      "B": "Allows ref struct to implement interfaces (e.g., via 'allows ref struct' anti-constraint)",
      "C": "Generic Structs",
      "D": "Static Virtual Members"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Method Table' (MT) in the context of the .NET Runtime?",
    "options": {
      "A": "A list of all methods in a text file",
      "B": "An internal structure that stores information about a type, including its virtual method pointers",
      "C": "A database table for logs",
      "D": "A tool to sort methods alphabetically"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'unmanaged' constraint do in a generic C# declaration?",
    "options": {
      "A": "It allows the class to run without a license",
      "B": "It restricts the type to be a non-reference type that doesn't contain reference type fields at any level",
      "C": "It disables the Garbage Collector for that type",
      "D": "It allows the type to be used in Python"
    },
    "answer": "B"
  },
  {
    "question": "Which .NET utility is used to analyze memory dumps for troubleshooting production crashes?",
    "options": {
      "A": "Postman",
      "B": "WinDbg (with SOS extension)",
      "C": "NuGet",
      "D": "Fiddler"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Tiered Compilation' in .NET?",
    "options": {
      "A": "Compiling code on different servers",
      "B": "A mechanism where the JIT first compiles code quickly (Tier 0) and then re-optimizes 'hot' methods (Tier 1)",
      "C": "A way to charge for different versions of an app",
      "D": "Compiling code into different languages"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'SearchValues' type introduced in .NET 8?",
    "options": {
      "A": "To search a database faster",
      "B": "To provide highly optimized searching for sets of characters or bytes within a span",
      "C": "To create a search engine",
      "D": "To replace the 'Where' clause in LINQ"
    },
    "answer": "B"
  },
  {
    "question": "Which C# feature allows you to define a 'Constant' string that is interpolated at compile-time?",
    "options": {
      "A": "String.Concat",
      "B": "Constant Interpolated Strings (C# 10+)",
      "C": "Raw Strings",
      "D": "Static Strings"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Tail Call Optimization' in the CLR?",
    "options": {
      "A": "Removing the end of a string",
      "B": "An optimization where the current stack frame is reused for a function call at the end of a method",
      "C": "Deleting old data",
      "D": "Adding a 'tail' to a variable name"
    },
    "answer": "B"
  },
  {
    "question": "Which property in .NET 9 (experimental/preview) improves 'Task' performance by reducing overhead in high-throughput apps?",
    "options": {
      "A": "Task.Speed",
      "B": "TimeProvider / Improved Task Scheduling",
      "C": "FastTask",
      "D": "DirectTask"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Zero-Parameter Primary Constructor' in C# 12?",
    "options": {
      "A": "A constructor that doesn't exist",
      "B": "A feature allowing classes to have primary constructors without any parameters",
      "C": "A way to delete a constructor",
      "D": "A constructor used only for static classes"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'SyncRoot' pattern used for in legacy .NET collections?",
    "options": {
      "A": "To sync the root of the hard drive",
      "B": "To provide an object that can be used to synchronize access to the collection across threads",
      "C": "To rename the collection",
      "D": "To delete duplicate entries"
    },
    "answer": "B"
  },
  {
    "question": "Which class is used to perform highly efficient, low-level asynchronous I/O with Pipes in .NET?",
    "options": {
      "A": "System.IO.File",
      "B": "System.IO.Pipelines.Pipe",
      "C": "System.Net.Sockets",
      "D": "System.IO.StreamReader"
    },
    "answer": "B"
  },
  {
    "question": "What is 'ValueStringBuilder' (Internal/Common in .NET source)?",
    "options": {
      "A": "A StringBuilder for numbers",
      "B": "A stack-allocated (ref struct) alternative to StringBuilder for small, short-lived string building",
      "C": "A way to build strings for databases",
      "D": "A tool to count string length"
    },
    "answer": "B"
  },
  {
    "question": "What is 'VTable' (Virtual Method Table)?",
    "options": {
      "A": "A table in SQL for virtual data",
      "B": "The mechanism used by .NET to support dynamic dispatch (polymorphism) at runtime",
      "C": "A graphical table in UI",
      "D": "A way to sort objects"
    },
    "answer": "B"
  },
  {
    "question": "Which C# 11 feature allows you to use a string literally without needing to escape special characters like quotes or backslashes?",
    "options": {
      "A": "Interpolated Strings",
      "B": "Raw String Literals",
      "C": "Verbatim Strings",
      "D": "Base64 Strings"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Double-Checked Locking' pattern?",
    "options": {
      "A": "Checking a password twice",
      "B": "A strategy to reduce the overhead of acquiring a lock by testing the lock criterion before acquiring the lock",
      "C": "A database security feature",
      "D": "Checking a file size twice"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the [StructLayout] attribute in C#?",
    "options": {
      "A": "To change the color of the UI",
      "B": "To control the physical layout of the data fields of a class or struct in memory",
      "C": "To prevent a struct from being copied",
      "D": "To automatically generate a database table"
    },
    "answer": "B"
  },
  {
    "question": "Which C# 13 feature allows for 'Ref Structs' to be used as type arguments for generic parameters?",
    "options": {
      "A": "Ref Generics",
      "B": "The 'allows ref struct' anti-constraint",
      "C": "Safe Stack Types",
      "D": "Generic Struct Pointers"
    },
    "answer": "B"
  },
  {
    "question": "What is 'P/Invoke' (Platform Invocation Services) used for?",
    "options": {
      "A": "To call methods in another .NET assembly",
      "B": "To allow managed code to call unmanaged functions implemented in a DLL (like Win32 API)",
      "C": "To connect to a cloud provider",
      "D": "To debug asynchronous tasks"
    },
    "answer": "B"
  },
  {
    "question": "Which threading primitive is used to wait for a signal from another thread without using a busy-wait loop?",
    "options": {
      "A": "Thread.Sleep()",
      "B": "ManualResetEventSlim",
      "C": "Lock",
      "D": "While(true)"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Flyweight' pattern's primary application in .NET memory optimization?",
    "options": {
      "A": "Reducing memory usage by sharing as much data as possible with similar objects",
      "B": "Making objects fly across threads",
      "C": "Deleting objects that are too heavy",
      "D": "Automatically compressing strings"
    },
    "answer": "A"
  },
  {
    "question": "What is the role of the 'MetadataLoadContext' class?",
    "options": {
      "A": "To load data into a database",
      "B": "To inspect assemblies for metadata without actually executing the code inside them",
      "C": "To load CSS files",
      "D": "To manage user identities"
    },
    "answer": "B"
  },
  {
    "question": "Which keyword in C# ensures that a variable is read from and written to main memory, preventing CPU register caching?",
    "options": {
      "A": "static",
      "B": "volatile",
      "C": "extern",
      "D": "async"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'GCHandle' in .NET?",
    "options": {
      "A": "To handle Garbage Collector errors",
      "B": "To provide a way to access a managed object from unmanaged memory or to 'pin' it",
      "C": "To manually trigger a GC collection",
      "D": "To name a GC thread"
    },
    "answer": "B"
  },
  {
    "question": "What does 'COM Interop' allow a .NET application to do?",
    "options": {
      "A": "Communicate with a web browser",
      "B": "Interact with existing Component Object Model (COM) objects",
      "C": "Compile code for mobile devices",
      "D": "Compress large files"
    },
    "answer": "B"
  },
  {
    "question": "In .NET 8/9, what is 'Frozen Collections'?",
    "options": {
      "A": "Collections that cannot be read",
      "B": "Highly optimized, immutable collections designed for very fast read-only operations",
      "C": "Collections stored on a cold server",
      "D": "A bug where the app stops responding"
    },
    "answer": "B"
  },
  {
    "question": "Which utility class provides a mechanism to receive notifications when a file system changes?",
    "options": {
      "A": "FileChangeDetector",
      "B": "FileSystemWatcher",
      "C": "FileMonitor",
      "D": "DirectoryObserver"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Blazor WebAssembly' (WASM)?",
    "options": {
      "A": "A server-side rendering engine",
      "B": "A client-side web framework that runs .NET code in the browser using WebAssembly",
      "C": "A database for web apps",
      "D": "A way to compile JavaScript into C#"
    },
    "answer": "B"
  },
  {
    "question": "Which C# operator is used to determine the size, in bytes, of a value type at compile time?",
    "options": {
      "A": "sizeof",
      "B": "lengthof",
      "C": "bytesize",
      "D": "memoryof"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'Dispose' pattern used for in C#?",
    "options": {
      "A": "To hide code from users",
      "B": "To provide a deterministic way to release unmanaged resources like file handles or database connections",
      "C": "To delete old users from a database",
      "D": "To clear the cache of a web browser"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Expression Bodied Members' in C#?",
    "options": {
      "A": "A way to write code using emojis",
      "B": "A concise syntax for providing a member's implementation using the lambda arrow (=>)",
      "C": "A method to calculate math expressions",
      "D": "A tool for UI design"
    },
    "answer": "B"
  },
  {
    "question": "What is 'IAsyncEnumerable<T>' used for in C#?",
    "options": {
      "A": "To store a list of tasks in a database",
      "B": "To represent a data stream that can be iterated asynchronously using 'await foreach'",
      "C": "To sort a collection in a background thread",
      "D": "To download multiple files simultaneously"
    },
    "answer": "B"
  },
  {
    "question": "Which component is used to generate custom high-performance diagnostic events for ETW (Event Tracing for Windows)?",
    "options": {
      "A": "System.Diagnostics.EventSource",
      "B": "System.Logging.Debug",
      "C": "System.Console",
      "D": "System.Runtime.Tracker"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Stackalloc' used for in C#?",
    "options": {
      "A": "To allocate memory on the heap",
      "B": "To allocate a block of memory on the stack, which is automatically reclaimed when the method returns",
      "C": "To increase the size of the stack",
      "D": "To prevent stack overflow errors"
    },
    "answer": "B"
  },
  {
    "question": "Which C# 13 feature (experimental) improves overload resolution for methods involving spans and arrays?",
    "options": {
      "A": "Span Overload Priority",
      "B": "Implicit Span Conversion",
      "C": "Method Priority Attribute",
      "D": "Static Method Binding"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'Boxing' cost associated with using Interfaces on Value Types?",
    "options": {
      "A": "There is no cost",
      "B": "Calling a method through an interface on a struct causes the struct to be boxed into a reference type",
      "C": "The struct becomes a static class",
      "D": "The memory usage is reduced"
    },
    "answer": "B"
  },
  {
    "question": "What is 'MemoryPack' or 'MessagePack' used for in .NET performance tuning?",
    "options": {
      "A": "Formatting code automatically",
      "B": "Extremely fast binary serialization frameworks that outperform JSON or XML",
      "C": "Compressing memory dumps",
      "D": "Storing passwords in a secure way"
    },
    "answer": "B"
  },
  {
    "question": "What does 'GC.Collect()' do when called manually?",
    "options": {
      "A": "It deletes all variables in the app",
      "B": "It forces an immediate garbage collection of all generations (usually discouraged in production)",
      "C": "It closes all database connections",
      "D": "It restarts the web server"
    },
    "answer": "B"
  },
  {
    "question": "Which C# keyword is used to define a 'partial' method that can be optionally implemented in another part of a partial class?",
    "options": {
      "A": "abstract",
      "B": "partial",
      "C": "virtual",
      "D": "extern"
    },
    "answer": "B"
  },
  {
    "question": "What is 'SIMD' (Single Instruction, Multiple Data) primarily useful for?",
    "options": {
      "A": "Handling user login requests",
      "B": "Performing the same mathematical operation on a large array of data in parallel at the CPU level",
      "C": "Connecting to multiple SQL databases",
      "D": "Managing file system changes"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Inlining' in the context of JIT compilation?",
    "options": {
      "A": "Writing code in a single line",
      "B": "The process of replacing a function call with the actual body of the function to reduce call overhead",
      "C": "Moving code to the cloud",
      "D": "Converting C# to JavaScript"
    },
    "answer": "B"
  },
  {
    "question": "Which C# feature allows you to use 'pattern matching' to check the properties of an object?",
    "options": {
      "A": "Property Patterns",
      "B": "Object Checks",
      "C": "Regex Match",
      "D": "Dynamic Inspection"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Task.WhenAll' used for?",
    "options": {
      "A": "To run all tasks sequentially",
      "B": "To create a task that completes when all the provided tasks have finished",
      "C": "To delete all tasks",
      "D": "To restart the thread pool"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'ValueTask' over 'Task'?",
    "options": {
      "A": "It is easier to read",
      "B": "It is a struct that can avoid heap allocations in cases where the operation completes synchronously",
      "C": "It supports more data types",
      "D": "It can only be used with integers"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Hardware Intrinsics' in .NET?",
    "options": {
      "A": "A tool to fix broken hardware",
      "B": "APIs that allow direct access to CPU instructions (like SSE, AVX) for maximum performance",
      "C": "A way to measure CPU temperature",
      "D": "A legacy feature for old printers"
    },
    "answer": "B"
  },
  {
    "question": "Which C# 11 feature allows for static methods to be part of an interface?",
    "options": {
      "A": "Interface Statics",
      "B": "Static Virtual Members in Interfaces",
      "C": "Global Statics",
      "D": "Fixed Interface Members"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Allocation Ticketing' in the context of the .NET Garbage Collector?",
    "options": {
      "A": "A way to charge for memory usage",
      "B": "A mechanism to track how much memory each thread allocates to determine when a GC should be triggered",
      "C": "A method for sorting objects by size",
      "D": "A tool to limit the number of objects created"
    },
    "answer": "B"
  },
  {
    "question": "Which C# feature allows for 'Generic Math' by defining static abstract members in interfaces?",
    "options": {
      "A": "Dynamic Math",
      "B": "Static Virtual Members in Interfaces (C# 11)",
      "C": "Mathematical Generics",
      "D": "Operator Overloading"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Tier 1' JIT compilation in .NET?",
    "options": {
      "A": "The first time a method is compiled (quickly)",
      "B": "A re-optimization of 'hot' methods using full optimizations like loop unrolling and SIMD",
      "C": "Compiling code for mobile devices",
      "D": "A way to compile code into a browser"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Lock Contention' in a .NET application?",
    "options": {
      "A": "When a lock is deleted",
      "B": "When multiple threads attempt to acquire the same lock simultaneously, causing performance degradation",
      "C": "A security feature that prevents hacking",
      "D": "A way to speed up thread execution"
    },
    "answer": "B"
  },
  {
    "question": "Which class is used to perform high-performance, lock-free updates to a numeric value across multiple threads?",
    "options": {
      "A": "System.Threading.Interlocked",
      "B": "System.Threading.Monitor",
      "C": "System.Threading.Mutex",
      "D": "System.Threading.SpinLock"
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
    skill = ".Net"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
