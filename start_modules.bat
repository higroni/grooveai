@echo off
echo Starting all modules...
echo.

start "Module 1: File Reader" cmd /k "python modules/file_reader/main.py"
timeout /t 2 /nobreak >nul

start "Module 2: Text Normalizer" cmd /k "python modules/text_normalizer/main.py"
timeout /t 2 /nobreak >nul

start "Module 3: Latinizer" cmd /k "python modules/latinizer/main.py"
timeout /t 2 /nobreak >nul

start "Module 4: Legal Parser" cmd /k "python modules/legal_parser/main.py"
timeout /t 2 /nobreak >nul

echo.
echo All modules started in separate windows!
echo Press any key to exit this window...
pause >nul

@REM Made with Bob
