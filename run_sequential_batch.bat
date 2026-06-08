@echo off
REM Sequential Batch Processor - No multiprocessing, automatic restart
REM Usage: run_sequential_batch.bat

echo ========================================
echo SEQUENTIAL BATCH PROCESSOR
echo ========================================
echo.
echo This version processes documents one at a time
echo and automatically restarts every 20 documents
echo to prevent memory leaks.
echo.
echo ========================================
echo.

REM Configuration
set INPUT_DIR=D:\POSAO\ZAKON_O_RADU\ZAKON_O_RADU_DOCX
set OUTPUT_DIR=batch_output_sequential
set RESTART_INTERVAL=20

echo Input:  %INPUT_DIR%
echo Output: %OUTPUT_DIR%
echo Restart interval: %RESTART_INTERVAL% documents
echo.
echo Press Ctrl+C to stop
echo.

python batch_processor_sequential.py --input-dir "%INPUT_DIR%" --output-dir "%OUTPUT_DIR%" --restart-interval %RESTART_INTERVAL%

echo.
echo ========================================
echo PROCESSING COMPLETE
echo ========================================
pause

@REM Made with Bob
