from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS =  [
    {
        "question": "What does SQL stand for?",
        "options": {
            "A": "Structured Query Language",
            "B": "Simple Query Language",
            "C": "Standard Query List",
            "D": "System Query Logic"
        },
        "answer": "A"
    },
    {
        "question": "Which command is used to create a new database in MySQL?",
        "options": {
            "A": "MAKE DATABASE name;",
            "B": "CREATE DATABASE name;",
            "C": "NEW DATABASE name;",
            "D": "ADD DATABASE name;"
        },
        "answer": "B"
    },
    {
        "question": "Which statement is used to delete a table and all its data from a database?",
        "options": {
            "A": "REMOVE TABLE name;",
            "B": "DELETE TABLE name;",
            "C": "DROP TABLE name;",
            "D": "TRUNCATE TABLE name;"
        },
        "answer": "C"
    },
    {
        "question": "Which data type is best for storing long text or descriptions?",
        "options": {
            "A": "VARCHAR",
            "B": "INT",
            "C": "TEXT",
            "D": "CHAR"
        },
        "answer": "C"
    },
    {
        "question": "What is the purpose of the 'PRIMARY KEY' constraint?",
        "options": {
            "A": "To allow duplicate values",
            "B": "To uniquely identify each record in a table",
            "C": "To group similar data together",
            "D": "To sort the data alphabetically"
        },
        "answer": "B"
    },
    {
        "question": "Which keyword is used to add a new column to an existing table?",
        "options": {
            "A": "UPDATE",
            "B": "ALTER TABLE",
            "C": "INSERT INTO",
            "D": "MODIFY"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to see the list of all databases available on the server?",
        "options": {
            "A": "GET DATABASES;",
            "B": "SHOW DATABASES;",
            "C": "LIST DATABASES;",
            "D": "DISPLAY DATABASES;"
        },
        "answer": "B"
    },
    {
        "question": "How do you select a database to start working with it?",
        "options": {
            "A": "OPEN database_name;",
            "B": "SELECT database_name;",
            "C": "USE database_name;",
            "D": "CONNECT database_name;"
        },
        "answer": "C"
    },
    {
        "question": "What is the maximum length of a VARCHAR column in modern MySQL versions?",
        "options": {
            "A": "255 characters",
            "B": "65,535 characters",
            "C": "Unlimited",
            "D": "1,024 characters"
        },
        "answer": "B"
    },
    {
        "question": "Which constraint ensures that a column cannot have a NULL value?",
        "options": {
            "A": "UNIQUE",
            "B": "NOT NULL",
            "C": "DEFAULT",
            "D": "CHECK"
        },
        "answer": "B"
    },
    {
        "question": "What does the TRUNCATE command do?",
        "options": {
            "A": "Deletes the table structure",
            "B": "Deletes all rows in a table but keeps the structure",
            "C": "Renames the table",
            "D": "Deletes only the last row"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to change the data type of an existing column?",
        "options": {
            "A": "ALTER TABLE name MODIFY column type;",
            "B": "UPDATE TABLE name SET type;",
            "C": "CHANGE COLUMN name type;",
            "D": "ALTER DATABASE name type;"
        },
        "answer": "A"
    },
    {
        "question": "What is a 'Foreign Key'?",
        "options": {
            "A": "A key that is not used in MySQL",
            "B": "A field in one table that refers to the Primary Key in another table",
            "C": "A key used for encryption",
            "D": "The main password for the database"
        },
        "answer": "B"
    },
    {
        "question": "Which numeric data type should be used for exact currency calculations?",
        "options": {
            "A": "FLOAT",
            "B": "DOUBLE",
            "C": "DECIMAL",
            "D": "INT"
        },
        "answer": "C"
    },
    {
        "question": "What is the command to delete a database permanently?",
        "options": {
            "A": "DELETE DATABASE name;",
            "B": "REMOVE DATABASE name;",
            "C": "DROP DATABASE name;",
            "D": "CLEAR DATABASE name;"
        },
        "answer": "C"
    },
    {
        "question": "Which command provides the structure/schema details of a specific table?",
        "options": {
            "A": "VIEW table_name;",
            "B": "DESCRIBE table_name;",
            "C": "SHOW table_name;",
            "D": "STRUCT table_name;"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'AUTO_INCREMENT' attribute do?",
        "options": {
            "A": "Increases the server speed",
            "B": "Automatically generates a unique number for new rows",
            "C": "Automatically backs up the database",
            "D": "Increases the size of the column"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to rename an existing table?",
        "options": {
            "A": "RENAME TABLE old_name TO new_name;",
            "B": "UPDATE TABLE name SET new_name;",
            "C": "ALTER TABLE old_name RENAME new_name;",
            "D": "Both A and C"
        },
        "answer": "D"
    },
    {
        "question": "Which SQL category does the CREATE command fall into?",
        "options": {
            "A": "DML",
            "B": "DDL",
            "C": "DQL",
            "D": "DCL"
        },
        "answer": "B"
    },
    {
        "question": "How do you add a 'UNIQUE' constraint to a column during table creation?",
        "options": {
            "A": "column_name type UNIQUE",
            "B": "column_name type ONLY",
            "C": "column_name type PRIMARY",
            "D": "column_name type DISTINCT"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of the 'DEFAULT' constraint?",
        "options": {
            "A": "To make the column a primary key",
            "B": "To provide a value for the column if none is specified",
            "C": "To prevent null values",
            "D": "To sort the table"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is a valid storage engine in MySQL?",
        "options": {
            "A": "InnoDB",
            "B": "MyISAM",
            "C": "Memory",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "Which storage engine is the default for MySQL (version 5.5.5 and later) and supports transactions?",
        "options": {
            "A": "MyISAM",
            "B": "InnoDB",
            "C": "Archive",
            "D": "CSV"
        },
        "answer": "B"
    },
    {
        "question": "Which data type is used to store fixed-length strings?",
        "options": {
            "A": "VARCHAR",
            "B": "CHAR",
            "C": "STRING",
            "D": "TEXT"
        },
        "answer": "B"
    },
    {
        "question": "What happens if you try to insert a duplicate value into a column with a 'UNIQUE' constraint?",
        "options": {
            "A": "MySQL overwrites the old value",
            "B": "MySQL throws an error and the insertion fails",
            "C": "MySQL creates a new table",
            "D": "MySQL ignores the constraint"
        },
        "answer": "B"
    },
    {
        "question": "Which statement is used to remove a column from a table?",
        "options": {
            "A": "ALTER TABLE name DELETE column;",
            "B": "ALTER TABLE name DROP COLUMN column;",
            "C": "REMOVE COLUMN from name;",
            "D": "DELETE column FROM name;"
        },
        "answer": "B"
    },
    {
        "question": "What is the correct syntax to create a table?",
        "options": {
            "A": "CREATE TABLE table_name (col1 type, col2 type);",
            "B": "NEW TABLE table_name (col1 type);",
            "C": "MAKE TABLE table_name col1 type;",
            "D": "CREATE table_name AS TABLE (col1 type);"
        },
        "answer": "A"
    },
    {
        "question": "What is the range of a TINYINT signed column?",
        "options": {
            "A": "0 to 255",
            "B": "-128 to 127",
            "C": "-32768 to 32767",
            "D": "0 to 100"
        },
        "answer": "B"
    },
    {
        "question": "Which data type stores date and time in 'YYYY-MM-DD HH:MM:SS' format?",
        "options": {
            "A": "DATE",
            "B": "TIMESTAMP",
            "C": "DATETIME",
            "D": "TIME"
        },
        "answer": "C"
    },
    {
        "question": "What is the command to see the structure of all tables in a database?",
        "options": {
            "A": "SHOW TABLES;",
            "B": "DESCRIBE TABLES;",
            "C": "LIST TABLES;",
            "D": "GET TABLES;"
        },
        "answer": "A"
    },
    {
        "question": "Which command is used to add a comment to a column definition?",
        "options": {
            "A": "COMMENT 'text'",
            "B": "NOTE 'text'",
            "C": "REMARK 'text'",
            "D": "DESC 'text'"
        },
        "answer": "A"
    },
    {
        "question": "What is the difference between DROP and DELETE?",
        "options": {
            "A": "DROP removes data, DELETE removes the table",
            "B": "DROP removes the table structure, DELETE removes rows from the table",
            "C": "They are the same",
            "D": "DROP is for databases only"
        },
        "answer": "B"
    },
    {
        "question": "Which data type is used for storing binary data like images or files?",
        "options": {
            "A": "TEXT",
            "B": "BLOB",
            "C": "VARCHAR",
            "D": "BINARY"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to start the MySQL command-line client?",
        "options": {
            "A": "start mysql",
            "B": "mysql -u username -p",
            "C": "connect mysql",
            "D": "run mysql"
        },
        "answer": "B"
    },
    {
        "question": "Which constraint is used to link two tables together?",
        "options": {
            "A": "PRIMARY KEY",
            "B": "FOREIGN KEY",
            "C": "UNIQUE",
            "D": "LINK"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'DESC' keyword in a table description?",
        "options": {
            "A": "To sort the results",
            "B": "It is an alias for DESCRIBE to show table metadata",
            "C": "To delete the table",
            "D": "To show hidden columns"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is NOT a valid integer type in MySQL?",
        "options": {
            "A": "SMALLINT",
            "B": "MEDIUMINT",
            "C": "LARGEINT",
            "D": "BIGINT"
        },
        "answer": "C"
    },
    {
        "question": "What is the result of selecting a database that does not exist?",
        "options": {
            "A": "MySQL creates it automatically",
            "B": "MySQL throws an 'Unknown database' error",
            "C": "MySQL selects the default database",
            "D": "Nothing happens"
        },
        "answer": "B"
    },
    {
        "question": "Which command allows you to change the character set of a table?",
        "options": {
            "A": "ALTER TABLE name CHARACTER SET utf8;",
            "B": "UPDATE TABLE name SET CHARSET utf8;",
            "C": "MODIFY TABLE CHARSET utf8;",
            "D": "SET TABLE name CHARSET utf8;"
        },
        "answer": "A"
    },
    {
        "question": "What is a 'Database Schema'?",
        "options": {
            "A": "The data inside the tables",
            "B": "The logical structure and organization of the database",
            "C": "The user password",
            "D": "The physical server hardware"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to create a table with the same structure as another table?",
        "options": {
            "A": "CREATE TABLE new LIKE old;",
            "B": "COPY TABLE old TO new;",
            "C": "CREATE TABLE new AS old;",
            "D": "DUPLICATE TABLE old TO new;"
        },
        "answer": "A"
    },
    {
        "question": "What does 'INT(11)' mean in MySQL?",
        "options": {
            "A": "It limits the number to 11 digits",
            "B": "It is a display width hint (doesn't affect storage or range)",
            "C": "It uses 11 bytes of storage",
            "D": "It is deprecated"
        },
        "answer": "B"
    },
    {
        "question": "Which constraint ensures all values in a column are unique and NOT NULL?",
        "options": {
            "A": "UNIQUE",
            "B": "PRIMARY KEY",
            "C": "INDEX",
            "D": "CHECK"
        },
        "answer": "B"
    },
    {
        "question": "Can a table have more than one PRIMARY KEY?",
        "options": {
            "A": "Yes",
            "B": "No"
        },
        "answer": "B"
    },
    {
        "question": "Can a table have more than one FOREIGN KEY?",
        "options": {
            "A": "Yes",
            "B": "No"
        },
        "answer": "A"
    },
    {
        "question": "Which command is used to view the SQL statement that created a specific table?",
        "options": {
            "A": "SHOW TABLE name;",
            "B": "SHOW CREATE TABLE name;",
            "C": "DESCRIBE CREATE TABLE name;",
            "D": "GET CREATE TABLE name;"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'IF EXISTS' clause in DROP TABLE?",
        "options": {
            "A": "To create the table if it doesn't exist",
            "B": "To prevent an error if the table is already missing",
            "C": "To check for data inside the table",
            "D": "To archive the table before dropping"
        },
        "answer": "B"
    },
    {
        "question": "Which data type is most efficient for storing 'Yes/No' or 'True/False' values?",
        "options": {
            "A": "BOOLEAN (Alias for TINYINT(1))",
            "B": "VARCHAR(5)",
            "C": "INT",
            "D": "TEXT"
        },
        "answer": "A"
    },
    {
        "question": "What command is used to clear the screen in the MySQL command line?",
        "options": {
            "A": "CLEAR",
            "B": "system cls (Windows) or system clear (Linux)",
            "C": "CLS",
            "D": "RESET"
        },
        "answer": "B"
    },
    {
        "question": "Which keyword is used to stop the current MySQL session?",
        "options": {
            "A": "STOP",
            "B": "EXIT or QUIT",
            "C": "CLOSE",
            "D": "END"
        },
        "answer": "B"
    },
    {
"question": "Which command is used to retrieve data from a database?",
"options": {
"A": "GET",
"B": "SELECT",
"C": "EXTRACT",
"D": "OPEN"
},
"answer": "B"
},
{
"question": "Which clause is used to filter records based on a specific condition?",
"options": {
"A": "GROUP BY",
"B": "WHERE",
"C": "SORT",
"D": "IF"
},
"answer": "B"
},
{
"question": "How do you select all columns from a table named 'Users'?",
"options": {
"A": "SELECT all FROM Users;",
"B": "SELECT * FROM Users;",
"C": "SELECT Users FROM ;",
"D": "SHOW Users;"
},
"answer": "B"
},
{
"question": "Which keyword is used to sort the result-set?",
"options": {
"A": "SORT BY",
"B": "ORDER BY",
"C": "ALIGN",
"D": "GROUP BY"
},
"answer": "B"
},
{
"question": "What is the default sorting order of the ORDER BY clause?",
"options": {
"A": "Descending (DESC)",
"B": "Ascending (ASC)",
"C": "Random",
"D": "Alphabetical only"
},
"answer": "B"
},
{
"question": "Which command is used to add new rows of data into a table?",
"options": {
"A": "ADD RECORD",
"B": "INSERT INTO",
"C": "UPDATE",
"D": "NEW ROW"
},
"answer": "B"
},
{
"question": "Which keyword is used to update existing data within a table?",
"options": {
"A": "MODIFY",
"B": "UPDATE",
"C": "CHANGE",
"D": "SAVE"
},
"answer": "B"
},
{
"question": "What happens if you use an UPDATE statement without a WHERE clause?",
"options": {
"A": "Nothing happens",
"B": "All records in the table will be updated",
"C": "MySQL will throw an error",
"D": "Only the first record is updated"
},
"answer": "B"
},
{
"question": "Which command is used to remove specific rows from a table?",
"options": {
"A": "REMOVE",
"B": "DELETE FROM",
"C": "DROP",
"D": "TRUNCATE"
},
"answer": "B"
},
{
"question": "Which keyword is used to return only different (unique) values in a SELECT statement?",
"options": {
"A": "UNIQUE",
"B": "DISTINCT",
"C": "DIFFERENT",
"D": "SINGLE"
},
"answer": "B"
},
{
"question": "How do you select the first 5 records from a table in MySQL?",
"options": {
"A": "SELECT TOP 5 * FROM Users;",
"B": "SELECT * FROM Users LIMIT 5;",
"C": "SELECT * FROM Users FETCH FIRST 5;",
"D": "SELECT FIRST 5 * FROM Users;"
},
"answer": "B"
},
{
"question": "Which operator is used to search for a specified pattern in a column?",
"options": {
"A": "GET",
"B": "LIKE",
"C": "MATCH",
"D": "CONTAINS"
},
"answer": "B"
},
{
"question": "In a LIKE pattern, which wildcard character represents zero, one, or multiple characters?",
"options": {
"A": "_ (underscore)",
"B": "% (percent)",
"C": " (asterisk)",
"D": "? (question mark)"
},
"answer": "B"
},
{
"question": "In a LIKE pattern, which wildcard character represents a single character?",
"options": {
"A": "%",
"B": "_",
"C": "#",
"D": "?"
},
"answer": "B"
},
{
"question": "Which operator is used to select values within a given range (inclusive)?",
"options": {
"A": "AMONG",
"B": "BETWEEN",
"C": "IN",
"D": "RANGE"
},
"answer": "B"
},
{
"question": "Which operator allows you to specify multiple values in a WHERE clause?",
"options": {
"A": "BETWEEN",
"B": "IN",
"C": "LIKE",
"D": "OR"
},
"answer": "B"
},
{
"question": "Which logical operator displays a record if both the first and second conditions are true?",
"options": {
"A": "OR",
"B": "AND",
"C": "BOTH",
"D": "PLUS"
},
"answer": "B"
},
{
"question": "Which keyword is used to sort the results in descending order?",
"options": {
"A": "DOWN",
"B": "DESC",
"C": "REVERSE",
"D": "BACK"
},
"answer": "B"
},
{
"question": "How do you check for a NULL value in a WHERE clause?",
"options": {
"A": "column = NULL",
"B": "column IS NULL",
"C": "column IS EMPTY",
"D": "column == NULL"
},
"answer": "B"
},
{
"question": "Which of the following is the correct syntax for an INSERT statement?",
"options": {
"A": "INSERT (col1) INTO Table VALUES (val1);",
"B": "INSERT INTO Table (col1) VALUES (val1);",
"C": "INSERT Table VALUES (val1);",
"D": "ADD INTO Table VALUES (val1);"
},
"answer": "B"
},
{
"question": "Which keyword is used to alias a column or table name in a query?",
"options": {
"A": "NAME",
"B": "AS",
"C": "SET",
"D": "USING"
},
"answer": "B"
},
{
"question": "Which operator is used to combine two or more SELECT statements (returning distinct rows)?",
"options": {
"A": "JOIN",
"B": "UNION",
"C": "COMBINE",
"D": "MERGE"
},
"answer": "B"
},
{
"question": "What is the result of 'SELECT 5 + 10;' in MySQL?",
"options": {
"A": "An error",
"B": "15",
"C": "510",
"D": "NULL"
},
"answer": "B"
},
{
"question": "Which keyword is used to provide a specific value for an UPDATE statement?",
"options": {
"A": "WHERE",
"B": "SET",
"C": "VALUE",
"D": "ASSIGN"
},
"answer": "B"
},
{
"question": "Which of the following will select all users whose name starts with 'A'?",
"options": {
"A": "SELECT * FROM Users WHERE name = 'A%';",
"B": "SELECT * FROM Users WHERE name LIKE 'A%';",
"C": "SELECT * FROM Users WHERE name LIKE '%A';",
"D": "SELECT * FROM Users WHERE name CONTAINS 'A';"
},
"answer": "B"
},
{
"question": "Which command is used to delete all data from a table without removing the table structure?",
"options": {
"A": "DROP TABLE",
"B": "TRUNCATE TABLE",
"C": "REMOVE TABLE",
"D": "CLEAR TABLE"
},
"answer": "B"
},
{
"question": "In a SELECT statement, where does the ORDER BY clause typically appear?",
"options": {
"A": "Before the FROM clause",
"B": "At the very end of the query",
"C": "Immediately after the SELECT keyword",
"D": "Inside the WHERE clause"
},
"answer": "B"
},
{
"question": "Which operator is used to find values that are NOT NULL?",
"options": {
"A": "IS NOT NULL",
"B": "NOT NULL",
"C": "!= NULL",
"D": "<> NULL"
},
"answer": "A"
},
{
"question": "How do you insert multiple rows in a single INSERT statement?",
"options": {
"A": "INSERT INTO Table VALUES (row1), (row2);",
"B": "INSERT INTO Table VALUES (row1) AND (row2);",
"C": "INSERT MULTIPLE INTO Table VALUES (row1), (row2);",
"D": "You cannot insert multiple rows at once"
},
"answer": "A"
},
{
"question": "Which clause is used to sort results by multiple columns?",
"options": {
"A": "ORDER BY col1, col2",
"B": "SORT BY col1 THEN col2",
"C": "ORDER BY col1 AND col2",
"D": "GROUP BY col1, col2"
},
"answer": "A"
},
{
"question": "What does 'SELECT 1;' return in the MySQL console?",
"options": {
"A": "Nothing",
"B": "1",
"C": "TRUE",
"D": "An error"
},
"answer": "B"
},
{
"question": "Which keyword is used to handle 'Top-N' queries in MySQL?",
"options": {
"A": "TOP",
"B": "LIMIT",
"C": "ROWNUM",
"D": "FETCH"
},
"answer": "B"
},
{
"question": "How do you find users with an age between 18 and 25 (including 18 and 25)?",
"options": {
"A": "WHERE age BETWEEN 18 AND 25",
"B": "WHERE age > 18 AND age < 25",
"C": "WHERE age IN (18, 25)",
"D": "WHERE age >= 18 OR age <= 25"
},
"answer": "A"
},
{
"question": "Which comparison operator means 'Not Equal to' in MySQL?",
"options": {
"A": "!=",
"B": "<>",
"C": "Both A and B",
"D": "NOT ="
},
"answer": "C"
},
{
"question": "What is the purpose of 'SELECT DISTINCT column1, column2'?",
"options": {
"A": "Find unique values for column1 only",
"B": "Find unique combinations of column1 and column2",
"C": "Find values where column1 does not equal column2",
"D": "It is an invalid syntax"
},
"answer": "B"
},
{
"question": "How do you select rows where the 'city' is 'Paris', 'London', or 'Berlin'?",
"options": {
"A": "WHERE city IN ('Paris', 'London', 'Berlin')",
"B": "WHERE city = ('Paris', 'London', 'Berlin')",
"C": "WHERE city LIKE ('Paris', 'London', 'Berlin')",
"D": "WHERE city AMONG ('Paris', 'London', 'Berlin')"
},
"answer": "A"
},
{
"question": "In an UPDATE statement, which keyword connects the column name to its new value?",
"options": {
"A": "AS",
"B": "SET",
"C": "TO",
"D": "WITH"
},
"answer": "B"
},
{
"question": "What is the default behavior of the UNION operator?",
"options": {
"A": "Keeps all duplicates",
"B": "Removes duplicate rows",
"C": "Only returns duplicates",
"D": "Sorts the result automatically"
},
"answer": "B"
},
{
"question": "Which command is used to get all rows from Table A that are also in Table B?",
"options": {
"A": "UNION",
"B": "INNER JOIN",
"C": "OUTER JOIN",
"D": "MINUS"
},
"answer": "B"
},
{
"question": "Which wildcard matches any user whose name ends with 'y'?",
"options": {
"A": "LIKE 'y%'",
"B": "LIKE '%y'",
"C": "LIKE 'y'",
"D": "LIKE '*y'"
},
"answer": "B"
},
{
"question": "Can you use the WHERE clause with the DELETE statement?",
"options": {
"A": "Yes",
"B": "No"
},
"answer": "A"
},
{
"question": "What is the maximum number of tables that can be joined in a single MySQL query?",
"options": {
"A": "32",
"B": "61",
"C": "Unlimited",
"D": "255"
},
"answer": "B"
},
{
"question": "Which of these is used to concatenate strings in MySQL?",
"options": {
"A": "CONCAT() function",
"B": "The '+' operator",
"C": "The '||' operator",
"D": "The '&' operator"
},
"answer": "A"
},
{
"question": "How do you select records where 'price' is greater than 100 and 'stock' is greater than 0?",
"options": {
"A": "WHERE price > 100 AND stock > 0",
"B": "WHERE price > 100 OR stock > 0",
"C": "WHERE price > 100, stock > 0",
"D": "WHERE price > 100 && stock > 0"
},
"answer": "A"
},
{
"question": "Which keyword is used to combine columns from multiple tables based on a related column?",
"options": {
"A": "UNION",
"B": "JOIN",
"C": "COMBINE",
"D": "LINK"
},
"answer": "B"
},
{
"question": "What is the limit of the OFFSET in a LIMIT clause?",
"options": {
"A": "It specifies where to start returning rows",
"B": "It specifies how many rows to return",
"C": "It specifies the maximum row length",
"D": "It is not a valid keyword"
},
"answer": "A"
},
{
"question": "How do you select users whose name has 'a' as the second character?",
"options": {
"A": "WHERE name LIKE 'a%'",
"B": "WHERE name LIKE 'a%'",
"C": "WHERE name LIKE '%a'",
"D": "WHERE name LIKE 'a%'"
},
"answer": "A"
},
{
"question": "What does the query 'SELECT * FROM Users ORDER BY name DESC, age ASC;' do?",
"options": {
"A": "Sorts by name Z-A, then by age 0-9 for users with the same name",
"B": "Sorts by name A-Z, then by age 9-0",
"C": "Throws an error because you can't use DESC and ASC together",
"D": "Only sorts by age"
},
"answer": "A"
},
{
"question": "Which statement is used to remove all records from a table, but cannot be rolled back in most configurations?",
"options": {
"A": "DELETE FROM",
"B": "TRUNCATE",
"C": "DROP",
"D": "REMOVE"
},
"answer": "B"
},
{
"question": "Which operator is used to search for a value that is NOT within a range?",
"options": {
"A": "NOT BETWEEN",
"B": "OUTSIDE",
"C": "EXCLUDE",
"D": "NOT IN RANGE"
},
"answer": "A"
},
{
"question": "Which aggregate function is used to return the total number of rows that match a specific criterion?",
"options": {
"A": "SUM()",
"B": "COUNT()",
"C": "TOTAL()",
"D": "NUMBER()"
},
"answer": "B"
},
{
"question": "Which function is used to calculate the average value of a numeric column?",
"options": {
"A": "MEAN()",
"B": "AVG()",
"C": "MID()",
"D": "AVERAGE()"
},
"answer": "B"
},
{
"question": "Which function returns the highest value in a set of values?",
"options": {
"A": "TOP()",
"B": "MAX()",
"C": "HIGH()",
"D": "UPPER()"
},
"answer": "B"
},
{
"question": "Which function returns the lowest value in a set of values?",
"options": {
"A": "MIN()",
"B": "LOW()",
"C": "BOTTOM()",
"D": "LEAST()"
},
"answer": "A"
},
{
"question": "Which function is used to calculate the total sum of a numeric column?",
"options": {
"A": "ADD()",
"B": "SUM()",
"C": "TOTAL()",
"D": "PLUS()"
},
"answer": "B"
},
{
"question": "Which clause is used with aggregate functions to group the result-set by one or more columns?",
"options": {
"A": "ORDER BY",
"B": "GROUP BY",
"C": "SORT BY",
"D": "CATEGORY BY"
},
"answer": "B"
},
{
"question": "Why can't you use the WHERE clause to filter groups created by GROUP BY?",
"options": {
"A": "Because WHERE filters individual rows before grouping occurs",
"B": "Because WHERE only works with the SELECT clause",
"C": "Because WHERE is slower than HAVING",
"D": "It is actually possible to use WHERE for this"
},
"answer": "A"
},
{
"question": "Which clause is specifically used to filter groups based on aggregate values?",
"options": {
"A": "WHERE",
"B": "HAVING",
"C": "FILTER",
"D": "GROUP WHERE"
},
"answer": "B"
},
{
"question": "What is the correct order of clauses in a SQL query?",
"options": {
"A": "SELECT, FROM, WHERE, GROUP BY, HAVING, ORDER BY",
"B": "SELECT, FROM, GROUP BY, WHERE, HAVING, ORDER BY",
"C": "SELECT, FROM, HAVING, WHERE, GROUP BY, ORDER BY",
"D": "SELECT, WHERE, FROM, GROUP BY, HAVING, ORDER BY"
},
"answer": "A"
},
{
"question": "What does COUNT() do?",
"options": {
"A": "Counts only non-null values in the first column",
"B": "Counts all rows in the table, including those with NULL values",
"C": "Counts only unique rows",
"D": "Throws an error if there are no rows"
},
"answer": "B"
},
{
"question": "How do you count the number of unique cities in a 'Customers' table?",
"options": {
"A": "SELECT COUNT(city) FROM Customers;",
"B": "SELECT COUNT(DISTINCT city) FROM Customers;",
"C": "SELECT DISTINCT COUNT(city) FROM Customers;",
"D": "SELECT COUNT(UNIQUE city) FROM Customers;"
},
"answer": "B"
},
{
"question": "What is the result of SUM() on a column that contains only NULL values?",
"options": {
"A": "0",
"B": "NULL",
"C": "An error",
"D": "1"
},
"answer": "B"
},
{
"question": "Which of the following is a valid query to find the total salary for each department?",
"options": {
"A": "SELECT dept, SUM(salary) FROM employees WHERE dept = 'Sales';",
"B": "SELECT dept, SUM(salary) FROM employees GROUP BY dept;",
"C": "SELECT SUM(salary) FROM employees HAVING dept;",
"D": "SELECT dept, TOTAL(salary) FROM employees GROUP BY dept;"
},
"answer": "B"
},
{
"question": "Can you use multiple aggregate functions in a single SELECT statement?",
"options": {
"A": "Yes",
"B": "No"
},
"answer": "A"
},
{
"question": "How do you filter for departments where the average salary is greater than 50,000?",
"options": {
"A": "WHERE AVG(salary) > 50000",
"B": "HAVING AVG(salary) > 50000",
"C": "GROUP BY salary > 50000",
"D": "WHERE salary > 50000"
},
"answer": "B"
},
{
"question": "Which function would you use to find the alphabetically last name in a column?",
"options": {
"A": "LAST()",
"B": "MAX()",
"C": "END()",
"D": "TOP()"
},
"answer": "B"
},
{
"question": "What is 'Aggregated Data'?",
"options": {
"A": "Data that has been encrypted",
"B": "Data that has been combined or summarized into a single value",
"C": "Data that has been deleted",
"D": "Data that is stored in multiple tables"
},
"answer": "B"
},
{
"question": "Which of these cannot be used with the GROUP BY clause?",
"options": {
"A": "Column names",
"B": "Aliases",
"C": "Column positions (e.g., GROUP BY 1)",
"D": "All of the above can be used"
},
"answer": "D"
},
{
"question": "What happens if you use an aggregate function without a GROUP BY clause for a table with 100 rows?",
"options": {
"A": "It returns 100 separate results",
"B": "It treats the entire table as a single group and returns 1 row",
"C": "It throws a syntax error",
"D": "It returns 0"
},
"answer": "B"
},
{
"question": "How do you find the total number of orders placed in the year 2023?",
"options": {
"A": "SELECT COUNT() FROM orders WHERE order_date LIKE '2023%';",
"B": "SELECT SUM() FROM orders WHERE year = 2023;",
"C": "SELECT COUNT() FROM orders HAVING year = 2023;",
"D": "SELECT TOTAL() FROM orders WHERE order_date = 2023;"
},
"answer": "A"
},
{
"question": "Which function ignores NULL values by default?",
"options": {
"A": "SUM()",
"B": "AVG()",
"C": "COUNT(column_name)",
"D": "All of the above"
},
"answer": "D"
},
{
"question": "What is the result of 'SELECT COUNT(NULL);'?",
"options": {
"A": "1",
"B": "0",
"C": "NULL",
"D": "Error"
},
"answer": "B"
},
{
"question": "In a GROUP BY query, every column in the SELECT list must either be an aggregate function or listed in the GROUP BY clause. True or False?",
"options": {
"A": "True (standard SQL rule)",
"B": "False"
},
"answer": "A"
},
{
"question": "Which operator is often used within a HAVING clause?",
"options": {
"A": "=",
"B": ">",
"C": "IN",
"D": "All of the above"
},
"answer": "D"
},
{
"question": "How do you find the minimum and maximum price in the 'Products' table in one query?",
"options": {
"A": "SELECT MIN(price), MAX(price) FROM Products;",
"B": "SELECT MIN(price) AND MAX(price) FROM Products;",
"C": "SELECT RANGE(price) FROM Products;",
"D": "SELECT LIMITS(price) FROM Products;"
},
"answer": "A"
},
{
"question": "Which function would you use to get the current date and time in MySQL?",
"options": {
"A": "GETDATE()",
"B": "NOW()",
"C": "CURRENT()",
"D": "TIME()"
},
"answer": "B"
},
{
"question": "What is the purpose of the 'WITH ROLLUP' modifier in a GROUP BY clause?",
"options": {
"A": "To sort the groups",
"B": "To provide summary rows (subtotals and grand totals) in the result set",
"C": "To group by every column automatically",
"D": "To roll back the transaction if it fails"
},
"answer": "B"
},
{
"question": "How do you find the average price of products, but only for categories with more than 10 products?",
"options": {
"A": "SELECT category, AVG(price) FROM Products GROUP BY category HAVING COUNT() > 10;",
"B": "SELECT category, AVG(price) FROM Products WHERE COUNT() > 10 GROUP BY category;",
"C": "SELECT category, AVG(price) FROM Products GROUP BY category WHERE COUNT() > 10;",
"D": "SELECT category, AVG(price) FROM Products HAVING COUNT() > 10;"
},
"answer": "A"
},
{
"question": "Which function can be used to round a numeric value to a specified number of decimal places?",
"options": {
"A": "FIX()",
"B": "ROUND()",
"C": "DECIMAL()",
"D": "APPROX()"
},
"answer": "B"
},
{
"question": "Which function returns only the current date (without the time)?",
"options": {
"A": "CURDATE()",
"B": "DATEONLY()",
"C": "NOW()",
"D": "TODAY()"
},
"answer": "A"
},
{
"question": "What does the 'GROUP_CONCAT()' function do in MySQL?",
"options": {
"A": "Adds numbers in a group",
"B": "Concatenates strings from a group into a single string with a delimiter",
"C": "Joins two tables together",
"D": "Counts the strings in a group"
},
"answer": "B"
},
{
"question": "How do you get the total quantity of items sold for each 'product_id'?",
"options": {
"A": "SELECT product_id, SUM(quantity) FROM sales GROUP BY product_id;",
"B": "SELECT product_id, COUNT(quantity) FROM sales GROUP BY product_id;",
"C": "SELECT product_id, TOTAL(quantity) FROM sales GROUP BY product_id;",
"D": "SELECT product_id, ADD(quantity) FROM sales GROUP BY product_id;"
},
"answer": "A"
},
{
"question": "What is the difference between COUNT(column) and COUNT(DISTINCT column)?",
"options": {
"A": "COUNT(column) counts all non-null values; COUNT(DISTINCT column) counts only unique non-null values",
"B": "There is no difference",
"C": "COUNT(DISTINCT) includes NULL values",
"D": "COUNT(column) is faster"
},
"answer": "A"
},
{
"question": "Which function returns the absolute value of a number?",
"options": {
"A": "ABS()",
"B": "POS()",
"C": "VALUE()",
"D": "MAGNITUDE()"
},
"answer": "A"
},
{
"question": "How do you group results by both 'year' and 'month'?",
"options": {
"A": "GROUP BY year AND month",
"B": "GROUP BY year, month",
"C": "GROUP BY (year, month)",
"D": "GROUP BY year + month"
},
"answer": "B"
},
{
"question": "Which function is used to convert a string to all uppercase letters?",
"options": {
"A": "UPPER()",
"B": "UCASE()",
"C": "Both A and B",
"D": "CAPS()"
},
"answer": "C"
},
{
"question": "What does 'HAVING COUNT() > 1' usually help identify in a table?",
"options": {
"A": "Primary keys",
"B": "Duplicate entries (based on the grouped columns)",
"C": "Null values",
"D": "The first row"
},
"answer": "B"
},
{
"question": "Which function returns the number of characters in a string?",
"options": {
"A": "LENGTH()",
"B": "CHAR_LENGTH()",
"C": "Both A and B (with subtle differences for multi-byte characters)",
"D": "SIZE()"
},
"answer": "C"
},
{
"question": "What is the 'STDEV()' function used for?",
"options": {
"A": "Standard Deviation",
"B": "String Development",
"C": "Storage Device",
"D": "Static Division"
},
"answer": "A"
},
{
"question": "How can you find the average of a column while treating NULLs as 0?",
"options": {
"A": "AVG(IFNULL(column, 0))",
"B": "AVG(column) + 0",
"C": "MEAN(column, 0)",
"D": "NULLs are automatically treated as 0 in AVG()"
},
"answer": "A"
},
{
"question": "Which keyword is used to calculate the variance of a numeric column?",
"options": {
"A": "VAR_POP() or VARIANCE()",
"B": "VARY()",
"C": "VAR_CALC()",
"D": "DIFF()"
},
"answer": "A"
},
{
"question": "Which clause is used to filter results before any grouping occurs?",
"options": {
"A": "HAVING",
"B": "WHERE",
"C": "SELECT",
"D": "LIMIT"
},
"answer": "B"
},
{
"question": "How do you find the maximum salary in each department, but only for departments in 'New York'?",
"options": {
"A": "SELECT dept, MAX(salary) FROM employees WHERE city = 'New York' GROUP BY dept;",
"B": "SELECT dept, MAX(salary) FROM employees GROUP BY dept HAVING city = 'New York';",
"C": "SELECT dept, MAX(salary) FROM employees HAVING city = 'New York' GROUP BY dept;",
"D": "SELECT dept, MAX(salary) FROM employees WHERE city = 'New York';"
},
"answer": "A"
},
{
"question": "What does the 'CEIL()' function do?",
"options": {
"A": "Returns the largest integer less than or equal to a value",
"B": "Returns the smallest integer greater than or equal to a value",
"C": "Rounds to the nearest even number",
"D": "Deletes the decimal part"
},
"answer": "B"
},
{
"question": "What does 'FLOOR()' do?",
"options": {
"A": "Returns the largest integer less than or equal to a value",
"B": "Returns the smallest integer greater than or equal to a value",
"C": "Cleans the database",
"D": "Moves a row to the bottom"
},
"answer": "A"
},
{
"question": "Which function is used to remove leading and trailing spaces from a string?",
"options": {
"A": "CLEAN()",
"B": "TRIM()",
"C": "STRIP()",
"D": "REMOVE_SPACES()"
},
"answer": "B"
},
{
"question": "Can you use an aggregate function inside a WHERE clause?",
"options": {
"A": "Yes",
"B": "No (unless it is inside a subquery)",
"C": "Only COUNT()",
"D": "Only with MySQL 8.0+"
},
"answer": "B"
},
{
"question": "What is the purpose of 'RAND()'?",
"options": {
"A": "To generate a random number between 0 and 1",
"B": "To sort data randomly (when used with ORDER BY)",
"C": "Both A and B",
"D": "To select a random table"
},
"answer": "C"
},
{
"question": "How do you find the length of the string 'MySQL'?",
"options": {
"A": "SELECT LENGTH('MySQL');",
"B": "SELECT SIZE('MySQL');",
"C": "SELECT COUNT('MySQL');",
"D": "SELECT CHARACTERS('MySQL');"
},
"answer": "A"
},
{
"question": "Which clause is most useful for generating reports that show summary statistics for different categories?",
"options": {
"A": "WHERE",
"B": "GROUP BY",
"C": "ORDER BY",
"D": "LIMIT"
},
"answer": "B"
},

{
"question": "Which type of JOIN returns records that have matching values in both tables?",
"options": {
"A": "LEFT JOIN",
"B": "RIGHT JOIN",
"C": "INNER JOIN",
"D": "FULL JOIN"
},
"answer": "C"
},
{
"question": "Which JOIN returns all records from the left table and the matched records from the right table?",
"options": {
"A": "INNER JOIN",
"B": "LEFT JOIN",
"C": "RIGHT JOIN",
"D": "OUTER JOIN"
},
"answer": "B"
},
{
"question": "If a row in the left table has no match in the right table during a LEFT JOIN, what is the value for the right table's columns?",
"options": {
"A": "0",
"B": "NULL",
"C": "Blank space",
"D": "An error is thrown"
},
"answer": "B"
},
{
"question": "Which JOIN returns all records from the right table and the matched records from the left table?",
"options": {
"A": "LEFT JOIN",
"B": "RIGHT JOIN",
"C": "INNER JOIN",
"D": "CROSS JOIN"
},
"answer": "B"
},
{
"question": "What is a 'Self Join'?",
"options": {
"A": "A join between two different databases",
"B": "A regular join where a table is joined with itself",
"C": "A join that doesn't require a condition",
"D": "A join that deletes matching records"
},
"answer": "B"
},
{
"question": "Which keyword is used to specify the condition for a JOIN?",
"options": {
"A": "WHERE",
"B": "ON",
"C": "WITH",
"D": "USING"
},
"answer": "B"
},
{
"question": "What is a 'Cross Join'?",
"options": {
"A": "A join that returns the Cartesian product of the two tables",
"B": "A join that only returns unique values",
"C": "A join between more than three tables",
"D": "A join used for error checking"
},
"answer": "A"
},
{
"question": "Which JOIN type is NOT directly supported as a single keyword in MySQL but can be emulated using UNION?",
"options": {
"A": "INNER JOIN",
"B": "FULL OUTER JOIN",
"C": "LEFT JOIN",
"D": "RIGHT JOIN"
},
"answer": "B"
},
{
"question": "What is a 'Subquery'?",
"options": {
"A": "A query that is deleted",
"B": "A query nested inside another query",
"C": "The first query in a transaction",
"D": "A query that returns only one column"
},
"answer": "B"
},
{
"question": "In which part of a SQL statement can a subquery be placed?",
"options": {
"A": "SELECT",
"B": "FROM",
"C": "WHERE",
"D": "All of the above"
},
"answer": "D"
},
{
"question": "What is an 'Index' used for in MySQL?",
"options": {
"A": "To secure the data",
"B": "To speed up the retrieval of records",
"C": "To decrease the file size",
"D": "To list the table names"
},
"answer": "B"
},
{
"question": "Which command is used to create an index on a table?",
"options": {
"A": "MAKE INDEX index_name ON table(col);",
"B": "CREATE INDEX index_name ON table(col);",
"C": "ADD INDEX index_name ON table(col);",
"D": "NEW INDEX index_name ON table(col);"
},
"answer": "B"
},
{
"question": "What is a 'Composite Index'?",
"options": {
"A": "An index on multiple columns",
"B": "An index that is automatically deleted",
"C": "An index on a view",
"D": "An index for strings only"
},
"answer": "A"
},
{
"question": "Which keyword is used to remove an index?",
"options": {
"A": "DELETE INDEX",
"B": "DROP INDEX",
"C": "REMOVE INDEX",
"D": "CLEAR INDEX"
},
"answer": "B"
},
{
"question": "What is the primary disadvantage of having too many indexes?",
"options": {
"A": "Queries become slower",
"B": "INSERT, UPDATE, and DELETE operations become slower",
"C": "The database becomes less secure",
"D": "You cannot have more than 5 indexes"
},
"answer": "B"
},
{
"question": "Which operator is used with a subquery to check if a value exists in a list of values?",
"options": {
"A": "EXISTS",
"B": "IN",
"C": "ANY",
"D": "All of the above"
},
"answer": "D"
},
{
"question": "What does the 'EXISTS' operator return?",
"options": {
"A": "A list of values",
"B": "TRUE if the subquery returns one or more records",
"C": "The first row of the subquery",
"D": "The number of rows found"
},
"answer": "B"
},
{
"question": "What is a 'Correlated Subquery'?",
"options": {
"A": "A subquery that can run independently of the outer query",
"B": "A subquery that uses values from the outer query",
"C": "A subquery that returns a table",
"D": "A subquery used only for deletions"
},
"answer": "B"
},
{
"question": "Which command is used to start a new transaction in MySQL?",
"options": {
"A": "START TRANSACTION;",
"B": "BEGIN;",
"C": "Both A and B",
"D": "OPEN TRANSACTION;"
},
"answer": "C"
},
{
"question": "Which command is used to save all changes made during a transaction?",
"options": {
"A": "SAVE;",
"B": "COMMIT;",
"C": "END TRANSACTION;",
"D": "STORE;"
},
"answer": "B"
},
{
"question": "Which command is used to undo all changes made during a transaction if an error occurs?",
"options": {
"A": "UNDO;",
"B": "ROLLBACK;",
"C": "REVERSE;",
"D": "DELETE;"
},
"answer": "B"
},
{
"question": "What does 'ACID' stand for in the context of database transactions?",
"options": {
"A": "Atomicity, Consistency, Isolation, Durability",
"B": "Access, Control, Integrity, Data",
"C": "Automatic, Concurrent, Internal, Distributed",
"D": "Account, Code, Index, Database"
},
"answer": "A"
},
{
"question": "What is a 'View' in MySQL?",
"options": {
"A": "A physical table that stores redundant data",
"B": "A virtual table based on the result-set of an SQL statement",
"C": "A snapshot of the database at a point in time",
"D": "The UI of the MySQL client"
},
"answer": "B"
},
{
"question": "Which command is used to create a view?",
"options": {
"A": "CREATE VIEW view_name AS SELECT ...",
"B": "NEW VIEW view_name FOR SELECT ...",
"C": "MAKE VIEW view_name AS SELECT ...",
"D": "ADD VIEW view_name FROM SELECT ..."
},
"answer": "A"
},
{
"question": "What is the benefit of using a View?",
"options": {
"A": "Simplifies complex queries",
"B": "Provides an extra layer of security by restricting column access",
"C": "Both A and B",
"D": "Speeds up data insertion"
},
"answer": "C"
},
{
"question": "Which command is used to delete a View?",
"options": {
"A": "DELETE VIEW view_name;",
"B": "DROP VIEW view_name;",
"C": "REMOVE VIEW view_name;",
"D": "CLEAR VIEW view_name;"
},
"answer": "B"
},
{
"question": "What is a 'Stored Procedure'?",
"options": {
"A": "A backup of the database",
"B": "A prepared SQL code that you can save and reuse",
"C": "A method to encrypt data",
"D": "A table that stores log files"
},
"answer": "B"
},
{
"question": "Which command is used to execute a stored procedure?",
"options": {
"A": "EXEC procedure_name;",
"B": "CALL procedure_name();",
"C": "RUN procedure_name;",
"D": "START procedure_name;"
},
"answer": "B"
},
{
"question": "What is a 'Trigger'?",
"options": {
"A": "A scheduled backup",
"B": "A stored program that automatically executes when a specific event occurs (INSERT, UPDATE, DELETE)",
"C": "An error message",
"D": "A way to restart the server"
},
"answer": "B"
},
{
"question": "Which event can 'trigger' a Trigger?",
"options": {
"A": "BEFORE INSERT",
"B": "AFTER UPDATE",
"C": "BEFORE DELETE",
"D": "All of the above"
},
"answer": "D"
},
{
"question": "What is a 'Unique Index'?",
"options": {
"A": "An index that allows only unique values in the column",
"B": "An index that is the only one in the database",
"C": "An index for the Primary Key only",
"D": "A temporary index"
},
"answer": "A"
},
{
"question": "Which of these is used to find the execution plan of a query to optimize performance?",
"options": {
"A": "PLAN SELECT ...",
"B": "EXPLAIN SELECT ...",
"C": "SHOW SELECT ...",
"D": "CHECK SELECT ..."
},
"answer": "B"
},
{
"question": "What does 'NULL' represent in MySQL?",
"options": {
"A": "A value of zero",
"B": "The absence of any data or a value unknown",
"C": "An empty string",
"D": "A space character"
},
"answer": "B"
},
{
"question": "Which constraint is used to ensure a child table's data remains consistent with its parent table?",
"options": {
"A": "CHECK",
"B": "FOREIGN KEY",
"C": "NOT NULL",
"D": "DEFAULT"
},
"answer": "B"
},
{
"question": "What is 'Normalization'?",
"options": {
"A": "The process of organizing data to reduce redundancy and improve integrity",
"B": "Making all strings lowercase",
"C": "Converting all data to numbers",
"D": "Deleting old records"
},
"answer": "A"
},
{
"question": "What is 'Denormalization'?",
"options": {
"A": "A database error",
"B": "Intentionally adding redundancy to improve read performance",
"C": "Removing all Primary Keys",
"D": "Converting a database to a CSV file"
},
"answer": "B"
},
{
"question": "Which command is used to create a new user in MySQL?",
"options": {
"A": "CREATE USER 'username'@'host' IDENTIFIED BY 'password';",
"B": "ADD USER 'username';",
"C": "NEW USER 'username';",
"D": "INSERT INTO users VALUES ('username');"
},
"answer": "A"
},
{
"question": "Which command is used to give a user permission to access the database?",
"options": {
"A": "ALLOW",
"B": "GRANT",
"C": "PERMIT",
"D": "GIVE"
},
"answer": "B"
},
{
"question": "Which command is used to remove permissions from a user?",
"options": {
"A": "REMOVE",
"B": "REVOKE",
"C": "TAKE",
"D": "DENY"
},
"answer": "B"
},
{
"question": "What does 'SHOW PROCESSLIST;' do?",
"options": {
"A": "Lists all tables",
"B": "Shows the currently running threads/queries on the server",
"C": "Shows the history of all commands",
"D": "Lists all users"
},
"answer": "B"
},
{
"question": "What is a 'Database Transaction'?",
"options": {
"A": "A single query",
"B": "A sequence of one or more SQL statements executed as a single unit of work",
"C": "Payment for database software",
"D": "Sending data to another server"
},
"answer": "B"
},
{
"question": "Which JOIN is the same as just 'JOIN'?",
"options": {
"A": "LEFT JOIN",
"B": "INNER JOIN",
"C": "RIGHT JOIN",
"D": "CROSS JOIN"
},
"answer": "B"
},
{
"question": "What is the purpose of 'ON DELETE CASCADE'?",
"options": {
"A": "To prevent deletion of a parent row",
"B": "To automatically delete child rows when the parent row is deleted",
"C": "To archive data when deleted",
"D": "To slow down the deletion process"
},
"answer": "B"
},
{
"question": "Which of these is a valid way to write a comment in MySQL?",
"options": {
"A": "# This is a comment",
"B": "-- This is a comment",
"C": "/* This is a comment */",
"D": "All of the above"
},
"answer": "D"
},
{
"question": "What is 'Primary Key' vs 'Unique Key'?",
"options": {
"A": "Primary Key cannot be NULL; Unique Key can have one NULL value",
"B": "A table can only have one Primary Key, but multiple Unique Keys",
"C": "Both A and B",
"D": "There is no difference"
},
"answer": "C"
},
{
"question": "What does 'SELECT VERSION();' do?",
"options": {
"A": "Shows the version of the MySQL server",
"B": "Shows the version of the database schema",
"C": "Updates MySQL to the latest version",
"D": "Lists all versioned tables"
},
"answer": "A"
},
{
"question": "Which function is used to get the ID of the last row inserted?",
"options": {
"A": "LAST_INSERT_ID()",
"B": "GET_ID()",
"C": "RECENT_ID()",
"D": "ROW_ID()"
},
"answer": "A"
},
{
"question": "What is the 'root' user in MySQL?",
"options": {
"A": "A guest user",
"B": "The administrative superuser with all privileges",
"C": "The first user created in a table",
"D": "A user with no permissions"
},
"answer": "B"
},
{
"question": "Which command is used to check the tables in a database?",
"options": {
"A": "CHECK TABLES;",
"B": "SHOW TABLES;",
"C": "DESCRIBE TABLES;",
"D": "VIEW TABLES;"
},
"answer": "B"
},
{
"question": "What is the default port for MySQL?",
"options": {
"A": "80",
"B": "3306",
"C": "443",
"D": "21"
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
    skill = "MYSQL"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
