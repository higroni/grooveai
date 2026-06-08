@echo off
REM Memory Monitor - Shows top 5 processes by memory usage
REM Usage: monitor_memory.bat [interval] [process_name]
REM Example: monitor_memory.bat 2 python.exe

echo Starting Memory Monitor...
echo.

if "%1"=="" (
    REM Default: 2 second interval, no specific process
    python monitor_memory.py
) else if "%2"=="" (
    REM Custom interval, no specific process
    python monitor_memory.py --interval %1
) else (
    REM Custom interval and process name
    python monitor_memory.py --interval %1 --process %2
)

@REM Made with Bob
