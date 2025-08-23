# Email Project Environment Setup Guide

## Quick Setup

1. **Run the setup script:**
   ```batch
   setup_environment.bat
   ```

2. **Verify installation:**
   ```batch
   python --version
   pip list | findstr pandas
   pip list | findstr jinja2
   ```

## Manual Setup (Alternative)

### Prerequisites
- **Python 3.7+** (tested with Python 3.8+)
- **pip** (Python package installer)

### Installation Steps

1. **Install Python Dependencies:**
   ```batch
   pip install -r requirements.txt
   ```

2. **Verify Directory Structure:**
   ```
   emailproject/
   ├── data/
   │   ├── ingest/         # Place CSV files here
   │   └── backup/         # Automatic backups
   ├── database/           # JSON database storage
   ├── config/             # Configuration files
   ├── daily/scripts/      # Processing scripts
   └── requirements.txt    # Python dependencies
   ```

## Dependencies

The project requires these Python packages:

- **pandas** (≥1.5.0) - Data manipulation and CSV processing
- **numpy** (≥1.24.0) - Numerical operations
- **jinja2** (≥3.1.0) - HTML template engine for dashboards

## Configuration

### SLA Configuration
Edit `config/sla_config.json` to customize:
- Business hours (default: 7 AM - 9 PM)
- SLA thresholds (default: 30 unread emails)
- Response time targets (default: 60 minutes)

### Directory Structure
The setup script creates these directories if missing:
- `data/ingest/` - For placing new CSV files
- `data/backup/` - Automatic backups with timestamps
- `database/` - JSON database storage

## Usage Workflow

### 1. Data Ingestion
```batch
# Place files in data/ingest/:
# - Complete_List_Raw.csv
# - UnreadCount.csv

# Run the update
update_database.bat
```

### 2. Dashboard Generation
```batch
# Generate daily dashboard
python daily/scripts/generate_dashboard.py

# Generate weekly dashboard  
python weekly/scripts/generate_weekly_dashboard.py

# View latest dashboard
start daily/dashboard/output/latest.html
```

### 3. Data Processing Features
- **Complete conversation tracking** across multiple days
- **Automatic deduplication** prevents double-counting
- **Intelligent merging** with existing data
- **Timestamped backups** for audit trail

## Troubleshooting

### Python Installation Issues
```batch
# Check Python version
python --version

# Check if pip is available
pip --version

# Install/upgrade pip if needed
python -m ensurepip --upgrade
```

### Package Installation Issues
```batch
# Upgrade pip first
python -m pip install --upgrade pip

# Install packages individually if batch fails
pip install pandas>=1.5.0
pip install numpy>=1.24.0
pip install jinja2>=3.1.0
```

### Missing Directories
```batch
# Create manually if setup script fails
mkdir data\ingest
mkdir data\backup
mkdir database
```

### File Permission Issues
- Ensure you have write permissions in the project directory
- Run command prompt as Administrator if needed
- Check antivirus settings (may block file operations)

## Project Architecture

### Core Components
- **Ingestion System** (`daily/scripts/ingest_and_update.py`)
  - Processes CSV files intelligently
  - Handles cross-day conversations
  - Creates automatic backups

- **Dashboard Generator** (`daily/scripts/generate_dashboard.py`)
  - Creates HTML dashboards with SVG charts
  - Uses configurable business hours
  - Responsive design with modern styling

- **Configuration** (`config/sla_config.json`)
  - Business hours and SLA thresholds
  - KPI targets and alert levels
  - Customizable for different organizations

### Data Flow
```
CSV Files → [data/ingest/] → Ingestion → [database/email_database.json] → Dashboard → HTML Output
```

## Advanced Features

### Weekly Dashboards
```batch
# Generate weekly dashboard
python weekly/scripts/generate_weekly_dashboard.py --last-7-days
python weekly/scripts/generate_weekly_dashboard.py --week 2024-W33
```

### Command Line Options
```batch
# List available dates
python daily/scripts/generate_dashboard.py --list-dates

# Generate for specific date
python daily/scripts/generate_dashboard.py --date 2024-08-20

# Validate data completeness
python daily/scripts/generate_dashboard.py --date 2024-08-20 --validate-only
```

## Getting Help

1. **Check logs** - Scripts provide detailed logging output
2. **Validate data** - Use `--validate-only` flags to check data completeness
3. **Review backups** - Check `data/backup/` for timestamped file copies
4. **Configuration** - Verify `config/sla_config.json` settings

## Performance Notes

- Processing time: Typically < 30 seconds for most datasets
- Memory usage: Moderate (depends on CSV file size)
- Storage: Minimal (JSON database is compressed)
- Browser compatibility: Modern browsers (Chrome, Firefox, Edge)