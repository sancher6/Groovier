import os
import logging
import discord
from discord.ext.commands.converter import _get_from_guilds
from dotenv import load_dotenv
from discord.ext import commands
from pathlib import Path
from utils import get_videoid, concat_args, get_song_title
import urllib.parse
import pafy
import asyncio
from itertools import cycle
import youtube_dl

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
TOKEN = "OTA1OTE5MTcxNzEwMzIwNzUx.YYRE-Q.iBHVWoFlqegfz1kmPg88fgdU9M0"
THUMBS_UP = "\N{THUMBS UP SIGN}"
THUMBS_DOWN = "\N{THUMBS DOWN SIGN}"
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}
bot = commands.Bot(command_prefix="-")
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
song_queue=[] # holds pairs of video url followed by song title, as [url0, song_title0, url1, etc]

# async def update_queue(ctx):
#     voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
#     await ctx.channel.send(f"Song queue is: {song_queue}")
#     while len(song_queue) > 0:
#         if not voice.is_playing():
#             play_song(ctx, song_queue[0])
#             del song_queue[0]
#             del song_queue[0]
#         await asyncio.sleep(1)
async def update_queue(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    await ctx.channel.send(f"Song queue is: {song_queue}")
    while len(song_queue) > 0:
        if not voice.is_playing():
            await play_song(ctx, song_queue[0])
            del song_queue[0]
            del song_queue[0]
        await asyncio.sleep(1)


async def play_song(ctx, video_url):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    song = pafy.new(video_url)

    audio = song.getbestaudio()

    source = discord.FFmpegPCMAudio(audio.url, **FFMPEG_OPTIONS)
    if not voice.is_playing():
        voice.play(source)
        await ctx.send(f"Now playing {song_queue[1]}")
    else:
        asyncio.sleep(1)
        # asyncio.run_coroutine_threadsafe(update_queue(ctx), bot.loop)


@bot.event
async def on_ready():
    logging.info(f"{bot.user} has connected to Discord!")
    await bot.change_presence(activity=discord.Game(THUMBS_DOWN))

    voice = discord.utils.get(bot.voice_clients)
    if voice is not None:
        await voice.disconnect()


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
    # author_channel = ctx.author.voice
    # if author_channel is not None:
    #     await author_channel.channel.connect()
    author_channel = ctx.author.voice
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if author_channel is None:
        await ctx.send("Join a voice channel to use bot commands")
        return
    
    if voice is None:
        await author_channel.channel.connect()
        logging.info(f"We have succesfully joined: {author_channel.channel}")
        return

    if author_channel.channel is voice.channel:
        await ctx.send("Already connected to this voice channel")
        return

    if author_channel.channel is not voice.channel:
        await leave(ctx)
        await author_channel.channel.connect()
        logging.info(f"We have succesfully joined: {author_channel.channel}")
    

@bot.command(help="`-leave` disconnects bot from current voice channel")
async def leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice is not None:
        await voice.disconnect()


# @bot.command(name="add", aliases=['a'], help="`-a *song name*` adds the specified song to the top of queue")
# async def add_song(ctx, *args):


@bot.command(name="play", aliases=['p'], help="`-p *song name*` plays the specified song")
async def add_song(ctx, *args):
    if ctx.message.author.voice == None:
        await ctx.send("No Voice Channel", "You need to be in a voice channel to use this command")
        return

    join(ctx)

    if len(args) > 0:

        search_phrase = concat_args(args)

        video_id = get_videoid(search_phrase)

        if video_id == "":
            await ctx.send(f"No results found for \"{search_phrase}\"")
            return

        video_url=f"https://www.youtube.com/watch?v={video_id}"
        song_queue.append(video_url)
        song_queue.append(get_song_title(video_id))
        logging.info(f"New song's video url: {song_queue[0]}\nVideo Title: {song_queue[1]}")

        ## the stuff below this point is what actually plays the audio, what's above it gets the info and queues the song

        # this is the part I'm talking about
        # await update_queue(ctx)
        asyncio.run_coroutine_threadsafe(update_queue(ctx), bot.loop)


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
        await ctx.send("The bot was not paused.")


bot.run(TOKEN)