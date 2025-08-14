# Email Dashboard Project Architecture

## Project Overview

This project addresses a data recovery and analytics challenge where tracking system errors resulted in lost email performance data. We are creating a leadership dashboard to visualize unread email counts and SLA compliance using data recovered from Power Automate flows exported from SharePoint.

## Current Data Assets

### Files Analyzed
- **UnreadCount.csv** (data/UnreadCount.csv)
  - Date range: 6/30/2025 to 8/12/2025
  - Columns: Title, Date, TotalUnread, Messages Received, Hour of the Day
  - SLA Status: Binary classification (SLA MET/SLA NOT MET)
  - Tracking window: 7 AM to 9 PM hourly measurements
  - Messages Received column: Currently empty/unused

### SLA Definition
- **Unread SLA Threshold: 30 emails**
- SLA MET: TotalUnread ≤ 30
- SLA NOT MET: TotalUnread > 30
- Measured hourly during business operations (7 AM - 9 PM)

### Data Patterns Identified
- SLA compliance varies significantly by time of day
- Evening hours (8-9 PM) show frequent SLA violations (40-72 unread emails)
- Morning hours (7-10 AM) typically maintain SLA compliance (8-28 unread emails)
- Afternoon degradation pattern visible (violations starting around 11 AM - 1 PM)

## Current Project Structure

```
emailproject/
├── data/
│   └── UnreadCount.csv        # Primary data source analyzed
├── documentation/
│   ├── chat/                  # Conversation logs and decisions
│   └── architecture.md        # This document
└── .windsurf/
    └── workflows/
        └── spark.md           # Agent workflow guidance
```

## Technical Constraints

### Infrastructure Limitations
- No server infrastructure approved
- Static web technologies only (HTML/CSS - NO JavaScript)
- No database - CSV file processing only
- No real-time updates - manual CSV refresh cycle
- No user authentication system
- No client-side interactivity - pure static HTML/CSS only

### Data Limitations
- Single data source: CSV exports from SharePoint
- Manual data refresh required
- Potential data gaps from original tracking system errors
- Messages Received data not captured

## Current Objectives

Based on available data analysis, the dashboard will focus on:
- **SLA Compliance Tracking**: Hourly compliance rates over time
- **Unread Email Volume**: Trends and patterns by hour/day
- **Peak Load Identification**: Time periods with highest email volumes
- **Leadership Visibility**: Executive summary of email handling performance

## Technology Stack

### Data Processing
- **Python** - Data analysis and processing
- **Pandas** - CSV manipulation and analysis
- **CSV/JSON** - Data interchange formats

### Dashboard
- **HTML5/CSS3** - Static page structure and styling only
- **Python-generated HTML** - Data visualizations embedded as static HTML/CSS
- **No JavaScript** - Purely static sites constraint

## Key Obstacles

1. **Limited Data Scope**: Only unread count data available so far
2. **No Response Time Data**: Cannot measure actual response times without additional CSV files
3. **Missing Volume Data**: Messages Received column is empty
4. **Static Generation**: Dashboard must be manually regenerated for updates
5. **No Historical Context**: Unknown baseline for "normal" email volumes
6. **No JavaScript**: All visualizations must be generated as static HTML/CSS by Python

---

*Last Updated: 2025-08-14*
*Status: Data Discovery Phase - 1 CSV file analyzed*