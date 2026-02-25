from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
    {
        "question": "What is the primary goal of 'Continuous Integration' (CI)?",
        "options": {
            "A": "To keep the developers busy",
            "B": "To automate the merging of code changes from multiple contributors into a single project",
            "C": "To write documentation",
            "D": "To manually review all code"
        },
        "answer": "B"
    },
    {
        "question": "What does 'Continuous Delivery' ensure?",
        "options": {
            "A": "That code is always deployed to production automatically",
            "B": "That the software is always in a releasable state throughout its lifecycle",
            "C": "That the internet speed is constant",
            "D": "That the hardware is never replaced"
        },
        "answer": "B"
    },
    {
        "question": "What is the difference between 'Continuous Delivery' and 'Continuous Deployment'?",
        "options": {
            "A": "There is no difference",
            "B": "Deployment is fully automated to production; Delivery requires a manual trigger to release",
            "C": "Delivery is faster than deployment",
            "D": "Deployment is only for mobile apps"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Build Pipeline'?",
        "options": {
            "A": "A physical pipe in the server room",
            "B": "A set of automated processes that allow developers to compile, test, and deploy their code",
            "C": "A list of developer names",
            "D": "A database of images"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Artifact' in a CI/CD pipeline?",
        "options": {
            "A": "An old piece of code",
            "B": "The output of the build process (e.g., a JAR file, Docker image, or binary)",
            "C": "A security bug",
            "D": "A system log"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Unit Testing'?",
        "options": {
            "A": "Testing the entire system at once",
            "B": "Testing individual components or functions of the code in isolation",
            "C": "Testing the hardware",
            "D": "Testing the user's internet"
        },
        "answer": "B"
    },
    {
        "question": "Which CI/CD concept involves 'shifting left'?",
        "options": {
            "A": "Moving tasks to the end of the project",
            "B": "Performing testing and security checks earlier in the development lifecycle",
            "C": "Changing the layout of the UI",
            "D": "Deleting old code"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Blue-Green Deployment'?",
        "options": {
            "A": "Using blue and green themes for the website",
            "B": "Running two identical production environments to ensure zero-downtime updates",
            "C": "Scaling the UI to different colors",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Canary Release'?",
        "options": {
            "A": "Releasing code on a bird-shaped server",
            "B": "Rolling out a new feature to a small subset of users before making it available to everyone",
            "C": "A backup of the database",
            "D": "A manual code review"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Jenkins'?",
        "options": {
            "A": "A text editor",
            "B": "An open-source automation server used to build, test, and deploy software",
            "C": "A database tool",
            "D": "A browser plugin"
        },
        "answer": "B"
    },
    {
        "question": "What is 'GitOps'?",
        "options": {
            "A": "Operations performed by a person named Git",
            "B": "A paradigm that uses Git as the single source of truth for infrastructure and application configurations",
            "C": "A social network for developers",
            "D": "A way to store images"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Static Code Analysis'?",
        "options": {
            "A": "Running the code to see if it works",
            "B": "Debugging code without executing it to find potential bugs or security issues",
            "C": "Checking the hardware speed",
            "D": "Scaling the server"
        },
        "answer": "B"
    },
    {
        "question": "Which file is commonly used to define a GitHub Actions pipeline?",
        "options": {
            "A": "config.json",
            "B": "A YAML file in .github/workflows/",
            "C": "setup.exe",
            "D": "script.py"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'WebHook' in CI/CD?",
        "options": {
            "A": "A fishing tool for the web",
            "B": "An automated message sent from an app when something happens (e.g., code push) to trigger a pipeline",
            "C": "A browser bookmark",
            "D": "A security password"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Infrastructure as Code' (IaC)?",
        "options": {
            "A": "Building servers by hand",
            "B": "Managing and provisioning infrastructure through machine-readable definition files",
            "C": "Writing code for a calculator",
            "D": "Storing hardware in a database"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Self-healing' in the context of deployment?",
        "options": {
            "A": "The code fixing its own syntax errors",
            "B": "The ability of a system to detect failure and automatically restart or replace faulty components",
            "C": "Updating the OS automatically",
            "D": "A health check for developers"
        },
        "answer": "B"
    },
    {
        "question": "What does 'TDD' stand for?",
        "options": {
            "A": "Total Data Delivery",
            "B": "Test-Driven Development",
            "C": "Technical Design Document",
            "D": "Terminal Design Data"
        },
        "answer": "B"
    },
    {
        "question": "In CI/CD, what is 'Idempotency'?",
        "options": {
            "A": "Running a task twice and getting different results",
            "B": "Running an operation multiple times with the same result as running it once",
            "C": "A type of encryption",
            "D": "The speed of the pipeline"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Regression Testing'?",
        "options": {
            "A": "Testing new features only",
            "B": "Testing to ensure that new code changes haven't adversely affected existing features",
            "C": "Deleting old tests",
            "D": "Scaling the UI"
        },
        "answer": "B"
    },
    {
        "question": "Which tool is commonly used for 'Infrastructure as Code'?",
        "options": {
            "A": "Photoshop",
            "B": "Terraform",
            "C": "Excel",
            "D": "Chrome"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Code Coverage'?",
        "options": {
            "A": "The amount of code written in a day",
            "B": "A metric that measures the percentage of your source code that is executed during testing",
            "C": "A security scan",
            "D": "The file size of the project"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Smoke Testing'?",
        "options": {
            "A": "Testing the server room for fire",
            "B": "A set of preliminary tests to ensure the most vital functions of the software work",
            "C": "A type of stress test",
            "D": "Deleting temporary files"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Docker' in CI/CD?",
        "options": {
            "A": "To write documentation",
            "B": "To ensure that the software runs in the same environment from development to production",
            "C": "To backup the database",
            "D": "To speed up the internet"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Rolling Update'?",
        "options": {
            "A": "Updating the server while it's moving",
            "B": "Gradually replacing old versions of an application with new ones to avoid downtime",
            "C": "Deleting old logs",
            "D": "A hardware upgrade"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Environment Parity'?",
        "options": {
            "A": "Using the same wallpaper on all computers",
            "B": "Keeping the development, staging, and production environments as similar as possible",
            "C": "Scaling the CPU",
            "D": "A security policy"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Semantic Versioning' (SemVer)?",
        "options": {
            "A": "Naming versions based on the weather",
            "B": "A versioning scheme (MAJOR.MINOR.PATCH) that conveys meaning about the underlying changes",
            "C": "A random list of numbers",
            "D": "The order of files in a folder"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Dark Launching'?",
        "options": {
            "A": "Launching at night",
            "B": "Deploying code to production but keeping it hidden from users to test its impact on the system",
            "C": "A secret security scan",
            "D": "Deleting the model"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Master' or 'Main' branch in Git?",
        "options": {
            "A": "A branch for temporary experiments",
            "B": "The primary branch where the code is considered stable and ready for deployment",
            "C": "A deleted branch",
            "D": "The branch for security logs"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Feature Flag' (Feature Toggle)?",
        "options": {
            "A": "A literal flag on the server",
            "B": "A technique that allows developers to turn features on or off without deploying new code",
            "C": "A type of encryption",
            "D": "A hardware switch"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Linting'?",
        "options": {
            "A": "Cleaning the computer screen",
            "B": "The process of running a tool that analyzes source code for programmatic and stylistic errors",
            "C": "A type of unit test",
            "D": "A database backup"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Automated Rollback'?",
        "options": {
            "A": "A car feature",
            "B": "The ability to automatically revert to a previous stable version if a new deployment fails",
            "C": "Deleting old code",
            "D": "A manual update"
        },
        "answer": "B"
    },
    {
        "question": "Which tool is commonly used for 'Container Orchestration' in CD?",
        "options": {
            "A": "Photoshop",
            "B": "Kubernetes",
            "C": "Excel",
            "D": "Notepad"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Staging Environment'?",
        "options": {
            "A": "A theater stage",
            "B": "An environment that mimics production for final testing before release",
            "C": "A temporary folder",
            "D": "A hardware lab"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Integration Testing'?",
        "options": {
            "A": "Testing a single function",
            "B": "Testing how different modules or services work together as a group",
            "C": "Testing the internet speed",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Pipeline as Code'?",
        "options": {
            "A": "Building a pipe by hand",
            "B": "Defining your CI/CD pipeline using a configuration file (like Jenkinsfile or .gitlab-ci.yml)",
            "C": "A physical server",
            "D": "A type of database"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Build Agent' (Runner)?",
        "options": {
            "A": "A secret spy",
            "B": "A machine or process that actually executes the steps defined in the pipeline",
            "C": "A type of hard drive",
            "D": "The user's monitor"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Secrets Management' in CI/CD?",
        "options": {
            "A": "Keeping secrets from the boss",
            "B": "Safely storing and managing sensitive data like API keys and passwords within the pipeline",
            "C": "Encryption for emails",
            "D": "A private chat"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Continuous Monitoring'?",
        "options": {
            "A": "Watching the screen all day",
            "B": "The process of tracking the performance and health of an application in production in real-time",
            "C": "Deleting logs",
            "D": "Scaling the CPU"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Post-mortem' in DevOps?",
        "options": {
            "A": "A medical exam",
            "B": "A meeting or document to analyze what went wrong after a system failure",
            "C": "A backup of code",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What does 'SLA' stand for?",
        "options": {
            "A": "Service Level Agreement",
            "B": "Static Logic Analysis",
            "C": "System Level Access",
            "D": "Service Logic Array"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Dependency Scanning'?",
        "options": {
            "A": "Scanning the hard drive",
            "B": "Checking project dependencies (libraries) for known security vulnerabilities",
            "C": "A type of unit test",
            "D": "Deleting unused files"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Helm' used for in CI/CD?",
        "options": {
            "A": "A ship's wheel",
            "B": "A package manager for Kubernetes to simplify deployment of applications",
            "C": "A browser",
            "D": "A database"
        },
        "answer": "B"
    },
    {
        "question": "What is 'UAT' (User Acceptance Testing)?",
        "options": {
            "A": "Testing by developers",
            "B": "The final phase of testing where real users test the software for its intended use",
            "C": "A hardware test",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Deployment Slot'?",
        "options": {
            "A": "A parking space",
            "B": "A separate instance of an app that allows for easy swapping between versions (e.g., staging to production)",
            "C": "A hardware port",
            "D": "A security cage"
        },
        "answer": "B"
    },
    {
        "question": "What is 'YAML'?",
        "options": {
            "A": "A programming language",
            "B": "A human-readable data serialization language often used for configuration files",
            "C": "A type of database",
            "D": "An encryption tool"
        },
        "answer": "B"
    },
    {
        "question": "What is the role of a 'Registry' (like Docker Hub) in CD?",
        "options": {
            "A": "Storing user names",
            "B": "A central repository to store and distribute container images used for deployment",
            "C": "A physical log book",
            "D": "A security firewall"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Containerization'?",
        "options": {
            "A": "Building a box",
            "B": "Packaging an application and all its dependencies into a single container",
            "C": "Deleting data",
            "D": "Scaling the CPU"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Agile' in software development?",
        "options": {
            "A": "Being very fast at typing",
            "B": "An iterative approach to software development that focuses on continuous delivery and customer feedback",
            "C": "A programming language",
            "D": "A type of database"
        },
        "answer": "B"
    },
    {
        "question": "What is 'DevOps'?",
        "options": {
            "A": "A person who develops apps",
            "B": "A set of practices that combines software development (Dev) and IT operations (Ops)",
            "C": "A software program",
            "D": "A security protocol"
        },
        "answer": "B"
    },
    {
        "question": "Final question: Which animal is the mascot for the 'Jenkins' project?",
        "options": {
            "A": "Dog",
            "B": "A butler (human)",
            "C": "Whale",
            "D": "Elephant"
        },
        "answer": "B"
    },
      {
        "question": "What is 'DevSecOps'?",
        "options": {
            "A": "A specialized security software",
            "B": "The practice of integrating security at every stage of the CI/CD pipeline",
            "C": "A team that only works on firewalls",
            "D": "A replacement for developers"
        },
        "answer": "B"
    },
    {
        "question": "What is 'DAST' (Dynamic Application Security Testing)?",
        "options": {
            "A": "Testing the code while it is idle",
            "B": "Testing the application for vulnerabilities while it is running",
            "C": "Checking the hardware speed",
            "D": "Scanning a Git repository"
        },
        "answer": "B"
    },
    {
        "question": "What is 'SAST' (Static Application Security Testing)?",
        "options": {
            "A": "Testing the UI in a browser",
            "B": "Analyzing source code or binaries for security vulnerabilities without executing them",
            "C": "A physical security check",
            "D": "Testing network latency"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Deployment Pipeline's' first stage usually called?",
        "options": {
            "A": "Production",
            "B": "Commit Stage (or Source Stage)",
            "C": "UAT",
            "D": "Archive"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Configuration Drift'?",
        "options": {
            "A": "Setting the computer to sleep",
            "B": "When the actual environment configuration deviates from the defined state in the code",
            "C": "A type of database backup",
            "D": "A slow internet connection"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Immutable Infrastructure'?",
        "options": {
            "A": "Changing servers every hour",
            "B": "Replacing the entire server with a new one rather than modifying it for updates",
            "C": "Making the code unreadable",
            "D": "A permanent backup"
        },
        "answer": "B"
    },
    {
        "question": "In CI/CD, what is 'Orchestration'?",
        "options": {
            "A": "Managing a musical group",
            "B": "Coordinating automated tasks across multiple systems or services",
            "C": "Writing new code",
            "D": "A manual update"
        },
        "answer": "B"
    },
    {
        "question": "What is 'A/B Deployment'?",
        "options": {
            "A": "Deploying only two files",
            "B": "Splitting traffic between two versions of an app to measure performance or user behavior",
            "C": "An alphabetical sorting of servers",
            "D": "A backup strategy"
        },
        "answer": "B"
    },
    {
        "question": "Which tool is often used for 'GitOps' to sync Kubernetes clusters with Git?",
        "options": {
            "A": "ArgoCD",
            "B": "Photoshop",
            "C": "Excel",
            "D": "Slack"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Parallelism' in a CI/CD pipeline?",
        "options": {
            "A": "Running tasks one by one",
            "B": "Executing multiple independent jobs or tests simultaneously to reduce pipeline time",
            "C": "A type of code encryption",
            "D": "Scaling the UI"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Runner' in GitLab CI?",
        "options": {
            "A": "A person who delivers hardware",
            "B": "A lightweight, isolated environment that executes the CI/CD jobs",
            "C": "A faster version of Git",
            "D": "A security auditor"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Artifact Repository'?",
        "options": {
            "A": "A museum for old code",
            "B": "A centralized location to store and manage build artifacts (e.g., JFrog Artifactory)",
            "C": "A database of user names",
            "D": "A security log"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Mean Time to Recovery' (MTTR)?",
        "options": {
            "A": "The time it takes to write code",
            "B": "The average time it takes to restore a service after a failure",
            "C": "The age of the server",
            "D": "The number of users online"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Mean Time Between Failures' (MTBF)?",
        "options": {
            "A": "The time to build a pipeline",
            "B": "The average time between the start of one failure and the start of the next",
            "C": "The speed of the network",
            "D": "The file size of the project"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Infrastructure Drift'?",
        "options": {
            "A": "Servers moving in a rack",
            "B": "When the state of the infrastructure changes over time due to manual edits",
            "C": "A type of network error",
            "D": "A hardware upgrade"
        },
        "answer": "B"
    },
    {
        "question": "What is 'ChatOps'?",
        "options": {
            "A": "Talking to other developers",
            "B": "Integrating development and operations tasks into a chat platform (like Slack) using bots",
            "C": "A new chat application",
            "D": "A security filter"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Self-Service' pipeline?",
        "options": {
            "A": "A pipeline that builds itself",
            "B": "Allowing developers to trigger deployments or provision infrastructure without intervention from Ops",
            "C": "A manual update process",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Environment Variables' in a pipeline?",
        "options": {
            "A": "To change the weather",
            "B": "To pass configuration data (like database URLs) into the build or deployment process",
            "C": "To name the files",
            "D": "To encrypt the OS"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to start a Jenkins build manually?",
        "options": {
            "A": "Start Build",
            "B": "Build Now",
            "C": "Execute",
            "D": "Launch"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Container Scanning'?",
        "options": {
            "A": "Scanning a box with a laser",
            "B": "The process of looking for vulnerabilities in the layers of a container image",
            "C": "Finding containers on a network",
            "D": "Deleting old containers"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Branching Strategy'?",
        "options": {
            "A": "A way to grow trees",
            "B": "A set of rules for how developers use Git branches (e.g., GitFlow, Trunk-based development)",
            "C": "A type of unit test",
            "D": "A hardware layout"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Trunk-based Development'?",
        "options": {
            "A": "Developing in a car trunk",
            "B": "A strategy where all developers work on a single shared branch (the 'trunk') and merge small changes frequently",
            "C": "Using only one file for code",
            "D": "A backup method"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Shift-Right' testing?",
        "options": {
            "A": "Moving tasks to the beginning",
            "B": "Performing testing in a production or post-production environment (e.g., monitoring, A/B testing)",
            "C": "Deleting the tests",
            "D": "Scaling the CPU"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Performance Testing'?",
        "options": {
            "A": "Testing a car",
            "B": "Evaluating how a system performs in terms of responsiveness and stability under a particular workload",
            "C": "Testing the color of the UI",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Chaos Engineering'?",
        "options": {
            "A": "Making a mess on purpose",
            "B": "The discipline of experimenting on a software system in production to build confidence in its resilience",
            "C": "Writing bad code",
            "D": "A security threat"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Secret Masking'?",
        "options": {
            "A": "Wearing a mask",
            "B": "The process of hiding sensitive data (like passwords) in pipeline logs to prevent exposure",
            "C": "Encrypted emails",
            "D": "A private chat"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Multi-tenancy' in CI/CD?",
        "options": {
            "A": "Many people living in one house",
            "B": "A single instance of a tool (like Jenkins) serving multiple teams or projects separately",
            "C": "A type of hard drive",
            "D": "Scaling the UI"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Pipeline Orchestration'?",
        "options": {
            "A": "Directing a symphony",
            "B": "The management of end-to-end workflows that involve multiple pipelines and environments",
            "C": "Writing a new script",
            "D": "A manual update"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Quality Gate'?",
        "options": {
            "A": "A physical gate at the office",
            "B": "A set of conditions that must be met before a project can move to the next stage of the pipeline",
            "C": "A type of unit test",
            "D": "A security password"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Deployment Freeze'?",
        "options": {
            "A": "Putting the server in a freezer",
            "B": "A period where no new code is allowed to be deployed to production (e.g., during holidays or major sales)",
            "C": "A crash of the system",
            "D": "A permanent backup"
        },
        "answer": "B"
    },
    {
        "question": "Which tool is commonly used for 'Continuous Monitoring'?",
        "options": {
            "A": "Prometheus",
            "B": "Photoshop",
            "C": "Excel",
            "D": "Word"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Compliance as Code'?",
        "options": {
            "A": "Following the rules in a book",
            "B": "Defining and managing compliance policies through code and automated tests",
            "C": "A type of unit test",
            "D": "A legal contract"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Synthetic Monitoring'?",
        "options": {
            "A": "Watching fake users",
            "B": "Using scripts to simulate user interactions with an application to monitor performance and availability",
            "C": "Checking the hardware speed",
            "D": "Deleting logs"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Post-deployment Verification'?",
        "options": {
            "A": "Checking the code before it is released",
            "B": "Automated tests run against a production environment immediately after a new deployment",
            "C": "A manual code review",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Serverless Deployment'?",
        "options": {
            "A": "Deploying without a computer",
            "B": "Deploying code to a cloud provider that manages the infrastructure automatically (e.g., AWS Lambda)",
            "C": "A physical server",
            "D": "A database tool"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Secret Rotation'?",
        "options": {
            "A": "Spinning the password",
            "B": "The process of periodically changing credentials (API keys, passwords) to minimize the impact of a leak",
            "C": "Deleting the password",
            "D": "A manual update"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Environment as a Service' (EaaS)?",
        "options": {
            "A": "The weather as a service",
            "B": "Automatically provisioning complete, isolated environments for testing or development on demand",
            "C": "A hardware lab",
            "D": "Scaling the CPU"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Load Balancing' in the context of CD?",
        "options": {
            "A": "Balancing the weight of the servers",
            "B": "Distributing network traffic across multiple servers to ensure reliability and performance",
            "C": "Scaling the UI",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Version Control System' (VCS)?",
        "options": {
            "A": "A tool to control the computer's volume",
            "B": "A system that tracks changes to files over time (e.g., Git)",
            "C": "A type of database",
            "D": "A hardware update"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Pull Request' (PR) / 'Merge Request' (MR)?",
        "options": {
            "A": "Asking for more data",
            "B": "A method of submitting contributions to an open development project",
            "C": "A type of unit test",
            "D": "A security password"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Code Review'?",
        "options": {
            "A": "To rewrite the whole program",
            "B": "To examine code for bugs and quality before it is merged into the main branch",
            "C": "A type of unit test",
            "D": "A manual update"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Continuous Feedback'?",
        "options": {
            "A": "The sound of a loud speaker",
            "B": "The process of providing results from automated tests and monitors back to developers in real-time",
            "C": "Deleting logs",
            "D": "Scaling the UI"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Fail Fast'?",
        "options": {
            "A": "Falling over quickly",
            "B": "A strategy where the pipeline stops immediately at the first sign of an error to save time",
            "C": "A type of stress test",
            "D": "Deleting temporary files"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Docker Swarm' in CD?",
        "options": {
            "A": "A group of bees",
            "B": "A native clustering and orchestration tool for Docker containers",
            "C": "A type of network",
            "D": "A security threat"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Infrastructure Automation'?",
        "options": {
            "A": "Building servers by hand",
            "B": "Using tools to automate the provisioning and management of IT infrastructure",
            "C": "A type of unit test",
            "D": "A hardware lab"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Blue-Green' Rollback?",
        "options": {
            "A": "Changing colors back",
            "B": "Quickly reverting traffic to the 'Green' environment if the 'Blue' environment fails after deployment",
            "C": "A type of unit test",
            "D": "A manual update"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Build Duration'?",
        "options": {
            "A": "The height of the server rack",
            "B": "The total time it takes for a CI/CD pipeline to complete its execution",
            "C": "The age of the code",
            "D": "The number of users"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Deployment Frequency'?",
        "options": {
            "A": "How often the server is replaced",
            "B": "A DORA metric that measures how often an organization successfully releases to production",
            "C": "The speed of the network",
            "D": "The number of files"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Lead Time for Changes'?",
        "options": {
            "A": "The time it takes to buy a computer",
            "B": "A DORA metric that measures the time it takes for code to go from commit to production",
            "C": "A type of unit test",
            "D": "The speed of the pipeline"
        },
        "answer": "B"
    },
    {
        "question": "Final question: Which company originally created 'Kubernetes'?",
        "options": {
            "A": "Amazon",
            "B": "Google",
            "C": "Microsoft",
            "D": "IBM"
        },
        "answer": "B"
    },
    {
        "question": "In Jenkins, what is a 'Jenkinsfile'?",
        "options": {
            "A": "A file used to store user passwords",
            "B": "A text file that contains the definition of a Jenkins Pipeline as code",
            "C": "A backup of the server configuration",
            "D": "A list of installed plugins"
        },
        "answer": "B"
    },
    {
        "question": "What is the difference between 'Declarative' and 'Scripted' pipelines in Jenkins?",
        "options": {
            "A": "There is no difference",
            "B": "Declarative uses a stricter, pre-defined structure; Scripted uses Groovy-based logic",
            "C": "Declarative is only for Python",
            "D": "Scripted is faster than Declarative"
        },
        "answer": "B"
    },
    {
        "question": "In GitHub Actions, what is a 'Workflow'?",
        "options": {
            "A": "A social network for developers",
            "B": "An automated procedure added to a repository to build, test, package, release, or deploy",
            "C": "A manual code review",
            "D": "A database of images"
        },
        "answer": "B"
    },
    {
        "question": "What are 'Actions' in GitHub Actions?",
        "options": {
            "A": "The physical movement of the mouse",
            "B": "The smallest portable building block of a workflow (reusable code units)",
            "C": "The buttons in the UI",
            "D": "The number of users on a project"
        },
        "answer": "B"
    },
    {
        "question": "In GitLab CI/CD, which file is used to define the pipeline configuration?",
        "options": {
            "A": "config.json",
            "B": ".gitlab-ci.yml",
            "C": "setup.sh",
            "D": "pipeline.txt"
        },
        "answer": "B"
    },
    {
        "question": "What is the role of a 'Shared Runner' in GitLab?",
        "options": {
            "A": "A runner that only one person can use",
            "B": "A runner available to all projects in a GitLab instance",
            "C": "A runner that shares data between users",
            "D": "A hardware cable"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Terraform' primarily used for in a CI/CD context?",
        "options": {
            "A": "To write documentation",
            "B": "To provision and manage infrastructure using a high-level configuration language (HCL)",
            "C": "To edit images",
            "D": "To monitor the CPU"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Ansible' used for?",
        "options": {
            "A": "A type of database",
            "B": "Configuration management and application deployment automation",
            "C": "A social network",
            "D": "A browser plugin"
        },
        "answer": "B"
    },
    {
        "question": "In CI/CD pipelines, what is a 'Step'?",
        "options": {
            "A": "A physical staircase",
            "B": "An individual task that runs a command or an action",
            "C": "A user's rank",
            "D": "A network port"
        },
        "answer": "B"
    },
    {
        "question": "In CI/CD pipelines, what is a 'Job'?",
        "options": {
            "A": "The developer's salary",
            "B": "A set of steps that execute on the same runner",
            "C": "A type of unit test",
            "D": "A security log"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Matrix Build' (Strategy)?",
        "options": {
            "A": "Building code for the Matrix movie",
            "B": "A feature that allows running a job across multiple versions of a language or OS simultaneously",
            "C": "A 3D chart of the code",
            "D": "A security filter"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Cache' in CI/CD pipelines used for?",
        "options": {
            "A": "To store money",
            "B": "To store dependencies and build outputs to speed up subsequent pipeline runs",
            "C": "To delete old data",
            "D": "To encrypt the OS"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Docker-in-Docker' (DinD)?",
        "options": {
            "A": "Two physical boxes",
            "B": "A technique to run Docker containers inside a Docker container (common in CI agents)",
            "C": "A faster version of Docker",
            "D": "A security vulnerability"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Artifact Expiry'?",
        "options": {
            "A": "The code becoming too old to read",
            "B": "Setting a time limit after which build artifacts are automatically deleted to save space",
            "C": "A security password",
            "D": "A manual update"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Self-Hosted Runner'?",
        "options": {
            "A": "A runner that lives on its own",
            "B": "A machine that you manage yourself to run jobs for your CI/CD service (GitHub/GitLab)",
            "C": "A type of unit test",
            "D": "A hardware lab"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Replay' in Jenkins?",
        "options": {
            "A": "Playing a video of the build",
            "B": "A feature to re-run a pipeline while modifying the script temporarily for debugging",
            "C": "A backup of the code",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Pre-commit Hook'?",
        "options": {
            "A": "A fishing tool",
            "B": "A script that runs automatically before a 'git commit' to check for errors or styling",
            "C": "A type of unit test",
            "D": "A manual code review"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Deployment Environment'?",
        "options": {
            "A": "The weather outside the server room",
            "B": "The target system where the code is deployed (Dev, Staging, Prod)",
            "C": "A folder on a laptop",
            "D": "A security cage"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Blue Ocean' in Jenkins?",
        "options": {
            "A": "A type of fish",
            "B": "A modern, graphical user interface for Jenkins built for CD pipelines",
            "C": "A security update",
            "D": "A hardware manufacturer"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Parameter' in a pipeline?",
        "options": {
            "A": "A physical measurement",
            "B": "User-defined inputs provided when a pipeline is triggered (e.g., target branch)",
            "C": "The speed of the CPU",
            "D": "The number of users"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Cron Syntax' used for in CI/CD?",
        "options": {
            "A": "To write code",
            "B": "To schedule pipelines to run at specific times or intervals (nightly builds)",
            "C": "To encrypt data",
            "D": "To sort the files"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Kubernetes Operator' in CD?",
        "options": {
            "A": "A person driving a tractor",
            "B": "A method of packaging, deploying, and managing a Kubernetes application",
            "C": "A hardware cable",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Terraform State' file?",
        "options": {
            "A": "A list of US states",
            "B": "A file that keeps track of the resources Terraform has provisioned and their configuration",
            "C": "A backup of the code",
            "D": "A security log"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Plan' phase in Terraform?",
        "options": {
            "A": "Drawing a picture",
            "B": "Generating an execution plan to show what changes will be made before applying them",
            "C": "Writing new code",
            "D": "A manual update"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Apply' phase in Terraform?",
        "options": {
            "A": "Asking for a job",
            "B": "Executing the actions defined in a Terraform plan to reach the desired state",
            "C": "Scaling the CPU",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Configuration Management'?",
        "options": {
            "A": "Managing the office layout",
            "B": "The process of maintaining computer systems and software in a desired, consistent state",
            "C": "A type of unit test",
            "D": "A hardware lab"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Liquibase' or 'Flyway' used for in CI/CD?",
        "options": {
            "A": "Building websites",
            "B": "Database schema migration and version control automation",
            "C": "A social network",
            "D": "A browser plugin"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Pipeline Visualization'?",
        "options": {
            "A": "Seeing through pipes",
            "B": "A graphical representation of the stages, jobs, and status of a CI/CD workflow",
            "C": "A type of unit test",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'GitHub Secret'?",
        "options": {
            "A": "A secret about GitHub",
            "B": "Encrypted environment variables that are used to store sensitive information in GitHub Actions",
            "C": "A private message",
            "D": "A deleted branch"
        },
        "answer": "B"
    },
    {
        "question": "What is 'CircleCI'?",
        "options": {
            "A": "A circular server",
            "B": "A cloud-based CI/CD platform that automates the software development process",
            "C": "A type of database",
            "D": "A browser"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Travis CI'?",
        "options": {
            "A": "A person named Travis",
            "B": "A hosted continuous integration service used to build and test software projects on GitHub",
            "C": "A type of hard drive",
            "D": "A security firewall"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Azure DevOps'?",
        "options": {
            "A": "A cloud platform by Microsoft that provides developer services for teams to plan, develop, and deliver work",
            "B": "A blue server",
            "C": "A type of unit test",
            "D": "A hardware lab"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Code Pipeline' in AWS?",
        "options": {
            "A": "A physical pipe in Seattle",
            "B": "A fully managed continuous delivery service that helps you automate your release pipelines",
            "C": "A type of database",
            "D": "A security log"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Bitbucket Pipelines'?",
        "options": {
            "A": "An integrated CI/CD service, built into Bitbucket",
            "B": "A bucket of code",
            "C": "A security scan",
            "D": "A type of unit test"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Manifest' file in CD?",
        "options": {
            "A": "A list of passengers",
            "B": "A file that describes the desired state of a deployment (common in Kubernetes)",
            "C": "A backup of code",
            "D": "A security password"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Orchestrator'?",
        "options": {
            "A": "The conductor of an orchestra",
            "B": "A tool that coordinates the execution of tasks and workflows across multiple systems",
            "C": "A type of database",
            "D": "A hardware cable"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Web UI' of a CI server?",
        "options": {
            "A": "The physical monitor",
            "B": "The browser-based interface used to manage and monitor build jobs",
            "C": "The internet connection",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Docker Build' stage?",
        "options": {
            "A": "Building a shipping container",
            "B": "The stage where a Docker image is created from a Dockerfile",
            "C": "Scaling the CPU",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Image Tagging' in CI/CD?",
        "options": {
            "A": "Writing on a picture",
            "B": "Assigning labels (like 'latest' or a version number) to container images to identify them",
            "C": "A type of unit test",
            "D": "A hardware update"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Service Mesh' in CD context?",
        "options": {
            "A": "A type of network fabric",
            "B": "An infrastructure layer for handling service-to-service communication, often using a sidecar proxy",
            "C": "A security threat",
            "D": "A way to backup images"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Istio'?",
        "options": {
            "A": "A popular open-source service mesh",
            "B": "A Greek island",
            "C": "A type of database",
            "D": "A programming language"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Helm Chart'?",
        "options": {
            "A": "A map for a ship",
            "B": "A collection of files that describe a related set of Kubernetes resources",
            "C": "A type of unit test",
            "D": "A security password"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Multi-stage Docker Build' used for in CI?",
        "options": {
            "A": "To build for different countries",
            "B": "To create smaller final images by separating the build environment from the runtime environment",
            "C": "To scale the UI",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Pipeline Trigger'?",
        "options": {
            "A": "The start of a gun race",
            "B": "An event that initiates a pipeline run (e.g., code push, manual click, scheduled time)",
            "C": "A type of unit test",
            "D": "A security password"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Post-build Action'?",
        "options": {
            "A": "Tasks that run after the build process completes (e.g., sending emails, archiving artifacts)",
            "B": "Rebuilding the code",
            "C": "A type of unit test",
            "D": "A security scan"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Agentless' configuration management?",
        "options": {
            "A": "Managing without people",
            "B": "A system that doesn't require a permanent agent to be installed on target machines (e.g., Ansible)",
            "C": "A security threat",
            "D": "Scaling the CPU"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Push-based' deployment?",
        "options": {
            "A": "Pushing the server by hand",
            "B": "A model where the CI/CD server connects to and 'pushes' the code to the target environment",
            "C": "A manual update",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Pull-based' deployment?",
        "options": {
            "A": "Pulling a rope",
            "B": "A model where an agent in the target environment monitors for changes and 'pulls' them from the source",
            "C": "A type of unit test",
            "D": "A hardware lab"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Secret Masking' in logs?",
        "options": {
            "A": "Wearing a mask",
            "B": "Automatically hiding sensitive data from appearing in clear text in pipeline logs",
            "C": "Encrypted emails",
            "D": "A private chat"
        },
        "answer": "B"
    },
    {
        "question": "Final question: Which Groovy-based language is used for Jenkins pipeline scripts?",
        "options": {
            "A": "Python",
            "B": "Groovy",
            "C": "Java",
            "D": "Ruby"
        },
        "answer": "B"
    },
  {
        "question": "What is the primary purpose of 'Post-Mortem' analysis in a CI/CD culture?",
        "options": {
            "A": "To find someone to blame for the failure",
            "B": "To identify root causes and implement preventative measures without assigning blame",
            "C": "To delete old code logs",
            "D": "To restart the server manually"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Toil' in the context of Site Reliability Engineering (SRE)?",
        "options": {
            "A": "Creative development work",
            "B": "Manual, repetitive, and automatable work that provides no long-term value",
            "C": "Hardware maintenance",
            "D": "Writing documentation"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Error Budget'?",
        "options": {
            "A": "The amount of money spent on bugs",
            "B": "The maximum amount of time a system can be failing without violating an SLO",
            "C": "The total number of lines of code",
            "D": "A marketing budget for tech companies"
        },
        "answer": "B"
    },
    {
        "question": "In a pipeline, what is 'Hydration'?",
        "options": {
            "A": "Giving the servers water",
            "B": "The process of injecting configuration data into a generic manifest or template",
            "C": "Cleaning the database",
            "D": "Scaling the UI"
        },
        "answer": "B"
    },
    {
        "question": "What does 'SLO' stand for?",
        "options": {
            "A": "System Level Output",
            "B": "Service Level Objective",
            "C": "Standard Logic Operation",
            "D": "Security Layer Option"
        },
        "answer": "B"
    },
    {
        "question": "What is 'SLI'?",
        "options": {
            "A": "Service Level Indicator (a quantitative measure of some aspect of the level of service provided)",
            "B": "System Logic Interface",
            "C": "Standard Layout Image",
            "D": "Security Log In"
        },
        "answer": "A"
    },
    {
        "question": "What is 'MTTI'?",
        "options": {
            "A": "Mean Time to Install",
            "B": "Mean Time to Identify (the time between a failure occurring and it being detected)",
            "C": "Maximum Total Integration",
            "D": "Main Technical Input"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Downtime'?",
        "options": {
            "A": "The time spent sleeping",
            "B": "The period during which a system or service is unavailable",
            "C": "The time to build code",
            "D": "A system update"
        },
        "answer": "B"
    },
    {
        "question": "Which strategy involves deploying code to a single server first to verify stability?",
        "options": {
            "A": "Blue-Green",
            "B": "Canary",
            "C": "One-box",
            "D": "All-at-once"
        },
        "answer": "C"
    },
    {
        "question": "What is 'Feedback Loop' speed in CI/CD?",
        "options": {
            "A": "The volume of the speakers",
            "B": "How quickly a developer learns if their code change has broken something",
            "C": "The internet download speed",
            "D": "The rate of user comments"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Build Thrashing'?",
        "options": {
            "A": "Exercising in the server room",
            "B": "A situation where a high volume of commits causes the CI server to become overloaded and slow",
            "C": "Deleting a project",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Pre-flight Check'?",
        "options": {
            "A": "Checking for airplanes",
            "B": "A set of automated tests run on a local machine before pushing code to the repository",
            "C": "Buying a server",
            "D": "A manual update"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Pipeline Latency'?",
        "options": {
            "A": "The physical length of cables",
            "B": "The delay between a code commit and the completion of the deployment",
            "C": "The time it takes to type code",
            "D": "A network error"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Ephemeral Environment'?",
        "options": {
            "A": "A permanent server",
            "B": "A short-lived environment created for a specific purpose (e.g., testing a PR) and then destroyed",
            "C": "A database backup",
            "D": "A hardware port"
        },
        "answer": "B"
    },
    {
        "question": "What is 'GitFlow'?",
        "options": {
            "A": "The speed of the internet",
            "B": "A specific Git branching model that involves multiple branches for features, releases, and hotfixes",
            "C": "A type of unit test",
            "D": "A database tool"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Hotfix'?",
        "options": {
            "A": "A warm server",
            "B": "A critical bug fix deployed outside the regular release cycle to production",
            "C": "A security scan",
            "D": "A hardware update"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Squash Merge'?",
        "options": {
            "A": "Deleting a branch",
            "B": "Combining all commits from a feature branch into a single commit on the main branch",
            "C": "A type of database join",
            "D": "Scaling the UI"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Rebase' in Git?",
        "options": {
            "A": "Moving a branch to a new starting point to create a clean linear history",
            "B": "Deleting the database",
            "C": "Renaming a file",
            "D": "A security log"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Cherry-picking' in Git?",
        "options": {
            "A": "Choosing fruit",
            "B": "Applying a specific commit from one branch to another",
            "C": "Deleting a repository",
            "D": "A manual code review"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Infrastructure Orchestration'?",
        "options": {
            "A": "Conducting an orchestra",
            "B": "The automated arrangement, coordination, and management of complex computer systems and services",
            "C": "Writing new code",
            "D": "A hardware lab"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Descriptive Pipeline'?",
        "options": {
            "A": "A pipeline that talks",
            "B": "A pipeline defined by what the end state should be rather than how to get there",
            "C": "A manual script",
            "D": "A security filter"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Pull Model' of monitoring?",
        "options": {
            "A": "Pulling a rope",
            "B": "A system where the monitor periodically requests data from the services (e.g., Prometheus)",
            "C": "Deleting logs",
            "D": "Scaling the CPU"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Push Model' of monitoring?",
        "options": {
            "A": "Pushing the server",
            "B": "A system where services send their metrics to a centralized monitoring system",
            "C": "A manual update",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Gated Commit'?",
        "options": {
            "A": "A physical gate",
            "B": "A system that ensures code is only committed to the repository if it passes all tests",
            "C": "Deleting a branch",
            "D": "A manual update"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Golden Image'?",
        "options": {
            "A": "A photo made of gold",
            "B": "A template for a virtual machine or container that is pre-configured and ready for use",
            "C": "A security password",
            "D": "A database tool"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Bastion Host'?",
        "options": {
            "A": "A type of server rack",
            "B": "A special-purpose server used to access a private network from an external network safely",
            "C": "A database tool",
            "D": "A security log"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Secret Sprawl'?",
        "options": {
            "A": "Moving secrets to a new server",
            "B": "The uncontrolled and unmanaged distribution of sensitive information across various systems and files",
            "C": "Deleting passwords",
            "D": "Scaling the UI"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Zero Trust' Security?",
        "options": {
            "A": "Not trusting the boss",
            "B": "A security model that requires strict identity verification for every person and device trying to access resources",
            "C": "Deleting the firewall",
            "D": "A hardware update"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Sidecar Proxy'?",
        "options": {
            "A": "A proxy for motorcycles",
            "B": "A helper process that runs alongside a main application container to handle tasks like logging or network traffic",
            "C": "A security scan",
            "D": "Scaling the CPU"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Service Discovery'?",
        "options": {
            "A": "Finding new services to buy",
            "B": "The automatic detection of devices and services offered by a computer network",
            "C": "A database backup",
            "D": "A security log"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Stateful' application?",
        "options": {
            "A": "An application in a specific US state",
            "B": "An application that remembers client data from one session to the next",
            "C": "A type of unit test",
            "D": "Scaling the UI"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Stateless' application?",
        "options": {
            "A": "An application that does not store data on its own server, allowing it to be easily scaled",
            "B": "A broken application",
            "C": "A hardware lab",
            "D": "A security scan"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Circuit Breaker' pattern?",
        "options": {
            "A": "A physical fuse",
            "B": "A design pattern that prevents a system from repeatedly trying to perform an operation that is likely to fail",
            "C": "Deleting the database",
            "D": "Scaling the CPU"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Observability'?",
        "options": {
            "A": "Watching the screen",
            "B": "The ability to measure the internal state of a system based on its external outputs (logs, metrics, traces)",
            "C": "A security scan",
            "D": "Scaling the UI"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Tracing' in monitoring?",
        "options": {
            "A": "Drawing over a picture",
            "B": "Tracking the flow of a single request as it moves through multiple services in a system",
            "C": "Deleting old logs",
            "D": "A manual update"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Structured Logging'?",
        "options": {
            "A": "Writing logs in a notebook",
            "B": "Writing logs in a machine-readable format (like JSON) to make them easier to search and analyze",
            "C": "A security scan",
            "D": "Scaling the CPU"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Aggregation' of logs?",
        "options": {
            "A": "Collecting logs from multiple sources and storing them in a central location",
            "B": "Deleting logs",
            "C": "Renaming files",
            "D": "A security scan"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Alert Fatigue'?",
        "options": {
            "A": "Being tired of exercise",
            "B": "The exhaustion experienced when receiving too many monitoring alerts, leading to critical ones being ignored",
            "C": "Scaling the CPU",
            "D": "Deleting the database"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Incident Response'?",
        "options": {
            "A": "Answering the phone",
            "B": "The process of managing and resolving an IT service disruption",
            "C": "A manual update",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'On-call' rotation?",
        "options": {
            "A": "A phone call to the boss",
            "B": "A schedule where specific team members are responsible for responding to production incidents outside regular hours",
            "C": "Scaling the UI",
            "D": "A hardware update"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Compliance Audit' in CI/CD?",
        "options": {
            "A": "A legal review of code",
            "B": "A review of the pipeline and processes to ensure they meet internal and external standards",
            "C": "Deleting old tests",
            "D": "Scaling the CPU"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Binary Authorization'?",
        "options": {
            "A": "Counting with zeros and ones",
            "B": "A security control that ensures only trusted container images are deployed",
            "C": "Scaling the UI",
            "D": "A database tool"
        },
        "answer": "B"
    },
    {
        "question": "What is 'SBOM' (Software Bill of Materials)?",
        "options": {
            "A": "A list of developers",
            "B": "A comprehensive list of all software components and dependencies in an application",
            "C": "A type of unit test",
            "D": "A hardware lab"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Vulnerability Patching'?",
        "options": {
            "A": "Applying updates to fix security weaknesses in the software or infrastructure",
            "B": "Deleting code",
            "C": "Scaling the CPU",
            "D": "A manual update"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Air-gapped' environment?",
        "options": {
            "A": "An environment with a lot of fans",
            "B": "A highly secure environment that has no connection to the internet",
            "C": "Scaling the UI",
            "D": "A database backup"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Cloud-native' application?",
        "options": {
            "A": "An application built for the sky",
            "B": "An application specifically designed to run in a cloud environment using microservices and containers",
            "C": "A type of hardware",
            "D": "A security log"
        },
        "answer": "B"
    },
    {
        "question": "What is '12-Factor App' methodology?",
        "options": {
            "A": "12 steps to build a server",
            "B": "A set of best practices for building modern, cloud-native applications",
            "C": "12 different programming languages",
            "D": "A database tool"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Microservices' architecture?",
        "options": {
            "A": "A very small computer",
            "B": "Developing an application as a collection of small, independent services that communicate over a network",
            "C": "Scaling the CPU",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Monolith' architecture?",
        "options": {
            "A": "A large stone",
            "B": "Developing an application as a single, unified unit",
            "C": "Scaling the UI",
            "D": "A database backup"
        },
        "answer": "B"
    },
    {
        "question": "Final question: What is the most important cultural aspect of DevOps?",
        "options": {
            "A": "Having the fastest internet",
            "B": "Collaboration, trust, and shared responsibility between development and operations teams",
            "C": "Using the most expensive tools",
            "D": "Deleting bad code immediately"
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
    skill = "CICD"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
