from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
    {
        "question": "What is Flask primarily categorized as in the Python web framework ecosystem?",
        "options": {
            "A": "Full-stack framework",
            "B": "Micro-framework",
            "C": "Database engine",
            "D": "Asynchronous-only framework",
            "E": "Frontend library"
        },
        "answer": "B"
    },
    {
        "question": "Which Python library is the foundation of Flask's request and response handling?",
        "options": {
            "A": "Django",
            "B": "Werkzeug",
            "C": "Requests",
            "D": "SQLAlchemy"
        },
        "answer": "B"
    },
    {
        "question": "Which template engine does Flask use by default?",
        "options": {
            "A": "Mako",
            "B": "Jinja2",
            "C": "Pug",
            "D": "Mustache"
        },
        "answer": "B"
    },
    {
        "question": "How do you define a basic route in Flask?",
        "options": {
            "A": "@app.route('/')",
            "B": "@app.path('/')",
            "C": "@route.app('/')",
            "D": "app.add_url('/')"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of the 'static' folder in a Flask project?",
        "options": {
            "A": "To store Python scripts",
            "B": "To store CSS, JavaScript, and images",
            "C": "To store database migrations",
            "D": "To store HTML templates"
        },
        "answer": "B"
    },
    {
        "question": "In which folder should you place your HTML files for Flask to find them automatically?",
        "options": {
            "A": "html",
            "B": "templates",
            "C": "views",
            "D": "pages"
        },
        "answer": "B"
    },
    {
        "question": "What is the correct way to run a Flask app named 'app.py' from the terminal in development mode?",
        "options": {
            "A": "python app.py",
            "B": "flask run",
            "C": "run flask",
            "D": "python -m flask start"
        },
        "answer": "B"
    },
    {
        "question": "Which Flask function is used to render an HTML template?",
        "options": {
            "A": "render()",
            "B": "render_template()",
            "C": "show_page()",
            "D": "display_html()"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'request' object in Flask represent?",
        "options": {
            "A": "A call to the database",
            "B": "The current HTTP request data sent by the client",
            "C": "The server's internal state",
            "D": "A list of all active users"
        },
        "answer": "B"
    },
    {
        "question": "How do you access URL parameters like '/user/<name>' inside a function?",
        "options": {
            "A": "request.args['name']",
            "B": "As an argument to the function: def profile(name):",
            "C": "request.form['name']",
            "D": "session['name']"
        },
        "answer": "B"
    },
    {
        "question": "Which HTTP methods does a Flask route handle by default?",
        "options": {
            "A": "GET only",
            "B": "GET and POST",
            "C": "POST only",
            "D": "All methods"
        },
        "answer": "A"
    },
    {
        "question": "How do you specify that a route should handle both GET and POST requests?",
        "options": {
            "A": "@app.route('/', methods=['GET', 'POST'])",
            "B": "@app.route('/', type='both')",
            "C": "@app.route('/', get_post=True)",
            "D": "@app.handle(['GET', 'POST'])"
        },
        "answer": "A"
    },
    {
        "question": "What is 'url_for()' used for?",
        "options": {
            "A": "To create a database URL",
            "B": "To dynamically generate a URL for a specific function",
            "C": "To download a file from the internet",
            "D": "To redirect to an external website"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to send the user to a different route?",
        "options": {
            "A": "move_to()",
            "B": "redirect()",
            "C": "forward()",
            "D": "jump()"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'flash()' in Flask?",
        "options": {
            "A": "To speed up the application",
            "B": "To show a one-time message to the user (e.g., success or error)",
            "C": "To clear the cache",
            "D": "To reload the page"
        },
        "answer": "B"
    },
    {
        "question": "How do you access form data sent via a POST request?",
        "options": {
            "A": "request.query",
            "B": "request.form",
            "C": "request.body",
            "D": "request.json"
        },
        "answer": "B"
    },
    {
        "question": "What is the default port for the Flask development server?",
        "options": {
            "A": "8080",
            "B": "5000",
            "C": "3000",
            "D": "8000"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'g' object in Flask stand for?",
        "options": {
            "A": "Global variables",
            "B": "A global namespace for holding data during a single application context (request)",
            "C": "Google analytics",
            "D": "General configuration"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Session' used for in Flask?",
        "options": {
            "A": "To store data permanently in a database",
            "B": "To store information specific to a user across multiple requests",
            "C": "To track server uptime",
            "D": "To style the webpage"
        },
        "answer": "B"
    },
    {
        "question": "Where are Flask sessions stored by default?",
        "options": {
            "A": "On the server's hard drive",
            "B": "In a cryptographically signed cookie on the client side",
            "C": "In a Redis database",
            "D": "In a global Python dictionary"
        },
        "answer": "B"
    },
    {
        "question": "What is required to be set in the app config to use sessions or flashing?",
        "options": {
            "A": "DEBUG_MODE",
            "B": "SECRET_KEY",
            "C": "SESSION_ID",
            "D": "PORT_NUMBER"
        },
        "answer": "B"
    },
    {
        "question": "How do you return a JSON response from a Flask route?",
        "options": {
            "A": "return json.dumps(data)",
            "B": "return jsonify(data)",
            "C": "return data.to_json()",
            "D": "return str(data)"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Blueprint' object in Flask used for?",
        "options": {
            "A": "To design the database schema",
            "B": "To organize an application into smaller, reusable components/modules",
            "C": "To create a CSS layout",
            "D": "To plan the project timeline"
        },
        "answer": "B"
    },
    {
        "question": "Which decorator is used to execute a function before every request?",
        "options": {
            "A": "@app.start_request",
            "B": "@app.before_request",
            "C": "@app.init",
            "D": "@app.pre_handle"
        },
        "answer": "B"
    },
    {
        "question": "Which Jinja2 syntax is used to output a variable in a template?",
        "options": {
            "A": "{% variable %}",
            "B": "{{ variable }}",
            "C": "[# variable #]",
            "D": "(( variable ))"
        },
        "answer": "B"
    },
    {
        "question": "Which Jinja2 syntax is used for control structures like 'if' or 'for'?",
        "options": {
            "A": "{{ if ... }}",
            "B": "{% if ... %}",
            "C": "[[ if ... ]]",
            "D": "<% if ... %>"
        },
        "answer": "B"
    },
    {
        "question": "How do you implement template inheritance in Jinja2?",
        "options": {
            "A": "Using {% include 'base.html' %}",
            "B": "Using {% extends 'base.html' %} and {% block %}",
            "C": "Using <import 'base.html'>",
            "D": "Copy-pasting the code"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Application Context' in Flask?",
        "options": {
            "A": "The folder where the app is located",
            "B": "The state where application-level variables like 'current_app' are available",
            "C": "The user's login session",
            "D": "The database connection string"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Request Context'?",
        "options": {
            "A": "The metadata of the Python file",
            "B": "The state where request-level variables like 'request' and 'session' are available",
            "C": "A type of database join",
            "D": "The browser's window size"
        },
        "answer": "B"
    },
    {
        "question": "How do you retrieve a value from the query string (e.g., /search?q=flask)?",
        "options": {
            "A": "request.form.get('q')",
            "B": "request.args.get('q')",
            "C": "request.values['q']",
            "D": "request.params['q']"
        },
        "answer": "B"
    },
    {
        "question": "Which Flask extension is the standard for database integration?",
        "options": {
            "A": "Flask-Database",
            "B": "Flask-SQLAlchemy",
            "C": "Flask-ORM",
            "D": "Flask-PyMongo"
        },
        "answer": "B"
    },
    {
        "question": "Which Flask extension is used to handle user login/logout and session management?",
        "options": {
            "A": "Flask-User",
            "B": "Flask-Login",
            "C": "Flask-Auth",
            "D": "Flask-Security"
        },
        "answer": "B"
    },
    {
        "question": "How do you abort a request with a 404 error manually?",
        "options": {
            "A": "return '404'",
            "B": "abort(404)",
            "C": "raise Error404()",
            "D": "stop(404)"
        },
        "answer": "B"
    },
    {
        "question": "Which decorator is used to handle specific HTTP errors (like 404 or 500) with a custom function?",
        "options": {
            "A": "@app.on_error",
            "B": "@app.errorhandler()",
            "C": "@app.catch()",
            "D": "@app.fail()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'WSGI'?",
        "options": {
            "A": "A Python web server",
            "B": "Web Server Gateway Interface—a standard for communication between web servers and Python web apps",
            "C": "A type of encryption",
            "D": "A frontend framework"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is a common production WSGI server for Flask?",
        "options": {
            "A": "Flask server",
            "B": "Gunicorn",
            "C": "Apache only",
            "D": "Python Interpreter"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'app.config.from_object()'?",
        "options": {
            "A": "To create a new object",
            "B": "To load configuration settings from a Python class or object",
            "C": "To connect to the database",
            "D": "To upload a file"
        },
        "answer": "B"
    },
    {
        "question": "How do you enable 'Debug Mode' in code?",
        "options": {
            "A": "app.debug = True",
            "B": "app.run(debug=True)",
            "C": "Both A and B",
            "D": "None"
        },
        "answer": "C"
    },
    {
        "question": "What is the security risk of leaving Debug Mode ON in production?",
        "options": {
            "A": "The app runs too slow",
            "B": "It allows remote code execution via the interactive debugger",
            "C": "It deletes the database",
            "D": "It changes the UI colors"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to install Flask?",
        "options": {
            "A": "get flask",
            "B": "pip install flask",
            "C": "install flask",
            "D": "python flask install"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Config.py' usually used for?",
        "options": {
            "A": "To write HTML",
            "B": "To store environment-specific variables like database URLs and API keys",
            "C": "To store logs",
            "D": "To define routes"
        },
        "answer": "B"
    },
    {
        "question": "How do you get the uploaded file object from a request?",
        "options": {
            "A": "request.data",
            "B": "request.files",
            "C": "request.upload",
            "D": "request.body"
        },
        "answer": "B"
    },
    {
        "question": "Which function ensures a filename is safe to store on the filesystem?",
        "options": {
            "A": "make_safe()",
            "B": "secure_filename()",
            "C": "clean_name()",
            "D": "validate_file()"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'current_app' object?",
        "options": {
            "A": "A list of users online",
            "B": "A proxy to the active Flask application instance",
            "C": "A backup of the app",
            "D": "The current page URL"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Request Hook'?",
        "options": {
            "A": "A way to hack the server",
            "B": "Functions that run at certain points during the request lifecycle (e.g., before or after a request)",
            "C": "A type of URL",
            "D": "A database index"
        },
        "answer": "B"
    },
    {
        "question": "Which decorator is used to run a function after the request is processed, but before the response is sent?",
        "options": {
            "A": "@app.after_request",
            "B": "@app.end",
            "C": "@app.post_handle",
            "D": "@app.finish"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of 'make_response()'?",
        "options": {
            "A": "To create a request",
            "B": "To wrap a return value in a response object to manually set headers or cookies",
            "C": "To restart the server",
            "D": "To show a success message"
        },
        "answer": "B"
    },
    {
        "question": "How do you set a cookie in Flask?",
        "options": {
            "A": "session['cookie'] = value",
            "B": "response.set_cookie('key', 'value')",
            "C": "request.cookies['key'] = value",
            "D": "flask.cookie('key', 'value')"
        },
        "answer": "B"
    },
    {
        "question": "Which command displays all routes defined in your Flask app?",
        "options": {
            "A": "flask routes",
            "B": "flask list-routes",
            "C": "flask show-urls",
            "D": "flask run --list"
        },
        "answer": "A"
    },
    {
        "question": "Final question of Batch 1: Who created Flask?",
        "options": {
            "A": "Guido van Rossum",
            "B": "Armin Ronacher",
            "C": "Mark Zuckerberg",
            "D": "Elon Musk"
        },
        "answer": "B"
    },
    {
    "question": "What is the primary purpose of a 'Blueprint' in a large Flask application?",
    "options": {
      "A": "To create a database backup",
      "B": "To organize the application into distinct modules or components",
      "C": "To generate a UI mock-up",
      "D": "To speed up the server's boot time"
    },
    "answer": "B"
  },
  {
    "question": "Which decorator is used in a Blueprint to define a route?",
    "options": {
      "A": "@app.route()",
      "B": "@blueprint_name.route()",
      "C": "@route.blueprint()",
      "D": "@mod.path()"
    },
    "answer": "B"
  },
  {
    "question": "How do you register a Blueprint named 'auth_bp' in the main application file?",
    "options": {
      "A": "app.include(auth_bp)",
      "B": "app.register_blueprint(auth_bp)",
      "C": "app.add_blueprint(auth_bp)",
      "D": "flask.register(auth_bp)"
    },
    "answer": "B"
  },
  {
    "question": "Which Flask extension is the industry standard for handling user authentication and session management?",
    "options": {
      "A": "Flask-Auth",
      "B": "Flask-Login",
      "C": "Flask-Security",
      "D": "Flask-JWT"
    },
    "answer": "B"
  },
  {
    "question": "Which method must a User model implement to work with Flask-Login?",
    "options": {
      "A": "get_id()",
      "B": "is_active",
      "C": "is_authenticated",
      "D": "All of the above"
    },
    "answer": "D"
  },
  {
    "question": "What is the purpose of the '@login_required' decorator?",
    "options": {
      "A": "To force a user to log out",
      "B": "To restrict access to a route to only authenticated users",
      "C": "To encrypt the login form",
      "D": "To save the user's password in a cookie"
    },
    "answer": "B"
  },
  {
    "question": "Which function is used by Flask-Login to log a user into the session?",
    "options": {
      "A": "session.login()",
      "B": "login_user()",
      "C": "user.authenticate()",
      "D": "auth.start()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'CORS' in the context of Flask APIs?",
    "options": {
      "A": "Centralized Object Routing System",
      "B": "Cross-Origin Resource Sharing",
      "C": "Core Object Relational Storage",
      "D": "Custom Origin Response System"
    },
    "answer": "B"
  },
  {
    "question": "Which extension is typically used to enable CORS in a Flask application?",
    "options": {
      "A": "Flask-Security",
      "B": "Flask-CORS",
      "C": "Flask-Cross",
      "D": "Flask-Shield"
    },
    "answer": "B"
  },
  {
    "question": "What is the default behavior of 'url_for' when using Blueprints?",
    "options": {
      "A": "url_for('function_name')",
      "B": "url_for('blueprint_name.function_name')",
      "C": "url_for('.function_name')",
      "D": "Both B and C"
    },
    "answer": "D"
  },
  {
    "question": "What is 'Werkzeug' in the context of Flask?",
    "options": {
      "A": "A template engine",
      "B": "A comprehensive WSGI web application library that Flask is built upon",
      "C": "A database migration tool",
      "D": "A frontend CSS framework"
    },
    "answer": "B"
  },
  {
    "question": "Which status code should a Flask API return when a resource is successfully created?",
    "options": {
      "A": "200",
      "B": "201",
      "C": "204",
      "D": "400"
    },
    "answer": "B"
  },
  {
    "question": "How do you handle a JSON body sent in a POST request to a Flask API?",
    "options": {
      "A": "request.form['data']",
      "B": "request.get_json()",
      "C": "request.json_data",
      "D": "json.load(request.data)"
    },
    "answer": "B"
  },
  {
    "question": "What is 'SQLAlchemy-Utils' used for?",
    "options": {
      "A": "To write faster SQL",
      "B": "To provide various helper types and functions for SQLAlchemy models (like ChoiceType or EmailType)",
      "C": "To delete the database",
      "D": "To manage server hardware"
    },
    "answer": "B"
  },
  {
    "question": "Which Flask extension is used to build REST APIs quickly with class-based views?",
    "options": {
      "A": "Flask-RESTful",
      "B": "Flask-API",
      "C": "Flask-RESTX",
      "D": "Both A and C"
    },
    "answer": "D"
  },
  {
    "question": "What is the purpose of 'flask.cli.with_appcontext'?",
    "options": {
      "A": "To style the command line",
      "B": "To ensure a custom CLI command has access to application variables like 'db'",
      "C": "To restart the application",
      "D": "To upload files"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Application Factor Pattern' in Flask?",
    "options": {
      "A": "A way to calculate server speed",
      "B": "A pattern where the application is created inside a function (create_app) for better testing and configuration",
      "C": "A database design",
      "D": "A security scan"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'user_loader' callback used for in Flask-Login?",
    "options": {
      "A": "To create a new user account",
      "B": "To reload the user object from the user ID stored in the session",
      "C": "To log out a user",
      "D": "To encrypt a password"
    },
    "answer": "B"
  },
  {
    "question": "Which library is commonly used with Flask for background task processing?",
    "options": {
      "A": "Flask-Background",
      "B": "Celery",
      "C": "Flask-Task",
      "D": "Threading"
    },
    "answer": "B"
  },
  {
    "question": "How do you protect a Flask-WTF form from CSRF attacks?",
    "options": {
      "A": "Manually checking the user's IP",
      "B": "Including {{ form.csrf_token }} in the HTML template",
      "C": "Encrypting the HTML file",
      "D": "Using a special browser plugin"
    },
    "answer": "B"
  },
  {
    "question": "What is the role of 'flask_bcrypt'?",
    "options": {
      "A": "To create database tables",
      "B": "To provide utilities for hashing and checking passwords securely",
      "C": "To handle URL routing",
      "D": "To render templates"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used to check if a plaintext password matches a hashed password in Flask-Bcrypt?",
    "options": {
      "A": "bcrypt.match()",
      "B": "bcrypt.check_password_hash()",
      "C": "bcrypt.verify()",
      "D": "bcrypt.validate()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Flask-Mail' used for?",
    "options": {
      "A": "To send the code via email",
      "B": "To send emails to users from a Flask application",
      "C": "To receive physical mail",
      "D": "To manage server logs"
    },
    "answer": "B"
  },
  {
    "question": "What is 'SQLAlchemy session.rollback()' used for?",
    "options": {
      "A": "To save the data twice",
      "B": "To undo changes in the current session if an error occurs",
      "C": "To restart the database",
      "D": "To delete a table"
    },
    "answer": "B"
  },
  {
    "question": "Which status code represents 'Unauthorized' access?",
    "options": {
      "A": "400",
      "B": "401",
      "C": "403",
      "D": "404"
    },
    "answer": "B"
  },
  {
    "question": "Which status code represents 'Forbidden' access (even with login)?",
    "options": {
      "A": "401",
      "B": "403",
      "C": "405",
      "D": "500"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Database Relationship backref'?",
    "options": {
      "A": "A way to delete data",
      "B": "A shortcut to define a reverse relationship from the target model back to the source",
      "C": "A backup tool",
      "D": "A security certificate"
    },
    "answer": "B"
  },
  {
    "question": "What is the difference between 'db.drop_all()' and 'db.create_all()'?",
    "options": {
      "A": "One is for NoSQL",
      "B": "drop_all deletes all tables; create_all creates tables based on models",
      "C": "They are the same",
      "D": "One is only for testing"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Flask-Migrate' built on top of?",
    "options": {
      "A": "Django Migrations",
      "B": "Alembic",
      "C": "SQLAlchemy Core",
      "D": "Git"
    },
    "answer": "B"
  },
  {
    "question": "How do you create a many-to-many relationship in Flask-SQLAlchemy?",
    "options": {
      "A": "Using a simple Foreign Key",
      "B": "Using an association table and the 'secondary' argument in db.relationship",
      "C": "Using a Python list",
      "D": "It is not possible"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Flask-Sitemap'?",
    "options": {
      "A": "A map for the office",
      "B": "An extension to automatically generate sitemaps for SEO",
      "C": "A database tool",
      "D": "A security scan"
    },
    "answer": "B"
  },
  {
    "question": "Which function allows you to get the next page the user was trying to visit before being redirected to login?",
    "options": {
      "A": "request.next",
      "B": "request.args.get('next')",
      "C": "session['next']",
      "D": "user.last_page"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Method Decorator' in Flask RESTful?",
    "options": {
      "A": "Styling the code",
      "B": "Applying specific decorators to the HTTP methods of a Resource class",
      "C": "A security attack",
      "D": "A performance bug"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Flask-Caching'?",
    "options": {
      "A": "To save the app state",
      "B": "To improve performance by storing the results of expensive operations or views",
      "C": "To clear the browser history",
      "D": "To encrypt data"
    },
    "answer": "B"
  },
  {
    "question": "What is '@app.template_filter()'?",
    "options": {
      "A": "A way to filter data in the DB",
      "B": "A decorator used to register a custom function as a Jinja2 filter",
      "C": "A security scan",
      "D": "A performance bug"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'request.headers'?",
    "options": {
      "A": "To see the developer's name",
      "B": "To access the HTTP headers sent by the client (e.g., User-Agent, Authorization)",
      "C": "To set the page title",
      "D": "To manage server hardware"
    },
    "answer": "B"
  },
  {
    "question": "How do you handle 'File Upload' size limits in Flask?",
    "options": {
      "A": "In the HTML template",
      "B": "By setting the 'MAX_CONTENT_LENGTH' configuration key",
      "C": "In the database",
      "D": "By restarting the server"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Signal' in Flask (using Blinker)?",
    "options": {
      "A": "A type of internet connection",
      "B": "A system to notify subscribers when specific events occur in the application",
      "C": "A security vulnerability",
      "D": "A performance report"
    },
    "answer": "B"
  },
  {
    "question": "Which status code represents 'Method Not Allowed'?",
    "options": {
      "A": "403",
      "B": "405",
      "C": "410",
      "D": "500"
    },
    "answer": "B"
  },
  {
    "question": "Final question: What is the primary advantage of using 'JSONify' over 'json.dumps'?",
    "options": {
      "A": "It is faster",
      "B": "It automatically sets the Content-Type header to application/json",
      "C": "It is safer",
      "D": "It works with mobile apps"
    },
    "answer": "B"
  },
  {
    "question": "When using the Application Factory pattern, how do you handle extensions like SQLAlchemy that require an 'app' instance?",
    "options": {
      "A": "Re-instantiate the extension in every file",
      "B": "Initialize the extension globally without an app, then call ext.init_app(app) inside the factory function",
      "C": "Extensions do not work with the factory pattern",
      "D": "Pass the app instance as a global variable"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'flask.cli.AppGroup'?",
    "options": {
      "A": "To group users in the UI",
      "B": "To create nested custom command-line interfaces for specific application modules",
      "C": "To manage server clusters",
      "D": "To group database tables"
    },
    "answer": "B"
  },
  {
    "question": "Which Flask extension is specifically designed to handle JSON Web Tokens (JWT) for stateless authentication?",
    "options": {
      "A": "Flask-Login",
      "B": "Flask-JWT-Extended",
      "C": "Flask-Secure-Token",
      "D": "Flask-OAuth"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Session Fixation' and how does Flask prevent it?",
    "options": {
      "A": "A bug where sessions never expire; Flask uses permanent sessions",
      "B": "An attack where an attacker sets a user's session ID; Flask-Login refreshes the session ID on login",
      "C": "A database error; Flask uses SQLAlchemy to fix it",
      "D": "A CSS issue; Flask uses Jinja2"
    },
    "answer": "B"
  },
  {
    "question": "Which HTTP header is typically used to send a JWT to a Flask API?",
    "options": {
      "A": "Set-Cookie",
      "B": "Authorization: Bearer <token>",
      "C": "X-API-Key",
      "D": "Content-Type"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'pytest-flask'?",
    "options": {
      "A": "To speed up the app",
      "B": "A pytest plugin that provides fixtures to simplify testing Flask applications",
      "C": "To convert Flask to a testing tool",
      "D": "To generate HTML test reports"
    },
    "answer": "B"
  },
  {
    "question": "How do you simulate a client request in a Flask unit test?",
    "options": {
      "A": "Using the browser",
      "B": "Using app.test_client()",
      "C": "Using the requests library directly",
      "D": "Restarting the server manually"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Context Preservation' in Flask testing?",
    "options": {
      "A": "Saving the database state",
      "B": "The ability to access request-bound variables (like 'request' or 'g') after a test request has finished",
      "C": "Keeping the browser open",
      "D": "Encrypting the test code"
    },
    "answer": "B"
  },
  {
    "question": "What is the role of 'HTTP Basic Auth' in Flask?",
    "options": {
      "A": "A styling theme",
      "B": "A simple authentication scheme built into the HTTP protocol, often handled via Flask-HTTPAuth",
      "C": "A database index",
      "D": "A frontend framework"
    },
    "answer": "B"
  },
  {
    "question": "Which status code should be returned if a JWT has expired?",
    "options": {
      "A": "200",
      "B": "401",
      "C": "403",
      "D": "500"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Database Pooling' and why is it used with Flask-SQLAlchemy?",
    "options": {
      "A": "Sharing data with other apps",
      "B": "Reusing a set of existing database connections to reduce the overhead of opening new ones for every request",
      "C": "Backing up the DB to a pool",
      "D": "Deleting old data"
    },
    "answer": "B"
  },
  {
    "question": "What is 'N+1 Query Problem' in SQLAlchemy?",
    "options": {
      "A": "A math error",
      "B": "A performance issue where related data is fetched using many small queries instead of one joined query",
      "C": "Adding one extra column",
      "D": "A security vulnerability"
    },
    "answer": "B"
  },
  {
    "question": "Which loading strategy in SQLAlchemy solves the N+1 problem by joining tables?",
    "options": {
      "A": "Lazy loading",
      "B": "Joined loading (joinedload)",
      "C": "Deferred loading",
      "D": "Random loading"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'flask-shell-ipython'?",
    "options": {
      "A": "To run Flask on a phone",
      "B": "To replace the standard 'flask shell' with a more powerful IPython interactive environment",
      "C": "To encrypt the terminal",
      "D": "To manage server logs"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Marshmallow' used for in Flask APIs?",
    "options": {
      "A": "Styling buttons",
      "B": "Object serialization and deserialization (converting complex types to JSON and vice-versa)",
      "C": "Caching responses",
      "D": "A type of database"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Flask-RESTful' RequestParser?",
    "options": {
      "A": "A tool to parse HTML",
      "B": "A way to define and validate input arguments for API endpoints",
      "C": "A database query engine",
      "D": "A CSS parser"
    },
    "answer": "B"
  },
  {
    "question": "How do you handle 'Large File Downloads' in Flask without consuming too much memory?",
    "options": {
      "A": "Reading the whole file into a string",
      "B": "Using a generator to stream the file in chunks with a Response object",
      "C": "Compressing the file into a ZIP",
      "D": "Using a global variable"
    },
    "answer": "B"
  },
  {
    "question": "What is 'ProxyFix' middleware used for in Flask?",
    "options": {
      "A": "To fix broken links",
      "B": "To correctly handle headers like X-Forwarded-For when Flask is behind a reverse proxy like Nginx",
      "C": "To encrypt the proxy",
      "D": "To speed up the network"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Flask-SocketIO' used for?",
    "options": {
      "A": "To connect to a printer",
      "B": "To enable real-time, bi-directional communication between the client and server (WebSockets)",
      "C": "To manage server hardware",
      "D": "To style the UI"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Request Throttling' and which extension handles it in Flask?",
    "options": {
      "A": "Flask-Login",
      "B": "Flask-Limiter",
      "C": "Flask-Speed",
      "D": "Flask-Throttle"
    },
    "answer": "B"
  },
  {
    "question": "How do you set the 'Content-Security-Policy' header in Flask?",
    "options": {
      "A": "In the HTML <head>",
      "B": "By modifying the response.headers dictionary in an @after_request hook or using Flask-Talisman",
      "C": "In the database",
      "D": "In the CSS file"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Flask-Talisman'?",
    "options": {
      "A": "A lucky charm for the code",
      "B": "An extension that handles common security headers (HTTPS, CSP, HSTS) for Flask apps",
      "C": "A performance report",
      "D": "A database tool"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Flask-Admin'?",
    "options": {
      "A": "A person who manages the server",
      "B": "An extension that provides a customizable administrative interface for managing database models",
      "C": "A security scan",
      "D": "A performance report"
    },
    "answer": "B"
  },
  {
    "question": "What is 'SQLAlchemy Hybrid Property'?",
    "options": {
      "A": "A property that is half SQL and half Python",
      "B": "A property that can be used both as a Python attribute and in a SQL query expression",
      "C": "A type of sharding",
      "D": "A security certificate"
    },
    "answer": "B"
  },
  {
    "question": "How do you prevent 'SQL Injection' in Flask?",
    "options": {
      "A": "By never using a database",
      "B": "By using SQLAlchemy's ORM or parameterized queries (avoiding raw f-string SQL)",
      "C": "By using a browser plugin",
      "D": "By naming variables 'safe'"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Flask-Seeder' used for?",
    "options": {
      "A": "Planting trees",
      "B": "Automatically populating the database with initial or mock data for development",
      "C": "A type of backup",
      "D": "A security scan"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Click' in the context of Flask?",
    "options": {
      "A": "A user clicking a button",
      "B": "The underlying library Flask uses for its Command Line Interface (CLI)",
      "C": "A database engine",
      "D": "A styling framework"
    },
    "answer": "B"
  },
  {
    "question": "How do you access the 'User-Agent' of a visitor?",
    "options": {
      "A": "request.agent",
      "B": "request.headers.get('User-Agent')",
      "C": "session['agent']",
      "D": "user.browser"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'app.app_context().push()' in scripts?",
    "options": {
      "A": "To start the web server",
      "B": "To manually create an application context so you can use features like 'db' outside of a web request",
      "C": "To update the app",
      "D": "To upload files"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Flask-Babel' used for?",
    "options": {
      "A": "To talk to databases",
      "B": "Internationalization (i18n) and localization (l10n) support for Flask apps",
      "C": "A type of unit test",
      "D": "A performance report"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Signal' safety in Flask?",
    "options": {
      "A": "Internet speed",
      "B": "Ensuring that signal handlers don't interrupt critical database transactions",
      "C": "A security scan",
      "D": "A performance bug"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Werkzeug Debugger' pin?",
    "options": {
      "A": "A physical pin on the server",
      "B": "A security feature that requires a numeric code to access the interactive debugger in the browser",
      "C": "A type of unit test",
      "D": "A performance report"
    },
    "answer": "B"
  },
  {
    "question": "How do you serve 'Static Files' from a custom directory?",
    "options": {
      "A": "In the CSS file",
      "B": "By setting 'static_folder' and 'static_url_path' when initializing the Flask object",
      "C": "In the database",
      "D": "By renaming the folder to 'static'"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Flask-Script'?",
    "options": {
      "A": "A legacy extension for managing CLI commands (now largely replaced by Flask's built-in CLI)",
      "B": "A tool to write Python",
      "C": "A database engine",
      "D": "A CSS framework"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Flask-OpenID'?",
    "options": {
      "A": "A person's ID",
      "B": "An extension to allow users to sign in using OpenID providers",
      "C": "A type of database",
      "D": "A security scanner"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Gevent' or 'Eventlet' in a Flask context?",
    "options": {
      "A": "A list of events",
      "B": "Asynchronous network libraries often used as worker types in Gunicorn to handle concurrent requests",
      "C": "A styling theme",
      "D": "A security firewall"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Pre-fork' worker model in Gunicorn?",
    "options": {
      "A": "Eating with a fork",
      "B": "The master process creates multiple child worker processes to handle requests simultaneously",
      "C": "A security scan",
      "D": "A database design"
    },
    "answer": "B"
  },
  {
    "question": "What is 'HTTP 429' status code?",
    "options": {
      "A": "Forbidden",
      "B": "Too Many Requests (Rate Limited)",
      "C": "Gone",
      "D": "Teapot"
    },
    "answer": "B"
  },
  {
    "question": "How do you access the raw request body data if it's not JSON or Form data?",
    "options": {
      "A": "request.raw",
      "B": "request.data",
      "C": "request.get_data()",
      "D": "Both B and C"
    },
    "answer": "D"
  },
  {
    "question": "What is 'Circular Dependency' in Flask Blueprints and how is it solved?",
    "options": {
      "A": "A circle in the code; use local imports inside functions or the factory pattern",
      "B": "A database error; use SQLite",
      "C": "A security scan result",
      "D": "A performance bug"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Flask-Uploads' used for?",
    "options": {
      "A": "To upload code to GitHub",
      "B": "A framework-flexible way to handle file uploads and categorize them (images, docs, etc.)",
      "C": "A database tool",
      "D": "A performance report"
    },
    "answer": "B"
  },
  {
    "question": "Which decorator is used to inject variables automatically into all templates?",
    "options": {
      "A": "@app.inject",
      "B": "@app.context_processor",
      "C": "@app.global_var",
      "D": "@app.pre_render"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Response Header' injection?",
    "options": {
      "A": "A security vulnerability",
      "B": "Manually adding or modifying HTTP headers in the response object",
      "C": "A type of sharding",
      "D": "A database index"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Flask-Cors' origins='*'?",
    "options": {
      "A": "Only the original server can access",
      "B": "Allows any domain to access the API (common for public APIs but risky for private ones)",
      "C": "A security scan",
      "D": "A performance report"
    },
    "answer": "B"
  },
  {
    "question": "What is 'SQLAlchemy Query Pagination'?",
    "options": {
      "A": "Counting the pages",
      "B": "Dividing a large result set into small 'pages' of records using .paginate()",
      "C": "A type of sharding",
      "D": "A security scan"
    },
    "answer": "B"
  },
  {
    "question": "What is 'flask.helpers.send_from_directory'?",
    "options": {
      "A": "Sending an email",
      "B": "A secure way to serve files from a specific folder to the user",
      "C": "A type of unit test",
      "D": "A security scanner"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Server-Side Sessions' (Flask-Session)?",
    "options": {
      "A": "Sessions on the client",
      "B": "An extension that stores session data on the server (Redis, Memcached) instead of client cookies",
      "C": "A type of sharding",
      "D": "A performance report"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'flask.wrappers.Request'?",
    "options": {
      "A": "To wrap the app in a box",
      "B": "The internal class used to represent the HTTP request object",
      "C": "A security scan",
      "D": "A database design"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Flask-Compress'?",
    "options": {
      "A": "Compiling code",
      "B": "An extension to automatically compress responses using Gzip",
      "C": "A type of sharding",
      "D": "A security scanner"
    },
    "answer": "B"
  },
  {
    "question": "Final question of Batch 3: Which command initializes a new migration directory?",
    "options": {
      "A": "flask db start",
      "B": "flask db init",
      "C": "flask db new",
      "D": "flask db create"
    },
    "answer": "B"
  },
  {
    "question": "Starting with Flask 2.0, how can you define a route to handle asynchronous code?",
    "options": {
      "A": "Using the @app.async_route decorator",
      "B": "By simply defining the view function with 'async def'",
      "C": "By setting app.async_mode = True",
      "D": "Flask 2.0 does not support async"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary benefit of using 'async def' in Flask routes?",
    "options": {
      "A": "It makes CPU-bound tasks faster",
      "B": "It allows the server to handle other requests while waiting for I/O-bound tasks (like API calls or DB queries)",
      "C": "It automatically encrypts the response",
      "D": "It removes the need for a database"
    },
    "answer": "B"
  },
  {
    "question": "Which WSGI server is commonly used to run Flask in a way that supports asynchronous workers?",
    "options": {
      "A": "Apache",
      "B": "Uvicorn (using an adapter) or Gunicorn with Gevent/Eventlet workers",
      "C": "The built-in development server",
      "D": "Windows Task Manager"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Zappa' in the Flask ecosystem?",
    "options": {
      "A": "A new template engine",
      "B": "A tool to deploy Flask applications as serverless functions on AWS Lambda",
      "C": "A database migration tool",
      "D": "A security firewall"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Frozen-Flask' extension used for?",
    "options": {
      "A": "To pause the application",
      "B": "To convert a Flask application into a set of static HTML files",
      "C": "To prevent code changes",
      "D": "To encrypt the source code"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Idempotency' in the context of RESTful APIs created with Flask?",
    "options": {
      "A": "The speed of the API",
      "B": "The property where making the same request multiple times has the same effect as making it once",
      "C": "A type of encryption",
      "D": "A database join"
    },
    "answer": "B"
  },
  {
    "question": "Which HTTP method is considered non-idempotent by design?",
    "options": {
      "A": "GET",
      "B": "PUT",
      "C": "POST",
      "D": "DELETE"
    },
    "answer": "C"
  },
  {
    "question": "What is 'Circuit Breaker' pattern and how can it be implemented with Flask?",
    "options": {
      "A": "A physical switch on the server",
      "B": "A pattern to stop requests to a failing downstream service, often implemented using the 'pybreaker' library",
      "C": "A type of unit test",
      "D": "A CSS layout"
    },
    "answer": "B"
  },
  {
    "question": "What is 'API Gateway' pattern in a Flask microservices setup?",
    "options": {
      "A": "A firewall for the API",
      "B": "A single entry point that routes requests to various microservices (e.g., using Kong or Nginx)",
      "C": "A type of database",
      "D": "A documentation tool"
    },
    "answer": "B"
  },
  {
    "question": "How do you handle 'Graceful Shutdown' in a Flask application running in a container?",
    "options": {
      "A": "By pulling the plug",
      "B": "By catching the SIGTERM signal and ensuring all cleanup tasks (like closing DB connections) are finished",
      "C": "Flask handles this automatically by default",
      "D": "By deleting the container"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Prometheus-Flask-Exporter' used for?",
    "options": {
      "A": "To export the code to GitHub",
      "B": "To provide metrics like request latency and count for monitoring in Prometheus",
      "C": "To style the UI",
      "D": "To manage user logins"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Structured Logging' in a Flask production environment?",
    "options": {
      "A": "Logging in a specific font",
      "B": "Outputting logs in machine-readable formats like JSON for easy ingestion into ELK or Splunk",
      "C": "Writing logs by hand",
      "D": "Only logging errors"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Flask-SocketIO' message acknowledgment?",
    "options": {
      "A": "The client saying 'thank you'",
      "B": "A feature where the receiver sends a callback to the sender to confirm a message was received",
      "C": "A type of encryption",
      "D": "A performance bug"
    },
    "answer": "B"
  },
  {
    "question": "How do you achieve 'High Availability' for a Flask app?",
    "options": {
      "A": "Using a faster CPU",
      "B": "Deploying multiple instances of the app behind a load balancer",
      "C": "Increasing the memory",
      "D": "Naming the app 'available'"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Database Sharding' in a Flask context?",
    "options": {
      "A": "Splitting the database into multiple smaller, faster pieces across different servers",
      "B": "Deleting the database",
      "C": "A type of unit test",
      "D": "A security certificate"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'Semantic Versioning' (SemVer) used for Flask extensions?",
    "options": {
      "A": "The color of the logo",
      "B": "A numbering system (MAJOR.MINOR.PATCH) to indicate the level of changes in a release",
      "C": "A type of encryption",
      "D": "A database design"
    },
    "answer": "B"
  },
  {
    "question": "What is 'CORS Preflight' request (OPTIONS method)?",
    "options": {
      "A": "A request sent before the actual request to check if the server allows the cross-origin call",
      "B": "A faster way to send data",
      "C": "A security attack",
      "D": "A type of backup"
    },
    "answer": "A"
  },
  {
    "question": "What is 'HSTS' (HTTP Strict Transport Security) in a Flask app?",
    "options": {
      "A": "A faster protocol",
      "B": "A security header that forces browsers to only use HTTPS to communicate with the site",
      "C": "A database index",
      "D": "A performance report"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Content-Type: application/merge-patch+json' used for in Flask APIs?",
    "options": {
      "A": "To merge two databases",
      "B": "To perform partial updates to a resource (PATCH) in a standardized way",
      "C": "To upload images",
      "D": "To delete data"
    },
    "answer": "B"
  },
  {
    "question": "Which status code should be returned if a client sends a request that is semantically incorrect?",
    "options": {
      "A": "400 Bad Request",
      "B": "422 Unprocessable Entity",
      "C": "500 Internal Error",
      "D": "404 Not Found"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Health Check' endpoint in a microservices architecture?",
    "options": {
      "A": "A page for doctors",
      "B": "An endpoint that returns the status of the service (UP/DOWN) for orchestration tools like Kubernetes",
      "C": "A security scan",
      "D": "A performance report"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Liveness' vs 'Readiness' probe in Kubernetes for a Flask app?",
    "options": {
      "A": "They are the same",
      "B": "Liveness checks if the app is running; Readiness checks if the app is ready to serve traffic",
      "C": "Readiness is for mobile; Liveness is for web",
      "D": "Liveness is for databases"
    },
    "answer": "B"
  },
  {
    "question": "How do you handle 'Configuration Secrets' (like DB passwords) in a production Flask app?",
    "options": {
      "A": "Hardcode them in the Python file",
      "B": "Use environment variables or a secret management service (like HashiCorp Vault or AWS Secrets Manager)",
      "C": "Commit them to GitHub",
      "D": "Save them in a public text file"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Gzip' middleware for Flask?",
    "options": {
      "A": "Compresses the source code",
      "B": "Compresses the HTTP response body to reduce bandwidth usage",
      "C": "A type of encryption",
      "D": "A security scanner"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Brotli' compression compared to Gzip?",
    "options": {
      "A": "It is slower",
      "B": "A more modern compression algorithm that often provides better compression ratios than Gzip",
      "C": "A database engine",
      "D": "A type of sharding"
    },
    "answer": "B"
  },
  {
    "question": "Which Flask extension is used for OpenID Connect (OIDC) and OAuth 2.0 integration?",
    "options": {
      "A": "Flask-Login",
      "B": "Authlib or Flask-OIDC",
      "C": "Flask-Auth",
      "D": "Flask-Token"
    },
    "answer": "B"
  },
  {
    "question": "What is 'SQLAlchemy-Continuum' used for?",
    "options": {
      "A": "To keep the server running",
      "B": "To provide versioning and auditing for your database models (keeping track of every change)",
      "C": "To delete old data",
      "D": "To manage server logs"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Blue-Green Deployment' for a Flask application?",
    "options": {
      "A": "A colorful UI theme",
      "B": "A deployment strategy where you have two identical environments and switch traffic to the new one (Green) once it is tested",
      "C": "A security attack",
      "D": "A type of unit test"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Canary Release'?",
    "options": {
      "A": "Releasing the app to birds",
      "B": "Rolling out a new version to a small subset of users before deploying it to everyone",
      "C": "A type of database backup",
      "D": "A security scan"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Flask-RESTX' compared to Flask-RESTful?",
    "options": {
      "A": "It is exactly the same",
      "B": "A fork that includes Swagger/OpenAPI documentation support by default",
      "C": "A legacy version",
      "D": "A frontend framework"
    },
    "answer": "B"
  },
  {
    "question": "What is 'gRPC' in a Python context?",
    "options": {
      "A": "A type of database",
      "B": "A high-performance Remote Procedure Call framework developed by Google that uses Protocol Buffers",
      "C": "A styling theme",
      "D": "A security firewall"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Protobuf' (Protocol Buffers)?",
    "options": {
      "A": "A type of exercise",
      "B": "A method of serializing structured data, more efficient and smaller than JSON/XML",
      "C": "A security protocol",
      "D": "A type of unit test"
    },
    "answer": "B"
  },
  {
    "question": "How do you handle 'CORS' with Blueprints?",
    "options": {
      "A": "CORS must be applied to the whole app only",
      "B": "CORS can be applied to specific Blueprints or even specific routes using the @cross_origin decorator",
      "C": "CORS is not needed for Blueprints",
      "D": "By restarting the server"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Flask-Security-Too'?",
    "options": {
      "A": "A bug in Flask-Security",
      "B": "A modern, maintained fork of the original Flask-Security extension for handling authentication and authorization",
      "C": "A type of sharding",
      "D": "A performance report"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Request Id' in microservices and how is it used in Flask?",
    "options": {
      "A": "A random number for fun",
      "B": "A unique identifier for a request that is passed between services to correlate logs and trace errors",
      "C": "A security scan",
      "D": "A database index"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Profiling' a Flask application performance?",
    "options": {
      "A": "Taking a photo of the code",
      "B": "Using tools (like Werkzeug Profiler or cProfile) to identify slow functions and bottlenecks in the code",
      "C": "Checking the user's profile",
      "D": "A security scan"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Memory Profiler' for Python?",
    "options": {
      "A": "A tool to measure server RAM",
      "B": "A tool to monitor memory usage of a Python program line-by-line",
      "C": "A type of unit test",
      "D": "A security scanner"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Rate Limiting' bypass?",
    "options": {
      "A": "Running faster",
      "B": "A security risk where an attacker finds a way to exceed rate limits (e.g., using different IPs)",
      "C": "A feature of the app",
      "D": "A performance bug"
    },
    "answer": "B"
  },
  {
    "question": "What is 'HTTP 204 No Content' commonly used for in APIs?",
    "options": {
      "A": "When an error occurs",
      "B": "A successful request where no body is returned (e.g., after a successful DELETE)",
      "C": "When the database is empty",
      "D": "A type of backup"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Flask-User'?",
    "options": {
      "A": "A person who uses Flask",
      "B": "An extension that adds ready-to-use user management features like registration, password reset, and email confirmation",
      "C": "A security scan",
      "D": "A performance report"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Pydantic' and can it be used with Flask?",
    "options": {
      "A": "A database; no",
      "B": "A data validation and settings management library; yes, often used for request/response validation in Flask APIs",
      "C": "A styling theme; yes",
      "D": "A performance tool; no"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Static Analysis' of Flask code?",
    "options": {
      "A": "Analyzing code while it's running",
      "B": "Analyzing code without executing it (e.g., using Flake8, MyPy, or Bandit) to find bugs and security issues",
      "C": "A type of sharding",
      "D": "A performance report"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Bandit' for Python?",
    "options": {
      "A": "A type of unit test",
      "B": "A tool designed to find common security issues in Python code",
      "C": "A database engine",
      "D": "A CSS framework"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Dependency Scanning' in CI/CD?",
    "options": {
      "A": "Checking if the developer is reliable",
      "B": "Automatically checking your project's dependencies for known security vulnerabilities",
      "C": "A type of sharding",
      "D": "A performance report"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Flask-CORS' resources={'/api/*': {'origins': '*'}}?",
    "options": {
      "A": "Allows any domain to access any route",
      "B": "Specifically allows cross-origin access only to routes starting with /api/",
      "C": "A performance bug",
      "D": "A security scan"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Thread-local Storage' in Flask?",
    "options": {
      "A": "Saving data to a local thread",
      "B": "The underlying mechanism Flask uses to ensure variables like 'request' are isolated to the specific thread handling a request",
      "C": "A type of sharding",
      "D": "A security scan"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Werkzeug LocalStack'?",
    "options": {
      "A": "A physical stack of servers",
      "B": "A class used to manage thread-local variables efficiently",
      "C": "A database engine",
      "D": "A security firewall"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Flask-SocketIO' namespace?",
    "options": {
      "A": "A name for the server",
      "B": "A way to multiplex multiple logical connections over a single physical WebSocket connection",
      "C": "A type of unit test",
      "D": "A performance report"
    },
    "answer": "B"
  },
  {
    "question": "Final question: What is the primary purpose of the 'flask' command-line interface?",
    "options": {
      "A": "To write code",
      "B": "To manage the application's lifecycle, including running the server and custom commands",
      "C": "To style the UI",
      "D": "To manage the database only"
    },
    "answer": "B"
  },
  {
    "question": "What is 'SignalR' equivalent in Flask?",
    "options": {
      "A": "Flask-Login",
      "B": "Flask-SocketIO",
      "C": "Flask-Mail",
      "D": "Flask-Admin"
    },
    "answer": "B"
  },
  {
    "question": "When scaling a Flask application horizontally across multiple containers, why is it critical to use a centralized session store like Redis (via Flask-Session)?",
    "options": {
      "A": "To increase the encryption strength of the session cookie",
      "B": "To prevent 'Session Loss' when a load balancer directs a user to a different server instance that doesn't have their local cookie data",
      "C": "To allow the app to run without a SECRET_KEY",
      "D": "To speed up Jinja2 template rendering"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary function of the 'Werkzeug' middle-layer in a Flask stack?",
    "options": {
      "A": "To serve as the primary database ORM",
      "B": "To provide the WSGI utility library that handles request/response objects and HTTP routing logic",
      "C": "To act as a CSS pre-processor",
      "D": "To manage asynchronous task queues"
    },
    "answer": "B"
  },
  {
    "question": "Which decorator would you use in a Flask Blueprint to apply a function to every request across the entire application, regardless of which blueprint handles it?",
    "options": {
      "A": "@blueprint.before_request",
        "B": "@blueprint.app_context_processor",
      "C": "@blueprint.app_errorhandler",
      "D": "@blueprint.before_app_request"
    },
    "answer": "D"
  },
  {
    "question": "In the context of 'Flask-SQLAlchemy', what is the danger of using 'db.drop_all()' in a production environment?",
    "options": {
      "A": "It permanently deletes all tables and data defined in the models without a recovery prompt",
      "B": "It only deletes the database logs",
      "C": "It renames the database to 'dropped'",
      "D": "It disconnects active users but keeps the data"
    },
    "answer": "A"
  },
  {
    "question": "How does Flask's 'Teardown_appcontext' differ from 'After_request'?",
    "options": {
      "A": "After_request only runs on success; Teardown_appcontext runs even if an exception occurred",
      "B": "Teardown_appcontext runs before the response is sent",
      "C": "After_request is only for Blueprints",
      "D": "There is no functional difference"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Application Dispatching' in Flask?",
    "options": {
      "A": "Sending the code to a client",
      "B": "The process of combining multiple Flask applications at the WSGI level",
      "C": "A type of database sharding",
      "D": "A security protocol"
    },
    "answer": "B"
  },
  {
    "question": "Which status code is most appropriate for a Flask API to return if a client's request is rate-limited?",
    "options": {
      "A": "401 Unauthorized",
      "B": "429 Too Many Requests",
      "C": "503 Service Unavailable",
      "D": "403 Forbidden"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Self' parameter in a Flask-RESTful Resource class method?",
    "options": {
      "A": "A reference to the active request",
      "B": "A reference to the specific instance of the Resource class",
      "C": "A global app object",
      "D": "A database connection"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Stream_with_context' used for in Flask?",
    "options": {
      "A": "To play video files",
      "B": "To keep the request context alive during a long-running generator-based response",
      "C": "To encrypt streaming data",
      "D": "To manage multiple user sessions"
    },
    "answer": "B"
  },
  {
    "question": "Final question: Why is 'Gunicorn' preferred over Flask’s built-in server for production?",
    "options": {
      "A": "Gunicorn is easier to debug",
      "B": "Gunicorn is a production-grade WSGI server that can handle concurrent requests via worker processes; the built-in server is not secure or scalable",
      "C": "Gunicorn supports HTML5",
      "D": "The built-in server cannot connect to SQL"
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
    skill = "Flask"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
