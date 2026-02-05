import json
import asyncio

from pathlib import Path
from collections import deque
from groovier.constants import *

class MusicPlayer:
    def __init__(self, bot):
        self.bot = bot
        self.queue = deque()
        self.current_song = None
        self.voice_client = None
        self.playlists = self.load_playlists()
        self.is_playing = False
        self.is_paused = False

    def load_playlists(self):
        """Load saved playlists from file"""
        if Path(PLAYLISTS_FILE).exists():
            with open(PLAYLISTS_FILE, 'r') as f:
                data = json.load(f)
                # Convert song dicts back to Song objects
                for playlist_name in data:
                    data[playlist_name] = [Song.from_dict(s) for s in data[playlist_name]]
                return data
        return {}

    def save_playlists(self):
        """Save playlists to file"""
        data = {name: [s.to_dict() for s in songs] for name, songs in self.playlists.items()}
        with open(PLAYLISTS_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def save_queue_state(self):
        """Save current queue state for web interface"""
        queue_data = {
            'current_song': self.current_song.to_dict() if self.current_song else None,
            'queue': [s.to_dict() for s in self.queue],
            'is_playing': self.is_playing,
            'is_paused': self.is_paused
        }
        with open(QUEUE_FILE, 'w') as f:
            json.dump(queue_data, f, indent=2)

    async def search_song(self, query):
        """Search for a song and return Song object"""
        loop = asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))
            
            if 'entries' in data:
                # Take first result from search
                data = data['entries'][0]
            
            song_url = data['url']
            title = data['title']
            duration = data.get('duration', 0)
            thumbnail = data.get('thumbnail', '')
            
            return song_url, title, duration, thumbnail
        except Exception as e:
            print(f"Error searching song: {e}")
            return None

    async def play_next(self):
        """Play the next song in queue"""
        if len(self.queue) > 0:
            self.current_song = self.queue.popleft()
            self.is_playing = True
            self.is_paused = False
            
            try:
                source = discord.FFmpegPCMAudio(self.current_song.url, **ffmpeg_options)
                self.voice_client.play(
                    source,
                    after=lambda e: asyncio.run_coroutine_threadsafe(
                        self.play_next(), self.bot.loop
                    )
                )
                self.save_queue_state()
            except Exception as e:
                print(f"Error playing song: {e}")
                await self.play_next()
        else:
            self.current_song = None
            self.is_playing = False
            self.is_paused = False
            self.save_queue_state()

    async def add_to_queue(self, song):
        """Add a song to the queue"""
        self.queue.append(song)
        self.save_queue_state()
        
        if not self.is_playing and self.voice_client:
            await self.play_next()