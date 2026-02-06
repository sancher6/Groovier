# Discord Music Bot - Setup Guide

A Discord music bot with queue management, playlist saving, and a live web interface to view the current queue and playlists.

## Features

### Discord Bot Commands
- `!join` - Join your current voice channel
- `!leave` - Leave the voice channel and clear queue
- `!play <song/URL>` - Play a song (YouTube URL or search query)
- `!pause` - Pause the current song
- `!resume` - Resume the paused song
- `!skip` - Skip the current song
- `!queue` - Show the current queue
- `!clear` - Clear the entire queue
- `!nowplaying` - Show currently playing song
- `!playlist_save <name>` - Save current queue as a playlist
- `!playlist_load <name>` - Load a saved playlist
- `!playlist_list` - List all saved playlists
- `!playlist_delete <name>` - Delete a saved playlist

### Web Interface
- Real-time view of currently playing song
- Live queue display
- View all saved playlists
- Auto-refreshes every 5 seconds
- Distinctive retro-futuristic design with vinyl record animation

## Prerequisites

1. **Python 3.11 or higher**
2. **FFmpeg** - Required for audio playback
3. **Discord Bot Token** - Create a bot at https://discord.com/developers/applications
4. **Cloudflare Tunnel** (optional) - For external access to web interface

## Installation

### 1. Configure the Bot

Edit `discord_music_bot.py` and replace the token:

```python
DISCORD_TOKEN = 'YOUR_BOT_TOKEN_HERE'
```

Or set it as an environment variable:

```bash
export DISCORD_TOKEN='YOUR_BOT_TOKEN_HERE'
```

## Running the Bot

### Start the Discord Bot

```bash
python discord_music_bot.py
```

### Start the Web Interface

In a separate terminal:

```bash
python web_app.py
```

The web interface will be available at `http://localhost:5000`

## Setting Up Cloudflare Tunnel

To make the web interface accessible to your Discord server members:

### 1. Install Cloudflare Tunnel

**Windows:**
- Download from https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/

**macOS:**
```bash
brew install cloudflare/cloudflare/cloudflared
```

**Linux:**
```bash
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

### 2. Authenticate Cloudflare Tunnel

```bash
cloudflared tunnel login
```

This will open a browser window to authenticate with your Cloudflare account.

### 3. Create a Tunnel

First run application
```bash
python web_app.py
```

Then create tunnel
```bash
winget install --id Cloudflare.cloudflared
``` 

## Usage Guide

### Playing Music

1. Join a voice channel in Discord
2. Type `!join` to make the bot join your channel
3. Type `!play <song name or URL>` to add songs to the queue
4. Multiple users can add songs - they'll be added to the queue in order

### Managing Queue

- See what's playing: `!nowplaying`
- View the queue: `!queue`
- Skip a song: `!skip`
- Pause/Resume: `!pause` and `!resume`
- Clear everything: `!clear`

### Creating Playlists

1. Add songs to the queue using `!play`
2. Save the queue as a playlist: `!playlist_save My Playlist`
3. Later, load it anytime: `!playlist_load My Playlist`
4. View all playlists: `!playlist_list`

### Viewing the Web Interface

1. Open the URL in your browser (either `http://localhost:5000` or your Cloudflare Tunnel URL)
2. The page will automatically refresh every 5 seconds
3. You'll see:
   - Current playback status (Playing/Paused/Stopped)
   - Currently playing song with animated vinyl record
   - Upcoming songs in the queue
   - All saved playlists

Share the Cloudflare Tunnel URL with your Discord server members so they can view what's playing!

## File Structure

```
discord-music-bot/
├── discord_music_bot.py    # Main Discord bot
├── web_app.py              # Flask web application
├── templates/
│   └── index.html          # Web interface
├── requirements.txt        # Python dependencies
├── playlists.json         # Saved playlists (auto-generated)
├── current_queue.json     # Current queue state (auto-generated)
└── README.md              # This file
```