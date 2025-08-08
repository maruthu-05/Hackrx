@echo off
echo Fixing sentence-transformers compatibility issue...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

echo Uninstalling problematic packages...
pip uninstall sentence-transformers huggingface_hub transformers torch -y

echo Installing compatible versions...
pip install torch==2.1.2 --index-url https://download.pytorch.org/whl/cpu
pip install transformers==4.36.2
pip install huggingface_hub==0.20.3
pip install sentence-transformers==2.7.0

echo.
echo ✅ Dependencies fixed! Try running python main.py again.
echo.
pause