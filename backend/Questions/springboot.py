from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
    {
        "question": "What is the primary philosophy of Spring Boot?",
        "options": {
            "A": "Configuration over Convention",
            "B": "Convention over Configuration",
            "C": "Manual Dependency Management",
            "D": "XML-based setup only"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to mark the main class of a Spring Boot application?",
        "options": {
            "A": "@Configuration",
            "B": "@SpringBootApplication",
            "C": "@EnableAutoConfiguration",
            "D": "@ComponentScan"
        },
        "answer": "B"
    },
    {
        "question": "The @SpringBootApplication annotation is a combination of which three annotations?",
        "options": {
            "A": "@Component, @Service, @Repository",
            "B": "@Configuration, @EnableAutoConfiguration, @ComponentScan",
            "C": "@Controller, @ResponseBody, @Service",
            "D": "@Bean, @Inject, @Autowired"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Spring Boot Starters'?",
        "options": {
            "A": "To start the computer",
            "B": "To provide a set of convenient dependency descriptors to simplify Maven/Gradle configuration",
            "C": "To create a new project from scratch",
            "D": "To monitor the application health"
        },
        "answer": "B"
    },
    {
        "question": "Which starter dependency is required to build a RESTful web application?",
        "options": {
            "A": "spring-boot-starter-test",
            "B": "spring-boot-starter-web",
            "C": "spring-boot-starter-jdbc",
            "0": "spring-boot-starter-data-jpa"
        },
        "answer": "B"
    },
    {
        "question": "How does Spring Boot achieve 'Auto-configuration'?",
        "options": {
            "A": "By scanning the source code for bugs",
            "B": "By looking at the classpath dependencies and automatically configuring beans accordingly",
            "C": "By asking the developer for input during runtime",
            "D": "By connecting to the internet to download settings"
        },
        "answer": "B"
    },
    {
        "question": "Which embedded server is used by default in spring-boot-starter-web?",
        "options": {
            "A": "Jetty",
            "B": "Tomcat",
            "C": "Undertow",
            "D": "Glassfish"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'application.properties' file?",
        "options": {
            "A": "To write Java code",
            "B": "To externalize configuration like server port, database URL, and application names",
            "C": "To store user passwords in plain text",
            "D": "To define the project folder structure"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to inject dependencies into a Spring bean?",
        "options": {
            "A": "@Inject",
            "B": "@Autowired",
            "C": "@Resource",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Inversion of Control' (IoC) in Spring?",
        "options": {
            "A": "Controlling the hardware with code",
            "B": "A process where the framework manages the lifecycle and dependencies of objects instead of the developer",
            "C": "Turning the computer off after a crash",
            "D": "A type of security encryption"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Spring Bean'?",
        "options": {
            "A": "A physical vegetable",
            "B": "An object that is instantiated, assembled, and managed by the Spring IoC container",
            "C": "A type of database table",
            "D": "A specialized version of a JAR file"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to define a REST controller in Spring Boot?",
        "options": {
            "A": "@Controller",
            "B": "@RestController",
            "C": "@Service",
            "D": "@Component"
        },
        "answer": "B"
    },
    {
        "question": "What is the difference between @Controller and @RestController?",
        "options": {
            "A": "@RestController is older",
            "B": "@RestController is a combination of @Controller and @ResponseBody",
            "C": "@Controller only works with XML",
            "D": "There is no difference"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation maps an HTTP GET request to a specific handler method?",
        "options": {
            "A": "@PostMapping",
            "B": "@GetMapping",
            "C": "@RequestMapping(method = GET)",
            "D": "Both B and C"
        },
        "answer": "D"
    },
    {
        "question": "What is the purpose of the 'Spring Initializr' (start.spring.io)?",
        "options": {
            "A": "To compile the application",
            "B": "A web-based tool to bootstrap a new Spring Boot project with desired dependencies",
            "C": "To deploy the application to the cloud",
            "D": "To check for security vulnerabilities"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to run a Spring Boot application from the terminal using Maven?",
        "options": {
            "A": "mvn run",
            "B": "mvn spring-boot:run",
            "C": "java -jar start",
            "D": "spring run app"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Dependency Injection' (DI)?",
        "options": {
            "A": "A way to inject CSS into HTML",
            "B": "A design pattern used to implement IoC, where dependencies are 'injected' into an object",
            "C": "A manual way to link files",
            "D": "A security vulnerability"
        },
        "answer": "B"
    },
    {
        "question": "Which scope is the default for a Spring Bean?",
        "options": {
            "A": "Prototype",
            "B": "Singleton",
            "C": "Request",
            "D": "Session"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'Prototype' scope mean for a Spring Bean?",
        "options": {
            "A": "Only one instance is created",
            "B": "A new instance is created every time the bean is requested",
            "C": "The bean is only available during testing",
            "D": "The bean is deleted after one use"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used on a class to indicate it contains business logic?",
        "options": {
            "A": "@Repository",
            "B": "@Service",
            "C": "@Component",
            "D": "@Logic"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used on a class to indicate it interacts with the database (DAO layer)?",
        "options": {
            "A": "@Service",
            "B": "@Repository",
            "C": "@Database",
            "D": "@Controller"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Component Scanning' in Spring?",
        "options": {
            "A": "Scanning the hardware for components",
            "B": "The process of searching the classpath for classes annotated with @Component, @Service, etc., to register them as beans",
            "C": "A type of security scan",
            "D": "Deleting unused files"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to pass a value from a properties file into a Java variable?",
        "options": {
            "A": "@Inject",
            "B": "@Value",
            "C": "@Property",
            "D": "@Config"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Spring Boot DevTools'?",
        "options": {
            "A": "To write the code automatically",
            "B": "To provide features like automatic restart and LiveReload to improve the developer experience",
            "C": "To manage project dependencies",
            "D": "To monitor production servers"
        },
        "answer": "B"
    },
    {
        "question": "Which file is the project configuration file for a Maven-based Spring Boot project?",
        "options": {
            "A": "build.gradle",
            "B": "pom.xml",
            "C": "settings.xml",
            "D": "application.json"
        },
        "answer": "B"
    },
    {
        "question": "What does '@PathVariable' do in a Spring MVC controller?",
        "options": {
            "A": "Accesses a query parameter (?id=1)",
            "B": "Extracts values directly from the URL path (/users/{id})",
            "C": "Sets the path for the database",
            "D": "Validates the user's path"
        },
        "answer": "B"
    },
    {
        "question": "What does '@RequestParam' do?",
        "options": {
            "A": "Extracts values from the URL path",
            "B": "Accesses query parameters or form data from the request",
            "C": "Injects a service",
            "D": "Sets a cookie"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to bind the HTTP request body to a Java object?",
        "options": {
            "A": "@ResponseBody",
            "B": "@RequestBody",
            "C": "@Param",
            "D": "@Model"
        },
        "answer": "B"
    },
    {
        "question": "What does '@ResponseBody' indicate?",
        "options": {
            "A": "The method takes a body as input",
            "B": "The return value of the method should be bound to the web response body (converted to JSON/XML)",
            "C": "The method is private",
            "D": "The response should be encrypted"
        },
        "answer": "B"
    },
    {
        "question": "Which interface can be used to run code immediately after the Spring Boot application starts?",
        "options": {
            "A": "CommandLineRunner",
            "B": "ApplicationContext",
            "C": "BootRunner",
            "D": "StartInterface"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of 'Profiles' in Spring Boot?",
        "options": {
            "A": "To store user profile pictures",
            "B": "To provide a way to segregate parts of the application configuration and make it only available in certain environments (e.g., dev, prod)",
            "C": "To manage the developer's GitHub profile",
            "D": "To monitor CPU performance"
        },
        "answer": "B"
    },
    {
        "question": "How do you activate a specific profile called 'prod'?",
        "options": {
            "A": "set profile=prod",
            "B": "spring.profiles.active=prod",
            "C": "active_profile: prod",
            "D": "run prod"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Spring Boot Actuator' used for?",
        "options": {
            "A": "To write the business logic",
            "B": "To provide production-ready features like health checks, metrics, and auditing",
            "C": "To design the UI",
            "D": "To compile the project"
        },
        "answer": "B"
    },
    {
        "question": "Which Actuator endpoint is used to check the health of the application?",
        "options": {
            "A": "/metrics",
            "B": "/health",
            "C": "/info",
            "D": "/status"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Fat JAR' in Spring Boot?",
        "options": {
            "A": "A JAR file that is very large in size",
            "B": "An executable JAR file that contains the application code and all its dependencies, including the embedded server",
            "C": "A JAR file for image storage",
            "D": "A JAR file that requires external servers"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to handle exceptions globally in a Spring Boot application?",
        "options": {
            "A": "@ExceptionHandler",
            "B": "@ControllerAdvice",
            "C": "@GlobalError",
            "D": "@ErrorController"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used inside a @ControllerAdvice class to handle a specific exception?",
        "options": {
            "A": "@Catch",
            "B": "@ExceptionHandler",
            "C": "@OnError",
            "D": "@HandleError"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'DispatcherServlet'?",
        "options": {
            "A": "A physical server in the data center",
            "B": "The front controller that coordinates the whole HTTP request-handling process in Spring MVC",
            "C": "A database connection pool",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to enable scheduling in a Spring Boot application?",
        "options": {
            "A": "@Schedule",
            "B": "@EnableScheduling",
            "C": "@Timed",
            "D": "@Async"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to mark a method to be executed periodically?",
        "options": {
            "A": "@Periodic",
            "B": "@Scheduled",
            "C": "@Repeat",
            "D": "@Timer"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Lombok' often used for in Spring Boot projects?",
        "options": {
            "A": "To manage the database",
            "B": "To reduce boilerplate code like getters, setters, and constructors using annotations",
            "C": "To style the UI",
            "D": "To monitor network speed"
        },
        "answer": "B"
    },
    {
        "question": "Which Lombok annotation generates a constructor with one parameter for each field in the class?",
        "options": {
            "A": "@NoArgsConstructor",
            "B": "@AllArgsConstructor",
            "C": "@RequiredArgsConstructor",
            "D": "@Data"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Spring Data JPA'?",
        "options": {
            "A": "A specialized version of Java",
            "B": "A library that makes it easy to implement JPA-based repositories by reducing boilerplate code",
            "C": "A database engine",
            "D": "A security module"
        },
        "answer": "B"
    },
    {
        "question": "What is the default naming convention for Spring Boot properties in YAML?",
        "options": {
            "A": "camelCase",
            "B": "kebab-case",
            "C": "snake_case",
            "D": "PascalCase"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to inject a configuration class into the Spring container?",
        "options": {
            "A": "@Service",
            "B": "@Configuration",
            "C": "@Bean",
            "D": "@Component"
        },
        "answer": "B"
    },
    {
        "question": "What is the use of the '@Bean' annotation?",
        "options": {
            "A": "To mark a class as a service",
            "B": "To tell Spring that a method returns a bean that should be registered in the application context",
            "C": "To create a new database table",
            "D": "To inject a property value"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Spring Boot CLI'?",
        "options": {
            "A": "A cloud platform",
            "B": "A command-line tool that can be used to quickly prototype with Spring using Groovy scripts",
            "C": "A security scan tool",
            "D": "A database driver"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to mark a class as a component but without any specialized role?",
        "options": {
            "A": "@Service",
            "B": "@Component",
            "C": "@Repository",
            "D": "@Controller"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Banner' in Spring Boot?",
        "options": {
            "A": "An advertisement on the website",
            "B": "The ASCII art printed in the console during application startup",
            "C": "A security warning",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "Final question: What is the primary advantage of 'Fat JAR' deployment?",
        "options": {
            "A": "It is cheaper",
            "B": "It is highly portable and doesn't require pre-installed servers on the host machine",
            "C": "It is faster for developers",
            "D": "It replaces the database"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to ensure a method runs within a database transaction?",
        "options": {
            "A": "@Transactional",
            "B": "@Atomic",
            "C": "@Commit",
            "D": "@Begin"
        },
        "answer": "A"
    },
    {
        "question": "What is the default behavior of @Transactional if a RuntimeException occurs?",
        "options": {
            "A": "The transaction is committed anyway",
            "B": "The transaction is rolled back",
            "C": "The database is deleted",
            "D": "The application stops"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to define a custom JPQL query in a repository interface?",
        "options": {
            "A": "@SQL",
            "B": "@Query",
            "C": "@Select",
            "D": "@Native"
        },
        "answer": "B"
    },
    {
        "question": "How do you specify a native SQL query instead of JPQL in the @Query annotation?",
        "options": {
            "A": "Set nativeQuery = true",
            "B": "Use the prefix 'SQL:'",
            "C": "Use the @NativeQuery annotation",
            "D": "It is not possible"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of the 'mappedBy' attribute in a @OneToMany relationship?",
        "options": {
            "A": "To name the database table",
            "B": "To indicate the field in the child entity that owns the relationship",
            "C": "To encrypt the relationship",
            "D": "To sort the children"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to map a Many-to-Many relationship?",
        "options": {
            "A": "@ManyToMany",
            "B": "@JoinTable",
            "C": "Both A and B are typically used together",
            "D": "@MultiRelation"
        },
        "answer": "C"
    },
    {
        "question": "What is 'Dirty Checking' in Hibernate/JPA?",
        "options": {
            "A": "Checking for invalid characters in strings",
            "B": "The mechanism that automatically detects changes to an entity and syncs them with the database upon transaction commit",
            "C": "A security scan of the database",
            "D": "Deleting corrupted data"
        },
        "answer": "B"
    },
    {
        "question": "Which interface provides pagination and sorting capabilities in Spring Data?",
        "options": {
            "A": "CrudRepository",
            "B": "PagingAndSortingRepository",
            "C": "ListRepository",
            "D": "QueryRepository"
        },
        "answer": "B"
    },
    {
        "question": "Which class is used to pass pagination information to a repository method?",
        "options": {
            "A": "PageInfo",
            "B": "PageRequest",
            "C": "SortOrder",
            "D": "Limit"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'existsById()' method in JpaRepository return?",
        "options": {
            "A": "The object if found",
            "B": "A boolean value (true if the entity exists, false otherwise)",
            "C": "An Optional wrapper",
            "D": "An integer count"
        },
        "answer": "B"
    },
    {
        "question": "What is the role of the 'Persistence Context'?",
        "options": {
            "A": "A backup of the database",
            "B": "A first-level cache where all entities are managed during a transaction",
            "C": "A configuration file",
            "D": "A security layer"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to mark a method as a producer of a REST response (usually for non-RestController classes)?",
        "options": {
            "A": "@RequestBody",
            "B": "@ResponseBody",
            "C": "@ResponseModel",
            "D": "@JsonOutput"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Content Negotiation' in Spring Boot REST APIs?",
        "options": {
            "A": "Negotiating the price of the API",
            "B": "The process of determining which media type (JSON, XML) to return based on the 'Accept' header of the request",
            "C": "Encrypting the content",
            "D": "Changing the URL path"
        },
        "answer": "B"
    },
    {
        "question": "Which dependency is primarily responsible for JSON serialization/deserialization in Spring Boot?",
        "options": {
            "A": "GSON",
            "B": "Jackson",
            "C": "JSON-B",
            "D": "FastJSON"
        },
        "answer": "B"
    },
    {
        "question": "What does @ResponseStatus(HttpStatus.NOT_FOUND) do when placed on a custom exception?",
        "options": {
            "A": "Finds the error on Google",
            "B": "Automatically returns a 404 status code when that exception is thrown from a controller",
            "C": "Deletes the missing resource",
            "D": "Restarts the server"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'ResponseEntity' in a controller method?",
        "options": {
            "A": "To encrypt the response",
            "B": "To provide full control over the HTTP response, including headers, body, and status code",
            "C": "To redirect the user",
            "D": "To handle database errors"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to automatically populate 'created_at' and 'updated_at' fields?",
        "options": {
            "A": "@Timed",
            "B": "@EntityListeners(AuditingEntityListener.class)",
            "C": "@AutoTime",
            "D": "@Clock"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Open Session in View' (OSIV) pattern?",
        "options": {
            "A": "Keeping the database open all day",
            "B": "Keeping the database session open during the entire request to allow lazy loading in the view layer",
            "C": "A security vulnerability",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "Which property disables 'Open Session in View'?",
        "options": {
            "A": "spring.jpa.open-in-view=false",
            "B": "hibernate.session.close=true",
            "C": "jpa.osiv=disabled",
            "D": "spring.datasource.close-on-view=true"
        },
        "answer": "A"
    },
    {
        "question": "What is an 'Embedded' object in JPA?",
        "options": {
            "A": "A video inside a webpage",
            "B": "A Java object whose fields are mapped to the same table as the parent entity using @Embeddable",
            "C": "A database inside another database",
            "D": "A hidden field"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used on a class that will be 'Embedded' into another entity?",
        "options": {
            "A": "@Embedded",
            "B": "@Embeddable",
            "C": "@Component",
            "D": "@Entity"
        },
        "answer": "B"
    },
    {
        "question": "What is 'N+1 Select Problem'?",
        "options": {
            "A": "A math error in a loop",
            "B": "A performance issue where one query for a parent results in 'N' additional queries for its children",
            "C": "A primary key collision",
            "D": "A database version conflict"
        },
        "answer": "B"
    },
    {
        "question": "Which JPA feature is used to solve the N+1 problem?",
        "options": {
            "A": "Lazy Loading",
            "B": "Entity Graphs or JOIN FETCH queries",
            "C": "Caching",
            "D": "Indexing"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Optimistic Locking'?",
        "options": {
            "A": "Believing no errors will occur",
            "B": "A strategy to prevent data conflicts by checking a version field before updating a row",
            "C": "Locking the database for all users",
            "D": "A security password"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to implement Optimistic Locking?",
        "options": {
            "A": "@Lock",
            "B": "@Version",
            "C": "@Check",
            "D": "@Sequence"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Pessimistic Locking'?",
        "options": {
            "A": "Expecting the worst errors",
            "B": "Explicitly locking a database row during a transaction to prevent any other access",
            "C": "A type of unit test",
            "D": "A firewall setting"
        },
        "answer": "B"
    },
    {
        "question": "In a REST API, what does the 405 status code mean?",
        "options": {
            "A": "Resource not found",
            "B": "Method Not Allowed (e.g., trying to POST to a GET endpoint)",
            "C": "Server Error",
            "D": "Unauthorized"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Projection' in Spring Data JPA?",
        "options": {
            "A": "Predicting the future size of data",
            "B": "Retrieving only a subset of fields from an entity using interfaces or DTOs",
            "C": "Displaying data on a screen",
            "D": "A type of database join"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to specify a join column in a relationship?",
        "options": {
            "A": "@Column",
            "B": "@JoinColumn",
            "C": "@ForeignKey",
            "D": "@MapColumn"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 2: Why is it recommended to use DTOs (Data Transfer Objects) in REST controllers?",
        "options": {
            "A": "To make the code harder to read",
            "B": "To decouple the API contract from the internal database schema and improve security",
            "C": "Because Spring Boot requires them",
            "D": "To speed up the network"
        },
        "answer": "B"
    },
    {
        "question": "Which starter dependency is used to add security features to a Spring Boot application?",
        "options": {
            "A": "spring-boot-starter-auth",
            "B": "spring-boot-starter-security",
            "C": "spring-security-core",
            "D": "spring-boot-starter-lock"
        },
        "answer": "B"
    },
    {
        "question": "What is the default security behavior when 'spring-boot-starter-security' is added?",
        "options": {
            "A": "No security is applied",
            "B": "All endpoints are protected and require basic authentication",
            "C": "Only the /admin endpoint is protected",
            "D": "The application becomes read-only"
        },
        "answer": "B"
    },
    {
        "question": "Which class is commonly extended in Spring Security (up to version 2.6) to configure HTTP security?",
        "options": {
            "A": "SecurityAdapter",
            "B": "WebSecurityConfigurerAdapter",
            "C": "SecurityConfiguration",
            "D": "AuthManager"
        },
        "answer": "B"
    },
    {
        "question": "In Spring Security 5.7+ (Spring Boot 2.7/3.0+), how is security configured instead of extending an adapter?",
        "options": {
            "A": "Using XML files",
            "B": "By defining a SecurityFilterChain bean",
            "C": "Using properties only",
            "D": "Security is configured automatically by AI"
        },
        "answer": "B"
    },
    {
        "question": "Which interface is used to load user-specific data during authentication?",
        "options": {
            "A": "UserDetailsService",
            "B": "AuthenticationProvider",
            "C": "PrincipalExtractor",
            "D": "IdentityManager"
        },
        "answer": "A"
    },
    {
        "question": "What does the 'PasswordEncoder' bean do?",
        "options": {
            "A": "Encrypts the database",
            "B": "Provides a service for encoding and matching passwords securely (e.g., BCrypt)",
            "C": "Sets the user's password to a random string",
            "D": "Hides passwords in the UI"
        },
        "answer": "B"
    },
    {
        "question": "What is 'CSRF' (Cross-Site Request Forgery) protection?",
        "options": {
            "A": "A type of database backup",
            "B": "A security measure that prevents unauthorized commands from being transmitted from a user that the web app trusts",
            "C": "A firewall for the server",
            "D": "A performance optimization"
        },
        "answer": "B"
    },
    {
        "question": "Why is CSRF protection often disabled for Stateless REST APIs using JWT?",
        "options": {
            "A": "Because it makes the API slow",
            "B": "Because JWTs are usually stored in headers rather than cookies, making them immune to classic CSRF",
            "C": "Because REST APIs don't have users",
            "D": "It should never be disabled"
        },
        "answer": "B"
    },
    {
        "question": "What are the three parts of a JSON Web Token (JWT)?",
        "options": {
            "A": "User, Password, Key",
            "B": "Header, Payload, Signature",
            "C": "Id, Secret, Expiry",
            "D": "Version, Data, Hash"
        },
        "answer": "B"
    },
    {
        "question": "In which HTTP header is a JWT typically sent during an API request?",
        "options": {
            "A": "Authentication",
            "B": "Authorization",
            "C": "X-Token",
            "D": "Bearer"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Bearer' prefix used for in the Authorization header?",
        "options": {
            "A": "To name the server",
            "B": "To indicate the type of token being provided",
            "C": "To encrypt the request",
            "D": "To count the number of login attempts"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to restrict method access based on user roles (Method Security)?",
        "options": {
            "A": "@Secured",
            "B": "@PreAuthorize",
            "C": "@RolesAllowed",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "What is 'CORS' (Cross-Origin Resource Sharing)?",
        "options": {
            "A": "A database tool",
            "B": "A mechanism that allows a web page from one domain to access resources from a different domain",
            "C": "A type of Java class",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation can be used on a Controller to enable CORS for that specific controller?",
        "options": {
            "A": "@CORS",
            "B": "@CrossOrigin",
            "C": "@AllowOrigin",
            "D": "@SafeSource"
        },
        "answer": "B"
    },
    {
        "question": "What is 'OAuth2'?",
        "options": {
            "A": "A new version of Java",
            "B": "An industry-standard protocol for authorization (e.g., 'Login with Google')",
            "C": "A type of sharding",
            "D": "A database engine"
        },
        "answer": "B"
    },
    {
        "question": "What is the difference between Authentication and Authorization?",
        "options": {
            "A": "They are the same",
            "B": "Authentication is verifying who you are; Authorization is verifying what you are allowed to do",
            "C": "Authorization is for admins only",
            "D": "Authentication is for the database"
        },
        "answer": "B"
    },
    {
        "question": "Which filter in Spring Security is responsible for processing the 'basic' authentication header?",
        "options": {
            "A": "UsernamePasswordAuthenticationFilter",
            "B": "BasicAuthenticationFilter",
            "C": "JwtFilter",
            "D": "HeaderFilter"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'SecurityContextHolder'?",
        "options": {
            "A": "A physical vault for the server",
            "B": "A helper class that provides access to the current SecurityContext, which contains information about the authenticated user",
            "C": "A configuration file",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "Which method in a SecurityFilterChain bean is used to define which URLs require authentication?",
        "options": {
            "A": "authorizeRequests() / authorizeHttpRequests()",
            "B": "setAuth()",
            "C": "checkUrl()",
            "D": "secureAll()"
        },
        "answer": "A"
    },
    {
        "question": "What does 'permitAll()' do in security configuration?",
        "options": {
            "A": "Allows everyone to write code",
            "B": "Allows unauthenticated access to specific URL patterns (e.g., /login, /public)",
            "C": "Gives everyone admin rights",
            "D": "Disables the firewall"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Form Login' in Spring Security?",
        "options": {
            "A": "Logging in with a paper form",
            "B": "The default mechanism that provides a generated HTML login page for the user",
            "C": "A type of unit test",
            "D": "A database table for forms"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Salt' in password hashing?",
        "options": {
            "A": "A seasoning for the server room",
            "B": "Random data added to a password before hashing to protect against rainbow table attacks",
            "C": "A type of sharding",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to enable method-level security (e.g., @PreAuthorize)?",
        "options": {
            "A": "@EnableSecurity",
            "B": "@EnableGlobalMethodSecurity / @EnableMethodSecurity",
            "C": "@SecureMethods",
            "D": "@AuthRequired"
        },
        "answer": "B"
    },
    {
        "question": "What is 'OpenID Connect' (OIDC)?",
        "options": {
            "A": "A type of database",
            "B": "An identity layer on top of the OAuth 2.0 protocol",
            "C": "A browser plugin",
            "D": "A routing strategy"
        },
        "answer": "B"
    },
    {
        "question": "What is 'RBAC' (Role-Based Access Control)?",
        "options": {
            "A": "An authorization model where permissions are assigned to roles, which are then assigned to users",
            "B": "A type of sharding",
            "C": "A performance metric",
            "D": "A security certificate"
        },
        "answer": "A"
    },
    {
        "question": "In Spring Security, what is the 'Principal'?",
        "options": {
            "A": "The school director",
            "B": "The currently authenticated user",
            "C": "The main database table",
            "D": "The application's entry point"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Session Fixation' protection?",
        "options": {
            "A": "Fixing a broken session",
            "B": "A security feature that changes the session ID after a successful login to prevent session hijacking",
            "C": "A type of unit test",
            "D": "A performance test"
        },
        "answer": "B"
    },
    {
        "question": "Which Spring Security class is responsible for managing the actual authentication process?",
        "options": {
            "A": "SecurityManager",
            "B": "AuthenticationManager",
            "C": "LoginController",
            "D": "UserProvider"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Stateless' authentication?",
        "options": {
            "A": "Authentication without any rules",
            "B": "An approach (common with JWT) where the server does not store user session data; every request must contain credentials",
            "C": "Logging in without a password",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Social Login'?",
        "options": {
            "A": "Talking to other users",
            "B": "Allowing users to authenticate using their existing social media accounts via OAuth2",
            "C": "A type of unit test",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'BCryptPasswordEncoder'?",
        "options": {
            "A": "The default and recommended password encoder in Spring Security, which uses the BCrypt hashing function",
            "B": "A tool to encrypt files",
            "C": "A type of sharding",
            "D": "A security certificate"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Security Filter Chain'?",
        "options": {
            "A": "A chain of locks on the server",
            "B": "A sequence of filters that a request must pass through to be authenticated and authorized",
            "C": "A type of unit test",
            "D": "A database relation"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Remember-Me' authentication?",
        "options": {
            "A": "The server remembering the user's name",
            "B": "A feature that allows a user to stay logged in across browser sessions via a cookie",
            "C": "A security scan",
            "D": "A performance test"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'grantedAuthorities' in a UserDetails object?",
        "options": {
            "A": "The user's favorite permissions",
            "B": "A collection of roles or permissions assigned to the user",
            "C": "A list of database tables",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What does '.hasRole(\"ADMIN\")' check for internally in Spring Security?",
        "options": {
            "A": "The word 'ADMIN'",
            "B": "The authority 'ROLE_ADMIN' (adds the 'ROLE_' prefix automatically)",
            "C": "The user's age",
            "D": "The database admin table"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Authority' vs 'Role' in Spring Security?",
        "options": {
            "A": "They are the same",
            "B": "Authorities are individual permissions; Roles are groups of authorities (usually prefixed with ROLE_)",
            "C": "Roles are faster",
            "D": "Authorities are for admins only"
        },
        "answer": "B"
    },
    {
        "question": "Which Actuator endpoint provides security-related information about the app (if enabled)?",
        "options": {
            "A": "/health",
            "B": "/configprops",
            "C": "/env",
            "D": "/auditevents"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Brute Force' attack protection in Spring Security?",
        "options": {
            "A": "Stopping the server during an attack",
            "B": "Implementing features like account lockout after multiple failed login attempts",
            "C": "Using a stronger firewall",
            "D": "Encrypting the source code"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Security Header' configuration?",
        "options": {
            "A": "Writing code in the header",
            "B": "Configuring HTTP response headers like X-Content-Type-Options or HSTS to enhance browser security",
            "C": "Styling the website header",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "What is 'XSS' (Cross-Site Scripting)?",
        "options": {
            "A": "An attack where malicious scripts are injected into trusted websites",
            "B": "A type of sharding",
            "C": "A database query tool",
            "D": "A security certificate"
        },
        "answer": "A"
    },
    {
        "question": "What is 'SQL Injection'?",
        "options": {
            "A": "Injecting SQL into the user's brain",
            "B": "An attack where malicious SQL statements are inserted into entry fields for execution",
            "C": "A type of sharding",
            "D": "A performance test"
        },
        "answer": "B"
    },
    {
        "question": "How does Spring Data JPA help prevent SQL Injection?",
        "options": {
            "A": "By blocking all SQL",
            "B": "By using parameterized queries (PreparedStatements) internally",
            "C": "By encrypting the database",
            "D": "By requiring a password for queries"
        },
        "answer": "B"
    },
    {
        "question": "What is 'SSL/TLS' for Spring Boot?",
        "options": {
            "A": "To compress data",
            "B": "To encrypt the communication between the client and the server (HTTPS)",
            "C": "To speed up the network",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "Which property is used to set the server's SSL key store path?",
        "options": {
            "A": "server.ssl.key-store",
            "B": "ssl.path",
            "C": "security.ssl.store",
            "D": "server.key"
        },
        "answer": "A"
    },
    {
        "question": "What is 'HSTS' (HTTP Strict Transport Security)?",
        "options": {
            "A": "A policy that tells browsers to only interact with the site using HTTPS",
            "B": "A type of sharding",
            "C": "A database tool",
            "D": "A security certificate"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Basic Auth'?",
        "options": {
            "A": "Logging in with only a username",
            "B": "A simple authentication scheme where credentials are sent as Base64 encoded 'user:pass' in the header",
            "C": "A type of unit test",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Session Management' in Spring Security?",
        "options": {
            "A": "The process of managing user sessions, including concurrency control and session timeout",
            "B": "Writing session code",
            "C": "Managing the database session",
            "D": "A type of performance test"
        },
        "answer": "A"
    },
    {
        "question": "Which method in security configuration is used to disable session creation for a stateless API?",
        "options": {
            "A": ".sessionManagement().sessionCreationPolicy(SessionCreationPolicy.STATELESS)",
            "B": ".noSessions()",
            "C": ".disable(sessions)",
            "D": ".stateless()"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Ant Matchers' used for?",
        "options": {
            "A": "To catch ants in the server",
            "B": "To define URL patterns (e.g., /api/**) for applying security rules",
            "C": "A type of unit test",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 3: What is the primary reason to use JWT for a modern microservices architecture?",
        "options": {
            "A": "It is cheaper",
            "B": "It allows for stateless, scalable authentication across multiple independent services",
            "C": "It replaces the need for a database",
            "D": "It is faster for developers"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to load the full application context for integration testing in Spring Boot?",
        "options": {
            "A": "@TestContext",
            "B": "@SpringBootTest",
            "C": "@SpringJUnitConfig",
            "D": "@FullContext"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the '@MockBean' annotation?",
        "options": {
            "A": "To create a real database bean",
            "B": "To add a mock object to the Spring ApplicationContext, replacing any existing bean of the same type",
            "C": "To style the test output",
            "D": "To mark a test as a mock"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used for testing only the web layer (Controllers) without loading the full context?",
        "options": {
            "A": "@WebMvcTest",
            "B": "@ControllerTest",
            "C": "@RestTest",
            "D": "@MvcSlice"
        },
        "answer": "A"
    },
    {
        "question": "Which utility class is used to perform requests and verify responses in a @WebMvcTest?",
        "options": {
            "A": "RestTemplate",
            "B": "MockMvc",
            "C": "WebClient",
            "D": "TestClient"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Testcontainers' used for in Spring Boot testing?",
        "options": {
            "A": "To contain the test code",
            "B": "A Java library that supports JUnit tests by providing lightweight, throwaway instances of common databases or message brokers in Docker containers",
            "C": "To test UI components",
            "D": "To run tests in a browser"
        },
        "answer": "B"
    },
    {
        "question": "Which Spring Cloud component is commonly used for 'Service Discovery'?",
        "options": {
            "A": "Config Server",
            "B": "Netflix Eureka",
            "C": "API Gateway",
            "D": "Resilience4j"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary role of an 'API Gateway' in a microservices architecture?",
        "options": {
            "A": "To store the database",
            "B": "To act as a single entry point for all clients, handling routing, security, and rate limiting",
            "C": "To write the business logic",
            "D": "To monitor CPU heat"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Circuit Breaker' pattern used for in microservices?",
        "options": {
            "A": "To turn off the server during a fire",
            "B": "To prevent cascading failures by stopping calls to a failing service and providing a fallback",
            "C": "To speed up the network",
            "D": "To encrypt inter-service communication"
        },
        "answer": "B"
    },
    {
        "question": "Which library is the modern standard for implementing Circuit Breakers in Spring Boot?",
        "options": {
            "A": "Hystrix (deprecated)",
            "B": "Resilience4j",
            "C": "Spring Guard",
            "D": "CircuitFix"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Spring Cloud Config' used for?",
        "options": {
            "A": "To configure the computer hardware",
            "B": "To provide server-side and client-side support for externalized configuration in a distributed system",
            "C": "To manage user profile photos",
            "D": "To monitor network traffic"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Distributed Tracing' and which tool is often used with Spring Boot for it?",
        "options": {
            "A": "Drawing maps of the server room",
            "B": "The process of tracking requests as they flow through multiple microservices; Micrometer Tracing (formerly Sleuth) is the standard",
            "C": "A type of unit test",
            "D": "A database backup strategy"
        },
        "answer": "B"
    },
    {
        "question": "What does a 'Dockerfile' for a Spring Boot application typically contain?",
        "options": {
            "A": "The user's password",
            "B": "Instructions to build a container image, including the JRE and the application JAR file",
            "C": "The database schema only",
            "D": "A list of project developers"
        },
        "answer": "B"
    },
    {
        "question": "Which Maven command packages a Spring Boot app into an executable JAR ready for deployment?",
        "options": {
            "A": "mvn run",
            "B": "mvn clean package",
            "C": "mvn execute",
            "D": "mvn build-jar"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Blue-Green Deployment'?",
        "options": {
            "A": "Painting the server room blue and green",
            "B": "A deployment strategy where two identical production environments exist, allowing for zero-downtime updates",
            "C": "A type of color-blind accessibility test",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "What is the role of 'Kubernetes' in a microservices deployment?",
        "options": {
            "A": "To write Java code",
            "B": "An orchestration platform to automate the deployment, scaling, and management of containerized applications",
            "C": "To act as a database",
            "D": "To monitor the developer's computer"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to test data access components (Repositories) in isolation?",
        "options": {
            "A": "@DataJpaTest",
            "B": "@DbTest",
            "C": "@RepoSlice",
            "D": "@SpringDataTest"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Contract Testing'?",
        "options": {
            "A": "Testing a legal contract",
            "B": "Ensuring that a service provider and its consumers have a shared understanding of the API contract (e.g., using Spring Cloud Contract)",
            "C": "Testing the employee's contract",
            "D": "A type of manual UI test"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Saga Pattern' in microservices?",
        "options": {
            "A": "A long story about the project",
            "B": "A pattern for managing distributed transactions by coordinating a sequence of local transactions across services",
            "C": "A type of sharding",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "Which property is used to specify a different port for a Spring Boot application?",
        "options": {
            "A": "port.number",
            "B": "server.port",
            "C": "app.port",
            "D": "http.listen"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Graceful Shutdown' in Spring Boot?",
        "options": {
            "A": "Turning the computer off quickly",
            "B": "A feature that allows active requests to complete before the application shuts down during a redeploy",
            "C": "A manual way to close the app",
            "D": "A security scan during logout"
        },
        "answer": "B"
    },
    {
        "question": "Final question: What is the primary benefit of the Microservices architecture enabled by Spring Boot?",
        "options": {
            "A": "It makes the code simpler to write",
            "B": "It allows independent scaling, deployment, and technology choices for different parts of a large system",
            "C": "It is cheaper for small apps",
            "D": "It removes the need for a network"
        },
        "answer": "B"
    },
    {
        "question": "Which starter dependency is typically used to integrate Spring Data JPA with a relational database?",
        "options": {
            "A": "spring-boot-starter-jdbc",
            "B": "spring-boot-starter-data-jpa",
            "C": "spring-boot-starter-orm",
            "D": "jpa-persistence-starter"
        },
        "answer": "B"
    },
    {
        "question": "In Spring Data JPA, which interface should you extend to get standard CRUD operations without writing any implementation code?",
        "options": {
            "A": "JpaRepository",
            "B": "CrudService",
            "C": "HibernateTemplate",
            "D": "DatabaseRepository"
        },
        "answer": "A"
    },
    {
        "question": "Which annotation is used to map a Java class to a database table in a JPA-enabled application?",
        "options": {
            "A": "@Table",
            "B": "@Entity",
            "C": "@Repository",
            "D": "@Document"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the @Id annotation in a JPA entity?",
        "options": {
            "A": "To define the identity of the user session",
            "B": "To specify the primary key of the entity",
            "C": "To auto-increment the value",
            "D": "To hide the field from the database"
        },
        "answer": "B"
    },
    {
        "question": "Which property in application.properties allows you to see the actual SQL queries generated by Hibernate in the console?",
        "options": {
            "A": "spring.jpa.show-sql=true",
            "B": "hibernate.debug=true",
            "C": "spring.database.log=sql",
            "D": "sql.display=enabled"
        },
        "answer": "A"
    },
    {
        "question": "Which annotation is used to ensure a method runs within a database transaction?",
        "options": {
            "A": "@Transactional",
            "B": "@Atomic",
            "C": "@Commit",
            "D": "@Begin"
        },
        "answer": "A"
    },
    {
        "question": "What is the default behavior of @Transactional if a RuntimeException occurs?",
        "options": {
            "A": "The transaction is committed anyway",
            "B": "The transaction is rolled back",
            "C": "The database is deleted",
            "D": "The application stops"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to define a custom JPQL query in a repository interface?",
        "options": {
            "A": "@SQL",
            "B": "@Query",
            "C": "@Select",
            "D": "@Native"
        },
        "answer": "B"
    },
    {
        "question": "How do you specify a native SQL query instead of JPQL in the @Query annotation?",
        "options": {
            "A": "Set nativeQuery = true",
            "B": "Use the prefix 'SQL:'",
            "C": "Use the @NativeQuery annotation",
            "D": "It is not possible"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of the 'mappedBy' attribute in a @OneToMany relationship?",
        "options": {
            "A": "To name the database table",
            "B": "To indicate the field in the child entity that owns the relationship",
            "C": "To encrypt the relationship",
            "D": "To sort the children"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to map a Many-to-Many relationship?",
        "options": {
            "A": "@ManyToMany",
            "B": "@JoinTable",
            "C": "Both A and B are typically used together",
            "D": "@MultiRelation"
        },
        "answer": "C"
    },
    {
        "question": "What is 'Dirty Checking' in Hibernate/JPA?",
        "options": {
            "A": "Checking for invalid characters in strings",
            "B": "The mechanism that automatically detects changes to an entity and syncs them with the database upon transaction commit",
            "C": "A security scan of the database",
            "D": "Deleting corrupted data"
        },
        "answer": "B"
    },
    {
        "question": "Which interface provides pagination and sorting capabilities in Spring Data?",
        "options": {
            "A": "CrudRepository",
            "B": "PagingAndSortingRepository",
            "C": "ListRepository",
            "D": "QueryRepository"
        },
        "answer": "B"
    },
    {
        "question": "Which class is used to pass pagination information to a repository method?",
        "options": {
            "A": "PageInfo",
            "B": "PageRequest",
            "C": "SortOrder",
            "D": "Limit"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'existsById()' method in JpaRepository return?",
        "options": {
            "A": "The object if found",
            "B": "A boolean value (true if the entity exists, false otherwise)",
            "C": "An Optional wrapper",
            "D": "An integer count"
        },
        "answer": "B"
    },
    {
        "question": "What is the role of the 'Persistence Context'?",
        "options": {
            "A": "A backup of the database",
            "B": "A first-level cache where all entities are managed during a transaction",
            "C": "A configuration file",
            "D": "A security layer"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to map a One-to-Many relationship in Spring Data JPA?",
        "options": {
            "A": "@ManyToOne",
            "B": "@OneToMany",
            "C": "@JoinColumn",
            "D": "@Relationship"
        },
        "answer": "B"
    },
    {
        "question": "In a REST controller, which annotation is used to extract a variable from the URL path (e.g., /api/users/{id})?",
        "options": {
            "A": "@RequestParam",
            "B": "@PathVariable",
            "C": "@UrlVariable",
            "D": "@QueryParam"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'spring.jpa.hibernate.ddl-auto' property?",
        "options": {
            "A": "To automatically write Java code",
            "B": "To control how the database schema is initialized or updated (e.g., create, update, validate)",
            "C": "To set the database password",
            "D": "To enable auto-configuration"
        },
        "answer": "B"
    },
    {
        "question": "Which HTTP method is typically used to update an existing resource completely?",
        "options": {
            "A": "POST",
            "B": "PUT",
            "C": "PATCH",
            "D": "GET"
        },
        "answer": "B"
    },
    {
        "question": "Which dependency is primarily responsible for JSON serialization/deserialization in Spring Boot?",
        "options": {
            "A": "GSON",
            "B": "Jackson",
            "C": "JSON-B",
            "D": "FastJSON"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of @Transient in a JPA entity class?",
        "options": {
            "A": "To mark a field for encryption",
            "B": "To tell JPA not to persist a specific field to the database",
            "C": "To make a field required",
            "D": "To speed up the database query"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Fetching Strategy' (Lazy vs Eager) in JPA?",
        "options": {
            "A": "A way to download files",
            "B": "Determines whether related entities are loaded immediately (Eager) or only when accessed (Lazy)",
            "C": "A type of database indexing",
            "D": "A security policy for read access"
        },
        "answer": "B"
    },
    {
        "question": "What does @ResponseStatus(HttpStatus.NOT_FOUND) do when placed on a custom exception?",
        "options": {
            "A": "Finds the error on Google",
            "B": "Automatically returns a 404 status code when that exception is thrown from a controller",
            "C": "Deletes the missing resource",
            "D": "Restarts the server"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'ResponseEntity' in a controller method?",
        "options": {
            "A": "To encrypt the response",
            "B": "To provide full control over the HTTP response, including headers, body, and status code",
            "C": "To redirect the user",
            "D": "To handle database errors"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to automatically populate 'created_at' and 'updated_at' fields?",
        "options": {
            "A": "@Timed",
            "B": "@EntityListeners(AuditingEntityListener.class)",
            "C": "@AutoTime",
            "D": "@Clock"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Open Session in View' (OSIV) pattern?",
        "options": {
            "A": "Keeping the database open all day",
            "B": "Keeping the database session open during the entire request to allow lazy loading in the view layer",
            "C": "A security vulnerability",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "Which property disables 'Open Session in View'?",
        "options": {
            "A": "spring.jpa.open-in-view=false",
            "B": "hibernate.session.close=true",
            "C": "jpa.osiv=disabled",
            "D": "spring.datasource.close-on-view=true"
        },
        "answer": "A"
    },
    {
        "question": "What is an 'Embedded' object in JPA?",
        "options": {
            "A": "A video inside a webpage",
            "B": "A Java object whose fields are mapped to the same table as the parent entity using @Embeddable",
            "C": "A database inside another database",
            "D": "A hidden field"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used on a class that will be 'Embedded' into another entity?",
        "options": {
            "A": "@Embedded",
            "B": "@Embeddable",
            "C": "@Component",
            "D": "@Entity"
        },
        "answer": "B"
    },
    {
        "question": "What is 'N+1 Select Problem'?",
        "options": {
            "A": "A math error in a loop",
            "B": "A performance issue where one query for a parent results in 'N' additional queries for its children",
            "C": "A primary key collision",
            "D": "A database version conflict"
        },
        "answer": "B"
    },
    {
        "question": "Which JPA feature is used to solve the N+1 problem?",
        "options": {
            "A": "Lazy Loading",
            "B": "Entity Graphs or JOIN FETCH queries",
            "C": "Caching",
            "D": "Indexing"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Optimistic Locking'?",
        "options": {
            "A": "Believing no errors will occur",
            "B": "A strategy to prevent data conflicts by checking a version field before updating a row",
            "C": "Locking the database for all users",
            "D": "A security password"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to implement Optimistic Locking?",
        "options": {
            "A": "@Lock",
            "B": "@Version",
            "C": "@Check",
            "D": "@Sequence"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Pessimistic Locking'?",
        "options": {
            "A": "Expecting the worst errors",
            "B": "Explicitly locking a database row during a transaction to prevent any other access",
            "C": "A type of unit test",
            "D": "A firewall setting"
        },
        "answer": "B"
    },
    {
        "question": "In a REST API, what does the 405 status code mean?",
        "options": {
            "A": "Resource not found",
            "B": "Method Not Allowed (e.g., trying to POST to a GET endpoint)",
            "C": "Server Error",
            "D": "Unauthorized"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Projection' in Spring Data JPA?",
        "options": {
            "A": "Retrieving only a subset of fields from an entity using interfaces or DTOs",
            "B": "Predicting the future size of data",
            "C": "Displaying data on a screen",
            "D": "A type of database join"
        },
        "answer": "A"
    },
    {
        "question": "Which annotation is used to specify a join column in a relationship?",
        "options": {
            "A": "@Column",
            "B": "@JoinColumn",
            "C": "@ForeignKey",
            "D": "@MapColumn"
        },
        "answer": "B"
    },
    {
        "question": "How do you handle 'Audit' logic for entities automatically in Spring Data?",
        "options": {
            "A": "By using @EnableJpaAuditing on a config class",
            "B": "By writing manual triggers in SQL",
            "C": "It is active by default",
            "D": "By using @AuditEntity"
        },
        "answer": "A"
    },
    {
        "question": "What is the primary difference between save() and saveAndFlush() in JpaRepository?",
        "options": {
            "A": "saveAndFlush() forces immediate synchronization with the database",
            "B": "save() is faster and safer",
            "C": "saveAndFlush() is only for updates",
            "D": "There is no difference"
        },
        "answer": "A"
    },
    {
        "question": "Which annotation is used on a method to perform a partial update in REST?",
        "options": {
            "A": "@PostMapping",
            "B": "@PatchMapping",
            "C": "@UpdateMapping",
            "D": "@PutMethod"
        },
        "answer": "B"
    },
    {
        "question": "What does @Enumerated(EnumType.STRING) do?",
        "options": {
            "A": "Saves the Enum's name as a string in the database instead of its index",
            "B": "Converts all strings to Enums",
            "C": "Hides the Enum from the API",
            "D": "Speeds up the query"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of @OrderBy in a JPA relationship?",
        "options": {
            "A": "To sort the collection of related entities when they are loaded",
            "B": "To order a new computer",
            "C": "To group data by a specific field",
            "D": "To set the primary key order"
        },
        "answer": "A"
    },
    {
        "question": "Which annotation allows a class to pass its mapping information to its subclasses in JPA inheritance?",
        "options": {
            "A": "@MappedSuperclass",
            "B": "@Inherit",
            "C": "@BaseEntity",
            "D": "@ParentMapping"
        },
        "answer": "A"
    },
    {
        "question": "What is 'JPQL' (Java Persistence Query Language)?",
        "options": {
            "A": "A query language that operates on Java entities rather than database tables",
            "B": "A specialized version of SQL for Java",
            "C": "A type of unit test",
            "D": "A database engine"
        },
        "answer": "A"
    },
    {
        "question": "Which annotation is used to perform an update or delete operation with @Query?",
        "options": {
            "A": "@Modifying",
            "B": "@Update",
            "C": "@Alter",
            "D": "@Write"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of @DynamicUpdate in a JPA entity?",
        "options": {
            "A": "To ensure only modified columns are included in the SQL UPDATE statement",
            "B": "To update the database while the app is running",
            "C": "To update the UI dynamically",
            "D": "To encrypt update statements"
        },
        "answer": "A"
    },
    {
        "question": "Which HTTP status code represents 'No Content' (successful request with no body to return)?",
        "options": {
            "A": "204",
            "B": "200",
            "C": "201",
            "D": "404"
        },
        "answer": "A"
    },
    {
        "question": "What is a 'Derived Query'?",
        "options": {
            "A": "A query generated by Spring Data based on a method name like findByUsername",
            "B": "A query from another database",
            "C": "A manual SQL string",
            "D": "A performance metric"
        },
        "answer": "A"
    },
    {
        "question": "Final question of Batch 2: Why is it recommended to use DTOs (Data Transfer Objects) in REST controllers?",
        "options": {
            "A": "To decouple the API contract from the internal database schema and improve security",
            "B": "To make the code harder to read",
            "C": "Because Spring Boot requires them",
            "D": "To speed up the network"
        },
        "answer": "A"
    },
    {
        "question": "What is the 'Condition Evaluation Report' in Spring Boot and how can you view it?",
        "options": {
            "A": "A report on the developer's performance; viewed via email",
            "B": "A detailed log of which auto-configurations were applied and why; viewed by running with the --debug flag",
            "C": "A security scan report; viewed in the browser",
            "D": "A list of database errors; viewed in the SQL console"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the @ConditionalOnProperty annotation?",
        "options": {
            "A": "To encrypt a property",
            "B": "To allow a bean to be created only if a specific configuration property is present and has a specific value",
            "C": "To set a default value for a variable",
            "D": "To delete a property after use"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Spring Boot Loader'?",
        "options": {
            "A": "The part of the framework that allows the executable 'Fat JAR' to launch and load its own nested dependencies",
            "B": "A tool to load images into the UI",
            "C": "A database driver for fast loading",
            "D": "A system to update the app version"
        },
        "answer": "A"
    },
    {
        "question": "In a Spring Boot JAR, which directory contains the application's compiled classes?",
        "options": {
            "A": "META-INF/",
            "B": "BOOT-INF/classes/",
            "C": "lib/",
            "D": "src/main/java/"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Object-Relational Mapping' (ORM) Impedance Mismatch?",
        "options": {
            "A": "A network connection error",
            "B": "The conceptual and technical difficulties in mapping a rich object model to a relational database schema",
            "C": "A primary key collision",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of @Primary annotation when multiple beans of the same type exist?",
        "options": {
            "A": "To delete the other beans",
            "B": "To give higher precedence to a specific bean when multiple candidates are qualified to be injected",
            "C": "To mark a bean as the first one created",
            "D": "To hide the bean from the context"
        },
        "answer": "B"
    },
    {
        "question": "@Qualifier is used in conjunction with @Autowired to:",
        "options": {
            "A": "Speed up the injection",
            "B": "Specify exactly which bean should be injected by providing its name",
            "C": "Check the quality of the bean",
            "D": "Encrypt the dependency"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Constructor Injection' vs 'Field Injection'?",
        "options": {
            "A": "Constructor injection is the recommended way because it allows for immutable dependencies and easier testing",
            "B": "Field injection is faster",
            "C": "Constructor injection only works for strings",
            "D": "Field injection is safer for security"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Self-Invocation' problem with @Transactional?",
        "options": {
            "A": "The method calls itself forever",
            "B": "When a method in a bean calls another @Transactional method in the same bean, the proxy is bypassed and no transaction starts",
            "C": "A security vulnerability",
            "D": "A performance bottleneck"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'DeferredImportSelector' interface used for?",
        "options": {
            "A": "To delay the loading of the database",
            "B": "To ensure that auto-configuration classes are processed after all regular @Configuration classes",
            "C": "To import CSS files later",
            "D": "To skip unit tests"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Spring AOP' (Aspect-Oriented Programming)?",
        "options": {
            "A": "A way to write code using shapes",
            "B": "A programming paradigm that allows modularizing cross-cutting concerns like logging and transactions",
            "C": "A tool to manage API keys",
            "D": "A type of sharding"
        },
        "answer": "B"
    },
    {
        "question": "In AOP, what is a 'Join Point'?",
        "options": {
            "A": "Where two database tables join",
            "B": "A point during the execution of a program, such as the execution of a method or handling of an exception",
            "C": "A connection between two servers",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "In AOP, what is an 'Advice'?",
        "options": {
            "A": "Tips for the developer",
            "B": "The action taken by an aspect at a particular join point (e.g., @Before, @After)",
            "C": "A security recommendation",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Pointcut' in Spring AOP?",
        "options": {
            "A": "A physical cut in the wire",
            "B": "A predicate that matches join points to determine where Advice should be applied",
            "C": "A way to stop a program",
            "D": "A type of routing"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Proxy' in Spring AOP?",
        "options": {
            "A": "A server that hides the IP",
            "B": "An object created by the AOP framework to implement the aspect contracts (advice method executions)",
            "C": "A fake user",
            "D": "A type of cache"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Spring Boot Admin' (Third-party library)?",
        "options": {
            "A": "The person who manages the database",
            "B": "A community project used to manage and monitor Spring Boot applications via a nice UI",
            "C": "A security firewall",
            "D": "A specialized version of the CLI"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Twelve-Factor App' methodology in Spring Boot context?",
        "options": {
            "A": "A list of 12 bugs to avoid",
            "B": "A set of best practices for building modern, cloud-native applications that are portable and resilient",
            "C": "A type of sharding",
            "D": "A performance test"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Externalized Configuration' precedence in Spring Boot?",
        "options": {
            "A": "Properties in the code are always first",
            "B": "Command-line arguments override application.properties, which override default values",
            "C": "JSON files always override YAML files",
            "D": "There is no precedence"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Micrometer' in Spring Boot 2.0+?",
        "options": {
            "A": "A tool to measure the size of the computer",
            "B": "An application metrics facade that supports multiple monitoring systems like Prometheus and Datadog",
            "C": "A specialized compiler",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Spring WebFlux'?",
        "options": {
            "A": "A new version of the website",
            "B": "A reactive-stack web framework that is non-blocking and supports reactive streams",
            "C": "A tool for CSS animations",
            "D": "A database engine"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Netty' in the context of WebFlux?",
        "options": {
            "A": "A fishing net for the server",
            "B": "A non-blocking I/O client-server framework often used as the default embedded server for WebFlux",
            "C": "A security firewall",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Mono' in Project Reactor?",
        "options": {
            "A": "A type of speaker",
            "B": "A Reactive Streams Publisher that emits 0 to 1 element",
            "C": "A single-threaded application",
            "D": "A type of database index"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Flux' in Project Reactor?",
        "options": {
            "A": "A state of change",
            "B": "A Reactive Streams Publisher that emits 0 to N elements",
            "C": "A fast database query",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Spring Cloud Gateway'?",
        "options": {
            "A": "The entrance to the office",
            "B": "A library for building API Gateways on top of Spring WebFlux",
            "C": "A type of sharding",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "Final question: What is 'Spring Boot 3' primary baseline requirement?",
        "options": {
            "A": "Windows 11",
            "B": "Java 17 and Jakarta EE 9",
            "C": "Python 3.10",
            "D": "16GB of RAM"
        },
        "answer": "B"
    },
    {
        "question": "Which Spring Boot feature allows the application to be 'compiled' into a platform-specific executable for faster startup and lower memory footprint, specifically using GraalVM?",
        "options": {
            "A": "Fat JAR",
            "B": "Native Image support",
            "C": "AOT Compilation",
            "D": "JIT Transformation"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary role of 'ObservationRegistry' in modern Spring Boot (v3+)?",
        "options": {
            "A": "To observe user clicks in the UI",
            "B": "To provide a unified API for collecting both metrics and distributed tracing data",
            "C": "To monitor the physical temperature of the server",
            "D": "To observe database schema changes"
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
    skill = "springboot"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
