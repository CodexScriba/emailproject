# Data Ingest Directory

This directory is used for placing CSV files to be processed by the email ingestion system.

## Expected Files:
- `Complete_List_Raw.csv` - Email event data
- `UnreadCount.csv` - SLA unread count metrics

## Usage:
1. Place your CSV files in this directory
2. Run `update_database.sh` or `python3 daily/scripts/ingest_and_update.py`
3. Files will be processed and moved to `data/backup/` automatically

The ingestion system will:
- Process complete conversations across multiple days
- Update the unified JSON database
- Create timestamped backups
- Move processed files to backup folder