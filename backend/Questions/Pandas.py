from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
    {
        "question": "Which of the following is the primary 2D data structure in Pandas?",
        "options": {
            "A": "Series",
            "B": "DataFrame",
            "C": "Panel",
            "D": "Table"
        },
        "answer": "B"
    },
    {
        "question": "Which Pandas object is essentially a one-dimensional labeled array?",
        "options": {
            "A": "DataFrame",
            "B": "Series",
            "C": "Matrix",
            "D": "List"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to install Pandas via pip?",
        "options": {
            "A": "pip install pandas-lib",
            "B": "pip install pandas",
            "C": "pip get pandas",
            "D": "install pd"
        },
        "answer": "B"
    },
    {
        "question": "What is the standard way to import the Pandas library?",
        "options": {
            "A": "import pandas as p",
            "B": "import pandas as pd",
            "C": "from pandas import *",
            "D": "import pd"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to read a CSV file into a DataFrame?",
        "options": {
            "A": "pd.open_csv()",
            "B": "pd.read_csv()",
            "C": "pd.get_csv()",
            "D": "pd.load_csv()"
        },
        "answer": "B"
    },
    {
        "question": "How do you view the first 5 rows of a DataFrame 'df'?",
        "options": {
            "A": "df.show(5)",
            "B": "df.head()",
            "C": "df.first(5)",
            "D": "df.top()"
        },
        "answer": "B"
    },
    {
        "question": "Which attribute returns the dimensions of a DataFrame?",
        "options": {
            "A": "df.size",
            "B": "df.shape",
            "C": "df.dim",
            "D": "df.len"
        },
        "answer": "B"
    },
    {
        "question": "How do you check the data types of all columns in a DataFrame?",
        "options": {
            "A": "df.types",
            "B": "df.dtypes",
            "C": "df.info()",
            "D": "Both B and C"
        },
        "answer": "D"
    },
    {
        "question": "Which method provides a summary of statistics for numerical columns?",
        "options": {
            "A": "df.stats()",
            "B": "df.describe()",
            "C": "df.summary()",
            "D": "df.mean()"
        },
        "answer": "B"
    },
    {
        "question": "How do you select a single column named 'Age' from DataFrame 'df'?",
        "options": {
            "A": "df.get('Age')",
            "B": "df['Age']",
            "C": "df.Age",
            "D": "Both B and C"
        },
        "answer": "D"
    },
    {
        "question": "Which function is used to read data from an Excel file?",
        "options": {
            "A": "pd.read_excel()",
            "B": "pd.get_excel()",
            "C": "pd.read_xlsx()",
            "D": "pd.open_excel()"
        },
        "answer": "A"
    },
    {
        "question": "What does 'df.tail()' do?",
        "options": {
            "A": "Removes the last row",
            "B": "Shows the last 5 rows of the DataFrame",
            "C": "Returns the last column",
            "D": "Sorts the data from bottom to top"
        },
        "answer": "B"
    },
    {
        "question": "Which parameter in 'read_csv' is used to specify a custom delimiter (like a semicolon)?",
        "options": {
            "A": "delimiter",
            "B": "sep",
            "C": "Both A and B",
            "D": "split"
        },
        "answer": "C"
    },
    {
        "question": "How do you rename the index of a Series?",
        "options": {
            "A": "series.index = new_index",
            "B": "series.rename(index=...)",
            "C": "Both A and B",
            "D": "series.reindex()"
        },
        "answer": "C"
    },
    {
        "question": "Which method is used to convert a DataFrame into a CSV file?",
        "options": {
            "A": "df.save_csv()",
            "B": "df.to_csv()",
            "C": "df.write_csv()",
            "D": "df.as_csv()"
        },
        "answer": "B"
    },
    {
        "question": "What is the default index type in Pandas if none is provided?",
        "options": {
            "A": "A RangeIndex starting from 0",
            "B": "A list of strings",
            "C": "The first column of the data",
            "D": "Random integers"
        },
        "answer": "A"
    },
    {
        "question": "Which attribute returns the total number of elements (rows * columns) in a DataFrame?",
        "options": {
            "A": "df.count",
            "B": "df.size",
            "C": "df.length",
            "D": "df.volume"
        },
        "answer": "B"
    },
    {
        "question": "How do you select the first 3 rows and 2 columns using integer-based indexing?",
        "options": {
            "A": "df.loc[0:3, 0:2]",
            "B": "df.iloc[0:3, 0:2]",
            "C": "df.ix[0:3, 0:2]",
            "D": "df.slice(3, 2)"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to access data using labels (row/column names)?",
        "options": {
            "A": "df.iloc",
            "B": "df.loc",
            "C": "df.at",
            "D": "Both B and C"
        },
        "answer": "D"
    },
    {
        "question": "How do you create a DataFrame from a Dictionary where keys are column names?",
        "options": {
            "A": "pd.DataFrame(dict)",
            "B": "pd.from_dict(dict)",
            "C": "Both A and B",
            "D": "pd.DataFrame.dict(dict)"
        },
        "answer": "C"
    },
    {
        "question": "Which method returns the unique values of a Series?",
        "options": {
            "A": "series.distinct()",
            "B": "series.unique()",
            "C": "series.set()",
            "D": "series.single()"
        },
        "answer": "B"
    },
    {
        "question": "Which method returns the frequency count of each unique value in a Series?",
        "options": {
            "A": "series.count_values()",
            "B": "series.value_counts()",
            "C": "series.freq()",
            "D": "series.describe()"
        },
        "answer": "B"
    },
    {
        "question": "How do you drop a column named 'Salary' from a DataFrame 'df'?",
        "options": {
            "A": "df.drop('Salary')",
            "B": "df.drop('Salary', axis=1)",
            "C": "df.remove('Salary')",
            "D": "del df.Salary"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'inplace=True' parameter usually do in Pandas methods?",
        "options": {
            "A": "Creates a copy of the object",
            "B": "Modifies the existing object directly without returning a new one",
            "C": "Saves the object to disk",
            "D": "Speeds up the calculation"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to read data from a SQL database?",
        "options": {
            "A": "pd.read_sql()",
            "B": "pd.from_sql()",
            "C": "pd.query_sql()",
            "D": "pd.sql_table()"
        },
        "answer": "A"
    },
    {
        "question": "How do you set a specific column 'ID' as the index of the DataFrame?",
        "options": {
            "A": "df.index = 'ID'",
            "B": "df.set_index('ID')",
            "C": "df.make_index('ID')",
            "D": "df.reindex('ID')"
        },
        "answer": "B"
    },
    {
        "question": "Which attribute returns a list of column names in a DataFrame?",
        "options": {
            "A": "df.keys",
            "B": "df.columns",
            "C": "df.header",
            "D": "Both A and B"
        },
        "answer": "D"
    },
    {
        "question": "What is the difference between 'loc' and 'iloc'?",
        "options": {
            "A": "loc is for integers, iloc is for labels",
            "B": "loc is label-based, iloc is integer-position based",
            "C": "loc is faster than iloc",
            "D": "iloc only works on Series"
        },
        "answer": "B"
    },
    {
        "question": "How do you select all rows where 'Score' is greater than 80?",
        "options": {
            "A": "df.where(df['Score'] > 80)",
            "B": "df[df['Score'] > 80]",
            "C": "df.query('Score > 80')",
            "D": "Both B and C"
        },
        "answer": "D"
    },
    {
        "question": "Which function is used to read a JSON file?",
        "options": {
            "A": "pd.read_json()",
            "B": "pd.load_json()",
            "C": "pd.get_json()",
            "D": "pd.json_decode()"
        },
        "answer": "A"
    },
    {
        "question": "What does the 'T' attribute of a DataFrame return?",
        "options": {
            "A": "A Trend analysis",
            "B": "The Transpose (flipped rows and columns)",
            "C": "The Total sum",
            "D": "The Type of the data"
        },
        "answer": "B"
    },
    {
        "question": "How do you check for missing values in a DataFrame?",
        "options": {
            "A": "df.missing()",
            "B": "df.isnull()",
            "C": "df.isna()",
            "D": "Both B and C"
        },
        "answer": "D"
    },
    {
        "question": "Which method is used to save a DataFrame to a JSON file?",
        "options": {
            "A": "df.save_json()",
            "B": "df.to_json()",
            "C": "df.write_json()",
            "D": "df.dump_json()"
        },
        "answer": "B"
    },
    {
        "question": "What does 'df.info()' provide?",
        "options": {
            "A": "The first 10 rows",
            "B": "A summary of the DataFrame including non-null counts and memory usage",
            "C": "A list of the highest values in each column",
            "D": "A statistical description"
        },
        "answer": "B"
    },
    {
        "question": "Which parameter in 'read_csv' allows you to skip the first N rows?",
        "options": {
            "A": "skip",
            "B": "skiprows",
            "C": "header",
            "D": "startrow"
        },
        "answer": "B"
    },
    {
        "question": "Which attribute returns the index labels of a DataFrame?",
        "options": {
            "A": "df.rows",
            "B": "df.index",
            "C": "df.labels",
            "D": "df.axes[0]"
        },
        "answer": "B"
    },
    {
        "question": "How do you select rows 5 through 10 (exclusive of 10) in a Series 's'?",
        "options": {
            "A": "s[5:10]",
            "B": "s.iloc[5:10]",
            "C": "Both A and B",
            "D": "s.loc[5:10]"
        },
        "answer": "C"
    },
    {
        "question": "Which function allows you to read a table from a webpage into a list of DataFrames?",
        "options": {
            "A": "pd.read_web()",
            "B": "pd.read_html()",
            "C": "pd.get_table()",
            "D": "pd.scrape()"
        },
        "answer": "B"
    },
    {
        "question": "How do you access a single scalar value at row 'label1' and column 'col1'?",
        "options": {
            "A": "df.at['label1', 'col1']",
            "B": "df.iat[0, 0]",
            "C": "Both A and B (depending on index/position)",
            "D": "df.value('label1', 'col1')"
        },
        "answer": "C"
    },
    {
        "question": "What is the primary library Pandas is built upon for numerical arrays?",
        "options": {
            "A": "Matplotlib",
            "B": "NumPy",
            "C": "SciPy",
            "D": "Scikit-learn"
        },
        "answer": "B"
    },
    {
        "question": "Which parameter in 'to_csv' prevents Pandas from writing the index labels to the file?",
        "options": {
            "A": "no_index=True",
            "B": "index=False",
            "C": "header=False",
            "D": "exclude_index=True"
        },
        "answer": "B"
    },
    {
        "question": "How do you view the data types of columns in 'df' along with the memory usage?",
        "options": {
            "A": "df.dtypes",
            "B": "df.info()",
            "C": "df.memory_usage()",
            "D": "df.summary()"
        },
        "answer": "B"
    },
    {
        "question": "Which method returns the column names as an Index object?",
        "options": {
            "A": "df.columns",
            "B": "df.header",
            "C": "df.axes[1]",
            "D": "Both A and C"
        },
        "answer": "D"
    },
    {
        "question": "How do you load only specific columns from a CSV file?",
        "options": {
            "A": "Use the 'usecols' parameter in read_csv",
            "B": "Use the 'columns' parameter",
            "C": "You must load the whole file first",
            "D": "Use 'select_cols'"
        },
        "answer": "A"
    },
    {
        "question": "What does 'pd.Series([1, 2, 3], index=['a', 'b', 'c'])' create?",
        "options": {
            "A": "A DataFrame",
            "B": "A Series with custom labels 'a', 'b', 'c'",
            "C": "An error",
            "D": "A list"
        },
        "answer": "B"
    },
    {
        "question": "Which method provides the memory usage of each column in bytes?",
        "options": {
            "A": "df.size()",
            "B": "df.memory_usage()",
            "C": "df.nbytes",
            "D": "df.info()"
        },
        "answer": "B"
    },
    {
        "question": "How do you select the last 2 columns of 'df'?",
        "options": {
            "A": "df.iloc[:, -2:]",
            "B": "df.loc[:, -2:]",
            "C": "df.tail_cols(2)",
            "D": "df[-2:]"
        },
        "answer": "A"
    },
    {
        "question": "What happens if you multiply a DataFrame by 2?",
        "options": {
            "A": "It doubles the number of rows",
            "B": "It doubles the number of columns",
            "C": "It performs an element-wise multiplication on numeric values",
            "D": "It creates a copy of the DataFrame"
        },
        "answer": "C"
    },
    {
        "question": "Which function is used to create a DataFrame from a list of lists?",
        "options": {
            "A": "pd.DataFrame(list_of_lists)",
            "B": "pd.from_records(list_of_lists)",
            "C": "Both A and B",
            "D": "pd.Series(list_of_lists)"
        },
        "answer": "C"
    },
    {
        "question": "Which method returns the number of non-null values for each column?",
        "options": {
            "A": "df.count()",
            "B": "df.size()",
            "C": "df.info()",
            "D": "Both A and C"
        },
        "answer": "D"
    },
    {
        "question": "Which method is used to remove rows or columns with missing values?",
        "options": {
            "A": "df.remove_null()",
            "B": "df.dropna()",
            "C": "df.clean()",
            "D": "df.delete_na()"
        },
        "answer": "B"
    },
    {
        "question": "How do you fill missing values (NaN) with a specific value, like 0?",
        "options": {
            "A": "df.replace_nan(0)",
            "B": "df.fillna(0)",
            "C": "df.na_fill(0)",
            "D": "df.set_null(0)"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to sort a DataFrame by the values of one or more columns?",
        "options": {
            "A": "df.sort_index()",
            "B": "df.sort_values()",
            "C": "df.order_by()",
            "D": "df.rank()"
        },
        "answer": "B"
    },
    {
        "question": "How do you sort a DataFrame in descending order?",
        "options": {
            "A": "df.sort_values(ascending=False)",
            "B": "df.sort_values(order='desc')",
            "C": "df.sort_values(reverse=True)",
            "D": "df.sort_values(direction='down')"
        },
        "answer": "A"
    },
    {
        "question": "Which method is used to remove duplicate rows from a DataFrame?",
        "options": {
            "A": "df.unique()",
            "B": "df.drop_duplicates()",
            "C": "df.remove_repeats()",
            "D": "df.distinct()"
        },
        "answer": "B"
    },
    {
        "question": "How do you check for duplicate rows in a DataFrame?",
        "options": {
            "A": "df.is_duplicate()",
            "B": "df.duplicated()",
            "C": "df.find_repeats()",
            "D": "df.has_duplicates()"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to replace specific values in a DataFrame with new values?",
        "options": {
            "A": "df.change()",
            "B": "df.replace()",
            "C": "df.modify()",
            "D": "df.update_values()"
        },
        "answer": "B"
    },
    {
        "question": "How do you drop rows where a specific column 'Email' has missing values?",
        "options": {
            "A": "df.dropna(axis=1)",
            "B": "df.dropna(subset=['Email'])",
            "C": "df.dropna(how='any')",
            "D": "df['Email'].remove()"
        },
        "answer": "B"
    },
    {
        "question": "Which method sorts the DataFrame based on its index labels?",
        "options": {
            "A": "df.sort_values()",
            "B": "df.sort_index()",
            "C": "df.reorder()",
            "D": "df.arrange()"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'axis' parameter in 'df.drop()'? ",
        "options": {
            "A": "axis=0 for rows, axis=1 for columns",
            "B": "axis=1 for rows, axis=0 for columns",
            "C": "It defines the sorting direction",
            "D": "It identifies missing values"
        },
        "answer": "A"
    },
    {
        "question": "Which method is used to rename column names in a DataFrame?",
        "options": {
            "A": "df.rename(columns={'old': 'new'})",
            "B": "df.set_columns(['new'])",
            "C": "df.columns.rename()",
            "D": "df.change_header()"
        },
        "answer": "A"
    },
    {
        "question": "How do you convert a column 'Price' to a numeric data type?",
        "options": {
            "A": "pd.to_number(df['Price'])",
            "B": "pd.to_numeric(df['Price'])",
            "C": "df['Price'].astype(float)",
            "D": "Both B and C"
        },
        "answer": "D"
    },
    {
        "question": "Which method allows you to change the data type of a specific column?",
        "options": {
            "A": "df.convert()",
            "B": "df.astype()",
            "C": "df.cast()",
            "D": "df.type()"
        },
        "answer": "B"
    },
    {
        "question": "What does 'df.notnull()' do?",
        "options": {
            "A": "Returns a boolean mask where True indicates data is NOT missing",
            "B": "Returns only the rows with data",
            "C": "Removes all null values",
            "D": "Fills null values with a space"
        },
        "answer": "A"
    },
    {
        "question": "Which method returns the n largest values from a specific column?",
        "options": {
            "A": "df.max_values(n)",
            "B": "df.nlargest(n, 'column')",
            "C": "df.top(n)",
            "D": "df.sort_values().head(n)"
        },
        "answer": "B"
    },
    {
        "question": "How do you filter rows where the column 'City' is in a list ['NY', 'LA']?",
        "options": {
            "A": "df[df['City'] == ['NY', 'LA']]",
            "B": "df[df['City'].isin(['NY', 'LA'])]",
            "C": "df[df['City'].contains(['NY', 'LA'])]",
            "D": "df.query('City == NY or LA')"
        },
        "answer": "B"
    },
    {
        "question": "What is the result of 'any()' when applied to 'df.isnull()'?",
        "options": {
            "A": "It returns a Series showing if any column contains a null value",
            "B": "It returns a single True/False if the whole DataFrame has any null",
            "C": "Both A and B (depending on axis)",
            "D": "It returns the count of nulls"
        },
        "answer": "C"
    },
    {
        "question": "Which method is used to interpolate missing values based on different methods (linear, time)?",
        "options": {
            "A": "df.fill_linear()",
            "B": "df.interpolate()",
            "C": "df.guess_na()",
            "D": "df.smooth()"
        },
        "answer": "B"
    },
    {
        "question": "How do you drop a row by its index label 'row1'?",
        "options": {
            "A": "df.drop('row1')",
            "B": "df.remove('row1')",
            "C": "df.drop('row1', axis=1)",
            "D": "del df['row1']"
        },
        "answer": "A"
    },
    {
        "question": "Which parameter in 'drop_duplicates' allows you to keep the last occurrence instead of the first?",
        "options": {
            "A": "keep='last'",
            "B": "preference='last'",
            "C": "order='desc'",
            "D": "stay='last'"
        },
        "answer": "A"
    },
    {
        "question": "How do you convert all column names to lowercase?",
        "options": {
            "A": "df.columns.lower()",
            "B": "df.columns = [x.lower() for x in df.columns]",
            "C": "df.rename(lower=True)",
            "D": "df.lower_headers()"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to change the frequency of a time-series index?",
        "options": {
            "A": "df.reshape()",
            "B": "df.asfreq()",
            "C": "df.reindex()",
            "D": "df.time_step()"
        },
        "answer": "B"
    },
    {
        "question": "How do you get the number of unique elements in a Series?",
        "options": {
            "A": "series.count_unique()",
            "B": "series.nunique()",
            "C": "series.unique().length()",
            "D": "len(series.distinct())"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to convert a Series of strings to a date-time object?",
        "options": {
            "A": "pd.to_date()",
            "B": "pd.to_datetime()",
            "C": "pd.as_datetime()",
            "D": "series.parse_date()"
        },
        "answer": "B"
    },
    {
        "question": "What does 'df.dropna(how='all')' do?",
        "options": {
            "A": "Drops all rows in the DataFrame",
            "B": "Drops rows where all values are missing",
            "C": "Drops rows where at least one value is missing",
            "D": "Drops rows with no unique values"
        },
        "answer": "B"
    },
    {
        "question": "How do you filter a DataFrame to show only rows where 'Category' is NOT 'Furniture'?",
        "options": {
            "A": "df[df['Category'] != 'Furniture']",
            "B": "df[~df['Category'] == 'Furniture']",
            "C": "Both A and B",
            "D": "df.query('Category != Furniture')"
        },
        "answer": "C"
    },
    {
        "question": "Which method allows you to apply a custom function to every element in a DataFrame?",
        "options": {
            "A": "df.apply()",
            "B": "df.applymap()",
            "C": "df.map()",
            "D": "df.transform()"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'tilde' symbol (~) used for in boolean indexing?",
        "options": {
            "A": "Approximate match",
            "B": "Logical NOT (negation)",
            "C": "Combining conditions",
            "D": "Sorting data"
        },
        "answer": "B"
    },
    {
        "question": "How do you find the total number of missing values for each column?",
        "options": {
            "A": "df.isnull().sum()",
            "B": "df.na_count()",
            "C": "df.info()",
            "D": "df.describe()"
        },
        "answer": "A"
    },
    {
        "question": "Which method allows you to replace values based on a dictionary mapping?",
        "options": {
            "A": "series.map(dict)",
            "B": "series.replace(dict)",
            "C": "Both A and B",
            "D": "series.update(dict)"
        },
        "answer": "C"
    },
    {
        "question": "Which method returns the n smallest values from a specific column?",
        "options": {
            "A": "df.nsmallest(n, 'column')",
            "B": "df.bottom(n)",
            "C": "df.sort_values().tail(n)",
            "D": "df.min_values(n)"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of 'df.clip(lower, upper)'?",
        "options": {
            "A": "To remove rows outside the range",
            "B": "To trim values below the lower limit and above the upper limit",
            "C": "To crop the DataFrame size",
            "D": "To sort data within a range"
        },
        "answer": "B"
    },
    {
        "question": "How do you select only columns with 'float' data types?",
        "options": {
            "A": "df.select_dtypes(include=['float'])",
            "B": "df.filter(type='float')",
            "C": "df.get_floats()",
            "D": "df.loc['float']"
        },
        "answer": "A"
    },
    {
        "question": "Which method is used to swap the level of a MultiIndex?",
        "options": {
            "A": "df.swaplevel()",
            "B": "df.reorder_levels()",
            "C": "Both A and B",
            "D": "df.rotate()"
        },
        "answer": "C"
    },
    {
        "question": "How do you check if any value in a Series is null?",
        "options": {
            "A": "series.has_na()",
            "B": "series.isnull().any()",
            "C": "series.any_null()",
            "D": "series.is_empty()"
        },
        "answer": "B"
    },
    {
        "question": "What does 'df.reset_index()' do by default?",
        "options": {
            "A": "Deletes the current index",
            "B": "Converts the current index into a column and sets a new RangeIndex",
            "C": "Sorts the index alphabetically",
            "D": "Removes all data from the DataFrame"
        },
        "answer": "B"
    },
    {
        "question": "Which parameter in 'reset_index' prevents the old index from becoming a column?",
        "options": {
            "A": "drop=True",
            "B": "inplace=True",
            "C": "remove=True",
            "D": "clear=True"
        },
        "answer": "A"
    },
    {
        "question": "How do you find the mode (most frequent value) of a Series?",
        "options": {
            "A": "series.mean()",
            "B": "series.mode()",
            "C": "series.value_counts().head(1)",
            "D": "Both B and C"
        },
        "answer": "D"
    },
    {
        "question": "Which method is used to shift the index of a Series or DataFrame by a number of periods?",
        "options": {
            "A": "df.move()",
            "B": "df.shift()",
            "C": "df.lag()",
            "D": "df.offset()"
        },
        "answer": "B"
    },
    {
        "question": "What is the default behavior of 'df.sort_values()' regarding null values?",
        "options": {
            "A": "They are placed at the beginning",
            "B": "They are placed at the end",
            "C": "They are removed",
            "D": "They cause an error"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to detect 'outliers' using the Z-score in a numeric Series?",
        "options": {
            "A": "series.outliers()",
            "B": "There is no built-in function; use scipy.stats.zscore or manual calculation",
            "C": "series.zscore()",
            "D": "pd.detect_outliers()"
        },
        "answer": "B"
    },
    {
        "question": "How do you round all values in a DataFrame to 2 decimal places?",
        "options": {
            "A": "df.fix(2)",
            "B": "df.round(2)",
            "C": "df.format('.2f')",
            "D": "np.round(df, 2)"
        },
        "answer": "B"
    },
    {
        "question": "Which method calculates the rank of each data point in a Series?",
        "options": {
            "A": "series.order()",
            "B": "series.rank()",
            "C": "series.sort()",
            "D": "series.position()"
        },
        "answer": "B"
    },
    {
        "question": "How do you drop columns that have at least one missing value?",
        "options": {
            "A": "df.dropna(axis=1)",
            "B": "df.dropna(axis=0)",
            "C": "df.drop(columns='missing')",
            "D": "df.clean(axis='columns')"
        },
        "answer": "A"
    },
    {
        "question": "What does 'series.str.strip()' do?",
        "options": {
            "A": "Removes whitespace from the beginning and end of strings in a Series",
            "B": "Deletes the strings",
            "C": "Converts strings to uppercase",
            "D": "Splits strings into a list"
        },
        "answer": "A"
    },
    {
        "question": "Which method returns a random sample of rows from a DataFrame?",
        "options": {
            "A": "df.random()",
            "B": "df.sample()",
            "C": "df.pick()",
            "D": "df.shuffle().head()"
        },
        "answer": "B"
    },
    {
        "question": "How do you fill missing values using the value from the previous row?",
        "options": {
            "A": "df.fillna(method='ffill')",
            "B": "df.fillna(method='bfill')",
            "C": "df.fillna(method='pad')",
            "D": "Both A and C"
        },
        "answer": "D"
    },
    {
        "question": "How do you fill missing values using the value from the next row?",
        "options": {
            "A": "df.fillna(method='ffill')",
            "B": "df.fillna(method='bfill')",
            "C": "df.fillna(method='back')",
            "D": "Both B and C"
        },
        "answer": "D"
    },
    {
        "question": "Which method is used to compute the sample variance of values in a Series?",
        "options": {
            "A": "series.var()",
            "B": "series.std()",
            "C": "series.mean_sq()",
            "D": "series.diff_sq()"
        },
        "answer": "A"
    },
    {
        "question": "How do you convert a column 'Joined_Date' to just show the year?",
        "options": {
            "A": "df['Joined_Date'].dt.year",
            "B": "df['Joined_Date'].year()",
            "C": "pd.Year(df['Joined_Date'])",
            "D": "df['Joined_Date'].to_year()"
        },
        "answer": "A"
    },
    {
        "question": "Which method is used to group data based on one or more columns?",
        "options": {
            "A": "df.aggregate()",
            "B": "df.groupby()",
            "C": "df.cluster()",
            "D": "df.pivot()"
        },
        "answer": "B"
    },
    {
        "question": "How do you calculate the sum of 'Sales' for each 'Region'?",
        "options": {
            "A": "df.groupby('Region')['Sales'].sum()",
            "B": "df['Sales'].groupby('Region').total()",
            "C": "df.sum('Sales').by('Region')",
            "D": "pd.pivot_table(df, values='Sales', index='Region', aggfunc='sum')"
        },
        "answer": "A"
    },
    {
        "question": "Which method is used to apply multiple aggregate functions to grouped data at once?",
        "options": {
            "A": "df.groupby().apply()",
            "B": "df.groupby().agg()",
            "C": "df.groupby().transform()",
            "D": "df.groupby().summarize()"
        },
        "answer": "B"
    },
    {
        "question": "What is the difference between 'merge()' and 'concat()'?",
        "options": {
            "A": "merge() combines data on specific keys (SQL-like); concat() simply stacks data on an axis",
            "B": "concat() is for DataFrames; merge() is for Series",
            "C": "merge() is faster than concat()",
            "D": "There is no difference"
        },
        "answer": "A"
    },
    {
        "question": "Which type of join returns only the rows with matching keys in both DataFrames?",
        "options": {
            "A": "Left join",
            "B": "Outer join",
            "C": "Inner join",
            "D": "Right join"
        },
        "answer": "C"
    },
    {
        "question": "How do you perform a Left Join between DataFrames 'df1' and 'df2' on column 'key'?",
        "options": {
            "A": "pd.merge(df1, df2, on='key', how='left')",
            "B": "df1.join(df2, on='key')",
            "C": "pd.concat([df1, df2], axis=1)",
            "D": "df1.merge(df2, how='left')"
        },
        "answer": "A"
    },
    {
        "question": "Which method is used to combine two DataFrames based on their index labels?",
        "options": {
            "A": "df1.merge(df2)",
            "B": "df1.join(df2)",
            "C": "df1.stack(df2)",
            "D": "df1.append(df2)"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'transform()' method do after a 'groupby()'?",
        "options": {
            "A": "It reduces the data to a single value per group",
            "B": "It returns an object that is the same size as the original, broadcasted with group stats",
            "C": "It sorts the groups",
            "D": "It deletes the groups"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to create a spreadsheet-style pivot table?",
        "options": {
            "A": "df.pivot()",
            "B": "pd.pivot_table()",
            "C": "df.crosstab()",
            "D": "Both A and B"
        },
        "answer": "D"
    },
    {
        "question": "What is the default aggregation function for 'pd.pivot_table()'?",
        "options": {
            "A": "sum",
            "B": "mean",
            "C": "count",
            "D": "median"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to compute a simple cross-tabulation of two or more factors (frequency table)?",
        "options": {
            "A": "pd.pivot()",
            "B": "pd.crosstab()",
            "C": "df.value_counts()",
            "D": "df.groupby().size()"
        },
        "answer": "B"
    },
    {
        "question": "How do you stack a DataFrame (moving column labels to a new inner index level)?",
        "options": {
            "A": "df.unstack()",
            "B": "df.stack()",
            "C": "df.melt()",
            "D": "df.pivot()"
        },
        "answer": "B"
    },
    {
        "question": "Which method 'unpivots' a DataFrame from wide format to long format?",
        "options": {
            "A": "df.unstack()",
            "B": "df.melt()",
            "C": "df.pivot()",
            "D": "df.explode()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Method Chaining' in Pandas?",
        "options": {
            "A": "Using multiple 'for' loops",
            "B": "Calling multiple methods sequentially in a single line (e.g., df.groupby().sum().sort_values())",
            "C": "Linking different databases",
            "D": "A way to encrypt code"
        },
        "answer": "B"
    },
    {
        "question": "How do you get the first entry of each group in a 'groupby' object?",
        "options": {
            "A": "groups.head(1)",
            "B": "groups.first()",
            "C": "groups.nth(0)",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "Which parameter in 'concat()' allows you to create a MultiIndex to track the source of the data?",
        "options": {
            "A": "names",
            "B": "keys",
            "C": "labels",
            "D": "levels"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to calculate a 'rolling' window statistic (like 7-day moving average)?",
        "options": {
            "A": "df.moving()",
            "B": "df.rolling()",
            "C": "df.window()",
            "D": "df.shift()"
        },
        "answer": "B"
    },
    {
        "question": "What does 'df.groupby('A').filter(lambda x: x['B'].mean() > 0)' do?",
        "options": {
            "A": "Filters rows where B > 0",
            "B": "Keeps entire groups only if their mean of B is greater than 0",
            "C": "Changes group B values to 0",
            "D": "Returns the mean of each group"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to join multiple DataFrames at once if they share an index?",
        "options": {
            "A": "pd.merge()",
            "B": "df.join()",
            "C": "pd.concat()",
            "D": "Both B and C"
        },
        "answer": "D"
    },
    {
        "question": "How do you combine two Series 's1' and 's2' into a DataFrame where they are columns?",
        "options": {
            "A": "pd.concat([s1, s2], axis=1)",
            "B": "pd.DataFrame({'col1': s1, 'col2': s2})",
            "C": "Both A and B",
            "D": "s1.merge(s2)"
        },
        "answer": "C"
    },
    {
        "question": "What is a 'MultiIndex'?",
        "options": {
            "A": "An index with multiple names",
            "B": "A hierarchical index (multiple levels of indexing on one axis)",
            "C": "An index stored in multiple files",
            "D": "An index used for multiple DataFrames"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to convert a MultiIndex DataFrame back to a simple DataFrame?",
        "options": {
            "A": "df.flatten()",
            "B": "df.reset_index()",
            "C": "df.unstack()",
            "D": "Both B and C"
        },
        "answer": "D"
    },
    {
        "question": "How do you get the unique values of group names in a groupby object?",
        "options": {
            "A": "groups.names",
            "B": "groups.groups.keys()",
            "C": "groups.unique()",
            "D": "groups.indices"
        },
        "answer": "B"
    },
    {
        "question": "What does 'pd.get_dummies()' do?",
        "options": {
            "A": "Creates fake data for testing",
            "B": "Converts categorical variables into 'dummy' or 'indicator' variables (one-hot encoding)",
            "C": "Removes empty columns",
            "D": "Simplifies the DataFrame"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to combine two DataFrames where one has 'patches' of new data for the other?",
        "options": {
            "A": "df.merge()",
            "B": "df.update()",
            "C": "df.combine_first()",
            "D": "Both B and C"
        },
        "answer": "D"
    },
    {
        "question": "What is the purpose of 'df.groupby().size()'?",
        "options": {
            "A": "Returns the number of groups",
            "B": "Returns the number of rows in each group",
            "C": "Returns the memory size of each group",
            "D": "Returns the shape of each group"
        },
        "answer": "B"
    },
    {
        "question": "How do you calculate the cumulative sum within each group?",
        "options": {
            "A": "df.groupby('A').cumsum()",
            "B": "df.groupby('A').sum().cumsum()",
            "C": "df.cumsum().by('A')",
            "D": "pd.cumsum(df, group='A')"
        },
        "answer": "A"
    },
    {
        "question": "Which JOIN type returns all records from both tables, filling in NaNs where there is no match?",
        "options": {
            "A": "Inner Join",
            "B": "Outer Join (Full Join)",
            "C": "Cross Join",
            "D": "Union"
        },
        "answer": "B"
    },
    {
        "question": "In 'merge()', what if the column names you want to join on are different in 'left' and 'right' DataFrames?",
        "options": {
            "A": "You must rename them first",
            "B": "Use 'left_on' and 'right_on' parameters",
            "C": "Use the 'different_names=True' parameter",
            "D": "You can only join on index"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to calculate the percentage change between current and prior elements?",
        "options": {
            "A": "df.diff()",
            "B": "df.pct_change()",
            "C": "df.ratio()",
            "D": "df.shift()"
        },
        "answer": "B"
    },
    {
        "question": "What does 'df.groupby().ngroups' return?",
        "options": {
            "A": "The number of rows in each group",
            "B": "The total number of groups created",
            "C": "The names of the groups",
            "D": "The size of the groups"
        },
        "answer": "B"
    },
    {
        "question": "How do you apply a function to each group and return a DataFrame in the original shape?",
        "options": {
            "A": "groups.apply()",
            "B": "groups.transform()",
            "C": "groups.map()",
            "D": "groups.broadcast()"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to 'cut' continuous data into discrete 'bins' (e.g., ages into age-groups)?",
        "options": {
            "A": "pd.bin()",
            "B": "pd.cut()",
            "C": "pd.segment()",
            "D": "df.split_values()"
        },
        "answer": "B"
    },
    {
        "question": "What is the difference between 'pd.cut()' and 'pd.qcut()'?",
        "options": {
            "A": "cut uses equal-width bins; qcut uses equal-frequency bins (quantiles)",
            "B": "qcut is only for integers",
            "C": "cut is faster",
            "D": "There is no difference"
        },
        "answer": "A"
    },
    {
        "question": "Which method allows you to iterate over the name and data of each group in a groupby object?",
        "options": {
            "A": "for name, data in groups:",
            "B": "groups.iterate()",
            "C": "groups.items()",
            "D": "groups.to_dict()"
        },
        "answer": "A"
    },
    {
        "question": "Which parameter in 'pd.merge' handles duplicate column names by adding a suffix?",
        "options": {
            "A": "suffixes",
            "B": "labels",
            "C": "rename_duplicates",
            "D": "extra_names"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Expanding' window in Pandas?",
        "options": {
            "A": "A window that stays the same size",
            "B": "A window that grows as it includes all prior data points from the start",
            "C": "A window used for 3D data",
            "D": "A way to increase memory"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to transform a column of lists into multiple rows (one row per list element)?",
        "options": {
            "A": "df.split()",
            "B": "df.explode()",
            "C": "df.expand()",
            "D": "df.melt()"
        },
        "answer": "B"
    },
    {
        "question": "How do you select the third level of a MultiIndex 'df' along axis 0?",
        "options": {
            "A": "df.loc[level=2]",
            "B": "df.xs(key, level=2)",
            "C": "df.get_level(2)",
            "D": "df.index.get_level_values(2)"
        },
        "answer": "B"
    },
    {
        "question": "What does 'df.groupby().groups' return?",
        "options": {
            "A": "The actual data in groups",
            "B": "A dictionary mapping group names to the list of row indices",
            "C": "The number of groups",
            "D": "A list of group names"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to find the 'Rank' of values within each group?",
        "options": {
            "A": "df.groupby().rank()",
            "B": "df.groupby().sort()",
            "C": "df.groupby().position()",
            "D": "df.rank(group=True)"
        },
        "answer": "A"
    },
    {
        "question": "How do you perform a cross join (Cartesian product) in 'pd.merge'? ",
        "options": {
            "A": "how='cross' (in newer versions)",
            "B": "Assign a dummy key to both and join on it",
            "C": "Both A and B",
            "D": "pd.concat(axis=1)"
        },
        "answer": "C"
    },
    {
        "question": "Which method returns the correlation between two Series?",
        "options": {
            "A": "s1.corr(s2)",
            "B": "pd.correlation(s1, s2)",
            "C": "s1.compare(s2)",
            "D": "s1.match(s2)"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Downsampling' in time series?",
        "options": {
            "A": "Increasing frequency (e.g., months to days)",
            "B": "Decreasing frequency (e.g., days to months) while aggregating data",
            "C": "Removing data points",
            "D": "Sorting data downwards"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used for both upsampling and downsampling time series data?",
        "options": {
            "A": "df.shift()",
            "B": "df.resample()",
            "C": "df.retime()",
            "D": "df.asfreq()"
        },
        "answer": "B"
    },
    {
        "question": "What does 'df.pipe(func)' do?",
        "options": {
            "A": "Creates a data pipeline for unix",
            "B": "Allows for custom function application that can take the whole DataFrame as the first argument",
            "C": "Saves data to a pipe file",
            "D": "Connects to a server"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to concatenate arrays along the first axis (rows) by default?",
        "options": {
            "A": "pd.merge()",
            "B": "pd.concat()",
            "C": "df.append()",
            "D": "Both B and C"
        },
        "answer": "D"
    },
    {
        "question": "What is a 'Squeeze' operation in Pandas?",
        "options": {
            "A": "Compressing the file size",
            "B": "Converting a 1-item DataFrame to a Series or Scalar",
            "C": "Reducing memory usage",
            "D": "Deleting empty columns"
        },
        "answer": "B"
    },
    {
        "question": "How do you calculate the difference between the current and a previous row?",
        "options": {
            "A": "df.diff()",
            "B": "df.shift()",
            "C": "df.delta()",
            "D": "df.minus_prev()"
        },
        "answer": "A"
    },
    {
        "question": "Which method is used to 'flatten' a MultiIndex in columns into a single index?",
        "options": {
            "A": "df.columns.to_flat_index()",
            "B": "df.reset_index()",
            "C": "df.columns = df.columns.get_level_values(0)",
            "D": "Both A and C"
        },
        "answer": "D"
    },
    {
        "question": "Which Pandas object is used to represent a specific point in time?",
        "options": {
            "A": "Period",
            "B": "Timestamp",
            "C": "Timedelta",
            "D": "DateTime"
        },
        "answer": "B"
    },
    {
        "question": "Which function converts a string or list of strings to datetime objects?",
        "options": {
            "A": "pd.to_datetime()",
            "B": "pd.as_time()",
            "C": "df.parse_date()",
            "D": "pd.Timestamp()"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Timedelta' in Pandas?",
        "options": {
            "A": "A specific date",
            "B": "The difference between two datetimes (durations)",
            "C": "A time zone conversion",
            "D": "A countdown timer"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to localize a naive (timezone-unaware) Timestamp?",
        "options": {
            "A": "ts.to_timezone()",
            "B": "ts.tz_localize()",
            "C": "ts.set_tz()",
            "D": "ts.localize_time()"
        },
        "answer": "B"
    },
    {
        "question": "How do you generate a fixed-frequency DatetimeIndex (e.g., daily dates for a month)?",
        "options": {
            "A": "pd.date_range()",
            "B": "pd.time_series()",
            "C": "pd.create_dates()",
            "D": "pd.calendar()"
        },
        "answer": "A"
    },
    {
        "question": "Which frequency alias represents 'Business Day' in date_range?",
        "options": {
            "A": "D",
            "B": "B",
            "C": "W",
            "D": "M"
        },
        "answer": "B"
    },
    {
        "question": "What does 'df.resample('M').mean()' do?",
        "options": {
            "A": "Deletes data for every month",
            "B": "Aggregates time-series data to a monthly frequency by calculating the mean",
            "C": "Sorts data by month",
            "D": "Filters data for only one month"
        },
        "answer": "B"
    },
    {
        "question": "Which attribute of a datetime index allows you to extract the 'Day of the week' (0-6)?",
        "options": {
            "A": "df.index.day",
            "B": "df.index.dayofweek",
            "C": "df.index.weekday",
            "D": "Both B and C"
        },
        "answer": "D"
    },
    {
        "question": "What is the purpose of the 'Categorical' data type in Pandas?",
        "options": {
            "A": "To hide data",
            "B": "To save memory and improve performance for variables with a limited set of values",
            "C": "To sort data alphabetically",
            "D": "To allow for multiple data types in one column"
        },
        "answer": "B"
    },
    {
        "question": "How do you convert a column 'Status' to a Categorical type?",
        "options": {
            "A": "df['Status'].astype('category')",
            "B": "pd.Categorical(df['Status'])",
            "C": "Both A and B",
            "D": "df['Status'].to_cat()"
        },
        "answer": "C"
    },
    {
        "question": "Which method allows you to apply conditional formatting (like highlighting max values) to a DataFrame in a Jupyter Notebook?",
        "options": {
            "A": "df.format()",
            "B": "df.style",
            "C": "df.css",
            "D": "df.highlight()"
        },
        "answer": "B"
    },
    {
        "question": "Which 'style' method is used to create a background gradient based on cell values?",
        "options": {
            "A": "df.style.background_gradient()",
            "B": "df.style.color_scale()",
            "C": "df.style.heatmap()",
            "D": "df.style.apply_colors()"
        },
        "answer": "A"
    },
    {
        "question": "What is the 'eval()' function used for in Pandas?",
        "options": {
            "A": "Evaluating user passwords",
            "B": "Efficiently performing operations on DataFrames using string expressions",
            "C": "Checking for errors",
            "D": "Calculating the mean"
        },
        "answer": "B"
    },
    {
        "question": "Which method is similar to eval() but specifically for filtering data with strings?",
        "options": {
            "A": "df.filter()",
            "B": "df.query()",
            "C": "df.search()",
            "D": "df.select()"
        },
        "answer": "B"
    },
    {
        "question": "How can you significantly reduce the memory footprint of a numeric column that only contains small integers?",
        "options": {
            "A": "Convert it to 'object' type",
            "B": "Downcast it (e.g., from int64 to int8) using pd.to_numeric()",
            "C": "Delete the column",
            "D": "Keep it as is"
        },
        "answer": "B"
    },
    {
        "question": "Which Pandas function is used to 'flatten' a JSON-like dictionary into a flat table?",
        "options": {
            "A": "pd.json_decode()",
            "B": "pd.json_normalize()",
            "C": "pd.flatten_json()",
            "D": "pd.read_json()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Vectorization' in the context of Pandas?",
        "options": {
            "A": "Using 'for' loops to process data",
            "B": "Applying operations to entire arrays/columns at once using optimized C/Cython code",
            "C": "Converting a DataFrame into a 3D matrix",
            "D": "Drawing vectors on a chart"
        },
        "answer": "B"
    },
    {
        "question": "Which method provides the memory usage of a DataFrame in a human-readable format?",
        "options": {
            "A": "df.memory_usage(deep=True)",
            "B": "df.info()",
            "C": "Both A and B",
            "D": "df.size_info()"
        },
        "answer": "C"
    },
    {
        "question": "What does 'df.copy(deep=False)' create?",
        "options": {
            "A": "A complete independent copy of data and index",
            "B": "A 'shallow' copy that shares data with the original",
            "C": "An empty DataFrame",
            "D": "A sorted copy"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to perform element-wise comparison between two DataFrames?",
        "options": {
            "A": "df1.compare(df2)",
            "B": "df1.diff(df2)",
            "C": "df1.match(df2)",
            "D": "df1 == df2"
        },
        "answer": "A"
    },
    {
        "question": "How do you convert a Period object to a Timestamp?",
        "options": {
            "A": "period.to_timestamp()",
            "B": "period.as_time()",
            "C": "pd.Timestamp(period)",
            "D": "period.convert()"
        },
        "answer": "A"
    },
    {
        "question": "Which function is used to 'stack' multiple Series on top of each other horizontally (as columns)?",
        "options": {
            "A": "pd.concat(axis=1)",
            "B": "pd.merge()",
            "C": "pd.append()",
            "D": "pd.stack()"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Windowing' in time-series analysis?",
        "options": {
            "A": "Opening a new tab",
            "B": "Performing calculations on sub-segments of data that 'slide' over the time axis",
            "C": "Scaling the axis",
            "D": "Visualizing data"
        },
        "answer": "B"
    },
    {
        "question": "Which method allows you to apply a function that needs to look at the 'previous' or 'next' value in a Series?",
        "options": {
            "A": "apply()",
            "B": "shift()",
            "C": "map()",
            "D": "transform()"
        },
        "answer": "B"
    },
    {
        "question": "What is the result of 'pd.Timestamp('now')'?",
        "options": {
            "A": "The current date and time",
            "B": "A string 'now'",
            "C": "The start of the current year",
            "D": "An error"
        },
        "answer": "A"
    },
    {
        "question": "Which attribute returns the total memory used by each column in bytes?",
        "options": {
            "A": "df.memory_usage()",
            "B": "df.nbytes",
            "C": "df.size",
            "D": "df.itemsize"
        },
        "answer": "A"
    },
    {
        "question": "In 'read_csv', how do you handle dates that are not in the standard YYYY-MM-DD format?",
        "options": {
            "A": "Use the 'parse_dates' parameter",
            "B": "Use a custom 'date_parser' function",
            "C": "Both A and B",
            "D": "You must manually convert them after loading"
        },
        "answer": "C"
    },
    {
        "question": "What is the purpose of 'df.dropna(thresh=n)'?",
        "options": {
            "A": "Drops columns with more than n nulls",
            "B": "Keeps only rows that have at least n non-null values",
            "C": "Drops rows with exactly n nulls",
            "D": "Clears the cache"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to convert a 'Long' format DataFrame into a 'Wide' format?",
        "options": {
            "A": "melt()",
            "B": "pivot()",
            "C": "stack()",
            "D": "explode()"
        },
        "answer": "B"
    },
    {
        "question": "Which method returns the correlation of all pairs of columns in a DataFrame?",
        "options": {
            "A": "df.corr()",
            "B": "df.covariance()",
            "C": "df.pair_corr()",
            "D": "df.match()"
        },
        "answer": "A"
    },
    {
        "question": "What is the 'HDF5' format (pd.read_hdf) useful for?",
        "options": {
            "A": "Storing small text files",
            "B": "High-performance storage and retrieval of very large datasets",
            "C": "Displaying data on the web",
            "D": "Sending emails"
        },
        "answer": "B"
    },
    {
        "question": "How do you check the version of Pandas you are using?",
        "options": {
            "A": "pd.version",
            "B": "pd.__version__",
            "C": "pd.show_versions()",
            "D": "Both B and C"
        },
        "answer": "D"
    },
    {
        "question": "What does 'df.groupby().cumcount()' do?",
        "options": {
            "A": "Sums all values in a group",
            "B": "Returns the number of each item within each group (0 to n-1)",
            "C": "Counts the total groups",
            "D": "Calculates the average"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to merge two DataFrames based on the closest matching key (common in finance for timestamps)?",
        "options": {
            "A": "pd.merge()",
            "B": "pd.merge_asof()",
            "C": "pd.merge_ordered()",
            "D": "pd.fuzzy_merge()"
        },
        "answer": "B"
    },
    {
        "question": "How do you apply a function to a Series while passing additional arguments?",
        "options": {
            "A": "s.apply(func, args=(arg1,))",
            "B": "s.apply(func, arg1)",
            "C": "s.map(func, arg1)",
            "D": "s.transform(func, arg1)"
        },
        "answer": "A"
    },
    {
        "question": "Which method calculates the exponential moving average (EMA)?",
        "options": {
            "A": "df.rolling().mean()",
            "B": "df.ewm().mean()",
            "C": "df.expanding().mean()",
            "D": "df.moving_avg()"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'object' dtype usually used for in Pandas?",
        "options": {
            "A": "Integers",
            "B": "Strings or mixed data types",
            "C": "Booleans",
            "D": "Complex numbers"
        },
        "answer": "B"
    },
    {
        "question": "How do you clear the current styling of a Styler object?",
        "options": {
            "A": "styler.clear()",
            "B": "styler.reset_index()",
            "C": "There is no direct method; re-apply or re-initialize the styler",
            "D": "styler.remove()"
        },
        "answer": "C"
    },
    {
        "question": "Which parameter in 'to_excel' specifies the name of the sheet?",
        "options": {
            "A": "sheet_name",
            "B": "tab_name",
            "C": "header",
            "D": "name"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of 'df.memory_usage(index=True)'?",
        "options": {
            "A": "To include the memory used by the index labels in the total",
            "B": "To delete the index",
            "C": "To create an index for memory",
            "D": "To show only the index size"
        },
        "answer": "A"
    },
    {
        "question": "Which method returns the row index of the first occurrence of the maximum value?",
        "options": {
            "A": "s.argmax()",
            "B": "s.idxmax()",
            "C": "s.max_index()",
            "D": "s.top_index()"
        },
        "answer": "B"
    },
    {
        "question": "What does 'pd.NA' represent in newer Pandas versions?",
        "options": {
            "A": "A North American code",
            "B": "A experimental experimental missing value indicator for various data types",
            "C": "Not Applicable",
            "D": "A type of string"
        },
        "answer": "B"
    },
    {
        "question": "How do you filter for rows where 'Name' contains the substring 'Smith' (case-insensitive)?",
        "options": {
            "A": "df[df['Name'].str.contains('Smith', case=False)]",
            "B": "df[df['Name'] == 'Smith']",
            "C": "df.query('Name == Smith')",
            "D": "df.find('Smith')"
        },
        "answer": "A"
    },
    {
        "question": "What is the effect of 'df.convert_dtypes()'?",
        "options": {
            "A": "Converts everything to string",
            "B": "Attempts to convert columns to the best possible nullable types",
            "C": "Converts DataFrame to a NumPy array",
            "D": "Clears the data"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to 'explode' a column of lists into separate rows?",
        "options": {
            "A": "df.flatten()",
            "B": "df.explode()",
            "C": "df.split()",
            "D": "df.melt()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Method Overloading' in the context of Pandas 'plot()'?",
        "options": {
            "A": "A way to make the computer run faster",
            "B": "Using the same plot() method to generate different types of charts (bar, line, etc.) via the 'kind' parameter",
            "C": "Writing two functions with the same name",
            "D": "Deleting old plots"
        },
        "answer": "B"
    },
    {
        "question": "Which function is used to create a sample DataFrame with random values for testing?",
        "options": {
            "A": "pd.util.testing.makeDataFrame()",
            "B": "pd.random_df()",
            "C": "pd.sample()",
            "D": "np.random.df()"
        },
        "answer": "A"
    },
    {
        "question": "How do you calculate the correlation between all columns in 'df' using the 'Spearman' method?",
        "options": {
            "A": "df.corr(method='spearman')",
            "B": "df.spearman()",
            "C": "df.corr_spearman()",
            "D": "pd.spearman(df)"
        },
        "answer": "A"
    },
    {
        "question": "Which attribute returns the index object of the columns?",
        "options": {
            "A": "df.columns",
            "B": "df.axes[1]",
            "C": "Both A and B",
            "D": "df.header"
        },
        "answer": "C"
    },
    {
        "question": "Congratulations! You've reached the end. Which library is often used with Pandas for visualization?",
        "options": {
            "A": "Matplotlib",
            "B": "Seaborn",
            "C": "Plotly",
            "D": "All of the above"
        },
        "answer": "D"
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
    skill = "Pandas"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
