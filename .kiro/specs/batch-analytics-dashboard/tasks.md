# Tasks: Batch Analytics Dashboard

## Task 1: Add metrics computation function and state

### Description
Add the `computeBatchMetrics` helper function, `hoveredCard` state, and `animateIn` state/effect to `ResultsAI.js`.

### Files to modify
- `frontend/src/pages/ResultsAI.js`

### Steps
- [ ] 1.1 Add `hoveredCard` state (`useState(null)`) near the existing state declarations at the top of the component
- [ ] 1.2 Add `animateIn` state (`useState(false)`) near the existing state declarations
- [ ] 1.3 Add `useEffect` that resets and triggers `animateIn` when `viewMode` changes to 'detail' or `selectedRole` changes
- [ ] 1.4 Add `computeBatchMetrics(rows, tabType)` function after the existing `isPass` and `getScoreValue` helpers. It should return `{ total, passed, failed, onHold, avgScore, completionRate }` using the logic from the design document
- [ ] 1.5 Add `handleCardMouseMove(e, index)` function that computes tilt rotation from cursor position relative to card center

## Task 2: Implement the Analytics Panel JSX with 3D styling

### Description
Add the cinematic analytics panel with 3D metric cards inside the detail view section, positioned after the batch header and before the filter controls.

### Files to modify
- `frontend/src/pages/ResultsAI.js`

### Steps
- [ ] 2.1 Add a `<style>` tag inside the detail view block containing the `@keyframes batchCardFloat` animation definition
- [ ] 2.2 Add the analytics panel container `<div>` with the cinematic gradient background (`linear-gradient(135deg, #0f0c29, #302b63, #24243e)`), border-radius, padding, and fade-in transition tied to `animateIn` state
- [ ] 2.3 Add a panel title/header row inside the container (e.g., "Batch Analytics" with a subtle icon)
- [ ] 2.4 Add the CSS grid wrapper with `perspective: 1000px`, `gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))'`, and `gap: '1.2rem'`
- [ ] 2.5 Render 6 Metric Cards (Total Participants, Passed, Failed, On-Hold, Average Score, Completion Rate) each with: glassmorphism background, Font Awesome icon, metric value, metric label, accent color, floating animation, and staggered entry animation delay
- [ ] 2.6 Apply 3D transform styles to each card: `transform` with perspective rotation at rest, `transition: all 300ms ease`, and conditional hover transform/shadow using `hoveredCard` state
- [ ] 2.7 Attach `onMouseMove`, `onMouseEnter`, and `onMouseLeave` handlers to each card for interactive tilt effect and glow border on hover

## Task 3: Integrate panel into the detail view render flow

### Description
Wire the analytics panel into the correct position in the existing JSX structure and ensure it receives computed metrics.

### Files to modify
- `frontend/src/pages/ResultsAI.js`

### Steps
- [ ] 3.1 Call `computeBatchMetrics(allRows, activeTab)` to get the metrics object, placed after the `allRows` computation
- [ ] 3.2 Insert the analytics panel JSX block inside the `{viewMode === 'detail' && (...)}` section, after the existing batch header div (the one with the back button and "Batch Results" title) and before the filter/sort controls
- [ ] 3.3 Ensure the panel only renders when `viewMode === 'detail'` and `selectedRole` is truthy
- [ ] 3.4 Verify that tab switching (activeTab changes) causes metrics to recalculate by confirming `allRows` depends on `activeTab` (already the case via `getDataForActiveContext`)

## Task 4: Test and verify the implementation

### Description
Verify the analytics panel renders correctly, metrics are accurate, and interactions work as expected.

### Steps
- [ ] 4.1 Verify the panel appears only in detail view mode and disappears when navigating back to overview
- [ ] 4.2 Verify all 6 metric cards display with correct values matching the table data below
- [ ] 4.3 Verify hover effects produce visible 3D tilt and glow on each card
- [ ] 4.4 Verify the staggered entrance animation plays when entering detail view
- [ ] 4.5 Verify responsive layout: cards reflow correctly when browser window is resized
- [ ] 4.6 Verify edge case: batch with zero candidates shows 0 counts and "N/A" for percentages
- [ ] 4.7 Verify the panel does not break existing functionality (back button, tab switching, table rendering, filters)
