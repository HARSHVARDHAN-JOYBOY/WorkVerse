@echo off
REM WorkVerse - Windows Setup Script

echo ==========================================
echo    WorkVerse - Setup Script (Windows)
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python 3 is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo [OK] Python found
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [OK] Virtual environment created
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [OK] Dependencies installed successfully
echo.

REM Create uploads directory
echo Creating uploads directory...
if not exist "uploads" mkdir uploads
echo [OK] Uploads directory created
echo.

REM Database setup instructions
echo ==========================================
echo    Database Setup
echo ==========================================
echo.
echo Please ensure MySQL is running before proceeding.
echo.
echo To set up the database:
echo 1. Open MySQL Command Line Client or MySQL Workbench
echo 2. Run the following command:
echo    source database/schema.sql
echo.
echo OR from command line:
echo    mysql -u root -p ^< database/schema.sql
echo.
pause

REM Configuration instructions
echo.
echo ==========================================
echo    Configuration
echo ==========================================
echo.
echo IMPORTANT: Update config.py with your MySQL credentials
echo.
echo Default settings:
echo   DB_USER: root
echo   DB_PASSWORD: password
echo   DB_NAME: workverse_db
echo.
echo Edit config.py if your settings are different.
echo.
pause

REM Final instructions
echo.
echo ==========================================
echo    Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo.
echo 1. Activate virtual environment:
echo    venv\Scripts\activate
echo.
echo 2. Update config.py with your database credentials
echo.
echo 3. Run the application:
echo    python app.py
echo.
echo 4. Open browser and navigate to:
echo    http://127.0.0.1:5000
echo.
echo 5. Login with admin credentials:
echo    Email: admin@workverse.com
echo    Password: admin123
echo.
echo WARNING: Change the admin password after first login!
echo.
echo ==========================================
echo For more information, see README.md
echo ==========================================
echo.
pause
