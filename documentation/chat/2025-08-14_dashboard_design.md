# Dashboard Design Discussion - 2025-08-14

## Context
After analyzing all available CSV data files, we've identified severe data capture issues (94%+ of email lifecycle events missing) and need to create practical dashboards with available reliable data.

## Data Analysis Summary

### Files Analyzed
1. **UnreadCount.csv** - Reliable hourly SLA compliance data (historical 7 AM - 9 PM window; dashboards use configured business hours)
2. **Complete_List_Raw.csv** - Email arrival timestamps (limited sample)
3. **DailySummary.csv** - 3 months of daily volumes, but 95% missing response time data
4. **Reserve.csv** - Confirms massive data loss (only ~6% of emails captured)

### Key Findings
- SLA threshold: 30 unread emails
- Daily volume: 200-350 emails on weekdays
- Poor SLA compliance: 22-29% when measured
- Critical tracking system failure: Missing most email lifecycle events

## Dashboard Strategy Decision

**Two-Dashboard Approach:**
1. **Daily Dashboard** - Static HTML for email distribution to leadership
2. **Global Dashboard** - Historical analysis and correlation insights

## Daily Dashboard Design (Approved Structure)

### Executive KPI Cards (Top Row)
1. **Total Emails Received** - Daily count from available data
2. **SLA Compliance Rate** - % of hours with ≤30 unread emails
3. **Average Unread Count** - Daily average from hourly readings
4. **Average Response Time** - When available (show data gaps clearly)

### Main Visualization
**Hourly Email Flow Chart** - Side-by-side bar comparison:
- **Blue bars**: Emails received per hour (from Complete_List_Raw timestamps)
- **Red bars**: Unread emails per hour (from UnreadCount.csv)

### Design Foundation
- Using modern_dashboard.html as template (CSS-only, no JavaScript)
- Clean slate/blue color palette for professional appearance
- Card-based layout with status badges for SLA compliance
- CSS-only progress bars and visualizations

## Technical Requirements
- Static HTML/CSS only (no JavaScript allowed)
- Must be emailable as single file
- Python-generated visualizations embedded as HTML/CSS
- Professional appearance for leadership consumption
- Business hours configurable via `config/sla_config.json` (default 7 AM – 9 PM, Monday–Sunday)

## Next Steps
- Build daily dashboard template
- Create Python script to populate with real data
- Test with current CSV data
- Plan global dashboard for historical analysis

## Key Insights for Leadership
The hourly comparison chart will reveal:
- Peak intake periods vs unread buildup patterns
- Processing lag identification
- Time-of-day team effectiveness
- Operational bottlenecks requiring attention