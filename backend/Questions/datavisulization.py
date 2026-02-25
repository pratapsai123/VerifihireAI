from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
    {
        "question": "Which chart type is best for showing trends over a continuous period of time?",
        "options": {
            "A": "Bar Chart",
            "B": "Line Chart",
            "C": "Pie Chart",
            "D": "Scatter Plot"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary purpose of a Scatter Plot?",
        "options": {
            "A": "To show part-to-whole relationships",
            "B": "To visualize the correlation between two numerical variables",
            "C": "To display hierarchical data",
            "D": "To show ranking"
        },
        "answer": "B"
    },
    {
        "question": "In data visualization, what does 'Data-Ink Ratio' refer to?",
        "options": {
            "A": "The amount of ink used to print a chart",
            "B": "The proportion of ink used to represent actual data vs. non-information",
            "C": "The resolution of the digital image",
            "D": "The number of variables in the dataset"
        },
        "answer": "B"
    },
    {
        "question": "Which visualization is most effective for showing a 'Part-to-Whole' relationship with only 2 or 3 categories?",
        "options": {
            "A": "Histogram",
            "B": "Pie Chart",
            "C": "Box Plot",
            "D": "Heat Map"
        },
        "answer": "B"
    },
    {
        "question": "A Histogram is used to visualize which of the following?",
        "options": {
            "A": "Categorical data ranking",
            "B": "The distribution of a single continuous variable",
            "C": "Geographical locations",
            "D": "Stock market trends"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Chart Junk'?",
        "options": {
            "A": "Unnecessary visual elements that distract from the data",
            "B": "Data that contains errors",
            "C": "A chart with too many data points",
            "D": "The legend of a graph"
        },
        "answer": "A"
    },
    {
        "question": "Which color scale is best for representing categories like 'Apple', 'Orange', and 'Banana'?",
        "options": {
            "A": "Sequential (Light to Dark)",
            "B": "Diverging (Two colors meeting in the middle)",
            "C": "Qualitative (Distinctly different colors)",
            "D": "Grayscale"
        },
        "answer": "C"
    },
    {
        "question": "What does a Box Plot (Box-and-Whisker) primarily show?",
        "options": {
            "A": "Time series data",
            "B": "The five-number summary: min, Q1, median, Q3, and max",
            "C": "Correlation coefficients",
            "D": "Network connections"
        },
        "answer": "B"
    },
    {
        "question": "Which chart is best suited for comparing values across different categories?",
        "options": {
            "A": "Bar Chart",
            "B": "Area Chart",
            "C": "Bubble Chart",
            "D": "Donut Chart"
        },
        "answer": "A"
    },
    {
        "question": "In a Heat Map, how is data usually represented?",
        "options": {
            "A": "Using varying heights of bars",
            "B": "Using colors to represent values in a matrix",
            "C": "Using lines of different thicknesses",
            "D": "Using 3D shapes"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is a common Pitfall in data visualization?",
        "options": {
            "A": "Truncating the Y-axis of a bar chart to exaggerate differences",
            "B": "Using 3D effects on 2D data",
            "C": "Using too many colors",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "What is the best chart for visualizing hierarchical data structure?",
        "options": {
            "A": "Stacked Bar Chart",
            "B": "Treemap",
            "C": "Waterfall Chart",
            "D": "Radar Chart"
        },
        "answer": "B"
    },
    {
        "question": "Which type of chart is often used to visualize the flow of data through a system?",
        "options": {
            "A": "Sankey Diagram",
            "B": "Choropleth Map",
            "C": "Funnel Chart",
            "D": "Pareto Chart"
        },
        "answer": "A"
    },
    {
        "question": "What is an 'Outlier' in a visualization?",
        "options": {
            "A": "The title of the chart",
            "B": "A data point that differs significantly from other observations",
            "C": "The line of best fit",
            "D": "A missing value"
        },
        "answer": "B"
    },
    {
        "question": "Which variable type is best represented on a Choropleth Map?",
        "options": {
            "A": "Individual customer names",
            "B": "Aggregated data by geographic regions (e.g., states or countries)",
            "C": "Daily temperature changes at one station",
            "D": "A list of product IDs"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Gestalt Principle' of Proximity in visualization?",
        "options": {
            "A": "Objects that are close to each other are perceived as a group",
            "B": "Objects that look alike are grouped",
            "C": "Objects in a line are perceived as continuous",
            "D": "Using bright colors to grab attention"
        },
        "answer": "A"
    },
    {
        "question": "Which chart is best for showing a distribution of data and identifying skewness?",
        "options": {
            "A": "Histogram",
            "B": "Pie Chart",
            "C": "Gantt Chart",
            "D": "Bullet Graph"
        },
        "answer": "A"
    },
    {
        "question": "In a Bubble Chart, what does the third variable usually represent?",
        "options": {
            "A": "The color of the bubble",
            "B": "The size (area) of the bubble",
            "C": "The shape of the bubble",
            "D": "The label of the bubble"
        },
        "answer": "B"
    },
    {
        "question": "When visualizing data for color-blind users, which color combination should be avoided?",
        "options": {
            "A": "Blue and Orange",
            "B": "Red and Green",
            "C": "Black and White",
            "D": "Yellow and Blue"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of a 'Legend' in a chart?",
        "options": {
            "A": "To provide the name of the author",
            "B": "To explain what the symbols, colors, or patterns represent",
            "C": "To list the raw data table",
            "D": "To show the date of creation"
        },
        "answer": "B"
    },
    {
        "question": "Which chart is best for showing the stages in a process and the dropout rate at each stage?",
        "options": {
            "A": "Radar Chart",
            "B": "Funnel Chart",
            "C": "Line Chart",
            "D": "Box Plot"
        },
        "answer": "B"
    },
    {
        "question": "What does a 'Stacked Bar Chart' allow you to do that a regular Bar Chart doesn't?",
        "options": {
            "A": "Show the total and the sub-components simultaneously",
            "B": "Show negative values more clearly",
            "C": "Compare two unrelated datasets",
            "D": "Visualize time series data better"
        },
        "answer": "A"
    },
    {
        "question": "Which chart type is commonly used in Project Management to show schedules?",
        "options": {
            "A": "Gantt Chart",
            "B": "Waterfall Chart",
            "C": "Bullet Chart",
            "D": "Area Chart"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Visual Encoding'?",
        "options": {
            "A": "Writing code to generate a chart",
            "B": "Mapping data values to visual properties like length, color, or position",
            "C": "Saving a chart as a PNG file",
            "D": "Encrypting data visualizations"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is a 'Preattentive Attribute'?",
        "options": {
            "A": "Color",
            "B": "Size",
            "C": "Orientation",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
"question": "Which visual channel is the most accurate for humans to perceive quantitative differences?",
"options": {
"A": "Area",
"B": "Color Saturation",
"C": "Position on a common scale",
"D": "Angle"
},
"answer": "C"
},
{
"question": "A 'Waterfall Chart' is most commonly used for what purpose?",
"options": {
"A": "Visualizing ocean currents",
"B": "Showing how an initial value is affected by intermediate positive or negative changes",
"C": "Comparing the heights of different waterfalls",
"D": "Tracking website traffic over 24 hours"
},
"answer": "B"
},
{
"question": "What is the primary danger of using 3D Pie Charts?",
"options": {
"A": "They take too long to load",
"B": "Perspective distortion makes slices in the front appear larger than they are",
"C": "They can only show 3 categories",
"D": "The colors become muted"
},
"answer": "B"
},
{
"question": "Which chart type is best for comparing performance against a target or benchmark?",
"options": {
"A": "Donut Chart",
"B": "Bullet Graph",
"C": "Line Chart",
"D": "Word Cloud"
},
"answer": "B"
},
{
"question": "What does 'Small Multiples' (Trellis Chart) refer to?",
"options": {
"A": "A chart with very small fonts",
"B": "A series of similar graphs with the same scale and axes for easy comparison",
"C": "A chart showing only small numbers",
"D": "A bar chart with many categories"
},
"answer": "B"
},
{
"question": "In a 'Radar Chart' (Spider Chart), what does each 'spoke' represent?",
"options": {
"A": "A point in time",
"B": "A different variable or category",
"C": "A different user",
"D": "The frequency of data"
},
"answer": "B"
},
{
"question": "Which type of map uses dots to represent the presence or quantity of a feature?",
"options": {
"A": "Choropleth Map",
"B": "Dot Density Map",
"C": "Heat Map",
"D": "Topographic Map"
},
"answer": "B"
},
{
"question": "When should you use a Logarithmic scale on an axis?",
"options": {
"A": "When the data contains negative values",
"B": "When the data covers several orders of magnitude (huge range)",
"C": "To make a flat line look steeper",
"D": "When you have fewer than 10 data points"
},
"answer": "B"
},
{
"question": "What is 'Brushing' in an interactive visualization?",
"options": {
"A": "Deleting old data",
"B": "Selecting a subset of data in one view to highlight it in others",
"C": "Changing the color palette",
"D": "Smoothing out lines in a graph"
},
"answer": "B"
},
{
"question": "Which chart type displays word frequency through size and color?",
"options": {
"A": "Histogram",
"B": "Word Cloud",
"C": "Bubble Chart",
"D": "Treemap"
},
"answer": "B"
},
{
"question": "What is a 'Candlestick Chart' primarily used for?",
"options": {
"A": "Visualizing temperature changes",
"B": "Financial analysis (stock price movements)",
"C": "Energy consumption tracking",
"D": "Demographic shifts"
},
"answer": "B"
},
{
"question": "Which 'Gestalt Principle' explains why we see a line of dots as a single path?",
"options": {
"A": "Similarity",
"B": "Continuity",
"C": "Closure",
"D": "Enclosure"
},
"answer": "B"
},
{
"question": "What is the 'Moire Effect' in data visualization?",
"options": {
"A": "A type of color palette",
"B": "Visual shimmering caused by repetitive patterns (like stripes on bars)",
"C": "A way to calculate averages",
"D": "The transition between two charts"
},
"answer": "B"
},
{
"question": "Which visualization would you use to show the correlation between three numerical variables?",
"options": {
"A": "Standard Scatter Plot",
"B": "Bubble Chart (X, Y, and Bubble Size)",
"C": "Stacked Bar Chart",
"D": "Pie Chart"
},
"answer": "B"
},
{
"question": "What is 'Exploratory Data Analysis' (EDA)?",
"options": {
"A": "Presenting a final report to a CEO",
"B": "Visualizing data to find patterns and anomalies before formal modeling",
"C": "Cleaning data in a SQL database",
"D": "Publishing data on the web"
},
"answer": "B"
},
{
"question": "A 'Streamgraph' is a variation of which chart type?",
"options": {
"A": "Bar Chart",
"B": "Stacked Area Chart",
"C": "Pie Chart",
"D": "Scatter Plot"
},
"answer": "B"
},
{
"question": "Which visual attribute is best for representing 'Ordinal' data (ordered categories)?",
"options": {
"A": "Random colors",
"B": "Color intensity or size",
"C": "Shapes",
"D": "Different line patterns"
},
"answer": "B"
},
{
"question": "What is the primary function of a 'Parallel Coordinates Plot'?",
"options": {
"A": "To map GPS coordinates",
"B": "To visualize high-dimensional (multivariate) data",
"C": "To show simple rankings",
"D": "To replace a pie chart"
},
"answer": "B"
},
{
"question": "In a 'Choropleth Map', why is it better to use rates (like density) rather than raw counts?",
"options": {
"A": "Counts are too hard to calculate",
"B": "Raw counts often just highlight population density rather than the variable of interest",
"C": "Rates use fewer colors",
"D": "It makes the map look more complex"
},
"answer": "B"
},
{
"question": "What is 'Anisometry' in a visualization?",
"options": {
"A": "Using too many fonts",
"B": "Using different scales for the X and Y axes",
"C": "Using only one color",
"D": "A type of interactive hover effect"
},
"answer": "B"
},
{
"question": "Which visualization is most useful for identifying data clusters?",
"options": {
"A": "Scatter Plot",
"B": "Bar Chart",
"C": "Line Graph",
"D": "Gantt Chart"
},
"answer": "A"
},
{
"question": "What is 'Information Density'?",
"options": {
"A": "The speed of the internet connection",
"B": "The amount of data displayed per unit of area",
"C": "The total number of rows in a dataset",
"D": "The size of a chart file in kilobytes"
},
"answer": "B"
},
{
"question": "Which chart type shows the cumulative effect of values over time?",
"options": {
"A": "Waterfall Chart",
"B": "Pareto Chart",
"C": "Area Chart",
"D": "Both A and C"
},
"answer": "D"
},
{
"question": "What does the 'Lie Factor' in visualization measure?",
"options": {
"A": "The number of mistakes in the data",
"B": "The ratio of the size of the effect shown in the graphic to the actual size of the effect in the data",
"C": "The time it takes for someone to understand a chart",
"D": "The number of colors used"
},
"answer": "B"
},
{
"question": "Which type of visualization uses 'Nodes' and 'Edges'?",
"options": {
"A": "Map",
"B": "Network Diagram",
"C": "Treemap",
"D": "Histogram"
},
"answer": "B"
},
{
"question": "What is 'Annotations' in the context of data storytelling?",
"options": {
"A": "The raw data values",
"B": "Text overlays that point out specific insights or context on a chart",
"C": "The software code used",
"D": "The legend of the chart"
},
"answer": "B"
},
{
"question": "Which chart is often criticized because it's difficult for people to accurately judge area vs. height/length?",
"options": {
"A": "Bar Chart",
"B": "Pie Chart",
"C": "Line Chart",
"D": "Column Chart"
},
"answer": "B"
},
{
"question": "What is a 'Slopegraph' used for?",
"options": {
"A": "Measuring the steepness of a hill",
"B": "Comparing changes in rank or value between two points in time across multiple categories",
"C": "Showing the distribution of a variable",
"D": "Visualizing 3D terrain"
},
"answer": "B"
},
{
"question": "Which 'Preattentive Attribute' describes the perceived thickness of a line?",
"options": {
"A": "Length",
"B": "Width",
"C": "Enclosure",
"D": "Intensity"
},
"answer": "B"
},
{
"question": "In data viz, what is 'Truthful Representation'?",
"options": {
"A": "Using the most expensive software",
"B": "Designing visuals that accurately reflect the underlying data without misleading the viewer",
"C": "Using as much data as possible",
"D": "Making the chart look beautiful"
},
"answer": "B"
},
{
"question": "What is 'Cognitive Load'?",
"options": {
"A": "The battery life of a laptop",
"B": "The amount of mental effort required to process information from a visualization",
"C": "The speed of a data query",
"D": "The number of people viewing a chart"
},
"answer": "B"
},
{
"question": "Which color palette is best for showing temperatures ranging from -50 to +50 degrees?",
"options": {
"A": "Sequential (Single color)",
"B": "Diverging (e.g., Blue to Red with White in the middle)",
"C": "Qualitative (Rainbow)",
"D": "Grayscale"
},
"answer": "B"
},
{
"question": "What is a 'Heat Map' in the context of website analysis?",
"options": {
"A": "A map showing where the server is located",
"B": "A visual showing where users click or move their mouse most frequently",
"C": "A chart showing server temperature",
"D": "A list of popular search terms"
},
"answer": "B"
},
{
"question": "Which chart type is best for showing frequency and cumulative percentage simultaneously?",
"options": {
"A": "Pareto Chart",
"B": "Histogram",
"C": "Pie Chart",
"D": "Scatter Plot"
},
"answer": "A"
},
{
"question": "What is 'Drill-Down' in an interactive dashboard?",
"options": {
"A": "Deleting data",
"B": "Moving from a high-level summary to more detailed data by clicking a visual element",
"C": "Rotating a 3D chart",
"D": "Filtering for only negative values"
},
"answer": "B"
},
{
"question": "What does a 'Violin Plot' combine?",
"options": {
"A": "A Pie chart and a Bar chart",
"B": "A Box Plot and a Kernel Density Plot",
"C": "A Line graph and a Map",
"D": "A Scatter plot and a Word cloud"
},
"answer": "B"
},
{
"question": "Which of these is the 'Baseline' of a chart?",
"options": {
"A": "The title",
"B": "The starting point for the axes (usually 0)",
"C": "The most recent data point",
"D": "The source of the data"
},
"answer": "B"
},
{
"question": "What is 'Contextual Inquiry' in visualization design?",
"options": {
"A": "Running a SQL script",
"B": "Understanding the environment and needs of the user who will use the visualization",
"C": "Checking the data for nulls",
"D": "Asking a computer for the answer"
},
"answer": "B"
},
{
"question": "A 'Dumbbell Plot' (DNA chart) is used for what?",
"options": {
"A": "Biological research only",
"B": "Showing the change or gap between two points (e.g., Year 1 vs Year 2)",
"C": "Comparing weights in a gym",
"D": "Visualizing stock volume"
},
"answer": "B"
},
{
"question": "What is 'Explanatory Data Visualization'?",
"options": {
"A": "Exploring the data for the first time",
"B": "Creating visuals to communicate a specific insight or story to an audience",
"C": "Writing a long caption",
"D": "Using a dictionary to define data terms"
},
"answer": "B"
},
{
"question": "Which chart is often used to show a 'Process Flow' or 'Value Stream'?",
"options": {
"A": "Flowchart",
"B": "Sankey Diagram",
"C": "Both A and B",
"D": "None of the above"
},
"answer": "C"
},
{
"question": "In a 'Sunburst Chart', what do the outer rings represent?",
"options": {
"A": "Lower levels in a hierarchy",
"B": "Older data points",
"C": "The most important data",
"D": "Errors in the data"
},
"answer": "A"
},
{
"question": "What is 'Interaction Latency'?",
"options": {
"A": "The delay between a user action and the visual update",
"B": "How long a user looks at a chart",
"C": "The time it takes to draw a chart",
"D": "The interval between data updates"
},
"answer": "A"
},
{
"question": "Which visual mark is best for representing a specific data point in 2D space?",
"options": {
"A": "A line",
"B": "A dot (point)",
"C": "An area",
"D": "A volume"
},
"answer": "B"
},
{
"question": "What is the 'Golden Ratio' sometimes used for in design?",
"options": {
"A": "Calculating the average",
"B": "Determining aesthetically pleasing proportions for layouts",
"C": "Counting data points",
"D": "Choosing colors"
},
"answer": "B"
},
{
"question": "Which tool is best for 'Live' data visualization in a business setting?",
"options": {
"A": "Power BI / Tableau",
"B": "Adobe Photoshop",
"C": "Microsoft Word",
"D": "NotePad"
},
"answer": "A"
},
{
"question": "What is 'Data Humanism'?",
"options": {
"A": "Giving data human names",
"B": "Designing visualizations that prioritize human experience and narrative over raw cold numbers",
"C": "A robot that reads charts",
"D": "The study of human populations"
},
"answer": "B"
},
{
"question": "Which axis usually represents the Independent variable?",
"options": {
"A": "Y-axis (Vertical)",
"B": "X-axis (Horizontal)",
"C": "Z-axis",
"D": "The Legend"
},
"answer": "B"
},
{
"question": "Which axis usually represents the Dependent (Measured) variable?",
"options": {
"A": "X-axis",
"B": "Y-axis",
"C": "The Title",
"D": "The Gridlines"
},
"answer": "B"
},
{
"question": "What is 'Tufte’s Law' of Graphical Excellence?",
"options": {
"A": "Use as many colors as possible",
"B": "Give the viewer the greatest number of ideas in the shortest time with the least ink",
"C": "Always use 3D charts",
"D": "A chart should never have text"
},
"answer": "B"
},
{
"question": "Which Python library is considered the foundational 'grandfather' of data visualization?",
"options": {
"A": "Seaborn",
"B": "Matplotlib",
"C": "Plotly",
"D": "Bokeh"
},
"answer": "B"
},
{
"question": "In Matplotlib, which function is used to create a simple line plot?",
"options": {
"A": "plt.show()",
"B": "plt.plot()",
"C": "plt.line()",
"D": "plt.draw()"
},
"answer": "B"
},
{
"question": "Which Python library is built on top of Matplotlib and provides a high-level interface for drawing attractive statistical graphics?",
"options": {
"A": "Pandas",
"B": "Seaborn",
"C": "D3.js",
"D": "ggplot"
},
"answer": "B"
},
{
"question": "What is the primary advantage of the Plotly library?",
"options": {
"A": "It only produces black and white charts",
"B": "It creates interactive, web-ready visualizations easily",
"C": "It is the oldest library available",
"D": "It doesn't require any data"
},
"answer": "B"
},
{
"question": "In Tableau, what is the difference between 'Dimensions' and 'Measures'?",
"options": {
"A": "Dimensions are qualitative (categories); Measures are quantitative (numbers)",
"B": "Measures are qualitative; Dimensions are quantitative",
"C": "Dimensions are for time; Measures are for space",
"D": "There is no difference"
},
"answer": "A"
},
{
"question": "In Power BI, what does 'DAX' stand for?",
"options": {
"A": "Data Analysis Expressions",
"B": "Digital Analytics X-platform",
"C": "Data Archive Extension",
"D": "Direct Access X-ray"
},
"answer": "A"
},
{
"question": "Which JavaScript library is most famous for creating custom, complex, data-driven documents for the web?",
"options": {
"A": "React",
"B": "D3.js",
"C": "jQuery",
"D": "Angular"
},
"answer": "B"
},
{
"question": "In D3.js, what does the 'D3' stand for?",
"options": {
"A": "Data-Driven Documents",
"B": "Digital Data Display",
"C": "Dynamic Data Designs",
"D": "Distributed Data Diagrams"
},
"answer": "A"
},
{
"question": "Which R library is based on the 'Grammar of Graphics'?",
"options": {
"A": "Lattice",
"B": "ggplot2",
"C": "Base R",
"D": "Plotly"
},
"answer": "B"
},
{
"question": "What is the purpose of 'Data Scaling' before visualization?",
"options": {
"A": "To change the colors of the chart",
"B": "To ensure variables with different units or ranges can be compared effectively",
"C": "To delete small data points",
"D": "To make the file size larger"
},
"answer": "B"
},
{
"question": "What is a 'Dashboard' in the context of data visualization?",
"options": {
"A": "A single chart",
"B": "A collection of several visualizations and KPIs in one view for monitoring data",
"C": "A table of raw numbers",
"D": "The engine of a car"
},
"answer": "B"
},
{
"question": "Which visualization would be best to show the relationship between 'Height' and 'Weight' across a population?",
"options": {
"A": "Bar Chart",
"B": "Scatter Plot",
"C": "Pie Chart",
"D": "Gantt Chart"
},
"answer": "B"
},
{
"question": "What does 'Tidy Data' mean?",
"options": {
"A": "Data that is sorted alphabetically",
"B": "A standard format where each variable is a column and each observation is a row",
"C": "Data that has no outliers",
"D": "Data saved in a PDF"
},
"answer": "B"
},
{
"question": "Which Matplotlib function is used to save a chart as a file?",
"options": {
"A": "plt.save()",
"B": "plt.savefig()",
"C": "plt.export()",
"D": "plt.store()"
},
"answer": "B"
},
{
"question": "What is the function of a 'Pivot Table' in visualization prep?",
"options": {
"A": "To rotate a 3D chart",
"B": "To summarize and aggregate large datasets into a more manageable form",
"C": "To create a 3D effect",
"D": "To delete duplicate rows"
},
"answer": "B"
},
{
"question": "Which seaborn function creates a matrix of scatter plots for all numerical variables in a dataset?",
"options": {
"A": "sns.scatter_matrix()",
"B": "sns.pairplot()",
"C": "sns.allplot()",
"D": "sns.heatmap()"
},
"answer": "B"
},
{
"question": "What is the purpose of 'Normalization' in data preparation?",
"options": {
"A": "To make data look 'normal' on a graph",
"B": "Adjusting values measured on different scales to a common scale (e.g., 0 to 1)",
"C": "Removing all negative numbers",
"D": "Changing categories to numbers"
},
"answer": "B"
},
{
"question": "In Tableau, what is a 'Sheet'?",
"options": {
"A": "A single visualization or chart",
"B": "A combination of charts",
"C": "A story point",
"D": "A data source connection"
},
"answer": "A"
},
{
"question": "What is 'Overplotting'?",
"options": {
"A": "Plotting too much data in a small area, making it impossible to see individual points",
"B": "Using too many colors",
"C": "Making a chart too large",
"D": "Plotting the same data twice"
},
"answer": "A"
},
{
"question": "Which technique helps solve overplotting in a scatter plot?",
"options": {
"A": "Using transparency (alpha)",
"B": "Jittering (adding tiny random noise to positions)",
"C": "Binning data into a hexbin plot",
"D": "All of the above"
},
"answer": "D"
},
{
"question": "In SVG (Scalable Vector Graphics), what does 'path' define?",
"options": {
"A": "The location of a file",
"B": "A complex shape consisting of lines and curves",
"C": "The font style",
"D": "The color of a dot"
},
"answer": "B"
},
{
"question": "What is 'Canvas' in HTML5 visualization?",
"options": {
"A": "A script that runs in the background",
"B": "A pixel-based drawing area used for rendering graphics on the fly",
"C": "A type of database",
"D": "A style sheet"
},
"answer": "B"
},
{
"question": "Which chart is often used to show 'Survival Rates' over time in medical or customer research?",
"options": {
"A": "Kaplan-Meier Plot",
"B": "Pie Chart",
"C": "Heat Map",
"D": "Box Plot"
},
"answer": "A"
},
{
"question": "What is the 'SVG' format benefit over 'PNG' for web charts?",
"options": {
"A": "SVG can be scaled to any size without losing quality",
"B": "SVG is always a smaller file size",
"C": "PNG is interactive",
"D": "There is no benefit"
},
"answer": "A"
},
{
"question": "In Seaborn, what does the 'hue' parameter do?",
"options": {
"A": "Changes the brightness of the chart",
"B": "Adds a categorical variable to the plot using color encoding",
"C": "Rotates the labels",
"D": "Sets the background style"
},
"answer": "B"
},
{
"question": "Which tool would you use to create a simple 'Map' visualization without writing code?",
"options": {
"A": "Datawrapper",
"B": "Google My Maps",
"C": "Tableau Public",
"D": "All of the above"
},
"answer": "D"
},
{
"question": "What is a 'Choropleth'?",
"options": {
"A": "A type of dinosaur",
"B": "A map where areas are shaded in proportion to a statistical variable",
"C": "A chart showing musical notes",
"D": "A line graph for stock prices"
},
"answer": "B"
},
{
"question": "What is 'Missing Value Imputation'?",
"options": {
"A": "Deleting rows with missing data",
"B": "Filling in missing data points with estimated values (like the mean or median)",
"C": "Ignoring missing data in the chart",
"D": "Highlighting missing data in red"
},
"answer": "B"
},
{
"question": "Which of these is a categorical data type?",
"options": {
"A": "Price",
"B": "Age",
"C": "Gender",
"D": "Weight"
},
"answer": "C"
},
{
"question": "Which of these is a continuous numerical data type?",
"options": {
"A": "Car Model",
"B": "Temperature",
"C": "Zip Code",
"D": "User ID"
},
"answer": "B"
},
{
"question": "What is the purpose of 'Facetting'?",
"options": {
"A": "To add borders to a chart",
"B": "Splitting data into multiple sub-plots based on a categorical variable",
"C": "Changing the font size",
"D": "Using 3D effects"
},
"answer": "B"
},
{
"question": "In D3.js, which method is used to bind data to DOM elements?",
"options": {
"A": ".link()",
"B": ".data()",
"C": ".bind()",
"D": ".attach()"
},
"answer": "B"
},
{
"question": "What is 'SVG Grouping' (<g> tag) used for?",
"options": {
"A": "To group multiple SVG elements together for collective transformation or styling",
"B": "To create a group chat",
"C": "To group data in a database",
"D": "To sort the legend"
},
"answer": "A"
},
{
"question": "In Matplotlib, what does 'plt.subplots()' return?",
"options": {
"A": "A single chart",
"B": "A figure object and an array of axes objects",
"C": "A list of colors",
"D": "A CSV file"
},
"answer": "B"
},
{
"question": "What is the 'Bokeh' library used for in Python?",
"options": {
"A": "Static PDF reports",
"B": "Interactive, browser-based visualizations for large datasets",
"C": "Machine learning modeling",
"D": "Image editing"
},
"answer": "B"
},
{
"question": "Which library is better for 'Exploratory' (fast) visualization in Python?",
"options": {
"A": "D3.js",
"B": "Seaborn",
"C": "Matplotlib",
"D": "JavaScript"
},
"answer": "B"
},
{
"question": "What is a 'Tooltip' in an interactive chart?",
"options": {
"A": "A physical tool used to draw",
"B": "A small informational box that appears when a user hovers over a data point",
"C": "The tip of a line graph",
"D": "A programming hint"
},
"answer": "B"
},
{
"question": "What does 'Exploding' a pie chart slice mean?",
"options": {
"A": "Deleting the slice",
"B": "Pulling a slice slightly away from the center to highlight it",
"C": "Turning the pie chart into a bar chart",
"D": "Removing the colors"
},
"answer": "B"
},
{
"question": "In Power BI, what is the 'Power Query' editor used for?",
"options": {
"A": "Writing reports",
"B": "Data cleaning, transformation, and ETL (Extract, Transform, Load)",
"C": "Presenting to an audience",
"D": "Setting up user passwords"
},
"answer": "B"
},
{
"question": "What is 'Color Blind Friendly' design important?",
"options": {
"A": "Because about 8% of men have some form of color vision deficiency",
"B": "Because it uses fewer colors",
"C": "Because it makes charts look professional",
"D": "Because it is required by the computer"
},
"answer": "A"
},
{
"question": "Which chart type would you use to show the distribution of 'Exam Scores'?",
"options": {
"A": "Line Chart",
"B": "Histogram",
"C": "Sankey Diagram",
"D": "Word Cloud"
},
"answer": "B"
},
{
"question": "What is 'Aggregation' in data visualization?",
"options": {
"A": "Separating data into individual rows",
"B": "Summarizing data points into a single value (e.g., Sum, Average, Count)",
"C": "Deleting data",
"D": "Naming the data columns"
},
"answer": "B"
},
{
"question": "In ggplot2 (R), what does '+' signify?",
"options": {
"A": "Addition of two numbers",
"B": "Adding layers (geoms, scales, themes) to the plot",
"C": "A mathematical formula",
"D": "The end of the code"
},
"answer": "B"
},
{
"question": "What is 'Over-Aggregation'?",
"options": {
"A": "Grouping data so much that important patterns or outliers are hidden",
"B": "Using too many charts",
"C": "Using too many data points",
"D": "Adding too many titles"
},
"answer": "A"
},
{
"question": "What is a 'Diverging' color palette?",
"options": {
"A": "A single color getting darker",
"B": "Two contrasting colors that meet in the middle at a neutral color",
"C": "A rainbow of colors",
"D": "Black and white only"
},
"answer": "B"
},
{
"question": "Which chart is best for visualizing 'Correlation' between multiple pairs of variables simultaneously?",
"options": {
"A": "Correlogram (Heatmap of correlations)",
"B": "Bar Chart",
"C": "Pie Chart",
"D": "Waterfall Chart"
},
"answer": "A"
},
{
"question": "What is 'Data Granularity'?",
"options": {
"A": "The color of the data points",
"B": "The level of detail represented in the data (e.g., Daily vs. Monthly data)",
"C": "The size of the database",
"D": "The number of users"
},
"answer": "B"
},
{
"question": "Which tool is best for creating 'Hand-drawn' style data visualizations?",
"options": {
"A": "RoughViz (JS/Python)",
"B": "Tableau",
"C": "Excel",
"D": "Power BI"
},
"answer": "A"
},
{
"question": "What is 'Dynamic' data visualization?",
"options": {
"A": "A chart that never changes",
"B": "A visualization that updates automatically as new data comes in",
"C": "A 3D chart",
"D": "A chart with moving parts"
},
"answer": "B"
},
{
"question": "Which Python library is specifically designed for 'Geographical' data visualization?",
"options": {
"A": "Geopandas / Folium",
"B": "NumPy",
"C": "Requests",
"D": "Scikit-learn"
},
"answer": "A"
},
{
"question": "What is the 'F-Pattern' in dashboard design?",
"options": {
"A": "A type of statistical distribution",
"B": "The way users tend to scan a screen (top to bottom, left to right)",
"C": "A method for filtering data",
"D": "A way to format numbers"
},
"answer": "B"
},
{
"question": "Which of these is considered an 'Ethical' practice in data visualization?",
"options": {
"A": "Starting the Y-axis at zero for bar charts to avoid misrepresenting magnitude",
"B": "Cherry-picking only data that supports your argument",
"C": "Using 'spaghetti charts' to hide negative trends",
"D": "Changing the scale mid-axis without notice"
},
"answer": "A"
},
{
"question": "What is 'Data Storytelling'?",
"options": {
"A": "Writing a fictional story about numbers",
"B": "The practice of building a narrative around a set of data and its accompanying visualizations",
"C": "Reading the data out loud",
"D": "Converting data into a spreadsheet"
},
"answer": "B"
},
{
"question": "In dashboard design, what is a 'KPI'?",
"options": {
"A": "Key Performance Indicator",
"B": "Kernel Plot Interface",
"C": "Knowledge Processing Index",
"D": "Key Point Information"
},
"answer": "A"
},
{
"question": "Why is the use of 'Rainbow' color scales often discouraged for continuous data?",
"options": {
"A": "They are too expensive to print",
"B": "The transitions between colors (like yellow to green) are not perceptually uniform",
"C": "Computers cannot render them accurately",
"D": "They can only be used for children's data"
},
"answer": "B"
},
{
"question": "What is 'Tufte's Lie Factor' formula?",
"options": {
"A": "Total Data / Total Ink",
"B": "Size of effect shown in graphic / Size of effect in data",
"C": "Number of colors / Number of variables",
"D": "Chart height / Chart width"
},
"answer": "B"
},
{
"question": "Which visualization is best for showing 'Flow' and 'Resource Allocation'?",
"options": {
"A": "Sankey Diagram",
"B": "Pie Chart",
"C": "Box Plot",
"D": "Scatter Plot"
},
"answer": "A"
},
{
"question": "What does 'Cognitive Load' refer to in the context of a dashboard?",
"options": {
"A": "The processing power of the computer",
"B": "The total amount of mental effort being used in the working memory",
"C": "The number of users logged in",
"D": "The size of the database"
},
"answer": "B"
},
{
"question": "What is 'Redundancy' in visual encoding?",
"options": {
"A": "Repeating the same chart twice",
"B": "Using two different visual channels (e.g., color AND shape) to represent the same variable",
"C": "Having too many backups of data",
"D": "Deleting data that isn't needed"
},
"answer": "B"
},
{
"question": "Which of these is a 'Non-Data' ink element?",
"options": {
"A": "The bars in a bar chart",
"B": "The dots in a scatter plot",
"C": "Gridlines and decorative borders",
"D": "The trend line in a regression"
},
"answer": "C"
},
{
"question": "What is a 'Metric'?",
"options": {
"A": "A system of measurement",
"B": "A quantifiable measure that is used to track and assess the status of a specific process",
"C": "A type of chart",
"D": "A color palette"
},
"answer": "B"
},
{
"question": "In a dashboard, what is the 'High-Level' view?",
"options": {
"A": "The data from the previous year",
"B": "An executive summary showing overall performance at a glance",
"C": "The view from a drone",
"D": "A chart showing the most expensive items"
},
"answer": "B"
},
{
"question": "What does the 'Gestalt Principle of Closure' suggest?",
"options": {
"A": "Users will ignore incomplete charts",
"B": "The brain tends to perceive incomplete shapes as whole",
"C": "Every chart needs a border",
"D": "The chart should be closed after use"
},
"answer": "B"
},
{
"question": "Which visualization is most suitable for showing 'Interconnectedness' and 'Relationships' between people or entities?",
"options": {
"A": "Network Graph",
"B": "Histogram",
"C": "Area Chart",
"D": "Choropleth Map"
},
"answer": "A"
},
{
"question": "What is 'White Space' (Negative Space) in design?",
"options": {
"A": "A mistake where data is missing",
"B": "The empty space between elements used to improve readability and focus",
"C": "The color of the bars",
"D": "The area where the legend is placed"
},
"answer": "B"
},
{
"question": "Which chart type is best for showing 'Bottlenecks' in a supply chain?",
"options": {
"A": "Funnel Chart",
"B": "Pie Chart",
"C": "Radar Chart",
"D": "Donut Chart"
},
"answer": "A"
},
{
"question": "What is 'Moire Distortion'?",
"options": {
"A": "A French design style",
"B": "Visual vibration caused by using too many tight lines or patterns in a chart",
"C": "The scaling of an axis",
"D": "A type of data error"
},
"answer": "B"
},
{
"question": "Which color is traditionally used to represent 'Danger' or 'Negative' values in Western culture?",
"options": {
"A": "Blue",
"B": "Red",
"C": "Green",
"D": "Yellow"
},
"answer": "B"
},
{
"question": "What is 'Sequential' color mapping?",
"options": {
"A": "A range of distinct colors",
"B": "A variation of a single hue from light to dark to show increasing magnitude",
"C": "A random selection of colors",
"D": "Only black and white"
},
"answer": "B"
},
{
"question": "What is the '80/20 Rule' (Pareto Principle) often visualized with?",
"options": {
"A": "Pareto Chart",
"B": "Bubble Chart",
"C": "Line Graph",
"D": "Treemap"
},
"answer": "A"
},
{
"question": "Which visual attribute is least effective for showing precise numerical values?",
"options": {
"A": "Length",
"B": "Color Hue",
"C": "Position",
"D": "Slope"
},
"answer": "B"
},
{
"question": "What is a 'Sparkline'?",
"options": {
"A": "A very large line graph",
"B": "A small, simple line graph without axes, drawn without much detail, intended to show a trend within text",
"C": "A line that flashes on the screen",
"D": "A chart showing electrical sparks"
},
"answer": "B"
},
{
"question": "What does 'Interactivity' add to a visualization?",
"options": {
"A": "It makes it harder to understand",
"B": "It allows users to explore the data at their own pace and find specific answers",
"C": "It reduces the amount of data needed",
"D": "It changes the raw data in the database"
},
"answer": "B"
},
{
"question": "Which principle suggests that the most important information should be at the 'top-left' of a dashboard?",
"options": {
"A": "Rule of Thirds",
"B": "Visual Hierarchy",
"C": "Color Theory",
"D": "Data Density"
},
"answer": "B"
},
{
"question": "What is the 'McKinsey' style of chart design known for?",
"options": {
"A": "Using many bright colors",
"B": "Clear, professional, and insight-driven charts with a strong focus on titles",
"C": "3D graphics",
"D": "Hand-drawn elements"
},
"answer": "B"
},
{
"question": "What is 'Apophenia' in data analysis?",
"options": {
"A": "The fear of data",
"B": "The tendency to perceive patterns or meaning where none exists",
"C": "A type of chart",
"D": "The process of cleaning data"
},
"answer": "B"
},
{
"question": "Which visualization is most effective for 'Internal' comparison of 20+ categories?",
"options": {
"A": "Horizontal Bar Chart",
"B": "Vertical Bar Chart",
"C": "Pie Chart",
"D": "Radar Chart"
},
"answer": "A"
},
{
"question": "Why use 'Horizontal' bars instead of 'Vertical' bars?",
"options": {
"A": "They look cooler",
"B": "They provide more space for long category labels",
"C": "They are faster to render",
"D": "They use less ink"
},
"answer": "B"
},
{
"question": "What is 'Pre-attentive Processing'?",
"options": {
"A": "Studying before a test",
"B": "The subconscious accumulation of information from the environment before focused attention",
"C": "Cleaning the data",
"D": "Closing the browser"
},
"answer": "B"
},
{
"question": "Which attribute can be used to distinguish 'Outliers' instantly?",
"options": {
"A": "Size",
"B": "Color",
"C": "Shape",
"D": "All of the above"
},
"answer": "D"
},
{
"question": "In the context of 'Color Theory', what is 'Saturation'?",
"options": {
"A": "The name of a color",
"B": "The intensity or purity of a color",
"C": "The brightness of a color",
"D": "The mixing of two colors"
},
"answer": "B"
},
{
"question": "What is 'Double Encoding'?",
"options": {
"A": "Writing code twice",
"B": "Using two visual cues (like color and height) to represent one data point",
"C": "Encrypting the chart",
"D": "Using two different datasets"
},
"answer": "B"
},
{
"question": "What is the 'Visual Variable' used in a Bubble chart to represent the value?",
"options": {
"A": "Radius",
"B": "Area",
"C": "Circumference",
"D": "Diameter"
},
"answer": "B"
},
{
"question": "Why is 'Area' used instead of 'Radius' in bubble charts to represent value?",
"options": {
"A": "Radius is too hard to calculate",
"B": "Humans perceive the area of a circle more accurately than the radius relative to magnitude",
"C": "Area uses more color",
"D": "It is a standard rule with no reason"
},
"answer": "B"
},
{
"question": "What is a 'Metric Map'?",
"options": {
"A": "A map of the metric system",
"B": "A map that uses symbols (like circles) of varying sizes to represent data",
"C": "A topographic map",
"D": "A world map"
},
"answer": "B"
},
{
"question": "What is the primary goal of 'Business Intelligence' (BI)?",
"options": {
"A": "To sell data",
"B": "To transform raw data into actionable insights for business decision-making",
"C": "To write code",
"D": "To build computers"
},
"answer": "B"
},
{
"question": "Which of these is a common 'Dashboard' layout strategy?",
"options": {
"A": "The inverted pyramid (most important on top)",
"B": "The random layout",
"C": "The bottom-up approach",
"D": "The single-chart layout"
},
"answer": "A"
},
{
"question": "What is 'Self-Service BI'?",
"options": {
"A": "Users buying their own software",
"B": "Allowing non-technical users to create their own reports and visualizations",
"C": "A robot that builds charts",
"D": "An automated email report"
},
"answer": "B"
},
{
"question": "In 'Color Theory', what is 'Value'?",
"options": {
"A": "The price of the color",
"B": "The lightness or darkness of a color",
"C": "The name of the color",
"D": "The data represented"
},
"answer": "B"
},
{
"question": "What is 'Achromatic'?",
"options": {
"A": "A color palette with many colors",
"B": "A color scheme without color (Grayscale/Black and White)",
"C": "A 3D chart",
"D": "A type of interactive map"
},
"answer": "B"
},
{
"question": "What is 'Over-Indexing'?",
"options": {
"A": "Using too many charts",
"B": "When a specific group is over-represented in the visualization",
"C": "Sorting a list too many times",
"D": "A database error"
},
"answer": "B"
},
{
"question": "Which visualization is best for showing 'Hierarchical' part-to-whole relationships?",
"options": {
"A": "Pie Chart",
"B": "Treemap",
"C": "Scatter Plot",
"D": "Bar Chart"
},
"answer": "B"
},
{
"question": "What is 'Faceted Search' in a dashboard?",
"options": {
"A": "Searching for a specific face",
"B": "Filtering data by multiple independent dimensions or attributes",
"C": "A type of 3D search",
"D": "Searching the database directly"
},
"answer": "B"
},
{
"question": "What is a 'Polar Area' chart (Coxcomb)?",
"options": {
"A": "A chart of the North Pole",
"B": "A circular chart where the distance of each segment from the center is proportional to the value",
"C": "A type of bar chart",
"D": "A map of the magnetic field"
},
"answer": "B"
},
{
"question": "Who is credited with creating the first 'Polar Area' chart?",
"options": {
"A": "Isaac Newton",
"B": "Florence Nightingale",
"C": "Edward Tufte",
"D": "William Playfair"
},
"answer": "B"
},
{
"question": "What is 'Visual Saliency'?",
"options": {
"A": "The color of the ocean",
"B": "The distinct subjective perceptual quality which makes some items stand out from their neighbors",
"C": "The size of the chart",
"D": "The font style"
},
"answer": "B"
},
{
"question": "What is the 'Visual Narrative'?",
"options": {
"A": "The text in a chart",
"B": "The story told through the sequence and arrangement of visuals",
"C": "A movie about data",
"D": "The code used to draw"
},
"answer": "B"
},
{
"question": "What is 'Data Provenance'?",
"options": {
"A": "The location where the data is stored",
"B": "The history of data, including its origin and transformations over time",
"C": "The color of the data",
"D": "The future of data"
},
"answer": "B"
},
{
"question": "In 'Typography', what is 'Kerning'?",
"options": {
"A": "The color of the text",
"B": "Adjusting the space between individual characters",
"C": "The size of the font",
"D": "The style of the font"
},
"answer": "B"
},
{
"question": "What is the primary goal of 'Information Visualization'?",
"options": {
"A": "To make art",
"B": "To amplify cognition using visual representations of abstract data",
"C": "To store information",
"D": "To hide information"
},
"answer": "B"
},

{
"question": "What is 'Scrollytelling' in web-based data visualization?",
"options": {
"A": "A chart that scrolls horizontally",
"B": "A narrative technique where visual elements change or animate as the user scrolls down the page",
"C": "A robot that reads data out loud",
"D": "A way to delete data by scrolling"
},
"answer": "B"
},
{
"question": "What is 'Immersive Analytics'?",
"options": {
"A": "Using VR and AR to explore and visualize data in 3D space",
"B": "Reading a data report in a quiet room",
"C": "Using a very large monitor",
"D": "Visualizing data underwater"
},
"answer": "A"
},
{
"question": "Which term describes a visualization that simplifies complex data into a 'binary' or 'status' view (e.g., Green/Red)?",
"options": {
"A": "Indicator",
"B": "Scorecard",
"C": "Stoplight Chart",
"D": "All of the above"
},
"answer": "D"
},
{
"question": "What is 'Data Sonification'?",
"options": {
"A": "Printing data on paper",
"B": "Representing data through sound or music",
"C": "Measuring the volume of a speaker",
"D": "A type of chart color"
},
"answer": "B"
},
{
"question": "In dashboarding, what is 'Over-Aggregation Bias'?",
"options": {
"A": "Using too many charts on one page",
"B": "Assuming that a trend seen in a large group applies to every subgroup or individual",
"C": "The fear of big data",
"D": "A slow database connection"
},
"answer": "B"
},
{
"question": "What is the 'Rule of Thirds' in visual layout?",
"options": {
"A": "Only use 3 colors",
"B": "Dividing an image into 9 equal parts to place important elements along lines or at intersections",
"C": "Updating data every 3 hours",
"D": "Having 3 charts per row"
},
"answer": "B"
},
{
"question": "Which of these is a 'Non-Linear' scale used in visualization?",
"options": {
"A": "Linear Scale",
"B": "Logarithmic Scale",
"C": "Categorical Scale",
"D": "Ordinal Scale"
},
"answer": "B"
},
{
"question": "What is 'Responsive Design' in data visualization?",
"options": {
"A": "A chart that responds to voice commands",
"B": "A visualization that automatically adjusts its layout and size for different screen sizes (mobile vs. desktop)",
"C": "A chart that updates in real-time",
"D": "A chart that asks the user questions"
},
"answer": "B"
},
{
"question": "Which visualization is best for showing 'Uncertainty' or 'Confidence Intervals'?",
"options": {
"A": "Line chart with shaded Error Bands",
"B": "Standard Bar Chart",
"C": "Pie Chart",
"D": "Word Cloud"
},
"answer": "A"
},
{
"question": "What is 'Visual Literacy'?",
"options": {
"A": "The ability to read a book",
"B": "The ability to interpret, negotiate, and make meaning from information presented in the form of an image",
"C": "The ability to write code",
"D": "The number of charts a person can draw"
},
"answer": "B"
},
{
"question": "In 'Color Theory', what are 'Complementary Colors'?",
"options": {
"A": "Colors that are similar to each other",
"B": "Colors that are opposite each other on the color wheel",
"C": "Colors that are only used in the legend",
"D": "Black and White"
},
"answer": "B"
},
{
"question": "What is a 'Circular Packing' diagram?",
"options": {
"A": "A variation of a Treemap using nested circles to show hierarchy",
"B": "A chart showing the earth's orbit",
"C": "A map of a warehouse",
"D": "A type of pie chart"
},
"answer": "A"
},
{
"question": "What is the primary goal of the 'User Experience' (UX) in dashboard design?",
"options": {
"A": "To make the dashboard pretty",
"B": "To ensure the user can find the information they need with minimal effort and frustration",
"C": "To show as much data as possible",
"D": "To use the latest technology"
},
"answer": "B"
},
{
"question": "What is 'Data Democratization'?",
"options": {
"A": "Voting on data",
"B": "The process of making data accessible to non-technical users within an organization",
"C": "A type of government",
"D": "Sharing data on social media"
},
"answer": "B"
},
{
"question": "Which chart type is best for showing 'Multi-variate' data where variables have different units?",
"options": {
"A": "Parallel Coordinates Plot",
"B": "Stacked Bar Chart",
"C": "Pie Chart",
"D": "Line Chart"
},
"answer": "A"
},
{
"question": "What is 'Brushing and Linking'?",
"options": {
"A": "Cleaning the data links",
"B": "An interactive technique where selecting data in one plot automatically highlights it in other related plots",
"C": "A way to format text",
"D": "A database connection method"
},
"answer": "B"
},
{
"question": "What is 'Tufte’s Data-Ink Ratio' goal?",
"options": {
"A": "To maximize the ratio (use more ink for data, less for decoration)",
"B": "To minimize the ratio",
"C": "To have an equal amount of ink and data",
"D": "To use only one color of ink"
},
"answer": "A"
},
{
"question": "Which color is best for representing 'Neutral' or 'Middle' values in a diverging scale?",
"options": {
"A": "Red",
"B": "Gray or White",
"C": "Neon Green",
"D": "Black"
},
"answer": "B"
},
{
"question": "What is a 'Pictogram'?",
"options": {
"A": "A chart showing a picture of a gram",
"B": "A chart that uses icons or small images to represent data values",
"C": "A type of camera",
"D": "A social media post"
},
"answer": "B"
},
{
"question": "What is 'Visual Saliency' intended to do?",
"options": {
"A": "Hide important data",
"B": "Guide the viewer's attention to the most important parts of the visualization",
"C": "Make the chart look symmetrical",
"D": "Reduce the file size"
},
"answer": "B"
},
{
"question": "What is a 'Hexbin' plot used for?",
"options": {
"A": "Showing data from 6 different countries",
"B": "Handling overplotting in scatter plots by binning points into hexagonal areas",
"C": "Visualizing honey production",
"D": "A 3D bar chart"
},
"answer": "B"
},
{
"question": "What is 'Explorable Explanation'?",
"options": {
"A": "A long text document",
"B": "A combination of text and interactive visualizations that allows users to 'play' with data to learn a concept",
"C": "A dictionary for data terms",
"D": "A video of a data scientist"
},
"answer": "B"
},
{
"question": "In 'Data Storytelling', what is the 'Conflict'?",
"options": {
"A": "A bug in the code",
"B": "The business problem or challenge revealed by the data that needs to be solved",
"C": "An argument between two analysts",
"D": "Two charts that show different things"
},
"answer": "B"
},
{
"question": "Which visual channel is better for 'Categorical' data than for 'Quantitative' data?",
"options": {
"A": "Length",
"B": "Shape",
"C": "Position",
"D": "Angle"
},
"answer": "B"
},
{
"question": "What is the primary benefit of 'Small Multiples'?",
"options": {
"A": "It saves space",
"B": "It allows for easy comparison of trends across different categories by using the same scale/axes",
"C": "It is easier to print",
"D": "It uses more colors"
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
    skill = "datavisulization"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
