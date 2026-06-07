@echo off
echo Starting all GROOVE.AI modules...
echo.

start "M1-FileReader" cmd /k "python -m modules.file_reader.main"
timeout /t 2 /nobreak >nul

start "M2-TextNormalizer" cmd /k "python -m modules.text_normalizer.main"
timeout /t 2 /nobreak >nul

start "M3-Latinizer" cmd /k "python -m modules.latinizer.main"
timeout /t 2 /nobreak >nul

start "M4-LegalParser" cmd /k "python -m modules.legal_parser.main"
timeout /t 2 /nobreak >nul

start "M6-AssertionExtractor" cmd /k "python -m modules.assertion_extractor.main"
timeout /t 2 /nobreak >nul

start "M7-EntityRecognizer" cmd /k "python -m modules.entity_recognizer.main"
timeout /t 2 /nobreak >nul

start "M8-ConditionExtractor" cmd /k "python -m modules.condition_extractor.main"
timeout /t 2 /nobreak >nul

start "M9-AssertionClassifier" cmd /k "python -m modules.assertion_classifier.main"
timeout /t 2 /nobreak >nul

start "M10-KnowledgeEnrichment" cmd /k "python -m modules.knowledge_enrichment.main"

echo.
echo All modules started in separate windows.
echo Wait 10-15 seconds for all modules to initialize, then run tests.
echo.
pause

@REM Made with Bob
