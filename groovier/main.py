import os
import logging
import discord
from dotenv import load_dotenv
from discord.ext import commands
from pathlib import Path
from utils import concat_args
import urllib.request
import urllib.parse
import re
import pafy
import asyncio


# from keep_alive import keep_alive
import youtube_dl

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
# keep_alive()
THUMBS_UP = "\N{THUMBS UP SIGN}"
THUMBS_DOWN = "\N{THUMBS DOWN SIGN}"
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}
bot = commands.Bot(command_prefix="-")
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


@bot.event
async def on_ready():
    logging.info(f"{bot.user} has connected to Discord!")
    await bot.change_presence(activity=discord.Game(THUMBS_UP))


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    elif message.content == "test":
        await message.channel.send("Neeko Loves Cock <3")
    await bot.process_commands(message)


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


@bot.command(name="test", help="Test Sample MP3 like this: !test")
async def test_mp3(ctx, *args):
    file_name = Path(concat_args(args) + ".mp3")
    sounds_dir = Path("../test/sounds")
    test_file = sounds_dir / file_name

    if not Path(test_file).exists():
        logging.info("File Path Does not Exist")
        return

    author_connected = ctx.author.voice
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if author_connected:

        if (voice is None) or (voice.channel is not author_connected.channel):

            voice = await author_connected.channel.connect()
            logging.info(f"We have succesfully joined: {author_connected.channel}")

        voice.play(discord.FFmpegPCMAudio(test_file))
        # await voice.disconnect()

    else:
        await ctx.send("Please join a voice chat prior to using this command")


@bot.command(name="url", help="Test Sample URL to mp3 like this: !url")
async def test_url(ctx, *args):
    search = concat_args(args)
    search = urllib.parse.quote(search)
    logging.info(f"Search: {search}")
    html = urllib.request.urlopen(
        f"https://www.youtube.com/results?search_query={search}"
    )
    logging.info(f"the fucker is this: {html}")
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    video_url = "https://www.youtube.com/watch?v=" + video_ids[0]
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])


@bot.command(name="play", aliases=['p'], help="Play song like this: !p")
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
        search = concat_args(args)
        search = urllib.parse.quote(search)

        html = urllib.request.urlopen(
            f"https://www.youtube.com/results?search_query={search}"
        )
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        if len(video_ids) == 0: 
            await ctx.send("No results found...")
        song_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
        logging.info(f"Song Url: {song_url}")

        song = pafy.new(video_ids[0])

        audio = song.getbestaudio()

        source = discord.FFmpegPCMAudio(audio.url, **FFMPEG_OPTIONS)

        try: 
            voice.play(source)
        except discord.errors.ClientException: 
            # We are already playing Music in a channel
            if voice.channel is not author_connected.channel: 
                await ctx.send("Groovier is already Running in another Voice Channel")
                return
            # Queue the song 
            with open("queue.txt", "a") as f: 
                f.write(video_ids[0])
                f.write("\n")
            return


async def wait_queue(): 
    await bot.wait_until_ready()
    while not bot.is_closed: 
        with open("queue.txt", "w") as f: 
            lines = f.readlines() 
            if len(lines) > 0: 
                logging.info("Playing Next Song...")
                voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
                next_song = lines[0].rstrip()
                del lines[0]
                f.write(lines)
                song = pafy.new(next_song)

                audio = song.getbestaudio()

                source = discord.FFmpegPCMAudio(audio.url, **FFMPEG_OPTIONS)

                try: 
                    voice.play(source)
                except discord.errors.ClientException:
                    pass 
        await asyncio.sleep(1)
            


bot.loop.create_task(wait_queue())
bot.run(TOKEN)