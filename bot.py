# =====================================================
# 🎵 WOWSY BOT - MÜZİK KOMUTLARI (EJS FİX)
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
# 🍪 ÇEREZ AYARLARINI YÜKLE
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
    # Deno kontrol
    try:
        result = subprocess.run(['deno', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            return 'deno', result.stdout.split('\n')[0]
    except:
        pass
    
    # Node kontrol
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
    print("[UYARI] ⚠️ JavaScript runtime bulunamadı! YouTube çalışmayabilir.")
    print("[UYARI] 💡 Çözüm: curl -fsSL https://deno.land/install.sh | sh")

# =====================================================
# 🎵 MÜZİK FONKSİYONLARI
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


def get_ydl_opts(use_android=False):
    """yt-dlp ayarlarını oluştur"""
    
    if use_android:
        # ✅ Android client - JavaScript bypass
        opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'default_search': 'ytsearch',
            
            # ✅ Android client kullan
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
        # ✅ Normal ayarlar (EJS ile)
        opts = {
            'format': 'bestaudio[ext=webm]/bestaudio[ext=m4a]/bestaudio/best',
            'noplaylist': True,
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
            'default_search': 'ytsearch',
            'source_address': '0.0.0.0',
            'force_ipv4': True,
            'geo_bypass': True,
            'geo_bypass_country': 'US',
            
            'socket_timeout': 30,
            'retries': 10,
            'fragment_retries': 10,
            'extractor_retries': 5,
            'skip_unavailable_fragments': True,
            
            # ✅ EJS - Remote components
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                }
            },
            
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            },
            
            'youtube_include_dash_manifest': True,
            'youtube_include_hls_manifest': True,
        }
        
        # ✅ JavaScript runtime varsa remote components aktif et
        if JS_RUNTIME == 'deno':
            opts['allow_remote_components'] = ['ejs:github']

    # ✅ Çerez ekle
    if COOKIE_FILE and os.path.exists(COOKIE_FILE):
        opts['cookiefile'] = COOKIE_FILE
        print(f"[INFO] ✅ Çerez yüklendi: {COOKIE_FILE}")

    return opts


def search_and_get_audio(query):
    """Şarkı ara ve audio URL + başlık döndür"""
    
    # İlk deneme: Normal ayarlar
    audio_url, song_info = _try_search(query, use_android=False)
    
    if audio_url:
        return audio_url, song_info
    
    # İkinci deneme: Android client
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

            print(f"[INFO] 🔍 Aranıyor: {query}")
            info = ydl.extract_info(query, download=False)

            if 'entries' in info:
                if len(info['entries']) == 0:
                    print("[HATA] ❌ Sonuç bulunamadı")
                    return None, None
                info = info['entries'][0]

            # ✅ Audio URL bul
            audio_url = None
            
            # Direkt URL
            if info.get('url'):
                audio_url = info['url']
                print(f"[INFO] ✅ Direkt URL bulundu")
            
            # Formatlardan seç
            elif 'formats' in info:
                formats = info['formats']
                
                # Sadece audio formatları
                audio_formats = [
                    f for f in formats 
                    if f.get('acodec') != 'none' 
                    and f.get('vcodec') in ['none', None]
                    and f.get('url')
                    and not f.get('format_id', '').startswith('sb')  # Storyboard'ları atla
                ]
                
                if audio_formats:
                    best = max(audio_formats, key=lambda x: x.get('abr') or x.get('tbr') or 0)
                    audio_url = best['url']
                    print(f"[INFO] ✅ Audio format: {best.get('format_id')} ({best.get('abr')}kbps)")
                else:
                    # Video+audio formatları
                    video_formats = [
                        f for f in formats 
                        if f.get('acodec') != 'none' 
                        and f.get('url')
                        and not f.get('format_id', '').startswith('sb')
                    ]
                    
                    if video_formats:
                        best = min(video_formats, key=lambda x: x.get('height') or 9999)
                        audio_url = best['url']
                        print(f"[INFO] ⚠️ Video format kullanılıyor: {best.get('format_id')}")

            if not audio_url:
                print("[HATA] ❌ Oynatılabilir URL bulunamadı")
                return None, None

            title = info.get('title', 'Bilinmeyen Şarkı')
            duration = info.get('duration', 0)
            thumbnail = info.get('thumbnail')
            
            if not thumbnail and info.get('thumbnails'):
                thumbnail = info['thumbnails'][-1].get('url')

            print(f"[INFO] ✅ Başarılı: {title[:50]}...")
            
            return audio_url, {
                'title': title,
                'duration': duration,
                'thumbnail': thumbnail
            }

    except Exception as e:
        print(f"[HATA] ❌ Arama hatası: {e}")
        return None, None


async def ensure_voice_connection(channel, existing_vc=None):
    """Ses kanalına bağlantıyı garanti et"""
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
                    # Yeni URL al (eski URL expire olmuş olabilir)
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
                    print(f"[HATA] Sonraki şarkı çalınamadı: {e}")
                    clear_now_playing(guild_id)
                    
                    # Sıradakini dene
                    if len(queue) > 0:
                        asyncio.run_coroutine_threadsafe(
                            text_channel.send("⚠️ Şarkı çalınamadı, sıradaki deneniyor..."),
                            self.bot.loop
                        )
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

    def create_now_playing_embed(self, song_info, queue_position=None):
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

        if not vc:
            await interaction.followup.send("❌ Ses kanalına bağlanılamadı!")
            return

        searching_msg = await interaction.followup.send(f"🔍 Aranıyor: **{şarkı}**")

        audio_url, song_info = await asyncio.to_thread(search_and_get_audio, şarkı)

        if not audio_url:
            error_msg = (
                "❌ Şarkı bulunamadı!\n\n"
                "**Olası sebepler:**\n"
                "• YouTube bot koruması aktif\n"
                "• JavaScript runtime eksik (Deno/Node.js)\n"
                "• Çerez dosyası geçersiz\n\n"
                "**Çözüm:**\n"
                "```bash\n"
                "curl -fsSL https://deno.land/install.sh | sh\n"
                "```"
            )
            await searching_msg.edit(content=error_msg)
            return

        if vc.is_playing() or vc.is_paused():
            queue = get_queue(interaction.guild.id)
            queue.append({'url': audio_url, 'info': song_info})
            embed = self.create_now_playing_embed(song_info, queue_position=len(queue))
            await searching_msg.edit(content=None, embed=embed)
            return

        success = await self.play_song(vc, interaction.guild.id, audio_url, song_info, interaction.channel)

        if success:
            embed = self.create_now_playing_embed(song_info)
            await searching_msg.edit(content=None, embed=embed)
        else:
            await searching_msg.edit(content="❌ Şarkı çalınamadı!")

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
        await interaction.response.send_message("⏹️ Müzik durduruldu ve kuyruk temizlendi!")

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
                title = song['info']['title'][:45]
                if len(song['info']['title']) > 45:
                    title += "..."
                text += f"**{i+1}.** {title}\n"

            if len(queue) > 10:
                text += f"\n*... ve {len(queue) - 10} şarkı daha*"

            embed.add_field(name="📜 Sıradaki Şarkılar", value=text, inline=False)

        embed.set_footer(text=f"Toplam: {len(queue)} şarkı kuyrukta")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="join", description="Ses kanalına katıl")
    async def slash_join(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message("❌ Önce bir ses kanalına katıl!", ephemeral=True)
            return
        channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client
        vc, error = await ensure_voice_connection(channel, vc)
        if error:
            await interaction.response.send_message(f"❌ {error}", ephemeral=True)
            return
        await interaction.response.send_message(f"🔊 **{channel.name}** kanalına katıldım!")

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

    @app_commands.command(name="qclear", description="Müzik kuyruğunu temizle")
    async def slash_qclear(self, interaction: discord.Interaction):
        queue = get_queue(interaction.guild.id)
        count = len(queue)
        queue.clear()
        await interaction.response.send_message(f"🗑️ Kuyruk temizlendi! ({count} şarkı silindi)")

    # =====================================================
    # 🔧 TEST KOMUTU
    # =====================================================

    @app_commands.command(name="yttest", description="YouTube bağlantısını test et")
    async def slash_yttest(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        results = []
        
        # JavaScript runtime
        if JS_RUNTIME:
            results.append(f"✅ JavaScript Runtime: {JS_RUNTIME} {JS_VERSION}")
        else:
            results.append("❌ JavaScript Runtime: Bulunamadı")
            results.append("   💡 Çözüm: curl -fsSL https://deno.land/install.sh | sh")
        
        # yt-dlp versiyonu
        try:
            results.append(f"✅ yt-dlp: v{yt_dlp.version.__version__}")
        except:
            results.append("⚠️ yt-dlp versiyonu alınamadı")
        
        # Çerez dosyası
        if COOKIE_FILE and os.path.exists(COOKIE_FILE):
            size = os.path.getsize(COOKIE_FILE)
            results.append(f"✅ Çerez dosyası: {size} bytes")
        else:
            results.append("⚠️ Çerez dosyası bulunamadı")
        
        # Test arama
        results.append("\n🔍 Test araması yapılıyor...")
        
        try:
            audio_url, song_info = await asyncio.to_thread(search_and_get_audio, "Rick Astley Never Gonna")
            
            if audio_url:
                results.append(f"✅ Video bulundu: {song_info['title'][:40]}...")
                results.append(f"✅ URL uzunluğu: {len(audio_url)} karakter")
            else:
                results.append("❌ Video bulunamadı")
        except Exception as e:
            results.append(f"❌ Test hatası: {str(e)[:80]}")
        
        embed = discord.Embed(
            title="🔧 YouTube Sistem Testi",
            description="\n".join(results),
            color=discord.Color.orange()
        )
        
        await interaction.followup.send(embed=embed)

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

        if not vc:
            await msg.edit(content="❌ Ses kanalına bağlanılamadı!")
            return

        audio_url, song_info = await asyncio.to_thread(search_and_get_audio, query)

        if not audio_url:
            await msg.edit(content="❌ Şarkı bulunamadı! YouTube koruması aktif olabilir.")
            return

        if vc.is_playing() or vc.is_paused():
            queue = get_queue(ctx.guild.id)
            queue.append({'url': audio_url, 'info': song_info})
            embed = self.create_now_playing_embed(song_info, queue_position=len(queue))
            await msg.edit(content=None, embed=embed)
            return

        try:
            await msg.delete()
        except:
            pass

        success = await self.play_song(vc, ctx.guild.id, audio_url, song_info, ctx.channel)

        if success:
            embed = self.create_now_playing_embed(song_info)
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Şarkı çalınamadı!")

    @commands.command(aliases=['duraklat', 'dur'])
    async def pause(self, ctx):
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            await ctx.send("❌ Bot ses kanalında değil!")
            return
        if vc.is_playing():
            vc.pause()
            await ctx.send("⏸️ Müzik duraklatıldı!")
        else:
            await ctx.send("❌ Çalan müzik yok!")

    @commands.command(aliases=['resume', 'devam'])
    async def devam_et(self, ctx):
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            await ctx.send("❌ Bot ses kanalında değil!")
            return
        if vc.is_paused():
            vc.resume()
            await ctx.send("▶️ Müzik devam ediyor!")
        else:
            await ctx.send("❌ Duraklatılmış şarkı yok!")

    @commands.command(aliases=['atla', 's', 'next'])
    async def skip(self, ctx):
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            await ctx.send("❌ Bot ses kanalında değil!")
            return
        if vc.is_playing() or vc.is_paused():
            vc.stop()
            await ctx.send("⏭️ Şarkı atlandı!")
        else:
            await ctx.send("❌ Atlanacak şarkı yok!")

    @commands.command(aliases=['kapat', 'durdur'])
    async def stop(self, ctx):
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            await ctx.send("❌ Bot ses kanalında değil!")
            return
        get_queue(ctx.guild.id).clear()
        clear_now_playing(ctx.guild.id)
        if vc.is_playing() or vc.is_paused():
            vc.stop()
        await ctx.send("⏹️ Müzik durduruldu ve kuyruk temizlendi!")

    @commands.command(aliases=['çık', 'dc', 'disconnect', 'ayrıl'])
    async def leave(self, ctx):
        vc = ctx.voice_client
        if not vc:
            await ctx.send("❌ Zaten ses kanalında değilim!")
            return
        get_queue(ctx.guild.id).clear()
        clear_now_playing(ctx.guild.id)
        await vc.disconnect()
        await ctx.send("👋 Ses kanalından ayrıldım!")

    @commands.command(aliases=['q', 'kuyruk', 'sıra', 'liste'])
    async def queue(self, ctx):
        queue = get_queue(ctx.guild.id)
        current = get_now_playing(ctx.guild.id)
        embed = discord.Embed(title="📋 Müzik Kuyruğu", color=discord.Color.blue())
        if current:
            embed.add_field(name="🎵 Şu An Çalıyor", value=f"**{current}**", inline=False)
        if len(queue) == 0:
            embed.description = "Kuyrukta şarkı yok."
        else:
            text = ""
            for i, song in enumerate(queue[:10]):
                title = song['info']['title'][:45]
                if len(song['info']['title']) > 45:
                    title += "..."
                text += f"**{i+1}.** {title}\n"
            if len(queue) > 10:
                text += f"\n*... ve {len(queue) - 10} şarkı daha*"
            embed.add_field(name="📜 Sıradaki Şarkılar", value=text, inline=False)
        embed.set_footer(text=f"Toplam: {len(queue)} şarkı kuyrukta")
        await ctx.send(embed=embed)

    @commands.command(aliases=['katıl', 'gel', 'connect'])
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

    @commands.command(aliases=['nowplaying', 'şuan'])
    async def np(self, ctx):
        vc = ctx.voice_client
        current = get_now_playing(ctx.guild.id)
        if not vc or not vc.is_connected():
            await ctx.send("❌ Bot ses kanalında değil!")
            return
        if not current or (not vc.is_playing() and not vc.is_paused()):
            await ctx.send("❌ Şu an çalan şarkı yok!")
            return
        status = "⏸️ Duraklatıldı" if vc.is_paused() else "▶️ Çalıyor"
        embed = discord.Embed(title="🎵 Şu An Çalıyor", color=discord.Color.green())
        embed.description = f"**{current}**"
        embed.add_field(name="Durum", value=status)
        queue = get_queue(ctx.guild.id)
        if len(queue) > 0:
            embed.add_field(name="Sırada", value=f"{len(queue)} şarkı")
        await ctx.send(embed=embed)

    @commands.command(aliases=['karistir', 'karıştır'])
    async def shuffle(self, ctx):
        queue = get_queue(ctx.guild.id)
        if len(queue) < 2:
            await ctx.send("❌ Karıştırılacak yeterli şarkı yok!")
            return
        random.shuffle(queue)
        await ctx.send(f"🔀 Kuyruk karıştırıldı! ({len(queue)} şarkı)")

    @commands.command(aliases=['qclear', 'kuyruktemizle', 'sıfırla'])
    async def clearqueue(self, ctx):
        queue = get_queue(ctx.guild.id)
        count = len(queue)
        queue.clear()
        await ctx.send(f"🗑️ Kuyruk temizlendi! ({count} şarkı silindi)")

    @commands.command(aliases=['test', 'yttest'])
    async def youtube_test(self, ctx):
        """YouTube bağlantısını test et"""
        msg = await ctx.send("🔧 YouTube sistemi test ediliyor...")
        
        results = []
        
        # JS Runtime
        if JS_RUNTIME:
            results.append(f"✅ JS Runtime: {JS_RUNTIME}")
        else:
            results.append("❌ JS Runtime: Yok")
        
        # yt-dlp
        results.append(f"✅ yt-dlp: v{yt_dlp.version.__version__}")
        
        # Test
        results.append("\n🔍 Test aranıyor...")
        audio_url, info = await asyncio.to_thread(search_and_get_audio, "test")
        
        if audio_url:
            results.append(f"✅ Başarılı: {info['title'][:40]}")
        else:
            results.append("❌ Başarısız")
        
        embed = discord.Embed(
            title="🔧 YouTube Test",
            description="\n".join(results),
            color=discord.Color.orange()
        )
        await msg.edit(content=None, embed=embed)

    @play.error
    async def play_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Kullanım: `!play <şarkı adı veya link>`")
        else:
            await ctx.send(f"❌ Bir hata oluştu: {error}")


async def setup(bot):
    await bot.add_cog(Muzik(bot))
