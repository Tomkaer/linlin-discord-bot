import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import google.generativeai as genai
import yt_dlp
import asyncio

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(
    command_prefix="lin!",
    intents=intents,
    help_command=None
)

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
    await bot.change_presence(
        activity=discord.Game("lin!help")
    )

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    should_reply = False

    if bot.user in message.mentions:
        should_reply = True

    if message.content.lower().startswith("หลิน"):
        should_reply = True

    if should_reply:
        try:
            prompt = f"""
คุณคือ LinLin ผู้ช่วย Discord ภาษาไทย
ตอบอย่างสุภาพ เป็นกันเอง และกระชับ

ข้อความจากผู้ใช้:
{message.content}
"""

            response = model.generate_content(prompt)

            await message.reply(response.text[:1900])

        except Exception as e:
            await message.reply("ขออภัย ตอนนี้ AI ตอบไม่ได้ชั่วคราว")

    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 {round(bot.latency*1000)} ms")

@bot.command()
async def play(ctx, *, query):
    if not ctx.author.voice:
        await ctx.send("❌ เข้าห้องคอลก่อนครับ")
        return

    channel = ctx.author.voice.channel

    if not ctx.voice_client:
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

        await ctx.send(f"🎵 กำลังเล่น: **{title}**")

    except Exception as e:
        await ctx.send("❌ เปิดเพลงไม่สำเร็จ")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("⏹️ หยุดเพลงแล้ว")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 ออกจากห้องคอลแล้ว")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(
        f"🗑️ ลบ {amount} ข้อความแล้ว"
    )
    await asyncio.sleep(3)
    await msg.delete()

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="LinLin Commands",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="🎵 เพลง",
        value="""
lin!play <เพลง>
lin!stop
lin!leave
""",
        inline=False
    )

    embed.add_field(
        name="🛡️ จัดการ",
        value="""
lin!clear <จำนวน>
""",
        inline=False
    )

    embed.add_field(
        name="🤖 AI",
        value="""
แท็กบอท
หรือพิมพ์ขึ้นต้นด้วย 'หลิน'
""",
        inline=False
    )

    await ctx.send(embed=embed)

bot.run(DISCORD_TOKEN)
