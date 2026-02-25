from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
    {
        "question": "What is the primary difference between Selenium 3 and Selenium 4 architecture?",
        "options": {
            "A": "Selenium 4 requires a physical server",
            "B": "Selenium 4 replaced the JSON Wire Protocol with W3C WebDriver Protocol for direct communication with browsers",
            "C": "Selenium 4 no longer supports Chrome",
            "D": "Selenium 4 is written in a different programming language"
        },
        "answer": "B"
    },
    {
        "question": "Which component of Selenium is used to run tests on multiple machines and browsers simultaneously?",
        "options": {
            "A": "Selenium IDE",
            "B": "Selenium Grid",
            "C": "Selenium WebDriver",
            "D": "Selenium Client Library"
        },
        "answer": "B"
    },
    {
        "question": "Which Selenium locator is generally considered the most reliable and fastest for browser execution?",
        "options": {
            "A": "XPath",
            "B": "ID",
            "C": "CSS Selector",
            "D": "Link Text"
        },
        "answer": "B"
    },
    {
        "question": "What does the command 'driver.get(\"url\")' do?",
        "options": {
            "A": "Retrieves the page source",
            "B": "Navigates the browser to the specified URL and waits for the page to load",
            "C": "Downloads the website files",
            "D": "Checks if the URL is secure"
        },
        "answer": "B"
    },
    {
        "question": "How do you handle a browser-level 'Alert' in Selenium?",
        "options": {
            "A": "By clicking the 'OK' button manually",
            "B": "Using driver.switchTo().alert() and then calling accept() or dismiss()",
            "C": "By refreshing the page",
            "D": "By closing the browser window"
        },
        "answer": "B"
    },
    {
        "question": "What is the return type of the 'findElements()' method?",
        "options": {
            "A": "WebElement",
            "B": "List<WebElement>",
            "C": "String",
            "D": "Boolean"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to type text into an input field in Selenium?",
        "options": {
            "A": "typeText()",
            "B": "sendKeys()",
            "C": "inputText()",
            "D": "setValue()"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Implicit Wait' in Selenium?",
        "options": {
            "A": "To pause the script for a fixed amount of time",
            "B": "To tell the WebDriver to poll the DOM for a certain amount of time when trying to find an element",
            "C": "To wait for a specific condition like 'elementToBeClickable'",
            "D": "To speed up the execution"
        },
        "answer": "B"
    },
    {
        "question": "What is the difference between '/' and '//' in an XPath expression?",
        "options": {
            "A": "There is no difference",
            "B": " '/' is for immediate children; '//' is for any descendant (relative path)",
            "C": " '/' is for CSS; '//' is for XPath",
            "D": " '/' is for ID; '//' is for Class"
        },
        "answer": "B"
    },
    {
        "question": "Which Selenium command is used to delete all cookies in the browser session?",
        "options": {
            "A": "driver.clear()",
            "B": "driver.manage().deleteAllCookies()",
            "C": "driver.reset()",
            "D": "driver.cookies().remove()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Selenium IDE'?",
        "options": {
            "A": "The main coding engine",
            "B": "A record-and-playback tool implemented as a browser extension",
            "C": "A specialized hardware for testing",
            "D": "A database for test cases"
        },
        "answer": "B"
    },
    {
        "question": "Which interface must be implemented to create a custom listener in TestNG/Selenium?",
        "options": {
            "A": "WebDriverListener",
            "B": "ITestListener",
            "C": "SeleniumListener",
            "D": "ExecutionListener"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'Actions' class in Selenium?",
        "options": {
            "A": "To perform simple clicks",
            "B": "To handle complex user interactions like hover, drag-and-drop, and double-click",
            "C": "To write data to a file",
            "D": "To manage test priorities"
        },
        "answer": "B"
    },
    {
        "question": "How do you switch the focus to a specific 'iframe' in Selenium?",
        "options": {
            "A": "driver.jumpTo().frame()",
            "B": "driver.switchTo().frame()",
            "C": "driver.selectFrame()",
            "D": "driver.enterFrame()"
        },
        "answer": "B"
    },
    {
        "question": "What does 'driver.close()' do?",
        "options": {
            "A": "Shuts down the entire WebDriver session",
            "B": "Closes only the current window that has focus",
            "C": "Minimizes the browser",
            "D": "Deletes the browser cache"
        },
        "answer": "B"
    },
    {
        "question": "What does 'driver.quit()' do?",
        "options": {
            "A": "Closes the current window",
            "B": "Closes all browser windows and safely ends the WebDriver session",
            "C": "Logs out the user",
            "D": "Restarts the test"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to get the text present within a web element?",
        "options": {
            "A": "getValue()",
            "B": "getText()",
            "C": "getInnerHtml()",
            "D": "fetchText()"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Page Object Model' (POM)?",
        "options": {
            "A": "A tool to design the UI",
            "B": "A design pattern that creates an object repository for web elements to improve test maintenance",
            "C": "A database for web pages",
            "D": "A type of browser driver"
        },
        "answer": "B"
    },
    {
        "question": "Which locator allows you to find an element using its partial text value in a link?",
        "options": {
            "A": "By.linkText()",
            "B": "By.partialLinkText()",
            "C": "By.textMatch()",
            "D": "By.xpath()"
        },
        "answer": "B"
    },
    {
        "question": "What is the default port for Selenium Grid Hub?",
        "options": {
            "A": "8080",
            "B": "4444",
            "C": "9090",
            "D": "5555"
        },
        "answer": "B"
    },
    {
        "question": "In Selenium 4, what are 'Relative Locators'?",
        "options": {
            "A": "Locators for family-related websites",
            "B": "Locators that find elements based on their position relative to others (e.g., above, below, left of)",
            "C": "A way to use relative file paths",
            "D": "Locators for mobile apps"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to click on a radio button or checkbox?",
        "options": {
            "A": "check()",
            "B": "click()",
            "C": "select()",
            "D": "toggle()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Headless' browser execution?",
        "options": {
            "A": "Testing without a plan",
            "B": "Running browser tests without a visible graphical user interface (GUI)",
            "C": "Testing only the backend",
            "D": "A security scan of the browser"
        },
        "answer": "B"
    },
    {
        "question": "Which class is used to handle dropdowns that are built using the <select> tag?",
        "options": {
            "A": "Dropdown",
            "B": "Select",
            "C": "Options",
            "D": "List"
        },
        "answer": "B"
    },
    {
        "question": "What is 'WebDriverWait' in Selenium?",
        "options": {
            "A": "A fixed sleep command",
            "B": "An implementation of Explicit Wait used to wait for a specific condition for a specific duration",
            "C": "A tool to measure network speed",
            "D": "A database timeout"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'PageFactory' in Selenium?",
        "options": {
            "A": "A factory that builds physical servers",
            "B": "An extension to Page Object Model used to initialize web elements using @FindBy annotations",
            "C": "A tool to generate HTML reports",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to maximize the browser window?",
        "options": {
            "A": "driver.maximize()",
            "B": "driver.manage().window().maximize()",
            "C": "driver.window().fullScreen()",
            "D": "driver.setWindowSize(max)"
        },
        "answer": "B"
    },
    {
        "question": "How do you refresh the current page in Selenium using navigation?",
        "options": {
            "A": "driver.get(currentURL)",
            "B": "driver.navigate().refresh()",
            "C": "driver.reload()",
            "D": "driver.switchTo().defaultContent()"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'StaleElementReferenceException'?",
        "options": {
            "A": "The element is too old to be used",
            "B": "The element was present but is no longer attached to the DOM (e.g., page refresh)",
            "C": "The element has an invalid ID",
            "D": "The browser has crashed"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to retrieve the URL of the current page?",
        "options": {
            "A": "getUrl()",
            "B": "getCurrentUrl()",
            "C": "fetchUrl()",
            "D": "getPageSource()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'JavaScriptExecutor' used for in Selenium?",
        "options": {
            "A": "To write JavaScript code for the application",
            "B": "To execute custom JavaScript commands directly in the browser context",
            "C": "To debug Java code",
            "D": "To speed up CSS rendering"
        },
        "answer": "B"
    },
    {
        "question": "Which capability is used to bypass SSL certificate errors in Chrome?",
        "options": {
            "A": "setAcceptInsecureCerts(true)",
            "B": "ignoreSslErrors()",
            "C": "bypassSecurity()",
            "D": "trustAll()"
        },
        "answer": "A"
    },
    {
        "question": "How can you take a screenshot in Selenium?",
        "options": {
            "A": "driver.takePhoto()",
            "B": "Casting driver to (TakesScreenshot) and using getScreenshotAs()",
            "C": "Using the Robot class only",
            "D": "driver.saveImage()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Selenium WebDriver' primarily?",
        "options": {
            "A": "A standalone software",
            "B": "An API and a protocol that allows interacting with browsers",
            "C": "A browser itself",
            "D": "A test management tool"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to switch between multiple windows or tabs?",
        "options": {
            "A": "driver.nextWindow()",
            "B": "driver.switchTo().window(handle)",
            "C": "driver.changeTab()",
            "D": "driver.manage().windows()"
        },
        "answer": "B"
    },
    {
        "question": "What does 'getWindowHandles()' return?",
        "options": {
            "A": "A String",
            "B": "A Set of Strings containing unique IDs for all open windows",
            "C": "A List of WebElements",
            "D": "An integer count"
        },
        "answer": "B"
    },
    {
        "question": "What is the difference between 'submit()' and 'click()'?",
        "options": {
            "A": "There is no difference",
            "B": " 'submit()' only works for <form> elements; 'click()' works for any element",
            "C": " 'click()' is faster",
            "D": " 'submit()' clears the cookies"
        },
        "answer": "B"
    },
    {
        "question": "Which method helps to find if an element is currently visible on the page?",
        "options": {
            "A": "isEnabled()",
            "B": "isDisplayed()",
            "C": "isSelected()",
            "D": "isVisible()"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'DesiredCapabilities' class used for?",
        "options": {
            "A": "To set browser preferences like version and platform",
            "B": "To write better test cases",
            "C": "To measure the performance of the UI",
            "D": "To encrypt the test data"
        },
        "answer": "A"
    },
    {
        "question": "In Selenium 4, what is the 'Chrome DevTools Protocol' (CDP) support used for?",
        "options": {
            "A": "Writing CSS",
            "B": "Advanced features like network throttling, geolocations, and performance metrics",
            "C": "Viewing the console logs only",
            "D": "Running tests on Safari"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to move the mouse pointer to a specific element without clicking?",
        "options": {
            "A": "actions.moveToElement(element).perform()",
            "B": "driver.hover(element)",
            "C": "actions.click(element)",
            "D": "element.mouseOver()"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of 'Fluent Wait'?",
        "options": {
            "A": "To wait for a fixed 10 seconds",
            "B": "To wait for a condition with a configurable polling interval and the ability to ignore specific exceptions",
            "C": "To wait for the entire system to restart",
            "D": "To wait for the user to type"
        },
        "answer": "B"
    },
    {
        "question": "How do you find an element using its CSS class name?",
        "options": {
            "A": "By.id()",
            "B": "By.className()",
            "C": "By.cssSelector(\".classname\")",
            "D": "Both B and C are correct"
        },
        "answer": "D"
    },
    {
        "question": "Which method is used to clear the text from an input field?",
        "options": {
            "A": "delete()",
            "B": "clear()",
            "C": "reset()",
            "D": "empty()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Selenium Server' required for?",
        "options": {
            "A": "Running tests on a local machine only",
            "B": "Setting up a Selenium Grid for remote execution",
            "C": "Connecting to a database",
            "D": "Compiling Java code"
        },
        "answer": "B"
    },
    {
        "question": "What does 'driver.navigate().to(\"url\")' do compared to 'driver.get(\"url\")'?",
        "options": {
            "A": "They are exactly the same in terms of functionality",
            "B": " 'navigate().to()' maintains browser history allowing back and forward; 'get()' is for fresh navigation",
            "C": " 'get()' is only for Chrome",
            "D": " 'navigate().to()' is faster"
        },
        "answer": "B"
    },
    {
        "question": "How do you retrieve the value of a specific attribute (e.g., 'href') from a WebElement?",
        "options": {
            "A": "getText()",
            "B": "getAttribute(\"href\")",
            "C": "getValue()",
            "D": "fetchAttribute()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Session ID' in Selenium?",
        "options": {
            "A": "The user's password",
            "B": "A unique identifier for a specific browser session managed by the WebDriver",
            "C": "The IP address of the server",
            "D": "The version of Selenium being used"
        },
        "answer": "B"
    },
    {
        "question": "Which Selenium component is deprecated and no longer supported in Selenium 4?",
        "options": {
            "A": "Selenium Grid",
            "B": "Selenium RC (Remote Control)",
            "C": "Selenium IDE",
            "D": "Selenium WebDriver"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 1: What is the primary language used to write 'Gherkin' scripts for BDD testing with Selenium?",
        "options": {
            "A": "Java",
            "B": "English (or other natural languages) with Given-When-Then syntax",
            "C": "Python",
            "D": "HTML"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to move the mouse to the middle of an element using the Actions class?",
        "options": {
            "A": "hoverOver()",
            "B": "moveToElement(WebElement target)",
            "C": "scrollToElement()",
            "D": "focus()"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary difference between 'Fluent Wait' and 'WebDriverWait'?",
        "options": {
            "A": "Fluent Wait is only for Chrome",
            "B": "Fluent Wait allows you to configure the polling interval and ignore specific exceptions like NoSuchElementException",
            "C": "WebDriverWait is faster",
            "D": "There is no functional difference"
        },
        "answer": "B"
    },
    {
        "question": "How do you perform a 'Double Click' on an element in Selenium?",
        "options": {
            "A": "element.click().click()",
            "B": "actions.doubleClick(element).perform()",
            "C": "element.doubleTap()",
            "D": "driver.executeScript('doubleClick')"
        },
        "answer": "B"
    },
    {
        "question": "Which TestNG annotation is used to run a method before every test method in a class?",
        "options": {
            "A": "@BeforeClass",
            "B": "@BeforeMethod",
            "C": "@BeforeTest",
            "D": "@BeforeSuite"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'expectedConditions' class used for in an Explicit Wait?",
        "options": {
            "A": "To define the URL of the page",
            "B": "To provide predefined conditions like elementToBeClickable or visibilityOfElementLocated",
            "C": "To count the number of elements",
            "D": "To handle browser cookies"
        },
        "answer": "B"
    },
    {
        "question": "How do you drag and drop an element from one location to another?",
        "options": {
            "A": "element.dragAndDrop(target)",
            "B": "actions.dragAndDrop(source, target).perform()",
            "C": "actions.clickAndHold(source).moveToElement(target).release().build().perform()",
            "D": "Both B and C are valid approaches"
        },
        "answer": "D"
    },
    {
        "question": "What does the 'assert' keyword do in a TestNG/JUnit test?",
        "options": {
            "A": "It logs the result to a file",
            "B": "It verifies if the actual result matches the expected result and fails the test if they don't",
            "C": "It skips the current test",
            "D": "It restarts the browser"
        },
        "answer": "B"
    },
    {
        "question": "Which Selenium method is used to handle multiple windows by returning a unique ID for each?",
        "options": {
            "A": "getWindowId()",
            "B": "getWindowHandles()",
            "C": "getCurrentWindow()",
            "D": "listWindows()"
        },
        "answer": "B"
    },
    {
        "question": "How can you press the 'ENTER' key on a specific WebElement?",
        "options": {
            "A": "element.sendKeys(Keys.ENTER)",
            "B": "element.pressEnter()",
            "C": "driver.keyPress(13)",
            "D": "element.submit()"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of 'Soft Assert' in TestNG?",
        "options": {
            "A": "It is an assertion that doesn't work",
            "B": "It allows the test execution to continue even if an assertion fails, reporting all failures at the end",
            "C": "It is used for testing CSS only",
            "D": "It automatically retries the test"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to retrieve the value of a CSS property (e.g., 'color') of an element?",
        "options": {
            "A": "getStyle()",
            "B": "getCssValue(\"color\")",
            "C": "getAttribute(\"style\")",
            "D": "getColor()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Object Identification' flakiness usually caused by in dynamic web apps?",
        "options": {
            "A": "Slow internet",
            "B": "Dynamic IDs or attributes that change every time the page reloads",
            "C": "Too much RAM",
            "D": "Using the wrong browser version"
        },
        "answer": "B"
    },
    {
        "question": "Which XPath function is used to find an element whose attribute contains a specific substring?",
        "options": {
            "A": "matches()",
            "B": "contains()",
            "C": "substring()",
            "D": "hasText()"
        },
        "answer": "B"
    },
    {
        "question": "How do you navigate back to the previous page using the browser's history?",
        "options": {
            "A": "driver.goBack()",
            "B": "driver.navigate().back()",
            "C": "driver.history(-1)",
            "D": "driver.switchTo().previous()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Shadow DOM' and why is it challenging for Selenium?",
        "options": {
            "A": "It is a hidden version of the website",
            "B": "It is an encapsulated DOM tree that is not accessible through standard global document queries",
            "C": "It is a broken HTML link",
            "D": "It is a security firewall"
        },
        "answer": "B"
    },
    {
        "question": "In TestNG, how do you specify that a test method depends on the success of another method?",
        "options": {
            "A": "@Test(priority = 1)",
            "B": "@Test(dependsOnMethods = {\"methodName\"})",
            "C": "@Test(after = \"methodName\")",
            "D": "@Test(enabled = true)"
        },
        "answer": "B"
    },
    {
        "question": "Which class is used to take screenshots of a specific WebElement in Selenium 4?",
        "options": {
            "A": "TakesScreenshot",
            "B": "The WebElement interface now has a getScreenshotAs() method directly",
            "C": "ScreenshotUtil",
            "D": "Robot"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Parallel Execution' in TestNG?",
        "options": {
            "A": "Running tests one after another",
            "B": "Running multiple tests simultaneously across different threads to reduce execution time",
            "C": "Testing two different apps",
            "D": "A manual testing strategy"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'driver.switchTo().defaultContent()'?",
        "options": {
            "A": "To close the browser",
            "B": "To switch the focus back to the main page from an iframe or frame",
            "C": "To refresh the page",
            "D": "To delete cookies"
        },
        "answer": "B"
    },
    {
        "question": "Which Selenium 4 feature allows you to open a new window or tab and switch to it automatically?",
        "options": {
            "A": "driver.newTab()",
            "B": "driver.switchTo().newWindow(WindowType.TAB)",
            "C": "driver.navigate().newWindow()",
            "D": "actions.openNewWindow()"
        },
        "answer": "B"
    },
    {
        "question": "How do you find all elements that match a certain CSS selector?",
        "options": {
            "A": "driver.findElement(By.cssSelector())",
            "B": "driver.findElements(By.cssSelector())",
            "C": "driver.getAllElements()",
            "D": "driver.selectByCss()"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'PageFactory.initElements()' method used for?",
        "options": {
            "A": "To create a new browser instance",
            "B": "To initialize the WebElements defined in a Page Object class using @FindBy",
            "C": "To generate test reports",
            "D": "To close all windows"
        },
        "answer": "B"
    },
    {
        "question": "Which interface allows you to listen to events triggered by the WebDriver (like 'beforeClickOn')?",
        "options": {
            "A": "TestListener",
            "B": "WebDriverListener (Selenium 4) or WebDriverEventListener (Selenium 3)",
            "C": "ExecutionListener",
            "D": "BrowserListener"
        },
        "answer": "B"
    },
    {
        "question": "How do you handle a 'Dropdown' that does not use the standard <select> tag (e.g., a div-based menu)?",
        "options": {
            "A": "Use the Select class",
            "B": "Click the dropdown to open it and then locate and click the specific list item element",
            "C": "Use sendKeys() only",
            "D": "It cannot be automated"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Capabilities.setCapability()'?",
        "options": {
            "A": "To set the speed of the test",
            "B": "To define browser-specific configurations like version, platform, or enabling JavaScript",
            "C": "To name the test suite",
            "D": "To encrypt passwords"
        },
        "answer": "B"
    },
    {
        "question": "Which XPath axis is used to select all children of the current node?",
        "options": {
            "A": "parent::",
            "B": "child::",
            "C": "descendant::",
            "D": "following-sibling::"
        },
        "answer": "B"
    },
    {
        "question": "How do you execute a 'Scroll Down' operation using JavaScriptExecutor?",
        "options": {
            "A": "js.executeScript(\"window.scrollBy(0,250)\")",
            "B": "driver.scrollDown()",
            "C": "actions.scroll(0,250)",
            "D": "element.scrollToView()"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Thread.sleep()' and why is it generally discouraged in Selenium?",
        "options": {
            "A": "It crashes the browser",
            "B": "It is a static wait that pauses execution for a fixed time, making tests slow and brittle",
            "C": "It is only for Java",
            "D": "It uses too much CPU"
        },
        "answer": "B"
    },
    {
        "question": "Which TestNG attribute allows you to run a test multiple times?",
        "options": {
            "A": "timeOut",
            "B": "invocationCount",
            "C": "threadPoolSize",
            "D": "repeat"
        },
        "answer": "B"
    },
    {
        "question": "How do you check if an element is enabled for interaction (e.g., not grayed out)?",
        "options": {
            "A": "isDisplayed()",
            "B": "isEnabled()",
            "C": "isSelected()",
            "D": "isActive()"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'WebDriverManager' library used for?",
        "options": {
            "A": "To write test cases",
            "B": "To automatically manage (download and setup) the browser driver executables (like chromedriver.exe)",
            "C": "To manage multiple users",
            "D": "To generate HTML reports"
        },
        "answer": "B"
    },
    {
        "question": "Which method returns the HTML source code of the current page?",
        "options": {
            "A": "getHtml()",
            "B": "getPageSource()",
            "C": "getSource()",
            "D": "fetchBody()"
        },
        "answer": "B"
    },
    {
        "question": "What is an 'Absolute XPath'?",
        "options": {
            "A": "A path starting from a specific element",
            "B": "A path that starts from the root node (html) and follows the entire tree structure",
            "C": "A path that uses IDs only",
            "D": "A path for mobile apps"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Relative XPath'?",
        "options": {
            "A": "A path starting with '//' that searches for the element from anywhere in the document",
            "B": "A path for relative file locations",
            "C": "A path that only works in Chrome",
            "D": "A path that uses indexes"
        },
        "answer": "A"
    },
    {
        "question": "Which annotation is used in JUnit to mark a method as a test case?",
        "options": {
            "A": "@Before",
            "B": "@Test",
            "C": "@Ignore",
            "0": "@After"
        },
        "answer": "B"
    },
    {
        "question": "How do you find an element by its exact tag name (e.g., <a>)?",
        "options": {
            "A": "By.id(\"a\")",
            "B": "By.tagName(\"a\")",
            "C": "By.linkText(\"a\")",
            "D": "By.xpath(\"a\")"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'Dimension' class in Selenium?",
        "options": {
            "A": "To measure the time of a test",
            "B": "To set or get the size (width and height) of the browser window",
            "C": "To count the number of elements",
            "D": "To change the UI colors"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'Point' class in Selenium?",
        "options": {
            "A": "To give points to the tester",
            "B": "To set or get the (x, y) coordinates of the browser window or an element",
            "C": "To mark a bug in the code",
            "D": "To measure CPU points"
        },
        "answer": "B"
    },
    {
        "question": "Which TestNG listener is used to capture results of tests (Success, Failure, Skip)?",
        "options": {
            "A": "ISuiteListener",
            "B": "ITestListener",
            "C": "IReporter",
            "D": "IHookable"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Headless Chrome' used for in a CI/CD environment?",
        "options": {
            "A": "To display the UI on a big screen",
            "B": "To run tests in a server-side environment (like Jenkins) where no display hardware is present",
            "C": "To hide the tests from the developer",
            "D": "To speed up the internet"
        },
        "answer": "B"
    },
    {
        "question": "How do you clear the text in an input field before typing new text?",
        "options": {
            "A": "element.reset()",
            "B": "element.clear()",
            "C": "element.empty()",
            "D": "element.sendKeys(Keys.DELETE)"
        },
        "answer": "B"
    },
    {
        "question": "Which method is used to switch to a parent frame from a child frame?",
        "options": {
            "A": "driver.switchTo().parentFrame()",
            "B": "driver.switchTo().defaultContent()",
            "C": "driver.goUp()",
            "D": "driver.exitFrame()"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Implicit Wait' default value in Selenium?",
        "options": {
            "A": "10 seconds",
            "B": "0 (Zero)",
            "C": "5 seconds",
            "D": "Infinite"
        },
        "answer": "B"
    },
    {
        "question": "What is the return type of 'driver.getTitle()'?",
        "options": {
            "A": "WebElement",
            "B": "String",
            "C": "Boolean",
            "D": "Integer"
        },
        "answer": "B"
    },
    {
        "question": "Which class is used to perform keyboard-only actions like pressing the 'TAB' key?",
        "options": {
            "A": "Keyboard",
            "B": "Actions",
            "C": "Keys (enum used with sendKeys)",
            "D": "Both B and C are used"
        },
        "answer": "D"
    },
    {
        "question": "What is the purpose of '@DataProvider' in TestNG?",
        "options": {
            "A": "To provide the URL of the database",
            "B": "To enable Data-Driven Testing by passing parameters to a test method",
            "C": "To store the user credentials",
            "D": "To generate random data"
        },
        "answer": "B"
    },
    {
        "question": "How do you get the value of the 'value' attribute of an input field?",
        "options": {
            "A": "getText()",
            "B": "getAttribute(\"value\")",
            "C": "getValue()",
            "D": "fetchValue()"
        },
        "answer": "B"
    },
    {
        "question": "Which Selenium locator uses 'tag[attribute='value']' syntax?",
        "options": {
            "A": "XPath",
            "B": "CSS Selector",
            "C": "ID",
            "D": "Name"
        },
        "answer": "B"
    },
    {
        "question": "What is 'RemoteWebDriver'?",
        "options": {
            "A": "A driver for a TV remote",
            "B": "A class used to execute tests on a remote machine or a Selenium Grid Hub",
            "C": "A manual testing tool",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 2: Which command is used to get the window handle of the current window?",
        "options": {
            "A": "driver.getWindowHandles()",
            "B": "driver.getWindowHandle()",
            "C": "driver.getCurrentWindow()",
            "D": "driver.getId()"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Data-Driven Framework' in Selenium?",
        "options": {
            "A": "A framework that writes its own data",
            "B": "A framework where test data is separated from the test scripts and stored in external files like Excel, CSV, or XML",
            "C": "A framework that only tests database connections",
            "D": "A framework that uses AI to guess data"
        },
        "answer": "B"
    },
    {
        "question": "Which Apache library is commonly used to read and write data from Microsoft Excel files (.xls and .xlsx) in Selenium?",
        "options": {
            "A": "Apache POI",
            "B": "Apache Commons",
            "C": "Apache Log4j",
            "D": "Apache Maven"
        },
        "answer": "A"
    },
    {
        "question": "What is a 'Keyword-Driven Framework'?",
        "options": {
            "A": "A framework where tests are written in a spreadsheet using action keywords (e.g., click, login, type)",
            "B": "A framework that only uses Java keywords",
            "C": "A framework that searches for keywords on Google",
            "D": "A framework without any code"
        },
        "answer": "A"
    },
    {
        "question": "What is a 'Hybrid Framework' in Selenium?",
        "options": {
            "A": "A framework that runs on both Windows and Mac",
            "B": "A combination of multiple framework types, such as Data-Driven and Keyword-Driven with Page Object Model",
            "C": "A framework that uses two different programming languages",
            "D": "A framework that works for both Web and Mobile apps"
        },
        "answer": "B"
    },
    {
        "question": "Which Maven plugin is primarily used to execute TestNG or JUnit tests from the command line?",
        "options": {
            "A": "maven-compiler-plugin",
            "B": "maven-surefire-plugin",
            "C": "maven-deploy-plugin",
            "D": "maven-install-plugin"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'pom.xml' file in a Selenium Maven project?",
        "options": {
            "A": "To store the Page Objects",
            "B": "To manage project dependencies, plugins, and build configurations",
            "C": "To store user passwords",
            "D": "To act as a backup for the code"
        },
        "answer": "B"
    },
    {
        "question": "Which TestNG annotation allows you to run a single test method multiple times with different datasets provided by a method?",
        "options": {
            "A": "@Parameters",
            "B": "@DataProvider",
            "C": "@Factory",
            "D": "@Repeat"
        },
        "answer": "B"
    },
    {
        "question": "In a Page Object Model, where should the 'Assertions' ideally be located?",
        "options": {
            "A": "Inside the Page Object classes",
            "B": "Inside the Test classes (Test scripts)",
            "C": "In a separate Excel file",
            "D": "Assertions are not needed in POM"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Extent Reports' used for in a Selenium framework?",
        "options": {
            "A": "To write the test scripts",
            "B": "To generate rich, interactive, and customizable HTML reports with screenshots and logs",
            "C": "To manage the database",
            "D": "To speed up the browser"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Log4j' primarily used for in automation?",
        "options": {
            "A": "To take screenshots",
            "B": "To generate logs for debugging and tracking the execution flow of the tests",
            "C": "To store test data",
            "D": "To click on elements"
        },
        "answer": "B"
    },
    {
        "question": "Which Selenium 4 feature allows the inspection of network traffic and performance metrics via the Chrome DevTools Protocol?",
        "options": {
            "A": "NetworkInterceptor",
            "B": "DevTools interface",
            "C": "TrafficAnalyzer",
            "D": "CDPManager"
        },
        "answer": "B"
    },
    {
        "question": "What is the role of a 'Base Class' in a Selenium framework?",
        "options": {
            "A": "To store the main website URL only",
            "B": "To house common setup and teardown methods (e.g., driver initialization) inherited by all test classes",
            "C": "To store the database credentials",
            "D": "To write the test reports"
        },
        "answer": "B"
    },
    {
        "question": "How can you run Selenium tests in 'Parallel' using Maven?",
        "options": {
            "A": "By using the -p flag",
            "B": "By configuring the 'parallel' and 'threadCount' properties in the surefire-plugin configuration",
            "C": "Maven cannot run tests in parallel",
            "D": "By opening multiple command prompts"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Cross-Browser Testing'?",
        "options": {
            "A": "Testing two different apps",
            "B": "Verifying that the application functions correctly across different browsers (Chrome, Firefox, Safari, Edge)",
            "C": "Testing the browser settings",
            "D": "A type of security test"
        },
        "answer": "B"
    },
    {
        "question": "Which TestNG file is used to group tests, set parallel execution, and manage parameters at the suite level?",
        "options": {
            "A": "config.xml",
            "B": "testng.xml",
            "C": "suite.json",
            "D": "pom.xml"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Cucumber-JVM'?",
        "options": {
            "A": "A specialized version of Java",
            "B": "The Java implementation of Cucumber used to support BDD in Selenium frameworks",
            "C": "A tool to monitor system memory",
            "D": "A type of browser driver"
        },
        "answer": "B"
    },
    {
        "question": "In Cucumber, what is a 'Step Definition' file?",
        "options": {
            "A": "A file that defines the requirements",
            "B": "The code file where Gherkin steps are mapped to actual Java/Selenium code",
            "C": "A manual for the user",
            "D": "A list of bug reports"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Feature File' in Cucumber?",
        "options": {
            "A": "A file containing a list of software features",
            "B": "A file written in Gherkin that contains test scenarios and steps in natural language",
            "C": "A type of image file",
            "D": "A configuration file for the driver"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Selenium Grid 4' Distributed Mode?",
        "options": {
            "A": "A mode where the Hub and Nodes run in the same process",
            "B": "A mode where the Grid components (Router, Distributor, Sessions, etc.) run in separate processes",
            "C": "A mode for mobile testing only",
            "D": "A mode that ignores all errors"
        },
        "answer": "B"
    },
    {
        "question": "Which library is often used with Selenium to provide better assertions with more readable syntax (e.g., 'assertThat')?",
        "options": {
            "A": "TestNG",
            "B": "Hamcrest or AssertJ",
            "C": "Apache POI",
            "D": "Log4j"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Data Provider' in TestNG used for?",
        "options": {
            "A": "To provide internet connection",
            "B": "To supply data to a test method, enabling multiple executions with different data sets",
            "C": "To store the Page Object references",
            "D": "To manage the cloud server"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Parameterization' in testng.xml?",
        "options": {
            "A": "Naming the test cases",
            "B": "Passing simple data (like browser name or URL) to the test scripts via the XML file",
            "C": "A way to count parameters in a function",
            "D": "A security encryption method"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Static Keyword' used for in a Selenium framework's Driver initialization?",
        "options": {
            "A": "To make the driver constant",
            "B": "To ensure that a single instance of the WebDriver is shared across different classes (Single Threaded)",
            "C": "To hide the driver from other classes",
            "D": "To speed up execution"
        },
        "answer": "B"
    },
    {
        "question": "Which design pattern is best for handling shared data or driver instances across multiple parallel threads?",
        "options": {
            "A": "Singleton Pattern",
            "B": "ThreadLocal Class",
            "C": "Factory Pattern",
            "D": "Observer Pattern"
        },
        "answer": "B"
    },
    {
        "question": "What is 'WebDriverManager'?",
        "options": {
            "A": "A manual for WebDriver",
            "B": "An open-source library that automates the management of browser binaries (drivers)",
            "C": "A tool to track server uptime",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Runner Class' in Cucumber?",
        "options": {
            "A": "A person who runs the tests",
            "B": "A Java class used to set Cucumber options (like feature path and glue) and initiate test execution",
            "C": "A type of unit test",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Gherkin' Tags?",
        "options": {
            "A": "To identify the author",
            "B": "To group and selectively run specific scenarios (e.g., @Smoke, @Regression)",
            "C": "To style the reports",
            "D": "To define data variables"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Background' keyword in a Cucumber feature file?",
        "options": {
            "A": "Setting a background color for the app",
            "B": "Defining a set of steps that are executed before every scenario in the feature file",
            "C": "A way to hide tests",
            "D": "A type of performance test"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Scenario Outline' in Gherkin?",
        "options": {
            "A": "An outline of the project plan",
            "B": "A template scenario that runs multiple times using different data sets provided in an 'Examples' table",
            "C": "A way to skip tests",
            "D": "A summary of the bug"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Hooks' in Cucumber (@Before and @After)?",
        "options": {
            "A": "Tools to catch fish",
            "B": "Blocks of code that run before or after each scenario to handle setup and teardown (e.g., opening/closing browser)",
            "C": "A type of unit test",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to run a Maven build without executing the tests?",
        "options": {
            "A": "mvn install -skipTests",
            "B": "mvn install -DskipTests",
            "C": "mvn build no-test",
            "D": "mvn clean compile"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Continuous Integration' (CI)?",
        "options": {
            "A": "Testing without stopping",
            "B": "The practice of frequently merging code changes into a central repository and automatically running builds and tests",
            "C": "Manual testing every day",
            "D": "A type of security scan"
        },
        "answer": "B"
    },
    {
        "question": "Which tool is the industry standard for hosting a CI/CD server for Selenium projects?",
        "options": {
            "A": "GitHub",
            "B": "Jenkins",
            "C": "Jira",
            "D": "Postman"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Test Suite' in TestNG?",
        "options": {
            "A": "A luxury room for testers",
            "B": "A collection of multiple test cases or test groups meant to be executed together",
            "C": "A type of performance test",
            "D": "A bug report"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Soft Assertion' in TestNG?",
        "options": {
            "A": "An assertion that doesn't work",
            "B": "An assertion that allows the test to continue even if it fails, collecting all errors for the end",
            "C": "A manual check of the UI",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "Which method in TestNG SoftAssert class is used to report all collected assertion failures at the end of a test?",
        "options": {
            "A": "reportAll()",
            "B": "assertAll()",
            "C": "showErrors()",
            "D": "finish()"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary benefit of the Page Object Model (POM)?",
        "options": {
            "A": "It makes the test run faster",
            "B": "It improves code reusability and maintainability by keeping locators and test logic separate",
            "C": "It eliminates the need for Java",
            "D": "It replaces Selenium Grid"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Retry Analyzer' in TestNG?",
        "options": {
            "A": "A tool to retry the login",
            "B": "A mechanism to automatically re-run a failed test case to determine if it was a flaky failure",
            "C": "A security scanner",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "How do you handle 'Dynamic Locators' that change parts of their ID on every reload?",
        "options": {
            "A": "By using Absolute XPath",
            "B": "By using XPath/CSS functions like contains(), starts-with(), or ends-with()",
            "C": "By restarting the computer",
            "D": "By using the ID locator only"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'config.properties' file?",
        "options": {
            "A": "To write code",
            "B": "To store global configuration values like URL, Browser, and Timeouts as key-value pairs",
            "C": "To store bug reports",
            "D": "To monitor CPU usage"
        },
        "answer": "B"
    },
    {
        "question": "Which Java class is used to read data from a .properties file?",
        "options": {
            "A": "FileReader",
            "B": "Properties class",
            "C": "Scanner",
            "D": "BufferedReader"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Maven Central Repository'?",
        "options": {
            "A": "A place to store hardware",
            "B": "A public hosting of libraries and dependencies that Maven downloads automatically",
            "C": "A private database",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Headless Mode' and why is it useful in a Framework?",
        "options": {
            "A": "It is a hidden browser; useful for saving resources and running tests in CI environments (like Jenkins)",
            "B": "It is for testing backend only",
            "C": "It is a broken browser",
            "D": "It is faster for developers"
        },
        "answer": "A"
    },
    {
        "question": "What is 'DesiredCapabilities' primarily used for in modern frameworks?",
        "options": {
            "A": "To set browser window size",
            "B": "To define browser-specific configurations for remote execution on Selenium Grid or Cloud platforms",
            "C": "To write the test case",
            "D": "To monitor the network"
        },
        "answer": "B"
    },
    {
        "question": "What is 'SauceLabs' or 'BrowserStack'?",
        "options": {
            "A": "A type of coffee",
            "B": "Cloud-based testing platforms that provide remote Selenium Grids with thousands of browser/OS combinations",
            "C": "A tool to write code",
            "D": "A database tool"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Listener' in TestNG?",
        "options": {
            "A": "A person listening to the code",
            "B": "A TestNG feature that allows you to modify the behavior of TestNG through various interfaces (e.g., taking a screenshot on failure)",
            "C": "A microphone tool",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "Which annotation is used to initialize elements in a Page Object class when using PageFactory?",
        "options": {
            "A": "@Init",
            "B": "@FindBy",
            "C": "@Locate",
            "D": "@Element"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'mvn clean' command?",
        "options": {
            "A": "To clean the computer",
            "B": "To delete the 'target' folder and clear old build files before a new build",
            "C": "To format the code",
            "D": "To update dependencies"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Test Parallelism' at the method level?",
        "options": {
            "A": "Running two methods in one thread",
            "B": "Executing each test method in a separate thread simultaneously",
            "C": "Running tests on two different servers",
            "D": "Scaling the hardware"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 3: What is the primary reason to use an 'Interface' (like WebDriver) instead of a specific class (like ChromeDriver)?",
        "options": {
            "A": "It is faster",
            "B": "It allows the script to be browser-agnostic, supporting cross-browser testing with the same code",
            "C": "It is required by Java",
            "D": "It provides more methods"
        },
        "answer": "B"
    },
    {
        "question": "Which XPath axis is used to find an element that appears 'before' the current node in the document?",
        "options": {
            "A": "following-sibling::",
            "B": "preceding::",
            "C": "ancestor::",
            "D": "parent::"
        },
        "answer": "B"
    },
    {
        "question": "How do you handle a 'StaleElementReferenceException' in a robust way?",
        "options": {
            "A": "Increase the Thread.sleep() time",
            "B": "Implement a try-catch block to catch the exception and re-find the element before interacting again",
            "C": "Restart the browser driver",
            "D": "Ignore the error and continue"
        },
        "answer": "B"
    },
    {
        "question": "In Selenium 4, what is the 'Network Interceptor' used for?",
        "options": {
            "A": "To speed up the internet",
            "B": "To mock or modify HTTP requests and responses during test execution",
            "C": "To block all ads on the website",
            "D": "To monitor the developer's network usage"
        },
        "answer": "B"
    },
    {
        "question": "What is the CSS selector equivalent of the XPath '//div[@id='user']'?",
        "options": {
            "A": "div.user",
            "B": "div#user",
            "C": "div[user]",
            "D": "div(id=user)"
        },
        "answer": "B"
    },
    {
        "question": "Which command in Jenkins is used to trigger a Maven-based Selenium project?",
        "options": {
            "A": "mvn run tests",
            "B": "mvn clean test",
            "C": "mvn execute",
            "D": "mvn start"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Headless Firefox' execution?",
        "options": {
            "A": "Testing without a screen on Firefox browser",
            "B": "Testing without a computer",
            "C": "Testing only the backend of Firefox",
            "D": "A security scan for Firefox"
        },
        "answer": "A"
    },
    {
        "question": "How do you simulate a 'Right Click' (Context Click) using the Actions class?",
        "options": {
            "A": "actions.clickRight(element).perform()",
            "B": "actions.contextClick(element).perform()",
            "C": "actions.doubleClick(element).perform()",
            "D": "element.rightClick()"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Relative Locators' introduced in Selenium 4?",
        "options": {
            "A": "To find elements related to the family",
            "B": "To find elements based on their visual proximity to other elements (e.g., toLeftOf, toRightOf)",
            "C": "To find relative file paths",
            "D": "To find mobile app elements"
        },
        "answer": "B"
    },
    {
        "question": "Which exception is thrown when an element is present in the DOM but cannot be interacted with (e.g., hidden)?",
        "options": {
            "A": "NoSuchElementException",
            "B": "ElementNotInteractableException",
            "C": "TimeoutException",
            "D": "SessionNotFoundException"
        },
        "answer": "B"
    },
    {
        "question": "What is 'DesiredCapabilities.merge()' used for?",
        "options": {
            "A": "Merging two different test cases",
            "B": "Combining two capability objects into one",
            "C": "Merging two browser windows",
            "D": "Merging two code files"
        },
        "answer": "B"
    },
    {
        "question": "In Selenium 4, how can you emulate a specific 'Geolocation' (latitude/longitude)?",
        "options": {
            "A": "Using driver.setLocation()",
            "B": "Using the Chrome DevTools Protocol (CDP) through the DevTools interface",
            "C": "Using the Actions class",
            "D": "By changing the system clock"
        },
        "answer": "B"
    },
    {
        "question": "Which CSS selector syntax is used to select an element that has two classes (class1 and class2)?",
        "options": {
            "A": ".class1 .class2",
            "B": ".class1.class2",
            "C": ".class1 + .class2",
            "D": ".class1 > .class2"
        },
        "answer": "B"
    },
    {
        "question": "What is 'mvn install' used for in a Selenium framework?",
        "options": {
            "A": "Installing the browser",
            "B": "Compiling, testing, and packaging the project, then installing the artifact into the local Maven repository",
            "C": "Installing Java on the machine",
            "D": "Updating the computer"
        },
        "answer": "B"
    },
    {
        "question": "How do you get the 'X' and 'Y' coordinates of a WebElement?",
        "options": {
            "A": "element.getCoordinates()",
            "B": "element.getLocation()",
            "C": "element.getSize()",
            "D": "element.getPoint()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Grid 4 Hub' role in a Selenium Grid setup?",
        "options": {
            "A": "To run the browser",
            "B": "To act as a central point that receives test requests and routes them to the appropriate Node",
            "C": "To write the code",
            "D": "To store the database"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to run only a specific TestNG test class from the command line using Maven?",
        "options": {
            "A": "mvn test -Dtest=ClassName",
            "B": "mvn run ClassName",
            "C": "mvn execute -C ClassName",
            "D": "mvn test ClassName"
        },
        "answer": "A"
    },
    {
        "question": "What is 'SessionNotCreatedException'?",
        "options": {
            "A": "The browser closed too fast",
            "B": "The WebDriver failed to start a new session (often due to version mismatch between browser and driver)",
            "C": "The user password was wrong",
            "D": "The network was disconnected"
        },
        "answer": "B"
    },
    {
        "question": "How do you capture 'Console Logs' from the browser in Selenium 4?",
        "options": {
            "A": "driver.getLogs()",
            "B": "Using the LogInspector through the DevTools interface",
            "C": "Looking at the screen",
            "D": "Reading a file in the target folder"
        },
        "answer": "B"
    },
    {
        "question": "What is the CSS selector for 'every <a> element that is a direct child of a <div>'?",
        "options": {
            "A": "div a",
            "B": "div > a",
            "C": "div + a",
            "D": "div ~ a"
        },
        "answer": "B"
    },
    {
        "question": "Which Selenium class is used to interact with the 'Window' interface of the browser (resize, move)?",
        "options": {
            "A": "Window",
            "B": "WebDriver.Options.Window",
            "C": "BrowserWindow",
            "D": "ActionWindow"
        },
        "answer": "B"
    },
    {
        "question": "What is 'mvn dependency:tree' used for?",
        "options": {
            "A": "To draw a tree in the project",
            "B": "To see a visual representation of all project dependencies and resolve version conflicts",
            "C": "To list the project folders",
            "D": "To monitor CPU usage"
        },
        "answer": "B"
    },
    {
        "question": "In Selenium 4, how do you perform 'Basic Auth' using the DevTools protocol?",
        "options": {
            "A": "Using driver.get(\"user:pass@url\")",
            "B": "Using the register() method with a UsernameAndPassword supplier through DevTools",
            "C": "Using the Alert class",
            "D": "By typing into the pop-up"
        },
        "answer": "B"
    },
    {
        "question": "Which locator is best used if an element has a unique 'name' attribute?",
        "options": {
            "A": "By.id()",
            "B": "By.name()",
            "C": "By.tagName()",
            "D": "By.xpath()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'NoSuchWindowException'?",
        "options": {
            "A": "The browser didn't open",
            "B": "The window handle provided to switchTo().window() is invalid or the window was closed",
            "C": "The screen is black",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "Which TestNG attribute allows you to set a timeout for a specific test method?",
        "options": {
            "A": "timeOut",
            "B": "duration",
            "C": "limit",
            "D": "maxTime"
        },
        "answer": "A"
    },
    {
        "question": "How do you click on an element that is 'hidden' behind another element using JavaScript?",
        "options": {
            "A": "element.click()",
            "B": "js.executeScript(\"arguments[0].click();\", element)",
            "C": "actions.click(element)",
            "D": "It is impossible"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'Explicit Wait' in Selenium?",
        "options": {
            "A": "To wait for a fixed 5 seconds",
            "B": "To wait for a specific condition to occur before proceeding with the next step",
            "C": "To slow down the test",
            "D": "To restart the browser"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to take a screenshot of the 'full page' in Selenium 4 with Firefox?",
        "options": {
            "A": "getScreenshotAs()",
            "B": "getFullPageScreenshotAs()",
            "C": "captureFull()",
            "D": "snapshot()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'InsecureCertificates' capability used for?",
        "options": {
            "A": "To hack into a website",
            "B": "To allow the browser to navigate to websites with expired or invalid SSL certificates",
            "C": "To bypass the password",
            "D": "To speed up the internet"
        },
        "answer": "B"
    },
    {
        "question": "Which TestNG annotation is used to create a 'Data Provider' method?",
        "options": {
            "A": "@Data",
            "B": "@DataProvider",
            "C": "@Test(data)",
            "D": "@Parameter"
        },
        "answer": "B"
    },
    {
        "question": "What is 'mvn clean compile' used for?",
        "options": {
            "A": "To clean the code",
            "B": "To delete the build folder and compile the source code of the project",
            "C": "To run the tests",
            "D": "To install dependencies"
        },
        "answer": "B"
    },
    {
        "question": "What is 'ElementClickInterceptedException'?",
        "options": {
            "A": "The mouse is broken",
            "B": "The element you are trying to click is obscured by another element (e.g., an overlay)",
            "C": "The element is too small",
            "D": "The network is slow"
        },
        "answer": "B"
    },
    {
        "question": "How do you find an element by its exact text in XPath?",
        "options": {
            "A": "//tag[text()='value']",
            "B": "//tag[contains(text(),'value')]",
            "C": "//tag[@text='value']",
            "D": "tag.text('value')"
        },
        "answer": "A"
    },
    {
        "question": "Which TestNG interface allows you to define custom logic for when a test fails?",
        "options": {
            "A": "ITestListener",
            "B": "ISuiteListener",
            "C": "IReporter",
            "D": "IHookable"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Headless Edge' execution?",
        "options": {
            "A": "Running Microsoft Edge without a GUI for automated testing",
            "B": "Testing without the Edge browser",
            "C": "A specialized version of Edge",
            "D": "A security certificate"
        },
        "answer": "A"
    },
    {
        "question": "In Selenium 4, what is 'Network Throttling' used for?",
        "options": {
            "A": "To make the internet faster",
            "B": "To simulate different network speeds (e.g., 3G, 4G, Offline) to see how the app performs",
            "C": "To block certain websites",
            "D": "To monitor the data center"
        },
        "answer": "B"
    },
    {
        "question": "Which CSS selector syntax finds an element whose attribute 'starts with' a specific value?",
        "options": {
            "A": "tag[attribute^='value']",
            "B": "tag[attribute$='value']",
            "C": "tag[attribute*='value']",
            "D": "tag[attribute~='value']"
        },
        "answer": "A"
    },
    {
        "question": "What is 'InvalidSelectorException'?",
        "options": {
            "A": "The element does not exist",
            "B": "The XPath or CSS selector provided is syntactically incorrect",
            "C": "The user password was wrong",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "How do you switch back to the 'parent window' after closing a child window?",
        "options": {
            "A": "driver.switchTo().defaultContent()",
            "B": "driver.switchTo().window(parentHandle)",
            "C": "driver.goBack()",
            "D": "driver.close()"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to get the value of a 'Hidden' attribute from an element?",
        "options": {
            "A": "getText()",
            "B": "getAttribute()",
            "C": "getValue()",
            "D": "fetch()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Jenkins Pipeline' (Jenkinsfile)?",
        "options": {
            "A": "A list of developer names",
            "B": "A script that defines the entire CI/CD process (build, test, deploy) for the project",
            "C": "A type of database",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Selenium 4' BiDi API?",
        "options": {
            "A": "A two-way communication protocol that allows for better browser control and event listening (Bidirectional)",
            "B": "A version of Selenium for two languages",
            "C": "A tool to delete bug reports",
            "D": "A security certificate"
        },
        "answer": "A"
    },
    {
        "question": "Which CSS selector syntax finds an element whose attribute 'ends with' a specific value?",
        "options": {
            "A": "tag[attribute^='value']",
            "B": "tag[attribute$='value']",
            "C": "tag[attribute*='value']",
            "D": "tag[attribute~='value']"
        },
        "answer": "B"
    },
    {
        "question": "What is 'TimeoutException' in Selenium?",
        "options": {
            "A": "The computer shut down",
            "B": "Thrown when a command does not complete in enough time (usually during an Explicit Wait)",
            "C": "The browser was too fast",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to get the size of an element (width and height)?",
        "options": {
            "A": "element.getArea()",
            "B": "element.getSize()",
            "C": "element.getDimensions()",
            "D": "element.getBoundingBox()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Page Load Timeout'?",
        "options": {
            "A": "The time it takes to build a page",
            "B": "A setting that limits the amount of time the driver waits for a page to load completely before throwing an error",
            "C": "A security scan",
            "D": "A hardware monitor"
        },
        "answer": "B"
    },
    {
        "question": "How do you click the 'Refresh' button of the browser in Selenium?",
        "options": {
            "A": "driver.refresh()",
            "B": "driver.navigate().refresh()",
            "C": "driver.get(driver.getCurrentUrl())",
            "D": "Both B and C are valid"
        },
        "answer": "D"
    },
    {
        "question": "Which TestNG attribute is used to run tests in a specific order?",
        "options": {
            "A": "sequence",
            "B": "priority",
            "C": "order",
            "D": "rank"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Stale Element' avoidance strategy 'Self-Healing'?",
        "options": {
            "A": "The code fixing itself",
            "B": "An advanced framework feature that automatically tries to re-locate an element if a Stale exception is hit",
            "C": "A manual bug fix",
            "D": "A security policy"
        },
        "answer": "B"
    },
    {
        "question": "Final question: What is the primary advantage of 'CSS Selectors' over 'XPath'?",
        "options": {
            "A": "They are more powerful",
            "B": "They are generally faster and have better support across different browsers",
            "C": "They can navigate upwards in the DOM",
            "D": "They are easier to write"
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
        # Escape < and > in question text to prevent HTML parsing errors
        question_text = q['question'].replace('<', '&lt;').replace('>', '&gt;')
        elements.append(Paragraph(f"{i}. {question_text}", normal_style))
        elements.append(Spacer(1, 0.1 * inch))

        for key, value in q["options"].items():
            # Escape < and > in option text
            option_text = value.replace('<', '&lt;').replace('>', '&gt;')
            elements.append(Paragraph(f"{key}) {option_text}", normal_style))
            elements.append(Spacer(1, 0.05 * inch))

        # Escape < and > in answer text
        answer_text = q['answer'].replace('<', '&lt;').replace('>', '&gt;')
        elements.append(Paragraph(f"<b>Answer:</b> {answer_text}", normal_style))
        elements.append(Spacer(1, 0.3 * inch))

    doc.build(elements)
    print(f"✅ PDF Generated with {len(questions)} UNIQUE questions only.")


if __name__ == "__main__":
    skill = "Selenium"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
