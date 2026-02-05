# Discord Music Bot - Setup Guide

A feature-rich Discord music bot with queue management, playlist saving, and a live web interface to view the current queue and playlists.

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

1. **Python 3.8 or higher**
2. **FFmpeg** - Required for audio playback
3. **Discord Bot Token** - Create a bot at https://discord.com/developers/applications
4. **Cloudflare Tunnel** (optional) - For external access to web interface

## Installation

### 1. Install FFmpeg

**Windows:**
- Download from https://ffmpeg.org/download.html
- Extract and add to PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Discord Bot

1. Go to https://discord.com/developers/applications
2. Click "New Application" and give it a name
3. Go to "Bot" section and click "Add Bot"
4. Under "Privileged Gateway Intents", enable:
   - Message Content Intent
   - Server Members Intent
   - Presence Intent
5. Click "Reset Token" and copy your bot token
6. Go to "OAuth2" → "URL Generator"
7. Select scopes: `bot`, `applications.commands`
8. Select bot permissions:
   - Connect
   - Speak
   - Use Voice Activity
   - Send Messages
   - Embed Links
   - Read Message History
9. Copy the generated URL and open it in your browser to invite the bot to your server

### 4. Configure the Bot

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

```bash
cloudflared tunnel create discord-music-bot
```

This creates a tunnel and outputs a tunnel ID. Save this ID.

### 4. Configure the Tunnel

Create a config file at `~/.cloudflared/config.yml`:

```yaml
tunnel: <YOUR_TUNNEL_ID>
credentials-file: /Users/<your-user>/.cloudflared/<YOUR_TUNNEL_ID>.json

ingress:
  - hostname: music-bot.yourdomain.com
    service: http://localhost:5000
  - service: http_status:404
```

Replace:
- `<YOUR_TUNNEL_ID>` with your tunnel ID
- `<your-user>` with your username
- `music-bot.yourdomain.com` with your desired subdomain

### 5. Set Up DNS

```bash
cloudflared tunnel route dns <YOUR_TUNNEL_ID> music-bot.yourdomain.com
```

### 6. Run the Tunnel

```bash
cloudflared tunnel run discord-music-bot
```

Or run it in the background:

```bash
cloudflared tunnel run discord-music-bot &
```

### Quick Setup (No Custom Domain)

If you don't have a domain, use the quick tunnel feature:

```bash
cloudflared tunnel --url http://localhost:5000
```

This will give you a temporary `.trycloudflare.com` URL that you can share.

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

## Troubleshooting

### Bot doesn't play audio
- Ensure FFmpeg is installed and in your PATH
- Check that the bot has "Connect" and "Speak" permissions
- Try rejoining the voice channel with `!leave` then `!join`

### "429 Too Many Requests" errors
- YouTube may be rate limiting. Wait a few minutes and try again
- Consider using a VPN if the issue persists

### Web interface shows old data
- The interface auto-refreshes every 5 seconds
- Click the refresh button (⟳) in the bottom right to force an update
- Ensure both the bot and web app are running

### Cloudflare Tunnel connection issues
- Verify the tunnel is running: `cloudflared tunnel info <TUNNEL_ID>`
- Check the config file path is correct
- Ensure port 5000 is not blocked by firewall

## Advanced Configuration

### Change Web Interface Port

Edit `web_app.py`:

```python
app.run(host='0.0.0.0', port=8080, debug=True)  # Change 5000 to 8080
```

Remember to update your Cloudflare Tunnel config accordingly.

### Auto-start on System Boot

**Linux (systemd):**

Create `/etc/systemd/system/discord-music-bot.service`:

```ini
[Unit]
Description=Discord Music Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/bot
Environment="DISCORD_TOKEN=your-token"
ExecStart=/usr/bin/python3 discord_music_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable discord-music-bot
sudo systemctl start discord-music-bot
```

Do the same for the web app and Cloudflare Tunnel.

## Security Notes

- Never commit your Discord token to version control
- Use environment variables for sensitive data
- The web interface is read-only (users can't control playback from the web)
- Consider adding authentication to the web interface if exposing publicly

## License

This project is provided as-is for personal use.

## Support

For issues or questions:
1. Check that all dependencies are installed
2. Verify FFmpeg is working: `ffmpeg -version`
3. Check bot permissions in Discord
4. Review logs for error messages
