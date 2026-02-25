from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
  {
    "question": "Which method is used to initialize an Express application?",
    "options": {
      "A": "express.start()",
      "B": "express()",
      "C": "new Express()",
      "D": "express.init()"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary purpose of 'Middleware' in Express?",
    "options": {
      "A": "To design the database schema",
      "B": "To execute code between receiving a request and sending a response",
      "C": "To compile CSS files",
      "D": "To manage hardware drivers"
    },
    "answer": "B"
  },
  {
    "question": "In the function app.get('/', (req, res) => { ... }), what does 'res' represent?",
    "options": {
      "A": "The incoming Request object",
      "B": "The outgoing Response object",
      "C": "The Router object",
      "D": "The Resource object"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used to send a JSON response in Express?",
    "options": {
      "A": "res.sendJSON()",
      "B": "res.json()",
      "C": "res.writeJSON()",
      "D": "res.jsonify()"
    },
    "answer": "B"
  },
  {
    "question": "How do you define a route parameter in Express?",
    "options": {
      "A": "Using a question mark (?)",
      "B": "Using a colon (:)",
      "C": "Using curly braces ({})",
      "D": "Using a dollar sign ($)"
    },
    "answer": "B"
  },
  {
    "question": "Which command is typically used to install Express via npm?",
    "options": {
      "A": "npm add express",
      "B": "npm install express",
      "C": "npm get express",
      "D": "npm create express"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'next()' function do in middleware?",
    "options": {
      "A": "It ends the request-response cycle",
      "B": "It passes control to the next middleware function in the stack",
      "C": "It restarts the server",
      "D": "It sends a 404 error"
    },
    "answer": "B"
  },
  {
    "question": "Which built-in middleware is used to serve static files like images and CSS?",
    "options": {
      "A": "express.file()",
      "B": "express.static()",
      "C": "express.assets()",
      "D": "express.public()"
    },
    "answer": "B"
  },
  {
    "question": "How do you access the value of a route parameter named 'id'?",
    "options": {
      "A": "req.query.id",
      "B": "req.params.id",
      "C": "req.body.id",
      "D": "req.id"
    },
    "answer": "B"
  },
  {
    "question": "Which HTTP method is used to update an existing resource by replacing it?",
    "options": {
      "A": "POST",
      "B": "PUT",
      "C": "GET",
      "D": "DELETE"
    },
    "answer": "B"
  },
  {
    "question": "What is the correct way to handle a POST request at the '/submit' path?",
    "options": {
      "A": "app.post('/submit', callback)",
      "B": "app.get('/submit', callback)",
      "C": "app.request('/submit', callback)",
      "D": "app.put('/submit', callback)"
    },
    "answer": "A"
  },
  {
    "question": "Which package is commonly used as middleware to parse the body of incoming requests?",
    "options": {
      "A": "cookie-parser",
      "B": "body-parser",
      "C": "query-parser",
      "D": "request-parser"
    },
    "answer": "B"
  },
  {
    "question": "What does app.listen(3000) do?",
    "options": {
      "A": "It creates 3000 routes",
      "B": "It starts the server and listens for connections on port 3000",
      "C": "It limits the app to 3000 users",
      "D": "It deletes the port 3000"
    },
    "answer": "B"
  },
  {
    "question": "How do you set a custom HTTP status code for a response?",
    "options": {
      "A": "res.code(404)",
      "B": "res.status(404)",
      "C": "res.set(404)",
      "D": "res.http(404)"
    },
    "answer": "B"
  },
  {
    "question": "Which object in Express is used to create modular, mountable route handlers?",
    "options": {
      "A": "express.App",
      "B": "express.Router",
      "C": "express.Path",
      "D": "express.Module"
    },
    "answer": "B"
  },
  {
    "question": "Which function allows you to use a middleware for all incoming requests?",
    "options": {
      "A": "app.set()",
      "B": "app.use()",
      "C": "app.apply()",
      "D": "app.run()"
    },
    "answer": "B"
  },
  {
    "question": "In error-handling middleware, how many arguments are required in the callback function?",
    "options": {
      "A": "2",
      "B": "4",
      "C": "3",
      "D": "1"
    },
    "answer": "B"
  },
  {
    "question": "How do you retrieve a query string parameter 'user' from /search?user=John?",
    "options": {
      "A": "req.params.user",
      "B": "req.query.user",
      "C": "req.body.user",
      "D": "req.search.user"
    },
    "answer": "B"
  },
  {
    "question": "Which template engine is often used with Express to render dynamic HTML?",
    "options": {
      "A": "React",
      "B": "EJS",
      "C": "Redux",
      "D": "SASS"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of app.set('view engine', 'pug')?",
    "options": {
      "A": "To compile Pug into JavaScript",
      "B": "To specify the template engine to use for rendering views",
      "C": "To create a new view folder",
      "D": "To install the Pug package"
    },
    "answer": "B"
  },
  {
    "question": "Which property of the request object contains the cookies sent by the client (requires cookie-parser)?",
    "options": {
      "A": "req.headers.cookies",
      "B": "req.cookies",
      "C": "req.signedCookies",
      "D": "req.browser.cookies"
    },
    "answer": "B"
  },
  {
    "question": "How do you define error-handling middleware in Express?",
    "options": {
      "A": "app.use((req, res, next) => {})",
      "B": "app.use((err, req, res, next) => {})",
      "C": "app.error((err) => {})",
      "D": "app.use(err => {})"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used to redirect a client to a different URL?",
    "options": {
      "A": "res.move('/')",
      "B": "res.redirect('/')",
      "C": "res.location('/')",
      "D": "res.jump('/')"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'morgan' middleware in an Express app?",
    "options": {
      "A": "To hash passwords",
      "B": "To log HTTP requests to the console",
      "C": "To handle file uploads",
      "D": "To serve CSS files"
    },
    "answer": "B"
  },
  {
    "question": "Which middleware is commonly used to enable Cross-Origin Resource Sharing (CORS)?",
    "options": {
      "A": "express-cors",
      "B": "cors",
      "C": "cross-origin",
      "D": "helmet"
    },
    "answer": "B"
  },
  {
    "question": "How do you access JSON data sent in a POST request body (using express.json())?",
    "options": {
      "A": "req.query",
      "B": "req.body",
      "C": "req.json",
      "D": "req.data"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'helmet' package do for an Express application?",
    "options": {
      "A": "Speeds up the database",
      "B": "Sets various HTTP headers to improve security",
      "C": "Checks for syntax errors",
      "D": "Minifies JavaScript code"
    },
    "answer": "B"
  },
  {
    "question": "Which method on the response object is used to set a cookie?",
    "options": {
      "A": "res.setCookie()",
      "B": "res.cookie()",
      "C": "res.addCookie()",
      "D": "res.header('Cookie')"
    },
    "answer": "B"
  },
  {
    "question": "What is the default value of 'app.get('env')' if NODE_ENV is not set?",
    "options": {
      "A": "production",
      "B": "development",
      "C": "test",
      "D": "undefined"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used to remove a cookie from the client?",
    "options": {
      "A": "res.removeCookie()",
      "B": "res.clearCookie()",
      "C": "res.deleteCookie()",
      "D": "res.unset()"
    },
    "answer": "B"
  },
  {
    "question": "How do you serve a specific file (like an HTML file) using the response object?",
    "options": {
      "A": "res.file()",
      "B": "res.sendFile()",
      "C": "res.download()",
      "D": "res.render()"
    },
    "answer": "B"
  },
  {
    "question": "In Express 4.x, which middleware is required to parse URL-encoded bodies?",
    "options": {
      "A": "express.body()",
      "B": "express.urlencoded({ extended: true })",
      "C": "express.parse()",
      "D": "express.query()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'app.locals' used for?",
    "options": {
      "A": "Storing variables local to a specific request",
      "B": "Storing variables that are available to all templates rendered within the app",
      "C": "Managing local database connections",
      "D": "Tracking user IP addresses"
    },
    "answer": "B"
  },
  {
    "question": "Which HTTP method is best suited for deleting a resource?",
    "options": {
      "A": "GET",
      "B": "DELETE",
      "C": "POST",
      "D": "REMOVE"
    },
    "answer": "B"
  },
  {
    "question": "What does 'res.end()' do?",
    "options": {
      "A": "Restarts the server",
      "B": "Ends the response process without sending any data",
      "C": "Clears the browser cache",
      "D": "Deletes the request object"
    },
    "answer": "B"
  },
  {
    "question": "How do you mount a router onto a specific path, such as '/users'?",
    "options": {
      "A": "app.route('/users', userRouter)",
      "B": "app.use('/users', userRouter)",
      "C": "app.get('/users', userRouter)",
      "D": "app.mount('/users', userRouter)"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary use of 'res.locals'?",
    "options": {
      "A": "To store session IDs",
      "B": "To pass data to views that is only valid for the current request-response cycle",
      "C": "To store server configurations",
      "D": "To handle errors"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used to set the value of an Express application setting?",
    "options": {
      "A": "app.config()",
      "B": "app.set()",
      "C": "app.param()",
      "D": "app.put()"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'env' setting used for in Express?",
    "options": {
      "A": "To set the port number",
      "B": "To determine the current environment (e.g., development or production)",
      "C": "To enable encryption",
      "D": "To list all middleware"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used to render a view and send the rendered HTML to the client?",
    "options": {
      "A": "res.send()",
      "B": "res.render()",
      "C": "res.view()",
      "D": "res.display()"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'extended' option in express.urlencoded do?",
    "options": {
      "A": "Allows for larger payloads",
      "B": "Allows for parsing nested objects using the 'qs' library",
      "C": "Extends the timeout of the request",
      "D": "Enables HTTPS"
    },
    "answer": "B"
  },
  {
    "question": "Which object property is used to check if a request was made via AJAX?",
    "options": {
      "A": "req.ajax",
      "B": "req.xhr",
      "C": "req.isAjax",
      "D": "req.headers.ajax"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'app.all()'?",
    "options": {
      "A": "To delete all routes",
      "B": "To match a path regardless of the HTTP method used",
      "C": "To send a response to all users",
      "D": "To install all plugins"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used to send a file as an attachment, prompting the browser to download it?",
    "options": {
      "A": "res.sendFile()",
      "B": "res.download()",
      "C": "res.attachment()",
      "D": "res.save()"
    },
    "answer": "B"
  },
  {
    "question": "How do you get the value of an HTTP request header named 'Content-Type'?",
    "options": {
      "A": "req.headers('Content-Type')",
      "B": "req.get('Content-Type')",
      "C": "req.header.type",
      "D": "req.contentType"
    },
    "answer": "B"
  },
  {
    "question": "What is 'mountpath' property used for in a sub-app?",
    "options": {
      "A": "To find the file path of the app",
      "B": "To identify the path pattern on which a sub-app was mounted",
      "C": "To set the root directory",
      "D": "To define the database path"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used to define parameters for automatic data fetching or validation?",
    "options": {
      "A": "app.set()",
      "B": "app.param()",
      "C": "app.use()",
      "D": "app.get()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'strict routing' in Express?",
    "options": {
      "A": "A mode where routes must have a trailing slash",
      "B": "A setting where '/home' and '/home/' are treated as different routes",
      "C": "A mode where only HTTPS is allowed",
      "D": "A way to disable middleware"
    },
    "answer": "B"
  },
  {
    "question": "Which property indicates if a request is 'fresh' (based on ETag or Last-Modified)?",
    "options": {
      "A": "req.isNew",
      "B": "req.fresh",
      "C": "req.status",
      "D": "req.headers.fresh"
    },
    "answer": "B"
  },
  {
    "question": "How can you access the IP address of the requesting client?",
    "options": {
      "A": "req.ip",
      "B": "req.address",
      "C": "req.connection.ip",
      "D": "req.clientIp"
    },
    "answer": "A"
  },
  {
    "question": "What does 'app.disable('x-powered-by')' do?",
    "options": {
      "A": "Speeds up the app by 10%",
      "B": "Removes the 'X-Powered-By' header for security reasons",
      "C": "Turns off the server",
      "D": "Disables all plugins"
    },
    "answer": "B"
  },
  {
    "question": "Which method on the response object sets the HTTP 'Content-Type' header?",
    "options": {
      "A": "res.type()",
      "B": "res.contentType()",
      "C": "res.set('Content-Type')",
      "D": "Both A and C"
    },
    "answer": "D"
  },
  {
    "question": "What is the purpose of 'res.vary()'?",
    "options": {
      "A": "To change the response body",
      "B": "To add a field to the 'Vary' response header",
      "C": "To create a random response",
      "D": "To handle multiple file types"
    },
    "answer": "B"
  },
  {
    "question": "How do you check the 'Accepts' header of a request for a specific type?",
    "options": {
      "A": "req.check('html')",
      "B": "req.accepts('html')",
      "C": "req.is('html')",
      "D": "req.headers.accepts"
    },
    "answer": "B"
  },
  {
    "question": "What does 'res.format()' allow you to do?",
    "options": {
      "A": "Minify the HTML",
      "B": "Perform content negotiation on the 'Accept' HTTP header",
      "C": "Format the date",
      "D": "Convert JSON to XML"
    },
    "answer": "B"
  },
  {
    "question": "Which property returns the path part of the request URL?",
    "options": {
      "A": "req.url",
      "B": "req.path",
      "C": "req.originalUrl",
      "D": "req.basePath"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Case Sensitive Routing' setting?",
    "options": {
      "A": "Forces all URLs to be lowercase",
      "B": "Treats '/User' and '/user' as different routes",
      "C": "Treats all variables as case sensitive",
      "D": "A security feature for passwords"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'req.stale' property return?",
    "options": {
      "A": "True if the request is old",
      "B": "True if the 'req.fresh' property is false",
      "C": "True if the server needs a restart",
      "D": "True if the connection is closed"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used to set a response header?",
    "options": {
      "A": "res.header()",
      "B": "res.set()",
      "C": "res.put()",
      "D": "Both A and B"
    },
    "answer": "D"
  },
  {
    "question": "What is the purpose of 'app.path()'?",
    "options": {
      "A": "Returns the directory path of the app",
      "B": "Returns the canonical path of the app (string)",
      "C": "Creates a new folder",
      "D": "Sets the path for the database"
    },
    "answer": "B"
  },
  {
    "question": "Which middleware is built-in for parsing JSON bodies in Express 4.16+?",
    "options": {
      "A": "body-parser",
      "B": "express.json()",
      "C": "express.body()",
      "D": "json.parse()"
    },
    "answer": "B"
  },
  {
    "question": "How do you send a 201 Created status with a JSON body?",
    "options": {
      "A": "res.send(201, { data: 'ok' })",
      "B": "res.status(201).json({ data: 'ok' })",
      "C": "res.json(201, { data: 'ok' })",
      "D": "res.create({ data: 'ok' })"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Query Parser' setting used for?",
    "options": {
      "A": "To parse SQL queries",
      "B": "To configure the query string parsing library (e.g., 'simple' or 'extended')",
      "C": "To search the database",
      "D": "To filter the console logs"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used to determine if a request matches a specific content-type?",
    "options": {
      "A": "req.is()",
      "B": "req.accepts()",
      "C": "req.type()",
      "D": "req.check()"
    },
    "answer": "A"
  },
  {
    "question": "What does 'res.links()' do?",
    "options": {
      "A": "Lists all links in the HTML",
      "B": "Joins the 'Link' HTTP header field",
      "C": "Creates a hyperlink",
      "D": "Connects two routers"
    },
    "answer": "B"
  },
  {
    "question": "How do you define a route that matches a regular expression?",
    "options": {
      "A": "app.get('/user(id)?', callback)",
      "B": "app.get(/.*user$/, callback)",
      "C": "app.get(['/user', '/admin'], callback)",
      "D": "Both A and B"
    },
    "answer": "D"
  },
  {
    "question": "Which property of the request object returns the subdomains as an array?",
    "options": {
      "A": "req.domain",
      "B": "req.subdomains",
      "C": "req.host",
      "D": "req.url.sub"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'Trust Proxy' setting?",
    "options": {
      "A": "To allow all users to access the app",
      "B": "To trust the 'X-Forwarded-*' headers when the app is behind a proxy",
      "C": "To enable HTTPS",
      "D": "To whitelist IP addresses"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used to get the value of an app setting?",
    "options": {
      "A": "app.fetch()",
      "B": "app.get()",
      "C": "app.value()",
      "D": "app.config()"
    },
    "answer": "B"
  },
  {
    "question": "What happens if you don't call 'next()' or send a response in middleware?",
    "options": {
      "A": "The app crashes",
      "B": "The request is left hanging (the client waits until timeout)",
      "C": "The next middleware runs automatically",
      "D": "A 404 error is sent"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used in Mongoose to save a new document to the database?",
    "options": {
      "A": "document.create()",
      "B": "document.save()",
      "C": "document.push()",
      "D": "document.insert()"
    },
    "answer": "B"
  },
  {
    "question": "Where should a JSON Web Token (JWT) typically be stored on the client for maximum security against XSS?",
    "options": {
      "A": "LocalStorage",
      "B": "SessionStorage",
      "C": "An HttpOnly cookie",
      "D": "A global JavaScript variable"
    },
    "answer": "C"
  },
  {
    "question": "Which HTTP header is commonly used to send a JWT from the client to the Express server?",
    "options": {
      "A": "Authentication",
      "B": "Authorization",
      "C": "X-Token",
      "D": "Secret-Key"
    },
    "answer": "B"
  },
  {
    "question": "What is the standard prefix used in the Authorization header for JWTs?",
    "options": {
      "A": "Token",
      "B": "Bearer",
      "C": "JWT",
      "D": "Basic"
    },
    "answer": "B"
  },
  {
    "question": "Which package is the most popular middleware for handling file uploads in Express?",
    "options": {
      "A": "upload-file",
      "B": "multer",
      "C": "fs-extra",
      "D": "express-files"
    },
    "answer": "B"
  },
  {
    "question": "In Multer, which property of the request object contains the uploaded file details?",
    "options": {
      "A": "req.body.file",
      "B": "req.file",
      "C": "req.upload",
      "D": "req.attachment"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'express-session' middleware?",
    "options": {
      "A": "To hash passwords",
      "B": "To create and manage session data on the server side",
      "C": "To keep the server awake",
      "D": "To monitor CPU sessions"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used to clear all data from a server-side session?",
    "options": {
      "A": "req.session.clear()",
      "B": "req.session.destroy()",
      "C": "req.session.end()",
      "D": "res.clearSession()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'bcrypt' used for in an Express authentication flow?",
    "options": {
      "A": "To encrypt the database",
      "B": "To hash and salt passwords before storing them",
      "C": "To validate email addresses",
      "D": "To generate random usernames"
    },
    "answer": "B"
  },
  {
    "question": "Which Mongoose method finds a single document by its unique ID?",
    "options": {
      "A": "Model.getById()",
      "B": "Model.findById()",
      "C": "Model.selectOne()",
      "D": "Model.searchId()"
    },
    "answer": "B"
  },
  {
    "question": "What does 'passport.authenticate()' do in an Express route?",
    "options": {
      "A": "It creates a new user",
      "B": "It applies a specific authentication strategy (like Local or Google)",
      "C": "It sends an email",
      "D": "It generates a passport"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Query' object in a Mongoose find operation?",
    "options": {
      "A": "A plain JavaScript array",
      "B": "A thenable object that allows for chaining methods like .sort() and .limit()",
      "C": "An SQL string",
      "D": "A database index"
    },
    "answer": "B"
  },
  {
    "question": "Which HTTP status code is used when a user is not authenticated?",
    "options": {
      "A": "403 Forbidden",
      "B": "401 Unauthorized",
      "C": "400 Bad Request",
      "D": "404 Not Found"
    },
    "answer": "B"
  },
  {
    "question": "Which HTTP status code is used when a user is authenticated but lacks permission?",
    "options": {
      "A": "401 Unauthorized",
      "B": "403 Forbidden",
      "C": "405 Method Not Allowed",
      "D": "500 Server Error"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'dotenv' in an Express project?",
    "options": {
      "A": "To minify the code",
      "B": "To load environment variables from a .env file into process.env",
      "C": "To set the port number",
      "D": "To handle file system paths"
    },
    "answer": "B"
  },
  {
    "question": "How do you specify a sub-document schema in Mongoose?",
    "options": {
      "A": "By nesting an array of schemas within another schema",
      "B": "By using the 'extends' keyword",
      "C": "By creating a separate database",
      "D": "By using JSON.stringify"
    },
    "answer": "A"
  },
  {
    "question": "Which Mongoose middleware runs before a document is saved?",
    "options": {
      "A": "post('save')",
      "B": "pre('save')",
      "C": "during('save')",
      "D": "before('insert')"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'populate()' method used for in Mongoose?",
    "options": {
      "A": "To fill the database with fake data",
      "B": "To replace a reference ID with the actual document data from another collection",
      "C": "To update all fields at once",
      "D": "To increase the version number"
    },
    "answer": "B"
  },
  {
    "question": "Which package is used to validate and sanitize incoming request data in Express?",
    "options": {
      "A": "express-validator",
      "B": "express-sanitize",
      "C": "check-request",
      "D": "input-validator"
    },
    "answer": "A"
  },
  {
    "question": "What is 'CSRF' and which middleware helps prevent it in Express?",
    "options": {
      "A": "Cross-Site Request Forgery; 'csurf' middleware",
      "B": "Cross-Site Root Filtering; 'helmet' middleware",
      "C": "Client-Side Response Fail; 'cors' middleware",
      "D": "Common Service Resource File; 'morgan' middleware"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'EJS' tag used to output raw, unescaped data?",
    "options": {
      "A": "<%= %>",
      "B": "<%- %>",
      "C": "<%# %>",
      "D": "<%& %>"
    },
    "answer": "B"
  },
  {
    "question": "Which Mongoose option ensures that virtual properties are included when converting to JSON?",
    "options": {
      "A": "{ virtuals: true }",
      "B": "{ showVirtual: true }",
      "C": "{ includeHidden: true }",
      "D": "{ jsonVirtuals: true }"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Express-session' default storage location?",
    "options": {
      "A": "Redis",
      "B": "MemoryStore (Memory of the server)",
      "C": "MongoDB",
      "D": "The client's LocalStorage"
    },
    "answer": "B"
  },
  {
    "question": "Why is MemoryStore unsuitable for production sessions?",
    "options": {
      "A": "It is too slow",
      "B": "It will leak memory and data is lost if the server restarts or scales",
      "C": "It is encrypted by default",
      "D": "It doesn't support cookies"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Sequelize' in an Express ecosystem?",
    "options": {
      "A": "A logging tool",
      "B": "A Promise-based Node.js ORM for SQL databases (MySQL, Postgres, etc.)",
      "C": "A type of middleware",
      "D": "A deployment platform"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used in Sequelize to create a new record?",
    "options": {
      "A": "Model.save()",
      "B": "Model.create()",
      "C": "Model.insert()",
      "D": "Model.push()"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'res.locals' in the context of authentication?",
    "options": {
      "A": "To store the user's password",
      "B": "To make the authenticated user object available to all views in a single request",
      "C": "To store API keys",
      "D": "To redirect the user"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Partial' in EJS?",
    "options": {
      "A": "An incomplete route",
      "B": "A reusable template file (like a header or footer) included in other views",
      "C": "A type of variable",
      "D": "A database query"
    },
    "answer": "B"
  },
  {
    "question": "Which HTTP method is typically used to 'Login' (send credentials)?",
    "options": {
      "A": "GET",
      "B": "POST",
      "C": "PUT",
      "D": "HEAD"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'expiresIn' option do when signing a JWT?",
    "options": {
      "A": "It deletes the user account after a period",
      "B": "It sets the lifespan of the token before it becomes invalid",
      "C": "It limits the number of requests",
      "D": "It changes the token's color"
    },
    "answer": "B"
  },
  {
    "question": "Which property of a Mongoose schema allows you to prevent a field from being returned in queries by default?",
    "options": {
      "A": "hidden: true",
      "B": "select: false",
      "C": "private: true",
      "D": "omit: true"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'joi' package?",
    "options": {
      "A": "To handle file system tasks",
      "B": "To perform powerful schema description and data validation",
      "C": "To connect to Java applications",
      "D": "To log requests"
    },
    "answer": "B"
  },
  {
    "question": "In a REST API, what does 'HATEOAS' stand for?",
    "options": {
      "A": "High Availability Testing End Of All Systems",
      "B": "Hypermedia As The Engine Of Application State",
      "C": "Handling All Template Errors And Other Scenarios",
      "D": "Hypertext And Text Encryption Over All Servers"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Rate Limiting' and which Express middleware is often used for it?",
    "options": {
      "A": "Limiting the speed of the server; 'helmet'",
      "B": "Limiting the number of requests a client can make; 'express-rate-limit'",
      "C": "Limiting the file size of uploads; 'multer'",
      "D": "Limiting the number of database rows; 'mongoose'"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'cookie-session' middleware primarily used for?",
    "options": {
      "A": "Storing session data directly in the cookie on the client side",
      "B": "Managing sessions on Redis",
      "C": "Deleting cookies",
      "D": "Encrypting passwords"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to run an Express app using 'nodemon'?",
    "options": {
      "A": "run app.js",
      "B": "nodemon app.js",
      "C": "node start app.js",
      "D": "express nodemon"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'proxy-addr' package used for internally by Express?",
    "options": {
      "A": "To block proxies",
      "B": "To determine the IP address of the request, considering trusted proxies",
      "C": "To create a proxy server",
      "D": "To encrypt IP addresses"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'res.set('Content-Disposition', 'attachment')'?",
    "options": {
      "A": "To show the file in the browser",
      "B": "To force the browser to download the response as an attachment",
      "C": "To delete the file",
      "D": "To rename the file on the server"
    },
    "answer": "B"
  },
  {
    "question": "In Express, what does 'app.engine()' allow you to do?",
    "options": {
      "A": "Boost the server speed",
      "B": "Register a custom template engine for a specific file extension",
      "C": "Connect to a database engine",
      "D": "Change the Node.js version"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'method-override' middleware used for?",
    "options": {
      "A": "To change the name of functions",
      "B": "To support HTTP verbs such as PUT or DELETE in places where the client doesn't support them (like HTML forms)",
      "C": "To bypass authentication",
      "D": "To rename routes"
    },
    "answer": "B"
  },
  {
    "question": "Which status code should be returned if a REST API resource has been successfully deleted?",
    "options": {
      "A": "200 OK",
      "B": "204 No Content",
      "C": "201 Created",
      "D": "Both A and B are acceptable"
    },
    "answer": "D"
  },
  {
    "question": "What is 'Express-generator'?",
    "options": {
      "A": "A tool to create a project skeleton (boilerplate) for an Express app",
      "B": "An AI that writes Express code",
      "C": "A database migration tool",
      "D": "A test runner"
    },
    "answer": "A"
  },
  {
    "question": "Which method is used in Mongoose to update a document and return the modified version?",
    "options": {
      "A": "update()",
      "B": "findOneAndUpdate() with { new: true }",
      "C": "modify()",
      "D": "save()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Nginx' often used for in front of an Express application?",
    "options": {
      "A": "As a database",
      "B": "As a Reverse Proxy and Load Balancer",
      "C": "As a template engine",
      "D": "As a code editor"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'cluster' module in Node/Express?",
    "options": {
      "A": "To group users",
      "B": "To take advantage of multi-core systems by running multiple instances of the server",
      "C": "To group routes",
      "D": "To store data"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Bluebird' often used for in older Express/Node apps?",
    "options": {
      "A": "A logging tool",
      "B": "A high-performance Promise library",
      "C": "A CSS framework",
      "D": "A database"
    },
    "answer": "B"
  },
  {
    "question": "Which response method is used to set the 'Link' HTTP header field?",
    "options": {
      "A": "res.set()",
      "B": "res.links()",
      "C": "res.header()",
      "D": "res.append()"
    },
    "answer": "B"
  },
  {
    "question": "What is the function of 'compression' middleware?",
    "options": {
      "A": "To minify JavaScript",
      "B": "To compress response bodies using Gzip/Deflate to reduce payload size",
      "C": "To shrink image files",
      "D": "To reduce code length"
    },
    "answer": "B"
  },
  {
    "question": "In Mongoose, what is a 'Virtual'?",
    "options": {
      "A": "A field that is not stored in MongoDB but can be computed at runtime",
      "B": "A fake user",
      "C": "A remote database",
      "D": "A deprecated schema"
    },
    "answer": "A"
  },
  {
    "question": "What status code is sent when the server encounters an unexpected condition (generic error)?",
    "options": {
      "A": "404",
      "B": "500",
      "C": "400",
      "D": "502"
    },
    "answer": "B"
  },
  {
    "question": "Which library is most commonly used alongside Jest to test Express API endpoints?",
    "options": {
      "A": "Supertest",
      "B": "Axios",
      "C": "Mocha",
      "D": "Chai"
    },
    "answer": "A"
  },
  {
    "question": "What is the purpose of 'socket.io' when integrated with an Express server?",
    "options": {
      "A": "To handle file system operations",
      "B": "To enable real-time, bi-directional communication between web clients and servers",
      "C": "To encrypt the database",
      "D": "To manage CSS transitions"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used to broadcast a message to all connected clients except the sender in Socket.io?",
    "options": {
      "A": "socket.send()",
      "B": "socket.broadcast.emit()",
      "C": "io.emit()",
      "D": "socket.all.emit()"
    },
    "answer": "B"
  },
  {
    "question": "How do you 'export' an Express app instance for use in a test file?",
    "options": {
      "A": "export default app",
      "B": "module.exports = app",
      "C": "app.export()",
      "D": "return app"
    },
    "answer": "B"
  },
  {
    "question": "Which HTTP status code represents 'Permanent Redirect'?",
    "options": {
      "A": "302",
      "B": "301",
      "C": "307",
      "D": "308"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'PM2' process manager?",
    "options": {
      "A": "To edit code in the browser",
      "B": "To keep Node.js applications alive forever and reload them without downtime",
      "C": "To manage Git branches",
      "D": "To minify HTML"
    },
    "answer": "B"
  },
  {
    "question": "In a microservices architecture, how do Express services typically communicate over HTTP?",
    "options": {
      "A": "Using 'v-model'",
      "B": "Using REST APIs or gRPC",
      "C": "Via shared CSS files",
      "D": "Through the browser console"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Morgan' used for in a production Express environment?",
    "options": {
      "A": "Data encryption",
      "B": "Logging HTTP request details for monitoring and debugging",
      "C": "Serving static images",
      "D": "Database migration"
    },
    "answer": "B"
  },
  {
    "question": "Which command-line tool is used to monitor an Express app's resource usage in real-time?",
    "options": {
      "A": "npm start",
      "B": "pm2 monit",
      "C": "node -v",
      "D": "express-monitor"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Reverse Proxy' in the context of Express deployment?",
    "options": {
      "A": "A server that sits in front of the web server and forwards client requests to it (e.g., Nginx)",
      "B": "A tool that deletes code",
      "C": "A way to hide the database",
      "D": "A browser plugin"
    },
    "answer": "A"
  },
  {
    "question": "Which property of 'req' is used to check if a request was made over HTTPS?",
    "options": {
      "A": "req.isSecure",
      "B": "req.secure",
      "C": "req.protocol === 'https'",
      "D": "Both B and C"
    },
    "answer": "D"
  },
  {
    "question": "What is 'idempotency' in the context of PUT and DELETE methods?",
    "options": {
      "A": "The methods run faster each time",
      "B": "Multiple identical requests have the same effect as a single request",
      "C": "The methods cannot be used twice",
      "D": "The methods return random data"
    },
    "answer": "B"
  },
  {
    "question": "What does 'res.append()' do?",
    "options": {
      "A": "Adds data to the end of the body",
      "B": "Appends the specified value to the HTTP response header field",
      "C": "Appends a new route to the app",
      "D": "Adds a new user to the database"
    },
    "answer": "B"
  },
  {
    "question": "In Socket.io, how do you join a client to a specific 'room'?",
    "options": {
      "A": "socket.enter('room1')",
      "B": "socket.join('room1')",
      "C": "socket.room = 'room1'",
      "D": "io.to('room1')"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Graceful Shutdown' for an Express server?",
    "options": {
      "A": "Stopping the server immediately by pulling the plug",
      "B": "Finishing existing requests before closing the server connections",
      "C": "Deleting the log files",
      "D": "Logging out the admin"
    },
    "answer": "B"
  },
  {
    "question": "Which Mongoose method is used to remove a document and trigger middleware?",
    "options": {
      "A": "Model.delete()",
      "B": "document.remove()",
      "C": "Model.purge()",
      "D": "document.clear()"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'express-http-proxy'?",
    "options": {
      "A": "To block all proxies",
      "B": "To proxy a request to another host inside a middleware function",
      "C": "To speed up the internet",
      "D": "To handle file uploads"
    },
    "answer": "B"
  },
  {
    "question": "What status code is returned for 'Too Many Requests' (Rate Limiting)?",
    "options": {
      "A": "400",
      "B": "429",
      "C": "403",
      "D": "503"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'app.enable('trust proxy')' setting specifically affect?",
    "options": {
      "A": "It allows anyone to login",
      "B": "It allows Express to use the 'X-Forwarded-For' header to identify the client IP",
      "C": "It enables SSL by default",
      "D": "It trust all database connections"
    },
    "answer": "B"
  },
  {
    "question": "Which Socket.io event is triggered when a client disconnects?",
    "options": {
      "A": "exit",
      "B": "disconnect",
      "C": "close",
      "D": "end"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Blue-Green Deployment'?",
    "options": {
      "A": "Changing the app's color scheme",
      "B": "A technique that reduces downtime by running two identical production environments",
      "C": "Testing the app in a park",
      "D": "Using two different databases"
    },
    "answer": "B"
  },
  {
    "question": "In a Mongoose schema, what does 'index: true' do?",
    "options": {
      "A": "Adds the field to the home page",
      "B": "Creates a MongoDB index for that field to improve query performance",
      "C": "Counts the number of documents",
      "D": "Renames the collection"
    },
    "answer": "B"
  },
  {
    "question": "Which HTTP method is used by browsers for pre-flight CORS requests?",
    "options": {
      "A": "GET",
      "B": "OPTIONS",
      "C": "HEAD",
      "D": "TRACE"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Payload' in a JWT?",
    "options": {
      "A": "The secret key",
      "B": "The middle part of the token containing claims (user data)",
      "C": "The header specifying the algorithm",
      "D": "The digital signature"
    },
    "answer": "B"
  },
  {
    "question": "What is 'express.Router({ mergeParams: true })' used for?",
    "options": {
      "A": "To combine two routers",
      "B": "To preserve the req.params values from the parent router in the child router",
      "C": "To delete old parameters",
      "D": "To validate JSON"
    },
    "answer": "B"
  },
  {
    "question": "Which library is used to generate random IDs or UUIDs in Node/Express?",
    "options": {
      "A": "uuid",
      "B": "random-id",
      "C": "id-gen",
      "D": "unique"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Hydration' in Mongoose?",
    "options": {
      "A": "Cleaning up memory",
      "B": "The process of creating a Mongoose Document from a raw JSON object from MongoDB",
      "C": "Adding data to a view",
      "D": "Connecting to a cluster"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Content-Security-Policy' (CSP) header used for?",
    "options": {
      "A": "To speed up rendering",
      "B": "To prevent XSS and data injection attacks by restricting resource loading",
      "C": "To define the font family",
      "D": "To set the cookie lifespan"
    },
    "answer": "B"
  },
  {
    "question": "What does 'res.set('X-XSS-Protection', '1; mode=block')' do?",
    "options": {
      "A": "Blocks the user from the site",
      "B": "Enables the browser's Cross-Site Scripting filter",
      "C": "Encrypts the HTML",
      "D": "Disables JavaScript"
    },
    "answer": "B"
  },
  {
    "question": "In Mongoose, how do you handle validation errors in the catch block?",
    "options": {
      "A": "Check if err.name === 'ValidationError'",
      "B": "Check if err.code === 404",
      "C": "By restarting the server",
      "D": "Validation errors are not caught"
    },
    "answer": "A"
  },
  {
    "question": "Which method is used to send a '404 Not Found' response specifically for a view?",
    "options": {
      "A": "res.status(404).render('not-found')",
      "B": "res.render(404)",
      "C": "res.send(404)",
      "D": "app.error(404)"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Vertical Scaling'?",
    "options": {
      "A": "Adding more servers to the load balancer",
      "B": "Adding more CPU or RAM to an existing server instance",
      "C": "Rotating the server 90 degrees",
      "D": "Writing longer code"
    },
    "answer": "B"
  },
  {
    "question": "Which status code represents 'Conflict' (e.g., trying to register an existing email)?",
    "options": {
      "A": "400",
      "B": "409",
      "C": "403",
      "D": "422"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'package.json' field used to start the app on a cloud provider?",
    "options": {
      "A": "main",
      "B": "scripts: { 'start': 'node app.js' }",
      "C": "dependencies",
      "D": "engines"
    },
    "answer": "B"
  },
  {
    "question": "What does 'res.headersSent' property indicate?",
    "options": {
      "A": "The number of headers sent",
      "B": "A boolean indicating if the app has already sent HTTP headers for the response",
      "C": "The time headers were sent",
      "D": "If the headers were encrypted"
    },
    "answer": "B"
  },
  {
    "question": "In Express, what is 'Locals'?",
    "options": {
      "A": "Local people in the area",
      "B": "An object that stores data to be used by the view engine during rendering",
      "C": "A database on the computer",
      "D": "A type of middleware"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary benefit of using 'async/await' in Express routes over nested callbacks?",
    "options": {
      "A": "It is much faster",
      "B": "It prevents 'callback hell' and makes code more readable and easier to debug",
      "C": "It is required by Node.js",
      "D": "It enables multi-threading"
    },
    "answer": "B"
  },
  {
    "question": "Which method on a Sequelize model is used to find all records?",
    "options": {
      "A": "Model.findAll()",
      "B": "Model.select()",
      "C": "Model.getAll()",
      "D": "Model.fetch()"
    },
    "answer": "A"
  },
  {
    "question": "How do you apply a middleware to a specific HTTP method for a single route?",
    "options": {
      "A": "app.use('/route', middleware)",
      "B": "app.get('/route', middleware, controller)",
      "C": "app.all('/route', middleware)",
      "D": "middleware.apply(app)"
    },
    "answer": "B"
  },
  {
    "question": "What is 'ETag' in an Express response?",
    "options": {
      "A": "An electronic tag for shipping",
      "B": "An identifier for a specific version of a resource, used for web cache validation",
      "C": "A tag used in HTML",
      "D": "A database key"
    },
    "answer": "B"
  },
  {
    "question": "Which property of 'req' is an object containing the parsed request body?",
    "options": {
      "A": "req.query",
      "B": "req.body",
      "C": "req.params",
      "D": "req.payload"
    },
    "answer": "B"
  },
  {
    "question": "What is the default port for an Express app if not specified?",
    "options": {
      "A": "80",
      "B": "3000 (By convention, not by default; Express has no hardcoded default)",
      "C": "8080",
      "D": "There is no default port"
    },
    "answer": "D"
  },
  {
    "question": "What is 'res.status(200).send()' equivalent to?",
    "options": {
      "A": "res.json()",
      "B": "res.send()",
      "C": "res.end()",
      "D": "res.write()"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used to specify the directory where the view files are located?",
    "options": {
      "A": "app.set('views', path)",
      "B": "app.set('engine', path)",
      "C": "app.use('views', path)",
      "D": "app.get('views')"
    },
    "answer": "A"
  },
  {
    "question": "What is 'express-session' default 'resave' option recommended value?",
    "options": {
      "A": "true",
      "B": "false (to avoid unnecessary session updates)",
      "C": "null",
      "D": "depends on the database"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'morgan' log format 'dev'?",
    "options": {
      "A": "Detailed logs for production",
      "B": "Concise, colored output for development use",
      "C": "A log of all developer names",
      "D": "Encrypted log files"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Helmet' middleware used for in Express?",
    "options": {
      "A": "Protects the server from physical damage",
      "B": "Helps secure Express apps by setting various HTTP headers",
      "C": "Speeds up the app",
      "D": "Minifies JavaScript"
    },
    "answer": "B"
  },
  {
    "question": "What does 'next('route')' do?",
    "options": {
      "A": "Goes to the next website",
      "B": "Skips the remaining middleware functions in the current router stack",
      "C": "Throws an error",
      "D": "Restarts the request"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used to set multiple response header fields at once?",
    "options": {
      "A": "res.set({ field: value })",
      "B": "res.header({ field: value })",
      "C": "res.append({ field: value })",
      "D": "Both A and B"
    },
    "answer": "D"
  },
  {
    "question": "In 2026, which Express version is likely the stable standard for new projects?",
    "options": {
      "A": "v3",
      "B": "v5 (Stable)",
      "C": "v4",
      "D": "v6 (Beta)"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary benefit of using TypeScript with Express.js?",
    "options": {
      "A": "It makes the server run 2x faster",
      "B": "It provides static type checking, better autocompletion, and reduces runtime errors",
      "C": "It removes the need for middleware",
      "D": "It replaces the need for Node.js"
    },
    "answer": "B"
  },
  {
    "question": "Which package provides type definitions for Express when using TypeScript?",
    "options": {
      "A": "express-ts",
      "B": "@types/express",
      "C": "typescript-express",
      "D": "express.d.ts"
    },
    "answer": "B"
  },
  {
    "question": "How do you define a custom property on the 'Request' object in TypeScript (Module Augmentation)?",
    "options": {
      "A": "By editing the express source code in node_modules",
      "B": "By declaring a global namespace and extending the Express Request interface",
      "C": "By using 'any' for all requests",
      "D": "It is not possible in TypeScript"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Response Time' middleware used for?",
    "options": {
      "A": "To slow down the server",
      "B": "To record the time it takes for a request to be handled and send it in the 'X-Response-Time' header",
      "C": "To set the system clock",
      "D": "To limit user session time"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'cluster' module help achieve in a production Express app?",
    "options": {
      "A": "It groups users by location",
      "B": "It spawns multiple instances of the Node.js process to utilize multiple CPU cores",
      "C": "It minifies the source code",
      "D": "It encrypts the database"
    },
    "answer": "B"
  },
  {
    "question": "Which HTTP header is used to prevent the browser from 'sniffing' the MIME type away from the declared Content-Type?",
    "options": {
      "A": "X-Frame-Options",
      "B": "X-Content-Type-Options",
      "C": "Content-Security-Policy",
      "D": "Strict-Transport-Security"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'express-slow-down' middleware?",
    "options": {
      "A": "To stop the server",
      "B": "To slow down responses after a certain number of requests to discourage brute-force attacks",
      "C": "To handle large file uploads",
      "D": "To test the internet speed"
    },
    "answer": "B"
  },
  {
    "question": "How can you catch errors in an asynchronous Express route without using try/catch in every function?",
    "options": {
      "A": "It is impossible",
      "B": "By using a wrapper function that catches errors and passes them to next()",
      "C": "By using the 'error' keyword",
      "D": "By restarting the server"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Load Balancing' in the context of Express deployment?",
    "options": {
      "A": "Ensuring all files have the same size",
      "B": "Distributing incoming network traffic across multiple Express server instances",
      "C": "Charging users for data usage",
      "D": "Equating the number of GET and POST requests"
    },
    "answer": "B"
  },
  {
    "question": "Which setting in Express should be turned off to prevent revealing the server's technology stack?",
    "options": {
      "A": "env",
      "B": "x-powered-by",
      "C": "trust proxy",
      "D": "strict routing"
    },
    "answer": "B"
  },
  {
    "question": "In a Microservices architecture, what is an 'API Gateway'?",
    "options": {
      "A": "The database entry point",
      "B": "A single entry point that routes requests to various internal microservices",
      "C": "A firewall",
      "D": "The UI layer"
    },
    "answer": "B"
  },
  {
    "question": "What is 'ETag' used for in Express responses?",
    "options": {
      "A": "Electronic tracking",
      "B": "Client-side cache validation (checking if the content has changed)",
      "C": "Encrypting the body",
      "D": "Routing requests"
    },
    "answer": "B"
  },
  {
    "question": "Which package is used to validate that an environment variable exists before starting the app?",
    "options": {
      "A": "dotenv",
      "B": "envalid",
      "C": "validate-env",
      "D": "env-checker"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Hydration' in Mongoose when fetching data?",
    "options": {
      "A": "Clearing the cache",
      "B": "Converting a raw MongoDB BSON document into a Mongoose model instance with methods",
      "C": "Connecting to a database",
      "D": "Adding data to a view"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used to remove all event listeners from a Socket in Socket.io?",
    "options": {
      "A": "socket.clear()",
      "B": "socket.removeAllListeners()",
      "C": "socket.off()",
      "D": "socket.delete()"
    },
    "answer": "B"
  },
  {
    "question": "What is the role of 'Redis' in a scaled-out Socket.io environment?",
    "options": {
      "A": "As a primary database",
      "B": "As a Pub/Sub mechanism to sync messages across multiple server instances",
      "C": "As a CSS preprocessor",
      "D": "As a replacement for Express"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Memory Leak' in a Node/Express app?",
    "options": {
      "A": "The server running out of disk space",
      "B": "A failure to release unused memory, causing the app's RAM usage to grow until it crashes",
      "C": "Deleting the database",
      "D": "A slow internet connection"
    },
    "answer": "B"
  },
  {
    "question": "Which property of 'res' is used to check if the headers have already been sent to the client?",
    "options": {
      "A": "res.sent",
      "B": "res.headersSent",
      "C": "res.finished",
      "D": "res.isClosed"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'package-lock.json' file used for?",
    "options": {
      "A": "Locking the editor",
      "B": "Ensuring consistent dependency versions across different environments",
      "C": "Encrypting the project",
      "D": "Stopping the app"
    },
    "answer": "B"
  },
  {
    "question": "What does 'npm audit' do?",
    "options": {
      "A": "Checks the code for spelling errors",
      "B": "Scans the project dependencies for known security vulnerabilities",
      "C": "Checks if the developer is working",
      "D": "Counts the number of lines of code"
    },
    "answer": "B"
  },
  {
    "question": "In Mongoose, what is the 'discriminator' used for?",
    "options": {
      "A": "To delete users",
      "B": "A schema inheritance mechanism (creating multiple models with overlapping schemas)",
      "C": "To filter database results",
      "D": "To change the port"
    },
    "answer": "B"
  },
  {
    "question": "What is the benefit of using 'pino' or 'winston' over 'console.log' in production?",
    "options": {
      "A": "They are much faster and support structured logging (JSON)",
      "B": "They look prettier",
      "C": "They are required by Node.js",
      "D": "They fix bugs automatically"
    },
    "answer": "A"
  },
  {
    "question": "What does 'res.attachment('file.png')' do?",
    "options": {
      "A": "Displays the image in the browser",
      "B": "Sets the Content-Disposition header to 'attachment' with the given filename",
      "C": "Uploads a file to the server",
      "D": "Deletes the file"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Strict-Transport-Security' (HSTS) used for?",
    "options": {
      "A": "To speed up the network",
      "B": "To tell browsers that the site should only be accessed via HTTPS",
      "C": "To prevent SQL injection",
      "D": "To limit user login attempts"
    },
    "answer": "B"
  },
  {
    "question": "How do you define a route that handles all HTTP verbs at once?",
    "options": {
      "A": "app.get('*')",
      "B": "app.all('/path', callback)",
      "C": "app.use('/path', callback)",
      "D": "Both B and C"
    },
    "answer": "D"
  },
  {
    "question": "Which method is used to set the 'Content-Type' header automatically based on a file extension?",
    "options": {
      "A": "res.type('.html')",
      "B": "res.set('Content-Type')",
      "C": "res.format()",
      "D": "res.header()"
    },
    "answer": "A"
  },
  {
    "question": "What is the purpose of 'res.location('/login')'?",
    "options": {
      "A": "It redirects the user to /login",
      "B": "It only sets the 'Location' header but does not change the status or end the response",
      "C": "It finds the user's GPS coordinates",
      "D": "It deletes the cookie"
    },
    "answer": "B"
  },
  {
    "question": "In 2026, which feature of Express 5.0 is most notable for async handling?",
    "options": {
      "A": "Manual promise wrapping",
      "B": "Native support for returning Promises in route handlers and middleware",
      "C": "A built-in database",
      "D": "Removal of the 'next' function"
    },
    "answer": "B"
  },
  {
    "question": "What is 'vhost' middleware used for in Express?",
    "options": {
      "A": "Virtual hosting (running multiple domains/subdomains on the same IP)",
      "B": "Managing video hosts",
      "C": "Protecting the server from viruses",
      "D": "Speeding up the CPU"
    },
    "answer": "A"
  },
  {
    "question": "How do you check the current version of Express installed in your project?",
    "options": {
      "A": "express -v",
      "B": "npm list express",
      "C": "node -v",
      "D": "check-version"
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
    skill = "Express.js"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
