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
- **HTML/CSS/JS**: Dashboard output with modern, interactive visualizations
- **SVG**: Vector graphics for chart rendering in the dashboard

## File Tree and Descriptions

```
emailproject/
├── config/
│   └── sla_config.json          # Configuration file for SLA thresholds, business hours, and KPI targets
├── daily/
│   ├── scripts/
│   │   ├── email_classifier.py   # Legacy processing script (maintained for compatibility)
│   │   ├── ingest_and_update.py  # NEW: Intelligent ingestion system for complete conversation tracking
│   │   ├── generate_dashboard.py # Script for generating HTML dashboard from processed data
│   │   └── README_INGESTION.md   # Documentation for the new ingestion system
├── dashboard/
│   ├── templates/
│   │   └── kpi_cards.html        # Jinja2 template for the dashboard HTML structure and styling
│   ├── output/
│   │   ├── email_dashboard_[date].html # Generated dashboard HTML files with date stamps
│   │   └── latest.html           # Symlink to the most recent dashboard file
│   └── README.md                 # Documentation for dashboard usage and features
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

#### Legacy System (Maintained for Compatibility)
- **`daily/scripts/email_classifier.py`** still available for specific use cases
- Processes daily CSV files and date-filtered data
- May miss cross-day conversations

### Dashboard Generation Pipeline
1. **`daily/scripts/generate_dashboard.py`** reads the processed data from:
   - `database/email_database.json` (main data source)
   - `config/sla_config.json` (for business hours and KPI targets)
2. It uses the template file `dashboard/templates/kpi_cards.html` to render the dashboard
3. Generated HTML dashboards are saved in `dashboard/output/` with date-stamped filenames
4. A symlink `dashboard/output/latest.html` is created pointing to the most recent dashboard

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

This architecture ensures complete conversation tracking while maintaining data integrity through automatic backups and intelligent merging.
