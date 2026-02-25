from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
    {
        "question": "What is Apache Kafka primarily defined as?",
        "options": {
            "A": "A relational database",
            "B": "A distributed event streaming platform",
            "C": "A web server",
            "D": "A spreadsheet application"
        },
        "answer": "B"
    },
    {
        "question": "Which company originally developed Kafka?",
        "options": {
            "A": "Google",
            "B": "LinkedIn",
            "C": "Facebook",
            "D": "Amazon"
        },
        "answer": "B"
    },
    {
        "question": "In Kafka, what is a 'Topic'?",
        "options": {
            "A": "A physical server",
            "B": "A category or feed name to which records are published",
            "C": "A specific user account",
            "D": "A type of data encryption"
        },
        "answer": "B"
    },
    {
        "question": "What are 'Producers' in the Kafka ecosystem?",
        "options": {
            "A": "Applications that read data",
            "B": "Applications that publish (write) data to Kafka topics",
            "C": "Servers that store data",
            "D": "Tools that delete old messages"
        },
        "answer": "B"
    },
    {
        "question": "What are 'Consumers' in Kafka?",
        "options": {
            "A": "Applications that write data",
            "B": "Applications that subscribe to (read) and process data from topics",
            "C": "Hardware firewalls",
            "D": "Database administrators"
        },
        "answer": "B"
    },
    {
        "question": "Kafka is designed to be a distributed system. What is a single Kafka server called?",
        "options": {
            "A": "Node",
            "B": "Broker",
            "C": "Agent",
            "D": "Instance"
        },
        "answer": "B"
    },
    {
        "question": "To scale a topic, Kafka divides it into several __________.",
        "options": {
            "A": "Segments",
            "B": "Partitions",
            "C": "Slices",
            "D": "Fragments"
        },
        "answer": "B"
    },
    {
        "question": "What is an 'Offset' in Kafka?",
        "options": {
            "A": "The time a message was sent",
            "B": "A unique sequential ID assigned to each message within a partition",
            "C": "The size of the message in bytes",
            "D": "The distance between two brokers"
        },
        "answer": "B"
    },
    {
        "question": "How long does Kafka retain messages by default?",
        "options": {
            "A": "Until they are read",
            "B": "7 days",
            "C": "24 hours",
            "D": "Forever"
        },
        "answer": "B"
    },
    {
        "question": "Which component was traditionally used by Kafka to manage cluster metadata and leadership (pre-KRaft)?",
        "options": {
            "A": "Redis",
            "B": "Zookeeper",
            "C": "Elasticsearch",
            "D": "YARN"
        },
        "answer": "B"
    },
    {
        "question": "What is the newer, Zookeeper-less consensus mechanism in Kafka called?",
        "options": {
            "A": "K-Mesh",
            "B": "KRaft",
            "C": "K-Sync",
            "D": "K-Logic"
        },
        "answer": "B"
    },
    {
        "question": "Kafka provides strict ordering of messages at which level?",
        "options": {
            "A": "The Topic level",
            "B": "The Partition level",
            "C": "The Broker level",
            "D": "The Consumer Group level"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Consumer Group' in Kafka?",
        "options": {
            "A": "A group of people using Kafka",
            "B": "A set of consumers who cooperate to consume data from a topic",
            "C": "A list of topics",
            "D": "A backup cluster"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is a core guarantee provided by Kafka?",
        "options": {
            "A": "At-least-once delivery",
            "B": "Message persistence on disk",
            "C": "High availability through replication",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "What does 'Replication Factor' define?",
        "options": {
            "A": "How fast data is copied",
            "B": "The number of copies of data maintained across the cluster",
            "C": "The number of partitions per topic",
            "D": "The number of consumers in a group"
        },
        "answer": "B"
    },
    {
        "question": "In a partitioned topic, which partition copy handles all read and write requests?",
        "options": {
            "A": "Follower",
            "B": "Leader",
            "C": "Master",
            "D": "Primary"
        },
        "answer": "B"
    },
    {
        "question": "What is an 'In-Sync Replica' (ISR)?",
        "options": {
            "A": "A copy that is currently being deleted",
            "B": "A follower that is caught up with the leader's log",
            "C": "A backup server in a different city",
            "D": "A consumer that has read all messages"
        },
        "answer": "B"
    },
    {
        "question": "Which tool is used for streaming data between Kafka and other systems (like databases)?",
        "options": {
            "A": "Kafka Streams",
            "B": "Kafka Connect",
            "C": "Kafka Bridge",
            "D": "Kafka Flow"
        },
        "answer": "B"
    },
    {
        "question": "Which Kafka library is used for building real-time applications that process data within Kafka?",
        "options": {
            "A": "Kafka Connect",
            "B": "Kafka Streams",
            "C": "Kafka Producer API",
            "D": "Kafka Logic"
        },
        "answer": "B"
    },
    {
        "question": "What is 'ksqlDB'?",
        "options": {
            "A": "A new version of MySQL",
            "B": "An event streaming database that allows processing Kafka data using SQL",
            "C": "A database for storing Kafka logs",
            "D": "A tool to monitor broker hardware"
        },
        "answer": "B"
    },
    {
        "question": "How does a Producer decide which partition to send a message to if no key is provided?",
        "options": {
            "A": "It sends to all partitions",
            "B": "It uses a round-robin approach (or sticky partitioning)",
            "C": "It sends to the Leader only",
            "D": "It throws an error"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Log Compaction' in Kafka?",
        "options": {
            "A": "Deleting all old messages",
            "B": "A mechanism that ensures Kafka retains at least the last known value for each message key",
            "C": "Zipping log files to save space",
            "D": "Encrypted message storage"
        },
        "answer": "B"
    },
    {
        "question": "Which of the following is a primary use case for Kafka?",
        "options": {
            "A": "Messaging",
            "B": "Website Activity Tracking",
            "C": "Log Aggregation",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "What happens when a new consumer joins a Consumer Group?",
        "options": {
            "A": "It waits until the others finish",
            "B": "A 'Rebalance' occurs to redistribute partitions among members",
            "C": "The group is deleted",
            "D": "It starts reading from offset 0"
        },
        "answer": "B"
    },
    {
        "question": "What is the default port for Kafka brokers?",
        "options": {
            "A": "2181",
            "B": "9092",
            "C": "8080",
            "D": "3306"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Zero Copy' in Kafka?",
        "options": {
            "A": "Data is not replicated",
            "B": "A performance optimization where data is sent from disk to network without being copied into application space",
            "C": "No messages are lost",
            "D": "Consumers do not store copies of data"
        },
        "answer": "B"
    },
    {
        "question": "A Kafka record consists of which four parts?",
        "options": {
            "A": "ID, Name, Date, Size",
            "B": "Key, Value, Timestamp, Headers",
            "C": "Topic, Partition, Offset, Broker",
            "D": "User, Password, Host, Port"
        },
        "answer": "B"
    },
    {
        "question": "What is the role of the 'Controller' broker in a cluster?",
        "options": {
            "A": "To handle all client requests",
            "B": "To manage partition leadership and administrative tasks",
            "C": "To store the most data",
            "D": "To monitor network bandwidth"
        },
        "answer": "B"
    },
    {
        "question": "What does 'Batching' in Producers help with?",
        "options": {
            "A": "Security",
            "B": "Increasing throughput by sending multiple records in a single request",
            "C": "Deleting data",
            "D": "Sorting messages"
        },
        "answer": "B"
    },
    {
        "question": "Which parameter controls the maximum size of a single request sent by a Producer?",
        "options": {
            "A": "request.timeout.ms",
            "B": "max.request.size",
            "C": "batch.size",
            "D": "buffer.memory"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Consumer Lag'?",
        "options": {
            "A": "The time it takes to install Kafka",
            "B": "The difference between the latest message in a partition and the last message read by the consumer",
            "C": "The network speed",
            "D": "The number of brokers offline"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Commit' in the context of a Consumer?",
        "options": {
            "A": "Saving a file to disk",
            "B": "Updating the offset of the last successfully processed message",
            "C": "Joining a new group",
            "D": "Deleting a topic"
        },
        "answer": "B"
    },
    {
        "question": "Where are consumer offsets stored in modern Kafka versions (since 0.9)?",
        "options": {
            "A": "In Zookeeper",
            "B": "In an internal Kafka topic named __consumer_offsets",
            "C": "In a local text file",
            "D": "In a MySQL database"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Exactly-Once Semantics' (EOS) in Kafka?",
        "options": {
            "A": "Messages are sent only once and never arrive",
            "B": "A guarantee that messages are processed exactly once, even if failures occur",
            "C": "Every consumer sees only one message",
            "D": "There is only one partition per topic"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is NOT a supported 'acks' (acknowledgment) setting for Producers?",
        "options": {
            "A": "acks=0",
            "B": "acks=1",
            "C": "acks=all",
            "D": "acks=2"
        },
        "answer": "D"
    },
    {
        "question": "What does 'acks=all' guarantee?",
        "options": {
            "A": "No acknowledgment is needed",
            "B": "The leader and all in-sync replicas have received the data",
            "C": "Only the leader has received the data",
            "D": "The consumer has read the data"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Retention Policy' in Kafka?",
        "options": {
            "A": "The price of the software",
            "B": "Rules that determine how long Kafka keeps data before deleting it",
            "C": "The policy for hiring engineers",
            "D": "A way to speed up the brokers"
        },
        "answer": "B"
    },
    {
        "question": "In Kafka terminology, what is 'Throughput'?",
        "options": {
            "A": "The total storage capacity",
            "B": "The rate at which data is processed (messages per second or MB/s)",
            "C": "The number of users connected",
            "D": "The length of a message"
        },
        "answer": "B"
    },
    {
        "question": "Which component manages the schemas for Kafka message keys and values?",
        "options": {
            "A": "Kafka Connect",
            "B": "Schema Registry",
            "C": "Zookeeper",
            "D": "Admin Client"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary language used to build the core of Apache Kafka?",
        "options": {
            "A": "Java and Scala",
            "B": "Python",
            "C": "C++",
            "D": "Go"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of 'Partitions'?",
        "options": {
            "A": "To secure data",
            "B": "To allow for parallelism and load balancing",
            "C": "To backup the metadata",
            "D": "To limit message size"
        },
        "answer": "B"
    },
    {
        "question": "What is 'End-to-End Latency' in Kafka?",
        "options": {
            "A": "The time a message stays in the buffer",
            "B": "The time from when a message is produced until it is available for consumption",
            "C": "The time to restart a broker",
            "D": "The size of the network cable"
        },
        "answer": "B"
    },
    {
        "question": "What happens if a partition has no leader?",
        "options": {
            "A": "Data is lost",
            "B": "The partition becomes unavailable for reads and writes until a new leader is elected",
            "C": "A follower automatically takes over without election",
            "D": "The topic is deleted"
        },
        "answer": "B"
    },
    {
        "question": "Which setting controls how long Kafka waits for more data to arrive before sending a batch in the Producer?",
        "options": {
            "A": "batch.size",
            "B": "linger.ms",
            "C": "timeout.ms",
            "D": "buffer.memory"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Compression' used for in Kafka?",
        "options": {
            "A": "To encrypt messages",
            "B": "To reduce network bandwidth and disk storage usage",
            "C": "To shorten the keys",
            "D": "To increase the number of brokers"
        },
        "answer": "B"
    },
    {
        "question": "What does a 'Rebalance' in a consumer group do?",
        "options": {
            "A": "Restarts the brokers",
            "B": "Redistributes partition ownership among the available consumers",
            "C": "Deletes duplicate messages",
            "D": "Updates the topic schema"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is a popular serialization format used with Kafka?",
        "options": {
            "A": "Avro",
            "B": "Protobuf",
            "C": "JSON",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "What is 'At-Most-Once' delivery?",
        "options": {
            "A": "Messages are never lost",
            "B": "Messages may be lost but are never redelivered",
            "C": "Messages are delivered twice",
            "D": "The consumer only reads once"
        },
        "answer": "B"
    },
    {
        "question": "What is 'At-Least-Once' delivery?",
        "options": {
            "A": "Messages are never delivered",
            "B": "Messages are never lost but may be redelivered/duplicated",
            "C": "Messages are deleted after reading",
            "D": "The producer only sends once"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary benefit of Kafka's 'Sequential I/O' on disk?",
        "options": {
            "A": "It is more secure",
            "B": "It is extremely fast compared to random I/O, allowing disk to perform like RAM",
            "C": "It uses less power",
            "D": "It prevents data corruption"
        },
        "answer": "B"
    },
        {
        "question": "Which Producer configuration controls how many retries are attempted before a request fails?",
        "options": {
            "A": "max.retries",
            "B": "retries",
            "C": "retry.backoff.ms",
            "D": "attempt.count"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary role of the 'Key' in a ProducerRecord?",
        "options": {
            "A": "To encrypt the message",
            "B": "To determine which partition the message is sent to (affinity)",
            "C": "To act as a password",
            "D": "To name the topic"
        },
        "answer": "B"
    },
    {
        "question": "If multiple consumers in the same group are assigned to the same topic, how are partitions distributed?",
        "options": {
            "A": "Each partition is read by all consumers in the group",
            "B": "Each partition is assigned to exactly one consumer in the group",
            "C": "Consumers take turns reading every partition",
            "D": "The leader consumer reads everything and forwards it"
        },
        "answer": "B"
    },
    {
        "question": "Which method does a consumer use to retrieve records from a broker?",
        "options": {
            "A": "get()",
            "B": "poll()",
            "C": "fetch()",
            "D": "read()"
        },
        "answer": "B"
    },
    {
        "question": "What happens if the number of consumers in a group exceeds the number of partitions in a topic?",
        "options": {
            "A": "The extra consumers will remain idle",
            "B": "Kafka creates more partitions automatically",
            "C": "The consumers share partitions using time-slicing",
            "D": "The cluster crashes"
        },
        "answer": "A"
    },
    {
        "question": "What is 'enable.auto.commit' used for in the Consumer API?",
        "options": {
            "A": "To automatically join a group",
            "B": "To periodically commit the offsets of messages already fetched",
            "C": "To delete messages after reading",
            "D": "To restart the consumer on failure"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Group Coordinator' in Kafka?",
        "options": {
            "A": "A specialized client application",
            "B": "A broker responsible for managing a specific consumer group's state",
            "C": "The first consumer to join the group",
            "D": "A Zookeeper node"
        },
        "answer": "B"
    },
    {
        "question": "Which setting defines the behavior of a consumer when no initial offset exists (e.g., a new group)?",
        "options": {
            "A": "offset.reset",
            "B": "auto.offset.reset",
            "C": "start.position",
            "D": "initial.offset"
        },
        "answer": "B"
    },
    {
        "question": "What are the two most common values for 'auto.offset.reset'?",
        "options": {
            "A": "start and end",
            "B": "earliest and latest",
            "C": "first and last",
            "D": "zero and max"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Sticky Partitioning' strategy in the Producer API?",
        "options": {
            "A": "Messages stay on the broker forever",
            "B": "Messages without keys are batched together for a single partition to improve performance",
            "C": "Partitions are locked to specific users",
            "D": "Messages are stuck in the buffer"
        },
        "answer": "B"
    },
    {
        "question": "Which configuration ensures that a Producer only sends messages in the correct order even with retries?",
        "options": {
            "A": "order.strict=true",
            "B": "enable.idempotence=true",
            "C": "retry.order.fixed=true",
            "D": "max.in.flight.requests.per.connection=1"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Linger.ms' in the Producer configuration?",
        "options": {
            "A": "The time a message stays in the broker",
            "B": "The amount of time the producer waits to group individual records into a single batch",
            "C": "The delay before a consumer starts",
            "D": "The connection timeout"
        },
        "answer": "B"
    },
    {
        "question": "What does a 'Heartbeat' from a consumer to the Group Coordinator indicate?",
        "options": {
            "A": "The consumer is currently downloading data",
            "B": "The consumer is alive and healthy within the group",
            "C": "The consumer has finished its job",
            "D": "The consumer is requesting more partitions"
        },
        "answer": "B"
    },
    {
        "question": "Which setting defines the maximum time a consumer can go without sending a heartbeat before being considered dead?",
        "options": {
            "A": "heartbeat.interval.ms",
            "B": "session.timeout.ms",
            "C": "max.poll.interval.ms",
            "D": "group.expiry.ms"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Static Group Membership' in Kafka?",
        "options": {
            "A": "A group that never changes its size",
            "B": "A feature allowing consumers to keep their partitions during brief restarts without a rebalance",
            "C": "A group with only one consumer",
            "D": "A group stored in a database"
        },
        "answer": "B"
    },
    {
        "question": "Which Producer method is asynchronous and returns a Future?",
        "options": {
            "A": "write()",
            "B": "send()",
            "C": "emit()",
            "D": "push()"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'High Watermark' in a Kafka partition?",
        "options": {
            "A": "The maximum size of the partition",
            "B": "The offset of the last message that has been successfully replicated to all ISRs",
            "C": "The first message in the log",
            "D": "The oldest message allowed to be read"
        },
        "answer": "B"
    },
    {
        "question": "Can a consumer read messages beyond the High Watermark?",
        "options": {
            "A": "Yes, if configured to do so",
            "B": "No, to ensure consistency across the cluster",
            "C": "Only if the leader fails",
            "D": "Only if it is the administrative user"
        },
        "answer": "B"
    },
    {
        "question": "Which component is responsible for choosing the 'Group Leader' during a rebalance?",
        "options": {
            "A": "Zookeeper",
            "B": "The Group Coordinator broker",
            "C": "The first consumer to respond to the JoinGroup request",
            "D": "The Kafka Controller"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Cooperative Rebalancing' (Incremental Rebalancing)?",
        "options": {
            "A": "All consumers stop reading simultaneously",
            "B": "A strategy that redistributes only necessary partitions, reducing 'stop-the-world' time",
            "C": "Sharing data between two different groups",
            "D": "Using manual offsets"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'max.poll.records'?",
        "options": {
            "A": "The total number of messages in a topic",
            "B": "The maximum number of records returned in a single call to poll()",
            "C": "The limit of messages a broker can store",
            "D": "The number of retries for a failed read"
        },
        "answer": "B"
    },
    {
        "question": "What does 'compression.type' affect in the Producer API?",
        "options": {
            "A": "The size of the Java application",
            "B": "The compression algorithm (gzip, snappy, lz4, zstd) used for message batches",
            "C": "The encryption level",
            "D": "The speed of the disk"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Log End Offset' (LEO)?",
        "options": {
            "A": "The end of the configuration file",
            "B": "The offset of the next message to be written to a partition",
            "C": "The last message read by the consumer",
            "D": "The message that is about to be deleted"
        },
        "answer": "B"
    },
    {
        "question": "Which setting controls the 'Consumer Group ID'?",
        "options": {
            "A": "group.name",
            "B": "group.id",
            "C": "client.id",
            "D": "consumer.group"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Manual Offset Management'?",
        "options": {
            "A": "Typing offsets into a console",
            "B": "Disabling auto-commit and programmatically calling commitSync() or commitAsync()",
            "C": "Deleting offsets from Zookeeper",
            "D": "Manually assigning brokers"
        },
        "answer": "B"
    },
    {
        "question": "What is the risk of using 'commitAsync()'?",
        "options": {
            "A": "It slows down the consumer",
            "B": "It does not retry on failure, which could lead to missed commits (though usually solved by the next commit)",
            "C": "It deletes data",
            "D": "It requires a password"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to manually assign a specific partition to a consumer (bypassing the group coordinator)?",
        "options": {
            "A": "subscribe()",
            "B": "assign()",
            "C": "join()",
            "D": "attach()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Zombie Fencing' in Kafka?",
        "options": {
            "A": "Killing old messages",
            "B": "Preventing a timed-out producer or consumer from continuing to write/read after a new one has taken over",
            "C": "A security scan",
            "D": "Deleting idle groups"
        },
        "answer": "B"
    },
    {
        "question": "What does 'max.in.flight.requests.per.connection' define?",
        "options": {
            "A": "The number of users on the network",
            "B": "The maximum number of unacknowledged requests the producer will send on a single connection",
            "C": "The speed of the fan in the server",
            "D": "The total number of partitions"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Idempotent Producer'?",
        "options": {
            "A": "A producer that only sends one message",
            "B": "A producer that ensures messages are written exactly once to the log even if retries occur",
            "C": "A producer that encrypts keys",
            "D": "A producer that doesn't use a buffer"
        },
        "answer": "B"
    },
    {
        "question": "Which setting defines the 'Buffer Memory' on the Producer?",
        "options": {
            "A": "max.memory",
            "B": "buffer.memory",
            "C": "memory.limit",
            "D": "batch.buffer"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Fetch Min Bytes' setting in the Consumer?",
        "options": {
            "A": "The smallest message allowed",
            "B": "The minimum amount of data the broker should return for a fetch request (to reduce request count)",
            "C": "The size of the disk",
            "D": "The metadata size"
        },
        "answer": "B"
    },
    {
        "question": "In Kafka, what is a 'Tombstone'?",
        "options": {
            "A": "A crashed broker",
            "B": "A message with a null value used in log compaction to mark a key for deletion",
            "C": "An expired offset",
            "D": "A deleted topic"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'RoundRobinAssignor'?",
        "options": {
            "A": "To sort brokers",
            "B": "To distribute partitions across consumers in a group evenly in a circular fashion",
            "C": "To cycle through topics",
            "D": "To rotate passwords"
        },
        "answer": "B"
    },
    {
        "question": "What does 'max.poll.interval.ms' control?",
        "options": {
            "A": "The network timeout",
            "B": "The maximum time between poll() calls before the consumer is considered to have failed processing",
            "C": "The time to wait for a batch",
            "D": "The heartbeat frequency"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Transactional Messaging' in Kafka?",
        "options": {
            "A": "Sending data to a bank",
            "B": "The ability to produce to multiple topics and partitions atomically (all or nothing)",
            "C": "Paying for Kafka usage",
            "D": "A way to backup transactions"
        },
        "answer": "B"
    },
    {
        "question": "Which component manages transactions in Kafka?",
        "options": {
            "A": "The Transaction Coordinator",
            "B": "The Group Coordinator",
            "C": "The Controller",
            "D": "Zookeeper"
        },
        "answer": "A"
    },
    {
        "question": "What is the 'isolation.level' setting in the Consumer?",
        "options": {
            "A": "A security firewall",
            "B": "Determines whether the consumer reads only committed transactional messages or everything",
            "C": "The distance between nodes",
            "D": "The encryption strength"
        },
        "answer": "B"
    },
    {
        "question": "What is 'read_committed' vs 'read_uncommitted'?",
        "options": {
            "A": "Reading from disk vs RAM",
            "B": "Filtering out aborted transactions vs seeing every message written to the log",
            "C": "Reading with a password vs without",
            "D": "Historical vs live data"
        },
        "answer": "B"
    },
    {
        "question": "Which configuration identifies a unique producer instance for transactions?",
        "options": {
            "A": "client.id",
            "B": "transactional.id",
            "C": "producer.name",
            "D": "tx.id"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Consumer Rebalance Listener'?",
        "options": {
            "A": "A person monitoring the group",
            "B": "A callback interface to handle custom logic (like committing offsets) before or after a rebalance",
            "C": "An error log",
            "D": "A tool to restart consumers"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Metadata Timeout'?",
        "options": {
            "A": "The time to load a topic",
            "B": "The maximum time the producer will wait for metadata (like leader info) to be refreshed",
            "C": "The age of the broker",
            "D": "The license expiry"
        },
        "answer": "B"
    },
    {
        "question": "Which class is used to serialize keys and values into bytes?",
        "options": {
            "A": "Encoder",
            "B": "Serializer",
            "C": "ByteWriter",
            "D": "Converter"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Custom Partitioner'?",
        "options": {
            "A": "A person who splits data manually",
            "B": "A user-defined class that implements specific logic to choose the destination partition for a message",
            "C": "A way to divide the hardware",
            "D": "A tool for sharding databases"
        },
        "answer": "B"
    },
    {
        "question": "What does 'seek()' allow a consumer to do?",
        "options": {
            "A": "Search for a word",
            "B": "Manually jump to a specific offset in a partition",
            "C": "Find a new broker",
            "D": "Check for updates"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Fetch Max Wait'?",
        "options": {
            "A": "The time to wait for a bus",
            "B": "The maximum time the broker will wait to fill a fetch request with 'fetch.min.bytes' before returning",
            "C": "The connection timeout",
            "D": "The producer batch delay"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'StickyAssignor' intended to improve?",
        "options": {
            "A": "Throughput",
            "B": "Minimizing the number of partitions moved during a rebalance",
            "C": "Security",
            "D": "Disk usage"
        },
        "answer": "B"
    },
    {
        "question": "Can a single consumer be part of multiple consumer groups?",
        "options": {
            "A": "No, it's impossible",
            "B": "Yes, but it requires different configurations/instances for each group",
            "C": "Only if they share the same topic",
            "D": "Only if it is the leader"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Consumer Group Metadata'?",
        "options": {
            "A": "The list of users",
            "B": "Information about group members and their assigned partitions",
            "C": "The data in the topic",
            "D": "The server hardware specs"
        },
        "answer": "B"
    },
    {
        "question": "Which method is called to gracefully shut down a consumer?",
        "options": {
            "A": "stop()",
            "B": "close()",
            "C": "exit()",
            "D": "wakeup()"
        },
        "answer": "B"
    },
   {
        "question": "How does Kafka store its data on the physical disk?",
        "options": {
            "A": "In a relational table format",
            "B": "As an append-only sequence of files called segments",
            "C": "In a compressed ZIP archive per topic",
            "D": "In a distributed cache only"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Segment' in Kafka storage?",
        "options": {
            "A": "A single message",
            "B": "A smaller file that partitions are broken down into to manage storage better",
            "C": "A user-defined data group",
            "D": "The metadata for a broker"
        },
        "answer": "B"
    },
    {
        "question": "Which file contains the actual message data within a Kafka segment?",
        "options": {
            "A": ".index",
            "B": ".log",
            "C": ".timeindex",
            "D": ".data"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the '.index' file in a segment?",
        "options": {
            "A": "To encrypt the messages",
            "B": "To map offsets to physical positions in the .log file for fast lookup",
            "C": "To store the topic names",
            "D": "To list the consumers"
        },
        "answer": "B"
    },
    {
        "question": "Which parameter defines the maximum size of a single segment file before a new one is created?",
        "options": {
            "A": "segment.bytes",
            "B": "log.segment.bytes",
            "C": "max.segment.size",
            "D": "partition.segment.limit"
        },
        "answer": "B"
    },
    {
        "question": "What happens to the 'Active Segment' of a partition?",
        "options": {
            "A": "It is read-only",
            "B": "It is the only segment currently receiving writes from the producer",
            "C": "It is automatically compressed",
            "D": "It is stored in Zookeeper"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Preferred Leader' in a Kafka cluster?",
        "options": {
            "A": "The broker with the most RAM",
            "B": "The first broker listed in the replica set for a partition",
            "C": "The broker that was manually chosen by the admin",
            "D": "The newest broker in the cluster"
        },
        "answer": "B"
    },
    {
        "question": "What does 'Leader Election' do?",
        "options": {
            "A": "Votes for a new CEO of the company",
            "B": "Selects a new leader replica for a partition when the current leader fails",
            "C": "Assigns new IDs to consumers",
            "D": "Clears the metadata cache"
        },
        "answer": "B"
    },
    {
        "question": "Which component is responsible for triggering leader elections in a Zookeeper-based cluster?",
        "options": {
            "A": "The Producer",
            "B": "The Kafka Controller",
            "C": "The Consumer Group Leader",
            "D": "The Schema Registry"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Unclean Leader Election'?",
        "options": {
            "A": "An election held during maintenance",
            "B": "Allowing a non-in-sync replica (non-ISR) to become leader to maintain availability",
            "C": "An election that happens without Zookeeper",
            "D": "A failed election"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary risk of 'Unclean Leader Election'?",
        "options": {
            "A": "It slows down the cluster",
            "B": "Potential data loss, as the new leader may not have all the messages from the previous leader",
            "C": "It deletes the topic",
            "D": "It requires a server restart"
        },
        "answer": "B"
    },
    {
        "question": "What does 'min.insync.replicas' define?",
        "options": {
            "A": "The minimum number of consumers needed",
            "B": "The minimum number of in-sync replicas that must acknowledge a write for it to be successful (when acks=all)",
            "C": "The number of partitions per broker",
            "D": "The replication factor"
        },
        "answer": "B"
    },
    {
        "question": "What is the result if 'acks=all' is set but the number of ISRs is less than 'min.insync.replicas'?",
        "options": {
            "A": "The write succeeds on the leader only",
            "B": "The producer receives a NotEnoughReplicasException",
            "C": "The data is cached until a new replica joins",
            "D": "The broker crashes"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Availability' vs 'Durability' in Kafka?",
        "options": {
            "A": "There is no difference",
            "B": "Availability is the ability to read/write; Durability is the guarantee that data is not lost",
            "C": "Availability is for consumers; Durability is for producers",
            "D": "Availability is about speed; Durability is about size"
        },
        "answer": "B"
    },
    {
        "question": "How does Kafka achieve fault tolerance for its topics?",
        "options": {
            "A": "By using a RAID 10 configuration on every disk",
            "B": "By replicating partitions across multiple brokers",
            "C": "By backing up data to Amazon S3 every hour",
            "D": "By prohibiting more than one consumer per group"
        },
        "answer": "B"
    },
    {
        "question": "Which background thread in the broker is responsible for replicating data from the leader to the followers?",
        "options": {
            "A": "LogCleaner",
            "B": "ReplicaFetcherThread",
            "C": "GroupCoordinator",
            "D": "Processor"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Replica Lag'?",
        "options": {
            "A": "The time it takes to create a new topic",
            "B": "The delay between the leader's log end offset and a follower's log end offset",
            "C": "The distance between server racks",
            "D": "The number of users on the network"
        },
        "answer": "B"
    },
    {
        "question": "Which setting defines how far a follower can fall behind the leader before being removed from the ISR?",
        "options": {
            "A": "replica.lag.max.messages",
            "B": "replica.lag.time.max.ms",
            "C": "max.replica.delay",
            "D": "isr.sync.timeout"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Controller' in a Kafka cluster?",
        "options": {
            "A": "A hardware device",
            "B": "A specific broker responsible for administrative tasks like leadership changes and partition movements",
            "C": "The first producer connected",
            "D": "The Zookeeper root node"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Under-Replicated Partitions'?",
        "options": {
            "A": "Partitions with no data",
            "B": "Partitions where the number of current in-sync replicas is less than the desired replication factor",
            "C": "Partitions with only one consumer",
            "D": "Partitions that are being deleted"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Rack Awareness' in Kafka replication?",
        "options": {
            "A": "The broker knowing its physical shelf height",
            "B": "A strategy to ensure replicas are placed on different physical racks for higher availability",
            "C": "Limiting the number of racks in a data center",
            "D": "Increasing network speed between racks"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to change the replication factor of an existing topic?",
        "options": {
            "A": "kafka-topics.sh --alter --replication-factor",
            "B": "kafka-reassign-partitions.sh",
            "C": "kafka-configs.sh",
            "D": "Replication factor cannot be changed once a topic is created"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Log Retention by Bytes'?",
        "options": {
            "A": "Charging users for data",
            "B": "Deleting the oldest segments of a partition when the total size exceeds a threshold",
            "C": "The maximum size of a single message",
            "D": "The number of bits in a key"
        },
        "answer": "B"
    },
    {
        "question": "Which parameter controls the retention time for a specific topic?",
        "options": {
            "A": "log.retention.hours",
            "B": "retention.ms",
            "C": "data.expiry.time",
            "D": "log.life.ms"
        },
        "answer": "B"
    },
    {
        "question": "What is the result of setting 'retention.ms' to -1?",
        "options": {
            "A": "Data is deleted immediately",
            "B": "Data is retained infinitely",
            "C": "The broker throws an error",
            "D": "The topic is archived to S3"
        },
        "answer": "B"
    },
    {
        "question": "What does 'Log Compaction' do to messages with the same key?",
        "options": {
            "A": "Combines them into a list",
            "B": "Keeps only the most recent message (value) for each key",
            "C": "Deletes all of them",
            "D": "Compresses them using Gzip"
        },
        "answer": "B"
    },
    {
        "question": "Which segment is NEVER eligible for log compaction?",
        "options": {
            "A": "The oldest segment",
            "B": "The active segment (the one currently being written to)",
            "C": "Small segments",
            "D": "Segments with no keys"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Cleaner' thread in Kafka?",
        "options": {
            "A": "A thread that deletes temporary files",
            "B": "A background thread that performs log compaction",
            "C": "A thread that resets consumer offsets",
            "D": "A thread that checks for hardware errors"
        },
        "answer": "B"
    },
    {
        "question": "What is the benefit of 'End-to-End Compression'?",
        "options": {
            "A": "The producer compresses and the broker stores it compressed, saving CPU on the broker",
            "B": "It encrypts the data",
            "C": "It makes the keys shorter",
            "D": "It prevents network lag"
        },
        "answer": "A"
    },
    {
        "question": "Which setting defines where Kafka stores its data files on the local disk?",
        "options": {
            "A": "data.dir",
            "B": "log.dirs",
            "C": "kafka.storage.path",
            "D": "broker.data.root"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'File System Page Cache' in Kafka?",
        "options": {
            "A": "To store web pages",
            "B": "Kafka relies on the OS page cache for read/write speed instead of maintaining its own in-memory cache",
            "C": "To store logs on SSDs",
            "D": "To speed up Zookeeper"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Metadata Replication'?",
        "options": {
            "A": "Copying the actual message data",
            "B": "Replicating cluster state (topics, partitions, leaders) across all brokers",
            "C": "Backing up user passwords",
            "D": "Naming the brokers identically"
        },
        "answer": "B"
    },
    {
        "question": "In KRaft mode, which brokers handle metadata management instead of Zookeeper?",
        "options": {
            "A": "Data Brokers",
            "B": "Quorum Controllers (Voters)",
            "C": "Leader Brokers",
            "D": "Management Nodes"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Snapshot' in KRaft mode?",
        "options": {
            "A": "A photo of the cluster",
            "B": "A point-in-time capture of the metadata log to speed up recovery and startup",
            "C": "A backup of a topic",
            "D": "A copy of a consumer group"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Quorum' in Kafka replication?",
        "options": {
            "A": "A specific type of message",
            "B": "The minimum number of nodes that must be available for the cluster to function correctly",
            "C": "A group of consumers",
            "D": "A security setting"
        },
        "answer": "B"
    },
    {
        "question": "What happens if a broker loses its connection to the Quorum/Zookeeper?",
        "options": {
            "A": "It continues as normal",
            "B": "It stops serving requests and eventually shuts down or waits for reconnection",
            "C": "It becomes the new leader",
            "D": "It deletes its local data"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Fenced Broker'?",
        "options": {
            "A": "A broker behind a firewall",
            "B": "A broker that has been logically removed from the cluster state due to lack of heartbeats or errors",
            "C": "A broker used for testing",
            "D": "A broker with a password"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to check the health and synchronization status of a topic?",
        "options": {
            "A": "kafka-topics.sh --describe",
            "B": "kafka-topics.sh --health",
            "C": "kafka-broker-api-versions.sh",
            "D": "kafka-configs.sh --check"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Partition Reassignment'?",
        "options": {
            "A": "Renaming a partition",
            "B": "Moving partitions from one broker to another (usually for load balancing or broker decommissioning)",
            "C": "Changing the number of partitions",
            "D": "Deleting partitions"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Preferred Leader Election'?",
        "options": {
            "A": "An election where users vote",
            "B": "A process to move partition leadership back to the first replica in the list to maintain balance",
            "C": "Choosing the fastest broker",
            "D": "Choosing a broker with the most storage"
        },
        "answer": "B"
    },
    {
        "question": "Which parameter enables automatic preferred leader election?",
        "options": {
            "A": "auto.leader.rebalance.enable",
            "B": "leader.election.auto",
            "C": "rebalance.preferred.leader",
            "D": "broker.balance.enable"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Min In-Sync Replicas' default value?",
        "options": {
            "A": "0",
            "B": "1",
            "C": "2",
            "D": "3"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Jobodurability'?",
        "options": {
            "A": "A new Kafka feature",
            "B": "The assurance that a message is successfully stored across the requested number of replicas",
            "C": "The speed of the job",
            "D": "The length of the topic"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Disk Thrashing' in Kafka?",
        "options": {
            "A": "A hardware test",
            "B": "When multiple producers/consumers cause too many random I/O requests, killing performance",
            "C": "When a disk is full",
            "D": "Formatting a disk"
        },
        "answer": "B"
    },
    {
        "question": "How does Kafka handle 'Corrupted Messages' on disk?",
        "options": {
            "A": "It automatically fixes them",
            "B": "It uses CRC (Cyclic Redundancy Check) to detect corruption and throws an error/skips during read",
            "C": "It ignores them",
            "D": "It asks the producer to send again"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Ghosting' in Kafka storage?",
        "options": {
            "A": "A security threat",
            "B": "When data is deleted from the log but remains in the OS page cache for a brief time",
            "C": "Hidden partitions",
            "D": "Old consumer groups"
        },
        "answer": "B"
    },
    {
        "question": "What is 'MirrorMaker'?",
        "options": {
            "A": "A tool to create a UI for Kafka",
            "B": "A tool used to replicate data between two different Kafka clusters (Cross-cluster replication)",
            "C": "A tool to duplicate brokers",
            "D": "A tool to backup Zookeeper"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Active-Active' cluster configuration?",
        "options": {
            "A": "Two clusters that both accept reads and writes, with data synchronized between them",
            "B": "A cluster with no standby nodes",
            "C": "A cluster for testing only",
            "D": "Two producers sending to the same topic"
        },
        "answer": "A"
    },
    {
        "question": "What is the 'Broker ID'?",
        "options": {
            "A": "The name of the server",
            "B": "A unique integer that identifies each Kafka broker in a cluster",
            "C": "The IP address",
            "D": "The license number"
        },
        "answer": "B"
    },
    {
        "question": "Final question: What is the primary advantage of Kafka being 'Stateless' for its brokers?",
        "options": {
            "A": "It makes them more secure",
            "B": "It allows brokers to be easily replaced or scaled without complex state migration (state is in the logs)",
            "C": "It means they don't use RAM",
            "D": "It means they don't need a hard drive"
        },
        "answer": "B"
    },
     {
        "question": "What is 'Kafka Connect' designed for?",
        "options": {
            "A": "Writing complex Java logic",
            "B": "Scalable and reliable streaming of data between Kafka and other systems (databases, file systems, etc.)",
            "C": "Connecting brokers to each other",
            "D": "Monitoring the cluster temperature"
        },
        "answer": "B"
    },
    {
        "question": "In Kafka Connect, what is a 'Source Connector'?",
        "options": {
            "A": "A connector that writes data from Kafka to a database",
            "B": "A connector that ingests data from an external system into a Kafka topic",
            "C": "A connector for Python code",
            "D": "A backup for Zookeeper"
        },
        "answer": "B"
    },
    {
        "question": "In Kafka Connect, what is a 'Sink Connector'?",
        "options": {
            "A": "A connector that ingests data into Kafka",
            "B": "A connector that exports data from Kafka topics into an external system",
            "C": "A connector for mobile apps",
            "D": "A tool to delete topics"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Kafka Streams'?",
        "options": {
            "A": "A standalone cluster for processing",
            "B": "A client library for building applications and microservices where input and output are in Kafka",
            "C": "A video streaming service",
            "D": "A UI for viewing topics"
        },
        "answer": "B"
    },
    {
        "question": "In Kafka Streams, what is a 'KStream'?",
        "options": {
            "A": "A snapshot of the current state",
            "B": "An abstraction of a record stream, where each data record is an independent insert in the unbounded dataset",
            "C": "A list of users",
            "D": "A temporary table"
        },
        "answer": "B"
    },
    {
        "question": "In Kafka Streams, what is a 'KTable'?",
        "options": {
            "A": "A physical table in MySQL",
            "B": "An abstraction of a changelog stream, representing the latest value for each key (similar to a database table)",
            "C": "A spreadsheet in Excel",
            "D": "A configuration file"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Stateful Processing' in Kafka Streams?",
        "options": {
            "A": "Processing data only from one state/province",
            "B": "Processing that requires remembering information from previous records (e.g., joins, windowed aggregations)",
            "C": "Processing that never saves data",
            "D": "Processing only for government agencies"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Windowing' in Kafka Streams?",
        "options": {
            "A": "Viewing the data through a browser window",
            "B": "Grouping records that have the same key for stateful operations over a specific time period",
            "C": "Scaling the UI",
            "D": "Closing inactive topics"
        },
        "answer": "B"
    },
    {
        "question": "Which security mechanism provides encryption for data in transit between Kafka clients and brokers?",
        "options": {
            "A": "ACLs",
            "B": "SSL/TLS",
            "C": "SASL",
            "D": "Kerberos"
        },
        "answer": "B"
    },
    {
        "question": "What is 'SASL' used for in Kafka?",
        "options": {
            "A": "Encryption",
            "B": "Authentication (verifying the identity of a user or application)",
            "C": "Message compression",
            "D": "Topic partitioning"
        },
        "answer": "B"
    },
    {
        "question": "What does 'ACL' (Access Control List) manage in Kafka?",
        "options": {
            "A": "Network bandwidth",
            "B": "Authorization (defining what operations a specific user can perform on specific topics)",
            "C": "The number of partitions",
            "D": "Broker hardware settings"
        },
        "answer": "B"
    },
    {
        "question": "Which command-line tool is used to manage ACLs in Kafka?",
        "options": {
            "A": "kafka-topics.sh",
            "B": "kafka-acls.sh",
            "C": "kafka-security.sh",
            "D": "kafka-configs.sh"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Stateless Processing'?",
        "options": {
            "A": "Processing that forgets everything after each message",
            "B": "Processing that depends only on the information in the current record (e.g., filtering, transforming)",
            "C": "Processing without a database",
            "D": "Processing for random keys"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Topology' in Kafka Streams?",
        "options": {
            "A": "The map of the server room",
            "B": "A directed acyclic graph (DAG) of processing nodes representing the logic of the application",
            "C": "The list of IP addresses",
            "D": "The structure of the JSON"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Serdes' in Kafka Streams context?",
        "options": {
            "A": "Server-side Desktop",
            "B": "Serializer and Deserializer needed to convert data when reading/writing to Kafka topics",
            "C": "Series of Designs",
            "D": "Security Descriptors"
        },
        "answer": "B"
    },
    {
        "question": "What is the role of the 'State Store' in Kafka Streams?",
        "options": {
            "A": "To sell Kafka licenses",
            "B": "To locally store and query data needed for stateful operations (like RocksDB)",
            "C": "To backup the whole cluster",
            "D": "To store user credentials"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Interactive Queries' in Kafka Streams?",
        "options": {
            "A": "Chatting with the developers",
            "B": "A feature that allows querying the state stores of a running Kafka Streams application directly",
            "C": "Using SQL in the terminal",
            "D": "Searching the web"
        },
        "answer": "B"
    },
    {
        "question": "Which SASL mechanism is commonly used to integrate Kafka with Kerberos?",
        "options": {
            "A": "PLAIN",
            "B": "GSSAPI",
            "C": "SCRAM",
            "D": "OAUTHBEARER"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Quotas' in Kafka administration?",
        "options": {
            "A": "The price of the software",
            "B": "Limits on producer/consumer throughput or request rates to prevent one client from overwhelming the cluster",
            "C": "The number of topics allowed",
            "D": "The minimum number of followers"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'Alter Configs' permission allow a user to do?",
        "options": {
            "A": "Read messages",
            "B": "Modify configuration settings for topics or brokers",
            "C": "Delete the cluster",
            "D": "Create new users"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Kafka MirrorMaker 2' (MM2) based on?",
        "options": {
            "A": "MapReduce",
            "B": "Kafka Connect framework",
            "C": "Zookeeper",
            "D": "Spark Streaming"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to delete a topic?",
        "options": {
            "A": "kafka-topics.sh --remove",
            "B": "kafka-topics.sh --delete",
            "C": "kafka-topics.sh --kill",
            "D": "kafka-topics.sh --drop"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Rack-aware Consumer' (Client-side Rack Awareness)?",
        "options": {
            "A": "A consumer that knows the size of the rack",
            "B": "A feature where a consumer can read from the closest replica (follower) in the same rack to save on network costs",
            "C": "A consumer that only reads from rack 1",
            "D": "A consumer that manages rack power"
        },
        "answer": "B"
    },
    {
        "question": "In a secure cluster, what is a 'Principal'?",
        "options": {
            "A": "The school headmaster",
            "B": "An entity (user or service) that can be authenticated by Kafka",
            "C": "The main topic",
            "D": "The first broker"
        },
        "answer": "B"
    },
    {
        "question": "What does 'Inter-broker Protocol Version' define?",
        "options": {
            "A": "The network cable type",
            "B": "The version of the protocol used for communication between brokers (important for upgrades)",
            "C": "The speed of the fans",
            "D": "The language of the logs"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Exactly-Once Processing' in Kafka Streams?",
        "options": {
            "A": "Processing data only once a year",
            "B": "A feature ensuring that the read-process-write cycle happens atomically and exactly once",
            "C": "Processing only one key",
            "D": "A way to speed up the CPU"
        },
        "answer": "B"
    },
    {
        "question": "Which tool is used to visualize Kafka metrics, often used alongside Prometheus?",
        "options": {
            "A": "Grafana",
            "B": "Excel",
            "C": "Photoshop",
            "D": "Word"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Cruise Control' for Kafka?",
        "options": {
            "A": "A way to drive a car",
            "B": "An open-source tool for automated cluster rebalancing, self-healing, and monitoring",
            "C": "A feature to keep constant speed",
            "D": "A backup tool"
        },
        "answer": "B"
    },
    {
        "question": "Which parameter in 'server.properties' enables the deletion of topics?",
        "options": {
            "A": "topic.delete.enabled",
            "B": "delete.topic.enable",
            "C": "allow.delete.topic",
            "D": "can.remove.topic"
        },
        "answer": "B"
    },
    {
        "question": "Final question: Kafka is named after which famous author?",
        "options": {
            "A": "William Shakespeare",
            "B": "Franz Kafka",
            "C": "Ernest Hemingway",
            "D": "Mark Twain"
        },
        "answer": "B"
    },

    {
        "question": "What is the primary purpose of the 'Confluent Schema Registry'?",
        "options": {
            "A": "To store the actual message data",
            "B": "To provide a serving layer for your metadata and a central repository for schemas",
            "C": "To encrypt message keys",
            "D": "To manage broker passwords"
        },
        "answer": "B"
    },
    {
        "question": "Which Kafka metric is the most critical for identifying if a consumer is falling behind?",
        "options": {
            "A": "Incoming byte rate",
            "B": "Consumer Lag",
            "C": "Broker CPU usage",
            "D": "Replication factor"
        },
        "answer": "B"
    },
    {
        "question": "In 'Schema Registry', what does 'Backward Compatibility' ensure?",
        "options": {
            "A": "New schemas can read old data",
            "B": "Consumers using the new schema can read data written with the previous schema",
            "C": "Old consumers can read new data",
            "D": "Data is automatically backed up"
        },
        "answer": "B"
    },
    {
        "question": "What is 'JMX' (Java Management Extensions) used for in a Kafka broker?",
        "options": {
            "A": "To write message processors",
            "B": "To expose internal broker metrics for monitoring tools",
            "C": "To compress log segments",
            "D": "To restart the server"
        },
        "answer": "B"
    },
    {
        "question": "Which parameter controls the total memory a Producer can use to buffer messages waiting to be sent?",
        "options": {
            "A": "batch.size",
            "B": "buffer.memory",
            "C": "max.block.ms",
            "D": "memory.limit"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'Under-Replicated Partitions' metric signify?",
        "options": {
            "A": "The partitions have no data",
            "B": "The number of partitions where the number of ISRs is less than the replication factor",
            "C": "Partitions that are being deleted",
            "D": "Partitions with too many consumers"
        },
        "answer": "B"
    },
    {
        "question": "Which tool is commonly used to visualize Kafka metrics in a dashboard?",
        "options": {
            "A": "Grafana",
            "B": "Excel",
            "C": "Photoshop",
            "D": "PowerPoint"
        },
        "answer": "A"
    },
    {
        "question": "What is 'End-to-End Latency' in a Kafka pipeline?",
        "options": {
            "A": "The time it takes to install a broker",
            "B": "The time between a message being produced and it being processed by the final consumer",
            "C": "The network ping between nodes",
            "D": "The size of the log file"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Leader Queue' metrics?",
        "options": {
            "A": "To count the number of leaders",
            "B": "To monitor the time requests spend waiting in the broker's request queue",
            "C": "To sort the brokers",
            "D": "To manage user logins"
        },
        "answer": "B"
    },
    {
        "question": "Which setting prevents a producer from blocking indefinitely when the buffer is full?",
        "options": {
            "A": "linger.ms",
            "B": "max.block.ms",
            "C": "request.timeout.ms",
            "D": "retry.backoff.ms"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Schema Evolution'?",
        "options": {
            "A": "Deleting old schemas",
            "B": "The process of modifying a schema while maintaining compatibility with existing data",
            "C": "Upgrading Kafka versions",
            "D": "Changing topic names"
        },
        "answer": "B"
    },
    {
        "question": "Which metric tracks the number of times a partition leader has changed unexpectedly?",
        "options": {
            "A": "ActiveControllerCount",
            "B": "LeaderElectionRateAndTimeMs",
            "C": "UnderMinIsrPartitionCount",
            "D": "OfflinePartitionsCount"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Disk Utilization' threshold concern in Kafka?",
        "options": {
            "A": "Kafka runs faster when disks are full",
            "B": "High disk usage can trigger log retention and potentially lead to broker shutdown if the disk fills completely",
            "C": "Disks are not used in Kafka",
            "D": "Only SSDs are supported"
        },
        "answer": "B"
    },
    {
        "question": "In 'Schema Registry', what does 'Full Compatibility' mean?",
        "options": {
            "A": "Data is compressed",
            "B": "New schemas are both backward and forward compatible",
            "C": "The registry is connected to all brokers",
            "D": "All users have admin rights"
        },
        "answer": "B"
    },
    {
        "question": "Which Kafka component is responsible for enforcing Quotas?",
        "options": {
            "A": "The Producer",
            "B": "The Broker",
            "C": "The Consumer",
            "D": "Zookeeper"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Throughput' in a Kafka cluster?",
        "options": {
            "A": "The total amount of RAM",
            "B": "The amount of data successfully processed per unit of time (e.g., MB/s)",
            "C": "The number of files on disk",
            "D": "The number of developers"
        },
        "answer": "B"
    },
    {
        "question": "What is the impact of a high 'Fetch Consumer Request' rate?",
        "options": {
            "A": "Increased throughput",
            "B": "Increased CPU overhead on the broker due to processing many small requests",
            "C": "Faster data replication",
            "D": "Better encryption"
        },
        "answer": "B"
    },
    {
        "question": "Which tool provides a centralized view of multiple Kafka clusters?",
        "options": {
            "A": "Kafka UI / Confluent Control Center",
            "B": "Terminal",
            "C": "Notepad",
            "D": "Browser console"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Network Processor' usage in Kafka monitoring?",
        "options": {
            "A": "The speed of the network card",
            "B": "The percentage of time the network threads are busy processing requests",
            "C": "The number of connected users",
            "D": "The physical location of the router"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Partition Rebalance' time?",
        "options": {
            "A": "The time to create a partition",
            "B": "The duration during which consumers in a group stop processing to re-assign partitions",
            "C": "The time to backup a partition",
            "D": "The interval between heartbeats"
        },
        "answer": "B"
    },
    {
        "question": "Which of these contributes to 'End-to-End Latency'?",
        "options": {
            "A": "linger.ms",
            "B": "fetch.min.bytes",
            "C": "Network transmission time",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Garbage Collection' (GC) tuning important for in Kafka?",
        "options": {
            "A": "To clean up old topics",
            "B": "To prevent long JVM pauses that can lead to Zookeeper session timeouts and rebalances",
            "C": "To delete temporary files",
            "D": "To recycle hardware"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Message Conversion' overhead?",
        "options": {
            "A": "Translating messages to different languages",
            "B": "CPU cost incurred when the broker must convert message formats for older clients",
            "C": "Changing the message key",
            "D": "Sending messages to the cloud"
        },
        "answer": "B"
    },
    {
        "question": "What happens if 'Schema Registry' is unavailable?",
        "options": {
            "A": "The brokers stop working",
            "B": "Producers and Consumers using Avro/Protobuf may fail to serialize/deserialize new messages",
            "C": "Topics are deleted",
            "D": "Passwords are reset"
        },
        "answer": "B"
    },
    {
        "question": "Which metric shows the rate of produced messages that were rejected due to being too large?",
        "options": {
            "A": "FailedProduceRequestsPerSec",
            "B": "MessageSizeExceededRate",
            "C": "BytesInPerSec",
            "D": "BrokerState"
        },
        "answer": "A"
    },
    {
        "question": "What is 'OS Page Cache' utilization?",
        "options": {
            "A": "Storing web pages",
            "B": "How efficiently Kafka is reading/writing to the system's memory cache instead of direct disk I/O",
            "C": "The number of windows open",
            "D": "The CPU cache speed"
        },
        "answer": "B"
    },
    {
        "question": "What does 'max.poll.interval.ms' tuning prevent?",
        "options": {
            "A": "Network outages",
            "B": "Unnecessary consumer rebalances caused by long-running processing logic",
            "C": "Disk failure",
            "D": "Password expiry"
        },
        "answer": "B"
    },
    {
        "question": "Which tool is used to simulate high load on a Kafka cluster for testing?",
        "options": {
            "A": "kafka-producer-perf-test.sh",
            "B": "kafka-stress-test.sh",
            "C": "kafka-load-gen.sh",
            "D": "kafka-bench.sh"
        },
        "answer": "A"
    },
    {
        "question": "What is the 'Request Handler' pool used for?",
        "options": {
            "A": "Managing network connections",
            "B": "Threads that perform the actual work of reading from and writing to the log on disk",
            "C": "Handling user logins",
            "D": "Monitoring the UI"
        },
        "answer": "B"
    },
    {
        "question": "Final question: Which parameter helps balance throughput and latency in a Producer?",
        "options": {
            "A": "batch.size",
            "B": "linger.ms",
            "C": "Both A and B",
            "D": "topic.name"
        },
        "answer": "C"
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
    skill = "kafka"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
