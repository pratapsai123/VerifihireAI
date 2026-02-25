from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
    {
        "question": "What does DBMS stand for?",
        "options": {
            "A": "Data Binary Management System",
            "B": "Database Management System",
            "C": "Database Management Service",
            "D": "Data Backup Management System"
        },
        "answer": "B"
    },
    {
        "question": "Which of the following is considered a Relational Database?",
        "options": {
            "A": "MongoDB",
            "B": "Redis",
            "C": "MySQL",
            "D": "Cassandra"
        },
        "answer": "C"
    },
    {
        "question": "What is the primary purpose of a 'Primary Key'?",
        "options": {
            "A": "To encrypt the database",
            "B": "To uniquely identify each record in a table",
            "C": "To allow duplicate values",
            "D": "To link two databases together"
        },
        "answer": "B"
    },
    {
        "question": "Which SQL command is used to retrieve data from a database?",
        "options": {
            "A": "INSERT",
            "B": "SELECT",
            "C": "UPDATE",
            "D": "DELETE"
        },
        "answer": "B"
    },
    {
        "question": "Which clause is used to filter rows in a SELECT statement?",
        "options": {
            "A": "GROUP BY",
            "B": "ORDER BY",
            "C": "WHERE",
            "D": "HAVING"
        },
        "answer": "C"
    },
    {
        "question": "What is a 'Foreign Key'?",
        "options": {
            "A": "A key used to unlock a database",
            "B": "A column in one table that points to the Primary Key of another table",
            "C": "A key that cannot be null",
            "D": "A key used only in NoSQL databases"
        },
        "answer": "B"
    },
    {
        "question": "Which relationship exists when a student can enroll in many courses and a course can have many students?",
        "options": {
            "A": "One-to-One",
            "B": "One-to-Many",
            "C": "Many-to-Many",
            "D": "Many-to-One"
        },
        "answer": "C"
    },
    {
        "question": "What is 'Referential Integrity'?",
        "options": {
            "A": "The speed of the database",
            "B": "A rule ensuring that relationships between tables remain consistent",
            "C": "The backup of the database",
            "D": "The encryption level"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to remove a table and its data permanently?",
        "options": {
            "A": "DELETE",
            "B": "TRUNCATE",
            "C": "DROP",
            "D": "REMOVE"
        },
        "answer": "C"
    },
    {
        "question": "What does the 'ACID' acronym stand for in database transactions?",
        "options": {
            "A": "Access, Control, Integrity, Data",
            "B": "Atomicity, Consistency, Isolation, Durability",
            "C": "Allocation, Computation, Integration, Distribution",
            "D": "Auto, Check, Index, Delete"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Data Redundancy'?",
        "options": {
            "A": "Storing data in multiple locations to prevent loss",
            "B": "Unnecessary duplication of data within a database",
            "C": "The process of deleting old data",
            "D": "The speed of data transfer"
        },
        "answer": "B"
    },
    {
        "question": "Which normal form deals with removing partial functional dependencies?",
        "options": {
            "A": "1NF",
            "B": "2NF",
            "C": "3NF",
            "D": "BCNF"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Data Warehouse'?",
        "options": {
            "A": "A physical building for servers",
            "B": "A large collection of data used for decision-making and analysis",
            "C": "A temporary storage for user files",
            "D": "The same thing as a regular database"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is a Non-Relational (NoSQL) database?",
        "options": {
            "A": "Oracle",
            "B": "PostgreSQL",
            "C": "MongoDB",
            "D": "SQL Server"
        },
        "answer": "C"
    },
    {
        "question": "What is an 'Index' in a database used for?",
        "options": {
            "A": "To create a list of users",
            "B": "To speed up data retrieval operations",
            "C": "To link different databases",
            "D": "To store large images"
        },
        "answer": "B"
    },
    {
        "question": "What does 'SQL' stand for?",
        "options": {
            "A": "Simple Query Language",
            "B": "Structured Query Language",
            "C": "System Query Logic",
            "D": "Standard Query List"
        },
        "answer": "B"
    },
    {
        "question": "Which SQL command is used to add new data to a table?",
        "options": {
            "A": "ADD",
            "B": "UPDATE",
            "C": "INSERT",
            "D": "CREATE"
        },
        "answer": "C"
    },
    {
        "question": "Which join returns all records from the left table and the matched records from the right table?",
        "options": {
            "A": "INNER JOIN",
            "B": "LEFT JOIN",
            "C": "RIGHT JOIN",
            "D": "FULL JOIN"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'View' in a database?",
        "options": {
            "A": "A physical table stored on disk",
            "B": "A virtual table based on the result-set of an SQL statement",
            "C": "A backup of the database",
            "D": "A tool to see the database schema"
        },
        "answer": "B"
    },
    {
        "question": "Which property of ACID ensures that a transaction is all or nothing?",
        "options": {
            "A": "Atomicity",
            "B": "Consistency",
            "C": "Isolation",
            "D": "Durability"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Database Sharding'?",
        "options": {
            "A": "Deleting parts of the database",
            "B": "Horizontal partitioning of data across multiple servers",
            "C": "The process of indexing",
            "D": "Encrypting the database"
        },
        "answer": "B"
    },
    {
        "question": "Which of the following is an example of a DDL (Data Definition Language) command?",
        "options": {
            "A": "SELECT",
            "B": "UPDATE",
            "C": "CREATE",
            "D": "INSERT"
        },
        "answer": "C"
    },
    {
        "question": "Which normal form removes transitive dependencies?",
        "options": {
            "A": "1NF",
            "B": "2NF",
            "C": "3NF",
            "D": "4NF"
        },
        "answer": "C"
    },
    {
        "question": "What is a 'Candidate Key'?",
        "options": {
            "A": "A key that is not unique",
            "B": "A set of columns that can uniquely identify a row",
            "C": "A key used for encryption",
            "D": "A foreign key in a child table"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'TRUNCATE' command do?",
        "options": {
            "A": "Deletes the table structure",
            "B": "Removes all records from a table without logging individual row deletions",
            "C": "Removes specific rows based on a condition",
            "D": "Renames the table"
        },
        "answer": "B"
    },
    {
        "question": "Which SQL aggregate function finds the average of a column?",
        "options": {
            "A": "MEAN()",
            "B": "AVG()",
            "C": "SUM()",
            "D": "COUNT()"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Stored Procedure'?",
        "options": {
            "A": "A way to save files in a database",
            "B": "A prepared SQL code that you can save and reuse",
            "C": "A backup process",
            "D": "A database configuration file"
        },
        "answer": "B"
    },
    {
        "question": "Which clause is used with aggregate functions to filter groups?",
        "options": {
            "A": "WHERE",
            "B": "HAVING",
            "C": "ORDER BY",
            "D": "LIMIT"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Database Replication'?",
        "options": {
            "A": "Deleting duplicate data",
            "B": "The process of copying data from one database to another for consistency",
            "C": "The same as database sharding",
            "D": "An error in data entry"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Database Schema'?",
        "options": {
            "A": "The physical hardware used",
            "B": "The logical structure of the database",
            "C": "A backup of the data",
            "D": "A list of database users"
        },
        "answer": "B"
    },
    {
        "question": "Which join returns only rows that have matching values in both tables?",
        "options": {
            "A": "LEFT JOIN",
            "B": "RIGHT JOIN",
            "C": "INNER JOIN",
            "D": "FULL JOIN"
        },
        "answer": "C"
    },
    {
        "question": "Which command is used to change existing data in a table?",
        "options": {
            "A": "CHANGE",
            "B": "MODIFY",
            "C": "UPDATE",
            "D": "SET"
        },
        "answer": "C"
    },
    {
        "question": "What is the result of a 'Cartesian Product' (CROSS JOIN)?",
        "options": {
            "A": "A combination of every row from the first table with every row from the second",
            "B": "Only matching rows",
            "C": "The sum of all columns",
            "D": "An error"
        },
        "answer": "A"
    },
    {
        "question": "Which of these is a DML (Data Manipulation Language) command?",
        "options": {
            "A": "CREATE",
            "B": "DROP",
            "C": "DELETE",
            "D": "ALTER"
        },
        "answer": "C"
    },
    {
        "question": "What is 'Database Denormalization'?",
        "options": {
            "A": "Increasing redundancy to improve read performance",
            "B": "Reducing redundancy to improve integrity",
            "C": "Deleting indexes",
            "D": "Combining different NoSQL databases"
        },
        "answer": "A"
    },
    {
        "question": "Which SQL operator is used to search for a specific pattern in a column?",
        "options": {
            "A": "IN",
            "B": "BETWEEN",
            "C": "LIKE",
            "D": "EXISTS"
        },
        "answer": "C"
    },
    {
        "question": "What does the 'DISTINCT' keyword do?",
        "options": {
            "A": "Returns unique values in a result set",
            "B": "Filters based on a condition",
            "C": "Sorts the data",
            "D": "Calculates the sum"
        },
        "answer": "A"
    },
    {
        "question": "What is a 'Trigger'?",
        "options": {
            "A": "A user-initiated command",
            "B": "A procedural code that automatically executes in response to certain events on a table",
            "C": "A type of primary key",
            "D": "A database error"
        },
        "answer": "B"
    },
    {
        "question": "Which of these represents a 'Weak Entity' in an ER diagram?",
        "options": {
            "A": "An entity that has no primary key of its own",
            "B": "An entity with few attributes",
            "C": "A table with no rows",
            "D": "A temporary table"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Data Independence'?",
        "options": {
            "A": "The ability to change the schema at one level without affecting the higher level",
            "B": "Storing data on separate hard drives",
            "C": "Using NoSQL instead of SQL",
            "D": "Allowing users to access data without a password"
        },
        "answer": "A"
    },
    {
        "question": "Which SQL command is used to give a user permissions?",
        "options": {
            "A": "GIVE",
            "B": "ALLOW",
            "C": "GRANT",
            "D": "ASSIGN"
        },
        "answer": "C"
    },
    {
        "question": "What is the default port for PostgreSQL?",
        "options": {
            "A": "3306",
            "B": "1433",
            "C": "5432",
            "D": "1521"
        },
        "answer": "C"
    },
    {
        "question": "What is 'Metadata'?",
        "options": {
            "A": "Large amounts of data",
            "B": "Data about data",
            "C": "Encrypted data",
            "D": "Deleted data"
        },
        "answer": "B"
    },
    {
        "question": "Which property of ACID ensures that data remains in a valid state after a transaction?",
        "options": {
            "A": "Atomicity",
            "B": "Consistency",
            "C": "Isolation",
            "D": "Durability"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Entity-Relationship Diagram' (ERD)?",
        "options": {
            "A": "A chart of database users",
            "B": "A visual representation of the entities and their relationships within a database",
            "C": "A performance report",
            "D": "A list of SQL queries"
        },
        "answer": "B"
    },
    {
        "question": "Which SQL keyword is used to sort the result-set?",
        "options": {
            "A": "SORT BY",
            "B": "ARRANGE BY",
            "C": "ORDER BY",
            "D": "RANK BY"
        },
        "answer": "C"
    },
    {
        "question": "What is the purpose of 'COMMIT' in SQL?",
        "options": {
            "A": "To undo changes",
            "B": "To permanently save the changes made in a transaction",
            "C": "To close the connection",
            "D": "To create a new table"
        },
        "answer": "B"
    },
    {
        "question": "Which normal form removes partial dependencies?",
        "options": {
            "A": "1NF",
            "B": "2NF",
            "C": "3NF",
            "D": "BCNF"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Concurrency Control'?",
        "options": {
            "A": "Speeding up the database",
            "B": "Managing simultaneous operations on a database without conflict",
            "C": "Limiting the number of users",
            "D": "The process of backing up data"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is a popular Relational Database Management System?",
        "options": {
            "A": "Oracle",
            "B": "MySQL",
            "C": "PostgreSQL",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "What is the 'Query Optimizer' in a DBMS?",
        "options": {
            "A": "A person who writes fast queries",
            "B": "A software component that determines the most efficient way to execute a query",
            "C": "A tool for compressing data",
            "D": "A hardware upgrade for faster processing"
        },
        "answer": "B"
    },
    {
        "question": "Which level of the Three-Schema Architecture describes the physical storage structure?",
        "options": {
            "A": "External Level",
            "B": "Conceptual Level",
            "C": "Internal Level",
            "D": "Logical Level"
        },
        "answer": "C"
    },
    {
        "question": "What is a 'Deadlock' in a database?",
        "options": {
            "A": "A crashed server",
            "B": "A situation where two transactions are waiting for each other to release locks",
            "C": "A database with no records",
            "D": "An encrypted field"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is a 'Dense Index'?",
        "options": {
            "A": "An index that has an entry for every search key value in the data file",
            "B": "An index used only for strings",
            "C": "An index stored in a separate database",
            "D": "An index that is larger than the table itself"
        },
        "answer": "A"
    },
    {
        "question": "What is 'BCNF'?",
        "options": {
            "A": "Basic Core Normal Form",
            "B": "Boyce-Codd Normal Form",
            "C": "Binary Column Normal Form",
            "D": "Buffered Communication Normal Form"
        },
        "answer": "B"
    },
    {
        "question": "In the CAP theorem, what does 'P' stand for?",
        "options": {
            "A": "Performance",
            "B": "Partition Tolerance",
            "C": "Parallelism",
            "D": "Persistence"
        },
        "answer": "B"
    },
    {
        "question": "Which NoSQL category does 'Redis' primarily belong to?",
        "options": {
            "A": "Document Store",
            "B": "Graph Database",
            "C": "Key-Value Store",
            "D": "Column Family"
        },
        "answer": "C"
    },
    {
        "question": "What is a 'Composite Key'?",
        "options": {
            "A": "A key made of multiple tables",
            "B": "A primary key consisting of two or more columns",
            "C": "A hidden system key",
            "D": "An index for large files"
        },
        "answer": "B"
    },
    {
        "question": "Which SQL statement is used to undo a transaction that has not yet been committed?",
        "options": {
            "A": "UNDO",
            "B": "RESET",
            "C": "ROLLBACK",
            "D": "BACKOUT"
        },
        "answer": "C"
    },
    {
        "question": "What is the difference between 'DELETE' and 'DROP'?",
        "options": {
            "A": "DELETE removes data; DROP removes the entire table structure",
            "B": "DROP is faster than DELETE",
            "C": "DELETE is for NoSQL; DROP is for SQL",
            "D": "There is no difference"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Checkpointing' in a DBMS?",
        "options": {
            "A": "A security check for users",
            "B": "A point in time where the log and data are synchronized to disk",
            "C": "An index update",
            "D": "A way to count rows"
        },
        "answer": "B"
    },
    {
        "question": "Which NoSQL database type is best suited for social media networks (linking people)?",
        "options": {
            "A": "Key-Value",
            "B": "Document",
            "C": "Graph",
            "D": "Wide-column"
        },
        "answer": "C"
    },
    {
        "question": "What is 'Horizontal Scaling'?",
        "options": {
            "A": "Adding more RAM to a single server",
            "B": "Adding more servers to a database cluster",
            "C": "Updating the database version",
            "D": "Adding more columns to a table"
        },
        "answer": "B"
    },
    {
        "question": "Which SQL command is used to remove a specific column from an existing table?",
        "options": {
            "A": "DELETE COLUMN",
            "B": "REMOVE COLUMN",
            "C": "ALTER TABLE ... DROP COLUMN",
            "D": "DROP COLUMN"
        },
        "answer": "C"
    },
    {
        "question": "What is 'Dirty Read'?",
        "options": {
            "A": "Reading data that contains errors",
            "B": "Reading uncommitted data from another transaction",
            "C": "Reading data from a deleted table",
            "D": "A query that takes too much memory"
        },
        "answer": "B"
    },
    {
        "question": "What does 'Durability' ensure in ACID properties?",
        "options": {
            "A": "That data is accurate",
            "B": "That committed changes are permanent, even in the event of a system failure",
            "C": "That only one user can access data at a time",
            "D": "That the database is fast"
        },
        "answer": "B"
    },
    {
        "question": "What is 'OLTP'?",
        "options": {
            "A": "Online Logical Task Processing",
            "B": "Online Transaction Processing",
            "C": "Optimal Linear Time Protocol",
            "D": "Offline Table Loading Process"
        },
        "answer": "B"
    },
    {
        "question": "Which join returns all rows from the right table, and the matched records from the left table?",
        "options": {
            "A": "LEFT JOIN",
            "B": "RIGHT JOIN",
            "C": "FULL JOIN",
            "D": "INNER JOIN"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Clustered Index'?",
        "options": {
            "A": "An index that defines the physical order of data in the table",
            "B": "An index that clusters multiple tables together",
            "C": "An index that only works on numeric columns",
            "D": "A backup of the index"
        },
        "answer": "A"
    },
    {
        "question": "Which command is used to see the execution plan of an SQL query?",
        "options": {
            "A": "SHOW PLAN",
            "B": "EXPLAIN",
            "C": "QUERY INFO",
            "D": "ANALYZE"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Two-Phase Locking' (2PL)?",
        "options": {
            "A": "A locking protocol used to ensure serializability",
            "B": "A method to lock two different databases",
            "C": "A security feature for users",
            "D": "A way to speed up SELECT queries"
        },
        "answer": "A"
    },
    {
        "question": "Which SQL constraint ensures a column has a default value if none is provided?",
        "options": {
            "A": "SET DEFAULT",
            "B": "DEFAULT",
            "C": "FIXED",
            "D": "AUTO"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Normalization'?",
        "options": {
            "A": "To make the database larger",
            "B": "To minimize redundancy and prevent anomalies",
            "C": "To create more copies of data",
            "D": "To avoid using SQL"
        },
        "answer": "B"
    },
    {
        "question": "In database architecture, what is 'Concurrency'?",
        "options": {
            "A": "Storing data in order",
            "B": "The ability of a database to handle multiple users or transactions at the same time",
            "C": "The speed of the processor",
            "D": "A backup technique"
        },
        "answer": "B"
    },
    {
        "question": "Which type of NoSQL database is 'Cassandra'?",
        "options": {
            "A": "Document Store",
            "B": "Wide-column Store",
            "C": "Graph Store",
            "D": "Key-Value Store"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'System Catalog'?",
        "options": {
            "A": "A user manual",
            "B": "A repository of metadata that describes the database structure",
            "C": "A backup of the table rows",
            "D": "A list of all installed software"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Phantom Read'?",
        "options": {
            "A": "Reading data that was never there",
            "B": "When new rows are added by another transaction during a range query",
            "C": "A deleted record that still appears",
            "D": "A database error"
        },
        "answer": "B"
    },
    {
        "question": "Which SQL command is used to remove permissions from a user?",
        "options": {
            "A": "GRANT",
            "B": "TAKE",
            "C": "REVOKE",
            "D": "REMOVE"
        },
        "answer": "C"
    },
    {
        "question": "What is 'BASE' in NoSQL terminology?",
        "options": {
            "A": "Basic, Accessible, Stored, Encrypted",
            "B": "Basically Available, Soft state, Eventual consistency",
            "C": "Binary, Atomic, Sized, Extracted",
            "D": "Backup, Secure, Efficient"
        },
        "answer": "B"
    },
    {
        "question": "Which join is used to return only the rows that satisfy the join condition?",
        "options": {
            "A": "OUTER JOIN",
            "B": "INNER JOIN",
            "C": "LEFT JOIN",
            "D": "CROSS JOIN"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Cursor' in SQL?",
        "options": {
            "A": "A mouse pointer",
            "B": "A database object used to retrieve data from a result set one row at a time",
            "C": "A type of table",
            "D": "An error log"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Fragmentation' in a database?",
        "options": {
            "A": "Splitting data across multiple physical locations on disk",
            "B": "Deleting data",
            "C": "Creating a new schema",
            "D": "Adding a foreign key"
        },
        "answer": "A"
    },
    {
        "question": "Which SQL statement is used to rename a table?",
        "options": {
            "A": "UPDATE TABLE",
            "B": "RENAME TABLE / ALTER TABLE ... RENAME TO",
            "C": "CHANGE TABLE",
            "D": "SET TABLE"
        },
        "answer": "B"
    },
    {
        "question": "What is 'B-Tree' in databases?",
        "options": {
            "A": "A type of database software",
            "B": "A self-balancing tree data structure used for indexing",
            "C": "A backup method",
            "D": "A way to draw ER diagrams"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Foreign Key' constraints?",
        "options": {
            "A": "To increase speed",
            "B": "To ensure referential integrity",
            "C": "To allow null values",
            "D": "To group tables"
        },
        "answer": "B"
    },
    {
        "question": "What does 'Consistency' in CAP theorem mean?",
        "options": {
            "A": "The database is always fast",
            "B": "Every read receives the most recent write or an error",
            "C": "The data is backed up",
            "D": "The schema never changes"
        },
        "answer": "B"
    },
    {
        "question": "Which SQL keyword is used for pattern matching?",
        "options": {
            "A": "SAME",
            "B": "MATCH",
            "C": "LIKE",
            "D": "FIND"
        },
        "answer": "C"
    },
    {
        "question": "What is a 'Database Administrator' (DBA) responsible for?",
        "options": {
            "A": "Writing front-end code",
            "B": "Managing, securing, and maintaining the database system",
            "C": "Designing marketing posters",
            "D": "Buying new computers"
        },
        "answer": "B"
    },
    {
        "question": "Which join returns all rows from both tables when there is a match in either?",
        "options": {
            "A": "INNER JOIN",
            "B": "FULL OUTER JOIN",
            "C": "CROSS JOIN",
            "D": "NATURAL JOIN"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Cardinality' in an ER model?",
        "options": {
            "A": "The number of users",
            "B": "The number of instances of one entity that can be associated with another entity",
            "C": "The size of the database",
            "D": "The speed of the query"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Data Mining'?",
        "options": {
            "A": "The process of entering data",
            "B": "The process of discovering patterns in large data sets",
            "C": "Deleting old data",
            "D": "Backing up data"
        },
        "answer": "B"
    },
    {
        "question": "Which SQL command is used to add a new column to a table?",
        "options": {
            "A": "ADD COLUMN",
            "B": "INSERT COLUMN",
            "C": "ALTER TABLE ... ADD",
            "D": "SET COLUMN"
        },
        "answer": "C"
    },
    {
        "question": "What is 'Normalization' stage 1NF?",
        "options": {
            "A": "Removing duplicates",
            "B": "Ensuring each column contains atomic values and there are no repeating groups",
            "C": "Adding a foreign key",
            "D": "Creating a primary key"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Weak Entity'?",
        "options": {
            "A": "An entity that cannot be uniquely identified by its own attributes alone",
            "B": "A table with no data",
            "C": "A slow database",
            "D": "A database without a backup"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Denormalization' used for?",
        "options": {
            "A": "Improving data integrity",
            "B": "Improving read performance by introducing controlled redundancy",
            "C": "Reducing the database size",
            "D": "Adding more tables"
        },
        "answer": "B"
    },
    {
        "question": "What does 'Isolation' in ACID ensure?",
        "options": {
            "A": "Transactions are stored on separate disks",
            "B": "The concurrent execution of transactions results in a system state that would be obtained if transactions were executed serially",
            "C": "The database is not connected to the internet",
            "D": "Users cannot see each other's passwords"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to permanently remove all rows from a table, but keep the structure?",
        "options": {
            "A": "DROP",
            "B": "DELETE",
            "C": "TRUNCATE",
            "D": "REMOVE"
        },
        "answer": "C"
    },
    {
        "question": "What is 'ETL'?",
        "options": {
            "A": "Electronic Transfer Logic",
            "B": "Extract, Transform, Load",
            "C": "Estimated Time Limit",
            "D": "External Table Link"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Main Entry' in a database index called?",
        "options": {
            "A": "Record",
            "B": "Pointer",
            "C": "Search Key",
            "D": "Value"
        },
        "answer": "C"
    },
    {
        "question": "Which SQL clause is used to sort the results?",
        "options": {
            "A": "ORDER BY",
            "B": "GROUP BY",
            "C": "SORT BY",
            "D": "RANK BY"
        },
        "answer": "A"
    },
    {
        "question": "Which recovery technique involves undoing all transactions that were active at the time of a crash?",
        "options": {
            "A": "Deferred Update",
            "B": "Immediate Update",
            "C": "Shadow Paging",
            "D": "Log-based Recovery"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Polyglot Persistence'?",
        "options": {
            "A": "Using only one database for all needs",
            "B": "Using different data storage technologies for different data requirements within one application",
            "C": "A database that supports multiple languages",
            "D": "Encrypting data in multiple formats"
        },
        "answer": "B"
    },
    {
        "question": "Which type of lock prevents any other transaction from reading or writing the locked data?",
        "options": {
            "A": "Shared Lock (S)",
            "B": "Exclusive Lock (X)",
            "C": "Binary Lock",
            "D": "Intent Lock"
        },
        "answer": "B"
    },
    {
        "question": "In a B-Tree, what is the 'Fan-out'?",
        "options": {
            "A": "The number of rows in the table",
            "B": "The maximum number of children a node can have",
            "C": "The speed of the index",
            "D": "The process of deleting nodes"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'S' in BASE stand for?",
        "options": {
            "A": "Strict Consistency",
            "B": "Soft State",
            "C": "Secure Storage",
            "D": "Sequential Access"
        },
        "answer": "B"
    },
    {
        "question": "Which SQL command is used to create a virtual table from a query?",
        "options": {
            "A": "CREATE TABLE",
            "B": "CREATE VIEW",
            "C": "CREATE VIRTUAL",
            "D": "SET VIEW"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Materialized View'?",
        "options": {
            "A": "A view that is deleted after use",
            "B": "A view whose results are physically stored on disk for faster access",
            "C": "A view that only shows images",
            "D": "A database backup"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary difference between a B-Tree and a B+ Tree?",
        "options": {
            "A": "B+ Trees only store data pointers in the leaf nodes",
            "B": "B-Trees are faster for all queries",
            "C": "B+ Trees do not use keys",
            "D": "There is no difference"
        },
        "answer": "A"
    },
    {
        "question": "Which isolation level is the strictest and prevents all concurrency anomalies?",
        "options": {
            "A": "Read Committed",
            "B": "Repeatable Read",
            "C": "Serializable",
            "D": "Snapshot"
        },
        "answer": "C"
    },
    {
        "question": "What is 'Cascading Rollback'?",
        "options": {
            "A": "Rolling back a single transaction",
            "B": "A failure where rolling back one transaction causes others to roll back as well",
            "C": "A database update",
            "D": "A way to delete tables"
        },
        "answer": "B"
    },
    {
        "question": "Which NoSQL database uses 'Column Families' as its primary structure?",
        "options": {
            "A": "MongoDB",
            "B": "Apache Cassandra",
            "C": "Neo4j",
            "D": "Redis"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Vertical Partitioning'?",
        "options": {
            "A": "Splitting a table by rows",
            "B": "Splitting a table by columns into smaller tables with the same number of rows",
            "C": "Adding more RAM",
            "D": "Deleting columns"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Log' in a DBMS used for?",
        "options": {
            "A": "Storing user passwords",
            "B": "Recording all changes to the database for recovery purposes",
            "C": "Calculating query speed",
            "D": "A list of database software"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Normalization' 4NF designed to remove?",
        "options": {
            "A": "Transitive dependencies",
            "B": "Multi-valued dependencies",
            "C": "Partial dependencies",
            "D": "Join dependencies"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'REDO' operation in recovery?",
        "options": {
            "A": "To undo a failed transaction",
            "B": "To re-apply the changes of a committed transaction after a failure",
            "C": "To delete old data",
            "D": "To restart the server"
        },
        "answer": "B"
    },
    {
        "question": "Which type of join includes all rows from both tables, even those without matches?",
        "options": {
            "A": "Inner Join",
            "B": "Full Outer Join",
            "C": "Cross Join",
            "D": "Natural Join"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Write-Ahead Logging' (WAL)?",
        "options": {
            "A": "Writing data to the disk before the log",
            "B": "Writing transaction logs to stable storage before the data is updated on disk",
            "C": "Writing code before designing",
            "D": "A fast way to type SQL"
        },
        "answer": "B"
    },
    {
        "question": "In NoSQL, what is a 'Document'?",
        "options": {
            "A": "A PDF file",
            "B": "A set of key-value pairs (often JSON or BSON) that represents an object",
            "C": "A table row",
            "D": "A database schema"
        },
        "answer": "B"
    },
    {
        "question": "Which SQL command is used to modify the structure of an existing table?",
        "options": {
            "A": "UPDATE",
            "B": "ALTER",
            "C": "CHANGE",
            "D": "MODIFY"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Distributed Database'?",
        "options": {
            "A": "A database with many users",
            "B": "A single logical database that is physically spread across multiple computers",
            "C": "A database for distributors",
            "D": "A database stored in the cloud only"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Wait-Die' in deadlock prevention?",
        "options": {
            "A": "A way to stop a server",
            "B": "A timestamp-based protocol where older transactions wait and younger ones die",
            "C": "An error message",
            "D": "A manual restart"
        },
        "answer": "B"
    },
    {
        "question": "Which join returns all rows from the first table and matches from the second?",
        "options": {
            "A": "Right Join",
            "B": "Left Join",
            "C": "Inner Join",
            "D": "Cross Join"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Two-Phase Commit' (2PC) used for?",
        "options": {
            "A": "Locking a table",
            "B": "Ensuring a transaction is atomic across multiple distributed nodes",
            "C": "Speeding up local queries",
            "D": "Deleting duplicate rows"
        },
        "answer": "B"
    },
    {
        "question": "What does 'Eventual Consistency' mean?",
        "options": {
            "A": "The data is never consistent",
            "B": "If no new updates are made, all reads will eventually return the last updated value",
            "C": "The data is always consistent",
            "D": "Consistency is checked every 5 minutes"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Star Schema' in data warehousing?",
        "options": {
            "A": "A schema with no relationships",
            "B": "A central fact table surrounded by multiple dimension tables",
            "C": "A schema for astronomical data",
            "D": "A 3D database"
        },
        "answer": "B"
    },
    {
        "question": "Which SQL command is used to remove all records but keep the table structure?",
        "options": {
            "A": "DROP",
            "B": "TRUNCATE",
            "C": "DELETE",
            "D": "REMOVE"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Data Scrubbing'?",
        "options": {
            "A": "Deleting all data",
            "B": "The process of identifying and correcting or removing corrupt or inaccurate records",
            "C": "Encrypting data",
            "D": "Adding new data"
        },
        "answer": "B"
    },
    {
        "question": "Which NoSQL type is 'Neo4j'?",
        "options": {
            "A": "Document",
            "B": "Graph",
            "C": "Key-Value",
            "D": "Wide-column"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Shadow Paging'?",
        "options": {
            "A": "A hidden database",
            "B": "A recovery technique where updates are made to a copy of the page table",
            "C": "A way to browse data anonymously",
            "D": "An indexing method"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Composite Primary Key'?",
        "options": {
            "A": "A key made of images",
            "B": "A primary key that consists of more than one column",
            "C": "A key that points to another table",
            "D": "A hidden system index"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'FROM' clause specify in SQL?",
        "options": {
            "A": "The condition",
            "B": "The table or tables from which to retrieve data",
            "C": "The columns to show",
            "D": "The sorting order"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Database Tuning'?",
        "options": {
            "A": "Changing the database name",
            "B": "The group of activities used to optimize performance",
            "C": "Deleting old logs",
            "D": "Adding new users"
        },
        "answer": "B"
    },
    {
        "question": "Which type of dependency does 3NF eliminate?",
        "options": {
            "A": "Partial Dependency",
            "B": "Transitive Dependency",
            "C": "Multi-valued Dependency",
            "D": "Direct Dependency"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Big Data'?",
        "options": {
            "A": "A large computer",
            "B": "Extremely large data sets that may be analyzed computationally to reveal patterns",
            "C": "Data stored on a big disk",
            "D": "A database with many tables"
        },
        "answer": "B"
    },
    {
        "question": "Which SQL keyword is used to find unique values?",
        "options": {
            "A": "UNIQUE",
            "B": "DISTINCT",
            "C": "SINGLE",
            "D": "ONLY"
        },
        "answer": "B"
    },
    {
        "question": "What is 'OLAP' used for?",
        "options": {
            "A": "Daily transactions",
            "B": "Complex analytical queries and data discovery",
            "C": "Sending emails",
            "D": "Managing user passwords"
        },
        "answer": "B"
    },
    {
        "question": "Which join is used to find rows with no match in the other table?",
        "options": {
            "A": "Inner Join",
            "B": "Outer Join (Left/Right/Full)",
            "C": "Cross Join",
            "D": "Self Join"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Multi-version Concurrency Control' (MVCC)?",
        "options": {
            "A": "A method to store multiple copies of the database",
            "B": "A concurrency control method where each user sees a snapshot of the data",
            "C": "An error in version control",
            "D": "A way to update software"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Buffer Manager' responsible for?",
        "options": {
            "A": "Managing network speed",
            "B": "Managing the transfer of data between disk and main memory",
            "C": "Managing the sound of the server",
            "D": "Managing the size of the database"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Database Security'?",
        "options": {
            "A": "Hiding the computer",
            "B": "Protecting the database from unauthorized access or corruption",
            "C": "Deleting the data",
            "D": "Sharing passwords"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Primary Storage'?",
        "options": {
            "A": "Hard drive",
            "B": "RAM (Random Access Memory)",
            "C": "USB Drive",
            "D": "Cloud Storage"
        },
        "answer": "B"
    },
    {
        "question": "Which normal form deals with 'Join Dependencies'?",
        "options": {
            "A": "3NF",
            "B": "4NF",
            "C": "5NF",
            "D": "BCNF"
        },
        "answer": "C"
    },
    {
        "question": "What is a 'Transaction'?",
        "options": {
            "A": "A single SQL line",
            "B": "A logical unit of work that contains one or more SQL statements",
            "C": "A payment made online",
            "D": "A folder in the database"
        },
        "answer": "B"
    },
    {
        "question": "Which SQL clause is used to group rows?",
        "options": {
            "A": "ORDER BY",
            "B": "GROUP BY",
            "C": "SORT BY",
            "D": "ALIGN BY"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Referential Action'?",
        "options": {
            "A": "A user's comment",
            "B": "The behavior (like CASCADE or SET NULL) when a referenced primary key is updated/deleted",
            "C": "A way to sort data",
            "D": "An error message"
        },
        "answer": "B"
    },
    {
        "question": "What is 'In-Memory Database'?",
        "options": {
            "A": "A database you remember",
            "B": "A database that primarily relies on main memory for data storage",
            "C": "A database for brain research",
            "D": "A very small database"
        },
        "answer": "B"
    },
    {
        "question": "Which property of ACID ensures that transactions are isolated from each other?",
        "options": {
            "A": "Atomicity",
            "B": "Consistency",
            "C": "Isolation",
            "D": "Durability"
        },
        "answer": "C"
    },
    {
        "question": "What is 'Deadlock Detection'?",
        "options": {
            "A": "Preventing a deadlock",
            "B": "The process of identifying that a deadlock has occurred and selecting a victim to roll back",
            "C": "Restarting the computer",
            "D": "An antivirus check"
        },
        "answer": "B"
    },
    {
        "question": "Which SQL keyword is used to combine the results of two SELECT statements?",
        "options": {
            "A": "JOIN",
            "B": "UNION",
            "C": "COMBINE",
            "D": "MERGE"
        },
        "answer": "B"
    },
    {
        "question": "What is 'NoSQL'?",
        "options": {
            "A": "No SQL allowed",
            "B": "Not only SQL; a broad class of DBMS that differ from traditional relational systems",
            "C": "New SQL",
            "D": "Simple SQL"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Database Cluster'?",
        "options": {
            "A": "A group of tables",
            "B": "A set of database servers that work together as a single system",
            "C": "A folder of files",
            "D": "A list of users"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to add a Primary Key to an existing table?",
        "options": {
            "A": "CREATE PRIMARY KEY",
            "B": "ALTER TABLE ... ADD PRIMARY KEY",
            "C": "SET PRIMARY KEY",
            "D": "UPDATE TABLE"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Data Abstraction'?",
        "options": {
            "A": "Deleting data",
            "B": "Hiding the complexity of the data structure from the users",
            "C": "Making data hard to read",
            "D": "Sharing data"
        },
        "answer": "B"
    },
    {
        "question": "Which normal form requires the removal of 'Transitive Dependencies'?",
        "options": {
            "A": "1NF",
            "B": "2NF",
            "C": "3NF",
            "D": "BCNF"
        },
        "answer": "C"
    },
    {
        "question": "What is 'Database Recovery'?",
        "options": {
            "A": "Buying a new database",
            "B": "The process of restoring the database to a correct state after a failure",
            "C": "Deleting old data",
            "D": "Changing the password"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Snapshot Isolation'?",
        "options": {
            "A": "Taking a picture of the screen",
            "B": "A concurrency control technique where each transaction sees a consistent snapshot of the data",
            "C": "A way to pause a transaction",
            "D": "A database backup"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Natural Join'?",
        "options": {
            "A": "A join without any keywords",
            "B": "A join that automatically matches columns with the same name",
            "C": "A join of three tables",
            "D": "A join based on nature"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Logical Data Independence'?",
        "options": {
            "A": "Ability to change the physical storage without affecting the logical schema",
            "B": "Ability to change the conceptual schema without affecting the external views",
            "C": "Storing data logically",
            "D": "Using SQL"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Checkpoint'?",
        "options": {
            "A": "A security gate",
            "B": "A point where the DBMS ensures all log records and dirty buffers are written to disk",
            "C": "A save button",
            "D": "A way to check for errors"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Database Concurrency'?",
        "options": {
            "A": "Multiple databases running together",
            "B": "Multiple users accessing and modifying the same data at the same time",
            "C": "The speed of the database",
            "D": "The number of tables"
        },
        "answer": "B"
    },
    {
        "question": "What does 'Atomicity' guarantee?",
        "options": {
            "A": "That data is accurate",
            "B": "That a transaction is treated as a single unit, which either entirely succeeds or entirely fails",
            "C": "That the database is small",
            "D": "That users have unique IDs"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Physical Data Independence'?",
        "options": {
            "A": "Ability to change the logical schema without affecting users",
            "B": "Ability to change the physical storage structure without changing the conceptual schema",
            "C": "Storing data physically",
            "D": "Using a hard drive"
        },
        "answer": "B"
    },
    {
        "question": "Which NoSQL database is known for being 'Schema-less'?",
        "options": {
            "A": "PostgreSQL",
            "B": "MongoDB",
            "C": "Oracle",
            "D": "MySQL"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Data Consistency'?",
        "options": {
            "A": "The data is always the same",
            "B": "Data follows all predefined rules and constraints",
            "C": "The data is never deleted",
            "D": "The data is easy to read"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Write Lock'?",
        "options": {
            "A": "A lock that allows reading only",
            "B": "An exclusive lock that prevents other transactions from reading or writing the data",
            "C": "A pen used for writing",
            "D": "A security password"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Read Lock'?",
        "options": {
            "A": "A shared lock that allows other transactions to read but not write the data",
            "B": "A lock that stops everyone from reading",
            "C": "A way to encrypt text",
            "D": "A database backup"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Lock Granularity'?",
        "options": {
            "A": "The speed of the lock",
            "B": "The size or level of the data item being locked (e.g., row, page, or table)",
            "C": "The number of users locked",
            "D": "The strength of the encryption"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Deadlock Prevention'?",
        "options": {
            "A": "Detecting a deadlock after it happens",
            "B": "Designing the system to ensure that deadlocks can never occur",
            "C": "Rolling back a transaction",
            "D": "Restarting the system"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Wait-for Graph'?",
        "options": {
            "A": "A chart of query speeds",
            "B": "A directed graph used for deadlock detection",
            "C": "A list of users waiting to log in",
            "D": "A diagram of the database structure"
        },
        "answer": "B"
    },
    {
        "question": "Which SQL command is used to permanently save changes?",
        "options": {
            "A": "SAVE",
            "B": "COMMIT",
            "C": "FIX",
            "D": "DONE"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Secondary Storage'?",
        "options": {
            "A": "RAM",
            "B": "Hard Disk or SSD",
            "C": "The screen",
            "D": "The mouse"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Buffer'?",
        "options": {
            "A": "A fast computer",
            "B": "A region of physical memory used to temporarily store data while it is being moved",
            "C": "A database backup",
            "D": "A type of table"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Data Integrity'?",
        "options": {
            "A": "The speed of the data",
            "B": "The accuracy, completeness, and consistency of data",
            "C": "The total size of the data",
            "D": "The encryption of the data"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Index'?",
        "options": {
            "A": "The first page of a book",
            "B": "A data structure that improves the speed of data retrieval operations",
            "C": "A list of users",
            "D": "A type of database"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Hasing' in DBMS?",
        "options": {
            "A": "Deleting data",
            "B": "A technique to directly find the location of a data record based on a key value",
            "C": "A way to sort data",
            "D": "An encryption method"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Dense Index'?",
        "options": {
            "A": "An index for large tables",
            "B": "An index where an entry exists for every search key value in the file",
            "C": "A very heavy computer",
            "D": "An index stored in memory"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Sparse Index'?",
        "options": {
            "A": "An index where entries exist for only some of the search values",
            "B": "A small index",
            "C": "An index for NoSQL",
            "D": "An index that is never used"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Multilevel Indexing'?",
        "options": {
            "A": "An index with many columns",
            "B": "A technique that uses multiple levels of indexes to speed up retrieval",
            "C": "An index for many databases",
            "D": "A backup index"
        },
        "answer": "B"
    },
    {
        "question": "Which SQL statement is used to delete specific rows?",
        "options": {
            "A": "DROP",
            "B": "DELETE",
            "C": "REMOVE",
            "D": "TRUNCATE"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Referential Integrity Constraint'?",
        "options": {
            "A": "A rule that ensures every foreign key value matches a primary key value",
            "B": "A rule for usernames",
            "C": "A speed limit for queries",
            "D": "A database backup"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Self Join'?",
        "options": {
            "A": "A join of two different tables",
            "B": "A regular join in which a table is joined with itself",
            "C": "A join without any rows",
            "D": "A manual join"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Equi Join'?",
        "options": {
            "A": "A join of equal tables",
            "B": "A join that uses only equality comparisons in the join-condition",
            "C": "A join for NoSQL",
            "D": "An error in joining"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Natural Join'?",
        "options": {
            "A": "A join based on common column names",
            "B": "A join without code",
            "C": "A join of three tables",
            "D": "A join in the cloud"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Inner Join'?",
        "options": {
            "A": "The default join that returns only rows with matching values",
            "B": "A join that returns everything",
            "C": "A join for one table",
            "D": "A backup of a join"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Outer Join'?",
        "options": {
            "A": "A join that returns matched and unmatched rows from one or both tables",
            "B": "A join for external databases",
            "C": "A join that only returns unmatched rows",
            "D": "A join for NoSQL"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Cross Join'?",
        "options": {
            "A": "A join of two different databases",
            "B": "A Cartesian product of two tables",
            "C": "A join that deletes data",
            "D": "A very fast join"
        },
        "answer": "B"
    },
    {
        "question": "What is 'View'?",
        "options": {
            "A": "A virtual table",
            "B": "A physical table",
            "C": "A database tool",
            "D": "A backup"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Materialized View'?",
        "options": {
            "A": "A virtual table with stored results",
            "B": "A view of an image",
            "C": "A view for developers",
            "D": "A deleted view"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Authorization'?",
        "options": {
            "A": "Knowing who the user is",
            "B": "Determining what a user is allowed to do",
            "C": "Encrypting the data",
            "D": "Backing up the data"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Authentication'?",
        "options": {
            "A": "Verifying the identity of a user",
            "B": "Giving permissions",
            "C": "Deleting an account",
            "D": "Writing SQL code"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Database Mirroring'?",
        "options": {
            "A": "Flipping the data",
            "B": "A high-availability solution that maintains two copies of a database",
            "C": "Copying only the schema",
            "D": "A type of backup"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Database Failover'?",
        "options": {
            "A": "The process of a database crashing",
            "B": "Automatically switching to a standby database when the primary fails",
            "C": "Deleting a failed table",
            "D": "A database error"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Database Rollback'?",
        "options": {
            "A": "Returning to a previous state",
            "B": "Deleting the database",
            "C": "Updating the database",
            "D": "Adding a new user"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Database Snapshot'?",
        "options": {
            "A": "A read-only, static view of a database at a specific point in time",
            "B": "A picture of the server",
            "C": "A fast query",
            "D": "A type of index"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Database Schema'?",
        "options": {
            "A": "The physical server",
            "B": "The structure that defines the organization of data",
            "C": "A list of users",
            "D": "A type of backup"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Data Dictionary'?",
        "options": {
            "A": "A book of SQL terms",
            "B": "A set of metadata that contains definitions and representations of data",
            "C": "A list of user emails",
            "D": "A backup file"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Normalization'?",
        "options": {
            "A": "Making the database normal",
            "B": "The process of organizing data to reduce redundancy and improve integrity",
            "C": "Deleting old data",
            "D": "Encrypting data"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Primary Key'?",
        "options": {
            "A": "The most important key",
            "B": "A unique identifier for a record in a table",
            "C": "A key for the front door",
            "D": "A password"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Foreign Key'?",
        "options": {
            "A": "A key from another country",
            "B": "A field in one table that uniquely identifies a row in another table",
            "C": "A temporary key",
            "D": "A key for NoSQL"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Candidate Key'?",
        "options": {
            "A": "A key running for election",
            "B": "A column or set of columns that can uniquely identify any record",
            "C": "A backup primary key",
            "D": "A non-unique key"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Composite Key'?",
        "options": {
            "A": "A key composed of two or more columns",
            "B": "A key made of images",
            "C": "A very long key",
            "D": "A key for multiple databases"
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
    skill = "database"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
