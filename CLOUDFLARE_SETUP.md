# Cloudflare Tunnel Quick Start Guide

This guide will help you set up Cloudflare Tunnel to make your music bot's web interface accessible over the internet.

## Option 1: Quick Tunnel (No Account Required)

This is the fastest way to get started. The URL will be temporary and change each time you restart.

1. **Install Cloudflare Tunnel**
   # Windows - Download from:
   # https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
   This will ask you to run 
   ```bash
   winget install --id Cloudflare.cloudflared
   ``` 
   
2. **Start the Web App**
   ```bash
   python web_app.py
   ```

3. **Start Quick Tunnel**
   ```bash
   cloudflared tunnel --url http://localhost:5000
   ```

4. **Share the URL**
   - Look for a line like: `https://random-words-1234.trycloudflare.com`
   - Share this URL with your Discord server members
   - This URL will work as long as the tunnel is running

**Pros:**
- Super easy, no configuration needed
- Works immediately

**Cons:**
- URL changes every time you restart
- URL expires when you close the tunnel

---

## Option 2: Named Tunnel (Permanent URL)

This creates a permanent tunnel with a custom domain. Requires a Cloudflare account.

### Prerequisites
- A domain registered with Cloudflare (free account works)
- Or use a free subdomain: `your-bot.pages.dev`

### Setup Steps

1. **Install Cloudflare Tunnel** (same as Option 1)

2. **Login to Cloudflare**
   ```bash
   cloudflared tunnel login
   ```
   This opens a browser window - select your domain and authorize.

3. **Create a Named Tunnel**
   ```bash
   cloudflared tunnel create discord-music-bot
   ```
   
   Save the **Tunnel ID** that appears (looks like: `a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6`)

4. **Create Configuration File**
   
   Create `~/.cloudflared/config.yml`:
   
   ```yaml
   tunnel: YOUR_TUNNEL_ID_HERE
   credentials-file: /home/YOUR_USERNAME/.cloudflared/YOUR_TUNNEL_ID_HERE.json
   
   ingress:
     - hostname: music.yourdomain.com
       service: http://localhost:5000
     - service: http_status:404
   ```
   
   Replace:
   - `YOUR_TUNNEL_ID_HERE` with your tunnel ID
   - `YOUR_USERNAME` with your system username
   - `music.yourdomain.com` with your desired subdomain

5. **Set Up DNS**
   ```bash
   cloudflared tunnel route dns YOUR_TUNNEL_ID_HERE music.yourdomain.com
   ```
   
   This automatically creates a DNS record pointing to your tunnel.

6. **Run the Tunnel**
   ```bash
   cloudflared tunnel run discord-music-bot
   ```

7. **Share Your URL**
   - Your web interface is now at: `https://music.yourdomain.com`
   - Share this permanent URL with your server members!

### Keep Tunnel Running

**Run in Background:**
```bash
# macOS/Linux
cloudflared tunnel run discord-music-bot > tunnel.log 2>&1 &

# Windows (PowerShell)
Start-Process cloudflared -ArgumentList "tunnel", "run", "discord-music-bot" -WindowStyle Hidden
```

**Auto-start on Boot (Linux):**

Create `/etc/systemd/system/cloudflared.service`:
```ini
[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
ExecStart=/usr/local/bin/cloudflared tunnel run discord-music-bot
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

**Auto-start on Boot (macOS):**
```bash
brew services start cloudflared
```

---

## Verification

1. **Check Tunnel Status**
   ```bash
   cloudflared tunnel info YOUR_TUNNEL_ID
   ```

2. **Test Your URL**
   - Open the URL in a browser
   - You should see the music bot web interface
   - It should update when you play music in Discord

---

## Troubleshooting

### "Failed to connect to origin"
- Make sure the web app is running on port 5000
- Check that localhost:5000 works locally first

### "Tunnel credentials file not found"
- Verify the path in `config.yml` is correct
- Make sure you've run `cloudflared tunnel create`

### URL not accessible
- Check DNS has propagated: `nslookup music.yourdomain.com`
- Verify tunnel is running: `cloudflared tunnel info YOUR_TUNNEL_ID`
- Check firewall isn't blocking cloudflared

### Want to stop the tunnel?
```bash
# Find the process
ps aux | grep cloudflared

# Kill it
kill <PID>

# Or if running as service
sudo systemctl stop cloudflared
```

---

## Security Tips

1. **The web interface is read-only** - users can only view, not control playback
2. **Consider adding password protection** if your bot plays sensitive content
3. **Monitor access logs** to see who's viewing
4. **Use HTTPS** - Cloudflare Tunnel provides this automatically

---

## Complete Startup Script

Create `start_with_tunnel.sh`:

```bash
#!/bin/bash

echo "Starting Discord Music Bot with Cloudflare Tunnel..."

# Start the Discord bot
python discord_music_bot.py > logs/bot.log 2>&1 &
echo "Bot started (PID: $!)"

# Start the web app
python web_app.py > logs/web.log 2>&1 &
echo "Web app started (PID: $!)"

# Start Cloudflare Tunnel
cloudflared tunnel run discord-music-bot > logs/tunnel.log 2>&1 &
echo "Tunnel started (PID: $!)"

echo ""
echo "Everything is running!"
echo "Access at: https://music.yourdomain.com"
```

Make it executable and run:
```bash
chmod +x start_with_tunnel.sh
./start_with_tunnel.sh
```

---

## Need Help?

- Cloudflare Tunnel Docs: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/
- Check logs in `logs/tunnel.log`
- Test locally first: `curl http://localhost:5000`
