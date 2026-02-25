from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
    {
        "question": "What is Jenkins primarily used for in a software development lifecycle?",
        "options": {
            "A": "Writing source code",
            "B": "Continuous Integration and Continuous Delivery (CI/CD)",
            "C": "Hosting web applications",
            "D": "Graphic design"
        },
        "answer": "B"
    },
    {
        "question": "Jenkins is primarily written in which programming language?",
        "options": {
            "A": "Python",
            "B": "Java",
            "C": "C++",
            "D": "Ruby"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Jenkins Job' (or Project)?",
        "options": {
            "A": "A career opening at Jenkins",
            "B": "A runnable task controlled by Jenkins, such as building or testing code",
            "C": "A database table",
            "D": "A type of user account"
        },
        "answer": "B"
    },
    {
        "question": "Which of the following is the default port for the Jenkins web interface?",
        "options": {
            "A": "80",
            "B": "8080",
            "C": "443",
            "D": "3306"
        },
        "answer": "B"
    },
    {
        "question": "What is 'JENKINS_HOME'?",
        "options": {
            "A": "The Jenkins website URL",
            "B": "The directory where Jenkins stores all its data, including configurations and build logs",
            "C": "The user's home folder",
            "D": "A plugin name"
        },
        "answer": "B"
    },
    {
        "question": "Which file format is used for the classic 'Jenkinsfile'?",
        "options": {
            "A": "JSON",
            "B": "Groovy",
            "C": "YAML",
            "D": "XML"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Freestyle project' in Jenkins?",
        "options": {
            "A": "A project without a deadline",
            "B": "A simple, GUI-based configuration for build jobs",
            "C": "A project that costs nothing",
            "D": "A job that can only run on Linux"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of a 'Build Trigger'?",
        "options": {
            "A": "To delete old builds",
            "B": "To define the criteria that start a Jenkins job automatically",
            "C": "To style the Jenkins UI",
            "D": "To stop the server"
        },
        "answer": "B"
    },
    {
        "question": "What does 'Poll SCM' do?",
        "options": {
            "A": "It asks users for feedback",
            "B": "It periodically checks the source code repository for changes to trigger a build",
            "C": "It deletes the repository",
            "D": "It encrypts the code"
        },
        "answer": "B"
    },
    {
        "question": "Which syntax is commonly used in 'Build Triggers' to schedule periodic builds (e.g., H/15 * * * *)?",
        "options": {
            "A": "Regex",
            "B": "Cron",
            "C": "SQL",
            "D": "Markdown"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Jenkins Plugin'?",
        "options": {
            "A": "A physical hardware connector",
            "B": "An extension that adds specific functionality to Jenkins (e.g., Git, Docker, Slack integration)",
            "C": "A type of build error",
            "D": "A security vulnerability"
        },
        "answer": "B"
    },
    {
        "question": "Where do you manage and install plugins in the Jenkins UI?",
        "options": {
            "A": "Job Configuration",
            "B": "Manage Jenkins -> Plugins",
            "C": "User Settings",
            "D": "Build History"
        },
        "answer": "B"
    },
    {
        "question": "What is the role of a 'Jenkins Master' (Controller)?",
        "options": {
            "A": "To do all the heavy lifting of builds",
            "B": "To manage the Jenkins environment, schedule jobs, and monitor nodes",
            "C": "To store source code",
            "D": "To act as a firewall"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Jenkins Agent' (Slave)?",
        "options": {
            "A": "A person who sells Jenkins",
            "B": "An executable that runs on a remote machine to offload build tasks from the master",
            "C": "A type of plugin",
            "D": "A security log"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Post-build Action'?",
        "options": {
            "A": "An action taken before a build starts",
            "B": "A task executed after the build completes, such as sending emails or archiving artifacts",
            "C": "Deleting the job",
            "D": "Restarting Jenkins"
        },
        "answer": "B"
    },
    {
        "question": "What is an 'Artifact' in Jenkins?",
        "options": {
            "A": "Ancient code",
            "B": "A file produced during a build (like a .jar, .war, or .exe) that is saved for later use",
            "C": "A broken plugin",
            "D": "A user's profile picture"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Console Output' in a build?",
        "options": {
            "A": "A video of the build",
            "B": "The real-time log of the commands and output produced during the build process",
            "C": "A chat room for developers",
            "D": "The source code editor"
        },
        "answer": "B"
    },
    {
        "question": "What does a 'Stable' build status mean (indicated by a blue/green ball)?",
        "options": {
            "A": "The server is fast",
            "B": "The build completed successfully without any reported errors",
            "C": "The build failed but the server is okay",
            "D": "The build is currently running"
        },
        "answer": "B"
    },
    {
        "question": "What does an 'Unstable' build status mean (indicated by a yellow ball)?",
        "options": {
            "A": "The server crashed",
            "B": "The build completed, but some tests failed or other issues were detected",
            "C": "The build was cancelled",
            "D": "The plugins are out of date"
        },
        "answer": "B"
    },
    {
        "question": "What does a 'Failed' build status mean (indicated by a red ball)?",
        "options": {
            "A": "The user logged out",
            "B": "The build process encountered a fatal error and did not complete",
            "C": "The build is waiting in queue",
            "D": "The job was deleted"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Pipeline as Code'?",
        "options": {
            "A": "Writing code in a pipe",
            "B": "Defining the entire CI/CD process in a text file (Jenkinsfile) checked into version control",
            "C": "A type of compiler",
            "D": "A database schema"
        },
        "answer": "B"
    },
    {
        "question": "Which plugin is required to use the 'Pipeline' feature in Jenkins?",
        "options": {
            "A": "Git Plugin",
            "B": "Pipeline Plugin",
            "C": "Docker Plugin",
            "D": "SSH Plugin"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Credentials Management' in Jenkins?",
        "options": {
            "A": "To store user birthdays",
            "B": "To securely store and manage passwords, SSH keys, and tokens used by jobs",
            "C": "To list the developer's skills",
            "D": "To manage the physical building security"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'WebHook' in the context of Jenkins and GitHub?",
        "options": {
            "A": "A tool to catch fish",
            "B": "A mechanism that allows GitHub to notify Jenkins immediately when code is pushed",
            "C": "A security vulnerability",
            "D": "A type of CSS styling"
        },
        "answer": "B"
    },
    {
        "question": "How do you restart Jenkins via the URL?",
        "options": {
            "A": "[jenkins-url]/stop",
            "B": "[jenkins-url]/safeRestart",
            "C": "[jenkins-url]/close",
            "D": "[jenkins-url]/init"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Blue Ocean'?",
        "options": {
            "A": "A type of server hardware",
            "B": "A modern, simplified user interface for Jenkins Pipelines",
            "C": "A cloud provider",
            "D": "A networking protocol"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Multi-configuration project' (Matrix Project)?",
        "options": {
            "A": "A project with many developers",
            "B": "A job that allows running the same build with various combinations of parameters (e.g., different OS or versions)",
            "C": "A movie-related project",
            "D": "A project with no configuration"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Discard Old Builds' used for?",
        "options": {
            "A": "To hide build errors",
            "B": "To save disk space by automatically deleting old build history and artifacts",
            "C": "To restart the build process",
            "D": "To archive every build forever"
        },
        "answer": "B"
    },
    {
        "question": "Which environment variable gives the build number of the current job?",
        "options": {
            "A": "BUILD_ID",
            "B": "BUILD_NUMBER",
            "C": "JOB_ID",
            "D": "CURRENT_BUILD"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Workspace' in a Jenkins job?",
        "options": {
            "A": "The office where developers work",
            "B": "The local directory on the agent where the job checks out source code and performs the build",
            "C": "The Jenkins dashboard",
            "D": "A shared network drive"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Distributed Builds' in Jenkins?",
        "options": {
            "A": "Builds that take a long time",
            "B": "Running build jobs across multiple agent machines to improve performance and scalability",
            "C": "Sending builds via email",
            "D": "Building in the cloud only"
        },
        "answer": "B"
    },
    {
        "question": "Which of the following is a way to trigger a build manually?",
        "options": {
            "A": "Deleting the job",
            "B": "Clicking 'Build Now' in the job dashboard",
            "C": "Restarting the computer",
            "D": "Editing the Jenkinsfile"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Build Parameter'?",
        "options": {
            "A": "A limit on the build size",
            "B": "A variable that allows users to provide input (like environment or version) when starting a build",
            "C": "A performance metric",
            "D": "A type of plugin"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Quiet Period'?",
        "options": {
            "A": "The time when Jenkins is muted",
            "B": "The number of seconds Jenkins waits after a trigger before actually starting the build",
            "C": "A period with no builds",
            "D": "The time taken to shut down"
        },
        "answer": "B"
    },
    {
        "question": "Which file is the core configuration file for Jenkins (found in JENKINS_HOME)?",
        "options": {
            "A": "jenkins.json",
            "B": "config.xml",
            "C": "settings.yaml",
            "D": "app.properties"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Executor' slots on a Jenkins node?",
        "options": {
            "A": "To kill running jobs",
            "B": "To define the number of concurrent jobs that can run on that specific node",
            "C": "To store backup files",
            "D": "To manage user logins"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Script Console' in Jenkins?",
        "options": {
            "A": "A place to write Python",
            "B": "A Groovy-based shell that allows administrators to run scripts for troubleshooting or automation within Jenkins",
            "C": "The job editor",
            "D": "A security firewall"
        },
        "answer": "B"
    },
    {
        "question": "What is 'LTS' in Jenkins versions?",
        "options": {
            "A": "Latest Technical System",
            "B": "Long Term Support (stable versions released every 12 weeks)",
            "C": "Low Tier Software",
            "D": "Live Tracking Service"
        },
        "answer": "B"
    },
    {
        "question": "Which command-line tool can be used to interact with Jenkins?",
        "options": {
            "A": "Jenkins-cli",
            "B": "J-cmd",
            "C": "Git",
            "D": "Docker"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Archive the artifacts'?",
        "options": {
            "A": "Deleting old code",
            "B": "Saving the output files of a build so they can be downloaded or used by other jobs later",
            "C": "Hiding the build history",
            "D": "Encrypting the results"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Downstream Project'?",
        "options": {
            "A": "A project that is failing",
            "B": "A project that is triggered automatically after the current (upstream) project finishes",
            "C": "A project stored on a lower server",
            "D": "A legacy project"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Upstream Project'?",
        "options": {
            "A": "A project that triggers another project (downstream) upon completion",
            "B": "A project in the cloud",
            "C": "A project with high priority",
            "D": "The main Jenkins website"
        },
        "answer": "A"
    },
    {
        "question": "Which plugin is commonly used to visualize unit test results in Jenkins?",
        "options": {
            "A": "Git Plugin",
            "B": "JUnit Plugin",
            "C": "Email Plugin",
            "D": "Dashboard Plugin"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Build History'?",
        "options": {
            "A": "The history of the Jenkins logo",
            "B": "A chronological list of previous executions of a specific job, including their results",
            "C": "The list of all developers",
            "D": "A backup of the source code"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Safe Mode' during Jenkins restart?",
        "options": {
            "A": "Restarting with no plugins",
            "B": "Waiting for all running jobs to complete before restarting the server",
            "C": "Restarting with no security",
            "D": "Restarting in the background"
        },
        "answer": "B"
    },
    {
        "question": "Which user role in Jenkins has full permissions by default?",
        "options": {
            "A": "Viewer",
            "B": "Admin",
            "C": "Developer",
            "D": "Guest"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Global Tool Configuration'?",
        "options": {
            "A": "Configuring the office tools",
            "B": "Setting up the paths for external tools like JDK, Maven, or Git so Jenkins can use them",
            "C": "Managing user accounts",
            "D": "Installing the Jenkins UI"
        },
        "answer": "B"
    },
    {
        "question": "What is 'View' in the Jenkins dashboard?",
        "options": {
            "A": "A way to see the server hardware",
            "B": "A custom grouping of jobs displayed on the main page for easier organization",
            "C": "A security report",
            "D": "The job editor"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Labels' on Jenkins agents?",
        "options": {
            "A": "To name the computer",
            "B": "To group agents so jobs can be restricted to run only on specific machines (e.g., 'linux' or 'docker')",
            "C": "To list the price of the server",
            "D": "To show the user's name"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 1: Which of the following is an open-source automation server that forked into Jenkins?",
        "options": {
            "A": "Travis CI",
            "B": "Hudson",
            "C": "CircleCI",
            "D": "Bamboo"
        },
        "answer": "B"
    },
    {
        "question": "What are the two main types of Pipeline syntax in Jenkins?",
        "options": {
            "A": "Scripted and Declarative",
            "B": "Static and Dynamic",
            "C": "JSON and XML",
            "D": "Manual and Automated"
        },
        "answer": "A"
    },
    {
        "question": "Which keyword is the entry point for a 'Declarative Pipeline'?",
        "options": {
            "A": "node",
            "B": "pipeline",
            "C": "start",
            "D": "job"
        },
        "answer": "B"
    },
    {
        "question": "In a Scripted Pipeline, which keyword is used to allocate an executor and workspace?",
        "options": {
            "A": "pipeline",
            "B": "node",
            "C": "agent",
            "D": "executor"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'agent' directive in a Declarative Pipeline?",
        "options": {
            "A": "To define the user who started the build",
            "B": "To specify where the entire Pipeline or a specific stage will execute",
            "C": "To install a security plugin",
            "D": "To send an email notification"
        },
        "answer": "B"
    },
    {
        "question": "Which 'agent' value is used to run a stage on any available executor?",
        "options": {
            "A": "agent none",
            "B": "agent any",
            "C": "agent label 'any'",
            "D": "agent all"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Stage' in a Jenkins Pipeline?",
        "options": {
            "A": "A physical platform for servers",
            "B": "A block that groups a subset of steps (e.g., 'Build', 'Test', 'Deploy')",
            "C": "A version of the Jenkins UI",
            "D": "A type of user permission"
        },
        "answer": "B"
    },
    {
        "question": "Which directive allows running multiple stages simultaneously in a Pipeline?",
        "options": {
            "A": "concurrent",
            "B": "parallel",
            "C": "simultaneous",
            "D": "group"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'post' section in a Declarative Pipeline used for?",
        "options": {
            "A": "To define the blog post about the build",
            "B": "To run actions depending on the build status (success, failure, always)",
            "C": "To send data to a POST endpoint",
            "D": "To configure the mail server"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Jenkins Shared Libraries'?",
        "options": {
            "A": "A collection of books about Jenkins",
            "B": "A way to share common Groovy code across multiple Pipelines to promote DRY (Don't Repeat Yourself)",
            "C": "A database of shared plugins",
            "D": "A public Jenkins server"
        },
        "answer": "B"
    },
    {
        "question": "In a Shared Library, where should global variables/functions be stored?",
        "options": {
            "A": "src/ directory",
            "B": "vars/ directory",
            "C": "resources/ directory",
            "D": "root directory"
        },
        "answer": "B"
    },
    {
        "question": "Which directive is used to import a Shared Library into a Jenkinsfile?",
        "options": {
            "A": "import library",
            "B": "@Library('my-shared-library')",
            "C": "use shared_lib",
            "D": "include 'my-lib'"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Stashing' in a Pipeline?",
        "options": {
            "A": "Deleting old files",
            "B": "Saving a set of files to be used later in the same Pipeline run, potentially on a different node",
            "C": "A security vulnerability",
            "D": "Hiding the console output"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to retrieve files previously saved via 'stash'?",
        "options": {
            "A": "get_stash",
            "B": "unstash",
            "C": "pop_stash",
            "D": "load_files"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'input' directive used for in a Pipeline?",
        "options": {
            "A": "To read a file from disk",
            "B": "To pause the Pipeline and wait for manual approval from a user",
            "C": "To type commands in the terminal",
            "D": "To define environment variables"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Checkpoint' in Jenkins (Enterprise feature)?",
        "options": {
            "A": "A security scan",
            "B": "The ability to restart a Pipeline from a specific point rather than the beginning",
            "C": "A list of developers",
            "D": "A plugin update notification"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Pipeline Multibranch'?",
        "options": {
            "A": "A pipeline with many pipes",
            "B": "A job type that automatically creates a Pipeline for every branch in a source code repository",
            "C": "A type of database join",
            "D": "A way to install multiple plugins"
        },
        "answer": "B"
    },
    {
        "question": "Which file must exist in a branch for Multibranch Pipeline to recognize it?",
        "options": {
            "A": "config.xml",
            "B": "Jenkinsfile",
            "C": "pipeline.json",
            "D": "build.gradle"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Pipeline Syntax Snippet Generator'?",
        "options": {
            "A": "A tool to delete code",
            "B": "A GUI tool in Jenkins to help users generate Groovy code for Pipeline steps",
            "C": "A search engine",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'environment' directive do in a Pipeline?",
        "options": {
            "A": "Checks the weather",
            "B": "Defines a set of helper variables available to all or specific stages",
            "C": "Lists all installed software",
            "D": "Controls the server fans"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Replay' in the context of Jenkins Pipelines?",
        "options": {
            "A": "Playing a video of the build",
            "B": "Running a build again with modified Pipeline code without changing the actual Jenkinsfile",
            "C": "A way to undo a build",
            "D": "A performance test"
        },
        "answer": "B"
    },
    {
        "question": "Which symbol is used for string interpolation in Groovy Pipelines?",
        "options": {
            "A": "' ' (Single quotes)",
            "B": "\" \" (Double quotes)",
            "C": "[ ] (Brackets)",
            "D": "< > (Angle brackets)"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'tools' directive used for in a Declarative Pipeline?",
        "options": {
            "A": "To list the office tools",
            "B": "To automatically install and configure tools like Maven, JDK, or Gradle defined in Global Tool Configuration",
            "C": "To manage user accounts",
            "D": "To fix server hardware"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Non-CPS' (@NonCPS) used for in Scripted Pipelines?",
        "options": {
            "A": "To make the build faster",
            "B": "To tell Jenkins a method shouldn't be transformed into 'Continuation Passing Style' (used for complex Groovy logic)",
            "C": "To disable security",
            "D": "To bypass the proxy"
        },
        "answer": "B"
    },
    {
        "question": "Which directive allows you to retry a block of code multiple times if it fails?",
        "options": {
            "A": "repeat",
            "B": "retry",
            "C": "loop",
            "D": "tryAgain"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'timeout' step used for in a Pipeline?",
        "options": {
            "A": "To give the developer a break",
            "B": "To set a maximum time limit for a block of code; if exceeded, the Pipeline is aborted",
            "C": "To measure the network speed",
            "D": "To schedule a build later"
        },
        "answer": "B"
    },
    {
        "question": "What is 'When' directive in Declarative Pipeline?",
        "options": {
            "A": "To ask for the current time",
            "B": "To execute a stage only if specific conditions are met (e.g., branch name matches)",
            "C": "A type of loop",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "Which 'when' condition checks the name of the current branch?",
        "options": {
            "A": "checkBranch",
            "B": "branch",
            "C": "source",
            "D": "gitBranch"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Pipeline: Basic Steps' plugin?",
        "options": {
            "A": "A tutorial for Jenkins",
            "B": "A plugin that provides standard steps like echo, sleep, and file operations for Pipelines",
            "C": "A security scanner",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Global Shared Library' vs 'Folder-level Shared Library'?",
        "options": {
            "A": "Global is for the whole server; Folder-level is restricted to a specific Jenkins folder",
            "B": "One is for Linux, one for Windows",
            "C": "There is no difference",
            "D": "Global is free, Folder-level is paid"
        },
        "answer": "A"
    },
    {
        "question": "How do you access an environment variable 'MY_VAR' in a Groovy Pipeline?",
        "options": {
            "A": "env.MY_VAR",
            "B": "MY_VAR.value",
            "C": "getEnv('MY_VAR')",
            "D": "$MY_VAR"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Jenkins Pipeline: Stage View'?",
        "options": {
            "A": "A camera view of the server",
            "B": "A visual representation showing the time taken and status of each stage in recent runs",
            "C": "A list of developers",
            "D": "The source code editor"
        },
        "answer": "B"
    },
    {
        "question": "Which step is used to archive build artifacts in a Pipeline?",
        "options": {
            "A": "saveArtifacts",
            "B": "archiveArtifacts",
            "C": "storeFiles",
            "D": "uploadResults"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'options' directive in a Declarative Pipeline used for?",
        "options": {
            "A": "To choose a UI theme",
            "B": "To configure Pipeline-wide settings like 'buildDiscarder' or 'timestamps'",
            "C": "To manage user logins",
            "D": "To select a network port"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Script' block inside a Declarative Pipeline used for?",
        "options": {
            "A": "To write a story",
            "B": "To execute Scripted Pipeline code (standard Groovy) within a Declarative Pipeline",
            "C": "To install a plugin",
            "D": "To restart the server"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Orphaned Item Strategy' in Multibranch Pipelines?",
        "options": {
            "A": "Helping developers with no team",
            "B": "Determining how long Jenkins should keep the data for branches that have been deleted from the repository",
            "C": "A backup tool",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "Which plugin allows you to run Jenkins Pipelines inside Docker containers?",
        "options": {
            "A": "Docker Pipeline Plugin",
            "B": "K8s Plugin",
            "C": "Container Plugin",
            "D": "VirtualBox Plugin"
        },
        "answer": "A"
    },
    {
        "question": "What is 'agent { docker { image 'maven:3-alpine' } }' used for?",
        "options": {
            "A": "To download an image",
            "B": "To run the Pipeline steps inside a specific Docker container",
            "C": "To build a Docker image",
            "D": "To monitor Docker usage"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'parameters' directive in a Pipeline used for?",
        "options": {
            "A": "To set the server speed",
            "B": "To define the inputs a user must provide when starting the Pipeline manually",
            "C": "A performance report",
            "D": "A type of sharding"
        },
        "answer": "B"
    },
    {
        "question": "What is 'triggers' directive in Declarative Pipeline?",
        "options": {
            "A": "Setting off an alarm",
            "B": "Defining how the Pipeline should be automatically triggered (e.g., cron or pollSCM)",
            "C": "A security scanner",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "What is 'libraries' directive in Declarative Pipeline (alternative to @Library)?",
        "options": {
            "A": "To list the office library",
            "B": "A way to dynamically load shared libraries within the pipeline block",
            "C": "To update the plugins",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Externalizing' your Jenkinsfile?",
        "options": {
            "A": "Putting it on a billboard",
            "B": "Storing the Jenkinsfile in the SCM repository rather than the Jenkins UI",
            "C": "Sending it via email",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "Which step allows you to execute shell commands in a Linux agent?",
        "options": {
            "A": "bat",
            "B": "sh",
            "C": "cmd",
            "D": "exec"
        },
        "answer": "B"
    },
    {
        "question": "Which step allows you to execute batch commands in a Windows agent?",
        "options": {
            "A": "sh",
            "B": "bat",
            "C": "ps",
            "D": "win"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Pipeline: Nodes and Processes' plugin?",
        "options": {
            "A": "A tool to monitor CPU",
            "B": "The plugin that provides the 'node' and 'sh/bat' steps for Pipelines",
            "C": "A security scanner",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'error' step used for in a Pipeline?",
        "options": {
            "A": "To fix a bug",
            "B": "To manually fail the Pipeline with a specific error message",
            "C": "To ignore a failure",
            "D": "To show the error log"
        },
        "answer": "B"
    },
    {
        "question": "What is 'junit' step used for in a Pipeline?",
        "options": {
            "A": "To install Java",
            "B": "To record and display JUnit-format test results in the Jenkins UI",
            "C": "A performance report",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Mail' step used for in a Pipeline?",
        "options": {
            "A": "To send a physical letter",
            "B": "To send email notifications based on build results",
            "C": "To check the developer's inbox",
            "D": "To manage the SMTP server"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Properties' step in Scripted Pipeline?",
        "options": {
            "A": "To buy a house",
            "B": "To define job-level properties (like parameters or triggers) from within the script",
            "C": "A security scan",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'echo' step used for?",
        "options": {
            "A": "To hear a sound",
            "B": "To print a message to the Console Output",
            "C": "To repeat the build",
            "D": "A type of sharding"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 2: Which plugin provides the 'Declarative Pipeline' syntax?",
        "options": {
            "A": "Pipeline: Model Definition",
            "B": "Pipeline: Core",
            "C": "Pipeline: Groovy",
            "D": "Pipeline: UI"
        },
        "answer": "A"
    },
    {
        "question": "What are the two main facets of Access Control in Jenkins?",
        "options": {
            "A": "Encryption and Hashing",
            "B": "Security Realm (Authentication) and Authorization Strategy",
            "C": "Master and Agent",
            "D": "Plugins and Pipelines"
        },
        "answer": "B"
    },
    {
        "question": "Which 'Security Realm' is most suitable for large enterprise environments using Active Directory?",
        "options": {
            "A": "Jenkins' own user database",
            "B": "LDAP or SAML 2.0",
            "C": "Unix user/group database",
            "D": "Delegate to servlet container"
        },
        "answer": "B"
    },
    {
        "question": "Which authorization strategy allows assigning different permissions to specific users or groups via a granular table?",
        "options": {
            "A": "Anyone can do anything",
            "B": "Matrix-based security",
            "C": "Legacy mode",
            "D": "Logged-in users can do anything"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary advantage of the 'Role-Based Authorization Strategy' plugin over standard Matrix security?",
        "options": {
            "A": "It is faster to load",
            "B": "It allows defining roles (like 'Developer') and assigning them using regex patterns for job names",
            "C": "It removes the need for passwords",
            "D": "It works without a Master node"
        },
        "answer": "B"
    },
    {
        "question": "In Jenkins security, what does the 'crumb' refer to?",
        "options": {
            "A": "A small part of a plugin",
            "B": "A token generated to prevent Cross-Site Request Forgery (CSRF) attacks",
            "C": "A piece of build history",
            "D": "The password hint"
        },
        "answer": "B"
    },
    {
        "question": "What is the most secure way for a Jenkins Master to connect to a Linux Agent?",
        "options": {
            "A": "JNLP (Java Web Start)",
            "B": "SSH with Private Key",
            "C": "DCOM",
            "D": "Unencrypted HTTP"
        },
        "answer": "B"
    },
    {
        "question": "Which credential scope makes a secret available only to jobs within a specific Jenkins folder?",
        "options": {
            "A": "Global",
            "B": "System",
            "C": "Folder",
            "D": "Node"
        },
        "answer": "C"
    },
    {
        "question": "Where does Jenkins store the physical keys used to decrypt stored credentials?",
        "options": {
            "A": "In the GitHub repository",
            "B": "$JENKINS_HOME/secrets/",
            "C": "In the browser cookies",
            "D": "In the Java Virtual Machine (JVM)"
        },
        "answer": "B"
    },
    {
        "question": "Why is it a security risk to run builds on the 'Built-in Node' (Master)?",
        "options": {
            "A": "The master has limited CPU",
            "B": "A malicious build script could access the Jenkins configuration and secrets directory",
            "C": "It makes the UI slower",
            "D": "Builds cannot access the internet on the master"
        },
        "answer": "B"
    },
    {
        "question": "Which tool is recommended to automate the configuration of Jenkins security and settings (Config-as-Code)?",
        "options": {
            "A": "Jenkins JCasC (Configuration as Code) plugin",
            "B": "Jenkins Script Console",
            "C": "Manual XML editing",
            "D": "Docker Compose"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Inbound TCP Agent' connectivity (formerly JNLP)?",
        "options": {
            "A": "The Master connects to the Agent",
            "B": "The Agent initiates a connection back to the Master",
            "C": "Communication over email",
            "D": "A type of physical cable"
        },
        "answer": "B"
    },
    {
        "question": "When configuring an Inbound Agent, what is the 'Fixed' port option used for?",
        "options": {
            "A": "To repair a broken port",
            "B": "To ensure the port remains constant for consistent firewall rule management",
            "C": "To speed up the network",
            "D": "To encrypt the data"
        },
        "answer": "B"
    },
    {
        "question": "Which credential type should be used to store a GitHub Personal Access Token (PAT)?",
        "options": {
            "A": "Username and password",
            "B": "Secret text",
            "C": "SSH Username with private key",
            "D": "Certificate"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Agent-to-Controller Security Subsytem'?",
        "options": {
            "A": "A firewall between the two",
            "B": "A mechanism that restricts which files and commands an Agent can request from the Controller",
            "C": "A backup tool",
            "D": "A type of UI theme"
        },
        "answer": "B"
    },
    {
        "question": "Which plugin allows you to define 'Cloud' nodes that are spun up on-demand in Kubernetes or AWS?",
        "options": {
            "A": "Static Agent Plugin",
            "B": "Kubernetes Plugin / EC2 Plugin",
            "C": "Cloud Provider Plugin",
            "D": "Virtual Agent Plugin"
        },
        "answer": "B"
    },
    {
        "question": "What does 'Markup Formatter' control in Jenkins settings?",
        "options": {
            "A": "The code style",
            "B": "Whether Jenkins renders raw HTML in job descriptions (security risk) or uses Safe HTML/Markdown",
            "C": "The font size of logs",
            "D": "The color of the UI"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Audit Log' plugin used for?",
        "options": {
            "A": "To check the code quality",
            "B": "To record which user performed which action (e.g., who deleted a job or changed security)",
            "C": "To calculate the build time",
            "D": "To monitor CPU usage"
        },
        "answer": "B"
    },
    {
        "question": "Which CLI command is used to safe-restart Jenkins, ensuring no active builds are interrupted?",
        "options": {
            "A": "jenkins restart",
            "B": "java -jar jenkins-cli.jar safe-restart",
            "C": "init 6",
            "D": "service jenkins stop"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Secret Masking' in Jenkins build logs?",
        "options": {
            "A": "Hiding the code",
            "B": "Automatically replacing credential values with '****' in the console output",
            "C": "Encrypting the log file",
            "D": "Deleting the logs after a week"
        },
        "answer": "B"
    },
    {
        "question": "Which port type is typically used for SSH-based agents?",
        "options": {
            "A": "8080",
            "B": "22",
            "C": "443",
            "D": "50000"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Node Offline Cause' in Jenkins 2.551+?",
        "options": {
            "A": "To delete the node",
            "B": "To provide a reason (now safely HTML-escaped) for why a node was manually taken offline",
            "C": "To reboot the node",
            "D": "A performance bug"
        },
        "answer": "B"
    },
    {
        "question": "What is 'JNLP4-connect' protocol?",
        "options": {
            "A": "An old version of HTTP",
            "B": "A high-performance remoting protocol used for agent-master communication",
            "C": "A type of database join",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "How can you restrict a job to ONLY run on a node labeled 'production'?",
        "options": {
            "A": "By naming the job 'production'",
            "B": "Using the 'Restrict where this project can be run' setting with the label 'production'",
            "C": "By deleting other nodes",
            "D": "It is not possible"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Custom WorkDir path' for agents?",
        "options": {
            "A": "The developer's home",
            "B": "A specific directory on the agent machine used for remoting overhead rather than the project workspace",
            "C": "A hidden folder on the Master",
            "D": "A cloud storage path"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Slave-to-Master Access Control' (AIP-2)?",
        "options": {
            "A": "Masters controlling agents",
            "B": "A deprecated system replaced by 'Agent-to-Controller Security' to protect the Master from compromised agents",
            "C": "A type of sharding",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Which plugin is required to integrate Jenkins with Azure Active Directory (Microsoft Entra ID)?",
        "options": {
            "A": "Azure AD Plugin",
            "B": "SAML Plugin",
            "C": "Microsoft Entra Plugin",
            "D": "Both A and B"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Remoting' in the context of Jenkins?",
        "options": {
            "A": "Changing the TV channel",
            "B": "The library used for communication between the Master and Agents",
            "C": "A way to delete code",
            "D": "A mobile app for Jenkins"
        },
        "answer": "B"
    },
    {
        "question": "Which security vulnerability allows an attacker to inject scripts into the Jenkins UI?",
        "options": {
            "A": "SQL Injection",
            "B": "Cross-Site Scripting (XSS)",
            "C": "DDoS",
            "D": "Brute Force"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Matrix Authorization' permission 'Overall/Administer' equivalent to?",
        "options": {
            "A": "Read-only access",
            "B": "Full system administrator access",
            "C": "The ability to run jobs only",
            "D": "A guest account"
        },
        "answer": "B"
    },
    {
        "question": "Which setting prevents a user from seeing jobs they don't have permission to run?",
        "options": {
            "A": "Hide private jobs",
            "B": "Standard authorization (Job/Read) combined with Project-based Matrix",
            "C": "Encryption",
            "D": "Naming jobs with numbers"
        },
        "answer": "B"
    },
    {
        "question": "What is 'External Security Realm'?",
        "options": {
            "A": "Security for outside the office",
            "B": "Authenticating users against an external service like LDAP, GitHub, or Google",
            "C": "A type of firewall",
            "D": "A backup tool"
        },
        "answer": "B"
    },
    {
        "question": "How do you handle 'SSH Host Key Verification' for an agent?",
        "options": {
            "A": "By ignoring it (insecure)",
            "B": "By selecting 'manually trusted' or 'known hosts file' strategy",
            "C": "By deleting the keys",
            "D": "By using a browser"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'API Token' for a Jenkins user?",
        "options": {
            "A": "To buy plugins",
            "B": "To allow scripts/tools to authenticate as the user without using their actual password",
            "C": "To reset the password",
            "D": "To play games"
        },
        "answer": "B"
    },
    {
        "question": "What is 'System' scope in credentials management?",
        "options": {
            "A": "Available to all developers",
            "B": "Reserved for Jenkins internal system tasks (like agent connection) and hidden from job configurations",
            "C": "A type of sharding",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Which directive in a Jenkinsfile is used to safely inject a secret into a build step?",
        "options": {
            "A": "secret()",
            "B": "withCredentials()",
            "C": "getPass()",
            "D": "inject()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Crumb Issuer' configuration?",
        "options": {
            "A": "The person who gives snacks",
            "B": "The setting that enables/disables CSRF protection tokens",
            "C": "A database index",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "Which command-line argument disables the Jenkins setup wizard?",
        "options": {
            "A": "-Djenkins.install.runSetupWizard=false",
            "B": "--no-wizard",
            "C": "skip-init",
            "D": "auto-install"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Slave Jar'?",
        "options": {
            "A": "A container for old code",
            "B": "The agent.jar executable downloaded from the master to run on an agent node",
            "C": "A type of plugin",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Exclusive' usage mode on a Jenkins node?",
        "options": {
            "A": "The node is private",
            "B": "The node will only run jobs that specifically request it by label",
            "C": "The node is very fast",
            "D": "The node has no security"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Callable' role check in Jenkins hardening?",
        "options": {
            "A": "Checking the user's phone number",
            "B": "A security check that ensures code from an agent cannot execute unauthorized commands on the controller",
            "C": "A type of loop",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Which file in JENKINS_HOME contains the initial admin password?",
        "options": {
            "A": "password.txt",
            "B": "secrets/initialAdminPassword",
            "C": "config.xml",
            "D": "admin.key"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Markup Formatter' setting 'Raw HTML' discouraged?",
        "options": {
            "A": "It is too slow",
            "B": "It allows 'Stored XSS' attacks where an attacker can execute scripts in other users' browsers",
            "C": "It breaks the UI",
            "D": "It uses too much RAM"
        },
        "answer": "B"
    },
    {
        "question": "Which plugin is required to use 'GitHub' as a security realm?",
        "options": {
            "A": "Git Plugin",
            "B": "GitHub Authentication Plugin",
            "C": "SAML Plugin",
            "D": "Cloudbees Plugin"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Quiet Period' default value?",
        "options": {
            "A": "0 seconds",
            "B": "5 seconds",
            "C": "1 minute",
            "D": "5 minutes"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Node Monitored Data'?",
        "options": {
            "A": "A list of users",
            "B": "Real-time stats about an agent's disk space, swap, and clock skew used to take failing nodes offline",
            "C": "A security scan",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Which environment variable contains the URL to the Jenkins Master?",
        "options": {
            "A": "JENKINS_URL",
            "B": "MASTER_IP",
            "C": "APP_URL",
            "D": "SERVER_NAME"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Security Hardening' script?",
        "options": {
            "A": "A physical wall around the server",
            "B": "A Groovy script run in the Script Console to programmatically apply security best practices",
            "C": "A type of encryption",
            "D": "A backup tool"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Permission Inheritance' in Project-based Matrix?",
        "options": {
            "A": "Permissions are deleted every hour",
            "B": "Jobs in folders inherit the permissions set on the parent folder by default",
            "C": "Every job is independent",
            "D": "Only admins have permissions"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Global Security Configuration' page used for?",
        "options": {
            "A": "To buy insurance",
            "B": "To configure core security settings like the realm, strategy, and CSRF protection",
            "C": "To update the OS",
            "D": "To manage physical keys"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 3: What is the primary role of the 'Jenkins Security Team'?",
        "options": {
            "A": "To write code for users",
            "B": "To triage and fix security vulnerabilities in Jenkins core and plugins",
            "C": "To manage physical building security",
            "D": "To sell security software"
        },
        "answer": "B"
    },
    {
        "question": "When running Jenkins in Kubernetes, what is a 'Pod Template' used for?",
        "options": {
            "A": "To style the Jenkins website",
            "B": "To define the configuration of the temporary agent pod that Kubernetes spins up to execute a job",
            "C": "To create a backup of the Master",
            "D": "To manage user passwords"
        },
        "answer": "B"
    },
    {
        "question": "Which Jenkins feature allows for the execution of Groovy code outside of the sandbox for high-level administration?",
        "options": {
            "A": "Script Console",
            "B": "Pipeline Syntax",
            "C": "Blue Ocean",
            "D": "Freestyle Job"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of 'Pipeline: Groovy' library's CPS (Continuation Passing Style) transformation?",
        "options": {
            "A": "To make Groovy run faster",
            "B": "To allow Pipelines to be 'serializable,' meaning they can survive a Jenkins restart and continue from the same spot",
            "C": "To encrypt the code",
            "D": "To connect to SQL databases"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Jenkins Configuration as Code' (JCasC)?",
        "options": {
            "A": "Writing Jenkins in C++",
            "B": "Defining the entire Jenkins Master configuration (security, nodes, tools) in a single YAML file",
            "C": "A type of plugin for Docker",
            "D": "A database schema"
        },
        "answer": "B"
    },
    {
        "question": "Which tool is commonly used to monitor Jenkins performance metrics (JVM, queue size) in real-time?",
        "options": {
            "A": "Notepad",
            "B": "Prometheus and Grafana",
            "C": "Windows Paint",
            "D": "The browser history"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Build Executor Status' bar in Jenkins?",
        "options": {
            "A": "A list of developers online",
            "B": "A real-time visualization of which agents are busy, idle, or offline",
            "C": "A security scan report",
            "D": "A type of terminal"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary cause of the 'Jenkins is getting slow' issue related to the 'Build Queue'?",
        "options": {
            "A": "Not enough plugins installed",
            "B": "More builds are being triggered than there are available executors/agents to handle them",
            "C": "The Master node is too small",
            "D": "The UI color is set to red"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Docker-outside-of-Docker' (DooD) in Jenkins?",
        "options": {
            "A": "Running Docker on a separate PC",
            "B": "Mounting the host's Docker socket (/var/run/docker.sock) inside a Jenkins container so it can spawn sibling containers",
            "C": "A security certificate",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Docker-in-Docker' (DinD)?",
        "options": {
            "A": "Running a full Docker daemon inside another Docker container (often requiring privileged mode)",
            "B": "Moving Docker to the cloud",
            "C": "A type of backup",
            "D": "A performance bug"
        },
        "answer": "A"
    },
    {
        "question": "Which plugin is used to scale Jenkins agents on-demand in an Amazon EC2 environment?",
        "options": {
            "A": "S3 Plugin",
            "B": "Amazon EC2 Plugin",
            "C": "AWS CLI Plugin",
            "D": "CloudWatch Plugin"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Sidecar Container' in a Jenkins Kubernetes pod?",
        "options": {
            "A": "A container for trash",
            "B": "A secondary container (like a database or helper) that runs alongside the main build container in the same pod",
            "C": "A type of sharding",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Jenkins Remoting' overhead?",
        "options": {
            "A": "The speed of the mouse",
            "B": "The CPU and memory used by the communication protocol between Master and Agents",
            "C": "A database index",
            "D": "A type of plugin"
        },
        "answer": "B"
    },
    {
        "question": "Which file path in an agent workspace is often cleared to fix 'Disk Space' issues?",
        "options": {
            "A": "$WORKSPACE/.git",
            "B": "The whole workspace directory of old builds",
            "C": "The Windows folder",
            "D": "The user's desktop"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Zombie Process' in a Jenkins agent?",
        "options": {
            "A": "A process from a dead developer",
            "B": "A process that has completed but remains in the process table because the job didn't clean it up",
            "C": "A type of sharding",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "How do you 'Fingerprint' a file in Jenkins?",
        "options": {
            "A": "By touching the screen",
            "B": "By generating an MD5 checksum of an artifact to track its usage across different jobs and pipelines",
            "C": "By scanning the developer's thumb",
            "D": "By naming the file 'thumb'"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Pipeline: Input Step' used for?",
        "options": {
            "A": "To type code",
            "B": "To pause a pipeline for manual intervention, like a manager approving a production release",
            "C": "To upload a file",
            "D": "To restart the server"
        },
        "answer": "B"
    },
    {
        "question": "Which HTTP status code does the Jenkins API return if the crumb is missing in a POST request?",
        "options": {
            "A": "200",
            "B": "403 Forbidden",
            "C": "404 Not Found",
            "D": "500 Internal Error"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Jenkins Pipeline: Shared Groovy Libraries' security?",
        "options": {
            "A": "They are always insecure",
            "B": "They can be trusted (running outside the sandbox) if they are configured by an administrator",
            "C": "They only work on Windows",
            "D": "They use SSL by default"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Executor Starvation'?",
        "options": {
            "A": "The server being hungry",
            "B": "A condition where high-priority jobs cannot run because all executors are occupied by lower-priority long-running jobs",
            "C": "A security scan",
            "D": "A type of sharding"
        },
        "answer": "B"
    },
    {
        "question": "Which setting in 'Manage Jenkins' allows you to set the system-wide number of executors for the Master node?",
        "options": {
            "A": "Tool Configuration",
            "B": "Configure System -> # of executors",
            "C": "Security Settings",
            "D": "Plugin Manager"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Groovy CPS Method Mismatch' error?",
        "options": {
            "A": "A spelling error",
            "B": "An error when a non-serializable method is called from a serializable Pipeline context",
            "C": "A type of sharding",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Which plugin provides the 'lock' step to prevent multiple jobs from accessing a shared physical resource simultaneously?",
        "options": {
            "A": "Resource Disposer Plugin",
            "B": "Lockable Resources Plugin",
            "C": "Security Plugin",
            "D": "Master Plugin"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Pipeline: Milestones'?",
        "options": {
            "A": "A type of road sign",
            "B": "A way to ensure that newer builds don't overwrite the results of older builds in a specific stage",
            "C": "A performance report",
            "D": "A type of sharding"
        },
        "answer": "B"
    },
    {
        "question": "What is 'ThinBackup' plugin?",
        "options": {
            "A": "A way to lose weight",
            "B": "A tool to create lightweight backups of Jenkins configuration files (XMLs) without the heavy build history",
            "C": "A security scan",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Jenkins Health Report' icon (sun/cloud/storm)?",
        "options": {
            "A": "A weather forecast for the office",
            "B": "A visual representation of a job's reliability based on the success rate of recent builds",
            "C": "A performance report",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "What is 'AnsiColor' plugin?",
        "options": {
            "A": "A styling theme for the UI",
            "B": "A plugin that allows the Jenkins console to display colored output (ANSI escape sequences)",
            "C": "A security scanner",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "Which environment variable gives the name of the node where the build is currently running?",
        "options": {
            "A": "AGENT_NAME",
            "B": "NODE_NAME",
            "C": "COMPUTER_ID",
            "D": "HOST_IP"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Script Security' plugin?",
        "options": {
            "A": "A plugin to write scripts",
            "B": "The core plugin that manages the 'sandbox' and allows administrators to approve or reject unsafe Groovy scripts",
            "C": "A type of firewall",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Build with Parameters'?",
        "options": {
            "A": "Building with bricks",
            "B": "The action of starting a job where the user must first fill out a form (e.g., selecting a branch or target environment)",
            "C": "A security scan",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Jenkins User Database'?",
        "options": {
            "A": "A SQL database",
            "B": "The default security realm where Jenkins stores user information in local XML files",
            "C": "A list of developers on GitHub",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Reverse Proxy' setup for Jenkins?",
        "options": {
            "A": "Running Jenkins backwards",
            "B": "Placing a server like Nginx or Apache in front of Jenkins for SSL, caching, and load balancing",
            "C": "A type of sharding",
            "D": "A security vulnerability"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'JENKINS_URL' used for in notifications?",
        "options": {
            "A": "To download Jenkins",
            "B": "To ensure that links in emails and Slack messages point correctly back to the Jenkins Master",
            "C": "To update the plugins",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Master-to-Slave Access Control'?",
        "options": {
            "A": "A way to delete agents",
            "B": "A deprecated subsystem (now part of Core) that prevents agents from requesting sensitive files from the master",
            "C": "A type of sharding",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Pipeline: Basic Steps' echo vs Groovy println?",
        "options": {
            "A": "They are identical",
            "B": "echo prints to the build's Console Output; println prints to the Master's system log (usually invisible to users)",
            "C": "echo is only for Windows",
            "D": "println is faster"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Jenkins Home' directory size monitoring?",
        "options": {
            "A": "Watching the office size",
            "B": "Monitoring the disk space of $JENKINS_HOME to prevent the Master from crashing due to full logs or artifacts",
            "C": "A security scan",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Which status code represents 'Conflict' when using the Jenkins REST API (e.g., job already exists)?",
        "options": {
            "A": "400",
            "B": "409",
            "C": "500",
            "D": "404"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Slack Notification' plugin?",
        "options": {
            "A": "A plugin to talk to other developers",
            "B": "An extension that sends build success/failure messages directly to a Slack channel",
            "C": "A security scanner",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Blue Ocean' visual pipeline editor?",
        "options": {
            "A": "A tool to draw pictures",
            "B": "A graphical drag-and-drop tool to create and edit Jenkinsfiles without writing code",
            "C": "A type of sharding",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Log Rotation' in Jenkins?",
        "options": {
            "A": "Turning the logs sideways",
            "B": "Automatically deleting or compressing old build logs to save space",
            "C": "A type of unit test",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Jenkinsfile' multi-line string syntax?",
        "options": {
            "A": "Using ' ' ",
            "B": "Using triple single quotes ''' or triple double quotes \"\"\" ",
            "C": "Using [ ] ",
            "D": "Using < > "
        },
        "answer": "B"
    },
    {
        "question": "What is 'Script Approval' page?",
        "options": {
            "A": "A place to approve developers",
            "B": "A GUI where admins manually allow specific 'unsafe' Groovy methods to run in the sandbox",
            "C": "A performance report",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "What is 'SSH Agent' plugin?",
        "options": {
            "A": "A plugin to use SSH",
            "B": "A plugin that provides an SSH agent for build steps, allowing them to use SSH keys without storing them on the agent's disk",
            "C": "A security scanner",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Which of these is a way to trigger a build when a new tag is created in Git?",
        "options": {
            "A": "Poll SCM",
            "B": "Generic Webhook Trigger with a filter for tags",
            "C": "Deleting the job",
            "D": "It is not possible"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Jenkins Dashboard' customization?",
        "options": {
            "A": "Changing the office layout",
            "B": "Using the 'Dashboard View' plugin to create custom portal-like screens for job monitoring",
            "C": "A security scan",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Pipeline: Input' submitter restriction?",
        "options": {
            "A": "A way to stop inputs",
            "B": "Restricting who can click 'Approve' on an input step to a specific user or group",
            "C": "A security scan",
            "D": "A type of sharding"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Global Pipeline Libraries' refresh frequency?",
        "options": {
            "A": "Every minute",
            "B": "By default, Jenkins fetches the latest version of the library at the start of every pipeline run",
            "C": "Once a day",
            "D": "Never"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Jenkins Plugin' dependency conflict?",
        "options": {
            "A": "When two developers want the same plugin",
            "B": "When two plugins require different versions of the same core library, causing one to fail to load",
            "C": "A security scan",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Custom Tools' in Jenkins?",
        "options": {
            "A": "Tools made by the developer",
            "B": "Using the 'Custom Tools Plugin' to install specialized binaries that aren't part of standard auto-installers",
            "C": "A performance report",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Quiet Period' for SCM triggers?",
        "options": {
            "A": "Muting the developer",
            "B": "A wait period to ensure all related commits have arrived before starting a build",
            "C": "A security scan",
            "D": "A performance report"
        },
        "answer": "B"
    },
    {
        "question": "Final question: What is 'Jenkins' primary philosophy in the DevOps world?",
        "options": {
            "A": "To do everything for the user",
            "B": "Extensibility via a massive plugin ecosystem to fit any custom CI/CD workflow",
            "C": "To be the fastest server",
            "D": "To be the cheapest server"
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
    skill = "jenkins"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
