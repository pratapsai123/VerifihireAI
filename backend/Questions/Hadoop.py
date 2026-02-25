from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
    {
        "question": "Who are the original creators of Apache Hadoop?",
        "options": {
            "A": "James Gosling and Mike Sheridan",
            "B": "Doug Cutting and Mike Cafarella",
            "C": "Jeff Dean and Sanjay Ghemawat",
            "D": "Linus Torvalds"
        },
        "answer": "B"
    },
    {
        "question": "Hadoop was inspired by which two technical papers from Google?",
        "options": {
            "A": "Bigtable and Spanner",
            "B": "Google File System (GFS) and MapReduce",
            "C": "TensorFlow and Borg",
            "D": "Dremel and Colossus"
        },
        "answer": "B"
    },
    {
        "question": "What does 'HDFS' stand for?",
        "options": {
            "A": "High Definition File System",
            "B": "Hadoop Distributed File System",
            "C": "Hierarchical Data File System",
            "D": "Hosted Data File Storage"
        },
        "answer": "B"
    },
    {
        "question": "Which component in HDFS acts as the master and manages the file system metadata?",
        "options": {
            "A": "DataNode",
            "B": "NameNode",
            "C": "TaskTracker",
            "D": "Resource Manager"
        },
        "answer": "B"
    },
    {
        "question": "What is the default block size in Hadoop 2.x and 3.x?",
        "options": {
            "A": "64 MB",
            "B": "128 MB",
            "C": "256 MB",
            "D": "512 MB"
        },
        "answer": "B"
    },
    {
        "question": "How many replicas of each data block are stored in HDFS by default?",
        "options": {
            "A": "1",
            "B": "3",
            "C": "5",
            "D": "10"
        },
        "answer": "B"
    },
    {
        "question": "Which HDFS component stores the actual data blocks?",
        "options": {
            "A": "NameNode",
            "B": "DataNode",
            "C": "JobTracker",
            "D": "Zookeeper"
        },
        "answer": "B"
    },
    {
        "question": "What is the main goal of 'Rack Awareness' in Hadoop?",
        "options": {
            "A": "To increase network bandwidth",
            "B": "To ensure data reliability by placing replicas on different physical racks",
            "C": "To keep the hardware cool",
            "D": "To speed up data compression"
        },
        "answer": "B"
    },
    {
        "question": "Which of the following is NOT one of the '3 Vs' of Big Data?",
        "options": {
            "A": "Volume",
            "B": "Velocity",
            "C": "Visibility",
            "D": "Variety"
        },
        "answer": "C"
    },
    {
        "question": "What happens if the NameNode in a non-HA cluster fails?",
        "options": {
            "A": "DataNodes take over automatically",
            "B": "The HDFS cluster becomes unavailable",
            "C": "The data is lost permanently",
            "D": "MapReduce tasks continue to run"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to list files in the HDFS root directory?",
        "options": {
            "A": "hdfs dfs -ls /",
            "B": "hdfs root -list",
            "C": "hadoop show /",
            "D": "hadoop files -ls /"
        },
        "answer": "A"
    },
    {
        "question": "What is the role of the 'Secondary NameNode'?",
        "options": {
            "A": "To act as a backup for the NameNode in case of failure",
            "B": "To periodically merge the EditLogs with the FsImage",
            "C": "To manage MapReduce tasks",
            "D": "To store backup copies of DataNodes"
        },
        "answer": "B"
    },
    {
        "question": "Which of the following is an example of 'Variety' in Big Data?",
        "options": {
            "A": "Data growing from TBs to PBs",
            "B": "Data coming in structured, semi-structured, and unstructured formats",
            "C": "Data being generated every millisecond",
            "D": "Data being stored in multiple clouds"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Commodity Hardware' in the context of Hadoop?",
        "options": {
            "A": "Supercomputers used for NASA research",
            "B": "Inexpensive, standard servers that are widely available",
            "C": "Hardware designed specifically for Hadoop by Intel",
            "D": "Specialized GPUs for AI"
        },
        "answer": "B"
    },
    {
        "question": "HDFS is designed for which type of data access pattern?",
        "options": {
            "A": "Random Read/Write",
            "B": "Write Once, Read Many (WORM)",
            "C": "Real-time streaming only",
            "D": "Transactional updates"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Heartbeat' in Hadoop?",
        "options": {
            "A": "The clock speed of the NameNode",
            "B": "A signal sent by a DataNode to the NameNode to prove it is still alive",
            "C": "The time it takes to process one map task",
            "D": "A sound made by the server"
        },
        "answer": "B"
    },
    {
        "question": "Which HDFS file contains a snapshot of the file system's metadata?",
        "options": {
            "A": "EditLog",
            "B": "FsImage",
            "C": "DataSnapshot",
            "D": "HDFS_Meta"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to copy a file from the local filesystem to HDFS?",
        "options": {
            "A": "hdfs dfs -put",
            "B": "hdfs dfs -copyFromLocal",
            "C": "Both A and B",
            "D": "hdfs dfs -moveLocal"
        },
        "answer": "C"
    },
    {
        "question": "Which component manages resources and schedules applications in Hadoop 2.x and 3.x?",
        "options": {
            "A": "MapReduce",
            "B": "YARN",
            "C": "HDFS",
            "D": "Pig"
        },
        "answer": "B"
    },
    {
        "question": "What does 'YARN' stand for?",
        "options": {
            "A": "Yet Another Resource Negotiator",
            "B": "Yielding All Resource Networks",
            "C": "Yoke Active Resource Node",
            "D": "Yellow Array Resource Navigator"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Data Locality' in Hadoop?",
        "options": {
            "A": "Storing data only in one country",
            "B": "Moving the computation code to the data rather than the data to the code",
            "C": "Mapping data to specific geographic regions",
            "D": "Ensuring data is only stored on SSDs"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Block' in HDFS?",
        "options": {
            "A": "A single row of data",
            "B": "The minimum amount of data that HDFS can read or write",
            "C": "A physical hard drive",
            "D": "A security setting"
        },
        "answer": "B"
    },
    {
        "question": "Which tool is used for ingesting data from Relational Databases (RDBMS) into Hadoop?",
        "options": {
            "A": "Flume",
            "B": "Sqoop",
            "C": "Hive",
            "D": "Oozie"
        },
        "answer": "B"
    },
    {
        "question": "Which ecosystem component provides a SQL-like interface for querying data in HDFS?",
        "options": {
            "A": "Spark",
            "B": "Hive",
            "C": "Pig",
            "D": "HBase"
        },
        "answer": "B"
    },
    {
        "question": "Which component is used for log data ingestion and streaming into HDFS?",
        "options": {
            "A": "Sqoop",
            "B": "Flume",
            "C": "Mahout",
            "D": "Zookeeper"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Erasure Coding' in Hadoop 3.x?",
        "options": {
            "A": "Deleting data after a certain time",
            "B": "A method to reduce storage overhead while maintaining fault tolerance compared to replication",
            "C": "Encrypting data for security",
            "D": "A way to compress text files"
        },
        "answer": "B"
    },
    {
        "question": "Which daemon is responsible for tracking the health of individual nodes in a YARN cluster?",
        "options": {
            "A": "ResourceManager",
            "B": "NodeManager",
            "C": "ApplicationMaster",
            "D": "TimelineServer"
        },
        "answer": "B"
    },
    {
        "question": "In HDFS, which node receives the data first during a write operation?",
        "options": {
            "A": "The NameNode",
            "B": "The closest DataNode in the pipeline",
            "C": "All DataNodes simultaneously",
            "D": "The Secondary NameNode"
        },
        "answer": "B"
    },
    {
        "question": "What does 'Vertical Scaling' mean?",
        "options": {
            "A": "Adding more nodes to a cluster",
            "B": "Adding more RAM/CPU to an existing machine",
            "C": "Installing a newer version of Hadoop",
            "D": "Moving data to a higher shelf"
        },
        "answer": "B"
    },
    {
        "question": "Hadoop is primarily written in which programming language?",
        "options": {
            "A": "C++",
            "B": "Java",
            "C": "Python",
            "D": "Scala"
        },
        "answer": "B"
    },
    {
        "question": "Which file system command is used to check the health of the HDFS file system?",
        "options": {
            "A": "hdfs dfs -check",
            "B": "hdfs fsck /",
            "C": "hadoop health -status",
            "D": "hdfs admin -report"
        },
        "answer": "B"
    },
    {
        "question": "What is the function of 'Zookeeper' in a Hadoop HA cluster?",
        "options": {
            "A": "To store big data",
            "B": "To provide coordination services and help in automatic failover of the NameNode",
            "C": "To manage MapReduce tasks",
            "D": "To monitor DataNode temperatures"
        },
        "answer": "B"
    },
    {
        "question": "What is an 'ApplicationMaster' in YARN?",
        "options": {
            "A": "The main server for the cluster",
            "B": "A framework-specific library that negotiates resources from the ResourceManager for a single job",
            "C": "The user who submitted the job",
            "D": "A UI for monitoring tasks"
        },
        "answer": "B"
    },
    {
        "question": "Which of the following is a NoSQL database that runs on top of HDFS?",
        "options": {
            "A": "PostgreSQL",
            "B": "HBase",
            "C": "MySQL",
            "D": "Oracle"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Safe Mode' in HDFS?",
        "options": {
            "A": "A mode where data is encrypted",
            "B": "A read-only state HDFS enters during startup until enough DataNodes report their blocks",
            "C": "A mode where only the admin can access files",
            "D": "A backup mode"
        },
        "answer": "B"
    },
    {
        "question": "Which ecosystem component is used as a workflow scheduler to manage Hadoop jobs?",
        "options": {
            "A": "Zookeeper",
            "B": "Oozie",
            "C": "Pig",
            "D": "Flume"
        },
        "answer": "B"
    },
    {
        "question": "Which company currently manages the development of Apache Hadoop?",
        "options": {
            "A": "Google",
            "B": "The Apache Software Foundation",
            "C": "Cloudera",
            "D": "Microsoft"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Small Files' problem in HDFS?",
        "options": {
            "A": "Small files take too much disk space",
            "B": "Small files overwhelm the NameNode memory because each file is an object in metadata",
            "C": "Small files cannot be replicated",
            "D": "Small files are ignored by MapReduce"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Federated HDFS'?",
        "options": {
            "A": "A cloud version of Hadoop",
            "B": "An architecture that uses multiple independent NameNodes to scale the namespace",
            "C": "Hadoop for government agencies",
            "D": "Combining HDFS with Windows filesystems"
        },
        "answer": "B"
    },
    {
        "question": "In Hadoop 1.x, which component was responsible for both resource management and job scheduling?",
        "options": {
            "A": "ResourceManager",
            "B": "JobTracker",
            "C": "NameNode",
            "D": "TaskTracker"
        },
        "answer": "B"
    },
    {
        "question": "Which shell command is used to change the replication factor of an existing file in HDFS?",
        "options": {
            "A": "hdfs dfs -setrep",
            "B": "hdfs dfs -repfactor",
            "C": "hadoop rep -set",
            "D": "hdfs dfs -chrep"
        },
        "answer": "A"
    },
    {
        "question": "What does the 'EditLog' store in HDFS?",
        "options": {
            "A": "A list of users who logged in",
            "B": "A record of every change made to the filesystem metadata since the last FsImage",
            "C": "The actual content of text files",
            "D": "Errors found by the DataNode"
        },
        "answer": "B"
    },
    {
        "question": "Which YARN component is the ultimate authority that arbitrates resources among all applications in the system?",
        "options": {
            "A": "NodeManager",
            "B": "ResourceManager",
            "C": "ApplicationMaster",
            "D": "Container"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Container' in YARN?",
        "options": {
            "A": "A Docker image",
            "B": "A logical fraction of cluster resources (CPU, Memory) on a single node",
            "C": "A folder in HDFS",
            "D": "A backup unit"
        },
        "answer": "B"
    },
    {
        "question": "Which tool is used for machine learning on top of Hadoop?",
        "options": {
            "A": "Sqoop",
            "B": "Mahout",
            "C": "Hive",
            "D": "Flume"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary benefit of 'Short-Circuit Local Reads'?",
        "options": {
            "A": "Bypassing the DataNode to read data directly from the local disk if the client is on the same node",
            "B": "Reading data without a password",
            "C": "Skipping the NameNode",
            "D": "Reading data from the standby NameNode"
        },
        "answer": "A"
    },
    {
        "question": "Which HDFS command is used to display the disk space used by a directory?",
        "options": {
            "A": "hdfs dfs -df",
            "B": "hdfs dfs -du",
            "C": "hdfs dfs -size",
            "D": "hadoop space -check"
        },
        "answer": "B"
    },
    {
        "question": "In a Write pipeline, how does a client know the data was successfully written to all replicas?",
        "options": {
            "A": "The client checks each DataNode manually",
            "B": "The client receives an Acknowledgment (ACK) packet from the pipeline",
            "C": "The NameNode sends a confirmation email",
            "D": "The process times out after 10 seconds"
        },
        "answer": "B"
    },
    {
        "question": "Which mode of Hadoop installation is used for development/testing on a single machine?",
        "options": {
            "A": "Fully-Distributed Mode",
            "B": "Pseudo-Distributed Mode",
            "C": "Grid Mode",
            "D": "Cloud Mode"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Balance' in HDFS?",
        "options": {
            "A": "Ensuring the number of files matches the number of users",
            "B": "A tool that redistributes blocks among DataNodes so disk usage is even across the cluster",
            "C": "Calculating the total cost of the cluster",
            "D": "Checking the CPU load on the NameNode"
        },
        "answer": "B"
    },
    
    {
        "question": "What are the two primary phases of a MapReduce job?",
        "options": {
            "A": "Input and Output",
            "B": "Map and Reduce",
            "C": "Shuffle and Sort",
            "D": "Split and Combine"
        },
        "answer": "B"
    },
    {
        "question": "Which phase occurs between the Map and Reduce phases to organize data?",
        "options": {
            "A": "Partitioning",
            "B": "Shuffle and Sort",
            "C": "Aggregation",
            "D": "Serialization"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary input format for a Mapper in Hadoop?",
        "options": {
            "A": "Key-Value pairs",
            "B": "CSV lines",
            "C": "JSON objects",
            "D": "Binary blocks"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of an 'InputSplit' in MapReduce?",
        "options": {
            "A": "To divide the data into blocks in HDFS",
            "B": "To define a logical chunk of data for a single Map task",
            "C": "To compress the input file",
            "D": "To delete header rows"
        },
        "answer": "B"
    },
    {
        "question": "Which component is responsible for deciding which Reducer receives a specific Key-Value pair?",
        "options": {
            "A": "Combiner",
            "B": "Partitioner",
            "C": "RecordReader",
            "D": "OutputCommitter"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Combiner' in MapReduce often referred to as?",
        "options": {
            "A": "A mini-reducer",
            "B": "A pre-mapper",
            "C": "A data loader",
            "D": "A task scheduler"
        },
        "answer": "A"
    },
    {
        "question": "What is the main benefit of using a Combiner?",
        "options": {
            "A": "It increases the number of reducers",
            "B": "It reduces the amount of data transferred over the network (bandwidth optimization)",
            "C": "It sorts the final output",
            "D": "It secures the data"
        },
        "answer": "B"
    },
    {
        "question": "The 'Shuffle' phase involves which action?",
        "options": {
            "A": "Writing data to HDFS",
            "B": "Transferring Map outputs to the Reducer nodes",
            "C": "Deleting temporary files",
            "D": "Splitting the input file"
        },
        "answer": "B"
    },
    {
        "question": "In MapReduce, what happens if a task fails multiple times?",
        "options": {
            "A": "The job is automatically successful without that data",
            "B": "The entire job is marked as failed",
            "C": "The user is asked to fix the code manually",
            "D": "Hadoop restarts the cluster"
        },
        "answer": "B"
    },
    {
        "question": "Which method is called once for every Key-Value pair in the input split?",
        "options": {
            "A": "setup()",
            "B": "map()",
            "C": "cleanup()",
            "D": "run()"
        },
        "answer": "B"
    },
    {
        "question": "Where does the output of a Map task get stored temporarily?",
        "options": {
            "A": "In HDFS",
            "B": "On the local disk of the DataNode running the Map task",
            "C": "In the NameNode's RAM",
            "D": "In a cloud bucket"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'Sort' phase do in MapReduce?",
        "options": {
            "A": "Sorts the data by value",
            "B": "Groups and sorts all keys to ensure the Reducer receives them in order",
            "C": "Sorts the DataNodes by health",
            "D": "Alphabetizes the log files"
        },
        "answer": "B"
    },
    {
        "question": "Which class is used to read data from HDFS and convert it into Key-Value pairs for the Mapper?",
        "options": {
            "A": "RecordWriter",
            "B": "RecordReader",
            "C": "InputFormat",
            "D": "OutputFormat"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Speculative Execution' in Hadoop?",
        "options": {
            "A": "Predicting the next day's data",
            "B": "Launching a duplicate of a slow-running task on a different node to speed up the job",
            "C": "Checking for security threats",
            "D": "Estimating the cost of a job"
        },
        "answer": "B"
    },
    {
        "question": "What is the default Number of Reducers if not specified by the user?",
        "options": {
            "A": "0",
            "B": "1",
            "C": "Equal to the number of Mappers",
            "D": "Equal to the number of DataNodes"
        },
        "answer": "B"
    },
    {
        "question": "Which interface must a Key implement to be sorted in MapReduce?",
        "options": {
            "A": "Serializable",
            "B": "WritableComparable",
            "C": "Cloneable",
            "D": "Iterable"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'MapReduce Web UI' default port?",
        "options": {
            "A": "50070",
            "B": "8088",
            "C": "19888",
            "D": "9000"
        },
        "answer": "B"
    },
    {
        "question": "Which of the following is an example of a 'Map-only' job?",
        "options": {
            "A": "Word Count",
            "B": "Data filtering and transformation where no aggregation is needed",
            "C": "Finding the average temperature",
            "D": "Sorting a massive dataset"
        },
        "answer": "B"
    },
    {
        "question": "What happens if you set the number of Reducers to 0?",
        "options": {
            "A": "The job throws an error",
            "B": "The job becomes a Map-only job and outputs directly from the Mapper",
            "C": "The job runs forever",
            "D": "The job outputs to the Secondary NameNode"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'Context' object in the map() function do?",
        "options": {
            "A": "Provides a way to write the output Key-Value pairs",
            "B": "Changes the background color of the UI",
            "C": "Calculates the time of the job",
            "D": "Connects to the internet"
        },
        "answer": "A"
    },
    {
        "question": "In the standard WordCount example, what is the 'Value' emitted by the Mapper?",
        "options": {
            "A": "The word itself",
            "B": "1",
            "C": "The line number",
            "D": "The file name"
        },
        "answer": "B"
    },
    {
        "question": "Which phase of MapReduce is often the biggest bottleneck due to network traffic?",
        "options": {
            "A": "Map",
            "B": "Shuffle",
            "C": "Reduce",
            "D": "Setup"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Writable' interface used for in Hadoop?",
        "options": {
            "A": "Security and encryption",
            "B": "Efficient serialization of data for network transmission",
            "C": "Writing to a database",
            "D": "Drawing charts"
        },
        "answer": "B"
    },
    {
        "question": "Which class is the default 'InputFormat' in Hadoop?",
        "options": {
            "A": "KeyValueInputFormat",
            "B": "TextInputFormat",
            "C": "SequenceFileInputFormat",
            "D": "NLineInputFormat"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Distributed Cache' in Hadoop?",
        "options": {
            "A": "A way to speed up the internet",
            "B": "A facility to cache files (like text or jars) needed by applications across the cluster",
            "C": "A backup for HDFS",
            "D": "A type of RAM"
        },
        "answer": "B"
    },
    {
        "question": "How can you debug a failing MapReduce job locally without a cluster?",
        "options": {
            "A": "Using 'Standalone' (Local) mode",
            "B": "Calling the NameNode directly",
            "C": "Writing it in Python instead",
            "D": "It's impossible to debug locally"
        },
        "answer": "A"
    },
    {
        "question": "Which of the following is NOT a type of 'OutputFormat' in Hadoop?",
        "options": {
            "A": "TextOutputFormat",
            "B": "SequenceFileOutputFormat",
            "C": "ImageOutputFormat",
            "D": "NullOutputFormat"
        },
        "answer": "C"
    },
    {
        "question": "In a MapReduce job, what is the 'JobTracker' equivalent in Hadoop 2.x YARN?",
        "options": {
            "A": "NodeManager",
            "B": "ResourceManager / ApplicationMaster",
            "C": "Secondary NameNode",
            "D": "TaskTracker"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Streaming' in Hadoop?",
        "options": {
            "A": "Watching live video",
            "B": "A utility that allows you to write MapReduce jobs in any language (like Python or Ruby)",
            "C": "A fast way to copy files",
            "D": "Using Hadoop for audio files"
        },
        "answer": "B"
    },
    {
        "question": "Which function allows the user to perform initialization tasks like opening a connection to a database before the map() starts?",
        "options": {
            "A": "map()",
            "B": "setup()",
            "C": "cleanup()",
            "D": "run()"
        },
        "answer": "B"
    },
    {
        "question": "In MapReduce, what does the 'Partitioner' use by default to distribute keys?",
        "options": {
            "A": "The length of the key",
            "B": "A Hash of the key modulo the number of reducers",
            "C": "The alphabetical order of the key",
            "D": "Random assignment"
        },
        "answer": "B"
    },
    {
        "question": "What is the output of the 'Shuffle' phase?",
        "options": {
            "A": "A list of files in HDFS",
            "B": "A sorted list of values for each key, ready for the Reducer",
            "C": "A new Mapper task",
            "D": "A compressed archive"
        },
        "answer": "B"
    },
    {
        "question": "What is the role of 'TaskAttemptID'?",
        "options": {
            "A": "To uniquely identify a specific attempt to run a task",
            "B": "To name the whole job",
            "C": "To identify the user",
            "D": "To count the number of files"
        },
        "answer": "A"
    },
    {
        "question": "Which command is used to kill a running MapReduce job?",
        "options": {
            "A": "hadoop job -kill",
            "B": "mapred job -kill",
            "C": "Both A and B",
            "D": "hdfs job -stop"
        },
        "answer": "C"
    },
    {
        "question": "What is 'Counter' in Hadoop MapReduce?",
        "options": {
            "A": "A person who counts data",
            "B": "A mechanism to track job-level statistics like 'number of invalid records'",
            "C": "A tool to count the nodes",
            "D": "A part of the UI"
        },
        "answer": "B"
    },
    {
        "question": "Which class is the base class for all MapReduce jobs in the newer 'mapreduce' API?",
        "options": {
            "A": "JobClient",
            "B": "Job",
            "C": "JobConf",
            "D": "TaskRunner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Data Skew' in MapReduce?",
        "options": {
            "A": "When the data is encrypted",
            "B": "When one reducer receives significantly more data than others, slowing down the job",
            "C": "When the data is in the wrong format",
            "D": "When data is stored on a tilted server"
        },
        "answer": "B"
    },
    {
        "question": "How many times is the cleanup() function called in a Mapper task?",
        "options": {
            "A": "For every record",
            "B": "Once, at the very end of the task",
            "C": "Never",
            "D": "Infinite times"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Lazy Output' in MapReduce?",
        "options": {
            "A": "Output that takes a long time",
            "B": "A setting that prevents creating an empty output file if no records are written",
            "C": "Lowering the resolution of output",
            "D": "Writing output to a cache"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is a valid way to optimize a MapReduce job?",
        "options": {
            "A": "Using a Combiner",
            "B": "Tuning the number of Reducers",
            "C": "Using Compressed Map Outputs",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "Which type of join is performed in the Map phase and is generally faster if one table is small?",
        "options": {
            "A": "Reduce-side Join",
            "B": "Map-side Join",
            "C": "Cross Join",
            "D": "Outer Join"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary disadvantage of 'Reduce-side Joins'?",
        "options": {
            "A": "They cannot handle large datasets",
            "B": "They involve heavy network traffic during the Shuffle phase",
            "C": "They are only for SQL databases",
            "D": "They require the NameNode to be restarted"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Vectorization' in the context of query execution (used by tools like Hive on Hadoop)?",
        "options": {
            "A": "Turning data into images",
            "B": "Processing a batch of rows at once instead of one by one for better CPU performance",
            "C": "Sorting data by size",
            "D": "Scaling the cluster"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Splittable' compression format?",
        "options": {
            "A": "A format that can be deleted easily",
            "B": "A format (like Bzip2) that allows Hadoop to split a large compressed file into multiple Map tasks",
            "C": "A format used for audio",
            "D": "A format that doesn't use keys"
        },
        "answer": "B"
    },
    {
        "question": "Which command-line argument is used to pass a custom parameter to a MapReduce job?",
        "options": {
            "A": "-param",
            "B": "-D",
            "C": "-set",
            "D": "-var"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Total Order Partitioning'?",
        "options": {
            "A": "Ensuring the whole dataset is globally sorted across multiple output files",
            "B": "Sorting only one file",
            "C": "Counting all records",
            "D": "Naming the jobs numerically"
        },
        "answer": "A"
    },
    {
        "question": "Which property in mapred-site.xml defines the number of map tasks?",
        "options": {
            "A": "mapred.map.tasks",
            "B": "There is no direct property; it is determined by the number of InputSplits",
            "C": "mapred.task.count",
            "D": "cluster.map.total"
        },
        "answer": "B"
    },
    {
        "question": "In MapReduce, what is the role of the 'Reporter'?",
        "options": {
            "A": "Writing the final results",
            "B": "A mechanism for tasks to report progress and update counters",
            "C": "A person who monitors the cluster",
            "D": "A log aggregator"
        },
        "answer": "B"
    },
    {
        "question": "What happens if a Map task takes too long (Staggered Task)?",
        "options": {
            "A": "It is killed immediately",
            "B": "Hadoop might launch a speculative copy of it",
            "C": "The user must restart it",
            "D": "The whole cluster slows down to wait for it"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is the 'Mapper' output type in the WordCount example?",
        "options": {
            "A": "<Text, IntWritable>",
            "B": "<IntWritable, Text>",
            "C": "<LongWritable, Text>",
            "D": "<Text, Text>"
        },
        "answer": "A"
    },
    
    {
        "question": "Which Hadoop ecosystem component provides a data warehousing infrastructure and a SQL-like language called HQL?",
        "options": {
            "A": "Pig",
            "B": "Hive",
            "C": "Sqoop",
            "D": "Oozie"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary language used in Apache Pig for data flow scripts?",
        "options": {
            "A": "PigLatin",
            "B": "PigSQL",
            "C": "HQL",
            "D": "Python"
        },
        "answer": "A"
    },
    {
        "question": "In Hive, what is the 'Metastore'?",
        "options": {
            "A": "A place where the actual data is stored",
            "B": "A central repository that stores metadata (schema and location) of Hive tables",
            "C": "A backup for HDFS",
            "D": "A tool to track user logins"
        },
        "answer": "B"
    },
    {
        "question": "Which tool is best suited for streaming high-volume log data into HDFS?",
        "options": {
            "A": "Sqoop",
            "B": "Flume",
            "C": "Pig",
            "D": "Mahout"
        },
        "answer": "B"
    },
    {
        "question": "What is the main function of Apache Sqoop?",
        "options": {
            "A": "To process streaming data",
            "B": "To transfer bulk data between Hadoop and relational databases like MySQL or Oracle",
            "C": "To coordinate cluster nodes",
            "D": "To act as a NoSQL database"
        },
        "answer": "B"
    },
    {
        "question": "Which component in Hive is responsible for converting HQL queries into MapReduce, Tez, or Spark jobs?",
        "options": {
            "A": "Beeline",
            "B": "Hive Query Engine (Driver)",
            "C": "Metastore",
            "D": "SerDe"
        },
        "answer": "B"
    },
    {
        "question": "What is 'SerDe' in Hive?",
        "options": {
            "A": "Service Desktop",
            "B": "Serializer/Deserializer (used to read and write data in various formats)",
            "C": "Series Design",
            "D": "Server Definition"
        },
        "answer": "B"
    },
    {
        "question": "Which Hive table type deletes the underlying data when the table is dropped?",
        "options": {
            "A": "External Table",
            "B": "Managed (Internal) Table",
            "C": "Temporary Table",
            "D": "Virtual Table"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of an 'External Table' in Hive?",
        "options": {
            "A": "To store data outside of HDFS",
            "B": "To point to data already in HDFS without Hive taking ownership of the files",
            "C": "To allow external users to log in",
            "D": "To speed up data encryption"
        },
        "answer": "B"
    },
    {
        "question": "Which Apache Pig operator is used to load data from the file system?",
        "options": {
            "A": "READ",
            "B": "LOAD",
            "C": "GET",
            "D": "IMPORT"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'HBase' data model based on?",
        "options": {
            "A": "Relational tables",
            "B": "Google's Bigtable (Column-family based NoSQL)",
            "C": "Key-Value pairs only",
            "D": "Graph nodes"
        },
        "answer": "B"
    },
    {
        "question": "In HBase, what is a 'RegionServer'?",
        "options": {
            "A": "A server that stores geographic data",
            "B": "A daemon responsible for serving and managing data regions",
            "C": "A backup for the NameNode",
            "D": "A tool to manage user regions"
        },
        "answer": "B"
    },
    {
        "question": "Which tool is used for scheduling and managing a sequence of Hadoop jobs (Workflows)?",
        "options": {
            "A": "Zookeeper",
            "B": "Oozie",
            "C": "Sqoop",
            "D": "Flume"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Partitioning' in Hive used for?",
        "options": {
            "A": "To encrypt data",
            "B": "To prune data during queries by dividing a table into logical parts based on column values",
            "C": "To split the HDFS cluster into two",
            "D": "To limit the number of users per table"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Bucketing' in Hive?",
        "options": {
            "A": "Grouping files by size",
            "B": "Decomposing data into more manageable clusters (files) based on a hash of a column",
            "C": "A way to backup the Metastore",
            "D": "Creating temporary folders"
        },
        "answer": "B"
    },
    {
        "question": "Which Flume component receives data from an external source (like a web server)?",
        "options": {
            "A": "Channel",
            "B": "Source",
            "C": "Sink",
            "D": "Agent"
        },
        "answer": "B"
    },
    {
        "question": "Which Flume component delivers data to the final destination (like HDFS)?",
        "options": {
            "A": "Source",
            "B": "Sink",
            "C": "Channel",
            "D": "Intercepter"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Apache Ambari'?",
        "options": {
            "A": "A machine learning library",
            "B": "An open-source tool for provisioning, managing, and monitoring Hadoop clusters",
            "C": "A replacement for HDFS",
            "D": "A security plugin"
        },
        "answer": "B"
    },
    {
        "question": "In HBase, what does 'Zookeeper' help with?",
        "options": {
            "A": "Storing large blobs",
            "B": "Maintaining cluster state, master election, and region location",
            "C": "Processing MapReduce jobs",
            "D": "Sorting data"
        },
        "answer": "B"
    },
    {
        "question": "Which SQL command is NOT typically used in Hive HQL (as Hive is OLAP, not OLTP)?",
        "options": {
            "A": "SELECT",
            "B": "UPDATE (standard, non-ACID tables)",
            "C": "JOIN",
            "D": "WHERE"
        },
        "answer": "B"
    },
    {
        "question": "Which tool allows for interactive, low-latency SQL queries on Hadoop (alternative to Hive)?",
        "options": {
            "A": "Impala",
            "B": "Mahout",
            "C": "Sqoop",
            "D": "Oozie"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of 'Apache Phoenix'?",
        "options": {
            "A": "To backup HBase",
            "B": "To provide a relational database layer (SQL) over HBase",
            "C": "To replace Sqoop",
            "D": "To monitor YARN containers"
        },
        "answer": "B"
    },
    {
        "question": "Which data format is highly optimized for Hive queries due to its columnar storage?",
        "options": {
            "A": "CSV",
            "B": "ORC (Optimized Row Columnar)",
            "C": "JSON",
            "D": "XML"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Apache Falcon'?",
        "options": {
            "A": "A fast data transfer tool",
            "B": "A data governance and management framework for Hadoop",
            "C": "A NoSQL database",
            "D": "A search engine for HDFS"
        },
        "answer": "B"
    },
    {
        "question": "Which Oozie job type is used to schedule a workflow based on a regular time interval?",
        "options": {
            "A": "Workflow",
            "B": "Coordinator",
            "C": "Bundle",
            "D": "Timer"
        },
        "answer": "B"
    },
    {
        "question": "Which Apache Pig mode is used to run scripts on a Hadoop cluster?",
        "options": {
            "A": "Local mode",
            "B": "MapReduce mode",
            "C": "Interactive mode",
            "D": "Cluster mode"
        },
        "answer": "B"
    },
    {
        "question": "What is the function of 'HiveServer2'?",
        "options": {
            "A": "To store table data",
            "B": "To allow remote clients (like JDBC/ODBC) to execute queries against Hive",
            "C": "To act as a secondary NameNode",
            "D": "To compress HDFS blocks"
        },
        "answer": "B"
    },
    {
        "question": "Which Sqoop command is used to list all databases in a remote MySQL server?",
        "options": {
            "A": "sqoop list-databases",
            "B": "sqoop show-dbs",
            "C": "sqoop get-all",
            "D": "sqoop connect --list"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Apache Knox' used for in the Hadoop ecosystem?",
        "options": {
            "A": "Data processing",
            "B": "Security (Gateway for providing perimeter security)",
            "C": "Data ingestion",
            "D": "Workflow management"
        },
        "answer": "B"
    },
    {
        "question": "Which Apache Pig operator is used to remove duplicate rows?",
        "options": {
            "A": "UNIQUE",
            "B": "DISTINCT",
            "C": "SINGLE",
            "D": "GROUP"
        },
        "answer": "B"
    },
    {
        "question": "In HBase, data is physically sorted by which field?",
        "options": {
            "A": "Column Family",
            "B": "Row Key",
            "C": "Timestamp",
            "D": "Value"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Apache Ranger' used for?",
        "options": {
            "A": "Scheduling jobs",
            "B": "Comprehensive security management (Authorization/Audit) for the Hadoop cluster",
            "C": "Searching for files",
            "D": "Optimizing MapReduce"
        },
        "answer": "B"
    },
    {
        "question": "Which Hive component translates the execution plan into tasks for the cluster?",
        "options": {
            "A": "Parser",
            "B": "Optimizer",
            "C": "Executor",
            "D": "Compiler"
        },
        "answer": "C"
    },
    {
        "question": "What is the 'HDFS Federation' feature designed to solve?",
        "options": {
            "A": "Small files problem",
            "B": "Metadata scalability (allowing multiple NameNodes to manage different namespaces)",
            "C": "Data encryption",
            "D": "Slow data ingestion"
        },
        "answer": "B"
    },
    {
        "question": "Which Sqoop parameter is used to specify the number of parallel mappers for a data transfer?",
        "options": {
            "A": "-m",
            "B": "--mappers",
            "C": "-p",
            "D": "--threads"
        },
        "answer": "A"
    },
    {
        "question": "What does 'HPLSQL' (in Hive) allow users to do?",
        "options": {
            "A": "Write high-performance Python",
            "B": "Run Procedural SQL (PL/SQL) logic on Hive",
            "C": "Compress data with high ratios",
            "D": "Connect Hive to mobile apps"
        },
        "answer": "B"
    },
    {
        "question": "Which tool provides an interface to define metadata for different Hadoop components to allow sharing between Hive and Pig?",
        "options": {
            "A": "Oozie",
            "B": "HCatalog",
            "C": "Zookeeper",
            "D": "Mahout"
        },
        "answer": "B"
    },
    {
        "question": "In Pig, what is a 'Bag'?",
        "options": {
            "A": "A single row",
            "B": "A collection of tuples",
            "C": "A data file in HDFS",
            "D": "A temporary folder"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'HBase Master' responsible for?",
        "options": {
            "A": "Storing data",
            "B": "Administrative operations like creating/dropping tables and region assignment",
            "C": "Encryption",
            "D": "User login"
        },
        "answer": "B"
    },
    {
        "question": "Which Hive file format is a successor to RCFile and is highly optimized for performance?",
        "options": {
            "A": "AVRO",
            "B": "ORC",
            "C": "Parquet",
            "D": "Both B and C"
        },
        "answer": "D"
    },
    {
        "question": "Which Sqoop command is used to export data from HDFS back to an RDBMS?",
        "options": {
            "A": "sqoop import",
            "B": "sqoop export",
            "C": "sqoop send",
            "D": "sqoop upload"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Apache Atlas' used for?",
        "options": {
            "A": "World mapping",
            "B": "Data lineage and metadata management",
            "C": "Cluster monitoring",
            "D": "Text searching"
        },
        "answer": "B"
    },
    {
        "question": "Which Pig operator is used to join two data relations?",
        "options": {
            "A": "MERGE",
            "B": "JOIN",
            "C": "UNION",
            "D": "COMBINE"
        },
        "answer": "B"
    },
    {
        "question": "In Flume, what is the role of a 'Channel'?",
        "options": {
            "A": "To compress data",
            "B": "To act as a transient store that bridges the Source and the Sink",
            "C": "To encrypt data",
            "D": "To filter logs"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Hive Beeline'?",
        "options": {
            "A": "A tool to track bees",
            "B": "A command-line shell that connects to HiveServer2 via JDBC",
            "C": "A Hive backup tool",
            "D": "A Hive query optimizer"
        },
        "answer": "B"
    },
    {
        "question": "Which Sqoop parameter helps prevent a single mapper from being overloaded when importing data?",
        "options": {
            "A": "--split-by",
            "B": "--divide",
            "C": "--partition",
            "D": "--even"
        },
        "answer": "A"
    },
    {
        "question": "What does the 'STORE' operator do in Pig?",
        "options": {
            "A": "Saves data to a database",
            "B": "Saves the resulting relation to the file system (e.g., HDFS)",
            "C": "Displays data on the screen",
            "D": "Opens a shop"
        },
        "answer": "B"
    },
    {
        "question": "Which Oozie node type represents the start of a workflow?",
        "options": {
            "A": "Action node",
            "B": "Control node (Start node)",
            "C": "Data node",
            "D": "Meta node"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Apache Sqoop's' relationship with MapReduce?",
        "options": {
            "A": "It replaces MapReduce",
            "B": "It launches a Map-only job to perform data transfers in parallel",
            "C": "It is written in PigLatin",
            "D": "It has no relationship"
        },
        "answer": "B"
    },
    {
        "question": "Which ecosystem tool is used for massive graph processing on Hadoop?",
        "options": {
            "A": "Giraph",
            "B": "Pig",
            "C": "Mahout",
            "D": "HBase"
        },
        "answer": "A"
    },

    {
        "question": "Which security protocol is the standard for authentication in a 'Secure Hadoop' cluster?",
        "options": {
            "A": "SSL/TLS",
            "B": "Kerberos",
            "C": "OAuth 2.0",
            "D": "LDAP"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary function of the 'JournalNode' in an HDFS High Availability (HA) setup?",
        "options": {
            "A": "To store data blocks",
            "B": "To share EditLogs between the Active and Standby NameNodes",
            "C": "To act as a backup DataNode",
            "D": "To monitor network traffic"
        },
        "answer": "B"
    },
    {
        "question": "Which Hadoop 3.x feature allows for significant storage savings by using parity blocks instead of full replicas?",
        "options": {
            "A": "Erasure Coding",
            "B": "Block Compression",
            "C": "Data Deduplication",
            "D": "Federated HDFS"
        },
        "answer": "A"
    },
    {
        "question": "In HDFS High Availability, which daemon is responsible for detecting NameNode failure and triggering failover?",
        "options": {
            "A": "JournalNode",
            "B": "ZKFailoverController (ZKFC)",
            "C": "NodeManager",
            "D": "DataNode"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Fencing' in a High Availability cluster?",
        "options": {
            "A": "Building a firewall",
            "B": "A mechanism to ensure only one NameNode is 'Active' at a time to prevent 'split-brain' scenarios",
            "C": "Sorting data by size",
            "D": "Disconnecting the standby node"
        },
        "answer": "B"
    },
    {
        "question": "Which shell command is used to enter or leave 'Safe Mode' manually?",
        "options": {
            "A": "hdfs dfs -safemode",
            "B": "hdfs dfsadmin -safemode",
            "C": "hadoop safe -status",
            "D": "hdfs fsck -safe"
        },
        "answer": "B"
    },
    {
        "question": "What does 'HDFS Snapshots' allow an administrator to do?",
        "options": {
            "A": "Take photos of the server",
            "B": "Create read-only copies of the file system at a point in time for data protection",
            "C": "Increase the block size",
            "D": "Speed up MapReduce jobs"
        },
        "answer": "B"
    },
    {
        "question": "Which property in 'hdfs-site.xml' defines the HDFS replication factor?",
        "options": {
            "A": "dfs.replication",
            "B": "hdfs.rep.factor",
            "C": "fs.block.replica",
            "D": "core.rep.count"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Speculative Execution' designed to handle?",
        "options": {
            "A": "Security breaches",
            "B": "Straggler tasks (tasks that are running much slower than others due to hardware issues)",
            "C": "Data corruption",
            "D": "Network outages"
        },
        "answer": "B"
    },
    {
        "question": "Which file is used to list the hostnames of all DataNodes in the cluster?",
        "options": {
            "A": "datanodes",
            "B": "workers (or 'slaves' in older versions)",
            "C": "hosts.conf",
            "D": "nodes.txt"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Balancer' utility used for?",
        "options": {
            "A": "To balance the CPU load",
            "B": "To redistribute data blocks across DataNodes when disk usage is uneven",
            "C": "To manage user quotas",
            "D": "To synchronize clocks"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Keytab' file in Kerberos-secured Hadoop?",
        "options": {
            "A": "A list of SQL keys",
            "B": "A file containing Kerberos principals and encrypted keys for password-less authentication",
            "C": "A manual for encryption",
            "D": "A backup of the NameNode"
        },
        "answer": "B"
    },
    {
        "question": "Which daemon provides a centralized timeline for YARN applications to store and retrieve metrics?",
        "options": {
            "A": "HistoryServer",
            "B": "Timeline Service (TimelineServer)",
            "C": "MetricManager",
            "D": "JobTracker"
        },
        "answer": "B"
    },
    {
        "question": "In Hadoop 3.x, what is the default number of NameNodes supported for High Availability?",
        "options": {
            "A": "1",
            "B": "2",
            "C": "3 or more",
            "D": "Unlimited"
        },
        "answer": "C"
    },
    {
        "question": "Which command is used to display the current HDFS storage policy for a specific path?",
        "options": {
            "A": "hdfs storagepolicies -getStoragePolicy",
            "B": "hdfs dfs -showpolicy",
            "C": "hadoop fs -policy",
            "D": "hdfs admin -checkpolicy"
        },
        "answer": "A"
    },
    {
        "question": "What is 'DistCp'?",
        "options": {
            "A": "Distributed Compression",
            "B": "Distributed Copy (used for large-scale data transfer between clusters)",
            "C": "Distance Computation",
            "D": "Disk Partitioning"
        },
        "answer": "B"
    },
    {
        "question": "Which log file is most useful for troubleshooting a failing NameNode startup?",
        "options": {
            "A": "hadoop-hdfs-datanode.log",
            "B": "hadoop-hdfs-namenode.log",
            "C": "yarn-resourcemanager.out",
            "D": "syslog"
        },
        "answer": "B"
    },
    {
        "question": "What does 'HDFS Quota' manage?",
        "options": {
            "A": "The number of users allowed",
            "B": "The limits on the number of files or the amount of disk space used by a directory",
            "C": "The speed of data transfer",
            "D": "The number of concurrent jobs"
        },
        "answer": "B"
    },
    {
        "question": "Which feature allows different YARN applications to be isolated in terms of CPU and memory usage?",
        "options": {
            "A": "NameNode Federation",
            "B": "Cgroups (Control Groups)",
            "C": "Virtual Memory",
            "D": "Data Locality"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Preemption' in YARN scheduling?",
        "options": {
            "A": "Starting a job before others",
            "B": "Taking resources away from a lower-priority application to give to a higher-priority one",
            "C": "Deleting old containers",
            "D": "Reserving nodes for a specific user"
        },
        "answer": "B"
    },
    {
        "question": "Which HDFS storage policy is used for data that is frequently accessed and requires high performance?",
        "options": {
            "A": "COLD",
            "B": "HOT",
            "C": "ALL_SSD",
            "D": "LAZY_PERSIST"
        },
        "answer": "C"
    },
    {
        "question": "What is 'JMX' (Java Management Extensions) used for in Hadoop?",
        "options": {
            "A": "To write code",
            "B": "To monitor and manage Hadoop daemons and their metrics",
            "C": "To encrypt HDFS blocks",
            "D": "To sort log files"
        },
        "answer": "B"
    },
    {
        "question": "Which command-line tool is used to manage YARN applications, such as killing a job?",
        "options": {
            "A": "hadoop job",
            "B": "yarn application",
            "C": "mapred job",
            "D": "yarn kill"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Split-Brain' scenario in HDFS?",
        "options": {
            "A": "When the NameNode RAM is full",
            "B": "When two NameNodes think they are both 'Active' at the same time",
            "C": "When data is split into too many blocks",
            "D": "When the cluster is divided into two separate networks"
        },
        "answer": "B"
    },
    {
        "question": "Which Hadoop version introduced the 'Erasure Coding' feature officially?",
        "options": {
            "A": "1.0",
            "B": "2.7",
            "C": "3.0",
            "D": "3.3"
        },
        "answer": "C"
    },
    {
        "question": "What is the purpose of 'Hadoop Archive' (HAR)?",
        "options": {
            "A": "To compress small files into a larger file to reduce NameNode memory pressure",
            "B": "To delete old data",
            "C": "To create a ZIP of the cluster logs",
            "D": "To move data to a tape drive"
        },
        "answer": "A"
    },
    {
        "question": "Which YARN scheduler is designed to provide a guaranteed share of resources to different organizations/queues?",
        "options": {
            "A": "FIFO Scheduler",
            "B": "Capacity Scheduler",
            "C": "Fair Scheduler",
            "D": "Both B and C"
        },
        "answer": "D"
    },
    {
        "question": "What is the 'WebHDFS' protocol used for?",
        "options": {
            "A": "Browsing the internet on Hadoop",
            "B": "Providing a REST API for accessing HDFS data over HTTP",
            "C": "Securing the cluster",
            "D": "Visualizing data in a browser"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to find the location of a specific block for a file?",
        "options": {
            "A": "hdfs fsck [path] -files -blocks -locations",
            "B": "hdfs dfs -where [path]",
            "C": "hadoop locate [path]",
            "D": "hdfs admin -report -blocks"
        },
        "answer": "A"
    },
    {
        "question": "What is 'NFS Gateway' in Hadoop?",
        "options": {
            "A": "A way to play games on the cluster",
            "B": "Allows clients to mount HDFS to their local filesystem like a regular network drive",
            "C": "A tool to monitor network speed",
            "D": "A backup for the NameNode"
        },
        "answer": "B"
    },
    {
        "question": "Which daemon must be running to view the history of completed MapReduce jobs?",
        "options": {
            "A": "ResourceManager",
            "B": "JobHistoryServer",
            "C": "TimelineServer",
            "D": "TaskTracker"
        },
        "answer": "B"
    },
    {
        "question": "In a Kerberos-enabled cluster, which command does a user run to obtain a ticket-granting ticket?",
        "options": {
            "A": "kinit",
            "B": "hadoop login",
            "C": "ssh login",
            "D": "auth-get"
        },
        "answer": "A"
    },
    {
        "question": "What is the 'Disk Checker' feature in HDFS?",
        "options": {
            "A": "A tool to check the size of the disk",
            "B": "A mechanism where DataNodes periodically check their local disks for failures",
            "C": "A tool to defragment the disk",
            "D": "A way to format the disk"
        },
        "answer": "B"
    },
    {
        "question": "Which property in 'core-site.xml' specifies the default file system URI (NameNode address)?",
        "options": {
            "A": "fs.defaultFS",
            "B": "hdfs.namenode.url",
            "C": "core.fs.uri",
            "D": "default.hdfs.path"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Intra-DataNode Balancer' in Hadoop 3.x?",
        "options": {
            "A": "Balancing data between different DataNodes",
            "B": "Balancing data between multiple disks within a single DataNode",
            "C": "Balancing the CPU usage on a DataNode",
            "D": "Balancing network traffic"
        },
        "answer": "B"
    },
    {
        "question": "Which component acts as the 'Proxy' for web requests to the cluster, hiding the internal node addresses?",
        "options": {
            "A": "Knox Gateway",
            "B": "HttpFS",
            "C": "Both A and B",
            "D": "NameNode Web UI"
        },
        "answer": "C"
    },
    {
        "question": "What happens to a file in HDFS if its replication factor is reduced?",
        "options": {
            "A": "The file is deleted",
            "B": "Hadoop eventually deletes the extra replicas during its next cleanup cycle",
            "C": "The file becomes read-only",
            "D": "The block size is halved"
        },
        "answer": "B"
    },
    {
        "question": "Which tool is used to monitor the performance of HDFS and MapReduce using a dashboard (often provided by Cloudera/Hortonworks)?",
        "options": {
            "A": "Ambari",
            "B": "Cloudera Manager",
            "C": "Both A and B",
            "D": "Grafana"
        },
        "answer": "C"
    },
    {
        "question": "What is 'Rolling Upgrade'?",
        "options": {
            "A": "Upgrading the cluster while it remains operational by restarting nodes one by one",
            "B": "Upgrading the cluster on a weekend",
            "C": "A way to install Hadoop on a laptop",
            "D": "Upgrading only the client software"
        },
        "answer": "A"
    },
    {
        "question": "Which HDFS command is used to move a file to the HDFS trash bin instead of permanent deletion?",
        "options": {
            "A": "hdfs dfs -rm",
            "B": "hdfs dfs -trash",
            "C": "hdfs dfs -expunge",
            "D": "hdfs dfs -rm -skipTrash"
        },
        "answer": "A"
    },
    {
        "question": "What is the 'FsShell'?",
        "options": {
            "A": "The physical shell of the server",
            "B": "The command-line interface used to interact with HDFS (hdfs dfs)",
            "C": "A programming language",
            "D": "A security layer"
        },
        "answer": "B"
    },
    {
        "question": "Which property in 'yarn-site.xml' defines the amount of physical memory allowed for containers on a node?",
        "options": {
            "A": "yarn.nodemanager.resource.memory-mb",
            "B": "yarn.container.ram.limit",
            "C": "cluster.node.memory",
            "D": "yarn.resource.max-mem"
        },
        "answer": "A"
    },
    {
        "question": "What does 'HDFS Transparent Encryption' use to protect data?",
        "options": {
            "A": "Encryption Zones with HDFS KMS (Key Management Server)",
            "B": "Password-protected folders",
            "C": "SSL only",
            "D": "Disk-level encryption only"
        },
        "answer": "A"
    },
    {
        "question": "Which daemon is used to bridge the gap between Hadoop and Microsoft Active Directory?",
        "options": {
            "A": "SSSD",
            "B": "Winbind",
            "C": "Both A and B",
            "D": "LDAP-Connect"
        },
        "answer": "C"
    },
    {
        "question": "What is the 'Default' port for the YARN ResourceManager Web UI?",
        "options": {
            "A": "50070",
            "B": "8088",
            "C": "8042",
            "D": "19888"
        },
        "answer": "B"
    },
    {
        "question": "Which feature allows users to run Docker containers as YARN tasks?",
        "options": {
            "A": "Docker on YARN (introduced in Hadoop 3.x)",
            "B": "YARN-Docker Bridge",
            "C": "Containerize-Hadoop",
            "D": "YARN-Compose"
        },
        "answer": "A"
    },
    {
        "question": "What is the result of running 'hdfs dfsadmin -report'?",
        "options": {
            "A": "A list of all users",
            "B": "A detailed summary of the HDFS cluster state, including capacity and node health",
            "C": "A list of files",
            "D": "A query execution plan"
        },
        "answer": "B"
    },
    {
        "question": "Which property allows 'Opportunistic Containers' in YARN for better utilization?",
        "options": {
            "A": "yarn.resourcemanager.opportunistic-container-allocation.enabled",
            "B": "yarn.lucky.containers",
            "C": "cluster.extra.resources",
            "D": "yarn.idle.fill"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Distributed Load Balancing' in Hadoop 3.x?",
        "options": {
            "A": "Moving data to a different cloud",
            "B": "A client-side feature to better distribute read/write requests among DataNodes",
            "C": "A way to balance the power supply",
            "D": "Sorting files by name"
        },
        "answer": "B"
    },
    {
        "question": "Final question: Which animal is the mascot of Apache Hadoop?",
        "options": {
            "A": "A Bee",
            "B": "A Yellow Elephant",
            "C": "A Whale",
            "D": "A Pig"
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
    skill = "Hadoop"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
