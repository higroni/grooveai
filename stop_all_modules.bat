@echo off
echo ============================================================
echo GROOVE.AI - Stop All Modules
echo ============================================================
echo.

echo Stopping all Python processes on module ports...
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
echo [OK] All modules stopped
echo.
pause

@REM Made with Bob
