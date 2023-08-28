from math import ceil, floor
import os
import logging
import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext.commands.errors import (
    MissingPermissions,
    CommandNotFound,
    ExpectedClosingQuoteError,
)
from utils import concat_args
import urllib.request
import urllib.parse
import re
import pafy
import asyncio
import random

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
THUMBS_UP = "\N{THUMBS UP SIGN}"
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="-", intents=intents)
logger = logging.getLogger(__name__)
song_queue=[]

#####################################################################################################################################
# Functions
#####################################################################################################################################
async def wait_queue(ctx): 
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    while True: 
        global song_queue
        if len(song_queue) > 0: 
            if not voice.is_playing(): 
                while True: 
                    try: 
                        song = pafy.new(song_queue[0]['url'], basic=False)
                        await asyncio.sleep(1)
                    except KeyError as e: 
                        logger.info(f"Pafy KeyError: {e}")
                        del song_queue[0]
                    finally: 
                        break
                audio = song.getbestaudio()
                source = discord.FFmpegPCMAudio(audio.url, **FFMPEG_OPTIONS)
                logger.info(f"Now Playing {song_queue[0]['title']}")
                await ctx.send(f"Now Playing {song_queue[0]['title']}")
                del song_queue[0]
                voice.play(source)
            await asyncio.sleep(1)
        else: 
            break
    return
        


#####################################################################################################################################
# Events
#####################################################################################################################################
@bot.event
async def on_ready():
    logger.info("<" + bot.user.name + " Online>")
    await bot.change_presence(activity=discord.Game(name="with your mind! Use -help"))


@bot.event
async def on_error(event, *args, **kwargs):
    for arg in args:
        if isinstance(arg, Exception):
            raise arg


@bot.event
async def on_command_error(ctx, error):
    if ctx.cog is not None:
        # Errors coming from cogs
        logger.info("Received cog exception: {0}".format(error))
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


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    elif message.content == "test":
        await message.channel.send("Neeko Loves Cock <3")
    await bot.process_commands(message)

#####################################################################################################################################
# Commands
#####################################################################################################################################
@bot.command(help="Sends Pong with Bot Latency like this: !ping")
async def ping(ctx):
    await ctx.channel.send(f"PONG {bot.latency ** 1000}ms")


@bot.command()
async def join(ctx):
    author_channel = ctx.author.voice
    if author_channel is not None:
        await author_channel.channel.connect()


@bot.command()
async def leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice is not None:
        await voice.disconnect()


@bot.command(name="clear", aliases=['c'], help="View Queue like this: -q")
async def clear(ctx):
    song_queue.clear()
    await ctx.send("Cleared Queue")


@bot.command(name="remove", aliases=['r'], help="Remove from Queue like this: -r [location]")
async def remove(ctx, *args):
    if len(args) == 1:
        try: 
            loc_int = int(args[0])
            logger.info(f"Removing Queue Location: {loc_int}")
        except ValueError: 
            logger.info("Invalid Queue Location")
            await ctx.send("Invalid Queue Location")
            return
        finally: 
            await ctx.send(f"Removed: {song_queue[loc_int-1]['title']}")
            del song_queue[loc_int-1]
            return
    else: 
        logger.info("Invalid Queue Location")   
        await ctx.send("Invalid Queue Location")
        return


@bot.command(name="queue", aliases=['q'], help="View Queue like this: -q")
async def view_queue(ctx):
    if len(song_queue) > 0: 
        song_list = "```ini\n"
        for i, song in enumerate(song_queue): 
            queue_loc = str("[" + str(i+1) + "]")
            song_title = song['title']
            song_duration = str("\t[" + song['duration'] + "]")
            raw_list = ("{0:<5}{1:<5}{2:<5}\n".format(queue_loc, song_title, song_duration))
            song_list += raw_list
        song_list += "```"
        await ctx.send(song_list)
    else: 
        await ctx.send("No Songs in Queue")


@bot.command(name="shuffle", aliases=['s'], help="Shuffle like this: -s")
async def shuffle_queue(ctx):
    global song_queue
    if len(song_queue) > 0: 
        random.shuffle(song_queue)
        await ctx.send("Queue Shuffled")
    else: 
        await ctx.send("No Songs in Queue")


@bot.command(name="play", aliases=['p'], help="Play song like this: !p")
async def play_song(ctx, *args):
    global song_queue
    if ctx.message.author.voice == None:
        await ctx.send("No Voice Channel", "You need to be in a voice channel to use this command")
        return
        
    author_connected = ctx.message.author.voice
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if author_connected:

        if (voice is None) or (voice.channel is not author_connected.channel):
            logger.info(f"We are connected to: {author_connected.channel}")
            voice = await author_connected.channel.connect()
            logger.info(f"We have succesfully joined: {author_connected.channel}")
        # voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        # if voice and voice.is_connected():
        #     logger.info("Switching voice channels")
        #     await voice.move_to(ctx.author.voice.channel)
        # else: 
        #     logger.info("We weren't connected to anything")
        #     voice = await author_connected.connect()
        if len(args) > 0: 
            search = concat_args(args)
            search = urllib.parse.quote(search)
            try:
                html = urllib.request.urlopen(
                    f"https://www.youtube.com/results?search_query={search}"
                )
            except Exception as e: 
                logger.info(f"Error {e}")
            video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
            if len(video_ids) == 0: 
                await ctx.send("No results found...")
                return
            song_url = f"https://www.youtube.com/watch?v={video_ids[1]}"
            logger.info(f"Song Url: {song_url}")
            try: 
                song = pafy.new(song_url, basic=False)
                await asyncio.sleep(1)
            except KeyError as e: 
                logger.info(f"Pafy KeyError: {e}")
                return
            except Exception as e: 
                logger.info(f"Exception {e}")
                return
            song_queue.append({"title": song.title, "url": song_url, "duration": song.duration})
            if not voice.is_playing() and len(song_queue) == 0: 
                logger.info(f"Now Playing {song.title}")
                try: 
                    audio = song.getbestaudio()
                # except KeyError as e: 
                #     logger.info(f"Pafy KeyError: {e}")
                #     return
                except Exception as e: 
                    logger.info(f"Exception from audio{e}")
                    return
                try: 
                    source = discord.FFmpegPCMAudio(audio.url, **FFMPEG_OPTIONS)
                except Exception as e: 
                    logger.info(f"Exception from Source{e}")
                    return
                await ctx.send(f"Now Playing: {song.title}")
                del song_queue[0]
                voice.play(source)
                return
            else: 
                await ctx.send(f"Song Queued: {song.title}")
                if len(song_queue) == 1: 
                    asyncio.run_coroutine_threadsafe(wait_queue(ctx), bot.loop)
                return
        return


@bot.command(name="stop", help="Stop song like this: !s")
async def stop_playing(ctx, *args):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing(): 
        voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")


@bot.command(name="next", aliases=['n'], help="Play next song like this: -n")
async def next_song(ctx):
    global song_queue
    voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    if voice_client.is_playing(): 
        voice_client.pause()
        if len(song_queue) >= 1: 
            asyncio.run_coroutine_threadsafe(wait_queue(ctx), bot.loop)
        return
    return 

@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")
        

@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play command")


def launch(): 
    if TOKEN is None:
        raise ValueError("DISCORD_BOT_TOKEN variable has not been set!")
    bot.run(TOKEN)