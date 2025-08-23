@echo off
REM Email Project Environment Setup Script

echo ==========================================
echo Email Project Environment Setup
echo ==========================================
echo.

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and add it to your PATH
    pause
    exit /b 1
)

echo.
echo Installing required Python packages...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python packages
    pause
    exit /b 1
)

echo.
echo Verifying project structure...
if not exist "data\ingest" (
    echo Creating data\ingest directory...
    mkdir "data\ingest"
)

if not exist "data\backup" (
    echo Creating data\backup directory...
    mkdir "data\backup"
)

if not exist "database" (
    echo Creating database directory...
    mkdir "database"
)

echo.
echo ✅ Environment setup complete!
echo.
echo To use the email project:
echo 1. Place CSV files in data\ingest\
echo 2. Run: update_database.bat
echo 3. Generate dashboard: python daily\scripts\generate_dashboard.py
echo 4. View dashboard: daily\dashboard\output\latest.html
echo.
pause