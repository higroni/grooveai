@echo off
echo ============================================================
echo GROOVE.AI - Restart All Modules
echo ============================================================
echo.

echo [STEP 1] Stopping all Python processes on module ports...
echo.

REM Kill processes on specific ports
for %%p in (8101 8102 8103 8105 8106) do (
    echo Checking port %%p...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%%p ^| findstr LISTENING') do (
        echo   Killing process %%a on port %%p
        taskkill /F /PID %%a >nul 2>&1
    )
)

echo.
echo [OK] All processes stopped
echo.
timeout /t 2 /nobreak >nul

echo [STEP 2] Starting all modules...
echo.

REM Start Module 1: File Reader (port 8101)
echo Starting Module 1: File Reader (port 8101)...
start "Module 1: File Reader" cmd /k "python modules/file_reader/main.py"
timeout /t 2 /nobreak >nul

REM Start Module 2: Text Normalizer (port 8102)
echo Starting Module 2: Text Normalizer (port 8102)...
start "Module 2: Text Normalizer" cmd /k "python modules/text_normalizer/main.py"
timeout /t 2 /nobreak >nul

REM Start Module 3: Latinizer (port 8103)
echo Starting Module 3: Latinizer (port 8103)...
start "Module 3: Latinizer" cmd /k "python modules/latinizer/main.py"
timeout /t 2 /nobreak >nul

REM Start Module 4: Legal Parser (port 8105)
echo Starting Module 4: Legal Parser (port 8105)...
start "Module 4: Legal Parser" cmd /k "python modules/legal_parser/main.py"
timeout /t 2 /nobreak >nul

REM Start Module 6: Assertion Extractor (port 8106)
echo Starting Module 6: Assertion Extractor (port 8106)...
start "Module 6: Assertion Extractor" cmd /k "python modules/assertion_extractor/main.py"
timeout /t 2 /nobreak >nul

echo.
echo [OK] All modules started!
echo.
echo Waiting 5 seconds for modules to initialize...
timeout /t 5 /nobreak >nul

echo.
echo [STEP 3] Checking module health...
echo.

REM Check each module
python -c "import requests; import sys; modules = [('File Reader', 8101), ('Text Normalizer', 8102), ('Latinizer', 8103), ('Legal Parser', 8105), ('Assertion Extractor', 8106)]; [print(f'[OK] {name} (port {port})') if requests.get(f'http://localhost:{port}/health', timeout=2).status_code == 200 else print(f'[ERROR] {name} (port {port})') for name, port in modules]" 2>nul

if errorlevel 1 (
    echo.
    echo [WARN] Some modules may not be ready yet. Wait a few more seconds and check manually.
)

echo.
echo ============================================================
echo All modules should be running now!
echo ============================================================
echo.
echo Module URLs:
echo   - Module 1 (File Reader):        http://localhost:8101
echo   - Module 2 (Text Normalizer):    http://localhost:8102
echo   - Module 3 (Latinizer):          http://localhost:8103
echo   - Module 4 (Legal Parser):       http://localhost:8105
echo   - Module 6 (Assertion Extractor): http://localhost:8106
echo.
echo To run integration test:
echo   python test_pipeline_modules_1_2_3_4_6.py
echo.
pause

@REM Made with Bob
