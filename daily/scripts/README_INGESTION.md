# Email Database Ingestion System

## Overview
The `ingest_and_update.py` script provides intelligent ingestion of email data that handles complete conversations across multiple days, preventing data loss from day-boundary filtering.

## Key Features

### 1. **Complete Conversation Tracking**
- Processes entire `Complete_List_Raw.csv` file
- Tracks conversations that span multiple days
- Matches inbox emails with replies/completions regardless of date boundaries

### 2. **Intelligent Merging**
- Updates existing data without overwriting
- Deduplicates events to prevent double-counting
- Preserves historical data while adding new information

### 3. **Automatic Backup System**
- Creates timestamped backups before any updates
- Moves processed files to backup folder after successful ingestion
- Maintains audit trail of all data changes

## Usage

### Simple Method (Recommended)
```bash
# From project root:
./update_database.sh
```

### Direct Python Method
```bash
# Place files in data/ingest/:
# - Complete_List_Raw.csv
# - UnreadCount.csv

# Run the ingestion:
python3 daily/scripts/ingest_and_update.py
```

## How It Works

### 1. **File Processing**
- Reads `Complete_List_Raw.csv` from `data/ingest/`
- Reads `UnreadCount.csv` from `data/ingest/`
- Creates backups with timestamps in `data/backup/`

### 2. **Conversation Analysis**
- Groups all events by Conversation-Id
- For each inbox email, finds the next reply or completed event
- Calculates business hours response time
- Handles conversations that span multiple days

### 3. **Database Update**
- Loads existing `email_database.json`
- Merges new data intelligently:
  - Updates existing days with new information
  - Adds new days as needed
  - Preserves all historical data
- Saves updated database

### 4. **Cleanup**
- Moves processed files to `data/backup/` with timestamp
- Keeps ingest folder clean for next update

## File Structure

```
data/
├── ingest/              # Place new files here
│   ├── Complete_List_Raw.csv
│   └── UnreadCount.csv
├── backup/              # Automatic backups stored here
│   ├── Complete_List_Raw_20250819_143022.csv
│   ├── UnreadCount_20250819_143022.csv
│   └── email_database_20250819_143022.json
database/
└── email_database.json  # Main database (updated)
```

## Benefits Over Date Filtering

### Previous Approach (Date Filtering)
❌ Lost conversations that span multiple days
❌ Incomplete response time calculations
❌ Manual date range selection required
❌ Risk of missing important data

### New Approach (Full File Processing)
✅ Captures all conversations completely
✅ Accurate response times across day boundaries
✅ Automatic deduplication
✅ No data loss
✅ Simple "upload and run" workflow

## Example Workflow

1. **Export data from your email system**
   - Export all data to `Complete_List_Raw.csv`
   - Export unread counts to `UnreadCount.csv`

2. **Place files in ingest folder**
   ```bash
   cp /path/to/Complete_List_Raw.csv data/ingest/
   cp /path/to/UnreadCount.csv data/ingest/
   ```

3. **Run update**
   ```bash
   ./update_database.sh
   ```

4. **Generate dashboard**
   ```bash
   python3 dashboard/scripts/generate_dashboard.py
   ```

5. **View results**
   ```bash
   open dashboard/output/latest.html
   ```

## Automatic Features

- **Deduplication**: Prevents counting the same email multiple times
- **Backup Creation**: Every file is backed up before processing
- **Error Recovery**: Corrupted database files are backed up and recreated
- **Audit Trail**: All backups include timestamps for tracking

## Configuration

The script uses `config/sla_config.json` for:
- Business hours (default: 7 AM - 9 PM)
- Business days (default: Mon-Sun)
- SLA threshold (default: 30 unread emails)

## Troubleshooting

### No files found error
- Ensure files are in `data/ingest/` folder
- Check file names match exactly: `Complete_List_Raw.csv`, `UnreadCount.csv`

### Database corruption
- Script automatically backs up corrupted files
- Check `data/backup/` for `email_database_corrupted_*.json`

### Missing conversations
- Verify Complete_List_Raw.csv contains all EventTypes (Inbox, Replied, Completed)
- Check that Conversation-Id values match across events

## Notes

- The script processes ALL data in the input files
- Existing database entries are updated, not replaced
- Processing time depends on data volume (typically < 30 seconds)
- All timestamps are preserved in original timezone
