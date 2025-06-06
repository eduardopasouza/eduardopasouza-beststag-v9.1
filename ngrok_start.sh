#!/bin/bash
# Start ngrok tunnel to expose local FastAPI service on port 8000
nohup ngrok http 8000 --log=stdout > /dev/null 2>&1 &
sleep 2
URL=$(curl -s http://localhost:4040/api/tunnels | jq -r .tunnels[0].public_url)
echo "ngrok tunnel URL -> $URL"

