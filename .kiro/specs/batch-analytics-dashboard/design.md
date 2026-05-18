# Design Document: Batch Analytics Dashboard

## Overview

This design describes the implementation of a cinematic, 3D-styled analytics dashboard panel that appears in the AI Interview Results page when viewing batch details. The panel computes and displays key metrics from existing batch data using interactive 3D-styled metric cards with hover effects and entrance animations.

## Architecture

### Component Structure

The feature is implemented as a single inline component section within the existing `ResultsAI.js` file, consistent with the current codebase pattern of using inline styles and no external component files for this page.

```
ResultsAI.js (existing)
├── Detail View Section (viewMode === 'detail')
│   ├── Back Button (existing)
│   ├── Batch Header (existing)
│   ├── ★ BatchAnalyticsPanel (NEW - inserted here)
│   ├── Filter/Sort Controls (existing)
│   └── Results Table (existing)
```

### Data Flow

```
groupedData[selectedRole] → getDataForActiveContext() → allRows
                                                          ↓
                                              computeBatchMetrics(allRows, activeTab)
                                                          ↓
                                              { total, passed, failed, onHold, avgScore, completionRate }
                                                          ↓
                                              Analytics Panel renders Metric Cards
```

## Detailed Design

### 1. Metrics Computation Function

A `computeBatchMetrics` helper function will be defined inside the `ResultsAI` component (after the existing `isPass` and `getScoreValue` helpers):

```javascript
const computeBatchMetrics = (rows, tabType) => {
    const total = rows.length;
    if (total === 0) return { total: 0, passed: 0, failed: 0, onHold: 0, avgScore: 'N/A', completionRate: 'N/A' };

    const onHold = rows.filter(r => r.status === 'On-Hold').length;
    const passed = rows.filter(r => isPass(r, tabType) && r.status !== 'On-Hold').length;
    const failed = total - passed - onHold;

    const scores = rows.map(r => getScoreValue(r));
    const avgScore = Math.round(scores.reduce((sum, s) => sum + s, 0) / total);

    const completed = rows.filter(r => r.completed_at || r.submitted_at).length;
    const completionRate = Math.round((completed / total) * 100);

    return { total, passed, failed, onHold, avgScore, completionRate };
};
```

### 2. Analytics Panel Rendering

The panel renders conditionally inside the `viewMode === 'detail'` block, after the existing batch header `<div>` and before the filter controls. It uses a `<style>` tag injected for keyframe animations (since inline styles cannot define `@keyframes`).

### 3. 3D Metric Card Component

Each metric card is rendered inline with:
- **Perspective container**: `perspective: 1000px` on the grid wrapper
- **Card transform**: `transform: rotateX(2deg) translateZ(0)` at rest
- **Hover state**: Managed via React `onMouseEnter`/`onMouseLeave` state, applying `rotateX(-5deg) rotateY(var) translateZ(20px)` and enhanced shadow
- **Floating animation**: A CSS `@keyframes float` animation applied via `animationName` reference

### 4. Interactive Hover Implementation

Since inline styles cannot use `:hover` pseudo-classes, hover effects are implemented using React state:

```javascript
const [hoveredCard, setHoveredCard] = useState(null);
```

Each card tracks mouse position relative to its center to compute tilt direction:

```javascript
const handleCardMouseMove = (e, index) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;  // -0.5 to 0.5
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    setHoveredCard({ index, rotateY: x * 15, rotateX: -y * 15 });
};
```

### 5. Entrance Animation

Cards use `opacity` and `transform` transitions triggered by a `useState` flag that flips after mount:

```javascript
const [animateIn, setAnimateIn] = useState(false);
useEffect(() => {
    if (viewMode === 'detail') {
        setAnimateIn(false);
        setTimeout(() => setAnimateIn(true), 50);
    }
}, [viewMode, selectedRole]);
```

Each card gets a staggered delay: `transitionDelay: ${index * 100}ms`.

### 6. Responsive Grid

```javascript
display: 'grid',
gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
gap: '1.2rem'
```

This naturally flows from 6 columns on wide screens down to fewer columns as viewport narrows, with `minmax(180px, 1fr)` ensuring cards never get too small.

### 7. Style Injection for Keyframes

A `<style>` element is rendered once inside the panel for the floating animation keyframes:

```html
<style>{`
  @keyframes batchCardFloat {
    0%, 100% { transform: translateY(0px) rotateX(2deg); }
    50% { transform: translateY(-4px) rotateX(1deg); }
  }
`}</style>
```

## Visual Design Specifications

### Color Palette

| Element | Value |
|---------|-------|
| Panel background | `linear-gradient(135deg, #0f0c29, #302b63, #24243e)` |
| Card background | `rgba(255, 255, 255, 0.05)` with `backdrop-filter: blur(10px)` |
| Card border | `1px solid rgba(255, 255, 255, 0.1)` |
| Total participants accent | `#60A5FA` (blue) |
| Passed accent | `#34D399` (green) |
| Failed accent | `#F87171` (red) |
| On-Hold accent | `#FBBF24` (amber) |
| Average score accent | `#A78BFA` (purple) |
| Completion rate accent | `#2DD4BF` (teal) |

### Card Dimensions

- Min width: 180px
- Padding: 1.5rem
- Border radius: 16px
- Icon size: 2rem

### Animations

- Float cycle: 3s ease-in-out infinite
- Hover transition: 300ms ease
- Entry stagger: 100ms per card
- Entry duration: 500ms

## Correctness Properties

### Property 1: Metric Count Invariant
For any batch data, `passed + failed + onHold` SHALL always equal `total`. This arithmetic invariant ensures no candidates are lost or double-counted.

### Property 2: Pass Count Consistency
For any set of candidate rows and tab type, the `passed` metric SHALL equal the count of rows where `isPass(row, tabType)` returns true AND `row.status !== 'On-Hold'`.

### Property 3: Average Score Bounded
For any non-empty batch, `avgScore` SHALL be a number between 0 and 100 inclusive.

### Property 4: Completion Rate Bounded
For any non-empty batch, `completionRate` SHALL be a number between 0 and 100 inclusive.

### Property 5: Zero Participants Edge Case
When the batch contains zero rows, all count metrics SHALL be 0 and percentage metrics SHALL display "N/A".

### Property 6: On-Hold Count Accuracy
The `onHold` count SHALL equal the exact number of rows where `status === 'On-Hold'`.

## Dependencies

- No new npm packages required
- Uses existing Font Awesome icons (already loaded)
- Uses existing `isPass()` and `getScoreValue()` helper functions
- Uses existing `groupedData`, `selectedRole`, `activeTab`, and `viewMode` state

## File Changes

| File | Change Type | Description |
|------|-------------|-------------|
| `frontend/src/pages/ResultsAI.js` | Modified | Add `computeBatchMetrics` function, `hoveredCard` state, `animateIn` state/effect, and analytics panel JSX in detail view section |

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Performance with large batches (100+ candidates) | `computeBatchMetrics` is O(n) with simple filters; memoization via `useMemo` if needed |
| Inline `<style>` tag for keyframes may conflict | Use unique animation name `batchCardFloat` to avoid collisions |
| `backdrop-filter` not supported in older browsers | Fallback solid background color via `background` property set before the rgba value |
