# Weekly Response Time Distribution Card

## Overview
Add a "Response Time Distribution" card to the weekly dashboard template that shows aggregated email response performance across the entire week for leadership visibility.

## Placement
- Position: Below the existing "Weekly 2-Hour Email Metrics" section
- Position: Above the footer/summary section
- Purpose: Give leadership clear visibility into team response speed patterns

## Design Requirements

### Visual Consistency
- **Same styling** as daily dashboard response time distribution
- **Same emojis**: ⚡ Lightning Fast, 🚀 Fast Response, ⏱️ Moderate, 🐢 Slow, ⚠️ Very Slow, 🔴 Critical
- **Same colors**: success (green), warning (orange), danger (red) gradients
- **Same fonts**: Inter font family with consistent weights
- **Same animations**: shimmer effects, hover transforms, gradient bars

### Performance Categories
- **Lightning Fast**: Under 30 minutes (success color)
- **Fast Response**: 30-60 minutes (success color)  
- **Moderate**: 60-120 minutes (warning color)
- **Slow**: 120-180 minutes (warning color)
- **Very Slow**: 180-300 minutes (danger color)
- **Critical**: Over 300 minutes (danger color)

## Data Aggregation
- **Scope**: Aggregate ALL response times from entire week (all 7 days)
- **Display**: Total count of emails in each performance category
- **Format**: "45 emails" in Lightning Fast, "23 emails" in Moderate, etc.
- **Percentage**: Show percentage of total weekly emails for each category

## Technical Constraints
- **Tech Stack**: Only HTML/CSS (no JavaScript)
- **Template Engine**: Jinja2 for data rendering
- **Existing Libraries**: pandas, numpy for data processing
- **Architecture**: Must fit existing weekly dashboard generation system

## Card Structure
```
Weekly Response Time Distribution
└── Performance categories with horizontal bars
    ├── Category name with emoji and time range
    ├── Colored gradient bar showing count
    └── Percentage of total emails
```

## Integration Points
- Data source: Same `response_time_distribution` data structure as daily
- Template: `weekly/dashboard/templates/weekly_kpi_cards.html`
- Generator: `weekly/scripts/generate_weekly_dashboard.py`
- Styling: Reuse existing CSS classes from daily template

## Leadership Value
- Clear visual of team response speed performance
- Easy identification of response time patterns
- Performance benchmarking across weeks
- Visual confirmation of SLA compliance trends

## Implementation Notes
- Maintain design parity with daily dashboard
- Ensure responsive design for mobile viewing
- Keep existing hover effects and animations
- Use same gradient and color schemes
- Preserve accessibility features (titles, aria-labels)