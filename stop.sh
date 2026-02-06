#!/bin/bash

# Stop script for Discord Music Bot

echo "Stopping Discord Music Bot..."

# Stop Discord bot
if [ -f .bot.pid ]; then
    BOT_PID=$(cat .bot.pid)
    if ps -p $BOT_PID > /dev/null; then
        echo "Stopping Discord bot (PID: $BOT_PID)..."
        kill $BOT_PID
        echo "Discord bot stopped."
    else
        echo "Discord bot is not running."
    fi
    rm .bot.pid
else
    echo "No Discord bot PID file found."
fi

# Stop web app
if [ -f .web.pid ]; then
    WEB_PID=$(cat .web.pid)
    if ps -p $WEB_PID > /dev/null; then
        echo "Stopping web interface (PID: $WEB_PID)..."
        kill $WEB_PID
        echo "Web interface stopped."
    else
        echo "Web interface is not running."
    fi
    rm .web.pid
else
    echo "No web app PID file found."
fi

echo "Discord Music Bot has been stopped."
