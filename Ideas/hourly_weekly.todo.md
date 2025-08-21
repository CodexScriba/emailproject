# Hourly Weekly Email Volume Todo

## User Stories
- As a data analyst, I want to see email volume patterns across an entire week so I can identify trends and peak periods.
- As a manager, I want to compare different visualization options (lines vs bars) so I can choose the most effective display for our team.
- As a stakeholder, I want to view weekly email patterns at an hourly granularity so I can make informed decisions about resource allocation.
- As a dashboard user, I want consistent business hours scope (7 AM–9 PM) so weekly data aligns with our daily dashboard format.

## Phase 1: Foundation & Data Structure
- [ ] Create `Ideas/hourly_weekly_prototype.html` file for comparison testing
- [ ] Copy and import the complete CSS color system from `daily/dashboard/templates/kpi_cards.html`
- [ ] Set up basic HTML structure with two side-by-side sections for visualization comparison
- [ ] Define mock data structure for August 13-19, 2024 (7 days × 15 hours × email volumes)
- [ ] Create sample dataset with realistic email volume patterns (morning peaks, afternoon activity, evening decline)
- [ ] Set up basic CSS grid/flexbox layout for side-by-side chart comparison using existing `.container`, `.card` classes
- [ ] Add header section explaining the purpose using existing `.header` and `.brand-title` styling

## Phase 2: Line Chart Implementation (7 Lines Option)
- [ ] Create SVG container for line chart visualization
- [ ] Implement coordinate system for 15 hours (7 AM–9 PM) on X-axis
- [ ] Set up Y-axis for email volume (0-50 range to accommodate sample data)
- [ ] Generate 7 distinct colored lines using existing color variables (Tue: `--emails`, Wed: `--accent`, Thu: `--success`, Fri: `--warning`, Sat: `--danger`, Sun: `--accent-3`, Mon: `--primary-2`)
- [ ] Add data points with hover tooltips using existing `.data-point` styling
- [ ] Create legend using existing `.legend-item` and `.legend-line` classes
- [ ] Add grid lines using existing `.grid-line` class
- [ ] Implement styling consistent with existing `.line-emails`, `.point-emails` classes

## Phase 3: Bar Chart Implementation (Bars Option)
- [ ] Create SVG container for bar chart visualization  
- [ ] Design grouped bar layout: 15 hour groups, 7 bars per group (one per day)
- [ ] Implement X-axis labels for hours (7 AM, 8 AM, ..., 9 PM)
- [ ] Set up Y-axis for email volume matching line chart scale
- [ ] Generate color-coded bars using the same 7-day color scheme from line chart
- [ ] Add hover tooltips using existing tooltip styling and classes
- [ ] Create legend matching the line chart legend using `.legend-item` classes
- [ ] Implement spacing and grouping using existing chart container styling
- [ ] Add responsive behavior using existing media queries from template

## Phase 4: Enhanced Features & Polish
- [ ] Add interactive features: click to highlight specific day across both charts
- [ ] Implement zoom/pan functionality for detailed inspection
- [ ] Add summary statistics below each chart (peak hours, total volume, etc.)
- [ ] Create toggle buttons to show/hide individual days in both visualizations
- [ ] Add comparison metrics (space usage, visual clutter assessment)
- [ ] Implement print-friendly styling
- [ ] Add accessibility features (ARIA labels, keyboard navigation)
- [ ] Create export functionality (PNG/PDF) for management presentation

## Phase 5: Testing & Management Presentation
- [ ] Test both visualizations with various data patterns (high volume days, low activity periods)
- [ ] Validate readability across different screen sizes and devices
- [ ] Create evaluation criteria checklist (readability, space efficiency, pattern clarity)
- [ ] Prepare presentation notes highlighting pros/cons of each approach
- [ ] Document specific feedback questions for management review
- [ ] Test loading performance with larger datasets
- [ ] Create backup static images in case of technical issues during presentation

## Technical Specifications

### File Structure
```
Ideas/
├── hourly_weekly.idea.md
├── hourly_weekly.todo.md (this file)
└── hourly_weekly_prototype.html (to be created)
```

### Data Format
```javascript
const mockData = {
  "2024-08-13": { "07": 12, "08": 18, "09": 25, ... }, // Tuesday
  "2024-08-14": { "07": 15, "08": 22, "09": 28, ... }, // Wednesday
  // ... continue for 7 days
};
```

### Chart Dimensions
- **Line Chart**: 800px width × 400px height
- **Bar Chart**: 900px width × 400px height (needs extra width for grouped bars)
- **Container**: Side-by-side layout with responsive breakpoint at 1200px

### Color Palette
- Import and use the exact CSS color system from `daily/dashboard/templates/kpi_cards.html`
- Use the existing CSS variables: `--primary`, `--accent`, `--success`, `--warning`, `--danger`, `--emails`, etc.
- 7-day color scheme using variations of existing palette:
  - Tuesday: `var(--emails)` (#0EA5E9)
  - Wednesday: `var(--accent)` (#3B82F6) 
  - Thursday: `var(--success)` (#10B981)
  - Friday: `var(--warning)` (#F59E0B)
  - Saturday: `var(--danger)` (#EF4444)
  - Sunday: `var(--accent-3)` (#93C5FD)
  - Monday: `var(--primary-2)` (#3B82F6)
- Ensure sufficient contrast for accessibility using existing tested combinations

### Performance Considerations
- Keep mock data lightweight (< 1KB)
- Use efficient SVG rendering
- Minimize DOM manipulation during interactions
- Ensure smooth animations under 16ms for 60fps

### Integration Points
- Designed to potentially integrate with existing `daily/dashboard/output/` structure
- Compatible with unified JSON database format
- Follows business hours scope (7 AM–9 PM) from daily dashboard
- Maintains consistency with existing email dashboard styling patterns

## Success Criteria
- [ ] Both visualizations clearly show weekly patterns
- [ ] Management can easily compare the two approaches
- [ ] Prototype loads in under 2 seconds
- [ ] All interactive features work smoothly
- [ ] Charts are readable on both desktop and tablet devices
- [ ] Clear recommendation can be made based on evaluation
