from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
  {
    "question": "What is the primary goal of 'Scalability' in system design?",
    "options": {
      "A": "To make the code easier to read.",
      "B": "To handle a growing amount of work by adding resources to the system.",
      "C": "To reduce the number of servers to zero.",
      "D": "To encrypt all outgoing traffic."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Vertical Scaling' (Scaling Up) involves adding more power (CPU, RAM) to an existing server.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO benefits of 'Horizontal Scaling' (Scaling Out):",
    "options": {
      "A": "Higher availability (no single point of failure).",
      "B": "Easier to scale infinitely compared to vertical scaling.",
      "C": "It is always cheaper for small applications.",
      "D": "It requires no changes to application architecture."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A Load Balancer distributes incoming network traffic across a group of backend servers.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which Load Balancing algorithm sends the next request to the server with the fewest active connections?",
    "options": {
      "A": "Round Robin",
      "B": "Least Connections",
      "C": "IP Hash",
      "D": "Random"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO layers where Load Balancers typically operate in the OSI Model:",
    "options": {
      "A": "Layer 4 (Transport)",
      "B": "Layer 7 (Application)",
      "C": "Layer 2 (Data Link)",
      "D": "Layer 1 (Physical)"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "Which theorem states that a distributed system cannot simultaneously provide more than two out of three guarantees: Consistency, Availability, and Partition Tolerance?",
    "options": {
      "A": "Moore’s Law",
      "B": "CAP Theorem",
      "C": "Amdahl's Law",
      "D": "Reed's Law"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'N+1 Problem' in system performance?",
    "options": {
      "A": "Adding one extra server for N users.",
      "B": "A performance issue where an application makes N+1 database calls to retrieve N items.",
      "C": "Having one more backup than necessary.",
      "D": "A versioning error."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Database Sharding' involves breaking up a large database into smaller, faster, more manageable parts called shards.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which consistency model guarantees that if a process has updated a data item, any subsequent access by that process will return the updated value?",
    "options": {
      "A": "Monotonic Read Consistency",
      "B": "Read-Your-Writes Consistency",
      "C": "Eventual Consistency",
      "D": "Weak Consistency"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'CDN' (Content Delivery Network)?",
    "options": {
      "A": "A central database located in the primary data center.",
      "B": "Geographically distributed servers at the 'edge' of the network, closer to users.",
      "C": "A tool inside the user's browser only.",
      "D": "A type of local storage."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO common Cache Eviction policies:",
    "options": {
      "A": "LRU (Least Recently Used)",
      "B": "LFU (Least Frequently Used)",
      "C": "MFO (Most Frequently Opened)",
      "D": "RANDO (Random Only)"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What does a 'Circuit Breaker' do in a distributed system?",
    "options": {
      "A": "It shuts down the server physically.",
      "B": "It detects failures and prevents a failing service from causing a system-wide crash.",
      "C": "It acts as a network cable.",
      "D": "It generates random logs."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Infrastructure as Code' (IaC) allows developers to manage data centers through machine-readable definition files.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Chaos Engineering'?",
    "options": {
      "A": "Randomly deleting code.",
      "B": "Experimenting on a system to build confidence in its capability to withstand turbulent conditions.",
      "C": "A lack of project management.",
      "D": "Using unstable servers."
    },
    "answer": "B"
  },
  {
    "question": "In 'Primary-Secondary' (Master-Slave) replication, which node typically handles write requests?",
    "options": {
      "A": "The Primary (Master) node.",
      "B": "Any Secondary (Slave) node.",
      "C": "The Load Balancer.",
      "D": "All nodes simultaneously."
    },
    "answer": "A"
  },
  {
    "question": "True or False: A 'Stateless' service is easier to scale and recover from failures because it stores no client context between requests.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Blue-Green Deployment'?",
    "options": {
      "A": "Using two servers with different colored cables.",
      "B": "Running two identical production environments to reduce downtime and risk during updates.",
      "C": "Deleting the database after an update.",
      "D": "Updating users based on their location."
    },
    "answer": "B"
  },
  {
    "question": "Which mechanism ensures a system isn't overwhelmed by a sudden spike in traffic by dropping excess requests?",
    "options": {
      "A": "Load Shedding",
      "B": "Data Mining",
      "C": "Database Indexing",
      "D": "Manual Restart"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Latency' in system design?",
    "options": {
      "A": "The number of requests per second.",
      "B": "The time it takes for data to travel from source to destination.",
      "C": "The total capacity of a server.",
      "D": "The cost of a network cable."
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Reverse Proxy'?",
    "options": {
      "A": "A tool used by users to hide their IP.",
      "B": "A server that sits in front of backend servers and forwards client requests to them.",
      "C": "A database backup tool.",
      "D": "A type of programming language."
    },
    "answer": "B"
  },
  {
    "question": "Which status is known as 'Five Nines' availability?",
    "options": {
      "A": "99.9%",
      "B": "99.999%",
      "C": "95.555%",
      "D": "99.000%"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO benefits of a 'Layer 7' (Application Layer) Load Balancer:",
    "options": {
      "A": "It can route traffic based on URL paths.",
      "B": "It can perform SSL termination.",
      "C": "It is faster than a Layer 4 Load Balancer.",
      "D": "It requires no CPU power."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is 'Anycast' routing?",
    "options": {
      "A": "Sending data to all servers in the world.",
      "B": "Routing traffic to the 'nearest' or 'best' destination among a group sharing the same IP.",
      "C": "Routing traffic only to the primary server.",
      "D": "A type of radio broadcast."
    },
    "answer": "B"
  },
  {
    "question": "True or False: In a 'Consistent Hashing' scheme, adding or removing a node only requires remapping a small fraction of keys.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO ways to reduce 'Tail Latency' (99th percentile):",
    "options": {
      "A": "Using redundant requests (hedging).",
      "B": "Improving resource isolation.",
      "C": "Increasing database log size.",
      "D": "Disabling the cache."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is 'Backpressure' in a distributed system?",
    "options": {
      "A": "Air pressure in the data center.",
      "B": "A mechanism where a system signals to producers to slow down because it is overwhelmed.",
      "C": "The force of a database backup.",
      "D": "A security attack slowing the network."
    },
    "answer": "B"
  },
  {
    "question": "What does the 'A' in ACID transactions stand for?",
    "options": {
      "A": "Availability",
      "B": "Atomicity",
      "C": "Accuracy",
      "D": "Agility"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Eventual Consistency'?",
    "options": {
      "A": "Data is never consistent.",
      "B": "Eventually all accesses will return the last updated value if no new updates occur.",
      "C": "Data is consistent across all nodes immediately.",
      "D": "Data is only consistent on the weekend."
    },
    "answer": "B"
  },
  {
    "question": "Which storage type is best for large amounts of unstructured data like images or videos?",
    "options": {
      "A": "Block Storage",
      "B": "Object Storage (e.g., S3)",
      "C": "Relational Tables",
      "D": "Stacks"
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Normalization' in a relational database is used to reduce data redundancy.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is a 'Hotspot' in a sharded database?",
    "options": {
      "A": "A server with a high-speed CPU.",
      "B": "A single shard that receives significantly more traffic than others, leading to a bottleneck.",
      "C": "A database being backed up.",
      "D": "A region with many data centers."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO common Cache Eviction policies:",
    "options": {
      "A": "LRU (Least Recently Used)",
      "B": "LFU (Least Frequently Used)",
      "C": "MFO (Most Frequently Opened)",
      "D": "RANDO (Random Only)"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What happens in a 'Cache Stampede'?",
    "options": {
      "A": "The cache grows too large for the disk.",
      "B": "Multiple processes try to read/write to the cache simultaneously after it expires, overwhelming the backend.",
      "C": "The cache is stolen by hackers.",
      "D": "The cache server reboots too fast."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Throttling' in the context of API management?",
    "options": {
      "A": "Speeding up the CPU.",
      "B": "Deliberately limiting request rates to maintain system stability.",
      "C": "Deleting outdated data from the cache.",
      "D": "Changing the name of an API version."
    },
    "answer": "B"
  },
  {
    "question": "What is the 'At-Least-Once' delivery guarantee?",
    "options": {
      "A": "A message might be lost.",
      "B": "A message is guaranteed to be delivered, but might be delivered more than once.",
      "C": "A message is delivered exactly once.",
      "D": "A message is only delivered if the user is online."
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Backend for Frontend' (BFF) pattern?",
    "options": {
      "A": "A backup for the frontend code.",
      "B": "Creating separate backend services tailored for different frontend types (Mobile vs. Web).",
      "C": "A way to hide CSS.",
      "D": "A tool for manual testing."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Auto-scaling'?",
    "options": {
      "A": "Manually adding RAM to a server.",
      "B": "Automatically adding or removing compute resources based on real-time traffic.",
      "C": "Deleting old user accounts.",
      "D": "Changing the size of the company logo."
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Canary Release'?",
    "options": {
      "A": "Releasing code only to users named Canary.",
      "B": "Rolling out an update to a small subset of users before making it available to everyone.",
      "C": "A security attack using birds.",
      "D": "Deleting the database after an update."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Graceful Degradation'?",
    "options": {
      "A": "The server crashing immediately.",
      "B": "The ability of a system to maintain limited functionality even when some components fail.",
      "C": "A type of code comment.",
      "D": "Deleting data to save space."
    },
    "answer": "B"
  },
  {
    "question": "Which term refers to a database's ability to remain available for writes even during a network partition?",
    "options": {
      "A": "Strong Consistency",
      "B": "High Availability",
      "C": "Strict Durability",
      "D": "Atomic Isolation"
    },
    "answer": "B"
  },
  {
    "question": "True or False: In a 'Write-Ahead Log' (WAL), changes are first recorded in a log before being applied to the actual database files.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO primary reasons for implementing 'Database Sharding':",
    "options": {
      "A": "To overcome the storage limits of a single machine.",
      "B": "To improve write throughput by distributing data across nodes.",
      "C": "To eliminate the need for backups.",
      "D": "To make SQL joins faster across different tables."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Normalization' in a relational database is used to reduce data redundancy.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is a 'Hotspot' in a sharded database?",
    "options": {
      "A": "A server with a high-speed CPU.",
      "B": "A single shard that receives significantly more traffic than others, leading to a bottleneck.",
      "C": "A database that is currently being backed up.",
      "D": "A region with many data centers."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO properties of 'Graph Databases' (e.g., Neo4j):",
    "options": {
      "A": "They excel at managing complex relationships between data points.",
      "B": "They use nodes, edges, and properties to represent data.",
      "C": "They are strictly used for social media profile storage only.",
      "D": "They do not support any form of ACID transactions."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Denormalization' is often used in read-heavy systems to improve query performance by reducing the number of joins.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which consistency model guarantees that if a process has updated a data item, any subsequent access by that process will return the updated value?",
    "options": {
      "A": "Monotonic Read Consistency",
      "B": "Read-Your-Writes Consistency",
      "C": "Eventual Consistency",
      "D": "Weak Consistency"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO common problems solved by 'Consistent Hashing':",
    "options": {
      "A": "Minimizing data movement when a new server is added to a cluster.",
      "B": "Ensuring a more even distribution of keys across cache nodes.",
      "C": "Encrypting data at rest.",
      "D": "Automatically deleting old log files."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A 'Wide-Column Store' (like Cassandra or HBase) is optimized for high-performance writes and large-scale data storage.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the primary role of a 'Database Index'?",
    "options": {
      "A": "To compress the size of the database.",
      "B": "To speed up data retrieval operations at the cost of slower writes.",
      "C": "To serve as a backup for the primary key.",
      "D": "To encrypt sensitive columns."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Strict Serializability' is the strongest consistency level, combining serializability and linearizability.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO types of 'Replication Lag' issues:",
    "options": {
      "A": "Reading stale data from a follower.",
      "B": "Write conflicts in a multi-leader setup.",
      "C": "High CPU usage on the master.",
      "D": "Network cable failures."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: In 'Quorum-based' consistency, R + W > N (where N is the number of replicas) ensures a client always reads the latest write.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which indexing structure is commonly used in Relational Databases for disk-based storage?",
    "options": {
      "A": "Hash Map",
      "B": "B+ Tree",
      "C": "Linked List",
      "D": "Binary Search Tree"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO advantages of 'NoSQL' over 'SQL':",
    "options": {
      "A": "Flexible schema (Dynamic).",
      "B": "Better suited for unstructured or rapidly changing data.",
      "C": "Always guarantees ACID transactions by default.",
      "D": "Better for complex multi-table joins."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'SSTables' (Sorted String Tables) are used in LSM-tree-based storage engines like those in Cassandra.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Optimistic Concurrency Control'?",
    "options": {
      "A": "Locking a row before reading it.",
      "B": "Allowing multiple transactions to proceed without locks, checking for conflicts only at the time of commit.",
      "C": "Assuming the database will never crash.",
      "D": "Using a single-threaded database engine."
    },
    "answer": "B"
  },
  {
    "question": "Which term describes a database that is spread across multiple physical locations?",
    "options": {
      "A": "Federated Database",
      "B": "Geo-distributed Database",
      "C": "Relational Database",
      "D": "Centralized Database"
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Columnar Storage' is more efficient than row-based storage for analytical queries (OLAP) that only access a few columns.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO characteristics of 'ACID' transactions:",
    "options": {
      "A": "Isolation: Transactions are executed as if they are the only ones in the system.",
      "B": "Durability: Once a transaction is committed, it remains committed even during a crash.",
      "C": "Availability: The system is always available for writes.",
      "D": "Elasticity: The database grows automatically."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Pessimistic Locking' is better for high-contention environments where conflicts are frequent.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which database type uses 'Keyspaces' and 'Column Families'?",
    "options": {
      "A": "Document Store",
      "B": "Wide-Column Store",
      "C": "Relational Store",
      "D": "Graph Store"
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Database Federation' allows a single query to access data from multiple separate databases as if they were one.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is a 'Deadlock' in database transactions?",
    "options": {
      "A": "When a database server is powered off.",
      "B": "When two or more transactions are each waiting for the other to release a lock.",
      "C": "When a query takes more than 10 seconds to run.",
      "D": "When a database reaches its storage limit."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO common 'Partitioning Keys' strategies:",
    "options": {
      "A": "Range-based partitioning.",
      "B": "Hash-based partitioning.",
      "C": "Color-based partitioning.",
      "D": "Random partitioning without a key."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A 'Materialized View' is a pre-computed table that stores the results of a query for faster access.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which term refers to the 'C' in the BASE model of distributed systems?",
    "options": {
      "A": "Consistency",
      "B": "Cheap",
      "C": "Clean",
      "D": "Correctness"
    },
    "answer": "B"
  },
  {
    "question": "True or False: In 'Primary-Secondary' replication, only the Primary node can handle write requests.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Secondary Indexing'?",
    "options": {
      "A": "A backup of the primary index.",
      "B": "An index created on any non-primary key column to speed up searches.",
      "C": "An index used only by the secondary server.",
      "D": "A type of database encryption."
    },
    "answer": "B"
  },
  {
    "question": "Where is a 'CDN' (Content Delivery Network) typically located?",
    "options": {
      "A": "Only in the primary data center.",
      "B": "Geographically distributed at the 'edge' of the network, closer to users.",
      "C": "Inside the user's browser only.",
      "D": "In the database layer."
    },
    "answer": "B"
  },
  {
    "question": "True or False: Caching reduces the load on the backend database by storing frequently accessed data in high-speed memory.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO common Cache Eviction policies:",
    "options": {
      "A": "LRU (Least Recently Used)",
      "B": "LFU (Least Frequently Used)",
      "C": "MFO (Most Frequently Opened)",
      "D": "RANDO (Random Only)"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A 'Write-through' cache updates both the cache and the underlying database at the same time.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is a 'Cache Hit'?",
    "options": {
      "A": "When the cache is deleted.",
      "B": "When requested data is found in the cache.",
      "C": "When the cache server crashes.",
      "D": "When data is written to the cache for the first time."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO benefits of using a CDN:",
    "options": {
      "A": "Reduced latency for global users.",
      "B": "Reduced bandwidth costs for the origin server.",
      "C": "Improved SQL query complexity.",
      "D": "Automated code debugging."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Cache Invalidation' is the process of declaring cached data as stale or invalid when the underlying data changes.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Redis'?",
    "options": {
      "A": "A programming language.",
      "B": "An in-memory data structure store, used as a database, cache, and message broker.",
      "C": "A type of network cable.",
      "D": "An operating system."
    },
    "answer": "B"
  },
  {
    "question": "True or False: Caching can be applied at multiple levels, including the browser, CDN, and server.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What happens in a 'Cache Stampede'?",
    "options": {
      "A": "The cache grows too large for the disk.",
      "B": "Multiple threads or processes try to read/write to the cache simultaneously after it expires, overwhelming the backend.",
      "C": "The cache is stolen by hackers.",
      "D": "The cache server reboots too fast."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Cache Penetration'?",
    "options": {
      "A": "When the cache is successfully accessed.",
      "B": "When requests for data that doesn't exist overwhelm the database because the cache can't store null results.",
      "C": "When a cache server is hacked.",
      "D": "When the cache is too small."
    },
    "answer": "B"
  },
  {
    "question": "True or False: A 'Read-through' cache is responsible for hitting the database and updating itself if the data is not present when requested.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO benefits of a 'Write-back' (Write-behind) cache:",
    "options": {
      "A": "High write throughput.",
      "B": "Reduced direct load on the database for write operations.",
      "C": "Guaranteed data safety in case of a cache crash.",
      "D": "Immediate data consistency between cache and DB."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Time to Live' (TTL) is a setting that determines how long an item remains in the cache before being discarded.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which problem occurs when a frequently accessed cache entry expires and a massive spike of requests hits the database simultaneously?",
    "options": {
      "A": "Cache Avalanche",
      "B": "Cache Breakthrough",
      "C": "Cache Warming",
      "D": "Cache Splitting"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO layers where a CDN provides the most value:",
    "options": {
      "A": "Static assets (JS, CSS, Images).",
      "B": "Video streaming content.",
      "C": "Highly dynamic, personalized user data.",
      "D": "Database write logs."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Cache Warming' is the process of pre-loading the cache with data before users start requesting it.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which HTTP header is used to control how a resource is cached by proxies and browsers?",
    "options": {
      "A": "Cache-Control",
      "B": "Set-Cookie",
      "C": "Content-Type",
      "D": "User-Agent"
    },
    "answer": "A"
  },
  {
    "question": "True or False: A 'Distributed Cache' (like Memcached or Redis) allows multiple application servers to share the same cached data.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is a 'Negative Cache'?",
    "options": {
      "A": "A cache that deletes data automatically.",
      "B": "Caching the fact that a resource does NOT exist to prevent repeated database lookups for missing keys.",
      "C": "A cache that is running out of space.",
      "D": "A cache used only for errors."
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Thundering Herd' problem in caching?",
    "options": {
      "A": "Too many servers joining a cluster.",
      "B": "Many processes waking up to handle the same event (like a cache miss) simultaneously.",
      "C": "A database running out of disk space.",
      "D": "A network cable failure."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Client-side Caching' happens entirely within the user's web browser.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO popular open-source caching engines:",
    "options": {
      "A": "Redis",
      "B": "Memcached",
      "C": "SQLite",
      "D": "Oracle"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Local Caching' on an application server is faster than 'Distributed Caching' but data is not shared across servers.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Cache Consistency'?",
    "options": {
      "A": "Ensuring the cache is the same size as the database.",
      "B": "Ensuring that the data in the cache matches the data in the underlying storage.",
      "C": "Making sure the cache never crashes.",
      "D": "Using the same password for all cache servers."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Lazy Loading' (Cache-aside) only loads data into the cache when it is explicitly requested by a user.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO common headers used for cache validation:",
    "options": {
      "A": "ETag",
      "B": "Last-Modified",
      "C": "Content-Length",
      "D": "Host"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: In an 'Event-Driven' architecture, components communicate by producing and consuming events.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which communication type is 'Fire and Forget'?",
    "options": {
      "A": "Synchronous",
      "B": "Asynchronous",
      "C": "Persistent",
      "D": "Encrypted"
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Polling' involves a client repeatedly asking a server if new data is available.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO benefits of Asynchronous communication:",
    "options": {
      "A": "Improved system responsiveness.",
      "B": "Better decoupling of services.",
      "C": "Guaranteed immediate response.",
      "D": "Simpler code logic."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is 'Idempotency' in message processing?",
    "options": {
      "A": "The ability to process the same message multiple times with the same result.",
      "B": "The ability to delete messages automatically.",
      "C": "Encrypting messages.",
      "D": "Sending messages faster."
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO common messaging patterns:",
    "options": {
      "A": "Point-to-Point",
      "B": "Publish/Subscribe (Pub/Sub)",
      "C": "Circle/Square",
      "D": "Up/Down"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is the 'At-Least-Once' delivery guarantee?",
    "options": {
      "A": "A message might be lost.",
      "B": "A message is guaranteed to be delivered, but might be delivered more than once.",
      "C": "A message is delivered exactly once.",
      "D": "A message is only delivered if the user is online."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Remote Procedure Call' (RPC) allows a program to execute a sub-routine in a different address space (another server).",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'Microservices' architectural style?",
    "options": {
      "A": "Building one giant application with all features.",
      "B": "Building an application as a suite of small, independently deployable services.",
      "C": "Using only small servers.",
      "D": "Using only one database for the entire company."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Service Discovery' is needed in microservices to help services find each other's dynamic IP addresses.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO common communication protocols for microservices:",
    "options": {
      "A": "HTTP/REST",
      "B": "gRPC",
      "C": "SMTP",
      "D": "FTP"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is the purpose of a 'Message Queue'?",
    "options": {
      "A": "To sort messages alphabetically.",
      "B": "To enable asynchronous communication between different parts of a system.",
      "C": "To store user passwords.",
      "D": "To speed up CSS rendering."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO popular Message Brokers:",
    "options": {
      "A": "RabbitMQ",
      "B": "Apache Kafka",
      "C": "Microsoft Word",
      "D": "Google Chrome"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is a 'Circuit Breaker' in system design?",
    "options": {
      "A": "A physical switch in the data center.",
      "B": "A design pattern used to detect failures and prevent a failing service from causing a system-wide crash.",
      "C": "A tool to delete unused code.",
      "D": "A type of network firewall."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Sidecar Pattern' involves attaching a helper service (like a logger or proxy) to a main application container.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO benefits of the 'Saga Pattern' in distributed transactions:",
    "options": {
      "A": "Managing data consistency across multiple microservices.",
      "B": "Replacing distributed ACID transactions with a sequence of local transactions.",
      "C": "Making SQL joins faster.",
      "D": "Encrypting the database."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A 'Service Mesh' (like Istio) manages service-to-service communication, often handling security and retries.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'CQRS' (Command Query Responsibility Segregation)?",
    "options": {
      "A": "A method to compress queries.",
      "B": "An architectural pattern that separates read and write operations for a data store.",
      "C": "A way to delete old records.",
      "D": "A type of network cable."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Database per Service' is a recommended pattern in microservices to ensure loose coupling.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'Backend for Frontend' (BFF) pattern?",
    "options": {
      "A": "A backup for the frontend code.",
      "B": "Creating separate backend services tailored for different frontend types (Mobile vs. Web).",
      "C": "A way to hide the CSS.",
      "D": "A tool for manual testing."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO strategies for 'Service Versioning':",
    "options": {
      "A": "URI Versioning (e.g., /api/v1/...)",
      "B": "Header Versioning (using custom HTTP headers)",
      "C": "Changing the name of the service daily.",
      "D": "Using different programming languages for each version."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Observability' in microservices includes logging, metrics, and distributed tracing.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which tool is commonly used for 'Distributed Tracing' to track requests across services?",
    "options": {
      "A": "Jaeger",
      "B": "Excel",
      "C": "Chrome",
      "D": "Photoshop"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO characteristics of 'Serverless' computing:",
    "options": {
      "A": "No need to manage server infrastructure.",
      "B": "Scales automatically based on incoming requests.",
      "C": "Servers are physically removed from the data center.",
      "D": "It is only used for database storage."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Vendor Lock-in' is a potential risk when using proprietary cloud-native services.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Auto-scaling'?",
    "options": {
      "A": "Manually adding RAM to a server.",
      "B": "Automatically adding or removing compute resources based on real-time traffic.",
      "C": "Deleting old user accounts.",
      "D": "Changing the size of the company logo."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Blue-Green Deployment' involves running two identical production environments to reduce downtime during updates.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is a 'Canary Release'?",
    "options": {
      "A": "Releasing code only to users named Canary.",
      "B": "Rolling out an update to a small subset of users before making it available to everyone.",
      "C": "A security attack using birds.",
      "D": "Deleting the database after an update."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO cloud deployment models:",
    "options": {
      "A": "Public Cloud",
      "B": "Private Cloud",
      "C": "Local Cloud",
      "D": "Personal Cloud"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Infrastructure as Code' (IaC) allows developers to manage and provision data centers through machine-readable definition files.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which tool is a popular example of Infrastructure as Code?",
    "options": {
      "A": "Terraform",
      "B": "Slack",
      "C": "Zoom",
      "D": "Spotify"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO benefits of 'Containerization' (e.g., Docker):",
    "options": {
      "A": "Consistency across different environments (Dev, Test, Prod).",
      "B": "Efficient resource utilization.",
      "C": "It makes the internet faster.",
      "D": "It automatically writes the documentation."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Kubernetes' is a container orchestration platform used to automate deployment and scaling.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Chaos Engineering'?",
    "options": {
      "A": "Deleting random code to see what happens.",
      "B": "The discipline of experimenting on a system in order to build confidence in the system's capability to withstand turbulent conditions.",
      "C": "Hiring chaotic developers.",
      "D": "A type of project management."
    },
    "answer": "B"
  },
  {
    "question": "True or False: A 'Service Level Agreement' (SLA) is a commitment between a service provider and a client regarding service standards.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Rate Limiting'?",
    "options": {
      "A": "Limiting the speed of the CPU.",
      "B": "Controlling the number of requests a user can make to an API in a given timeframe.",
      "C": "Limiting the number of developers on a project.",
      "D": "Reducing the cost of cloud services."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Log Aggregation' involves collecting logs from multiple services into a single, searchable location.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO key metrics for system monitoring:",
    "options": {
      "A": "CPU Utilization",
      "B": "Response Time (P99 latency)",
      "C": "Number of lines of code",
      "D": "Office temperature"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Sharding' a database is usually the first step to scale, before implementing caching.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Dead Letter Queue' (DLQ)?",
    "options": {
      "A": "A queue for emails that weren't opened.",
      "B": "A service for messages that cannot be processed successfully after multiple attempts.",
      "C": "A deleted database.",
      "D": "A type of security firewall."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Distributed Tracing' allows you to follow a single request as it travels through multiple microservices.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO common methods for 'API Authentication':",
    "options": {
      "A": "OAuth 2.0",
      "B": "API Keys",
      "C": "CSS Selectors",
      "D": "HTML Tags"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "Final question of Batch 3: True or False: A 'WAF' (Web Application Firewall) helps protect web applications by filtering and monitoring HTTP traffic.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Data Partitioning'?",
    "options": {
      "A": "Deleting data in sections.",
      "B": "Dividing a dataset into several small parts to be stored and managed across multiple nodes.",
      "C": "Changing the format of data from JSON to XML.",
      "D": "Printing data on paper."
    },
    "answer": "B"
  },
  {
    "question": "Which mechanism is used to ensure that a system doesn't get overwhelmed by a sudden spike in traffic by dropping low-priority requests?",
    "options": {
      "A": "Load Shedding",
      "B": "Data Mining",
      "C": "Code Refactoring",
      "D": "Manual Restart"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO benefits of 'Infrastructure as Code' (IaC):",
    "options": {
      "A": "Version control for infrastructure changes.",
      "B": "Faster and more reliable environment provisioning.",
      "C": "It physically builds the servers in the data center.",
      "D": "It eliminates the need for an internet connection."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Graceful Degradation' is the ability of a system to maintain limited functionality even when some of its components have failed.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Cold Storage' in system design?",
    "options": {
      "A": "A server kept in a freezer.",
      "B": "Storage for data that is rarely accessed but must be preserved for long periods (e.g., AWS Glacier).",
      "C": "A database that has been shut down.",
      "D": "Storage that is only available in winter."
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm is commonly used to maintain 'Leader Election' in a distributed cluster?",
    "options": {
      "A": "Paxos or Raft",
      "B": "Bubble Sort",
      "C": "Binary Search",
      "D": "Round Robin"
    },
    "answer": "A"
  },
  {
    "question": "True or False: A 'Bloom Filter' is a space-efficient probabilistic data structure used to test whether an element is a member of a set, allowing for false positives but no false negatives.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO characteristics of 'Stateless' architecture:",
    "options": {
      "A": "No client data is stored on the server between requests.",
      "B": "Scaling is generally easier because any server can handle any request.",
      "C": "The server remembers the user's last action automatically.",
      "D": "It requires a permanent persistent socket connection."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Data Sovereignty' refers to the concept that data is subject to the laws and governance structures within the nation it is collected.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Multi-Tenancy'?",
    "options": {
      "A": "One user having multiple accounts.",
      "B": "An architecture where a single instance of software serves multiple customers (tenants), sharing resources while keeping data isolated.",
      "C": "Hiring multiple developers for one project.",
      "D": "Connecting a server to multiple power outlets."
    },
    "answer": "B"
  },
  {
    "question": "Which strategy involves directing users to the data center closest to them to minimize latency?",
    "options": {
      "A": "Geo-routing",
      "B": "Random routing",
      "C": "Alphabetical routing",
      "D": "Fixed routing"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO 'Disaster Recovery' metrics used to define business continuity plans:",
    "options": {
      "A": "RTO (Recovery Time Objective)",
      "B": "RPO (Recovery Point Objective)",
      "C": "FPS (Frames Per Second)",
      "D": "CPU Clock Speed"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Object-Relational Mapping' (ORM) is a technique used to query and manipulate data from a database using an object-oriented paradigm.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO common 'Anti-Patterns' in system design:",
    "options": {
      "A": "The God Object (a single class/service that does too much).",
      "B": "Spilled Milk (ignoring errors).",
      "C": "Golden Hammer (using the same tool for every problem regardless of fit).",
      "D": "Clean Code (following standard style guides)."
    },
    "answer": ["A", "C"]
  },
  {
    "question": "True or False: 'Linearizability' is a strong consistency guarantee where every operation appears to take place instantaneously at some point between its invocation and its response.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is a 'B-Tree' primarily used for in databases?",
    "options": {
      "A": "A tree that only grows in winter.",
      "B": "A self-balancing tree data structure that keeps data sorted and allows for efficient searches and sequential access.",
      "C": "A type of binary heap for priority queues.",
      "D": "A graph with no edges used for visualization."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Micro-frontends' is an architectural style where independently deliverable frontend applications are composed into a whole.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Dark Launching'?",
    "options": {
      "A": "Launching an app at night.",
      "B": "Releasing a feature to a small subset of users to test performance/usage without the feature being visible in the UI.",
      "C": "Deleting a feature secretly from the codebase.",
      "D": "Moving a data center to an underground location."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO components of a standard 'Logging Stack' (e.g., ELK or EFK):",
    "options": {
      "A": "Elasticsearch (Search and Indexing)",
      "B": "Logstash or Fluentd (Data Processing)",
      "C": "Excel (Data Visualization)",
      "D": "Microsoft Word (Report Writing)"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is a 'Service Level Indicator' (SLI)?",
    "options": {
      "A": "A specific quantitative measure of some aspect of the level of service provided (e.g., latency, throughput).",
      "B": "A physical LED light on a server rack.",
      "C": "The person responsible for checking server status.",
      "D": "A legal contract signed by the CEO."
    },
    "answer": "A"
  },
  {
    "question": "What is 'Data Partitioning'?",
    "options": {
      "A": "Deleting data in sections.",
      "B": "Dividing a dataset into several small parts to be stored and managed across multiple nodes.",
      "C": "Changing the format of data from JSON to XML.",
      "D": "Printing data on paper."
    },
    "answer": "B"
  },
  {
    "question": "Which mechanism is used to ensure that a system doesn't get overwhelmed by a sudden spike in traffic by dropping low-priority requests?",
    "options": {
      "A": "Load Shedding",
      "B": "Data Mining",
      "C": "Code Refactoring",
      "D": "Manual Restart"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO benefits of 'Infrastructure as Code' (IaC):",
    "options": {
      "A": "Version control for infrastructure changes.",
      "B": "Faster and more reliable environment provisioning.",
      "C": "It physically builds the servers in the data center.",
      "D": "It eliminates the need for an internet connection."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Graceful Degradation' is the ability of a system to maintain limited functionality even when some of its components have failed.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Cold Storage' in system design?",
    "options": {
      "A": "A server kept in a freezer.",
      "B": "Storage for data that is rarely accessed but must be preserved for long periods (e.g., AWS Glacier).",
      "C": "A database that has been shut down.",
      "D": "Storage that is only available in winter."
    },
    "answer": "B"
  },
  {
    "question": "Which algorithm is commonly used to maintain 'Leader Election' in a distributed cluster?",
    "options": {
      "A": "Paxos or Raft",
      "B": "Bubble Sort",
      "C": "Binary Search",
      "D": "Round Robin"
    },
    "answer": "A"
  },
  {
    "question": "True or False: A 'Bloom Filter' is a space-efficient probabilistic data structure used to test whether an element is a member of a set, allowing for false positives but no false negatives.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO characteristics of 'Stateless' architecture:",
    "options": {
      "A": "No client data is stored on the server between requests.",
      "B": "Scaling is generally easier because any server can handle any request.",
      "C": "The server remembers the user's last action automatically.",
      "D": "It requires a permanent persistent socket connection."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Data Sovereignty' refers to the concept that data is subject to the laws and governance structures within the nation it is collected.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Multi-Tenancy'?",
    "options": {
      "A": "One user having multiple accounts.",
      "B": "An architecture where a single instance of software serves multiple customers (tenants), sharing resources while keeping data isolated.",
      "C": "Hiring multiple developers for one project.",
      "D": "Connecting a server to multiple power outlets."
    },
    "answer": "B"
  },
  {
    "question": "Which strategy involves directing users to the data center closest to them to minimize latency?",
    "options": {
      "A": "Geo-routing",
      "B": "Random routing",
      "C": "Alphabetical routing",
      "D": "Fixed routing"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO 'Disaster Recovery' metrics used to define business continuity plans:",
    "options": {
      "A": "RTO (Recovery Time Objective)",
      "B": "RPO (Recovery Point Objective)",
      "C": "FPS (Frames Per Second)",
      "D": "CPU Clock Speed"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Object-Relational Mapping' (ORM) is a technique used to query and manipulate data from a database using an object-oriented paradigm.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO common 'Anti-Patterns' in system design:",
    "options": {
      "A": "The God Object (a single class/service that does too much).",
      "B": "Spilled Milk (ignoring errors).",
      "C": "Golden Hammer (using the same tool for every problem regardless of fit).",
      "D": "Clean Code (following standard style guides)."
    },
    "answer": ["A", "C"]
  },
  {
    "question": "True or False: 'Linearizability' is a strong consistency guarantee where every operation appears to take place instantaneously at some point between its invocation and its response.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is a 'B-Tree' primarily used for in databases?",
    "options": {
      "A": "A tree that only grows in winter.",
      "B": "A self-balancing tree data structure that keeps data sorted and allows for efficient searches and sequential access.",
      "C": "A type of binary heap for priority queues.",
      "D": "A graph with no edges used for visualization."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Micro-frontends' is an architectural style where independently deliverable frontend applications are composed into a whole.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Dark Launching'?",
    "options": {
      "A": "Launching an app at night.",
      "B": "Releasing a feature to a small subset of users to test performance/usage without the feature being visible in the UI.",
      "C": "Deleting a feature secretly from the codebase.",
      "D": "Moving a data center to an underground location."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO components of a standard 'Logging Stack' (e.g., ELK or EFK):",
    "options": {
      "A": "Elasticsearch (Search and Indexing)",
      "B": "Logstash or Fluentd (Data Processing)",
      "C": "Excel (Data Visualization)",
      "D": "Microsoft Word (Report Writing)"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is a 'Service Level Indicator' (SLI)?",
    "options": {
      "A": "A specific quantitative measure of some aspect of the level of service provided (e.g., latency, throughput).",
      "B": "A physical LED light on a server rack.",
      "C": "The person responsible for checking server status.",
      "D": "A legal contract signed by the CEO."
    },
    "answer": "A"
  },
  {
    "question": "Which consistency model ensures that if process A has communicated to process B that it has updated a data item, a subsequent access by process B will return the updated value?",
    "options": {
      "A": "Causal Consistency",
      "B": "Weak Consistency",
      "C": "Eventual Consistency",
      "D": "Monotonic Read Consistency"
    },
    "answer": "A"
  },
  {
    "question": "What is the primary role of a 'Service Mesh' sidecar proxy?",
    "options": {
      "A": "To store the application's database",
      "B": "To handle service-to-service communication, including retries, timeouts, and mTLS",
      "C": "To act as the primary user-facing UI",
      "D": "To compile the application source code"
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Change Data Capture' (CDC) is a process that identifies and captures changes made to a database so that action can be taken using the change data.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Stream Processing' in system design?",
    "options": {
      "A": "Processing data in large batches once a day",
      "B": "The real-time processing of data continuously as it is generated by sources",
      "C": "Watching a video stream on a server",
      "D": "Compressing old log files"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO common 'Leader Election' algorithms used in distributed systems:",
    "options": {
      "A": "Raft",
      "B": "Paxos",
      "C": "Dijkstra",
      "D": "A* Search"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What does 'Fencing' prevent in a distributed system with a leader?",
    "options": {
      "A": "Split-brain (where two nodes believe they are both the leader simultaneously)",
      "B": "A server from overheating",
      "C": "Users from accessing the API",
      "D": "The database from growing too large"
    },
    "answer": "A"
  },
  {
    "question": "True or False: 'Log-Structured Merge-Trees' (LSM-Trees) are optimized for high-write throughput by turning random writes into sequential writes.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Write Amplification' in a database system?",
    "options": {
      "A": "Making the font of the code larger",
      "B": "The phenomenon where the amount of data physically written to storage is a multiple of the data logically written by the application",
      "C": "Adding more hard drives to a cluster",
      "D": "Increasing the volume of system alerts"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO characteristics of an 'Idempotent' API operation:",
    "options": {
      "A": "It can be called multiple times without changing the result beyond the initial call",
      "B": "It helps in safely retrying failed network requests",
      "C": "It is always slower than non-idempotent operations",
      "D": "It requires the server to be in 'Maintenance Mode'"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is a 'Saga' in microservices?",
    "options": {
      "A": "A long story about a developer",
      "B": "A sequence of local transactions that helps maintain data consistency across multiple services without distributed locks",
      "C": "A type of high-speed network cable",
      "D": "A specific version of the Linux kernel"
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Pre-signed URLs' allow users to upload or download specific objects to a cloud bucket without requiring AWS/Cloud credentials.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which term describes the strategy of sending a request to multiple replicas and using the first response that arrives?",
    "options": {
      "A": "Hedging Requests",
      "B": "Load Balancing",
      "C": "Round Robin",
      "D": "Caching"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Data Gravity'?",
    "options": {
      "A": "The weight of a physical server",
      "B": "The idea that as data sets grow large, applications and services are naturally drawn toward them to minimize latency",
      "C": "The force that deletes old files",
      "D": "A type of encryption used in space"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO common components of an 'API Gateway':",
    "options": {
      "A": "Authentication and Authorization",
      "B": "Rate Limiting and Quota Management",
      "C": "Hard Drive partitioning",
      "D": "CSS style injection"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'TCP Keepalive' is used to check if a connection is still active and prevent it from being timed out by intermediaries.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Fan-out' in a messaging system?",
    "options": {
      "A": "Turning on the server cooling fans",
      "B": "The process of delivering a single message to multiple destinations or subscribers simultaneously",
      "C": "Reducing the number of users on a system",
      "D": "A type of network loop error"
    },
    "answer": "B"
  },
  {
    "question": "Which pattern involves a service pushing its state changes to a 'Read Model' that is optimized for queries?",
    "options": {
      "A": "CQRS (Command Query Responsibility Segregation)",
      "B": "Active Record",
      "C": "Singleton",
      "D": "Model-View-Controller"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Service Discovery' primarily used for?",
    "options": {
      "A": "Finding new open-source projects on GitHub",
      "B": "Automatically detecting the network locations of service instances which may have dynamic IP addresses",
      "C": "Searching for bugs in a local environment",
      "D": "Identifying the hardware manufacturer of a server"
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Consistent Hashing' is used to ensure that when the number of cache servers changes, only $1/n$ of the keys need to be remapped.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the function of a 'Gossip Protocol' in a distributed cluster?",
    "options": {
      "A": "To share developer rumors",
      "B": "To spread state information (like node health) across a decentralized network using a peer-to-peer approach",
      "C": "To encrypt user passwords",
      "D": "To restart the primary database"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary purpose of a 'Distributed Lock' (e.g., using Redis Redlock or Zookeeper)?",
    "options": {
      "A": "To lock the server room door remotely",
      "B": "To ensure that only one process across a distributed system can access a shared resource at a time",
      "C": "To encrypt the database password",
      "D": "To prevent users from logging out"
    },
    "answer": "B"
  },
  {
    "question": "In the context of 'Disaster Recovery', what does RTO (Recovery Time Objective) represent?",
    "options": {
      "A": "The amount of data loss that is acceptable",
      "B": "The maximum targeted duration of time a system can be down after a failure",
      "C": "The cost of the backup servers",
      "D": "The speed of the internet connection during a crash"
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Horizontal Partitioning' (Sharding) involves putting different rows of a single table into multiple different databases.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Vertical Partitioning' in database design?",
    "options": {
      "A": "Splitting a table by rows",
      "B": "Dividing a table into multiple tables with fewer columns, often based on access patterns",
      "C": "Moving the database to a taller server rack",
      "D": "Increasing the size of every column"
    },
    "answer": "B"
  },
  {
    "question": "Which of these is a 'Probabilistic Data Structure' used to check if an element exists in a set with very low memory overhead?",
    "options": {
      "A": "B-Tree",
      "B": "Bloom Filter",
      "C": "Linked List",
      "D": "Hash Map"
    },
    "answer": "B"
  },
  {
    "question": "What is the function of a 'Heartbeat' mechanism in a cluster?",
    "options": {
      "A": "To play a sound when the server is happy",
      "B": "A periodic signal sent by a node to the master or other nodes to indicate it is still alive",
      "C": "To measure the CPU's clock speed",
      "D": "To count the number of active users"
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Quorum' is the minimum number of votes that a distributed transaction or operation must obtain to be allowed to proceed.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Write-Ahead Logging' (WAL) used for?",
    "options": {
      "A": "To record user login times",
      "B": "To provide durability and atomicity by ensuring data changes are written to a log before the database file",
      "C": "To speed up CSS rendering",
      "D": "To track the location of the mouse cursor"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO common strategies for 'Caching Invalidation':",
    "options": {
      "A": "TTL (Time to Live)",
      "B": "Write-through",
      "C": "Manual file deletion",
      "D": "Random server reboots"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What does 'Split-Brain' refer to in a distributed system?",
    "options": {
      "A": "A developer working on two features at once",
      "B": "A condition where a cluster divides into two or more independent parts, each believing it is the leader",
      "C": "Running a database on two different operating systems",
      "D": "A type of memory corruption"
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Consistent Hashing' minimizes the number of keys that need to be remapped when a node is added or removed from a cache cluster.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Geo-Replication'?",
    "options": {
      "A": "Replicating data between two folders on the same disk",
      "B": "Storing copies of data in multiple geographically distant locations for low latency and high availability",
      "C": "Tracking the GPS location of all users",
      "D": "A way to draw maps using data"
    },
    "answer": "B"
  },
  {
    "question": "Which of these is an example of an 'In-Memory' database often used for ultra-low latency caching?",
    "options": {
      "A": "PostgreSQL",
      "B": "Redis",
      "C": "Oracle DB",
      "D": "Microsoft SQL Server"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Throughput' in a system?",
    "options": {
      "A": "The time it takes to process a single request",
      "B": "The total number of units of work (requests) processed in a specific time period",
      "C": "The distance data travels over fiber cables",
      "D": "The size of the hard drive"
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Load Shedding' is the intentional dropping of low-priority requests to protect a system from total failure during a spike.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'Cold Start' problem in Serverless computing?",
    "options": {
      "A": "The server room is too cold to start",
      "B": "The latency experienced when a function is invoked for the first time or after a period of inactivity",
      "C": "The database taking too long to back up",
      "D": "A type of hardware failure in winter"
    },
    "answer": "B"
  },
  {
    "question": "Which pattern is used to aggregate logs from multiple services into a central searchable store?",
    "options": {
      "A": "Log Aggregation (e.g., ELK stack)",
      "B": "Singleton",
      "C": "Model-View-Controller",
      "D": "Observer"
    },
    "answer": "A"
  },
  {
    "question": "True or False: 'Multi-AZ' (Availability Zone) deployment ensures that a system can survive the total failure of a single data center.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'API Throttling'?",
    "options": {
      "A": "Increasing the speed of the API",
      "B": "The process of limiting the number of API requests a user can make within a certain timeframe",
      "C": "Deleting old API keys",
      "D": "Changing the API version number"
    },
    "answer": "B"
  },
  {
    "question": "Final Question: Which term refers to the practice of simulating failures in production to test system resilience?",
    "options": {
      "A": "Unit Testing",
      "B": "Chaos Engineering",
      "C": "Performance Tuning",
      "D": "Manual QA"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Two-Phase Commit' (2PC) protocol used for?",
    "options": {
      "A": "To speed up the server boot process",
      "B": "To achieve atomic transaction commit in a distributed system across multiple nodes",
      "C": "To encrypt user data in two separate layers",
      "D": "To perform a double-entry backup of the database"
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Linearizability' ensures that if one operation is completed, any subsequent operation must see the result of that operation or a later one.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which messaging concept describes a message being moved to a separate queue after failing multiple delivery attempts?",
    "options": {
      "A": "Primary Queue",
      "B": "Dead Letter Queue (DLQ)",
      "C": "Garbage Queue",
      "D": "Buffered Storage"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Write Amplification' in the context of SSD-based database storage?",
    "options": {
      "A": "Increasing the volume of system alerts",
      "B": "The phenomenon where the actual amount of data written to storage is much higher than the data logically written by the application",
      "C": "Adding more hard drives to a cluster",
      "D": "Making the font of the database logs larger"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO common 'Health Check' types used by load balancers to monitor backend status:",
    "options": {
      "A": "TCP Handshake",
      "B": "HTTP GET to a /health endpoint",
      "C": "Manual ping from a developer's computer",
      "D": "Visual inspection of the server rack"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: 'Service Discovery' allows services to find each other without having hardcoded IP addresses in their configuration files.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Backpressure' in a streaming data pipeline?",
    "options": {
      "A": "Air pressure inside the server cooling system",
      "B": "A mechanism that tells upstream systems to slow down their data rate when downstream systems are overwhelmed",
      "C": "The force of a database backup being restored",
      "D": "A type of network attack that slows down traffic"
    },
    "answer": "B"
  },
  {
    "question": "Which term describes a database that is optimized for 'Write-Heavy' workloads by appending data to an immutable log?",
    "options": {
      "A": "Relational Database",
      "B": "Log-Structured Merge-Tree (LSM-Tree)",
      "C": "Flat File System",
      "D": "Cache-only Database"
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Eventually Consistent' systems are usually faster and more available than 'Strongly Consistent' systems.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Fan-out' in an event-driven architecture?",
    "options": {
      "A": "Turning on the server's fans to cool it down",
      "B": "A single event triggering multiple downstream actions or being sent to multiple subscribers",
      "C": "A database query that touches every row in a table",
      "D": "Reducing the number of users on a platform"
    },
    "answer": "B"
  },
  {
    "question": "In a 'Shared-Nothing' architecture, which of the following is true?",
    "options": {
      "A": "All nodes share the same physical RAM",
      "B": "Each node is independent and self-sufficient, with its own CPU and memory",
      "C": "The system cannot be scaled horizontally",
      "D": "There is only one master node and no followers"
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
    skill = "SystemDesign"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
