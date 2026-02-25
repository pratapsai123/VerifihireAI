from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
    {
        "question": "What is the primary difference between ASP.NET and ASP.NET Core?",
        "options": {
            "A": "ASP.NET is faster",
            "B": "ASP.NET Core is cross-platform and modular; ASP.NET is Windows-only",
            "C": "ASP.NET Core only supports VB.NET",
            "D": "There is no difference"
        },
        "answer": "B"
    },
    {
        "question": "Which file is the entry point for an ASP.NET Core application where the web host is configured?",
        "options": {
            "A": "Startup.cs",
            "B": "Program.cs",
            "C": "Web.config",
            "D": "App.settings"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Middleware' in ASP.NET Core?",
        "options": {
            "A": "A type of database",
            "B": "Software components assembled into an application pipeline to handle requests and responses",
            "C": "A frontend framework",
            "D": "A tool for UI design"
        },
        "answer": "B"
    },
    {
        "question": "Which method in the Startup class (legacy) or Program.cs (modern) is used to register services for Dependency Injection?",
        "options": {
            "A": "Configure()",
            "B": "ConfigureServices()",
            "C": "Main()",
            "D": "MapRoutes()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Dependency Injection' (DI)?",
        "options": {
            "A": "A security vulnerability",
            "B": "A design pattern used to achieve Inversion of Control between classes and their dependencies",
            "C": "A way to inject CSS into HTML",
            "D": "A database query technique"
        },
        "answer": "B"
    },
    {
        "question": "In ASP.NET Core DI, what is the 'Scoped' lifetime?",
        "options": {
            "A": "A new instance is created every time it is requested",
            "B": "A new instance is created once per client request (HTTP request)",
            "C": "A single instance is created for the entire application lifetime",
            "D": "The service is only available in the UI"
        },
        "answer": "B"
    },
    {
        "question": "In ASP.NET Core DI, what is the 'Singleton' lifetime?",
        "options": {
            "A": "Created once per request",
            "B": "Created once the first time they are requested and every subsequent request uses the same instance",
            "C": "Created every time they are requested",
            "D": "Used only for static files"
        },
        "answer": "B"
    },
    {
        "question": "In ASP.NET Core DI, what is the 'Transient' lifetime?",
        "options": {
            "A": "Created once per request",
            "B": "Created every time they are requested from the service container",
            "C": "Shared across all users",
            "D": "Deleted after 5 minutes"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Kestrel'?",
        "options": {
            "A": "A database engine",
            "B": "A cross-platform, open-source web server for ASP.NET Core",
            "C": "A code editor",
            "D": "A testing framework"
        },
        "answer": "B"
    },
    {
        "question": "What is 'MVC' in the context of ASP.NET?",
        "options": {
            "A": "Metadata, View, Content",
            "B": "Model-View-Controller architectural pattern",
            "C": "Multiple View Configuration",
            "D": "Modern Variable Coding"
        },
        "answer": "B"
    },
    {
        "question": "What is the role of the 'Controller' in MVC?",
        "options": {
            "A": "To store data",
            "B": "To handle user input, interact with the model, and select a view to render",
            "C": "To style the user interface",
            "D": "To manage the server hardware"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Razor' in ASP.NET?",
        "options": {
            "A": "A tool to clean the code",
            "B": "A markup syntax that lets you embed C# code into web pages",
            "C": "A database connection string",
            "D": "A security firewall"
        },
        "answer": "B"
    },
    {
        "question": "Which file extension is used for Razor views?",
        "options": {
            "A": ".html",
            "B": ".cshtml",
            "C": ".razor",
            "D": "Both B and C"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Attribute Routing'?",
        "options": {
            "A": "Routing based on file size",
            "B": "Defining routes by applying attributes directly to controllers or actions (e.g., [Route(\"api/[controller]\")])",
            "C": "A type of database index",
            "D": "Styling routes with CSS"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'appsettings.json' file used for?",
        "options": {
            "A": "To write C# code",
            "B": "To store application configuration settings like connection strings or API keys",
            "C": "To define the UI layout",
            "D": "To log errors"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Strongly Typed View'?",
        "options": {
            "A": "A view that is difficult to change",
            "B": "A view that is associated with a specific data model class",
            "C": "A view that uses only bold fonts",
            "D": "A view stored in the database"
        },
        "answer": "B"
    },
    {
        "question": "Which object is used to pass small amounts of data from a Controller to a View?",
        "options": {
            "A": "Session",
            "B": "ViewData or ViewBag",
            "C": "QueryString",
            "D": "Cookie"
        },
        "answer": "B"
    },
    {
        "question": "What is the main difference between ViewData and ViewBag?",
        "options": {
            "A": "ViewData is faster",
            "B": "ViewData uses a dictionary; ViewBag uses dynamic properties",
            "C": "ViewBag is for mobile apps",
            "D": "ViewData only stores strings"
        },
        "answer": "B"
    },
    {
        "question": "What is 'TempData' used for?",
        "options": {
            "A": "Permanent storage",
            "B": "Storing data that should survive for only one additional HTTP request (common for redirects)",
            "C": "Caching images",
            "D": "Storing temporary user passwords"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Model Binding'?",
        "options": {
            "A": "Tying a model to a database",
            "B": "The process of mapping data from HTTP requests to action method parameters",
            "C": "A security feature",
            "D": "A type of UI styling"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Tag Helper'?",
        "options": {
            "A": "A person who tags code",
            "B": "A server-side component for creating and rendering HTML elements in Razor files",
            "C": "A metadata tool",
            "D": "A CSS class"
        },
        "answer": "B"
    },
    {
        "question": "Which Tag Helper attribute is used to create a link to a specific action method?",
        "options": {
            "A": "href",
            "B": "asp-action",
            "C": "asp-link",
            "D": "action-target"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Entity Framework Core' (EF Core)?",
        "options": {
            "A": "A UI library",
            "B": "A lightweight, extensible, open-source, and cross-platform version of Entity Framework ORM",
            "C": "A web server",
            "D": "A project management tool"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to add a new migration in EF Core?",
        "options": {
            "A": "dotnet ef add",
            "B": "dotnet ef migrations add <Name>",
            "C": "dotnet migrate",
            "D": "ef update"
        },
        "answer": "B"
    },
    {
        "question": "What is 'WWWROOT' folder in ASP.NET Core?",
        "options": {
            "A": "The folder for C# source code",
            "B": "The root folder for static files like CSS, JavaScript, and images",
            "C": "A hidden system folder",
            "D": "The database storage folder"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Action Filter'?",
        "options": {
            "A": "A tool to filter data in the UI",
            "B": "Attributes that can be applied to a controller action or controller that modify the way the action is executed",
            "C": "A type of database join",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "Which filter is used to handle authorization in ASP.NET Core?",
        "options": {
            "A": "Result Filter",
            "B": "Authorize Filter",
            "C": "Exception Filter",
            "D": "Resource Filter"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Web API'?",
        "options": {
            "A": "A website for developers",
            "B": "A framework for building HTTP services that can be consumed by a broad range of clients (browsers, mobile)",
            "C": "A type of internet connection",
            "D": "A browser plugin"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the [ApiController] attribute?",
        "options": {
            "A": "To make the controller run faster",
            "B": "To enable API-specific behaviors like automatic 400 responses for validation errors",
            "C": "To encrypt the API",
            "D": "To show the API in a browser"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Content Negotiation'?",
        "options": {
            "A": "Discussing price with a client",
            "B": "The process of selecting the best representation (JSON, XML) for a given response when multiple options are available",
            "C": "Encrypting the data",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Which format is returned by default in ASP.NET Core Web API?",
        "options": {
            "A": "XML",
            "B": "JSON",
            "C": "HTML",
            "D": "Plain Text"
        },
        "answer": "B"
    },
    {
        "question": "What is 'NuGet'?",
        "options": {
            "A": "A type of database",
            "B": "The package manager for .NET",
            "C": "A coding language",
            "D": "A cloud provider"
        },
        "answer": "B"
    },
    {
        "question": "What is 'LaunchSettings.json' for?",
        "options": {
            "A": "To store production passwords",
            "B": "To define the profiles used to run and debug the application from Visual Studio",
            "C": "To configure the database",
            "D": "To set the app icon"
        },
        "answer": "B"
    },
    {
        "question": "What is the role of 'IConfiguration' interface?",
        "options": {
            "A": "To build the project",
            "B": "To provide access to application settings and configurations from berbagai sources (json, env vars)",
            "C": "To configure the UI",
            "D": "To manage user logins"
        },
        "answer": "B"
    },
    {
        "question": "What is 'View Component'?",
        "options": {
            "A": "A piece of the database",
            "B": "A powerful alternative to partial views, intended for logic-heavy UI chunks",
            "C": "A CSS class",
            "D": "A JavaScript function"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'HttpContext' object?",
        "options": {
            "A": "The text on the page",
            "B": "An object that holds information about the current HTTP request and response",
            "C": "A type of sharding",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'State Management' in ASP.NET?",
        "options": {
            "A": "Managing different countries",
            "B": "The process of maintaining user data across multiple requests (e.g., Session, Cookies)",
            "C": "Updating the server status",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "How do you enable 'Session' in ASP.NET Core?",
        "options": {
            "A": "It is enabled by default",
            "B": "By adding session services and middleware in Program.cs",
            "C": "By adding a cookie",
            "D": "By restarting the server"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Area' in ASP.NET MVC?",
        "options": {
            "A": "The size of the screen",
            "B": "A feature used to organize complex applications into smaller functional groups",
            "C": "A database partition",
            "D": "A security zone"
        },
        "answer": "B"
    },
    {
        "question": "Which attribute prevents a public method in a Controller from being treated as an action?",
        "options": {
            "A": "[Hidden]",
            "B": "[NonAction]",
            "C": "[Private]",
            "D": "[Ignore]"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Partial View'?",
        "options": {
            "A": "A view that is only half finished",
            "B": "A Razor file that can be rendered inside another view (reusable UI component)",
            "C": "A view for mobile only",
            "D": "A database view"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Model Validation' using Data Annotations?",
        "options": {
            "A": "Validating the database schema",
            "B": "Applying attributes like [Required] or [StringLength] to model properties to enforce rules",
            "C": "Checking the model size",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Which property of ModelState is checked to see if validation failed?",
        "options": {
            "A": "IsValid",
            "B": "HasError",
            "C": "Passed",
            "D": "Success"
        },
        "answer": "A"
    },
    {
        "question": "What is 'IIS' (Internet Information Services)?",
        "options": {
            "A": "A coding language",
            "B": "A flexible, general-purpose web server from Microsoft that runs on Windows",
            "C": "A cloud provider",
            "D": "A browser"
        },
        "answer": "B"
    },
    {
        "question": "What is 'CORS' (Cross-Origin Resource Sharing)?",
        "options": {
            "A": "A type of server hardware",
            "B": "A security feature that allows or restricts web applications from making requests to a different domain",
            "C": "A database join",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "Which middleware is used to serve static files?",
        "options": {
            "A": "app.UseRouting()",
            "B": "app.UseStaticFiles()",
            "C": "app.UseFileServer()",
            "D": "app.UseAssets()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Action Result'?",
        "options": {
            "A": "The result of a football game",
            "B": "The return type of a controller action that defines the response (e.g., ViewResult, JsonResult)",
            "C": "A security scan result",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Which method returns a 404 Not Found response in a Controller?",
        "options": {
            "A": "ReturnError()",
            "B": "NotFound()",
            "C": "Error404()",
            "D": "Missing()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Global Query Filter' in EF Core?",
        "options": {
            "A": "A filter for every user",
            "B": "A filter applied automatically to all queries for an entity (often used for soft deletes)",
            "C": "A type of index",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 1: What is 'Hot Reload' in .NET?",
        "options": {
            "A": "The server getting too hot",
            "B": "A feature that allows code changes to be applied to a running app without manual pause or rebuild",
            "C": "A security attack",
            "D": "A database backup"
        },
        "answer": "B"
    },
    {
        "question": "What is 'ASP.NET Core Identity'?",
        "options": {
            "A": "A profile of the developer",
            "B": "A membership system that adds login functionality, managing users, passwords, and roles",
            "C": "A database for storing images",
            "D": "A tool for UI themes"
        },
        "answer": "B"
    },
    {
        "question": "Which middleware is essential for enabling ASP.NET Core Identity in the request pipeline?",
        "options": {
            "A": "app.UseRouting()",
            "B": "app.UseAuthentication() and app.UseAuthorization()",
            "C": "app.UseIdentity()",
            "D": "app.UseLogin()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'SignalR' used for?",
        "options": {
            "A": "To increase the network signal",
            "B": "To add real-time web functionality, allowing server-side code to push content to clients instantly",
            "C": "To compress video files",
            "D": "To manage database backups"
        },
        "answer": "B"
    },
    {
        "question": "Which class does a server-side SignalR component inherit from?",
        "options": {
            "A": "Controller",
            "B": "Hub",
            "C": "Socket",
            "D": "Broadcaster"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Options Pattern' in ASP.NET Core?",
        "options": {
            "A": "Choosing between different themes",
            "B": "Using classes to provide strongly typed access to groups of related settings",
            "C": "A way to write SQL queries",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Cross-Site Scripting' (XSS) and how does ASP.NET Core help prevent it?",
        "options": {
            "A": "A type of CSS error",
            "B": "A vulnerability where scripts are injected into web pages; Razor automatically HTML-encodes output to prevent it",
            "C": "A database attack",
            "D": "A network speed issue"
        },
        "answer": "B"
    },
    {
        "question": "Which attribute is used to protect an action from Cross-Site Request Forgery (CSRF)?",
        "options": {
            "A": "[Protect]",
            "B": "[ValidateAntiForgeryToken]",
            "C": "[NoCsrf]",
            "D": "[Secure]"
        },
        "answer": "B"
    },
    {
        "question": "What is 'JWT' (JSON Web Token) commonly used for in Web APIs?",
        "options": {
            "A": "To store large images",
            "B": "For stateless authentication between a client and a server",
            "C": "To encrypt the database",
            "D": "To track page views"
        },
        "answer": "B"
    },
    {
        "question": "What are the three parts of a JWT?",
        "options": {
            "A": "Header, Body, Footer",
            "B": "Header, Payload, Signature",
            "C": "User, Pass, Key",
            "D": "Start, Middle, End"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Claims-Based Authorization'?",
        "options": {
            "A": "Asking for money",
            "B": "Authorization based on specific pieces of information about a user (claims) rather than just roles",
            "C": "A type of database join",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Policy-Based Authorization'?",
        "options": {
            "A": "Following company rules",
            "B": "A logic-based approach where an authorization requirement consists of one or more policies",
            "C": "A type of sharding",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "Which interface is used to interact with the database context in EF Core?",
        "options": {
            "A": "DbContext",
            "B": "EntitySession",
            "C": "SqlManager",
            "D": "DataContext"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Data Seeding'?",
        "options": {
            "A": "Planting trees in the server room",
            "B": "The process of populating a database with an initial set of data",
            "C": "A type of database backup",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Automapper' commonly used for in ASP.NET projects?",
        "options": {
            "A": "To find locations on a map",
            "B": "To automatically map properties between two different objects (e.g., Entity to DTO)",
            "C": "To generate SQL",
            "D": "To style the UI"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'DTO' (Data Transfer Object)?",
        "options": {
            "A": "A database table",
            "B": "An object that carries data between processes to reduce the number of method calls",
            "C": "A type of network cable",
            "D": "A security key"
        },
        "answer": "B"
    },
    {
        "question": "What is 'In-Memory Cache'?",
        "options": {
            "A": "Caching data on the user's brain",
            "B": "Storing data in the web server's memory to improve performance",
            "C": "A slow database",
            "D": "A backup on a USB drive"
        },
        "answer": "B"
    },
    {
        "question": "Which interface is used for In-Memory caching in ASP.NET Core?",
        "options": {
            "A": "ICache",
            "B": "IMemoryCache",
            "C": "IStore",
            "D": "IDataCache"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Distributed Cache' (e.g., Redis)?",
        "options": {
            "A": "A cache spread across the internet",
            "B": "A cache shared by multiple app servers, ensuring data consistency in a load-balanced environment",
            "C": "A cache for mobile only",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Response Caching' middleware?",
        "options": {
            "A": "Caching the user's keyboard input",
            "B": "Middleware that caches server responses based on HTTP cache headers",
            "C": "A type of sharding",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Self-Contained' deployment in .NET?",
        "options": {
            "A": "The app runs in a box",
            "B": "A deployment that includes the .NET runtime, so it doesn't need to be installed on the target machine",
            "C": "A private app",
            "D": "A database backup"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Framework-Dependent' deployment?",
        "options": {
            "A": "The app depends on the developer",
            "B": "A deployment that relies on a shared system-wide version of .NET being present on the target machine",
            "C": "A legacy feature",
            "D": "A security risk"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Environments' (Development, Staging, Production) in ASP.NET Core?",
        "options": {
            "A": "To change the background color",
            "B": "To allow different configurations and behaviors based on where the app is running",
            "C": "To track user locations",
            "D": "To manage multiple databases"
        },
        "answer": "B"
    },
    {
        "question": "Which environment variable is used to set the app environment?",
        "options": {
            "A": "DOTNET_ENV",
            "B": "ASPNETCORE_ENVIRONMENT",
            "C": "APP_SETTING",
            "D": "WEB_STATUS"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Health Checks' in ASP.NET Core?",
        "options": {
            "A": "Checking the developer's pulse",
            "B": "An endpoint that reports the health of app components like databases or external APIs",
            "C": "A security scan",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Which tool is commonly used to document and test ASP.NET Core Web APIs?",
        "options": {
            "A": "Word",
            "B": "Swagger (Swashbuckle)",
            "C": "Postman only",
            "D": "Excel"
        },
        "answer": "B"
    },
    {
        "question": "What is 'OpenAPI'?",
        "options": {
            "A": "A free API for everyone",
            "B": "A standard specification for describing RESTful APIs",
            "C": "A type of network protocol",
            "D": "A database query language"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Gzip' or 'Brotli' compression middleware used for?",
        "options": {
            "A": "To compress images",
            "B": "To reduce the size of HTTP responses (HTML, CSS, JS) to save bandwidth and speed up load times",
            "C": "To encrypt the data",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Logging' in ASP.NET Core?",
        "options": {
            "A": "Cutting down trees",
            "B": "Recording information about the application's execution for debugging and monitoring",
            "C": "Calculating the log of a number",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "Which interface is used for logging in ASP.NET Core?",
        "options": {
            "A": "ILog",
            "B": "ILogger<T>",
            "C": "IWrite",
            "D": "IJournal"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Serilog' or 'NLog'?",
        "options": {
            "A": "A coding language",
            "B": "Third-party logging frameworks that provide structured logging and various 'sinks' (outputs)",
            "C": "A type of database",
            "D": "A UI component"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Structured Logging'?",
        "options": {
            "A": "Logging in a straight line",
            "B": "Logging data as a set of name-value pairs (often JSON) so it can be easily searched and analyzed",
            "C": "A type of unit test",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Exception Handling Middleware'?",
        "options": {
            "A": "Middleware that fixes bugs automatically",
            "B": "Middleware that catches unhandled exceptions and returns a custom error page or JSON response",
            "C": "A type of firewall",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'HSTS' (HTTP Strict Transport Security)?",
        "options": {
            "A": "A faster network protocol",
            "B": "A security header that tells browsers to only interact with the site using HTTPS",
            "C": "A database index",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Antiforgery' service used for?",
        "options": {
            "A": "To catch fake money",
            "B": "To generate and validate tokens to protect against CSRF attacks",
            "C": "To check for stolen code",
            "D": "To verify user IDs"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Cookie Authentication'?",
        "options": {
            "A": "Eating cookies while coding",
            "B": "A stateful authentication mechanism where the server stores a session cookie in the client's browser",
            "C": "A security scan",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'External Authentication' (OAuth/OpenID Connect)?",
        "options": {
            "A": "Logging in from a different computer",
            "B": "Allowing users to sign in using third-party providers like Google, Facebook, or Microsoft",
            "C": "A security firewall",
            "D": "A type of sharding"
        },
        "answer": "B"
    },
    {
        "question": "What is 'IdentityServer'?",
        "options": {
            "A": "A server that stores IDs",
            "B": "A popular OpenID Connect and OAuth 2.0 framework for ASP.NET Core",
            "C": "A type of database",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Fluent Validation' library?",
        "options": {
            "A": "Validation that is very fast",
            "B": "A popular library for building strongly-typed validation rules using a fluent interface",
            "C": "A type of database join",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Background Tasks' (Hosted Services) in ASP.NET Core?",
        "options": {
            "A": "Tasks that run on the wallpaper",
            "B": "Long-running tasks that run in the background of the web application (e.g., email sending, data processing)",
            "C": "A type of sharding",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Which interface is implemented to create a background hosted service?",
        "options": {
            "A": "IService",
            "B": "IHostedService",
            "C": "IWorker",
            "D": "IBackground"
        },
        "answer": "B"
    },
    {
        "question": "What is 'SignalR Groups'?",
        "options": {
            "A": "A group of developers",
            "B": "A way to organize SignalR connections so you can send messages to a specific subset of users",
            "C": "A type of database join",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Sticky Sessions' in the context of SignalR?",
        "options": {
            "A": "Sessions that never end",
            "B": "A configuration that ensures a client always connects to the same server instance in a load-balanced environment",
            "C": "A security firewall",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Azure SignalR Service'?",
        "options": {
            "A": "To make SignalR run on a phone",
            "B": "A managed service that handles scaling and persistent connections for SignalR applications",
            "C": "A database engine",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'User Secrets' in ASP.NET Core development?",
        "options": {
            "A": "The user's password",
            "B": "A tool for storing sensitive configuration data (like API keys) locally during development, outside of source control",
            "C": "A private database",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Configuration Providers'?",
        "options": {
            "A": "People who set up the server",
            "B": "Components that read configuration data from various sources (JSON, XML, Environment Variables, Azure Key Vault)",
            "C": "A type of sharding",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Secret Manager' tool?",
        "options": {
            "A": "A person in charge of security",
            "B": "A command-line tool used to manage user secrets for a project",
            "C": "A security scanner",
            "D": "A database engine"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Key Vault' integration for?",
        "options": {
            "A": "Storing physical keys",
            "B": "Securely storing and accessing secrets, keys, and certificates in the cloud",
            "C": "A type of sharding",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Data Protection API' (DPAPI) in ASP.NET Core?",
        "options": {
            "A": "A way to lock the computer",
            "B": "A cryptographic API used to protect data at rest (e.g., cookies, state tokens)",
            "C": "A security scan",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Key Ring' in the Data Protection system?",
        "options": {
            "A": "A ring of developers",
            "B": "A collection of cryptographic keys used to encrypt and decrypt data",
            "C": "A security firewall",
            "D": "A type of sharding"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 2: Which component is responsible for token generation and management in ASP.NET Core Identity?",
        "options": {
            "A": "UserManager",
            "B": "SignInManager",
            "C": "TokenProvider",
            "D": "SecurityManager"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Eager Loading' in Entity Framework Core?",
        "options": {
            "A": "Loading data before the user asks for it",
            "B": "Fetching related data from the database as part of the initial query using the .Include() method",
            "C": "Loading data into the CPU cache",
            "D": "A way to speed up the UI"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Lazy Loading' in EF Core?",
        "options": {
            "A": "Loading data only when the developer is ready",
            "B": "A pattern where related data is transparently loaded from the database only when the navigation property is accessed",
            "C": "A performance bug that slows down the app",
            "D": "Loading data in the background"
        },
        "answer": "B"
    },
    {
        "question": "Which EF Core method is used to execute a raw SQL query that returns entities?",
        "options": {
            "A": "ExecuteSqlRaw()",
            "B": "FromSqlRaw()",
            "C": "RunSql()",
            "D": "GetEntitiesFromSql()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Shadow Properties' in EF Core?",
        "options": {
            "A": "Properties that don't have a value",
            "B": "Properties that are defined in the EF Core model but not in the actual C# class",
            "C": "Private properties",
            "D": "Hidden columns in the UI"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'AsNoTracking()' in a LINQ query?",
        "options": {
            "A": "To make the query private",
            "B": "To improve performance for read-only scenarios by telling EF Core not to track changes for the returned entities",
            "C": "To prevent the database from logging the query",
            "D": "To delete the entities after reading"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Unit Testing' in the context of ASP.NET Core?",
        "options": {
            "A": "Testing the whole app at once",
            "B": "Testing individual components or methods in isolation to ensure they work correctly",
            "C": "Testing the internet connection",
            "D": "Testing the database speed"
        },
        "answer": "B"
    },
    {
        "question": "Which framework is most commonly used for Unit Testing in .NET?",
        "options": {
            "A": "NUnit",
            "B": "xUnit",
            "C": "MSTest",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Moq' or 'NSubstitute' used for in testing?",
        "options": {
            "A": "To run the tests faster",
            "B": "To create 'Mock' objects that simulate the behavior of complex dependencies like databases or APIs",
            "C": "To style the test reports",
            "D": "To encrypt the test code"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Integration Testing'?",
        "options": {
            "A": "Testing if the developer fits in the team",
            "B": "Testing how different components of the application work together, including external dependencies like the database",
            "C": "Testing the app on different browsers",
            "D": "Combining code from different files"
        },
        "answer": "B"
    },
    {
        "question": "What is the role of 'WebApplicationFactory' in Integration Testing?",
        "options": {
            "A": "To build the website for production",
            "B": "To bootstrap the application in memory to run tests against the full request pipeline",
            "C": "To manage the cloud server",
            "D": "To generate sample data"
        },
        "answer": "B"
    },
    {
        "question": "What is 'In-Memory Database' provider in EF Core testing?",
        "options": {
            "A": "A way to save the DB to a USB",
            "B": "A provider that stores data in RAM, used to test database logic without a physical SQL server",
            "C": "A slow database",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Response Compression'?",
        "options": {
            "A": "Squeezing the UI onto a small screen",
            "B": "Reducing the size of data sent from the server to the client using algorithms like Gzip or Brotli",
            "C": "Deleting old responses",
            "D": "Compressing images only"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Bundling and Minification'?",
        "options": {
            "A": "Packing the server into a box",
            "B": "Combining multiple CSS/JS files into one and removing whitespace to reduce load times",
            "C": "A type of database join",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Kestrel' vs 'IIS' in a production environment?",
        "options": {
            "A": "Kestrel is for the frontend; IIS is for the backend",
            "B": "IIS often acts as a reverse proxy that forwards requests to the Kestrel edge server",
            "C": "Kestrel is only for Windows",
            "D": "IIS is a database; Kestrel is a web server"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Reverse Proxy'?",
        "options": {
            "A": "A proxy that works backward",
            "B": "A server (like Nginx or IIS) that sits in front of web servers and forwards client requests to them",
            "C": "A database backup",
            "D": "A security firewall"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Dockerization' of an ASP.NET Core app?",
        "options": {
            "A": "Making the app look like a ship",
            "B": "Packaging the application and its dependencies into a container to ensure consistent behavior across environments",
            "C": "Storing the app in a cloud",
            "D": "Updating the .NET version"
        },
        "answer": "B"
    },
    {
        "question": "Which file contains instructions for building a Docker image of an ASP.NET app?",
        "options": {
            "A": "Docker.json",
            "B": "Dockerfile",
            "C": "Container.config",
            "D": "Manifest.yaml"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Auto-Scaling' in cloud deployment (e.g., Azure App Service)?",
        "options": {
            "A": "Changing the size of the font automatically",
            "B": "Automatically increasing or decreasing the number of running instances of an app based on traffic",
            "C": "A type of database sharding",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Blue-Green Deployment'?",
        "options": {
            "A": "A colorful UI theme",
            "B": "A release strategy that uses two identical production environments to minimize downtime and risk",
            "C": "A security attack",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "What is 'SignalR Scale-out'?",
        "options": {
            "A": "Making SignalR work on larger screens",
            "B": "Using a backplane (like Redis) to sync messages across multiple server instances in a load-balanced setup",
            "C": "Adding more users to a group",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Concurrency Conflict' in EF Core?",
        "options": {
            "A": "Two developers working on the same file",
            "B": "When multiple users attempt to update the same database record at the same time",
            "C": "A performance bottleneck",
            "D": "A syntax error"
        },
        "answer": "B"
    },
    {
        "question": "How do you implement 'Optimistic Concurrency' in EF Core?",
        "options": {
            "A": "Hoping for the best",
            "B": "Using a concurrency token (like a RowVersion column) to detect changes before saving",
            "C": "Locking the database for 1 hour",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Database First' approach?",
        "options": {
            "A": "Creating the database before the code",
            "B": "Generating the C# models and DbContext from an existing database schema",
            "C": "A strategy for slow networks",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Code First' approach?",
        "options": {
            "A": "Writing code before thinking",
            "B": "Defining the data model using C# classes and then generating the database schema from them",
            "C": "A type of sharding",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Which tool is used for 'Profiling' an ASP.NET Core application performance?",
        "options": {
            "A": "DotTrace or Visual Studio Profiler",
            "B": "Notepad",
            "C": "Excel",
            "D": "Calculator"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Memory Leak' in a C# application?",
        "options": {
            "A": "CPU getting too hot",
            "B": "When objects are no longer needed but are still referenced, preventing the Garbage Collector from freeing RAM",
            "C": "A hard drive failure",
            "D": "A security vulnerability"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Garbage Collection' (GC)?",
        "options": {
            "A": "Taking out the office trash",
            "B": "The automatic memory management system in .NET that reclaims memory occupied by unused objects",
            "C": "Deleting old files",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Async/Await' for?",
        "options": {
            "A": "Making the code look modern",
            "B": "Performing non-blocking operations to improve application throughput and responsiveness",
            "C": "To pause the program",
            "D": "To speed up calculation"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Task.WhenAll()' used for?",
        "options": {
            "A": "To start all tasks at once",
            "B": "To wait for multiple asynchronous tasks to complete in parallel",
            "C": "To delete all tasks",
            "D": "To log task results"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Deadlock' in asynchronous programming?",
        "options": {
            "A": "A broken lock",
            "B": "A situation where two or more tasks are waiting for each other to finish, causing the app to hang",
            "C": "A security attack",
            "D": "A database error"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to map a C# property to a specific column name in the database?",
        "options": {
            "A": "[Table]",
            "B": "[Column(\"Name\")]",
            "C": "[Field]",
            "D": "[MapTo]"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Fluent API' in EF Core?",
        "options": {
            "A": "An API that speaks many languages",
            "B": "A way to configure the model by overriding the OnModelCreating method in the DbContext",
            "C": "A fast internet connection",
            "D": "A type of sharding"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Data Annotation' vs 'Fluent API'?",
        "options": {
            "A": "Fluent API is more powerful and keeps models clean; Data Annotations are simpler but clutter the model",
            "B": "Data Annotations are for mobile; Fluent API is for web",
            "C": "They are the same",
            "D": "Data Annotations are only for SQL"
        },
        "answer": "A"
    },
    {
        "question": "What is 'TDD' (Test Driven Development)?",
        "options": {
            "A": "Testing during development",
            "B": "The practice of writing a failing unit test before writing the code to pass it",
            "C": "Testing only at the end",
            "D": "A database index"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Red-Green-Refactor'?",
        "options": {
            "A": "A colorful UI theme",
            "B": "The core cycle of TDD: write failing test (Red), make it pass (Green), then optimize (Refactor)",
            "C": "A type of sharding",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Code Coverage'?",
        "options": {
            "A": "The number of lines of code",
            "B": "A metric that shows what percentage of your source code is executed when your test suite runs",
            "C": "A security scan",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Mocking' vs 'Stubbing'?",
        "options": {
            "A": "Mocking is for objects; Stubbing is for methods",
            "B": "Mocks verify interactions (was it called?); Stubs provide canned answers to calls",
            "C": "They are the same",
            "D": "Mocking is only for Java"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Output Caching' (ASP.NET Core 7+)?",
        "options": {
            "A": "Caching the UI icons",
            "B": "A middleware that caches the entire HTTP response on the server for later reuse",
            "C": "Caching database queries only",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Minimal APIs' introduced in .NET 6?",
        "options": {
            "A": "Small APIs for mobile",
            "B": "An approach to build HTTP APIs with minimal code and ceremony, typically in Program.cs",
            "C": "A bug in the API",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Endpoint Routing'?",
        "options": {
            "A": "Routing to the end of the page",
            "B": "A routing system that separates route matching from the execution of the endpoint (controller action)",
            "C": "A type of database join",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'IHttpClientFactory' used for?",
        "options": {
            "A": "To create the internet",
            "B": "To manage the lifecycle and configuration of HttpClient instances efficiently",
            "C": "To download files",
            "D": "To speed up the network"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Polly' library often used for with HttpClient?",
        "options": {
            "A": "A talking bird",
            "B": "A resilience and transient-fault-handling library (Retries, Circuit Breaker)",
            "C": "To style the UI",
            "D": "To generate SQL"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure App Service'?",
        "options": {
            "A": "A phone app",
            "B": "A fully managed platform for building, deploying, and scaling web apps in Azure",
            "C": "A database engine",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'CI/CD' (Continuous Integration / Continuous Deployment)?",
        "options": {
            "A": "Continuous coding",
            "B": "Automated processes to build, test, and deploy code changes frequently and reliably",
            "C": "A security scan",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Which tool is commonly used for CI/CD with .NET?",
        "options": {
            "A": "GitHub Actions",
            "B": "Azure DevOps",
            "C": "Jenkins",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "What is 'App Insights' (Application Insights)?",
        "options": {
            "A": "Insights into the developer's mind",
            "B": "An Azure monitoring service that provides real-time analytics and telemetry for web apps",
            "C": "A database query tool",
            "D": "A UI design tool"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Lazy Initialization' (Lazy<T>) in C#?",
        "options": {
            "A": "Waiting for the user to login",
            "B": "Delaying the creation of an object until it is accessed for the first time",
            "C": "A performance bug",
            "D": "A type of sharding"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'IAsyncEnumerable' in C# 8+?",
        "options": {
            "A": "To count fast",
            "B": "To stream results from a database or API asynchronously",
            "C": "To delete files",
            "D": "To sort data"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 3: Which EF Core feature allows you to use a different database provider for production and testing?",
        "options": {
            "A": "DbContextOptions",
            "B": "EntityProvider",
            "C": "DatabaseManager",
            "D": "ProviderSwitcher"
        },
        "answer": "A"
    },
    {
        "question": "What is the primary benefit of using gRPC over REST for service-to-service communication in ASP.NET Core?",
        "options": {
            "A": "It is easier to debug in a browser",
            "B": "Higher performance due to binary serialization (Protobuf) and HTTP/2 multiplexing",
            "C": "It does not require any contracts",
            "D": "It uses JSON by default"
        },
        "answer": "B"
    },
    {
        "question": "Which file type is used to define the service contract and messages in a gRPC project?",
        "options": {
            "A": ".json",
            "B": ".proto",
            "C": ".grpc",
            "D": ".xml"
        },
        "answer": "B"
    },
    {
        "question": "What is 'API Versioning' and why is it important?",
        "options": {
            "A": "To change the app name",
            "B": "To allow existing clients to continue working while introducing breaking changes in newer API versions",
            "C": "To update the .NET version",
            "D": "To show the developer's name"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Ocelot' in the context of ASP.NET Core microservices?",
        "options": {
            "A": "A testing framework",
            "B": "A lightweight API Gateway for microservices architecture",
            "C": "A database engine",
            "D": "A frontend library"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Distributed Tracing'?",
        "options": {
            "A": "Drawing diagrams across multiple computers",
            "B": "A method to track and observe requests as they flow through various services in a microservices environment",
            "C": "Logging only errors",
            "D": "A type of database join"
        },
        "answer": "B"
    },
    {
        "question": "Which tool is commonly used for distributed tracing in .NET (often with OpenTelemetry)?",
        "options": {
            "A": "Docker",
            "B": "Jaeger or Zipkin",
            "C": "Notepad++",
            "D": "Postman"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Health Check UI' middleware?",
        "options": {
            "A": "A tool to monitor developer health",
            "B": "A visual dashboard that displays the health status of various system dependencies",
            "C": "A type of firewall",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Graceful Shutdown' in ASP.NET Core?",
        "options": {
            "A": "The server crashing quietly",
            "B": "The ability of the app to finish processing existing requests before the server stops",
            "C": "A security certificate",
            "D": "A database backup"
        },
        "answer": "B"
    },
    {
        "question": "Which interface provides access to application lifetime events like 'Started' or 'Stopping'?",
        "options": {
            "A": "IAppLifetime",
            "B": "IHostApplicationLifetime",
            "C": "IWebLifetime",
            "D": "IServiceLifetime"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Response Buffering'?",
        "options": {
            "A": "The UI loading slowly",
            "B": "Storing the entire response in memory before sending it to the client",
            "C": "A type of sharding",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Rate Limiting' middleware used for?",
        "options": {
            "A": "To limit the speed of the CPU",
            "B": "To restrict the number of requests a client can make to the server within a specific timeframe",
            "C": "To charge users for bandwidth",
            "D": "To monitor database size"
        },
        "answer": "B"
    },
    {
        "question": "What is 'YARP' (Yet Another Reverse Proxy)?",
        "options": {
            "A": "A programming language",
            "B": "A toolkit for building high-performance reverse proxy servers using .NET",
            "C": "A database tool",
            "D": "A security attack"
        },
        "answer": "B"
    },
    {
        "question": "Which ASP.NET Core feature is used to handle real-time binary data streaming?",
        "options": {
            "A": "SignalR",
            "B": "gRPC Streaming",
            "C": "MVC Controller",
            "D": "Razor Pages"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Bff' (Backend for Frontend) pattern?",
        "options": {
            "A": "A backend that is best friends with the frontend",
            "B": "Creating separate backend services tailored specifically for different client types (e.g., Mobile vs. Web)",
            "C": "A type of database join",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Idempotency' in the context of APIs?",
        "options": {
            "A": "The speed of the API",
            "B": "The property where multiple identical requests have the same effect as a single request",
            "C": "A security certificate",
            "D": "A data compression type"
        },
        "answer": "B"
    },
    {
        "question": "Which HTTP method is NOT inherently idempotent?",
        "options": {
            "A": "GET",
            "B": "PUT",
            "C": "POST",
            "D": "DELETE"
        },
        "answer": "C"
    },
    {
        "question": "What is 'Circuit Breaker' pattern?",
        "options": {
            "A": "Turning off the power",
            "B": "A design pattern used to prevent a service from repeatedly trying to execute an operation that's likely to fail",
            "C": "A type of firewall",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Which library is the industry standard for implementing the Circuit Breaker pattern in .NET?",
        "options": {
            "A": "AutoMapper",
            "B": "Polly",
            "C": "Serilog",
            "D": "FluentValidation"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Docker Compose'?",
        "options": {
            "A": "A tool to write music for Docker",
            "B": "A tool for defining and running multi-container Docker applications",
            "C": "A type of database",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Kubernetes' (K8s)?",
        "options": {
            "A": "A programming language",
            "B": "An open-source system for automating deployment, scaling, and management of containerized applications",
            "C": "A cloud provider",
            "D": "A database engine"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Helm' in a Kubernetes/ASP.NET environment?",
        "options": {
            "A": "A steering wheel for the server",
            "B": "A package manager for Kubernetes used to define, install, and upgrade complex K8s applications",
            "C": "A type of unit test",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Service Mesh' (e.g., Istio or Linkerd)?",
        "options": {
            "A": "A messy server room",
            "B": "A dedicated infrastructure layer for facilitating service-to-service communication, adding security, and observability",
            "C": "A group of controllers",
            "D": "A type of sharding"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Secret Management' in microservices?",
        "options": {
            "A": "Hiding the developer's salary",
            "B": "The process of securely storing and accessing sensitive data like API keys and database credentials",
            "C": "A private database",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Event Sourcing'?",
        "options": {
            "A": "Sourcing events for a party",
            "B": "A pattern where state changes are logged as a sequence of events rather than just the current state",
            "C": "A type of unit test",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'CQRS'?",
        "options": {
            "A": "A type of CSS error",
            "B": "Command Query Responsibility Segregation; separating read and write operations for better scaling",
            "C": "A security protocol",
            "D": "A database join"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Vertical Slice Architecture'?",
        "options": {
            "A": "Cutting the server in half",
            "B": "An architectural pattern where code is organized by features (slices) rather than technical layers",
            "C": "A type of sharding",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'MassTransit' or 'NServiceBus' used for?",
        "options": {
            "A": "Public transportation apps",
            "B": "Distributed application frameworks that simplify building message-based microservices (using RabbitMQ/Azure Service Bus)",
            "C": "To style the UI",
            "D": "To manage the cloud"
        },
        "answer": "B"
    },
    {
        "question": "What is 'RabbitMQ' or 'Azure Service Bus'?",
        "options": {
            "A": "A coding language",
            "B": "Message brokers used for asynchronous, decoupled communication between services",
            "C": "A type of database",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Outbox Pattern'?",
        "options": {
            "A": "Deleting an email outbox",
            "B": "A pattern used to ensure reliable messaging by saving messages to the database before sending them to a broker",
            "C": "A type of sharding",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Ambassador' pattern?",
        "options": {
            "A": "A person representing the app",
            "B": "A helper service that sends network requests on behalf of a consumer service or application",
            "C": "A type of unit test",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Dead Letter Queue' (DLQ)?",
        "options": {
            "A": "A queue for expired passwords",
            "B": "A service that stores messages that could not be successfully processed for later analysis",
            "C": "A performance report",
            "D": "A type of sharding"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Saga' pattern?",
        "options": {
            "A": "A very long story",
            "B": "A pattern for managing distributed transactions and data consistency across microservices",
            "C": "A security protocol",
            "D": "A database join"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Log Aggregation' (e.g., ELK Stack)?",
        "options": {
            "A": "Deleting all logs",
            "B": "The process of collecting logs from all microservices into a central, searchable location",
            "C": "A performance report",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Prometheus' and 'Grafana'?",
        "options": {
            "A": "Greek gods",
            "B": "Tools for monitoring and visualizing system metrics and performance",
            "C": "Database engines",
            "D": "Coding languages"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Application Initialization' middleware?",
        "options": {
            "A": "Middleware that starts the server",
            "B": "Middleware used to perform tasks when the app starts up, such as warming up caches",
            "C": "A type of sharding",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Memory Dump' analysis?",
        "options": {
            "A": "Taking a break from coding",
            "B": "Inspecting a snapshot of memory to diagnose memory leaks or application crashes",
            "C": "A database backup",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'BenchmarkDotNet' used for?",
        "options": {
            "A": "To write unit tests",
            "B": "A popular .NET library for benchmarking code to measure performance accurately",
            "C": "To style the UI",
            "D": "To manage the database"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Cold Start' in a serverless ASP.NET environment (e.g., Azure Functions)?",
        "options": {
            "A": "Starting the app in winter",
            "B": "The latency experienced when a function is triggered after being idle and its container needs to be initialized",
            "C": "A security scan",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'KEDA' (Kubernetes Event-driven Autoscaling)?",
        "options": {
            "A": "A type of sharding",
            "B": "A Kubernetes-based event-driven autoscaler used to scale containers based on external events",
            "C": "A security certificate",
            "D": "A database engine"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Dapr' (Distributed Application Runtime)?",
        "options": {
            "A": "A type of diaper",
            "B": "A portable, event-driven runtime that makes it easy to build resilient, microservices for cloud and edge",
            "C": "A performance report",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'SignalR Message Pack' hub protocol?",
        "options": {
            "A": "Packing messages into boxes",
            "B": "A binary protocol for SignalR that reduces message size and increases performance over JSON",
            "C": "A security scan",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Middleware Short-circuiting'?",
        "options": {
            "A": "A broken server",
            "B": "When a middleware component handles a request and returns a response without calling the next middleware",
            "C": "A type of sharding",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Output Caching' vs 'Response Caching'?",
        "options": {
            "A": "They are the same",
            "B": "Output Caching (v7+) is server-side and configurable; Response Caching is based on client-side HTTP headers",
            "C": "Response Caching is faster",
            "D": "Output Caching is only for images"
        },
        "answer": "B"
    },
    {
        "question": "What is 'W3C Trace Context'?",
        "options": {
            "A": "A type of sharding",
            "B": "A standard for propagating distributed tracing context information across service boundaries",
            "C": "A performance report",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "Which header is used to propagate a trace ID in the W3C standard?",
        "options": {
            "A": "Trace-Id",
            "B": "traceparent",
            "C": "Parent-Id",
            "D": "X-Trace"
        },
        "answer": "B"
    },
    {
        "question": "What is 'AOT' (Ahead-of-Time) compilation in .NET?",
        "options": {
            "A": "Compiling code while you sleep",
            "B": "Compiling code into machine language at build time to reduce startup time and memory footprint",
            "C": "A legacy feature",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Trimming' in .NET deployment?",
        "options": {
            "A": "Cutting the developer's hair",
            "B": "A feature that removes unused code from an app to reduce its size for faster deployment",
            "C": "A security scan",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Final question: ASP.NET Core is built on top of which runtime?",
        "options": {
            "A": "Java Runtime Environment",
            "B": ".NET (formerly .NET Core)",
            "C": "Python Interpreter",
            "D": "Node.js"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Shadowing' in the context of API Gateways?",
        "options": {
            "A": "Hiding the API",
            "B": "Directing a copy of live traffic to a test service for testing without affecting production",
            "C": "A security scan",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Chaos Engineering' in microservices?",
        "options": {
            "A": "A messy office",
            "B": "The practice of intentionally injecting failures into a system to test its resilience",
            "C": "A security attack",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "When optimizing a high-traffic ASP.NET Core service for 'Zero-Allocation' performance, which technique is most effective for reducing Garbage Collector (GC) pressure when handling large request buffers?",
        "options": {
            "A": "Increasing the server's physical RAM",
            "B": "Using 'ArrayPool<T>' and 'Span<T>' to reuse memory blocks and avoid creating temporary objects on the managed heap",
            "C": "Switching from Kestrel to IIS",
            "D": "Calling 'GC.Collect()' manually after every HTTP request"
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
    skill = "ASP.NET"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
