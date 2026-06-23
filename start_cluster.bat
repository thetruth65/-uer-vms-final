@echo off
echo ==================================================
echo   Electoral System - Microservices Cluster Boot
echo ==================================================

echo 1. Starting Blockchain Service (Port 5000)...
start "Blockchain Node" cmd /k "cd blockchain-service && set PYTHONPATH=. && python -m uvicorn main:app --port 5000 --reload"

echo 2. Starting AI Biometric Service (Port 8001)...
start "AI Deduplication" cmd /k "cd ai-service && set PYTHONPATH=. && python -m uvicorn app.main:app --port 8001 --reload"

echo 3. Starting State Backend A - Delhi (Port 8000)...
start "Backend - Delhi" cmd /k "cd backend && set PYTHONPATH=. && set STATE_ID=STATE_A && set STATE_NAME=Delhi && set PEER_BACKEND_URL=http://localhost:8002 && set AI_SERVICE_URL=http://localhost:8001 && set BLOCKCHAIN_SERVICE_URL=http://localhost:5000 && python -m uvicorn app.main:app --port 8000 --reload"

echo 4. Starting State Backend B - Maharashtra (Port 8002)...
start "Backend - Maharashtra" cmd /k "cd backend && set PYTHONPATH=. && set STATE_ID=STATE_B && set STATE_NAME=Maharashtra && set PEER_BACKEND_URL=http://localhost:8000 && set AI_SERVICE_URL=http://localhost:8001 && set BLOCKCHAIN_SERVICE_URL=http://localhost:5000 && python -m uvicorn app.main:app --port 8002 --reload"

echo 5. Starting State Backend C - Karnataka (Port 8004)...
start "Backend - Karnataka" cmd /k "cd backend && set PYTHONPATH=. && set STATE_ID=STATE_C && set STATE_NAME=Karnataka && set PEER_BACKEND_URL=http://localhost:8000 && set AI_SERVICE_URL=http://localhost:8001 && set BLOCKCHAIN_SERVICE_URL=http://localhost:5000 && python -m uvicorn app.main:app --port 8004 --reload"

echo ==================================================
echo All Microservices have been launched in separate windows!
echo Please wait about 45-60 seconds for the AI service to load the TensorFlow models.
echo ==================================================
pause
