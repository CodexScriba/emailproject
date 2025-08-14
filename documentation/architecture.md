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

- **Complete_List_Raw.csv** (data/Complete_List_Raw.csv)
  - Date range: 8/13/2025 (single day sample)
  - Columns: Conversation-Id, Subject, Emails, EventType, TimeStamp, MessageId
  - EventType: "Inbox" events (email arrivals)
  - Volume: 100+ emails in 7.5 hours
  - Peak periods: Morning (8-10 AM) and midday (11 AM-1 PM)
  - Missing: "Replied" and "Completed" events in this sample

- **DailySummary.csv** (data/DailySummary.csv)
  - Date range: 5/18/2025 to 8/13/2025 (3 months)
  - Columns: Date, InboxTotal, SentTotal, CompletedTotal, AvgResponseInMinutes, AvgResponseInHours, Within SLA, Average Unread
  - Daily volumes: 200-350 emails on weekdays, 10-30 on weekends
  - Response time data: Only available for 2 days (5/23 & 5/24/2025)
  - SLA performance: 22-29% compliance when measured
  - Average response times: 125-158 minutes (2+ hours)

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
├── data/                       # Source data files only
│   ├── Complete_List_Raw.csv   # Email lifecycle events (522 records)
│   ├── UnreadCount.csv         # Hourly SLA compliance data  
│   ├── DailySummary.csv        # Daily volume and performance summaries
│   └── Reserve.csv             # Sample data for validation
├── scripts/                    # Python processing scripts
│   └── email_classifier.py     # Main email classification and analysis script
├── results/                    # Generated analysis outputs
│   ├── Email_Classification_Results.csv        # Detailed email classifications
│   ├── Email_Classification_Results_Summary.csv # Summary statistics
│   └── Hourly_Email_Distribution.csv           # Email volume by hour
├── documentation/
│   ├── architecture.md         # System architecture (this document)
│   ├── tasks.md                # Implementation tasks and progress
│   ├── todos.md                # Development todos
│   └── chat/                   # Conversation logs and decisions
├── venv/                       # Python virtual environment (gitignored)
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore configuration
└── .windsurf/
    └── workflows/
        └── spark.md            # Agent workflow guidance
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
- CSV exports from SharePoint with significant gaps
- Manual data refresh required
- **Critical tracking system failure**: Response time data missing for 95% of days
- Messages Received data not captured in UnreadCount.csv
- Email lifecycle events incomplete (missing "Replied" and "Completed" events)
- Only 2 days of response time measurements out of 3+ months

## Current Objectives

Based on available data analysis, the dashboard will focus on:
- **SLA Compliance Tracking**: Hourly unread count compliance (30 email threshold)
- **Daily Volume Analysis**: Email intake patterns and trends over 3 months
- **Peak Load Identification**: Time periods with highest email volumes
- **Response Time Analysis**: Limited to 2 days of available data
- **Performance Trends**: Daily completion rates and patterns
- **Leadership Visibility**: Executive summary highlighting tracking system gaps

## ✅ Implemented Email Classification System

### Core Functionality
- **Email Matching Algorithm**: Matches 262 inbox emails with their corresponding replies or completion events
- **Business Hours Calculation**: Calculates response times in business minutes (7 AM - 6 PM, Monday-Friday)
- **Status Classification**: Automatically categorizes emails as Replied, Completed, or Pending
- **Hourly Distribution Analysis**: Analyzes email volume patterns by hour of day

### Key Metrics Achieved
- **59.16% Reply Rate** (155 of 262 emails)
- **1.15% Completion Rate** (3 of 262 emails) 
- **39.69% Pending Rate** (104 of 262 emails)
- **65.2 minutes** average response time
- **43.5 minutes** median response time  
- **12:00 PM** identified as peak email hour (35 emails)

### Data Quality Improvements
- Resolved missing response time calculations
- Created comprehensive email lifecycle tracking
- Implemented business-hours-only time calculations
- Generated detailed hourly distribution analysis

## Technology Stack

### Development Environment
- **Python 3.12.3** - Core development language
- **Virtual Environment** - Isolated dependency management (`venv/`)

### Data Processing
- **Pandas 2.3.1** - CSV manipulation and data analysis
- **NumPy** - Numerical computations (pandas dependency)
- **python-dateutil 2.9.0** - Timestamp parsing and date operations

### Visualization & Charts
- **Matplotlib 3.10.5** - Static chart generation for HTML embedding
- **Seaborn 0.13.2** - Statistical visualizations and enhanced plotting

### HTML Generation
- **Jinja2 3.1.6** - Template engine for dynamic HTML generation
- **HTML5/CSS3** - Static page structure and styling only
- **Python-generated HTML** - Data visualizations embedded as static HTML/CSS
- **No JavaScript** - Purely static sites constraint

### Project Organization
- **scripts/** - All Python processing scripts and modules
- **results/** - Generated analysis outputs and processed data
- **data/** - Source CSV files and raw data (read-only)
- **venv/** - Isolated Python environment with managed dependencies
- **.gitignore** - Comprehensive ignore rules for Python development

## Key Obstacles

1. **Severe Data Loss**: 95% of response time data missing due to tracking system failure
2. **Incomplete Email Lifecycle**: Missing "Replied" and "Completed" events in available samples
3. **Poor SLA Performance**: 22-29% compliance rate reveals operational issues
4. **High Email Volume**: 200-350 daily emails with limited response capacity
5. **Static Generation**: Dashboard must be manually regenerated for updates
6. **No JavaScript**: All visualizations must be generated as static HTML/CSS by Python
7. **Data Quality Issues**: Multiple empty columns and inconsistent event tracking

---

*Last Updated: 2025-08-14*
*Status: Data Discovery Phase - 3 CSV files analyzed*