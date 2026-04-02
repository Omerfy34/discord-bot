# =====================================================
# 🎵 WOWSY BOT - MÜZİK KOMUTLARI (GÜNCEL)
# =====================================================

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random
import yt_dlp
import os
import subprocess

from config import FFMPEG_OPTIONS

# =====================================================
# 🍪 ÇEREZ AYARLARI
# =====================================================

try:
    from config import COOKIE_BROWSER
except ImportError:
    COOKIE_BROWSER = None

try:
    from config import COOKIE_FILE
except ImportError:
    COOKIE_FILE = None

# =====================================================
# 🔧 DENO/NODE KONTROLÜ
# =====================================================

def check_js_runtime():
    """JavaScript runtime kontrolü"""
    try:
        result = subprocess.run(['deno', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            return 'deno', result.stdout.split('\n')[0]
    except:
        pass

    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            return 'node', result.stdout.strip()
    except:
        pass

    return None, None

JS_RUNTIME, JS_VERSION = check_js_runtime()
if JS_RUNTIME:
    print(f"[INFO] ✅ JavaScript runtime: {JS_RUNTIME} {JS_VERSION}")
else:
    print("[UYARI] ⚠️ JavaScript runtime bulunamadı!")

# =====================================================
# 🎵 MÜZİK DEĞİŞKENLERİ
# =====================================================

music_queues = {}
now_playing = {}


def get_queue(guild_id):
    if guild_id not in music_queues:
        music_queues[guild_id] = []
    return music_queues[guild_id]


def set_now_playing(guild_id, title):
    now_playing[guild_id] = title


def get_now_playing(guild_id):
    return now_playing.get(guild_id, None)


def clear_now_playing(guild_id):
    if guild_id in now_playing:
        del now_playing[guild_id]


# =====================================================
# 🎵 YT-DLP AYARLARI
# =====================================================

def get_ydl_opts(use_android=False):
    """yt-dlp ayarlarını oluştur"""

    if use_android:
        opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'default_search': 'ytsearch',
            'extractor_args': {
                'youtube': {
                    'player_client': ['android_music', 'android'],
                }
            },
            'http_headers': {
                'User-Agent': 'com.google.android.youtube/19.02.39 (Linux; U; Android 14) gzip',
            },
            'socket_timeout': 30,
            'retries': 5,
            'geo_bypass': True,
            'geo_bypass_country': 'US',
        }
    else:
        opts = {
            'format': 'bestaudio[ext=webm]/bestaudio[ext=m4a]/bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'default_search': 'ytsearch',
            'source_address': '0.0.0.0',
            'force_ipv4': True,
            'geo_bypass': True,
            'geo_bypass_country': 'US',
            'socket_timeout': 30,
            'retries': 10,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                }
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            },
        }

    # Çerez ekle
    if COOKIE_FILE and os.path.exists(COOKIE_FILE):
        opts['cookiefile'] = COOKIE_FILE

    return opts


def search_and_get_audio(query):
    """Şarkı ara ve URL döndür"""

    # İlk deneme: Normal
    audio_url, song_info = _try_search(query, use_android=False)

    if audio_url:
        return audio_url, song_info

    # İkinci deneme: Android
    print("[INFO] 🔄 Android client deneniyor...")
    audio_url, song_info = _try_search(query, use_android=True)

    return audio_url, song_info


def _try_search(query, use_android=False):
    """Arama denemesi"""
    try:
        ydl_opts = get_ydl_opts(use_android=use_android)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            if not query.startswith(('http://', 'https://')):
                query = f"ytsearch:{query}"

            info = ydl.extract_info(query, download=False)

            if 'entries' in info:
                if len(info['entries']) == 0:
                    return None, None
                info = info['entries'][0]

            # URL bul
            audio_url = None

            if info.get('url'):
                audio_url = info['url']
            elif 'formats' in info:
                formats = info['formats']

                # Audio formatları
                audio_formats = [
                    f for f in formats
                    if f.get('acodec') != 'none'
                    and f.get('vcodec') in ['none', None]
                    and f.get('url')
                    and not f.get('format_id', '').startswith('sb')
                ]

                if audio_formats:
                    best = max(audio_formats, key=lambda x: x.get('abr') or x.get('tbr') or 0)
                    audio_url = best['url']
                else:
                    # Video+audio
                    video_formats = [
                        f for f in formats
                        if f.get('acodec') != 'none'
                        and f.get('url')
                        and not f.get('format_id', '').startswith('sb')
                    ]

                    if video_formats:
                        best = min(video_formats, key=lambda x: x.get('height') or 9999)
                        audio_url = best['url']

            if not audio_url:
                return None, None

            title = info.get('title', 'Bilinmeyen Şarkı')
            duration = info.get('duration', 0)
            thumbnail = info.get('thumbnail')

            if not thumbnail and info.get('thumbnails'):
                thumbnail = info['thumbnails'][-1].get('url')

            return audio_url, {
                'title': title,
                'duration': duration,
                'thumbnail': thumbnail
            }

    except Exception as e:
        print(f"[HATA] Arama hatası: {e}")
        return None, None


async def ensure_voice_connection(channel, existing_vc=None):
    """Ses kanalına bağlan"""
    try:
        if existing_vc:
            if existing_vc.channel.id == channel.id:
                return existing_vc, None
            await existing_vc.move_to(channel)
            await asyncio.sleep(0.5)
            return existing_vc, None

        vc = await channel.connect()

        for i in range(10):
            if vc.is_connected():
                break
            await asyncio.sleep(0.5)

        if not vc.is_connected():
            return None, "Ses kanalına bağlanılamadı!"

        return vc, None

    except Exception as e:
        return None, str(e)


def format_duration(seconds):
    if not seconds:
        return "Bilinmiyor"
    minutes, secs = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


# =====================================================
# 🎵 MÜZİK COG
# =====================================================

class Muzik(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_play_next_callback(self, guild_id, vc, text_channel):
        def play_next(error):
            if error:
                print(f"[HATA] Oynatma hatası: {error}")

            queue = get_queue(guild_id)

            if len(queue) > 0 and vc.is_connected():
                next_song = queue.pop(0)

                try:
                    # Yeni URL al
                    new_url, new_info = search_and_get_audio(next_song['info']['title'])

                    if new_url:
                        audio_url = new_url
                        song_info = new_info
                    else:
                        audio_url = next_song['url']
                        song_info = next_song['info']

                    source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)
                    vc.play(source, after=self.create_play_next_callback(guild_id, vc, text_channel))
                    set_now_playing(guild_id, song_info['title'])

                    embed = discord.Embed(
                        title="🎵 Şimdi Çalıyor",
                        description=f"**{song_info['title']}**",
                        color=discord.Color.green()
                    )
                    if song_info.get('duration'):
                        embed.add_field(name="⏱️ Süre", value=format_duration(song_info['duration']))
                    if song_info.get('thumbnail'):
                        embed.set_thumbnail(url=song_info['thumbnail'])

                    asyncio.run_coroutine_threadsafe(
                        text_channel.send(embed=embed),
                        self.bot.loop
                    )
                except Exception as e:
                    print(f"[HATA] Sonraki şarkı: {e}")
                    clear_now_playing(guild_id)
                    if len(queue) > 0:
                        play_next(None)
            else:
                clear_now_playing(guild_id)

        return play_next

    async def play_song(self, vc, guild_id, audio_url, song_info, text_channel):
        try:
            source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)
            vc.play(source, after=self.create_play_next_callback(guild_id, vc, text_channel))
            set_now_playing(guild_id, song_info['title'])
            return True
        except Exception as e:
            print(f"[HATA] Şarkı çalınamadı: {e}")
            return False

    def create_embed(self, song_info, queue_position=None):
        if queue_position:
            embed = discord.Embed(title="➕ Kuyruğa Eklendi", color=discord.Color.blue())
            embed.add_field(name="📋 Sıra", value=f"#{queue_position}", inline=True)
        else:
            embed = discord.Embed(title="🎵 Şimdi Çalıyor", color=discord.Color.green())

        embed.description = f"**{song_info['title']}**"

        if song_info.get('duration'):
            embed.add_field(name="⏱️ Süre", value=format_duration(song_info['duration']), inline=True)

        if song_info.get('thumbnail'):
            embed.set_thumbnail(url=song_info['thumbnail'])

        return embed

    # =====================================================
    # 🎵 SLASH KOMUTLARI
    # =====================================================

    @app_commands.command(name="play", description="Müzik çal")
    @app_commands.describe(şarkı="Şarkı adı veya YouTube linki")
    async def slash_play(self, interaction: discord.Interaction, şarkı: str):
        # Ses kanalı kontrolü
        if not interaction.user.voice:
            await interaction.response.send_message("❌ Önce bir ses kanalına katıl!", ephemeral=True)
            return

        # Hemen defer et (3 saniye limiti için)
        await interaction.response.defer()

        channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client

        # Ses kanalına bağlan
        vc, error = await ensure_voice_connection(channel, vc)

        if error:
            await interaction.followup.send(f"❌ {error}")
            return

        if not vc:
            await interaction.followup.send("❌ Ses kanalına bağlanılamadı!")
            return

        # Arama mesajı
        await interaction.followup.send(f"🔍 Aranıyor: **{şarkı}**")

        # Şarkı ara
        audio_url, song_info = await asyncio.to_thread(search_and_get_audio, şarkı)

        if not audio_url:
            await interaction.edit_original_response(
                content="❌ Şarkı bulunamadı! YouTube koruması aktif olabilir."
            )
            return

        # Zaten çalıyorsa kuyruğa ekle
        if vc.is_playing() or vc.is_paused():
            queue = get_queue(interaction.guild.id)
            queue.append({'url': audio_url, 'info': song_info})
            embed = self.create_embed(song_info, queue_position=len(queue))
            await interaction.edit_original_response(content=None, embed=embed)
            return

        # Şarkıyı çal
        success = await self.play_song(vc, interaction.guild.id, audio_url, song_info, interaction.channel)

        if success:
            embed = self.create_embed(song_info)
            await interaction.edit_original_response(content=None, embed=embed)
        else:
            await interaction.edit_original_response(content="❌ Şarkı çalınamadı!")

    @app_commands.command(name="join", description="Ses kanalına katıl")
    async def slash_join(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message("❌ Önce bir ses kanalına katıl!", ephemeral=True)
            return

        await interaction.response.defer()

        channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client

        vc, error = await ensure_voice_connection(channel, vc)

        if error:
            await interaction.followup.send(f"❌ {error}")
            return

        await interaction.followup.send(f"🔊 **{channel.name}** kanalına katıldım!")

    @app_commands.command(name="leave", description="Ses kanalından ayrıl")
    async def slash_leave(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc:
            await interaction.response.send_message("❌ Zaten ses kanalında değilim!", ephemeral=True)
            return

        get_queue(interaction.guild.id).clear()
        clear_now_playing(interaction.guild.id)
        await vc.disconnect()
        await interaction.response.send_message("👋 Ses kanalından ayrıldım!")

    @app_commands.command(name="pause", description="Müziği duraklat")
    async def slash_pause(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc or not vc.is_connected():
            await interaction.response.send_message("❌ Bot ses kanalında değil!", ephemeral=True)
            return
        if vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸️ Müzik duraklatıldı!")
        elif vc.is_paused():
            await interaction.response.send_message("❌ Müzik zaten duraklatılmış!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Çalan müzik yok!", ephemeral=True)

    @app_commands.command(name="devam", description="Müziği devam ettir")
    async def slash_devam(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc or not vc.is_connected():
            await interaction.response.send_message("❌ Bot ses kanalında değil!", ephemeral=True)
            return
        if vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶️ Müzik devam ediyor!")
        else:
            await interaction.response.send_message("❌ Duraklatılmış şarkı yok!", ephemeral=True)

    @app_commands.command(name="skip", description="Şarkıyı atla")
    async def slash_skip(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc or not vc.is_connected():
            await interaction.response.send_message("❌ Bot ses kanalında değil!", ephemeral=True)
            return
        if vc.is_playing() or vc.is_paused():
            vc.stop()
            await interaction.response.send_message("⏭️ Şarkı atlandı!")
        else:
            await interaction.response.send_message("❌ Atlanacak şarkı yok!", ephemeral=True)

    @app_commands.command(name="stop", description="Müziği durdur ve kuyruğu temizle")
    async def slash_stop(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc or not vc.is_connected():
            await interaction.response.send_message("❌ Bot ses kanalında değil!", ephemeral=True)
            return
        get_queue(interaction.guild.id).clear()
        clear_now_playing(interaction.guild.id)
        if vc.is_playing() or vc.is_paused():
            vc.stop()
        await interaction.response.send_message("⏹️ Müzik durduruldu!")

    @app_commands.command(name="queue", description="Müzik kuyruğunu göster")
    async def slash_queue(self, interaction: discord.Interaction):
        queue = get_queue(interaction.guild.id)
        current = get_now_playing(interaction.guild.id)

        embed = discord.Embed(title="📋 Müzik Kuyruğu", color=discord.Color.blue())

        if current:
            embed.add_field(name="🎵 Şu An Çalıyor", value=f"**{current}**", inline=False)

        if len(queue) == 0:
            embed.description = "Kuyrukta şarkı yok."
        else:
            text = ""
            for i, song in enumerate(queue[:10]):
                title = song['info']['title'][:40]
                if len(song['info']['title']) > 40:
                    title += "..."
                text += f"**{i+1}.** {title}\n"

            if len(queue) > 10:
                text += f"\n*... ve {len(queue) - 10} şarkı daha*"

            embed.add_field(name="📜 Sıradaki", value=text, inline=False)

        embed.set_footer(text=f"Toplam: {len(queue)} şarkı")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="np", description="Şu an çalan şarkıyı göster")
    async def slash_np(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        current = get_now_playing(interaction.guild.id)

        if not vc or not vc.is_connected():
            await interaction.response.send_message("❌ Bot ses kanalında değil!", ephemeral=True)
            return
        if not current or (not vc.is_playing() and not vc.is_paused()):
            await interaction.response.send_message("❌ Şu an çalan şarkı yok!", ephemeral=True)
            return

        status = "⏸️ Duraklatıldı" if vc.is_paused() else "▶️ Çalıyor"
        embed = discord.Embed(title="🎵 Şu An Çalıyor", color=discord.Color.green())
        embed.description = f"**{current}**"
        embed.add_field(name="Durum", value=status)

        queue = get_queue(interaction.guild.id)
        if len(queue) > 0:
            embed.add_field(name="Sırada", value=f"{len(queue)} şarkı")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="shuffle", description="Kuyruğu karıştır")
    async def slash_shuffle(self, interaction: discord.Interaction):
        queue = get_queue(interaction.guild.id)
        if len(queue) < 2:
            await interaction.response.send_message("❌ Karıştırılacak yeterli şarkı yok!", ephemeral=True)
            return
        random.shuffle(queue)
        await interaction.response.send_message(f"🔀 Kuyruk karıştırıldı! ({len(queue)} şarkı)")

    @app_commands.command(name="qclear", description="Kuyruğu temizle")
    async def slash_qclear(self, interaction: discord.Interaction):
        queue = get_queue(interaction.guild.id)
        count = len(queue)
        queue.clear()
        await interaction.response.send_message(f"🗑️ Kuyruk temizlendi! ({count} şarkı)")

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

        vc, error = await ensure_voice_connection(channel, vc)

        if error:
            await msg.edit(content=f"❌ {error}")
            return

        audio_url, song_info = await asyncio.to_thread(search_and_get_audio, query)

        if not audio_url:
            await msg.edit(content="❌ Şarkı bulunamadı!")
            return

        if vc.is_playing() or vc.is_paused():
            queue = get_queue(ctx.guild.id)
            queue.append({'url': audio_url, 'info': song_info})
            embed = self.create_embed(song_info, queue_position=len(queue))
            await msg.edit(content=None, embed=embed)
            return

        try:
            await msg.delete()
        except:
            pass

        success = await self.play_song(vc, ctx.guild.id, audio_url, song_info, ctx.channel)

        if success:
            embed = self.create_embed(song_info)
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Şarkı çalınamadı!")

    @commands.command(aliases=['katıl', 'gel'])
    async def join(self, ctx):
        if not ctx.author.voice:
            await ctx.send("❌ Önce bir ses kanalına katıl!")
            return

        channel = ctx.author.voice.channel
        vc = ctx.voice_client
        vc, error = await ensure_voice_connection(channel, vc)

        if error:
            await ctx.send(f"❌ {error}")
            return

        await ctx.send(f"🔊 **{channel.name}** kanalına katıldım!")

    @commands.command(aliases=['çık', 'dc'])
    async def leave(self, ctx):
        vc = ctx.voice_client
        if not vc:
            await ctx.send("❌ Zaten ses kanalında değilim!")
            return

        get_queue(ctx.guild.id).clear()
        clear_now_playing(ctx.guild.id)
        await vc.disconnect()
        await ctx.send("👋 Ayrıldım!")

    @commands.command(aliases=['dur'])
    async def pause(self, ctx):
        vc = ctx.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await ctx.send("⏸️ Duraklatıldı!")
        else:
            await ctx.send("❌ Çalan müzik yok!")

    @commands.command(aliases=['devam'])
    async def resume(self, ctx):
        vc = ctx.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await ctx.send("▶️ Devam ediyor!")
        else:
            await ctx.send("❌ Duraklatılmış şarkı yok!")

    @commands.command(aliases=['atla', 's'])
    async def skip(self, ctx):
        vc = ctx.voice_client
        if vc and (vc.is_playing() or vc.is_paused()):
            vc.stop()
            await ctx.send("⏭️ Atlandı!")
        else:
            await ctx.send("❌ Atlanacak şarkı yok!")

    @commands.command()
    async def stop(self, ctx):
        vc = ctx.voice_client
        if vc:
            get_queue(ctx.guild.id).clear()
            clear_now_playing(ctx.guild.id)
            if vc.is_playing() or vc.is_paused():
                vc.stop()
            await ctx.send("⏹️ Durduruldu!")
        else:
            await ctx.send("❌ Bot ses kanalında değil!")

    @commands.command(aliases=['q', 'kuyruk'])
    async def queue(self, ctx):
        queue = get_queue(ctx.guild.id)
        current = get_now_playing(ctx.guild.id)

        embed = discord.Embed(title="📋 Kuyruk", color=discord.Color.blue())

        if current:
            embed.add_field(name="🎵 Çalıyor", value=f"**{current}**", inline=False)

        if len(queue) == 0:
            embed.description = "Kuyruk boş."
        else:
            text = "\n".join([f"**{i+1}.** {s['info']['title'][:40]}" for i, s in enumerate(queue[:10])])
            embed.add_field(name="📜 Sırada", value=text, inline=False)

        await ctx.send(embed=embed)

    @commands.command(aliases=['np', 'şuan'])
    async def nowplaying(self, ctx):
        current = get_now_playing(ctx.guild.id)
        if current:
            await ctx.send(f"🎵 **{current}**")
        else:
            await ctx.send("❌ Şu an çalan şarkı yok!")

    @play.error
    async def play_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Kullanım: `!play <şarkı>`")


async def setup(bot):
    await bot.add_cog(Muzik(bot))
