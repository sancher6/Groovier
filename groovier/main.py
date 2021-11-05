import os
import logging
import discord
from discord.ext.commands.converter import _get_from_guilds
from dotenv import load_dotenv
from discord.ext import commands
from pathlib import Path
from utils import get_song_title
from utils import concat_args
import urllib.request
import urllib.parse
import re
import pafy
import asyncio
from itertools import cycle
import youtube_dl

load_dotenv()
# TOKEN = os.getenv("DISCORD_TOKEN")
TOKEN = "OTA1OTE5MTcxNzEwMzIwNzUx.YYRE-Q.iBHVWoFlqegfz1kmPg88fgdU9M0" # this is Doug's token
THUMBS_UP = "\N{THUMBS UP SIGN}"
THUMBS_DOWN = "\N{THUMBS DOWN SIGN}"
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}
bot = commands.Bot(command_prefix="-")
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
song_queue=[]
current_song_title=""


@bot.event
async def on_ready():
    logging.info(f"{bot.user} has connected to Discord!")
    await bot.change_presence(activity=discord.Game(THUMBS_DOWN))


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    elif message.content == "test":
        await message.channel.send("I'm gay")
    await bot.process_commands(message)


@bot.command(help="`-ping` checks bot latency, with pong")
async def ping(ctx):
    await ctx.channel.send(f"pong {bot.latency ** 1000}ms")


@bot.command(help="`-join` connects bot to current voice channel")
async def join(ctx):
    author_channel = ctx.author.voice
    if author_channel is not None:
        await author_channel.channel.connect()


@bot.command(help="`-leave` disconnects bot from current voice channel")
async def leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice is not None:
        await voice.disconnect()

async def wait_queue(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    while len(song_queue) > 0:
        if not voice.is_playing():
            await ctx.send(f"Now playing {current_song_title}")
            voice.play(song_queue[0])
            del song_queue[0]
        await asyncio.sleep(1)


@bot.command(name="play", aliases=['p'], help="`-p *song name*` plays the specified song")
async def play_song(ctx, *args):
    if ctx.message.author.voice == None:
        await ctx.send("No Voice Channel", "You need to be in a voice channel to use this command")
        return

    author_connected = ctx.author.voice
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if author_connected:

        if (voice is None) or (voice.channel is not author_connected.channel):

            voice = await author_connected.channel.connect()
            logging.info(f"We have succesfully joined: {author_connected.channel}")

        if len(args) > 0: 
            search = concat_args(args)
            search = urllib.parse.quote(search)

            html = urllib.request.urlopen(
                f"https://www.youtube.com/results?search_query={search}"
            )
            video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
            if len(video_ids) == 0: 
                await ctx.send("No results found...")
                return
            song_url = f"https://www.youtube.com/watch?v={video_ids[0]}"

            current_song_title=get_song_title(video_ids[0])
            logging.info(f"Song Url: {song_url}\nSong Title: {current_song_title}")

            song = pafy.new(video_ids[0])

            audio = song.getbestaudio()

            source = discord.FFmpegPCMAudio(audio.url, **FFMPEG_OPTIONS)
            if not voice.is_playing(): 
                voice.play(source)
                await ctx.send(f"Now playing {current_song_title}")
            else:
                song_queue.append(source)
                await ctx.send(f"{current_song_title} has been added to queue")
                asyncio.run_coroutine_threadsafe(wait_queue(ctx), bot.loop)


@bot.command(name="stop", aliases=['s'], help="`-s` stops playing current song")
async def stop_playing(ctx, *args):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing(): 
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")


@bot.command(name="next", aliases=['n'], help="`-n *song name*` queues the specified song")
async def next_song(ctx):
    voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    voice_client.pause()
    del song_queue[0]
    if len(song_queue) > 0: 
        song = pafy.new(song_queue[0])

        audio = song.getbestaudio()

        source = discord.FFmpegPCMAudio(audio.url, **FFMPEG_OPTIONS)
        voice_client.play(source)
        del song_queue[0]  


@bot.command(name='pause', help='`-pause` pauses the current song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")
        

@bot.command(name='resume', help='`-resume` resumes the current song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play command")

bot.run(TOKEN)