import os
import logging
import discord
from dotenv import load_dotenv
from discord.ext import commands
from pathlib import Path
from utils import concat_args, concat_filename
import urllib.request
import urllib.parse
import re

# from keep_alive import keep_alive
import youtube_dl

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
# keep_alive()
THUMBS_UP = "\N{THUMBS UP SIGN}"
THUMBS_DOWN = "\N{THUMBS DOWN SIGN}"
bot = commands.Bot(command_prefix="!")
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


@bot.event
async def on_ready():
    logging.info(f"{bot.user} has connected to Discord!")


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


bot.run(TOKEN)