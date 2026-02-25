from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
    {
        "question": "What does the 'ORDBMS' acronym stand for in the context of PostgreSQL?",
        "options": {
            "A": "Online Relational Database Management System",
            "B": "Object-Relational Database Management System",
            "C": "Optimized Recovery Data Management System",
            "D": "Open-Source Relational Database Management System"
        },
        "answer": "B"
    },
    {
        "question": "Which command-line utility is the primary interface for interacting with PostgreSQL?",
        "options": {
            "A": "mysql",
            "B": "psql",
            "C": "pgadmin",
            "D": "postsql"
        },
        "answer": "B"
    },
    {
        "question": "In PostgreSQL, what is a 'Schema'?",
        "options": {
            "A": "The database password",
            "B": "A namespace that contains named objects like tables and views",
            "C": "A backup file",
            "D": "A physical storage disk"
        },
        "answer": "B"
    },
    {
        "question": "Which data type is used in PostgreSQL to store a universally unique identifier?",
        "options": {
            "A": "SERIAL",
            "B": "UUID",
            "C": "GUID",
            "D": "UNIQUEID"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary difference between JSON and JSONB in PostgreSQL?",
        "options": {
            "A": "JSON is faster to write; JSONB is faster to process and supports indexing",
            "B": "JSONB is only for binary files",
            "C": "JSON does not support nested objects",
            "D": "There is no difference"
        },
        "answer": "A"
    },
    {
        "question": "Which PostgreSQL command is used to see the list of all tables in the current database via psql?",
        "options": {
            "A": "\\l",
            "B": "\\dt",
            "C": "\\d",
            "D": "SHOW TABLES;"
        },
        "answer": "B"
    },
    {
        "question": "Which feature allows PostgreSQL to handle concurrent transactions without locking the entire table?",
        "options": {
            "A": "Table Locking",
            "B": "MVCC (Multi-Version Concurrency Control)",
            "C": "Single-Threaded Processing",
            "D": "Two-Phase Commit"
        },
        "answer": "B"
    },
    {
        "question": "How do you create an auto-incrementing integer column in older PostgreSQL versions?",
        "options": {
            "A": "AUTO_INCREMENT",
            "B": "SERIAL",
            "C": "IDENTITY",
            "D": "SEQUENCE"
        },
        "answer": "B"
    },
    {
        "question": "Which PostgreSQL extension is famous for adding support for geographic objects (GIS)?",
        "options": {
            "A": "pg_stat_statements",
            "B": "PostGIS",
            "C": "pg_crypto",
            "D": "hstore"
        },
        "answer": "B"
    },
    {
        "question": "What is the maximum size for a single database in PostgreSQL?",
        "options": {
            "A": "4 TB",
            "B": "Unlimited",
            "C": "16 TB",
            "D": "64 TB"
        },
        "answer": "B"
    },
    {
        "question": "Which statement is used to create a custom data type in PostgreSQL?",
        "options": {
            "A": "DEFINE TYPE",
            "B": "CREATE TYPE",
            "C": "NEW TYPE",
            "D": "ADD TYPE"
        },
        "answer": "B"
    },
    {
        "question": "How do you define an array of integers in a table definition?",
        "options": {
            "A": "ARRAY(int)",
            "B": "INTEGER[]",
            "C": "LIST(int)",
            "D": "INT_ARRAY"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'EXPLAIN ANALYZE' command do?",
        "options": {
            "A": "Deletes the query plan",
            "B": "Shows the execution plan and actually executes the query to show true timings",
            "C": "Formats the SQL code",
            "D": "Checks for syntax errors only"
        },
        "answer": "B"
    },
    {
        "question": "Which constraint is used to ensure that a column contains values that satisfy a specific boolean expression?",
        "options": {
            "A": "UNIQUE",
            "B": "CHECK",
            "C": "ASSERT",
            "D": "VERIFY"
        },
        "answer": "B"
    },
    {
        "question": "Which keyword is used to return rows from the first query that are not present in the second query?",
        "options": {
            "A": "MINUS",
            "B": "EXCEPT",
            "C": "NOT IN",
            "D": "SUBTRACT"
        },
        "answer": "B"
    },
    {
        "question": "What is the default port for a PostgreSQL server?",
        "options": {
            "A": "3306",
            "B": "5432",
            "C": "8080",
            "D": "1521"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to get the current date and time with timezone?",
        "options": {
            "A": "GETDATE()",
            "B": "NOW()",
            "C": "CURRENT_TIME",
            "D": "TODAY()"
        },
        "answer": "B"
    },
    {
        "question": "In PostgreSQL, what is a 'CTE'?",
        "options": {
            "A": "Common Table Entry",
            "B": "Common Table Expression",
            "C": "Concurrent Table Execution",
            "D": "Column Type Extension"
        },
        "answer": "B"
    },
    {
        "question": "Which operator is used to check if a JSONB column contains a specific key?",
        "options": {
            "A": "->",
            "B": "?",
            "C": "@>",
            "D": "#>"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'WAL' in PostgreSQL?",
        "options": {
            "A": "Write-Ahead Logging",
            "B": "Web Access Layer",
            "C": "Wide Area Logic",
            "D": "Wait and Load"
        },
        "answer": "A"
    },
    {
        "question": "Which command is used to remove all rows from a table and reset its associated sequences?",
        "options": {
            "A": "DELETE",
            "B": "TRUNCATE ... RESTART IDENTITY",
            "C": "DROP TABLE",
            "D": "CLEAR TABLE"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'psql' command '\\d table_name' do?",
        "options": {
            "A": "Deletes the table",
            "B": "Displays the definition (columns, types, constraints) of the table",
            "C": "Drops the data",
            "D": "Downloads the table"
        },
        "answer": "B"
    },
    {
        "question": "How do you specify an 'Identity' column (SQL standard way) in PostgreSQL 10+?",
        "options": {
            "A": "SERIAL",
            "B": "GENERATED ALWAYS AS IDENTITY",
            "C": "AUTO_INCREMENT",
            "D": "IDENTITY_COLUMN"
        },
        "answer": "B"
    },
    {
        "question": "Which configuration file is primarily used to control client authentication in PostgreSQL?",
        "options": {
            "A": "postgresql.conf",
            "B": "pg_hba.conf",
            "C": "pg_ident.conf",
            "D": "auth.conf"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'View' that actually stores data physically on disk called?",
        "options": {
            "A": "Virtual Table",
            "B": "Materialized View",
            "C": "Stored View",
            "D": "Cached View"
        },
        "answer": "B"
    },
    {
        "question": "Which index type is best suited for full-text search and JSONB arrays in PostgreSQL?",
        "options": {
            "A": "B-Tree",
            "B": "GIN (Generalized Inverted Index)",
            "C": "Hash",
            "D": "BRIN"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of a 'Window Function' in PostgreSQL?",
        "options": {
            "A": "To open a new database connection",
            "B": "To perform calculations across a set of table rows related to the current row",
            "C": "To create a popup in the UI",
            "D": "To limit the number of rows returned"
        },
        "answer": "B"
    },
    {
        "question": "Which keyword is required to define the partitions for a Window Function?",
        "options": {
            "A": "GROUP BY",
            "B": "OVER",
            "C": "WINDOW",
            "D": "BETWEEN"
    },
    "answer": "B"
    },
    {
        "question": "Which command is used to update the data stored in a Materialized View?",
        "options": {
            "A": "UPDATE VIEW name;",
            "B": "REFRESH MATERIALIZED VIEW name;",
            "C": "RELOAD VIEW name;",
            "D": "ALTER VIEW name REFRESH;"
        },
        "answer": "B"
    },
    {
        "question": "Which PostgreSQL index type is specifically designed for very large tables where data is naturally sorted?",
        "options": {
            "A": "GiST",
            "B": "BRIN (Block Range Index)",
            "C": "SP-GiST",
            "D": "B-Tree"
        },
        "answer": "B"
    },
    {
        "question": "What does 'UPSERT' refer to in PostgreSQL?",
        "options": {
            "A": "An update that fails",
            "B": "An INSERT statement with an ON CONFLICT clause",
            "C": "Deleting and then inserting a row",
            "D": "Uploading data to a server"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to convert a string to a specific data type using a PostgreSQL-specific cast operator?",
        "options": {
            "A": "CAST(x AS type)",
            "B": "x::type",
            "C": "Both A and B",
            "D": "CONVERT(x, type)"
        },
        "answer": "C"
    },
    {
        "question": "Which operator is used to retrieve a value from a JSONB column as text?",
        "options": {
            "A": "->",
            "B": "->>",
            "C": "#>",
            "D": "@@"
        },
        "answer": "B"
    },
    {
        "question": "What is 'VACUUM' used for in PostgreSQL?",
        "options": {
            "A": "To delete all data",
            "B": "To reclaim storage occupied by dead tuples (deleted/updated rows)",
            "C": "To compress the database files",
            "D": "To restart the server"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to identify the current database user in a session?",
        "options": {
            "A": "SELECT current_user;",
            "B": "SELECT session_user;",
            "C": "Both A and B",
            "D": "WHOAMI;"
        },
        "answer": "C"
    },
    {
        "question": "What is the 'hstore' extension used for?",
        "options": {
            "A": "Storing history of changes",
            "B": "Storing sets of key/value pairs within a single PostgreSQL value",
            "C": "High-speed storage",
            "D": "Hardware monitoring"
        },
        "answer": "B"
    },
    {
        "question": "Which function returns the row number of the current row within its partition?",
        "options": {
            "A": "COUNT()",
            "B": "ROW_NUMBER()",
            "C": "RANK()",
            "D": "INDEX()"
        },
        "answer": "B"
    },
    {
        "question": "In a Window Function, what is the difference between RANK() and DENSE_RANK()?",
        "options": {
            "A": "RANK() leaves gaps in sequence after ties; DENSE_RANK() does not",
            "B": "DENSE_RANK() is only for numeric data",
            "C": "RANK() is faster",
            "D": "There is no difference"
        },
        "answer": "A"
    },
    {
        "question": "Which operator checks if the left JSONB value contains the right JSONB path/value?",
        "options": {
            "A": "?",
            "B": "@>",
            "C": "<@",
            "D": "&&"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to add a new partition to an existing partitioned table?",
        "options": {
            "A": "ADD PARTITION",
            "B": "CREATE TABLE ... PARTITION OF ...",
            "C": "ALTER TABLE ... ADD PARTITION",
            "D": "NEW PARTITION FOR"
        },
        "answer": "B"
    },
    {
        "question": "What is 'PL/pgSQL'?",
        "options": {
            "A": "A physical layout engine",
            "B": "A load-balancing tool",
            "C": "The procedural programming language for PostgreSQL",
            "D": "A type of join"
        },
        "answer": "C"
    },
    {
        "question": "Which function is used to generate a series of values, often used for creating dummy data or date ranges?",
        "options": {
            "A": "pd.date_range()",
            "B": "generate_series()",
            "C": "range_gen()",
            "D": "series_inc()"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Foreign Data Wrapper' (FDW)?",
        "options": {
            "A": "A way to encrypt data",
            "B": "A library for foreign keys",
            "C": "A tool to access and query data stored in external databases from within Postgres",
            "D": "A translation service for SQL"
        },
        "answer": "C"
    },
    {
        "question": "Which PostgreSQL command allows you to see the execution plan *without* running the query?",
        "options": {
            "A": "EXPLAIN",
            "B": "EXPLAIN ANALYZE",
            "C": "SHOW PLAN",
            "D": "QUERY PLAN"
        },
        "answer": "A"
    },
    {
        "question": "Which function returns the value evaluated at the row that is the 'n' rows before the current row?",
        "options": {
            "A": "LEAD()",
            "B": "LAG()",
            "C": "PREV()",
            "D": "LAST()"
        },
        "answer": "B"
    },
    {
        "question": "Which function returns the value evaluated at the row that is 'n' rows after the current row?",
        "options": {
            "A": "LAG()",
            "B": "LEAD()",
            "C": "NEXT()",
            "D": "FUTURE()"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'COALESCE'?",
        "options": {
            "A": "To combine two strings",
            "B": "To return the first non-null value in a list of arguments",
            "C": "To group similar data",
            "D": "To sort data"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to change the owner of a database?",
        "options": {
            "A": "ALTER DATABASE name OWNER TO new_owner;",
            "B": "GRANT DATABASE name TO new_owner;",
            "C": "UPDATE DATABASE owner SET new_owner;",
            "D": "CHANGE OWNER FOR name TO new_owner;"
        },
        "answer": "A"
    },
    {
        "question": "Which index type is best for geometric and spatial data types?",
        "options": {
            "A": "B-Tree",
            "B": "GiST (Generalized Search Tree)",
            "C": "Hash",
            "D": "GIN"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Autovacuum'?",
        "options": {
            "A": "A feature that deletes old backups",
            "B": "A background process that automatically runs VACUUM and ANALYZE",
            "C": "A tool for cleaning the server hardware",
            "D": "An automatic script to remove duplicates"
        },
        "answer": "B"
    },
{
        "question": "Which command is used to create a new stored procedure in PostgreSQL 11+?",
        "options": {
            "A": "CREATE FUNCTION",
            "B": "CREATE PROCEDURE",
            "C": "CREATE TASK",
            "D": "CREATE ACTION"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary difference between a FUNCTION and a PROCEDURE in PostgreSQL?",
        "options": {
            "A": "Functions can return values; Procedures cannot return values but support transaction control (COMMIT/ROLLBACK)",
            "B": "Procedures are faster",
            "C": "Functions can only be written in SQL",
            "D": "There is no difference"
        },
        "answer": "A"
    },
    {
        "question": "Which keyword is used to start the execution of a Trigger?",
        "options": {
            "A": "RUN",
            "B": "EXECUTE",
            "C": "TRIGGER",
            "D": "INVOKE"
        },
        "answer": "B"
    },
    {
        "question": "In a Trigger function, which special variable contains the new database row for INSERT/UPDATE operations?",
        "options": {
            "A": "OLD",
            "B": "NEW",
            "C": "CURRENT",
            "D": "ROW"
        },
        "answer": "B"
    },
    {
        "question": "In a Trigger function, which special variable contains the row being modified or deleted?",
        "options": {
            "A": "NEW",
            "B": "OLD",
            "C": "PREVIOUS",
            "D": "EXISTING"
        },
        "answer": "B"
    },
    {
        "question": "Which data type is used to store preprocessed documents for fast full-text searching?",
        "options": {
            "A": "TEXT",
            "B": "TSVECTOR",
            "C": "TSQUERY",
            "D": "VEC_SEARCH"
        },
        "answer": "B"
    },
    {
        "question": "Which function converts a plain string into a 'tsvector' for full-text search?",
        "options": {
            "A": "to_tsquery()",
            "B": "to_tsvector()",
            "C": "plainto_tsquery()",
            "D": "str_to_vec()"
        },
        "answer": "B"
    },
    {
        "question": "Which operator is used to match a 'tsvector' against a 'tsquery'?",
        "options": {
            "A": "==",
            "B": "@@",
            "C": "~~",
            "D": "::"
        },
        "answer": "B"
    },
    {
        "question": "What does 'Row-Level Security' (RLS) allow you to do?",
        "options": {
            "A": "Hide columns from users",
            "B": "Restrict which rows a user can see or modify based on a policy",
            "C": "Lock specific rows for editing",
            "D": "Encrypt individual rows"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to enable Row-Level Security on a table?",
        "options": {
            "A": "ALTER TABLE name ENABLE ROW LEVEL SECURITY;",
            "B": "CREATE POLICY ON name ...",
            "C": "GRANT RLS ON name TO user;",
            "D": "SET SECURITY ON name;"
        },
        "answer": "A"
    },
    {
        "question": "What is 'pg_dump' used for?",
        "options": {
            "A": "Viewing logs",
            "B": "Backing up a single PostgreSQL database",
            "C": "Deleting a database",
            "D": "Restoring a cluster"
        },
        "answer": "B"
    },
    {
        "question": "Which utility is used to backup an entire PostgreSQL database cluster?",
        "options": {
            "A": "pg_dump",
            "B": "pg_dumpall",
            "C": "pg_backup",
            "D": "pg_save"
        },
        "answer": "B"
    },
    {
        "question": "Which index type is specifically optimized for 'nearest neighbor' searches (like finding the closest store)?",
        "options": {
            "A": "B-Tree",
            "B": "GiST with KNN (K-Nearest Neighbors)",
            "C": "Hash",
            "D": "GIN"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'REINDEX' command?",
        "options": {
            "A": "To create a new index",
            "B": "To rebuild an existing index from scratch to improve performance",
            "C": "To change the column of an index",
            "D": "To list all indexes"
        },
        "answer": "B"
    },
    {
        "question": "Which table stores information about all tables in the database (system catalog)?",
        "options": {
            "A": "pg_tables",
            "B": "pg_class",
            "C": "pg_catalog",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Streaming Replication' in PostgreSQL?",
        "options": {
            "A": "Watching a video of the database",
            "B": "Continuously sending WAL records from a primary server to standby servers",
            "C": "Copying data over HTTP",
            "D": "Backup to a cloud service"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to stop a long-running query in PostgreSQL?",
        "options": {
            "A": "pg_cancel_backend(pid)",
            "B": "pg_stop_query(pid)",
            "C": "KILL query_id",
            "D": "TERMINATE pid"
        },
        "answer": "A"
    },
    {
        "question": "What is 'pg_stat_statements'?",
        "options": {
            "A": "A tool to write SQL",
            "B": "An extension that tracks execution statistics of all SQL statements",
            "C": "A manual for SQL commands",
            "D": "A way to view user passwords"
        },
        "answer": "B"
    },
    {
        "question": "Which type of Trigger is executed once for the entire SQL statement, regardless of how many rows are affected?",
        "options": {
            "A": "Row-level Trigger",
            "B": "Statement-level Trigger",
            "C": "Transaction-level Trigger",
            "D": "Global Trigger"
        },
        "answer": "B"
    },
    {
        "question": "Which keyword is used in a Trigger definition to specify it should run for every row?",
        "options": {
            "A": "FOR EACH STATEMENT",
            "B": "FOR EACH ROW",
            "C": "PER ROW",
            "D": "ON ROW"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Logical Decoding'?",
        "options": {
            "A": "Converting SQL to English",
            "B": "Extracting changes committed to the database for replication to other systems",
            "C": "Debugging logic errors",
            "D": "A type of data compression"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to create a point-in-time recovery marker (Restore Point)?",
        "options": {
            "A": "pg_create_restore_point()",
            "B": "pg_save_point()",
            "C": "pg_mark_time()",
            "D": "pg_checkpoint()"
        },
        "answer": "A"
    },
    {
        "question": "What is the result of 'VACUUM FULL'?",
        "options": {
            "A": "It runs faster than regular VACUUM",
            "B": "It rebuilds the entire table file to minimize disk space but requires an exclusive lock",
            "C": "It only cleans indexes",
            "D": "It deletes all records"
        },
        "answer": "B"
    },
    {
        "question": "Which view provides information about active locks in the database?",
        "options": {
            "A": "pg_locks",
            "B": "pg_stat_activity",
            "C": "pg_blockers",
            "D": "pg_security"
        },
        "answer": "A"
    },
    {
        "question": "What is the 'Search Path' in PostgreSQL?",
        "options": {
            "A": "The folder where Postgres is installed",
            "B": "A list of schemas that are searched to find an object when no schema is specified",
            "C": "The URL of the database",
            "D": "A tool for full-text search"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to see the current search path?",
        "options": {
            "A": "SHOW search_path;",
            "B": "GET PATH;",
            "C": "SELECT current_path;",
            "D": "psql \\path"
        },
        "answer": "A"
    },
    {
        "question": "Which function is used to cast a value to a different type safely (returning NULL on failure)?",
        "options": {
            "A": "SAFE_CAST",
            "B": "PostgreSQL does not have a built-in safe cast; you must use a custom function/CASE statement",
            "C": "TRY_CAST",
            "D": "TO_TYPE"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to create a new role that can log in?",
        "options": {
            "A": "CREATE ROLE name LOGIN;",
            "B": "CREATE USER name;",
            "C": "Both A and B",
            "D": "ADD USER name;"
        },
        "answer": "C"
    },
    {
        "question": "What is a 'Partial Index'?",
        "options": {
            "A": "An index that only stores half the data",
            "B": "An index built over a subset of a table defined by a conditional expression (WHERE clause)",
            "C": "An index that is currently being built",
            "D": "An index on a view"
        },
        "answer": "B"
    },
    {
        "question": "Which operator is used to extract an element from an array by index?",
        "options": {
            "A": "array[index]",
            "B": "array->index",
            "C": "array.get(index)",
            "D": "array{index}"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Inheritance' in PostgreSQL tables?",
        "options": {
            "A": "A child table inheriting columns from a parent table",
            "B": "Copying data from another user",
            "C": "Using the same password",
            "D": "A way to backup data"
        },
        "answer": "A"
    },
    {
        "question": "Which function allows you to calculate the similarity between two strings (requires pg_trgm extension)?",
        "options": {
            "A": "SIMILARITY(s1, s2)",
            "B": "LEVENSHTEIN(s1, s2)",
            "C": "Both A and B",
            "D": "MATCH(s1, s2)"
        },
        "answer": "C"
    },
    {
        "question": "What is 'pgAudit'?",
        "options": {
            "A": "A tool to check for slow queries",
            "B": "An extension that provides detailed logging for compliance and auditing",
            "C": "A database repair tool",
            "D": "A way to calculate totals"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to change a session-level configuration parameter?",
        "options": {
            "A": "ALTER SYSTEM SET ...",
            "B": "SET parameter = value;",
            "C": "UPDATE CONFIG ...",
            "D": "CONFIG SET ..."
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'LISTEN' and 'NOTIFY'?",
        "options": {
            "A": "Sending emails",
            "B": "Simple inter-process communication (IPC) between clients connected to the same database",
            "C": "System monitoring",
            "D": "Chatting with other users"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to unnest an array into a set of rows?",
        "options": {
            "A": "UNPACK()",
            "B": "UNNEST()",
            "C": "EXPAND()",
            "D": "FLATTEN()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'TOAST' (The Oversized-Attribute Storage Technique)?",
        "options": {
            "A": "A way to warm up the database",
            "B": "A mechanism to store large field values that exceed the page size",
            "C": "A type of data encryption",
            "D": "A caching system"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to verify the integrity of the data files?",
        "options": {
            "A": "pg_checksums",
            "B": "pg_verify",
            "C": "pg_check",
            "D": "verify_data"
        },
        "answer": "A"
    },
    {
        "question": "What does 'ON DELETE SET NULL' do in a foreign key constraint?",
        "options": {
            "A": "Deletes the row if parent is deleted",
            "B": "Sets the foreign key column to NULL if the referenced parent row is deleted",
            "C": "Prevents deletion of the parent",
            "D": "Throws an error"
        },
        "answer": "B"
    },
    {
        "question": "Which function returns the OID (Object Identifier) of a table?",
        "options": {
            "A": "table_oid()",
            "B": "'table_name'::regclass::oid",
            "C": "get_oid('table_name')",
            "D": "oid(table_name)"
        },
        "answer": "B"
    },
    {
        "question": "What is 'pg_repack'?",
        "options": {
            "A": "A tool to rebuild tables and indexes without an exclusive lock (unlike VACUUM FULL)",
            "B": "A backup tool",
            "C": "A data migration script",
            "D": "A way to change data types"
        },
        "answer": "A"
    },
    {
        "question": "Which command lists all schemas in the database via psql?",
        "options": {
            "A": "\\dn",
            "B": "\\ls",
            "C": "\\ds",
            "D": "SHOW SCHEMAS;"
        },
        "answer": "A"
    },
    {
        "question": "How do you search for a value in an array column?",
        "options": {
            "A": "WHERE value = ANY(array_column)",
            "B": "WHERE array_column @> ARRAY[value]",
            "C": "Both A and B",
            "D": "WHERE value IN array_column"
        },
        "answer": "C"
    },
    {
        "question": "What is 'Cursor' in PostgreSQL PL/pgSQL?",
        "options": {
            "A": "The mouse pointer",
            "B": "A reference to the result set of a query, allowing you to process rows one by one",
            "C": "A type of index",
            "D": "A system log"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to permanently remove a role?",
        "options": {
            "A": "DELETE ROLE",
            "B": "DROP ROLE",
            "C": "REMOVE ROLE",
            "D": "REVOKE ROLE"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Parallel Query'?",
        "options": {
            "A": "Running two databases at once",
            "B": "The ability to use multiple CPU cores to execute a single SQL query faster",
            "C": "Executing queries in alphabetical order",
            "D": "A tool for data comparison"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to convert JSONB back to a record type?",
        "options": {
            "A": "jsonb_to_record()",
            "B": "jsonb_populate_record()",
            "C": "Both A and B",
            "D": "cast_json_to_row()"
        },
        "answer": "C"
    },
    {
        "question": "What is 'Foreign Key' referential integrity?",
        "options": {
            "A": "Ensuring passwords are strong",
            "B": "Ensuring that the relationship between tables remains consistent (child always points to existing parent)",
            "C": "Connecting to external databases",
            "D": "Using unique IDs"
        },
        "answer": "B"
    },
    {
        "question": "Which psql command is used to turn on query timing?",
        "options": {
            "A": "\\timing",
            "B": "\\time",
            "C": "SET TIMING ON;",
            "D": "\\clock"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Advisory Locks'?",
        "options": {
            "A": "Warning messages",
            "B": "Application-defined locks that have no inherent meaning to the database but can be used for custom locking logic",
            "C": "Locks that expire automatically",
            "D": "Read-only locks"
        },
        "answer": "B"
    },
    {
        "question": "Which file is the primary configuration file for PostgreSQL server settings?",
        "options": {
            "A": "pg_hba.conf",
            "B": "postgresql.conf",
            "C": "pg_ident.conf",
            "D": "postmaster.opts"
        },
        "answer": "B"
    },
    {
        "question": "In 'Streaming Replication', which file must be present on the standby server to tell it to enter recovery mode (pre-v12)?",
        "options": {
            "A": "standby.signal",
            "B": "recovery.conf",
            "C": "replica.opts",
            "D": "pg_recovery"
        },
        "answer": "B"
    },
    {
        "question": "Starting from PostgreSQL 12, which file is used to signal that the server should start in standby mode?",
        "options": {
            "A": "recovery.conf",
            "B": "standby.signal",
            "C": "recovery.signal",
            "D": "postmaster.pid"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'slot' in 'Replication Slots' used for?",
        "options": {
            "A": "Storing physical data",
            "B": "Ensuring the primary does not delete WAL files until they are received by the standby",
            "C": "Managing user connections",
            "D": "Scheduling backups"
        },
        "answer": "B"
    },
    {
        "question": "Which type of replication allows for different table structures or only specific tables to be replicated?",
        "options": {
            "A": "Physical Replication",
            "B": "Logical Replication",
            "C": "Streaming Replication",
            "D": "Synchronous Replication"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to create a publication in Logical Replication?",
        "options": {
            "A": "CREATE PUBLICATION",
            "B": "ADD REPLICATION",
            "C": "START LOGICAL",
            "D": "GENERATE STREAM"
        },
        "answer": "A"
    },
    {
        "question": "Which command is used on the subscriber node to start receiving data in Logical Replication?",
        "options": {
            "A": "CREATE SUBSCRIPTION",
            "B": "JOIN PUBLICATION",
            "C": "START REPLICA",
            "D": "RECEIVE STREAM"
        },
        "answer": "A"
    },
    {
        "question": "What does 'Synchronous Commit' ensure?",
        "options": {
            "A": "That the primary is faster than the standby",
            "B": "That a transaction is only considered committed after it is written to the standby",
            "C": "That all users are logged out during a commit",
            "D": "That the database is backed up daily"
        },
        "answer": "B"
    },
    {
        "question": "Which utility is used to perform a 'base backup' for setting up a standby server?",
        "options": {
            "A": "pg_dump",
            "B": "pg_basebackup",
            "C": "pg_clone",
            "D": "pg_copy"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'shared_buffers' configuration parameter?",
        "options": {
            "A": "To limit the number of users",
            "B": "To set the amount of memory dedicated to the database for caching data",
            "C": "To store logs",
            "D": "To share data with other databases"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Work Mem' (work_mem) used for?",
        "options": {
            "A": "General memory for every user",
            "B": "Memory used for complex sort operations and hash tables per query operation",
            "C": "Permanent storage",
            "D": "Connection pooling"
        },
        "answer": "B"
    },
    {
        "question": "What happens if a sort operation exceeds the 'work_mem' limit?",
        "options": {
            "A": "The query fails",
            "B": "The operation spills to disk (temporary files)",
            "C": "Postgres crashes",
            "D": "The memory is automatically increased"
        },
        "answer": "B"
    },
    {
        "question": "Which parameter defines how long the server waits before a transaction is considered 'deadlocked'?",
        "options": {
            "A": "lock_timeout",
            "B": "deadlock_timeout",
            "C": "statement_timeout",
            "D": "wait_time"
        },
        "answer": "B"
    },
    {
        "question": "What is 'PITR'?",
        "options": {
            "A": "Point-in-Time Recovery",
            "B": "Primary-Integrated Table Replication",
            "C": "Parallel-Index Total Reset",
            "D": "Persistent Interface for Tables"
        },
        "answer": "A"
    },
    {
        "question": "Which logging level provides the most detail for debugging in 'postgresql.conf'?",
        "options": {
            "A": "INFO",
            "B": "DEBUG5",
            "C": "WARNING",
            "D": "LOG"
        },
        "answer": "B"
    },
    {
        "question": "What is 'pg_control'?",
        "options": {
            "A": "A GUI tool",
            "B": "A binary file containing critical control information about the database cluster state",
            "C": "A user management table",
            "D": "A backup script"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to promote a standby server to become the primary?",
        "options": {
            "A": "pg_ctl promote",
            "B": "promote standby",
            "C": "SELECT pg_promote();",
            "D": "Both A and C"
        },
        "answer": "D"
    },
    {
        "question": "What is the 'Checkpoint' process in PostgreSQL?",
        "options": {
            "A": "A security scan",
            "B": "The process of flushing dirty data pages from memory to disk to ensure WAL can be recycled",
            "C": "A point where users must re-authenticate",
            "D": "A tool to count rows"
        },
        "answer": "B"
    },
    {
        "question": "Which extension is used to run SQL tasks on a schedule (similar to cron)?",
        "options": {
            "A": "pg_timer",
            "B": "pg_cron",
            "C": "pg_schedule",
            "D": "pg_task"
        },
        "answer": "B"
    },
    {
        "question": "How do you kill all connections to a specific database named 'my_db'?",
        "options": {
            "A": "DROP DATABASE my_db;",
            "B": "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'my_db';",
            "C": "KILL my_db;",
            "D": "ALTER DATABASE my_db SET ALLOW_CONNECTIONS = OFF;"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Maintenance Work Mem' (maintenance_work_mem) typically used for?",
        "options": {
            "A": "Daily backups",
            "B": "Maintenance tasks like VACUUM, CREATE INDEX, and ALTER TABLE",
            "C": "Cleaning the cache",
            "D": "User login sessions"
        },
        "answer": "B"
    },
    {
        "question": "Which view allows you to see the progress of a running VACUUM command?",
        "options": {
            "A": "pg_stat_progress_vacuum",
            "B": "pg_stat_activity",
            "C": "pg_vacuum_log",
            "D": "pg_control"
        },
        "answer": "A"
    },
    {
        "question": "What is the 'Effective Cache Size' parameter used for?",
        "options": {
            "A": "Allocating memory to the OS",
            "B": "Providing a hint to the query planner about how much memory is available for disk caching",
            "C": "Setting the maximum file size",
            "D": "Increasing the speed of SSDs"
        },
        "answer": "B"
    },
    {
        "question": "Which type of replication is safest against data loss but can slow down the primary?",
        "options": {
            "A": "Asynchronous Replication",
            "B": "Synchronous Replication",
            "C": "Snapshot Replication",
            "D": "Lazy Replication"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Hot Standby'?",
        "options": {
            "A": "A server that is overheating",
            "B": "A standby server that allows read-only queries while it is in recovery mode",
            "C": "A server that is ready for backups",
            "D": "A fast-loading database"
        },
        "answer": "B"
    },
    {
        "question": "What is 'PgBouncer' primarily used for?",
        "options": {
            "A": "Database encryption",
            "B": "A lightweight connection pooler for PostgreSQL",
            "C": "Automated backups",
            "D": "Visualizing query plans"
        },
        "answer": "B"
    },
    {
        "question": "In 'Patroni', what is the role of the 'DCS' (Distributed Configuration Store)?",
        "options": {
            "A": "To store the actual database data",
            "B": "To maintain consensus on which node is the leader in a High Availability cluster",
            "C": "To store user passwords",
            "D": "To compress WAL files"
        },
        "answer": "B"
    },
    {
        "question": "Which tool is commonly used with PostgreSQL to provide a 'Floating IP' or 'Virtual IP' for failover?",
        "options": {
            "A": "Keepalived",
            "B": "HAProxy",
            "C": "Both A and B",
            "D": "PgAdmin"
        },
        "answer": "C"
    },
    {
        "question": "What is the primary benefit of using 'Connection Pooling'?",
        "options": {
            "A": "It increases the number of physical disks",
            "B": "It reduces the overhead of creating new database connections by reusing existing ones",
            "C": "It makes the SQL queries shorter",
            "D": "It automatically fixes slow queries"
        },
        "answer": "B"
    },
    {
        "question": "Which extension allows PostgreSQL to act as a 'NoSQL' document store by providing a key-value data type?",
        "options": {
            "A": "pg_crypto",
            "B": "hstore",
            "C": "pg_trgm",
            "D": "uuid-ossp"
        },
        "answer": "B"
    },
    {
        "question": "What is 'TimescaleDB'?",
        "options": {
            "A": "A new version of PostgreSQL for mobile phones",
            "B": "An extension that optimizes PostgreSQL for time-series data using 'hypertables'",
            "C": "A tool to measure query time",
            "D": "A backup scheduler"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to enable a pre-installed extension in a specific database?",
        "options": {
            "A": "LOAD EXTENSION",
            "B": "CREATE EXTENSION",
            "C": "ADD EXTENSION",
            "D": "USE EXTENSION"
        },
        "answer": "B"
    },
    {
        "question": "In the context of AWS, what is 'Aurora PostgreSQL'?",
        "options": {
            "A": "A desktop version of Postgres",
            "B": "A cloud-native, highly available, and auto-scaling relational database engine compatible with PostgreSQL",
            "C": "A free tier database",
            "D": "A plugin for web browsers"
        },
        "answer": "B"
    },
    {
        "question": "What does 'pg_is_in_recovery()' return on a standby server?",
        "options": {
            "A": "False",
            "B": "True",
            "C": "The current time",
            "D": "The server's IP address"
        },
        "answer": "B"
    },
    {
        "question": "Which utility is used to upgrade a PostgreSQL data cluster to a newer major version?",
        "options": {
            "A": "pg_update",
            "B": "pg_upgrade",
            "C": "pg_migrate",
            "D": "pg_install"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Citus'?",
        "options": {
            "A": "A tool for UI design",
            "B": "An extension that transforms PostgreSQL into a distributed database (sharding)",
            "C": "A security auditing tool",
            "D": "A type of table constraint"
        },
        "answer": "B"
    },
    {
        "question": "Which parameter in 'postgresql.conf' controls the maximum number of concurrent connections?",
        "options": {
            "A": "max_users",
            "B": "max_connections",
            "C": "connection_limit",
            "D": "user_limit"
        },
        "answer": "B"
    },
    {
        "question": "What is 'ZSON' in the PostgreSQL ecosystem?",
        "options": {
            "A": "A 3D JSON type",
            "B": "An extension for transparent JSONB compression using a shared dictionary",
            "C": "A way to encrypt JSON",
            "D": "A replacement for XML"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Barman' (Backup and Recovery Manager)?",
        "options": {
            "A": "To manage database users",
            "B": "An administration tool for disaster recovery of PostgreSQL servers written in Python",
            "C": "A tool for data visualization",
            "D": "To monitor CPU usage"
        },
        "answer": "B"
    },
    {
        "question": "Which feature allows you to run PostgreSQL in a containerized environment like Kubernetes with ease?",
        "options": {
            "A": "Operators (e.g., CloudNativePG, Zalando)",
            "B": "KubeSQL",
            "C": "Postgres-Docker-Sync",
            "D": "There is no way to do this"
        },
        "answer": "A"
    },
    {
        "question": "What does 'synchronous_commit = off' do?",
        "options": {
            "A": "Disables all commits",
            "B": "Improves performance by not waiting for WAL to be flushed to disk, but risks data loss on crash",
            "C": "Encrypts all commits",
            "D": "Requires two users to commit"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Multicorn'?",
        "options": {
            "A": "A type of join",
            "B": "An extension that allows you to write Foreign Data Wrappers in Python",
            "C": "A multi-threaded server",
            "D": "A backup utility"
        },
        "answer": "B"
    },
    {
        "question": "Which view shows the background writer's activity and statistics?",
        "options": {
            "A": "pg_stat_bgwriter",
            "B": "pg_stat_activity",
            "C": "pg_writer_info",
            "D": "pg_cache_stats"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Hot Patching' in PostgreSQL?",
        "options": {
            "A": "Updating the database while it is on fire",
            "B": "The ability to apply certain minor security patches without a full restart",
            "C": "Changing a table's schema instantly",
            "D": "Deleting data quickly"
        },
        "answer": "B"
    },
    {
        "question": "Which 'pg_hba.conf' method is used for password-less authentication for local users based on the OS username?",
        "options": {
            "A": "md5",
            "B": "peer",
            "C": "trust",
            "D": "scram-sha-256"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Logical Replication Slot'?",
        "options": {
            "A": "A physical slot in a server rack",
            "B": "A mechanism to ensure the primary keeps WAL data needed for a logical subscriber",
            "C": "A type of user permission",
            "D": "A folder for backups"
        },
        "answer": "B"
    },
    {
        "question": "Which extension provides functions to encrypt specific columns of data?",
        "options": {
            "A": "pg_secure",
            "B": "pgcrypto",
            "C": "pg_vault",
            "D": "pg_encrypt"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Bloat' in a PostgreSQL table?",
        "options": {
            "A": "When the table has too many columns",
            "B": "Unused space in data files caused by many updates/deletes that VACUUM hasn't fully reclaimed",
            "C": "A very large backup file",
            "D": "Too many indexes"
        },
        "answer": "B"
    },
    {
        "question": "What does 'ANALYZE' (without VACUUM) do?",
        "options": {
            "A": "Deletes the table",
            "B": "Collects statistics about the contents of tables for the query planner",
            "C": "Checks for viruses",
            "D": "Reformats the SQL code"
        },
        "answer": "B"
    },
    {
        "question": "Congratulations! Which command exits the 'psql' terminal?",
        "options": {
            "A": "\\q",
            "B": "exit",
            "C": "quit",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "Which index type is best suited for full-text search and JSONB arrays in PostgreSQL?",
        "options": {
            "A": "B-Tree",
            "B": "GIN (Generalized Inverted Index)",
            "C": "Hash",
            "D": "BRIN"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of a 'Window Function' in PostgreSQL?",
        "options": {
            "A": "To open a new database connection",
            "B": "To perform calculations across a set of table rows related to the current row",
            "C": "To create a popup in the UI",
            "D": "To limit the number of rows returned"
        },
        "answer": "B"
    },
    {
        "question": "Which keyword is required to define the partitions for a Window Function?",
        "options": {
            "A": "GROUP BY",
            "B": "OVER",
            "C": "WINDOW",
            "D": "BETWEEN"
    },
    "answer": "B"
    },
    {
        "question": "Which command is used to update the data stored in a Materialized View?",
        "options": {
            "A": "UPDATE VIEW name;",
            "B": "REFRESH MATERIALIZED VIEW name;",
            "C": "RELOAD VIEW name;",
            "D": "ALTER VIEW name REFRESH;"
        },
        "answer": "B"
    },
    {
        "question": "Which PostgreSQL index type is specifically designed for very large tables where data is naturally sorted?",
        "options": {
            "A": "GiST",
            "B": "BRIN (Block Range Index)",
            "C": "SP-GiST",
            "D": "B-Tree"
        },
        "answer": "B"
    },
    {
        "question": "What does 'UPSERT' refer to in PostgreSQL?",
        "options": {
            "A": "An update that fails",
            "B": "An INSERT statement with an ON CONFLICT clause",
            "C": "Deleting and then inserting a row",
            "D": "Uploading data to a server"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to convert a string to a specific data type using a PostgreSQL-specific cast operator?",
        "options": {
            "A": "CAST(x AS type)",
            "B": "x::type",
            "C": "Both A and B",
            "D": "CONVERT(x, type)"
        },
        "answer": "C"
    },
    {
        "question": "Which operator is used to retrieve a value from a JSONB column as text?",
        "options": {
            "A": "->",
            "B": "->>",
            "C": "#>",
            "D": "@@"
        },
        "answer": "B"
    },
    {
        "question": "What is 'VACUUM' used for in PostgreSQL?",
        "options": {
            "A": "To delete all data",
            "B": "To reclaim storage occupied by dead tuples (deleted/updated rows)",
            "C": "To compress the database files",
            "D": "To restart the server"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to identify the current database user in a session?",
        "options": {
            "A": "SELECT current_user;",
            "B": "SELECT session_user;",
            "C": "Both A and B",
            "D": "WHOAMI;"
        },
        "answer": "C"
    },
    {
        "question": "What is the 'hstore' extension used for?",
        "options": {
            "A": "Storing history of changes",
            "B": "Storing sets of key/value pairs within a single PostgreSQL value",
            "C": "High-speed storage",
            "D": "Hardware monitoring"
        },
        "answer": "B"
    },
    {
        "question": "Which function returns the row number of the current row within its partition?",
        "options": {
            "A": "COUNT()",
            "B": "ROW_NUMBER()",
            "C": "RANK()",
            "D": "INDEX()"
        },
        "answer": "B"
    },
    {
        "question": "In a Window Function, what is the difference between RANK() and DENSE_RANK()?",
        "options": {
            "A": "RANK() leaves gaps in sequence after ties; DENSE_RANK() does not",
            "B": "DENSE_RANK() is only for numeric data",
            "C": "RANK() is faster",
            "D": "There is no difference"
        },
        "answer": "A"
    },
    {
        "question": "Which operator checks if the left JSONB value contains the right JSONB path/value?",
        "options": {
            "A": "?",
            "B": "@>",
            "C": "<@",
            "D": "&&"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to add a new partition to an existing partitioned table?",
        "options": {
            "A": "ADD PARTITION",
            "B": "CREATE TABLE ... PARTITION OF ...",
            "C": "ALTER TABLE ... ADD PARTITION",
            "D": "NEW PARTITION FOR"
        },
        "answer": "B"
    },
    {
        "question": "What is 'PL/pgSQL'?",
        "options": {
            "A": "A physical layout engine",
            "B": "A load-balancing tool",
            "C": "The procedural programming language for PostgreSQL",
            "D": "A type of join"
        },
        "answer": "C"
    },
    {
        "question": "Which function is used to generate a series of values, often used for creating dummy data or date ranges?",
        "options": {
            "A": "pd.date_range()",
            "B": "generate_series()",
            "C": "range_gen()",
            "D": "series_inc()"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Foreign Data Wrapper' (FDW)?",
        "options": {
            "A": "A way to encrypt data",
            "B": "A library for foreign keys",
            "C": "A tool to access and query data stored in external databases from within Postgres",
            "D": "A translation service for SQL"
        },
        "answer": "C"
    },
    {
        "question": "Which PostgreSQL command allows you to see the execution plan *without* running the query?",
        "options": {
            "A": "EXPLAIN",
            "B": "EXPLAIN ANALYZE",
            "C": "SHOW PLAN",
            "D": "QUERY PLAN"
        },
        "answer": "A"
    },
    {
        "question": "Which function returns the value evaluated at the row that is the 'n' rows before the current row?",
        "options": {
            "A": "LEAD()",
            "B": "LAG()",
            "C": "PREV()",
            "D": "LAST()"
        },
        "answer": "B"
    },
    {
        "question": "Which function returns the value evaluated at the row that is 'n' rows after the current row?",
        "options": {
            "A": "LAG()",
            "B": "LEAD()",
            "C": "NEXT()",
            "D": "FUTURE()"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'COALESCE'?",
        "options": {
            "A": "To combine two strings",
            "B": "To return the first non-null value in a list of arguments",
            "C": "To group similar data",
            "D": "To sort data"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to change the owner of a database?",
        "options": {
            "A": "ALTER DATABASE name OWNER TO new_owner;",
            "B": "GRANT DATABASE name TO new_owner;",
            "C": "UPDATE DATABASE owner SET new_owner;",
            "D": "CHANGE OWNER FOR name TO new_owner;"
        },
        "answer": "A"
    },
    {
        "question": "Which index type is best for geometric and spatial data types?",
        "options": {
            "A": "B-Tree",
            "B": "GiST (Generalized Search Tree)",
            "C": "Hash",
            "D": "GIN"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Autovacuum'?",
        "options": {
            "A": "A feature that deletes old backups",
            "B": "A background process that automatically runs VACUUM and ANALYZE",
            "C": "A tool for cleaning the server hardware",
            "D": "An automatic script to remove duplicates"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to create a new user-defined role in PostgreSQL?",
        "options": {
            "A": "ADD USER",
            "B": "CREATE ROLE",
            "C": "MAKE ROLE",
            "D": "NEW USER"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary difference between a 'User' and a 'Role' in PostgreSQL?",
        "options": {
            "A": "Users can own tables; roles cannot",
            "B": "A 'User' is just a 'Role' with the LOGIN attribute enabled",
            "C": "Users are for databases; roles are for servers",
            "D": "There is no difference in modern PostgreSQL"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to give a role permission to SELECT from a table?",
        "options": {
            "A": "ALLOW SELECT ON table TO role;",
            "B": "GRANT SELECT ON table TO role;",
            "C": "PERMIT SELECT ON table TO role;",
            "D": "GIVE SELECT ON table TO role;"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to remove a specific permission from a role?",
        "options": {
            "A": "REMOVE",
            "B": "REVOKE",
            "C": "TAKE",
            "D": "DENY"
        },
        "answer": "B"
    },
    {
        "question": "What does 'Table Partitioning' do in PostgreSQL?",
        "options": {
            "A": "Splits a large table into smaller physical pieces (shards) while remaining a single logical table",
            "B": "Creates a backup of the table",
            "C": "Encrypts the table data",
            "D": "Sorts the table alphabetically"
        },
        "answer": "A"
    },
    {
        "question": "Which type of partitioning splits data based on a range of values (e.g., dates)?",
        "options": {
            "A": "LIST Partitioning",
            "B": "RANGE Partitioning",
            "C": "HASH Partitioning",
            "D": "KEY Partitioning"
        },
        "answer": "B"
    },
    {
        "question": "Which type of partitioning is best for evenly distributing data across a fixed number of partitions?",
        "options": {
            "A": "LIST Partitioning",
            "B": "RANGE Partitioning",
            "C": "HASH Partitioning",
            "D": "RANDOM Partitioning"
        },
        "answer": "C"
    },
    {
        "question": "What is 'PgBouncer' primarily used for in a production environment?",
        "options": {
            "A": "Managing backups",
            "B": "Lightweight connection pooling to handle thousands of client connections",
            "C": "Query visualization",
            "D": "Automatic failover"
        },
        "answer": "B"
    },
    {
        "question": "Which pooling mode in PgBouncer is the most aggressive and allows the highest number of clients?",
        "options": {
            "A": "Session pooling",
            "B": "Transaction pooling",
            "C": "Statement pooling",
            "D": "Database pooling"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Patroni'?",
        "options": {
            "A": "A PostgreSQL backup tool",
            "B": "A template for high-availability (HA) management using Etcd or Consul",
            "C": "A specialized index type",
            "D": "A database migration script"
        },
        "answer": "B"
    },
    {
        "question": "Which parameter in 'postgresql.conf' defines the maximum number of concurrent connections?",
        "options": {
            "A": "max_users",
            "B": "max_connections",
            "C": "connection_limit",
            "D": "max_clients"
        },
        "answer": "B"
    },
    {
        "question": "What is 'maintenance_work_mem' used for?",
        "options": {
            "A": "Daily query processing",
            "B": "Memory for maintenance tasks like VACUUM, CREATE INDEX, and ALTER TABLE",
            "C": "Logging user activity",
            "D": "Connecting to standby servers"
        },
        "answer": "B"
    },
    {
        "question": "Which PostgreSQL command is used to encrypt a specific column (with the pgcrypto extension)?",
        "options": {
            "A": "ENCRYPT()",
            "B": "PGP_SYM_ENCRYPT()",
            "C": "HASH()",
            "D": "SECURE()"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Row Level Security' (RLS)?",
        "options": {
            "A": "To encrypt rows on disk",
            "B": "To restrict which rows a user can see/modify based on their identity",
            "C": "To lock rows during an update",
            "D": "To count the number of rows in a table"
        },
        "answer": "B"
    },
    {
        "question": "Which Linux kernel setting is often adjusted to help PostgreSQL manage large amounts of memory?",
        "options": {
            "A": "vm.swappiness",
            "B": "kernel.shmmax",
            "C": "Both A and B",
            "D": "net.core.somaxconn"
        },
        "answer": "C"
    },
    {
        "question": "What does 'EXPLAIN (FORMAT JSON)' do?",
        "options": {
            "A": "Converts table data to JSON",
            "B": "Outputs the query execution plan in a structured JSON format",
            "C": "Checks if the SQL is valid JSON",
            "D": "Saves the query to a file"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to see the size of a specific table in a human-readable format?",
        "options": {
            "A": "SELECT pg_size_pretty(pg_total_relation_size('table_name'));",
            "B": "SHOW TABLE SIZE table_name;",
            "C": "LIST SIZE table_name;",
            "D": "DESCRIBE SIZE table_name;"
        },
        "answer": "A"
    },
    {
        "question": "What is a 'Materialized View'?",
        "options": {
            "A": "A view that is only visible to admins",
            "B": "A view whose result is physically stored on disk and can be indexed",
            "C": "A view that deletes data after reading",
            "D": "A temporary table"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to refresh the data in a Materialized View?",
        "options": {
            "A": "UPDATE MATERIALIZED VIEW name;",
            "B": "REFRESH MATERIALIZED VIEW name;",
            "C": "RELOAD MATERIALIZED VIEW name;",
            "D": "SYNC MATERIALIZED VIEW name;"
        },
        "answer": "B"
    },
    {
        "question": "What is 'pg_stat_statements' used for?",
        "options": {
            "A": "Viewing user passwords",
            "B": "Tracking execution statistics (time, calls) for all SQL statements executed",
            "C": "Generating random SQL",
            "D": "Fixing corrupted tables"
        },
        "answer": "B"
    },
    {
        "question": "How do you enable an extension like 'PostGIS' in a database?",
        "options": {
            "A": "INSTALL EXTENSION postgis;",
            "B": "CREATE EXTENSION postgis;",
            "C": "LOAD EXTENSION postgis;",
            "D": "ADD EXTENSION postgis;"
        },
        "answer": "B"
    },
    {
        "question": "Which psql command lists all available extensions in the current database?",
        "options": {
            "A": "\\dx",
            "B": "\\de",
            "C": "\\extensions",
            "D": "SHOW EXTENSIONS;"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Barman'?",
        "options": {
            "A": "A PostgreSQL UI",
            "B": "A backup and disaster recovery manager for PostgreSQL",
            "C": "A connection pooler",
            "D": "A query optimizer"
        },
        "answer": "B"
    },
    {
        "question": "Which constraint ensures that a column does not contain duplicate values across the table?",
        "options": {
            "A": "CHECK",
            "B": "UNIQUE",
            "C": "NOT NULL",
            "D": "DEFAULT"
        },
        "answer": "B"
    },
    {
        "question": "What is the result of the 'pg_is_in_recovery()' function on a Primary server?",
        "options": {
            "A": "True",
            "B": "False",
            "C": "Null",
            "D": "Error"
        },
        "answer": "B"
    },
    {
        "question": "Which file specifies the 'Trust' or 'Password' authentication methods for users?",
        "options": {
            "A": "postgresql.conf",
            "B": "pg_hba.conf",
            "C": "pg_auth.conf",
            "D": "pg_ident.conf"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'effective_cache_size' parameter used for?",
        "options": {
            "A": "Actually allocating memory to Postgres",
            "B": "Estimating how much memory is available for OS-level disk caching to help the query planner",
            "C": "Setting the maximum file size for logs",
            "D": "Speeding up network connections"
        },
        "answer": "B"
    },
    {
        "question": "How do you permanently delete a database in PostgreSQL?",
        "options": {
            "A": "DELETE DATABASE name;",
            "B": "DROP DATABASE name;",
            "C": "REMOVE DATABASE name;",
            "D": "CLEAR DATABASE name;"
        },
        "answer": "B"
    },
    {
        "question": "Which keyword is used to start a new transaction block?",
        "options": {
            "A": "START;",
            "B": "BEGIN;",
            "C": "OPEN;",
            "D": "DO;"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to apply a transaction and make changes permanent?",
        "options": {
            "A": "SAVE;",
            "B": "COMMIT;",
            "C": "END;",
            "D": "Both B and C"
        },
        "answer": "D"
    },
    {
        "question": "Which command is used to discard all changes in a transaction?",
        "options": {
            "A": "UNDO;",
            "B": "ROLLBACK;",
            "C": "CANCEL;",
            "D": "RESET;"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Correlated Subquery'?",
        "options": {
            "A": "A query that runs in parallel",
            "B": "A subquery that refers to a column in the outer query",
            "C": "A query that is automatically cached",
            "D": "A query used only for joins"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to convert a JSONB array into a set of rows?",
        "options": {
            "A": "jsonb_to_rows()",
            "B": "jsonb_array_elements()",
            "C": "jsonb_split()",
            "D": "jsonb_unpack()"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'FOR UPDATE' clause do in a SELECT statement?",
        "options": {
            "A": "Updates the rows immediately",
            "B": "Locks the selected rows so other transactions cannot modify or lock them until the current transaction ends",
            "C": "Formats the output for an update",
            "D": "Deletes the rows after reading"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Deadlock' in PostgreSQL?",
        "options": {
            "A": "When the database crashes",
            "B": "When two transactions are waiting for each other to release locks, preventing both from proceeding",
            "C": "When a user forgets their password",
            "D": "When the disk is full"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to identify the current database name in a session?",
        "options": {
            "A": "SELECT current_database();",
            "B": "SHOW database;",
            "C": "GET DB_NAME;",
            "D": "psql \\db"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of 'VACUUM ANALYZE'?",
        "options": {
            "A": "Deletes the database",
            "B": "Reclaims space from deleted rows and updates statistics for the query planner",
            "C": "Checks for viruses",
            "D": "Backs up the database"
        },
        "answer": "B"
    },
    {
        "question": "Which log file configuration parameter tracks queries that take longer than a certain time?",
        "options": {
            "A": "log_slow_queries",
            "B": "log_min_duration_statement",
            "C": "log_query_time",
            "D": "debug_query_threshold"
        },
        "answer": "B"
    },
    {
        "question": "Which operator is used for element-wise string concatenation in PostgreSQL?",
        "options": {
            "A": "+",
            "B": "||",
            "C": "&",
            "D": "CONCAT"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Streaming Replication' lag?",
        "options": {
            "A": "The physical distance between servers",
            "B": "The delay between a change occurring on the Primary and it being applied on the Standby",
            "C": "The time it takes to backup",
            "D": "The number of users connected"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to calculate the age (interval) between two timestamps?",
        "options": {
            "A": "AGE(timestamp1, timestamp2)",
            "B": "DIFF(timestamp1, timestamp2)",
            "C": "INTERVAL(timestamp1, timestamp2)",
            "D": "TIME_BETWEEN(timestamp1, timestamp2)"
        },
        "answer": "A"
    },
    {
        "question": "What does the 'FILLFACTOR' parameter for a table control?",
        "options": {
            "A": "The maximum number of rows",
            "B": "The percentage of each data page that is packed, leaving space for future updates to avoid page splits",
            "C": "The speed of the disk",
            "D": "The number of indexes allowed"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to move a table from one tablespace to another?",
        "options": {
            "A": "MOVE TABLE name TO tablespace;",
            "B": "ALTER TABLE name SET TABLESPACE new_tablespace;",
            "C": "CHANGE TABLESPACE FOR name TO new_tablespace;",
            "D": "UPDATE TABLE location SET tablespace;"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Full Page Writes' in PostgreSQL?",
        "options": {
            "A": "Writing a whole book",
            "B": "A safety mechanism where the first time a data page is modified after a checkpoint, the whole page is written to WAL",
            "C": "Increasing the font size of results",
            "D": "A way to print the database"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to return the current PostgreSQL server version?",
        "options": {
            "A": "VERSION()",
            "B": "SHOW VERSION;",
            "C": "GET_VERSION()",
            "D": "Both A and B"
        },
        "answer": "D"
    },
    {
        "question": "What is 'pg_pathman'?",
        "options": {
            "A": "A game",
            "B": "An extension for optimized partition management",
            "C": "A backup utility",
            "D": "A tool to view table paths"
        },
        "answer": "B"
    },
    {
        "question": "Which command lists all roles/users in the psql terminal?",
        "options": {
            "A": "\\du",
            "B": "\\dr",
            "C": "\\roles",
            "D": "LIST USERS;"
        },
        "answer": "A"
    },
    {
        "question": "What is the result of '1 / 0' in PostgreSQL?",
        "options": {
            "A": "Infinity",
            "B": "Division by zero error",
            "C": "Null",
            "D": "0"
        },
        "answer": "B"
    },
    {
        "question": "Which view displays information about all active connections and their current state?",
        "options": {
            "A": "pg_connections",
            "B": "pg_stat_activity",
            "C": "pg_users_online",
            "D": "pg_session_stats"
        },
        "answer": "B"
    },
    {
        "question": "Final question: What is the most common extension for handling spatial/location data in PostgreSQL?",
        "options": {
            "A": "PostGIS",
            "B": "pg_spatial",
            "C": "pg_geo",
            "D": "LocationDB"
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
    skill = "PostgreSQL"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
