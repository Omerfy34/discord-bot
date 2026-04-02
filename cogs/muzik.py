# =====================================================
# 🎵 WOWSY BOT - MÜZİK KOMUTLARI (OPTİMİZE EDİLMİŞ)
# =====================================================

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random
import yt_dlp
import os

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


def get_ydl_opts():
    """yt-dlp ayarlarını oluştur (çerez desteği ile)"""
    opts = {
        # ✅ Format seçimi - daha esnek (YouTube bot korumasını aşmak için)
        'format': 'ba[ext=webm]/ba[ext=m4a]/ba[ext=mp3]/ba/b[height<=480]/b',
        
        'noplaylist': True,
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
        'default_search': 'ytsearch',
        'source_address': '0.0.0.0',
        'force_ipv4': True,
        'geo_bypass': True,
        'geo_bypass_country': 'US',
        
        # ✅ Zaman aşımı ayarları
        'socket_timeout': 30,
        'retries': 10,
        'fragment_retries': 10,
        'extractor_retries': 5,
        'skip_unavailable_fragments': True,
        
        # ✅ YouTube Premium kalitesini devre dışı bırak
        'format_sort': [
            'quality', 'res', 'fps', 'hdr:12', 
            'codec:vp9.2', 'size', 'br', 'asr', 'proto'
        ],
        'ignore_no_formats_error': True,
        'allow_unplayable_formats': False,
        
        # ✅ Bot korumasını aşmak için gelişmiş headers
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,tr;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
        },
        
        # ✅ Ekstra güvenlik ayarları
        'nocheckcertificate': True,
        'prefer_insecure': False,
        'age_limit': None,
        'extract_flat': False,
        'youtube_include_dash_manifest': False,
        'youtube_include_hls_manifest': False,
    }

    # ✅ Çerez dosyası kontrolü
    if COOKIE_FILE:
        if os.path.exists(COOKIE_FILE):
            opts['cookiefile'] = COOKIE_FILE
            print(f"[INFO] ✅ Çerez dosyası yüklendi: {COOKIE_FILE}")
        else:
            print(f"[UYARI] ❌ Çerez dosyası bulunamadı: {COOKIE_FILE}")
    
    # ✅ Tarayıcı çerezleri (VDS'de çalışmaz genelde)
    elif COOKIE_BROWSER:
        opts['cookiesfrombrowser'] = (COOKIE_BROWSER,)
        print(f"[INFO] ✅ Tarayıcı çerezleri kullanılıyor: {COOKIE_BROWSER}")

    return opts


def search_and_get_audio(query):
    """Şarkı ara ve audio URL + başlık döndür"""
    try:
        ydl_opts = get_ydl_opts()

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

            # ✅ Gelişmiş format seçimi
            audio_url = None
            selected_format = None
            
            # 1. Yöntem: Doğrudan URL varsa kullan
            if info.get('url'):
                audio_url = info['url']
                print(f"[INFO] ✅ Direkt URL bulundu")
            
            # 2. Yöntem: Formatlardan en iyisini seç
            elif 'formats' in info:
                formats = info['formats']
                
                # ✅ Öncelik sırası ile format ara
                # Önce sadece audio formatları
                audio_formats = [
                    f for f in formats 
                    if f.get('vcodec') == 'none' and f.get('acodec') != 'none' and f.get('url')
                ]
                
                if audio_formats:
                    # Bitrate'e göre sırala (en yüksek kalite)
                    best_audio = max(
                        audio_formats, 
                        key=lambda x: (x.get('abr') or 0, x.get('tbr') or 0)
                    )
                    audio_url = best_audio['url']
                    selected_format = best_audio.get('format_id', 'unknown')
                    print(f"[INFO] ✅ Audio format bulundu: {selected_format} (abr: {best_audio.get('abr')})")
                
                else:
                    # ✅ Audio bulunamazsa, video+audio formatı dene
                    combined_formats = [
                        f for f in formats 
                        if f.get('acodec') != 'none' and f.get('url')
                    ]
                    
                    if combined_formats:
                        # En düşük video kalitesini seç (daha az bant genişliği)
                        best_combined = min(
                            combined_formats, 
                            key=lambda x: (x.get('height') or 9999)
                        )
                        audio_url = best_combined['url']
                        selected_format = best_combined.get('format_id', 'unknown')
                        print(f"[INFO] ⚠️ Kombine format kullanılıyor: {selected_format}")
                    
                    else:
                        # ✅ Son çare: herhangi bir format
                        for f in formats:
                            if f.get('url'):
                                audio_url = f['url']
                                selected_format = f.get('format_id', 'unknown')
                                print(f"[INFO] ⚠️ Yedek format kullanılıyor: {selected_format}")
                                break

            # ✅ requested_formats kontrolü (bazı videolar için)
            if not audio_url and 'requested_formats' in info:
                for rf in info['requested_formats']:
                    if rf.get('acodec') != 'none' and rf.get('url'):
                        audio_url = rf['url']
                        print(f"[INFO] ✅ Requested format bulundu")
                        break

            if not audio_url:
                print("[HATA] ❌ Oynatılabilir URL bulunamadı")
                # Debug: Mevcut formatları listele
                if 'formats' in info:
                    print(f"[DEBUG] Mevcut format sayısı: {len(info['formats'])}")
                    for f in info['formats'][:5]:
                        print(f"  - {f.get('format_id')}: vcodec={f.get('vcodec')}, acodec={f.get('acodec')}")
                return None, None

            title = info.get('title', 'Bilinmeyen Şarkı')
            duration = info.get('duration', 0)
            thumbnail = info.get('thumbnail', None)
            
            # ✅ Thumbnail yoksa alternatif dene
            if not thumbnail and info.get('thumbnails'):
                thumbnail = info['thumbnails'][-1].get('url')

            print(f"[INFO] ✅ Başarılı: {title[:50]}...")
            
            return audio_url, {
                'title': title,
                'duration': duration,
                'thumbnail': thumbnail
            }

    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        print(f"[HATA] ❌ YouTube Download Error: {error_msg}")
        
        # ✅ Spesifik hata mesajları
        if "Sign in to confirm" in error_msg:
            print("[ÇÖZÜM] 🔧 YouTube giriş istiyor - cookies.txt dosyasını güncelleyin!")
        elif "Requested format is not available" in error_msg:
            print("[ÇÖZÜM] 🔧 Format mevcut değil - yt-dlp'yi güncelleyin: pip install -U yt-dlp")
        elif "Video unavailable" in error_msg:
            print("[ÇÖZÜM] 🔧 Video mevcut değil veya bölgenizde engellenmiş")
        elif "Private video" in error_msg:
            print("[ÇÖZÜM] 🔧 Video özel")
            
        return None, None
        
    except Exception as e:
        print(f"[HATA] ❌ search_and_get_audio: {e}")
        import traceback
        traceback.print_exc()
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
                
                # ✅ URL'nin hala geçerli olup olmadığını kontrol et
                # YouTube URL'leri kısa sürede expire olabilir
                try:
                    # Yeni URL al (daha güvenilir)
                    new_url, new_info = search_and_get_audio(next_song['info']['title'])
                    
                    if new_url:
                        audio_url = new_url
                        song_info = new_info
                    else:
                        audio_url = next_song['url']
                        song_info = next_song['info']
                    
                    source = discord.FFmpegPCMAudio(
                        audio_url, **FFMPEG_OPTIONS
                    )
                    vc.play(
                        source,
                        after=self.create_play_next_callback(
                            guild_id, vc, text_channel
                        )
                    )

                    set_now_playing(guild_id, song_info['title'])

                    embed = discord.Embed(
                        title="🎵 Şimdi Çalıyor",
                        description=f"**{song_info['title']}**",
                        color=discord.Color.green()
                    )
                    if song_info.get('duration'):
                        embed.add_field(
                            name="⏱️ Süre",
                            value=format_duration(song_info['duration'])
                        )
                    if song_info.get('thumbnail'):
                        embed.set_thumbnail(url=song_info['thumbnail'])

                    asyncio.run_coroutine_threadsafe(
                        text_channel.send(embed=embed),
                        self.bot.loop
                    )
                except Exception as e:
                    print(f"[HATA] Sonraki şarkı çalınamadı: {e}")
                    clear_now_playing(guild_id)
                    
                    # ✅ Hata durumunda sıradaki şarkıya geç
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
            vc.play(
                source,
                after=self.create_play_next_callback(
                    guild_id, vc, text_channel
                )
            )
            set_now_playing(guild_id, song_info['title'])
            return True
        except Exception as e:
            print(f"[HATA] Şarkı çalınamadı: {e}")
            return False

    def create_now_playing_embed(self, song_info, queue_position=None):
        if queue_position:
            embed = discord.Embed(
                title="➕ Kuyruğa Eklendi",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="📋 Sıra",
                value=f"#{queue_position}",
                inline=True
            )
        else:
            embed = discord.Embed(
                title="🎵 Şimdi Çalıyor",
                color=discord.Color.green()
            )

        embed.description = f"**{song_info['title']}**"

        if song_info.get('duration'):
            embed.add_field(
                name="⏱️ Süre",
                value=format_duration(song_info['duration']),
                inline=True
            )

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
            await interaction.response.send_message(
                "❌ Önce bir ses kanalına katıl!",
                ephemeral=True
            )
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

        searching_msg = await interaction.followup.send(
            f"🔍 Aranıyor: **{şarkı}**"
        )

        audio_url, song_info = await asyncio.to_thread(
            search_and_get_audio, şarkı
        )

        if not audio_url:
            await searching_msg.edit(
                content="❌ Şarkı bulunamadı!\n"
                "**Olası sebepler:**\n"
                "• YouTube bot koruması aktif\n"
                "• Çerez dosyası geçersiz/eksik\n"
                "• Video bölgenizde engellenmiş\n"
                "• yt-dlp güncel değil (`pip install -U yt-dlp`)"
            )
            return

        if vc.is_playing() or vc.is_paused():
            queue = get_queue(interaction.guild.id)
            queue.append({'url': audio_url, 'info': song_info})

            embed = self.create_now_playing_embed(
                song_info, queue_position=len(queue)
            )
            await searching_msg.edit(content=None, embed=embed)
            return

        success = await self.play_song(
            vc,
            interaction.guild.id,
            audio_url,
            song_info,
            interaction.channel
        )

        if success:
            embed = self.create_now_playing_embed(song_info)
            await searching_msg.edit(content=None, embed=embed)
        else:
            await searching_msg.edit(content="❌ Şarkı çalınamadı!")

    @app_commands.command(name="pause", description="Müziği duraklat")
    async def slash_pause(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc or not vc.is_connected():
            await interaction.response.send_message(
                "❌ Bot ses kanalında değil!", ephemeral=True
            )
            return
        if vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸️ Müzik duraklatıldı!")
        elif vc.is_paused():
            await interaction.response.send_message(
                "❌ Müzik zaten duraklatılmış!", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ Çalan müzik yok!", ephemeral=True
            )

    @app_commands.command(name="devam", description="Müziği devam ettir")
    async def slash_devam(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc or not vc.is_connected():
            await interaction.response.send_message(
                "❌ Bot ses kanalında değil!", ephemeral=True
            )
            return
        if vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶️ Müzik devam ediyor!")
        else:
            await interaction.response.send_message(
                "❌ Duraklatılmış şarkı yok!", ephemeral=True
            )

    @app_commands.command(name="skip", description="Şarkıyı atla")
    async def slash_skip(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc or not vc.is_connected():
            await interaction.response.send_message(
                "❌ Bot ses kanalında değil!", ephemeral=True
            )
            return
        if vc.is_playing() or vc.is_paused():
            vc.stop()
            await interaction.response.send_message("⏭️ Şarkı atlandı!")
        else:
            await interaction.response.send_message(
                "❌ Atlanacak şarkı yok!", ephemeral=True
            )

    @app_commands.command(
        name="stop", description="Müziği durdur ve kuyruğu temizle"
    )
    async def slash_stop(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc or not vc.is_connected():
            await interaction.response.send_message(
                "❌ Bot ses kanalında değil!", ephemeral=True
            )
            return
        get_queue(interaction.guild.id).clear()
        clear_now_playing(interaction.guild.id)
        if vc.is_playing() or vc.is_paused():
            vc.stop()
        await interaction.response.send_message(
            "⏹️ Müzik durduruldu ve kuyruk temizlendi!"
        )

    @app_commands.command(name="leave", description="Ses kanalından ayrıl")
    async def slash_leave(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc:
            await interaction.response.send_message(
                "❌ Zaten ses kanalında değilim!", ephemeral=True
            )
            return
        get_queue(interaction.guild.id).clear()
        clear_now_playing(interaction.guild.id)
        await vc.disconnect()
        await interaction.response.send_message("👋 Ses kanalından ayrıldım!")

    @app_commands.command(name="queue", description="Müzik kuyruğunu göster")
    async def slash_queue(self, interaction: discord.Interaction):
        queue = get_queue(interaction.guild.id)
        current = get_now_playing(interaction.guild.id)

        embed = discord.Embed(
            title="📋 Müzik Kuyruğu", color=discord.Color.blue()
        )

        if current:
            embed.add_field(
                name="🎵 Şu An Çalıyor",
                value=f"**{current}**",
                inline=False
            )

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

            embed.add_field(
                name="📜 Sıradaki Şarkılar",
                value=text,
                inline=False
            )

        embed.set_footer(text=f"Toplam: {len(queue)} şarkı kuyrukta")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="join", description="Ses kanalına katıl")
    async def slash_join(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message(
                "❌ Önce bir ses kanalına katıl!",
                ephemeral=True
            )
            return
        channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client
        vc, error = await ensure_voice_connection(channel, vc)
        if error:
            await interaction.response.send_message(
                f"❌ {error}", ephemeral=True
            )
            return
        await interaction.response.send_message(
            f"🔊 **{channel.name}** kanalına katıldım!"
        )

    @app_commands.command(
        name="np", description="Şu an çalan şarkıyı göster"
    )
    async def slash_np(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        current = get_now_playing(interaction.guild.id)
        if not vc or not vc.is_connected():
            await interaction.response.send_message(
                "❌ Bot ses kanalında değil!", ephemeral=True
            )
            return
        if not current or (not vc.is_playing() and not vc.is_paused()):
            await interaction.response.send_message(
                "❌ Şu an çalan şarkı yok!", ephemeral=True
            )
            return
        status = "⏸️ Duraklatıldı" if vc.is_paused() else "▶️ Çalıyor"
        embed = discord.Embed(
            title="🎵 Şu An Çalıyor", color=discord.Color.green()
        )
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
            await interaction.response.send_message(
                "❌ Karıştırılacak yeterli şarkı yok!", ephemeral=True
            )
            return
        random.shuffle(queue)
        await interaction.response.send_message(
            f"🔀 Kuyruk karıştırıldı! ({len(queue)} şarkı)"
        )

    @app_commands.command(
        name="qclear", description="Müzik kuyruğunu temizle"
    )
    async def slash_qclear(self, interaction: discord.Interaction):
        queue = get_queue(interaction.guild.id)
        count = len(queue)
        queue.clear()
        await interaction.response.send_message(
            f"🗑️ Kuyruk temizlendi! ({count} şarkı silindi)"
        )

    # =====================================================
    # 🔧 TEST KOMUTU (Debug için)
    # =====================================================

    @app_commands.command(name="yttest", description="YouTube bağlantısını test et")
    async def slash_yttest(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        test_results = []
        
        # 1. Çerez dosyası kontrolü
        if COOKIE_FILE:
            if os.path.exists(COOKIE_FILE):
                file_size = os.path.getsize(COOKIE_FILE)
                test_results.append(f"✅ Çerez dosyası mevcut ({file_size} bytes)")
            else:
                test_results.append(f"❌ Çerez dosyası bulunamadı: {COOKIE_FILE}")
        else:
            test_results.append("⚠️ COOKIE_FILE tanımlanmamış")
        
        # 2. yt-dlp versiyonu
        try:
            test_results.append(f"✅ yt-dlp versiyonu: {yt_dlp.version.__version__}")
        except:
            test_results.append("⚠️ yt-dlp versiyonu alınamadı")
        
        # 3. Test videosu
        test_results.append("\n🔍 Test videosu deneniyor...")
        
        try:
            audio_url, song_info = await asyncio.to_thread(
                search_and_get_audio, "Rick Astley Never Gonna Give You Up"
            )
            
            if audio_url:
                test_results.append(f"✅ Video bulundu: {song_info['title'][:40]}...")
                test_results.append(f"✅ URL uzunluğu: {len(audio_url)} karakter")
            else:
                test_results.append("❌ Video bulunamadı - YouTube bot koruması aktif olabilir")
        except Exception as e:
            test_results.append(f"❌ Hata: {str(e)[:100]}")
        
        embed = discord.Embed(
            title="🔧 YouTube Bağlantı Testi",
            description="\n".join(test_results),
            color=discord.Color.orange()
        )
        
        embed.add_field(
            name="💡 Çözüm Önerileri",
            value=(
                "1. `pip install -U yt-dlp` ile güncelleyin\n"
                "2. cookies.txt dosyasını yeniden oluşturun\n"
                "3. VPN/Proxy kullanmayı deneyin"
            ),
            inline=False
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

        audio_url, song_info = await asyncio.to_thread(
            search_and_get_audio, query
        )

        if not audio_url:
            await msg.edit(
                content="❌ Şarkı bulunamadı!\n"
                "**Olası sebepler:**\n"
                "• YouTube bot koruması aktif\n"
                "• Çerez dosyası geçersiz/eksik\n"
                "• Video bölgenizde engellenmiş"
            )
            return

        if vc.is_playing() or vc.is_paused():
            queue = get_queue(ctx.guild.id)
            queue.append({'url': audio_url, 'info': song_info})
            embed = self.create_now_playing_embed(
                song_info, queue_position=len(queue)
            )
            await msg.edit(content=None, embed=embed)
            return

        try:
            await msg.delete()
        except Exception:
            pass

        success = await self.play_song(
            vc, ctx.guild.id, audio_url, song_info, ctx.channel
        )

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
        embed = discord.Embed(
            title="📋 Müzik Kuyruğu", color=discord.Color.blue()
        )
        if current:
            embed.add_field(
                name="🎵 Şu An Çalıyor",
                value=f"**{current}**",
                inline=False
            )
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
            embed.add_field(
                name="📜 Sıradaki Şarkılar",
                value=text,
                inline=False
            )
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
        embed = discord.Embed(
            title="🎵 Şu An Çalıyor", color=discord.Color.green()
        )
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

    # =====================================================
    # 🔧 PREFIX TEST KOMUTU
    # =====================================================

    @commands.command(aliases=['test', 'yttest'])
    async def youtube_test(self, ctx):
        """YouTube bağlantısını test et"""
        msg = await ctx.send("🔧 YouTube bağlantısı test ediliyor...")
        
        test_results = []
        
        # 1. Çerez dosyası kontrolü
        if COOKIE_FILE:
            if os.path.exists(COOKIE_FILE):
                file_size = os.path.getsize(COOKIE_FILE)
                test_results.append(f"✅ Çerez dosyası mevcut ({file_size} bytes)")
            else:
                test_results.append(f"❌ Çerez dosyası bulunamadı: {COOKIE_FILE}")
        else:
            test_results.append("⚠️ COOKIE_FILE tanımlanmamış")
        
        # 2. yt-dlp versiyonu
        try:
            test_results.append(f"✅ yt-dlp: {yt_dlp.version.__version__}")
        except:
            test_results.append("⚠️ yt-dlp versiyonu alınamadı")
        
        # 3. Test videosu
        test_results.append("\n🔍 Test videosu deneniyor...")
        
        try:
            audio_url, song_info = await asyncio.to_thread(
                search_and_get_audio, "test video"
            )
            
            if audio_url:
                test_results.append(f"✅ Video bulundu!")
                test_results.append(f"✅ Başlık: {song_info['title'][:40]}...")
            else:
                test_results.append("❌ Video bulunamadı")
        except Exception as e:
            test_results.append(f"❌ Hata: {str(e)[:100]}")
        
        embed = discord.Embed(
            title="🔧 YouTube Bağlantı Testi",
            description="\n".join(test_results),
            color=discord.Color.orange()
        )
        
        await msg.edit(content=None, embed=embed)

    @play.error
    async def play_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Kullanım: `!play <şarkı adı veya link>`")
        else:
            await ctx.send(f"❌ Bir hata oluştu: {error}")
            print(f"[HATA] play komutu: {error}")


async def setup(bot):
    await bot.add_cog(Muzik(bot))
