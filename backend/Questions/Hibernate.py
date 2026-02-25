from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
    {
        "question": "What is the primary purpose of Hibernate in a Java application?",
        "options": {
            "A": "To provide a web server",
            "B": "To map Java objects to relational database tables (Object-Relational Mapping)",
            "C": "To handle frontend styling",
            "D": "To manage dependency injection"
        },
        "answer": "B"
    },
    {
        "question": "Which interface is used to create a Session object in Hibernate?",
        "options": {
            "A": "SessionManager",
            "B": "SessionFactory",
            "C": "EntityManager",
            "D": "ConnectionProvider"
        },
        "answer": "B"
    },
    {
        "question": "What is the difference between Hibernate and JPA?",
        "options": {
            "A": "Hibernate is the specification; JPA is the implementation",
            "B": "JPA is the Java specification for ORM; Hibernate is a popular implementation of that specification",
            "C": "They are the same thing with different names",
            "D": "JPA is only for mobile; Hibernate is for web"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is required at the class level to mark a Java class as a Hibernate entity?",
        "options": {
            "A": "@Table",
            "B": "@Entity",
            "C": "@Persistent",
            "D": "@Id"
        },
        "answer": "B"
    },
    {
        "question": "What does the @Id annotation signify in a Hibernate entity?",
        "options": {
            "A": "The user's login ID",
            "B": "The primary key of the entity",
            "C": "A unique index only",
            "D": "The table name"
        },
        "answer": "B"
    },
    {
        "question": "Which file is typically used for XML-based Hibernate configuration?",
        "options": {
            "A": "hibernate.xml",
            "B": "hibernate.cfg.xml",
            "C": "persistence.xml",
            "D": "Both B and C"
        },
        "answer": "D"
    },
    {
        "question": "In the Hibernate Entity Lifecycle, what is a 'Transient' object?",
        "options": {
            "A": "An object stored in the database",
            "B": "A new object that has no association with a Session and no representation in the database",
            "C": "An object that is being deleted",
            "D": "An object loaded from the cache"
        },
        "answer": "B"
    },
    {
        "question": "In the Hibernate Entity Lifecycle, what is a 'Persistent' object?",
        "options": {
            "A": "An object that exists in the database but not in memory",
            "B": "An object associated with an active Session and representing a row in the database",
            "C": "An object that cannot be deleted",
            "D": "A static object"
        },
        "answer": "B"
    },
    {
        "question": "What happens to a 'Persistent' object when the Session is closed?",
        "options": {
            "A": "It is deleted from the database",
            "B": "It becomes 'Detached'",
            "C": "It remains Persistent",
            "D": "It becomes Transient"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to move a Transient object to a Persistent state?",
        "options": {
            "A": "session.update()",
            "B": "session.save() or session.persist()",
            "C": "session.merge()",
            "D": "session.get()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Dirty Checking' in Hibernate?",
        "options": {
            "A": "Checking the database for corruption",
            "B": "The process where Hibernate automatically detects changes in persistent objects and synchronizes them with the database",
            "C": "Validating user input",
            "D": "A security scan of the SQL"
        },
        "answer": "B"
    },
    {
        "question": "Which method would you use to re-attach a 'Detached' object to a new Session?",
        "options": {
            "A": "save()",
            "B": "merge() or update()",
            "C": "persist()",
            "D": "refresh()"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'hbm2ddl.auto' property?",
        "options": {
            "A": "To automatically optimize queries",
            "B": "To automatically validate, create, or update the database schema based on entities",
            "C": "To handle automated backups",
            "D": "To encrypt the database"
        },
        "answer": "B"
    },
    {
        "question": "What does 'hbm2ddl.auto=update' do?",
        "options": {
            "A": "Drops and recreates the database",
            "B": "Compares the existing schema with the entity mappings and adds missing columns/tables",
            "C": "Deletes all data",
            "D": "Does nothing"
        },
        "answer": "B"
    },
    {
        "question": "Which Hibernate object is thread-safe and usually created once per application?",
        "options": {
            "A": "Session",
            "B": "SessionFactory",
            "C": "Transaction",
            "D": "Query"
        },
        "answer": "B"
    },
    {
        "question": "Which Hibernate object is NOT thread-safe and should be created per request/unit of work?",
        "options": {
            "A": "SessionFactory",
            "B": "Session",
            "C": "Configuration",
            "D": "StandardServiceRegistry"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the @Table annotation?",
        "options": {
            "A": "To create a UI table",
            "B": "To specify the name and details of the database table for an entity",
            "C": "To define the primary key",
            "D": "To link two classes"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Lazy Loading' in Hibernate?",
        "options": {
            "A": "Waiting for the developer to finish",
            "B": "Postponing the initialization of an object or collection until it is actually accessed",
            "C": "Loading data from a slow database",
            "D": "A performance bug"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Eager Loading'?",
        "options": {
            "A": "Loading data as fast as possible",
            "B": "Fetching an associated object or collection at the same time as the parent entity",
            "C": "Loading data from memory",
            "D": "A way to reduce RAM usage"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to map a column name if it differs from the Java field name?",
        "options": {
            "A": "@Field",
            "B": "@Column",
            "C": "@Attribute",
            "D": "@DBField"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Dialect' in Hibernate?",
        "options": {
            "A": "A language for entities",
            "B": "A class that tells Hibernate how to generate SQL specifically for a particular database (e.g., MySQL, Oracle)",
            "C": "A reporting tool",
            "D": "A security layer"
        },
        "answer": "B"
    },
    {
        "question": "What is 'L1 Cache' (First-level Cache)?",
        "options": {
            "A": "A cache on the hard drive",
            "B": "The mandatory Session-level cache that stores persistent objects during a single session",
            "C": "A shared cache across the cluster",
            "D": "A cache for SQL queries"
        },
        "answer": "B"
    },
    {
        "question": "What is the difference between session.get() and session.load()?",
        "options": {
            "A": "get() is for XML; load() is for Annotations",
            "B": "get() returns the actual object and hits the DB immediately; load() returns a proxy and delays hitting the DB",
            "C": "load() returns null if the record is missing; get() throws an exception",
            "D": "There is no difference"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Proxy' in Hibernate?",
        "options": {
            "A": "A network security setting",
            "B": "A placeholder object that Hibernate uses for lazy loading, which fetches the real data only when needed",
            "C": "An admin user",
            "D": "A database view"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to define a one-to-many relationship?",
        "options": {
            "A": "@ManyToOne",
            "B": "@OneToMany",
            "C": "@Collection",
            "D": "@JoinTable"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'mappedBy' in a relationship mapping?",
        "options": {
            "A": "To specify the database name",
            "B": "To indicate the 'non-owning' side of a bidirectional relationship",
            "C": "To map a column to a field",
            "D": "To enable primary key generation"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Cascading' in Hibernate?",
        "options": {
            "A": "Styling the database",
            "B": "The ability to propagate operations (like save or delete) from a parent entity to its associated children",
            "C": "A type of database join",
            "D": "A sequence generator"
        },
        "answer": "B"
    },
    {
        "question": "Which CascadeType ensures children are deleted if the parent is deleted?",
        "options": {
            "A": "PERSIST",
            "B": "REMOVE",
            "C": "DETACH",
            "D": "REFRESH"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Orphan Removal'?",
        "options": {
            "A": "Deleting old users",
            "B": "Automatically deleting a child entity if it is removed from the parent's collection/association",
            "C": "Cleaning up the transaction log",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to generate primary key values automatically?",
        "options": {
            "A": "@AutoValue",
            "B": "@GeneratedValue",
            "C": "@Sequence",
            "D": "@Primary"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Identity' strategy for ID generation?",
        "options": {
            "A": "Using a sequence table",
            "B": "Using the database's native auto-increment column feature",
            "C": "Using a UUID",
            "D": "Manual entry"
        },
        "answer": "B"
    },
    {
        "question": "Which interface is used to define a custom query in Hibernate?",
        "options": {
            "A": "SQLQuery",
            "B": "Query (org.hibernate.query.Query)",
            "C": "Criteria",
            "D": "Both B and C"
        },
        "answer": "B"
    },
    {
        "question": "What is HQL (Hibernate Query Language)?",
        "options": {
            "A": "A language for HTML",
            "B": "An object-oriented query language, similar to SQL, but operating on persistent objects and their properties",
            "C": "A way to style entities",
            "D": "A performance monitoring tool"
        },
        "answer": "B"
    },
    {
        "question": "How do you prevent a field from being persisted in the database?",
        "options": {
            "A": "@Ignore",
            "B": "@Transient",
            "C": "@Hidden",
            "D": "Making the field private"
        },
        "answer": "B"
    },
    {
        "question": "What is 'L2 Cache' (Second-level Cache)?",
        "options": {
            "A": "A cache in the browser",
            "B": "An optional cache that is shared across all Sessions of a SessionFactory",
            "C": "A cache on the CPU",
            "D": "A type of backup"
        },
        "answer": "B"
    },
    {
        "question": "What is 'N+1 Select Problem'?",
        "options": {
            "A": "A database version error",
            "B": "A performance issue where Hibernate executes one query to fetch N parent records, and then N separate queries to fetch children for each parent",
            "C": "A syntax error in HQL",
            "D": "A security vulnerability"
        },
        "answer": "B"
    },
    {
        "question": "Which FetchType is default for @ManyToOne relationships?",
        "options": {
            "A": "LAZY",
            "B": "EAGER",
            "C": "OPTIONAL",
            "D": "DYNAMIC"
        },
        "answer": "B"
    },
    {
        "question": "Which FetchType is default for @OneToMany relationships?",
        "options": {
            "A": "EAGER",
            "B": "LAZY",
            "C": "MANDATORY",
            "D": "STATIC"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Transaction' in Hibernate?",
        "options": {
            "A": "To transfer money",
            "B": "To ensure that a group of operations succeed or fail as a single unit (ACID properties)",
            "C": "To speed up the network",
            "D": "To monitor the log"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to finalize the changes in a Transaction?",
        "options": {
            "A": "save()",
            "B": "commit()",
            "C": "flush()",
            "D": "close()"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of session.flush()?",
        "options": {
            "A": "To close the session",
            "B": "To synchronize the in-memory state of objects with the database immediately, without committing the transaction",
            "C": "To clear the cache",
            "D": "To delete transient objects"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Component Mapping' (@Embeddable)?",
        "options": {
            "A": "Mapping multiple tables to one class",
            "B": "Mapping a POJO as a group of columns within another entity's table rather than as a separate table",
            "C": "Mapping a UI component",
            "D": "A type of inheritance"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to define the owning side of a Many-to-Many relationship?",
        "options": {
            "A": "@JoinColumn",
            "B": "@JoinTable",
            "C": "@ManyToMany",
            "D": "Both B and C"
        },
        "answer": "D"
    },
    {
        "question": "What is the 'Query Cache'?",
        "options": {
            "A": "A cache for query results",
            "B": "A cache that stores the IDs of results returned by a specific HQL/Criteria query",
            "C": "A cache for SQL syntax",
            "D": "A type of index"
        },
        "answer": "B"
    },
    {
        "question": "Which inheritance strategy creates one table per class (including subclasses)?",
        "options": {
            "A": "SINGLE_TABLE",
            "B": "TABLE_PER_CLASS",
            "C": "JOINED",
            "D": "MAPPED_SUPERCLASS"
        },
        "answer": "B"
    },
    {
        "question": "What is 'SINGLE_TABLE' inheritance strategy?",
        "options": {
            "A": "Every entity has its own table",
            "B": "All classes in a hierarchy are mapped to a single table with a discriminator column",
            "C": "A table with only one row",
            "D": "A database view"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Discriminator' column?",
        "options": {
            "A": "A column used to delete data",
            "B": "A column in a SINGLE_TABLE hierarchy used to identify which class a specific row belongs to",
            "C": "A primary key",
            "D": "A foreign key"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of @Version in Hibernate?",
        "options": {
            "A": "To track the app version",
            "B": "To implement optimistic locking and prevent concurrent modifications (Lost Update problem)",
            "C": "To store the timestamp of creation",
            "D": "To rename the table"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Optimistic Locking'?",
        "options": {
            "A": "Hoping no one else edits the data",
            "B": "A strategy that assumes no conflicts will occur but checks for a version change before updating a row",
            "C": "Locking the database for 1 hour",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 1: Which object is used to define the physical database connection properties in a modern Hibernate 5/6 application?",
        "options": {
            "A": "SessionFactory",
            "B": "StandardServiceRegistry",
            "C": "Metadata",
            "D": "Session"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary difference between HQL and Native SQL?",
        "options": {
            "A": "HQL is faster",
            "B": "HQL is database-independent and uses class/property names; Native SQL is database-specific and uses table/column names",
            "C": "Native SQL cannot be used in Hibernate",
            "D": "HQL only works for SELECT statements"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to map a collection of basic types (like a List of Strings) that are not entities themselves?",
        "options": {
            "A": "@OneToMany",
            "text": "@ElementCollection",
            "C": "@BasicCollection",
            "D": "@Embedded"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the @JoinColumn annotation?",
        "options": {
            "A": "To create a new table",
            "B": "To specify the physical column used for joining an entity association or a secondary table",
            "C": "To define a primary key",
            "D": "To merge two entities"
        },
        "answer": "B"
    },
    {
        "question": "Which interface provides a type-safe, programmatic way to create queries in JPA?",
        "options": {
            "A": "Query",
            "B": "CriteriaBuilder",
            "C": "EntityTransaction",
            "D": "PersistenceProvider"
        },
        "answer": "B"
    },
    {
        "question": "In a @ManyToMany relationship, which attribute is used to define the 'Join Table' details?",
        "options": {
            "A": "@Table",
            "B": "@JoinTable",
            "C": "@MappingTable",
            "D": "@BridgeTable"
        },
        "answer": "B"
    },
    {
        "question": "What does 'Pagination' in Hibernate allow you to do?",
        "options": {
            "A": "Sort the results",
            "B": "Fetch a specific subset (range) of rows from a large result set using setFirstResult() and setMaxResults()",
            "C": "Print the results to pages",
            "D": "Delete duplicate rows"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation allows an entity to inherit fields from a base class without that base class being a separate table?",
        "options": {
            "A": "@Inheritance",
            "B": "@MappedSuperclass",
            "C": "@EntityListeners",
            "D": "@Embedded"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'JOINED' inheritance strategy?",
        "options": {
            "A": "All classes in one table",
            "B": "Each class in the hierarchy has its own table, and subclass tables are linked to the base table via foreign keys",
            "C": "No tables are created",
            "D": "A strategy for many-to-many joins"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to remove a persistent object from the database?",
        "options": {
            "A": "session.delete() or session.remove()",
            "B": "session.clear()",
            "C": "session.detach()",
            "D": "session.discard()"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of the 'session.evict(object)' method?",
        "options": {
            "A": "To delete the object from the DB",
            "B": "To remove a specific object from the Session-level (L1) cache",
            "C": "To refresh the object from the DB",
            "D": "To close the session"
        },
        "answer": "B"
    },
    {
        "question": "What does 'Pessimistic Locking' do?",
        "options": {
            "A": "Assumes no conflicts will occur",
            "B": "Locks the database record immediately upon reading to prevent any other transaction from modifying it until the current one finishes",
            "C": "Deletes the record if a conflict occurs",
            "D": "A strategy for slow networks"
        },
        "answer": "B"
    },
    {
        "question": "Which JPA annotation is used to execute a specific method automatically 'before' an entity is persisted?",
        "options": {
            "A": "@PreUpdate",
            "B": "@PrePersist",
            "C": "@PostLoad",
            "D": "@BeforeSave"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Named Query' in Hibernate?",
        "options": {
            "A": "A query that has a nickname",
            "B": "A statically defined query with a fixed name, usually defined via annotations on the entity, for better reuse and performance",
            "C": "A query for the user's name",
            "D": "A dynamic query built at runtime"
        },
        "answer": "B"
    },
    {
        "question": "What is the difference between @Enumerated(EnumType.ORDINAL) and @Enumerated(EnumType.STRING)?",
        "options": {
            "A": "ORDINAL stores the index (int); STRING stores the name of the enum constant",
            "B": "STRING is for numbers; ORDINAL is for text",
            "C": "ORDINAL is faster but less safe if the enum order changes",
            "D": "Both A and C"
        },
        "answer": "D"
    },
    {
        "question": "What is the 'Persistence Context'?",
        "options": {
            "A": "A database configuration file",
            "B": "The environment where entities are managed by the EntityManager/Session, ensuring each entity has a unique instance within a transaction",
            "C": "The physical location of the server",
            "D": "A tool for generating SQL"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to map a Java 'Date' or 'Calendar' object to a specific SQL temporal type (DATE, TIME, TIMESTAMP)?",
        "options": {
            "A": "@DateType",
            "B": "@Temporal",
            "C": "@SQLDate",
            "D": "@TimeMapping"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Fetching Strategy' in Hibernate?",
        "options": {
            "A": "A way to download entities",
            "B": "The logic that determines when and how associated objects are loaded (Lazy vs Eager, Join vs Select)",
            "C": "A security setting",
            "D": "A backup tool"
        },
        "answer": "B"
    },
    {
        "question": "Which FetchMode uses a separate SELECT statement to fetch the associated collection?",
        "options": {
            "A": "JOIN",
            "B": "SELECT",
            "C": "SUBSELECT",
            "D": "BATCH"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Batch Fetching' used for?",
        "options": {
            "A": "To fetch all entities at once",
            "B": "To optimize the N+1 problem by fetching associated collections for multiple parents in a single query using an IN clause",
            "C": "To delete data in batches",
            "D": "To speed up the JVM"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Constructor Expression' in JPQL?",
        "options": {
            "A": "A query that creates a new database",
            "B": "A query that instantiates a DTO (Data Transfer Object) directly from the query results using 'NEW' keyword",
            "C": "A way to call Java constructors from SQL",
            "D": "A type of subquery"
        },
        "answer": "B"
    },
    {
        "question": "Which interface allows you to define 'Callbacks' for entity lifecycle events?",
        "options": {
            "A": "EntityListener",
            "B": "Lifecycle",
            "C": "PersistenceListener",
            "D": "SessionListener"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of @AttributeOverride?",
        "options": {
            "A": "To rename a Java variable",
            "B": "To override the column mapping of an @Embeddable class property within a specific entity",
            "C": "To delete an attribute",
            "D": "To change the primary key"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Session.clear()' used for?",
        "options": {
            "A": "To delete all data in the DB",
            "B": "To detach all entities currently managed by the Session, emptying the L1 cache",
            "C": "To reset the database connection",
            "D": "To commit the transaction"
        },
        "answer": "B"
    },
    {
        "question": "How do you map a many-to-one relationship to a column that is not the primary key of the target entity?",
        "options": {
            "A": "Use referencedColumnName in @JoinColumn",
            "B": "It is not possible",
            "C": "Use @PrimaryKeyJoinColumn",
            "D": "Use @IdClass"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Static Metamodel' in JPA Criteria API?",
        "options": {
            "A": "A model of the hardware",
            "B": "A set of generated classes that represent the entity properties, allowing for compile-time type-safe queries",
            "C": "A static database",
            "D": "A type of L2 cache"
        },
        "answer": "B"
    },
    {
        "question": "What does the @OrderBy annotation do?",
        "options": {
            "A": "Sorts the database table physically",
            "B": "Specifies the ordering of elements in a collection when it is loaded from the database",
            "C": "Prioritizes specific entities",
            "D": "A reporting tool"
        },
        "answer": "B"
    },
    {
        "question": "Which interface is used to manage transactions programmatically in JPA?",
        "options": {
            "A": "Session",
            "B": "EntityTransaction",
            "C": "TransactionManager",
            "D": "Connection"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'TABLE_PER_CLASS' inheritance strategy disadvantage?",
        "options": {
            "A": "Polymorphic queries (e.g., fetching all base types) are very expensive because they require UNION across all subclass tables",
            "B": "It uses too many primary keys",
            "C": "It does not support lazy loading",
            "D": "It is not standard JPA"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of @SecondaryTable?",
        "options": {
            "A": "To create a backup table",
            "B": "To map a single entity to two or more separate database tables",
            "C": "To define a many-to-many join table",
            "D": "To store logs"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Identity' ID generation downside?",
        "options": {
            "A": "It is not secure",
            "B": "It disables Hibernate's 'Batch Insert' optimization because the ID is only known after the insert occurs",
            "C": "It is only for Oracle",
            "D": "It requires manual entry"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation allows you to map a Map<String, Entity> where the key is a property of the target entity?",
        "options": {
            "A": "@MapKey",
            "B": "@JoinTable",
            "C": "@ElementCollection",
            "D": "@KeyMapping"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Bytecode Enhancement' in Hibernate?",
        "options": {
            "A": "Writing faster Java code",
            "B": "A process of modifying entity classes at compile-time to provide features like field-level lazy loading and better performance",
            "C": "Encrypting the .class files",
            "D": "A type of L2 cache"
        },
        "answer": "B"
    },
    {
        "question": "Which method returns a 'Stream' of results in modern Hibernate/JPA?",
        "options": {
            "A": "list()",
            "B": "getResultStream()",
            "C": "stream()",
            "D": "Both B and C"
        },
        "answer": "D"
    },
    {
        "question": "What is a 'Composite Primary Key'?",
        "options": {
            "A": "A primary key made of two or more columns",
            "B": "A primary key that is also a foreign key",
            "C": "A primary key for a DTO",
            "D": "A hidden column"
        },
        "answer": "A"
    },
    {
        "question": "Which two annotations can be used to define a Composite Primary Key?",
        "options": {
            "A": "@IdClass and @EmbeddedId",
            "B": "@Composite and @MultiId",
            "C": "@Id and @Key",
            "D": "@Table and @Column"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Soft Delete' implementation in Hibernate?",
        "options": {
            "A": "Deleting data from the cache only",
            "B": "Using a flag (like is_deleted) instead of physically removing a row, typically implemented via @SQLDelete and @Where",
            "C": "Deleting data after 1 hour",
            "D": "A type of L2 cache"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to filter out 'Soft Deleted' records automatically in all queries?",
        "options": {
            "A": "@Filter",
            "B": "@Where",
            "C": "@Exclude",
            "D": "@Hide"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Immutable Entity' (@Immutable)?",
        "options": {
            "A": "An entity that cannot be deleted",
            "B": "An entity whose state cannot be changed once persisted; Hibernate ignores any updates to it for performance",
            "C": "A read-only database",
            "D": "A static class"
        },
        "answer": "B"
    },
    {
        "question": "What does @DynamicUpdate do?",
        "options": {
            "A": "Speeds up the DB",
            "B": "Ensures that the generated SQL UPDATE statement only includes columns that have actually changed",
            "C": "Automatically updates the schema",
            "D": "Updates the UI"
        },
        "answer": "B"
    },
    {
        "question": "Which Hibernate feature allows you to intercept every SQL statement before it is executed?",
        "options": {
            "A": "Interceptor",
            "B": "StatementInspector",
            "C": "Both A and B",
            "D": "EntityListener"
        },
        "answer": "C"
    },
    {
        "question": "What is 'Natural Id' (@NaturalId)?",
        "options": {
            "A": "The primary key",
            "B": "A business key that uniquely identifies an entity in the real world (e.g., SSN or Email), allowing for specialized caching",
            "C": "A random number",
            "D": "An auto-increment ID"
        },
        "answer": "B"
    },
    {
        "question": "How do you enable 'L2 Caching' for a specific entity?",
        "options": {
            "A": "It is enabled by default",
            "B": "Using @Cacheable (JPA) or @Cache (Hibernate)",
            "C": "Using @Static",
            "D": "Configuring the L1 cache"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Cache Concurrency Strategy'?",
        "options": {
            "A": "The speed of the cache",
            "B": "A setting that defines how the cache handles concurrent access (e.g., READ_ONLY, NONSTRICT_READ_WRITE)",
            "C": "A database index",
            "D": "A transaction type"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Multi-tenancy' in Hibernate?",
        "options": {
            "A": "Having many users",
            "B": "An architecture where a single instance of the application serves multiple customers (tenants) with isolated data",
            "C": "A type of L2 cache",
            "D": "A security setting"
        },
        "answer": "B"
    },
    {
        "question": "Which interface is used to resolve the current tenant ID in a multi-tenant application?",
        "options": {
            "A": "TenantResolver",
            "B": "CurrentTenantIdentifierResolver",
            "C": "SessionIdentifier",
            "D": "TenantProvider"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'session.isDirty()' method?",
        "options": {
            "A": "To check if the database is corrupt",
            "B": "To check if the current Session contains any pending changes that need to be flushed",
            "C": "To check for security vulnerabilities",
            "D": "To check if the connection is open"
        },
        "answer": "B"
    },
    {
        "question": "What is 'StatelessSession'?",
        "options": {
            "A": "A session for web apps",
            "B": "A command-oriented API that does not use a persistence context (L1 cache) or dirty checking, ideal for bulk operations",
            "C": "A session that never times out",
            "D": "A legacy object"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to specify a custom naming strategy for tables and columns?",
        "options": {
            "A": "@Naming",
            "B": "ImplicitNamingStrategy / PhysicalNamingStrategy (configured in properties)",
            "C": "@Alias",
            "D": "@ColumnName"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Envers' in the Hibernate ecosystem?",
        "options": {
            "A": "A testing tool",
            "B": "A library for entity versioning and auditing, allowing you to track historical changes to data",
            "C": "A performance monitor",
            "D": "A security framework"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 2: Which method is used to manually synchronize the entity state from the database back into the managed entity instance?",
        "options": {
            "A": "session.refresh()",
            "B": "session.update()",
            "C": "session.merge()",
            "D": "session.sync()"
        },
        "answer": "A"
    },
    {
        "question": "Which caching provider is most commonly integrated with Hibernate for L2 caching?",
        "options": {
            "A": "Redis",
            "B": "Ehcache",
            "C": "Hazelcast",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "What is the 'Connection Release Mode' in Hibernate?",
        "options": {
            "A": "The speed of closing a connection",
            "B": "A configuration that determines when Hibernate returns a JDBC connection to the pool (e.g., after each statement or after a transaction)",
            "C": "A security setting for remote DBs",
            "D": "A way to delete idle connections"
        },
        "answer": "B"
    },
    {
        "question": "How can you solve the N+1 problem using HQL/JPQL?",
        "options": {
            "A": "Use 'JOIN FETCH' in your query",
            "B": "Use 'SELECT DISTINCT'",
            "C": "Use 'ORDER BY'",
            "D": "It cannot be solved via query"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of the 'Entity Graph' in JPA 2.1?",
        "options": {
            "A": "To visualize the database schema",
            "B": "To define a template for fetching an entity and its associations, allowing for dynamic control over Eager vs Lazy loading",
            "C": "To create a chart of entity growth",
            "D": "To map entities to a graph database"
        },
        "answer": "B"
    },
    {
        "question": "Which Spring Data JPA interface provides built-in methods for CRUD operations and Pagination?",
        "options": {
            "A": "JpaRepository",
            "B": "CrudRepository",
            "C": "PagingAndSortingRepository",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Query Derivation' in Spring Data JPA?",
        "options": {
            "A": "Deriving SQL from HQL",
            "B": "Automatically generating the query logic based on the method name in the Repository interface (e.g., findByEmail)",
            "C": "Calculating the speed of a query",
            "D": "Mapping a query to a DTO"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used in Spring Data JPA to execute a custom Native SQL or JPQL query?",
        "options": {
            "A": "@Native",
            "B": "@Query",
            "C": "@SQL",
            "D": "@Execute"
        },
        "answer": "B"
    },
    {
        "question": "What does the @Modifying annotation do in Spring Data JPA?",
        "options": {
            "A": "Allows the user to modify the entity",
            "B": "Indicates that a query performs an UPDATE, INSERT, or DELETE operation rather than a SELECT",
            "C": "Changes the table schema",
            "D": "Refreshes the L1 cache"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Pessimistic Write' lock (@Lock(LockModeType.PESSIMISTIC_WRITE))?",
        "options": {
            "A": "A lock that assumes the transaction will fail",
            "B": "A lock that prevents other transactions from reading or writing to the row until the current one finishes",
            "C": "A lock for static tables",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Query Plan Cache'?",
        "options": {
            "A": "A cache for query results",
            "B": "A cache that stores the translated SQL version of HQL/JPQL queries to avoid repeated parsing overhead",
            "C": "A backup of the database",
            "D": "A type of index"
        },
        "answer": "B"
    },
    {
        "question": "Which interface allows you to define custom persistence logic that Spring Data JPA can then incorporate into its repository?",
        "options": {
            "A": "JpaRepositoryCustom",
            "B": "CustomPersistence",
            "C": "RepositoryLogic",
            "D": "PersistenceContext"
        },
        "answer": "A"
    },
    {
        "question": "What is 'FlushMode.COMMIT'?",
        "options": {
            "A": "Flushing after every line of code",
            "B": "The Session is only flushed when the transaction is committed",
            "C": "Flushing manually only",
            "D": "Deleting the cache"
        },
        "answer": "B"
    },
    {
        "question": "What is 'FlushMode.AUTO'?",
        "options": {
            "A": "Flushing only at the end",
            "B": "Hibernate decides when to flush, typically before executing a query to ensure results are consistent with in-memory changes",
            "C": "Flushing every 10 seconds",
            "D": "A type of L2 cache"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Statement Batching' size configuration?",
        "options": {
            "A": "The size of the SQL file",
            "B": "The number of similar SQL statements grouped together in a single JDBC batch to reduce network round-trips",
            "C": "The number of users",
            "D": "The RAM usage"
        },
        "answer": "B"
    },
    {
        "question": "What is 'DetachedCriteria'?",
        "options": {
            "A": "A query that has failed",
            "B": "A Criteria query created outside the scope of a Session, which can be executed later by passing it to any Session",
            "C": "A deleted entity",
            "D": "A type of subquery"
        },
        "answer": "B"
    },
    {
        "question": "Which tool provides a GUI to browse Hibernate L2 cache content?",
        "options": {
            "A": "Hibernate Console",
            "B": "JMX (Java Management Extensions) beans",
            "C": "SQL Developer",
            "D": "Browser console"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Natural Id' caching?",
        "options": {
            "A": "Caching the primary key",
            "B": "A specialized L2 cache that allows looking up an entity by its business key (@NaturalId) without hitting the database",
            "C": "Caching the file system",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to mark a field as the 'Version' for Optimistic Locking in Spring Data JPA?",
        "options": {
            "A": "@Version",
            "B": "@Sequence",
            "C": "@Lock",
            "D": "@Id"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Projections' in Spring Data JPA?",
        "options": {
            "A": "Displaying the DB on a screen",
            "B": "A way to fetch only specific fields of an entity (using interfaces or DTOs) rather than the whole object",
            "C": "A type of join",
            "D": "Calculating the future size of the DB"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'CGLIB' proxy vs 'JDK' proxy in Hibernate?",
        "options": {
            "A": "JDK is for interfaces; CGLIB is used to proxy classes directly",
            "B": "CGLIB is only for mobile",
            "C": "JDK is faster",
            "D": "There is no difference"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Hibernate Statistics'?",
        "options": {
            "A": "The number of developers using it",
            "B": "An API that provides metrics like cache hit ratios, query execution times, and connection usage",
            "C": "A type of unit test",
            "D": "A security report"
        },
        "answer": "B"
    },
    {
        "question": "Which property enables SQL logging in Hibernate?",
        "options": {
            "A": "hibernate.show_sql",
            "B": "hibernate.log_sql",
            "C": "hibernate.print_sql",
            "D": "hibernate.trace_sql"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of the 'hibernate.format_sql' property?",
        "options": {
            "A": "To convert SQL to HQL",
            "B": "To make the logged SQL more readable by adding indentation and line breaks",
            "C": "To change the database schema",
            "D": "To encrypt the SQL"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Bytecode Instrumentation' used for in lazy loading?",
        "options": {
            "A": "To hide the code",
            "B": "To enable lazy loading of individual basic attributes (like a large CLOB/BLOB) rather than just associations",
            "C": "To speed up the JVM",
            "D": "A type of L2 cache"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to map a list where the order is maintained by a dedicated column in the database?",
        "options": {
            "A": "@OrderBy",
            "B": "@OrderColumn",
            "C": "@Sort",
            "D": "@Sequence"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Collection Fetching' in Hibernate performance?",
        "options": {
            "A": "Fetching all tables",
            "B": "The strategy for loading a collection (e.g., using a join, a separate select, or a subselect)",
            "C": "A security scan",
            "D": "A backup tool"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Subselect' fetch mode advantage?",
        "options": {
            "A": "It is faster for single entities",
            "B": "It fetches all collections for all parents loaded in the previous query using a single sub-query, avoiding N+1",
            "C": "It requires less memory",
            "D": "It works on all databases"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Transaction Propagation' in Spring (@Transactional)?",
        "options": {
            "A": "The speed of the transaction",
            "B": "A setting that determines how a new transaction relates to an existing one (e.g., REQUIRED, REQUIRES_NEW)",
            "C": "A type of join",
            "D": "Deleting the logs"
        },
        "answer": "B"
    },
    {
        "question": "What does 'Propagation.REQUIRES_NEW' do?",
        "options": {
            "A": "Uses the existing transaction",
            "B": "Suspends the current transaction and starts a completely new one",
            "C": "Fails if no transaction exists",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Read-Only' flag in @Transactional used for?",
        "options": {
            "A": "To block the database",
            "B": "To optimize the session by disabling dirty checking since no changes are expected",
            "C": "To protect the code",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "Which class is used to manually handle Transactions in a Spring Boot application?",
        "options": {
            "A": "TransactionTemplate",
            "B": "PlatformTransactionManager",
            "C": "Both A and B",
            "D": "JdbcTemplate"
        },
        "answer": "C"
    },
    {
        "question": "What is 'Attribute Converter' (@Converter) in JPA?",
        "options": {
            "A": "Converting XML to JSON",
            "B": "A way to define custom logic for mapping a Java type to a database column (e.g., Boolean to 'Y'/'N')",
            "C": "A type of join",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Dirty Generation' in Hibernate 6?",
        "options": {
            "A": "Detecting changes in entities",
            "B": "The improved mechanism for detecting changes that is more performant than previous versions",
            "C": "Generating random data",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to handle 'Conflict' in Version-based optimistic locking?",
        "options": {
            "A": "OptimisticLockException (thrown by JPA)",
            "B": "@Conflict",
            "C": "@Catch",
            "D": "@Retry"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Database Sharding' in the context of Hibernate?",
        "options": {
            "A": "Deleting parts of the DB",
            "B": "Distributing data across multiple physical database instances to improve scalability",
            "C": "A type of index",
            "D": "A security framework"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Default' cache provider if none is specified?",
        "options": {
            "A": "Ehcache",
            "B": "No L2 cache is enabled by default",
            "C": "In-memory Map",
            "D": "Redis"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Query Hint' in JPA?",
        "options": {
            "A": "A tip for the developer",
            "B": "A way to pass provider-specific information (like timeout or cache settings) to the JPA engine",
            "C": "A type of subquery",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Self-Invocation' problem with Spring @Transactional?",
        "options": {
            "A": "Calling a method on another server",
            "B": "When a method in a class calls another @Transactional method in the same class, the proxy is bypassed and the transaction doesn't start",
            "C": "A memory leak",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "Which interface is used to define 'Specifications' for dynamic Criteria queries in Spring Data JPA?",
        "options": {
            "A": "JpaSpecificationExecutor",
            "B": "CriteriaBuilder",
            "C": "Querydsl",
            "D": "DynamicRepository"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Querydsl'?",
        "options": {
            "A": "A type of database",
            "B": "A framework that provides a type-safe way to write queries using a fluent API, often used with Spring Data",
            "C": "A reporting tool",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Audit Logging' in Hibernate Envers?",
        "options": {
            "A": "Logging the SQL",
            "B": "Automatically creating a 'shadow' table that stores every change made to an entity with a timestamp and revision number",
            "C": "A performance report",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation enables auditing for a specific entity in Envers?",
        "options": {
            "A": "@Audit",
            "B": "@Audited",
            "C": "@Version",
            "D": "@History"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Bulk Operations' in HQL?",
        "options": {
            "A": "Running queries on a weekend",
            "B": "Using UPDATE or DELETE statements in HQL that affect multiple rows at once (executes directly against the DB)",
            "C": "Fetching 1 million rows",
            "D": "A type of L2 cache"
        },
        "answer": "B"
    },
    {
        "question": "What is the danger of Bulk Operations in Hibernate?",
        "options": {
            "A": "They are slow",
            "B": "They bypass the Persistence Context (L1 cache) and lifecycle interceptors, meaning managed entities may become out of sync",
            "C": "They only work on MySQL",
            "D": "A security scan result"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Identifier' of an entity?",
        "options": {
            "A": "Its class name",
            "B": "The primary key value that uniquely identifies the entity in the database and the Session",
            "C": "The user's email",
            "D": "The database name"
        },
        "answer": "B"
    },
    {
        "question": "Which class is the entry point for configuring Hibernate programmatically?",
        "options": {
            "A": "Configuration",
            "B": "Bootstrapping",
            "C": "SessionFactoryBuilder",
            "D": "Metadata"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Connection Pooling' library often used with Spring/Hibernate?",
        "options": {
            "A": "HikariCP",
            "B": "C3P0",
            "C": "DBCP",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Schema Validation' in Hibernate?",
        "options": {
            "A": "Checking if the DB is full",
            "B": "Ensuring that the database schema exactly matches the entity mappings without making any changes",
            "C": "Validating user passwords",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Which interface is used to create an 'EntityManager' in a JPA environment?",
        "options": {
            "A": "EntityManagerFactory",
            "B": "PersistenceContext",
            "C": "SessionBuilder",
            "D": "TransactionManager"
        },
        "answer": "A"
    },
    {
        "question": "Final question of Batch 3: What is the benefit of 'Soft Assertion' in Hibernate testing?",
        "options": {
            "A": "It speeds up the tests",
            "B": "It allows multiple assertions to fail and provides a report of all failures at the end",
            "C": "It ignores all errors",
            "D": "A security scan result"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'SQM' (Semantic Query Model) introduced in Hibernate 6?",
        "options": {
            "A": "A new database engine",
            "B": "A redesigned internal representation of HQL/JPQL queries that improves performance and stability",
            "C": "A type of L2 cache",
            "D": "A security encryption layer"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Fetch Graph' vs 'Load Graph' in JPA?",
        "options": {
            "A": "Fetch Graph treats all unlisted attributes as Lazy; Load Graph treats them according to their default mapping",
            "B": "They are identical",
            "C": "Fetch Graph is for UI; Load Graph for DB",
            "D": "Load Graph is only for mobile apps"
        },
        "answer": "A"
    },
    {
        "question": "Which Hibernate feature is used to handle 'Multi-tenancy' by adding a discriminator column to shared tables?",
        "options": {
            "A": "SCHEMA strategy",
            "B": "DATABASE strategy",
            "C": "DISCRIMINATOR strategy",
            "D": "SHARED strategy"
        },
        "answer": "C"
    },
    {
        "question": "What is the 'N+1 Select' solution that uses a single join instead of multiple selects?",
        "options": {
            "A": "Join Fetching",
            "B": "Batch Fetching",
            "C": "Subselect Fetching",
            "D": "Eager Loading"
        },
        "answer": "A"
    },
    {
        "question": "What does 'hibernate.jdbc.batch_versioned_data' enable?",
        "options": {
            "A": "Batching of deletes",
            "B": "Batching of updates/inserts for entities that use versioning (@Version)",
            "C": "Versioning the logs",
            "D": "Security scanning"
        },
        "answer": "B"
    },
    {
        "question": "Which interface allows you to define a custom ID generation logic in Hibernate 6?",
        "options": {
            "A": "IdentifierGenerator",
            "B": "IdProvider",
            "C": "SequenceManager",
            "D": "CustomId"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Connection Monitoring' useful for in production?",
        "options": {
            "A": "Checking the internet speed",
            "B": "Detecting leaked or long-running database connections via Hibernate Statistics",
            "C": "A performance report",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "How do you map a JSON column in PostgreSQL to a Java Map using Hibernate 6?",
        "options": {
            "A": "Using @JdbcTypeCode(SqlTypes.JSON)",
            "B": "Using @Type(JsonType.class)",
            "C": "Using @JsonColumn",
            "D": "Both A and B"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Attribute Converter' autoApply=true for?",
        "options": {
            "A": "To apply the converter to all entities globally for the matching Java type",
            "B": "To speed up the app",
            "C": "To delete the attribute",
            "D": "To refresh the cache"
        },
        "answer": "A"
    },
    {
        "question": "Which Hibernate 6 feature allows for 'Type-safe' sorting in Criteria queries?",
        "options": {
            "A": "Order objects",
            "B": "Metamodel classes",
            "C": "SQM parser",
            "D": "Static sorting"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'EntityGraph' in Spring Data JPA?",
        "options": {
            "A": "To draw a flowchart",
            "B": "To define a group of attributes to be fetched eagerly in a specific repository method",
            "C": "To visualize relationships",
            "D": "To monitor SQL growth"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Transaction Isolation Level'?",
        "options": {
            "A": "The speed of the transaction",
            "B": "A setting that determines how one transaction is isolated from the effects of others (e.g., READ_COMMITTED)",
            "C": "A security firewall",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Dirty Read'?",
        "options": {
            "A": "Reading a corrupt file",
            "B": "When a transaction reads data that has been modified by another concurrent transaction but not yet committed",
            "C": "A database index",
            "D": "A security scan result"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Phantom Read'?",
        "options": {
            "A": "Reading a deleted file",
            "B": "When a transaction retrieves a set of rows twice and finds that a new row has been added by another transaction in between",
            "C": "A performance bug",
            "D": "A security vulnerability"
        },
        "answer": "B"
    },
    {
        "question": "Which isolation level prevents 'Dirty Reads' but allows 'Non-repeatable reads'?",
        "options": {
            "A": "READ_UNCOMMITTED",
            "B": "READ_COMMITTED",
            "C": "REPEATABLE_READ",
            "D": "SERIALIZABLE"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Session.doWork()' used for?",
        "options": {
            "A": "To start a background job",
            "B": "To execute raw JDBC code while staying within the current Hibernate Session and Transaction",
            "C": "To update the UI",
            "D": "To clear the cache"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Flush' cost in large sessions?",
        "options": {
            "A": "Increased memory usage",
            "B": "High CPU overhead as Hibernate iterates through all managed entities to check for changes",
            "C": "Database lockdown",
            "D": "Network latency"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Query.setHint(SpecHints.HINT_SPEC_FETCH_GRAPH, graph)' used for?",
        "options": {
            "A": "To ignore the cache",
            "B": "To apply a specific JPA EntityGraph to a query at runtime",
            "C": "To speed up the server",
            "D": "To delete a graph"
        },
        "answer": "B"
    },
    {
        "question": "In Hibernate 6, what replaces the legacy 'Criteria' API?",
        "options": {
            "A": "HQL only",
            "B": "JPA Criteria API (standardized)",
            "C": "SQL only",
            "D": "Metadata API"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Hibernate.initialize(proxy)'?",
        "options": {
            "A": "To start Hibernate",
            "B": "To manually force the loading (initialization) of a lazy-loaded object or collection",
            "C": "To create a new DB",
            "D": "To reset the Session"
        },
        "answer": "B"
    },
    {
        "question": "What is 'LockMode.NONE'?",
        "options": {
            "A": "No locking occurs",
            "B": "The record is locked for 1 second",
            "C": "The user is logged out",
            "D": "A security scanner"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Implicit Join' in HQL?",
        "options": {
            "A": "A join that is hidden",
            "B": "Navigating associations using the dot (.) operator in a query (e.g., employee.department.name)",
            "C": "A type of subquery",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Cartesian Product' risk in Hibernate?",
        "options": {
            "A": "Mathematical error in pricing",
            "B": "Fetching multiple collections simultaneously using JOIN FETCH, leading to a massive, redundant result set",
            "C": "A performance metric",
            "D": "A type of sharding"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to map a Java 'Enum' as an ordinal in Hibernate?",
        "options": {
            "A": "@Enumerated(EnumType.ORDINAL)",
            "B": "@Enum",
            "C": "@Mapping(ENUM)",
            "D": "@Id"
        },
        "answer": "A"
    },
    {
        "question": "What is the 'Session.getTenantId()' method for?",
        "options": {
            "A": "To get the user's ID",
            "B": "To retrieve the ID of the current tenant in a multi-tenant environment",
            "C": "To monitor the DB",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation allows for 'Polymorphic' queries across multiple entities?",
        "options": {
            "A": "@Inheritance",
            "B": "@Entity",
            "C": "@DiscriminatorValue",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Query Pagination' memory risk?",
        "options": {
            "A": "Using setMaxResults() with JOIN FETCH of collections can lead to incorrect results or memory issues",
            "B": "It uses no memory",
            "C": "It is too slow",
            "D": "It deletes data"
        },
        "answer": "A"
    },
    {
        "question": "Which class provides a 'Stateless' way to interact with the database in Hibernate?",
        "options": {
            "A": "StatelessSession",
            "B": "Session",
            "C": "EntityManager",
            "D": "Connection"
        },
        "answer": "A"
    },
    {
        "question": "What is 'LockMode.PESSIMISTIC_FORCE_INCREMENT'?",
        "options": {
            "A": "Forces a version increment even if no changes were made to the entity",
            "B": "Speeds up the DB",
            "C": "A security scan",
            "D": "A performance report"
        },
        "answer": "A"
    },
    {
        "question": "What is 'JPA Entity Listener'?",
        "options": {
            "A": "A class that listens to music",
            "B": "A separate class that contains lifecycle callback methods for entities",
            "C": "A database trigger",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Attribute Override' on a collection of embeddables?",
        "options": {
            "A": "@AssociationOverride",
            "B": "@AttributeOverride",
            "C": "Both are used depending on the mapping",
            "D": "@Column"
        },
        "answer": "C"
    },
    {
        "question": "Which interface handles 'ID Generation' via an external database sequence?",
        "options": {
            "A": "SequenceGenerator",
            "B": "TableGenerator",
            "C": "IdentityGenerator",
            "D": "None"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Auto-flush' trigger?",
        "options": {
            "A": "Before any HQL/Criteria query is executed",
            "B": "Before transaction commit",
            "C": "Both A and B",
            "D": "Only manually"
        },
        "answer": "C"
    },
    {
        "question": "What is 'Subselect Fetching' advantage?",
        "options": {
            "A": "It is faster for 1 row",
            "B": "It fetchs collections for ALL parent objects from a previous query in one go",
            "C": "A security scan",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Natural Id' immutability?",
        "options": {
            "A": "The natural ID can never change",
            "B": "Hibernate can optimize lookups if it knows the natural ID is immutable",
            "C": "A type of sharding",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "Which class is the modern 'Bootstrapping' entry point for Hibernate 6?",
        "options": {
            "A": "StandardServiceRegistryBuilder",
            "B": "Configuration",
            "C": "MetadataSources",
            "D": "SessionFactory"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Query.setCacheable(true)' for?",
        "options": {
            "A": "To enable L1 cache",
            "B": "To store the results of this specific query in the L2 Query Cache",
            "C": "To delete the cache",
            "D": "To speed up the network"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Envers' default table suffix?",
        "options": {
            "A": "_HISTORY",
            "B": "_AUD",
            "C": "_REV",
            "D": "_LOG"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to create a 'One-to-One' mapping using a shared primary key?",
        "options": {
            "A": "@PrimaryKeyJoinColumn",
            "B": "@JoinColumn",
            "C": "@MapsId",
            "D": "Both A and C"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Session.unwrap(Connection.class)' for?",
        "options": {
            "A": "To get the JDBC connection",
            "B": "To delete the session",
            "C": "To restart the DB",
            "D": "A security scanner"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Dialect' auto-detection?",
        "options": {
            "A": "Hibernate automatically choosing the SQL dialect based on the database metadata",
            "B": "A security scan",
            "C": "A performance report",
            "D": "A type of sharding"
        },
        "answer": "A"
    },
    {
        "question": "What is 'LockMode.UPGRADE'?",
        "options": {
            "A": "A legacy lock mode equivalent to PESSIMISTIC_WRITE",
            "B": "Upgrading the database",
            "C": "A performance report",
            "D": "A security scanner"
        },
        "answer": "A"
    },
    {
        "question": "Which annotation provides a way to define 'Dynamic Filters' on an entity?",
        "options": {
            "A": "@FilterDef",
            "B": "@Filter",
            "C": "Both are needed",
            "D": "@Where"
        },
        "answer": "C"
    },
    {
        "question": "What is 'Batch Size' on a collection mapping?",
        "options": {
            "A": "How many items in the list",
            "B": "How many collections to fetch in one query using IN clause",
            "C": "A performance report",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Persistence Unit' in JPA?",
        "options": {
            "A": "A grouping of entities and their configuration settings defined in persistence.xml",
            "B": "A single entity",
            "C": "A database table",
            "D": "A security certificate"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Detached' entity risk?",
        "options": {
            "A": "It can be deleted easily",
            "B": "Changes made to it are not tracked by Hibernate until it is merged/updated",
            "C": "A security scanner",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation handles 'Multi-column' mapping of a single Java property?",
        "options": {
            "A": "@Columns",
            "B": "@Composite",
            "C": "Custom @Type (UserType)",
            "D": "Both A and C"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Session.refresh()' purpose?",
        "options": {
            "A": "To clear the cache",
            "B": "To reload the entity state from the DB, overwriting any unsaved local changes",
            "C": "To update the DB",
            "D": "To close the session"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Hibernate Search'?",
        "options": {
            "A": "A tool to search the logs",
            "B": "An extension that provides full-text search (Lucene/Elasticsearch) for persistent entities",
            "C": "A security framework",
            "D": "A performance monitor"
        },
        "answer": "B"
    },
    {
        "question": "Final question: What is the primary advantage of Hibernate 6 over previous versions?",
        "options": {
            "A": "Native JSON support and a faster internal query engine (SQM)",
            "B": "It is written in Python",
            "C": "It does not use SQL",
            "D": "It has no annotations"
        },
        "answer": "A"
    },
    
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
    skill = "Hibernate"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
