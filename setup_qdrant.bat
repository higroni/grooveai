@echo off
echo ========================================
echo GROOVE.AI - Qdrant Setup
echo ========================================
echo.

echo Step 1: Starting Qdrant with Docker Compose...
docker-compose -f docker-compose.qdrant.yml up -d

echo.
echo Waiting for Qdrant to be ready...
timeout /t 10 /nobreak > nul

echo.
echo Step 2: Checking Qdrant health...
curl -s http://localhost:6333/health

echo.
echo.
echo ========================================
echo Qdrant is ready!
echo ========================================
echo.
echo Web UI: http://localhost:6333/dashboard
echo REST API: http://localhost:6333
echo.
echo To load data, run: python load_data_to_qdrant.py
echo To stop Qdrant: docker-compose -f docker-compose.qdrant.yml down
echo.
pause

@REM Made with Bob
