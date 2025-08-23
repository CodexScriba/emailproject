# Weekly Response Time Distribution Todo

## User Stories
- As a leadership team member, I want to see aggregated weekly response time performance so I can assess team efficiency across longer time periods
- As a manager, I want to identify response time patterns over a full week so I can spot trends and areas for improvement
- As an executive, I want visual confirmation of SLA compliance trends so I can make data-driven decisions about team performance
- As a stakeholder, I want consistent visual design with daily dashboards so I can easily understand the metrics without learning new layouts

## Phase 1: Data Processing Foundation
- [ ] Analyze existing daily dashboard data structure for `response_time_distribution`
- [ ] Examine `weekly/scripts/generate_weekly_dashboard.py` to understand current data processing flow
- [ ] Identify where weekly aggregation logic should be implemented
- [ ] Design data aggregation function to combine 7 days of response time data
- [ ] Implement response time categorization logic for weekly data:
  - Lightning Fast: Under 30 minutes
  - Fast Response: 30-60 minutes
  - Moderate: 60-120 minutes
  - Slow: 120-180 minutes
  - Very Slow: 180-300 minutes
  - Critical: Over 300 minutes
- [ ] Add percentage calculation for each category relative to total weekly emails
- [ ] Test data aggregation with existing database entries

## Phase 2: Template Integration
- [ ] Examine existing `weekly/dashboard/templates/weekly_kpi_cards.html` structure
- [ ] Identify optimal placement below "Weekly 2-Hour Email Metrics" section
- [ ] Study daily dashboard response time distribution card for design reference
- [ ] Copy and adapt the HTML structure from daily template
- [ ] Ensure Jinja2 template variables are properly mapped for weekly data
- [ ] Maintain exact same emoji usage: ⚡ 🚀 ⏱️ 🐢 ⚠️ 🔴
- [ ] Preserve all CSS class names for visual consistency
- [ ] Adapt card title to "Weekly Response Time Distribution"
- [ ] Update data display format to show "X emails" instead of daily counts

## Phase 3: Visual Design Consistency
- [ ] Copy exact CSS styling from daily dashboard response time card
- [ ] Ensure Inter font family consistency across all text elements
- [ ] Maintain same color scheme:
  - Success colors (green) for Lightning Fast and Fast Response
  - Warning colors (orange) for Moderate and Slow
  - Danger colors (red) for Very Slow and Critical
- [ ] Preserve gradient bar animations and hover effects
- [ ] Keep shimmer effects and transform animations on hover
- [ ] Ensure responsive design works on mobile devices
- [ ] Maintain accessibility features (titles, aria-labels)
- [ ] Test visual consistency by comparing side-by-side with daily dashboard

## Phase 4: Integration & Testing
- [ ] Integrate new card into weekly dashboard generation workflow
- [ ] Update `generate_weekly_dashboard.py` to pass aggregated data to template
- [ ] Test with actual database data across multiple weeks
- [ ] Verify percentage calculations are accurate
- [ ] Ensure card displays properly in different screen sizes
- [ ] Validate that all six performance categories display correctly
- [ ] Test with edge cases (weeks with no emails, weeks with only one category)
- [ ] Generate sample weekly dashboard and verify placement and styling
- [ ] Document any configuration changes needed in the system

## Technical Specifications

### Component Structure
```
Weekly Response Time Distribution Card
├── Card Header: "Weekly Response Time Distribution"
├── Performance Categories (6 rows):
│   ├── Category Header: [Emoji] [Name] ([Time Range])
│   ├── Progress Bar: Gradient bar showing relative count
│   ├── Count Display: "X emails"
│   └── Percentage Display: "Y% of weekly total"
└── Card Footer: Responsive styling
```

### Data Integration Points
- **Source**: `database/email_database.json`
- **Processor**: `weekly/scripts/generate_weekly_dashboard.py`
- **Template**: `weekly/dashboard/templates/weekly_kpi_cards.html`
- **Output**: `weekly/dashboard/output/weekly_dashboard_*.html`

### Required Dependencies
- **pandas**: For data aggregation and processing (≥1.5.0)
- **numpy**: For numerical operations (≥1.24.0)
- **jinja2**: For template rendering (≥3.1.0)

### Performance Considerations
- Aggregate data processing should be efficient for large datasets
- Template rendering should maintain fast load times
- CSS animations should not impact page performance
- Responsive design should work smoothly across devices

### Integration Constraints
- **No new dependencies**: Must use only existing HTML, CSS, and Jinja2
- **Visual parity**: Must match daily dashboard styling exactly
- **Data compatibility**: Must work with existing database schema
- **Template consistency**: Must integrate seamlessly with current weekly template structure

## Success Criteria
- [ ] Card displays exactly like daily dashboard version with weekly data
- [ ] All six performance categories show correct aggregated counts
- [ ] Percentages accurately represent weekly email distribution
- [ ] Visual design is indistinguishable from daily dashboard styling
- [ ] Card is properly positioned in weekly dashboard layout
- [ ] Responsive design works on mobile and desktop
- [ ] Leadership can easily interpret weekly response performance trends