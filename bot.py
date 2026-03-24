print("BOT BAŞLATILIYOR...")

import discord
from discord.ext import commands
from discord import app_commands
import os
import json
from dotenv import load_dotenv
import asyncio
from datetime import datetime, timedelta
import random
import urllib.request
import urllib.parse
import re
import subprocess
from groq import Groq

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

print(f"Token: {TOKEN[:20] if TOKEN else 'YOK'}...")
print(f"Groq: {GROQ_API_KEY[:20] if GROQ_API_KEY else 'YOK'}...")

if not TOKEN:
    print("HATA: Token yok!")
    exit()

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
music_queues = {}

# =====================================================
# 🛡️ GÜVENLİ YANIT FONKSİYONU
# =====================================================

async def guvenli_cevap(interaction: discord.Interaction, icerik=None, embed=None, ephemeral=False):
    """Tüm slash komutlar için güvenli yanıt - ASLA HATA VERMEZ"""
    try:
        if not interaction.response.is_done():
            if embed:
                await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
            elif icerik:
                await interaction.response.send_message(icerik, ephemeral=ephemeral)
        else:
            if embed:
                await interaction.followup.send(embed=embed, ephemeral=ephemeral)
            elif icerik:
                await interaction.followup.send(icerik, ephemeral=ephemeral)
        return True
    except:
        return False

# =====================================================
# 📁 VERİ FONKSİYONLARI
# =====================================================

def veri_olustur():
    os.makedirs('data', exist_ok=True)
    for d in ['economy.json', 'levels.json', 'warnings.json']:
        if not os.path.exists(f'data/{d}'):
            with open(f'data/{d}', 'w') as f:
                json.dump({}, f)

veri_olustur()

def json_oku(d):
    try:
        with open(f'data/{d}', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def json_yaz(d, v):
    with open(f'data/{d}', 'w', encoding='utf-8') as f:
        json.dump(v, f, indent=2, ensure_ascii=False)

# =====================================================
# 🚀 BOT HAZIR
# =====================================================

@bot.event
async def on_ready():
    print("="*40)
    print(f"BOT AKTİF: {bot.user.name}")
    print(f"Sunucu: {len(bot.guilds)}")
    print("="*40)
    await bot.change_presence(activity=discord.Game(name="/yardım"))
    print("📁 Slash komutlar yükleniyor...")
    try:
        for guild in bot.guilds:
            bot.tree.copy_global_to(guild=guild)
            await bot.tree.sync(guild=guild)
            print(f"✅ {guild.name} sync edildi!")
    except Exception as e:
        print(f"❌ Slash hata: {e}")
    print("✅ Bot hazır!")

@bot.event
async def on_member_join(member):
    kanal = member.guild.system_channel
    if kanal:
        await kanal.send(f"🎉 Hoş geldin {member.mention}!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)

# =====================================================
# 🛡️ MODERASYON - ! KOMUTLARI
# =====================================================

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Sebep yok"):
    await member.kick(reason=reason)
    embed = discord.Embed(title="👢 Kick", description=f"{member.mention} atıldı!", color=discord.Color.orange())
    embed.add_field(name="Sebep", value=reason)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Sebep yok"):
    await member.ban(reason=reason)
    embed = discord.Embed(title="🔨 Ban", description=f"{member.mention} yasaklandı!", color=discord.Color.red())
    embed.add_field(name="Sebep", value=reason)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def sil(ctx, miktar: int):
    await ctx.channel.purge(limit=miktar + 1)
    msg = await ctx.send(f"🗑️ {miktar} mesaj silindi!")
    await asyncio.sleep(2)
    await msg.delete()

@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, dakika: int):
    await member.timeout(timedelta(minutes=dakika))
    await ctx.send(f"🔇 {member.mention} {dakika}dk susturuldu!")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def uyar(ctx, member: discord.Member, *, sebep):
    warnings = json_oku('warnings.json')
    uid = str(member.id)
    if uid not in warnings:
        warnings[uid] = []
    warnings[uid].append({'sebep': sebep, 'tarih': datetime.now().strftime("%d/%m/%Y")})
    json_yaz('warnings.json', warnings)
    await ctx.send(f"⚠️ {member.mention} uyarıldı! Toplam: {len(warnings[uid])}")

# =====================================================
# 🛡️ MODERASYON - / KOMUTLARI
# =====================================================

@bot.tree.command(name="kick", description="Kullanıcıyı sunucudan at")
@app_commands.describe(member="Atılacak kullanıcı", reason="Sebep")
async def slash_kick(interaction: discord.Interaction, member: discord.Member, reason: str = "Sebep yok"):
    if not interaction.user.guild_permissions.kick_members:
        await guvenli_cevap(interaction, "❌ Yetkin yok!", ephemeral=True)
        return
    await member.kick(reason=reason)
    embed = discord.Embed(title="👢 Kick", description=f"{member.mention} atıldı!", color=discord.Color.orange())
    embed.add_field(name="Sebep", value=reason)
    await guvenli_cevap(interaction, embed=embed)

@bot.tree.command(name="ban", description="Kullanıcıyı yasakla")
@app_commands.describe(member="Yasaklanacak kullanıcı", reason="Sebep")
async def slash_ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Sebep yok"):
    if not interaction.user.guild_permissions.ban_members:
        await guvenli_cevap(interaction, "❌ Yetkin yok!", ephemeral=True)
        return
    await member.ban(reason=reason)
    embed = discord.Embed(title="🔨 Ban", description=f"{member.mention} yasaklandı!", color=discord.Color.red())
    embed.add_field(name="Sebep", value=reason)
    await guvenli_cevap(interaction, embed=embed)

@bot.tree.command(name="sil", description="Mesaj sil")
@app_commands.describe(miktar="Silinecek mesaj sayısı")
async def slash_sil(interaction: discord.Interaction, miktar: int):
    if not interaction.user.guild_permissions.manage_messages:
        await guvenli_cevap(interaction, "❌ Yetkin yok!", ephemeral=True)
        return
    await guvenli_cevap(interaction, f"🗑️ {miktar} mesaj siliniyor...", ephemeral=True)
    await interaction.channel.purge(limit=miktar)

@bot.tree.command(name="timeout", description="Kullanıcıyı sustur")
@app_commands.describe(member="Susturulacak kullanıcı", dakika="Süre (dakika)")
async def slash_timeout(interaction: discord.Interaction, member: discord.Member, dakika: int):
    if not interaction.user.guild_permissions.moderate_members:
        await guvenli_cevap(interaction, "❌ Yetkin yok!", ephemeral=True)
        return
    await member.timeout(timedelta(minutes=dakika))
    await guvenli_cevap(interaction, f"🔇 {member.mention} {dakika}dk susturuldu!")

@bot.tree.command(name="uyar", description="Kullanıcıyı uyar")
@app_commands.describe(member="Uyarılacak kullanıcı", sebep="Uyarı sebebi")
async def slash_uyar(interaction: discord.Interaction, member: discord.Member, sebep: str):
    if not interaction.user.guild_permissions.moderate_members:
        await guvenli_cevap(interaction, "❌ Yetkin yok!", ephemeral=True)
        return
    warnings = json_oku('warnings.json')
    uid = str(member.id)
    if uid not in warnings:
        warnings[uid] = []
    warnings[uid].append({'sebep': sebep, 'tarih': datetime.now().strftime("%d/%m/%Y")})
    json_yaz('warnings.json', warnings)
    await guvenli_cevap(interaction, f"⚠️ {member.mention} uyarıldı! Toplam: {len(warnings[uid])}")

# =====================================================
# 🎵 MÜZİK - ! KOMUTLARI
# =====================================================

def get_queue(guild_id):
    if guild_id not in music_queues:
        music_queues[guild_id] = []
    return music_queues[guild_id]

def youtube_search(query):
    try:
        if 'youtube.com' in query or 'youtu.be' in query:
            return query
        search_query = urllib.parse.quote(query)
        html = urllib.request.urlopen(f'https://www.youtube.com/results?search_query={search_query}', timeout=10)
        video_ids = re.findall(r'watch\?v=(\S{11})', html.read().decode())
        if video_ids:
            return f'https://www.youtube.com/watch?v={video_ids[0]}'
    except:
        pass
    return None

def get_audio(url):
    try:
        result = subprocess.run(['yt-dlp', '--no-playlist', '-f', 'bestaudio', '-g', url], capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            return result.stdout.strip().split('\n')[0]
    except:
        pass
    return None

def get_title(url):
    try:
        result = subprocess.run(['yt-dlp', '--no-playlist', '--get-title', url], capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return "Bilinmeyen Şarkı"

@bot.command(aliases=['p', 'çal'])
async def play(ctx, *, query):
    if not ctx.author.voice:
        await ctx.send("❌ Önce ses kanalına katıl!")
        return
    channel = ctx.author.voice.channel
    if not ctx.voice_client:
        try:
            await channel.connect()
            await ctx.send(f"🔊 **{channel.name}** kanalına katıldım!")
        except Exception as e:
            await ctx.send(f"❌ Katılamadım: {e}")
            return
    msg = await ctx.send("🔍 Aranıyor...")
    url = youtube_search(query)
    if not url:
        await msg.edit(content="❌ Şarkı bulunamadı!")
        return
    title = get_title(url)
    audio_url = get_audio(url)
    if not audio_url:
        await msg.edit(content="❌ Şarkı yüklenemedi!")
        return
    vc = ctx.voice_client
    if vc.is_playing():
        queue = get_queue(ctx.guild.id)
        queue.append({'url': audio_url, 'title': title})
        await msg.edit(content=f"➕ Kuyruğa eklendi: **{title}**")
        return
    await msg.delete()
    FFMPEG_OPT = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    def after_play(error):
        queue = get_queue(ctx.guild.id)
        if len(queue) > 0:
            next_song = queue.pop(0)
            async def play_next():
                source = discord.FFmpegPCMAudio(next_song['url'], **FFMPEG_OPT)
                vc.play(source, after=after_play)
                await ctx.send(f"🎵 Çalıyor: **{next_song['title']}**")
            asyncio.run_coroutine_threadsafe(play_next(), bot.loop)
    source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPT)
    vc.play(source, after=after_play)
    embed = discord.Embed(title="🎵 Şimdi Çalıyor", description=title, color=discord.Color.green())
    await ctx.send(embed=embed)

@bot.command(aliases=['duraklat'])
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ Duraklatıldı!")
    else:
        await ctx.send("❌ Müzik çalmıyor!")

@bot.command(aliases=['resume'])
async def devam(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ Devam!")
    else:
        await ctx.send("❌ Duraklatılmamış!")

@bot.command(aliases=['atla', 's'])
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ Atlandı!")
    else:
        await ctx.send("❌ Müzik çalmıyor!")

@bot.command(aliases=['kapat'])
async def stop(ctx):
    if ctx.voice_client:
        get_queue(ctx.guild.id).clear()
        ctx.voice_client.stop()
        await ctx.send("⏹️ Durduruldu!")

@bot.command(aliases=['çık', 'dc'])
async def leave(ctx):
    if ctx.voice_client:
        get_queue(ctx.guild.id).clear()
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Ayrıldım!")
    else:
        await ctx.send("❌ Kanalda değilim!")

@bot.command(aliases=['q', 'kuyruk'])
async def queue(ctx):
    q = get_queue(ctx.guild.id)
    if len(q) == 0:
        await ctx.send("📋 Kuyruk boş!")
    else:
        text = "\n".join([f"{i+1}. {s['title']}" for i, s in enumerate(q[:10])])
        embed = discord.Embed(title="📋 Kuyruk", description=text, color=discord.Color.blue())
        await ctx.send(embed=embed)

@bot.command(aliases=['katıl'])
async def join(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
        await ctx.send("🔊 Katıldım!")
    else:
        await ctx.send("❌ Ses kanalında değilsin!")

# =====================================================
# 🎵 MÜZİK - / KOMUTLARI
# =====================================================

@bot.tree.command(name="play", description="Müzik çal")
@app_commands.describe(şarkı="Şarkı adı veya YouTube linki")
async def slash_play(interaction: discord.Interaction, şarkı: str):
    await guvenli_cevap(interaction, f"🔍 Aranıyor: **{şarkı}**")
    if not interaction.user.voice:
        await interaction.edit_original_response(content="❌ Önce ses kanalına katıl!")
        return
    channel = interaction.user.voice.channel
    if not interaction.guild.voice_client:
        try:
            await channel.connect()
        except Exception as e:
            await interaction.edit_original_response(content=f"❌ Katılamadım: {e}")
            return
    url = youtube_search(şarkı)
    if not url:
        await interaction.edit_original_response(content="❌ Şarkı bulunamadı!")
        return
    title = get_title(url)
    audio_url = get_audio(url)
    if not audio_url:
        await interaction.edit_original_response(content="❌ Şarkı yüklenemedi!")
        return
    vc = interaction.guild.voice_client
    if vc.is_playing():
        queue = get_queue(interaction.guild.id)
        queue.append({'url': audio_url, 'title': title})
        await interaction.edit_original_response(content=f"➕ Kuyruğa eklendi: **{title}**")
        return
    FFMPEG_OPT = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    def after_play(error):
        queue = get_queue(interaction.guild.id)
        if len(queue) > 0:
            next_song = queue.pop(0)
            async def play_next():
                source = discord.FFmpegPCMAudio(next_song['url'], **FFMPEG_OPT)
                vc.play(source, after=after_play)
            asyncio.run_coroutine_threadsafe(play_next(), bot.loop)
    source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPT)
    vc.play(source, after=after_play)
    embed = discord.Embed(title="🎵 Şimdi Çalıyor", description=title, color=discord.Color.green())
    await interaction.edit_original_response(content=None, embed=embed)

@bot.tree.command(name="pause", description="Müziği duraklat")
async def slash_pause(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.pause()
        await guvenli_cevap(interaction, "⏸️ Duraklatıldı!")
    else:
        await guvenli_cevap(interaction, "❌ Müzik çalmıyor!", ephemeral=True)

@bot.tree.command(name="devam", description="Müziği devam ettir")
async def slash_devam(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_paused():
        interaction.guild.voice_client.resume()
        await guvenli_cevap(interaction, "▶️ Devam!")
    else:
        await guvenli_cevap(interaction, "❌ Duraklatılmamış!", ephemeral=True)

@bot.tree.command(name="skip", description="Şarkıyı atla")
async def slash_skip(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.stop()
        await guvenli_cevap(interaction, "⏭️ Atlandı!")
    else:
        await guvenli_cevap(interaction, "❌ Müzik çalmıyor!", ephemeral=True)

@bot.tree.command(name="stop", description="Müziği durdur")
async def slash_stop(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        get_queue(interaction.guild.id).clear()
        interaction.guild.voice_client.stop()
        await guvenli_cevap(interaction, "⏹️ Durduruldu!")
    else:
        await guvenli_cevap(interaction, "❌ Müzik çalmıyor!", ephemeral=True)

@bot.tree.command(name="leave", description="Ses kanalından ayrıl")
async def slash_leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        get_queue(interaction.guild.id).clear()
        await interaction.guild.voice_client.disconnect()
        await guvenli_cevap(interaction, "👋 Ayrıldım!")
    else:
        await guvenli_cevap(interaction, "❌ Kanalda değilim!", ephemeral=True)

@bot.tree.command(name="queue", description="Müzik kuyruğunu göster")
async def slash_queue(interaction: discord.Interaction):
    q = get_queue(interaction.guild.id)
    if len(q) == 0:
        await guvenli_cevap(interaction, "📋 Kuyruk boş!")
    else:
        text = "\n".join([f"{i+1}. {s['title']}" for i, s in enumerate(q[:10])])
        embed = discord.Embed(title="📋 Kuyruk", description=text, color=discord.Color.blue())
        await guvenli_cevap(interaction, embed=embed)

# =====================================================
# 🎮 OYUNLAR - ! KOMUTLARI
# =====================================================

@bot.command(aliases=['av'])
async def hunt(ctx):
    hayvanlar = {
        '🐀': (10, 30, "Fare"),
        '🐇': (20, 50, "Tavşan"),
        '🦊': (40, 80, "Tilki"),
        '🐺': (60, 120, "Kurt"),
        '🐻': (100, 200, "Ayı"),
        '🦁': (150, 300, "Aslan"),
        '🐉': (300, 600, "Ejderha")
    }
    weights = [25, 20, 15, 12, 10, 5, 3]
    emoji, (min_p, max_p, isim) = random.choices(list(hayvanlar.items()), weights=weights)[0]
    para = random.randint(min_p, max_p)
    economy = json_oku('economy.json')
    uid = str(ctx.author.id)
    if uid not in economy:
        economy[uid] = {'para': 1000, 'banka': 0}
    economy[uid]['para'] += para
    json_yaz('economy.json', economy)
    embed = discord.Embed(title="🏹 Avlanma", color=discord.Color.green())
    embed.description = f"{ctx.author.mention} bir **{isim}** {emoji} avladı!"
    embed.add_field(name="💰 Kazanç", value=f"+{para}💰")
    embed.add_field(name="🎒 Bakiye", value=f"{economy[uid]['para']}💰")
    await ctx.send(embed=embed)

@bot.command()
async def slot(ctx, miktar: int = 10):
    emojiler = ['🍒', '🍋', '🍊', '🍇', '💎', '7️⃣']
    economy = json_oku('economy.json')
    uid = str(ctx.author.id)
    if uid not in economy:
        economy[uid] = {'para': 1000, 'banka': 0}
    if miktar < 10:
        await ctx.send("❌ Minimum 10💰!")
        return
    if economy[uid]['para'] < miktar:
        await ctx.send("❌ Yeterli paran yok!")
        return
    economy[uid]['para'] -= miktar
    sans = random.randint(1, 100)
    if sans <= 2:
        secilen = random.choice(emojiler)
        sonuc = [secilen, secilen, secilen]
        if secilen == '💎':
            odul = miktar * 50
        elif secilen == '7️⃣':
            odul = miktar * 30
        else:
            odul = miktar * 10
        economy[uid]['para'] += odul
        mesaj = f"🎉 **JACKPOT!** +{odul}💰"
        renk = discord.Color.gold()
    elif sans <= 15:
        secilen = random.choice(emojiler)
        diger = random.choice([e for e in emojiler if e != secilen])
        sonuc = [secilen, secilen, diger]
        random.shuffle(sonuc)
        odul = int(miktar * 1.5)
        economy[uid]['para'] += odul
        mesaj = f"✨ **İkili!** +{odul}💰"
        renk = discord.Color.green()
    else:
        sonuc = random.sample(emojiler, 3)
        mesaj = f"😢 Kaybettin! -{miktar}💰"
        renk = discord.Color.red()
    json_yaz('economy.json', economy)
    embed = discord.Embed(title="🎰 SLOT", color=renk)
    embed.description = f"**[ {' | '.join(sonuc)} ]**\n\n{mesaj}"
    embed.add_field(name="💰 Bakiye", value=f"{economy[uid]['para']}💰")
    await ctx.send(embed=embed)

@bot.command(aliases=['cf', 'yazıtura'])
async def coinflip(ctx, miktar: int):
    if miktar < 10:
        await ctx.send("❌ Minimum 10💰!")
        return
    economy = json_oku('economy.json')
    uid = str(ctx.author.id)
    if uid not in economy:
        economy[uid] = {'para': 1000, 'banka': 0}
    if economy[uid]['para'] < miktar:
        await ctx.send("❌ Yeterli paran yok!")
        return
    economy[uid]['para'] -= miktar
    if random.randint(1, 100) <= 45:
        odul = miktar * 2
        economy[uid]['para'] += odul
        sonuc = "🪙 YAZI"
        mesaj = f"🎉 Kazandın! +{odul}💰"
        renk = discord.Color.green()
    else:
        sonuc = "🪙 TURA"
        mesaj = f"😢 Kaybettin! -{miktar}💰"
        renk = discord.Color.red()
    json_yaz('economy.json', economy)
    embed = discord.Embed(title="🪙 Coinflip", color=renk)
    embed.description = f"Sonuç: **{sonuc}**\n{mesaj}"
    embed.add_field(name="💰 Bakiye", value=f"{economy[uid]['para']}💰")
    await ctx.send(embed=embed)

@bot.command(aliases=['savaş'])
async def battle(ctx, member: discord.Member):
    if member.bot or member == ctx.author:
        await ctx.send("❌ Geçersiz rakip!")
        return
    can1, can2 = 100, 100
    msg = await ctx.send(f"⚔️ **SAVAŞ!**\n{ctx.author.name}: ❤️{can1}\n{member.name}: ❤️{can2}")
    while can1 > 0 and can2 > 0:
        await asyncio.sleep(1)
        h1 = random.randint(15, 35)
        h2 = random.randint(15, 35)
        can2 -= h1
        can1 -= h2
        await msg.edit(content=f"⚔️ **SAVAŞ!**\n{ctx.author.name}: ❤️{max(0,can1)}\n{member.name}: ❤️{max(0,can2)}")
    kazanan = ctx.author if can1 > can2 else member
    odul = random.randint(50, 150)
    economy = json_oku('economy.json')
    wid = str(kazanan.id)
    if wid not in economy:
        economy[wid] = {'para': 1000, 'banka': 0}
    economy[wid]['para'] += odul
    json_yaz('economy.json', economy)
    await msg.edit(content=f"🏆 **{kazanan.mention}** kazandı! +{odul}💰")

@bot.command(aliases=['rulet'])
async def roulette(ctx, miktar: int, secim: str):
    secim = secim.lower()
    if secim in ['kırmızı', 'k', 'red']:
        secim = 'kırmızı'
    elif secim in ['siyah', 's', 'black']:
        secim = 'siyah'
    elif secim in ['yeşil', 'y', 'green']:
        secim = 'yeşil'
    else:
        await ctx.send("❌ kırmızı/siyah/yeşil seç!")
        return
    if miktar < 10:
        await ctx.send("❌ Minimum 10💰!")
        return
    economy = json_oku('economy.json')
    uid = str(ctx.author.id)
    if uid not in economy:
        economy[uid] = {'para': 1000, 'banka': 0}
    if economy[uid]['para'] < miktar:
        await ctx.send("❌ Yeterli paran yok!")
        return
    economy[uid]['para'] -= miktar
    sans = random.randint(1, 100)
    if sans <= 5:
        sonuc = 'yeşil'
        emoji = '🟢'
    elif sans <= 52:
        sonuc = 'kırmızı'
        emoji = '🔴'
    else:
        sonuc = 'siyah'
        emoji = '⚫'
    if sonuc == secim:
        if sonuc == 'yeşil':
            odul = miktar * 14
        else:
            odul = miktar * 2
        economy[uid]['para'] += odul
        mesaj = f"🎉 Kazandın! +{odul}💰"
        renk = discord.Color.green()
    else:
        mesaj = f"😢 Kaybettin! -{miktar}💰"
        renk = discord.Color.red()
    json_yaz('economy.json', economy)
    embed = discord.Embed(title="🎡 Rulet", color=renk)
    embed.description = f"{emoji} **{sonuc.upper()}**\n{mesaj}"
    embed.add_field(name="💰 Bakiye", value=f"{economy[uid]['para']}💰")
    await ctx.send(embed=embed)

@bot.command(aliases=['balık', 'fishing'])
async def fish(ctx):
    economy = json_oku('economy.json')
    uid = str(ctx.author.id)
    if uid not in economy:
        economy[uid] = {'para': 1000, 'banka': 0}
    simdi = datetime.now()
    if 'son_balik' in economy[uid] and economy[uid]['son_balik']:
        son = datetime.fromisoformat(economy[uid]['son_balik'])
        if simdi - son < timedelta(minutes=5):
            kalan = timedelta(minutes=5) - (simdi - son)
            dk = int(kalan.total_seconds() // 60)
            sn = int(kalan.total_seconds() % 60)
            await ctx.send(f"🎣 Oltanı hazırlıyorsun! **{dk}dk {sn}sn** bekle.")
            return
    economy[uid]['son_balik'] = simdi.isoformat()
    baliklar = [
        ('🗑️', 'Çöp', 0, 0, 15),
        ('🦐', 'Karides', 5, 15, 20),
        ('🐟', 'Balık', 15, 35, 25),
        ('🐠', 'Tropikal Balık', 30, 60, 18),
        ('🦑', 'Kalamar', 50, 100, 10),
        ('🐙', 'Ahtapot', 80, 150, 7),
        ('🦈', 'Köpekbalığı', 150, 300, 4),
        ('🐋', 'Balina', 500, 1000, 1),
    ]
    secimler = []
    agirliklar = []
    for b in baliklar:
        secimler.append(b)
        agirliklar.append(b[4])
    yakalanan = random.choices(secimler, weights=agirliklar)[0]
    emoji, isim, min_p, max_p, _ = yakalanan
    if min_p == 0:
        para = 0
        mesaj = f"💔 Sadece **{isim}** {emoji} çıktı..."
        renk = discord.Color.greyple()
    else:
        para = random.randint(min_p, max_p)
        economy[uid]['para'] += para
        if isim == 'Balina':
            mesaj = f"🎉 **EFSANE!** Bir **{isim}** {emoji} yakaladın!"
            renk = discord.Color.gold()
        elif isim in ['Köpekbalığı', 'Ahtapot']:
            mesaj = f"✨ **NADİR!** Bir **{isim}** {emoji} yakaladın!"
            renk = discord.Color.purple()
        else:
            mesaj = f"🎣 Bir **{isim}** {emoji} yakaladın!"
            renk = discord.Color.blue()
    json_yaz('economy.json', economy)
    embed = discord.Embed(title="🎣 Balık Tutma", color=renk)
    embed.description = mesaj
    if para > 0:
        embed.add_field(name="💰 Kazanç", value=f"+{para}💰", inline=True)
    embed.add_field(name="🎒 Bakiye", value=f"{economy[uid]['para']}💰", inline=True)
    await ctx.send(embed=embed)

@bot.command(aliases=['bj', '21'])
async def blackjack(ctx, bahis: int):
    if bahis < 10:
        await ctx.send("❌ Minimum 10💰!")
        return
    economy = json_oku('economy.json')
    uid = str(ctx.author.id)
    if uid not in economy:
        economy[uid] = {'para': 1000, 'banka': 0}
    if economy[uid]['para'] < bahis:
        await ctx.send("❌ Yeterli paran yok!")
        return
    economy[uid]['para'] -= bahis
    kartlar = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    semboller = ['♠️', '♥️', '♦️', '♣️']
    def kart_cek():
        return random.choice(kartlar), random.choice(semboller)
    def hesapla(el):
        toplam = 0
        as_sayisi = 0
        for kart, _ in el:
            if kart in ['J', 'Q', 'K']:
                toplam += 10
            elif kart == 'A':
                toplam += 11
                as_sayisi += 1
            else:
                toplam += int(kart)
        while toplam > 21 and as_sayisi > 0:
            toplam -= 10
            as_sayisi -= 1
        return toplam
    def el_goster(el):
        return ' '.join([f"{k}{s}" for k, s in el])
    oyuncu = [kart_cek(), kart_cek()]
    kurpiye = [kart_cek(), kart_cek()]
    oyuncu_toplam = hesapla(oyuncu)
    if oyuncu_toplam == 21:
        odul = int(bahis * 2.5)
        economy[uid]['para'] += odul
        json_yaz('economy.json', economy)
        embed = discord.Embed(title="🃏 BLACKJACK!", color=discord.Color.gold())
        embed.description = f"**Elin:** {el_goster(oyuncu)} = **21**\n\n🎉 **BLACKJACK!** +{odul}💰"
        await ctx.send(embed=embed)
        return
    embed = discord.Embed(title="🃏 Blackjack", color=discord.Color.blue())
    embed.add_field(name="🎴 Senin Elin", value=f"{el_goster(oyuncu)} = **{oyuncu_toplam}**", inline=False)
    embed.add_field(name="🎩 Kurpiye", value=f"{kurpiye[0][0]}{kurpiye[0][1]} ❓", inline=False)
    embed.set_footer(text="✅ 'ç' = Çek | 🛑 'd' = Dur")
    msg = await ctx.send(embed=embed)
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['ç', 'd', 'c', 'cek', 'çek', 'dur']
    while True:
        try:
            cevap = await bot.wait_for('message', check=check, timeout=30)
            try:
                await cevap.delete()
            except:
                pass
            if cevap.content.lower() in ['ç', 'c', 'cek', 'çek']:
                oyuncu.append(kart_cek())
                oyuncu_toplam = hesapla(oyuncu)
                embed = discord.Embed(title="🃏 Blackjack", color=discord.Color.blue())
                embed.add_field(name="🎴 Senin Elin", value=f"{el_goster(oyuncu)} = **{oyuncu_toplam}**", inline=False)
                embed.add_field(name="🎩 Kurpiye", value=f"{kurpiye[0][0]}{kurpiye[0][1]} ❓", inline=False)
                embed.set_footer(text="✅ 'ç' = Çek | 🛑 'd' = Dur")
                await msg.edit(embed=embed)
                if oyuncu_toplam > 21:
                    json_yaz('economy.json', economy)
                    embed = discord.Embed(title="🃏 Blackjack", color=discord.Color.red())
                    embed.add_field(name="🎴 Senin Elin", value=f"{el_goster(oyuncu)} = **{oyuncu_toplam}**", inline=False)
                    embed.description = f"💥 **BATTINIZ!** -{bahis}💰"
                    await msg.edit(embed=embed)
                    return
            else:
                break
        except asyncio.TimeoutError:
            json_yaz('economy.json', economy)
            await msg.edit(content="⏰ Süre doldu! Bahis kaybedildi.")
            return
    kurpiye_toplam = hesapla(kurpiye)
    while kurpiye_toplam < 17:
        kurpiye.append(kart_cek())
        kurpiye_toplam = hesapla(kurpiye)
    if kurpiye_toplam > 21:
        odul = bahis * 2
        economy[uid]['para'] += odul
        sonuc = f"🎉 **Kurpiye battı!** +{odul}💰"
        renk = discord.Color.green()
    elif oyuncu_toplam > kurpiye_toplam:
        odul = bahis * 2
        economy[uid]['para'] += odul
        sonuc = f"🎉 **Kazandın!** +{odul}💰"
        renk = discord.Color.green()
    elif oyuncu_toplam < kurpiye_toplam:
        sonuc = f"😢 **Kaybettin!** -{bahis}💰"
        renk = discord.Color.red()
    else:
        economy[uid]['para'] += bahis
        sonuc = f"🤝 **Berabere!** Bahis iade."
        renk = discord.Color.greyple()
    json_yaz('economy.json', economy)
    embed = discord.Embed(title="🃏 Blackjack", color=renk)
    embed.add_field(name="🎴 Senin Elin", value=f"{el_goster(oyuncu)} = **{oyuncu_toplam}**", inline=False)
    embed.add_field(name="🎩 Kurpiye", value=f"{el_goster(kurpiye)} = **{kurpiye_toplam}**", inline=False)
    embed.description = sonuc
    embed.add_field(name="💰 Bakiye", value=f"{economy[uid]['para']}💰", inline=False)
    await msg.edit(embed=embed)

@bot.command()
async def crash(ctx, bahis: int):
    if bahis < 10:
        await ctx.send("❌ Minimum 10💰!")
        return
    economy = json_oku('economy.json')
    uid = str(ctx.author.id)
    if uid not in economy:
        economy[uid] = {'para': 1000, 'banka': 0}
    if economy[uid]['para'] < bahis:
        await ctx.send("❌ Yeterli paran yok!")
        return
    economy[uid]['para'] -= bahis
    patlama = round(random.uniform(1.1, 10.0), 2)
    if random.randint(1, 100) <= 40:
        patlama = round(random.uniform(1.1, 2.0), 2)
    elif random.randint(1, 100) <= 70:
        patlama = round(random.uniform(1.5, 4.0), 2)
    carpan = 1.00
    embed = discord.Embed(title="🚀 Crash", color=discord.Color.green())
    embed.description = f"📈 Çarpan: **{carpan}x**\n💰 Bahis: **{bahis}💰**\n\n🛑 **'ç' yaz** = Parayı Çek"
    msg = await ctx.send(embed=embed)
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['ç', 'c', 'cek', 'çek']
    cekildi = False
    while carpan < patlama:
        await asyncio.sleep(1)
        carpan = round(carpan + random.uniform(0.1, 0.5), 2)
        if carpan >= patlama:
            break
        if carpan < 2:
            renk = discord.Color.green()
        elif carpan < 4:
            renk = discord.Color.gold()
        else:
            renk = discord.Color.purple()
        embed = discord.Embed(title="🚀 Crash", color=renk)
        embed.description = f"📈 Çarpan: **{carpan}x**\n💰 Potansiyel: **{int(bahis * carpan)}💰**\n\n🛑 **'ç' yaz** = Parayı Çek"
        await msg.edit(embed=embed)
        try:
            cevap = await bot.wait_for('message', check=check, timeout=0.5)
            try:
                await cevap.delete()
            except:
                pass
            cekildi = True
            break
        except asyncio.TimeoutError:
            continue
    if cekildi:
        odul = int(bahis * carpan)
        economy[uid]['para'] += odul
        json_yaz('economy.json', economy)
        embed = discord.Embed(title="🚀 Crash", color=discord.Color.green())
        embed.description = f"✅ **{carpan}x** çarpanında çektin!\n\n🎉 **+{odul}💰** kazandın!"
        embed.add_field(name="💰 Bakiye", value=f"{economy[uid]['para']}💰")
        await msg.edit(embed=embed)
    else:
        json_yaz('economy.json', economy)
        embed = discord.Embed(title="🚀 Crash", color=discord.Color.red())
        embed.description = f"💥 **PATLADI!** ({patlama}x)\n\n😢 **-{bahis}💰** kaybettin!"
        embed.add_field(name="💰 Bakiye", value=f"{economy[uid]['para']}💰")
        await msg.edit(embed=embed)

# =====================================================
# 🎮 OYUNLAR - / KOMUTLARI
# =====================================================

@bot.tree.command(name="hunt", description="Hayvan avla ve para kazan")
async def slash_hunt(interaction: discord.Interaction):
    hayvanlar = {
        '🐀': (10, 30, "Fare"),
        '🐇': (20, 50, "Tavşan"),
        '🦊': (40, 80, "Tilki"),
        '🐺': (60, 120, "Kurt"),
        '🐻': (100, 200, "Ayı"),
        '🦁': (150, 300, "Aslan"),
        '🐉': (300, 600, "Ejderha")
    }
    weights = [25, 20, 15, 12, 10, 5, 3]
    emoji, (min_p, max_p, isim) = random.choices(list(hayvanlar.items()), weights=weights)[0]
    para = random.randint(min_p, max_p)
    economy = json_oku('economy.json')
    uid = str(interaction.user.id)
    if uid not in economy:
        economy[uid] = {'para': 1000, 'banka': 0}
    economy[uid]['para'] += para
    json_yaz('economy.json', economy)
    embed = discord.Embed(title="🏹 Avlanma", color=discord.Color.green())
    embed.description = f"{interaction.user.mention} bir **{isim}** {emoji} avladı!"
    embed.add_field(name="💰 Kazanç", value=f"+{para}💰")
    embed.add_field(name="🎒 Bakiye", value=f"{economy[uid]['para']}💰")
    await guvenli_cevap(interaction, embed=embed)

@bot.tree.command(name="slot", description="Slot makinesi oyna")
@app_commands.describe(miktar="Bahis miktarı (minimum 10)")
async def slash_slot(interaction: discord.Interaction, miktar: int = 10):
    emojiler = ['🍒', '🍋', '🍊', '🍇', '💎', '7️⃣']
    economy = json_oku('economy.json')
    uid = str(interaction.user.id)
    if uid not in economy:
        economy[uid] = {'para': 1000, 'banka': 0}
    if miktar < 10:
        await guvenli_cevap(interaction, "❌ Minimum 10💰!", ephemeral=True)
        return
    if economy[uid]['para'] < miktar:
        await guvenli_cevap(interaction, "❌ Yeterli paran yok!", ephemeral=True)
        return
    economy[uid]['para'] -= miktar
    sans = random.randint(1, 100)
    if sans <= 2:
        secilen = random.choice(emojiler)
        sonuc = [secilen, secilen, secilen]
        if secilen == '💎':
            odul = miktar * 50
        elif secilen == '7️⃣':
            odul = miktar * 30
        else:
            odul = miktar * 10
        economy[uid]['para'] += odul
        mesaj = f"🎉 **JACKPOT!** +{odul}💰"
        renk = discord.Color.gold()
    elif sans <= 15:
        secilen = random.choice(emojiler)
        diger = random.choice([e for e in emojiler if e != secilen])
        sonuc = [secilen, secilen, diger]
        random.shuffle(sonuc)
        odul = int(miktar * 1.5)
        economy[uid]['para'] += odul
        mesaj = f"✨ **İkili!** +{odul}💰"
        renk = discord.Color.green()
    else:
        sonuc = random.sample(emojiler, 3)
        mesaj = f"😢 Kaybettin! -{miktar}💰"
        renk = discord.Color.red()
    json_yaz('economy.json', economy)
    embed = discord.Embed(title="🎰 SLOT", color=renk)
    embed.description = f"**[ {' | '.join(sonuc)} ]**\n\n{mesaj}"
    embed.add_field(name="💰 Bakiye", value=f"{economy[uid]['para']}💰")
    await guvenli_cevap(interaction, embed=embed)

@bot.tree.command(name="fish", description="Balık tut ve para kazan")
async def slash_fish(interaction: discord.Interaction):
    economy = json_oku('economy.json')
    uid = str(interaction.user.id)
    if uid not in economy:
        economy[uid] = {'para': 1000, 'banka': 0}
    simdi = datetime.now()
    if 'son_balik' in economy[uid] and economy[uid]['son_balik']:
        son = datetime.fromisoformat(economy[uid]['son_balik'])
        if simdi - son < timedelta(minutes=5):
            kalan = timedelta(minutes=5) - (simdi - son)
            dk = int(kalan.total_seconds() // 60)
            sn = int(kalan.total_seconds() % 60)
            await guvenli_cevap(interaction, f"🎣 Oltanı hazırlıyorsun! **{dk}dk {sn}sn** bekle.", ephemeral=True)
            return
    economy[uid]['son_balik'] = simdi.isoformat()
    baliklar = [
        ('🗑️', 'Çöp', 0, 0, 15),
        ('🦐', 'Karides', 5, 15, 20),
        ('🐟', 'Balık', 15, 35, 25),
        ('🐠', 'Tropikal Balık', 30, 60, 18),
        ('🦑', 'Kalamar', 50, 100, 10),
        ('🐙', 'Ahtapot', 80, 150, 7),
        ('🦈', 'Köpekbalığı', 150, 300, 4),
        ('🐋', 'Balina', 500, 1000, 1),
    ]
    secimler = []
    agirliklar = []
    for b in baliklar:
        secimler.append(b)
        agirliklar.append(b[4])
    yakalanan = random.choices(secimler, weights=agirliklar)[0]
    emoji, isim, min_p, max_p, _ = yakalanan
    if min_p == 0:
        para = 0
        mesaj = f"💔 Sadece **{isim}** {emoji} çıktı..."
        renk = discord.Color.greyple()
    else:
        para = random.randint(min_p, max_p)
        economy[uid]['para'] += para
        if isim == 'Balina':
            mesaj = f"🎉 **EFSANE!** Bir **{isim}** {emoji} yakaladın!"
            renk = discord.Color.gold()
        elif isim in ['Köpekbalığı', 'Ahtapot']:
            mesaj = f"✨ **NADİR!** Bir **{isim}** {emoji} yakaladın!"
            renk = discord.Color.purple()
        else:
            mesaj = f"🎣 Bir **{isim}** {emoji} yakaladın!"
            renk = discord.Color.blue()
    json_yaz('economy.json', economy)
    embed = discord.Embed(title="🎣 Balık Tutma", color=renk)
    embed.description = mesaj
    if para > 0:
        embed.add_field(name="💰 Kazanç", value=f"+{para}💰", inline=True)
    embed.add_field(name="🎒 Bakiye", value=f"{economy[uid]['para']}💰", inline=True)
    await guvenli_cevap(interaction, embed=embed)

@bot.tree.command(name="coinflip", description="Yazı-tura oyna")
@app_commands.describe(miktar="Bahis miktarı (minimum 10)")
async def slash_coinflip(interaction: discord.Interaction, miktar: int):
    economy = json_oku('economy.json')
    uid = str(interaction.user.id)
    if uid not in economy:
        economy[uid] = {'para': 1000, 'banka': 0}
    if miktar < 10:
        await guvenli_cevap(interaction, "❌ Minimum 10💰!", ephemeral=True)
        return
    if economy[uid]['para'] < miktar:
        await guvenli_cevap(interaction, "❌ Yeterli paran yok!", ephemeral=True)
        return
    economy[uid]['para'] -= miktar
    if random.randint(1, 100) <= 45:
        odul = miktar * 2
        economy[uid]['para'] += odul
        sonuc = "🪙 YAZI"
        mesaj = f"🎉 Kazandın! +{odul}💰"
        renk = discord.Color.green()
    else:
        sonuc = "🪙 TURA"
        mesaj = f"😢 Kaybettin! -{miktar}💰"
        renk = discord.Color.red()
    json_yaz('economy.json', economy)
    embed = discord.Embed(title="🪙 Coinflip", color=renk)
    embed.description = f"Sonuç: **{sonuc}**\n{mesaj}"
    embed.add_field(name="💰 Bakiye", value=f"{economy[uid]['para']}💰")
    await guvenli_cevap(interaction, embed=embed)

@bot.tree.command(name="battle", description="Biriyle savaş")
@app_commands.describe(member="Rakip")
async def slash_battle(interaction: discord.Interaction, member: discord.Member):
    if member.bot or member == interaction.user:
        await guvenli_cevap(interaction, "❌ Geçersiz rakip!", ephemeral=True)
        return
    await guvenli_cevap(interaction, f"⚔️ **SAVAŞ BAŞLIYOR!**\n{interaction.user.name}: ❤️100\n{member.name}: ❤️100")
    can1, can2 = 100, 100
    while can1 > 0 and can2 > 0:
        await asyncio.sleep(1)
        h1 = random.randint(15, 35)
        h2 = random.randint(15, 35)
        can2 -= h1
        can1 -= h2
        await interaction.edit_original_response(content=f"⚔️ **SAVAŞ!**\n{interaction.user.name}: ❤️{max(0,can1)}\n{member.name}: ❤️{max(0,can2)}")
    kazanan = interaction.user if can1 > can2 else member
    odul = random.randint(50, 150)
    economy = json_oku('economy.json')
    wid = str(kazanan.id)
    if wid not in economy:
        economy[wid] = {'para': 1000, 'banka': 0}
    economy[wid]['para'] += odul
    json_yaz('economy.json', economy)
    await interaction.edit_original_response(content=f"🏆 **{kazanan.mention}** kazandı! +{odul}💰")

@bot.tree.command(name="roulette", description="Rulet oyna")
@app_commands.describe(miktar="Bahis miktarı", renk="kırmızı/siyah/yeşil")
@app_commands.choices(renk=[
    app_commands.Choice(name="🔴 Kırmızı", value="kırmızı"),
    app_commands.Choice(name="⚫ Siyah", value="siyah"),
    app_commands.Choice(name="🟢 Yeşil", value="yeşil")
])
async def slash_roulette(interaction: discord.Interaction, miktar: int, renk: str):
    economy = json_oku('economy.json')
    uid = str(interaction.user.id)
    if uid not in economy:
        economy[uid] = {'para': 1000, 'banka': 0}
    if miktar < 10:
        await guvenli_cevap(interaction, "❌ Minimum 10💰!", ephemeral=True)
        return
    if economy[uid]['para'] < miktar:
        await guvenli_cevap(interaction, "❌ Yeterli paran yok!", ephemeral=True)
        return
    economy[uid]['para'] -= miktar
    sans = random.randint(1, 100)
    if sans <= 5:
        sonuc = 'yeşil'
        emoji = '🟢'
    elif sans <= 52:
        sonuc = 'kırmızı'
        emoji = '🔴'
    else:
        sonuc = 'siyah'
        emoji = '⚫'
    if sonuc == renk:
        if sonuc == 'yeşil':
            odul = miktar * 14
        else:
            odul = miktar * 2
        economy[uid]['para'] += odul
        mesaj = f"🎉 Kazandın! +{odul}💰"
        renk_embed = discord.Color.green()
    else:
        mesaj = f"😢 Kaybettin! -{miktar}💰"
        renk_embed = discord.Color.red()
    json_yaz('economy.json', economy)
    embed = discord.Embed(title="🎡 Rulet", color=renk_embed)
    embed.description = f"{emoji} **{sonuc.upper()}**\n{mesaj}"
    embed.add_field(name="💰 Bakiye", value=f"{economy[uid]['para']}💰")
    await guvenli_cevap(interaction, embed=embed)

@bot.tree.command(name="blackjack", description="21 kart oyunu")
@app_commands.describe(bahis="Bahis miktarı (minimum 10)")
async def slash_blackjack(interaction: discord.Interaction, bahis: int):
    economy = json_oku('economy.json')
    uid = str(interaction.user.id)
    if uid not in economy:
        economy[uid] = {'para': 1000, 'banka': 0}
    if bahis < 10:
        await guvenli_cevap(interaction, "❌ Minimum 10💰!", ephemeral=True)
        return
    if economy[uid]['para'] < bahis:
        await guvenli_cevap(interaction, "❌ Yeterli paran yok!", ephemeral=True)
        return
    economy[uid]['para'] -= bahis
    kartlar = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    semboller = ['♠️', '♥️', '♦️', '♣️']
    def kart_cek():
        return random.choice(kartlar), random.choice(semboller)
    def hesapla(el):
        toplam = 0
        as_sayisi = 0
        for kart, _ in el:
            if kart in ['J', 'Q', 'K']:
                toplam += 10
            elif kart == 'A':
                toplam += 11
                as_sayisi += 1
            else:
                toplam += int(kart)
        while toplam > 21 and as_sayisi > 0:
            toplam -= 10
            as_sayisi -= 1
        return toplam
    def el_goster(el):
        return ' '.join([f"{k}{s}" for k, s in el])
    oyuncu = [kart_cek(), kart_cek()]
    kurpiye = [kart_cek(), kart_cek()]
    oyuncu_toplam = hesapla(oyuncu)
    if oyuncu_toplam == 21:
        odul = int(bahis * 2.5)
        economy[uid]['para'] += odul
        json_yaz('economy.json', economy)
        embed = discord.Embed(title="🃏 BLACKJACK!", color=discord.Color.gold())
        embed.description = f"**Elin:** {el_goster(oyuncu)} = **21**\n\n🎉 **BLACKJACK!** +{odul}💰"
        await guvenli_cevap(interaction, embed=embed)
        return
    embed = discord.Embed(title="🃏 Blackjack", color=discord.Color.blue())
    embed.add_field(name="🎴 Senin Elin", value=f"{el_goster(oyuncu)} = **{oyuncu_toplam}**", inline=False)
    embed.add_field(name="🎩 Kurpiye", value=f"{kurpiye[0][0]}{kurpiye[0][1]} ❓", inline=False)
    embed.set_footer(text="✅ 'ç' yaz = Çek | 🛑 'd' yaz = Dur (30 saniye)")
    await guvenli_cevap(interaction, embed=embed)
    def check(m):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id and m.content.lower() in ['ç', 'd', 'c', 'cek', 'çek', 'dur']
    while True:
        try:
            cevap = await bot.wait_for('message', check=check, timeout=30)
            try:
                await cevap.delete()
            except:
                pass
            if cevap.content.lower() in ['ç', 'c', 'cek', 'çek']:
                oyuncu.append(kart_cek())
                oyuncu_toplam = hesapla(oyuncu)
                embed = discord.Embed(title="🃏 Blackjack", color=discord.Color.blue())
                embed.add_field(name="🎴 Senin Elin", value=f"{el_goster(oyuncu)} = **{oyuncu_toplam}**", inline=False)
                embed.add_field(name="🎩 Kurpiye", value=f"{kurpiye[0][0]}{kurpiye[0][1]} ❓", inline=False)
                embed.set_footer(text="✅ 'ç' yaz = Çek | 🛑 'd' yaz = Dur")
                await interaction.edit_original_response(embed=embed)
                if oyuncu_toplam > 21:
                    json_yaz('economy.json', economy)
                    embed = discord.Embed(title="🃏 Blackjack", color=discord.Color.red())
                    embed.add_field(name="🎴 Senin Elin", value=f"{el_goster(oyuncu)} = **{oyuncu_toplam}**", inline=False)
                    embed.description = f"💥 **BATTINIZ!** -{bahis}💰"
                    await interaction.edit_original_response(embed=embed)
                    return
            else:
                break
        except asyncio.TimeoutError:
            json_yaz('economy.json', economy)
            await interaction.edit_original_response(content="⏰ Süre doldu! Bahis kaybedildi.", embed=None)
            return
    kurpiye_toplam = hesapla(kurpiye)
    while kurpiye_toplam < 17:
        kurpiye.append(kart_cek())
        kurpiye_toplam = hesapla(kurpiye)
    if kurpiye_toplam > 21:
        odul = bahis * 2
        economy[uid]['para'] += odul
        sonuc = f"🎉 **Kurpiye battı!** +{odul}💰"
        renk = discord.Color.green()
    elif oyuncu_toplam > kurpiye_toplam:
        odul = bahis * 2
        economy[uid]['para'] += odul
        sonuc = f"🎉 **Kazandın!** +{odul}💰"
        renk = discord.Color.green()
    elif oyuncu_toplam < kurpiye_toplam:
        sonuc = f"😢 **Kaybettin!** -{bahis}💰"
        renk = discord.Color.red()
    else:
        economy[uid]['para'] += bahis
        sonuc = f"🤝 **Berabere!** Bahis iade."
        renk = discord.Color.greyple()
    json_yaz('economy.json', economy)
    embed = discord.Embed(title="🃏 Blackjack", color=renk)
    embed.add_field(name="🎴 Senin Elin", value=f"{el_goster(oyuncu)} = **{oyuncu_toplam}**", inline=False)
    embed.add_field(name="🎩 Kurpiye", value=f"{el_goster(kurpiye)} = **{kurpiye_toplam}**", inline=False)
    embed.description = sonuc
    embed.add_field(name="💰 Bakiye", value=f"{economy[uid]['para']}💰", inline=False)
    await interaction.edit_original_response(embed=embed)

@bot.tree.command(name="crash", description="Çarpan yükselir, patlamadan çek!")
@app_commands.describe(bahis="Bahis miktarı (minimum 10)")
async def slash_crash(interaction: discord.Interaction, bahis: int):
    economy = json_oku('economy.json')
    uid = str(interaction.user.id)
    if uid not in economy:
        economy[uid] = {'para': 1000, 'banka': 0}
    if bahis < 10:
        await guvenli_cevap(interaction, "❌ Minimum 10💰!", ephemeral=True)
        return
    if economy[uid]['para'] < bahis:
        await guvenli_cevap(interaction, "❌ Yeterli paran yok!", ephemeral=True)
        return
    economy[uid]['para'] -= bahis
    patlama = round(random.uniform(1.1, 10.0), 2)
    if random.randint(1, 100) <= 40:
        patlama = round(random.uniform(1.1, 2.0), 2)
    elif random.randint(1, 100) <= 70:
        patlama = round(random.uniform(1.5, 4.0), 2)
    carpan = 1.00
    embed = discord.Embed(title="🚀 Crash", color=discord.Color.green())
    embed.description = f"📈 Çarpan: **{carpan}x**\n💰 Bahis: **{bahis}💰**\n\n🛑 **'ç' yaz** = Parayı Çek"
    await guvenli_cevap(interaction, embed=embed)
    def check(m):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id and m.content.lower() in ['ç', 'c', 'cek', 'çek']
    cekildi = False
    while carpan < patlama:
        await asyncio.sleep(1)
        carpan = round(carpan + random.uniform(0.1, 0.5), 2)
        if carpan >= patlama:
            break
        if carpan < 2:
            renk = discord.Color.green()
        elif carpan < 4:
            renk = discord.Color.gold()
        else:
            renk = discord.Color.purple()
        embed = discord.Embed(title="🚀 Crash", color=renk)
        embed.description = f"📈 Çarpan: **{carpan}x**\n💰 Potansiyel: **{int(bahis * carpan)}💰**\n\n🛑 **'ç' yaz** = Parayı Çek"
        await interaction.edit_original_response(embed=embed)
        try:
            cevap = await bot.wait_for('message', check=check, timeout=0.5)
            try:
                await cevap.delete()
            except:
                pass
            cekildi = True
            break
        except asyncio.TimeoutError:
            continue
    if cekildi:
        odul = int(bahis * carpan)
        economy[uid]['para'] += odul
        json_yaz('economy.json', economy)
        embed = discord.Embed(title="🚀 Crash", color=discord.Color.green())
        embed.description = f"✅ **{carpan}x** çarpanında çektin!\n\n🎉 **+{odul}💰** kazandın!"
        embed.add_field(name="💰 Bakiye", value=f"{economy[uid]['para']}💰")
        await interaction.edit_original_response(embed=embed)
    else:
        json_yaz('economy.json', economy)
        embed = discord.Embed(title="🚀 Crash", color=discord.Color.red())
        embed.description = f"💥 **PATLADI!** ({patlama}x)\n\n😢 **-{bahis}💰** kaybettin!"
        embed.add_field(name="💰 Bakiye", value=f"{economy[uid]['para']}💰")
        await interaction.edit_original_response(embed=embed)

# =====================================================
# 💰 EKONOMİ - ! KOMUTLARI
# =====================================================

@bot.command(aliases=['bal', 'para'])
async def bakiye(ctx, member: discord.Member = None):
    member = member or ctx.author
    economy = json_oku('economy.json')
    uid = str(member.id)
    if uid not in economy:
        economy[uid] = {'para': 1000, 'banka': 0}
        json_yaz('economy.json', economy)
    para = economy[uid]['para']
    banka = economy[uid].get('banka', 0)
    embed = discord.Embed(title=f"💰 {member.name}", color=discord.Color.gold())
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="💵 Cüzdan", value=f"{para:,}💰", inline=True)
    embed.add_field(name="🏦 Banka", value=f"{banka:,}💰", inline=True)
    embed.add_field(name="💎 Toplam", value=f"{para + banka:,}💰", inline=True)
    await ctx.send(embed=embed)

@bot.command(aliases=['daily'])
async def günlük(ctx):
    economy = json_oku('economy.json')
    uid = str(ctx.author.id)
    if uid not in economy:
        economy[uid] = {'para': 1000, 'banka': 0}
    simdi = datetime.now()
    if 'son_gunluk' in economy[uid] and economy[uid]['son_gunluk']:
        son = datetime.fromisoformat(economy[uid]['son_gunluk'])
        if simdi - son < timedelta(hours=24):
            kalan = timedelta(hours=24) - (simdi - son)
            saat = int(kalan.total_seconds() // 3600)
            dk = int((kalan.total_seconds() % 3600) // 60)
            await ctx.send(f"⏰ Bekle! **{saat}s {dk}dk** kaldı.")
            return
    if 'streak' not in economy[uid]:
        economy[uid]['streak'] = 0
    if 'son_gunluk' in economy[uid] and economy[uid]['son_gunluk']:
        son = datetime.fromisoformat(economy[uid]['son_gunluk'])
        if simdi - son < timedelta(hours=48):
            economy[uid]['streak'] += 1
        else:
            economy[uid]['streak'] = 1
    else:
        economy[uid]['streak'] = 1
    streak = economy[uid]['streak']
    base = random.randint(200, 500)
    bonus = min(streak * 25, 250)
    toplam = base + bonus
    economy[uid]['para'] += toplam
    economy[uid]['son_gunluk'] = simdi.isoformat()
    json_yaz('economy.json', economy)
    embed = discord.Embed(title="🎁 Günlük Ödül", color=discord.Color.gold())
    embed.add_field(name="💰 Temel", value=f"+{base}💰", inline=True)
    embed.add_field(name="🔥 Streak", value=f"+{bonus}💰 ({streak} gün)", inline=True)
    embed.add_field(name="💎 Toplam", value=f"+{toplam}💰", inline=True)
    await ctx.send(embed=embed)

@bot.command(aliases=['free'])
async def bedava(ctx):
    economy = json_oku('economy.json')
    uid = str(ctx.author.id)
    if uid not in economy:
        economy[uid] = {'para': 1000, 'banka': 0}
    simdi = datetime.now()
    if 'son_bedava' in economy[uid] and economy[uid]['son_bedava']:
        son = datetime.fromisoformat(economy[uid]['son_bedava'])
        if simdi - son < timedelta(hours=2):
            kalan = timedelta(hours=2) - (simdi - son)
            dk = int(kalan.total_seconds() // 60)
            await ctx.send(f"⏰ Bekle! **{dk} dakika** kaldı.")
            return
    para = random.randint(50, 150)
    economy[uid]['para'] += para
    economy[uid]['son_bedava'] = simdi.isoformat()
    json_yaz('economy.json', economy)
    await ctx.send(f"💸 Bedava: **+{para}💰**")

@bot.command(aliases=['work', 'iş'])
async def çalış(ctx):
    economy = json_oku('economy.json')
    uid = str(ctx.author.id)
    if uid not in economy:
        economy[uid] = {'para': 1000, 'banka': 0}
    simdi = datetime.now()
    if 'son_calis' in economy[uid] and economy[uid]['son_calis']:
        son = datetime.fromisoformat(economy[uid]['son_calis'])
        if simdi - son < timedelta(minutes=30):
            kalan = timedelta(minutes=30) - (simdi - son)
            dk = int(kalan.total_seconds() // 60)
            await ctx.send(f"⏰ Dinleniyorsun! **{dk} dakika** bekle.")
            return
    isler = [
        ("💻 Programlama yaptın", 100, 200),
        ("🍕 Pizza dağıttın", 50, 100),
        ("🚗 Uber çalıştın", 80, 150),
        ("📦 Kargo taşıdın", 60, 120),
        ("🎨 Tasarım yaptın", 120, 220)
    ]
    is_secim = random.choice(isler)
    kazanc = random.randint(is_secim[1], is_secim[2])
    economy[uid]['para'] += kazanc
    economy[uid]['son_calis'] = simdi.isoformat()
    json_yaz('economy.json', economy)
    await ctx.send(f"{is_secim[0]} ve **+{kazanc}💰** kazandın!")

@bot.command(aliases=['deposit'])
async def yatır(ctx, miktar: str):
    economy = json_oku('economy.json')
    uid = str(ctx.author.id)
    if uid not in economy:
        economy[uid] = {'para': 1000, 'banka': 0}
    if miktar.lower() in ['hepsi', 'all']:
        miktar = economy[uid]['para']
    else:
        try:
            miktar = int(miktar)
        except:
            await ctx.send("❌ Geçerli miktar gir!")
            return
    if miktar <= 0 or economy[uid]['para'] < miktar:
        await ctx.send("❌ Yeterli paran yok!")
        return
    economy[uid]['para'] -= miktar
    economy[uid]['banka'] = economy[uid].get('banka', 0) + miktar
    json_yaz('economy.json', economy)
    await ctx.send(f"🏦 **{miktar}💰** yatırıldı!")

@bot.command(aliases=['withdraw'])
async def çek(ctx, miktar: str):
    economy = json_oku('economy.json')
    uid = str(ctx.author.id)
    if uid not in economy:
        economy[uid] = {'para': 1000, 'banka': 0}
    banka = economy[uid].get('banka', 0)
    if miktar.lower() in ['hepsi', 'all']:
        miktar = banka
    else:
        try:
            miktar = int(miktar)
        except:
            await ctx.send("❌ Geçerli miktar gir!")
            return
    if miktar <= 0 or banka < miktar:
        await ctx.send("❌ Bankada yeterli para yok!")
        return
    economy[uid]['banka'] -= miktar
    economy[uid]['para'] += miktar
    json_yaz('economy.json', economy)
    await ctx.send(f"💵 **{miktar}💰** çekildi!")

@bot.command(aliases=['give', 'ver'])
async def gönder(ctx, member: discord.Member, miktar: int):
    if member.bot or member == ctx.author:
        await ctx.send("❌ Geçersiz!")
        return
    economy = json_oku('economy.json')
    uid = str(ctx.author.id)
    tid = str(member.id)
    if uid not in economy:
        economy[uid] = {'para': 1000, 'banka': 0}
    if tid not in economy:
        economy[tid] = {'para': 1000, 'banka': 0}
    if economy[uid]['para'] < miktar:
        await ctx.send("❌ Yeterli paran yok!")
        return
    economy[uid]['para'] -= miktar
    economy[tid]['para'] += miktar
    json_yaz('economy.json', economy)
    await ctx.send(f"💸 {ctx.author.mention} → {member.mention}: **{miktar}💰**")

@bot.command(aliases=['lb', 'top'])
async def zenginler(ctx):
    economy = json_oku('economy.json')
    siralama = sorted(economy.items(), key=lambda x: x[1]['para'] + x[1].get('banka', 0), reverse=True)[:10]
    embed = discord.Embed(title="💎 En Zenginler", color=discord.Color.gold())
    emojiler = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    text = ""
    for i, (user_id, data) in enumerate(siralama):
        user = bot.get_user(int(user_id))
        toplam = data['para'] + data.get('banka', 0)
        if user:
            text += f"{emojiler[i]} **{user.name}** - {toplam:,}💰\n"
    embed.description = text if text else "Henüz kimse yok!"
    await ctx.send(embed=embed)

@bot.command(aliases=['rob', 'soy'])
async def soygun(ctx, member: discord.Member):
    if member.bot or member == ctx.author:
        await ctx.send("❌ Geçersiz hedef!")
        return
    economy = json_oku('economy.json')
    uid = str(ctx.author.id)
    tid = str(member.id)
    if uid not in economy:
        economy[uid] = {'para': 1000, 'banka': 0}
    if tid not in economy:
        economy[tid] = {'para': 1000, 'banka': 0}
    simdi = datetime.now()
    if 'son_soygun' in economy[uid] and economy[uid]['son_soygun']:
        son = datetime.fromisoformat(economy[uid]['son_soygun'])
        if simdi - son < timedelta(hours=1):
            kalan = timedelta(hours=1) - (simdi - son)
            dk = int(kalan.total_seconds() // 60)
            await ctx.send(f"⏰ Polisler arıyor! **{dk} dk** bekle.")
            return
    economy[uid]['son_soygun'] = simdi.isoformat()
    if economy[tid]['para'] < 100:
        await ctx.send(f"❌ {member.mention} çok fakir!")
        json_yaz('economy.json', economy)
        return
    if random.randint(1, 100) <= 30:
        calınan = random.randint(economy[tid]['para'] // 10, economy[tid]['para'] // 4)
        economy[tid]['para'] -= calınan
        economy[uid]['para'] += calınan
        embed = discord.Embed(title="🔫 Soygun Başarılı!", description=f"**{calınan}💰** çaldın!", color=discord.Color.green())
    else:
        ceza = random.randint(100, 300)
        economy[uid]['para'] = max(0, economy[uid]['para'] - ceza)
        embed = discord.Embed(title="🚔 Yakalandın!", description=f"**{ceza}💰** ceza ödedin!", color=discord.Color.red())
    json_yaz('economy.json', economy)
    await ctx.send(embed=embed)

# =====================================================
# 💰 EKONOMİ - / KOMUTLARI
# =====================================================

@bot.tree.command(name="bakiye", description="Bakiyeni göster")
@app_commands.describe(member="Kullanıcı (boş bırakırsan kendin)")
async def slash_bakiye(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    economy = json_oku('economy.json')
    uid = str(member.id)
    if uid not in economy:
        economy[uid] = {'para': 1000, 'banka': 0}
        json_yaz('economy.json', economy)
    para = economy[uid]['para']
    banka = economy[uid].get('banka', 0)
    embed = discord.Embed(title=f"💰 {member.name}", color=discord.Color.gold())
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="💵 Cüzdan", value=f"{para:,}💰", inline=True)
    embed.add_field(name="🏦 Banka", value=f"{banka:,}💰", inline=True)
    embed.add_field(name="💎 Toplam", value=f"{para + banka:,}💰", inline=True)
    await guvenli_cevap(interaction, embed=embed)

@bot.tree.command(name="günlük", description="Günlük ödülünü al")
async def slash_gunluk(interaction: discord.Interaction):
    economy = json_oku('economy.json')
    uid = str(interaction.user.id)
    if uid not in economy:
        economy[uid] = {'para': 1000, 'banka': 0}
    simdi = datetime.now()
    if 'son_gunluk' in economy[uid] and economy[uid]['son_gunluk']:
        son = datetime.fromisoformat(economy[uid]['son_gunluk'])
        if simdi - son < timedelta(hours=24):
            kalan = timedelta(hours=24) - (simdi - son)
            saat = int(kalan.total_seconds() // 3600)
            dk = int((kalan.total_seconds() % 3600) // 60)
            await guvenli_cevap(interaction, f"⏰ Bekle! **{saat}s {dk}dk** kaldı.", ephemeral=True)
            return
    if 'streak' not in economy[uid]:
        economy[uid]['streak'] = 0
    if 'son_gunluk' in economy[uid] and economy[uid]['son_gunluk']:
        son = datetime.fromisoformat(economy[uid]['son_gunluk'])
        if simdi - son < timedelta(hours=48):
            economy[uid]['streak'] += 1
        else:
            economy[uid]['streak'] = 1
    else:
        economy[uid]['streak'] = 1
    streak = economy[uid]['streak']
    base = random.randint(200, 500)
    bonus = min(streak * 25, 250)
    toplam = base + bonus
    economy[uid]['para'] += toplam
    economy[uid]['son_gunluk'] = simdi.isoformat()
    json_yaz('economy.json', economy)
    embed = discord.Embed(title="🎁 Günlük Ödül", color=discord.Color.gold())
    embed.add_field(name="💰 Temel", value=f"+{base}💰", inline=True)
    embed.add_field(name="🔥 Streak", value=f"+{bonus}💰 ({streak} gün)", inline=True)
    embed.add_field(name="💎 Toplam", value=f"+{toplam}💰", inline=True)
    await guvenli_cevap(interaction, embed=embed)

@bot.tree.command(name="bedava", description="Bedava para al (2 saatte bir)")
async def slash_bedava(interaction: discord.Interaction):
    economy = json_oku('economy.json')
    uid = str(interaction.user.id)
    if uid not in economy:
        economy[uid] = {'para': 1000, 'banka': 0}
    simdi = datetime.now()
    if 'son_bedava' in economy[uid] and economy[uid]['son_bedava']:
        son = datetime.fromisoformat(economy[uid]['son_bedava'])
        if simdi - son < timedelta(hours=2):
            kalan = timedelta(hours=2) - (simdi - son)
            dk = int(kalan.total_seconds() // 60)
            await guvenli_cevap(interaction, f"⏰ Bekle! **{dk} dakika** kaldı.", ephemeral=True)
            return
    para = random.randint(50, 150)
    economy[uid]['para'] += para
    economy[uid]['son_bedava'] = simdi.isoformat()
    json_yaz('economy.json', economy)
    await guvenli_cevap(interaction, f"💸 Bedava: **+{para}💰**")

@bot.tree.command(name="çalış", description="Çalışarak para kazan")
async def slash_calis(interaction: discord.Interaction):
    economy = json_oku('economy.json')
    uid = str(interaction.user.id)
    if uid not in economy:
        economy[uid] = {'para': 1000, 'banka': 0}
    simdi = datetime.now()
    if 'son_calis' in economy[uid] and economy[uid]['son_calis']:
        son = datetime.fromisoformat(economy[uid]['son_calis'])
        if simdi - son < timedelta(minutes=30):
            kalan = timedelta(minutes=30) - (simdi - son)
            dk = int(kalan.total_seconds() // 60)
            await guvenli_cevap(interaction, f"⏰ Dinleniyorsun! **{dk} dakika** bekle.", ephemeral=True)
            return
    isler = [
        ("💻 Programlama yaptın", 100, 200),
        ("🍕 Pizza dağıttın", 50, 100),
        ("🚗 Uber çalıştın", 80, 150),
        ("📦 Kargo taşıdın", 60, 120),
        ("🎨 Tasarım yaptın", 120, 220)
    ]
    is_secim = random.choice(isler)
    kazanc = random.randint(is_secim[1], is_secim[2])
    economy[uid]['para'] += kazanc
    economy[uid]['son_calis'] = simdi.isoformat()
    json_yaz('economy.json', economy)
    await guvenli_cevap(interaction, f"{is_secim[0]} ve **+{kazanc}💰** kazandın!")

@bot.tree.command(name="zenginler", description="En zenginler listesi")
async def slash_zenginler(interaction: discord.Interaction):
    economy = json_oku('economy.json')
    siralama = sorted(economy.items(), key=lambda x: x[1]['para'] + x[1].get('banka', 0), reverse=True)[:10]
    embed = discord.Embed(title="💎 En Zenginler", color=discord.Color.gold())
    emojiler = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    text = ""
    for i, (user_id, data) in enumerate(siralama):
        user = bot.get_user(int(user_id))
        toplam = data['para'] + data.get('banka', 0)
        if user:
            text += f"{emojiler[i]} **{user.name}** - {toplam:,}💰\n"
    embed.description = text if text else "Henüz kimse yok!"
    await guvenli_cevap(interaction, embed=embed)

# =====================================================
# 🎲 EĞLENCE - ! KOMUTLARI
# =====================================================

@bot.command(aliases=['flip', 'coin'])
async def tura(ctx):
    await ctx.send(f"🪙 **{random.choice(['YAZI', 'TURA'])}**")

@bot.command(aliases=['dice'])
async def zar(ctx, adet: int = 1):
    if adet > 10:
        adet = 10
    zarlar = [random.randint(1, 6) for _ in range(adet)]
    await ctx.send(f"🎲 {zarlar} = **{sum(zarlar)}**")

@bot.command(aliases=['pfp'])
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"{member.name}", color=discord.Color.blue())
    embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(aliases=['joke'])
async def şaka(ctx):
    şakalar = [
        "Neden bilgisayarlar soğuk algınlığına yakalanmaz? Çünkü pencereleri kapalıdır! 😄",
        "Programcı nasıl ölür? Debuglanır! 💀",
        "Neden programcılar doğayı sevmez? Çok fazla bug var! 🐛",
        "Discord botu kimin oğludur? Pythonun! 🐍"
    ]
    await ctx.send(random.choice(şakalar))

@bot.command(aliases=['8ball'])
async def soru(ctx, *, soru):
    cevaplar = ["✅ Evet", "❌ Hayır", "🤔 Belki", "👍 Kesinlikle", "👎 Asla", "🔮 Büyük ihtimalle"]
    embed = discord.Embed(title="🎱 Sihirli Küre", color=discord.Color.purple())
    embed.add_field(name="❓ Soru", value=soru, inline=False)
    embed.add_field(name="💭 Cevap", value=random.choice(cevaplar), inline=False)
    await ctx.send(embed=embed)

# =====================================================
# 🎲 EĞLENCE - / KOMUTLARI
# =====================================================

@bot.tree.command(name="tura", description="Yazı-tura at")
async def slash_tura(interaction: discord.Interaction):
    await guvenli_cevap(interaction, f"🪙 **{random.choice(['YAZI', 'TURA'])}**")

@bot.tree.command(name="zar", description="Zar at")
@app_commands.describe(adet="Kaç zar (max 10)")
async def slash_zar(interaction: discord.Interaction, adet: int = 1):
    if adet > 10:
        adet = 10
    zarlar = [random.randint(1, 6) for _ in range(adet)]
    await guvenli_cevap(interaction, f"🎲 {zarlar} = **{sum(zarlar)}**")

@bot.tree.command(name="avatar", description="Avatar göster")
@app_commands.describe(member="Kullanıcı")
async def slash_avatar(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(title=f"{member.name}", color=discord.Color.blue())
    embed.set_image(url=member.display_avatar.url)
    await guvenli_cevap(interaction, embed=embed)

@bot.tree.command(name="şaka", description="Şaka yap")
async def slash_saka(interaction: discord.Interaction):
    şakalar = [
        "Neden bilgisayarlar soğuk algınlığına yakalanmaz? Çünkü pencereleri kapalıdır! 😄",
        "Programcı nasıl ölür? Debuglanır! 💀",
        "Neden programcılar doğayı sevmez? Çok fazla bug var! 🐛"
    ]
    await guvenli_cevap(interaction, random.choice(şakalar))

@bot.tree.command(name="8ball", description="Sihirli küreye sor")
@app_commands.describe(soru="Sorun")
async def slash_8ball(interaction: discord.Interaction, soru: str):
    cevaplar = ["✅ Evet", "❌ Hayır", "🤔 Belki", "👍 Kesinlikle", "👎 Asla", "🔮 Büyük ihtimalle"]
    embed = discord.Embed(title="🎱 Sihirli Küre", color=discord.Color.purple())
    embed.add_field(name="❓ Soru", value=soru, inline=False)
    embed.add_field(name="💭 Cevap", value=random.choice(cevaplar), inline=False)
    await guvenli_cevap(interaction, embed=embed)

# =====================================================
# ℹ️ BİLGİ - ! KOMUTLARI
# =====================================================

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 **{round(bot.latency * 1000)}ms**")

@bot.command(aliases=['server'])
async def sunucu(ctx):
    g = ctx.guild
    embed = discord.Embed(title=g.name, color=discord.Color.blue())
    if g.icon:
        embed.set_thumbnail(url=g.icon.url)
    embed.add_field(name="👥 Üye", value=g.member_count, inline=True)
    embed.add_field(name="💬 Kanal", value=len(g.channels), inline=True)
    embed.add_field(name="🎭 Rol", value=len(g.roles), inline=True)
    await ctx.send(embed=embed)

@bot.command(aliases=['user', 'whois'])
async def kullanıcı(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"👤 {member}", color=member.color)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="🆔 ID", value=member.id, inline=True)
    embed.add_field(name="📅 Katılma", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
    await ctx.send(embed=embed)

# =====================================================
# ℹ️ BİLGİ - / KOMUTLARI
# =====================================================

@bot.tree.command(name="ping", description="Bot gecikmesi")
async def slash_ping(interaction: discord.Interaction):
    await guvenli_cevap(interaction, f"🏓 **{round(bot.latency * 1000)}ms**")

@bot.tree.command(name="sunucu", description="Sunucu bilgisi")
async def slash_sunucu(interaction: discord.Interaction):
    g = interaction.guild
    embed = discord.Embed(title=g.name, color=discord.Color.blue())
    if g.icon:
        embed.set_thumbnail(url=g.icon.url)
    embed.add_field(name="👥 Üye", value=g.member_count, inline=True)
    embed.add_field(name="💬 Kanal", value=len(g.channels), inline=True)
    embed.add_field(name="🎭 Rol", value=len(g.roles), inline=True)
    await guvenli_cevap(interaction, embed=embed)

@bot.tree.command(name="kullanıcı", description="Kullanıcı bilgisi")
@app_commands.describe(member="Kullanıcı")
async def slash_kullanici(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(title=f"👤 {member}", color=member.color)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="🆔 ID", value=member.id, inline=True)
    embed.add_field(name="📅 Katılma", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
    await guvenli_cevap(interaction, embed=embed)

# =====================================================
# 🤖 YAPAY ZEKA - ! ve / KOMUTLARI
# =====================================================

@bot.command(aliases=['sor', 'chat'])
async def ai(ctx, *, soru):
    if not groq_client:
        await ctx.send("❌ AI ayarlanmamış!")
        return
    msg = await ctx.send("🤖 Düşünüyorum...")
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Sen yardımcı bir Türkçe asistansın. KISA cevaplar ver. Maximum 300 karakter."},
                {"role": "user", "content": soru}
            ],
            max_tokens=150
        )
        cevap = response.choices[0].message.content[:1000]
        embed = discord.Embed(title="🤖 Yapay Zeka", color=discord.Color.blue())
        embed.add_field(name="❓ Soru", value=soru[:256], inline=False)
        embed.add_field(name="💬 Cevap", value=cevap, inline=False)
        await msg.edit(content=None, embed=embed)
    except Exception as e:
        await msg.edit(content=f"❌ Hata: {str(e)[:100]}")

@bot.tree.command(name="ai", description="Yapay zekaya soru sor")
@app_commands.describe(soru="Sormak istediğin soru")
async def slash_ai(interaction: discord.Interaction, soru: str):
    if not groq_client:
        await guvenli_cevap(interaction, "❌ AI ayarlanmamış!", ephemeral=True)
        return
    await guvenli_cevap(interaction, "🤖 Düşünüyorum...")
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Sen yardımcı bir Türkçe asistansın. KISA cevaplar ver. Maximum 300 karakter."},
                {"role": "user", "content": soru}
            ],
            max_tokens=150
        )
        cevap = response.choices[0].message.content[:1000]
        embed = discord.Embed(title="🤖 Yapay Zeka", color=discord.Color.blue())
        embed.add_field(name="❓ Soru", value=soru[:256], inline=False)
        embed.add_field(name="💬 Cevap", value=cevap, inline=False)
        await interaction.edit_original_response(content=None, embed=embed)
    except Exception as e:
        await interaction.edit_original_response(content=f"❌ Hata: {str(e)[:100]}")

# =====================================================
# 📚 YARDIM - ! ve / KOMUTLARI
# =====================================================

@bot.command(aliases=['help', 'komutlar', 'h'])
async def yardım(ctx):
    embed = discord.Embed(title="📚 BOT KOMUTLARI", description="**/ yazarak otomatik tamamlama kullan!**", color=discord.Color.purple())
    embed.add_field(name="🎵 Müzik", value="`/play` `/pause` `/devam` `/skip` `/stop` `/queue` `/leave`", inline=False)
    embed.add_field(name="🎮 Oyunlar", value="`/hunt` `/fish` `/slot` `/blackjack` `/crash` `/coinflip` `/battle` `/roulette`", inline=False)
    embed.add_field(name="💰 Ekonomi", value="`/bakiye` `/günlük` `/bedava` `/çalış` `/zenginler`", inline=False)
    embed.add_field(name="🛡️ Moderasyon", value="`/kick` `/ban` `/sil` `/timeout` `/uyar`", inline=False)
    embed.add_field(name="🎲 Eğlence", value="`/tura` `/zar` `/avatar` `/şaka` `/8ball`", inline=False)
    embed.add_field(name="🤖 Yapay Zeka", value="`/ai`", inline=False)
    embed.add_field(name="ℹ️ Bilgi", value="`/ping` `/sunucu` `/kullanıcı` `/yardım`", inline=False)
    embed.set_footer(text="/ yazınca otomatik tamamlama çıkar!")
    await ctx.send(embed=embed)

@bot.tree.command(name="yardım", description="Tüm komutları göster")
async def slash_yardim(interaction: discord.Interaction):
    embed = discord.Embed(title="📚 BOT KOMUTLARI", description="**/ yazarak otomatik tamamlama kullan!**", color=discord.Color.purple())
    embed.add_field(name="🎵 Müzik", value="`/play` `/pause` `/devam` `/skip` `/stop` `/queue` `/leave`", inline=False)
    embed.add_field(name="🎮 Oyunlar", value="`/hunt` `/fish` `/slot` `/blackjack` `/crash` `/coinflip` `/battle` `/roulette`", inline=False)
    embed.add_field(name="💰 Ekonomi", value="`/bakiye` `/günlük` `/bedava` `/çalış` `/zenginler`", inline=False)
    embed.add_field(name="🛡️ Moderasyon", value="`/kick` `/ban` `/sil` `/timeout` `/uyar`", inline=False)
    embed.add_field(name="🎲 Eğlence", value="`/tura` `/zar` `/avatar` `/şaka` `/8ball`", inline=False)
    embed.add_field(name="🤖 Yapay Zeka", value="`/ai`", inline=False)
    embed.add_field(name="ℹ️ Bilgi", value="`/ping` `/sunucu` `/kullanıcı` `/yardım`", inline=False)
    embed.set_footer(text="/ yazınca otomatik tamamlama çıkar!")
    await guvenli_cevap(interaction, embed=embed)

# =====================================================
# ❌ HATA YÖNETİMİ
# =====================================================

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Yetkin yok!")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Kullanıcı bulunamadı!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Eksik: `{error.param.name}`")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        print(f"Hata: {error}")

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    print(f"Slash Hata: {error}")

# =====================================================
# 🚀 BOTU BAŞLAT
# =====================================================

print("Bot başlatılıyor...")

try:
    bot.run(TOKEN)
except discord.LoginFailure:
    print("❌ TOKEN GEÇERSİZ!")
except discord.PrivilegedIntentsRequired:
    print("❌ INTENTS KAPALI!")
except Exception as e:
    print(f"❌ HATA: {e}")

print("Bot kapandı.")