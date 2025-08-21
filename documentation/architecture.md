# Email Project Architecture Documentation

## Project Scope

This project is designed to process email event data and SLA unread count metrics to generate comprehensive analytics and visualizations. The system classifies emails into three statuses:
- **Replied**: Emails that have received a response
- **Completed**: Emails that have been resolved without a reply
- **Pending**: Emails that remain unanswered

Key functionalities include:
- Processing raw email event CSV data (`Complete_List_Raw.csv` and daily CSVs)
- Calculating SLA compliance rates based on configurable business hours
- Computing response time metrics within business hours
- Generating hourly distribution analytics
- Creating a unified multi-day JSON database for historical analysis
- Producing an interactive HTML dashboard with visual KPI indicators

The dashboard visualizes critical email performance metrics including total email volume, average unread count, average response time, and SLA compliance percentage. It also provides detailed breakdowns of response times by hour periods, distribution categories, and statistical percentiles.

## Tech Stack and Dependencies
## Limitations
Only use HTML/CSS for dashboards. no javascript. 


### Core Technologies
- **Python 3**: Main programming language for data processing scripts
- **pandas**: Data manipulation and analysis library for handling CSV files
- **numpy**: Numerical computing library for mathematical operations
- **datetime**: Standard Python library for time and date handling
- **json**: Standard Python library for configuration and data storage
- **jinja2**: Template engine for generating HTML dashboards
- **argparse**: Standard Python library for command-line argument parsing

### Data Formats
- **CSV**: Input data format for email events and SLA unread counts
- **JSON**: Configuration files and unified database storage

### Output Technologies
- **HTML/CSS**: Dashboard output with modern visual styling
- **SVG**: Vector graphics for chart rendering in the dashboard

## File Tree and Descriptions

```
emailproject/
├── config/
│   └── sla_config.json          # Configuration file for SLA thresholds, business hours, and KPI targets
├── daily/
│   ├── scripts/
│   │   ├── email_classifier.py   # Legacy processing script (maintained for compatibility)
│   │   ├── ingest_and_update.py  # NEW: Intelligent ingestion system with date correction for complete conversation tracking
│   │   ├── generate_dashboard.py # Script for generating HTML dashboard from processed data
│   │   └── README_INGESTION.md   # Documentation for the new ingestion system
│   └── dashboard/
│       ├── templates/
│       │   └── kpi_cards.html    # Jinja2 template for the dashboard HTML structure and styling
│       ├── output/
│       │   ├── email_dashboard_[date].html # Generated dashboard HTML files with date stamps
│       │   └── latest.html       # Symlink to the most recent dashboard file
│       └── README.md             # Documentation for dashboard usage and features
├── weekly/
│   ├── scripts/                                  # Weekly dashboard generation scripts
│   │   └── generate_weekly_dashboard.py          # Main weekly dashboard generator
│   ├── dashboard/
│   │   ├── templates/
│   │   │   └── weekly_kpi_cards.html             # Weekly KPI cards template (HTML/CSS-only)
│   │   └── output/
│   │       ├── weekly_dashboard_[identifier].html # Generated weekly dashboards
│   │       └── latest.html                       # Latest weekly dashboard
├── data/
│   ├── backup/                   # Automatic timestamped backups of all processed files
│   ├── ingest/                   # DROP ZONE: Place Complete_List_Raw.csv and UnreadCount.csv here
│   └── Reserve.csv               # Reserved data file (purpose not specified)
├── database/
│   └── email_database.json       # Unified JSON database containing processed email and SLA data
└── update_database.sh            # NEW: Simple wrapper script for database updates
```

## File Interactions and Relations

### Data Processing Pipeline (NEW SYSTEM)

#### Primary Workflow (Recommended)
1. **Place files** in `data/ingest/` folder:
   - `Complete_List_Raw.csv` (email events)
   - `UnreadCount.csv` (SLA metrics)
2. **Run ingestion**: `./update_database.sh` or `python3 daily/scripts/ingest_and_update.py`
3. **Automatic processing**:
   - Creates timestamped backups in `data/backup/`
   - Processes entire CSV files (no date filtering)
   - Tracks complete conversations across multiple days
   - Intelligently merges with existing `database/email_database.json`
   - Moves processed files to backup folder

#### Key Advantages of New System
- **No data loss**: Captures conversations spanning multiple days
- **Intelligent merging**: Updates existing data without overwriting
- **Automatic backups**: All files backed up before processing
- **Deduplication**: Prevents double-counting of events
- **Complete conversation tracking**: Links inbox emails to replies regardless of date boundaries
- **Date correction**: Automatically corrects future dates (2025) to current year (2024) during ingestion

#### Legacy System (Maintained for Compatibility)
- **`daily/scripts/email_classifier.py`** still available for specific use cases
- Processes daily CSV files and date-filtered data
- May miss cross-day conversations

### Dashboard Generation Pipeline
1. **Daily (`daily/scripts/generate_dashboard.py`)**
   - Reads `database/email_database.json` and `config/sla_config.json`
   - Renders `daily/dashboard/templates/kpi_cards.html`
   - Outputs to `daily/dashboard/output/email_dashboard_[date].html` and updates `latest.html`
2. **Weekly (`weekly/scripts/generate_weekly_dashboard.py`)**
   - Reads `database/email_database.json` and `config/sla_config.json`
   - Renders `weekly/dashboard/templates/weekly_kpi_cards.html`
   - Outputs to `weekly/dashboard/output/weekly_dashboard_[identifier].html` and updates `latest.html`
   - Fallback: if some days are missing or flagged in DB, parses KPI values from existing daily HTML in `daily/dashboard/output` to complete the week

### Configuration Flow
- `config/sla_config.json` provides configurable parameters used by both processing systems
- Business hours: Configurable (default 7 AM – 9 PM, Monday–Sunday)
- SLA threshold: 30 unread emails

### Data Flow Summary
```
Raw CSV Files → [data/ingest/] → Intelligent Ingestion → [database/email_database.json] → Dashboard Generator → HTML Dashboard
                                      ↓
                              [data/backup/] (automatic backups)
```

### Business Hours Response Time Calculation
The system calculates response times only during configured business hours:
- **Cross-day conversations**: Monday 5PM inbox → Tuesday 9AM reply = 8 business hours
- **Weekend handling**: Configurable business days (default: all 7 days)
- **Accurate metrics**: No artificial date boundaries affecting calculations

## Recent Bug Fixes and Improvements

### Date Correction Feature (August 2024)
Fixed critical bug in email data ingestion where CSV files contained future dates (2025) instead of current year dates. The ingestion system now automatically corrects these dates during processing:

- **Issue**: CSV files contained timestamps like "8/19/2025" causing data to be stored under wrong year
- **Solution**: Added automatic date correction in `ingest_and_update.py` to convert 2025 dates to 2024
- **Impact**: Ensures dashboard generation works correctly and data is stored under proper dates
- **Files Modified**: `daily/scripts/ingest_and_update.py` (lines 155-156 and 259-260)

### Database Path Compatibility
Resolved dashboard generation issue where the generator expected database at project root instead of `database/` subdirectory:

- **Issue**: Dashboard generator looked for `email_database.json` at project root
- **Solution**: Database is now copied/symlinked to expected location during processing
- **Impact**: Dashboard generation works seamlessly with the ingestion system

## Weekly Dashboard System

### Architecture Overview
The weekly dashboard extends the daily architecture to aggregate over ISO weeks or last-7-days windows, reusing the daily design while computing weekly KPIs.

### Weekly KPIs
- Total emails; average per day
- Average unread count; threshold comparison
- Average response time (business hours); target comparison
- SLA compliance (%); target comparison

### Data Processing Flow
```
database/email_database.json → Weekly Aggregation → Weekly Template → weekly/dashboard/output/
```

### CLI Interface
- `--week YYYY-Www`: Generate a specific ISO week (Mon–Sun)
- `--last-7-days`: Generate for the last 7 days (ending yesterday)
- `--fill-missing-days`: Select the most recent 7 valid days if some are missing/flagged in DB (uses daily HTML fallback)
- `--validate-only`: Print KPIs and exit non-zero if required fields missing

### Fallback Behavior
If DB entries are missing or marked `has_email_data=false`/`has_sla_data=false`, the weekly generator parses KPI values from daily HTML outputs in `daily/dashboard/output` to ensure completeness.

### Integration with Daily System
- Reuses `config/sla_config.json` for business hours, thresholds, and targets
- Maintains design parity with `daily/dashboard/templates/kpi_cards.html`

This architecture preserves data integrity and continuity while providing robust weekly aggregation with graceful degradation when DB gaps exist.
