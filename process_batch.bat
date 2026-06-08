@echo off
setlocal enabledelayedexpansion

REM ============================================================================
REM GROOVE.AI Batch Processor - Windows Batch Script
REM ============================================================================
REM Processes all documents in input directory by calling Python script
REM for each file separately. NO Python orchestrator - pure batch script.
REM ============================================================================

set INPUT_DIR=%1
set OUTPUT_DIR=%2
set SEMANTIC=%3

if "%INPUT_DIR%"=="" (
    echo ERROR: Input directory not specified
    echo Usage: process_batch.bat INPUT_DIR OUTPUT_DIR [--disable-semantic]
    exit /b 1
)

if "%OUTPUT_DIR%"=="" (
    echo ERROR: Output directory not specified
    echo Usage: process_batch.bat INPUT_DIR OUTPUT_DIR [--disable-semantic]
    exit /b 1
)

REM Create output directory if it doesn't exist
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

echo ================================================================================
echo BATCH PROCESSOR - WINDOWS BATCH MODE
echo ================================================================================
echo Input directory: %INPUT_DIR%
echo Output directory: %OUTPUT_DIR%
echo Semantic extraction: %SEMANTIC%
echo ================================================================================
echo.

set /a TOTAL=0
set /a PROCESSED=0
set /a FAILED=0

REM Count total files
for %%F in ("%INPUT_DIR%\*.pdf" "%INPUT_DIR%\*.docx" "%INPUT_DIR%\*.txt") do (
    set /a TOTAL+=1
)

echo Total documents: !TOTAL!
echo.

REM Process each file
set /a COUNTER=0
for %%F in ("%INPUT_DIR%\*.pdf" "%INPUT_DIR%\*.docx" "%INPUT_DIR%\*.txt") do (
    set /a COUNTER+=1
    echo [!COUNTER!/!TOTAL!] %%~nxF
    
    REM Build command
    set CMD=python process_single_document.py --input-file "%%F" --output-dir "%OUTPUT_DIR%"
    if "%SEMANTIC%"=="--disable-semantic" set CMD=!CMD! --disable-semantic
    
    REM Execute command
    !CMD!
    
    REM Check exit code
    if !ERRORLEVEL! EQU 0 (
        set /a PROCESSED+=1
    ) else (
        set /a FAILED+=1
        echo   ERROR: Processing failed with code !ERRORLEVEL!
    )
    
    echo.
)

REM Summary
echo ================================================================================
echo BATCH PROCESSING COMPLETE
echo ================================================================================
echo Total processed: !PROCESSED!/!TOTAL!
echo Failed: !FAILED!
set /a SUCCESS_RATE=!PROCESSED!*100/!TOTAL!
echo Success rate: !SUCCESS_RATE!%%
echo ================================================================================

endlocal

@REM Made with Bob
