from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
    {
        "question": "What is Cypress primarily used for?",
        "options": {
            "A": "Unit testing backend Java code",
            "B": "End-to-End (E2E) testing for modern web applications",
            "C": "Managing database backups",
            "D": "Stress testing network hardware"
        },
        "answer": "B"
    },
    {
        "question": "Which programming language is used to write Cypress tests?",
        "options": {
            "A": "Java",
            "B": "JavaScript / TypeScript",
            "C": "Python",
            "D": "C#"
        },
        "answer": "B"
    },
    {
        "question": "Cypress runs inside which of the following?",
        "options": {
            "A": "The browser",
            "B": "A separate Selenium server",
            "C": "The JVM",
            "D": "The command line only"
        },
        "answer": "A"
    },
    {
        "question": "Which command is used to visit a URL in a Cypress test?",
        "options": {
            "A": "cy.go()",
            "B": "cy.visit()",
            "C": "cy.open()",
            "D": "cy.navigate()"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary selector command used to find a DOM element?",
        "options": {
            "A": "cy.find()",
            "B": "cy.get()",
            "C": "cy.select()",
            "D": "cy.element()"
        },
        "answer": "B"
    },
    {
        "question": "How do you click an element in Cypress?",
        "options": {
            "A": "cy.get('.btn').press()",
            "B": "cy.get('.btn').click()",
            "C": "cy.get('.btn').trigger('click')",
            "D": "cy.click('.btn')"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to type text into an input field?",
        "options": {
            "A": "cy.get('input').write('text')",
            "B": "cy.get('input').type('text')",
            "C": "cy.get('input').input('text')",
            "D": "cy.get('input').send('text')"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of the 'cy.contains()' command?",
        "options": {
            "A": "To check if a variable contains a string",
            "B": "To find a DOM element based on the text it contains",
            "C": "To see if a file contains data",
            "D": "To validate a database record"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to make assertions in Cypress (Chai/Sinon based)?",
        "options": {
            "A": "expect()",
            "B": "should()",
            "C": "assert()",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "Cypress commands are asynchronous. How do they handle execution order?",
        "options": {
            "A": "They return standard Promises",
            "B": "They are enqueued and run serially",
            "C": "They run all at once simultaneously",
            "D": "They require 'await' for every line"
        },
        "answer": "B"
    },
    {
        "question": "What is the default timeout for most Cypress commands (like cy.get)?",
        "options": {
            "A": "1000ms",
            "B": "4000ms",
            "C": "10000ms",
            "D": "500ms"
        },
        "answer": "B"
    },
    {
        "question": "Which file is the main configuration file for Cypress (v10+)?",
        "options": {
            "A": "cypress.json",
            "B": "cypress.config.js",
            "C": "config.cypress.ts",
            "D": "package.json"
        },
        "answer": "B"
    },
    {
        "question": "How do you start the Cypress Test Runner UI?",
        "options": {
            "A": "npx cypress run",
            "B": "npx cypress open",
            "C": "npx cypress start",
            "D": "npm test"
        },
        "answer": "B"
    },
    {
        "question": "Which command allows you to work with a subset of the DOM from a parent element?",
        "options": {
            "A": "cy.within()",
            "B": "cy.inside()",
            "C": "cy.children()",
            "D": "cy.narrow()"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of the 'fixtures' folder in Cypress?",
        "options": {
            "A": "To store CSS files",
            "B": "To store static data (JSON) that can be used throughout tests",
            "C": "To store the test scripts",
            "D": "To store screenshots"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to load data from a fixture file?",
        "options": {
            "A": "cy.load()",
            "B": "cy.fixture()",
            "C": "cy.json()",
            "D": "cy.getData()"
        },
        "answer": "B"
    },
    {
        "question": "How do you check if an element is visible on the page?",
        "options": {
            "A": "cy.get('.el').should('be.visible')",
            "B": "cy.get('.el').isVisible()",
            "C": "cy.get('.el').check('visibility')",
            "D": "expect('.el').to.show()"
        },
        "answer": "A"
    },
    {
        "question": "Which command clears the text in an input or textarea?",
        "options": {
            "A": "cy.get('input').empty()",
            "B": "cy.get('input').clear()",
            "C": "cy.get('input').delete()",
            "D": "cy.get('input').type('{backspace}')"
        },
        "answer": "B"
    },
    {
        "question": "What does 'cy.wait(5000)' do?",
        "options": {
            "A": "Waits for an element to appear for 5 seconds",
            "B": "Pauses the test execution for 5000 milliseconds (fixed wait)",
            "C": "Waits for the network to be idle",
            "D": "Retries the previous command for 5 seconds"
        },
        "answer": "B"
    },
    {
        "question": "How do you select an option from a <select> dropdown?",
        "options": {
            "A": "cy.get('select').choose('Option')",
            "B": "cy.get('select').select('Option')",
            "C": "cy.get('select').click('Option')",
            "D": "cy.get('select').set('Option')"
        },
        "answer": "B"
    },
    {
        "question": "What is 'cy.request()' used for?",
        "options": {
            "A": "Requesting user permission",
            "B": "Making HTTP requests (API testing) outside of the browser UI",
            "C": "Requesting a file from the disk",
            "D": "Asking the server to reboot"
        },
        "answer": "B"
    },
    {
        "question": "Which folder typically contains the test files in a Cypress project?",
        "options": {
            "A": "cypress/tests",
            "B": "cypress/e2e",
            "C": "cypress/integration",
            "D": "Both B and C (depending on version)"
        },
        "answer": "D"
    },
    {
        "question": "How do you run Cypress tests in headless mode (terminal only)?",
        "options": {
            "A": "npx cypress open",
            "B": "npx cypress run",
            "C": "npx cypress headless",
            "D": "npm run e2e"
        },
        "answer": "B"
    },
    {
        "question": "What does the 'cy.reload()' command do?",
        "options": {
            "A": "Reloads the Cypress configuration",
            "B": "Refreshes the current page in the browser",
            "C": "Reloads the test file",
            "D": "Clears the cache"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to select a checkbox or radio button?",
        "options": {
            "A": "cy.get('input').click()",
            "B": "cy.get('input').check()",
            "C": "cy.get('input').select()",
            "D": "cy.get('input').on()"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'support/e2e.js' file?",
        "options": {
            "A": "To write the actual tests",
            "B": "To configure global hooks and behaviors that run before every test file",
            "C": "To store JSON data",
            "D": "To manage third-party plugins"
        },
        "answer": "B"
    },
    {
        "question": "How can you debug a Cypress test and pause execution at a certain line?",
        "options": {
            "A": "cy.stop()",
            "B": "cy.debug()",
            "C": "cy.pause()",
            "D": "Both B and C"
        },
        "answer": "D"
    },
    {
        "question": "Which command is used to check the current URL of the page?",
        "options": {
            "A": "cy.url()",
            "B": "cy.location()",
            "C": "cy.getPath()",
            "D": "Both A and B"
        },
        "answer": "D"
    },
    {
        "question": "How do you verify that an element does NOT exist in the DOM?",
        "options": {
            "A": "cy.get('.el').should('not.exist')",
            "B": "cy.get('.el').should('be.hidden')",
            "C": "cy.get('.el').missing()",
            "D": "expect('.el').to.be.gone()"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of 'cy.log()'?",
        "options": {
            "A": "To write a message to the browser console",
            "B": "To print a message into the Cypress Command Log in the Test Runner",
            "C": "To save a file to the system",
            "D": "To log the user into the app"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to move forward or backward in the browser history?",
        "options": {
            "A": "cy.navigate()",
            "B": "cy.go()",
            "C": "cy.history()",
            "D": "cy.back()"
        },
        "answer": "B"
    },
    {
        "question": "How do you select the first element in a list found by cy.get()?",
        "options": {
            "A": "cy.get('li').first()",
            "B": "cy.get('li').index(0)",
            "C": "cy.get('li').get(0)",
            "D": "cy.get('li').one()"
        },
        "answer": "A"
    },
    {
        "question": "Which command checks if a checkbox is checked?",
        "options": {
            "A": "cy.get('input').should('be.on')",
            "B": "cy.get('input').should('be.checked')",
            "C": "cy.get('input').isChecked()",
            "D": "expect('input').to.be.true()"
        },
        "answer": "B"
    },
    {
        "question": "What is the shorthand command for 'cy.get(...).should(...)'?",
        "options": {
            "A": "cy.verify()",
            "B": "cy.should()",
            "C": "cy.expect()",
            "D": "There is no shorthand; should is an alias of and"
        },
        "answer": "D"
    },
    {
        "question": "How do you invoke a function on a DOM element (like .val() or .text())?",
        "options": {
            "A": "cy.get('div').call('text')",
            "B": "cy.get('div').invoke('text')",
            "C": "cy.get('div').run('text')",
            "D": "cy.get('div').text()"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'cy.wrap()' command used for?",
        "options": {
            "A": "To wrap an element in a div",
            "B": "To wrap an object or a Promise so that Cypress commands can be chained off it",
            "C": "To wrap the text in a component",
            "D": "To restart the Cypress process"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to set the browser's viewport size?",
        "options": {
            "A": "cy.resize()",
            "B": "cy.viewport()",
            "C": "cy.screen()",
            "D": "cy.window('size')"
        },
        "answer": "B"
    },
    {
        "question": "Which hook is used to run a set of commands before 'each' individual test in a file?",
        "options": {
            "A": "before()",
            "B": "beforeEach()",
            "C": "init()",
            "D": "start()"
        },
        "answer": "B"
    },
    {
        "question": "Which hook is used to run a set of commands only 'once' before all tests in a file?",
        "options": {
            "A": "beforeEach()",
            "B": "before()",
            "C": "setup()",
            "D": "startOnce()"
        },
        "answer": "B"
    },
    {
        "question": "What does 'cy.title()' return?",
        "options": {
            "A": "The text of the <h1> tag",
            "B": "The document title (found in the <title> tag of the <head>)",
            "C": "The name of the test file",
            "D": "The user's job title"
        },
        "answer": "B"
    },
    {
        "question": "How do you chain another assertion to a 'should' command?",
        "options": {
            "A": ".then()",
            "B": ".and()",
            "C": ".also()",
            "D": ".with()"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'cy.blur()'?",
        "options": {
            "A": "To hide an element from view",
            "B": "To remove focus from a focused DOM element",
            "C": "To make the screenshot blurry",
            "D": "To clear the console"
        },
        "answer": "B"
    },
    {
        "question": "How do you check for a specific CSS class on an element?",
        "options": {
            "A": "cy.get('div').should('have.class', 'active')",
            "B": "cy.get('div').hasClass('active')",
            "C": "cy.get('div').check('active')",
            "D": "expect('div').to.own('active')"
        },
        "answer": "A"
    },
    {
        "question": "What is the purpose of the 'cypress/screenshots' folder?",
        "options": {
            "A": "To store user-uploaded images",
            "B": "To automatically store screenshots taken when a test fails",
            "C": "To store the UI design system",
            "D": "To store the app's logo"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to access the global 'window' object of the application?",
        "options": {
            "A": "cy.browser()",
            "B": "cy.window()",
            "C": "cy.dom()",
            "D": "cy.get('window')"
        },
        "answer": "B"
    },
    {
        "question": "How do you select the parent element of a currently selected element?",
        "options": {
            "A": "cy.get('li').up()",
            "B": "cy.get('li').parent()",
            "C": "cy.get('li').root()",
            "D": "cy.get('li').top()"
        },
        "answer": "B"
    },
    {
        "question": "What does 'cy.dblclick()' do?",
        "options": {
            "A": "Clicks two different buttons",
            "B": "Performs a double-click on a DOM element",
            "C": "Restarts the test",
            "D": "Clicks a button twice with a delay"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to trigger a right-click on an element?",
        "options": {
            "A": "cy.get('div').click('right')",
            "B": "cy.get('div').rightclick()",
            "C": "cy.get('div').trigger('contextmenu')",
            "D": "Both B and C"
        },
        "answer": "D"
    },
    {
        "question": "How do you scroll a specific element into view?",
        "options": {
            "A": "cy.get('footer').scroll()",
            "B": "cy.get('footer').scrollIntoView()",
            "C": "cy.get('footer').move()",
            "D": "cy.scrollTo('footer')"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 1: What makes Cypress different from Selenium?",
        "options": {
            "A": "Selenium runs outside the browser; Cypress runs inside the browser",
            "B": "Selenium supports more languages; Cypress is JS-only",
            "C": "Cypress has automatic waiting; Selenium requires manual waits",
            "D": "All of the above"
        },
        "answer": "D"
    },
   {
        "question": "What is the primary purpose of 'Aliases' in Cypress?",
        "options": {
            "A": "To give the developer a nickname",
            "B": "To store and reference elements, objects, or XHR requests for later use in a test",
            "C": "To rename the test files",
            "D": "To hide sensitive data from logs"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to create an alias?",
        "options": {
            "A": ".name()",
            "B": ".as()",
            "C": ".alias()",
            "D": ".set()"
        },
        "answer": "B"
    },
    {
        "question": "How do you reference an alias named 'submitBtn' in a later command?",
        "options": {
            "A": "cy.get('submitBtn')",
            "B": "cy.get('@submitBtn')",
            "C": "cy.use('submitBtn')",
            "D": "cy.alias('submitBtn')"
        },
        "answer": "B"
    },
    {
        "question": "Where are 'Custom Commands' typically defined in a Cypress project?",
        "options": {
            "A": "cypress/e2e/commands.js",
            "B": "cypress/support/commands.js",
            "C": "cypress.config.js",
            "D": "package.json"
        },
        "answer": "B"
    },
    {
        "question": "Which syntax is used to add a new custom command named 'login'?",
        "options": {
            "A": "cy.add('login', ...)",
            "B": "Cypress.Commands.add('login', ...)",
            "C": "cy.Commands.create('login', ...)",
            "D": "Cypress.addCommand('login', ...)"
        },
        "answer": "B"
    },
    {
        "question": "What happens if a Cypress command fails an assertion?",
        "options": {
            "A": "The test continues to the next line",
            "B": "The test fails immediately and stops execution",
            "C": "Cypress restarts the browser",
            "D": "The command is ignored"
        },
        "answer": "B"
    },
    {
        "question": "Cypress commands are NOT return values. What do they return instead?",
        "options": {
            "A": "null",
            "B": "A special object that is compatible with Promises and can be chained",
            "C": "A string of the DOM element",
            "D": "The actual DOM element immediately"
        },
        "answer": "B"
    },
    {
        "question": "How do you access the value yielded by a Cypress command (like text from an element)?",
        "options": {
            "A": "const val = cy.get('div').text()",
            "B": "cy.get('div').then(($el) => { ... })",
            "C": "cy.get('div').extract()",
            "D": "cy.get('div').yield()"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'cy.intercept()'?",
        "options": {
            "A": "To stop the user from clicking",
            "B": "To spy on, stub, or modify network requests and responses",
            "C": "To intercept browser errors",
            "D": "To block third-party CSS"
        },
        "answer": "B"
    },
    {
        "question": "Which command replaced 'cy.route()' in modern Cypress versions?",
        "options": {
            "A": "cy.network()",
            "B": "cy.intercept()",
            "C": "cy.request()",
            "D": "cy.stub()"
        },
        "answer": "B"
    },
    {
        "question": "What does 'cy.tick()' do in a test?",
        "options": {
            "A": "Measures the performance in seconds",
            "B": "Moves the browser's clock forward by a specified amount of time",
            "C": "Clicks a checkbox",
            "D": "Restarts a timer"
        },
        "answer": "B"
    },
    {
        "question": "How do you 'stub' a function in Cypress using Sinon.js?",
        "options": {
            "A": "cy.get('fn').stub()",
            "B": "cy.stub(object, 'method')",
            "C": "cy.mock('method')",
            "D": "cy.intercept('method')"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'cy.spy()'?",
        "options": {
            "A": "To watch the user's screen",
            "B": "To record function calls and arguments without changing the function's behavior",
            "C": "To find hidden elements",
            "D": "To monitor network speed"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to clear local storage in the browser?",
        "options": {
            "A": "cy.clearLocalStorage()",
            "B": "cy.clearCookies()",
            "C": "cy.reset()",
            "D": "cy.deleteStorage()"
        },
        "answer": "A"
    },
    {
        "question": "What is the default behavior of Cypress regarding Cookies between tests?",
        "options": {
            "A": "It persists all cookies",
            "B": "It automatically clears all cookies before each test",
            "C": "It only saves 'session' cookies",
            "D": "It asks the user to clear them"
        },
        "answer": "B"
    },
    {
        "question": "Which command allows you to access and modify cookies during a test?",
        "options": {
            "A": "cy.cookie()",
            "B": "cy.getCookie() / cy.setCookie()",
            "C": "cy.manageCookies()",
            "D": "cy.request('cookie')"
        },
        "answer": "B"
    },
    {
        "question": "How do you handle a browser alert/window in Cypress?",
        "options": {
            "A": "cy.get('alert').click()",
            "B": "Cypress handles it automatically (auto-confirms)",
            "C": "cy.on('window:alert', (str) => { ... })",
            "D": "Both B and C"
        },
        "answer": "D"
    },
    {
        "question": "What is the 'root' of a Cypress test file (the main container)?",
        "options": {
            "A": "describe() or context()",
            "B": "test()",
            "C": "file()",
            "D": "main()"
        },
        "answer": "A"
    },
    {
        "question": "Which function is used to define an individual test case?",
        "options": {
            "A": "case()",
            "B": "it() or specify()",
            "C": "test()",
            "D": "run()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Retry-ability' in Cypress?",
        "options": {
            "A": "The ability to run a failed test again automatically",
            "B": "The core feature where Cypress retries commands and assertions until they pass or timeout",
            "C": "The ability to restart the server",
            "D": "Manual loop to check elements"
        },
        "answer": "B"
    },
    {
        "question": "How do you find an element that is 'hidden' but exists in the DOM?",
        "options": {
            "A": "cy.get('.hidden')",
            "B": "cy.get('.hidden', { force: true })",
            "C": "cy.get('.hidden').should('exist')",
            "D": "Cypress cannot find hidden elements"
        },
        "answer": "C"
    },
    {
        "question": "What does the '.each()' command do?",
        "options": {
            "A": "Clicks every button on the page",
            "B": "Iterates through an array-like structure (like a list of DOM elements)",
            "C": "Runs the test 10 times",
            "D": "Deletes each element"
        },
        "answer": "B"
    },
    {
        "question": "How do you access the text of an element and compare it using an assertion inside a '.then()' block?",
        "options": {
            "A": "expect($el.text()).to.equal('Hello')",
            "B": "cy.text().should('Hello')",
            "C": "assert.text($el, 'Hello')",
            "D": "$el.check('Hello')"
        },
        "answer": "A"
    },
    {
        "question": "Which command is used to check for the presence of a specific text on the entire page?",
        "options": {
            "A": "cy.get('body').contains('Text')",
            "B": "cy.contains('Text')",
            "C": "cy.hasText('Text')",
            "D": "Both A and B"
        },
        "answer": "D"
    },
    {
        "question": "What is 'cy.its()' used for?",
        "options": {
            "A": "To check if an element 'is' visible",
            "B": "To get a property on the previously yielded subject",
            "C": "To create an identity",
            "D": "To start a timer"
        },
        "answer": "B"
    },
    {
        "question": "Which command allows you to select an element by its index in a list of matches?",
        "options": {
            "A": "cy.get('li').index(2)",
            "B": "cy.get('li').eq(2)",
            "C": "cy.get('li').at(2)",
            "D": "cy.get('li').nth(2)"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'cy.origin()' (v12+)?",
        "options": {
            "A": "To find the original developer",
            "B": "To perform cross-origin testing (visiting different domains in one test)",
            "C": "To reset the test to the start",
            "D": "To check the server's IP"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to trigger a keyboard event like 'Enter'?",
        "options": {
            "A": "cy.get('input').enter()",
            "B": "cy.get('input').type('{enter}')",
            "C": "cy.get('input').press('enter')",
            "D": "cy.get('input').key('enter')"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'cy.session()'?",
        "options": {
            "A": "To start a video call",
            "B": "To cache and restore the state of a user session (like login) to speed up tests",
            "C": "To set the database session",
            "D": "To logout the user"
        },
        "answer": "B"
    },
    {
        "question": "How do you click an element at a specific coordinate?",
        "options": {
            "A": "cy.get('canvas').click(100, 200)",
            "B": "cy.get('canvas').move(100, 200).click()",
            "C": "cy.clickAt(100, 200)",
            "D": "cy.get('canvas').trigger('click', { x: 100, y: 200 })"
        },
        "answer": "A"
    },
    {
        "question": "Which command is used to select all sibling elements?",
        "options": {
            "A": "cy.get('li').siblings()",
            "B": "cy.get('li').others()",
            "C": "cy.get('li').nextAll()",
            "D": "cy.get('li').prevAll()"
        },
        "answer": "A"
    },
    {
        "question": "What does 'cy.task()' do?",
        "options": {
            "A": "Creates a task list in the UI",
            "B": "Allows executing Node.js code outside of the browser (like database seeding)",
            "C": "Checks the task manager",
            "D": "Assigns a developer to a test"
        },
        "answer": "B"
    },
    {
        "question": "How do you verify the value of an input field?",
        "options": {
            "A": "cy.get('input').should('have.text', 'value')",
            "B": "cy.get('input').should('have.value', 'value')",
            "C": "cy.get('input').val().should('value')",
            "D": "expect('input').to.be('value')"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to select elements that are NOT the chosen selector?",
        "options": {
            "A": ".exclude()",
            "B": ".not()",
            "C": ".filter()",
            "D": ".remove()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'cy.request({ failOnStatusCode: false })' used for?",
        "options": {
            "A": "To ignore all errors",
            "B": "To allow Cypress to continue the test even if the API returns a 4xx or 5xx error",
            "C": "To hide the request from the logs",
            "D": "To speed up the request"
        },
        "answer": "B"
    },
    {
        "question": "How do you check if an element is disabled?",
        "options": {
            "A": "cy.get('button').should('be.disabled')",
            "B": "cy.get('button').isDisabled()",
            "C": "cy.get('button').check('off')",
            "D": "expect('button').to.be.false()"
        },
        "answer": "A"
    },
    {
        "question": "Which command allows you to get the children of a DOM element?",
        "options": {
            "A": ".find()",
            "B": ".children()",
            "C": ".sub()",
            "D": ".inner()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'cy.clock()' used for?",
        "options": {
            "A": "To show the time in the Test Runner",
            "B": "To control time-based functions like setTimeout or setInterval",
            "C": "To time the test duration",
            "D": "To schedule a test"
        },
        "answer": "B"
    },
    {
        "question": "What does 'cy.scrollTo('bottom')' do?",
        "options": {
            "A": "Deletes the bottom of the page",
            "B": "Scrolls the entire window/container to the very bottom",
            "C": "Clicks the bottom button",
            "D": "Finds the footer"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to find the first 'ancestor' element that matches a selector?",
        "options": {
            "A": ".parent()",
            "B": ".closest()",
            "C": ".root()",
            "D": ".top()"
        },
        "answer": "B"
    },
    {
        "question": "How do you find an element by its 'data-cy' attribute?",
        "options": {
            "A": "cy.get('data-cy=btn')",
            "B": "cy.get('[data-cy=btn]')",
            "C": "cy.get('#btn')",
            "D": "cy.get('.btn')"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'cy.clearAllLocalStorage()'?",
        "options": {
            "A": "Clears storage for all domains (v12+)",
            "B": "Clears storage for the current domain only",
            "C": "Deletes the browser cache",
            "D": "Restarts the app"
        },
        "answer": "A"
    },
    {
        "question": "Which command returns the focus to a specific element?",
        "options": {
            "A": "cy.get('input').focus()",
            "B": "cy.get('input').click()",
            "C": "cy.get('input').on()",
            "D": "cy.get('input').active()"
        },
        "answer": "A"
    },
    {
        "question": "What happens when you use 'it.only()' in a test file?",
        "options": {
            "A": "It runs that test once",
            "B": "Cypress will only run that specific test and skip all others in the file",
            "C": "The test is marked as private",
            "D": "It deletes the other tests"
        },
        "answer": "B"
    },
    {
        "question": "What happens when you use 'it.skip()'?",
        "options": {
            "A": "Cypress skips the rest of the test",
            "B": "Cypress skips that specific test entirely",
            "C": "Cypress restarts the test",
            "D": "The test runs faster"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to select the next sibling element in the DOM?",
        "options": {
            "A": ".forward()",
            "B": ".next()",
            "C": ".after()",
            "D": ".sibling()"
        },
        "answer": "B"
    },
    {
        "question": "How do you verify that an element 'has' a certain attribute?",
        "options": {
            "A": "cy.get('a').should('have.attr', 'href')",
            "B": "cy.get('a').hasAttr('href')",
            "C": "cy.get('a').check('href')",
            "D": "expect('a').to.own('href')"
        },
        "answer": "A"
    },
    {
        "question": "What is 'cy.document()' used for?",
        "options": {
            "A": "To download a PDF",
            "B": "To access the window.document object of the application",
            "C": "To print the test results",
            "D": "To write documentation"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to get the previous sibling element?",
        "options": {
            "A": ".back()",
            "B": ".prev()",
            "C": ".before()",
            "D": ".last()"
        },
        "answer": "B"
    },
    {
        "question": "Final question of Batch 2: Why are 'cy.get()' selectors considered better than manual 'document.querySelector' in tests?",
        "options": {
            "A": "They look cooler",
            "B": "They include automatic retry-ability until the element exists or the timeout is reached",
            "C": "They can select more elements",
            "D": "They are faster"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to spy on and stub network requests in modern Cypress versions?",
        "options": {
          "A": "cy.route()",
          "B": "cy.intercept()",
          "C": "cy.xhr()",
          "D": "cy.listen()"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary benefit of using cy.intercept() over cy.request()?",
        "options": {
          "A": "cy.intercept() is faster",
          "B": "cy.intercept() manages traffic between the browser and the server, allowing for stubbed responses",
          "C": "cy.request() cannot handle JSON",
          "D": "There is no difference"
        },
        "answer": "B"
    },
    {
        "question": "How do you wait for a specific intercepted network request to complete before continuing the test?",
        "options": {
          "A": "cy.wait('@aliasName')",
          "B": "cy.pause()",
          "C": "cy.hold()",
          "D": "cy.sleep(network)"
        },
        "answer": "A"
    },
    {
        "question": "What does it mean to 'stub' a network response?",
        "options": {
          "A": "To delete the response",
          "B": "To provide a predefined (fake) response to a request instead of hitting the real backend",
          "C": "To speed up the server",
          "D": "To encrypt the data"
        },
        "answer": "B"
    },
    {
        "question": "Which argument in cy.intercept() is used to provide a mock response body?",
        "options": {
          "A": "body",
          "B": "fixture",
          "C": "statusCode",
          "D": "All of the above (within the StaticResponse object)"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Cypress Cloud' (formerly Dashboard) used for?",
        "options": {
          "A": "Writing code in the browser",
          "B": "Recording test results, managing parallelization, and analyzing failures in CI/CD",
          "C": "Storing user passwords",
          "D": "A type of database"
        },
        "answer": "B"
    },
    {
        "question": "How do you run Cypress tests in parallel across multiple machines?",
        "options": {
          "A": "npx cypress run --parallel",
          "B": "npx cypress open --multi",
          "C": "npm run speed",
          "D": "Parallelization is automatic in the Test Runner"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Flakiness' in automated testing?",
        "options": {
          "A": "A test that always fails",
          "B": "A test that inconsistently passes or fails without any changes to the code",
          "C": "A test that runs too fast",
          "D": "A bug in the CSS"
        },
        "answer": "B"
    },
    {
        "question": "How can you mitigate flakiness in Cypress?",
        "options": {
          "A": "Using fixed waits (cy.wait(5000))",
          "B": "Leveraging Cypress's automatic retry-ability and waiting for network aliases",
          "C": "Deleting the test",
          "D": "Restarting the computer"
        },
        "answer": "B"
    },
    {
        "question": "Which command-line flag is used to record a test run to the Cypress Cloud?",
        "options": {
          "A": "--save",
          "B": "--record",
          "C": "--cloud",
          "D": "--log"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'retries' configuration in cypress.config.js?",
        "options": {
          "A": "To retry the entire build if one test fails",
          "B": "To automatically re-run a failed test case a specified number of times before marking it as failed",
          "C": "To retry a failed network request",
          "D": "To loop a test forever"
        },
        "answer": "B"
    },
    {
        "question": "Which environment variable is used to provide a project ID for Cypress Cloud recording?",
        "options": {
          "A": "CYPRESS_RECORD_KEY",
          "B": "CYPRESS_PROJECT_ID",
          "C": "PROJECT_NAME",
          "D": "CLOUD_SECRET"
        },
        "answer": "A"
    },
    {
        "question": "What is 'cy.exec()' used for?",
        "options": {
          "A": "To execute a function in the browser",
          "B": "To run system shell commands (like seeding a database or clearing folders)",
          "C": "To exit the test",
          "D": "To restart the computer"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'Module API' in Cypress?",
        "options": {
          "A": "A way to use ES modules",
          "B": "A way to run Cypress from a Node.js script instead of the command line",
          "C": "A type of routing",
          "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "How do you access 'Environment Variables' inside a Cypress test?",
        "options": {
          "A": "process.env.VAR",
          "B": "Cypress.env('VAR')",
          "C": "cy.getEnv('VAR')",
          "D": "window.VAR"
        },
        "answer": "B"
    },
    {
        "question": "Which file is used to store environment variables locally for Cypress?",
        "options": {
          "A": ".env",
          "B": "cypress.env.json",
          "C": "secrets.json",
          "D": "config.env"
        },
        "answer": "B"
    },
    {
        "question": "What does 'cy.stub()' return in a test?",
        "options": {
          "A": "A boolean",
          "B": "A wrapped function that can be used to make assertions (e.g., .should('be.called'))",
          "C": "Nothing",
          "D": "The original function"
        },
        "answer": "B"
    },
    {
        "question": "How do you verify that a network request was made exactly once?",
        "options": {
          "A": "cy.wait('@alias').should('have.count', 1)",
          "B": "cy.get('@alias.all').should('have.length', 1)",
          "C": "cy.checkCall('@alias')",
          "D": "expect(network).to.be.one()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Cypress.config()' used for inside a test?",
        "options": {
          "A": "To change the computer settings",
          "B": "To retrieve or override configuration values for the duration of the test",
          "C": "To write documentation",
          "D": "To update the app version"
        },
        "answer": "B"
    },
    {
        "question": "Which command allows you to work with <iframe> elements?",
        "options": {
          "A": "cy.iframe()",
          "B": "cy.get('iframe').its('0.contentDocument.body').should('not.be.empty').then(cy.wrap)",
          "C": "cy.switchTo()",
          "D": "Cypress does not support iframes"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Custom Reporters' in Cypress?",
        "options": {
          "A": "People who report bugs",
          "B": "The ability to use different output formats (like JUnit or Mochawesome) for test results",
          "C": "A type of routing",
          "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "How do you prevent a test from failing due to an uncaught exception in the application code?",
        "options": {
          "A": "cy.on('uncaught:exception', () => false)",
          "B": "cy.ignoreErrors()",
          "C": "cy.config('failOnException', false)",
          "D": "It is not possible"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Time Travel' in the Cypress Test Runner?",
        "options": {
          "A": "Actually changing the computer's date",
          "B": "The ability to hover over commands in the log to see the state of the application at that specific moment",
          "C": "A performance metric",
          "D": "A type of routing"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to take a manual screenshot during a test?",
        "options": {
          "A": "cy.capture()",
          "B": "cy.screenshot()",
          "C": "cy.snap()",
          "D": "cy.saveImage()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'cy.writeFile()' used for?",
        "options": {
          "A": "Writing code for the app",
          "B": "Creating a file on the local file system from within a test",
          "C": "Sending an email",
          "D": "A performance test"
        },
        "answer": "B"
    },
    {
        "question": "What is 'cy.readFile()' used for?",
        "options": {
          "A": "Reading the user's mind",
          "B": "Reading the contents of a file on the local file system",
          "C": "Checking the database",
          "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "Which hook runs after 'all' tests in a file have completed?",
        "options": {
          "A": "afterEach()",
          "B": "after()",
          "C": "finish()",
          "D": "stop()"
        },
        "answer": "B"
    },
    {
        "question": "How do you handle a scenario where the application opens a new browser tab?",
        "options": {
          "A": "Cypress switches tabs automatically",
          "B": "Cypress does not support multiple tabs; you should remove 'target=_blank' before clicking",
          "C": "cy.switchTab()",
          "D": "cy.get('window').at(1)"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Headless' browser execution?",
        "options": {
          "A": "Running without a developer present",
          "B": "Running the browser without a visible User Interface (UI), common in CI/CD",
          "C": "A browser without a header",
          "D": "A performance test"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to clear all browser cookies?",
        "options": {
          "A": "cy.clearCookies()",
          "B": "cy.resetCookies()",
          "C": "cy.deleteCookies()",
          "D": "cy.clearAllCookies() (v12.1+ for multiple domains)"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Stubbing the server'?",
        "options": {
          "A": "Deleting the server",
          "B": "Using cy.intercept() to provide fake data, allowing frontend testing without a backend",
          "C": "Restarting the backend",
          "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "Which status code represents a 'Not Found' error in an intercepted request?",
        "options": {
          "A": "200",
          "B": "404",
          "C": "500",
          "D": "403"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Parallelization' in the context of Cypress CI?",
        "options": {
          "A": "Running tests at the same time on one computer",
          "B": "Dividing tests across multiple virtual machines to reduce total execution time",
          "C": "A type of routing",
          "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "Which command allows you to perform an action on the parent of a DOM element?",
        "options": {
          "A": ".child()",
          "B": ".parent()",
          "C": ".root()",
          "D": ".top()"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'cypress/videos' folder?",
        "options": {
          "A": "To store movies for the developers",
          "B": "To store MP4 video recordings of test runs, often used for debugging CI failures",
          "C": "A database for images",
          "D": "A performance test"
        },
        "answer": "B"
    },
    {
        "question": "How do you check if an element 'contains' a specific value, ignoring case sensitivity?",
        "options": {
          "A": "cy.contains('text', { matchCase: false })",
          "B": "cy.get('.el').should('include', 'text')",
          "C": "cy.find('text').any()",
          "D": "expect('text').to.be.lowered()"
        },
        "answer": "A"
    },
    {
        "question": "Which tool is commonly used to generate HTML reports from Cypress JSON results?",
        "options": {
          "A": "Prettier",
          "B": "Mochawesome",
          "C": "Eslint",
          "D": "Vite"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Cypress Component Testing'?",
        "options": {
          "A": "Testing the individual React/Vue/Angular components in isolation rather than the whole app",
          "B": "Testing the computer hardware",
          "C": "A type of routing",
          "D": "A security scan"
        },
        "answer": "A"
    },
    {
        "question": "What is the 'baseUrl' configuration used for?",
        "options": {
          "A": "To name the server",
          "B": "To set a prefix for all cy.visit() and cy.request() commands, making tests more portable",
          "C": "To secure the URL",
          "D": "To monitor traffic"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to trigger a keyboard shortcut like 'CMD + S'?",
        "options": {
          "A": "cy.type('{meta}{s}')",
          "B": "cy.shortcut('S')",
          "C": "cy.get('body').press('S')",
          "D": "cy.hotkey('S')"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Request Polling' in a test?",
        "options": {
          "A": "Asking the user for a vote",
          "B": "Repeatedly making a request until a certain condition is met",
          "C": "A type of unit test",
          "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "What does 'cy.then()' ensure regarding asynchronous code?",
        "options": {
          "A": "It makes the code faster",
          "B": "It allows you to work with the yielded subject after the previous Cypress command has fully resolved",
          "C": "It ignores all errors",
          "D": "It restarts the test"
        },
        "answer": "B"
    },
    {
        "question": "How do you check if an element is 'focused'?",
        "options": {
          "A": "cy.get('input').should('have.focus')",
          "B": "cy.get('input').isFocused()",
          "C": "cy.get('input').on()",
          "D": "expect('input').to.be.active()"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Shadow DOM' support in Cypress?",
        "options": {
          "A": "A hidden mode for developers",
          "B": "The ability to find and interact with elements inside a Shadow Root by setting 'includeShadowDom: true'",
          "C": "A backup of the UI",
          "D": "A type of routing"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to clear the focus from an element?",
        "options": {
          "A": "cy.get('input').blur()",
          "B": "cy.get('input').off()",
          "C": "cy.get('input').clear()",
          "D": "cy.get('input').reset()"
        },
        "answer": "A"
    },
    {
        "question": "How do you verify the background color of an element?",
        "options": {
          "A": "cy.get('div').should('have.css', 'background-color', 'rgb(0, 0, 0)')",
          "B": "cy.get('div').getColor()",
          "C": "cy.get('div').style('color')",
          "D": "expect('div').to.be.black()"
        },
        "answer": "A"
    },
    {
        "question": "What is the 'watchForFileChanges' configuration used for?",
        "options": {
          "A": "To watch for user errors",
          "B": "Determines if Cypress should automatically re-run tests when a test file is saved",
          "C": "A performance test",
          "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "Which utility is used to define custom environment variables in a shell before running Cypress?",
        "options": {
          "A": "export CYPRESS_VAR=val",
          "B": "set VAR=val",
          "C": "env VAR=val",
          "D": "Both A and B (OS dependent)"
        },
        "answer": "D"
    },
    {
        "question": "Final question of Batch 3: What is the primary cause of 'Test Flakiness' in modern SPAs?",
        "options": {
          "A": "Slow internet",
          "B": "Asynchronous data loading and race conditions where elements aren't ready when the test tries to interact",
          "C": "Incorrect CSS",
          "D": "The computer is too old"
        },
        "answer": "B"
    },
    {
        "question": "What is the primary difference between E2E and Component Testing in Cypress?",
        "options": {
            "A": "E2E is for backend; Component is for frontend",
            "B": "E2E tests the whole application; Component testing mounts a specific component in isolation",
            "C": "Component testing is only for mobile",
            "D": "E2E is faster than Component testing"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to mount a React or Vue component in a Component Test?",
        "options": {
            "A": "cy.visit()",
            "B": "cy.mount()",
            "*": "cy.render()",
            "D": "cy.setComponent()"
        },
        "answer": "B"
    },
    {
        "question": "How does Cypress handle 'Cross-Origin' errors compared to older versions?",
        "options": {
            "A": "It still blocks all cross-origin requests",
            "B": "The 'cy.origin()' command allows interacting with multiple domains in a single test",
            "C": "It requires a paid license for cross-origin",
            "D": "It only works in Chrome"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Cypress.session.clearAllSavedSessions()' used for?",
        "options": {
            "A": "Deleting user accounts",
            "B": "Clearing all cached session data created by cy.session()",
            "C": "Restarting the browser",
            "D": "Clearing the console"
        },
        "answer": "B"
    },
    {
        "question": "Which property in the config file allows you to define custom folder paths for tests?",
        "options": {
            "A": "testFiles",
            "B": "specPattern",
            "C": "folderPath",
            "D": "sourceMap"
        },
        "answer": "B"
    },
    {
        "question": "What is a 'Cypress Plugin' primarily used for?",
        "options": {
            "A": "To add visual themes to the UI",
            "B": "To tap into the internal lifecycle of Cypress and extend its Node.js capabilities",
            "C": "To write the HTML of the app",
            "D": "To manage database passwords"
        },
        "answer": "B"
    },
    {
        "question": "What is 'cypress-real-events' plugin used for?",
        "options": {
            "A": "Tracking real people using the app",
            "B": "Simulating native browser events (like hover or swipe) that cy.trigger() might miss",
            "C": "Measuring real network speed",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "How do you handle 'File Uploads' in Cypress?",
        "options": {
            "A": "cy.get('input').type('path/to/file')",
            "B": "Using the .selectFile() command (built-in in modern versions)",
            "C": "cy.upload('file')",
            "D": "It is not possible in Cypress"
        },
        "answer": "B"
    },
    {
        "question": "What is 'cy.request({ method: \"POST\" })' useful for during an E2E test?",
        "options": {
            "A": "Updating the UI",
            "B": "Quickly setting up state (like logging in or creating data) via the API before the UI test starts",
            "C": "Checking for CSS errors",
            "D": "A performance test"
        },
        "answer": "B"
    },
    {
        "question": "Which assertion is used to verify the number of elements found in a collection?",
        "options": {
            "A": "should('have.length', 5)",
            "B": "should('be.count', 5)",
            "C": "should('size', 5)",
            "D": "expect(5).to.exist()"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Visual Regression' testing in Cypress?",
        "options": {
            "A": "Checking if the code looks clean",
            "B": "Comparing screenshots of the UI against baseline images to detect unintended visual changes",
            "C": "Testing for color-blind users",
            "D": "A type of routing"
        },
        "answer": "B"
    },
    {
        "question": "Which third-party service is popular for Visual Testing with Cypress?",
        "options": {
            "A": "Applitools or Percy",
            "B": "GitHub",
            "C": "Postman",
            "D": "Jenkins"
        },
        "answer": "A"
    },
    {
        "question": "What is the 'cypress/fixtures' file size limit?",
        "options": {
            "A": "1MB",
            "B": "There is no hard limit, but large files can slow down test execution",
            "C": "10MB",
            "D": "100KB"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Data-Driven Testing' in Cypress?",
        "options": {
            "A": "Testing the database directly",
            "B": "Running the same test logic multiple times using different sets of data from a fixture",
            "C": "A type of unit test",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What does 'cy.stub().as(\"myStub\")' allow you to do later in the test?",
        "options": {
            "A": "Delete the stub",
            "B": "Verify that the stub was called using cy.get('@myStub').should('have.been.called')",
            "C": "Rename the function",
            "D": "Encrypt the function"
        },
        "answer": "B"
    },
    {
        "question": "How can you speed up Cypress tests in a CI environment?",
        "options": {
            "A": "Disable video recording and screenshots for passing tests",
            "B": "Use parallelization",
            "C": "Increase the machine's RAM",
            "D": "All of the above"
        },
        "answer": "D"
    },
    {
        "question": "What is 'Atomic Testing' in Cypress?",
        "options": {
            "A": "Testing nuclear software",
            "B": "Keeping tests small and focused on a single feature to make them faster and easier to debug",
            "C": "A type of sharding",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is the 'experimentalStudio' feature?",
        "options": {
            "A": "A new UI for developers",
            "B": "A low-code feature that allows users to record their interactions to generate test code (deprecated/moved to plugins)",
            "C": "A database for experiments",
            "D": "A performance test"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to ensure a list of elements 'at least' has a certain number of items?",
        "options": {
            "A": "should('have.length.at.least', 3)",
            "B": "should('be.more.than', 2)",
            "C": "expect(list).to.be.big()",
            "D": "cy.check(min, 3)"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Chrome Web Security' setting (chromeWebSecurity: false) used for?",
        "options": {
            "A": "To make the browser more secure",
            "B": "To bypass certain security restrictions (like Same-Origin Policy) during testing",
            "C": "To update the browser",
            "D": "A security scan"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Cypress.on('window:confirm')' useful for?",
        "options": {
            "A": "Confirming the user's password",
            "B": "Handling browser confirmation dialogs by returning true or false programmatically",
            "C": "Confirming the test results",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "What is the purpose of 'cypress-axe' plugin?",
        "options": {
            "A": "To delete files",
            "B": "To run accessibility (a11y) audits on your application during tests",
            "C": "A specialized version of the CLI",
            "D": "To measure network speed"
        },
        "answer": "B"
    },
    {
        "question": "How do you verify that an element has a specific 'value' in an input field?",
        "options": {
            "A": "should('have.value', 'abc')",
            "B": "should('have.text', 'abc')",
            "C": "expect('abc').to.exist()",
            "D": "cy.get('val').be('abc')"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Alias referencing' with 'this' context (not using arrow functions)?",
        "options": {
            "A": "A way to share data between tests",
            "B": "Accessing an alias value via this.aliasName in traditional function blocks",
            "C": "A security vulnerability",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "What does 'cy.clock()' allow you to manipulate?",
        "options": {
            "A": "The computer's system time",
            "B": "The browser's Date object and timers (setTimeout, setInterval)",
            "C": "The time zone of the server",
            "D": "The test duration"
        },
        "answer": "B"
    },
    {
        "question": "Which command is used to 'wait' for a specific amount of time, even if it is discouraged?",
        "options": {
            "A": "cy.pause()",
            "B": "cy.wait(number)",
            "C": "cy.delay()",
            "D": "cy.stop()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'cy.scrollTo('center')' used for?",
        "options": {
          "A": "Centering a component on the screen",
          "B": "Scrolling the current container to the center position",
          "C": "Moving the mouse to the center",
          "D": "A type of routing"
        },
        "answer": "B"
    },
    {
        "question": "How do you run only the tests that have changed in a Git commit?",
        "options": {
            "A": "npx cypress run --changed",
            "B": "Cypress does not natively support this; it requires a CI script or custom tool",
            "C": "npm run git-test",
            "D": "cy.git('run')"
        },
        "answer": "B"
    },
    {
        "question": "What is 'cy.spy()' usage after a function call?",
        "options": {
            "A": "To see what the function does",
            "B": "To assert that the function was called with specific arguments",
            "C": "To delete the function",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Cypress.Promise' used for?",
        "options": {
            "A": "Making a promise to finish the test",
            "B": "Using a Bluebird-powered Promise implementation inside a test",
            "C": "A type of unit test",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "Which property in 'cy.intercept()' allows for throttling network speed?",
        "options": {
            "A": "speed",
            "B": "throttle",
            "C": "delay",
            "D": "latency"
        },
        "answer": "C"
    },
    {
        "question": "What is 'cy.request({ auth: { ... } })' used for?",
        "options": {
            "A": "Asking for permission",
            "B": "Making an API request with Basic Authentication credentials",
            "C": "A type of routing",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "How do you clear 'Session Storage' (specifically)?",
        "options": {
            "A": "cy.clearLocalStorage()",
            "B": "Cypress does not have a native cy.clearSessionStorage; you use window.sessionStorage.clear()",
            "C": "cy.reset()",
            "D": "cy.clearAll()"
        },
        "answer": "B"
    },
    {
        "question": "What is 'cy.setCookie()' used for?",
        "options": {
            "A": "Baking a cookie",
            "B": "Manually setting a browser cookie to bypass login or set preferences",
            "C": "A type of sharding",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Cypress.arch'?",
        "options": {
            "A": "A physical arch in the office",
            "B": "A property that returns the CPU architecture of the machine running Cypress (e.g., x64)",
            "C": "A type of routing",
            "D": "A performance test"
        },
        "answer": "B"
    },
    {
        "question": "What is 'cy.location('pathname')' used for?",
        "options": {
            "A": "Finding the server location",
            "B": "Verifying the current path of the URL (e.g., /dashboard)",
            "C": "Checking the GPS",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "What does 'expect(val).to.be.within(5, 10)' check?",
        "options": {
            "A": "If the value is a number between 5 and 10",
            "B": "If the value is found in the office",
            "C": "A type of routing",
            "D": "A security scan"
        },
        "answer": "A"
    },
    {
        "question": "What is 'Stubbing' vs 'Mocking' in Cypress terminology?",
        "options": {
            "A": "They are the same thing",
            "B": "Stubbing provides a fixed response; Mocking (spying/intercepting) verifies behavior/expectations",
            "C": "Stubbing is for CSS; Mocking for JS",
            "D": "Mocking is faster"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Cypress Dashboard Parallelization' requirement?",
        "options": {
            "A": "A paid plan and multiple CI containers",
            "B": "Just a fast computer",
            "C": "A database",
            "D": "A specific version of Linux"
        },
        "answer": "A"
    },
    {
        "question": "What is 'cy.get().find()' used for?",
        "options": {
            "A": "To double-search for a file",
            "B": "To find a specific descendant element within a parent element already found by get()",
            "C": "A performance test",
            "D": "A type of unit test"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Cypress.spec' property used for?",
        "options": {
            "A": "To see the specs of the computer",
            "B": "To access metadata about the current test file (name, relative path, etc.)",
            "C": "A type of unit test",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'cy.root()' used for?",
        "options": {
            "A": "To find the root of the server",
            "B": "Returns the current root DOM element (usually <html>, or the parent element inside a .within() block)",
            "C": "To restart the app",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "What is 'cy.fixture().then()' common usage?",
        "options": {
            "A": "To delete the fixture",
            "B": "To perform operations (like an API post) using the data loaded from the fixture file",
            "C": "To update the app version",
            "D": "A performance test"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Default Command Timeout' in Cypress?",
        "options": {
            "A": "4 seconds",
            "B": "10 seconds",
            "C": "1 minute",
            "D": "500ms"
        },
        "answer": "A"
    },
    {
        "question": "What is 'cy.intercept({ times: 1 })' used for?",
        "options": {
            "A": "To intercept 1 second of traffic",
            "B": "To intercept the request only once and then let subsequent requests pass through to the real server",
            "C": "To speed up the network",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "What is 'cy.get().type(\"{esc}\")' used for?",
        "options": {
            "A": "To type the letters E-S-C",
            "B": "To simulate the user pressing the Escape key",
            "C": "To close Cypress",
            "D": "A security scanner"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Cypress.env()' without arguments used for?",
        "options": {
            "A": "To delete all environment variables",
            "B": "To return an object containing all defined environment variables",
            "C": "To check the server status",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "What is 'cy.request({ followRedirect: false })' useful for?",
        "options": {
            "A": "To stop the user from navigating",
            "B": "To test that a specific URL actually returns a 301/302 redirect instead of following it automatically",
            "C": "A performance test",
            "D": "A security certificate"
        },
        "answer": "B"
    },
    {
        "question": "What is 'Cypress Testing Library'?",
        "options": {
            "A": "A physical library of books",
            "B": "A popular plugin that adds user-centric selectors (like findByRole, findByText) to Cypress",
            "C": "A type of database",
            "D": "A performance metric"
        },
        "answer": "B"
    },
    {
        "question": "Final question: What is the main goal of using Cypress for the VerifiHire AI portal?",
        "options": {
            "A": "To make the UI look better",
            "B": "To ensure reliable, bug-free user journeys across the assessment platform",
            "C": "To replace the developers",
            "D": "To speed up the internet"
        },
        "answer": "B"
    } ,
    {
        "question": "Cypress provides a feature called 'Automatic Waiting'. Which of the following best describes how it handles a command like cy.get('.btn').click()?",
        "options": {
            "A": "It waits for a fixed 5-second interval before every click",
            "B": "It automatically waits for the element to exist, become visible, stop animating, and become 'actionable' before attempting the click",
            "C": "It attempts the click immediately and restarts the entire test if the element is missing",
            "D": "It requires the developer to manually write 'await' before every command"
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
    skill = "Cypress"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
