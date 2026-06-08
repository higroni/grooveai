@echo off
REM Analyze all documents for normative content extraction
REM Usage: run_normative_analysis.bat

echo ========================================
echo NORMATIVE CONTENT ANALYSIS
echo ========================================
echo.
echo This script will process all documents
echo and extract normative content:
echo - Obligations
echo - Prohibitions
echo - Permissions
echo - Definitions
echo.
echo ========================================
echo.

REM Configuration
set INPUT_DIR=D:\POSAO\ZAKON_O_RADU\ZAKON_O_RADU_DOCX
set OUTPUT_FILE=normative_analysis_all.json

echo Input:  %INPUT_DIR%
echo Output: %OUTPUT_FILE%
echo.
echo Press Ctrl+C to cancel, or
pause

python analyze_all_documents_normative.py "%INPUT_DIR%" "%OUTPUT_FILE%"

echo.
echo ========================================
echo ANALYSIS COMPLETE
echo ========================================
echo.
echo Results saved to: %OUTPUT_FILE%
echo.
echo You can now:
echo 1. Open %OUTPUT_FILE% to view results
echo 2. Analyze patterns to improve regex
echo 3. Share results for further analysis
echo.
pause

@REM Made with Bob
