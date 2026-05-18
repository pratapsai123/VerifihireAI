# Requirements Document

## Introduction

This feature adds a cinematic, 3D-styled analytics dashboard panel to the AI Interview Results page. When a user clicks on a batch to view its detail results, an interactive analytics panel appears above the results table showing key metrics such as total participants, pass/fail/on-hold counts, average score, and completion rate. The panel uses 3D visual effects, animations, and interactive elements to create an immersive data visualization experience.

## Glossary

- **Analytics_Panel**: The cinematic dashboard component that displays batch-level metrics above the results table in detail view mode
- **Batch**: A group of candidates organized by role/job title, represented by a key in the `groupedData` object
- **Detail_View**: The view mode (`viewMode === 'detail'`) activated when a user clicks a batch card from the overview
- **Metric_Card**: An individual 3D-styled card within the Analytics_Panel that displays a single metric value
- **Results_Page**: The `ResultsAI.js` page component that displays AI interview, assessment, and resume screening results
- **Candidate**: A person who has participated in a batch's hiring process (resume, assessment, or interview stage)
- **Pass_Status**: A candidate whose result meets the passing threshold for the active tab type (resume ≥ 70, assessment ≥ 50%, interview ≥ 50%)
- **Fail_Status**: A candidate whose result does not meet the passing threshold and is not on hold
- **On_Hold_Status**: A candidate whose status is explicitly set to 'On-Hold' pending manual review
- **Completion_Rate**: The percentage of candidates who have a completed submission out of total participants in the batch
- **3D_Effect**: CSS-based visual transformations including perspective, rotateX/Y, translateZ, and box-shadow depth to simulate three-dimensional appearance

## Requirements

### Requirement 1: Analytics Panel Visibility

**User Story:** As an HR user, I want to see a batch analytics panel when I view batch details, so that I can quickly understand the overall performance of that batch.

#### Acceptance Criteria

1. WHEN the user clicks a batch card and the view mode transitions to 'detail', THE Analytics_Panel SHALL render above the results table and below the back navigation button
2. WHEN the view mode is 'overview' or 'transcript', THE Analytics_Panel SHALL NOT be visible
3. THE Analytics_Panel SHALL compute metrics from the currently selected batch's data in `groupedData[selectedRole]`

### Requirement 2: Key Metrics Display

**User Story:** As an HR user, I want to see total participants, passed, failed, on-hold counts, average score, and completion rate for the batch, so that I can assess batch performance at a glance.

#### Acceptance Criteria

1. THE Analytics_Panel SHALL display a Metric_Card for total number of participants in the selected batch
2. THE Analytics_Panel SHALL display a Metric_Card for the count of candidates with Pass_Status
3. THE Analytics_Panel SHALL display a Metric_Card for the count of candidates with Fail_Status
4. THE Analytics_Panel SHALL display a Metric_Card for the count of candidates with On_Hold_Status
5. THE Analytics_Panel SHALL display a Metric_Card showing the average score as a percentage, computed from all candidates in the active tab context
6. THE Analytics_Panel SHALL display a Metric_Card showing the Completion_Rate as a percentage
7. WHEN the active tab changes within detail view, THE Analytics_Panel SHALL recalculate all metrics based on the new tab's data subset

### Requirement 3: Cinematic 3D Visual Styling

**User Story:** As a user, I want the analytics panel to have a cinematic, immersive visual style with 3D elements, so that the dashboard feels modern and engaging.

#### Acceptance Criteria

1. THE Analytics_Panel SHALL use CSS `perspective` and `transform` properties to create a 3D depth effect on Metric_Cards
2. Each Metric_Card SHALL have a layered box-shadow that simulates elevation and depth
3. THE Analytics_Panel SHALL use a gradient background that creates a cinematic dark-to-accent color atmosphere
4. Each Metric_Card SHALL include a subtle idle animation using CSS `@keyframes` to create a floating or breathing effect
5. THE Analytics_Panel SHALL use inline styles consistent with the existing Results_Page styling approach (no external CSS framework)
6. Each Metric_Card SHALL display a Font Awesome icon relevant to its metric type

### Requirement 4: Interactive Hover and Focus Effects

**User Story:** As a user, I want the metric cards to respond to my interactions with 3D tilt and glow effects, so that the dashboard feels alive and interactive.

#### Acceptance Criteria

1. WHEN the user hovers over a Metric_Card, THE Metric_Card SHALL apply a CSS 3D rotation transform (tilt toward the cursor direction) with a smooth transition
2. WHEN the user hovers over a Metric_Card, THE Metric_Card SHALL increase its box-shadow intensity to simulate the card lifting toward the user
3. WHEN the user moves the cursor away from a Metric_Card, THE Metric_Card SHALL smoothly transition back to its resting position within 300 milliseconds
4. WHEN the user hovers over a Metric_Card, THE Metric_Card SHALL display a subtle glow border effect using the metric's accent color

### Requirement 5: Responsive Layout

**User Story:** As a user, I want the analytics panel to display correctly on different screen sizes, so that I can view batch analytics on any device.

#### Acceptance Criteria

1. THE Analytics_Panel SHALL arrange Metric_Cards in a CSS grid layout that wraps from 3 columns on wide screens to 2 columns on medium screens to 1 column on narrow screens
2. THE Analytics_Panel SHALL maintain readable font sizes and adequate spacing at all supported viewport widths
3. THE Analytics_Panel SHALL not cause horizontal overflow on the Results_Page at any viewport width

### Requirement 6: Animated Entry on View Transition

**User Story:** As a user, I want the analytics panel to appear with a cinematic entrance animation when I open a batch, so that the transition feels polished and intentional.

#### Acceptance Criteria

1. WHEN the Detail_View is activated, THE Analytics_Panel SHALL animate into view using a staggered fade-in and slide-up animation for each Metric_Card
2. Each Metric_Card SHALL have a sequential animation delay (increasing by 100 milliseconds per card) to create a cascade reveal effect
3. THE Analytics_Panel background SHALL fade in over 400 milliseconds when the Detail_View is activated

### Requirement 7: Metric Accuracy

**User Story:** As an HR user, I want the displayed metrics to accurately reflect the batch data, so that I can trust the analytics for decision-making.

#### Acceptance Criteria

1. THE Analytics_Panel SHALL compute the participant count as the total number of rows returned by `getDataForActiveContext()` for the selected batch
2. THE Analytics_Panel SHALL compute Pass_Status count using the same `isPass()` logic already defined in the Results_Page, excluding On_Hold candidates
3. THE Analytics_Panel SHALL compute Fail_Status count as total participants minus passed count minus On_Hold count
4. THE Analytics_Panel SHALL compute On_Hold_Status count by filtering candidates whose status equals 'On-Hold'
5. THE Analytics_Panel SHALL compute average score using the existing `getScoreValue()` helper function across all candidates in the active context
6. THE Analytics_Panel SHALL compute Completion_Rate as the percentage of candidates who have a non-null `completed_at` or `submitted_at` date field
7. IF the batch contains zero participants, THEN THE Analytics_Panel SHALL display zero for all count metrics and "N/A" for percentage metrics
