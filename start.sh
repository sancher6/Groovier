#!/bin/bash

# Startup script for Discord Music Bot
# This script starts both the Discord bot and the web interface

echo "Starting Discord Music Bot..."

# Check if .env file exists
if [ -f .env ]; then
    export $(cat .env | xargs)
else
    echo "Warning: .env file not found. Using default settings."
fi

# Check if Discord token is set
if [ -z "$DISCORD_TOKEN" ]; then
    echo "Error: DISCORD_TOKEN not set!"
    echo "Please set it in .env file or as an environment variable."
    exit 1
fi

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "Error: FFmpeg is not installed!"
    echo "Please install FFmpeg before running the bot."
    exit 1
fi

# Create log directory
mkdir -p logs

# Start Discord bot in background
echo "Starting Discord bot..."
python discord_music_bot.py > logs/bot.log 2>&1 &
BOT_PID=$!
echo "Discord bot started (PID: $BOT_PID)"

# Wait a moment for bot to initialize
sleep 2

# Start web app in background
echo "Starting web interface..."
python web_app.py > logs/web.log 2>&1 &
WEB_PID=$!
echo "Web interface started (PID: $WEB_PID)"

echo ""
echo "======================================"
echo "Discord Music Bot is now running!"
echo "======================================"
echo "Discord Bot PID: $BOT_PID"
echo "Web App PID: $WEB_PID"
echo "Web Interface: http://localhost:5000"
echo ""
echo "To stop the bot, run: ./stop.sh"
echo "To view logs:"
echo "  - Bot: tail -f logs/bot.log"
echo "  - Web: tail -f logs/web.log"
echo "======================================"

# Save PIDs to file for stop script
echo "$BOT_PID" > .bot.pid
echo "$WEB_PID" > .web.pid
