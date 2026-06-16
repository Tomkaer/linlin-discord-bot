import discord
from discord.ext import commands
import yt_dlp
import asyncio

# ตั้งค่า Intents สำหรับเข้าถึงระบบเสียงและข้อความ
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ตั้งค่า yt-dlp สำหรับดึงเสียงจาก YouTube / URL อื่นๆ
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        
        if 'entries' in data:
            data = data['entries'][0]
            
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)

# เหตุการณ์เมื่อบอทออนไลน์
@bot.event
async def on_ready():
    print(f'บอทเพลงเปิดใช้งานแล้ว: {bot.user.name}')

# คำสั่งสั่งให้บอทเข้าห้อง และเล่นเพลง
@bot.command(name='play', help='สั่งให้บอทเล่นเพลง เช่น !play ชื่อเพลง หรือ ลิงก์')
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        await ctx.send("คุณต้องเข้าห้องเสียง (Voice Channel) ก่อนสั่งเปิดเพลงจ้า!")
        return

    voice_channel = ctx.author.voice.channel
    
    if ctx.voice_client is None:
        await voice_channel.connect()
    else:
        await ctx.voice_client.move_to(voice_channel)

    async with ctx.typing():
        try:
            player = await YTDLSource.from_url(search, loop=bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
            await ctx.send(f'🎵 กำลังเปิดเพลง: **{player.title}**')
        except Exception as e:
            await ctx.send(f'เกิดข้อผิดพลาดในการดึงข้อมูลเพลง: {e}')

# คำสั่งหยุดเพลงชั่วคราว
@bot.command(name='pause', help='หยุดเพลงชั่วคราว')
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ หยุดเพลงชั่วคราวแล้ว")

# คำสั่งเล่นเพลงต่อ
@bot.command(name='resume', help='เล่นเพลงต่อจากที่หยุดไว้')
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ เล่นเพลงต่อแล้ว")

# คำสั่งหยุดเล่นและล้างคิว
@bot.command(name='stop', help='หยุดเล่นเพลง')
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("⏹️ หยุดเล่นเพลงแล้ว")

# คำสั่งเตะบอทออกจากห้องเสียง
@bot.command(name='leave', help='สั่งให้บอทออกจากห้อง')
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 บอทออกจากห้องเสียงแล้วจ้า")
    else:
        await ctx.send("บอทไม่ได้อยู่ในห้องเสียงนะ")

# ใส่ TOKEN บอทของคุณที่นี่
bot.run('ใส่_TOKEN_บอทตรงนี้')
                }
            });
            message.reply(`กำลังเล่น: **${track.title}**`);
        } catch (e) {
            message.reply('ไม่พบเพลงหรือเกิดข้อผิดพลาดในการเล่น');
        }
    }

    else if (command === 'skip') {
        const queue = player.nodes.get(message.guildId);
        if (!queue || !queue.isPlaying()) return message.reply('ไม่มีเพลงกำลังเล่นอยู่');
        queue.node.skip();
        message.reply('ข้ามเพลงเรียบร้อย!');
    }

    else if (command === 'stop') {
        const queue = player.nodes.get(message.guildId);
        if (!queue) return message.reply('ไม่มีเพลงกำลังเล่นอยู่');
        queue.delete();
        message.reply('หยุดเพลงและออกจากห้องแล้ว!');
    }
});

// ใส่ Bot Token ของคุณที่นี่
client.login('YOUR_DISCORD_BOT_TOKEN');
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
