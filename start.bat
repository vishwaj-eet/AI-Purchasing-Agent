@echo off
echo ==============================================================================
echo ProcurePulse AI - Autonomous Procurement & Supply Chain Agent Platform
echo ==============================================================================
echo.
echo Installing dependencies (if needed)...
python -m pip install -r requirements.txt
echo.
echo Starting FastAPI and LangGraph multi-agent orchestrator...
echo Access Web Dashboard at: http://localhost:8000
echo Access OpenAPI Specs at: http://localhost:8000/docs
echo.
python main.py
pause
