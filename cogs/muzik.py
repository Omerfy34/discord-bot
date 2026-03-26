# =====================================================
# 🎵 WOWSY BOT - MÜZİK KOMUTLARI
# =====================================================

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import yt_dlp

from config import FFMPEG_OPTIONS
from utils import guvenli_cevap

# =====================================================
# 🎵 MÜZİK FONKSİYONLARI
# =====================================================

# Müzik kuyrukları (sunucu bazlı)
music_queues = {}

def get_queue(guild_id):
    """Sunucu için müzik kuyruğunu döndür"""
    if guild_id not in music_queues:
        music_queues[guild_id] = []
    return music_queues[guild_id]

def search_and_get_audio(query):
    """Şarkı ara ve audio URL + başlık döndür"""
    try:
        ydl_opts = {
            'format': 'bestaudio[ext=webm]/bestaudio[ext=m4a]/bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'default_search': 'ytsearch',
            'source_address': '0.0.0.0',
            'force_ipv4': True,
            'geo_bypass': True,
            'socket_timeout': 15,
            'retries': 5,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            if not query.startswith(('http://', 'https://')):
                query = f"ytsearch:{query}"
            
            info = ydl.extract_info(query, download=False)
            
            if 'entries' in info:
                if len(info['entries']) == 0:
                    return None, None
                info = info['entries'][0]
            
            audio_url = None
            if 'url' in info:
                audio_url = info['url']
            elif 'formats' in info:
                for f in info['formats']:
                    if f.get('acodec') != 'none':
                        audio_url = f['url']
                        break
            
            if not audio_url:
                return None, None
            
            title = info.get('title', 'Bilinmeyen Şarkı')
            return audio_url, title
            
    except Exception as e:
        print(f"[HATA] search_and_get_audio: {e}")
        return None, None

# =====================================================
# 🎵 MÜZİK COG
# =====================================================

class Muzik(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =====================================================
    # 🎵 SLASH KOMUTLARI
    # =====================================================

    @app_commands.command(name="play", description="Müzik çal")
    @app_commands.describe(şarkı="Şarkı adı veya YouTube linki")
    async def slash_play(self, interaction: discord.Interaction, şarkı: str):
        if not interaction.user.voice:
            await guvenli_cevap(interaction, "❌ Önce bir ses kanalına katıl!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client
        
        if not vc:
            try:
                vc = await channel.connect()
                await asyncio.sleep(0.5)
            except Exception as e:
                await interaction.followup.send(f"❌ Ses kanalına katılamadım: {e}")
                return
        elif vc.channel != channel:
            try:
                await vc.move_to(channel)
                await asyncio.sleep(0.3)
            except Exception as e:
                await interaction.followup.send(f"❌ Kanala taşınamadım: {e}")
                return
        
        await interaction.followup.send(f"🔍 Aranıyor: **{şarkı}**")
        
        audio_url, title = search_and_get_audio(şarkı)
        
        if not audio_url:
            await interaction.edit_original_response(content="❌ Şarkı bulunamadı!")
            return
        
        if vc.is_playing() or vc.is_paused():
            queue = get_queue(interaction.guild.id)
            queue.append({'url': audio_url, 'title': title})
            
            embed = discord.Embed(title="➕ Kuyruğa Eklendi", color=discord.Color.blue())
            embed.description = f"**{title}**"
            embed.add_field(name="📋 Sıra", value=f"#{len(queue)}")
            await interaction.edit_original_response(content=None, embed=embed)
            return
        
        def play_next(error):
            if error:
                print(f"Oynatma hatası: {error}")
            queue = get_queue(interaction.guild.id)
            if len(queue) > 0 and vc.is_connected():
                next_song = queue.pop(0)
                try:
                    source = discord.FFmpegPCMAudio(next_song['url'], **FFMPEG_OPTIONS)
                    vc.play(source, after=play_next)
                except Exception as e:
                    print(f"Sonraki şarkı hatası: {e}")
        
        try:
            source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)
            vc.play(source, after=play_next)
            
            embed = discord.Embed(title="🎵 Şimdi Çalıyor", color=discord.Color.green())
            embed.description = f"**{title}**"
            await interaction.edit_original_response(content=None, embed=embed)
        except Exception as e:
            await interaction.edit_original_response(content=f"❌ Çalma hatası: {e}")

    @app_commands.command(name="pause", description="Müziği duraklat")
    async def slash_pause(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client:
            await guvenli_cevap(interaction, "❌ Müzik çalmıyor!", ephemeral=True)
            return
        
        vc = interaction.guild.voice_client
        
        if vc.is_playing():
            vc.pause()
            await guvenli_cevap(interaction, "⏸️ Müzik duraklatıldı!")
        else:
            await guvenli_cevap(interaction, "❌ Zaten duraklatılmış veya çalmıyor!", ephemeral=True)

    @app_commands.command(name="devam", description="Müziği devam ettir")
    async def slash_devam(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client:
            await guvenli_cevap(interaction, "❌ Müzik çalmıyor!", ephemeral=True)
            return
        
        vc = interaction.guild.voice_client
        
        if vc.is_paused():
            vc.resume()
            await guvenli_cevap(interaction, "▶️ Müzik devam ediyor!")
        else:
            await guvenli_cevap(interaction, "❌ Duraklatılmış şarkı yok!", ephemeral=True)

    @app_commands.command(name="skip", description="Şarkıyı atla")
    async def slash_skip(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client:
            await guvenli_cevap(interaction, "❌ Müzik çalmıyor!", ephemeral=True)
            return
        
        vc = interaction.guild.voice_client
        
        if vc.is_playing() or vc.is_paused():
            vc.stop()
            await guvenli_cevap(interaction, "⏭️ Şarkı atlandı!")
        else:
            await guvenli_cevap(interaction, "❌ Atlanacak şarkı yok!", ephemeral=True)

    @app_commands.command(name="stop", description="Müziği durdur ve kuyruğu temizle")
    async def slash_stop(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client:
            await guvenli_cevap(interaction, "❌ Müzik çalmıyor!", ephemeral=True)
            return
        
        vc = interaction.guild.voice_client
        get_queue(interaction.guild.id).clear()
        vc.stop()
        
        await guvenli_cevap(interaction, "⏹️ Müzik durduruldu ve kuyruk temizlendi!")

    @app_commands.command(name="leave", description="Ses kanalından ayrıl")
    async def slash_leave(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client:
            await guvenli_cevap(interaction, "❌ Zaten kanalda değilim!", ephemeral=True)
            return
        
        get_queue(interaction.guild.id).clear()
        await interaction.guild.voice_client.disconnect()
        
        await guvenli_cevap(interaction, "👋 Ses kanalından ayrıldım!")

    @app_commands.command(name="queue", description="Müzik kuyruğunu göster")
    async def slash_queue(self, interaction: discord.Interaction):
        q = get_queue(interaction.guild.id)
        
        if len(q) == 0:
            await guvenli_cevap(interaction, "📋 Kuyruk boş!")
            return
        
        embed = discord.Embed(title="📋 Müzik Kuyruğu", color=discord.Color.blue())
        
        text = ""
        for i, song in enumerate(q[:10]):
            text += f"**{i+1}.** {song['title'][:50]}\n"
        
        if len(q) > 10:
            text += f"\n... ve {len(q) - 10} şarkı daha"
        
        embed.description = text
        embed.set_footer(text=f"Toplam: {len(q)} şarkı")
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="join", description="Ses kanalına katıl")
    async def slash_join(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            await guvenli_cevap(interaction, "❌ Önce bir ses kanalına katıl!", ephemeral=True)
            return
        
        channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client
        
        try:
            if vc:
                if vc.channel.id == channel.id:
                    await guvenli_cevap(interaction, f"✅ Zaten **{channel.name}** kanalındayım!")
                    return
                await vc.move_to(channel)
                await guvenli_cevap(interaction, f"🔊 **{channel.name}** kanalına taşındım!")
            else:
                await channel.connect()
                await guvenli_cevap(interaction, f"🔊 **{channel.name}** kanalına katıldım!")
        except Exception as e:
            await guvenli_cevap(interaction, f"❌ Hata: {e}", ephemeral=True)

    @app_commands.command(name="np", description="Şu an çalan şarkıyı göster")
    async def slash_np(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client or not interaction.guild.voice_client.is_playing():
            await guvenli_cevap(interaction, "❌ Şu an çalan şarkı yok!", ephemeral=True)
            return
        
        await guvenli_cevap(interaction, "🎵 Şu an bir şarkı çalıyor!")

    # =====================================================
    # 🎵 PREFIX KOMUTLARI
    # =====================================================

    @commands.command(aliases=['p', 'çal', 'oynat'])
    async def play(self, ctx, *, query):
        if not ctx.author.voice:
            await ctx.send("❌ Önce bir ses kanalına katıl!")
            return
        
        msg = await ctx.send(f"🔍 Aranıyor: **{query}**")
        
        channel = ctx.author.voice.channel
        vc = ctx.voice_client
        
        if not vc:
            try:
                vc = await channel.connect()
                await asyncio.sleep(0.5)
            except Exception as e:
                await msg.edit(content=f"❌ Kanala katılamadım: {e}")
                return
        elif vc.channel != channel:
            try:
                await vc.move_to(channel)
                await asyncio.sleep(0.3)
            except Exception as e:
                await msg.edit(content=f"❌ Kanala taşınamadım: {e}")
                return
        
        audio_url, title = search_and_get_audio(query)
        
        if not audio_url:
            await msg.edit(content="❌ Şarkı bulunamadı!")
            return
        
        if vc.is_playing() or vc.is_paused():
            queue = get_queue(ctx.guild.id)
            queue.append({'url': audio_url, 'title': title})
            await msg.edit(content=f"➕ Kuyruğa eklendi: **{title}**")
            return
        
        def play_next(error):
            if error:
                print(f"Oynatma hatası: {error}")
            queue = get_queue(ctx.guild.id)
            if len(queue) > 0 and vc.is_connected():
                next_song = queue.pop(0)
                try:
                    source = discord.FFmpegPCMAudio(next_song['url'], **FFMPEG_OPTIONS)
                    vc.play(source, after=play_next)
                    asyncio.run_coroutine_threadsafe(
                        ctx.send(f"🎵 Şimdi çalıyor: **{next_song['title']}**"),
                        self.bot.loop
                    )
                except Exception as e:
                    print(f"Sonraki şarkı hatası: {e}")
        
        try:
            await msg.delete()
            source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)
            vc.play(source, after=play_next)
            
            embed = discord.Embed(title="🎵 Şimdi Çalıyor", description=title, color=discord.Color.green())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Çalma hatası: {e}")

    @commands.command(aliases=['duraklat', 'dur'])
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ Müzik duraklatıldı!")
        else:
            await ctx.send("❌ Müzik çalmıyor!")

    @commands.command(aliases=['resume', 'devam'])
    async def devam_et(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ Müzik devam ediyor!")
        else:
            await ctx.send("❌ Duraklatılmış şarkı yok!")

    @commands.command(aliases=['atla', 's', 'next'])
    async def skip(self, ctx):
        if ctx.voice_client and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
            ctx.voice_client.stop()
            await ctx.send("⏭️ Şarkı atlandı!")
        else:
            await ctx.send("❌ Atlanacak şarkı yok!")

    @commands.command(aliases=['kapat', 'durdur'])
    async def stop(self, ctx):
        if ctx.voice_client:
            get_queue(ctx.guild.id).clear()
            ctx.voice_client.stop()
            await ctx.send("⏹️ Müzik durduruldu!")
        else:
            await ctx.send("❌ Müzik çalmıyor!")

    @commands.command(aliases=['çık', 'dc', 'disconnect', 'ayrıl'])
    async def leave(self, ctx):
        if ctx.voice_client:
            get_queue(ctx.guild.id).clear()
            await ctx.voice_client.disconnect()
            await ctx.send("👋 Ses kanalından ayrıldım!")
        else:
            await ctx.send("❌ Zaten kanalda değilim!")

    @commands.command(aliases=['q', 'kuyruk', 'sıra', 'liste'])
    async def queue(self, ctx):
        q = get_queue(ctx.guild.id)
        
        if len(q) == 0:
            await ctx.send("📋 Kuyruk boş!")
            return
        
        embed = discord.Embed(title="📋 Müzik Kuyruğu", color=discord.Color.blue())
        
        text = ""
        for i, song in enumerate(q[:10]):
            text += f"**{i+1}.** {song['title'][:50]}\n"
        
        if len(q) > 10:
            text += f"\n... ve {len(q) - 10} şarkı daha"
        
        embed.description = text
        embed.set_footer(text=f"Toplam: {len(q)} şarkı")
        
        await ctx.send(embed=embed)

    @commands.command(aliases=['katıl', 'gel', 'connect'])
    async def join(self, ctx):
        if not ctx.author.voice:
            await ctx.send("❌ Önce bir ses kanalına katıl!")
            return
        
        channel = ctx.author.voice.channel
        vc = ctx.voice_client
        
        try:
            if vc:
                if vc.channel.id == channel.id:
                    await ctx.send(f"✅ Zaten **{channel.name}** kanalındayım!")
                    return
                await vc.move_to(channel)
                await ctx.send(f"🔊 **{channel.name}** kanalına taşındım!")
            else:
                await channel.connect()
                await ctx.send(f"🔊 **{channel.name}** kanalına katıldım!")
        except Exception as e:
            await ctx.send(f"❌ Hata: {e}")

    @commands.command(aliases=['nowplaying', 'şuan'])
    async def np(self, ctx):
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            await ctx.send("❌ Şu an çalan şarkı yok!")
            return
        
        await ctx.send("🎵 Şu an bir şarkı çalıyor!")

# =====================================================
# 🔧 COG YÜKLEME
# =====================================================

async def setup(bot):
    await bot.add_cog(Muzik(bot))