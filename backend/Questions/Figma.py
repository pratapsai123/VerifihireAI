from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
  {
    "question": "What is the primary difference between Figma and many other design tools like Sketch or Adobe XD?",
    "options": {
      "A": "Figma is only for photo editing",
      "B": "Figma is a cloud-based, collaborative tool that runs in a browser as well as a desktop app",
      "C": "Figma does not support vector graphics",
      "D": "Figma requires a constant manual 'Save' to prevent data loss"
    },
    "answer": "B"
  },
  {
    "question": "In Figma, what is a 'Frame' primarily used for?",
    "options": {
      "A": "To add a decorative border to an image",
      "B": "To act as a container for layers, similar to an Artboard, but with additional properties like layout grids and nesting",
      "C": "To crop a photo",
      "D": "To group layers so they cannot be edited individually"
    },
    "answer": "B"
  },
  {
    "question": "Which keyboard shortcut is used to create a Frame (F) or an Artboard in Figma?",
    "options": {
      "A": "A",
      "B": "F",
      "C": "G",
      "D": "Both A and B are common, though F is the standard shortcut"
    },
    "answer": "D"
  },
  {
    "question": "What is the 'Assets' panel used for in Figma?",
    "options": {
      "A": "Storing local hard drive files",
      "B": "Managing and dragging instances of Components and Library elements into your design",
      "C": "Exporting images to PNG",
      "D": "Editing CSS code"
    },
    "answer": "B"
  },
  {
    "question": "In the Figma interface, where would you find the 'Design', 'Prototype', and 'Inspect' tabs?",
    "options": {
      "A": "The Left Sidebar",
      "B": "The Right Sidebar (Properties Panel)",
      "C": "The Top Toolbar",
      "D": "The Bottom Status Bar"
    },
    "answer": "B"
  },
  {
    "question": "What happens when you hold 'Alt' (Windows) or 'Option' (Mac) while dragging an object?",
    "options": {
      "A": "It deletes the object",
      "B": "It creates a duplicate of the object",
      "C": "It locks the object in place",
      "D": "It changes the object's color"
    },
    "answer": "B"
  },
  {
    "question": "What is 'FigJam' used for?",
    "options": {
      "A": "High-fidelity UI prototyping",
      "B": "An online whiteboard for brainstorming, diagramming, and early-stage collaboration",
      "C": "Editing video files",
      "D": "A tool to compress Figma files"
    },
    "answer": "B"
  },
  {
    "question": "How do you 'Group' selected layers in Figma?",
    "options": {
      "A": "Ctrl + G (Windows) / Cmd + G (Mac)",
      "B": "Ctrl + L (Windows) / Cmd + L (Mac)",
      "C": "Right-click > Flatten",
      "D": "Alt + G"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'Boolean Groups' feature used for?",
    "options": {
      "A": "Writing code inside Figma",
      "B": "Combining shapes using operations like Union, Subtract, Intersect, and Exclude",
      "C": "Setting true/false variables for users",
      "D": "Managing font weights"
    },
    "answer": "B"
  },
  {
    "question": "Which tool would you use to create a custom, non-standard vector shape by drawing points?",
    "options": {
      "A": "Rectangle tool",
      "B": "Pen tool (P)",
      "C": "Move tool",
      "D": "Slice tool"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Constraints' in Figma?",
    "options": {
      "A": "To limit the number of collaborators",
      "B": "To define how layers respond when their parent Frame is resized",
      "C": "To lock a layer so it can't be moved",
      "D": "To force a specific color palette"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'Clip Content' checkbox do on a Frame?",
    "options": {
      "A": "It deletes everything outside the frame",
      "B": "It hides objects within the frame that extend beyond the frame's boundaries",
      "C": "It copies the content to the clipboard",
      "D": "It reduces the file size"
    },
    "answer": "B"
  },
  {
    "question": "How do you view the distance between two objects in Figma?",
    "options": {
      "A": "By using the Ruler tool",
      "B": "By selecting one object and holding 'Alt/Option' while hovering over another",
      "C": "By checking the Layers panel",
      "D": "By double-clicking the canvas"
    },
    "answer": "B"
  },
  {
    "question": "Which panel allows you to change the Opacity, Fill, and Stroke of a selected element?",
    "options": {
      "A": "Layers Panel",
      "B": "Design Sidebar",
      "C": "Assets Panel",
      "D": "Prototype Sidebar"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Version History' in Figma?",
    "options": {
      "A": "A list of all users who have viewed the file",
      "B": "A record of saved states of the design, allowing you to view or restore earlier versions",
      "C": "A tool to update Figma software",
      "D": "The file's size history"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary benefit of using 'Auto Layout' in Figma?",
    "options": {
      "A": "It automatically chooses colors for your design",
      "B": "It creates dynamic frames that grow or shrink as you change text or add/remove layers",
      "C": "It speeds up the export process to PNG",
      "D": "It automatically saves the file to the cloud"
    },
    "answer": "B"
  },
  {
    "question": "How do you turn a selected layer or frame into a 'Main Component'?",
    "options": {
      "A": "Ctrl + G",
      "B": "Ctrl + Alt + K (Windows) / Cmd + Option + K (Mac)",
      "C": "Right-click > Flatten",
      "D": "Double-click the layer name"
    },
    "answer": "B"
  },
  {
    "question": "What is an 'Instance' in Figma?",
    "options": {
      "A": "A unique version of a file",
      "B": "A copy of a Main Component that stays linked to it and inherits its changes",
      "C": "A type of animation trigger",
      "D": "A temporary draft of a design"
    },
    "answer": "B"
  },
  {
    "question": "In Auto Layout, what does 'Hug Contents' mean for a frame's width or height?",
    "options": {
      "A": "The frame stays at a fixed size regardless of content",
      "B": "The frame resizes itself to fit exactly around the elements inside it",
      "C": "The frame expands to fill the entire parent container",
      "D": "The frame centers the content automatically"
    },
    "answer": "B"
  },
  {
    "question": "What are 'Variants' in Figma components?",
    "options": {
      "A": "Different files for the same project",
      "B": "A way to group similar components into a single container (e.g., different states of a button like Default, Hover, and Disabled)",
      "C": "Custom fonts used in the design",
      "D": "Plugins that change the UI"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Component Properties' (e.g., Boolean, Instance Swap, Text)?",
    "options": {
      "A": "To write code inside the component",
      "B": "To allow users to customize specific parts of an instance through the right sidebar without detaching it",
      "C": "To protect the component from being edited",
      "D": "To change the component's file location"
    },
    "answer": "B"
  },
  {
    "question": "What happens if you change the 'Fill' color of a Main Component?",
    "options": {
      "A": "Only that Main Component changes",
      "B": "All instances of that component will automatically update to the new color, unless they have a local override",
      "C": "Figma creates a new variant",
      "D": "Nothing happens until you click 'Push Changes'"
    },
    "answer": "B"
  },
  {
    "question": "What is the shortcut to add Auto Layout to a selection?",
    "options": {
      "A": "Alt + L",
      "B": "Shift + A",
      "C": "Ctrl + Shift + G",
      "D": "Ctrl + J"
    },
    "answer": "B"
  },
  {
    "question": "In Auto Layout, what is 'Absolute Positioning' used for?",
    "options": {
      "A": "To fix a layer to the top of the browser",
      "B": "To place an element anywhere inside an Auto Layout frame without it affecting the flow of other elements",
      "C": "To set coordinates relative to the whole canvas",
      "D": "To lock an element so it can't be moved"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Style' in Figma (e.g., Color Style, Text Style)?",
    "options": {
      "A": "A way to dress up the Figma interface",
      "B": "A reusable definition of properties that can be applied across multiple layers to maintain consistency",
      "C": "A specific layout grid",
      "D": "A plugin for CSS generation"
    },
    "answer": "B"
  },
  {
    "question": "How can you tell a 'Main Component' from an 'Instance' in the Layers panel?",
    "options": {
      "A": "Main Components are blue; Instances are purple",
      "B": "Main Components use a four-diamond icon; Instances use a single hollow diamond icon",
      "C": "Main Components are always at the top of the list",
      "D": "Instances have a 'Lock' icon next to them"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Fill Container' do in an Auto Layout child element?",
    "options": {
      "A": "It makes the element as small as possible",
      "B": "It stretches the element to take up all available space within its parent Auto Layout frame",
      "C": "It adds a background color to the element",
      "D": "It centers the element"
    },
    "answer": "B"
  },
  {
    "question": "Which feature allows you to change an icon inside a component instance to a different icon from your library?",
    "options": {
      "A": "Boolean Property",
      "B": "Instance Swap Property",
      "C": "Text Property",
      "D": "Layer Mask"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Detaching an Instance'?",
    "options": {
      "A": "Moving an instance to a different page",
      "B": "Breaking the link between an instance and its Main Component, making it a regular set of layers",
      "C": "Deleting the instance",
      "D": "Hiding the instance from the design"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'Vertical Gap' and 'Horizontal Padding' settings in Auto Layout?",
    "options": {
      "A": "To set the transparency of the frame",
      "B": "To control the spacing between items and the inner space of the frame boundary",
      "C": "To set the thickness of the border",
      "D": "To change the font size"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary requirement for 'Smart Animate' to work correctly between two frames?",
    "options": {
      "A": "The frames must have different background colors",
      "B": "Layers must have the exact same name and hierarchy across both frames",
      "C": "Both frames must be the same size",
      "D": "You must use the Pen tool to draw the path"
    },
    "answer": "B"
  },
  {
    "question": "What are 'Variables' in Figma (introduced in 2023)?",
    "options": {
      "A": "A way to write JavaScript inside a design",
      "B": "Reusable values that can be applied to design properties like colors, numbers, and strings to build dynamic design systems",
      "C": "A tool to track how many users click a button",
      "D": "Different versions of a plugin"
    },
    "answer": "B"
  },
  {
    "question": "Which Prototyping trigger allows an action to happen automatically after a set amount of time?",
    "options": {
      "A": "On Click",
      "B": "After Delay",
      "C": "On Hover",
      "D": "While Pressing"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Flow Starting Point' in Figma Prototyping?",
    "options": {
      "A": "The first page of the design file",
      "B": "The specific frame where a user begins an interactive prototype session",
      "C": "The moment a developer inspects the file",
      "D": "The baseline of a text layer"
    },
    "answer": "B"
  },
  {
    "question": "In the context of Variables, what does 'Mode' (e.g., Light Mode and Dark Mode) allow you to do?",
    "options": {
      "A": "Change the Figma interface theme only",
      "B": "Switch between different sets of variable values across an entire design or frame instantly",
      "C": "Edit the code of a component",
      "D": "View the design in grayscale"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Overlay' action used for in prototyping?",
    "options": {
      "A": "To stack two images on top of each other permanently",
      "B": "To show content (like a modal, menu, or alert) on top of the current frame without navigating away",
      "C": "To change the blend mode of a layer",
      "D": "To create a background blur effect"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Section' (Shift + S) help with in a complex Figma file?",
    "options": {
      "A": "It creates a new page",
      "B": "It groups related frames together and allows for organized prototyping and developer handoff",
      "C": "It cuts an image into smaller pieces",
      "D": "It acts as a mask for vector shapes"
    },
    "answer": "B"
  },
  {
    "question": "Which prototyping feature allows a user to move back to the previous screen they were on?",
    "options": {
      "A": "Navigate to",
      "B": "Back",
      "C": "Scroll to",
      "D": "Close Overlay"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Sticky' scroll behavior in Figma?",
    "options": {
      "A": "To make the prototype lag",
      "B": "To keep an element (like a header or sidebar) fixed in a specific position while the rest of the content scrolls",
      "C": "To group elements together so they can't be moved",
      "D": "To add a shadow to an object"
    },
    "answer": "B"
  },
  {
    "question": "In the 'Inspect' or 'Dev Mode' panel, what information can developers primarily extract?",
    "options": {
      "A": "The user's personal data",
      "B": "CSS, Swift, or Kotlin code snippets, along with spacing, colors, and asset export options",
      "C": "The purchase history of the file",
      "D": "The original sketch drawings"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Individual Padding' in Auto Layout allow you to do?",
    "options": {
      "A": "Change the padding for every single user",
      "B": "Set different padding values for the Top, Right, Bottom, and Left sides of a frame",
      "C": "Add padding to a text character",
      "D": "Remove padding from all components at once"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Scale Tool' (K) used for that the 'Move Tool' (V) does not do?",
    "options": {
      "A": "Moving objects between pages",
      "B": "Resizing an object and all its properties (like strokes and effects) proportionally",
      "C": "Changing the color of an object",
      "D": "Creating a component"
    },
    "answer": "B"
  },
  {
    "question": "Which feature allows you to define a set of 'Tokens' for spacing, such as 4px, 8px, and 16px?",
    "options": {
      "A": "Styles",
      "B": "Number Variables",
      "C": "Constraints",
      "D": "Layout Grids"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Interactive Components'?",
    "options": {
      "A": "Components that talk to the user",
      "B": "A feature that allows you to define prototype interactions between variants within a component set (e.g., a checkbox toggling)",
      "C": "A way to write code in a button",
      "D": "A plugin for user testing"
    },
    "answer": "B"
  },
  {
    "question": "How do you 'Fix' a position of a layer so it doesn't move during scrolling in a prototype?",
    "options": {
      "A": "Lock the layer",
      "B": "Check 'Fix position when scrolling' in the Design or Prototype tab",
      "C": "Move the layer to a different page",
      "D": "Group it with a background image"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Publishing' a library in Figma?",
    "options": {
      "A": "To post the design on social media",
      "B": "To make components and styles available for use across other files within a team or organization",
      "C": "To save the file to a local PDF",
      "D": "To finalize the design so it can never be edited again"
    },
    "answer": "B"
  },
  {
    "question": "Which role in a Figma Team allows a user to edit files and manage libraries?",
    "options": {
      "A": "Viewer",
      "B": "Editor",
      "C": "Admin",
      "D": "Both B and C"
    },
    "answer": "D"
  },
  {
    "question": "What does 'Review State' (Ready for Dev) signify in a Section or Frame?",
    "options": {
      "A": "The design is being deleted",
      "B": "A signal to developers that this specific design is finalized and ready for implementation",
      "C": "The file is currently being presented",
      "D": "The design has failed accessibility tests"
    },
    "answer": "B"
  },
  {
    "question": "In a shared library, what happens when a Main Component is updated and published?",
    "options": {
      "A": "All instances in other files update automatically without warning",
      "B": "Subscribed files receive a notification allowing users to review and accept the updates",
      "C": "The instances in other files are automatically detached",
      "D": "The library is locked for 24 hours"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Branching' in Figma (available on Enterprise/Organization plans)?",
    "options": {
      "A": "Creating a copy of the file for every user",
      "B": "A controlled environment to explore changes in a file without affecting the main version until merged",
      "C": "A tool to draw trees and foliage",
      "D": "A way to split the design into multiple pages"
    },
    "answer": "B"
  },
  {
    "question": "How do you invite a collaborator to a specific Figma file?",
    "options": {
      "A": "Share button > Enter email or copy link",
      "B": "File > Export > Email",
      "C": "Right-click the canvas > Invite",
      "D": "Drag their profile picture into the file"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'Figma Community' used for?",
    "options": {
      "A": "A place to chat with other designers",
      "B": "A space to browse and install plugins, widgets, and design templates shared by others",
      "C": "A customer support forum",
      "D": "A tool for hiring new designers"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Code Connect' in Figma's Dev Mode?",
    "options": {
      "A": "A way to write CSS",
      "B": "A tool that allows developers to see actual code components from their own codebase (React, Swift, etc.) associated with Figma components",
      "C": "A plugin that translates designs into Python",
      "D": "A chat tool for developers"
    },
    "answer": "B"
  },
  {
    "question": "Which feature allows you to see every change made to a file by different users over time?",
    "options": {
      "A": "Activity Log",
      "B": "Version History",
      "C": "Layers Panel",
      "D": "Inspect Panel"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Widget' in Figma/FigJam?",
    "options": {
      "A": "A static image",
      "B": "An interactive object that adds functionality to the canvas (e.g., polls, charts, or timers)",
      "C": "A type of layer group",
      "D": "A tool to resize frames"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'Multiplayer' feature refer to in Figma?",
    "options": {
      "A": "A gaming mode",
      "B": "The ability for multiple people to work in the same file at the same time",
      "C": "Connecting multiple mice to one computer",
      "D": "Exporting to multiple file formats simultaneously"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Private Plugins' in an Organization plan?",
    "options": {
      "A": "Plugins that only one person can use",
      "B": "Plugins developed internally that are only accessible to members of that specific organization",
      "C": "Plugins that cost money",
      "D": "Plugins that hide design data"
    },
    "answer": "B"
  },
  {
    "question": "How do you 'Archive' a project in Figma?",
    "options": {
      "A": "Move it to the Trash",
      "B": "Move it to an 'Archived' folder/project to hide it from the active dashboard without deleting it",
      "C": "Compress it into a .zip file",
      "D": "Rename it with 'Archive' at the start"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Design Handoff'?",
    "options": {
      "A": "Giving the mouse to another designer",
      "B": "The process of transferring design specifications, assets, and documentation to developers for production",
      "C": "Exporting the final design as a PNG",
      "D": "Deleting the Figma file after completion"
    },
    "answer": "B"
  },
  {
    "question": "Which panel shows the 'CSS Box Model' for a selected element in Dev Mode?",
    "options": {
      "A": "Layers",
      "B": "Inspect / Layout",
      "C": "Assets",
      "D": "Prototype"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary purpose of 'Slot' components in a professional Figma design system?",
    "options": {
      "A": "To act as a placeholder within a complex component (like a Modal) that allows for flexible content swapping",
      "B": "To create a list of all colors used in a file",
      "C": "To automate the naming of layers",
      "D": "To speed up the rendering of 3D objects"
    },
    "answer": "A"
  },
  {
    "question": "When using 'Conditional Logic' in prototyping, what can you check before performing an action?",
    "options": {
      "A": "The user's battery level",
      "B": "The value of a variable (e.g., 'If CartValue > 100')",
      "C": "The time of day on the designer's computer",
      "D": "The number of layers in the file"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Loom' or 'Screen Recording' integration used for in Figma comments?",
    "options": {
      "A": "To record the user's face while they design",
      "B": "To provide video-based feedback or walkthroughs directly on the design canvas",
      "C": "To create a movie of the final prototype",
      "D": "To monitor employee productivity"
    },
    "answer": "B"
  },
  {
    "question": "Which Figma feature helps you check if your text contrast ratios meet WCAG standards?",
    "options": {
      "A": "Auto Layout",
      "B": "Accessibility Plugins (e.g., Stark or Contrast)",
      "C": "The Inspect Tab",
      "D": "Variables Mode"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Local Variable' vs. a 'Library Variable'?",
    "options": {
      "A": "Local variables only work in the current file; Library variables are published and accessible across the team",
      "B": "Local variables are for numbers; Library variables are for colors",
      "C": "Local variables are faster",
      "D": "There is no difference"
    },
    "answer": "A"
  },
  {
    "question": "In Advanced Prototyping, what does 'Set Variable' allow you to do during an interaction?",
    "options": {
      "A": "Change the name of a component",
      "B": "Update a variable's value dynamically (e.g., incrementing a counter or changing a status string)",
      "C": "Delete a color style",
      "D": "Change the file owner"
    },
    "answer": "B"
  },
  {
    "question": "What is the benefit of 'Naming Conventions' like 'atoms/button/primary' in a design system?",
    "options": {
      "A": "It makes the file size smaller",
      "B": "It automatically organizes components into a folder hierarchy in the Assets panel",
      "C": "It prevents other designers from editing the layers",
      "D": "It's required for Figma to save the file"
    },
    "answer": "B"
  },
  {
    "question": "Which tool would you use to create a 'Responsive Grid' that adapts to different screen sizes (Desktop, Tablet, Mobile)?",
    "options": {
      "A": "Slice tool",
      "B": "Layout Grids (with Columns and Gutters)",
      "C": "Pen tool",
      "D": "Pencil tool"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Component Property Scoping' used for in Variables?",
    "options": {
      "A": "To limit which properties a variable can be applied to (e.g., preventing a 'Corner Radius' variable from being used as a 'Fill')",
      "B": "To hide components from developers",
      "C": "To increase the contrast of a button",
      "D": "To rename all instances at once"
    },
    "answer": "A"
  },
  {
    "question": "What does the 'Min-Width' and 'Max-Width' settings in Auto Layout help achieve?",
    "options": {
      "A": "It makes the font size change automatically",
      "B": "It ensures a frame doesn't become too small or too large when being resized or filled with dynamic content",
      "C": "It sets the resolution of the export",
      "D": "It locks the height of the frame"
    },
    "answer": "B"
  },
  {
    "question": "Which Figma feature allows you to create a 'Multi-level' interactive menu without creating dozens of separate frames?",
    "options": {
      "A": "Standard Navigation",
      "B": "Nested Overlays and Variables",
      "C": "Grouped Layers",
      "D": "Boolean Operations"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Design Token' aliasing in Figma?",
    "options": {
      "A": "Using a fake name for a designer",
      "B": "Mapping a specific value (like #FF0000) to a 'Primitive' variable, and then mapping that variable to a 'Semantic' variable (like 'brand-primary')",
      "C": "Deleting unused colors",
      "D": "A way to encrypt design files"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'Selection Colors' section in the right sidebar?",
    "options": {
      "A": "To choose a random color for the selection",
      "B": "To see and bulk-edit every color used within a complex selection of multiple layers",
      "C": "To see who else has selected the same object",
      "D": "To test the colors for color-blindness"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Key Event' in Figma's Prototyping triggers?",
    "options": {
      "A": "An important event in the project timeline",
      "B": "A trigger that responds to specific keyboard presses (e.g., pressing 'Enter' to submit a form)",
      "C": "A click on the 'Main' button",
      "D": "An event that locks the file"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Library Analytics' (for Business/Enterprise plans)?",
    "options": {
      "A": "To see which designer is the fastest",
      "B": "To track how often components and styles are used and detached across the entire organization",
      "C": "To count the number of pixels in a library",
      "D": "To see which colors are trending globally"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary benefit of using 'Variable Expressions' in Figma Prototyping?",
    "options": {
      "A": "To change the background of the Figma UI",
      "B": "To perform mathematical operations (addition, subtraction, etc.) to update variable values dynamically during a prototype",
      "C": "To write CSS code directly into a button",
      "D": "To automatically translate text into different languages"
    },
    "answer": "B"
  },
  {
    "question": "In a design system, what is the difference between 'Primitive' and 'Semantic' tokens?",
    "options": {
      "A": "Primitive tokens are for shapes; Semantic tokens are for text",
      "B": "Primitive tokens represent raw values (Blue-500); Semantic tokens represent usage (Button-Background)",
      "C": "Primitive tokens are only used by developers",
      "D": "Semantic tokens are used for animation only"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'Change to' action do in an Interactive Component?",
    "options": {
      "A": "It navigates the user to a new page",
      "B": "It swaps the current variant of a component for another variant without a page transition",
      "C": "It changes the user's role to Editor",
      "D": "It deletes the current instance"
    },
    "answer": "B"
  },
  {
    "question": "How do you enable 'Dev Mode' in Figma?",
    "options": {
      "A": "By pressing Ctrl + D",
      "B": "By toggling the '</>' switch in the top right of the toolbar",
      "C": "By right-clicking a layer and selecting 'Code'",
      "D": "It is only available in the Desktop App's file menu"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Variable Scoping' used for in the Variables panel?",
    "options": {
      "A": "To search for variables in other files",
      "B": "To limit where a variable can be applied (e.g., ensuring a 'Spacing' variable only appears in gap/padding fields)",
      "C": "To see who created the variable",
      "D": "To change the font size of the variable name"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'Focus' state in an accessible design system?",
    "options": {
      "A": "To help the designer concentrate",
      "B": "To provide a visual indicator for keyboard users navigating through interactive elements",
      "C": "To blur the background of a modal",
      "D": "To show which designer is currently editing a layer"
    },
    "answer": "B"
  },
  {
    "question": "Which Figma feature allows you to create a fixed navigation bar that stays visible even as the page content scrolls behind it?",
    "options": {
      "A": "Auto Layout",
      "B": "Scroll Behavior: Fixed (Stay in place)",
      "C": "Clip Content",
      "D": "Absolute Positioning"
    },
    "answer": "B"
  },
  {
    "question": "In Figma Variables, what is a 'Collection'?",
    "options": {
      "A": "A group of design files",
      "B": "A set of related variables (e.g., a 'Color' collection or a 'Spacing' collection) within a single file",
      "C": "A list of all plugins installed",
      "D": "A gallery of user-generated components"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'Reset Scroll Position' checkbox do in a prototype interaction?",
    "options": {
      "A": "It stops the user from scrolling",
      "B": "It ensures the new frame starts at the top of the screen instead of maintaining the previous scroll depth",
      "C": "It clears the browser cache",
      "D": "It scrolls the user back to the home page"
    },
    "answer": "B"
  },
  {
    "question": "How do 'Modes' in Variables assist with Multi-brand design systems?",
    "options": {
      "A": "They allow you to change the logo automatically",
      "B": "They allow a single component to switch between different brand values (colors, spacing) by changing the mode on its parent frame",
      "C": "They prevent other brands from seeing your design",
      "D": "They increase the rendering speed of variants"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary function of 'Plugin API' for Figma developers?",
    "options": {
      "A": "To build mobile apps inside Figma",
      "B": "To create custom tools that automate repetitive tasks or integrate Figma with external data/services",
      "C": "To sell designs to other users",
      "D": "To track user keyboard shortcuts"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Layout Grid' snapping?",
    "options": {
      "A": "When the grid disappears",
      "B": "A feature that causes objects to align automatically with the edges of your layout grid columns or rows when moved",
      "C": "A tool to measure the distance between grids",
      "D": "A way to color the grid lines"
    },
    "answer": "B"
  },
  {
    "question": "In Dev Mode, what does 'Annotations' allow designers to do?",
    "options": {
      "A": "Draw emojis on the design",
      "B": "Provide specific implementation notes or documentation directly attached to components for developers to see",
      "C": "Write personal notes that are hidden from everyone",
      "D": "Highlight spelling errors in the UI"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Main Component' icon color in the Layers panel when it is published in a library?",
    "options": {
      "A": "Blue",
      "B": "Purple",
      "C": "Green",
      "D": "Orange"
    },
    "answer": "B"
  },
  {
    "question": "Which tool would you use to create 'Touch Target' annotations to ensure buttons meet minimum size requirements for mobile (e.g., 44x44px)?",
    "options": {
      "A": "The Slice Tool",
      "B": "Redlines/Accessibility Plugins or the Measure Tool in Dev Mode",
      "C": "The Pen Tool",
      "D": "Auto Layout Padding"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary purpose of 'Instance Swap' properties in a Figma component?",
    "options": {
      "A": "To change the background color of the component",
      "B": "To allow users to easily replace a specific sub-component (like an icon) with another one from the library",
      "C": "To convert an instance back into a frame",
      "D": "To move an instance to a different page"
    },
    "answer": "B"
  },
  {
    "question": "In the context of Figma Variables, what is 'Aliasing'?",
    "options": {
      "A": "Using a fake name for a component",
      "B": "Linking one variable's value to another variable (e.g., Brand-Color-1 links to Primary-Button-Fill)",
      "C": "Hiding a variable from developers",
      "D": "Creating a shortcut for a plugin"
    },
    "answer": "B"
  },
  {
    "question": "Which feature allows you to show or hide layers within a component instance based on a simple toggle in the properties panel?",
    "options": {
      "A": "Text Property",
      "B": "Boolean Property",
      "C": "Variant Property",
      "D": "Layer Mask"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Inspect' mode in Figma's Dev Mode specifically designed for?",
    "options": {
      "A": "Finding spelling errors in the UI",
      "B": "Allowing developers to view measurements, grab CSS/Swift/Kotlin code, and export assets efficiently",
      "C": "Editing the vector paths of a logo",
      "D": "Recording user testing sessions"
    },
    "answer": "B"
  },
  {
    "question": "When building a Design System, what does 'Atomic Design' help structure?",
    "options": {
      "A": "The speed of the cloud sync",
      "B": "A hierarchy of components starting from Atoms (icons/buttons) to Molecules, Organisms, and Templates",
      "C": "The resolution of the exported images",
      "D": "The number of users allowed in a file"
    },
    "answer": "B"
  },
  {
    "question": "Which trigger is most appropriate for a 'ToolTip' that appears when a user's mouse rests on an icon?",
    "options": {
      "A": "On Click",
      "B": "While Hovering",
      "C": "After Delay",
      "D": "On Drag"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Layout Grid' column type 'Stretch' used for?",
    "options": {
      "A": "To make the grid lines thicker",
      "B": "To ensure the grid columns expand and contract proportionally with the parent frame's width",
      "C": "To center the grid in the middle of the screen",
      "D": "To fix the grid to a specific pixel width"
    },
    "answer": "B"
  },
  {
    "question": "In Figma Prototyping, what does 'Preserve Scroll Position' do during a navigation?",
    "options": {
      "A": "It stops the user from scrolling on the next screen",
      "B": "It keeps the vertical/horizontal scroll position at the same level when transitioning between two frames",
      "C": "It saves the scroll history to a CSV file",
      "D": "It resets the view to the top of the page"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Library Analytics' report useful for?",
    "options": {
      "A": "Measuring the designer's typing speed",
      "B": "Understanding how many files are using a specific component and which components are frequently 'detached'",
      "C": "Tracking the total number of files in the organization",
      "D": "Calculating the time spent in meetings"
    },
    "answer": "B"
  },
  {
    "question": "Which action allows you to send a user to an external website from a Figma prototype?",
    "options": {
      "A": "Navigate To",
      "B": "Open Link",
      "C": "Open Overlay",
      "D": "Swap Overlay"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Base Component' (or Master) strategy?",
    "options": {
      "A": "Deleting all components before launch",
      "B": "Creating a hidden 'private' component that acts as a single source of truth for multiple public variants",
      "C": "Using only one color for the whole system",
      "D": "Naming the first component 'Master'"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Auto Layout Wrap' used for?",
    "options": {
      "A": "To wrap text around an image",
      "B": "To allow elements in a row to automatically move to a new line when they run out of space (responsive design)",
      "C": "To group elements into a circle",
      "D": "To hide elements that are too large"
    },
    "answer": "B"
  },
  {
    "question": "Which feature in Dev Mode allows a designer to 'mark' specific properties for developer attention?",
    "options": {
      "A": "Selection Colors",
      "B": "Dev Mode Annotations",
      "C": "Layout Grids",
      "D": "Smart Animate"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Fill Container' do inside an Auto Layout parent?",
    "options": {
      "A": "It keeps the object at a fixed size",
      "B": "It forces the object to stretch and fill all available space in its parent container",
      "C": "It adds a background color to the container",
      "D": "It centers the object"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Variable Mode' primarily used for in multi-themed applications?",
    "options": {
      "A": "To create different languages for the UI",
      "B": "To instantly switch a design between themes (e.g., Light vs Dark or Brand A vs Brand B) using the same variables",
      "C": "To change the font size of the whole file",
      "D": "To restrict user editing access"
    },
    "answer": "B"
  },
  {
    "question": "What is the result of using a 'Mathematical Expression' in a Figma variable (e.g., #CartCount + 1)?",
    "options": {
      "A": "It renames the layer to the result",
      "B": "It allows the prototype to dynamically update numerical values based on user interactions",
      "C": "It changes the color of the text to red",
      "D": "It creates a new variant of the component"
    },
    "answer": "B"
  },
  {
    "question": "In Figma Variables, what does 'Scoping' a color to 'Frame Fill' ensure?",
    "options": {
      "A": "The color is only visible to the owner",
      "B": "The variable will only appear in the color picker for Frame backgrounds, not for text or strokes",
      "C": "The color becomes transparent",
      "D": "The variable is deleted after use"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'State Management' benefit of using Variables in Prototyping?",
    "options": {
      "A": "It records the user's screen during the test",
      "B": "It allows the prototype to remember user choices (like a selected checkbox) across different frames",
      "C": "It speeds up the loading time of images",
      "D": "It automatically generates a user flow diagram"
    },
    "answer": "B"
  },
  {
    "question": "Which Dev Mode feature allows a developer to see the specific 'Diff' (changes) between two versions of a design?",
    "options": {
      "A": "Inspect Tab",
      "B": "Versions / Compare Changes",
      "C": "Asset Export",
      "D": "Layout Grid"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Ghosting' or 'Skeleton Screens' in UX design, and how are they typically built in Figma?",
    "options": {
      "A": "Hiding layers from other designers",
      "B": "Creating simplified, low-fidelity versions of components to indicate content is loading",
      "C": "A bug where layers disappear",
      "D": "A type of background blur"
    },
    "answer": "B"
  },
  {
    "question": "How do you trigger a 'Navigate To' action based on a specific numerical variable value reaching a limit?",
    "options": {
      "A": "By using an 'If/Else' conditional statement within the Prototype interaction",
      "B": "By setting the layer to 'Hidden'",
      "C": "By renaming the frame to 'Limit'",
      "D": "By using the Pen tool to draw a line"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Multi-edit' in Figma?",
    "options": {
      "A": "Many people editing one file",
      "B": "A feature that allows you to select and edit multiple matching layers across different frames simultaneously",
      "C": "Editing the CSS and the Vector at the same time",
      "D": "A plugin for batch renaming"
    },
    "answer": "B"
  },
  {
    "question": "Which Figma feature is best for creating 'Fixed' table headers that don't move when the table rows scroll?",
    "options": {
      "A": "Group",
      "B": "Scroll Behavior: Sticky",
      "C": "Clip Content",
      "D": "Auto Layout Wrap"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Plugin manifest.json' used for in Figma development?",
    "options": {
      "A": "To list all fonts in the design",
      "B": "To define the plugin's metadata, permissions, and entry points for the Figma API",
      "C": "To store the user's password",
      "D": "To compress the design file"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Hidden' scoping in Variables?",
    "options": {
      "A": "Hiding the variable from everyone",
      "B": "Preventing a variable from being seen in the published library while still using it internally for aliasing",
      "C": "Making the layer invisible",
      "D": "A way to encrypt design data"
    },
    "answer": "B"
  },
  {
    "question": "In a Design System, what is a 'Recipe' component?",
    "options": {
      "A": "A list of colors",
      "B": "A specific combination of base components (atoms) pre-configured for a common use case",
      "C": "A plugin for cooking",
      "D": "The CSS code for a button"
    },
    "answer": "B"
  },
  {
    "question": "Which boolean operation is non-destructive, allowing you to edit the original shapes later?",
    "options": {
      "A": "Flatten",
      "B": "Boolean Groups (Union, Subtract, etc.)",
      "C": "Outline Stroke",
      "D": "Masking"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Individual Corner Radius' allow you to do on a rectangle?",
    "options": {
      "A": "Make the rectangle a circle",
      "B": "Set a different roundness for each of the four corners independently",
      "C": "Hide the corners",
      "D": "Rotate only the corners"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Private' components (prefixed with . or _)?",
    "options": {
      "A": "They are only visible to the Admin",
      "B": "They are used within the library file but are not published to the team-wide Assets panel",
      "C": "They require a password to view",
      "D": "They are excluded from the file size"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Figma Slides' (introduced in 2024)?",
    "options": {
      "A": "A tool for creating sliding doors",
      "B": "A dedicated presentation tool within Figma designed for storytelling and sharing design work",
      "C": "An animation type in prototyping",
      "D": "A way to scroll between pages"
    },
    "answer": "B"
  },
  {
    "question": "In Figma's advanced prototyping, what is a 'String Variable' primarily used for?",
    "options": {
      "A": "To measure the length of a vector path",
      "B": "To dynamically change text content (e.g., a username or a label) based on user interaction",
      "C": "To tie multiple components together with a rope",
      "D": "To set the thickness of a font stroke"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'Set Variable' action allow you to do during a prototype interaction?",
    "options": {
      "A": "Change the name of a file",
      "B": "Update the value of a variable (e.g., Incrementing a 'Count' number when a button is clicked)",
      "C": "Lock a variable so it cannot be changed",
      "D": "Assign a variable to a different designer"
    },
    "answer": "B"
  },
  {
    "question": "What is the benefit of 'Variable Aliasing' for Design Tokens?",
    "options": {
      "A": "It makes the file size smaller",
      "B": "It allows a semantic token (e.g., 'button-hover') to point to a primitive token (e.g., 'blue-600'), making global updates easier",
      "C": "It hides the original color from developers",
      "D": "It translates the design into different languages automatically"
    },
    "answer": "B"
  },
  {
    "question": "Which Figma feature helps you check contrast ratios and screen reader labels directly in the design?",
    "options": {
      "A": "Auto Layout",
      "B": "Accessibility (A11y) Plugins and Annotations",
      "C": "Smart Animate",
      "D": "Component Variants"
    },
    "answer": "B"
  },
  {
    "question": "What is 'State Management' in a Figma prototype?",
    "options": {
      "A": "Managing the legal status of the design company",
      "B": "Using variables to track and maintain the 'current state' (e.g., logged in, item in cart) across multiple screens",
      "C": "The order of states in a dropdown menu",
      "D": "The history of file versions"
    },
    "answer": "B"
  },
  {
    "question": "Which action in a prototype would you use to 'reset' a variable to its initial value?",
    "options": {
      "A": "Navigate To",
      "B": "Set Variable (using the original value in the expression)",
      "C": "Close Overlay",
      "D": "Back"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Figma Config'?",
    "options": {
      "A": "The settings menu in the app",
      "B": "Figma's annual global design conference where new features are often announced",
      "C": "A plugin for configuration management",
      "D": "A file type for exporting settings"
    },
    "answer": "B"
  },
  {
    "question": "In a 'Many-to-Many' variable relationship, what is a 'Mode' useful for?",
    "options": {
      "A": "Switching between design and code view",
      "B": "Switching between different themes (e.g., Light vs Dark) by changing the value set of the variables in a frame",
      "C": "Turning on the flashlight on your phone",
      "D": "Measuring the distance between objects"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Sandbox' environment in Figma Plugin development?",
    "options": {
      "A": "A place to play with shapes",
      "B": "An isolated environment where plugin code runs to ensure it doesn't crash the main Figma application",
      "C": "A specific folder for draft designs",
      "D": "A plugin for designing playgrounds"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Individual Padding' allow you to do in Auto Layout?",
    "options": {
      "A": "Set the same padding for everyone on the team",
      "B": "Set different padding values for the top, right, bottom, and left sides of a frame",
      "C": "Remove padding from all components",
      "D": "Add padding to a single letter of text"
    },
    "answer": "B"
  },
  {
    "question": "Which tool would you use to create a 'Mask' in Figma?",
    "options": {
      "A": "Pen Tool",
      "B": "The 'Use as Mask' button (Ctrl+Alt+M / Cmd+Opt+M) after placing a shape behind an image",
      "C": "The Slice Tool",
      "D": "The Eraser Tool"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Design Ops' (Design Operations)?",
    "options": {
      "A": "Operating the Figma software",
      "B": "The practice of optimizing design processes, people, and tools to scale design's impact within an organization",
      "C": "The surgical removal of design flaws",
      "D": "A specific department that only handles vector icons"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Redlining' in the handoff process?",
    "options": {
      "A": "Drawing red lines all over the design",
      "B": "The process of annotating designs with exact measurements, specs, and spacing for developers",
      "C": "Checking for spelling errors in red",
      "D": "Marking a design as rejected"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Figma AI' (introduced in 2024) primarily designed to help with?",
    "options": {
      "A": "Replacing designers entirely",
      "B": "Assisting with tasks like layer naming, basic component generation, and searching for similar designs",
      "C": "Calculating the company's taxes",
      "D": "Answering emails automatically"
    },
    "answer": "B"
  },
  {
    "question": "Which feature allows you to 'Lock' a specific layer so it cannot be selected or moved on the canvas?",
    "options": {
      "A": "Hide (Eye icon)",
      "B": "Lock (Padlock icon)",
      "C": "Flatten",
      "D": "Group"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Clone' or 'Mirroring' technique in complex Figma components?",
    "options": {
      "A": "Copying a file to another account",
      "B": "Using a single 'Base' component as a nested layer in multiple variants to ensure global updates to structure and layout",
      "C": "Reflecting an image horizontally",
      "D": "Making the Figma app window appear on two screens"
    },
    "answer": "B"
  },
  {
    "question": "In a multi-file Design System, what is the best practice for managing 'Global' vs. 'Component-specific' variables?",
    "options": {
      "A": "Put all variables in every file",
      "B": "House global primitives in a Foundation library and alias them to specific semantic variables in component libraries",
      "C": "Use only local variables to avoid syncing issues",
      "D": "Delete all primitive variables once the design is finished"
    },
    "answer": "B"
  },
  {
    "question": "Which Figma feature allows you to ensure a 'Header' component spans the full width of a frame but keeps its internal navigation items centered?",
    "options": {
      "A": "Standard Grouping",
      "B": "Auto Layout with 'Space Between' and 'Fill Container' constraints",
      "C": "Flattening the header",
      "D": "Using a background image"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Layout Grid' column type 'Left' or 'Right' with a fixed width used for?",
    "options": {
      "A": "Creating responsive websites",
      "B": "Creating fixed-width sidebars or navigation panels that do not resize with the frame",
      "C": "Making the grid invisible",
      "D": "Setting the font alignment"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Instance Swap' property benefit for designers using a Design System?",
    "options": {
      "A": "It allows them to change the text of a button",
      "B": "It allows them to swap icons or sub-elements within a component without detaching the instance",
      "C": "It renames the component automatically",
      "D": "It deletes the original component"
    },
    "answer": "B"
  },
  {
    "question": "How does 'Code Connect' in Dev Mode impact the handoff between design and engineering?",
    "options": {
      "A": "It writes the code for the designer",
      "B": "It displays real production code snippets (React, etc.) for a component instead of generic CSS",
      "C": "It records the meeting audio",
      "D": "It translates the design into 10 languages"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Variable Logic' in a prototype?",
    "options": {
      "A": "A logical way to name variables",
      "B": "The use of 'If/Else' conditions and expressions to create dynamic, state-aware prototypes (e.g., login validation)",
      "C": "Changing colors based on the weather",
      "D": "The order variables appear in the sidebar"
    },
    "answer": "B"
  },
  {
    "question": "In Figma Variables, what is 'Aliasing'?",
    "options": {
      "A": "Giving a designer a nickname",
      "B": "Connecting one variable to another so that changes to the 'source' variable update all linked 'alias' variables",
      "C": "Hiding a variable name from developers",
      "D": "Creating a secondary shortcut"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Library Analytics' for a Design System Manager?",
    "options": {
      "A": "To see who is designing the most",
      "B": "To track component adoption, find detached instances, and understand which parts of the system need improvement",
      "C": "To count the number of pixels in the file",
      "D": "To monitor the server's CPU usage"
    },
    "answer": "B"
  },
  {
    "question": "Which action allows you to change a variable's value when a user clicks an element in a prototype?",
    "options": {
      "A": "Navigate To",
      "B": "Set Variable",
      "C": "Open Overlay",
      "D": "Scroll To"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Component Property Scoping'?",
    "options": {
      "A": "Searching for properties",
      "B": "Restricting which properties can be controlled at the instance level vs. the main component level",
      "C": "Cleaning the computer screen",
      "D": "A way to hide layers"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Figma Slides' primarily used for?",
    "options": {
      "A": "Creating a playground slide",
      "B": "A specialized tool for creating and delivering presentations directly within the Figma ecosystem",
      "C": "Making elements slide across the screen",
      "D": "A type of animation trigger"
    },
    "answer": "B"
  },
  {
    "question": "In a design system, what is 'Visual Regression Testing'?",
    "options": {
      "A": "Testing the designer's eyesight",
      "B": "Checking if new component updates accidentally break existing designs using automated tools",
      "C": "Deleting old designs",
      "D": "A way to revert to older file versions"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Dev Mode Plugins' useful for?",
    "options": {
      "A": "Drawing shapes in dev mode",
      "B": "Extending Figma's developer handoff capabilities with custom tools for documentation, Jira integration, or code generation",
      "C": "Recording the developer's screen",
      "D": "Changing the color of the dev mode UI"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Absolute Positioning' inside an Auto Layout frame allow?",
    "options": {
      "A": "It moves the element to a different file",
      "B": "It allows an element to be placed anywhere in the frame without being affected by the Auto Layout flow",
      "C": "It locks the element's color",
      "D": "It prevents the element from being seen"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary benefit of using 'Min/Max Dimensions' in a design system component?",
    "options": {
      "A": "To limit the number of colors used",
      "B": "To ensure components remain functional and visually stable when used in fluid or responsive layouts",
      "C": "To decrease the file size of the component",
      "D": "To prevent developers from editing the code"
    },
    "answer": "B"
  },
  {
    "question": "In a professional Design System, what is 'Visual Regression Testing'?",
    "options": {
      "A": "Testing if the designer needs glasses",
      "B": "An automated process to detect unintended visual changes in components after an update or publish",
      "C": "Reverting the design to a version from a year ago",
      "D": "Checking the color contrast manually"
    },
    "answer": "B"
  },
  {
    "question": "How does the 'Context' feature in Dev Mode help a developer?",
    "options": {
      "A": "It records the meeting notes for them",
      "B": "It provides information about which section or frame the current selection belongs to, helping them understand the hierarchy",
      "C": "It translates the design into 10 different languages",
      "D": "It predicts when the developer will finish the code"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Design Token Syncing' between Figma and GitHub/GitLab?",
    "options": {
      "A": "A way to back up images to GitHub",
      "B": "Automating the export of variable values into code-ready formats (JSON/SCSS) so design changes update the codebase instantly",
      "C": "Using GitHub to track who edited a layer",
      "D": "Creating a website for the design system"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Sandbox' in the context of Figma Plugin development?",
    "options": {
      "A": "A folder for deleted designs",
      "B": "An isolated environment where plugin code runs to prevent it from accessing sensitive user data or crashing Figma",
      "C": "A playground for children",
      "D": "The main canvas where you draw shapes"
    },
    "answer": "B"
  },
  {
    "question": "Which Figma feature allows a design system manager to see which components are the most and least used across the entire organization?",
    "options": {
      "A": "The Layers Panel",
      "B": "Library Analytics",
      "C": "The Inspect Tab",
      "D": "Version History"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Slot-based Component' architecture primarily used for?",
    "options": {
      "A": "To create a gambling app",
      "B": "To build flexible 'wrapper' components (like Modals or Drawers) that allow for any content to be injected into a specific area",
      "C": "To group icons alphabetically",
      "D": "To limit the number of layers in a file"
    },
    "answer": "B"
  },
  {
    "question": "What is the function of the 'manifest.json' file in a Figma plugin?",
    "options": {
      "A": "To list the colors used in the plugin",
      "B": "To provide the metadata, permissions, and script entry points for the plugin to function within Figma",
      "C": "To store the designer's personal settings",
      "D": "To compress the plugin's code"
    },
    "answer": "B"
  },
  {
    "question": "In Advanced Prototyping, what is a 'Literal'?",
    "options": {
      "A": "A fixed value (like the number 10 or the string 'Hello') used directly in an expression or conditional",
      "B": "A person who follows rules exactly",
      "C": "A type of component variant",
      "D": "An animation style"
    },
    "answer": "A"
  },
  {
    "question": "Which Dev Mode tool allows developers to see the exact spacing and margin between elements by hovering?",
    "options": {
      "A": "The Pen Tool",
      "B": "The Inspect Tool / Measurement",
      "C": "The Slice Tool",
      "D": "The Paint Bucket"
    },
    "answer": "B"
  },
  {
    "question": "What is 'W3C Design Token' standard and why does Figma support it?",
    "options": {
      "A": "It's a way to name layers",
      "B": "It's a standardized format for tokens that ensures compatibility between different design tools and development environments",
      "C": "It's a tool for measuring screen brightness",
      "D": "It's a type of layout grid"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Private Components' (those starting with . or _)?",
    "options": {
      "A": "They are hidden from everyone but the owner",
      "B": "They are used for internal building within a library but are not published to the end-users' Assets panel",
      "C": "They are encrypted components",
      "D": "They are only for the developer's eyes"
    },
    "answer": "B"
  },
  {
    "question": "How do 'Modes' in Variables facilitate 'Density' testing (e.g., Compact vs. Spacious layouts)?",
    "options": {
      "A": "By automatically resizing all images",
      "B": "By allowing a collection of spacing and sizing variables to have different values for each 'Density' mode",
      "C": "By changing the font weight to bold",
      "D": "By deleting unused spacing"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Instance Swapping' through the properties panel help maintain?",
    "options": {
      "A": "The file's version history",
      "B": "Component overrides and internal spacing when switching between similar sub-components (like icons)",
      "C": "The user's login session",
      "D": "The color of the canvas"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Box Model' view in Figma's Dev Mode?",
    "options": {
      "A": "A way to view 3D boxes",
      "B": "A visualization of an element's dimensions, padding, borders, and margins, matching web development standards",
      "C": "A tool to pack files for export",
      "D": "A specific type of layout grid"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary architectural purpose of a 'Base' or 'Master' component that is never used directly in designs?",
    "options": {
      "A": "To save storage space on the Figma cloud",
      "B": "To act as a single source of truth for structural layout changes across all public variants",
      "C": "To hide the design from unauthorized viewers",
      "D": "To allow for faster PNG exports"
    },
    "answer": "B"
  },
  {
    "question": "In Advanced Prototyping, which operator is used to check if a value is 'Not Equal' to another in a conditional statement?",
    "options": {
      "A": "==",
      "B": "!=",
      "C": "<>",
      "D": "NOT"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Variable Scoping' specifically used for in a mature Design System?",
    "options": {
      "A": "To search for variables across different teams",
      "B": "To restrict specific variables so they only appear in relevant fields (e.g., Corner Radius vs. Text Color)",
      "C": "To see the history of who edited the variable",
      "D": "To measure the performance of the file"
    },
    "answer": "B"
  },
  {
    "question": "Which Figma feature allows a designer to create a button that automatically changes from 'Enabled' to 'Loading' based on a variable change?",
    "options": {
      "A": "Standard Overlays",
      "B": "Interactive Components tied to Variable States",
      "C": "Smart Animate on a single frame",
      "D": "Auto Layout resizing"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Mode Mapping' in the context of multi-brand design systems?",
    "options": {
      "A": "Assigning different designers to different brands",
      "B": "Linking variable collections to specific frames so they switch brand values automatically (e.g., Brand A vs Brand B)",
      "C": "Creating a map of the file structure",
      "D": "Automatically generating logos for different modes"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Plugin UI' built with in Figma development?",
    "options": {
      "A": "C++",
      "B": "Standard Web Technologies (HTML, CSS, JavaScript/TypeScript)",
      "C": "Python",
      "D": "Figma's internal vector language"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'Absolute Position' feature within an Auto Layout frame allow a designer to achieve?",
    "options": {
      "A": "It moves the object to the center of the canvas",
      "B": "It allows an object to overlap others without being pushed by the Auto Layout flow (e.g., a notification badge)",
      "C": "It locks the X and Y coordinates relative to the screen",
      "D": "It prevents the object from being exported"
    },
    "answer": "B"
  },
  {
    "question": "In Dev Mode, what is 'Code Connect' primarily used for?",
    "options": {
      "A": "To chat with other developers",
      "B": "To link Figma components to actual code snippets from a private design system repository (e.g., React or Swift)",
      "C": "To automatically push designs to GitHub",
      "D": "To see the file's version history in code format"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Box Model' visualization in Figma’s Inspect panel used to communicate to developers?",
    "options": {
      "A": "The weight of the fonts used",
      "B": "The dimensions, padding, borders, and margins of an element as they relate to web development standards",
      "C": "A 3D view of the component",
      "D": "The number of layers inside a group"
    },
    "answer": "B"
  },
  {
    "question": "Which Figma action is used to create a 'Mask' out of a shape?",
    "options": {
      "A": "Ctrl + G",
      "B": "Ctrl + Alt + M (Win) / Cmd + Opt + M (Mac)",
      "C": "Right-click > Flatten",
      "D": "Shift + A"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'W3C Design Token' format support in Figma?",
    "options": {
      "A": "A standardized JSON format that allows design tokens to be shared across different design and development tools",
      "B": "A special font type for web accessibility",
      "C": "A method to compress PNG files",
      "D": "A way to encrypt private Figma files"
    },
    "answer": "A"
  },
  {
    "question": "In Auto Layout 5.0, what does 'Wrap' allow a row of elements to do when the parent frame is resized?",
    "options": {
      "A": "It stretches the elements to fill the width",
      "B": "It automatically moves elements to the next line (vertical) when horizontal space is depleted",
      "C": "It hides the overflowing elements",
      "D": "It scales the font size down to fit the row"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary function of 'Variables' in the context of 'Multi-Mode' prototyping?",
    "options": {
      "A": "To create different versions of the same logo",
      "B": "To allow a single design to toggle between different themes (e.g., Light vs Dark) by switching variable value sets",
      "C": "To record the user's voice during testing",
      "D": "To change the speed of a 'Smart Animate' transition"
    },
    "answer": "B"
  },
  {
    "question": "Which Figma feature is used to define 'Min-Width' constraints on an element within a responsive layout?",
    "options": {
      "A": "Standard Constraints",
      "B": "The 'Min-Width' field in the Design panel (under the Frame or Auto Layout section)",
      "C": "Layout Grids",
      "D": "Absolute Positioning"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Instance Overriding' in Figma?",
    "options": {
      "A": "Deleting a component instance",
      "B": "The ability to change properties like color, text, or strokes in an instance without breaking its link to the Main Component",
      "C": "Renaming a component after it's been published",
      "D": "Moving a component from one page to another"
    },
    "answer": "B"
  },
  {
    "question": "How do 'Number Variables' help in creating a consistent spacing system?",
    "options": {
      "A": "By allowing designers to define fixed spacing values (e.g., 8px, 16px) that can be reused across all Auto Layout gaps and paddings",
      "B": "By automatically calculating the area of a shape",
      "C": "By converting text into numbers",
      "D": "By limiting the number of layers in a file"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Component Property' nesting?",
    "options": {
      "A": "Putting components inside folders",
      "B": "Exposing the properties of a nested sub-component on the top-level parent component's property panel for easier access",
      "C": "Deleting properties from a component",
      "D": "Creating a copy of a component"
    },
    "answer": "B"
  },
  {
    "question": "Which tool would you use to 'Slice' a specific area of the canvas for export without affecting the actual layout?",
    "options": {
      "A": "Frame Tool",
      "B": "Slice Tool (S)",
      "C": "Pen Tool",
      "D": "Rectangle Tool"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Individual Stroke' allow you to do in the design panel?",
    "options": {
      "A": "Apply a stroke to only one side (Top, Bottom, Left, or Right) of an element",
      "B": "Change the stroke color for every layer",
      "C": "Make the stroke invisible",
      "D": "Create a dashed line"
    },
    "answer": "A"
  },
  {
    "question": "In Figma, what is 'Section' (Shift + S) primarily used for during developer handoff?",
    "options": {
      "A": "To crop images",
      "B": "To group related screens and mark them with a 'Ready for Dev' status",
      "C": "To create a 3D effect",
      "D": "To hide private notes from developers"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary function of 'Library Swap' when moving from a 'Staging' library to a 'Production' library?",
    "options": {
      "A": "It deletes all components in the original file",
      "B": "It replaces all component instances in a file with matching components from a different library while maintaining overrides",
      "C": "It changes the color palette to grayscale",
      "D": "It renames all layers to match a developer's naming convention"
    },
    "answer": "B"
  },
  {
    "question": "In Figma Variables, what does 'Boolean' scoping for a variable allow you to control dynamically?",
    "options": {
      "A": "The numerical width of an object",
      "B": "The visibility (True/False) of layers or the activation of component properties",
      "C": "The hex code of a fill",
      "D": "The font weight of a text layer"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Variable Publishing Scoping' used for in large-scale design systems?",
    "options": {
      "A": "To limit who can see the variables",
      "B": "To ensure certain 'Internal/Primitive' variables are hidden from the user-facing library while remaining functional for aliasing",
      "C": "To translate variables into CSS",
      "D": "To count how many times a variable is used"
    },
    "answer": "B"
  },
  {
    "question": "Which Figma API capability allows for 'Headless Design System' workflows?",
    "options": {
      "A": "The ability to read and write Variable values programmatically, allowing syncing between Figma and external code repositories",
      "B": "A feature that removes the UI of Figma for faster performance",
      "C": "A tool that generates designs from a command line",
      "D": "Automatic screenshot generation"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Token Aliasing' specifically useful for in a multi-brand architecture?",
    "options": {
      "A": "Using a nickname for designers",
      "B": "Linking a semantic token (e.g., 'action-primary') to different primitive tokens (e.g., 'blue-500' vs 'red-500') based on the theme mode",
      "C": "Hiding the original color hex code from developers",
      "D": "Reducing the number of layers in a file"
    },
    "answer": "B"
  },
  {
    "question": "How does 'Focus Order' annotation in Figma assist in accessible design handoff?",
    "options": {
      "A": "It helps the designer focus on their work",
      "B": "It defines the sequential order in which a screen reader or keyboard user navigates through interactive elements",
      "C": "It locks the screen so the user can only see one button",
      "D": "It increases the contrast of the active element"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Component Sets' in Figma?",
    "options": {
      "A": "To group different components like buttons and inputs together",
      "B": "To group multiple variants of the same component (e.g., Primary, Secondary, Hover) into a single logical unit",
      "C": "To create a folder for all images",
      "D": "To export multiple layers as a single PNG"
    },
    "answer": "B"
  },
  {
    "question": "In Auto Layout, what is the 'Stroke exclusion' setting used for?",
    "options": {
      "A": "To hide the stroke from the design",
      "B": "To decide whether an object's stroke should be included in its overall dimensions for spacing and alignment",
      "C": "To change the color of the stroke based on the background",
      "D": "To prevent the stroke from being exported"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Code Connect' for Figma's Dev Mode?",
    "options": {
      "A": "A chat tool for developers",
      "B": "A feature that maps Figma components directly to production code components (like React or SwiftUI) for a more accurate handoff",
      "C": "A way to write CSS inside Figma",
      "D": "A plugin that translates designs into Python"
    },
    "answer": "B"
  },
  {
    "question": "What does 'Instance Swapping' through the 'Properties' panel help preserve that manual swapping does not?",
    "options": {
      "A": "The file name",
      "B": "The overrides (like color or text changes) of the nested component being swapped",
      "C": "The user's login session",
      "D": "The original creator's name"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary benefit of 'Number Variable Aliasing' in a responsive design system?",
    "options": {
      "A": "It automatically changes the font family to match the screen size",
      "B": "It allows a single 'Gap' variable to point to different numerical values (e.g., 16px vs 24px) based on the current Mode (Mobile vs Desktop)",
      "C": "It renames all layers to match the pixel count",
      "D": "It prevents the designer from using decimal points"
    },
    "answer": "B"
  },
  {
    "question": "When using 'Conditional Logic' in a prototype, which action allows you to check if a specific variable equals a string (e.g., if Status == 'Logged_In')?",
    "options": {
      "A": "Set Variable",
      "B": "Conditional (If/Else)",
      "C": "Navigate To",
      "D": "Swap Overlay"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'Absolute Position' toggle do to an element inside an Auto Layout frame?",
    "options": {
      "A": "It moves the element to the center of the canvas",
      "B": "It removes the element from the Auto Layout flow, allowing it to be placed anywhere in the frame without affecting its siblings",
      "C": "It locks the element's width and height",
      "D": "It forces the element to stay fixed during scrolling"
    },
    "answer": "B"
  },
  {
    "question": "In a professional design system, what is the 'Hidden' property of a variable collection used for?",
    "options": {
      "A": "Hiding the design from developers",
      "B": "Preventing specific variables from appearing in the library search while still allowing them to be used for aliasing",
      "C": "Making the layer invisible in the prototype",
      "D": "Deleting the variable after the file is closed"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Code Connect' in Figma's Dev Mode specifically designed to bridge?",
    "options": {
      "A": "The gap between the designer's mouse and the screen",
      "B": "The gap between Figma components and actual production code (React, SwiftUI, etc.) stored in an external repository",
      "C": "The connection between two different Figma accounts",
      "D": "The speed of the internet connection"
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
    skill = "Figma"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
