from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
  {
    "question": "Which Xcode area is used to manage files, see the project hierarchy, and select resources?",
    "options": {
      "A": "Inspector Area",
      "B": "Navigator Area",
      "C": "Debug Area",
      "D": "Editor Area"
    },
    "answer": "B"
  },
  {
    "question": "What is the keyboard shortcut to 'Build' a project in Xcode?",
    "options": {
      "A": "Cmd + R",
      "B": "Cmd + B",
      "C": "Cmd + N",
      "D": "Cmd + Shift + K"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'Scheme' in Xcode?",
    "options": {
      "A": "To choose the app's color theme",
      "B": "A configuration that defines which targets to build, what configuration to use, and which executable to launch",
      "C": "To write database queries",
      "D": "To manage app store subscriptions"
    },
    "answer": "B"
  },
  {
    "question": "Which Xcode feature allows you to see real-time previews of SwiftUI code without running the full simulator?",
    "options": {
      "A": "Interface Builder",
      "B": "Canvas (SwiftUI Previews)",
      "C": "Console",
      "D": "Instruments"
    },
    "answer": "B"
  },
  {
    "question": "What is an 'xcworkspace' file used for?",
    "options": {
      "A": "A backup of the code",
      "B": "A container used to group multiple projects and libraries, often required when using CocoaPods",
      "C": "A configuration file for the App Store",
      "D": "A type of image asset"
    },
    "answer": "B"
  },
  {
    "question": "Which Xcode tool is used to profile performance, memory leaks, and energy usage?",
    "options": {
      "A": "Simulator",
      "B": "Instruments",
      "C": "Organizer",
      "D": "Asset Catalog"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Cmd + Shift + K' do in Xcode?",
    "options": {
      "A": "Kills the app",
      "B": "Cleans the build folder",
      "C": "Creates a new class",
      "D": "Opens the Keyboard settings"
    },
    "answer": "B"
  },
  {
    "question": "In the Navigator area, which tab allows you to see and manage breakpoints?",
    "options": {
      "A": "Project Navigator",
      "B": "Breakpoint Navigator",
      "C": "Issue Navigator",
      "D": "Report Navigator"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Attributes Inspector' used for in Interface Builder?",
    "options": {
      "A": "To write Swift functions",
      "B": "To configure properties of UI elements, such as text color, alignment, and button titles",
      "C": "To manage git branches",
      "D": "To see memory usage"
    },
    "answer": "B"
  },
  {
    "question": "What is 'LLVM' in the context of Xcode?",
    "options": {
      "A": "A type of UI layout",
      "B": "The compiler infrastructure used by Xcode to translate source code into machine code",
      "C": "A library for video editing",
      "D": "The system for cloud backups"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'Asset Catalog' (.xcassets)?",
    "options": {
      "A": "To store the app's source code",
      "B": "To manage images, colors, app icons, and other media assets in a centralized location",
      "C": "To track third-party dependencies",
      "D": "To manage user data"
    },
    "answer": "B"
  },
  {
    "question": "Which Xcode debugging feature allows you to pause execution and inspect the values of variables at a specific line?",
    "options": {
      "A": "Console logging",
      "B": "Breakpoints",
      "C": "Unit Testing",
      "D": "Static Analysis"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Autocreate Schemes'?",
    "options": {
      "A": "An AI that writes code",
      "B": "An Xcode feature that automatically generates a build scheme for every target in the project",
      "C": "A way to automatically upload to the App Store",
      "D": "A type of unit test"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Organizer' window in Xcode used for?",
    "options": {
      "A": "To organize the files on your desktop",
      "B": "To manage archived builds, view crash logs, and submit apps to the App Store",
      "C": "To edit the code in multiple windows",
      "D": "To track the developer's calendar"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Edit All-in-Scope'?",
    "options": {
      "A": "Deleting all files in the project",
      "B": "A feature that allows you to rename a variable and have it updated across all occurrences in the current scope",
      "C": "A type of global search",
      "D": "A security scan"
    },
    "answer": "B"
  },
  {
    "question": "In the Xcode Editor, what does the 'Mini Map' provide?",
    "options": {
      "A": "The location of the Apple headquarters",
      "B": "A high-level visual overview of the code in the current file for quick navigation",
      "C": "A map of all the UI connections",
      "D": "The GPS coordinates of the user"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Target' in an Xcode project?",
    "options": {
      "A": "A goal for the development team",
      "B": "A product to be built, such as an app, a library, or a unit test bundle",
      "C": "The user's age group",
      "D": "A specific line of code"
    },
    "answer": "B"
  },
  {
    "question": "Which panel in Xcode is used to see the output of 'print()' statements and LLDB commands?",
    "options": {
      "A": "Navigator",
      "B": "Console (Debug Area)",
      "C": "Inspector",
      "D": "Library"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Quick Help' in Xcode?",
    "options": {
      "A": "A chat with Apple support",
      "B": "A pop-up that shows documentation for the symbol currently under the cursor",
      "C": "A tool to fix syntax errors automatically",
      "D": "A way to search the web"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Library' (Cmd + Shift + L) in Xcode used for?",
    "options": {
      "A": "To read books about Swift",
      "B": "To drag and drop UI components, code snippets, and media into your project",
      "C": "To manage third-party frameworks",
      "D": "To see the build history"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'LLDB' acronym stand for in the context of Xcode debugging?",
    "options": {
      "A": "Local Logical Data Builder",
      "B": "Low Level Debugger",
      "C": "Linked List Data Buffer",
      "D": "Live Language Debugging Base"
    },
    "answer": "B"
  },
  {
    "question": "Which LLDB command is used to print the value of a variable in the console?",
    "options": {
      "A": "print",
      "B": "po (print object)",
      "C": "show",
      "D": "val"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Build Configurations' (Debug vs. Release)?",
    "options": {
      "A": "Debug is for testing; Release is optimized for the App Store with no debug symbols",
      "B": "Debug is for Swift; Release is for Objective-C",
      "C": "Release is only for paid apps",
      "D": "Debug allows for multiple users"
    },
    "answer": "A"
  },
  {
    "question": "Where can you manage the app's 'Capabilities' like Push Notifications or iCloud in Xcode?",
    "options": {
      "A": "Info.plist",
      "B": "Signing & Capabilities tab in Project Settings",
      "C": "Build Settings",
      "D": "The Organizer"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Code Signing' in Xcode?",
    "options": {
      "A": "A way to format code automatically",
      "B": "A security process that uses digital signatures to verify that the app was created by you and hasn't been tampered with",
      "C": "Writing your name in the comments",
      "D": "Enabling dark mode for the IDE"
    },
    "answer": "B"
  },
  {
    "question": "Which tool in Xcode allows you to visualize the relationship between different Git branches and commits?",
    "options": {
      "A": "Issue Navigator",
      "B": "Source Control Navigator",
      "C": "Symbol Navigator",
      "D": "Report Navigator"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'View Debugger' used for?",
    "options": {
      "A": "To see who viewed the code",
      "B": "To inspect the 3D hierarchy of UI views to find layout overlaps or clipping issues",
      "C": "To watch training videos",
      "D": "To preview the app on an iPad"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Static Analysis' (Product > Analyze) do in Xcode?",
    "options": {
      "A": "Checks if the app is fast enough",
      "B": "Examines source code without executing it to find potential bugs like memory leaks or uninitialized variables",
      "C": "Analyzes user data",
      "D": "Generates documentation"
    },
    "answer": "B"
  },
  {
    "question": "What is an 'Exception Breakpoint'?",
    "options": {
      "A": "A breakpoint that only works on weekends",
      "B": "A special breakpoint that pauses execution the moment a crash-inducing exception is thrown",
      "C": "A way to skip errors",
      "D": "A tool to delete code"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Derived Data' folder?",
    "options": {
      "A": "A folder for user profile data",
      "B": "A location where Xcode stores intermediate build products, indexes, and logs",
      "C": "The main source code folder",
      "D": "A backup of the App Store assets"
    },
    "answer": "B"
  },
  {
    "question": "Which Xcode feature allows you to compare two versions of a file side-by-side?",
    "options": {
      "A": "Standard Editor",
      "B": "Comparison View / Version Editor",
      "C": "Debug Area",
      "D": "Assistant Editor"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Assistant Editor'?",
    "options": {
      "A": "An AI that writes code for you",
      "B": "A secondary editor pane that automatically opens related files (like a UI file and its Class)",
      "C": "A chat window for team members",
      "D": "A tool for fixing syntax errors"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Slicing' in the Asset Catalog?",
    "options": {
      "A": "Cutting an image into smaller files for speed",
      "B": "Defining how an image should stretch (like buttons or backgrounds) while keeping corners fixed",
      "C": "Deleting unused assets",
      "D": "Creating a collage"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'Build Rules' tab?",
    "options": {
      "A": "To tell the team how to behave",
      "B": "To define how specific file types (like custom scripts or shaders) should be processed during the build",
      "C": "To set the app's age rating",
      "D": "To manage the git merge rules"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Address Sanitizer' used for in Xcode schemes?",
    "options": {
      "A": "To clean up user addresses in the database",
      "B": "A runtime tool to detect memory corruption issues like buffer overflows",
      "C": "A security tool to hide the IP address",
      "D": "A way to reset the simulator"
    },
    "answer": "B"
  },
  {
    "question": "Which file extension is used for Xcode's Project configuration file?",
    "options": {
      "A": ".xcconfig",
      "B": ".xcodeproj",
      "C": ".xcconfiguraiton",
      "D": ".plist"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Main Thread Checker'?",
    "options": {
      "A": "A tool to see if the main developer is active",
      "B": "A runtime tool that identifies when UI calls are made on a background thread",
      "C": "A security scanner",
      "D": "A way to check CPU usage"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Run Script' phase in Build Phases?",
    "options": {
      "A": "A place to write the app's story",
      "B": "A custom build step that allows you to execute shell scripts during the compilation process",
      "C": "A way to start the app",
      "D": "A type of unit test"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Precedence' in Xcode's build settings?",
    "options": {
      "A": "The speed of the build",
      "B": "The hierarchy of where settings are defined (Project vs. Target vs. Config file)",
      "C": "The order of the files in the navigator",
      "D": "The priority of the app in the App Store"
    },
    "answer": "B"
  },
  {
    "question": "Which tool is used to manage localized strings and translations in Xcode?",
    "options": {
      "A": "Asset Catalog",
      "B": "String Catalogs (.xcstrings)",
      "C": "Info.plist",
      "D": "The Console"
    },
    "answer": "B"
  },
  {
    "question": "Which Xcode feature allows you to add third-party dependencies directly via a GitHub URL without using external tools like CocoaPods?",
    "options": {
      "A": "Xcode Extensions",
      "B": "Swift Package Manager (SPM)",
      "C": "Carthage Connector",
      "D": "Library Linker"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'DocC' framework in Xcode?",
    "options": {
      "A": "To compress code files",
      "B": "To build and publish interactive documentation for Swift frameworks and packages",
      "C": "To manage medical app data",
      "D": "To scan for security vulnerabilities"
    },
    "answer": "B"
  },
  {
    "question": "Which file within a Swift Package defines its targets, dependencies, and supported platforms?",
    "options": {
      "A": "Info.plist",
      "B": "Package.swift",
      "C": "README.md",
      "D": "Config.json"
    },
    "answer": "B"
  },
  {
    "question": "In the Test Navigator, what does a 'Green Checkmark' next to a test case indicate?",
    "options": {
      "A": "The test is ready to run",
      "B": "The test passed successfully",
      "C": "The test is disabled",
      "D": "The test found a bug"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Code Coverage' in Xcode's Report Navigator?",
    "options": {
      "A": "A metric showing what percentage of your source code was executed during tests",
      "B": "The total number of lines in your project",
      "C": "A security scan result",
      "D": "The percentage of comments in the code"
    },
    "answer": "A"
  },
  {
    "question": "Which tool allows you to simulate 'Slow Network' or 'High Latency' conditions while testing an app?",
    "options": {
      "A": "Interface Builder",
      "B": "Network Link Conditioner",
      "C": "Instruments",
      "D": "Asset Catalog"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Snapshot Test'?",
    "options": {
      "A": "A quick memory check",
      "B": "A test that compares the visual appearance of a UI component against a reference image",
      "C": "A backup of the database",
      "D": "A performance report"
    },
    "answer": "B"
  },
  {
    "question": "In the iOS Simulator, what does 'Shake Gesture' (Cmd + Ctrl + Z) typically trigger in a debug environment?",
    "options": {
      "A": "A screen rotation",
      "B": "The in-app developer menu or an undo action",
      "C": "A hard reset of the device",
      "D": "The App Store app"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Library' (Cmd + Shift + L) used for when working in a Storyboard?",
    "options": {
      "A": "To manage git branches",
      "B": "To drag and drop UI elements like Buttons, Labels, and View Controllers",
      "C": "To edit code snippets",
      "D": "To see build errors"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Mark' (// MARK:) used for in the Xcode code editor?",
    "options": {
      "A": "To mark a line for deletion",
      "B": "To create organized headings and separators in the Jump Bar for easier navigation",
      "C": "To highlight a syntax error",
      "D": "To encrypt a section of code"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Quick Open' (Cmd + Shift + O) used for?",
    "options": {
      "A": "To open the app on the phone",
      "B": "To quickly search for and open any file or symbol in the project by name",
      "C": "To open the terminal",
      "D": "To open the Apple website"
    },
    "answer": "B"
  },
  {
    "question": "Which feature allows you to change a variable name throughout the entire project in one step?",
    "options": {
      "A": "Global Find and Replace",
      "B": "Refactor > Rename",
      "C": "Edit All-in-Scope",
      "D": "Code Folding"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Build Path' in Xcode?",
    "options": {
      "A": "The folder where the final app binary is stored",
      "B": "The sequence of files the compiler follows",
      "C": "A security certificate",
      "D": "The user's navigation history"
    },
    "answer": "A"
  },
  {
    "question": "In the iOS Simulator, how can you simulate a 'Location' change to a specific city?",
    "options": {
      "A": "By moving your computer",
      "B": "Features > Location menu",
      "C": "By editing the Info.plist",
      "D": "By restarting Xcode"
    },
    "answer": "B"
  },
  {
    "question": "What is 'App Sandbox' in the context of the Simulator?",
    "options": {
      "A": "A game for developers",
      "B": "The isolated file system directory where an individual app's data is stored",
      "C": "A security firewall for the Mac",
      "D": "A type of unit test"
    },
    "answer": "B"
  },
  {
    "question": "Which file format is used for Xcode Documentation Catalogs?",
    "options": {
      "A": ".txt",
      "B": ".docc",
      "C": ".pdf",
      "D": ".html"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Thread Sanitizer' used for in Xcode schemes?",
    "options": {
      "A": "To speed up the processor",
      "B": "To detect data races and threading issues at runtime",
      "C": "To clean up unused threads",
      "D": "To manage user sessions"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Symbolic Breakpoint'?",
    "options": {
      "A": "A breakpoint that uses emojis",
      "B": "A breakpoint that triggers when a specific function or method is called, regardless of where it is in the code",
      "C": "A way to skip errors",
      "D": "A performance report"
    },
    "answer": "B"
  },
  {
    "question": "Which tab in the Project Settings allows you to define the 'Minimum Deployments' (iOS version support)?",
    "options": {
      "A": "General",
      "B": "Build Settings",
      "C": "Info",
      "D": "Signing"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'Jump Bar' in the Xcode editor?",
    "options": {
      "A": "A tool to skip animations",
      "B": "A navigation bar at the top of the editor that shows the path to the current file and allows jumping to symbols",
      "C": "A list of high-priority tasks",
      "D": "A button to restart the app"
    },
    "answer": "B"
  },
  {
    "question": "Which Instrument is best used to find and fix memory leaks in an iOS application?",
    "options": {
      "A": "Time Profiler",
      "B": "Leaks",
      "C": "Core Animation",
      "D": "Network"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Time Profiler' used for in the Instruments app?",
    "options": {
      "A": "To check the time in different countries",
      "B": "To analyze CPU usage and identify which functions are consuming the most execution time",
      "C": "To measure network latency",
      "D": "To schedule app updates"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Xcode Cloud' primarily designed for?",
    "options": {
      "A": "Storing personal photos",
      "B": "A continuous integration and delivery (CI/CD) service integrated into Xcode for automated building, testing, and distribution",
      "C": "Hosting a web server",
      "D": "Backup for the Mac hard drive"
    },
    "answer": "B"
  },
  {
    "question": "Which Xcode tool is used to capture and inspect a single frame of GPU work for Metal performance tuning?",
    "options": {
      "A": "Interface Builder",
      "B": "Metal Frame Debugger",
      "C": "Console",
      "D": "Asset Catalog"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Reality Composer Pro' used for in the visionOS development workflow?",
    "options": {
      "A": "Writing Swift code",
      "B": "Preparing and assembling 3D assets, materials, and particle effects for spatial computing apps",
      "C": "Managing app store reviews",
      "D": "Testing network speed"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Simulator Playgrounds'?",
    "options": {
      "A": "A place for children to play",
      "B": "A way to quickly prototype and test small snippets of code and UI without creating a full project",
      "C": "A database for user profiles",
      "D": "A security firewall"
    },
    "answer": "B"
  },
  {
    "question": "In the Xcode 'Scheme' settings, what does the 'Parallelize Build' option do?",
    "options": {
      "A": "Runs the app on two phones at once",
      "B": "Builds independent targets simultaneously to reduce overall build time",
      "C": "Encrypts the code in parallel",
      "D": "Deletes duplicate files"
    },
    "answer": "B"
  },
  {
    "question": "What is 'XCODE_SESSION_ID' used for in environment variables?",
    "options": {
      "A": "To log in to the App Store",
      "B": "To uniquely identify a specific execution session for debugging and logging purposes",
      "C": "To pay for developer subscriptions",
      "D": "To track user location"
    },
    "answer": "B"
  },
  {
    "question": "Which feature allows you to see the memory usage of each individual 'Scene' in a multi-window iPad or visionOS app?",
    "options": {
      "A": "Navigator",
      "B": "Memory Report in the Debug Navigator",
      "C": "Instruments",
      "D": "Console"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Argument Buffer' in Metal debugging?",
    "options": {
      "A": "A place for arguments between developers",
      "B": "A mechanism to pass a large number of resources to the GPU more efficiently",
      "C": "A type of unit test",
      "D": "A network buffer"
    },
    "answer": "B"
  },
  {
    "question": "What is 'App Sandbox' inheritance in macOS/iOS tools?",
    "options": {
      "A": "Getting a sandbox from a previous project",
      "B": "The principle that child processes are governed by the same security restrictions as their parent app",
      "C": "A type of code versioning",
      "D": "A performance report"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Code Coverage's' 'Partial' status (yellow bar) in the editor gutter?",
    "options": {
      "A": "The code is half-deleted",
      "B": "The line was executed, but not all conditional branches (e.g., in an 'if' statement) were tested",
      "C": "The line has a syntax error",
      "D": "The code is running in the background"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Symbolicating' a crash report?",
    "options": {
      "A": "Adding emojis to the report",
      "B": "Replacing memory addresses with human-readable function names and line numbers",
      "C": "Sending the report to Apple",
      "D": "Deleting the report to save space"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Bitcode' and why was it previously used in Xcode archives?",
    "options": {
      "A": "A type of cryptocurrency",
      "B": "An intermediate representation of the app that allowed Apple to re-optimize binaries without a new submission",
      "C": "A security token",
      "D": "A way to hide source code"
    },
    "answer": "B"
  },
  {
    "question": "Which Xcode navigator shows the status of recent builds, tests, and distribution logs?",
    "options": {
      "A": "Project Navigator",
      "B": "Report Navigator",
      "C": "Debug Navigator",
      "D": "Find Navigator"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Runtime Sanitization'?",
    "options": {
      "A": "Cleaning the computer screen",
      "B": "A set of tools (Address, Thread, Undefined Behavior) that detect bugs while the app is running",
      "C": "Deleting unused data at runtime",
      "D": "Encrypting network traffic"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Test Plan' in Xcode?",
    "options": {
      "A": "A written document for the QA team",
      "B": "A configuration file that allows you to manage and run different sets of tests with various configurations",
      "C": "A way to test the App Store price",
      "D": "A type of beta test"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Visual Diagnostics' tool in the Metal debugger?",
    "options": {
      "A": "A tool to see if the UI is pretty",
      "B": "A feature that helps identify rendering issues like pixel overdraw or incorrect depth testing",
      "C": "A way to take screenshots",
      "D": "A performance report"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Pre-warming' in the context of Xcode's Simulator?",
    "options": {
      "A": "Heating the battery of the Mac",
      "B": "A feature where the OS starts the app process in the background to reduce perceived launch time",
      "C": "Compiling code before it is written",
      "D": "A way to clear the cache"
    },
    "answer": "B"
  },
  {
    "question": "Final question: What is 'WWDC' and how is it related to Xcode?",
    "options": {
      "A": "World Wide Data Center",
      "B": "Apple’s annual Worldwide Developers Conference where new versions of Xcode and SDKs are announced",
      "C": "A type of wireless charging",
      "D": "A security protocol for Xcode"
    },
    "answer": "B"
  },
  {
    "question": "Which Xcode feature allows you to see real-time updates to your SwiftUI code without rebuilding the entire app?",
    "options": {
      "A": "Simulator",
      "B": "Canvas (Previews)",
      "C": "Interface Builder",
      "D": "Instruments"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'Scheme' in Xcode?",
    "options": {
      "A": "To define the app's color palette",
      "B": "To define a collection of targets to build, a configuration to use, and an executable to launch",
      "C": "To manage the app's folder structure in Finder",
      "D": "To encrypt the app's source code"
    },
    "answer": "B"
  },
  {
    "question": "In the 'Build Phases' tab, what does 'Link Binary With Libraries' do?",
    "options": {
      "A": "It downloads third-party code from the internet",
      "B": "It specifies which frameworks and libraries should be linked to the executable during the build",
      "C": "It renames variables to make them shorter",
      "D": "It compresses the images in the Asset Catalog"
    },
    "answer": "B"
  },
  {
    "question": "Which LLDB command is used to change the value of a variable during a breakpoint session?",
    "options": {
      "A": "set",
      "B": "expression (or 'e')",
      "C": "change",
      "D": "modify"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Command + Shift + K' do in Xcode?",
    "options": {
      "A": "Deletes the current line of code",
      "B": "Cleans the build folder (removes derived data for the project)",
      "C": "Kills the running simulator",
      "D": "Keeps the current file open in a new window"
    },
    "answer": "B"
  },
  {
    "question": "Where can you find the 'Privacy - Camera Usage Description' key to allow an app to access the camera?",
    "options": {
      "A": "AppDelegate.swift",
      "B": "Info.plist (or the Info tab of the Target)",
      "C": "Build Settings",
      "D": "Assets.xcassets"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Debug Memory Graph' used for in Xcode?",
    "options": {
      "A": "To see how much disk space the app occupies",
      "B": "To visualize object relationships and identify strong reference cycles (memory leaks)",
      "C": "To draw charts of the app's user growth",
      "D": "To monitor the GPU temperature"
    },
    "answer": "B"
  },
  {
    "question": "Which area in Xcode is used to manage Swift Packages (SPM) dependencies?",
    "options": {
      "A": "Source Control menu",
      "B": "Project Settings -> Package Dependencies",
      "C": "The Console",
      "D": "The Library popover"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Size Classes' in Xcode's Interface Builder?",
    "options": {
      "A": "To categorize the file size of different images",
      "B": "To create different layouts for different screen dimensions (e.g., iPhone vs. iPad)",
      "C": "To group Swift classes by their line count",
      "D": "To limit the number of views in a hierarchy"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'Quick Help' inspector (Option + Click) provide?",
    "options": {
      "A": "Technical support chat with Apple",
      "B": "Documentation, declaration details, and descriptions for symbols and methods",
      "C": "A way to automatically fix all compiler errors",
      "D": "A tutorial on how to use the Mac"
    },
    "answer": "B"
  },
  {
    "question": "Which keyboard shortcut is used to 'Build' the project without running it?",
    "options": {
      "A": "Cmd + R",
      "B": "Cmd + B",
      "C": "Cmd + .",
      "D": "Cmd + U"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'Symbolic Breakpoint' in Xcode?",
    "options": {
      "A": "To stop execution when a specific variable changes",
      "B": "To stop execution when a specific method or function is called, even without the source code",
      "C": "To highlight syntax errors in symbols",
      "D": "To rename all symbols in a project"
    },
    "answer": "B"
  },
  {
    "question": "Which tab in the Project Settings is used to add 'Capabilities' like Push Notifications or iCloud?",
    "options": {
      "A": "General",
      "B": "Signing & Capabilities",
      "C": "Build Settings",
      "D": "Info"
    },
    "answer": "B"
  },
  {
    "question": "In Xcode's Source Control, what does 'Stash Changes' do?",
    "options": {
      "A": "Deletes all local changes permanently",
      "B": "Temporarily saves uncommitted changes to a dirty working directory to be applied later",
      "C": "Uploads code directly to the App Store",
      "D": "Merges two branches together"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Filter' bar at the bottom of the Project Navigator used for?",
    "options": {
      "A": "To change the background color of Xcode",
      "B": "To quickly search for specific files by name within the project",
      "C": "To filter out build errors",
      "D": "To sort files by size"
    },
    "answer": "B"
  },
  {
    "question": "Which tool allows you to simulate different network conditions (like 3G or High Latency) on a device?",
    "options": {
      "A": "Time Profiler",
      "B": "Network Link Conditioner",
      "C": "Core Data Lab",
      "D": "Instruments Allocations"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'm' icon next to a filename in the Project Navigator signify?",
    "options": {
      "A": "The file is a Main file",
      "B": "The file has been Modified since the last git commit",
      "C": "The file is Missing",
      "D": "The file is part of a Module"
    },
    "answer": "B"
  },
  {
    "question": "Which command in LLDB allows you to see the entire call stack of the current thread?",
    "options": {
      "A": "thread list",
      "B": "bt (backtrace)",
      "C": "frame info",
      "D": "step over"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Library' (Shift + Cmd + L) used for in Xcode?",
    "options": {
      "A": "To browse Apple's online documentation",
      "B": "To access UI elements, code snippets, and media assets to drag into code or storyboards",
      "C": "To manage framework dependencies",
      "D": "To view previous versions of the app"
    },
    "answer": "B"
  },
  {
    "question": "Which Build Setting allows you to specify the minimum iOS version the app supports?",
    "options": {
      "A": "Base SDK",
      "B": "iOS Deployment Target",
      "C": "Swift Language Version",
      "D": "Architectures"
    },
    "answer": "B"
  },
  {
    "question": "In the Issue Navigator, what does a red icon indicate?",
    "options": {
      "A": "A suggested improvement",
      "B": "A build error that prevents the app from compiling",
      "C": "A warning about deprecated code",
      "D": "An active breakpoint"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Preview Device' in SwiftUI Previews?",
    "options": {
      "A": "To buy a new iPhone from the Apple Store",
      "B": "To see how the UI looks on different Apple devices without launching the full simulator",
      "C": "To record a demo video of the app",
      "D": "To test the app's battery consumption"
    },
    "answer": "B"
  },
  {
    "question": "Which file handles the launch screen of an application in a traditional UIKit project?",
    "options": {
      "A": "Info.plist",
      "B": "LaunchScreen.storyboard",
      "C": "AppDelegate.swift",
      "D": "Main.storyboard"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Cmd + /' do in the Xcode Editor?",
    "options": {
      "A": "Deletes the current line",
      "B": "Comments or uncomments the selected lines of code",
      "C": "Indents the code",
      "D": "Opens the help menu"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Code Coverage' used for in Xcode Testing?",
    "options": {
      "A": "To measure the percentage of source code executed during tests",
      "B": "To ensure the code is encrypted",
      "C": "To check for plagiarism",
      "D": "To automatically write unit tests"
    },
    "answer": "A"
  },
  {
    "question": "Which Xcode area is used to configure 'Build Rules'?",
    "options": {
      "A": "Interface Builder",
      "B": "Project Settings -> Build Rules",
      "C": "Organizer",
      "D": "Debug Console"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Bitcode' in Xcode's build settings?",
    "options": {
      "A": "A currency used in the App Store",
      "B": "An intermediate representation of a compiled program that allows Apple to re-optimize the app binary",
      "C": "A security feature that hides the code",
      "D": "A way to compress image assets"
    },
    "answer": "B"
  },
  {
    "question": "How do you create a 'Segue' between two View Controllers in a Storyboard?",
    "options": {
      "A": "Double click the first controller",
      "B": "Control-drag from a button or controller to another controller",
      "C": "Right click the project file",
      "D": "Use the 'Link' command in the File menu"
    },
    "answer": "B"
  },
  {
    "question": "What is the function of the 'Global Search' (Shift + Cmd + F) in Xcode?",
    "options": {
      "A": "To search for code on Stack Overflow",
      "B": "To search for a text string across the entire project or workspace",
      "C": "To search for files in the macOS Finder",
      "D": "To find all apps in the App Store"
    },
    "answer": "B"
  },
  {
    "question": "In Instruments, which template helps track GPU utilization and frame rates?",
    "options": {
      "A": "Leaks",
      "B": "Core Animation",
      "C": "Allocations",
      "D": "File Activity"
    },
    "answer": "B"
  },
  {
    "question": "Which framework is used to create unit and UI tests in Xcode?",
    "options": {
      "A": "SwiftUI",
      "B": "XCTest",
      "C": "CoreData",
      "D": "Foundation"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'XCUIAutomation' in Xcode?",
    "options": {
      "A": "To automatically write code comments",
      "B": "To simulate user interactions like taps and swipes for UI testing",
      "C": "To automatically upload the app to the App Store",
      "D": "To format Swift code automatically"
    },
    "answer": "B"
  },
  {
    "question": "Which file defines the dependencies and products of a Swift Package?",
    "options": {
      "A": "Info.plist",
      "B": "Package.swift",
      "C": "Config.json",
      "D": "Dependencies.swift"
    },
    "answer": "B"
  },
  {
    "question": "How do you enable 'Zombie Objects' to debug memory crashes?",
    "options": {
      "A": "In the Instruments Leaks tool",
      "B": "In the Scheme Editor under 'Diagnostics'",
      "C": "In the Project Navigator settings",
      "D": "In the Attributes Inspector"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'Conflict' icon (gray diamond) represent in Xcode Source Control?",
    "options": {
      "A": "A successful merge",
      "B": "Changes in the same line of code from two different branches that cannot be merged automatically",
      "C": "A deleted file",
      "D": "An unpushed commit"
    },
    "answer": "B"
  },
  {
    "question": "Which inspector allows you to change a View's accessibility label for VoiceOver?",
    "options": {
      "A": "Attributes Inspector",
      "B": "Accessibility Inspector",
      "C": "Identity Inspector",
      "D": "Size Inspector"
    },
    "answer": "B"
  },
  {
    "question": "In the 'Link Binary with Libraries' section, what is the difference between 'Required' and 'Optional'?",
    "options": {
      "A": "Required means it's free, Optional costs money",
      "B": "Required crashes the app if the library is missing at runtime; Optional allows the app to run without it",
      "C": "Optional is only for beta testing",
      "D": "Required is for Swift, Optional is for Objective-C"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Object Library' shortcut in Interface Builder?",
    "options": {
      "A": "Cmd + L",
      "B": "Shift + Cmd + L",
      "C": "Opt + Cmd + L",
      "D": "Cmd + 1"
    },
    "answer": "B"
  },
  {
    "question": "Which LLDB command prints the address of an object in memory?",
    "options": {
      "A": "print",
      "B": "p",
      "C": "addr",
      "D": "show"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Code Signing' required for in Xcode?",
    "options": {
      "A": "Running code on the simulator",
      "B": "Running code on a physical device and distributing to the App Store",
      "C": "Compiling Swift code",
      "D": "Using the 'Open Quickly' feature"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'Canvas' toggle do in the top right of the editor?",
    "options": {
      "A": "Shows the console",
      "B": "Shows or hides the SwiftUI Preview area",
      "C": "Opens the Git history",
      "D": "Activates the 3D View Debugger"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Workspace' in Xcode?",
    "options": {
      "A": "A physical desk layout for developers",
      "B": "A container that allows you to group multiple projects and libraries to work on them together",
      "C": "A paid version of Xcode",
      "D": "A folder for temporary files"
    },
    "answer": "B"
  },
  {
    "question": "Which keyboard shortcut jumps to the definition of a symbol?",
    "options": {
      "A": "Cmd + Click (or Cmd + Ctrl + J)",
      "B": "Shift + Cmd + D",
      "C": "Cmd + R",
      "D": "Opt + Cmd + Up"
    },
    "answer": "A"
  },
  {
    "question": "In Interface Builder, what is the 'Safe Area'?",
    "options": {
      "A": "A password-protected folder",
      "B": "The portion of the view not covered by navigation bars, tab bars, or toolbars",
      "C": "A mode where you cannot delete views",
      "D": "The sandbox directory of the app"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'Step Over' button do during debugging?",
    "options": {
      "A": "Skips the current breakpoint entirely",
      "B": "Executes the current line and pauses at the next line in the same function",
      "C": "Enters into the function call on the current line",
      "D": "Exits the current function"
    },
    "answer": "B"
  },
  {
    "question": "Which file type is used for localized strings in Xcode?",
    "options": {
      "A": ".json",
      "B": ".strings",
      "C": ".txt",
      "D": ".local"
    },
    "answer": "B"
  },
  {
    "question": "How do you add a 'Build Phase' script (Shell Script)?",
    "options": {
      "A": "Right-click any Swift file",
      "B": "Target Settings -> Build Phases -> '+' button -> New Run Script Phase",
      "C": "In the AppDelegate",
      "D": "Using the terminal only"
    },
    "answer": "B"
  },
  {
    "question": "What is 'App Thinning' in the context of Xcode distribution?",
    "options": {
      "A": "Removing unused code to make the app faster",
      "B": "Optimizing the app installation by delivering only the resources needed for a specific device",
      "C": "Deleting the app from the simulator",
      "D": "Compressing the source code files"
    },
    "answer": "B"
  },
  {
    "question": "Which tool is used to view the system logs of a connected device?",
    "options": {
      "A": "Project Navigator",
      "B": "Devices and Simulators window (Cmd + Shift + 2)",
      "C": "Interface Builder",
      "D": "Attributes Inspector"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Identity Inspector' used for in Storyboards?",
    "options": {
      "A": "To change the background color",
      "B": "To set the custom class for a View or View Controller",
      "C": "To manage git branches",
      "D": "To set the app icon"
    },
    "answer": "B"
  },
  {
    "question": "Which command-line tool is used to build Xcode projects from the Terminal?",
    "options": {
      "A": "swift build",
      "B": "xcodebuild",
      "6": "make",
      "D": "gcc"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Preview Providers' in SwiftUI?",
    "options": {
      "A": "To provide data to a database",
      "B": "To define the data and environment for the Xcode Canvas to render a preview",
      "C": "To handle App Store subscriptions",
      "D": "To provide icons for the app"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'Stack View' do in Auto Layout?",
    "options": {
      "A": "Displays a list of all variables",
      "B": "Automatically manages the layout of a collection of views in a row or column",
      "C": "Crashes the app when there is too much data",
      "D": "Organizes the file structure in the navigator"
    },
    "answer": "B"
  },
  {
    "question": "How do you open the 'Quick Open' search bar?",
    "options": {
      "A": "Cmd + F",
      "B": "Cmd + Shift + O",
      "C": "Cmd + Shift + F",
      "D": "Cmd + P"
    },
    "answer": "B"
  },
  {
    "question": "In XCTest, which method is called before every single test case runs?",
    "options": {
      "A": "tearDown()",
      "B": "setUpWithError()",
      "C": "testStart()",
      "D": "main()"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'Debug Bar' located above the debug area?",
    "options": {
      "A": "To change the font size of the code",
      "B": "To control the execution of the app (pause, step over, step into, continue)",
      "C": "To search for text in the console",
      "D": "To manage the Git repository"
    },
    "answer": "B"
  },
  {
    "question": "Which inspector allows you to set the 'Restoration ID' for a view?",
    "options": {
      "A": "Attributes Inspector",
      "B": "Identity Inspector",
      "C": "Size Inspector",
      "D": "File Inspector"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Live Previews' in SwiftUI?",
    "options": {
      "A": "A live stream of the developer's screen",
      "B": "An interactive preview where you can run the app logic directly in the Canvas",
      "C": "A feature for broadcasting the app to YouTube",
      "D": "A tool for real-time multiplayer gaming"
    },
    "answer": "B"
  },
  {
    "question": "Which keyboard shortcut hides/shows the Utilities area (Right panel)?",
    "options": {
      "A": "Cmd + 0",
      "B": "Opt + Cmd + 0",
      "C": "Cmd + Opt + Ctrl + 0",
      "D": "Shift + Cmd + 0"
    },
    "answer": "B"
  },
  {
    "question": "What is an 'Exception Breakpoint'?",
    "options": {
      "A": "A breakpoint that only triggers on Mondays",
      "B": "A breakpoint that pauses execution the moment an error or exception is thrown",
      "C": "A breakpoint for code that works perfectly",
      "D": "A way to skip errors"
    },
    "answer": "B"
  },
  {
    "question": "What is 'SwiftLint' commonly used for in Xcode projects?",
    "options": {
      "A": "To translate Swift to Objective-C",
      "B": "To enforce Swift style and conventions through build warnings and errors",
      "C": "To speed up the compilation time",
      "D": "To manage asset sizes"
    },
    "answer": "B"
  },
  {
    "question": "Which Xcode feature shows the CPU and Memory usage in a small gauge while the app is running?",
    "options": {
      "A": "Navigator Area",
      "B": "Debug Navigator (Cmd + 7)",
      "C": "Report Navigator",
      "D": "Inspector Area"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Command + J' do in the editor?",
    "options": {
      "A": "Jumps to a specific line number",
      "B": "Allows you to move the focus between different editor panes",
      "C": "Joins two files together",
      "D": "Opens the JSON editor"
    },
    "answer": "B"
  },
  {
    "question": "In the File Inspector, what does 'Target Membership' define?",
    "options": {
      "A": "The author of the file",
      "B": "Which targets (apps, tests, or libraries) the selected file belongs to",
      "C": "The date the file was created",
      "D": "The folder location in Finder"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'XIB' file?",
    "options": {
      "A": "A type of image format",
      "B": "An XML-based file format representing a single visual view or screen",
      "C": "A compiled binary file",
      "D": "A script for server communication"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Command + Opt + [' do?",
    "options": {
      "A": "Deletes a line",
      "B": "Moves the current line or selection up",
      "C": "Closes the current tab",
      "D": "Minimizes Xcode"
    },
    "answer": "B"
  },
  {
    "question": "Which tool in Xcode allows you to see the current 'Memory Footprint' of your app?",
    "options": {
      "A": "Project Navigator",
      "B": "Debug Navigator -> Memory",
      "C": "File Inspector",
      "D": "Library"
    },
    "answer": "B"
  },
  {
    "question": "What is 'CocoaPods'?",
    "options": {
      "A": "A fruit found at Apple Headquarters",
      "B": "A third-party dependency manager for Swift and Objective-C projects",
      "C": "A type of UI element in SwiftUI",
      "D": "The internal name for the Apple Watch"
    },
    "answer": "B"
  },
  {
    "question": "How do you change the 'Display Name' of an app?",
    "options": {
      "A": "Rename the Project file",
      "B": "Modify the 'Display Name' field in the Target's General tab",
      "C": "Change the name of AppDelegate",
      "D": "You cannot change it once created"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Size Inspector' (Opt + Cmd + 6) used for?",
    "options": {
      "A": "To change the font size",
      "B": "To adjust the dimensions, positions, and Auto Layout constraints of a view",
      "C": "To check the disk size of the project",
      "D": "To resize the Xcode window"
    },
    "answer": "B"
  },
  {
    "question": "In LLDB, what is the shortcut for 'continue' execution?",
    "options": {
      "A": "c",
      "B": "cont",
      "C": "resume",
      "D": "go"
    },
    "answer": "A"
  },
  {
    "question": "What does the 'Assistant' icon (overlapping circles) do?",
    "options": {
      "A": "Opens Siri",
      "B": "Opens the Assistant Editor to show code related to the current UI file",
      "C": "Calls Apple Support",
      "D": "Checks for software updates"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Minimap' in the Xcode editor?",
    "options": {
      "A": "A GPS for finding the office",
      "B": "A visual overview of the code in the current file for quick navigation",
      "C": "A list of all files in the project",
      "D": "A way to see the app's folder structure"
    },
    "answer": "B"
  },
  {
    "question": "Which property in the Info.plist allows the app to run in the background for music playback?",
    "options": {
      "A": "Background Music",
      "B": "UIBackgroundModes",
      "C": "KeepAlive",
      "D": "AudioPlay"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Source Control Management' (SCM) in Xcode?",
    "options": {
      "A": "Managing the power source of the Mac",
      "B": "Built-in support for version control systems like Git",
      "C": "Controlling the brightness of the screen",
      "D": "The license manager for Xcode"
    },
    "answer": "B"
  },
  {
    "question": "Which button in the bottom left of Interface Builder allows you to see the layout on different devices?",
    "options": {
      "A": "Preview Assistant",
      "B": "View as: [Device Name]",
      "C": "Device Selector",
      "D": "Orientation Lock"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Main Thread Checker' in Xcode?",
    "options": {
      "A": "A tool that ensures UI updates only happen on the main thread",
      "B": "A tool that checks the internet connection",
      "C": "A way to count the number of threads in the app",
      "D": "A debugger for background tasks"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Localization' in Xcode?",
    "options": {
      "A": "Finding the user's GPS coordinates",
      "B": "The process of adapting an app to different languages and regions",
      "C": "Using a local server for testing",
      "D": "Storing data locally on the phone"
    },
    "answer": "B"
  },
  {
    "question": "Which inspector allows you to view the 'Connection' (IBOutlets/IBActions) for a view?",
    "options": {
      "A": "Attributes Inspector",
      "B": "Connections Inspector (Opt + Cmd + 8)",
      "C": "Identity Inspector",
      "D": "File Inspector"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Jump Bar'?",
    "options": {
      "A": "A bar that allows you to jump to different levels of the file hierarchy and symbols",
      "B": "A physical bar on the MacBook keyboard",
      "C": "The progress bar during a build",
      "D": "A tool for jumping between breakpoints"
    },
    "answer": "A"
  },
  {
    "question": "What is the purpose of a 'Slicing' in the Xcode Asset Catalog?",
    "options": {
      "A": "To cut an image into separate files",
      "B": "To define how an image should stretch while preserving specific corners or edges",
      "C": "To reduce the file size of a video",
      "D": "To remove unused code from the binary"
    },
    "answer": "B"
  },
  {
    "question": "In Xcode Cloud, what is a 'Workflow'?",
    "options": {
      "A": "A list of developer daily tasks",
      "B": "A set of automated steps to build, test, and distribute your app upon code changes",
      "C": "A visual representation of the app's navigation",
      "D": "A tool for tracking employee work hours"
    },
    "answer": "B"
  },
  {
    "question": "Which file extension is used for the Core Data model editor in Xcode?",
    "options": {
      "A": ".sqlite",
      "B": ".xcdatamodeld",
      "C": ".json",
      "D": ".coredata"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'Preserve Vector Data' checkbox in the Asset Catalog do?",
    "options": {
      "A": "It converts PNGs into PDFs",
      "B": "It allows PDF/SVG assets to be scaled infinitely at runtime without losing quality",
      "C": "It prevents images from being deleted",
      "D": "It encrypts the image data"
    },
    "answer": "B"
  },
  {
    "question": "Which Xcode window is used to view crash logs sent from users via App Store Connect?",
    "options": {
      "A": "Console",
      "B": "Organizer (Crashes tab)",
      "C": "Issue Navigator",
      "D": "Devices and Simulators"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'Prepare for Display' method in Xcode's cell lifecycle?",
    "options": {
      "A": "To download data from the web",
      "B": "To reset or pre-populate a table view cell before it appears on screen",
      "C": "To delete the cell from memory",
      "D": "To change the app icon"
    },
    "answer": "B"
  },
  {
    "question": "In the Scheme settings, what does the 'Parallelize Build' option do?",
    "options": {
      "A": "Builds the app for two different countries at once",
      "B": "Builds independent targets simultaneously to reduce total build time",
      "C": "Runs the app on two simulators at once",
      "D": "Doubles the internet speed of the Mac"
    },
    "answer": "B"
  },
  {
    "question": "What is the keyboard shortcut to 'Step Into' a function during a debug session?",
    "options": {
      "A": "F6",
      "B": "F7",
      "C": "F8",
      "D": "Cmd + I"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Development Provisioning Profile' used for?",
    "options": {
      "A": "To sell the app on the App Store",
      "B": "To allow an app to be installed and run on a physical device for testing",
      "C": "To create a developer account",
      "D": "To unlock the Pro version of Xcode"
    },
    "answer": "B"
  },
  {
    "question": "Which SwiftUI attribute is used to create a preview with a dark color scheme?",
    "options": {
      "A": ".darkMode()",
      "B": ".preferredColorScheme(.dark)",
      "C": ".colorStyle(.black)",
      "D": ".background(.dark)"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Address Sanitizer' in Xcode's Diagnostics used for?",
    "options": {
      "A": "To clean up the user's mailing address",
      "B": "To detect memory errors like use-after-free and buffer overflows",
      "C": "To verify email addresses in a form",
      "D": "To speed up database queries"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'Show the Quick Help Inspector' shortcut (Cmd + Opt + 3) do?",
    "options": {
      "A": "Opens the Apple Developer website",
      "B": "Opens the right-hand pane showing documentation for the selected code",
      "C": "Triggers a live chat with a bot",
      "D": "Shows the console logs"
    },
    "answer": "B"
  },
  {
    "question": "How do you add a new 'Capability' like 'In-App Purchase' to your target?",
    "options": {
      "A": "In the Info.plist",
      "B": "In the 'Signing & Capabilities' tab of the Target settings",
      "C": "In the Build Settings search bar",
      "D": "By emailing Apple Support"
    },
    "answer": "B"
  },
  {
    "question": "What is the function of 'IBDesignable'?",
    "options": {
      "A": "To allow custom views to be rendered in real-time within Interface Builder",
      "B": "To mark a class as ready for the App Store",
      "C": "To design app icons",
      "D": "To create a database schema"
    },
    "answer": "A"
  },
  {
    "question": "Which LLDB command prints the properties and values of a variable in a structured way?",
    "options": {
      "A": "print",
      "B": "v (or frame variable)",
      "C": "list",
      "D": "inspect"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Command + Shift + J' do in the Navigator?",
    "options": {
      "A": "Jumps to the bottom of the file",
      "B": "Reveals the current file in the Project Navigator",
      "C": "Joins two lines of code",
      "D": "Opens the JSON validator"
    },
    "answer": "B"
  },
  {
    "question": "What is 'App Sandbox' in the context of macOS development in Xcode?",
    "options": {
      "A": "A folder for testing game mechanics",
      "B": "An access control technology that limits the app's access to system resources and user data",
      "C": "A beta testing program",
      "D": "A tool for building UI with blocks"
    },
    "answer": "B"
  },
  {
    "question": "Which tool in Xcode allows you to visualize the performance of your app's energy usage?",
    "options": {
      "A": "Network Log",
      "B": "Energy Log (within Instruments)",
      "C": "Battery Monitor",
      "D": "CPU Gauge"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Module' in Swift/Xcode?",
    "options": {
      "A": "A single line of code",
      "B": "A single unit of code distribution, like a framework or an app target",
      "C": "A folder in the Project Navigator",
      "D": "A plugin for the Xcode editor"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'XCTContext.runActivity' in UI testing?",
    "options": {
      "A": "To run a background task",
      "B": "To group test steps together into a named, organized block in the test report",
      "C": "To measure the speed of the test",
      "D": "To clear the simulator data"
    },
    "answer": "B"
  },
  {
    "question": "Which checkbox in Xcode allows an app to be used on Mac (Apple Silicon) without any code changes?",
    "options": {
      "A": "Mac Catalyst",
      "B": "Destination: My Mac (Designed for iPad/iPhone)",
      "C": "Universal App",
      "D": "App Sandbox"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Command + Alt + P' do in a SwiftUI file?",
    "options": {
      "A": "Prints the file",
      "B": "Resumes the SwiftUI Preview (Canvas)",
      "C": "Plays the app in the simulator",
      "D": "Pauses the music"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Dependency Graph' in Xcode?",
    "options": {
      "A": "A chart showing user retention",
      "B": "A visualization of how different targets and libraries depend on each other",
      "C": "A list of all variables in the app",
      "D": "A tool for managing server APIs"
    },
    "answer": "B"
  },
  {
    "question": "In the Asset Catalog, what is a 'Color Set'?",
    "options": {
      "A": "A list of colors used in a paint app",
      "B": "A named color that can have different values for Light and Dark mode",
      "C": "A way to group images by color",
      "D": "A tool for editing photos"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'Optimization Level' setting in Build Settings control?",
    "options": {
      "A": "The speed of the developer's typing",
      "B": "How the compiler balances build speed vs. runtime performance of the binary",
      "C": "The resolution of the app icons",
      "D": "The number of lines of code in a file"
    },
    "answer": "B"
  },
  {
    "question": "Which Xcode feature helps you find 'Hang' risks in your UI?",
    "options": {
      "A": "Time Profiler",
      "B": "Thread Performance Checker",
      "C": "Memory Graph",
      "D": "Console"
    },
    "answer": "B"
  },
  {
    "question": "What is 'TestFlight' used for?",
    "options": {
      "A": "To check if the Mac is working correctly",
      "B": "To distribute beta versions of an app to external testers",
      "C": "To run unit tests in the cloud",
      "D": "To buy airline tickets"
    },
    "answer": "B"
  },
  {
    "question": "Which SwiftUI view property is used to specify how a view should align within a parent?",
    "options": {
      "A": "gravity",
      "B": "frame(alignment:)",
      "C": "placeAt",
      "D": "setCenter"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'Report Navigator' (Cmd + 9)?",
    "options": {
      "A": "To file a complaint with Apple",
      "B": "To view history and details of previous builds, tests, and exports",
      "C": "To see the weather report",
      "D": "To report a bug in your own code"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Swift Package Index' used for?",
    "options": {
      "A": "A dictionary of Swift words",
      "B": "A search engine to find third-party Swift libraries for your Xcode project",
      "C": "A list of all Swift versions",
      "D": "The internal documentation for Apple employees"
    },
    "answer": "B"
  },
  {
    "question": "Which area of Xcode displays the hierarchy of the currently selected file's methods and properties?",
    "options": {
      "A": "Project Navigator",
      "B": "Symbol Navigator (Cmd + 3)",
      "C": "Issue Navigator",
      "D": "Debug Navigator"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Build Folder' default location called?",
    "options": {
      "A": "Application Support",
      "B": "Derived Data",
      "C": "Library",
      "D": "Documents"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Object Inspector' shortcut in Interface Builder?",
    "options": {
      "A": "Cmd + Opt + 4",
      "B": "Cmd + Opt + 1",
      "C": "Cmd + Opt + 7",
      "D": "Shift + Cmd + J"
    },
    "answer": "B"
  },
  {
    "question": "How do you 'Archive' an app for distribution?",
    "options": {
      "A": "Cmd + Shift + A",
      "B": "Product menu -> Archive",
      "C": "File menu -> Save As Zip",
      "D": "Right click the project folder"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Test Coverage' in the Report Navigator?",
    "options": {
      "A": "The insurance for the development Mac",
      "B": "A percentage representing how much of your code was executed by your test suite",
      "C": "A list of all devices the app was tested on",
      "D": "The number of hours spent testing"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Command + Control + Left Arrow' do?",
    "options": {
      "A": "Moves the window to a different monitor",
      "B": "Goes back to the previous file in the editor history",
      "C": "Deletes the line to the left",
      "D": "Hides the project navigator"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Snapshot' in the context of XCUITest?",
    "options": {
      "A": "A quick photo of the developer",
      "B": "A capture of the UI state and hierarchy at a specific point in a test",
      "C": "A backup of the source code",
      "D": "A temporary variable"
    },
    "answer": "B"
  },
  {
    "question": "Which tab in the organizer shows you the battery usage of your app in the wild?",
    "options": {
      "A": "Crashes",
      "B": "Energy",
      "C": "Metrics",
      "D": "Archives"
    },
    "answer": "C"
  },
  {
    "question": "What is 'SwiftUI App Lifecycle'?",
    "options": {
      "A": "The time a developer spends on an app",
      "B": "The system that uses an 'App' protocol and 'WindowGroup' instead of AppDelegate",
      "C": "The cycle of updates in the App Store",
      "D": "The battery life of a SwiftUI app"
    },
    "answer": "B"
  },
  {
    "question": "How do you resolve a 'Merge Conflict' in Xcode?",
    "options": {
      "A": "By deleting the project and starting over",
      "B": "Using the 'Conflict Resolver' tool to choose between local, remote, or both changes",
      "C": "By changing the file extension",
      "D": "By calling the other developer"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Entitlements' file (.entitlements)?",
    "options": {
      "A": "A list of developer names",
      "B": "A file that specifies the security and service permissions for an app (like Push Notifications)",
      "C": "A file that lists the app's pricing",
      "D": "A legal document for Apple"
    },
    "answer": "B"
  },
  {
    "question": "Which inspector allows you to change the 'Autosizing' mask of a view?",
    "options": {
      "A": "Attributes Inspector",
      "B": "Size Inspector",
      "C": "Identity Inspector",
      "D": "Connections Inspector"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Command + Option + Shift + K' do?",
    "options": {
      "A": "Opens the keyboard settings",
      "B": "Cleans the build folder (including all derived data)",
      "C": "Restarts Xcode",
      "D": "Deletes the project"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Mini Map' shortcut?",
    "options": {
      "A": "Cmd + M",
      "B": "Cmd + Ctrl + Shift + M",
      "C": "Cmd + Opt + Ctrl + M",
      "D": "None (must be enabled in Editor menu)"
    },
    "answer": "D"
  },
  {
    "question": "What is 'Localization Catalog' (.xcloc)?",
    "options": {
      "A": "A list of map coordinates",
      "B": "A container used to send strings to translators and import them back into Xcode",
      "C": "A list of nearby Apple stores",
      "D": "A settings file for the GPS"
    },
    "answer": "B"
  },
  {
    "question": "What does 'IBInspectable' do?",
    "options": {
      "A": "It makes a property visible and editable within the Attributes Inspector in Interface Builder",
      "B": "It searches the code for bugs",
      "C": "It inspects the binary for viruses",
      "D": "It hides code from the inspector"
    },
    "answer": "A"
  },
  {
    "question": "Which tool is used to monitor real-time network traffic in Xcode?",
    "options": {
      "A": "CPU Gauge",
      "B": "Network Report in Debug Navigator",
      "C": "Time Profiler",
      "D": "Console"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Universal Binary'?",
    "options": {
      "A": "A file that works on Windows and Mac",
      "B": "A single app binary that contains code for both Intel and Apple Silicon architectures",
      "C": "A language for all computers",
      "D": "An app that is translated into every language"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'Identity Inspector's' Accessibility section?",
    "options": {
      "A": "To change the font size for people with poor vision",
      "B": "To set unique identifiers and labels for UI elements to support VoiceOver and UI Testing",
      "C": "To check if the user is logged in",
      "D": "To set the app's privacy policy"
    },
    "answer": "B"
  },
  {
    "question": "Which area of Xcode manages 'User-Defined Build Settings'?",
    "options": {
      "A": "Info.plist",
      "B": "Build Settings tab (bottom section)",
      "C": "Project Navigator",
      "D": "Organizer"
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
    skill = "Xcode"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
