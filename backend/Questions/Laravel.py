from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
    {
        "question": "What is Laravel?",
        "options": {
            "a": "A PHP framework",
            "b": "A JavaScript library",
            "c": "A Python package",
            "d": "A Ruby gem"
        },
        "answer": "a"
    },
    {
        "question": "Which command is used to create a new Laravel project?",
        "options": {
            "a": "laravel new project-name",
            "b": "npm install laravel",
            "c": "composer create-project --prefer-dist laravel/laravel project-name",
            "d": "laravel create project-name"
        },
        "answer": "c"
    },
    {
        "question": "What is Eloquent in Laravel?",
        "options": {
            "a": "A templating engine",
            "b": "An ORM (Object-Relational Mapping) system",
            "c": "A routing system",
            "d": "A testing framework"
        },
        "answer": "b"
    },
    {
    "question": "Which PHP design pattern is Laravel primarily based on?",
    "options": {
      "A": "Singleton",
      "B": "MVC (Model-View-Controller)",
      "C": "Factory",
      "D": "Observer"
    },
    "answer": "B"
  },
  {
    "question": "Which tool is used as the dependency manager for Laravel?",
    "options": {
      "A": "NPM",
      "B": "Composer",
      "C": "Artisan",
      "D": "Bower"
    },
    "answer": "B"
  },
  {
    "question": "What is the name of the command-line interface included with Laravel?",
    "options": {
      "A": "Lara-CLI",
      "B": "Artisan",
      "C": "Forge",
      "D": "Vapor"
    },
    "answer": "B"
  },
  {
    "question": "In which directory are the web routes defined in a standard Laravel 10/11 installation?",
    "options": {
      "A": "app/Http/Routes",
      "B": "routes/web.php",
      "C": "config/routes.php",
      "D": "resources/routes.php"
    },
    "answer": "B"
  },
  {
    "question": "Which Artisan command is used to create a new controller?",
    "options": {
      "A": "php artisan make:controller ControllerName",
      "B": "php artisan create:controller ControllerName",
      "C": "php artisan controller:make ControllerName",
      "D": "php artisan controller ControllerName"
    },
    "answer": "A"
  },
  {
    "question": "What is the purpose of the '.env' file in Laravel?",
    "options": {
      "A": "To store CSS styles",
      "B": "To store environment-specific configuration and sensitive credentials",
      "C": "To define database schemas",
      "D": "To list all installed packages"
    },
    "answer": "B"
  },
  {
    "question": "Which templating engine does Laravel use?",
    "options": {
      "A": "Twig",
      "B": "Blade",
      "C": "Smarty",
      "D": "Mustache"
    },
    "answer": "B"
  },
  {
    "question": "How do you define a route that accepts a parameter in Laravel?",
    "options": {
      "A": "Route::get('/user/{id}', ...)",
      "B": "Route::get('/user/:id', ...)",
      "C": "Route::get('/user/$id', ...)",
      "D": "Route::get('/user/[id]', ...)"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Middleware' in Laravel?",
    "options": {
      "A": "A bridge between the database and the controller",
      "B": "A mechanism for filtering HTTP requests entering your application",
      "C": "A tool to compile Javascript",
      "D": "The core logic of a Model"
    },
    "answer": "B"
  },
  {
    "question": "Which Artisan command is used to start the local development server?",
    "options": {
      "A": "php artisan start",
      "B": "php artisan serve",
      "C": "php artisan run",
      "D": "php artisan server"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Service Container' in Laravel?",
    "options": {
      "A": "A folder for saving files",
      "B": "A powerful tool for managing class dependencies and performing dependency injection",
      "C": "A database table for services",
      "D": "The server where Laravel is hosted"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used in a Controller to return a view?",
    "options": {
      "A": "Response::view()",
      "B": "view()",
      "C": "render()",
      "D": "get_view()"
    },
    "answer": "B"
  },
  {
    "question": "How can you protect a route so that only authenticated users can access it?",
    "options": {
      "A": "By using the 'guard' middleware",
      "B": "By using the 'auth' middleware",
      "C": "By adding 'secret' to the route",
      "D": "By setting the route to private"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'public' folder used for in Laravel?",
    "options": {
      "A": "Storing private PHP logic",
      "B": "Serving as the entry point for the application and storing public assets like images, CSS, and JS",
      "C": "Storing database migrations",
      "D": "Storing user uploaded private documents"
    },
    "answer": "B"
  },
  {
    "question": "Which Artisan command lists all the routes defined in your application?",
    "options": {
      "A": "php artisan route:all",
      "B": "php artisan route:list",
      "C": "php artisan show:routes",
      "D": "php artisan get:routes"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Eloquent' in Laravel?",
    "options": {
      "A": "A JavaScript library",
      "B": "Laravel's built-in Object-Relational Mapper (ORM)",
      "C": "A command-line tool for CSS",
      "D": "A server-side caching engine"
    },
    "answer": "B"
  },
  {
    "question": "Which Artisan command is used to create a new database migration?",
    "options": {
      "A": "php artisan migration:create",
      "B": "php artisan make:migration",
      "C": "php artisan db:migrate",
      "D": "php artisan new:migration"
    },
    "answer": "B"
  },
  {
    "question": "In an Eloquent model, what does the 'protected $fillable' property do?",
    "options": {
      "A": "Defines the table name",
      "B": "Specifies which attributes are mass assignable",
      "C": "Hides columns from JSON output",
      "D": "Sets default values for columns"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used to define a 'One-to-Many' relationship in an Eloquent model?",
    "options": {
      "A": "belongsTo()",
      "B": "hasMany()",
      "C": "hasOne()",
      "D": "belongsToMany()"
    },
    "answer": "B"
  },
  {
    "question": "How do you run all outstanding migrations in Laravel?",
    "options": {
      "A": "php artisan migrate:run",
      "B": "php artisan migrate",
      "C": "php artisan db:migrate",
      "D": "php artisan start:migration"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Seeders' in Laravel?",
    "options": {
      "A": "To create database backups",
      "B": "To populate the database with dummy or initial data",
      "C": "To optimize database queries",
      "D": "To delete old records"
    },
    "answer": "B"
  },
  {
    "question": "Which Artisan command is used to create a model and a migration file simultaneously?",
    "options": {
      "A": "php artisan make:model ModelName --migration",
      "B": "php artisan make:model ModelName -m",
      "C": "php artisan model:create ModelName -db",
      "D": "Both A and B"
    },
    "answer": "D"
  },
  {
    "question": "Which Eloquent method is used to retrieve a record by its primary key and throw an error if not found?",
    "options": {
      "A": "find()",
      "B": "findOrFail()",
      "C": "get()",
      "D": "first()"
    },
    "answer": "B"
  },
  {
    "question": "What is the default naming convention for a table associated with a model named 'Flight'?",
    "options": {
      "A": "Flight_table",
      "B": "flights",
      "C": "flight_data",
      "D": "tbl_flight"
    },
    "answer": "B"
  },
  {
    "question": "Which relationship type requires a 'pivot table'?",
    "options": {
      "A": "One-to-One",
      "B": "One-to-Many",
      "C": "Many-to-Many",
      "D": "Has-Many-Through"
    },
    "answer": "C"
  },
  {
    "question": "How do you revert the last migration operation?",
    "options": {
      "A": "php artisan migrate:undo",
      "B": "php artisan migrate:rollback",
      "C": "php artisan migrate:back",
      "D": "php artisan db:rollback"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Eager Loading' used for in Laravel?",
    "options": {
      "A": "To speed up the page load by downloading images",
      "B": "To solve the 'N+1' query problem by loading related models upfront",
      "C": "To load the database into the server cache",
      "D": "To load the application faster on mobile"
    },
    "answer": "B"
  },
  {
    "question": "Which Eloquent method allows you to soft delete a record?",
    "options": {
      "A": "The model must use the 'SoftDeletes' trait",
      "B": "The model must use 'delete()'",
      "C": "The table must have a 'deleted_at' column",
      "D": "Both A and C"
    },
    "answer": "D"
  },
  {
    "question": "Which query builder method is used to filter results using a SQL 'WHERE' clause?",
    "options": {
      "A": "filter()",
      "B": "where()",
      "C": "find()",
      "D": "search()"
    },
    "answer": "B"
  },
  {
    "question": "What does 'DB::table('users')->count()' return?",
    "options": {
      "A": "All users as a collection",
      "B": "The total number of records in the 'users' table",
      "C": "The first user in the table",
      "D": "An array of user IDs"
    },
    "answer": "B"
  },
  {
    "question": "Which file extension is used for Laravel Blade templates?",
    "options": {
      "A": ".blade.php",
      "B": ".laravel.php",
      "C": ".view.php",
      "D": ".template.php"
    },
    "answer": "A"
  },
  {
    "question": "Which Blade directive is used to display the content of a section?",
    "options": {
      "A": "@show",
      "B": "@yield",
      "C": "@display",
      "D": "@section"
    },
    "answer": "B"
  },
  {
    "question": "How do you echo data in a Blade template while escaping HTML entities?",
    "options": {
      "A": "{ data }",
      "B": "{{ $data }}",
      "C": "{!! $data !!}",
      "D": "<% $data %>"
    },
    "answer": "B"
  },
  {
    "question": "Which Blade directive is the equivalent of a PHP 'foreach' loop?",
    "options": {
      "A": "@loop",
      "B": "@foreach",
      "C": "@for-each",
      "D": "@iterate"
    },
    "answer": "B"
  },
  {
    "question": "Which directive would you use to include a partial view inside another Blade view?",
    "options": {
      "A": "@partial",
      "B": "@include",
      "C": "@insert",
      "D": "@extend"
    },
    "answer": "B"
  },
  {
    "question": "In Laravel, where should you typically define validation rules for incoming requests?",
    "options": {
      "A": "In the Blade view",
      "B": "In the Controller or a Form Request class",
      "C": "In the .env file",
      "D": "In the database schema"
    },
    "answer": "B"
  },
  {
    "question": "Which validation rule ensures that a field is not empty?",
    "options": {
      "A": "present",
      "B": "required",
      "C": "filled",
      "D": "not_null"
    },
    "answer": "B"
  },
  {
    "question": "Which method on the Request object is used to retrieve all input data as an array?",
    "options": {
      "A": "get()",
      "B": "all()",
      "C": "input()",
      "D": "data()"
    },
    "answer": "B"
  },
  {
    "question": "Which Blade directive is used to prevent Cross-Site Request Forgery (CSRF) in forms?",
    "options": {
      "A": "@security",
      "B": "@csrf",
      "C": "@token",
      "D": "@protection"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'old()' helper function in a Laravel form?",
    "options": {
      "A": "To retrieve the previous user's data",
      "B": "To repopulate form fields with input from the previous request after a validation failure",
      "C": "To show data from a year ago",
      "D": "To clear the form"
    },
    "answer": "B"
  },
  {
    "question": "Which class provides the 'Auth' facade used for user authentication?",
    "options": {
      "A": "Illuminate\\Support\\Facades\\Auth",
      "B": "App\\Models\\User",
      "C": "Illuminate\\Auth\\Guard",
      "D": "System\\Security\\Auth"
    },
    "answer": "A"
  },
  {
    "question": "How do you check if the current user is logged in using the Auth facade?",
    "options": {
      "A": "Auth::isLoggedIn()",
      "B": "Auth::check()",
      "C": "Auth::userExists()",
      "D": "Auth::logged()"
    },
    "answer": "B"
  },
  {
    "question": "Which method retrieves the currently authenticated user instance?",
    "options": {
      "A": "Auth::current()",
      "B": "Auth::user()",
      "C": "Auth::get()",
      "D": "Auth::profile()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Laravel Breeze'?",
    "options": {
      "A": "A database optimization tool",
      "B": "A minimal, simple implementation of all of Laravel's authentication features",
      "C": "A cloud hosting service",
      "D": "A style for the Blade editor"
    },
    "answer": "B"
  },
  {
    "question": "Which Blade directive is used to only show content if the user is authenticated?",
    "options": {
      "A": "@user",
      "B": "@auth",
      "C": "@logged",
      "D": "@secure"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Laravel Sanctum' primarily used for?",
    "options": {
      "A": "Encrypting database passwords",
      "B": "A featherweight authentication system for SPAs and simple APIs using API tokens",
      "C": "Managing server-side caching",
      "D": "Compressing images on upload"
    },
    "answer": "B"
  },
  {
    "question": "Which class is used in Laravel to transform models and collections into JSON responses for an API?",
    "options": {
      "A": "JsonEncoder",
      "B": "API Resource",
      "C": "DataMapper",
      "D": "ModelConverter"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Laravel Queues'?",
    "options": {
      "A": "To sort database records",
      "B": "To defer the processing of a time-consuming task, such as sending an email, until a later time",
      "C": "To manage user login attempts",
      "D": "To list all active routes"
    },
    "answer": "B"
  },
  {
    "question": "Which Artisan command is used to start the process that listens for and executes queued jobs?",
    "options": {
      "A": "php artisan queue:start",
      "B": "php artisan queue:work",
      "C": "php artisan job:run",
      "D": "php artisan listen:queue"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Task Scheduling' in Laravel?",
    "options": {
      "A": "A calendar for developers",
      "B": "A way to fluently define your command schedule within Laravel itself, requiring only a single Cron entry on your server",
      "C": "A tool to track project deadlines",
      "D": "The order in which controllers are executed"
    },
    "answer": "B"
  },
  {
    "question": "Which helper function is used to dispatch an event in Laravel?",
    "options": {
      "A": "trigger()",
      "B": "event()",
      "C": "fire()",
      "D": "broadcast()"
    },
    "answer": "B"
  },
  {
    "question": "What is the role of a 'Listener' in Laravel's Event system?",
    "options": {
      "A": "To record user audio",
      "B": "To handle the logic that should run when a specific event is dispatched",
      "C": "To wait for a database connection",
      "D": "To monitor server traffic"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Laravel Horizon'?",
    "options": {
      "A": "A new frontend framework",
      "B": "A dashboard and code-driven configuration system for Laravel-powered Redis queues",
      "C": "A cloud backup service",
      "D": "A tool for horizontal scaling of databases"
    },
    "answer": "B"
  },
  {
    "question": "In Laravel APIs, which HTTP status code is typically returned for a successful 'POST' request that creates a resource?",
    "options": {
      "A": "200 OK",
      "B": "201 Created",
      "C": "204 No Content",
      "D": "400 Bad Request"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Rate Limiting' in Laravel?",
    "options": {
      "A": "Restricting the size of file uploads",
      "B": "Limiting the number of requests a user can make to a specific route or API within a timeframe",
      "C": "A way to measure database speed",
      "D": "Limiting the number of users in the database"
    },
    "answer": "B"
  },
  {
    "question": "Which trait must be added to a Job class to allow it to be processed in the background?",
    "options": {
      "A": "Dispatchable",
      "B": "InteractsWithQueue",
      "C": "Queueable",
      "D": "All of the above"
    },
    "answer": "D"
  },
  {
    "question": "What is the purpose of 'Laravel Valet'?",
    "options": {
      "A": "A deployment tool for AWS",
      "B": "A minimalist development environment for macOS users",
      "C": "A package for managing API keys",
      "D": "A database GUI"
    },
    "answer": "B"
  },
  {
    "question": "Which Artisan command is used to create a custom CLI command?",
    "options": {
      "A": "php artisan create:command",
      "B": "php artisan make:command",
      "C": "php artisan cli:make",
      "D": "php artisan artisan:make"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Service Provider' in Laravel?",
    "options": {
      "A": "A company that hosts your website",
      "B": "The central place to configure and bootstrap all Laravel applications",
      "C": "A class that handles API requests",
      "D": "A database configuration file"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Polymorphic Relationships' in Eloquent?",
    "options": {
      "A": "A relationship that uses many databases",
      "B": "A relationship where a model can belong to more than one other type of model using a single association",
      "C": "A relationship between three models",
      "D": "A way to hide model data"
    },
    "answer": "B"
  },
  {
    "question": "In Laravel 11, where is the main application configuration now predominantly handled to reduce file clutter?",
    "options": {
      "A": "config/app.php",
      "B": "bootstrap/app.php",
      "C": "app/Providers/AppServiceProvider.php",
      "D": "routes/api.php"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Eloquent Scopes' used for?",
    "options": {
      "A": "To limit the number of users",
      "B": "To define common sets of query constraints that you may easily re-use throughout your application",
      "C": "To view the database in a GUI",
      "D": "To set the timezone of the model"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Repository Pattern' often used for in Laravel?",
    "options": {
      "A": "To create database backups",
      "B": "To create a layer of abstraction between the Eloquent ORM and the Controller for better testability",
      "C": "To store images in the cloud",
      "D": "To manage git repositories"
    },
    "answer": "B"
  },
  {
    "question": "Which Artisan command is used to generate a 'Policy' for authorizing actions against a model?",
    "options": {
      "A": "php artisan make:auth",
      "B": "php artisan make:policy",
      "C": "php artisan make:gate",
      "D": "php artisan create:policy"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Pruning' feature in Laravel Eloquent models?",
    "options": {
      "A": "Compressing the database",
      "B": "Automatically removing obsolete records from the database that are no longer needed",
      "C": "Deleting unused controllers",
      "D": "Optimizing CSS files"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Laravel Reverb' (introduced in Laravel 11)?",
    "options": {
      "A": "A testing framework",
      "B": "A first-party, high-performance WebSocket server for real-time communication",
      "C": "A tool to record server logs",
      "D": "A database migration tool"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used in a Migration to add a 'Foreign Key' constraint to a table?",
    "options": {
      "A": "foreignKey()",
      "B": "constrained()",
      "C": "link()",
      "D": "belongsTo()"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'N+1 Query Problem'?",
    "options": {
      "A": "When the database has one too many columns",
      "B": "A performance issue where the application executes 1 query to get a list and N additional queries to get data for each item",
      "C": "An error when a migration fails",
      "D": "When a route is defined twice"
    },
    "answer": "B"
  },
  {
    "question": "Which helper function would you use to generate a temporary signed URL for a private file?",
    "options": {
      "A": "URL::signed()",
      "B": "URL::temporarySignedRoute()",
      "C": "Storage::url()",
      "D": "Route::sign()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Model Observers' in Laravel?",
    "options": {
      "A": "A tool for debugging models",
      "B": "Classes used to group event listeners for a specific Eloquent model (created, updated, deleted)",
      "C": "A way to view models in the browser",
      "D": "A security layer for database tables"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Laravel Pulse' primarily used for?",
    "options": {
      "A": "Building mobile apps",
      "B": "Monitoring the health and performance of your Laravel application (usage, slow routes, jobs)",
      "C": "Generating dummy data",
      "D": "Managing user passwords"
    },
    "answer": "B"
  },
  {
    "question": "How do you specify a custom table name in an Eloquent model?",
    "options": {
      "A": "protected $name = 'my_table';",
      "B": "protected $table = 'my_table';",
      "C": "public $database = 'my_table';",
      "D": "method table()"
    },
    "answer": "B"
  },
  {
    "question": "Which Artisan command is used to optimize the application by caching configuration and routes?",
    "options": {
      "A": "php artisan optimize",
      "B": "php artisan cache:all",
      "C": "php artisan speed:up",
      "D": "php artisan config:save"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Mass Assignment' vulnerability?",
    "options": {
      "A": "When a database becomes too large",
      "B": "When a user sends unexpected HTTP parameters that change columns they shouldn't (like 'is_admin')",
      "C": "When multiple users register at once",
      "D": "A bug in the login form"
    },
    "answer": "B"
  },
  {
    "question": "In Laravel architecture, what is a 'Contract'?",
    "options": {
      "A": "A legal document for developers",
      "B": "A set of interfaces that define the core services provided by the framework",
      "C": "A relationship between two models",
      "D": "A way to lock the code"
    },
    "answer": "B"
  },
 {
    "question": "What is the purpose of 'Eloquent API Resources'?",
    "options": {
      "A": "To create database tables via API",
      "B": "To act as a transformation layer between Eloquent models and the JSON responses sent to clients",
      "C": "To store API keys in the database",
      "D": "To speed up the connection to MySQL"
    },
    "answer": "B"
  },
  {
    "question": "Which Laravel testing tool, often used as an alternative to PHPUnit, provides a more 'human-readable' syntax?",
    "options": {
      "A": "Mocha",
      "B": "Pest",
      "C": "Cypress",
      "D": "Dusk"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'lazy()' method on an Eloquent query do?",
    "options": {
      "A": "It delays the query until the next day",
      "B": "It retrieves records in chunks using a cursor to keep memory usage low while iterating",
      "C": "It prevents the model from saving data",
      "D": "It automatically formats strings to lowercase"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Database Transactions' used for in Laravel?",
    "options": {
      "A": "To track how much money a user spends",
      "B": "To ensure a set of database operations either all succeed or all fail together (atomicity)",
      "C": "To translate database names",
      "D": "To send data to an external API"
    },
    "answer": "B"
  },
  {
    "question": "Which Artisan command is used to clear the application's cache, including config and routes, in one go?",
    "options": {
      "A": "php artisan clear:all",
      "B": "php artisan optimize:clear",
      "C": "php artisan cache:forget",
      "D": "php artisan refresh:app"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Virtual Column' in a Laravel Migration?",
    "options": {
      "A": "A column that only exists in the UI",
      "B": "A column whose value is automatically generated by the database based on other columns (Generated Column)",
      "C": "A hidden column",
      "D": "A column stored in a different database"
    },
    "answer": "B"
  },
  {
    "question": "How do you define a 'Custom Collection' for an Eloquent model?",
    "options": {
      "A": "By overriding the newCollection() method in the model",
      "B": "By creating a new folder in /app",
      "C": "By changing the .env file",
      "D": "By using the collect() helper in the controller"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Laravel Echo'?",
    "options": {
      "A": "A logging tool for audio files",
      "B": "A JavaScript library that makes it easy to subscribe to channels and listen for events broadcast by Laravel",
      "C": "A database replication tool",
      "D": "The command line interface for Laravel Forge"
    },
    "answer": "B"
  },
  {
    "question": "Which Eloquent relationship allows you to get a single related model through a 'parent' model?",
    "options": {
      "A": "hasMany",
      "B": "hasOneThrough",
      "C": "belongsToMany",
      "D": "morphMany"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Single Action Controller' in Laravel?",
    "options": {
      "A": "A controller that only handles GET requests",
      "B": "A controller that contains only the __invoke() method",
      "C": "A controller with no methods",
      "D": "A controller that deletes itself after use"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Laravel Socialite' primarily used for?",
    "options": {
      "A": "Building a social network",
      "B": "Handling OAuth authentication with providers like Google, Facebook, and GitHub",
      "C": "Sharing reports on Twitter",
      "D": "Managing user friends lists"
    },
    "answer": "B"
  },
  {
    "question": "In a Laravel Migration, what does 'unsignedBigInteger' typically represent when used for a foreign key?",
    "options": {
      "A": "A very small number",
      "B": "A 64-bit integer that cannot be negative, matching the standard ID type",
      "C": "A text string used as an ID",
      "D": "A random number generator"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Laravel Sail'?",
    "options": {
      "A": "A tool to deploy to the ocean",
      "B": "A light-weight command-line interface for interacting with Laravel's default Docker development environment",
      "C": "A frontend styling kit",
      "D": "A testing framework for APIs"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used in a Controller to prevent a user from performing an action using a Policy?",
    "options": {
      "A": "check()",
      "B": "authorize()",
      "C": "allow()",
      "D": "gate()"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Boot' method used for in a Service Provider?",
    "options": {
      "A": "To restart the server",
      "B": "To register bindings or perform actions after all other service providers have been registered",
      "C": "To load the .env file",
      "D": "To start a database migration"
    },
    "answer": "B"
  },
   {
    "question": "In Laravel 11, which file has been significantly reduced, with most internal configuration now handled by the framework core?",
    "options": {
      "A": "app/Http/Kernel.php",
      "B": "bootstrap/app.php",
      "C": "public/index.php",
      "D": "composer.json"
    },
    "answer": "A"
  },
  {
    "question": "What is the purpose of the 'EnsureTokenIsValid' middleware in a Sanctum-protected API?",
    "options": {
      "A": "To check if the user is an admin",
      "B": "To verify that the incoming request has a valid Personal Access Token",
      "C": "To encrypt the request body",
      "D": "To check the user's browser version"
    },
    "answer": "B"
  },
  {
    "question": "Which method in a Job class is used to specify the maximum number of times a job should be attempted before failing?",
    "options": {
      "A": "public $tries",
      "B": "public $attempts",
      "C": "public $retries",
      "D": "public $limit"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Laravel Octane' used for?",
    "options": {
      "A": "A testing suite for slow routes",
      "B": "A high-performance application server using Swoole or RoadRunner to keep the app in memory",
      "C": "A tool to compress database backups",
      "D": "An authentication starter kit"
    },
    "answer": "B"
  },
  {
    "question": "Which Eloquent relationship is used to define a 'Many-to-Many' relationship through a 'pivot' model that also contains custom data?",
    "options": {
      "A": "belongsToMany()->withPivot()",
      "B": "hasMany()",
      "C": "morphToMany()",
      "D": "hasOne()"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Route Model Binding'?",
    "options": {
      "A": "Connecting two routes together",
      "B": "Automatically injecting a model instance directly into your route closure or controller based on the ID in the URL",
      "C": "Renaming models to match routes",
      "D": "A way to hide model data from the frontend"
    },
    "answer": "B"
  },
  {
    "question": "How do you define a 'Global Scope' in Laravel to always filter results (e.g., only active users)?",
    "options": {
      "A": "By adding a where clause to every query",
      "B": "By implementing the Scope interface and applying it in the model's booted method",
      "C": "By changing the .env file",
      "D": "By editing the controller"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Laravel Folio'?",
    "options": {
      "A": "A database for images",
      "B": "A file-based router that allows you to define routes by simply creating Blade files in a specific directory",
      "C": "A tool for generating PDFs",
      "D": "A system for managing user portfolios"
    },
    "answer": "B"
  },
  {
    "question": "Which Artisan command is used to see a breakdown of which files are taking up the most space in your 'storage' directory?",
    "options": {
      "A": "php artisan storage:list",
      "B": "php artisan top",
      "C": "php artisan about",
      "D": "Laravel does not have a native command for this; it requires external tools"
    },
    "answer": "D"
  },
  {
    "question": "In Laravel 11, where do you now register your scheduled tasks?",
    "options": {
      "A": "app/Console/Kernel.php",
      "B": "routes/console.php",
      "C": "bootstrap/app.php (using withSchedule)",
      "D": "config/schedule.php"
    },
    "answer": "C"
  },
  {
    "question": "What is 'Laravel Precognition'?",
    "options": {
      "A": "An AI tool to predict user behavior",
      "B": "A feature that allows you to validate a form on the frontend using your backend validation rules before the form is submitted",
      "C": "A way to see future database entries",
      "D": "A debugging tool for slow queries"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Database Sharding' support in Laravel?",
    "options": {
      "A": "Splitting a large database into smaller, faster pieces across multiple servers",
      "B": "Creating a backup of a single table",
      "C": "Merging two databases into one",
      "D": "Changing the database engine"
    },
    "answer": "A"
  },
  {
    "question": "Which helper function is used to throw a 403 'Forbidden' response if a condition is not met?",
    "options": {
      "A": "stop()",
      "B": "abort(403)",
      "C": "fail()",
      "D": "block()"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Laravel Pennant'?",
    "options": {
      "A": "A tool for managing team flags",
      "B": "A lightweight feature flag library to manage A/B testing or gradual feature rollouts",
      "C": "A package for generating site maps",
      "D": "A system for tracking user badges"
    },
    "answer": "B"
  },
  {
    "question": "In a Migration, what does 'nullableTimeline' do?",
    "options": {
      "A": "It creates two columns: created_at and updated_at that can be null",
      "B": "There is no such method; the correct method is 'timestamps()'",
      "C": "It creates a column for a video timeline",
      "D": "It adds a date column that allows nulls"
    },
    "answer": "B"
  },
  {
    "question": "In Laravel 11, how are API routes enabled, given they are no longer present in the default skeleton?",
    "options": {
      "A": "By manually creating routes/api.php",
      "B": "By running 'php artisan install:api'",
      "C": "By editing the .env file",
      "D": "By enabling them in config/app.php"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Double Secret' encryption used for in Laravel's 'encrypted' cast?",
    "options": {
      "A": "It encrypts the data twice with different keys",
      "B": "It is not a real term; Laravel uses standard AES-256 and AES-128 encryption via OpenSSL",
      "C": "It stores the password in the database twice",
      "D": "It requires two passwords to open the file"
    },
    "answer": "B"
  },
  {
    "question": "Which Laravel package is the official tool for managing serverless deployments on AWS Lambda?",
    "options": {
      "A": "Laravel Forge",
      "B": "Laravel Vapor",
      "C": "Laravel Envoy",
      "D": "Laravel Valet"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Atomic Locks' in Laravel's Cache system?",
    "options": {
      "A": "A way to prevent users from deleting data",
      "B": "A mechanism to ensure a specific task is only being executed by one process at a time",
      "C": "A physical lock on the server",
      "D": "A database encryption feature"
    },
    "answer": "B"
  },
  {
    "question": "In a Laravel Migration, what does 'through()' do in a relationship definition?",
    "options": {
      "A": "It defines a 'Has-Many-Through' or 'Has-One-Through' relationship",
      "B": "It skips the current table",
      "C": "It creates a temporary bridge table",
      "D": "It deletes the relationship"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Laravel Pulse's' primary advantage over standard logging?",
    "options": {
      "A": "It records audio logs",
      "B": "It provides a real-time, visual dashboard of high-traffic routes, slow jobs, and server resource usage",
      "C": "It is cheaper to host",
      "D": "It automatically fixes code errors"
    },
    "answer": "B"
  },
  {
    "question": "Which Artisan command allows you to view the 'Execution Plan' of your scheduled tasks?",
    "options": {
      "A": "php artisan schedule:list",
      "B": "php artisan schedule:show",
      "C": "php artisan list:cron",
      "D": "php artisan schedule:test"
    },
    "answer": "A"
  },
  {
    "question": "What is 'PHP Fibers', and how does Laravel use them in Octane?",
    "options": {
      "A": "A new type of database connection",
      "B": "A way to handle asynchronous code execution within a single thread to improve concurrency",
      "C": "A tool to compress images",
      "D": "A framework for building mobile apps"
    },
    "answer": "B"
  },
  {
    "question": "Which Eloquent method is used to conditionally add 'where' clauses based on a boolean value?",
    "options": {
      "A": "if()",
      "B": "when()",
      "C": "case()",
      "D": "maybe()"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Laravel Telescope'?",
    "options": {
      "A": "To view distant servers",
      "B": "An elegant debug assistant that provides insight into requests, exceptions, log entries, and database queries",
      "C": "A CSS framework",
      "D": "A tool to generate documentation"
    },
    "answer": "B"
  },
  {
    "question": "In Laravel 11, where do you define custom Artisan commands?",
    "options": {
      "A": "app/Console/Kernel.php",
      "B": "routes/console.php",
      "C": "config/commands.php",
      "D": "bootstrap/app.php"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Database Notification' in Laravel?",
    "options": {
      "A": "An email sent by the database",
      "B": "A system that allows you to store and display notifications to users within your application database",
      "C": "A log of database errors",
      "D": "A popup that appears in MySQL Workbench"
    },
    "answer": "B"
  },
  {
    "question": "Which facade is used to programmatically interact with the filesystem (local or cloud)?",
    "options": {
      "A": "File",
      "B": "Storage",
      "C": "Cloud",
      "D": "Disk"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Laravel Pail' (introduced in 2024)?",
    "options": {
      "A": "A tool to delete old files",
      "B": "A CLI tool to easily tail your Laravel log files directly in the terminal with filtering",
      "C": "A new database engine",
      "D": "A package for managing user subscriptions"
    },
    "answer": "B"
  },
  {
    "question": "Which Artisan command is used to remove all expired tokens from the 'personal_access_tokens' table in Sanctum?",
    "options": {
      "A": "php artisan sanctum:clear",
      "B": "php artisan sanctum:prune-expired",
      "C": "php artisan tokens:delete",
      "D": "php artisan auth:clear-tokens"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Lazy Eager Loading' in Laravel?",
    "options": {
      "A": "Loading a relationship only if a user clicks a button",
      "B": "Eager loading a relationship on a model instance that has already been retrieved",
      "C": "Loading data from a cache instead of the database",
      "D": "A way to load CSS files asynchronously"
    },
    "answer": "B"
  },
  {
    "question": "In Laravel 11, how do you add custom middleware to the application's global stack?",
    "options": {
      "A": "Edit the 'app/Http/Kernel.php' file",
      "B": "Use the 'withMiddleware' method in 'bootstrap/app.php'",
      "C": "Register it in the 'AppServiceProvider'",
      "D": "Manually add it to the 'routes/web.php' file"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'upsert' method in Eloquent?",
    "options": {
      "A": "To sort records in ascending order",
      "B": "To insert multiple records or update them if they already exist, using a single query",
      "C": "To delete all records and re-insert them",
      "D": "To verify if a database connection is active"
    },
    "answer": "B"
  },
  {
    "question": "Which Laravel feature allows you to encrypt entire database columns while still allowing for basic searching (via blind indexing)?",
    "options": {
      "A": "Standard Bcrypt",
      "B": "Eloquent Encryption (Model Casting)",
      "C": "Laravel Fortify",
      "D": "Native MySQL Encryption"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Multi-tenancy' in a Laravel context?",
    "options": {
      "A": "One developer working on multiple projects",
      "B": "A single application instance serving multiple distinct customers (tenants) with data isolation",
      "C": "Connecting to multiple types of databases (MySQL and MongoDB)",
      "D": "A server that hosts multiple websites"
    },
    "answer": "B"
  },
  {
    "question": "Which Artisan command allows you to monitor your application's 'events' in real-time in the console?",
    "options": {
      "A": "php artisan event:listen",
      "B": "php artisan event:list",
      "C": "php artisan event:monitor",
      "D": "php artisan show:events"
    },
    "answer": "C"
  },
  {
    "question": "What does the 'preventLazyLoading' method do in the AppServiceProvider?",
    "options": {
      "A": "It speeds up the application automatically",
      "B": "It throws an exception if a relationship is lazy-loaded, helping developers catch N+1 query issues during development",
      "C": "It prevents the user from clicking buttons too fast",
      "D": "It disables the database connection"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Laravel Envoy' used for?",
    "options": {
      "A": "A testing library for APIs",
      "B": "A tool for executing common tasks (like deployments) on remote servers using Blade-style syntax",
      "C": "A bridge between PHP and Python",
      "D": "An authentication system for mobile apps"
    },
    "answer": "B"
  },
  {
    "question": "Which Eloquent method is used to retrieve only the 'ID' and 'Name' columns as a flat associative array?",
    "options": {
      "A": "get(['id', 'name'])",
      "B": "pluck('name', 'id')",
      "C": "select('id', 'name')->toArray()",
      "D": "only('id', 'name')"
    },
    "answer": "B"
  },
  {
    "question": "In Laravel security, what is 'Mass Assignment' protection enabled by default through?",
    "options": {
      "A": "The .env file",
      "B": "The $guarded or $fillable properties on a model",
      "C": "The auth middleware",
      "D": "The database schema"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Laravel Fortify'?",
    "options": {
      "A": "A firewall for Laravel applications",
      "B": "A frontend-agnostic authentication backend that handles registration, login, and two-factor auth",
      "C": "A tool to compress database tables",
      "D": "A system for managing server clusters"
    },
    "answer": "B"
  },
  {
    "question": "Which method on a collection is used to split a single collection into multiple smaller collections of a specific size?",
    "options": {
      "A": "split()",
      "B": "chunk()",
      "C": "divide()",
      "D": "part()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Signed URLs' useful for in Laravel?",
    "options": {
      "A": "URLs that require a digital signature from a pen",
      "B": "Creating public links that expire or have a 'tamper-proof' hash, often used for email verification or file downloads",
      "C": "Hiding the URL from the browser's address bar",
      "D": "Changing the domain name of the link"
    },
    "answer": "B"
  },
  {
    "question": "Which Artisan command is used to remove all 'stale' password reset tokens from the database?",
    "options": {
      "A": "php artisan auth:clear-resets",
      "B": "php artisan auth:prune-tokens",
      "C": "php artisan clear:resets",
      "D": "php artisan tokens:prune"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'Conditionable' trait used for in Laravel classes?",
    "options": {
      "A": "To check the weather",
      "B": "To allow the use of 'when()' and 'unless()' methods for fluent, conditional method chaining",
      "C": "To handle database errors",
      "D": "To validate user inputs"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Decorator Pattern' equivalent in Laravel's Middleware implementation?",
    "options": {
      "A": "Singleton",
      "B": "The Onion Architecture (wrapping the request in layers)",
      "C": "Factory",
      "D": "Facade"
    },
    "answer": "B"
  },
  {
    "question": "Which method in a Job class allows you to handle a job that has exceeded its maximum number of retry attempts?",
    "options": {
      "A": "public function fail()",
      "B": "public function failed(Throwable $exception)",
      "C": "public function handleFailure()",
      "D": "public function stop()"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Prunable' trait in Eloquent used for?",
    "options": {
      "A": "Compressing the database file",
      "B": "Defining a query to identify and automatically delete obsolete records during a scheduled command",
      "C": "Changing the primary key type",
      "D": "Hiding rows from the frontend"
    },
    "answer": "B"
  },
  {
    "question": "Which Laravel tool is used to mock a real-time event broadcasting server for testing purposes?",
    "options": {
      "A": "Event::fake()",
      "B": "Broadcast::fake()",
      "C": "Echo::mock()",
      "D": "Pusher::test()"
    },
    "answer": "B"
  },
  {
    "question": "In Laravel 11, where is the 'Exception' handling logic primarily configured for custom responses?",
    "options": {
      "A": "app/Exceptions/Handler.php",
      "B": "bootstrap/app.php (using withExceptions)",
      "C": "config/exceptions.php",
      "D": "AppServiceProvider"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Database Notification' vs 'Mail Notification'?",
    "options": {
      "A": "Database is only for errors; Mail is for users",
      "B": "Database stores notifications in a table; Mail sends an actual email using a driver",
      "C": "Database is faster",
      "D": "Mail is only for admin users"
    },
    "answer": "B"
  },
  {
    "question": "Which Eloquent method allows you to update a record if it exists, or create it if it doesn't, based on a set of attributes?",
    "options": {
      "A": "save()",
      "B": "updateOrCreate()",
      "C": "insertOrUpdate()",
      "D": "firstOrCreate()"
    },
    "answer": "B"
  },
  {
    "question": "What does 'WithoutOverlapping' do when applied to a scheduled task?",
    "options": {
      "A": "It prevents two different tasks from running at once",
      "B": "It ensures a specific task does not run if a previous instance of that same task is still executing",
      "C": "It prevents users from logging in twice",
      "D": "It stops the server from crashing"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'Macroable' trait in Laravel?",
    "options": {
      "A": "To record keyboard macros",
      "B": "To allow you to add custom methods to core framework classes at runtime",
      "C": "To create Excel macros",
      "D": "To speed up Artisan commands"
    },
    "answer": "B"
  },
  {
    "question": "Which testing method is used to verify that a specific view contains a certain string of text?",
    "options": {
      "A": "assertSee()",
      "B": "assertText()",
      "C": "assertContain()",
      "D": "assertViewHas()"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Polyfill' in the context of Laravel's support for older PHP versions?",
    "options": {
      "A": "A new database engine",
      "B": "A library that provides modern PHP functionality to older PHP versions using code-based workarounds",
      "C": "A way to compress PHP files",
      "D": "A frontend framework"
    },
    "answer": "B"
  },
  {
    "question": "Which Artisan command allows you to view the configuration of your application as it is currently loaded in memory?",
    "options": {
      "A": "php artisan config:show",
      "B": "php artisan about",
      "C": "php artisan config:list",
      "D": "php artisan env"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Virtual/Generated Columns' support in Laravel Migrations useful for?",
    "options": {
      "A": "Storing hidden passwords",
      "B": "Creating columns that are calculated by the database (e.g., full_name from first and last name) to save application logic",
      "C": "Adding more rows to a table",
      "D": "Hiding columns from the database admin"
    },
    "answer": "B"
  },
  {
    "question": "Which helper function is used to securely hash a string (like a password) using the default driver?",
    "options": {
      "A": "encrypt()",
      "B": "Hash::make()",
      "C": "md5()",
      "D": "password_verify()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Laravel Envoy'?",
    "options": {
      "A": "A real-time chat package",
      "B": "A tool for executing common tasks on remote servers using a clean, minimal syntax",
      "C": "A bridge for Python scripts",
      "D": "An authentication driver"
    },
    "answer": "B"
  },
  {
    "question": "Which Laravel Octane driver utilizes a 'Shared Memory' approach to share data between worker processes?",
    "options": {
      "A": "Swoole",
      "B": "RoadRunner",
      "C": "FrankenPHP",
      "D": "PHP-FPM"
    },
    "answer": "A"
  },
  {
    "question": "What is the primary purpose of 'Lazy Service Providers' in Laravel?",
    "options": {
      "A": "To write less code",
      "B": "To defer the registration of a service until it is actually needed, improving boot performance",
      "C": "To prevent the database from connecting",
      "D": "To slow down the application during testing"
    },
    "answer": "B"
  },
  {
    "question": "Which method in a custom Artisan command is used to prompt the user for secret information that shouldn't be echoed back to the console?",
    "options": {
      "A": "ask()",
      "B": "secret()",
      "C": "anticipate()",
      "D": "password()"
    },
    "answer": "B"
  },
  {
    "question": "In Laravel 11, how can you programmatically prevent specific exceptions from being reported to your logging service?",
    "options": {
      "A": "Edit the 'dontReport' array in the Handler.php",
      "B": "Use the 'stopIgnoring' or 'dontReport' methods within bootstrap/app.php",
      "C": "Delete the exception class",
      "D": "Change the .env log level"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Hydration' refer to in the context of Laravel Eloquent?",
    "options": {
      "A": "Updating the server's RAM",
      "B": "The process of converting raw database results into Eloquent model instances",
      "C": "Saving a model to the database",
      "D": "Refreshing the browser cache"
    },
    "answer": "B"
  },
  {
    "question": "Which Eloquent feature allows you to cast a JSON database column directly into a specialized Class or Value Object?",
    "options": {
      "A": "AsCollection",
      "B": "AsObject",
      "C": "Custom Casts (implementing CastsAttributes)",
      "D": "Array mapping"
    },
    "answer": "C"
  },
  {
    "question": "What is 'Database Query Tagging' in Laravel useful for?",
    "options": {
      "A": "Adding hashtags to user comments",
      "B": "Adding comments to SQL queries so they can be easily identified in database logs or monitoring tools",
      "C": "Sorting tables by category",
      "D": "Encrypting the query string"
    },
    "answer": "B"
  },
  {
    "question": "Which interface should a class implement to be used as a 'Custom Validation Rule' in Laravel?",
    "options": {
      "A": "Rule",
      "B": "ValidationRule",
      "C": "ValidatesAttribute",
      "D": "CustomRule"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Laravel Pint'?",
    "options": {
      "A": "To measure server temperature",
      "B": "An opinionated PHP code style fixer for Laravel, built on top of PHP-CS-Fixer",
      "C": "A tool to generate documentation",
      "D": "A database migration manager"
    },
    "answer": "B"
  },
  {
    "question": "In a 'Many-to-Many' relationship, which method is used to add records to the pivot table without removing existing ones?",
    "options": {
      "A": "sync()",
      "B": "attach()",
      "C": "toggle()",
      "D": "save()"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Failover' cache driver in Laravel?",
    "options": {
      "A": "A driver that only works when the internet is down",
      "B": "A configuration that allows Laravel to switch to a secondary cache store if the primary one fails",
      "C": "A way to delete the cache",
      "D": "A tool to test server crashes"
    },
    "answer": "B"
  },
  {
    "question": "Which helper function is used to convert a string to 'Camel Case'?",
    "options": {
      "A": "Str::camel()",
      "B": "Str::studly()",
      "C": "Str::snake()",
      "D": "Str::case()"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Laravel Prompts' primarily used for?",
    "options": {
      "A": "Sending push notifications to browsers",
      "B": "Building beautiful and user-friendly command-line interfaces with interactive forms",
      "C": "Managing AI prompts for ChatGPT",
      "D": "Displaying alerts in Blade views"
    },
    "answer": "B"
  },
  {
    "question": "Which testing method is used to 'Freeze' the current time so that time-dependent logic can be tested accurately?",
    "options": {
      "A": "Time::stop()",
      "B": "this->travelTo()",
      "C": "Carbon::freeze()",
      "D": "clock()->pause()"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Service Locator' anti-pattern in Laravel?",
    "options": {
      "A": "Using dependency injection too much",
      "B": "Using the 'app()' helper or global facades inside a class instead of injecting dependencies through the constructor",
      "C": "A way to find nearby servers",
      "D": "Creating too many service providers"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Decorator' pattern equivalent in Laravel when using 'bind' and 'extend' in a Service Provider?",
    "options": {
      "A": "Singleton",
      "B": "Binding a wrapper class that adds functionality to an existing service",
      "C": "Factory",
      "D": "Facade"
    },
    "answer": "B"
  },
  {
    "question": "In Laravel 11, which Artisan command would you use to create a 'Class-based' middleware instead of an anonymous function?",
    "options": {
      "A": "php artisan make:middleware",
      "B": "php artisan middleware:create",
      "C": "php artisan new:middleware",
      "D": "php artisan add:middleware"
    },
    "answer": "A"
  },
  {
    "question": "What does the 'Scope Resolution Operator' (::) do when used with a Model in a Controller's 'invoke' method?",
    "options": {
      "A": "Deletes the model",
      "B": "Allows access to static methods or constants of the Model class",
      "C": "Changes the database connection",
      "D": "Initializes a new object"
    },
    "answer": "B"
  },
  {
    "question": "Which Laravel feature allows you to intercept and modify every database query executed by the application for auditing purposes?",
    "options": {
      "A": "DB::listen()",
      "B": "DB::watch()",
      "C": "DB::intercept()",
      "D": "DB::log()"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Partial Mocking' in Laravel Testing?",
    "options": {
      "A": "Mocking only the database",
      "B": "Mocking only specific methods of a class while keeping the rest of the class implementation real",
      "C": "Mocking the CSS",
      "D": "Mocking the user login"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'Context' facade introduced in Laravel 11?",
    "options": {
      "A": "To change the UI theme",
      "B": "To store and retrieve information (like request IDs or trace IDs) across logs, jobs, and notifications during a single lifecycle",
      "C": "To manage multiple databases",
      "D": "To handle translations"
    },
    "answer": "B"
  },
  {
    "question": "Which Eloquent method is used to retrieve a collection of IDs from a large table without loading the full model into memory?",
    "options": {
      "A": "all()->pluck('id')",
      "B": "toQuery()->pluck('id')",
      "C": "pluck('id')",
      "D": "select('id')->get()"
    },
    "answer": "C"
  },
  {
    "question": "What is 'Route Caching' primarily used for in production?",
    "options": {
      "A": "To save the HTML of a page",
      "B": "To significantly reduce the time it takes to register all of your application routes by converting them into a single PHP array",
      "C": "To store user passwords",
      "D": "To speed up file uploads"
    },
    "answer": "B"
  },
  {
    "question": "Which method on the 'Gate' facade is used to check multiple permissions at once?",
    "options": {
      "A": "check()",
      "B": "any()",
      "C": "none()",
      "D": "all()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Laravel Vapor's' environment-level secret management tool?",
    "options": {
      "A": "Vault",
      "B": "Secret Manager (AWS integration)",
      "C": "Env-Lock",
      "D": "Safe-Storage"
    },
    "answer": "B"
  },
  {
    "question": "Which design pattern is the 'Service Provider' in Laravel an implementation of?",
    "options": {
      "A": "Observer Pattern",
      "B": "Dependency Injection / Inversion of Control (IoC) Pattern",
      "C": "Strategy Pattern",
      "D": "Command Pattern"
    },
    "answer": "B"
  },
  {
    "question": "What happens when you use 'php artisan config:cache' in production?",
    "options": {
      "A": "The application stops working",
      "B": "Laravel combines all config files into a single file for faster loading; global env() calls will return null except in config files",
      "C": "The .env file is deleted",
      "D": "The database is backed up"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Conditional Middleware' in Laravel?",
    "options": {
      "A": "Middleware that only works on weekends",
      "B": "Middleware that can be skipped or included based on a specific boolean logic at runtime",
      "C": "Middleware for error handling",
      "D": "A way to rename middleware"
    },
    "answer": "B"
  },
  {
    "question": "Which Artisan command helps you identify the exact location of a specific service binding in the container?",
    "options": {
      "A": "php artisan app:name",
      "B": "php artisan container:show",
      "C": "php artisan about (under Drivers/Providers)",
      "D": "php artisan list"
    },
    "answer": "C"
  },
  {
    "question": "What is the purpose of the 'Lottery' class in Laravel?",
    "options": {
      "A": "To build a gambling app",
      "B": "To execute a piece of code based on a specific probability (e.g., 1 out of 100 times), useful for sampling or cleanup",
      "C": "To generate random numbers for IDs",
      "D": "To choose a random user"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Decorator' pattern equivalent in Laravel when using 'bind' and 'extend' in a Service Provider?",
    "options": {
      "A": "Singleton",
      "B": "Binding a wrapper class that adds functionality to an existing service",
      "C": "Factory",
      "D": "Facade"
    },
    "answer": "B"
  },
  {
    "question": "In Laravel 11, which Artisan command would you use to create a 'Class-based' middleware instead of an anonymous function?",
    "options": {
      "A": "php artisan make:middleware",
      "B": "php artisan middleware:create",
      "C": "php artisan new:middleware",
      "D": "php artisan add:middleware"
    },
    "answer": "A"
  },
  {
    "question": "What does the 'Scope Resolution Operator' (::) do when used with a Model in a Controller's 'invoke' method?",
    "options": {
      "A": "Deletes the model",
      "B": "Allows access to static methods or constants of the Model class",
      "C": "Changes the database connection",
      "D": "Initializes a new object"
    },
    "answer": "B"
  },
  {
    "question": "Which Laravel feature allows you to intercept and modify every database query executed by the application for auditing purposes?",
    "options": {
      "A": "DB::listen()",
      "B": "DB::watch()",
      "C": "DB::intercept()",
      "D": "DB::log()"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Partial Mocking' in Laravel Testing?",
    "options": {
      "A": "Mocking only the database",
      "B": "Mocking only specific methods of a class while keeping the rest of the class implementation real",
      "C": "Mocking the CSS",
      "D": "Mocking the user login"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'Context' facade introduced in Laravel 11?",
    "options": {
      "A": "To change the UI theme",
      "B": "To store and retrieve information (like request IDs or trace IDs) across logs, jobs, and notifications during a single lifecycle",
      "C": "To manage multiple databases",
      "D": "To handle translations"
    },
    "answer": "B"
  },
  {
    "question": "Which Eloquent method is used to retrieve a collection of IDs from a large table without loading the full model into memory?",
    "options": {
      "A": "all()->pluck('id')",
      "B": "toQuery()->pluck('id')",
      "C": "pluck('id')",
      "D": "select('id')->get()"
    },
    "answer": "C"
  },
  {
    "question": "What is 'Route Caching' primarily used for in production?",
    "options": {
      "A": "To save the HTML of a page",
      "B": "To significantly reduce the time it takes to register all of your application routes by converting them into a single PHP array",
      "C": "To store user passwords",
      "D": "To speed up file uploads"
    },
    "answer": "B"
  },
  {
    "question": "Which method on the 'Gate' facade is used to check multiple permissions at once?",
    "options": {
      "A": "check()",
      "B": "any()",
      "C": "none()",
      "D": "all()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Laravel Vapor's' environment-level secret management tool?",
    "options": {
      "A": "Vault",
      "B": "Secret Manager (AWS integration)",
      "C": "Env-Lock",
      "D": "Safe-Storage"
    },
    "answer": "B"
  },
  {
    "question": "Which design pattern is the 'Service Provider' in Laravel an implementation of?",
    "options": {
      "A": "Observer Pattern",
      "B": "Dependency Injection / Inversion of Control (IoC) Pattern",
      "C": "Strategy Pattern",
      "D": "Command Pattern"
    },
    "answer": "B"
  },
  {
    "question": "What happens when you use 'php artisan config:cache' in production?",
    "options": {
      "A": "The application stops working",
      "B": "Laravel combines all config files into a single file for faster loading; global env() calls will return null except in config files",
      "C": "The .env file is deleted",
      "D": "The database is backed up"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Conditional Middleware' in Laravel?",
    "options": {
      "A": "Middleware that only works on weekends",
      "B": "Middleware that can be skipped or included based on a specific boolean logic at runtime",
      "C": "Middleware for error handling",
      "D": "A way to rename middleware"
    },
    "answer": "B"
  },
  {
    "question": "Which Artisan command helps you identify the exact location of a specific service binding in the container?",
    "options": {
      "A": "php artisan app:name",
      "B": "php artisan container:show",
      "C": "php artisan about (under Drivers/Providers)",
      "D": "php artisan list"
    },
    "answer": "C"
  },
  {
    "question": "What is the purpose of the 'Lottery' class in Laravel?",
    "options": {
      "A": "To build a gambling app",
      "B": "To execute a piece of code based on a specific probability (e.g., 1 out of 100 times), useful for sampling or cleanup",
      "C": "To generate random numbers for IDs",
      "D": "To choose a random user"
    },
    "answer": "B"
  },
  {
    "question": "Which design pattern does Laravel use to process a request through a series of 'pipes' (middleware) before reaching the controller?",
    "options": {
      "A": "The Pipeline Pattern",
      "B": "The Bridge Pattern",
      "C": "The Composite Pattern",
      "D": "The Proxy Pattern"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'Static Analysis' benefit of using Laravel Larastan/PHPStan?",
    "options": {
      "A": "It speeds up the database queries",
      "B": "It finds bugs in your code without actually running it by analyzing types and logic",
      "C": "It creates a static version of your website",
      "D": "It minifies your CSS and JS files"
    },
    "answer": "B"
  },
  {
    "question": "In the Service Container, what is the difference between 'bind' and 'singleton'?",
    "options": {
      "A": "Bind is for classes; Singleton is for interfaces",
      "B": "Bind creates a new instance every time it is resolved; Singleton resolves the same instance throughout the lifecycle",
      "C": "Singleton is only for Laravel 11",
      "D": "Bind is faster than Singleton"
    },
    "answer": "B"
  },
  {
    "question": "Which Artisan command is used to generate a 'Scoped' session for a specific user during manual testing or debugging?",
    "options": {
      "A": "php artisan session:user",
      "B": "Laravel does not have a native command for this; it requires the 'Laravel Impersonate' package or custom logic",
      "C": "php artisan auth:test",
      "D": "php artisan user:login"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Database Deadlock' and how does Laravel handle it in a transaction?",
    "options": {
      "A": "When the database stops responding; Laravel restarts the server",
      "B": "When two transactions wait for each other; Laravel provides a 'retry' argument in the transaction method to attempt the logic again",
      "C": "When a migration fails midway",
      "D": "When the database reaches its storage limit"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Laravel Benchmarking' (introduced via the Benchmark class)?",
    "options": {
      "A": "To compare Laravel with other frameworks",
      "B": "To measure the execution time of specific code blocks or closures accurately",
      "C": "To test the internet speed of the server",
      "D": "To count the number of lines in a file"
    },
    "answer": "B"
  },
  {
    "question": "Which method in a custom Service Provider is executed only after ALL other service providers have been registered?",
    "options": {
      "A": "register()",
      "B": "boot()",
      "C": "after()",
      "D": "initialize()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Zero-downtime Deployment' in the context of Laravel Forge or Envoyer?",
    "options": {
      "A": "The server never restarts",
      "B": "The process of deploying code to a new directory and switching a symbolic link only after the build is successful",
      "C": "Deploying only on weekends",
      "D": "Using a server with 100% uptime guarantee"
    },
    "answer": "B"
  },
  {
    "question": "In Eloquent, what is the 'Touch' property used for on a child relationship?",
    "options": {
      "A": "To delete the child record",
      "B": "To update the 'updated_at' timestamp of the parent model whenever a child model is updated",
      "C": "To count the number of children",
      "D": "To hide the child from the API"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Horizontal Scaling' for a Laravel application?",
    "options": {
      "A": "Adding more RAM to a single server",
      "B": "Adding more server instances and using a load balancer to distribute traffic",
      "C": "Making the website work on widescreen monitors",
      "D": "Moving the database to a separate server"
    },
    "answer": "B"
  },
  {
    "question": "Which package is used to create 'API Documentation' automatically from your Laravel routes and docblocks?",
    "options": {
      "A": "Laravel Telescope",
      "B": "Scribe or L5-Swagger",
      "C": "Laravel Pulse",
      "D": "Laravel Breeze"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Through' relationship (e.g., hasOneThrough) primarily used to avoid?",
    "options": {
      "A": "Writing SQL manually",
      "B": "Unnecessary intermediate model instantiations when accessing distant relations",
      "C": "Creating many-to-many tables",
      "D": "Using the .env file"
    },
    "answer": "B"
  },
  {
    "question": "Which Artisan command is used to 'Prune' failed jobs from the database?",
    "options": {
      "A": "php artisan queue:flush",
      "B": "php artisan queue:prune-failed",
      "C": "php artisan job:delete",
      "D": "php artisan queue:clear"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Route Grouping' with 'Subdomains' useful for?",
    "options": {
      "A": "To make the URL look shorter",
      "B": "To assign specific routes to a subdomain (e.g., account.verifihire.com) and capture the subdomain as a parameter",
      "C": "To hide routes from the main domain",
      "D": "To speed up DNS lookups"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Laravel Valet's' 'isolate' command?",
    "options": {
      "A": "To disconnect from the internet",
      "B": "To run a specific site using a different version of PHP than the global Valet version",
      "C": "To hide a site from other users on the network",
      "D": "To run the site in a virtual machine"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary function of the 'Pipeline' facade in Laravel's internal architecture?",
    "options": {
      "A": "To manage database migrations in a sequence",
      "B": "To pass an object through a series of 'pipes' (classes) that perform operations on it before returning the final result",
      "C": "To connect the application to an external CI/CD pipeline",
      "D": "To compress data streams for faster API responses"
    },
    "answer": "B"
  },
  {
    "question": "In the context of Laravel's Service Container, what is 'Contextual Binding'?",
    "options": {
      "A": "Binding a service to the user's geographical location",
      "B": "The ability to inject different implementations of an interface depending on which class is requesting it",
      "C": "Automatically translating the database context based on the browser language",
      "D": "Restricting a service to only work within a specific controller"
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
    skill = "Laravel"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
