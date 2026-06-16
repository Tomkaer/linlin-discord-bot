const { Client, GatewayIntentBits } = require('discord.js');
const { Player } = require('discord-player');

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildVoiceStates
    ]
});

const player = new Player(client);

client.on('ready', () => {
    console.log(`Logged in as ${client.user.tag}!`);
});

client.on('messageCreate', async message => {
    if (message.author.bot || !message.content.startsWith('!')) return;

    const args = message.content.slice(1).trim().split(/ +/);
    const command = args.shift().toLowerCase();

    // เช็คว่าผู้ใช้และบอทอยู่ในห้องเสียงเดียวกันหรือไม่
    const channel = message.member.voice.channel;
    if (!channel && command === 'play') {
        return message.reply('คุณต้องเข้าห้องเสียงก่อน!');
    }

    if (command === 'play') {
        const query = args.join(' ');
        if (!query) return message.reply('กรุณาระบุชื่อเพลงหรือ URL!');

        try {
            const { track } = await player.play(channel, query, {
                nodeOptions: {
                    metadata: message
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
