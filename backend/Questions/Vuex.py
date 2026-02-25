from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
  {
    "question": "What is the primary constraint of a Vuex Mutation?",
    "options": {
      "A": "It must return a Promise",
      "B": "It must be synchronous",
      "C": "It must be asynchronous",
      "D": "It can only change one state property at a time"
    },
    "answer": "B"
  },
  {
    "question": "Which of the following is the 'payload' in: store.commit('updateName', 'John')?",
    "options": {
      "A": "updateName",
      "B": "store",
      "C": "John",
      "D": "commit"
    },
    "answer": "C"
  },
  {
    "question": "Why does Vuex enforce mutations for state changes instead of direct assignment?",
    "options": {
      "A": "To make the code look more complex",
      "B": "To allow devtools to track every change and enable time-travel debugging",
      "C": "Because direct assignment is deprecated in JavaScript",
      "D": "To improve CSS rendering speed"
    },
    "answer": "B"
  },
  {
    "question": "What is the first argument received by a Mutation handler?",
    "options": {
      "A": "The root state",
      "B": "The current module's state",
      "C": "The action context",
      "D": "The getters object"
    },
    "answer": "B"
  },
  {
    "question": "In 'Object-Style Commits', how is the mutation type specified?",
    "options": {
      "A": "As the first argument string",
      "B": "As a 'type' property within the object",
      "C": "As a comment",
      "D": "As a separate variable"
    },
    "answer": "B"
  },
  {
    "question": "Can an Action call another Action?",
    "options": {
      "A": "No, actions are isolated",
      "B": "Yes, using context.dispatch()",
      "C": "Only if they are in different modules",
      "D": "Only in strict mode"
    },
    "answer": "B"
  },
  {
    "question": "How do you handle a successful API response inside an Action?",
    "options": {
      "A": "Update the state directly with the response",
      "B": "Commit a mutation with the response data as the payload",
      "C": "Call a getter to save the data",
      "D": "Refresh the browser"
    },
    "answer": "B"
  },
  {
    "question": "What is the benefit of returning a Promise from an Action?",
    "options": {
      "A": "It makes the action run faster",
      "B": "It allows the component to know when the action is finished (e.g., using .then() or await)",
      "C": "It is required for mutations to work",
      "D": "It hides the data from the user"
    },
    "answer": "B"
  },
  {
    "question": "Which helper is used to map store.dispatch calls to local component methods?",
    "options": {
      "A": "mapState",
      "B": "mapMutations",
      "C": "mapActions",
      "D": "mapGetters"
    },
    "answer": "C"
  },
  {
    "question": "What happens if you perform an asynchronous task inside a Mutation?",
    "options": {
      "A": "The app crashes immediately",
      "B": "State changes won't be trackable by devtools and may cause race conditions",
      "C": "Vuex automatically converts it to an Action",
      "D": "Nothing, it is perfectly fine"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Action Composition' refer to?",
    "options": {
      "A": "Writing actions in a specific CSS format",
      "B": "Chaining multiple actions together to handle complex async flows",
      "C": "The way actions are deleted",
      "D": "Using actions instead of components"
    },
    "answer": "B"
  },
  {
    "question": "In the Action context, what is 'rootGetters' used for?",
    "options": {
      "A": "To access getters from the global store within a namespaced module",
      "B": "To delete all getters",
      "C": "To update the state",
      "D": "To change the root URL"
    },
    "answer": "A"
  },
  {
    "question": "When using 'mapMutations', where do these usually go in a Vue component?",
    "options": {
      "A": "In computed",
      "B": "In data",
      "C": "In methods",
      "D": "In watch"
    },
    "answer": "C"
  },
  {
    "question": "What is a 'Mutation Type' usually defined as to prevent typos?",
    "options": {
      "A": "A random number",
      "B": "A string constant (e.g., export const SOME_MUTATION = 'SOME_MUTATION')",
      "C": "A CSS class",
      "D": "A local component variable"
    },
    "answer": "B"
  },
  {
    "question": "Which of these is the correct way to commit a mutation with a payload?",
    "options": {
      "A": "this.$store.commit('myMutation', { id: 1 })",
      "B": "this.$store.state.myMutation({ id: 1 })",
      "C": "this.$store.dispatch('myMutation', { id: 1 })",
      "D": "this.$store.getters.myMutation({ id: 1 })"
    },
    "answer": "A"
  },
  {
    "question": "Can you access 'State' directly inside an Action?",
    "options": {
      "A": "No, only via mutations",
      "B": "Yes, through context.state",
      "C": "Only if it is public",
      "D": "Only in Vue 2"
    },
    "answer": "B"
  },
  {
    "question": "What is the main purpose of the 'context' object in Actions?",
    "options": {
      "A": "To provide access to commit, dispatch, state, and getters",
      "B": "To store temporary data",
      "C": "To connect to the database",
      "D": "To render the template"
    },
    "answer": "A"
  },
  {
    "question": "Is it possible to use 'async/await' inside a Vuex Action?",
    "options": {
      "A": "No, only Promises are allowed",
      "B": "Yes, it is the modern way to handle asynchronous code in actions",
      "C": "Only if the mutation is also async",
      "D": "Only with a plugin"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Store' in the Vuex context?",
    "options": {
      "A": "A local database",
      "B": "A reactive container that holds the app state and logic",
      "C": "A component",
      "D": "An HTML tag"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used to manually watch store changes from outside a component?",
    "options": {
      "A": "store.observe()",
      "B": "store.watch()",
      "C": "store.look()",
      "D": "store.track()"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Dispatching' an action return?",
    "options": {
      "A": "The new state",
      "B": "A Promise (if the action handler returns one or is async)",
      "C": "The mutation type",
      "D": "Nothing"
    },
    "answer": "B"
  },
  {
    "question": "If an Action is triggered by a button click, where should the 'loading' state usually be toggled?",
    "options": {
      "A": "In the component template",
      "B": "Inside the Action (committing a mutation before and after the async task)",
      "C": "In the CSS",
      "D": "In the router"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary role of mapActions in a component?",
    "options": {
      "A": "To create new actions",
      "B": "To alias store actions as local methods for easier use",
      "C": "To prevent actions from running",
      "D": "To log action history"
    },
    "answer": "B"
  },
  {
    "question": "How do you pass a payload to an action using 'dispatch'?",
    "options": {
      "A": "store.dispatch('actionName', payload)",
      "B": "store.dispatch('actionName').payload(data)",
      "C": "store.dispatch(payload, 'actionName')",
      "D": "store.actionName(payload)"
    },
    "answer": "A"
  },
  {
    "question": "Can a single Action commit multiple Mutations?",
    "options": {
      "A": "No, one action = one mutation",
      "B": "Yes, an action can commit as many mutations as needed",
      "C": "Only in production",
      "D": "Only if they are in the same file"
    },
    "answer": "B"
  },
  {
    "question": "Which concept ensures that state is only changed in a predictable way?",
    "options": {
      "A": "Actions",
      "B": "Mutations",
      "C": "Getters",
      "D": "Modules"
    },
    "answer": "B"
  },
  {
    "question": "What is 'State' in the context of Vuex?",
    "options": {
      "A": "A list of functions",
      "B": "The data that the application depends on",
      "C": "The server URL",
      "D": "The HTML structure"
    },
    "answer": "B"
  },
  {
    "question": "When should you use 'this.$store.dispatch'?",
    "options": {
      "A": "When you want to change state synchronously",
      "B": "When you want to trigger logic that may include async operations or multiple mutations",
      "C": "When you want to fetch a getter",
      "D": "When you want to navigate to a new page"
    },
    "answer": "B"
  },
  {
    "question": "How does Vuex track changes for DevTools?",
    "options": {
      "A": "By intercepting every action",
      "B": "By taking snapshots of the state after every mutation",
      "C": "By reading the console logs",
      "D": "By restarting the app"
    },
    "answer": "B"
  },
  {
    "question": "What is the advantage of using constants for Mutation types?",
    "options": {
      "A": "It makes the app faster",
      "B": "It helps collaborators see what mutations are available and prevents spelling errors",
      "C": "It is required by the Vue compiler",
      "D": "It encrypts the mutation name"
    },
    "answer": "B"
  },
  {
    "question": "Can you pass an object as a payload to a mutation?",
    "options": {
      "A": "No, only strings",
      "B": "Yes, and it is common practice for passing multiple values",
      "C": "Only if the object is flat",
      "D": "Only in Vue 3"
    },
    "answer": "B"
  },
  {
    "question": "What happens if two different actions have the same name in a non-namespaced store?",
    "options": {
      "A": "Only the first one runs",
      "B": "Both are triggered when the action name is dispatched",
      "C": "Vue throws a fatal error",
      "D": "The app ignores both"
    },
    "answer": "B"
  },
  {
    "question": "Which of these is a common pattern for handling errors in Actions?",
    "options": {
      "A": "try/catch blocks with async/await",
      "B": "If/else statements in mutations",
      "C": "Using CSS error classes",
      "D": "Deleting the state"
    },
    "answer": "A"
  },
  {
    "question": "What does 'mapMutations({ add: 'INCREMENT' })' do in a component?",
    "options": {
      "A": "Maps the 'add' mutation to a local 'INCREMENT' method",
      "B": "Maps the 'INCREMENT' mutation to a local 'add' method",
      "C": "Creates a new mutation called add",
      "D": "Adds a number to the state"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Commit with payload' syntax?",
    "options": {
      "A": "store.commit('name', payload)",
      "B": "store.commit(payload, 'name')",
      "C": "store('name').commit(payload)",
      "D": "commit.name(payload)"
    },
    "answer": "A"
  },
  {
    "question": "How does 'this.$store' become available in all components?",
    "options": {
      "A": "By importing Vuex in every component",
      "B": "By 'injecting' the store into the root Vue instance during initialization",
      "C": "By declaring it as a global window variable",
      "D": "It is built-in to JavaScript"
    },
    "answer": "B"
  },
  {
    "question": "Can you use Mutations inside an Action?",
    "options": {
      "A": "No, only actions call actions",
      "B": "Yes, by calling context.commit()",
      "C": "Only if the action is synchronous",
      "D": "Only if the mutation returns a Promise"
    },
    "answer": "B"
  },
  {
    "question": "What is the result of using 'dispatch' on an action that returns a value?",
    "options": {
      "A": "The value is lost",
      "B": "The value is returned to the caller",
      "C": "The value is saved to state automatically",
      "D": "The value is logged to the console"
    },
    "answer": "B"
  },
  {
    "question": "In a Mutation, can you access other Getters?",
    "options": {
      "A": "Yes, as the third argument",
      "B": "No, mutations only have access to state and payload",
      "C": "Only if they are global",
      "D": "Only in Vuex 4"
    },
    "answer": "B"
  },
  {
    "question": "What is the recommended way to structure a large Vuex store?",
    "options": {
      "A": "One giant file",
      "B": "Using Modules to split state by feature",
      "C": "Using multiple separate stores",
      "D": "Putting everything in component local state"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Flux' architecture which Vuex is based on?",
    "options": {
      "A": "A bidirectional data flow",
      "B": "A unidirectional data flow pattern for state management",
      "C": "A type of server-side rendering",
      "D": "A database query language"
    },
    "answer": "B"
  },
  {
    "question": "Does Vuex replace the need for an API layer?",
    "options": {
      "A": "Yes, it handles database connections",
      "B": "No, it acts as a middleman between your components and your API services",
      "C": "Only for GET requests",
      "D": "Only for mobile apps"
    },
    "answer": "B"
  },
  {
    "question": "What does 'store.replaceState(newState)' do?",
    "options": {
      "A": "Adds new properties to the state",
      "B": "Replaces the entire current state with a new object (often used for hydration from SSR)",
      "C": "Deletes the state",
      "D": "Updates a single property"
    },
    "answer": "B"
  },
  {
    "question": "Can you call 'dispatch' from within a Mutation?",
    "options": {
      "A": "Yes, via the context argument",
      "B": "No, mutations cannot trigger actions; they can only modify state",
      "C": "Only in strict mode",
      "D": "Only if it is a namespaced mutation"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Action context destructuring'?",
    "options": {
      "A": "Breaking the store into modules",
      "B": "Using { commit } instead of context in the action argument (e.g., actionName({ commit }) { ... })",
      "C": "Deleting context properties",
      "D": "Renaming the state"
    },
    "answer": "B"
  },
  {
    "question": "How do you define a default value for the store state?",
    "options": {
      "A": "In the mutation",
      "B": "In the initial state object passed to createStore",
      "C": "In the HTML template",
      "D": "In the component props"
    },
    "answer": "B"
  },
  {
    "question": "What is the best practice for naming Actions vs Mutations?",
    "options": {
      "A": "Use the same name for both",
      "B": "Use descriptive verbs for actions (fetchData) and simple names for mutations (SET_DATA)",
      "C": "There is no best practice",
      "D": "Actions must be all lowercase"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Vuex Logger'?",
    "options": {
      "A": "A tool to log user activity",
      "B": "An official plugin that logs state changes and mutations to the console for debugging",
      "C": "A security feature",
      "D": "A server-side tool"
    },
    "answer": "B"
  },
  {
    "question": "What does it mean that Vuex is 'opinionated'?",
    "options": {
      "A": "It can't be used with other libraries",
      "B": "It enforces a specific structure and set of rules for how state should change",
      "C": "It only works with Vue 2",
      "D": "It has its own browser"
    },
    "answer": "B"
  },
  {
    "question": "In a large team, what is the primary benefit of Vuex?",
    "options": {
      "A": "It makes the app smaller",
      "B": "It provides a standardized way to manage state, making code more predictable and easier to debug",
      "C": "It removes the need for meetings",
      "D": "It speeds up the build process"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'modules' property in the Vuex store?",
    "options": {
      "A": "To import CSS modules",
      "B": "To divide the store into smaller pieces, each with its own state, mutations, and actions",
      "C": "To install third-party plugins",
      "D": "To manage multiple Vue apps on one page"
    },
    "answer": "B"
  },
  {
    "question": "By default, are actions and mutations inside modules registered under the global namespace?",
    "options": {
      "A": "No, they are always private",
      "B": "Yes, multiple modules can react to the same mutation/action type",
      "C": "Only if they are in the root file",
      "D": "Only in Vuex 3"
    },
    "answer": "B"
  },
  {
    "question": "How do you make a module self-contained and encapsulated?",
    "options": {
      "A": "Set 'private: true' in the module",
      "B": "Set 'namespaced: true' in the module",
      "C": "Use a different file extension",
      "D": "It is automatic in Vue 3"
    },
    "answer": "B"
  },
  {
    "question": "How do you dispatch a namespaced action called 'login' in a module named 'auth'?",
    "options": {
      "A": "dispatch('auth.login')",
      "B": "dispatch('auth/login')",
      "C": "dispatch('login', { module: 'auth' })",
      "D": "auth.dispatch('login')"
    },
    "answer": "B"
  },
  {
    "question": "In a namespaced module, how does an action commit a mutation to the global root store?",
    "options": {
      "A": "commit('mutationName', null, { root: true })",
      "B": "commit('root/mutationName')",
      "C": "rootCommit('mutationName')",
      "D": "It is not possible"
    },
    "answer": "A"
  },
  {
    "question": "What does 'mapState' return when used in a component?",
    "options": {
      "A": "A single function",
      "B": "An object containing computed getter functions",
      "C": "A promise",
      "D": "A list of strings"
    },
    "answer": "B"
  },
  {
    "question": "Which property in the module allows access to the parent state from a getter?",
    "options": {
      "A": "parentState",
      "B": "rootState",
      "C": "superState",
      "D": "globalState"
    },
    "answer": "B"
  },
  {
    "question": "How can you register a module after the store has already been created?",
    "options": {
      "A": "store.addModule()",
      "B": "store.registerModule()",
      "C": "store.injectModule()",
      "D": "You cannot register modules dynamically"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Strict Mode' in Vuex?",
    "options": {
      "A": "A mode that prevents the app from running",
      "B": "A development tool that throws an error if state is mutated outside of mutation handlers",
      "C": "A mode that forces all variable names to be uppercase",
      "D": "A production-only optimization"
    },
    "answer": "B"
  },
  {
    "question": "Should you enable 'Strict Mode' in production?",
    "options": {
      "A": "Yes, to ensure data integrity",
      "B": "No, because it performs a deep watch on the state tree and can impact performance",
      "C": "Only if using a slow server",
      "D": "Strict mode only works in production"
    },
    "answer": "B"
  },
  {
    "question": "Which Vuex feature is best for filtering a list of items based on a search query?",
    "options": {
      "A": "Mutations",
      "B": "Getters",
      "C": "Actions",
      "D": "Strict Mode"
    },
    "answer": "B"
  },
  {
    "question": "Can a Getter receive arguments from a component?",
    "options": {
      "A": "No, they are read-only",
      "B": "Yes, by returning a function from the getter",
      "C": "Only if namespaced",
      "D": "Only via a payload object"
    },
    "answer": "B"
  },
  {
    "question": "What is 'State Hydration'?",
    "options": {
      "A": "Cleaning up the state",
      "B": "The process of filling the store with state from a server-side rendered (SSR) application",
      "C": "Increasing the memory usage",
      "D": "Syncing state with a database"
    },
    "answer": "B"
  },
  {
    "question": "Which function is used to initialize Vuex in a Vue 3 application?",
    "options": {
      "A": "new Vuex.Store()",
      "B": "createStore()",
      "C": "initStore()",
      "D": "Vue.use(Store)"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'mapGetters'?",
    "options": {
      "A": "To create new getters in a component",
      "B": "To map store getters to local computed properties",
      "C": "To log getter results",
      "D": "To delete getters"
    },
    "answer": "B"
  },
  {
    "question": "What happens if you mutate state directly in a component while using Vuex?",
    "options": {
      "A": "Vuex blocks the change",
      "B": "The change will work locally but will not be tracked by devtools, leading to unpredictable bugs",
      "C": "The component is destroyed",
      "D": "The API is automatically called"
    },
    "answer": "B"
  },
  {
    "question": "In a Getter, what is the 'getters' (second) argument used for?",
    "options": {
      "A": "To access the state",
      "B": "To access other getters in the store",
      "C": "To access the component",
      "D": "To change the state"
    },
    "answer": "B"
  },
  {
    "question": "How do you access a namespaced state using 'mapState'?",
    "options": {
      "A": "mapState('moduleName', ['property'])",
      "B": "mapState(['moduleName.property'])",
      "C": "mapState({ property: 'moduleName/property' })",
      "D": "Both A and C"
    },
    "answer": "D"
  },
  {
    "question": "What is 'Time-Travel Debugging'?",
    "options": {
      "A": "Running the app on an older browser",
      "B": "The ability to jump back and forth between mutation states in DevTools to find bugs",
      "C": "Scheduling actions for the future",
      "D": "Deleting the Git history"
    },
    "answer": "B"
  },
  {
    "question": "Can Vuex be used with the Composition API in Vue 3?",
    "options": {
      "A": "No, it only works with Options API",
      "B": "Yes, by using the 'useStore' function",
      "C": "Only with a separate plugin",
      "D": "Only in the setup() function"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Module Decoration'?",
    "options": {
      "A": "Adding CSS to a module",
      "B": "A pattern used in TypeScript to define Vuex modules using classes and decorators",
      "C": "Renaming a module",
      "D": "Deleting a module"
    },
    "answer": "B"
  },
  {
    "question": "What does the helper 'mapMutations' simplify?",
    "options": {
      "A": "Commiting mutations without using this.$store.commit",
      "B": "Creating new mutations",
      "C": "Mapping actions to mutations",
      "D": "Validating payloads"
    },
    "answer": "A"
  },
  {
    "question": "When should you NOT use Vuex?",
    "options": {
      "A": "In large enterprise apps",
      "B": "In very simple, small applications where prop drilling is manageable",
      "C": "When using TypeScript",
      "D": "When building a mobile app"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Plugin' system in Vuex used for?",
    "options": {
      "A": "To add new components",
      "B": "To hook into mutations for tasks like persistence, logging, or sync",
      "C": "To change the theme",
      "D": "To speed up the network"
    },
    "answer": "B"
  },
  {
    "question": "How do you subscribe to every mutation in a Vuex plugin?",
    "options": {
      "A": "store.onMutation()",
      "B": "store.subscribe()",
      "C": "store.listen()",
      "D": "store.watch()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Hot Reloading' in Vuex?",
    "options": {
      "A": "Restarting the server",
      "B": "Updating the actions and mutations in a running app without losing the current state",
      "C": "Changing the state manually",
      "D": "Deleting the cache"
    },
    "answer": "B"
  },
  {
    "question": "In a namespaced module action, what does 'rootState' refer to?",
    "options": {
      "A": "The state of the current module",
      "B": "The state of the entire store (including all modules)",
      "C": "The state of the parent module",
      "D": "The state of the DOM"
    },
    "answer": "B"
  },
  {
    "question": "Which Vuex feature allows you to react to store changes from outside the Vue instance?",
    "options": {
      "A": "store.commit",
      "B": "store.subscribe",
      "C": "store.dispatch",
      "D": "store.getters"
    },
    "answer": "B"
  },
  {
    "question": "What is the result of using the spread operator with mapState in a component?",
    "options": {
      "A": "It merges the store state into the component's local data",
      "B": "It merges the mapped state properties into the component's computed properties",
      "C": "It creates a copy of the store",
      "D": "It deletes local computed properties"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'action destructuring' in Vuex?",
    "options": {
      "A": "To delete an action",
      "B": "To access specific properties like commit or state from the context object directly",
      "C": "To combine multiple actions into one",
      "D": "To speed up JavaScript execution"
    },
    "answer": "B"
  },
  {
    "question": "In Vue 3, how do you access the Vuex store inside the 'setup' function?",
    "options": {
      "A": "this.$store",
      "B": "useStore()",
      "C": "inject('store')",
      "D": "getStore()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'State Persistence' in a Vuex context?",
    "options": {
      "A": "Making the state read-only",
      "B": "Saving the store's state to local storage or cookies so it survives a page refresh",
      "C": "Increasing the size of the state",
      "D": "Moving the state to a global variable"
    },
    "answer": "B"
  },
  {
    "question": "Which argument does a Vuex Plugin receive?",
    "options": {
      "A": "The Vue instance",
      "B": "The Store instance",
      "C": "The Router instance",
      "D": "The Axios instance"
    },
    "answer": "B"
  },
  {
    "question": "What happens to the Vuex state when the browser page is manually refreshed?",
    "options": {
      "A": "It remains unchanged",
      "B": "It is reset to its initial state",
      "C": "It is saved to the server",
      "D": "It becomes undefined"
    },
    "answer": "B"
  },
  {
    "question": "How do you define a Getter that filters state based on a dynamic ID?",
    "options": {
      "A": "By returning a function from the getter that accepts the ID",
      "B": "By passing the ID to store.commit",
      "C": "By using a global variable",
      "D": "Getters cannot take dynamic IDs"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'Flux' pattern's core rule regarding state updates?",
    "options": {
      "A": "State is updated by any component",
      "B": "State is read-only and can only be modified via specific, dispatched actions/mutations",
      "C": "State is stored in the DOM",
      "D": "State is managed by CSS"
    },
    "answer": "B"
  },
  {
    "question": "In a large app, what is the best way to avoid naming collisions in the store?",
    "options": {
      "A": "Using longer variable names",
      "B": "Using Namespaced Modules",
      "C": "Creating multiple stores",
      "D": "Using local state only"
    },
    "answer": "B"
  },
  {
    "question": "Which of these is a popular plugin for Vuex state persistence?",
    "options": {
      "A": "vuex-persistedstate",
      "B": "vue-router",
      "C": "vuex-logger",
      "D": "axios"
    },
    "answer": "A"
  },
  {
    "question": "Can you use Vuex to manage state for a non-Vue application?",
    "options": {
      "A": "No, it is strictly for Vue",
      "B": "Yes, it is a standalone state management library",
      "C": "Only if using React",
      "D": "Only with a Chrome extension"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary difference between mapState and mapGetters?",
    "options": {
      "A": "mapState is faster",
      "B": "mapState maps raw data, while mapGetters maps computed/derived data",
      "C": "mapGetters is for mutations",
      "D": "mapState is only for Vue 2"
    },
    "answer": "B"
  },
  {
    "question": "What is 'strict: true' used for in the store configuration?",
    "options": {
      "A": "To prevent the use of actions",
      "B": "To ensure that state is only mutated through mutation handlers",
      "C": "To force the use of TypeScript",
      "D": "To encrypt the state"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'rootContext' in a namespaced module action?",
    "options": {
      "A": "Access to the HTML root",
      "B": "Access to the global store's state and getters from within the module",
      "C": "The root URL of the API",
      "D": "A way to delete the store"
    },
    "answer": "B"
  },
  {
    "question": "When should you commit a mutation: before or after an async API call?",
    "options": {
      "A": "Before, to show a loading state",
      "B": "After, to update the state with the returned data",
      "C": "Both, if tracking loading and success states",
      "D": "Mutations are not used with API calls"
    },
    "answer": "C"
  },
  {
    "question": "In Vuex 4, what is the recommended way to create a store instance?",
    "options": {
      "A": "new Vuex.Store({})",
      "B": "createStore({})",
      "C": "Vue.use(Vuex)",
      "D": "initVuex()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Module Hot Reloading' helpful for?",
    "options": {
      "A": "Speeding up the browser",
      "B": "Allowing developers to swap out modules without refreshing the page and losing state",
      "C": "Connecting to a local server",
      "D": "Clearing the cache"
    },
    "answer": "B"
  },
  {
    "question": "Does Vuex support 'Time-Travel' for asynchronous actions?",
    "options": {
      "A": "Yes, natively",
      "B": "No, it only tracks the synchronous mutations that result from the actions",
      "C": "Only with Pinia",
      "D": "Only in production"
    },
    "answer": "B"
  },
  {
    "question": "What does 'store.unregisterModule' do?",
    "options": {
      "A": "Deletes the entire store",
      "B": "Dynamically removes a module from the store at runtime",
      "C": "Logs the user out",
      "D": "Hides a module from DevTools"
    },
    "answer": "B"
  },
  {
    "question": "Is it possible to have nested modules in Vuex?",
    "options": {
      "A": "No, they must be flat",
      "B": "Yes, modules can contain other modules",
      "C": "Only in Vuex 2",
      "D": "Only with a plugin"
    },
    "answer": "B"
  },
  {
    "question": "In the Action context, what is 'dispatch' used for?",
    "options": {
      "A": "To call a mutation",
      "B": "To trigger another action (local or global)",
      "C": "To update a getter",
      "D": "To refresh the page"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'payload' in a mutation?",
    "options": {
      "A": "The name of the mutation",
      "B": "The data passed to the mutation to update the state",
      "C": "The previous state",
      "D": "An error message"
    },
    "answer": "B"
  },
  {
    "question": "Why use 'mapActions' instead of 'this.$store.dispatch'?",
    "options": {
      "A": "It is faster for the computer",
      "B": "It makes the code cleaner and more readable by reducing boilerplate",
      "C": "It is required for async actions",
      "D": "It is the only way to use actions in Vue 3"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Global Namespace' in Vuex?",
    "options": {
      "A": "The window object",
      "B": "The default state where all actions/mutations are registered if namespacing is off",
      "C": "The API endpoint",
      "D": "A list of global CSS variables"
    },
    "answer": "B"
  },
  {
    "question": "In a namespaced module, how do you map a state named 'count'?",
    "options": {
      "A": "mapState(['auth/count'])",
      "B": "mapState('auth', ['count'])",
      "C": "mapState('auth.count')",
      "D": "Both A and B"
    },
    "answer": "D"
  },
  {
    "question": "Which Vue directive is commonly used with Vuex state for two-way binding?",
    "options": {
      "A": "v-for",
      "B": "v-model (with a setter/getter computed property)",
      "C": "v-if",
      "D": "v-bind"
    },
    "answer": "B"
  },
  {
    "question": "How do you handle multiple mutations in a single 'mapMutations' call?",
    "options": {
      "A": "Pass an array of mutation names",
      "B": "Call the function multiple times",
      "C": "It is not possible",
      "D": "Use a switch statement"
    },
    "answer": "A"
  },
  {
    "question": "What is 'store.hasModule' used for?",
    "options": {
      "A": "To check if a module is currently registered in the store",
      "B": "To count the number of modules",
      "C": "To check if the user is logged in",
      "D": "To check for updates"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'Mutation Tree'?",
    "options": {
      "A": "A visual chart of all mutations",
      "B": "The object in a module containing all the mutation handler functions",
      "C": "A way to delete mutations",
      "D": "A TypeScript interface"
    },
    "answer": "B"
  },
  {
    "question": "Does Vuex 4 support 'Hot Module Replacement' (HMR)?",
    "options": {
      "A": "No",
      "B": "Yes, using the 'store.hotUpdate' method",
      "C": "Only with Webpack",
      "D": "Only with Vite"
    },
    "answer": "B"
  },
  {
    "question": "What happens if a mutation is called with no payload?",
    "options": {
      "A": "The app crashes",
      "B": "The payload argument in the handler becomes undefined",
      "C": "The state is reset",
      "D": "The previous payload is used"
    },
    "answer": "B"
  },
  {
    "question": "Can you use a Getter as a property in another Getter?",
    "options": {
      "A": "No",
      "B": "Yes, it is passed as the second argument (getters)",
      "C": "Only if they are in the same file",
      "D": "Only in namespaced modules"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'createLogger' function?",
    "options": {
      "A": "A tool to create custom error logs",
      "B": "An export from 'vuex/dist/logger' that creates a console-logging plugin",
      "C": "A way to track API calls",
      "D": "A security feature"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary benefit of the 'Unidirectional Data Flow'?",
    "options": {
      "A": "Faster rendering",
      "B": "Easier to trace the source of state changes and debug the application",
      "C": "Support for multiple languages",
      "D": "Reduced CSS code"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Vuex Module Reuse'?",
    "options": {
      "A": "Copy-pasting code",
      "B": "Using a function to create a module object to avoid state sharing between instances",
      "C": "Using the same module for different Vue versions",
      "D": "There is no such thing"
    },
    "answer": "B"
  },
  {
    "question": "How do you access 'Getters' inside a component without a helper?",
    "options": {
      "A": "this.$store.state.getters",
      "B": "this.$store.getters",
      "C": "this.$getters",
      "D": "this.$store.fetch()"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Base Store'?",
    "options": {
      "A": "The root store instance",
      "B": "A store without modules",
      "C": "A store for CSS variables",
      "D": "The API server"
    },
    "answer": "A"
  },
  {
    "question": "Can an action dispatch to a different module's action?",
    "options": {
      "A": "No",
      "B": "Yes, by providing the full path and '{ root: true }' in the dispatch",
      "C": "Only if they share a parent",
      "D": "Only in strict mode"
    },
    "answer": "B"
  },
  {
    "question": "What does 'mapActions({ localName: 'storeName' })' do?",
    "options": {
      "A": "Renames a store action to a local method name",
      "B": "Creates a copy of an action",
      "C": "Deletes the store action",
      "D": "Maps an action to a getter"
    },
    "answer": "A"
  },
  {
    "question": "Which tool provides the 'Vuex' tab for state inspection?",
    "options": {
      "A": "Chrome Task Manager",
      "B": "Vue DevTools",
      "C": "Visual Studio Code",
      "D": "Postman"
    },
    "answer": "B"
  },
  {
    "question": "What is 'State Tree'?",
    "options": {
      "A": "A list of components",
      "B": "The single object that contains the entire application state",
      "C": "A file structure",
      "D": "A type of UI layout"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Module namespacing' intended to solve?",
    "options": {
      "A": "Slow performance",
      "B": "Namespace clashes where two modules use the same action/mutation names",
      "C": "API authentication issues",
      "D": "CSS conflicts"
    },
    "answer": "B"
  },
  {
    "question": "How do you map namespaced getters in a component?",
    "options": {
      "A": "mapGetters('module', ['getter'])",
      "B": "mapGetters(['module/getter'])",
      "C": "mapGetters({ g: 'module/getter' })",
      "D": "All of the above"
    },
    "answer": "D"
  },
  {
    "question": "Can you use a Vuex mutation to fetch data from an API?",
    "options": {
      "A": "Yes",
      "B": "No, mutations must be synchronous; API calls go in Actions",
      "C": "Only if the API is local",
      "D": "Only in Vue 2"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'rootContext' for?",
    "options": {
      "A": "To call mutations in the current module",
      "B": "To access global store properties from within a namespaced module action",
      "C": "To restart the app",
      "D": "To clear the cache"
    },
    "answer": "B"
  },
  {
    "question": "What does 'createStore' replace from Vuex 3?",
    "options": {
      "A": "Vue.use(Vuex)",
      "B": "new Vuex.Store({})",
      "C": "mapState",
      "D": "The whole library"
    },
    "answer": "B"
  },
  {
    "question": "What is 'store.subscribeAction'?",
    "options": {
      "A": "A way to watch when actions are triggered (before or after they execute)",
      "B": "A way to delete actions",
      "C": "A way to map actions to getters",
      "D": "A way to run actions in the background"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'SSOT' principle in Vuex?",
    "options": {
      "A": "Single Stream of Truth",
      "B": "Single Source of Truth (one store for one app)",
      "C": "Synchronous System of Tasks",
      "D": "Shared Server of Tools"
    },
    "answer": "B"
  },
  {
    "question": "In a non-namespaced store, can multiple modules respond to the same mutation?",
    "options": {
      "A": "No",
      "B": "Yes, all modules with that mutation name will be triggered",
      "C": "Only the first module registered",
      "D": "Only the root module"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary reason for moving from Vuex to Pinia in Vue 3?",
    "options": {
      "A": "Vuex is no longer functional",
      "B": "Pinia offers a simpler API, better TypeScript support, and removes the need for mutations",
      "C": "Pinia is made by a different company",
      "D": "Vuex does not support the Composition API"
    },
    "answer": "B"
  },
  {
    "question": "In a TypeScript-based Vuex store, what is an 'Injection Key' used for?",
    "options": {
      "A": "To encrypt the store data",
      "B": "To provide type safety when using useStore() in components",
      "C": "To bypass the mutation requirement",
      "D": "To connect to an external database"
    },
    "answer": "B"
  },
  {
    "question": "How do you test a Vuex Mutation in isolation?",
    "options": {
      "A": "By launching the browser and clicking buttons",
      "B": "By exporting the mutation and calling it as a plain JavaScript function with a mock state",
      "C": "Mutations cannot be tested",
      "D": "By using the Vue Router"
    },
    "answer": "B"
  },
  {
    "question": "What is the benefit of 'Action Context' typing in TypeScript?",
    "options": {
      "A": "It makes the code run faster",
      "B": "It provides autocompletion for commit and dispatch within an action",
      "C": "It changes the background color of the editor",
      "D": "It is not possible to type the context"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'store.hotUpdate' method do?",
    "options": {
      "A": "Restarts the server",
      "B": "Replaces actions and mutations without refreshing the page during development",
      "C": "Updates the user's browser version",
      "D": "Clears the local storage"
    },
    "answer": "B"
  },
  {
    "question": "In Vuex 4, how can you define a global type for 'this.$store' in Options API?",
    "options": {
      "A": "By editing the Vue source code",
      "B": "By using TypeScript's module augmentation on '@vue/runtime-core'",
      "C": "It is done automatically",
      "D": "By using a CSS file"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Vuex Persistence' usually implemented with?",
    "options": {
      "A": "A store.subscribe() listener that writes to localStorage",
      "B": "A special HTML tag",
      "C": "An API call in every component",
      "D": "A database driver"
    },
    "answer": "A"
  },
  {
    "question": "Which testing library is commonly used to test Vue components with a Vuex store?",
    "options": {
      "A": "Cypress",
      "B": "Vue Test Utils",
      "C": "Postman",
      "D": "Bootstrap"
    },
    "answer": "B"
  },
  {
    "question": "When testing an Action, what should you typically 'mock'?",
    "options": {
      "A": "The browser",
      "B": "The commit and dispatch methods, and any external API calls",
      "C": "The CSS styles",
      "D": "The hardware"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'createLogger' option 'collapsed' used for?",
    "options": {
      "A": "To hide the store entirely",
      "B": "To automatically collapse the logged mutation details in the console",
      "C": "To reduce the file size of the app",
      "D": "To stop the app from running"
    },
    "answer": "B"
  },
  {
    "question": "In a namespaced module, how do you access a root action from a local action?",
    "options": {
      "A": "dispatch('actionName', null, { root: true })",
      "B": "dispatch('/actionName')",
      "C": "rootDispatch('actionName')",
      "D": "It is impossible"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Deep Watching' in the context of Vuex Strict Mode?",
    "options": {
      "A": "Watching the developer through the webcam",
      "B": "Recursively monitoring all properties in the state tree for illegal mutations",
      "C": "Searching for bugs in the API",
      "D": "A way to speed up the app"
    },
    "answer": "B"
  },
  {
    "question": "Can Vuex 4 be used with Vue 2?",
    "options": {
      "A": "Yes, perfectly",
      "B": "No, Vuex 4 is designed specifically for the Vue 3 plugin API",
      "C": "Only with a shim",
      "D": "Only in production"
    },
    "answer": "B"
  },
  {
    "question": "What is the recommended file name for the main Vuex file?",
    "options": {
      "A": "state.js",
      "B": "index.js (inside a store folder)",
      "C": "vuex.js",
      "D": "main.js"
    },
    "answer": "B"
  },
  {
    "question": "What does 'mapGetters' do if you pass an object instead of an array?",
    "options": {
      "A": "It fails",
      "B": "It allows you to give local aliases to the store getters",
      "C": "It creates a nested store",
      "D": "It deletes the getters"
    },
    "answer": "B"
  },
  {
    "question": "How do you provide a mock store to a component in Vue Test Utils?",
    "options": {
      "A": "By setting a global variable",
      "B": "Using the 'global.plugins' option in the mount function",
      "C": "By editing the component's code",
      "D": "By using a real API"
    },
    "answer": "B"
  },
  {
    "question": "What is the risk of using 'this.$store.state' directly in a v-model?",
    "options": {
      "A": "It will cause an infinite loop",
      "B": "It will attempt to mutate state outside of a mutation handler, which fails in strict mode",
      "C": "It is not allowed by HTML",
      "D": "It slows down the keyboard"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'State' return type in a TypeScript store definition?",
    "options": {
      "A": "A string",
      "B": "An interface or type representing the shape of the store's data",
      "C": "An array of numbers",
      "D": "Any"
    },
    "answer": "B"
  },
  {
    "question": "What happens if you use a mutation name that doesn't exist?",
    "options": {
      "A": "Vuex ignores it silently",
      "B": "Vuex logs a warning (in development) that the mutation type is unknown",
      "C": "The computer restarts",
      "D": "The API is called automatically"
    },
    "answer": "B"
  },
  {
    "question": "Can an action return a boolean value?",
    "options": {
      "A": "No, only objects",
      "B": "Yes, actions can return any value, which will be wrapped in a Promise",
      "C": "Only if it is not async",
      "D": "Only in strict mode"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Vuex 5' commonly referred to as in the community?",
    "options": {
      "A": "Vuex Pro",
      "B": "Pinia (as it fulfills the design goals of Vuex 5)",
      "C": "VueStore",
      "D": "Legacy Vuex"
    },
    "answer": "B"
  },
  {
    "question": "How do you access the 'commit' function in a setup() block without useStore()?",
    "options": {
      "A": "You can't; useStore() is the standard way",
      "B": "By importing commit from 'vuex'",
      "C": "By using window.commit",
      "D": "By using a ref"
    },
    "answer": "A"
  },
  {
    "question": "What is the best way to handle 'Loading' and 'Error' states for a specific API call?",
    "options": {
      "A": "Inside the component only",
      "B": "By dedicating state properties (e.g., status: 'loading' | 'success' | 'error') in the store",
      "C": "Using browser alerts",
      "D": "By crashing the app"
    },
    "answer": "B"
  },
  {
    "question": "What is 'vuex-module-decorators'?",
    "options": {
      "A": "A tool to add icons to modules",
      "B": "A library for writing Vuex modules in a class-based style with TypeScript",
      "C": "A way to delete modules",
      "D": "A CSS framework"
    },
    "answer": "B"
  },
  {
    "question": "What does 'store.subscribeAction''s 'before' hook allow?",
    "options": {
      "A": "Changing the action code",
      "B": "Running logic just before an action is dispatched, useful for analytics or logging",
      "C": "Stopping the action from running",
      "D": "Deleting the state"
    },
    "answer": "B"
  },
  {
    "question": "Is it recommended to put large, non-reactive objects in the Vuex state?",
    "options": {
      "A": "Yes, it is the best place for all data",
      "B": "No, it can cause significant performance overhead because Vue will try to make them reactive",
      "C": "Only if the object is frozen",
      "D": "Only in production"
    },
    "answer": "B"
  },
  {
    "question": "How do you 'reset' a store state to its initial values?",
    "options": {
      "A": "store.reset()",
      "B": "By committing a mutation that re-assigns the state to its initial object",
      "C": "By refreshing the page",
      "D": "By deleting the store file"
    },
    "answer": "B"
  },
  {
    "question": "In TypeScript, what is 'RootState' typically used for?",
    "options": {
      "A": "To define the state of the root module",
      "B": "To provide a type for the entire store's state tree, including modules",
      "C": "To define the HTML root",
      "D": "To manage the API root URL"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Circular Dependency' in Vuex modules?",
    "options": {
      "A": "A module that calls itself",
      "B": "When two modules import each other, which can lead to undefined state during initialization",
      "C": "A module that is round in shape",
      "D": "A loop in a getter"
    },
    "answer": "B"
  },
  {
    "question": "Can you use Vuex with the 'script setup' syntax?",
    "options": {
      "A": "No",
      "B": "Yes, using the useStore hook",
      "C": "Only with mapState",
      "D": "Only with a separate script block"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Object.freeze()' on data before putting it in Vuex?",
    "options": {
      "A": "To prevent the app from changing",
      "B": "To prevent Vue from making the data reactive, improving performance for large read-only lists",
      "C": "To save memory",
      "D": "To encrypt the data"
    },
    "answer": "B"
  },
  {
    "question": "How do you provide the Vuex store to a 'Teleport' component?",
    "options": {
      "A": "You don't need to; it's globally available via this.$store or useStore",
      "B": "By passing it as a prop",
      "C": "By using a portal",
      "D": "Teleport components cannot access Vuex"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Vuex-ORM'?",
    "options": {
      "A": "A tool for managing the office",
      "B": "A plugin that allows you to manage Vuex state as if it were a relational database",
      "C": "A type of CSS animation",
      "D": "A server-side framework"
    },
    "answer": "B"
  },
  {
    "question": "What is 'State Snapshotting'?",
    "options": {
      "A": "Taking a photo of the code",
      "B": "Capturing the state at a specific point in time, often for debugging or error reporting",
      "C": "Deleting the state",
      "D": "Updating the state"
    },
    "answer": "B"
  },
  {
    "question": "Which Vue lifecycle hook is best for dispatching an initial 'fetchData' action?",
    "options": {
      "A": "beforeCreate",
      "B": "created (or onMounted in Composition API)",
      "C": "updated",
      "D": "destroyed"
    },
    "answer": "B"
  },
  {
    "question": "Can you use 'v-model' directly on a Vuex state property?",
    "options": {
      "A": "Yes, always",
      "B": "No, it violates the one-way data flow; you must use a getter/setter computed property",
      "C": "Only if strict mode is off",
      "D": "Only for strings"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Getter memoization'?",
    "options": {
      "A": "Deleting a getter",
      "B": "The fact that getters are cached based on their dependencies and only re-evaluate when a dependency changes",
      "C": "Writing getters in a specific font",
      "D": "A way to hide getters"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Module auto-registration'?",
    "options": {
      "A": "A built-in feature of Vuex",
      "B": "A common pattern using Webpack or Vite to automatically import and register modules from a folder",
      "C": "A security risk",
      "D": "A way to make the store slower"
    },
    "answer": "B"
  },
  {
    "question": "How do you access the 'rootState' from a module's Mutation?",
    "options": {
      "A": "It is passed as the third argument",
      "B": "Mutations do not have access to rootState; they only affect the local state",
      "C": "Via context.rootState",
      "D": "Via window.state"
    },
    "answer": "B"
  },
  {
    "question": "What is 'store.watch' primarily used for?",
    "options": {
      "A": "To keep the screen on",
      "B": "To reactively watch a specific piece of state or a getter and run a callback when it changes",
      "C": "To check the time",
      "D": "To monitor the CPU"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'unwatch' function returned by store.watch do?",
    "options": {
      "A": "Deletes the state",
      "B": "Stops the watch listener and cleans up memory",
      "C": "Hides the store",
      "D": "Restarts the listener"
    },
    "answer": "B"
  },
  {
    "question": "In a TypeScript project, where should you define your store interfaces?",
    "options": {
      "A": "In a separate 'types.ts' file for better organization",
      "B": "Inside the HTML",
      "C": "In the CSS",
      "D": "They are not needed"
    },
    "answer": "A"
  },
  {
    "question": "What is the role of 'MapState' with an object argument in TypeScript?",
    "options": {
      "A": "It provides no benefit",
      "B": "It allows you to map state to custom local names, but typing can be difficult",
      "C": "It is the only way to use TypeScript",
      "D": "It deletes the state"
    },
    "answer": "B"
  },
  {
    "question": "What happens if you define the same module name twice?",
    "options": {
      "A": "They merge",
      "B": "The second one overwrites the first",
      "C": "Vuex throws an error",
      "D": "Both are ignored"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Action Dispatcher'?",
    "options": {
      "A": "The $store.dispatch method",
      "B": "A separate library",
      "C": "A person who writes code",
      "D": "The API server"
    },
    "answer": "A"
  },
  {
    "question": "Can you use Vuex to share state across multiple browser tabs?",
    "options": {
      "A": "No",
      "B": "Yes, but you need an additional plugin like 'vuex-shared-mutations' using BroadcastChannel or localStorage events",
      "C": "Yes, it is built-in",
      "D": "Only in Chrome"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Hydration' in a Vuex context?",
    "options": {
      "A": "Cleaning the code",
      "B": "Synchronizing the client-side store with the state sent from the server in SSR",
      "C": "Adding more data",
      "D": "Increasing performance"
    },
    "answer": "B"
  },
  {
    "question": "Which command is used to install Vuex 4 via npm?",
    "options": {
      "A": "npm install vuex",
      "B": "npm install vuex@next",
      "C": "npm install store",
      "D": "npm install vue-store"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Vuex-Reset'?",
    "options": {
      "A": "A button in the browser",
      "B": "A common plugin or utility function to clear the store back to its initial state",
      "C": "A way to delete the app",
      "D": "A CSS property"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'final' advice for Vuex users in 2026?",
    "options": {
      "A": "Keep using Vuex 2",
      "B": "Stick with Vuex 4 for legacy apps, but choose Pinia for all new projects",
      "C": "Delete the store",
      "D": "Move to jQuery"
    },
    "answer": "B"
  },
  {
    "question": "Which Vuex feature should be used to avoid deep-watching the state in production for performance?",
    "options": {
      "A": "Namespacing",
      "B": "Strict Mode (set to false)",
      "C": "Action Composition",
      "D": "Module Decoration"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary reason 'Mutations' were removed in Pinia (the successor to Vuex)?",
    "options": {
      "A": "They were too fast",
      "B": "To reduce boilerplate and simplify the flow by letting Actions handle state changes",
      "C": "They didn't support CSS",
      "D": "They were incompatible with HTML5"
    },
    "answer": "B"
  },
  {
    "question": "In the context of 'mapState', can you use an arrow function to access local component data?",
    "options": {
      "A": "Yes, always",
      "B": "No, because 'this' will not be bound to the component instance",
      "C": "Only in Vue 2",
      "D": "Only if the store is global"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'store.hotUpdate' method specifically target for replacement?",
    "options": {
      "A": "The browser cache",
      "B": "Actions, Mutations, and Getters",
      "C": "The API endpoint",
      "D": "The HTML template"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Vuex-Persist' intended to solve?",
    "options": {
      "A": "High CPU usage",
      "B": "Data loss upon browser refresh by syncing state with localStorage",
      "C": "Slow API responses",
      "D": "CSS style conflicts"
    },
    "answer": "B"
  },
  {
    "question": "In a TypeScript Vuex store, what does 'InjectionKey' ensure?",
    "options": {
      "A": "Data encryption",
      "B": "Type safety when calling useStore()",
      "C": "Automated login",
      "D": "Faster builds"
    },
    "answer": "B"
  },
  {
    "question": "How do you check if a specific module is already registered in a dynamic Vuex store?",
    "options": {
      "A": "store.exists()",
      "B": "store.hasModule('moduleName')",
      "C": "store.check()",
      "D": "store.find()"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'rootContext' object in an Action mainly used for?",
    "options": {
      "A": "To restart the app",
      "B": "To access global state and getters from within a namespaced module",
      "C": "To clear the console",
      "D": "To edit the index.html"
    },
    "answer": "B"
  },
  {
    "question": "Which Vuex helper is most similar to a component's 'Methods' option?",
    "options": {
      "A": "mapState",
      "B": "mapActions",
      "C": "mapGetters",
      "D": "mapProps"
    },
    "answer": "B"
  },
  {
    "question": "What is the default return value of 'store.dispatch'?",
    "options": {
      "A": "The new state",
      "B": "A Promise",
      "C": "An integer",
      "D": "Undefined"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Pure Mutation' in Vuex?",
    "options": {
      "A": "A mutation that affects no state",
      "B": "A mutation that only depends on its arguments and has no side effects",
      "C": "A mutation that calls an API",
      "D": "A mutation written in TypeScript"
    },
    "answer": "B"
  },
  {
    "question": "What is the role of 'createStore' in Vuex 4?",
    "options": {
      "A": "To build the CSS",
      "B": "To initialize a new Vuex store instance in a Vue 3 application",
      "C": "To create a local database",
      "D": "To manage routes"
    },
    "answer": "B"
  },
  {
    "question": "Can you use 'v-model' directly on a Vuex state property in a component?",
    "options": {
      "A": "Yes, and it is the best way",
      "B": "No, you must use a computed property with a getter and setter to commit mutations",
      "C": "Only for text inputs",
      "D": "Only if using Pinia"
    },
    "answer": "B"
  },
  {
    "question": "What happens if an Action does not return a value or a Promise?",
    "options": {
      "A": "The app crashes",
      "B": "Dispatch returns a Promise that resolves immediately",
      "C": "The state is cleared",
      "D": "The browser reloads"
    },
    "answer": "B"
  },
  {
    "question": "Which tool provides the 'Time Travel' feature for Vuex?",
    "options": {
      "A": "Visual Studio Code",
      "B": "Vue DevTools",
      "C": "Chrome Task Manager",
      "D": "Postman"
    },
    "answer": "B"
  },
  {
    "question": "What is 'State Hydration'?",
    "options": {
      "A": "Adding comments to the state",
      "B": "Populating the client-side store with state data sent from the server in SSR",
      "C": "Deleting old state data",
      "D": "Encrypting the store"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'mapGetters' in the Options API?",
    "options": {
      "A": "To change state",
      "B": "To expose store getters as computed properties in the component",
      "C": "To create new actions",
      "D": "To validate data"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Module Decoration'?",
    "options": {
      "A": "Adding icons to files",
      "B": "A TypeScript pattern for defining Vuex modules using classes",
      "C": "Applying CSS to the store",
      "D": "Hiding modules from users"
    },
    "answer": "B"
  },
  {
    "question": "In a namespaced module, how do you specify a global mutation?",
    "options": {
      "A": "By setting { global: true }",
      "B": "By setting { root: true } in the commit call",
      "C": "By prefixing the name with 'root/'",
      "D": "Global mutations are not allowed"
    },
    "answer": "B"
  },
  {
    "question": "Which function is used to access the store in the Vue 3 Composition API?",
    "options": {
      "A": "getStore()",
      "B": "useStore()",
      "C": "injectStore()",
      "D": "this.$store"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Getter Memoization'?",
    "options": {
      "A": "Deleting a getter after use",
      "B": "Caching the result of a getter until its dependencies change",
      "C": "Naming a getter after a memory",
      "D": "Translating a getter"
    },
    "answer": "B"
  },
  {
    "question": "What happens to the Vuex store if 'strict' mode is enabled and you mutate state directly?",
    "options": {
      "A": "The mutation is ignored",
      "B": "An error is thrown stating state cannot be mutated outside mutation handlers",
      "C": "The app works fine but slowly",
      "D": "The data is automatically saved"
    },
    "answer": "B"
  },
  {
    "question": "What is 'vuex-shared-mutations' used for?",
    "options": {
      "A": "Sharing code with React",
      "B": "Syncing Vuex state across multiple browser tabs",
      "C": "Sharing state with the server",
      "D": "Compressing state data"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'store.subscribeAction' method?",
    "options": {
      "A": "To create a new action",
      "B": "To subscribe to action dispatches, allowing you to run code before or after an action executes",
      "C": "To delete all actions",
      "D": "To map actions to a different module"
    },
    "answer": "B"
  },
  {
    "question": "In a Vuex module, what does the 'state' property need to be to ensure it can be reused multiple times without sharing state instances?",
    "options": {
      "A": "A constant object",
      "B": "A function that returns a new state object",
      "C": "A string",
      "D": "An array"
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
    skill = "Vuex"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
