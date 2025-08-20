#!/bin/bash
# Simple wrapper script to update the email database

echo "=========================================="
echo "Email Database Update Tool"
echo "=========================================="
echo ""
echo "This script will:"
echo "1. Process Complete_List_Raw.csv and UnreadCount.csv from data/ingest/"
echo "2. Update the email_database.json with ALL conversations"
echo "3. Create timestamped backups in data/backup/"
echo "4. Move processed files to backup folder"
echo ""

# Check if files exist
if [ ! -f "data/ingest/Complete_List_Raw.csv" ] && [ ! -f "data/ingest/UnreadCount.csv" ]; then
    echo "ERROR: No input files found!"
    echo "Please place at least one of these files in data/ingest/:"
    echo "  - Complete_List_Raw.csv"
    echo "  - UnreadCount.csv"
    exit 1
fi

echo "Found input files:"
[ -f "data/ingest/Complete_List_Raw.csv" ] && echo "  ✓ Complete_List_Raw.csv"
[ -f "data/ingest/UnreadCount.csv" ] && echo "  ✓ UnreadCount.csv"
echo ""

# Run the ingestion script
python3 daily/scripts/ingest_and_update.py

# Check if successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database updated successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Generate dashboard: python3 dashboard/scripts/generate_dashboard.py"
    echo "2. View dashboard: open dashboard/output/latest.html"
else
    echo ""
    echo "❌ Update failed. Check the logs above for details."
    exit 1
fi
