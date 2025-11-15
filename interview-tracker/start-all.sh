#!/bin/bash

echo "================================================"
echo "Starting Interview Tracker (Backend + Frontend)"
echo "================================================"
echo ""
echo "This will start both the backend and frontend servers."
echo "Backend will run on: http://localhost:8080"
echo "Frontend will run on: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers."
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "All servers stopped."
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend in background
echo "Starting backend..."
cd backend
mvn spring-boot:run > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
echo "Waiting for backend to initialize..."
sleep 10

# Start frontend in background
echo "Starting frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo ""
echo "✓ Backend started (PID: $BACKEND_PID)"
echo "✓ Frontend started (PID: $FRONTEND_PID)"
echo ""
echo "Application is running!"
echo "• Backend API: http://localhost:8080"
echo "• Frontend UI: http://localhost:3000"
echo "• H2 Console: http://localhost:8080/h2-console"
echo ""
echo "Logs are being written to backend.log and frontend.log"
echo ""
echo "Press Ctrl+C to stop all servers."

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
