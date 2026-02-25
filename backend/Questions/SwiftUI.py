from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
  {
    "question": "Which property wrapper is used to manage simple, private state that is owned by a single view?",
    "options": {
      "A": "@ObservedObject",
      "B": "@State",
      "C": "@Environment",
      "D": "@Binding"
    },
    "answer": "B"
  },
  {
    "question": "Which layout container is used to stack views horizontally?",
    "options": {
      "A": "VStack",
      "B": "HStack",
      "C": "ZStack",
      "D": "List"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary return type of the 'body' property in a SwiftUI View?",
    "options": {
      "A": "View",
      "B": "some View",
      "C": "AnyView",
      "D": "Group"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier is used to change the color of the text in a 'Text' view?",
    "options": {
      "A": ".background()",
      "B": ".foregroundColor()",
      "C": ".tint()",
      "D": ".color()"
    },
    "answer": "B"
  },
  {
    "question": "In SwiftUI, what does the '$' prefix before a state variable name signify?",
    "options": {
      "A": "A constant value",
      "B": "A projected value (Binding)",
      "C": "A private variable",
      "D": "An environment value"
    },
    "answer": "B"
  },
  {
    "question": "Which view is used to create a scrollable list of data similar to UITableView?",
    "options": {
      "A": "ScrollView",
      "B": "List",
      "C": "Form",
      "D": "ForEach"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of a 'Spacer' in a stack?",
    "options": {
      "A": "To add a fixed gap",
      "B": "To expand and fill all available space along the stack's axis",
      "C": "To create a border",
      "D": "To center the text"
    },
    "answer": "B"
  },
  {
    "question": "Which attribute is required for an object to be used with the '@StateObject' property wrapper?",
    "options": {
      "A": "Identifiable",
      "B": "ObservableObject",
      "C": "Codable",
      "D": "Equatable"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier adds a clickable action to any SwiftUI view?",
    "options": {
      "A": ".onTapGesture()",
      "B": ".onClick()",
      "C": ".press()",
      "D": ".action()"
    },
    "answer": "A"
  },
  {
    "question": "How do you apply a border to a view in SwiftUI?",
    "options": {
      "A": ".border(Color.red, width: 2)",
      "B": ".stroke(2)",
      "C": ".outline(red)",
      "D": ".padding(.border)"
    },
    "answer": "A"
  },
  {
    "question": "What is the purpose of 'ZStack'?",
    "options": {
      "A": "To stack views horizontally",
      "B": "To stack views on top of each other (depth)",
      "C": "To create a grid",
      "D": "To manage state"
    },
    "answer": "B"
  },
  {
    "question": "Which property wrapper is used to create a two-way connection between a view and a state variable owned by a parent view?",
    "options": {
      "A": "@State",
      "B": "@Binding",
      "C": "@Published",
      "D": "@Environment"
    },
    "answer": "B"
  },
  {
    "question": "Which view is used to display an image from your assets catalog?",
    "options": {
      "A": "ImageView",
      "B": "Image",
      "C": "Picture",
      "D": "Asset"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier allows an image to be resized beyond its original dimensions?",
    "options": {
      "A": ".scale()",
      "B": ".resizable()",
      "C": ".aspectRatio()",
      "D": ".frame()"
    },
    "answer": "B"
  },
  {
    "question": "What is the function of the 'Divider' view?",
    "options": {
      "A": "To perform math",
      "B": "To draw a thin line separating content",
      "C": "To create a new section",
      "D": "To split a string"
    },
    "answer": "B"
  },
  {
    "question": "Which view is used to navigate to a new screen when clicked?",
    "options": {
      "A": "NavigationButton",
      "B": "NavigationLink",
      "C": "NavigationContainer",
      "D": "Segue"
    },
    "answer": "B"
  },
  {
    "question": "What does the '@Published' attribute do inside an ObservableObject?",
    "options": {
      "A": "It saves the data to disk",
      "B": "It triggers a view update whenever the property value changes",
      "C": "It makes the property public",
      "D": "It prints the value to the console"
    },
    "answer": "B"
  },
  {
    "question": "Which container allows for a grouping of views without affecting the layout hierarchy?",
    "options": {
      "A": "VStack",
      "B": "Group",
      "C": "Section",
      "D": "Container"
    },
    "answer": "B"
  },
  {
    "question": "How do you add padding to all sides of a view?",
    "options": {
      "A": ".padding()",
      "B": ".margin()",
      "C": ".inset()",
      "D": ".space()"
    },
    "answer": "A"
  },
  {
    "question": "Which modifier is used to set the width and height of a view?",
    "options": {
      "A": ".size()",
      "B": ".frame()",
      "C": ".bounds()",
      "D": ".dimension()"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'ForEach' in SwiftUI?",
    "options": {
      "A": "To create a loop in Swift logic",
      "B": "To compute views dynamically from a collection of data",
      "C": "To search for an item",
      "D": "To filter a list"
    },
    "answer": "B"
  },
  {
    "question": "Which property wrapper is used to retrieve values like 'colorScheme' or 'dismiss' from the system?",
    "options": {
      "A": "@StateObject",
      "B": "@Environment",
      "C": "@System",
      "D": "@AppStorage"
    },
    "answer": "B"
  },
  {
    "question": "Which view displays a single-line editable text field?",
    "options": {
      "A": "Text",
      "B": "TextField",
      "C": "Editor",
      "D": "Input"
    },
    "answer": "B"
  },
  {
    "question": "How do you center text within a 'Text' view that has a large frame?",
    "options": {
      "A": ".textAlign(.center)",
      "B": ".multilineTextAlignment(.center)",
      "C": ".gravity(.center)",
      "D": ".centerText()"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Button' in SwiftUI?",
    "options": {
      "A": "To display a label only",
      "B": "To perform an action when the user triggers it",
      "C": "To navigate between apps",
      "D": "To manage dark mode"
    },
    "answer": "B"
  },
  {
    "question": "Which view provides a way to pick a date or time?",
    "options": {
      "A": "Calendar",
      "B": "DatePicker",
      "C": "TimePicker",
      "D": "Picker"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier makes a view semi-transparent?",
    "options": {
      "A": ".transparency()",
      "B": ".opacity()",
      "C": ".alpha()",
      "D": ".clear()"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Canvas' in Xcode used for?",
    "options": {
      "A": "To write code",
      "B": "To see a real-time preview of your SwiftUI views",
      "C": "To upload the app",
      "D": "To manage the database"
    },
    "answer": "B"
  },
  {
    "question": "Which view is used to create a toggle switch (On/Off)?",
    "options": {
      "A": "Switch",
      "B": "Toggle",
      "C": "CheckBox",
      "D": "Selector"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the '@main' attribute in a SwiftUI app?",
    "options": {
      "A": "To define the primary theme",
      "B": "To indicate the entry point of the application",
      "C": "To mark a view as public",
      "D": "To handle network calls"
    },
    "answer": "B"
  },
  {
    "question": "Which layout container is used to stack views vertically?",
    "options": {
      "A": "HStack",
      "B": "VStack",
      "C": "ZStack",
      "D": "DStack"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier is used to add a rounded corner to a background?",
    "options": {
      "A": ".radius()",
      "B": ".cornerRadius()",
      "C": ".round()",
      "D": ".shape()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'State' in SwiftUI?",
    "options": {
      "A": "The physical location of the user",
      "B": "A source of truth that triggers a view redraw when it changes",
      "C": "A database table",
      "D": "A network status"
    },
    "answer": "B"
  },
  {
    "question": "Which view allows users to select one option from a list of choices?",
    "options": {
      "A": "Selector",
      "B": "Picker",
      "C": "Choice",
      "D": "OptionList"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier is used to add a shadow to a view?",
    "options": {
      "A": ".elevation()",
      "B": ".shadow()",
      "C": ".glow()",
      "D": ".darken()"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Label' in SwiftUI?",
    "options": {
      "A": "To display text only",
      "B": "To display an icon and text together as a standard UI unit",
      "C": "To tag a view for search",
      "D": "To create a form field"
    },
    "answer": "B"
  },
  {
    "question": "Which property wrapper is used for an external object that is already created and passed into a view?",
    "options": {
      "A": "@State",
      "B": "@ObservedObject",
      "C": "@StateObject",
      "D": "@Environment"
    },
    "answer": "B"
  },
  {
    "question": "What is the function of '.onAppear()'?",
    "options": {
      "A": "To make a view visible",
      "B": "To run a block of code when a view is added to the screen",
      "C": "To animate a view",
      "D": "To refresh the database"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier changes the thickness of the text?",
    "options": {
      "A": ".weight()",
      "B": ".fontWeight()",
      "C": ".bold()",
      "D": "Both B and C"
    },
    "answer": "D"
  },
  {
    "question": "What is 'SF Symbols'?",
    "options": {
      "A": "A font used by Apple",
      "B": "A library of iconography designed to integrate with system fonts",
      "C": "A coding language",
      "D": "A database system"
    },
    "answer": "B"
  },
  {
    "question": "Which view provides a way to display progress to the user?",
    "options": {
      "A": "LoadingView",
      "B": "ProgressView",
      "C": "Spinner",
      "D": "ActivityView"
    },
    "answer": "B"
  },
  {
    "question": "How do you ignore the safe area (like the notch) for a background color?",
    "options": {
      "A": ".noSafe()",
      "B": ".ignoresSafeArea()",
      "C": ".expandAll()",
      "D": ".fullScreen()"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier is used to scale a view by a certain factor?",
    "options": {
      "A": ".size()",
      "B": ".scaleEffect()",
      "C": ".magnify()",
      "D": ".transform()"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'Slider' view?",
    "options": {
      "A": "To scroll through images",
      "B": "To select a value from a continuous range of values",
      "C": "To navigate between screens",
      "D": "To adjust the text font"
    },
    "answer": "B"
  },
  {
    "question": "Which view is used to display a multi-line editable text block?",
    "options": {
      "A": "TextField",
      "B": "TextEditor",
      "C": "MultiLine",
      "D": "TextBox"
    },
    "answer": "B"
  },
  {
    "question": "What is the difference between @StateObject and @ObservedObject?",
    "options": {
      "A": "@StateObject creates the object; @ObservedObject just watches it",
      "B": "@ObservedObject is for local state",
      "C": "They are identical",
      "D": "@StateObject is only for strings"
    },
    "answer": "A"
  },
  {
    "question": "Which modifier is used to add a header or footer to a Section in a List?",
    "options": {
      "A": ".header()",
      "B": "Section(header:footer:content:)",
      "C": ".addDecoration()",
      "D": ".listStyle()"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Stepper'?",
    "options": {
      "A": "To measure steps taken by the user",
      "B": "To increment or decrement a value using plus and minus buttons",
      "C": "To create a wizard flow",
      "D": "To animate a view"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier is used to set the font of a 'Text' view to a system style like 'title'?",
    "options": {
      "A": ".style(.title)",
      "B": ".font(.title)",
      "C": ".appearance(.headline)",
      "D": ".type(.body)"
    },
    "answer": "B"
  },
  {
    "question": "In SwiftUI, what is 'Declarative Syntax'?",
    "options": {
      "A": "Writing step-by-step instructions for the UI",
      "B": "Describing *what* the UI should look like for a given state",
      "C": "Using only XML",
      "D": "Writing only in objective-C"
    },
    "answer": "B"
  },
  
  {
    "question": "Which view is used to create a circular shape that fills its container?",
    "options": {
      "A": "Circle",
      "B": "Oval",
      "C": "Round()",
      "D": "Arc"
    },
    "answer": "A"
  },
  {
    "question": "Which modifier is used to fill a Shape with a specific color or gradient?",
    "options": {
      "A": ".background()",
      "B": ".fill()",
      "C": ".stroke()",
      "D": ".color()"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary difference between '.fill()' and '.stroke()' for a Shape?",
    "options": {
      "A": "Fill is for text, stroke is for images",
      "B": "Fill colors the interior; stroke colors the outline",
      "C": "Fill is faster",
      "D": "Stroke is used for shadows"
    },
    "answer": "B"
  },
  {
    "question": "Which view allows for building a grid that grows vertically as more items are added?",
    "options": {
      "A": "VGrid",
      "B": "LazyVGrid",
      "C": "List",
      "D": "GridView"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'GridItem' type in a LazyVGrid?",
    "options": {
      "A": "To store the data for a cell",
      "B": "To define the size and behavior of the grid columns (fixed, flexible, or adaptive)",
      "C": "To handle clicks on a grid item",
      "D": "To set the grid background"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier is used to add a basic linear transition animation to a view when a state change occurs?",
    "options": {
      "A": ".animate()",
      "B": ".withAnimation()",
      "C": ".animation(.linear, value: stateVariable)",
      "D": ".transition()"
    },
    "answer": "C"
  },
  {
    "question": "What is 'Implicit Animation' in SwiftUI?",
    "options": {
      "A": "An animation that never runs",
      "B": "Using the .animation() modifier directly on a view to animate its changes",
      "C": "Animations defined in a database",
      "D": "An animation that requires a manual start"
    },
    "answer": "B"
  },
  {
    "question": "Which wrapper is used to perform 'Explicit Animations' by wrapping state changes in a block?",
    "options": {
      "A": ".animation()",
      "B": "withAnimation { ... }",
      "C": "doAnimation { ... }",
      "D": "runAnimation()"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier is used to change the shape of a view's clipping area (e.g., to a Capsule)?",
    "options": {
      "A": ".mask()",
      "B": ".clipShape()",
      "C": ".shape()",
      "D": ".cornerRadius()"
    },
    "answer": "B"
  },
  {
    "question": "Which gradient type radiates from a central point?",
    "options": {
      "A": "LinearGradient",
      "B": "RadialGradient",
      "C": "AngularGradient",
      "D": "EllipticalGradient"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'Capsule' shape?",
    "options": {
      "A": "To store data",
      "B": "A rounded rectangle where the corner radius is half of the smallest side",
      "C": "To create a 3D effect",
      "D": "To manage app memory"
    },
    "answer": "B"
  },
  {
    "question": "Which gesture is triggered when a user moves a finger across a view?",
    "options": {
      "A": "TapGesture",
      "B": "DragGesture",
      "C": "LongPressGesture",
      "D": "RotationGesture"
    },
    "answer": "B"
  },
  {
    "question": "How do you detect a rotation gesture (two-finger twist) in SwiftUI?",
    "options": {
      "A": ".onRotate()",
      "B": "RotationGesture()",
      "C": "TwistGesture()",
      "D": ".gesture(Twist())"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier is used to apply a 3D rotation effect to a view?",
    "options": {
      "A": ".rotate3D()",
      "B": ".rotation3DEffect()",
      "C": ".transform3D()",
      "D": ".perspective()"
    },
    "answer": "B"
  },
  {
    "question": "What is the role of 'GeometryReader' in complex layouts?",
    "options": {
      "A": "To read text from the screen",
      "B": "To get the size and position of a view relative to its parent container",
      "C": "To draw geometric shapes",
      "D": "To handle math logic"
    },
    "answer": "B"
  },
  {
    "question": "Which view is used to group multiple items that can overlap in depth (Z-axis)?",
    "options": {
      "A": "VStack",
      "B": "ZStack",
      "C": "DepthStack",
      "D": "OverlayStack"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier adds a background view behind the current view?",
    "options": {
      "A": ".overlay()",
      "B": ".background()",
      "C": ".behind()",
      "D": ".under()"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier adds a foreground view in front of the current view?",
    "options": {
      "A": ".overlay()",
      "B": ".background()",
      "C": ".front()",
      "D": ".top()"
    },
    "answer": "A"
  },
  {
    "question": "What does the 'transition' modifier do?",
    "options": {
      "A": "Changes the color of a view",
      "B": "Defines how a view enters or leaves the screen (e.g., slide, scale, opacity)",
      "C": "Navigates to a new view",
      "D": "Converts a string to a number"
    },
    "answer": "B"
  },
  {
    "question": "Which animation curve starts slow, speeds up, and then ends slow?",
    "options": {
      "A": ".linear",
      "B": ".easeInOut",
      "C": ".easeIn",
      "D": ".easeOut"
    },
    "answer": "B"
  },
  {
    "question": "How do you apply a spring animation that feels bouncy?",
    "options": {
      "A": ".animation(.bouncy)",
      "B": ".animation(.spring())",
      "C": ".animation(.jump())",
      "D": ".animation(.elastic())"
    },
    "answer": "B"
  },
  {
    "question": "Which view is used to display a list that can be grouped into sections with headers?",
    "options": {
      "A": "List",
      "B": "Form",
      "C": "GroupedList",
      "D": "SectionList"
    },
    "answer": "A"
  },
  {
    "question": "What is 'State Persistence' in SwiftUI using @AppStorage?",
    "options": {
      "A": "Saving data to a JSON file",
      "B": "Persisting small pieces of data (like user settings) automatically to UserDefaults",
      "C": "Storing images in the cloud",
      "D": "Keeping the app active in the background"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier is used to change the style of a List (e.g., Plain, Grouped, Inset)?",
    "options": {
      "A": ".listStyle()",
      "B": ".appearance()",
      "C": ".style()",
      "D": ".formatList()"
    },
    "answer": "A"
  },
  {
    "question": "How do you hide a view visually without removing it from the layout hierarchy?",
    "options": {
      "A": ".hidden()",
      "B": ".opacity(0)",
      "C": ".invisible()",
      "D": "Both A and B"
    },
    "answer": "D"
  },
  {
    "question": "Which gesture is used to detect a user holding a finger down for a specific duration?",
    "options": {
      "A": "HoldGesture",
      "B": "LongPressGesture",
      "C": "DurationGesture",
      "D": "TimerGesture"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of '.onDelete' in a List?",
    "options": {
      "A": "To delete the whole list",
      "B": "To provide swipe-to-delete functionality for items in a ForEach loop",
      "C": "To clear the cache",
      "D": "To remove a view from the screen"
    },
    "answer": "B"
  },
  {
    "question": "Which view is used to draw custom paths and lines in SwiftUI?",
    "options": {
      "A": "Line",
      "B": "Path",
      "C": "Vector",
      "D": "Pen"
    },
    "answer": "B"
  },
  {
    "question": "How do you apply a blur effect to a view?",
    "options": {
      "A": ".glass()",
      "B": ".blur(radius: 5)",
      "C": ".focus(false)",
      "D": ".shade()"
    },
    "answer": "B"
  },
  {
    "question": "Which property wrapper is used to manage global app data that can be accessed by any child view in the environment?",
    "options": {
      "A": "@StateObject",
      "B": "@EnvironmentObject",
      "C": "@ObservedObject",
      "D": "@Binding"
    },
    "answer": "B"
  },
  {
    "question": "What does '.aspectRatio(contentMode: .fit)' do to an image?",
    "options": {
      "A": "It stretches the image to fill the frame",
      "B": "It scales the image so it fits entirely within the frame while maintaining its proportions",
      "C": "It crops the image",
      "D": "It flips the image"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier allows you to position a view at a specific (x, y) coordinate relative to its parent?",
    "options": {
      "A": ".offset()",
      "B": ".position()",
      "C": ".coord()",
      "D": ".location()"
    },
    "answer": "B"
  },
  {
    "question": "What is the difference between '.offset()' and '.position()'?",
    "options": {
      "A": "Offset moves the view relative to its original spot; position centers it on a point in the parent",
      "B": "Position is faster",
      "C": "They are the same",
      "D": "Offset only works for text"
    },
    "answer": "A"
  },
  {
    "question": "Which shape creates a rectangle with specific corner radii?",
    "options": {
      "A": "Rectangle",
      "B": "RoundedRectangle",
      "C": "CornerRect",
      "D": "Box"
    },
    "answer": "B"
  },
  {
    "question": "How do you define an animation that repeats forever?",
    "options": {
      "A": ".animation(.linear.repeatForever())",
      "B": ".animation(.infinite())",
      "C": ".loopAnimation()",
      "D": ".repeat()"
    },
    "answer": "A"
  },
  {
    "question": "Which view provides a way to visually group input controls with a label (e.g., settings screens)?",
    "options": {
      "A": "List",
      "B": "Form",
      "C": "Group",
      "D": "SettingsView"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier allows you to scale a view up or down when it is tapped?",
    "options": {
      "A": ".scaleEffect()",
      "B": ".magnificationEffect()",
      "C": ".zoom()",
      "D": ".enlarge()"
    },
    "answer": "A"
  },
  {
    "question": "What is the purpose of 'MatchedGeometryEffect'?",
    "options": {
      "A": "To calculate the volume of a shape",
      "B": "To create smooth hero-like transitions between two different views in a hierarchy",
      "C": "To align views in a grid",
      "D": "To handle geometric math"
    },
    "answer": "B"
  },
  {
    "question": "Which gradient type uses a sweep around a circle (like a radar or color wheel)?",
    "options": {
      "A": "LinearGradient",
      "B": "RadialGradient",
      "C": "AngularGradient (or Conic)",
      "D": "MeshGradient"
    },
    "answer": "C"
  },
  {
    "question": "What does the '.onMove' modifier enable in a List?",
    "options": {
      "A": "Moving the app to background",
      "B": "Drag-and-drop reordering of items within the list",
      "C": "Animating the scroll",
      "D": "Removing an item"
    },
    "answer": "B"
  },
  {
    "question": "How do you set a maximum width for a view while allowing it to grow up to that point?",
    "options": {
      "A": ".maxWidth(100)",
      "B": ".frame(maxWidth: 100)",
      "C": ".limitWidth(100)",
      "D": ".bounds(width: 100)"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier is used to rotate a view by a specific angle (e.g., Degrees or Radians)?",
    "options": {
      "A": ".rotate()",
      "B": ".rotationEffect()",
      "C": ".spin()",
      "D": ".turn()"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'ColorScheme' in SwiftUI environment?",
    "options": {
      "A": "To choose a favorite color",
      "B": "To detect if the device is in light or dark mode",
      "C": "To change the text color",
      "D": "To design a custom theme"
    },
    "answer": "B"
  },
  {
    "question": "Which view is used to display a hierarchy of data that can be expanded or collapsed?",
    "options": {
      "A": "List",
      "B": "OutlineGroup",
      "C": "TreeStack",
      "D": "HList"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier allows you to change the opacity of a background color while keeping the view content solid?",
    "options": {
      "A": ".background(Color.black.opacity(0.5))",
      "B": ".opacity(0.5)",
      "C": ".clearBackground()",
      "D": ".shadeBackground()"
    },
    "answer": "A"
  },
  {
    "question": "What does the 'ignoresSafeArea' modifier do?",
    "options": {
      "A": "Deletes the notch",
      "B": "Allows a view to extend beyond the system safe boundaries into the Status Bar or Home Indicator area",
      "C": "Locks the screen",
      "D": "Increases the tap area"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier is used to create a staggered animation for multiple views?",
    "options": {
      "A": ".stagger()",
      "B": ".animation(.default.delay())",
      "C": ".sequence()",
      "D": ".wait()"
    },
    "answer": "B"
  },
  {
    "question": "Which view provides a way to group several views into one unit so they can be styled together?",
    "options": {
      "A": "Group",
      "B": "VStack",
      "C": "ZStack",
      "D": "Collection"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Canvas' in the context of Drawing and Graphics in SwiftUI?",
    "options": {
      "A": "The Preview window",
      "B": "A view used for high-performance immediate-mode drawing of complex 2D graphics",
      "C": "A tool to draw icons",
      "D": "The main window"
    },
    "answer": "B"
  },
  {
    "question": "How do you detect a 3D touch (Pressure) or deep press in SwiftUI?",
    "options": {
      "A": "PressureGesture",
      "B": "Not natively supported; use LongPressGesture or custom interaction",
      "C": "DeepTouch()",
      "D": ".onPressure()"
    },
    "answer": "B"
  },
{
    "question": "In the MVVM pattern for SwiftUI, what is the primary responsibility of the 'ViewModel'?",
    "options": {
      "A": "To layout the UI components",
      "B": "To handle business logic and transform data into a form that the View can display",
      "C": "To store data permanently on disk",
      "D": "To manage network hardware directly"
    },
    "answer": "B"
  },
  {
    "question": "Which property wrapper is used to share an ObservableObject across many views without passing it manually through initializers?",
    "options": {
      "A": "@StateObject",
      "B": "@EnvironmentObject",
      "C": "@ObservedObject",
      "D": "@Binding"
    },
    "answer": "B"
  },
  {
    "question": "What happens if you try to use an @EnvironmentObject in a view but fail to provide it via the '.environmentObject()' modifier in a parent?",
    "options": {
      "A": "The app shows a blank screen",
      "B": "The app crashes at runtime",
      "C": "The compiler shows an error",
      "D": "The object is initialized to nil"
    },
    "answer": "B"
  },
  {
    "question": "Which Combine framework component is used to watch for changes in a property and execute code in response?",
    "options": {
      "A": "Publisher",
      "B": "Subscriber",
      "C": "Operator",
      "D": "Subject"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of '.onReceive()' in a SwiftUI View?",
    "options": {
      "A": "To receive text input",
      "B": "To perform an action when a publisher (like a Timer or NotificationCenter) emits a value",
      "C": "To download data from a URL",
      "D": "To handle touch events"
    },
    "answer": "B"
  },
  {
    "question": "Which property wrapper is best suited for a ViewModel that is created and owned by a specific View?",
    "options": {
      "A": "@ObservedObject",
      "B": "@StateObject",
      "C": "@State",
      "D": "@Environment"
    },
    "answer": "B"
  },
  {
    "question": "What is the role of '@Published' in a class conforming to ObservableObject?",
    "options": {
      "A": "It publishes the app to the App Store",
      "B": "It automatically calls 'objectWillChange.send()' whenever the property is modified",
      "C": "It makes the property thread-safe",
      "D": "It saves the property to UserDefaults"
    },
    "answer": "B"
  },
  {
    "question": "Which SwiftUI modifier is used to handle asynchronous data fetching as soon as a view is created?",
    "options": {
      "A": ".onAppear()",
      "B": ".task()",
      "C": ".async()",
      "D": ".onLoad()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Escaping Closure' in the context of a network call completion handler?",
    "options": {
      "A": "A closure that runs inside the function",
      "B": "A closure that is called after the function returns, often when the network response arrives",
      "C": "A closure that exits the app",
      "D": "A closure used for error handling only"
    },
    "answer": "B"
  },
  {
    "question": "Which protocol must a custom data model conform to in order to be easily decoded from a JSON response?",
    "options": {
      "A": "ObservableObject",
      "B": "Codable",
      "C": "Identifiable",
      "D": "Equatable"
    },
    "answer": "B"
  },
  {
    "question": "How do you handle multiple asynchronous network requests in parallel using Swift Concurrency?",
    "options": {
      "A": "Use multiple .task() modifiers",
      "B": "Use 'async let' or a 'TaskGroup'",
      "C": "Use a serial DispatchQueue",
      "D": "Call 'await' on each request sequentially"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'MainActor' attribute in a ViewModel?",
    "options": {
      "A": "To make it the main class of the app",
      "B": "To ensure that property updates occur on the main thread for UI safety",
      "C": "To allow it to run in the background",
      "D": "To speed up data processing"
    },
    "answer": "B"
  },
  {
    "question": "Which property wrapper allows you to persist and sync data across the entire app using the user's iCloud account?",
    "options": {
      "A": "@AppStorage",
      "B": "@NSUbiquitousKeyValueStore (or via CloudKit)",
      "C": "@StateObject",
      "D": "@CloudStorage"
    },
    "answer": "B"
  },
  {
    "question": "In Combine, which operator is used to limit the frequency of values sent by a publisher (e.g., for search typing)?",
    "options": {
      "A": "delay",
      "B": "debounce",
      "C": "filter",
      "D": "compactMap"
    },
    "answer": "B"
  },
  {
    "question": "What does the '.sink' method do in a Combine pipeline?",
    "options": {
      "A": "It deletes the data",
      "B": "It attaches a subscriber with closure-based behavior to a publisher",
      "C": "It sends data to a server",
      "D": "It filters out nil values"
    },
    "answer": "B"
  },
  {
    "question": "Which SwiftUI view is used to provide a fallback UI (like a spinner) while waiting for an 'AsyncImage' to load?",
    "options": {
      "A": "ProgressView",
      "B": "placeholder parameter in AsyncImage",
      "C": "ZStack",
      "D": "Loader"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Cancellable' in Combine?",
    "options": {
      "A": "To stop an animation",
      "B": "A protocol indicating that an activity or subscription can be canceled to free up resources",
      "C": "To delete a database entry",
      "D": "To close a view"
    },
    "answer": "B"
  },
  {
    "question": "Which property wrapper is used to access 'Scene' level storage that persists even if the app is put in the background?",
    "options": {
      "A": "@AppStorage",
      "B": "@SceneStorage",
      "C": "@State",
      "D": "@Environment"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Dependency Injection' in SwiftUI?",
    "options": {
      "A": "Downloading libraries via Swift Package Manager",
      "B": "The practice of passing dependencies (like a service) into a view or ViewModel rather than hardcoding them",
      "C": "Injecting code into the system kernel",
      "D": "A way to handle network errors"
    },
    "answer": "B"
  },
  {
    "question": "In Swift Concurrency, what is the role of 'await'?",
    "options": {
      "A": "To start a timer",
      "B": "To suspend the current task until the asynchronous function returns a result",
      "C": "To force a function to run on a background thread",
      "D": "To wait for user input"
    },
    "answer": "B"
  },
  {
    "question": "Which Combine operator is used to transform the data type of a publisher's output?",
    "options": {
      "A": "filter",
      "B": "map",
      "C": "scan",
      "D": "reduce"
    },
    "answer": "B"
  },
  {
    "question": "What is 'AnyCancellable' usually used for in a ViewModel?",
    "options": {
      "A": "To store a list of active subscriptions so they aren't destroyed immediately",
      "B": "To handle errors",
      "C": "To navigate between screens",
      "D": "To store user profile data"
    },
    "answer": "A"
  },
  {
    "question": "Which property wrapper is used to read data from a Core Data fetch request in SwiftUI?",
    "options": {
      "A": "@State",
      "B": "@FetchRequest",
      "C": "@CoreData",
      "D": "@Environment"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'Identifiable' protocol in a data model?",
    "options": {
      "A": "To make the model searchable",
      "B": "To provide a stable 'id' property so SwiftUI can uniquely track items in a List",
      "C": "To encrypt the model",
      "D": "To convert the model to JSON"
    },
    "answer": "B"
  },
  {
    "question": "How do you handle a JSON array of objects in SwiftUI?",
    "options": {
      "A": "Use a ForEach loop inside a List",
      "B": "Decode the JSON into an Array of Codable structs",
      "C": "Both A and B",
      "D": "SwiftUI cannot handle arrays"
    },
    "answer": "C"
  },
  {
    "question": "Which modifier allows you to change the navigation title of a view?",
    "options": {
      "A": ".title()",
      "B": ".navigationTitle()",
      "C": ".header()",
      "D": ".barTitle()"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Swift Package Manager' (SPM) used for?",
    "options": {
      "A": "To manage app versions",
      "B": "To add and manage third-party libraries and dependencies in your project",
      "C": "To upload the app to App Store",
      "D": "To bundle images"
    },
    "answer": "B"
  },
  {
    "question": "In SwiftUI, what is 'Single Source of Truth'?",
    "options": {
      "A": "Using only one file for code",
      "B": "A design principle where data is stored in one place and referenced/bound by other views",
      "C": "A specific type of database",
      "D": "Using only @State"
    },
    "answer": "B"
  },
  {
    "question": "Which property wrapper is used to create a globally accessible object that is shared by all instances of an app (Singleton style)?",
    "options": {
      "A": "@EnvironmentObject",
      "B": "Using a static let instance inside a class",
      "C": "@State",
      "D": "@Global"
    },
    "answer": "B"
  },
  {
    "question": "What does the '.onDismiss' closure in a '.sheet' modifier do?",
    "options": {
      "A": "Closes the sheet",
      "B": "Runs a block of code when the user finishes dismissing the sheet",
      "C": "Prevents the sheet from closing",
      "D": "Deletes the sheet data"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier is used to limit the number of lines a Text view can occupy?",
    "options": {
      "A": ".limitLines()",
      "B": ".lineLimit()",
      "C": ".maxLines()",
      "D": ".truncationMode()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'URLRequest' in Swift networking?",
    "options": {
      "A": "The response from the server",
      "B": "An object that represents a specific URL request, including headers and HTTP methods",
      "C": "A browser tool",
      "D": "The URL string itself"
    },
    "answer": "B"
  },
  {
    "question": "Which property wrapper is used to respond to orientation changes or window size changes in SwiftUI?",
    "options": {
      "A": "@Environment(\\.horizontalSizeClass)",
      "B": "@State",
      "C": "@Orientation",
      "D": "@ScreenSize"
    },
    "answer": "A"
  },
  {
    "question": "What is the primary benefit of using 'AsyncImage' over a custom image downloader?",
    "options": {
      "A": "It is faster",
      "B": "It is a built-in SwiftUI view that handles loading, caching (to an extent), and placeholder logic",
      "C": "It only works with local images",
      "D": "It supports 3D images"
    },
    "answer": "B"
  },
  {
    "question": "In Combine, what is a 'Subject'?",
    "options": {
      "A": "A user's profile",
      "B": "A publisher that you can manually inject values into (Passthrough or CurrentValue)",
      "C": "A network error",
      "D": "A database key"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used in Combine to run a closure when a publisher completes successfully?",
    "options": {
      "A": ".onSuccess",
      "B": ".handleEvents(receiveCompletion:)",
      "C": ".sink(receiveCompletion:)",
      "D": "Both B and C"
    },
    "answer": "D"
  },
  {
    "question": "What is the purpose of 'JSONDecoder'?",
    "options": {
      "A": "To write JSON files",
      "B": "To parse JSON data into Swift objects",
      "C": "To encrypt data",
      "D": "To validate a URL"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier allows you to specify a custom 'ID' for a view, often used to help SwiftUI identify it during transitions?",
    "options": {
      "A": ".tag()",
      "B": ".id()",
      "C": ".key()",
      "D": ".identity()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'State Hoisting' in SwiftUI?",
    "options": {
      "A": "Moving @State from a child view to its parent to allow sharing or synchronization",
      "B": "Deleting state variables",
      "C": "Lifting the app to the cloud",
      "D": "Using @EnvironmentObject everywhere"
    },
    "answer": "A"
  },
  {
    "question": "Which property wrapper is used to manage and track the current focus state of text fields?",
    "options": {
      "A": "@State",
      "B": "@FocusState",
      "C": "@ActiveField",
      "D": "@KeyboardState"
    },
    "answer": "B"
  },
  {
    "question": "What is the role of 'Task' in SwiftUI?",
    "options": {
      "A": "To assign work to developers",
      "B": "A unit of asynchronous work that can run on a background thread",
      "C": "A UI component for progress",
      "D": "A database migration script"
    },
    "answer": "B"
  },
  {
    "question": "Which Combine operator allows you to merge multiple publishers into one stream?",
    "options": {
      "A": "combineLatest",
      "B": "merge",
      "C": "zip",
      "D": "All of the above"
    },
    "answer": "D"
  },
  {
    "question": "What is the purpose of '.alert' modifier?",
    "options": {
      "A": "To play a sound",
      "B": "To present a pop-up dialog box with a message and buttons based on a state change",
      "C": "To log errors",
      "D": "To highlight text"
    },
    "answer": "B"
  },
  {
    "question": "Which property wrapper is used to access the current 'dismiss' action for a sheet or navigation stack?",
    "options": {
      "A": "@Environment(\\.dismiss)",
      "B": "@State",
      "C": "@Binding",
      "D": "@Presentation"
    },
    "answer": "A"
  },
  {
    "question": "What does the 'Equatable' protocol help with in SwiftUI views?",
    "options": {
      "A": "Enables sorting of views",
      "B": "Allows SwiftUI to skip re-rendering a view if its data hasn't changed (EquatableView)",
      "C": "Makes the view resizable",
      "D": "Handles network responses"
    },
    "answer": "B"
  },
  {
    "question": "Which property wrapper is used to create a link to a setting stored in the 'Info.plist'?",
    "options": {
      "A": "@AppStorage",
      "B": "@Environment",
      "C": "SwiftUI cannot access Info.plist via property wrappers",
      "D": "@Setting"
    },
    "answer": "C"
  },
  {
    "question": "What is 'Combine' in the context of iOS?",
    "options": {
      "A": "A tool to merge files",
      "B": "A declarative Swift API for processing values over time (Reactive Programming)",
      "C": "A multi-platform framework",
      "D": "A database engine"
    },
    "answer": "B"
  },
  {
    "question": "Which view is used to create a popup that covers a portion of the screen like a modal?",
    "options": {
      "A": ".sheet()",
      "B": ".fullScreenCover()",
      "C": ".popover()",
      "D": "All of the above"
    },
    "answer": "D"
  },
  {
    "question": "In MVVM, why should the View NOT have a reference to the Model?",
    "options": {
      "A": "To keep the View small",
      "B": "To maintain separation of concerns and ensure the ViewModel acts as the sole translator",
      "C": "Models are too heavy for views",
      "D": "Views can only handle ViewModels"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier is used to define the style of a button (e.g., Bordered, Prominent)?",
    "options": {
      "A": ".buttonStyle()",
      "B": ".style()",
      "C": ".format()",
      "D": ".appearance()"
    },
    "answer": "A"
  },
  {
    "question": "Which tool in Xcode is used to profile SwiftUI views and identify unnecessary re-renders?",
    "options": {
      "A": "Logcat",
      "B": "Instruments (SwiftUI View Subsystem)",
      "C": "Canvas debugger",
      "D": "Console"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary cause of 'Jank' or stuttering in a SwiftUI List?",
    "options": {
      "A": "Using too many colors",
      "B": "Performing heavy computation or blocking the Main Thread inside a view's body",
      "C": "Using @State instead of @Binding",
      "D": "Having more than 5 items in the list"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier is used to provide a specific description for a UI element to be read by VoiceOver?",
    "options": {
      "A": ".help()",
      "B": ".accessibilityLabel()",
      "C": ".voiceOver()",
      "D": ".label()"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'AnyView' in SwiftUI?",
    "options": {
      "A": "To create any shape",
      "B": "A type-erased wrapper used to return different types of views from a single property (though often discouraged for performance)",
      "C": "To view any file type",
      "D": "To bypass the body requirement"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier allows a view to respond to a 'Phase' based animation (e.g., repeating a sequence of states)?",
    "options": {
      "A": ".phaseAnimator()",
      "B": ".sequence()",
      "C": ".repeatAnimation()",
      "D": ".loop()"
    },
    "answer": "A"
  },
  {
    "question": "What does the '.drawingGroup()' modifier do?",
    "options": {
      "A": "Groups views for dragging",
      "B": "Flattens a view hierarchy into a single Metal-backed layer to improve performance for complex graphics",
      "C": "Saves a drawing to the library",
      "D": "Aligns items in a grid"
    },
    "answer": "B"
  },
  {
    "question": "Which property wrapper is used to create a link to a value in the device's Keychain?",
    "options": {
      "A": "@AppStorage",
      "B": "SwiftUI does not provide a native wrapper for Keychain; custom implementation is required",
      "C": "@KeyStorage",
      "D": "@SecureState"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'accessibilityAddTraits'?",
    "options": {
      "A": "To add new features to the app",
      "B": "To tell assistive technologies that an element behaves like a specific type (e.g., .isButton or .isSelected)",
      "C": "To translate the app",
      "D": "To increase font size"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier is used to prevent an element from being seen by VoiceOver?",
    "options": {
      "A": ".hidden()",
      "B": ".accessibilityHidden(true)",
      "C": ".ignoreAccess()",
      "D": ".silent()"
    },
    "answer": "B"
  },
  {
    "question": "In SwiftUI, what is the role of a 'ViewModifier'?",
    "options": {
      "A": "To change the app's version",
      "B": "To encapsulate a set of view transformations into a reusable object",
      "C": "To manage the database",
      "D": "To handle network responses"
    },
    "answer": "B"
  },
  {
    "question": "Which method is used to create a custom ViewModifier?",
    "options": {
      "A": "makeView()",
      "B": "body(content:)",
      "C": "modify(_:)",
      "D": "transform()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Container Relative Shape'?",
    "options": {
      "A": "A shape that fits inside a box",
      "B": "A shape that automatically adjusts its corner radius to match its parent container (common in Widgets)",
      "C": "A circular view",
      "D": "A layout for iPad"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier allows a View to capture the current focus, such as making a TextField active automatically?",
    "options": {
      "A": ".focus()",
      "B": ".focused($isFocused)",
      "C": ".setActive()",
      "D": ".keyboard(true)"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'ViewBuilder' attribute?",
    "options": {
      "A": "To build the app for release",
      "B": "A parameter attribute that allows a closure to provide multiple child views (used in stacks and custom containers)",
      "C": "To create a 3D model",
      "D": "To manage state"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier is used to set the preferred orientation for a specific view in SwiftUI?",
    "options": {
      "A": ".rotate()",
      "B": "SwiftUI manages this via Info.plist or AppDelegate; limited per-view control is available via task/onAppear",
      "C": ".orientation(.landscape)",
      "D": ".lockRotation()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Self-Sizing' in the context of SwiftUI views?",
    "options": {
      "A": "A view that resizes its parent",
      "B": "A view that calculates its own size based on its content without requiring an explicit frame",
      "C": "A view that grows with the network speed",
      "D": "A database scaling feature"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier allows you to define a custom 'content shape' for hits and interactions (e.g., making the whole area of a spacer tappable)?",
    "options": {
      "A": ".hitArea()",
      "B": ".contentShape(Rectangle())",
      "C": ".tapArea()",
      "D": ".interactionZone()"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'SwiftUI Lifecycle' vs 'AppDelegate Lifecycle'?",
    "options": {
      "A": "SwiftUI is for Android",
      "B": "The SwiftUI Lifecycle uses the 'App' protocol and 'WindowGroup' instead of AppDelegate/SceneDelegate",
      "C": "They are the same",
      "D": "AppDelegate is faster"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier is used to provide a suggestion or hint for an accessibility element?",
    "options": {
      "A": ".help()",
      "B": ".accessibilityHint()",
      "C": ".info()",
      "D": ".tooltip()"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of '.id(UUID())' when applied to a List or ScrollView?",
    "options": {
      "A": "To set the user's ID",
      "B": "To force the entire view to be recreated (often used to reset scroll position)",
      "C": "To encrypt the list",
      "D": "To sort the items"
    },
    "answer": "B"
  },
  {
    "question": "Which property wrapper is used for data that is stored in the 'SceneStorage' and is unique to each window on iPad?",
    "options": {
      "A": "@AppStorage",
      "B": "@SceneStorage",
      "C": "@WindowState",
      "D": "@LocalState"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of '.equatable()' modifier?",
    "options": {
      "A": "To make views equal",
      "B": "To optimize performance by preventing re-renders if the view's data hasn't changed",
      "C": "To handle math logic",
      "D": "To sort a list"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier is used to apply a tint color to standard controls like switches and sliders?",
    "options": {
      "A": ".foregroundColor()",
      "B": ".accentColor() / .tint()",
      "C": ".paint()",
      "D": ".shade()"
    },
    "answer": "B"
  },
  {
    "question": "What is the role of 'UIViewRepresentable'?",
    "options": {
      "A": "To convert SwiftUI to UIKit",
      "B": "To wrap a UIKit view so it can be used inside a SwiftUI layout",
      "C": "To manage system settings",
      "D": "To handle 3D graphics"
    },
    "answer": "B"
  },
  {
    "question": "Which method must be implemented in 'UIViewRepresentable' to create the initial UIKit view?",
    "options": {
      "A": "updateUIView()",
      "B": "makeUIView(context:)",
      "C": "initView()",
      "D": "startView()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Coordinator' in the context of UIViewRepresentable?",
    "options": {
      "A": "A person who manages code",
      "B": "A helper class used to communicate changes from the UIKit view back to SwiftUI",
      "C": "A layout manager",
      "D": "A database tool"
    },
    "answer": "B"
  },
  {
    "question": "Which property wrapper is used to track the 'Horizontal Size Class' (Compact vs Regular) for adaptive layouts?",
    "options": {
      "A": "@State",
      "B": "@Environment(\\.horizontalSizeClass)",
      "C": "@ScreenMode",
      "D": "@DeviceType"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'PreviewDevice' in SwiftUI?",
    "options": {
      "A": "To buy a new device",
      "B": "To specify which Apple device (e.g., iPhone 15) the Canvas should use for the preview",
      "C": "To test the camera",
      "D": "To check battery life"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier is used to set the 'search' behavior in a List or NavigationStack?",
    "options": {
      "A": ".searchable()",
      "B": ".find()",
      "C": ".lookup()",
      "D": ".query()"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Dynamic Type' support in SwiftUI?",
    "options": {
      "A": "Changing code at runtime",
      "B": "The UI automatically scaling text based on the user's system font size preference",
      "C": "A specific variable type",
      "D": "An animation style"
    },
    "answer": "B"
  },
  {
    "question": "Which property wrapper is used to create a state that is shared across all instances of a Widget?",
    "options": {
      "A": "@State",
      "B": "@AppStorage",
      "C": "@Environment",
      "D": "Widgets use entries from a TimelineProvider, not property wrappers for state"
    },
    "answer": "D"
  },
  {
    "question": "What is 'TimelineProvider' used for?",
    "options": {
      "A": "To manage social media",
      "B": "To provide a sequence of data (entries) to a Widget over time",
      "C": "To track app history",
      "D": "To schedule notifications"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier is used to show a 'Badge' (number/dot) on a TabView item or List row?",
    "options": {
      "A": ".notification()",
      "B": ".badge()",
      "C": ".dot()",
      "D": ".alertCount()"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of '.disabled(true)'?",
    "options": {
      "A": "To delete a view",
      "B": "To prevent user interaction and dim the appearance of a view hierarchy",
      "C": "To stop the network",
      "D": "To turn off the screen"
    },
    "answer": "B"
  },
  {
    "question": "Which property wrapper allows you to detect when the app moves from Active to Background state?",
    "options": {
      "A": "@Environment(\\.scenePhase)",
      "B": "@State",
      "C": "@AppStatus",
      "D": "@Background"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Color.primary'?",
    "options": {
      "A": "The color blue",
      "B": "A semantic color that is black in light mode and white in dark mode",
      "C": "A user's favorite color",
      "D": "A transparent color"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier is used to apply a shadow that follows the shape of an image or text (Drop Shadow)?",
    "options": {
      "A": ".shadow()",
      "B": ".dropShadow()",
      "C": ".outerGlow()",
      "D": ".elevate()"
    },
    "answer": "A"
  },
  {
    "question": "What is the purpose of 'Transaction' in SwiftUI animations?",
    "options": {
      "A": "To handle payments",
      "B": "An object that carries information about how the current state change should be animated",
      "C": "A database log",
      "D": "A screen transition"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier is used to add a 'Swipe Action' with a custom icon/color to a List row?",
    "options": {
      "A": ".onDelete()",
      "B": ".swipeActions()",
      "C": ".swipeRow()",
      "D": ".rowAction()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Namespace' in the context of hero animations?",
    "options": {
      "A": "A variable name",
      "B": "A property wrapper used to synchronize IDs between two views for MatchedGeometryEffect",
      "C": "A file organization tool",
      "D": "A network domain"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier allows you to change the background style of a List (e.g. removing the default gray)?",
    "options": {
      "A": ".listStyle()",
      "B": ".scrollContentBackground(.hidden)",
      "C": ".clearBackground()",
      "D": ".noColor()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'SwiftUI Introspection'?",
    "options": {
      "A": "Self-reflection for developers",
      "B": "The process of reaching into the underlying UIKit/AppKit components of a SwiftUI view to apply custom styles",
      "C": "Checking the code for bugs",
      "D": "Monitoring app memory"
    },
    "answer": "B"
  },
  {
    "question": "Which property wrapper is used to manage a value that should be available to all views in a specific 'Window'?",
    "options": {
      "A": "@AppStorage",
      "B": "@EnvironmentObject",
      "C": "@StateObject",
      "D": "@ObservedObject"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Safe Area'?",
    "options": {
      "A": "A testing area",
      "B": "The portion of the screen not covered by the notch, status bar, or home indicator",
      "C": "A secure database",
      "D": "A password manager"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier is used to display a 'Tool Bar' with items at the top or bottom of a view?",
    "options": {
      "A": ".navigationBar()",
      "B": ".toolbar()",
      "C": ".actionBar()",
      "D": ".menuBar()"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Opaque Return Type' (some View)?",
    "options": {
      "A": "A hidden view",
      "B": "A return type that hides the specific implementation of the view tree from the compiler to simplify complex hierarchies",
      "C": "A view that isn't transparent",
      "D": "A private view"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier is used to add a 'Context Menu' that appears on right-click or long-press?",
    "options": {
      "A": ".menu()",
      "B": ".contextMenu()",
      "C": ".popover()",
      "D": ".rightClick()"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'View Protocol'?",
    "options": {
      "A": "A set of rules for the app",
      "B": "The fundamental protocol that all SwiftUI UI elements must conform to",
      "C": "A networking protocol",
      "D": "A database schema"
    },
    "answer": "B"
  },
  {
    "question": "Which modifier is used to add a 'Corner Radius' to only specific corners?",
    "options": {
      "A": ".cornerRadius()",
      "B": "Using a .clipShape() with a custom UnevenRoundedRectangle",
      "C": ".sideRadius()",
      "D": ".partialRound()"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'AppStorage'?",
    "options": {
      "A": "To store the app on the phone",
      "B": "A property wrapper that reads and writes to UserDefaults and refreshes the view automatically",
      "C": "To store images in the cloud",
      "D": "To manage database migrations"
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
    skill = "SwiftUI"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
