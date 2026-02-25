from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
    {
        "question": "What is the 'Cloud Computing' model where you only pay for the resources you use?",
        "options": {
            "A": "Fixed-cost model",
            "B": "Consumption-based model",
            "C": "Prepaid-only model",
            "D": "Physical-asset model"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure service is used to manage user identities and provide secure access to resources?",
        "options": {
            "A": "Azure Sentinel",
            "B": "Microsoft Entra ID (formerly Azure AD)",
            "C": "Azure Bastion",
            "0": "Azure Policy"
        },
        "answer": "B"
    },
    {
        "question": "What is an Azure 'Region'?",
        "options": {
            "A": "A single data center",
            "B": "A set of data centers deployed within a latency-defined perimeter and connected through a dedicated regional low-latency network",
            "C": "A specific country's entire cloud infrastructure",
            "D": "A group of user accounts"
        },
        "answer": "B"
    },
    {
        "question": "What are 'Availability Zones' (AZs) in Azure?",
        "options": {
            "A": "Different countries where Azure is available",
            "B": "Physically separate locations within an Azure region that provide protection against data center failures",
            "C": "Virtual sections of a single server",
            "D": "Backup drives for the cloud"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure compute service is best for running virtual machines in the cloud?",
        "options": {
            "A": "Azure Functions",
            "B": "Azure Virtual Machines (VMs)",
            "C": "Azure App Service",
            "D": "Azure Container Instances"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure App Service'?",
        "options": {
            "A": "A service for physical app delivery",
            "B": "A fully managed HTTP-based service for hosting web applications, REST APIs, and mobile backends",
            "C": "A database for storing app data",
            "D": "A tool to monitor phone battery"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Functions'?",
        "options": {
            "A": "A math library for C#",
            "B": "A serverless solution that allows you to write less code, maintain less infrastructure, and save on costs",
            "C": "A type of physical hardware",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure service provides a managed environment for running containerized applications without managing VMs?",
        "options": {
            "A": "Azure Virtual Desktop",
            "B": "Azure Container Instances (ACI)",
            "C": "Azure Batch",
            "D": "Azure Disk Storage"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Kubernetes Service' (AKS)?",
        "options": {
            "A": "A service to manage physical servers",
            "B": "A managed container orchestration service based on the open-source Kubernetes system",
            "C": "A type of storage volume",
            "D": "A version of Azure for developers only"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure component represents a logical grouping of Azure services that are billed together?",
        "options": {
            "A": "Resource Group",
            "B": "Azure Subscription",
            "C": "Management Group",
            "D": "Tenant"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Resource Group' in Azure?",
        "options": {
            "A": "A way to group employees by department",
            "B": "A container that holds related resources for an Azure solution",
            "C": "A physical server rack",
            "D": "A type of network cable"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Resource Manager' (ARM)?",
        "options": {
            "A": "A person who manages physical assets",
            "B": "The deployment and management service for Azure that provides a management layer for creating, updating, and deleting resources",
            "C": "A hardware monitor",
            "D": "A security guard for data centers"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Virtual Desktop'?",
        "options": {
            "A": "A physical computer in the cloud",
            "B": "A desktop and app virtualization service that runs on the cloud",
            "C": "A screensaver for Azure users",
            "D": "A tool to design the UI"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure service is a globally distributed, multi-model database service?",
        "options": {
            "A": "Azure SQL Database",
            "B": "Azure Cosmos DB",
            "C": "Azure Table Storage",
            "D": "Azure Cache for Redis"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure SQL Database'?",
        "options": {
            "A": "A manual for SQL users",
            "B": "A fully managed relational database with auto-scaling, integral high availability, and enterprise-grade security",
            "C": "A type of text file",
            "D": "A programming language"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure service is a managed, in-memory data store used to improve performance of applications?",
        "options": {
            "A": "Azure Blob Storage",
            "B": "Azure Cache for Redis",
            "C": "Azure Queue Storage",
            "D": "Azure Data Lake"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Blob Storage'?",
        "options": {
            "A": "A service for storing small blobs of jelly",
            "B": "Azure's object storage solution for the cloud, optimized for storing massive amounts of unstructured data",
            "C": "A database for user profiles",
            "D": "A security scan tool"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure storage service is best for highly available network file shares?",
        "options": {
            "A": "Azure Disk Storage",
            "B": "Azure Files",
            "C": "Azure Blob Storage",
            "D": "Azure Table Storage"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Virtual Network' (VNet)?",
        "options": {
            "A": "A social network for Azure fans",
            "B": "The fundamental building block for your private network in Azure",
            "C": "A high-speed Wi-Fi connection",
            "D": "A tool to track server location"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure VPN Gateway'?",
        "options": {
            "A": "A physical portal",
            "B": "A specific type of virtual network gateway that is used to send encrypted traffic between an Azure virtual network and an on-premises location",
            "C": "A browser extension",
            "D": "A network security monitor"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure service provides a dedicated, private connection between your on-premises infrastructure and Azure data centers?",
        "options": {
            "A": "Azure VPN",
            "B": "Azure ExpressRoute",
            "C": "Azure Peering",
            "D": "Azure Front Door"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure DNS'?",
        "options": {
            "A": "A tool to rename the cluster",
            "B": "A hosting service for DNS domains that provides name resolution using Microsoft Azure infrastructure",
            "C": "A security certificate",
            "D": "A list of developer names"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Load Balancer'?",
        "options": {
            "A": "A person who carries server equipment",
            "B": "A Layer-4 (TCP, UDP) load balancer that distributes incoming traffic among healthy service instances",
            "C": "A type of storage volume",
            "D": "A power supply"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Application Gateway'?",
        "options": {
            "A": "A physical gate at the data center",
            "B": "A web traffic load balancer that enables you to manage traffic to your web applications (Layer 7)",
            "C": "A database for app logs",
            "D": "A tool to measure internet speed"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure service is a managed Distributed Denial of Service (DDoS) protection service?",
        "options": {
            "A": "Azure Sentinel",
            "B": "Azure DDoS Protection",
            "C": "Azure Key Vault",
            "D": "Azure Bastion"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Firewall'?",
        "options": {
            "A": "A physical fire extinguisher",
            "B": "A managed, cloud-based network security service that protects your Azure Virtual Network resources",
            "C": "A password manager",
            "D": "An encryption tool"
        },
        "answer": "B"
    },
    {
        "question": "Which service acts as a secure, managed gateway to provide RDP and SSH access to VMs without public IP addresses?",
        "options": {
            "A": "Azure VPN",
            "B": "Azure Bastion",
            "C": "Azure ExpressRoute",
            "D": "Azure Private Link"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Key Vault' used for?",
        "options": {
            "A": "A place to store physical keys",
            "B": "A cloud service for securely storing and accessing secrets, keys, and certificates",
            "C": "A database for user profiles",
            "D": "A security report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Policy'?",
        "options": {
            "A": "A legal contract with Microsoft",
            "B": "A service used to create, assign, and manage policies that enforce different rules over your resources",
            "C": "A list of company rules",
            "D": "A training course"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Blueprints'?",
        "options": {
            "A": "Architectural drawings of data centers",
            "B": "A way to define a repeatable set of Azure resources that implement and adhere to an organization's standards",
            "C": "A screensaver",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure service provides a comprehensive security management system for your infrastructure and cloud workloads?",
        "options": {
            "A": "Azure Monitor",
            "B": "Microsoft Defender for Cloud",
            "C": "Azure Policy",
            "D": "Azure Sentinel"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Sentinel'?",
        "options": {
            "A": "A robot that guards servers",
            "B": "A cloud-native Security Information and Event Management (SIEM) and Security Orchestration Automated Response (SOAR) solution",
            "C": "A tool to monitor network speed",
            "D": "A password manager"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Monitor'?",
        "options": {
            "A": "A high-resolution computer screen",
            "B": "A comprehensive solution for collecting, analyzing, and acting on telemetry from your cloud and on-premises environments",
            "C": "A tool to watch developers",
            "D": "A security scan tool"
        },
        "answer": "B"
    },
    {
        "question": "Which component of Azure Monitor provides a way to visually map and troubleshoot dependencies between applications?",
        "options": {
            "A": "Application Insights",
            "B": "Log Analytics",
            "C": "Azure Advisor",
            "D": "Azure Service Health"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Azure Advisor'?",
        "options": {
            "A": "A Microsoft employee you can call",
            "B": "A personalized cloud consultant that helps you follow best practices to optimize your Azure deployments",
            "C": "A tool for financial planning",
            "D": "A software library"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Service Health'?",
        "options": {
            "A": "A health insurance plan for developers",
            "B": "A suite of experiences that provide personalized guidance and support when Azure service issues affect you",
            "C": "A type of unit test",
            "D": "A hardware monitor"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure DevOps'?",
        "options": {
            "A": "A team of developers at Microsoft",
            "B": "A suite of services that provides developer services for support teams to plan work, collaborate on code development, and build/deploy applications",
            "C": "A training manual",
            "D": "A security protocol"
        },
        "answer": "B"
    },
    {
        "question": "Which service provides a managed platform for data integration and transformation (ETL)?",
        "options": {
            "A": "Azure Synapse Analytics",
            "B": "Azure Data Factory",
            "C": "Azure Stream Analytics",
            "D": "Azure Databricks"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Synapse Analytics'?",
        "options": {
            "A": "A tool for biological research",
            "B": "An enterprise analytics service that accelerates time to insight across data warehouses and big data systems",
            "C": "A high-speed database for gaming",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Databricks'?",
        "options": {
            "A": "A physical brick used for data center construction",
            "B": "An Apache Spark-based analytics platform optimized for the Microsoft Azure cloud",
            "C": "A tool to build websites",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure service is an enterprise-grade AI service for conversational AI (bots)?",
        "options": {
            "A": "Azure Machine Learning",
            "B": "Azure AI Bot Service",
            "C": "Azure Cognitive Search",
            "D": "Azure Video Indexer"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Machine Learning'?",
        "options": {
            "A": "A training program for machines",
            "B": "A cloud-based environment used to train, deploy, automate, manage, and track ML models",
            "C": "A specialized AI training chip",
            "D": "A database for AI research"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure IoT Hub'?",
        "options": {
            "A": "A central meeting place for IoT devices",
            "B": "A managed service that acts as a central message hub for bi-directional communication between your IoT application and the devices it manages",
            "C": "A physical router for IoT",
            "D": "A security scanner for smart homes"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure service provides a serverless platform for connecting apps, data, and systems using workflows?",
        "options": {
            "A": "Azure Functions",
            "B": "Azure Logic Apps",
            "C": "Azure Event Grid",
            "D": "Azure Service Bus"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Event Grid'?",
        "options": {
            "A": "A physical grid for electricity",
            "B": "A highly scalable, serverless event broker that you can use to integrate applications using events",
            "C": "A tool to schedule meetings",
            "D": "A network security tool"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Service Bus'?",
        "options": {
            "A": "A physical bus for Azure employees",
            "B": "A fully managed enterprise message broker with message queues and publish-subscribe topics",
            "C": "A database for messaging logs",
            "D": "A tool to track server uptime"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure service is a managed cloud-based identity and access management service for your web and mobile applications?",
        "options": {
            "A": "Microsoft Entra ID",
            "B": "Azure AD B2C",
            "C": "Azure AD Domain Services",
            "D": "Azure AD App Proxy"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Cost Management + Billing'?",
        "options": {
            "A": "A tool to ask for a raise",
            "B": "A suite of tools provided by Microsoft that help you analyze, manage, and optimize the costs of your workloads",
            "C": "A spreadsheet of company expenses",
            "D": "A way to reduce the price of Blob Storage"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Azure Cloud Shell'?",
        "options": {
            "A": "A physical shell from the beach",
            "B": "An interactive, browser-accessible shell for managing Azure resources",
            "C": "A backup for the code",
            "D": "A type of container"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 1: What is the primary advantage of Azure 'Sovereign' Clouds (like Azure Government)?",
        "options": {
            "A": "They are faster than the public cloud",
            "B": "They meet the strict security and compliance requirements of specific governments or industries",
            "C": "They are free for government employees",
            "D": "They use a different color scheme for the portal"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure storage service is designed to store massive amounts of unstructured data such as text or binary data?",
        "options": {
            "A": "Azure Files",
            "B": "Azure Blob Storage",
            "C": "Azure Table Storage",
            "D": "Azure Queue Storage"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary purpose of 'Azure Virtual Network Peering'?",
        "options": {
            "A": "To connect your VNet to the internet",
            "B": "To seamlessly connect two Azure virtual networks in the same or different regions",
            "C": "To backup a virtual network to another account",
            "D": "To monitor the traffic on a subnet"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure SQL deployment option provides nearly 100% compatibility with the SQL Server (on-premises) engine?",
        "options": {
            "A": "Azure SQL Database",
            "B": "Azure SQL Managed Instance",
            "C": "Azure SQL Edge",
            "D": "Azure Cosmos DB"
        },
        "answer": "B"
    },
    {
        "question": "What are 'Azure Network Security Groups' (NSGs) used for?",
        "options": {
            "A": "To group users by their network access levels",
            "B": "To filter network traffic to and from Azure resources in an Azure virtual network",
            "C": "To encrypt the physical network cables",
            "D": "To manage the public IP addresses of the cluster"
        },
        "answer": "B"
    },
    {
        "question": "In Azure Blob Storage, which access tier is optimized for data that is accessed frequently?",
        "options": {
            "A": "Cool tier",
            "B": "Hot tier",
            "C": "Archive tier",
            "D": "Premium tier"
        },
        "answer": "B"
    },
    {
        "question": "Which service acts as a global, scalable entry point for web applications, providing Layer 7 load balancing and WAF capabilities?",
        "options": {
            "A": "Azure Load Balancer",
            "B": "Azure Front Door",
            "C": "Azure Traffic Manager",
            "D": "Azure ExpressRoute"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Cosmos DB' consistency level 'Strong'?",
        "options": {
            "A": "Data is eventually consistent across regions",
            "B": "Guarantees that a read always returns the most recent version of an item",
            "C": "Provides the highest performance with no guarantees",
            "D": "Only works for single-region databases"
        },
        "answer": "B"
    },
    {
        "question": "What is the role of 'Azure Private Link'?",
        "options": {
            "A": "A private chat service for Azure admins",
            "B": "Enables you to access Azure PaaS Services over a private endpoint in your virtual network",
            "C": "A tool to hide your subscription ID",
            "D": "A way to encrypt emails in Outlook"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure storage redundancy option replicates your data to a secondary region hundreds of miles away from the primary region?",
        "options": {
            "A": "Locally-redundant storage (LRS)",
            "B": "Geo-redundant storage (GRS)",
            "C": "Zone-redundant storage (ZRS)",
            "D": "Standard storage"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Traffic Manager' primarily used for?",
        "options": {
            "A": "Managing car traffic to Azure offices",
            "B": "A DNS-based traffic load balancer that enables you to distribute traffic optimally to services across global Azure regions",
            "C": "A tool to speed up the internet",
            "D": "A network security monitor"
        },
        "answer": "B"
    },
    {
        "question": "What is an 'Azure Managed Disk'?",
        "options": {
            "A": "A physical DVD sent by Microsoft",
            "B": "Block-level storage volumes that are managed by Azure and used with Azure Virtual Machines",
            "C": "A database for storing disk logs",
            "D": "A cloud-based floppy disk"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure service is a managed relational database specifically for the PostgreSQL engine?",
        "options": {
            "A": "Azure SQL Database",
            "B": "Azure Database for PostgreSQL",
            "C": "Azure Cosmos DB",
            "D": "Azure Table Storage"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Application Gateway' Web Application Firewall (WAF) primarily protecting against?",
        "options": {
            "A": "Physical theft of servers",
            "B": "Common web vulnerabilities like SQL injection and cross-site scripting",
            "C": "Unauthorized user logins to the portal",
            "D": "Hardware failure"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Blob Storage' lifecycle management?",
        "options": {
            "A": "The lifespan of the physical hard drive",
            "B": "A rule-based policy used to transition blob data to the appropriate access tiers or at the end of the data's lifecycle",
            "C": "A backup for the database",
            "D": "A security policy for passwords"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure service is a fully managed NoSQL database for key-value and document data?",
        "options": {
            "A": "Azure SQL",
            "B": "Azure Cosmos DB",
            "C": "Azure Database for MariaDB",
            "D": "Azure Synapse"
        },
        "answer": "B"
    },
    {
        "question": "What is an 'Azure VNet Subnet'?",
        "options": {
            "A": "A smaller network inside the VNet used to organize resources",
            "B": "A backup for the VNet",
            "C": "The physical port on a router",
            "D": "A type of security certificate"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Azure ExpressRoute' Global Reach?",
        "options": {
            "A": "A way to use Azure for free worldwide",
            "B": "A feature that connects your on-premises networks through the ExpressRoute service across the Microsoft global network",
            "C": "A high-speed satellite internet",
            "D": "A marketing program"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Data Lake Storage Gen2'?",
        "options": {
            "A": "A service for fishing data",
            "B": "A set of capabilities dedicated to big data analytics, built on Azure Blob Storage",
            "C": "A type of unit test",
            "D": "A hardware monitor"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure service is used to host enterprise-level network file shares?",
        "options": {
            "A": "Azure Blob Storage",
            "B": "Azure Files",
            "C": "Azure Queue Storage",
            "D": "Azure Disk Storage"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Route Server'?",
        "options": {
            "A": "A tool to rename the server",
            "B": "A service that simplifies dynamic routing between your network virtual appliance and your virtual network",
            "C": "A security certificate",
            "D": "A list of developer names"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Virtual WAN'?",
        "options": {
            "A": "A social network for wide area networks",
            "B": "A networking service that brings many networking, security, and routing functionalities together to provide a single operational interface",
            "C": "A high-speed Wi-Fi connection",
            "D": "A tool to track server location"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Firewall' Premium primarily offering over Standard?",
        "options": {
            "A": "A different color theme",
            "B": "Advanced threat protection capabilities like IDPS and TLS inspection",
            "C": "More public IPs",
            "D": "A faster UI"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Default' outbound access for Azure VMs?",
        "options": {
            "A": "Completely blocked by default",
            "B": "Open to the internet via an auto-assigned public IP (Legacy behavior)",
            "C": "Only allowed to other Azure services",
            "D": "A security threat"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure SQL' Always Encrypted?",
        "options": {
            "A": "A database that never closes",
            "B": "A feature designed to protect sensitive data by ensuring it is encrypted at rest and in transit, and only decrypted by authorized applications",
            "C": "A type of password",
            "D": "A backup strategy"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure storage type is used for 'Point-in-time' recovery of virtual machine data?",
        "options": {
            "A": "Blob Snapshots",
            "B": "Azure Disk Snapshots",
            "C": "Table Storage",
            "D": "Queue Storage"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Cosmos DB' Request Unit (RU)?",
        "options": {
            "A": "A measure of the developer's skill",
            "B": "The measure of throughput in Azure Cosmos DB, representing the cost of a database operation",
            "C": "A type of currency",
            "D": "A hardware limit"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure Networking service provides a dedicated IP address for a specific resource?",
        "options": {
            "A": "VNet Peering",
            "B": "Public IP Address",
            "C": "Network ACL",
            "D": "Route Table"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure NAT Gateway'?",
        "options": {
            "A": "A portal for users",
            "B": "A fully managed and highly resilient Network Address Translation (NAT) service for virtual networks",
            "C": "A type of unit test",
            "D": "A hardware lab"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure SQL Database' Serverless tier?",
        "options": {
            "A": "A database without a server",
            "B": "A compute tier for single databases that automatically scales compute based on workload demand",
            "C": "A database for developers only",
            "D": "A tool to edit SQL code"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Table Storage'?",
        "options": {
            "A": "A service for storing physical tables",
            "B": "A NoSQL key-value store for rapid development using massive semi-structured datasets",
            "C": "A database for user profiles",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Storage' Shared Access Signature (SAS)?",
        "options": {
            "A": "A physical signature on a document",
            "B": "A URI that grants restricted access rights to Azure Storage resources",
            "C": "A security certificate for the office",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Storage Explorer'?",
        "options": {
            "A": "A web browser",
            "B": "A standalone app that makes it easy to work with Azure Storage data on Windows, macOS, and Linux",
            "C": "A tool to search for physical storage",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Data Box'?",
        "options": {
            "A": "A physical box for server hardware",
            "B": "A service that provides devices to help you move large amounts of data to Azure in a cost-effective way",
            "C": "A virtual storage volume",
            "D": "A cloud backup"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure Networking component allows you to override Azure's default system routes?",
        "options": {
            "A": "User-Defined Routes (UDR)",
            "B": "Service Tags",
            "C": "Application Security Groups",
            "D": "VNet Flow Logs"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Azure Private Endpoint'?",
        "options": {
            "A": "The end of a network cable",
            "B": "A network interface that uses a private IP address from your virtual network for an Azure service",
            "C": "A secret IP address",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure SQL' Elastic Pool?",
        "options": {
            "A": "A swimming pool at Microsoft",
            "B": "A simple, cost-effective solution for managing and scaling multiple databases that have varying and unpredictable usage demands",
            "C": "A database for scaling UI",
            "D": "A backup tool"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure File Sync'?",
        "options": {
            "A": "Syncing files between your laptop and phone",
            "B": "A service that allows you to centralize your organization's file shares in Azure Files, while keeping the flexibility of an on-premises file server",
            "C": "A tool to backup code",
            "D": "A security policy"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Disk' Encryption?",
        "options": {
            "A": "Locking the physical disk in a safe",
            "B": "A feature that helps protect and safeguard your data to meet your organizational security and compliance commitments by encrypting VM disks",
            "C": "A password for the VM",
            "D": "Scaling the CPU"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Backup'?",
        "options": {
            "A": "A spare server",
            "B": "A cost-effective, one-click backup solution that's scalable based on your backup storage needs",
            "C": "A cloud region",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Site Recovery' (ASR)?",
        "options": {
            "A": "A tool to find lost files",
            "B": "A disaster recovery service that helps keep your business applications and workloads running during outages",
            "C": "A type of unit test",
            "D": "A hardware monitor"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Service Tag'?",
        "options": {
            "A": "A physical tag on a server",
            "B": "A predefined identifier that represents a group of IP address prefixes from a given Azure service",
            "C": "A name for a developer",
            "D": "A version of the API"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Application Security Group' (ASG)?",
        "options": {
            "A": "A group of security guards",
            "B": "Allows you to configure network security as an extension of an application's structure, rather than IP addresses",
            "C": "A type of unit test",
            "D": "A storage limit"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure SQL Database' Hyperscale?",
        "options": {
            "A": "A database for giant servers",
            "B": "A highly scalable service tier for single databases that can grow up to 100 TB in size",
            "C": "A tool for scaling UI",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Storage' soft delete?",
        "options": {
            "A": "Deleting files gently",
            "B": "A feature that allows you to recover data that was accidentally deleted or overwritten",
            "C": "A tool to delete logs",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Storage' Immutable Storage?",
        "options": {
            "A": "Storage that never changes",
            "B": "A feature that enables users to store business-critical data in a WORM (Write Once, Read Many) state",
            "C": "A type of unit test",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Database for MySQL'?",
        "options": {
            "A": "A managed database service based on the open-source MySQL engine",
            "B": "A tool to edit MySQL code",
            "C": "A security certificate",
            "D": "A hardware monitor"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Azure Database for MariaDB'?",
        "options": {
            "A": "A managed database service based on the open-source MariaDB engine",
            "B": "A tool to edit MariaDB code",
            "C": "A security certificate",
            "D": "A hardware monitor"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Azure Cosmos DB' Multi-Region Writes?",
        "options": {
            "A": "Writing code in different countries",
            "B": "A feature that allows you to write data to any region associated with your Cosmos DB account",
            "C": "A way to backup data",
            "D": "Scaling the CPU"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Cosmos DB' Change Feed?",
        "options": {
            "A": "A news feed for developers",
            "B": "A persistent record of changes to a container in the order they occurred",
            "C": "A tool to delete data",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 2: Which Azure Networking component provides a firewall for web applications?",
        "options": {
            "A": "Azure Load Balancer",
            "B": "Azure Application Gateway with WAF",
            "C": "Azure DNS",
            "D": "Azure ExpressRoute"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure service provides a central dashboard for monitoring the health of your Azure resources and applications?",
        "options": {
            "A": "Azure Sentinel",
            "B": "Azure Monitor",
            "C": "Azure Advisor",
            "D": "Azure Service Health"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Log Analytics'?",
        "options": {
            "A": "A tool to write code logs",
            "B": "A tool in the Azure portal used to edit and run log queries from data collected by Azure Monitor",
            "C": "A database for storing user names",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure service provides personalized recommendations based on your usage to improve cost, performance, and security?",
        "options": {
            "A": "Azure Monitor",
            "B": "Azure Advisor",
            "C": "Azure Policy",
            "D": "Azure Blueprints"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Service Health' primarily used for?",
        "options": {
            "A": "To track a developer's steps",
            "B": "To notify you about Azure service incidents, planned maintenance, and other health advisories",
            "C": "To monitor CPU performance",
            "D": "To scan for viruses"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure feature allows you to prevent accidental deletion or modification of critical resources?",
        "options": {
            "A": "Azure Policy",
            "B": "Resource Locks",
            "C": "Azure Blueprints",
            "D": "RBAC"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Policy' used for?",
        "options": {
            "A": "To pay the cloud bill",
            "B": "To enforce organizational standards and assess compliance at scale",
            "C": "To write documentation",
            "D": "To manage physical hardware"
        },
        "answer": "B"
    },
    {
        "question": "Which tool provides a unified view of security across all of your Azure, on-premises, and multi-cloud resources?",
        "options": {
            "A": "Azure Sentinel",
            "B": "Microsoft Defender for Cloud",
            "C": "Azure Key Vault",
            "D": "Azure Bastion"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Sentinel'?",
        "options": {
            "A": "A robot that guards data centers",
            "B": "A cloud-native SIEM (Security Information and Event Management) and SOAR solution",
            "C": "A network security monitor",
            "D": "A password manager"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Azure RBAC' (Role-Based Access Control)?",
        "options": {
            "A": "To assign roles in a movie",
            "B": "To manage who has access to Azure resources, what they can do with those resources, and what areas they have access to",
            "C": "To group servers by their physical role",
            "D": "To monitor the cluster"
        },
        "answer": "B"
    },
    {
        "question": "What is an 'Azure Blueprint'?",
        "options": {
            "A": "An architectural drawing",
            "B": "A way for declarative orchestration of various resource templates and other artifacts such as role assignments and policy assignments",
            "C": "A type of unit test",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure service is used to manage and rotate application secrets, such as API keys and passwords?",
        "options": {
            "A": "Azure Sentinel",
            "B": "Azure Key Vault",
            "C": "Azure Policy",
            "D": "Azure Monitor"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Bastion'?",
        "options": {
            "A": "A physical portal",
            "B": "A fully managed service that provides more secure and seamless RDP and SSH access to your virtual machines",
            "C": "A browser extension",
            "D": "A database for logs"
        },
        "answer": "B"
    },
    {
        "question": "Which tool provides a way to estimate the costs you will incur after migrating your workloads to Azure?",
        "options": {
            "A": "Azure Cost Explorer",
            "B": "Azure Pricing Calculator",
            "C": "Azure Advisor",
            "D": "TCO Calculator"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'Azure TCO (Total Cost of Ownership) Calculator'?",
        "options": {
            "A": "To see the price of a single VM",
            "B": "To estimate the cost savings of moving your on-premises workloads to Azure over a set period",
            "C": "To calculate the price of a hard drive",
            "D": "To pay the bill"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure service is used for governance, focusing on discovering and protecting sensitive information at scale?",
        "options": {
            "A": "Azure Policy",
            "B": "Microsoft Purview",
            "C": "Azure Blueprints",
            "D": "Azure Sentinel"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Cost Management + Billing' used for?",
        "options": {
            "A": "To ask for a raise",
            "B": "To analyze, manage, and optimize the costs of your cloud workloads",
            "C": "A spreadsheet for company lunch",
            "D": "A way to reduce the price of S3"
        },
        "answer": "B"
    },
    {
        "question": "Which Microsoft Entra ID feature helps identify and mitigate potential identity-based risks?",
        "options": {
            "A": "MFA",
            "B": "Entra ID Protection (formerly Azure AD Identity Protection)",
            "C": "Conditional Access",
            "D": "B2C"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Conditional Access' in Microsoft Entra ID?",
        "options": {
            "A": "Access only on weekends",
            "B": "A policy-based approach to grant or block access to resources based on specific signals (user, location, device)",
            "C": "Access for developers only",
            "D": "A way to bypass passwords"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Dedicated Host'?",
        "options": {
            "A": "A host for a party",
            "B": "A physical server dedicated to one Azure subscription, providing hardware isolation at the physical server level",
            "C": "A tool to host websites",
            "D": "A security guard"
        },
        "answer": "B"
    },
    {
        "question": "Which tool allows you to perform advanced threat hunting and investigation across your entire enterprise?",
        "options": {
            "A": "Azure Monitor",
            "B": "Microsoft Sentinel",
            "C": "Azure Policy",
            "D": "Azure Bastion"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Arc'?",
        "options": {
            "A": "A physical building",
            "B": "A bridge that extends Azure management and services to any infrastructure (on-premises, edge, multi-cloud)",
            "C": "A tool for data center construction",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Resource Graph'?",
        "options": {
            "A": "A chart of resources",
            "B": "An Azure service that allows you to query your resources at scale across multiple subscriptions",
            "C": "A way to delete resources",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "Which service acts as a 'Compliance' dashboard, showing how your organization measures up against industry standards?",
        "options": {
            "A": "Azure Advisor",
            "B": "Microsoft Purview Compliance Portal",
            "C": "Azure Monitor",
            "D": "Azure Sentinel"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Lighthouse'?",
        "options": {
            "A": "A light for data centers",
            "B": "A service that enables cross-tenant management for service providers to manage multiple customers at scale",
            "C": "A search engine for Azure",
            "D": "A type of firewall"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Information Protection' (AIP) used for?",
        "options": {
            "A": "To protect user names",
            "B": "To help organizations discover, classify, and protect documents and emails by applying labels",
            "C": "A tool to backup code",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Automation'?",
        "options": {
            "A": "Automatic updates of the OS",
            "B": "A cloud-based automation and configuration service that supports consistent management across Azure and non-Azure environments",
            "C": "A tool to write code",
            "D": "A hardware monitor"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure feature helps you track changes made to your resources over time for auditing purposes?",
        "options": {
            "A": "Azure Monitor",
            "B": "Azure Change Analysis",
            "C": "Azure Policy",
            "D": "Azure Advisor"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Microsoft Entra Privileged Identity Management' (PIM)?",
        "options": {
            "A": "A tool for high-level employees only",
            "B": "A service that enables you to manage, control, and monitor access to important resources in your organization",
            "C": "A type of password",
            "D": "A security report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Just-In-Time' (JIT) VM Access?",
        "options": {
            "A": "Access only when you are in the office",
            "B": "A feature that reduces exposure to brute force attacks by providing controlled access to VM management ports only when needed",
            "C": "Access for 1 hour only",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure AD B2C' (Business to Consumer)?",
        "options": {
            "A": "A way to sell items on Azure",
            "B": "A customer identity access management (CIAM) solution that supports millions of users and billions of authentications",
            "C": "A tool for business meetings",
            "D": "A database of company profiles"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure AD B2B' (Business to Business)?",
        "options": {
            "A": "A service to connect two companies' networks",
            "B": "A feature that allows you to share your organization's applications and services with guest users from any other organization",
            "C": "A way to buy hardware from Microsoft",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Security Benchmark'?",
        "options": {
            "A": "A test for security guards",
            "B": "A set of high-impact security recommendations you can use to help secure the services you use in Azure",
            "C": "A hardware limit",
            "D": "A security report"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure feature provides 'Tags' for resources?",
        "options": {
            "A": "Physical stickers on servers",
            "B": "Key-value pairs applied to resources to logically organize them into a taxonomy",
            "C": "Names for the developer",
            "D": "Version numbers"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary purpose of 'Azure Management Groups'?",
        "options": {
            "A": "To group people into teams",
            "B": "To provide a level of scope above subscriptions, allowing you to manage access, policy, and compliance for those subscriptions",
            "C": "To group resources by their color",
            "D": "To monitor the cluster"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Service Level Agreement' (SLA)?",
        "options": {
            "A": "A law about cloud speed",
            "B": "Microsoft's commitment to uptime and connectivity for Azure services",
            "C": "A training manual",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Reservation'?",
        "options": {
            "A": "Booking a desk at Microsoft",
            "B": "A way to save money by committing to a one-year or three-year plan for several products",
            "C": "A backup for the database",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Hybrid Benefit'?",
        "options": {
            "A": "Working from home",
            "B": "A licensing benefit that helps you significantly reduce the costs of running your workloads in the cloud using existing on-premises licenses",
            "C": "A tool for data center construction",
            "D": "A hardware monitor"
        },
        "answer": "B"
    },
    {
        "question": "Which tool in the Azure portal allows you to see your current and forecasted costs at a glance?",
        "options": {
            "A": "Azure Advisor",
            "B": "Azure Cost Analysis",
            "C": "Azure Budgets",
            "D": "Azure Policy"
        },
        "answer": "B"
    },
    {
        "question": "What is an 'Azure Budget' alert?",
        "options": {
            "A": "A notification that you are spending too much",
            "B": "A tool to set spending limits and be notified when you approach or exceed those limits",
            "C": "A way to ask for more money",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Quickstart Center'?",
        "options": {
            "A": "A fast car sponsored by Microsoft",
            "B": "A guided experience in the Azure portal to help you set up and configure your first Azure environment",
            "C": "A type of unit test",
            "D": "A hardware lab"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Migrate'?",
        "options": {
            "A": "A bird migration tracker",
            "B": "A central hub to discover, assess, and migrate on-premises servers, infrastructure, applications, and data to Azure",
            "C": "A way to move files between folders",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure tool provides a way to interact with Azure through a command-line interface available on Windows, macOS, and Linux?",
        "options": {
            "A": "Azure CLI",
            "B": "Azure PowerShell",
            "C": "Azure Cloud Shell",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Azure SDK' (Software Development Kit)?",
        "options": {
            "A": "A hardware kit for developers",
            "B": "A collection of libraries that make it easier to interact with Azure services from your preferred programming language",
            "C": "A training manual",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Resource Manager' (ARM) Template?",
        "options": {
            "A": "A physical template for server racks",
            "B": "A JSON file that defines the infrastructure and configuration for your Azure project",
            "C": "A list of developer names",
            "D": "A security log"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Bicep' in Azure?",
        "options": {
            "A": "A muscle in the arm",
            "B": "A Domain Specific Language (DSL) that uses declarative syntax to deploy Azure resources",
            "C": "A type of hardware",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Application Insights'?",
        "options": {
            "A": "A way to see inside a computer",
            "B": "An extensible Application Performance Management (APM) service for developers and DevOps professionals",
            "C": "A type of unit test",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Metrics'?",
        "options": {
            "A": "Measurements of physical server weight",
            "B": "Numerical values that describe some aspect of a system at a particular point in time",
            "C": "A way to sort files",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Log Analytics' workspace?",
        "options": {
            "A": "A physical office space",
            "B": "A unique environment for Azure Monitor log data, where each workspace has its own data repository and configuration",
            "C": "A type of unit test",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Activity Log'?",
        "options": {
            "A": "A log of physical movements in the office",
            "B": "A platform log in Azure that provides insight into subscription-level events (e.g., when a resource is modified)",
            "C": "A diary for developers",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 3: Which Azure feature provides a high-level overview of whether Microsoft is following security best practices?",
        "options": {
            "A": "Azure Advisor",
            "B": "Microsoft Service Trust Portal",
            "C": "Azure Policy",
            "D": "Azure Sentinel"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure service provides a comprehensive platform for building, training, and deploying machine learning models at scale?",
        "options": {
            "A": "Azure AI Services",
            "B": "Azure Machine Learning (Azure ML)",
            "C": "Azure AI Bot Service",
            "D": "Azure AI Search"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary purpose of 'Azure AI Services' (formerly Cognitive Services)?",
        "options": {
            "A": "To provide raw virtual machines for data scientists",
            "B": "To provide pre-built AI models for vision, speech, language, and decision-making via APIs",
            "C": "To backup the SQL database",
            "D": "To monitor network latency"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure AI service would you use to extract text, key-value pairs, and tables from documents automatically?",
        "options": {
            "A": "Azure AI Vision",
            "B": "Azure AI Document Intelligence",
            "C": "Azure AI Language",
            "D": "Azure AI Speech"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure DevOps Pipelines'?",
        "options": {
            "A": "A physical pipe in the data center",
            "B": "A cloud service that provides CI/CD to build, test, and deploy code to any target",
            "C": "A database for storing code versions",
            "D": "A tool to track developer work hours"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure service is a managed data factory used for creating, scheduling, and orchestrating ETL/ELT workflows?",
        "options": {
            "A": "Azure Synapse Analytics",
            "B": "Azure Data Factory",
            "C": "Azure Databricks",
            "D": "Azure Stream Analytics"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Databricks' primarily used for?",
        "options": {
            "A": "Building web apps in PHP",
            "B": "Big data analytics and machine learning based on Apache Spark",
            "C": "Hosting simple WordPress sites",
            "D": "Managing physical server cooling"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure service acts as a secure, managed message broker for highly reliable asynchronous communication?",
        "options": {
            "A": "Azure Event Grid",
            "B": "Azure Service Bus",
            "C": "Azure Queue Storage",
            "D": "Azure Notification Hubs"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure IoT Hub'?",
        "options": {
            "A": "A meeting room for IoT developers",
            "B": "A managed service that acts as a central message hub for bi-directional communication between IoT applications and devices",
            "C": "A physical router for smart homes",
            "D": "A database for sensor temperatures"
        },
        "answer": "B"
    },
    {
        "question": "Which service allows you to run containers on Azure without managing any virtual machines?",
        "options": {
            "A": "Azure Virtual Machines",
            "B": "Azure Container Instances (ACI)",
            "C": "Azure Kubernetes Service (AKS)",
            "D": "Azure Batch"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Azure Well-Architected Framework'?",
        "options": {
            "A": "A set of blueprints for Microsoft offices",
            "B": "A set of guiding tenets (Cost, Security, Reliability, etc.) used to improve the quality of a workload",
            "C": "A software library for C#",
            "D": "A cloud certification exam"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure tool helps you migrate on-premises servers, databases, and applications to Azure?",
        "options": {
            "A": "Azure Advisor",
            "B": "Azure Migrate",
            "C": "Azure Site Recovery",
            "D": "Azure Backup"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Arc'?",
        "options": {
            "A": "A physical server rack",
            "B": "A service that extends Azure management and services to any infrastructure, including on-premises and multi-cloud",
            "C": "A type of network bridge",
            "D": "A backup for the Azure Portal"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure AI service provides advanced search capabilities over a large amount of unstructured data using AI-powered indexing?",
        "options": {
            "A": "Azure AI Vision",
            "B": "Azure AI Search",
            "C": "Azure AI Language",
            "D": "Azure Open AI"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure OpenAI Service'?",
        "options": {
            "A": "An open-source version of Azure",
            "B": "Provides REST API access to OpenAI's powerful language models including GPT-4 and Embeddings within Azure's enterprise security",
            "C": "A community forum for AI",
            "D": "A tool to generate Azure PowerShell scripts"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary use of 'Azure Logic Apps'?",
        "options": {
            "A": "Writing complex C++ logic for games",
            "B": "Automating and orchestrating tasks, business processes, and workflows with little to no code",
            "C": "Scaling the CPU of a VM",
            "D": "Managing user passwords"
        },
        "answer": "B"
    },
    {
        "question": "Which service is a managed service for deploying, managing, and scaling OpenSearch clusters?",
        "options": {
            "A": "Azure AI Search",
            "B": "Azure Search Service",
            "C": "None (Azure uses Azure AI Search; OpenSearch is not a native top-level managed service like AWS)",
            "D": "Azure Monitor"
        },
        "answer": "C"
    },
    {
        "question": "What is 'Azure Stream Analytics'?",
        "options": {
            "A": "A video streaming service like Netflix",
            "B": "A real-time analytics and complex event-processing engine designed to analyze and process high volumes of fast-streaming data",
            "C": "A tool to measure internet download speed",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "Which tool provides a unified view of your application architecture and identifies high-risk areas based on best practices?",
        "options": {
            "A": "Azure Advisor",
            "B": "Azure Well-Architected Tool",
            "C": "Azure Config",
            "D": "Azure Monitor"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Site Recovery' (ASR) primarily for?",
        "options": {
            "A": "Finding lost files on a computer",
            "B": "Disaster recovery by replicating workloads from a primary site to a secondary location",
            "C": "Moving a website to a new domain",
            "D": "Deleting temporary files"
        },
        "answer": "B"
    },
    {
        "question": "What is an 'Azure Managed Identity'?",
        "options": {
            "A": "A fake name for a developer",
            "B": "An identity in Microsoft Entra ID that is automatically managed by Azure for an Azure resource (like a VM or Function)",
            "C": "A passport for the data center",
            "D": "A way to log in without a username"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure service is best for highly scalable, real-time ingestion of data from millions of devices?",
        "options": {
            "A": "Azure IoT Hub",
            "B": "Azure Event Hubs",
            "C": "Azure Service Bus",
            "D": "Azure Data Lake"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Blueprint' definition?",
        "options": {
            "A": "A physical photo of a server",
            "B": "A declarative way to orchestrate the deployment of various resource templates and other artifacts such as role and policy assignments",
            "C": "A list of developer names",
            "D": "A type of security certificate"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure service is a managed Redis cache that provides a secure, dedicated Redis cache?",
        "options": {
            "A": "Azure Cache for Redis",
            "B": "Azure Database for Redis",
            "C": "Azure Storage Cache",
            "D": "Azure MemoryDB"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Azure Front Door' WAF?",
        "options": {
            "A": "A physical door guard",
            "B": "A web application firewall integrated with Azure Front Door to protect at the edge",
            "C": "A security scan for the portal",
            "D": "A way to lock the VNet"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Azure Hybrid' cloud model?",
        "options": {
            "A": "A cloud that uses solar and wind power",
            "B": "A computing environment that combines a public cloud (Azure) and an on-premises infrastructure (private cloud)",
            "C": "Using both Azure and AWS",
            "D": "A laptop connected to the cloud"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Stack'?",
        "options": {
            "A": "A pile of Azure books",
            "B": "A family of products that extend Azure services and capabilities to your environment of choice (data center to edge)",
            "C": "A type of memory storage",
            "D": "A list of Azure services"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure AI service provides pre-built bots that can interact with users through text or speech?",
        "options": {
            "A": "Azure AI Language",
            "B": "Azure AI Bot Service",
            "C": "Azure AI Video Indexer",
            "D": "Azure AI Translator"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Cognitive Search' (now part of AI Search) 'Skillsets'?",
        "options": {
            "A": "The skills of the developer",
            "B": "A set of AI-driven enrichment steps used during the indexing process to extract information from data",
            "C": "A type of network bridge",
            "D": "A storage limit"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Container Registry' (ACR) 'Tasks'?",
        "options": {
            "A": "A to-do list for developers",
            "B": "A suite of features that automate container image builds, testing, and OS/framework patching",
            "C": "A way to delete old containers",
            "D": "A hardware monitor"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Blue-Green' deployment using Slots?",
        "options": {
            "A": "Using blue and green themes",
            "B": "Deploying to a staging slot and swapping with production to ensure zero-downtime updates",
            "C": "Scaling the CPU in different colors",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "Which service is a managed, highly available private registry for Docker and OCI images?",
        "options": {
            "A": "Azure Blob Storage",
            "B": "Azure Container Registry (ACR)",
            "C": "Azure Image Store",
            "D": "Azure DevOps Repos"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Static Web Apps'?",
        "options": {
            "A": "Websites that never change",
            "B": "A service that automatically builds and deploys full stack web apps to Azure from a code repository",
            "C": "A tool to design logos",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Machine Learning' Designer?",
        "options": {
            "A": "A tool for UI design",
            "B": "A drag-and-drop interface used to build, test, and deploy machine learning models visually",
            "C": "A training program for machines",
            "D": "A database for AI research"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure service is best for low-latency, real-time analytics on telemetry data from IoT devices?",
        "options": {
            "A": "Azure SQL",
            "B": "Azure Data Explorer",
            "C": "Azure Cosmos DB",
            "D": "Azure Synapse"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Digital Twins'?",
        "options": {
            "A": "A backup of the Azure portal",
            "B": "An IoT platform that enables you to create digital representations of real-world things, places, business processes, and people",
            "C": "Two identical Azure accounts",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Private Link' Service?",
        "options": {
            "A": "A private message service",
            "B": "A feature that allows you to provide your own service to other virtual networks over a private endpoint",
            "C": "A way to hide your IP",
            "D": "A security policy"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure DevOps service is used for planning and tracking work using Kanban boards or Backlogs?",
        "options": {
            "A": "Azure Pipelines",
            "B": "Azure Boards",
            "C": "Azure Repos",
            "D": "Azure Artifacts"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Repos'?",
        "options": {
            "A": "A place to buy Azure gear",
            "B": "A set of version control tools that you use to manage your code",
            "C": "A type of unit test",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Test Plans'?",
        "options": {
            "A": "A plan to test the office internet",
            "B": "A browser-based test management solution that provides capabilities for planned manual testing, user acceptance testing, and exploratory testing",
            "C": "A hardware lab",
            "D": "A security report"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure AI service provides pre-trained models to convert speech to text and text to speech?",
        "options": {
            "A": "Azure AI Vision",
            "B": "Azure AI Speech",
            "C": "Azure AI Translator",
            "D": "Azure AI Language"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure HDInsight'?",
        "options": {
            "A": "A type of monitor",
            "B": "A managed, full-spectrum, open-source analytics service for enterprises (Hadoop, Spark, Hive, etc.)",
            "C": "A security scan for hard drives",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Event Hubs' primarily used for?",
        "options": {
            "A": "A calendar for events",
            "B": "A big data streaming platform and event ingestion service",
            "C": "A tool to schedule meetings",
            "D": "A hardware monitor"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Application Proxy'?",
        "options": {
            "A": "A substitute developer",
            "B": "A feature that provides secure remote access to on-premises web applications using Entra ID",
            "C": "A type of storage volume",
            "D": "A network monitor"
        },
        "answer": "B"
    },
    {
        "question": "Which service helps you manage and automate your SSL/TLS certificates for use with Azure services?",
        "options": {
            "A": "Azure Policy",
            "B": "Azure Key Vault",
            "C": "Azure Bastion",
            "D": "Azure Sentinel"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Dedicated HSM'?",
        "options": {
            "A": "A physical safe for server keys",
            "B": "A service that provides managed hardware security modules (HSMs) in the cloud for cryptographic operations",
            "C": "A database for user profiles",
            "D": "A hardware lab"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Information Protection' (AIP) scanner?",
        "options": {
            "A": "A scanner for physical documents",
            "B": "A tool that discovers, labels, and protects files on network shares and SharePoint document libraries",
            "C": "A security scan for code",
            "D": "A hardware monitor"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Confidential Computing'?",
        "options": {
            "A": "Secretly using the cloud",
            "B": "Protects your data while it is in use by performing computation in a hardware-based Trusted Execution Environment (TEE)",
            "C": "A type of database",
            "D": "A security report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Front Door' Traffic Routing?",
        "options": {
            "A": "Monitoring car traffic",
            "B": "Determining how traffic is routed to different backends based on latency, priority, or weight",
            "C": "A security scan",
            "D": "A way to lock the VNet"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure Automation' Runbooks?",
        "options": {
            "A": "A book about Azure",
            "B": "A set of scripts used to automate recurring and time-consuming tasks across Azure and on-premises environments",
            "C": "A list of developer names",
            "D": "A security log"
        },
        "answer": "B"
    },
    {
        "question": "Final question: What is the primary advantage of 'Infrastructure as Code' (IaC) in Azure?",
        "options": {
            "A": "It makes the code look better",
            "B": "It enables rapid and consistent deployment of infrastructure through code, reducing manual errors and improving scalability",
            "C": "It is faster than the CLI",
            "D": "It provides free snacks"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure feature allows you to define a repeatable set of Azure resources that implement and adhere to an organization's standards, patterns, and requirements?",
        "options": {
            "A": "Azure Policy",
            "B": "Azure Blueprints",
            "C": "Azure Resource Graph",
            "D": "Azure Management Groups"
        },
        "answer": "B"
    },
    {
        "question": "When using Azure Cosmos DB, which consistency level offers the 'strongest' guarantee that a read always returns the most recent version of an item?",
        "options": {
            "A": "Session",
            "B": "Strong",
            "C": "Bounded Staleness",
            "D": "Eventual"
        },
        "answer": "B"
    },
    {
        "question": "Which Azure service provides a cloud-native SIEM and SOAR solution to help identify and respond to security threats across the entire enterprise?",
        "options": {
            "A": "Microsoft Defender for Cloud",
            "B": "Microsoft Sentinel",
            "C": "Azure Bastion",
            "D": "Azure Key Vault"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary function of Azure 'Conditional Access' policies within Microsoft Entra ID?",
        "options": {
            "A": "To provide access only on certain days of the week",
            "B": "To grant or block access to resources based on specific signals like user location, device state, and risk level",
            "C": "To allow users to access the Azure portal without a password",
            "D": "To automatically delete inactive user accounts"
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
    skill = "Azure"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
