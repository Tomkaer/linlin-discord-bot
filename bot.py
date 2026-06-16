import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="lin!", intents=intents)

YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "default_search": "ytsearch"
}

FFMPEG_OPTIONS = {
    "options": "-vn"
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

@bot.event
async def on_ready():
    print(f"{bot.user} ออนไลน์แล้ว!")

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

@bot.command()
async def play(ctx, *, query):
    if not ctx.author.voice:
        await ctx.send("❌ กรุณาเข้าห้องเสียงก่อน")
        return

    channel = ctx.author.voice.channel

    if ctx.voice_client is None:
        await channel.connect()

    try:
        loop = asyncio.get_running_loop()

        data = await loop.run_in_executor(
            None,
            lambda: ytdl.extract_info(query, download=False)
        )

        if "entries" in data:
            data = data["entries"][0]

        url = data["url"]
        title = data["title"]

        source = discord.FFmpegPCMAudio(
            url,
            **FFMPEG_OPTIONS
        )

        vc = ctx.voice_client

        if vc.is_playing():
            vc.stop()

        vc.play(source)

        await ctx.send(f"🎵 กำลังเล่น: {title}")

    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("⏹️ หยุดเพลงแล้ว")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 ออกจากห้องเสียงแล้ว")

bot.run(TOKEN)
