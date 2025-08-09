@echo off
echo Installing LLM Query-Retrieval System on Windows...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found. Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing core packages...
pip install fastapi==0.104.1
pip install uvicorn==0.24.0
pip install python-multipart==0.0.6
pip install pydantic==2.5.0
pip install requests==2.31.0

echo Installing document processing packages...
pip install PyPDF2==3.0.1
pip install python-docx==1.1.0

echo Installing ML packages...
pip install scikit-learn==1.3.2
pip install numpy==1.24.3

echo Installing Google Gemini and utilities...
pip install google-generativeai==0.3.2
pip install pandas==2.1.3
pip install python-dotenv==1.0.0
pip install aiofiles==23.2.0
pip install httpx==0.25.2

echo.
echo ✅ Installation completed successfully!
echo.
echo To run the application:
echo 1. Make sure virtual environment is activated: venv\Scripts\activate
echo 2. Set your Gemini API key in .env file
echo 3. Run: python main.py
echo.
pause