import discord
import os

from discord.ext import commands
from discord.ext.commands.errors import (
    MissingPermissions,
    CommandNotFound,
    ExpectedClosingQuoteError,
)

from dotenv import load_dotenv

from groovier.models.music_player import MusicPlayer
from groovier.models.song import Song
from groovier.constants import *

# Bot setup
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='!', intents=intents)


# Global player instance
player = MusicPlayer(bot)


#####################################################################################################################################
# Events
#####################################################################################################################################

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.change_presence(activity=discord.Game(name="with your mind! Use -help"))
    player.save_queue_state()

@bot.event
async def on_error(event, *args, **kwargs):
    for arg in args:
        if isinstance(arg, Exception):
            raise arg    

@bot.event
async def on_command_error(ctx, error):
    if ctx.cog is not None:
        # Errors coming from cogs
        print(f"Received cog exception: {error}")
        raise error.original

    if isinstance(error, MissingPermissions):
        # Handle missing permissions
        await ctx.channel.send("Permission denied.")
    elif isinstance(error, CommandNotFound):
        await ctx.channel.send("Command not found")
    elif isinstance(error, ExpectedClosingQuoteError):
        await ctx.channel.send("Command not found")
    else:
        await ctx.channel.send("Something went wrong...")
        raise error.original        

#####################################################################################################################################
# Core Commands
#####################################################################################################################################

@bot.command(name='leave', help='Leave the voice channel')
async def leave(ctx):
    if player.voice_client:
        await player.voice_client.disconnect()
        player.voice_client = None
        player.queue.clear()
        player.current_song = None
        player.is_playing = False
        player.is_paused = False
        player.save_queue_state()
        await ctx.send("Disconnected from voice channel!")
    else:
        await ctx.send("I'm not in a voice channel!")

@bot.command(name='join', help='Join the voice channel')
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send("You need to be in a voice channel to use this command!")
        return
    
    channel = ctx.author.voice.channel
    if player.voice_client and player.voice_client.is_connected():
        await player.voice_client.move_to(channel)
    else:
        player.voice_client = await channel.connect()
    
    await ctx.send(f"Joined {channel.name}!")        

#####################################################################################################################################
# Basic Commands
#####################################################################################################################################


@bot.command(name='play', help='Play a song (URL or search query)')
async def play(ctx, *, query):
    if not ctx.author.voice:
        await ctx.send("You need to be in a voice channel!")
        return
    
    if not player.voice_client:
        await join(ctx)
    
    await ctx.send(f"🔍 Searching for: {query}")
    
    result = await player.search_song(query)
    if not result:
        await ctx.send("❌ Could not find that song!")
        return
    
    song_url, title, duration, thumbnail = result
    song = Song(song_url, title, duration, thumbnail, str(ctx.author))
    
    await player.add_to_queue(song)
    
    if player.is_playing:
        await ctx.send(f"✅ Added to queue: **{title}** (Position: {len(player.queue)})")
    else:
        await ctx.send(f"▶️ Now playing: **{title}**")


@bot.command(name='pause', help='Pause the current song')
async def pause(ctx):
    if player.voice_client and player.voice_client.is_playing():
        player.voice_client.pause()
        player.is_paused = True
        player.save_queue_state()
        await ctx.send("⏸️ Paused")
    else:
        await ctx.send("Nothing is playing right now!")


@bot.command(name='resume', help='Resume the paused song')
async def resume(ctx):
    if player.voice_client and player.voice_client.is_paused():
        player.voice_client.resume()
        player.is_paused = False
        player.save_queue_state()
        await ctx.send("▶️ Resumed")
    else:
        await ctx.send("Nothing is paused!")


@bot.command(name='skip', help='Skip the current song')
async def skip(ctx):
    if player.voice_client and player.voice_client.is_playing():
        player.voice_client.stop()
        await ctx.send("⏭️ Skipped")
    else:
        await ctx.send("Nothing is playing right now!")


@bot.command(name='queue', help='Show the current queue')
async def show_queue(ctx):
    if not player.current_song and len(player.queue) == 0:
        await ctx.send("The queue is empty!")
        return
    
    embed = discord.Embed(title="🎵 Music Queue", color=discord.Color.blue())
    
    if player.current_song:
        status = "⏸️ Paused" if player.is_paused else "▶️ Playing"
        embed.add_field(
            name=f"{status} Now",
            value=f"**{player.current_song.title}**\nRequested by: {player.current_song.requester}",
            inline=False
        )
    
    if len(player.queue) > 0:
        queue_text = "\n".join([
            f"{i+1}. **{song.title}** - {song.requester}"
            for i, song in enumerate(list(player.queue)[:10])
        ])
        embed.add_field(name="Up Next", value=queue_text, inline=False)
        
        if len(player.queue) > 10:
            embed.add_field(name="", value=f"...and {len(player.queue) - 10} more", inline=False)
    
    await ctx.send(embed=embed)


@bot.command(name='clear', help='Clear the entire queue')
async def clear_queue(ctx):
    player.queue.clear()
    player.save_queue_state()
    await ctx.send("🗑️ Queue cleared!")


#####################################################################################################################################
# Playlist Commands 
#####################################################################################################################################

@bot.command(name='playlist_save', help='Save current queue as a playlist')
async def save_playlist(ctx, *, name):
    if not player.current_song and len(player.queue) == 0:
        await ctx.send("Nothing to save! The queue is empty.")
        return
    
    songs = []
    if player.current_song:
        songs.append(player.current_song)
    songs.extend(list(player.queue))
    
    player.playlists[name] = songs
    player.save_playlists()
    
    await ctx.send(f"💾 Saved playlist **{name}** with {len(songs)} songs!")


@bot.command(name='playlist_load', help='Load a saved playlist')
async def load_playlist(ctx, *, name):
    if name not in player.playlists:
        await ctx.send(f"❌ Playlist **{name}** not found!")
        return
    
    if not player.voice_client:
        await join(ctx)
    
    songs = player.playlists[name]
    for song in songs:
        await player.add_to_queue(song)
    
    await ctx.send(f"✅ Loaded playlist **{name}** ({len(songs)} songs)")


@bot.command(name='playlist_list', help='List all saved playlists')
async def list_playlists(ctx):
    if not player.playlists:
        await ctx.send("No playlists saved yet!")
        return
    
    embed = discord.Embed(title="📚 Saved Playlists", color=discord.Color.green())
    
    for name, songs in player.playlists.items():
        embed.add_field(
            name=name,
            value=f"{len(songs)} songs",
            inline=True
        )
    
    await ctx.send(embed=embed)


@bot.command(name='playlist_delete', help='Delete a saved playlist')
async def delete_playlist(ctx, *, name):
    if name not in player.playlists:
        await ctx.send(f"❌ Playlist **{name}** not found!")
        return
    
    del player.playlists[name]
    player.save_playlists()
    await ctx.send(f"🗑️ Deleted playlist **{name}**")


@bot.command(name='nowplaying', help='Show currently playing song')
async def now_playing(ctx):
    if not player.current_song:
        await ctx.send("Nothing is playing right now!")
        return
    
    embed = discord.Embed(title="Now Playing", color=discord.Color.purple())
    embed.add_field(name="Title", value=player.current_song.title, inline=False)
    embed.add_field(name="Requested by", value=player.current_song.requester, inline=True)
    
    if player.current_song.thumbnail:
        embed.set_thumbnail(url=player.current_song.thumbnail)
    
    status = "⏸️ Paused" if player.is_paused else "▶️ Playing"
    embed.set_footer(text=status)
    
    await ctx.send(embed=embed)

def main(): 
    if DISCORD_TOKEN is None:
        raise ValueError("DISCORD_BOT_TOKEN variable has not been set!")    
    bot.run(DISCORD_TOKEN)


if __name__ == '__main__':
    main()
