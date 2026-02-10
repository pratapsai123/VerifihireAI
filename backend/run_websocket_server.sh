#!/bin/bash
# Run Django server with WebSocket support using Daphne
cd "$(dirname "$0")"
echo "Starting Django server with WebSocket support..."
echo ""
echo "Server will be available at:"
echo "  HTTP: http://127.0.0.1:8001/"
echo "  WebSocket: ws://127.0.0.1:8001/ws/interview/{session_id}/{role}/"
echo ""
daphne -b 0.0.0.0 -p 8001 VerifiHireAI_backend.asgi:application
