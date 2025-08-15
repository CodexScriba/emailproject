# Email Dashboard Project Architecture

## Project Overview

This project addresses a data recovery and analytics challenge where tracking system errors resulted in lost email performance data. We are creating a leadership dashboard to visualize unread email counts and SLA compliance using data recovered from Power Automate flows exported from SharePoint.

## Current Data Assets

### Files Analyzed
- **UnreadCount.csv** (data/UnreadCount.csv) ✅ **INTEGRATED**
  - Date range: 5/18/2025 to 8/13/2025 (88 days)
  - Columns: Title, Date, TotalUnread, Messages Received, Hour of the Day
  - SLA Status: Binary classification (SLA MET/SLA NOT MET)
  - Tracking window: 7 AM to 9 PM hourly measurements
  - 1,303 SLA records processed into unified database
  - **68.58% average SLA compliance** across all measured days

- **Complete_List_Raw.csv** (data/Complete_List_Raw.csv) ✅ **INTEGRATED**
  - Date range: 8/13/2025 (single day sample with complete lifecycle events)
  - Columns: Conversation-Id, Subject, Emails, EventType, TimeStamp, MessageId
  - EventTypes: "Inbox", "Replied", "Completed" events processed
  - Volume: 262 inbox emails with full classification analysis
  - Peak periods: 12:00 PM (35 emails), with hourly distribution analysis
  - **59.16% reply rate, 65.2 min average response time**

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
├── daily/                      # Daily processing pipeline
│   ├── scripts/               # Daily analysis Python scripts
│   │   └── email_classifier.py # Main email classification and analysis script
│   └── outputs/               # Daily analysis outputs (cleaned up)
├── email_database.json         # ✅ Unified 88-day JSON database (459KB, single source of truth)
├── dashboard/                   # Dashboard generation system
│   ├── scripts/               # Python dashboard generators
│   ├── templates/             # HTML/CSS templates
│   └── output/                # Generated dashboard HTML files
├── documentation/
│   ├── architecture.md         # System architecture (this document)
│   ├── tasks.md                # Implementation tasks and progress
│   ├── todos.md                # Development todos
│   └── chat/                   # Conversation logs and decisions
├── examples/                   # HTML dashboard examples and templates
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
- No database - JSON file processing only (unified single source of truth)
- No real-time updates - manual data refresh cycle
- No user authentication system
- No client-side interactivity - pure static HTML/CSS only

### Data Limitations ✅ **SIGNIFICANTLY RESOLVED**
- CSV exports from SharePoint with gaps (**now integrated into unified database**)
- Manual data refresh required (**streamlined with unified JSON processing**)
- **SLA data integrated**: 88 days of hourly SLA compliance measurements
- **Email lifecycle complete**: Full "Inbox", "Replied", "Completed" event processing
- **Response time analysis**: Business hours calculations implemented
- **Remaining limitation**: Email response data only available for 1 day (Aug 13)

## Current Objectives

Based on available data analysis, the dashboard will focus on:
- **SLA Compliance Tracking**: Hourly unread count compliance (30 email threshold)
- **Daily Volume Analysis**: Email intake patterns and trends over 3 months
- **Peak Load Identification**: Time periods with highest email volumes
- **Response Time Analysis**: Limited to 2 days of available data
- **Performance Trends**: Daily completion rates and patterns
- **Leadership Visibility**: Executive summary highlighting tracking system gaps

## ✅ Unified Database with Complete SLA Integration

### Core Functionality
- **Email Matching Algorithm**: Matches 262 inbox emails with their corresponding replies or completion events
- **Business Hours Calculation**: Calculates response times in business minutes (7 AM - 6 PM, Monday-Friday)
- **Status Classification**: Automatically categorizes emails as Replied, Completed, or Pending
- **SLA Processing**: Processes 1,303 SLA records across 88 days with hourly compliance tracking
- **Multi-Source Integration**: Unified schema supporting both email lifecycle and SLA compliance data
- **Dashboard-Ready Data**: Optimized for KPI cards and executive reporting

### Key Metrics Achieved

#### Email Performance (August 13, 2025)
- **59.16% Reply Rate** (155 of 262 emails)
- **1.15% Completion Rate** (3 of 262 emails) 
- **39.69% Pending Rate** (104 of 262 emails)
- **65.2 minutes** average response time
- **43.5 minutes** median response time  
- **12:00 PM** identified as peak email hour (35 emails)

#### SLA Performance (88 days: May 18 - August 13, 2025)
- **68.58% Average SLA Compliance** across all measured days
- **Range**: 12.5% to 100% daily compliance (significant variation)
- **August 13 SLA**: 66.67% compliance with 29.5 avg unread emails
- **Complete hourly tracking**: 7 AM - 9 PM business operations

### Database Scale & Performance
- **88 days of unified data**: From May 18 - August 13, 2025
- **459KB optimized database**: Comprehensive yet dashboard-focused
- **Dual data sources**: Complete integration of UnreadCount.csv + Complete_List_Raw.csv
- **Single source of truth**: Eliminated multiple CSV file dependencies
- **Scalable schema**: Ready for additional days and data sources

## ✅ Unified JSON Database Schema

### Current Database Stats
- **88 days processed** (May 18 - August 13, 2025)
- **459KB total size** with complete SLA and email integration
- **Dual data sources**: UnreadCount.csv + Complete_List_Raw.csv
- **Ready for KPI dashboard generation**

### Structure Overview
```json
{
  "metadata": {
    "last_updated": "2025-08-14T13:40:08.439010",
    "total_days_processed": 88,
    "data_sources": ["UnreadCount.csv", "Complete_List_Raw.csv"],
    "earliest_date": "2025-05-18",
    "latest_date": "2025-08-13"
  },
  "days": {
    "2025-08-13": {
      "date": "2025-08-13",
      "has_sla_data": true,
      "has_email_data": true,
      "daily_summary": {
        "sla_compliance_rate": 66.67,
        "avg_unread_count": 29.5,
        "total_emails": 262,
        "reply_rate_percent": 59.16,
        "avg_response_time_minutes": 65.2,
        "median_response_time_minutes": 43.5
      },
      "hourly_data": [
        {
          "hour": 12,
          "unread_count": 28,
          "sla_met": true,
          "emails_received": 35,
          "emails_replied": 22,
          "avg_response_time": 73.64
        }
      ]
    }
  }
}
```

### Schema Features
- **Complete Integration**: August 13 shows both SLA (66.67% compliance) and email data (262 emails)
- **87 SLA-only days**: May 18 - August 12 with hourly compliance tracking
- **1 complete day**: August 13 with both email performance and SLA metrics
- **Perfect for KPIs**: Direct access to all 4 key dashboard metrics

### KPI Dashboard Ready
The unified database provides direct access to all required KPI metrics:

**4 Core KPI Cards:**
1. **Total Emails**: `data.days["2025-08-13"].daily_summary.total_emails` → **262**
2. **Avg Response Time**: `data.days["2025-08-13"].daily_summary.avg_response_time_minutes` → **65.2 min**
3. **SLA Compliance**: `data.days["2025-08-13"].daily_summary.sla_compliance_rate` → **66.67%**
4. **Avg Unread Count**: `data.days["2025-08-13"].daily_summary.avg_unread_count` → **29.5**

**Query Benefits:**
- **Simple JSON paths**: Direct access to dashboard metrics
- **Multi-day support**: Historical trends and comparisons available
- **Hourly granularity**: Detailed time-based analysis ready
- **Null handling**: Graceful degradation for missing data periods

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
- **daily/** - Daily processing pipeline with focused scope
  - **daily/scripts/** - Daily analysis Python scripts and modules
  - **daily/outputs/** - Daily analysis outputs (currently empty - cleaned up)
- **data/** - Source CSV files and raw data (read-only)
- **email_database.json** - Unified 88-day JSON database (459KB, single source of truth)
- **dashboard/** - Dashboard generation system
  - **dashboard/scripts/** - Python generators for HTML/CSS dashboard creation
  - **dashboard/templates/** - HTML/CSS templates for KPI cards and visualizations
  - **dashboard/output/** - Generated static dashboard files
- **examples/** - HTML dashboard templates and prototypes
- **venv/** - Isolated Python environment with managed dependencies
- **.gitignore** - Comprehensive ignore rules for Python development

## Relations

- **`daily/scripts/email_classifier.py` ↔ `data/*.csv`**
  - Reads: `data/Complete_List_Raw.csv`, `data/UnreadCount.csv`, optionally `data/DailySummary.csv`
  - Produces unified JSON: `email_database.json`
  - Exposes metrics: total emails, reply/completion counts, response times, hourly unread counts/SLA

- **`email_database.json` ↔ `dashboard/templates/*.html`**
  - Source of truth consumed by dashboard generation
  - Provides values for KPI cards and hourly charts (e.g., totals, averages, hourly distributions)

- **`dashboard/templates/kpi_cards.html` ↔ `dashboard/scripts/`**
  - Template used by Python (Jinja2) generators under `dashboard/scripts/` to render static dashboards
  - Receives context populated from `email_database.json`

- **`dashboard/output/*.html` ↔ `dashboard/templates/*.html`**
  - Generated static files produced by rendering templates (with data) into finalized HTML
  - Example: `dashboard/output/email_dashboard_2025-08-13.html` is a rendered snapshot for Aug 13, 2025

- **`examples/*.html` ↔ `dashboard/templates/*.html`**
  - Examples serve as visual/style references for building templates
  - Not directly tied to data; used for design inspiration and UI patterns

- **`requirements.txt` ↔ all Python scripts**
  - Declares dependencies required by `daily/scripts/` and `dashboard/scripts/` (e.g., pandas, Jinja2, matplotlib, seaborn)

- **`documentation/*` ↔ project root**
  - Documents architecture, tasks, todos, and conversations that guide how code and data connect

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
*Status: SLA Integration Complete - KPI Dashboard Development In Progress*

## 🚧 Current Development: KPI Dashboard Cards

**Next Phase:** Creating static HTML/CSS dashboard with 4 core KPI cards using design elements from modern_dashboard.html template. Dashboard will showcase the complete 88-day dataset with focus on August 13 metrics that include both email performance and SLA compliance data.