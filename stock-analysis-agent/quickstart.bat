@echo off
REM Quick Start Script for Stock Analysis Agent (Windows)

echo ==================================
echo Stock Analysis Agent - Quick Start
echo ==================================
echo.
echo WARNING: Educational tool only!
echo    NOT for actual trading decisions.
echo ==================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    echo Please install Python 3.11 or higher
    pause
    exit /b 1
)

python --version
echo.

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install requirements
echo Installing Python dependencies...
echo (This may take a few minutes...)
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet
echo Dependencies installed
echo.

REM Download NLTK data
echo Downloading NLP data...
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('vader_lexicon', quiet=True); nltk.download('stopwords', quiet=True)"
echo NLP data downloaded
echo.

REM Create directories
echo Creating directories...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
echo Directories created
echo.

REM Initialize system
echo Initializing system...
echo n | python -m src.cli setup
echo System initialized
echo.

REM Run tests
echo Running system tests...
python -m src.cli test
echo.

echo ==================================
echo Setup Complete!
echo ==================================
echo.
echo You can now use the system!
echo.
echo Try these commands:
echo   python -m src.cli market quote AAPL
echo   python -m src.cli news scan
echo   python -m src.cli analyze stock TSLA
echo.
echo For detailed guide, see: GETTING_STARTED.md
echo.
echo To activate virtual environment in future:
echo   venv\Scripts\activate.bat
echo.
pause
