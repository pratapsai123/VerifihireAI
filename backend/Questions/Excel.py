from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
  {
    "question": "What is the intersection of a row and a column in Excel called?",
    "options": {
      "A": "Box",
      "B": "Cell",
      "C": "Block",
      "D": "Section"
    },
    "answer": "B"
  },
  {
    "question": "Which symbol must every Excel formula begin with?",
    "options": {
      "A": "+",
      "B": "=",
      "C": "#",
      "D": "@"
    },
    "answer": "B"
  },
  {
    "question": "What is the file extension for a standard Excel workbook in modern versions?",
    "options": {
      "A": ".xls",
      "B": ".xlsx",
      "C": ".xlsm",
      "D": ".xml"
    },
    "answer": "B"
  },
  {
    "question": "Which keyboard shortcut is used to quickly copy a selected range of cells?",
    "options": {
      "A": "Ctrl + P",
      "B": "Ctrl + C",
      "C": "Ctrl + V",
      "D": "Ctrl + X"
    },
    "answer": "B"
  },
  {
    "question": "How do you display the 'Format Cells' dialog box using a keyboard shortcut?",
    "options": {
      "A": "Ctrl + 1",
      "B": "Ctrl + F",
      "C": "Ctrl + D",
      "D": "Ctrl + Shift + F"
    },
    "answer": "A"
  },
  {
    "question": "Which function is used to add all numbers in a range of cells?",
    "options": {
      "A": "ADD()",
      "B": "SUM()",
      "C": "TOTAL()",
      "D": "COUNT()"
    },
    "answer": "B"
  },
  {
    "question": "What happens if you double-click the boundary between two column headers?",
    "options": {
      "A": "It deletes the column",
      "B": "It auto-fits the column width to the longest entry",
      "C": "It hides the column",
      "D": "It merges the columns"
    },
    "answer": "B"
  },
  {
    "question": "Which feature allows you to keep specific rows or columns visible while scrolling through a large worksheet?",
    "options": {
      "A": "Split Panes",
      "B": "Freeze Panes",
      "C": "Lock Cells",
      "D": "Static Rows"
    },
    "answer": "B"
  },
  {
    "question": "In a formula, what does '$A$1' signify?",
    "options": {
      "A": "Relative Cell Reference",
      "B": "Absolute Cell Reference",
      "C": "Mixed Cell Reference",
      "D": "Currency Value"
    },
    "answer": "B"
  },
  {
    "question": "Which function allows you to count the number of cells that contain numbers in a range?",
    "options": {
      "A": "COUNTA()",
      "B": "COUNT()",
      "C": "COUNTIF()",
      "D": "NUM()"
    },
    "answer": "B"
  },
  {
    "question": "How can you select an entire column in a worksheet using the keyboard?",
    "options": {
      "A": "Shift + Space",
      "B": "Ctrl + Space",
      "C": "Alt + Space",
      "D": "Ctrl + A"
    },
    "answer": "B"
  },
  {
    "question": "Which Excel tool is used to quickly change the appearance of cells based on specific rules (e.g., highlighting values > 100)?",
    "options": {
      "A": "AutoFormat",
      "B": "Conditional Formatting",
      "C": "Cell Styles",
      "D": "Data Validation"
    },
    "answer": "B"
  },
  {
    "question": "What does the error '#VALUE!' typically mean in Excel?",
    "options": {
      "A": "A formula is dividing by zero",
      "B": "A formula has the wrong type of argument (e.g., trying to add text and numbers)",
      "C": "The column is too narrow",
      "D": "The formula refers to a deleted cell"
    },
    "answer": "B"
  },
  {
    "question": "Which ribbon tab contains the 'Sort & Filter' options?",
    "options": {
      "A": "Insert",
      "B": "Data",
      "C": "Review",
      "D": "View"
    },
    "answer": "B"
  },
  {
    "question": "How do you start a new line within the same cell?",
    "options": {
      "A": "Enter",
      "B": "Alt + Enter",
      "C": "Ctrl + Enter",
      "D": "Shift + Enter"
    },
    "answer": "B"
  },
  {
    "question": "Which function is used to find the highest value in a range?",
    "options": {
      "A": "HIGH()",
      "B": "MAX()",
      "C": "TOP()",
      "D": "LARGE()"
    },
    "answer": "B"
  },
  {
    "question": "What is the shortcut to save an Excel workbook?",
    "options": {
      "A": "Ctrl + S",
      "B": "Ctrl + Shift + S",
      "C": "F12",
      "D": "Both A and C"
    },
    "answer": "D"
  },
  {
    "question": "Which tool would you use to combine multiple cells into one larger cell?",
    "options": {
      "A": "Wrap Text",
      "B": "Merge & Center",
      "C": "Consolidate",
      "D": "Join Cells"
    },
    "answer": "B"
  },
  {
    "question": "Which function is used to find the average of a range of numbers?",
    "options": {
      "A": "MEAN()",
      "B": "AVERAGE()",
      "C": "AVG()",
      "D": "MEDIAN()"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Workbook' in Excel?",
    "options": {
      "A": "A single page in a file",
      "B": "An Excel file that contains one or more worksheets",
      "C": "The area where formulas are written",
      "D": "A collection of charts"
    },
    "answer": "B"
  },
  {
    "question": "Which feature automatically completes a series of data (e.g., days of the week) when you drag the corner of a cell?",
    "options": {
      "A": "AutoCorrect",
      "B": "AutoFill",
      "C": "AutoSum",
      "D": "Flash Fill"
    },
    "answer": "B"
  },
  {
    "question": "What is the shortcut to undo the last action?",
    "options": {
      "A": "Ctrl + Y",
      "B": "Ctrl + Z",
      "C": "Ctrl + U",
      "D": "Ctrl + R"
    },
    "answer": "B"
  },
  {
    "question": "Which function returns the current date and time?",
    "options": {
      "A": "DATE()",
      "B": "NOW()",
      "C": "TODAY()",
      "D": "TIME()"
    },
    "answer": "B"
  },
  {
    "question": "What symbol is used to represent 'not equal to' in Excel formulas?",
    "options": {
      "A": "!=",
      "B": "<>",
      "C": "~=",
      "D": "NOT="
    },
    "answer": "B"
  },
  {
    "question": "Which feature allows you to view only the rows that meet certain criteria?",
    "options": {
      "A": "Sorting",
      "B": "Filtering",
      "C": "Grouping",
      "D": "Validation"
    },
    "answer": "B"
  },
  {
    "question": "Which function would you use to check if a condition is met and return one value if TRUE and another if FALSE?",
    "options": {
      "A": "CHECK()",
      "B": "IF()",
      "C": "MATCH()",
      "D": "CASE()"
    },
    "answer": "B"
  },
  {
    "question": "In the VLOOKUP function, what does the 'col_index_num' argument represent?",
    "options": {
      "A": "The value to be searched for",
      "B": "The column number in the range from which the matching value should be returned",
      "C": "The total number of columns in the sheet",
      "D": "The row index"
    },
    "answer": "B"
  },
  {
    "question": "Which function is used to join two or more text strings into one?",
    "options": {
      "A": "JOIN()",
      "B": "CONCATENATE()",
      "C": "MERGE()",
      "D": "COMBINE()"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the IFERROR function?",
    "options": {
      "A": "To find all errors in a worksheet",
      "B": "To return a custom value if a formula results in an error",
      "C": "To prevent the user from typing wrong data",
      "D": "To delete cells with errors"
    },
    "answer": "B"
  },
  {
    "question": "Which logical function returns TRUE only if ALL of its arguments are true?",
    "options": {
      "A": "OR()",
      "B": "AND()",
      "C": "NOT()",
      "D": "ANY()"
    },
    "answer": "B"
  },
  {
    "question": "Which feature allows you to restrict the type of data or the values that users enter into a cell?",
    "options": {
      "A": "Data Restriction",
      "B": "Data Validation",
      "C": "Cell Protection",
      "D": "Input Mask"
    },
    "answer": "B"
  },
  {
    "question": "If you want to find an exact match in VLOOKUP, what value should you use for the 'range_lookup' argument?",
    "options": {
      "A": "TRUE",
      "B": "FALSE (or 0)",
      "C": "1",
      "D": "EXACT"
    },
    "answer": "B"
  },
  {
    "question": "Which function counts the number of cells within a range that meet a single specific criterion?",
    "options": {
      "A": "COUNT()",
      "B": "COUNTIF()",
      "C": "SUMIF()",
      "D": "COUNTIFS()"
    },
    "answer": "B"
  },
  {
    "question": "What does the HLOOKUP function search for?",
    "options": {
      "A": "Values in a specific column",
      "B": "Values in the top row of a table or array",
      "C": "Hidden values in a sheet",
      "D": "Hyperlinks"
    },
    "answer": "B"
  },
  {
    "question": "Which tool is used to separate a single column of text (like 'First Last') into multiple columns?",
    "options": {
      "A": "Flash Fill",
      "B": "Text to Columns",
      "C": "Format Painter",
      "D": "Data Consolidate"
    },
    "answer": "B"
  },
  {
    "question": "What keyboard shortcut toggles absolute and relative references in a formula (e.g., A1 to $A$1)?",
    "options": {
      "A": "F2",
      "B": "F4",
      "C": "F9",
      "D": "F12"
    },
    "answer": "B"
  },
  {
    "question": "Which function is used to remove extra spaces from text, except for single spaces between words?",
    "options": {
      "A": "CLEAN()",
      "B": "TRIM()",
      "C": "REPLACE()",
      "D": "SUBSTITUTE()"
    },
    "answer": "B"
  },
  {
    "question": "What is the result of the formula =LEN('Excel')?",
    "options": {
      "A": "5",
      "B": "6",
      "C": "E",
      "D": "1"
    },
    "answer": "A"
  },
  {
    "question": "Which feature would you use to create a dropdown list in a cell?",
    "options": {
      "A": "Slicer",
      "B": "Data Validation",
      "C": "ComboBox",
      "D": "PivotTable"
    },
    "answer": "B"
  },
  {
    "question": "Which function would you use to find the position of a value in a range rather than the value itself?",
    "options": {
      "A": "VLOOKUP()",
      "B": "MATCH()",
      "C": "INDEX()",
      "D": "FIND()"
    },
    "answer": "B"
  },
  {
    "question": "What does the error '#N/A' usually indicate in a VLOOKUP formula?",
    "options": {
      "A": "The column index is wrong",
      "B": "The lookup value was not found in the first column of the table array",
      "C": "The formula contains a typo",
      "D": "The source data is deleted"
    },
    "answer": "B"
  },
  {
    "question": "How do you hide a row in Excel using a keyboard shortcut?",
    "options": {
      "A": "Ctrl + 0",
      "B": "Ctrl + 9",
      "C": "Ctrl + H",
      "D": "Ctrl + Shift + ("
    },
    "answer": "B"
  },
  {
    "question": "Which function adds the cells specified by a given set of conditions or criteria?",
    "options": {
      "A": "ADDIF()",
      "B": "SUMIFS()",
      "C": "TOTALIF()",
      "D": "SUMPRODUCT()"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary benefit of using a Named Range in Excel?",
    "options": {
      "A": "It makes the file smaller",
      "B": "It makes formulas easier to read and maintain",
      "C": "It speeds up the calculation engine",
      "D": "It prevents users from seeing the data"
    },
    "answer": "B"
  },
  {
    "question": "Which tool would you use to automatically fill in data when it senses a pattern (e.g., extracting emails from names)?",
    "options": {
      "A": "AutoSum",
      "B": "Flash Fill",
      "C": "Format Painter",
      "D": "AutoCorrect"
    },
    "answer": "B"
  },
  {
    "question": "Which function returns a sub-portion of a text string starting from the left side?",
    "options": {
      "A": "PART()",
      "B": "LEFT()",
      "C": "RIGHT()",
      "D": "MID()"
    },
    "answer": "B"
  },
  {
    "question": "What is the keyboard shortcut to insert a new worksheet?",
    "options": {
      "A": "Shift + F11",
      "B": "Ctrl + N",
      "C": "Alt + Shift + F1",
      "D": "Both A and C"
    },
    "answer": "D"
  },
  {
    "question": "Which function returns the arithmetic mean of all cells in a range that meet a given criteria?",
    "options": {
      "A": "AVERAGE()",
      "B": "AVERAGEIF()",
      "C": "MEANIF()",
      "D": "SUMIF()"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'OR' function return if at least one argument is TRUE?",
    "options": {
      "A": "FALSE",
      "B": "TRUE",
      "C": "The value of the argument",
      "D": "#VALUE!"
    },
    "answer": "B"
  },
  {
    "question": "Which feature would you use to remove all identical rows from a table?",
    "options": {
      "A": "Filter",
      "B": "Remove Duplicates",
      "C": "Consolidate",
      "D": "Clear All"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary purpose of a PivotTable in Excel?",
    "options": {
      "A": "To create a backup of the data",
      "B": "To summarize, analyze, explore, and present large amounts of data quickly",
      "C": "To write VBA macros",
      "D": "To protect a worksheet with a password"
    },
    "answer": "B"
  },
  {
    "question": "Which area in the PivotTable Fields pane would you use to group data by categories like 'Region' or 'Year'?",
    "options": {
      "A": "Values",
      "B": "Rows",
      "C": "Filters",
      "D": "Legend"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Slicer' in the context of PivotTables?",
    "options": {
      "A": "A tool to cut a worksheet into separate files",
      "B": "A visual filtering component that allows users to filter data in a PivotTable with a single click",
      "C": "A way to delete rows and columns",
      "D": "A type of 3D pie chart"
    },
    "answer": "B"
  },
  {
    "question": "Which function is the modern, more powerful replacement for VLOOKUP that can look both left and right?",
    "options": {
      "A": "ZLOOKUP()",
      "B": "XLOOKUP()",
      "C": "MATCH()",
      "D": "LOOKUP()"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Spill' error in modern Excel?",
    "options": {
      "A": "When the computer runs out of memory",
      "B": "When a dynamic array formula cannot return multiple results because existing data is blocking the range",
      "C": "When a formula contains a typo",
      "D": "When data is copied to the wrong sheet"
    },
    "answer": "B"
  },
  {
    "question": "Which dynamic array function is used to return a list of unique values from a range?",
    "options": {
      "A": "DISTINCT()",
      "B": "UNIQUE()",
      "C": "SINGLE()",
      "D": "FILTER()"
    },
    "answer": "B"
  },
  {
    "question": "In a PivotTable, how do you change a field from 'Sum' to 'Average'?",
    "options": {
      "A": "Right-click the value > Value Field Settings",
      "B": "Double-click the column header",
      "C": "Go to the Design tab",
      "D": "Rewrite the data source"
    },
    "answer": "A"
  },
  {
    "question": "What is the purpose of 'Power Pivot' in Excel?",
    "options": {
      "A": "To create colorful charts",
      "B": "To handle large datasets (millions of rows) and create complex data models with relationships",
      "C": "To automate tasks with mouse clicks",
      "D": "To edit PDF files in Excel"
    },
    "answer": "B"
  },
  {
    "question": "Which function allows you to combine the results of two or more arrays horizontally?",
    "options": {
      "A": "VSTACK()",
      "B": "HSTACK()",
      "C": "JOIN()",
      "D": "MERGE()"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'INDEX' function return?",
    "options": {
      "A": "The position of a value",
      "B": "The value of a cell at a specific row and column intersection within a range",
      "C": "The total number of rows in a sheet",
      "D": "The date the file was created"
    },
    "answer": "B"
  },
  {
    "question": "Which tool would you use to see what value an input must be to reach a specific target (e.g., 'What must sales be to reach $1M profit?')?",
    "options": {
      "A": "Solver",
      "B": "Goal Seek",
      "C": "Scenario Manager",
      "D": "Data Table"
    },
    "answer": "B"
  },
  {
    "question": "What is the keyboard shortcut to create a PivotTable from a selected range?",
    "options": {
      "A": "Alt + N + V",
      "B": "Ctrl + P",
      "C": "Alt + F1",
      "D": "Ctrl + T"
    },
    "answer": "A"
  },
  {
    "question": "Which function would you use to sort a range of data automatically using a formula?",
    "options": {
      "A": "ORDER()",
      "B": "SORT()",
      "C": "ARRANGE()",
      "D": "RANK()"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Calculated Field' in a PivotTable?",
    "options": {
      "A": "A field in the original data source",
      "B": "A custom field created within the PivotTable that performs calculations on other fields",
      "C": "A field that only counts the number of rows",
      "D": "A field used for filtering only"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Data Model' in Excel?",
    "options": {
      "A": "A template for a spreadsheet",
      "B": "A collection of tables with defined relationships that acts as the backbone for Power Pivot",
      "C": "A graph that shows data trends",
      "D": "A way to organize files on a drive"
    },
    "answer": "B"
  },
  {
    "question": "Which dynamic array function is used to extract data from a range based on a specific condition?",
    "options": {
      "A": "SEARCH()",
      "B": "FILTER()",
      "C": "MATCH()",
      "D": "EXTRACT()"
    },
    "answer": "B"
  },
  {
    "question": "In Power Pivot, what is 'DAX'?",
    "options": {
      "A": "Data Analysis Expressions, a formula language used for advanced calculations",
      "B": "Digital Array X-change, a file format",
      "C": "A tool to create animations",
      "D": "A way to compress files"
    },
    "answer": "A"
  },
  {
    "question": "What does the '#REF!' error indicate?",
    "options": {
      "A": "A division by zero",
      "B": "A formula refers to a cell that is no longer valid (often because it was deleted)",
      "C": "The text is too long for the cell",
      "D": "A problem with the internet connection"
    },
    "answer": "B"
  },
  {
    "question": "Which feature allows you to see the relationships between formulas and the cells they reference?",
    "options": {
      "A": "Data Validation",
      "B": "Trace Precedents / Trace Dependents",
      "C": "Watch Window",
      "D": "Error Checking"
    },
    "answer": "B"
  },
  {
    "question": "What is the shortcut to 'Flash Fill' a column based on a pattern?",
    "options": {
      "A": "Ctrl + F",
      "B": "Ctrl + E",
      "C": "Ctrl + G",
      "D": "Ctrl + D"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Power Query' used for in Excel?",
    "options": {
      "A": "To create 3D charts",
      "B": "To connect, combine, and refine data from multiple sources (ETL)",
      "C": "To check spelling in multiple languages",
      "D": "To speed up the computer's CPU"
    },
    "answer": "B"
  },
  {
    "question": "Which tab must be enabled in the Ribbon to access Visual Basic for Applications (VBA)?",
    "options": {
      "A": "Data",
      "B": "Developer",
      "C": "Review",
      "D": "Add-ins"
    },
    "answer": "B"
  },
  {
    "question": "What is an Excel 'Macro'?",
    "options": {
      "A": "A large spreadsheet",
      "B": "A recorded sequence of instructions that automates repetitive tasks",
      "C": "A type of advanced formula",
      "D": "A way to increase the font size"
    },
    "answer": "B"
  },
  {
    "question": "What is the file extension for an Excel workbook that contains macros?",
    "options": {
      "A": ".xlsx",
      "B": ".xlsm",
      "C": ".csv",
      "D": ".docx"
    },
    "answer": "B"
  },
  {
    "question": "In VBA, what does 'Sub' stand for?",
    "options": {
      "A": "Subtract",
      "B": "Subroutine",
      "C": "Substitute",
      "D": "Subject"
    },
    "answer": "B"
  },
  {
    "question": "Which keyboard shortcut opens the Visual Basic Editor (VBE)?",
    "options": {
      "A": "Alt + F8",
      "B": "Alt + F11",
      "C": "Ctrl + F11",
      "D": "Alt + Shift + F11"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Query Folding' in Power Query?",
    "options": {
      "A": "Hiding queries in folders",
      "B": "The ability to push data transformations back to the source database (like SQL)",
      "C": "Compressing the query to save space",
      "D": "Deleting duplicate queries"
    },
    "answer": "B"
  },
  {
    "question": "Which tool would you use to find the optimal value for a formula in one cell subject to constraints on other cells?",
    "options": {
      "A": "Goal Seek",
      "B": "Solver",
      "C": "Scenario Manager",
      "D": "PivotTable"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Option Explicit' do in a VBA module?",
    "options": {
      "A": "It makes the code run faster",
      "B": "It forces the explicit declaration of all variables",
      "C": "It hides the code from users",
      "D": "It allows the use of Greek symbols"
    },
    "answer": "B"
  },
  {
    "question": "Which Power Query transformation changes columns into rows?",
    "options": {
      "A": "Transpose",
      "B": "Unpivot",
      "C": "Pivot",
      "D": "Group By"
    },
    "answer": "B"
  },
  {
    "question": "In VBA, what is a 'Variable' used for?",
    "options": {
      "A": "To create a dropdown menu",
      "B": "To store a data value in memory for use during code execution",
      "C": "To change the sheet name",
      "D": "To protect the workbook"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Watch Window' used for in Excel?",
    "options": {
      "A": "To watch training videos",
      "B": "To monitor the values of specific cells even when working in different sheets",
      "C": "To see who else is editing the file",
      "D": "To set an alarm for data refresh"
    },
    "answer": "B"
  },
  {
    "question": "Which VBA command is used to display a simple popup message to the user?",
    "options": {
      "A": "Alert()",
      "B": "MsgBox",
      "C": "Popup()",
      "D": "ShowMessage"
    },
    "answer": "B"
  },
  {
    "question": "What is 'M' in the context of Excel?",
    "options": {
      "A": "A math function",
      "B": "The formula language used behind the scenes in Power Query",
      "C": "A shortcut for 'Macros'",
      "D": "A unit of memory measurement"
    },
    "answer": "B"
  },
  {
    "question": "Which feature would you use to automatically run code when a specific event occurs, such as opening a workbook?",
    "options": {
      "A": "AutoRun Macro",
      "B": "Event Procedures (e.g., Workbook_Open)",
      "C": "Schedule Task",
      "D": "Data Refresh"
    },
    "answer": "B"
  },
  {
    "question": "What does 'ActiveCell.Value = 10' do in VBA?",
    "options": {
      "A": "Checks if the cell value is 10",
      "B": "Assigns the number 10 to the currently selected cell",
      "C": "Deletes the cell if it contains 10",
      "D": "Moves the selection 10 cells down"
    },
    "answer": "B"
  },
  {
    "question": "Which tool allows you to see the step-by-step transformation of data in Power Query?",
    "options": {
      "A": "History Log",
      "B": "Applied Steps Pane",
      "C": "Query Navigator",
      "D": "Formula Bar"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'User Defined Function' (UDF) in Excel?",
    "options": {
      "A": "A standard function like SUM",
      "B": "A custom function created using VBA to perform calculations not available in built-in functions",
      "C": "A function that only works for one user",
      "D": "A button on the ribbon"
    },
    "answer": "B"
  },
  {
    "question": "Which shortcut is used to 'Step Into' code line-by-line while debugging in VBA?",
    "options": {
      "A": "F5",
      "B": "F8",
      "C": "F9",
      "D": "F2"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Fuzzy Matching' in Power Query?",
    "options": {
      "A": "Matching values with different colors",
      "B": "A technique to join tables based on approximate text matches rather than exact strings",
      "C": "Cleaning blurry images in a sheet",
      "D": "A logic error in a formula"
    },
    "answer": "B"
  },
  {
    "question": "Which chart type is best suited for showing the relationship between two numerical variables to identify correlations?",
    "options": {
      "A": "Line Chart",
      "B": "Scatter Plot",
      "C": "Bar Chart",
      "D": "Radar Chart"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Sparkline' in Excel?",
    "options": {
      "A": "A special type of macro",
      "B": "A tiny chart that resides within a single cell to show a data trend",
      "C": "A line that connects two different workbooks",
      "D": "A tool to highlight errors"
    },
    "answer": "B"
  },
  {
    "question": "In Power Pivot, what is the 'Measures' area used for?",
    "options": {
      "A": "Storing raw text data",
      "B": "Defining explicit DAX calculations that aggregate data (like Total Sales)",
      "C": "Setting the column width",
      "D": "Naming the workbook"
    },
    "answer": "B"
  },
  {
    "question": "Which feature allows you to display a small icon or bar inside a cell based on its value compared to others?",
    "options": {
      "A": "Sparklines",
      "B": "Conditional Formatting (Data Bars/Icon Sets)",
      "C": "Data Validation",
      "D": "Cell Styles"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Sensitivity Analysis' typically performed with in Excel?",
    "options": {
      "A": "PivotTables",
      "B": "Data Tables (What-If Analysis)",
      "C": "VLOOKUP",
      "D": "Filter"
    },
    "answer": "B"
  },
  {
    "question": "Which DAX function in Power Pivot is used to change the filter context of a calculation?",
    "options": {
      "A": "SUM()",
      "B": "CALCULATE()",
      "C": "FILTER()",
      "D": "ALL()"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Waterfall Chart' primarily used to visualize?",
    "options": {
      "A": "Continuous trends over time",
      "B": "The cumulative effect of sequentially introduced positive or negative values",
      "C": "The distribution of a population",
      "D": "Top 10 items in a list"
    },
    "answer": "B"
  },
  {
    "question": "How do you protect only specific cells in a worksheet while leaving others editable?",
    "options": {
      "A": "Format Cells > Protection > Uncheck 'Locked', then Protect Sheet",
      "B": "Password protect the whole file",
      "C": "Hide the rows you don't want edited",
      "D": "This is not possible in Excel"
    },
    "answer": "A"
  },
  {
    "question": "Which tool helps identify which cells are used in a selected formula by drawing arrows?",
    "options": {
      "A": "Formula Bar",
      "B": "Trace Precedents",
      "C": "Error Checking",
      "D": "Watch Window"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Inquire' in Excel (Professional versions)?",
    "options": {
      "A": "A chat bot for help",
      "B": "An add-in for analyzing, auditing, and reviewing workbooks to understand their design and dependencies",
      "C": "A search engine for templates",
      "D": "A way to email a sheet"
    },
    "answer": "B"
  },
  {
    "question": "In a PivotTable, what does 'Grouping' a Date field allow you to do?",
    "options": {
      "A": "Delete old dates",
      "B": "Summarize data by Months, Quarters, or Years instead of individual days",
      "C": "Sort the dates alphabetically",
      "D": "Change the date format"
    },
    "answer": "B"
  },
  {
    "question": "Which chart is best for showing parts of a whole where the total is 100%?",
    "options": {
      "A": "Pie or Donut Chart",
      "B": "Area Chart",
      "C": "Scatter Plot",
      "D": "Histogram"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'Camera' tool in Excel useful for?",
    "options": {
      "A": "Taking a selfie for the user profile",
      "B": "Creating a dynamic 'live' image of a range of cells that updates as the source data changes",
      "C": "Scanning receipts",
      "D": "Recording a video macro"
    },
    "answer": "B"
  },
  {
    "question": "Which function allows you to aggregate data in a list or database while ignoring hidden rows or errors?",
    "options": {
      "A": "SUM()",
      "B": "AGGREGATE()",
      "C": "SUBTOTAL()",
      "D": "Both B and C"
    },
    "answer": "D"
  },
  {
    "question": "What is 'Data Modeling' in Excel?",
    "options": {
      "A": "Drawing a picture of the data",
      "B": "Defining relationships between multiple tables to enable complex analysis in PivotTables",
      "C": "Choosing a color theme for the sheet",
      "D": "A way to organize files"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary function of the 'Merge Queries' feature in Power Query?",
    "options": {
      "A": "To add rows from one table to another",
      "B": "To join two tables based on a matching column (similar to a SQL Join or VLOOKUP)",
      "C": "To delete duplicate queries",
      "D": "To combine multiple workbooks into one zip file"
    },
    "answer": "B"
  },
  {
    "question": "Which financial function calculates the Net Present Value of an investment based on a series of periodic cash flows?",
    "options": {
      "A": "IRR()",
      "B": "NPV()",
      "C": "PV()",
      "D": "FV()"
    },
    "answer": "B"
  },
  {
    "question": "In a Dynamic Array environment, what does the '#' symbol do when added to a cell reference (e.g., =SUM(A2#))?",
    "options": {
      "A": "It indicates a protected cell",
      "B": "It refers to the entire 'spilled' range originating from that cell",
      "C": "It marks the cell as a header",
      "D": "It triggers an error message"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Advanced Editor' in Power Query used for?",
    "options": {
      "A": "To change the font style of the query",
      "B": "To view and edit the underlying 'M' code of the data transformations",
      "C": "To write VBA macros",
      "D": "To connect to a printer"
    },
    "answer": "B"
  },
  {
    "question": "Which tool allows you to create multiple versions of data sets to compare different outcomes within the same cells?",
    "options": {
      "A": "Goal Seek",
      "B": "Scenario Manager",
      "C": "Data Validation",
      "D": "Consolidate"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'PMT' function calculate?",
    "options": {
      "A": "The total interest paid over a year",
      "B": "The periodic payment for a loan based on constant payments and a constant interest rate",
      "C": "The time remaining until a loan is paid off",
      "D": "The percentage of tax on a purchase"
    },
    "answer": "B"
  },
  {
    "question": "Which Excel feature helps prevent 'broken' links by allowing you to manage connections to external workbooks?",
    "options": {
      "A": "Protect Workbook",
      "B": "Edit Links",
      "C": "Data Validation",
      "D": "Freeze Panes"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'TRANSPOSE' function in Excel?",
    "options": {
      "A": "To translate text into another language",
      "B": "To switch the orientation of a range from vertical to horizontal or vice-versa",
      "C": "To hide specific rows",
      "D": "To increase the numerical value of a cell"
    },
    "answer": "B"
  },
  {
    "question": "Which Power Query transformation would you use to turn a column of delimited text (e.g., 'Red,Blue,Green') into separate rows?",
    "options": {
      "A": "Split Column by Delimiter (to Rows)",
      "B": "Pivot Column",
      "C": "Unpivot Column",
      "D": "Merge Columns"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'Excel Data Model's' relationship limit regarding 'Many-to-Many'?",
    "options": {
      "A": "It is not supported",
      "B": "It is supported in modern versions to relate two tables where neither has unique values",
      "C": "It only works with Excel 2010",
      "D": "It requires a VBA script to function"
    },
    "answer": "B"
  },
  {
    "question": "Which function allows you to calculate the internal rate of return for a series of non-periodic cash flows?",
    "options": {
      "A": "IRR()",
      "B": "XIRR()",
      "C": "MIRR()",
      "D": "RATE()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Conditional Branching' in a Power Query 'Add Column' step?",
    "options": {
      "A": "Adding a column of random numbers",
      "B": "Creating a new column based on 'if-then-else' logic applied to existing columns",
      "C": "Changing the color of a column",
      "D": "Moving a column to a new sheet"
    },
    "answer": "B"
  },
  {
    "question": "Which tool highlights all cells that contain 'Hardcoded' numbers instead of formulas?",
    "options": {
      "A": "Find & Select > Constants",
      "B": "Trace Dependents",
      "C": "Conditional Formatting > Duplicate Values",
      "D": "Data Validation"
    },
    "answer": "A"
  },
  {
    "question": "What is the purpose of 'LET' function in modern Excel?",
    "options": {
      "A": "To let the user edit the sheet",
      "B": "To assign names to calculation results, improving performance and readability within a formula",
      "C": "To create a list of users",
      "D": "To format text as bold"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Workbook.Queries' in VBA allow you to do?",
    "options": {
      "A": "Edit the text in a cell",
      "B": "Programmatically refresh or modify Power Query connections",
      "C": "Change the printer settings",
      "D": "Delete all charts"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary function of the 'LAMBDA' function in Excel?",
    "options": {
      "A": "To translate text into Greek",
      "B": "To create custom, reusable functions without using VBA or JavaScript",
      "C": "To automate the deletion of empty rows",
      "D": "To connect to a Linux server"
    },
    "answer": "B"
  },
  {
    "question": "Which tool would you use to find the relationship between multiple variables and predict a future outcome based on trends?",
    "options": {
      "A": "Goal Seek",
      "B": "Regression Analysis (Analysis ToolPak)",
      "C": "Consolidate",
      "D": "Data Validation"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'VSTACK' function do in modern Excel?",
    "options": {
      "A": "It creates a vertical bar chart",
      "B": "It appends arrays vertically to create a single, larger array",
      "C": "It hides all vertical gridlines",
      "D": "It calculates the vertical distance between cells"
    },
    "answer": "B"
  },
  {
    "question": "In Power Query, what is 'Privacy Levels' (Public, Organizational, Private) used for?",
    "options": {
      "A": "To hide the query from other users",
      "B": "To prevent data from being leaked between incompatible data sources during a merge",
      "C": "To set a password for the data source",
      "D": "To encrypt the Excel file"
    },
    "answer": "B"
  },
  {
    "question": "Which keyboard shortcut is used to open the 'Power Pivot Window'?",
    "options": {
      "A": "Alt + B",
      "B": "Alt + Y + M",
      "C": "Alt + N",
      "D": "Ctrl + Shift + P"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'CUBE' function (e.g., CUBEVALUE) used for?",
    "options": {
      "A": "To calculate the volume of a 3D shape",
      "B": "To extract data directly from an Analysis Services or Power Pivot data model into a cell",
      "C": "To create a 3D chart",
      "D": "To multiply a number by itself three times"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Self-Referencing Query' in Power Query?",
    "options": {
      "A": "A query that asks for the user's name",
      "B": "A query that uses its own output table as a source to keep historical data snapshots",
      "C": "A query that has no source",
      "D": "A query that only works on the current sheet"
    },
    "answer": "B"
  },
  {
    "question": "Which function allows you to perform horizontal and vertical lookups simultaneously to find a value at an intersection?",
    "options": {
      "A": "VLOOKUP()",
      "B": "XLOOKUP() (using nested lookups)",
      "C": "HLOOKUP()",
      "D": "MATCH()"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Object Model' in Excel VBA?",
    "options": {
      "A": "A physical model of the software",
      "B": "A hierarchy of all the elements in Excel (Application > Workbook > Worksheet > Range)",
      "C": "A way to draw shapes with code",
      "D": "A database of user profiles"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Enable Background Refresh' do in a Data Connection?",
    "options": {
      "A": "Changes the background color of the sheet during refresh",
      "B": "Allows the user to continue working in Excel while the data is being updated",
      "C": "Refreshes the data even when the file is closed",
      "D": "Updates the Windows background"
    },
    "answer": "B"
  },
  {
    "question": "Which dynamic array function is used to create a sequence of numbers (e.g., 1 to 100) automatically?",
    "options": {
      "A": "NUMBER()",
      "B": "SEQUENCE()",
      "C": "LIST()",
      "D": "SERIES()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Data Profiling' in the Power Query Editor?",
    "options": {
      "A": "Creating a social media profile for the data",
      "B": "Visual tools to see the quality, distribution, and statistics of your data (e.g., Column Quality, Column Distribution)",
      "C": "Changing the file name based on data",
      "D": "Hiding columns from the user"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'BYROW' and 'BYCOL' lambda helper functions?",
    "options": {
      "A": "To sort data by row or column",
      "B": "To apply a custom LAMBDA function to each row or column of an array and return the results",
      "C": "To hide rows or columns",
      "D": "To merge rows and columns"
    },
    "answer": "B"
  },
  {
    "question": "Which Excel feature is used to manage and compare different sets of input values (variables) to see their results on formulas?",
    "options": {
      "A": "Solver",
      "B": "Scenario Manager",
      "C": "Goal Seek",
      "D": "Data Validation"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Native Query' in the context of Power Query?",
    "options": {
      "A": "A query written in English",
      "B": "A raw database query (like SQL) sent directly to the server to perform transformations",
      "C": "A query that only works in Excel",
      "D": "A query that has no errors"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Office Scripts' in Excel for the Web?",
    "options": {
      "A": "A new version of VBA for the desktop",
      "B": "A TypeScript-based automation tool designed for Excel on the Web and automation via Power Automate",
      "C": "A way to write formulas in plain English",
      "D": "A tool to design report templates"
    },
    "answer": "B"
  },
  {
    "question": "Which DAX function in Power Pivot would you use to return a table of all the values in a column, ignoring any filters applied to that column?",
    "options": {
      "A": "FILTER()",
      "B": "ALL()",
      "C": "VALUES()",
      "D": "DISTINCT()"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'SCAN' function in Excel's dynamic arrays?",
    "options": {
      "A": "To scan documents using the camera",
      "B": "To iterate through an array and build a running total or accumulator for each step",
      "C": "To find viruses in the file",
      "D": "To search for a text string"
    },
    "answer": "B"
  },
  {
    "question": "In Power Query, what is a 'Parameter' used for?",
    "options": {
      "A": "To set the color of the UI",
      "B": "To create a dynamic value (like a file path or date) that can be changed to update multiple queries at once",
      "C": "To count the number of rows",
      "D": "To protect a cell with a password"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Implicit Measure' vs 'Explicit Measure' in Power Pivot?",
    "options": {
      "A": "Implicit is created by dragging a field; Explicit is written as a DAX formula (best practice)",
      "B": "Implicit is for text; Explicit is for numbers",
      "C": "Implicit is faster",
      "D": "There is no difference"
    },
    "answer": "A"
  },
  {
    "question": "Which tool allows you to visually inspect the relationships and dependencies between different workbooks on a network?",
    "options": {
      "A": "Trace Precedents",
      "B": "Spreadsheet Relationship Diagram (Inquire Add-in)",
      "C": "Power Query",
      "D": "Edit Links"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'REDUCE' function do in Excel's Lambda helper functions?",
    "options": {
      "A": "It makes the file size smaller",
      "B": "It applies a LAMBDA to an entire array and returns a single accumulated result",
      "C": "It deletes duplicate rows",
      "D": "It hides columns"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Linked Entity' in Power BI/Excel Dataflows?",
    "options": {
      "A": "A cell with a hyperlink",
      "B": "An entity that points to a data source in a different dataflow to avoid data duplication",
      "C": "A shortcut to another file",
      "D": "A way to connect to a website"
    },
    "answer": "B"
  },
  {
    "question": "Which function allows you to determine if a value is even or odd within a logic string?",
    "options": {
      "A": "ISEVEN() / ISODD()",
      "B": "CHECKVALUE()",
      "C": "TYPE()",
      "D": "NUMBER()"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'Action Recorder' in Excel for the Web?",
    "options": {
      "A": "A tool to record a video of your screen",
      "B": "A feature that translates your clicks into Office Scripts (TypeScript)",
      "C": "A way to record a voice memo",
      "D": "A log of all user logins"
    },
    "answer": "B"
  },
  {
    "question": "Which DAX function returns the arithmetic mean of all rows that meet specific criteria in a related table?",
    "options": {
      "A": "AVERAGE()",
      "B": "AVERAGEX()",
      "C": "MEAN()",
      "D": "SUMX()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Row Level Security' (RLS) in an Excel Data Model?",
    "options": {
      "A": "Putting a password on a row",
      "B": "A method to restrict data access based on user roles (defined in the Tabular model)",
      "C": "Hiding rows manually",
      "D": "A way to lock the top row"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Table.TransformColumnTypes' in Power Query?",
    "options": {
      "A": "To change the name of the table",
      "B": "To ensure each column is correctly identified as a specific data type (e.g., Date, Int64, Text)",
      "C": "To rotate the columns",
      "D": "To delete columns"
    },
    "answer": "B"
  },
  {
    "question": "Which Excel feature allows you to see how a change in one cell affects a formula in a distant part of the workbook?",
    "options": {
      "A": "Freeze Panes",
      "B": "Watch Window",
      "C": "Split View",
      "D": "Data Table"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Fuzzy Grouping' in Power Query used for?",
    "options": {
      "A": "Grouping blurry images",
      "B": "Consolidating rows with similar but not identical text (e.g., 'Microsoft' and 'Microsoft Inc.')",
      "C": "A way to randomise data",
      "D": "Hiding data groups"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary difference between '.xlsx' and '.xlsb' file formats?",
    "options": {
      "A": ".xlsx is for Mac, .xlsb is for Windows",
      "B": ".xlsx is XML-based, while .xlsb is a Binary format that is often faster and results in smaller files for large datasets",
      "C": ".xlsb does not support macros",
      "D": ".xlsx supports more rows than .xlsb"
    },
    "answer": "B"
  },
  {
    "question": "Which DAX function would you use in Power Pivot to calculate the 'Year-to-Date' total for a sales measure?",
    "options": {
      "A": "SUMYTD()",
      "B": "TOTALYTD()",
      "C": "CUMULATIVE_SUM()",
      "D": "YEARSUM()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Column Profiling' in Power Query useful for?",
    "options": {
      "A": "Changing the color of the column",
      "B": "Analyzing data quality, such as identifying the percentage of errors, empty cells, or unique values in a column",
      "C": "Sorting data alphabetically",
      "D": "Naming the column"
    },
    "answer": "B"
  },
  {
    "question": "Which Excel feature allows you to 'Unpivot' data that is organized in a cross-tab format?",
    "options": {
      "A": "Transpose",
      "B": "Power Query (Unpivot Columns)",
      "C": "Flash Fill",
      "D": "Paste Special"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'MAKEARRAY' function do in modern Excel?",
    "options": {
      "A": "It creates a new worksheet",
      "B": "It returns a calculated array of a specified row and column size by applying a LAMBDA function",
      "C": "It converts text into an array",
      "D": "It deletes an array"
    },
    "answer": "B"
  },
  {
    "question": "In Power Pivot, what is a 'Calculated Column'?",
    "options": {
      "A": "A column that only exists in the report view",
      "B": "A column added to a table in the data model that evaluates a DAX formula for every row",
      "C": "A column imported from SQL",
      "D": "A column used for filtering only"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Query Folding' in Power Query?",
    "options": {
      "A": "Hiding queries in the navigator",
      "B": "The process of pushing data transformations back to the source database to be executed as a single SQL query",
      "C": "Compressing the file size",
      "D": "Deleting duplicate queries"
    },
    "answer": "B"
  },
  {
    "question": "Which keyboard shortcut opens the 'Name Manager' to manage LAMBDAs and Defined Names?",
    "options": {
      "A": "Ctrl + F1",
      "B": "Ctrl + F3",
      "C": "Ctrl + N",
      "D": "Alt + F3"
    },
    "answer": "B"
  },
  {
    "question": "What is 'M' in the context of Power Query?",
    "options": {
      "A": "A math function",
      "B": "The formula language (Data Mashup) used to define query steps",
      "C": "A shortcut for 'Macros'",
      "D": "A unit of memory"
    },
    "answer": "B"
  },
  {
    "question": "Which function is used to check if a specific cell contains a formula?",
    "options": {
      "A": "ISFORMULA()",
      "B": "HASCODE()",
      "C": "CHECK()",
      "D": "TYPE()"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'XMLA Endpoint' useful for in enterprise Excel environments?",
    "options": {
      "A": "To send emails from Excel",
      "B": "To allow third-party tools to connect to and manage datasets in Power BI/Excel models",
      "C": "To create a website from a spreadsheet",
      "D": "To encrypt the file"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'EXPAND' function in dynamic arrays?",
    "options": {
      "A": "To make the font size larger",
      "B": "To grow or pad an array to specified dimensions",
      "C": "To open all hidden rows",
      "D": "To increase the column width"
    },
    "answer": "B"
  },
  {
    "question": "Which DAX function in Excel would you use to compare sales from the 'Same Period Last Year'?",
    "options": {
      "A": "LASTYEAR()",
      "B": "SAMEPERIODLASTYEAR()",
      "C": "PREVIOUSYEAR()",
      "D": "YEAROVER()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Self-Service ETL'?",
    "options": {
      "A": "Ordering food via a spreadsheet",
      "B": "The ability for business users to clean and transform data themselves using tools like Power Query",
      "C": "A macro that runs automatically",
      "D": "A way to backup files"
    },
    "answer": "B"
  },
  {
    "question": "What happens when you 'Enable Load' is unchecked in Power Query?",
    "options": {
      "A": "The query is deleted",
      "B": "The query results are not loaded into the Excel worksheet or Data Model but can still be referenced by other queries",
      "C": "Excel stops responding",
      "D": "The data is hidden from the developer"
    },
    "answer": "B"
  },
  {
    "question": "In Power Query (M), what is the difference between 'Table.AddColumn' and 'Table.TransformColumns'?",
    "options": {
      "A": "AddColumn creates a new column; TransformColumns modifies the data within an existing column",
      "B": "AddColumn is for numbers; TransformColumns is for text",
      "C": "AddColumn is slower than TransformColumns",
      "D": "There is no difference"
    },
    "answer": "A"
  },
  {
    "question": "Which DAX function in Excel returns the values of a column as a single-column table after applying all current filters?",
    "options": {
      "A": "ALL()",
      "B": "VALUES()",
      "C": "FILTER()",
      "D": "DISTINCT()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Row Context' vs 'Filter Context' in Excel's Power Pivot?",
    "options": {
      "A": "Row context is for rows; Filter context is for columns",
      "B": "Row context exists during row-by-row iteration; Filter context is the set of filters applied by PivotTable coordinates and slicers",
      "C": "Row context is faster than filter context",
      "D": "Filter context only applies to text"
    },
    "answer": "B"
  },
  {
    "question": "Which dynamic array function is used to 'reshape' a one-dimensional array into a two-dimensional grid?",
    "options": {
      "A": "WRAPROWS()",
      "B": "TRANSPOSE()",
      "C": "VSTACK()",
      "D": "GRID()"
    },
    "answer": "A"
  },
  {
    "question": "What is the purpose of the 'List.Generate' function in Power Query?",
    "options": {
      "A": "To create a simple list of numbers",
      "B": "To create a list of values based on a loop-like functional approach (useful for API pagination)",
      "C": "To generate a random list",
      "D": "To sort a list alphabetically"
    },
    "answer": "B"
  },
  {
    "question": "In VBA, what is the 'Immediate Window' used for?",
    "options": {
      "A": "To save the file immediately",
      "B": "To debug code, test snippets, or query variable values during runtime",
      "C": "To display error messages to the end-user",
      "D": "To record a macro"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Context Transition' in DAX?",
    "options": {
      "A": "Moving data from Excel to Power BI",
      "B": "The process where a Row Context is transformed into a Filter Context using the CALCULATE function",
      "C": "Changing the format of a date",
      "D": "Deleting a filter from a PivotTable"
    },
    "answer": "B"
  },
  {
    "question": "Which Office Script command is used to log information to the console for debugging in Excel for the Web?",
    "options": {
      "A": "MsgBox()",
      "B": "console.log()",
      "C": "Debug.Print",
      "D": "alert()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Data Lineage' in an enterprise Excel environment?",
    "options": {
      "A": "The history of the developer's family",
      "B": "The path that data takes from its origin source through various transformations to the final report",
      "C": "A list of all users who opened the file",
      "D": "The number of rows in the data model"
    },
    "answer": "B"
  },
  {
    "question": "Which function allows you to determine if a dynamic array formula has successfully 'spilled' or is blocked?",
    "options": {
      "A": "ISERR()",
      "B": "ISERROR()",
      "C": "Excel does not have a specific function for this; it displays a #SPILL! error in the cell",
      "D": "CHECKFILL()"
    },
    "answer": "C"
  },
  {
    "question": "What is the 'VertiPaq' engine in the context of Excel?",
    "options": {
      "A": "A new brand of printer",
      "B": "The high-performance, in-memory columnar database engine that powers Power Pivot",
      "C": "A tool to compress images in Excel",
      "D": "The engine used for spellcheck"
    },
    "answer": "B"
  },
  {
    "question": "Which DAX function would you use to find the 'Total Sales' for all products, regardless of the filter applied to the 'Product Name' slicer?",
    "options": {
      "A": "SUM(Sales[Amount])",
      "B": "CALCULATE(SUM(Sales[Amount]), ALL(Products[ProductName]))",
      "C": "FILTER(Sales, Amount > 0)",
      "D": "VALUES(Products[ProductName])"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'Workbook.Model' object in VBA?",
    "options": {
      "A": "To create a 3D model of the workbook",
      "B": "To programmatically interact with the Power Pivot Data Model and its tables/relationships",
      "C": "To change the theme of the workbook",
      "D": "To protect the workbook with a password"
    },
    "answer": "B"
  },
  {
    "question": "Which Power Query tool allows you to see a graphical representation of how all queries in a workbook are connected?",
    "options": {
      "A": "Query Navigator",
      "B": "Query Dependencies View",
      "C": "Applied Steps",
      "D": "Data Profiling"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Sensitivity Labeling' in Microsoft 365 Excel?",
    "options": {
      "A": "A way to label cells based on their color",
      "B": "A governance feature to classify and protect sensitive data (e.g., 'Confidential') across the organization",
      "C": "A tool to detect emotional language in text",
      "D": "A way to hide rows based on user roles"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary benefit of using 'Variable' (VAR) in a complex DAX measure in Excel?",
    "options": {
      "A": "It makes the formula look more professional",
      "B": "It improves performance by evaluating an expression once and reusing the result, while also making code easier to read",
      "C": "It allows the formula to be exported to Word",
      "D": "It deletes old data automatically"
    },
    "answer": "B"
  },
  {
    "question": "Which Power Query 'M' function is used to create a loop-like structure for handling paginated API responses?",
    "options": {
      "A": "Table.Loop()",
      "B": "List.Generate()",
      "C": "Query.Repeat()",
      "D": "Table.Iterate()"
    },
    "answer": "B"
  },
  {
    "question": "In Office Scripts (TypeScript), which object represents the top-level interface to the Excel application on the web?",
    "options": {
      "A": "Application",
      "B": "Workbook",
      "C": "Excel.Interface",
      "D": "Main"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Columnar Storage' in the context of the Excel VertiPaq engine?",
    "options": {
      "A": "Storing data in columns instead of rows to achieve high compression and fast aggregation",
      "B": "A way to hide columns from users",
      "C": "A tool to sort columns alphabetically",
      "D": "Formatting columns with specific colors"
    },
    "answer": "A"
  },
  {
    "question": "Which DAX function would you use to find the first date in the current filter context where a measure is not blank?",
    "options": {
      "A": "FIRSTDATE()",
      "B": "FIRSTNONBLANK()",
      "C": "MIN()",
      "D": "STARTDATE()"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Data Mesh' integration in modern enterprise Excel refer to?",
    "options": {
      "A": "A disorganized spreadsheet",
      "B": "A decentralized data architecture where Excel connects to domain-specific data products rather than a single central warehouse",
      "C": "A type of table formatting",
      "D": "A way to merge multiple sheets"
    },
    "answer": "B"
  },
  {
    "question": "Which keyboard shortcut is used to 'Step Out' of a function during VBA debugging?",
    "options": {
      "A": "F8",
      "B": "Ctrl + Shift + F8",
      "C": "F5",
      "D": "Alt + F8"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Lazy Evaluation' behavior in the Power Query M engine?",
    "options": {
      "A": "The engine waits for the user to click 'Refresh'",
      "B": "The engine only evaluates the specific steps or parts of a query that are actually required for the final output",
      "C": "The engine runs slower on older computers",
      "D": "The engine skips errors to save time"
    },
    "answer": "B"
  },
  {
    "question": "Which dynamic array function allows you to remove rows or columns from the start or end of an array?",
    "options": {
      "A": "SLICE()",
      "B": "DROP()",
      "C": "TAKE()",
      "D": "Both B and C"
    },
    "answer": "D"
  },
  {
    "question": "What is 'Object-Level Security' (OLS) used for in a Power Pivot model?",
    "options": {
      "A": "Protecting images and shapes",
      "B": "Hiding entire sensitive tables or columns from specific users, preventing them from even seeing the metadata",
      "C": "Locking the file with a password",
      "D": "Hiding the ribbon"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'Value.NativeQuery' function in Power Query?",
    "options": {
      "A": "To translate a query into another language",
      "B": "To pass a raw SQL query directly to a database while maintaining potential for query folding",
      "C": "To create a list of numbers",
      "D": "To refresh the connection"
    },
    "answer": "B"
  },
  {
    "question": "Which DAX function acts as an 'Iterator', evaluating an expression for every row of a table and then summing the results?",
    "options": {
      "A": "SUM()",
      "B": "SUMX()",
      "C": "TOTAL()",
      "D": "CALCULATE()"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'BIML' (Business Intelligence Markup Language) used for in advanced Excel automation?",
    "options": {
      "A": "To format text in a cell",
      "B": "To define and generate SSIS packages or Excel Data Models using XML-based scripts",
      "C": "To create a 3D model of the data",
      "D": "To protect a worksheet"
    },
    "answer": "B"
  },
  {
    "question": "Which tool in Excel allows you to analyze the performance of your DAX measures and identify 'hot spots' in the engine?",
    "options": {
      "A": "Performance Analyzer",
      "B": "DAX Studio (External Tool)",
      "C": "Task Manager",
      "D": "Watch Window"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Referential Integrity' in an Excel Data Model relationship?",
    "options": {
      "A": "Ensuring all rows in a Fact table have a corresponding row in the related Dimension table",
      "B": "Ensuring the file name is correct",
      "C": "Protecting the file from hackers",
      "D": "Sorting data by ID"
    },
    "answer": "A"
  },
  {
    "question": "What is the primary benefit of the 'Power Pivot' Data Model over standard Excel tables for large datasets?",
    "options": {
      "A": "It allows for more colorful charts",
      "B": "It uses a compressed columnar database (VertiPaq) that can handle millions of rows without slowing down",
      "C": "It automatically corrects spelling errors",
      "D": "It saves the file as a PDF"
    },
    "answer": "B"
  },
  {
    "question": "Which Excel feature allows you to see the result of a formula change across multiple 'what-if' scenarios in a single table?",
    "options": {
      "A": "PivotTable",
      "B": "Data Table (under What-If Analysis)",
      "C": "Consolidate",
      "D": "Data Validation"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Drill Down' in a PivotTable?",
    "options": {
      "A": "Deleting a specific row",
      "B": "Double-clicking a value to see the underlying source data that makes up that number",
      "C": "Increasing the font size",
      "D": "Sorting data in descending order"
    },
    "answer": "B"
  },
  {
    "question": "In Power Query, what does 'Choose Columns' do to the underlying M-code to improve performance?",
    "options": {
      "A": "It just hides the columns visually",
      "B": "It applies a 'SelectColumns' step that can enable Query Folding and reduce data transfer from the source",
      "C": "It deletes the data from the hard drive",
      "D": "It renames the query"
    },
    "answer": "B"
  },
  {
    "question": "Which DAX function would you use to return a table of all the distinct values of a column, including the 'Blank' row if it exists due to relationship mismatches?",
    "options": {
      "A": "DISTINCT()",
      "B": "VALUES()",
      "C": "ALL()",
      "D": "FILTER()"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Solver' add-in primarily used for in financial modeling?",
    "options": {
      "A": "To find the average of a list",
      "B": "Optimization—finding a maximum, minimum, or specific value for a cell by changing other variables within constraints",
      "C": "To create a pivot table",
      "D": "To protect a worksheet"
    },
    "answer": "B"
  },
  {
    "question": "Which dynamic array function is used to vertically stack multiple ranges into a single continuous range?",
    "options": {
      "A": "HSTACK()",
      "B": "VSTACK()",
      "C": "APPEND()",
      "D": "COMBINE()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Context Transition' specifically triggered by in DAX?",
    "options": {
      "A": "The SUM function",
      "B": "The CALCULATE function",
      "C": "The IF function",
      "D": "The DATE function"
    },
    "answer": "B"
  },
  {
    "question": "Which tool in Excel's 'Inquire' add-in is used to find broken links and hidden dependencies between different files?",
    "options": {
      "A": "Clean Excess Cell Formatting",
      "B": "Workbook Relationship Diagram",
      "C": "Trace Dependents",
      "D": "Compare Files"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Fuzzy Matching' in the context of merging two Power Queries?",
    "options": {
      "A": "Matching values based on their color",
      "B": "Using algorithms to join tables based on approximate text matches (e.g., 'Apple' vs 'Appel')",
      "C": "Matching values with different font sizes",
      "D": "A query that has no source"
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
    skill = "Excel"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
