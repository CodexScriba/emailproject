@echo off
REM Windows batch file to update the email database

echo ==========================================
echo Email Database Update Tool
echo ==========================================
echo.
echo This script will:
echo 1. Process Complete_List_Raw.csv and UnreadCount.csv from data\ingest\
echo 2. Update the email_database.json with ALL conversations
echo 3. Create timestamped backups in data\backup\
echo 4. Move processed files to backup folder
echo.

REM Check if files exist
if not exist "data\ingest\Complete_List_Raw.csv" if not exist "data\ingest\UnreadCount.csv" (
    echo ERROR: No input files found!
    echo Please place at least one of these files in data\ingest\:
    echo   - Complete_List_Raw.csv
    echo   - UnreadCount.csv
    exit /b 1
)

echo Found input files:
if exist "data\ingest\Complete_List_Raw.csv" echo   ✓ Complete_List_Raw.csv
if exist "data\ingest\UnreadCount.csv" echo   ✓ UnreadCount.csv
echo.

REM Run the ingestion script
python daily\scripts\ingest_and_update.py

REM Check if successful
if %errorlevel% equ 0 (
    echo.
    echo ✅ Database updated successfully!
    echo.
    echo Next steps:
    echo 1. Generate dashboard: python daily\scripts\generate_dashboard.py
    echo 2. View dashboard: open daily\dashboard\output\latest.html
) else (
    echo.
    echo ❌ Update failed. Check the logs above for details.
    exit /b 1
)