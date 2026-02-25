from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
  {
    "question": "What is the core philosophy of Ruby on Rails regarding application structure?",
    "options": {
      "A": "Configuration over Convention (CoC)",
      "B": "Convention over Configuration (CoC) and Don't Repeat Yourself (DRY)",
      "C": "Manual memory management and low-level control",
      "D": "Heavy reliance on XML configuration files"
    },
    "answer": "B"
  },
  {
    "question": "In the Rails MVC architecture, what is the primary responsibility of the 'Controller'?",
    "options": {
      "A": "Defining the database schema and table relationships",
      "B": "Handling incoming web requests, interacting with the model, and rendering the appropriate view",
      "C": "Providing the CSS and JavaScript for the frontend",
      "D": "Managing the Ruby version manager (RVM)"
    },
    "answer": "B"
  },
  {
    "question": "Which command is used to create a new database table or modify an existing one in Rails?",
    "options": {
      "A": "rails generate table",
      "B": "rails db:migrate",
      "C": "rails db:update",
      "D": "rails server --db"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Active Record' in Ruby on Rails?",
    "options": {
      "A": "A tool for recording the user's screen during testing",
      "B": "The Object-Relational Mapping (ORM) layer that connects Ruby objects to database tables",
      "C": "A background job processor for sending emails",
      "D": "The default web server for development"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'Gemfile' in a Rails project?",
    "options": {
      "A": "To store high-resolution images (gems) for the UI",
      "B": "To list and manage the Ruby library dependencies (gems) required for the application",
      "C": "To encrypt the application's source code",
      "D": "To define the routes for the web application"
    },
    "answer": "B"
  },
  {
    "question": "In Rails routing, what does 'resources :photos' automatically create?",
    "options": {
      "A": "A folder named photos in the assets directory",
      "B": "A set of seven standard RESTful routes (index, show, new, create, etc.) for the Photos controller",
      "C": "A database table named photos",
      "D": "A backup of all photo files on the server"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Action View' responsible for?",
    "options": {
      "A": "Monitoring the performance of the server",
      "B": "Compiling and rendering the templates (like ERB or HAML) that generate the HTML response",
      "C": "Handling background tasks and cron jobs",
      "D": "Interacting directly with the SQL database"
    },
    "answer": "B"
  },
  {
    "question": "Which Rails feature allows you to execute code in the background, outside the main request-response cycle?",
    "options": {
      "A": "Action Cable",
      "B": "Active Job",
      "C": "Active Storage",
      "D": "Action Mailer"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'Strong Parameters' feature prevent?",
    "options": {
      "A": "Weak passwords from being saved",
      "B": "Mass assignment vulnerabilities by explicitly requiring and permitting specific parameters",
      "C": "Large files from being uploaded to the server",
      "D": "Slow network connections from timing out"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Asset Pipeline' (Sprockets/Propshaft) used for?",
    "options": {
      "A": "Managing the flow of physical assets in a warehouse",
      "B": "Concatenating, minifying, and processing CSS, JavaScript, and image files for faster loading",
      "C": "Connecting the app to an Amazon S3 bucket",
      "D": "Tracking the financial assets of the company"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Polymorphic Association' in Rails?",
    "options": {
      "A": "A model that can encrypt multiple types of data",
      "B": "An association that allows a model to belong to more than one other model on a single association",
      "C": "A database table that can store both strings and integers in the same column",
      "D": "A way to connect Rails to multiple different database types simultaneously"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary purpose of an 'Active Record Scope'?",
    "options": {
      "A": "To limit the physical size of the database file",
      "B": "To define commonly-used queries as method calls on the model that can be easily chained",
      "C": "To view the source code of the Ruby interpreter",
      "D": "To increase the security scope of the admin panel"
    },
    "answer": "B"
  },
  {
    "question": "In Rails, what is the 'N+1 Query Problem'?",
    "options": {
      "A": "When the database has one more column than the model",
      "B": "A performance issue where the application executes one query to fetch parent records and then 'N' additional queries to fetch associated records",
      "C": "A mathematical error in the Ruby math library",
      "D": "When two users try to update the same record at the exact same time"
    },
    "answer": "B"
  },
  {
    "question": "Which Active Record method is used to solve the N+1 query problem via eager loading?",
    "options": {
      "A": "all",
      "B": "includes",
      "C": "select",
      "D": "pluck"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Action Mailer' do in a Rails application?",
    "options": {
      "A": "It physically prints letters to be sent by post",
      "B": "It allows you to send emails from your application using a mailer model and view",
      "C": "It manages the internal messaging system between developers",
      "D": "It handles the shipping and logistics of physical goods"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Active Support' in the context of Ruby on Rails?",
    "options": {
      "A": "A premium customer support service for Rails developers",
      "B": "A component of Rails that provides Ruby language extensions, utilities, and other transversal concerns",
      "C": "A tool that keeps the server active during high traffic",
      "D": "A database driver for SQLite"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Callbacks' (like before_save) in Active Record?",
    "options": {
      "A": "To call the user on their phone after they register",
      "B": "To trigger logic at specific points in the life cycle of an Active Record object",
      "C": "To revert the database to a previous state",
      "D": "To restart the Rails server after a crash"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Schema.rb' file used for?",
    "options": {
      "A": "Storing the application's secret API keys",
      "B": "A source-controlled representation of the current state of the database schema",
      "C": "Writing custom CSS for the database management tool",
      "D": "Defining the routes of the application"
    },
    "answer": "B"
  },
  {
    "question": "In Rails, what is 'Turbolinks' (or Hotwire/Turbo)?",
    "options": {
      "A": "A way to speed up the physical hard drive",
      "B": "Techniques used to make navigating between pages in a web application faster by avoiding full page reloads",
      "C": "A tool for generating random passwords",
      "D": "A type of turbo-charged engine for server cooling"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Concerns' directory in Rails models/controllers used for?",
    "options": {
      "A": "Storing complaints from users",
      "B": "Extracting and sharing common code across multiple models or controllers (Mixins)",
      "C": "Saving the logs of errors that concern the developer",
      "D": "Handling the configuration of the Ruby environment"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Action Cable' in a Rails application?",
    "options": {
      "A": "To connect the server to a physical fiber-optic cable",
      "B": "To integrate WebSockets with the rest of the Rails application for real-time features",
      "C": "To manage background file uploads to cloud storage",
      "D": "To speed up the connection between the database and the model"
    },
    "answer": "B"
  },
  {
    "question": "In Rails, what is a 'Jbuilder' template used for?",
    "options": {
      "A": "Building custom JavaScript libraries",
      "B": "Providing a DSL for declaring JSON structures, typically used for API responses",
      "C": "Generating CSS-in-JS code automatically",
      "D": "Compiling Ruby code into Java"
    },
    "answer": "B"
  },
  {
    "question": "Which testing framework is the most popular community alternative to the default Minitest in Rails?",
    "options": {
      "A": "PyTest",
      "B": "RSpec",
      "C": "JUnit",
      "D": "Mocha"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Database Seeding' in Rails?",
    "options": {
      "A": "Deleting the database and starting from scratch",
      "B": "Providing initial data (via seeds.rb) required for an application to run in a fresh environment",
      "C": "Encrypting the database for security",
      "D": "Splitting the database into multiple smaller shards"
    },
    "answer": "B"
  },
  {
    "question": "What does 'self-healing' refer to in the context of Rails 7's 'Import Maps'?",
    "options": {
      "A": "The server automatically fixes broken Ruby code",
      "B": "Managing JavaScript dependencies without a complex build step like Webpack or Node.js",
      "C": "Automatically restoring deleted database records",
      "D": "Fixing CSS layout shifts in the browser"
    },
    "answer": "B"
  },
  {
    "question": "What is the role of a 'Service Object' in a Rails architecture?",
    "options": {
      "A": "To provide internet service to the application",
      "B": "To encapsulate a single business action or complex logic that doesn't fit well in a Model or Controller",
      "C": "To manage the physical hardware of the server",
      "D": "To handle the connection to third-party APIs exclusively"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Flash' hash used for in Rails controllers?",
    "options": {
      "A": "Storing large image files temporarily",
      "B": "Passing temporary messages (like 'Success' or 'Error') from one action to the next viewed page",
      "C": "Creating high-speed animations in the browser",
      "D": "Managing the server's cache duration"
    },
    "answer": "B"
  },
  {
    "question": "What does 'render :json => @user' do in a controller action?",
    "options": {
      "A": "Converts the user object into a PDF",
      "B": "Serializes the @user object into a JSON string and sends it as the HTTP response",
      "C": "Displays the user's data in a table format",
      "D": "Saves the user's data to a JSON file on the server"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Active Storage' used for?",
    "options": {
      "A": "Storing Ruby code in a cloud repository",
      "B": "Facilitating file uploads (like avatars or documents) to cloud services like Amazon S3 or Google Cloud Storage",
      "C": "Keeping the database active during heavy traffic",
      "D": "Managing local browser storage (localStorage)"
    },
    "answer": "B"
  },
  {
    "question": "In Rails, what is a 'Migration' primarily used for?",
    "options": {
      "A": "Moving the application to a different server",
      "B": "A DSL for managing the database schema over time in a consistent and version-controlled way",
      "C": "Translating the application into different languages",
      "D": "Importing data from an old Excel file"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary benefit of using 'Sidekiq' over the default Active Job 'async' adapter in production?",
    "options": {
      "A": "Sidekiq is written in JavaScript, making it faster for frontend tasks",
      "B": "Sidekiq uses Redis for message persistence and can handle millions of jobs efficiently across multiple threads",
      "C": "Sidekiq replaces the need for a SQL database",
      "D": "Sidekiq automatically writes the Ruby code for background tasks"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Russian Doll Caching' in Rails?",
    "options": {
      "A": "A method to encrypt data in nested layers",
      "B": "A caching strategy where nested fragment caches are invalidated automatically when the inner object is updated (via the 'touch' option)",
      "C": "A way to hide the server's IP address behind multiple proxies",
      "D": "Storing different versions of the same image for different countries"
    },
    "answer": "B"
  },
  {
    "question": "In Active Record, what does the 'touch: true' option do in a 'belongs_to' association?",
    "options": {
      "A": "It enables touch-screen support for the model in the UI",
      "B": "It updates the 'updated_at' timestamp of the parent record whenever the child record is saved or destroyed",
      "C": "It deletes the parent record if the child is touched",
      "D": "It creates a physical backup of the record on a separate drive"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Metaprogramming' in Ruby, frequently used by Rails?",
    "options": {
      "A": "Writing code that can only be understood by a compiler",
      "B": "The ability of a program to write or manipulate its own code at runtime (e.g., dynamic method definition)",
      "C": "A way to program the server hardware directly",
      "D": "Building a program that can only run inside another program"
    },
    "answer": "B"
  },
  {
    "question": "How does Rails protect against 'Session Fixation' attacks?",
    "options": {
      "A": "By requiring the user to log in every 5 minutes",
      "B": "By resetting the session ID after a successful login",
      "C": "By disabling cookies entirely",
      "D": "By encrypting the user's mouse movements"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'Rack' interface in the Rails stack?",
    "options": {
      "A": "A physical shelf for holding servers in a data center",
      "B": "A minimal, modular, and adaptable interface for developing web applications in Ruby, sitting between the web server and the framework",
      "C": "A database tool for organizing tables into rows",
      "D": "A security protocol for verifying SSL certificates"
    },
    "answer": "B"
  },
  {
    "question": "In Rails, what is 'Eager Loading' designed to prevent?",
    "options": {
      "A": "The server from loading too much data into the RAM at once",
      "B": "The N+1 query problem, where the application makes too many separate database calls",
      "C": "The user from seeing the page before it is fully ready",
      "D": "The database from becoming corrupted during an update"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Content Security Policy' (CSP) help mitigate in a Rails app?",
    "options": {
      "A": "Slow database queries",
      "B": "Cross-Site Scripting (XSS) and data injection attacks by restricting where resources can be loaded from",
      "C": "The cost of hosting the application in the cloud",
      "D": "The amount of content a user can see without a subscription"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Database Index' and why should you use it in Rails migrations?",
    "options": {
      "A": "A list of all the developers who have worked on the database",
      "B": "A data structure that improves the speed of data retrieval operations on a table at the cost of additional storage and slower writes",
      "C": "A way to name the tables in alphabetical order",
      "D": "A security feature that prevents unauthorized access to specific rows"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Scope' in a Rails Model commonly used for?",
    "options": {
      "A": "Measuring the performance of the CPU",
      "B": "Defining custom, reusable database queries that can be called like class methods",
      "C": "Viewing the code through a specialized editor",
      "D": "Increasing the visibility of the website on Google"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Hotwire' in the context of modern Ruby on Rails (v7+)?",
    "options": {
      "A": "A physical hardware upgrade for Ruby servers",
      "B": "A suite of technologies (Turbo and Stimulus) that send HTML over the wire instead of JSON, reducing the need for complex JavaScript",
      "C": "A tool used for real-time video streaming",
      "D": "A security feature that alerts developers of a breach"
    },
    "answer": "B"
  },
  {
    "question": "In Rails 7, what is the purpose of 'Import Maps'?",
    "options": {
      "A": "To create maps of the server's physical location",
      "B": "To allow developers to import JavaScript modules directly in the browser without requiring a transpilation or bundling step like Webpack",
      "C": "To import legacy database records from CSV files",
      "D": "To map specific users to specific geographic regions"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Turbo Streams' capable of doing?",
    "options": {
      "A": "Encoding videos at high speeds",
      "B": "Delivering live page updates to specific parts of the DOM over a WebSocket or in response to an HTTP request",
      "C": "Streaming large database backups to a cloud bucket",
      "D": "Compressing the Rails source code into a smaller file"
    },
    "answer": "B"
  },
  {
    "question": "How does Rails manage 'Multi-database' support (introduced in v6)?",
    "options": {
      "A": "By requiring a separate Rails app for each database",
      "B": "By allowing a model to connect to a different database role (e.g., primary for writes and replica for reads) or an entirely separate database",
      "C": "By converting all SQL databases into a single NoSQL file",
      "D": "By using a special adapter that merges all tables into one"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Stimulus JS' used for in a Rails application?",
    "options": {
      "A": "To provide high-speed animations",
      "B": "A modest JavaScript framework that augments HTML by connecting elements to JavaScript objects via data attributes",
      "C": "To replace the Ruby on Rails backend entirely",
      "D": "To manage the server-side state in the browser"
    },
    "answer": "B"
  },
  {
    "question": "Which Rails feature allows for 'Encrypted Credentials'?",
    "options": {
      "A": "Active Cryptography",
      "B": "Credentials.yml.enc, which stores sensitive data like API keys in an encrypted file that is decrypted with a master key",
      "C": "Action Secret",
      "D": "A third-party plugin named 'SecureKey'",
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Enum' in an Active Record model?",
    "options": {
      "A": "To create an infinite loop for testing",
      "B": "To map an integer column in the database to a set of human-readable symbols in the model",
      "C": "To list the number of users in the system",
      "D": "To define a range of numbers for a slider"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Active Model::Serializer' or 'Blueprinter' provide?",
    "options": {
      "A": "A way to print the Ruby code on paper",
      "B": "Tools to customize the JSON structure of API responses, separating the data representation from the model",
      "C": "A method to serialize Ruby objects into XML",
      "D": "A backup tool for database records"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Active Record Encryption' (Rails 7+)?",
    "options": {
      "A": "Encrypting the entire physical server",
      "B": "A built-in way to provide at-rest encryption for specific attributes in a database table",
      "C": "A tool that requires a password to open the database",
      "D": "A way to hide table names from other developers"
    },
    "answer": "B"
  },
 {
    "question": "What is 'Solid Queue' introduced as the default in Rails 8?",
    "options": {
      "A": "A new physical cabling system for Ruby servers",
      "B": "A DB-based queuing backend for Active Job that eliminates the need for Redis in many applications",
      "C": "A way to encrypt Ruby code into solid binary files",
      "D": "A tool that prevents users from leaving the site"
    },
    "answer": "B"
  },
  {
    "question": "In Rails, what is 'Shallow Routing' used for?",
    "options": {
      "A": "Reducing the depth of the HTML source code",
      "B": "Generating shorter URLs for nested resources by only nesting the 'index', 'new', and 'create' actions",
      "C": "A way to route traffic to the closest server geographically",
      "D": "Limiting the number of users who can access a route"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'respond_to' block in a controller action?",
    "options": {
      "A": "To ensure the server responds within a specific time limit",
      "B": "To allow the action to return different formats (like HTML, JSON, or XML) depending on the request header",
      "C": "To force the user to respond to a survey",
      "D": "To automatically reply to all incoming emails"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'inverse_of' option in an association do?",
    "options": {
      "A": "It reverses the order of the database records",
      "B": "It informs Active Record about the two-way nature of an association to optimize memory and data consistency",
      "C": "It deletes the child record when the parent is updated",
      "D": "It flips the color of the UI elements for that model"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Middleware' in the context of the Rails/Rack stack?",
    "options": {
      "A": "A physical component in the middle of a server rack",
      "B": "An object that sits between the web server and the Rails application to filter or modify requests and responses",
      "C": "A tool used for managing CSS files in the middle of the project",
      "D": "The database layer that sits between the model and the controller"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Partial Iteration' using the 'collection' parameter?",
    "options": {
      "A": "Rendering only half of the items in a list to save space",
      "B": "An efficient way to render a partial for every item in a collection using a single render call (render partial: 'item', collection: @items)",
      "C": "A loop that stops halfway through the database",
      "D": "A security feature that limits how many times a user can see a list"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'delegate' in a Rails model?",
    "options": {
      "A": "To send a developer to a conference",
      "B": "To forward a method call from one object to another (often an association), following the Law of Demeter",
      "C": "To allow a user to vote for a specific record",
      "D": "To move a database table to a different server"
    },
    "answer": "B"
  },
  {
    "question": "In Active Record, what does 'locking_column' enable?",
    "options": {
      "A": "Physical locking of the hard drive",
      "B": "Optimistic Locking, preventing two users from overwriting each other's changes if they edit the same record simultaneously",
      "C": "Hiding a specific column from the index",
      "D": "Enforcing a password on a specific database field"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Active Record Store' used for?",
    "options": {
      "A": "Selling Ruby on Rails merchandise",
      "B": "Providing a simple way to store a hash of attributes in a single database column (serialized as JSON or YAML)",
      "C": "Storing the physical address of the company",
      "D": "Caching the results of every SQL query"
    },
    "answer": "B"
  },
  {
    "question": "What is the role of 'config.autoload_paths' in Rails?",
    "options": {
      "A": "To automatically download new gems when needed",
      "B": "To tell Rails which additional directories to monitor for classes and modules so they can be loaded without an explicit require statement",
      "C": "To define the paths for a self-driving car application",
      "D": "To map the physical location of the server's folders"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Solid Cable' in Rails 8?",
    "options": {
      "A": "A physical ethernet adapter optimized for Ruby",
      "B": "A database-backed Action Cable adapter that removes the requirement for Redis for WebSockets",
      "C": "A tool that prevents cable-related hardware failures",
      "D": "An encryption layer for local network traffic"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary benefit of using the 'ViewComponent' library in a Rails project?",
    "options": {
      "A": "It converts HTML into React components automatically",
      "B": "It provides a framework for building reusable, testable, and encapsulated view components as Ruby objects",
      "C": "It speeds up the database by caching the view layer",
      "D": "It allows the database to be viewed in a web browser"
    },
    "answer": "B"
  },
  {
    "question": "In Active Record, what is the difference between 'count' and 'size' on a collection?",
    "options": {
      "A": "Count is for strings, and size is for integers",
      "B": "Count always executes a SQL COUNT query; size uses the counter cache if available or the loaded collection's length",
      "C": "Size always reloads the database, while count uses the cache",
      "D": "There is no functional difference between them"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Conditional GET' in the context of Rails caching?",
    "options": {
      "A": "Only allowing GET requests if the user is an admin",
      "B": "Using HTTP headers (ETag and Last-Modified) to tell the browser not to re-download a page if it hasn't changed",
      "C": "A way to fetch data only if the server is under low load",
      "D": "A security feature that prevents POST requests from being cached"
    },
    "answer": "B"
  },
  {
    "question": "What is the role of 'Active Support::CurrentAttributes'?",
    "options": {
      "A": "To keep track of the current weather at the data center",
      "B": "To provide a thread-isolated attributes singleton, useful for tracking per-request values like the current user or request ID",
      "C": "To store the physical attributes of the server hardware",
      "D": "To automatically update the database with current timestamps"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'System Test' in Rails?",
    "options": {
      "A": "A test that checks the computer's CPU and RAM",
      "B": "A full-stack test that uses a real or headless browser to test the application's behavior from the user's perspective",
      "C": "A test that only checks the operating system's version",
      "D": "A test that verifies the electrical system in the data center"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Enum' prefix/suffix options in Rails 7+?",
    "options": {
      "A": "To add random letters to the database names",
      "B": "To avoid naming collisions when multiple enums in the same model use the same value names",
      "C": "To translate the enum values into different languages",
      "D": "To increase the security of the enum column"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Database Throttling' in a Rails application?",
    "options": {
      "A": "Increasing the database speed by 200%",
      "B": "Intentionally slowing down background jobs or requests to prevent the database from being overwhelmed",
      "C": "Using a physical throttle to control the server",
      "D": "Deleting slow records to speed up the index"
    },
    "answer": "B"
  },
  {
    "question": "What does 'ActiveRecord::Base.transaction' ensure?",
    "options": {
      "A": "That the user pays for the service before using it",
      "B": "That a block of database operations either all succeed or all fail together (Atomicity)",
      "C": "That the database is backed up after every change",
      "D": "That the server is in a secure transaction mode"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Prop_tags' helper used for in modern Rails assets?",
    "options": {
      "A": "Adding tags to a physical property",
      "B": "Generating the correct HTML tags for Import Maps and JavaScript modules",
      "C": "Tagging users who have not paid their subscription",
      "D": "Organizing the CSS files into different categories"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Solid Slot' (introduced in Rails 8) primarily used for?",
    "options": {
      "A": "Inserting physical expansion cards into the server",
      "B": "A database-backed session store that replaces the need for Redis or CookieStore in high-security environments",
      "C": "A way to slot different CSS themes into a single layout",
      "D": "A tool that tracks the time slots for background jobs"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Horizontal Sharding' in Active Record?",
    "options": {
      "A": "Rotating the database tables by 90 degrees",
      "B": "Distributing data across multiple database instances based on a shard key to improve scalability",
      "C": "Splitting a single table into multiple tables based on column types",
      "D": "Moving the database from a vertical server to a rack-mounted server"
    },
    "answer": "B"
  },
  {
    "question": "In Rails, what does 'rescue_from' do in a Controller or ActiveJob?",
    "options": {
      "A": "It rescues the server from a physical fire alert",
      "B": "It provides a declarative way to handle specific exceptions and define a custom response or cleanup logic",
      "C": "It automatically calls the support team when an error occurs",
      "D": "It restarts the database whenever a query fails"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Action Policy' as an alternative to Pundit?",
    "options": {
      "A": "To create physical policies for the office building",
      "B": "A specialized authorization framework that provides higher performance and better integration with Rails' testing suite",
      "C": "A tool that generates legal documents for the web app",
      "D": "A way to set the insurance policy for the server hardware"
    },
    "answer": "B"
  },
  {
    "question": "What does 'ActiveRecord::Base.ignored_columns' allow developers to do?",
    "options": {
      "A": "Hide columns that they don't like from the database view",
      "B": "Safely remove columns from the database by telling Rails to ignore them before the physical migration is run",
      "C": "Delete data from the database without a backup",
      "D": "Rename columns to stay anonymous"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Fragment Caching' in a Rails view?",
    "options": {
      "A": "Caching only the broken (fragmented) parts of the code",
      "B": "Caching specific parts of a view template that change less frequently than the whole page",
      "C": "Splitting the cache into small fragments to save RAM",
      "D": "A way to hide parts of the page from the user"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Rack::Attack' commonly used for in Rails?",
    "options": {
      "A": "Attacking other servers on the network",
      "B": "A middleware for throttling, blocking, and tracking malicious requests based on IP or other parameters",
      "C": "A tool for testing the physical strength of the server rack",
      "D": "An automated system for updating Ruby gems"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Loose Foreign Keys' in the context of GitLab's contribution to Rails patterns?",
    "options": {
      "A": "Foreign keys that are not yet connected to a table",
      "B": "A way to handle cross-database referential integrity without using hard database-level foreign keys",
      "C": "A bug where foreign keys are deleted by accident",
      "D": "A security flaw where foreign keys are exposed to the user"
    },
    "answer": "B"
  },
  {
    "question": "In Rails 7.1+, what does 'ActiveSupport::MessagePack' provide?",
    "options": {
      "A": "A way to send physical packages to other developers",
      "B": "An efficient binary serialization format that is faster and smaller than JSON for caching and internal messaging",
      "C": "A tool for packing CSS files into a single zip file",
      "D": "A system for tracking the delivery of emails"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Query Retrying' in Active Record?",
    "options": {
      "A": "Asking the user to re-type their search query",
      "B": "Automatically retrying a database query if it fails due to a deadlock or connection error",
      "C": "Manually rewriting a slow SQL query",
      "D": "A way to check if the database is still online"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Thrashing' in the context of Rails Active Record caching, and how is it prevented?",
    "options": {
      "A": "The server making loud noises; prevented by soundproofing",
      "B": "A state where the cache is constantly invalidated and rebuilt; prevented by using stable cache keys and 'touch' appropriately",
      "C": "A bug in the Ruby garbage collector",
      "D": "When the database writes data faster than it can read it"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Apartment' or 'ActsAsTenant' gem typically used for in Rails?",
    "options": {
      "A": "Renting out server space to other developers",
      "B": "Implementing Multi-Tenancy, allowing a single Rails application to serve multiple clients with data isolation",
      "C": "Managing physical real estate listings",
      "D": "A tool that organizes the Rails project into different folders called 'rooms'"
    },
    "answer": "B"
  },
  {
    "question": "In Rails 7+, what is the purpose of 'Turbo Morphs'?",
    "options": {
      "A": "Converting Ruby code into JavaScript automatically",
      "B": "A technique to update the DOM by 'morphing' existing elements rather than replacing them, preserving scroll position and focus",
      "C": "A way to change the UI color theme instantly",
      "D": "Transforming database records into different data types on the fly"
    },
    "answer": "B"
  },
  {
    "question": "What does 'ActiveRecord::Base.suppress' allow a developer to do?",
    "options": {
      "A": "Silence the computer's cooling fans",
      "B": "Temporarily prevent a model from saving to the database during the execution of a block",
      "C": "Hide specific error messages from the logs",
      "D": "Force a user to log out of the system"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Strict Loading' in Rails 6.1+?",
    "options": {
      "A": "A mode that prevents the server from starting if there are any bugs",
      "B": "A setting that raises an error if an association is lazy-loaded, helping to catch N+1 queries during development",
      "C": "Requiring a password to load the database schema",
      "D": "A way to limit the amount of RAM a single request can use"
    },
    "answer": "B"
  },
  {
    "question": "What is the role of 'Action Text' in a Rails application?",
    "options": {
      "A": "Sending text messages to users' phones",
      "B": "Handling rich text content, including images and formatting, integrated with the Trix editor and Active Storage",
      "C": "Translating the website's text into different languages",
      "D": "A tool that checks the spelling of Ruby code"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Eager Preload' vs 'Joins' in Active Record performance optimization?",
    "options": {
      "A": "They are the same thing",
      "B": "'Joins' uses a single SQL JOIN to filter; 'Preload' (or includes) uses separate queries to load associated data into memory to avoid N+1 issues",
      "C": "'Joins' is only for numbers, while 'Preload' is for text",
      "D": "'Preload' is a security feature, while 'Joins' is for speed"
    },
    "answer": "B"
  },
  {
    "question": "What does 'config.active_record.encryption.primary_key' refer to?",
    "options": {
      "A": "The physical key used to unlock the server room",
      "B": "The root key used to encrypt and decrypt database attributes at rest in Rails 7+",
      "C": "The administrator's personal password",
      "D": "A unique ID assigned to every encrypted file on the server"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Schema Cache' in a production Rails environment?",
    "options": {
      "A": "A list of all the colors used in the UI",
      "B": "A serialized version of the database schema stored in memory to avoid querying the database for table metadata on every request",
      "C": "A backup of the database structure saved to a PDF",
      "D": "A way to hide table names from other developers"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Action Mailbox' designed to handle?",
    "options": {
      "A": "Sending physical mail to a user's home",
      "B": "Routing incoming emails to controller-like mailboxes for processing within the Rails app",
      "C": "Storing the email addresses of all the developers",
      "D": "A tool that generates fake email accounts for testing"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary architectural change introduced by 'Solid Cable' in Rails 8?",
    "options": {
      "A": "It moves all WebSocket logic to the client-side using WebAssembly",
      "B": "It replaces the Redis dependency for Action Cable with a database-backed adapter, simplifying deployment stacks",
      "C": "It requires physical fiber-optic connections for the server",
      "D": "It encrypts WebSocket traffic using a new proprietary protocol"
    },
    "answer": "B"
  },
  {
    "question": "In Rails, what is the 'Law of Demeter' primarily applied to avoid?",
    "options": {
      "A": "Writing more than 100 lines of code in a controller",
      "B": "Tight coupling between objects, often seen as long chains like '@user.profile.settings.theme_name'",
      "C": "Using more than one database in a single application",
      "D": "Allowing users to have multiple active sessions"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'pick' method do in Active Record (Rails 6+)?",
    "options": {
      "A": "It randomly selects a record from the database",
      "B": "It queries for a single value (or an array of values) from a single row, skipping the instantiation of a model object",
      "C": "It allows the user to 'pick' their favorite UI theme",
      "D": "It selects the most efficient index for a specific query"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Atomic Counters' in Active Record used for?",
    "options": {
      "A": "Counting the number of atoms in a physical server",
      "B": "Updating an integer column in the database directly via SQL (e.g., increment!) to avoid race conditions and stale data",
      "C": "Timing how long it takes to run a single Ruby method",
      "D": "Generating a unique serial number for every database record"
    },
    "answer": "B"
  },
  {
    "question": "What is the role of the 'Puma' web server in a standard Rails stack?",
    "options": {
      "A": "To handle the CSS and JavaScript assets",
      "B": "A multi-threaded, high-performance HTTP server that acts as the entry point for requests to the Rails app",
      "C": "To manage the database migrations",
      "D": "To act as a firewall for the server hardware"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Zeitwerk' in the context of Ruby on Rails?",
    "options": {
      "A": "A specialized gem for time-zone management",
      "B": "An efficient, thread-safe code loader that handles the automatic loading of Ruby classes and modules",
      "C": "A tool used for generating PDF reports",
      "D": "A security feature that prevents code from running at night"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Double Splat' operator (**params) used for in Ruby/Rails methods?",
    "options": {
      "A": "To multiply a number by two twice",
      "B": "To capture or pass a variable number of keyword arguments as a hash",
      "C": "To delete two records from the database at once",
      "D": "To comment out an entire block of code"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'config.force_ssl = true' in a Rails production environment?",
    "options": {
      "A": "To force the server to run at higher speeds",
      "B": "To ensure all communication between the browser and server happens over a secure HTTPS connection",
      "C": "To prevent users from using weak passwords",
      "D": "To require a physical security key for every login"
    },
    "answer": "B"
  },
  {
    "question": "In Active Record, what does 'reorder' do compared to 'order'?",
    "options": {
      "A": "It reverses the current order of the records",
      "B": "It replaces any existing order constraints on the query with new ones",
      "C": "It randomly shuffles the database results",
      "D": "It organizes the database tables by their creation date"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Null Object Pattern' used for in Rails development?",
    "options": {
      "A": "To delete all records that have null values",
      "B": "To provide an object that represents 'nothing' to avoid frequent 'if object.nil?' checks in the view or controller",
      "C": "To prevent the database from accepting null entries",
      "D": "To create a ghost user for testing purposes"
    },
    "answer": "B"
  },
  {
    "id": "ROR-441",
    "question": "What is the primary architectural advantage of Rails 8's 'Solid Cache' over traditional Redis-based caching?",
    "options": {
      "A": "It allows the cache to persist in the browser's local storage",
      "B": "It utilizes the SQL database for storage, reducing infrastructure complexity and cost by removing the need for a separate Redis server",
      "C": "It automatically encrypts the cache using quantum-resistant algorithms",
      "D": "It only stores cache fragments that are written in JavaScript"
    },
    "answer": "B"
  },
  {
    "id": "ROR-445",
    "question": "Rails 8 introduces a new built-in 'Authentication Generator'. What is its main purpose?",
    "options": {
      "A": "To replace Devise entirely for all enterprise-level applications",
      "B": "To provide a lightweight, dependency-free starting point for basic authentication (sign-up/login) within the framework",
      "C": "To automatically generate passwords for all new users",
      "D": "To scan the application for leaked API keys"
    },
    "answer": "B"
  },
  {
    "id": "PY-391",
    "question": "In Python 3.12+, what is the purpose of the 'typing.Protocol' for runtime checkable classes?",
    "options": {
      "A": "To define a set of rules for physical networking cables",
      "B": "To implement structural subtyping (static duck typing), allowing a class to be considered a subtype based on its methods rather than explicit inheritance",
      "C": "To encrypt the communication between Python and a database",
      "D": "To prevent the user from importing external libraries"
    },
    "answer": "B"
  },
  {
    "id": "PY-395",
    "question": "Python 3.13 introduces an experimental 'No-GIL' build. What is the goal of this feature?",
    "options": {
      "A": "To prevent the user from locking their computer while a script runs",
      "B": "To allow true parallel execution of Python code across multiple CPU cores without Global Interpreter Lock contention",
      "C": "To create a global lock on all internet traffic",
      "D": "To automatically delete unused variables from memory"
    },
    "answer": "B"
  },
  {
    "id": "ROR-450",
    "question": "Which Rails 8 feature allows background jobs to be processed without a separate Redis or Sidekiq instance?",
    "options": {
      "A": "Active Storage",
      "B": "Solid Queue",
      "C": "Turbo Streams",
      "D": "Action Mailer"
    },
    "answer": "B"
  },
  {
    "id": "PY-400",
    "question": "In Python 3.12, what does the new 'type' statement (e.g., type Point = tuple[float, float]) provide?",
    "options": {
      "A": "It creates a new class in the database",
      "B": "A cleaner, more explicit syntax for defining type aliases that supports generics natively",
      "C": "It forces the computer to type words faster",
      "D": "It identifies the type of hardware being used by the server"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary architectural benefit of 'Solid Cache' compared to traditional Redis caching in Rails 8?",
    "options": {
      "A": "It allows caching of physical hardware states",
      "B": "It utilizes the SQL database for storage, reducing the need for an external key-value store while maintaining high performance via optimized schema",
      "C": "It is written in JavaScript for faster frontend integration",
      "D": "It only works with static HTML files"
    },
    "answer": "B"
  },
  {
    "question": "In StimulusJS, what is the 'target' attribute used for?",
    "options": {
      "A": "To target the server for a cyberattack test",
      "B": "To map important elements to a controller so they can be referenced by name in JavaScript without using CSS selectors",
      "C": "To define the URL target for a form submission",
      "D": "To specify which version of Ruby the controller should use"
    },
    "answer": "B"
  },
  {
    "question": "What does 'ActiveRecord::Base.transaction' with the 'requires_new: true' option achieve?",
    "options": {
      "A": "It deletes the current transaction and starts over",
      "B": "It creates a sub-transaction (using SQL SAVEPOINTs), allowing part of a transaction to fail without rolling back the entire parent transaction",
      "C": "It requires the user to create a new account before proceeding",
      "D": "It forces the database to create a new physical file on the disk"
    },
    "answer": "B"
  },
  {
    "question": "Which Rails 8 feature facilitates 'Zero-Downtime Deploys' to simple VPS instances using Docker?",
    "options": {
      "A": "Action Cable",
      "B": "Kamal (formerly MRSK)",
      "C": "Active Job",
      "D": "Solid Cable"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Shadowing' in the context of Rails 8 Propshaft asset management?",
    "options": {
      "A": "Hiding the source code from other developers",
      "B": "The ability to override a gem's asset by providing a file with the same logical path in the main application",
      "C": "A security feature that prevents assets from being cached",
      "D": "A way to render assets in black and white for accessibility"
    },
    "answer": "B"
  },
  {
    "question": "In Action Cable, what is a 'Channel'?",
    "options": {
      "A": "A physical television channel used for streaming",
      "B": "An encapsulated logic unit that handles specific WebSocket subscriptions and data broadcasting",
      "C": "A way to connect the server to a specific Wi-Fi channel",
      "D": "A storage folder for video files"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Encapsulated Views' via the ViewComponent gem?",
    "options": {
      "A": "Hiding the views from the browser",
      "B": "Treating UI components as Ruby objects with their own data and logic, independent of global helpers",
      "C": "Compressing HTML into a single encrypted line",
      "D": "Moving all view logic into the SQL database"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'config.active_record.verify_foreign_keys_at_runtime'?",
    "options": {
      "A": "To check if the user is from a foreign country",
      "B": "To catch invalid foreign key assignments in the application layer before the database raises a constraint error",
      "C": "To automatically translate foreign key names",
      "D": "To prevent the database from using foreign keys entirely"
    },
    "answer": "B"
  },
  {
    "question": "What does 'ActiveSupport::Notification' allow a developer to do?",
    "options": {
      "A": "Send push notifications to mobile phones",
      "B": "Instrument and subscribe to events happening inside the Rails framework or the application for logging and profiling",
      "C": "Email the developer whenever a user logs in",
      "D": "Create a popup alert on the server's desktop"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Polyfill' management in Rails 8 using Import Maps?",
    "options": {
      "A": "Filling the database with random 'poly' data",
      "B": "Providing modern JavaScript features to older browsers without a complex build step",
      "C": "A way to manage multiple fonts in a single CSS file",
      "D": "Cleaning up unused Ruby code"
    },
    "answer": "B"
  },
  {
    "question": "Which architectural pattern does Ruby on Rails strictly follow?",
    "options": {
      "A": "MVVM",
      "B": "MVC (Model-View-Controller)",
      "C": "VIPER",
      "D": "Monolithic"
    },
    "answer": "B"
  },
  {
    "question": "In Rails, which component is responsible for handling business logic and communicating with the database?",
    "options": {
      "A": "Controller",
      "B": "View",
      "C": "Model",
      "D": "Helper"
    },
    "answer": "C"
  },
  {
    "question": "What is the primary purpose of the 'routes.rb' file in a Rails application?",
    "options": {
      "A": "To define database schemas",
      "B": "To map incoming HTTP requests to specific controller actions",
      "C": "To store environment variables",
      "D": "To configure mailer settings"
    },
    "answer": "B"
  },
  {
    "question": "Which Rails command is used to create a new database table and its corresponding model and controller in one step?",
    "options": {
      "A": "rails build",
      "B": "rails generate scaffold",
      "C": "rails new",
      "D": "rails db:create"
    },
    "answer": "B"
  },
  {
    "question": "What does 'DRY' stand for in the context of Rails development?",
    "options": {
      "A": "Data Retrieval Yield",
      "B": "Don't Repeat Yourself",
      "C": "Direct Rails Yield",
      "D": "Documenting Ruby Yields"
    },
    "answer": "B"
  },
  {
    "question": "Which Active Record method is used to find a record by its primary key and throws an error if not found?",
    "options": {
      "A": "where",
      "B": "find",
      "C": "search",
      "D": "lookup"
    },
    "answer": "B"
  },
  {
    "question": "What is the name of the tool used in Rails to manage database schema changes over time?",
    "options": {
      "A": "Active Storage",
      "B": "Migrations",
      "C": "Schema.rb",
      "D": "Action Pack"
    },
    "answer": "B"
  },
  {
    "question": "In a Rails controller, which method is typically used to handle a 'POST' request to create a new record?",
    "options": {
      "A": "new",
      "B": "create",
      "C": "update",
      "D": "index"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Convention over Configuration' (CoC) in Rails?",
    "options": {
      "A": "A requirement to write config files for every class",
      "B": "The philosophy that Rails assumes sensible defaults so you only need to specify unusual aspects",
      "C": "A rule that all code must be written in Ruby",
      "D": "A tool that converts code to JSON"
    },
    "answer": "B"
  },
  {
    "question": "Which directory in a Rails project contains the HTML templates rendered to the user?",
    "options": {
      "A": "app/models",
      "B": "app/views",
      "C": "app/controllers",
      "D": "public/assets"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Active Record' in Ruby on Rails?",
    "options": {
      "A": "A tool for recording user audio",
      "B": "An Object-Relational Mapping (ORM) framework",
      "C": "A type of JavaScript library",
      "D": "A security protocol for logins"
    },
    "answer": "B"
  },
  {
    "question": "Which command is used to run pending database migrations?",
    "options": {
      "A": "rails migrate:up",
      "B": "rails db:migrate",
      "C": "rails db:start",
      "D": "bundle install"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Gemfile' in a Rails application?",
    "options": {
      "A": "To store the application's logo",
      "B": "To list the dependencies (gems) required by the application",
      "C": "To configure database passwords",
      "D": "To define the routing paths"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Asset Pipeline' (Sprockets/Propshaft) used for?",
    "options": {
      "A": "Managing financial assets",
      "B": "Processing and compressing JavaScript, CSS, and images",
      "C": "Connecting to external APIs",
      "D": "Encrypting database records"
    },
    "answer": "B"
  },
  {
    "question": "In Rails, what is a 'Partial'?",
    "options": {
      "A": "A half-finished function",
      "B": "A reusable view template used to keep views clean and modular",
      "C": "A type of database index",
      "D": "A partial network connection"
    },
    "answer": "B"
  },
  {
    "question": "Which Rails tool allows you to interact with your application via a command-line interface?",
    "options": {
      "A": "Rails Terminal",
      "B": "Rails Console",
      "C": "Ruby Command",
      "D": "IRB"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Action Controller' responsible for?",
    "options": {
      "A": "Managing the database schema",
      "B": "Processing incoming web requests and generating the appropriate response",
      "C": "Sending background emails",
      "D": "Defining CSS styles"
    },
    "answer": "B"
  },
  {
    "question": "Which HTTP verb is associated with the 'update' action in a standard RESTful Rails controller?",
    "options": {
      "A": "GET",
      "B": "PATCH or PUT",
      "C": "POST",
      "D": "DELETE"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'db/seeds.rb' file?",
    "options": {
      "A": "To grow the database size",
      "B": "To populate the database with initial or sample data",
      "C": "To fix corrupted data",
      "D": "To encrypt user passwords"
    },
    "answer": "B"
  },
  {
    "question": "Which file handles the configuration for different environments (Development, Test, Production)?",
    "options": {
      "A": "config/routes.rb",
      "B": "config/environments/*.rb",
      "C": "app/assets/config.rb",
      "D": "Gemfile"
    },
    "answer": "B"
  },
  {
    "question": "Which architectural pattern is the core foundation of Ruby on Rails?",
    "options": {
      "A": "MVVM",
      "B": "MVC (Model-View-Controller)",
      "C": "Layered Architecture",
      "D": "Monolithic Architecture"
    },
    "answer": "B"
  },
  {
    "question": "In Rails, which Active Record association indicates that a model contains the foreign key of another model?",
    "options": {
      "A": "has_one",
      "B": "belongs_to",
      "C": "has_many",
      "D": "composed_of"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary purpose of a 'Migration' in Ruby on Rails?",
    "options": {
      "A": "To move the app from one server to another",
      "B": "To manage and evolve the database schema over time in a consistent way",
      "C": "To convert Ruby code into JavaScript",
      "D": "To import data from a CSV file"
    },
    "answer": "B"
  },
  {
    "question": "Which Rails command is used to start the built-in development web server?",
    "options": {
      "A": "rails start",
      "B": "rails server",
      "C": "rails up",
      "D": "ruby webserver.rb"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'DRY' principle stand for in Rails development?",
    "options": {
      "A": "Data Retrieval Yield",
      "B": "Don't Repeat Yourself",
      "C": "Direct Rails Yield",
      "D": "Database Restoration Yield"
    },
    "answer": "B"
  },
  {
    "question": "Which file is used to map incoming URLs to specific controller actions?",
    "options": {
      "A": "app/controllers/application_controller.rb",
      "B": "config/routes.rb",
      "C": "config/application.rb",
      "D": "db/schema.rb"
    },
    "answer": "B"
  },
  {
    "question": "In an Active Record model, which validation ensures that an attribute is not empty before saving?",
    "options": {
      "A": "validates :name, exists: true",
      "B": "validates :name, presence: true",
      "C": "validates :name, required: true",
      "D": "validates :name, check: true"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'Gemfile' in a Rails project?",
    "options": {
      "A": "To store CSS variables",
      "B": "To list and manage Ruby library dependencies (gems)",
      "C": "To configure database passwords",
      "D": "To define HTML templates"
    },
    "answer": "B"
  },
  {
    "question": "Which Active Record association is used to create a many-to-many relationship through a join table?",
    "options": {
      "A": "has_and_belongs_to_many",
      "B": "has_many :through",
      "C": "belongs_to_many",
      "D": "Both A and B"
    },
    "answer": "D"
  },
  {
    "question": "What is 'Convention over Configuration' (CoC)?",
    "options": {
      "A": "A rule that all code must be written in Ruby",
      "B": "The philosophy that Rails assumes sensible defaults so you only need to specify the unconventional parts",
      "C": "A tool that generates config files",
      "D": "A security setting for the database"
    },
    "answer": "B"
  },
  {
    "question": "Which directory contains the HTML templates (ERB files) in a Rails application?",
    "options": {
      "A": "app/models",
      "B": "app/views",
      "C": "app/controllers",
      "D": "public/html"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Fat Model, Skinny Controller'?",
    "options": {
      "A": "The idea that models should handle business logic, keeping controllers simple and focused on routing/responses",
      "B": "A method to optimize database queries",
      "C": "A naming convention for Rails files",
      "D": "A way to reduce the file size of the application"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to run all pending database migrations?",
    "options": {
      "A": "rails db:migrate",
      "B": "rails migrate",
      "C": "bundle exec migrate",
      "D": "rake db:start"
    },
    "answer": "A"
  },
  {
    "question": "In a RESTful Rails controller, which action is used to display a form for creating a new record?",
    "options": {
      "A": "index",
      "B": "new",
      "C": "create",
      "D": "show"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Cross-Site Request Forgery' (CSRF) protection in Rails?",
    "options": {
      "A": "A method to prevent SQL injection",
      "B": "A security feature that prevents malicious sites from making requests on behalf of a logged-in user",
      "C": "A way to hide images from other websites",
      "D": "A password encryption algorithm"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'rails generate scaffold' command do?",
    "options": {
      "A": "Creates only the database migration",
      "B": "Generates a full set of Model, View, and Controller files, along with migrations and tests for a resource",
      "C": "Deletes the entire project",
      "D": "Builds the production environment"
    },
    "answer": "B"
  },
  {
    "question": "Which tool is used in Rails to process and bundle JavaScript and CSS assets?",
    "options": {
      "A": "Asset Pipeline (Sprockets/Propshaft)",
      "B": "Active Storage",
      "C": "Action Cable",
      "D": "Rails API"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Action View' helper 'form_with' used for?",
    "options": {
      "A": "To create a connection to the database",
      "B": "To generate HTML forms for models or URLs that handle data submission",
      "C": "To create a table in the view",
      "D": "To send emails"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Strong Parameters' in Rails controllers?",
    "options": {
      "A": "To make the database faster",
      "B": "To protect against mass-assignment vulnerabilities by explicitly permitting which attributes can be updated",
      "C": "To encrypt user input",
      "D": "To validate the length of a string"
    },
    "answer": "B"
  },
  {
    "question": "Which Active Record method returns the first record found or nil if nothing is found?",
    "options": {
      "A": "find",
      "B": "find_by",
      "C": "where",
      "D": "select"
    },
    "answer": "B"
  },
  {
    "question": "What is an Active Record 'Callback'?",
    "options": {
      "A": "A method that calls a customer back",
      "B": "A hook into the lifecycle of an Active Record object that allows you to trigger logic before or after state changes",
      "C": "A way to restart the Rails server",
      "D": "A database recovery tool"
    },
    "answer": "B"
  },
  {
    "question": "Which callback is triggered specifically after a record is successfully saved to the database for the first time?",
    "options": {
      "A": "after_save",
      "B": "after_create",
      "C": "before_validation",
      "D": "after_commit"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of an 'Active Record Scope'?",
    "options": {
      "A": "To view the database in 3D",
      "B": "To define commonly-used queries as method calls on the model that can be chained",
      "C": "To set the app's global variables",
      "D": "To manage user permissions"
    },
    "answer": "B"
  },
  {
    "question": "Which Rails framework is used to send and receive emails?",
    "options": {
      "A": "Action Cable",
      "B": "Action Mailer",
      "C": "Action Text",
      "D": "Active Storage"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Polymorphic Association' in Rails?",
    "options": {
      "A": "An association that has multiple names",
      "B": "An association that allows a model to belong to more than one other model on a single association",
      "C": "A database with many tables",
      "D": "A way to encrypt foreign keys"
    },
    "answer": "B"
  },
  {
    "question": "In Rails, what is 'N+1 Query Problem'?",
    "options": {
      "A": "A security vulnerability",
      "B": "A performance issue where the app makes one query to fetch parent records and N additional queries to fetch associated children",
      "C": "A type of syntax error",
      "D": "A database locking issue"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used to solve the N+1 query problem by pre-loading associated records?",
    "options": {
      "A": "join",
      "B": "includes",
      "C": "preload_all",
      "D": "select"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Active Storage'?",
    "options": {
      "A": "To store the database in the cloud",
      "B": "To facilitate uploading files to a cloud storage service like Amazon S3 and attaching them to Active Record objects",
      "C": "To cache HTML fragments",
      "D": "To manage server memory"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Action Cable' used for?",
    "options": {
      "A": "Connecting the server to a physical cable",
      "B": "Integrating WebSockets with the rest of the Rails application for real-time features",
      "C": "Speeding up database migrations",
      "D": "Managing background jobs"
    },
    "answer": "B"
  },
  {
    "question": "Which command is used to see all the defined routes in a Rails application?",
    "options": {
      "A": "rails routes",
      "B": "rails list:paths",
      "C": "rails show:urls",
      "D": "bundle exec paths"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Turbolinks' (now part of Hotwire/Turbo)?",
    "options": {
      "A": "A high-speed database engine",
      "B": "A technique to make navigating web applications faster by using JavaScript to replace the body of the page",
      "C": "A tool to compress Ruby files",
      "D": "A security scanner"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'params' hash in a Rails controller?",
    "options": {
      "A": "A list of database passwords",
      "B": "A container for all parameters sent with the HTTP request, including URL and form data",
      "C": "A type of background worker",
      "D": "A configuration for the mailer"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'flash' messages (flash[:notice], flash[:alert])?",
    "options": {
      "A": "To display fast animations",
      "B": "To pass temporary strings (like success or error messages) from one action to the next rendered view",
      "C": "To store user sessions permanently",
      "D": "To debug the console"
    },
    "answer": "B"
  },
  {
    "question": "In a Rails migration, what does 't.timestamps' generate?",
    "options": {
      "A": "A clock on the website",
      "B": "Two columns: created_at and updated_at",
      "C": "The current time in the logs",
      "D": "A backup of the table"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Database Seeding'?",
    "options": {
      "A": "Deleting the database to start fresh",
      "B": "Populating the database with initial data required for the app to function or for testing",
      "C": "Encrypting the database schema",
      "D": "Scaling the database to multiple servers"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Active Job' in Rails?",
    "options": {
      "A": "A job board for Ruby developers",
      "B": "A framework for declaring background jobs and making them run on various queuing backends",
      "C": "A way to monitor CPU usage",
      "D": "A system for scheduling server reboots"
    },
    "answer": "B"
  },
  {
    "question": "Which gem is the default testing framework included with a new Rails installation?",
    "options": {
      "A": "RSpec",
      "B": "Minitest",
      "C": "Cucumber",
      "D": "Jasmine"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Rack' in the context of Ruby web applications?",
    "options": {
      "A": "A physical server shelf",
      "B": "A modular interface between web servers and web frameworks like Rails",
      "C": "A type of database indexing",
      "D": "A tool for code obfuscation"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Asset Pipeline' digest (fingerprinting)?",
    "options": {
      "A": "Checking the user's fingerprint for security",
      "B": "A technique that appends a unique string to asset filenames to help with cache busting",
      "C": "Compressing images into zip files",
      "D": "A way to identify the developer"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Partial Rendering'?",
    "options": {
      "A": "Only showing half of the webpage",
      "B": "Breaking views into smaller, reusable files that can be rendered within other views",
      "C": "Rendering the page slowly",
      "D": "Hiding the view from the controller"
    },
    "answer": "B"
  },
  {
    "question": "In Rails, what is a 'Concern'?",
    "options": {
      "A": "A bug report from a user",
      "B": "A module used to encapsulate and share code across multiple models or controllers",
      "C": "A security warning",
      "D": "A type of database constraint"
    },
    "answer": "B"
  },
  {
    "question": "Which Rails feature allows you to use 'plain text' in your database and automatically convert it to HTML (e.g., for blog posts)?",
    "options": {
      "A": "Action View",
      "B": "Action Text (Trix)",
      "C": "Active Record Base",
      "D": "Active Support"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Spring' in Rails?",
    "options": {
      "A": "A CSS animation library",
      "B": "A Rails application preloader that speeds up development by keeping your app running in the background",
      "C": "A database migration tool",
      "D": "The season Rails was released"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Content-Security-Policy' (CSP) in Rails?",
    "options": {
      "A": "A rule about what content is allowed in blog posts",
      "B": "A security header that helps prevent Cross-Site Scripting (XSS) and data injection attacks",
      "C": "A way to manage file uploads",
      "D": "A type of CSS framework"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'config.master.key'?",
    "options": {
      "A": "To open the office door",
      "B": "To decrypt the 'credentials.yml.enc' file which stores sensitive application secrets",
      "C": "To identify the main server",
      "D": "To grant admin access to the database"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Hotwire' in modern Rails?",
    "options": {
      "A": "A way to steal a car",
      "B": "A suite of tools (Turbo and Stimulus) for building fast, reactive web apps without writing much custom JavaScript",
      "C": "A high-speed server connection",
      "D": "A database optimization tool"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Stimulus' in the Hotwire ecosystem?",
    "options": {
      "A": "A type of database trigger",
      "B": "A modest JavaScript framework for the HTML you already have",
      "C": "A CSS preprocessor",
      "D": "A way to increase server speed"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'schema.rb' file?",
    "options": {
      "A": "A list of all the Ruby classes",
      "B": "The authoritative representation of the current state of your database schema",
      "C": "A backup of the production data",
      "D": "A log of all SQL queries"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used in a controller to verify that a user is logged in before allowing them to access an action?",
    "options": {
      "A": "verify_user",
      "B": "before_action",
      "C": "check_auth",
      "D": "guard_page"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Active Support' in Rails?",
    "options": {
      "A": "Customer service for Ruby developers",
      "B": "A collection of utility classes and Ruby standard library extensions used by Rails",
      "C": "A tool for fixing database errors",
      "D": "A type of technical support"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Russian Doll Caching' in Rails?",
    "options": {
      "A": "A security layer for international apps",
      "B": "A technique where fragment caches are nested inside each other, allowing the inner caches to be reused even if the outer cache expires",
      "C": "A database sharding method",
      "D": "A way to hide code from the browser"
    },
    "answer": "B"
  },
  {
    "question": "Which Rails method is used to perform a SQL 'INNER JOIN' between two tables?",
    "options": {
      "A": "includes",
      "B": "joins",
      "C": "preload",
      "D": "eager_load"
    },
    "answer": "B"
  },
  {
    "question": "What is the difference between 'joins' and 'includes' in Active Record?",
    "options": {
      "A": "They are identical",
      "B": "'joins' uses a single SQL JOIN to filter results, while 'includes' uses eager loading to prevent N+1 queries",
      "C": "'includes' is for CSS; 'joins' is for Ruby",
      "D": "'joins' is only for many-to-many relationships"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Eager Loading' mean in the context of Rails?",
    "options": {
      "A": "Loading the app before the user requests it",
      "B": "The process of loading the associated records of the objects returned by a find operation using as few queries as possible",
      "C": "A type of background job",
      "D": "A faster way to install gems"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Rack' middleware in a Rails application?",
    "options": {
      "A": "A physical server component",
      "B": "A minimal, modular, and adaptable interface for developing web applications in Ruby",
      "C": "A type of database indexing",
      "D": "A security firewall"
    },
    "answer": "B"
  },
  {
    "question": "Which Rails command is used to list all the middleware currently active in your application?",
    "options": {
      "A": "rails middleware",
      "B": "rails list:middleware",
      "C": "bundle exec rack",
      "D": "rails config:show"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Low-Level Caching' in Rails?",
    "options": {
      "A": "Caching only for old browsers",
      "B": "Manually caching specific values or query results using the Rails.cache.fetch method",
      "C": "Caching at the database hardware level",
      "D": "A way to reduce the file size of images"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Rails.cache.fetch'?",
    "options": {
      "A": "To download files from the internet",
      "B": "To read a value from the cache if it exists, or execute the block and write the result to the cache if it doesn't",
      "C": "To find a record in the database",
      "D": "To refresh the page"
    },
    "answer": "B"
  },
  {
    "question": "What is 'SQL Injection' and how does Rails protect against it?",
    "options": {
      "A": "A way to speed up the database",
      "B": "A vulnerability where attackers execute arbitrary SQL; Rails protects by using parameterized queries in Active Record",
      "C": "A tool to backup the database",
      "D": "A type of database encryption"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Cross-Site Scripting' (XSS) and how does Rails help prevent it in views?",
    "options": {
      "A": "A way to share scripts between sites",
      "B": "An attack that injects malicious scripts into web pages; Rails prevents this by automatically escaping HTML in templates",
      "C": "A method to compress JavaScript",
      "D": "A type of network firewall"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Action Text'?",
    "options": {
      "A": "A way to animate text in the UI",
      "B": "A framework that brings rich text content and editing (via the Trix editor) to Rails",
      "C": "A tool for translating text into different languages",
      "D": "A security feature for hiding text"
    },
    "answer": "B"
  },
  {
    "question": "Which gem is often used in Rails to handle user authentication (login/signup) easily?",
    "options": {
      "A": "AuthenticationKit",
      "B": "Devise",
      "C": "LoginManager",
      "D": "SecureUser"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Pundit' or 'CanCanCan' typically used for in a Rails app?",
    "options": {
      "A": "Database optimization",
      "B": "Authorization (defining what a logged-in user is allowed to do)",
      "C": "Sending emails in the background",
      "D": "Managing file uploads"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Database Transactions' in Active Record?",
    "options": {
      "A": "A way to pay for database hosting",
      "B": "A protective block that ensures a set of database operations either all succeed or all fail together (atomicity)",
      "C": "A log of all database changes",
      "D": "A type of database migration"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Sidekiq'?",
    "options": {
      "A": "A tool for pair programming",
      "B": "A background job processor for Ruby that uses Redis for storage",
      "C": "A testing framework",
      "D": "A type of Rails middleware"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Redis' and why is it commonly used with Rails?",
    "options": {
      "A": "A type of relational database like PostgreSQL",
      "B": "An in-memory data structure store used for caching and as a message broker for background jobs",
      "C": "A CSS framework",
      "D": "A security protocol for HTTPS"
    },
    "answer": "B"
  },
  {
    "question": "In a Rails migration, what does 'up' and 'down' (or 'change') represent?",
    "options": {
      "A": "The scroll direction of the page",
      "B": "The logic for applying a migration and the logic for reverting it",
      "C": "The order of database columns",
      "D": "The priority of the server"
    },
    "answer": "B"
  },
  {
    "question": "What is 'UUID' and why might you use it as a primary key in Rails?",
    "options": {
      "A": "A universal user ID for social media",
      "B": "A 128-bit number used to uniquely identify information, preferred for security and decentralized systems over incremental IDs",
      "C": "A type of database password",
      "D": "A way to speed up the UI"
    },
    "answer": "B"
  },
  {
    "question": "What is 'HTTP Streaming' in Rails?",
    "options": {
      "A": "Watching movies in the browser",
      "B": "A way to send the HTML response in chunks, allowing the browser to start rendering the head/CSS while the body is still processing",
      "C": "A type of network error",
      "D": "A background job for large files"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Enumerable' in Ruby/Rails?",
    "options": {
      "A": "A list of all users",
      "B": "A module providing a large set of search, sort, and traversal methods for collections like Arrays and Hashes",
      "C": "A type of database index",
      "D": "A security scan of the code"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Scoping' in the context of URLs in routes.rb?",
    "options": {
      "A": "Searching for a specific URL",
      "B": "Nesting routes under a common path (e.g., /admin) without affecting the controller's namespace",
      "C": "A way to hide URLs from search engines",
      "D": "A type of database query"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Public' directory used for?",
    "options": {
      "A": "Sharing code with the public",
      "B": "Static files (like 404 pages or robots.txt) that are served directly by the web server without hitting the Rails app",
      "C": "Storing private user photos",
      "D": "Managing the app's source code"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Action Cable' Identifier?",
    "options": {
      "A": "A person's name on a chat",
      "B": "The parameter used to differentiate between different WebSocket connections (e.g., current_user)",
      "C": "A type of physical cable",
      "D": "A security token for APIs"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Active Record' Store?",
    "options": {
      "A": "A physical shop for Ruby books",
      "B": "A simple way to save a hash of key-value pairs into a single database column",
      "C": "A tool to manage app assets",
      "D": "A type of cloud storage"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'log/' directory in a Rails project?",
    "options": {
      "A": "A place to keep wood for a fire",
      "B": "The directory where environment-specific runtime logs (development.log, production.log) are stored",
      "C": "A backup of the source code",
      "D": "A list of all the developers"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Asset Pipeline' Precompilation?",
    "options": {
      "A": "Compiling code before it is written",
      "B": "The process of preparing assets for production by merging, compressing, and adding digests for caching",
      "C": "A way to upload files to the server",
      "D": "A type of unit test"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Self-Join' in an Active Record model?",
    "options": {
      "A": "A model that is joined to itself (e.g., an Employee belonging to a Manager, who is also an Employee)",
      "B": "A model with only one column",
      "C": "A way to delete all records",
      "D": "A type of database locking"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Inverse_of' in an association?",
    "options": {
      "A": "A way to reverse the order of the data",
      "B": "An option that helps Rails optimize memory by informing it that two associations are two sides of the same relationship",
      "C": "A method to delete associated records",
      "D": "A security setting for foreign keys"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Counter Cache'?",
    "options": {
      "A": "A place to keep spare change",
      "B": "An optimization that stores the count of associated objects in a column on the parent table to avoid SQL COUNT queries",
      "C": "A tool to count lines of code",
      "D": "A way to limit the number of users"
    },
    "answer": "B"
  },
  {
    "question": "Final question of Batch 2: What is 'Action Dispatch'?",
    "options": {
      "A": "A way to ship physical products",
      "B": "The component of Rails that handles routing and parsing of HTTP requests",
      "C": "A background job processor",
      "D": "A tool for managing server memory"
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
    skill = "Ruby on Rails"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
