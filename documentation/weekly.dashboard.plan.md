# Weekly Dashboard Planning Document

## Overview
Planning document for weekly dashboard implementation based on existing daily dashboard system and architectural constraints.

## Design Decisions Log

### Component 1: Title and Basic KPI Cards

**Decision Date:** Current session

**Title Format:**
- **Format:** "Email Performance Dashboard Week #34"
- **Rationale:** Clear identification of week number for easy reference
- **Implementation:** Use ISO week number (e.g., #34 for week 34 of 2025)

**KPI Cards Modifications:**
1. **Total Emails Card:**
   - **Change:** "Emails received during the week (7 days)" instead of single day
   - **Calculation:** Sum of all emails across 7 days in the selected week
   - **Subtitle:** "Emails received during the week (7 days)"

2. **Average Emails Per Day Card (NEW):**
   - **Purpose:** Replace single day sample with meaningful weekly average
   - **Calculation:** Total week emails ÷ 7 days
   - **Label:** "Avg Emails Per Day"
   - **Subtitle:** "Daily average across the week"

3. **Avg Unread Count Card:**
   - **No Change:** Remains the same as current daily dashboard
   - **Reference:** Same logic and styling as daily/dashboard/output/email_dashboard_2025-08-13.html:628-636

4. **Avg Response Time Card:**
   - **No Change:** Remains the same as current daily dashboard  
   - **Reference:** Same logic and styling as daily/dashboard/output/email_dashboard_2025-08-13.html:638-647

5. **SLA Compliance Card:**
   - **No Change:** Remains the same as current daily dashboard
   - **Reference:** Same logic and styling as daily/dashboard/output/email_dashboard_2025-08-13.html:649-658

**Styling Reference:**
- Use existing KPI card classes and structure from daily dashboard
- Maintain color coding: success (green), warning (yellow), danger (red)
- Preserve animated effects and hover states

### Component 2: Daily Email Volume Chart

**Decision Date:** Current session

**Chart Type Selection:**
- **Chosen:** Bar Chart (vertical or horizontal)
- **Rationale:** 
  - Shows relative volume differences clearly between days
  - Easy to compare daily volumes at a glance
  - Natural fit with daily time periods (discrete categories)
  - Follows existing chart patterns in dashboard architecture
  - Better for showing absolute values (total emails per day)
- **Rejected:** Pie Chart
  - Pie charts better for parts-of-a-whole (percentages)
  - Data is absolute counts, not proportional breakdown
  - Harder to compare similar values across 7 slices
  - Doesn't match existing dashboard aesthetic

**Implementation Specifications:**
- **Data:** Daily email totals for 7 days (Mon-Sun)
- **Labels:** Day abbreviations (Mon, Tue, Wed, Thu, Fri, Sat, Sun)
- **Values:** Show exact email counts on/above each bar
- **Styling:** Use existing CSS color scheme from dashboard
- **Format:** CSS/HTML-only SVG following existing chart patterns
- **Container:** Standard chart-section card format

### Component 3: Hourly Email Distribution Heatmap

**Decision Date:** Current session

**Chart Type Selection:**
- **Chosen:** Hour×Day Heatmap
- **Scope:** Emails received only (not unread count)
- **Rationale:**
  - Excellent for spotting patterns (e.g., "Mondays 9AM always busy")
  - Identifies quiet periods (e.g., "Friday afternoons light")
  - Visual pattern recognition superior to line charts for this data
  - Compact display of 7×14 data points

**Implementation Specifications:**
- **Grid Structure:**
  - **Columns:** 7 days (Mon, Tue, Wed, Thu, Fri, Sat, Sun)
  - **Rows:** Business hours from config/sla_config.json (likely 7AM-9PM = 14-15 hours)
- **Color Coding:**
  - **Light/White:** Low email volume
  - **Dark/Intense:** High email volume 
  - **Color scheme:** Use existing dashboard color palette
- **Data Display:**
  - **Cell values:** Show exact email count in each cell
  - **Hover/interaction:** Not applicable (HTML/CSS only constraint)
- **Labels:**
  - **Column headers:** Day abbreviations
  - **Row headers:** Hour labels (7AM, 8AM, 9AM, etc.)
- **Title:** "Hourly Email Distribution - Week #34"
- **Container:** Standard chart-section card format

### Component 4: Response Time by Hour

**Decision Date:** Current session

**Chart Type Selection:**
- **Chosen:** Same format as existing daily dashboard
- **Handling:** Average response time calculation
- **Rationale:** Maintains consistency with current dashboard architecture

**Implementation Specifications:**
- **Data Aggregation:** Average response time across all 7 days for each business hour
- **Format:** Follow existing hourly response time chart from daily dashboard
- **Calculation:** Mean response time per hour across the week
- **Styling:** Use existing chart styling and structure
- **Container:** Standard chart-section card format
- **Reference:** Same logic as daily/dashboard/output/email_dashboard_2025-08-13.html hourly charts

### Component 5: Response Time Distribution

**Decision Date:** Current session

**Chart Type Selection:**
- **Chosen:** Same format as existing daily dashboard
- **Rationale:** Maintains consistency with current dashboard architecture

**Implementation Specifications:**
- **Format:** Follow existing response time distribution chart from daily dashboard
- **Data Aggregation:** Weekly aggregate of response time distribution categories
- **Styling:** Use existing chart styling and structure
- **Container:** Standard chart-section card format
- **Reference:** Same logic as daily/dashboard/output/email_dashboard_2025-08-13.html response time distribution

### Component 6: Response Time Percentiles

**Decision Date:** Current session

**Chart Type Selection:**
- **Chosen:** Same format as existing daily dashboard
- **Rationale:** Maintains consistency with current dashboard architecture

**Implementation Specifications:**
- **Format:** Follow existing response time percentiles chart from daily dashboard
- **Data Aggregation:** Weekly aggregate percentile calculations
- **Styling:** Use existing chart styling and structure
- **Container:** Standard chart-section card format
- **Reference:** Same logic as daily/dashboard/output/email_dashboard_2025-08-13.html response time percentiles

### Component 7: 2-Hour Email Metrics

**Decision Date:** Current session

**Chart Type Selection:**
- **Chosen:** Same format as existing daily dashboard
- **Rationale:** Maintains consistency with current dashboard architecture

**Implementation Specifications:**
- **Format:** Follow existing 2-hour email metrics chart from daily dashboard
- **Data Aggregation:** Weekly aggregate of 2-hour block performance
- **Styling:** Use existing chart styling and structure
- **Container:** Standard chart-section card format
- **Reference:** Same logic as daily/dashboard/output/email_dashboard_2025-08-13.html 2-hour metrics

### Component 8: Best/Worst Day Summary Cards

**Decision Date:** Current session

**Card Types:**
- **Best Day Card:** Day with highest SLA compliance percentage
- **Worst Day Card:** Day with longest average response time  
- **Busiest Day Card:** Day with highest email volume
- **Quietest Day Card:** Day with lowest email volume

**Implementation Specifications:**
- **Format:** 4 summary cards in a grid layout
- **Content Examples:**
  - "Tuesday had highest SLA compliance (89%)"
  - "Friday had longest avg response time (124 min)"
  - "Monday received 67 emails"
  - "Saturday received 8 emails"
- **Styling:** Use existing card styling with appropriate color coding
- **Container:** Standard grid layout for card display

### Component 9: Daily SLA Compliance Table

**Decision Date:** Current session

**Table Structure:**
- **Columns:** Day | SLA % | Status Badge
- **Rows:** 7 rows (Mon-Sun)
- **Status Badges:** Green/Yellow/Red based on SLA performance
- **Thresholds:** Use existing SLA target thresholds from config

**Implementation Specifications:**
- **Format:** Simple table with clear visual indicators
- **Color Coding:** 
  - Green: SLA target met or exceeded
  - Yellow: Close to target (warning threshold)
  - Red: Below target (danger threshold)
- **Container:** Standard table within card format

### Component 10: Weekly Peak Indicators

**Decision Date:** Current session

**Peak Indicators:**
1. **Peak Email Hour:** Hour and day with highest email volume
2. **Worst Response Time:** Hour and day with longest response time
3. **Max Unread Backlog:** Hour and day with highest unread count

**Implementation Specifications:**
- **Format:** 3 indicator cards or badges
- **Content Examples:**
  - "Peak email hour: Monday 9AM (23 emails)"
  - "Worst response time: Friday 4PM (187 min)"
  - "Max unread backlog: Tuesday 11AM (45 emails)"
- **Styling:** Use existing styling with warning/info color schemes
- **Container:** Horizontal layout or small card grid

### Component 11: AI Analysis & Recommendations

**Decision Date:** Current session

**Purpose:**
- AI-powered high-level analysis of weekly dashboard data
- Generate insights and recommendations based on patterns and trends
- Provide actionable feedback for performance improvement

**Current Implementation:**
- **AI Provider:** Claude Code (temporary solution)
- **Future Plans:** Flexible architecture for different AI systems

**Data Input:**
- Read database/email_database.json for the selected week
- Analyze all weekly metrics and patterns
- Consider historical context when available

**Pre-established Prompts:**
1. **Pattern Analysis:** "Identify key patterns in email volume, response times, and SLA performance across the week"
2. **Performance Assessment:** "Evaluate overall weekly performance against targets and highlight areas of concern"
3. **Trend Identification:** "Detect trends in hourly/daily patterns that may indicate operational issues"
4. **Recommendations:** "Provide 3-5 actionable recommendations for improving email handling performance"
5. **Risk Areas:** "Identify time periods or conditions that consistently show poor performance"

**Output Format:**
- **Executive Summary:** 2-3 sentence overview of weekly performance
- **Key Insights:** Bullet points of main findings
- **Performance Highlights:** Best performing areas
- **Areas for Improvement:** Issues requiring attention
- **Recommendations:** Specific actionable items
- **Risk Indicators:** Warning signs to monitor

**Implementation Specifications:**
- **Container:** Dedicated AI insights section/card
- **Styling:** Use existing styling with info/warning color schemes
- **Content Structure:** Organized sections with clear headings
- **Length:** Concise but comprehensive (avoid overwhelming detail)
- **Tone:** Professional, actionable, data-driven

**Technical Approach:**
- Generate AI analysis during dashboard creation process
- Cache results to avoid repeated API calls
- Include timestamp of when analysis was generated
- Error handling for AI service unavailability

### Architecture Alignment
- **Data Source**: Will use existing `database/email_database.json` (aggregating across date ranges)
- **Template System**: Follow existing pattern with Jinja2 templates in `weekly/templates/`
- **Output Structure**: Save to `weekly/output/weekly_dashboard_YYYY-Www.html` + `latest.html`
- **Tech Constraints**: HTML/CSS only (no JavaScript), following existing limitations
- **Business Hours**: Respect `config/sla_config.json` settings for consistency

### Directory Structure
```
weekly/
├── scripts/
│   └── generate_weekly_dashboard.py    # Main generation script
├── templates/
│   └── weekly.html                     # Main template (may split into partials)
└── output/
    ├── weekly_dashboard_YYYY-Www.html  # Date-stamped outputs
    └── latest.html                     # Symlink to most recent
```

## Component Planning

*Note: Each component will be discussed and planned individually in subsequent conversations*

### MVP Components (Phase 1)
1. **Weekly KPIs Strip** - High-level metrics with week-over-week comparison
2. **Day-by-Day Performance Table** - Detailed daily breakdown with status indicators
3. **Hour×Day Heatmaps** - Visual patterns for volume, unread, SLA compliance
4. **Weekly 2-Hour Block Rollup** - Aggregate performance by time windows
5. **Response Time Analytics** - Weekly distribution and percentiles
6. **Week-over-Week Comparison Panel** - Trend analysis
7. **SLA Threshold Visualization** - Weekly aggregate with threshold line

### Enhancement Components (Phase 2)
8. **Insight Cards** - Best/worst day analysis with key drivers
9. **Performance Factors Panel** - Contextual explanations for patterns
10. **Drill-Down Navigation** - Links to daily dashboards

### Future Components (Optional)
11. **Staffing Context Cards** - Agent count correlation (if staffing data available)
12. **Weekly Staffing Patterns** - Performance vs staffing analysis
13. **Export Options** - CSV export and print styling

## Technical Approach

### Data Aggregation Strategy
- Aggregate from `database/email_database.json` across selected date ranges
- Reuse existing daily computation logic where possible
- Handle missing days gracefully
- Support both ISO week and "last 7 days" selection

### CLI Interface Design
```bash
python3 weekly/scripts/generate_weekly_dashboard.py --week 2025-W34
python3 weekly/scripts/generate_weekly_dashboard.py --last-7-days
python3 weekly/scripts/generate_weekly_dashboard.py --compare-weeks 4
```

## Next Steps
Begin component-by-component discussion and detailed planning.