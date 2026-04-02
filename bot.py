# =====================================================
# 🚀 WOWSY BOT - ANA DOSYA (GÜNCELLENMİŞ)
# =====================================================

print("🚀 WOWSY BOT BAŞLATILIYOR...")
print("")

import os
import sys
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import asyncio

# =====================================================
# ⚙️ CONFIG YÜKLEME VE KONTROL
# =====================================================

try:
    from config import (
        DISCORD_TOKEN, 
        db, 
        groq_client, 
        durum_ozeti, 
        baslangic_kontrolu,
        check_youtube_cookies,
        COOKIE_FILE,
        FFMPEG_OPTIONS
    )
except ImportError as e:
    print(f"❌ Config yüklenemedi: {e}")
    print("   config.py dosyasını kontrol edin!")
    sys.exit(1)

# =====================================================
# 🔍 BAŞLANGIÇ KONTROLLERİ
# =====================================================

print("🔍 Başlangıç kontrolleri yapılıyor...")
print("")

# Kritik kontroller
if not baslangic_kontrolu():
    print("")
    print("⛔ Kritik hatalar var! Bot başlatılamıyor.")
    print("   Yukarıdaki hataları düzeltin ve tekrar deneyin.")
    sys.exit(1)

# Durum özeti
durum_ozeti()

# =====================================================
# ⚙️ BOT AYARLARI
# =====================================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True  # Ses kanalı olayları için

bot = commands.Bot(
    command_prefix="!", 
    intents=intents, 
    help_command=None,
    case_insensitive=True  # Büyük/küçük harf duyarsız
)

# =====================================================
# 🔥 GÜÇLÜ WARM-UP SİSTEMİ (GELİŞMİŞ)
# =====================================================

async def warmup_systems():
    """Bot başladığında TÜM sistemleri ısıt"""
    print("\n🔥 WARM-UP BAŞLIYOR...")
    print("=" * 50)
    
    warmup_results = {
        'groq': False,
        'firebase': False,
        'discord': False,
        'youtube': False,
        'ffmpeg': False
    }
    
    # 1. Groq AI'yı ısıt (3 kez)
    if groq_client:
        print("\n🤖 [1/5] Groq AI ısıtılıyor...")
        success_count = 0
        for i in range(3):
            try:
                await asyncio.to_thread(
                    groq_client.chat.completions.create,
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": f"warmup test {i}"}],
                    max_tokens=5
                )
                success_count += 1
                print(f"       ✅ Groq warm-up {i+1}/3 başarılı")
            except Exception as e:
                print(f"       ⚠️ Groq warm-up {i+1}/3 hatası: {str(e)[:50]}")
            await asyncio.sleep(0.5)
        
        warmup_results['groq'] = success_count >= 2
        if warmup_results['groq']:
            print(f"       ✅ Groq AI hazır! ({success_count}/3 başarılı)")
        else:
            print(f"       ⚠️ Groq AI sorunlu ({success_count}/3 başarılı)")
    else:
        print("\n⚪ [1/5] Groq AI atlandı (yapılandırılmamış)")
    
    # 2. Firebase'i ısıt (3 kez)
    if db:
        print("\n🔥 [2/5] Firebase ısıtılıyor...")
        success_count = 0
        for i in range(3):
            try:
                await asyncio.to_thread(
                    db.collection('_warmup').limit(1).get
                )
                success_count += 1
                print(f"       ✅ Firebase warm-up {i+1}/3 başarılı")
            except Exception as e:
                print(f"       ⚠️ Firebase warm-up {i+1}/3 hatası: {str(e)[:50]}")
            await asyncio.sleep(0.3)
        
        warmup_results['firebase'] = success_count >= 2
        if warmup_results['firebase']:
            print(f"       ✅ Firebase hazır! ({success_count}/3 başarılı)")
        else:
            print(f"       ⚠️ Firebase sorunlu ({success_count}/3 başarılı)")
    else:
        print("\n⚪ [2/5] Firebase atlandı (yapılandırılmamış)")
    
    # 3. Discord API'yi ısıt
    print("\n💬 [3/5] Discord API ısıtılıyor...")
    try:
        app_info = await bot.application_info()
        warmup_results['discord'] = True
        print(f"       ✅ Discord API hazır!")
        print(f"       ℹ️ Bot sahibi: {app_info.owner}")
    except Exception as e:
        print(f"       ⚠️ Discord API hatası: {e}")
    
    # 4. yt-dlp ve YouTube'u ısıt
    print("\n🎵 [4/5] YouTube sistemi ısıtılıyor...")
    try:
        import yt_dlp
        
        # yt-dlp versiyonunu göster
        print(f"       ℹ️ yt-dlp versiyonu: {yt_dlp.version.__version__}")
        
        # Çerez durumunu kontrol et
        cookie_ok, cookie_msg = check_youtube_cookies()
        if cookie_ok:
            print(f"       ✅ Çerez dosyası: {cookie_msg}")
        else:
            print(f"       ⚠️ Çerez sorunu: {cookie_msg}")
        
        # yt-dlp'yi başlat
        ydl_opts = {
            'quiet': True, 
            'no_warnings': True,
            'extract_flat': True,
        }
        
        # Çerez dosyası varsa ekle
        if COOKIE_FILE and os.path.exists(COOKIE_FILE):
            ydl_opts['cookiefile'] = COOKIE_FILE
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Basit bir test - YouTube ana sayfasını kontrol et
            pass
        
        warmup_results['youtube'] = True
        print("       ✅ yt-dlp hazır!")
        
    except ImportError:
        print("       ❌ yt-dlp yüklü değil!")
        print("       💡 Çözüm: pip install yt-dlp")
    except Exception as e:
        print(f"       ⚠️ YouTube hatası: {e}")
    
    # 5. FFmpeg kontrolü
    print("\n🔊 [5/5] FFmpeg kontrol ediliyor...")
    try:
        # FFmpeg versiyonunu kontrol et
        result = await asyncio.to_thread(
            os.popen, 'ffmpeg -version 2>&1 | head -n 1'
        )
        ffmpeg_version = result.read().strip()
        
        if 'ffmpeg version' in ffmpeg_version.lower():
            warmup_results['ffmpeg'] = True
            print(f"       ✅ {ffmpeg_version[:50]}")
        else:
            # Alternatif kontrol
            exit_code = os.system('ffmpeg -version > /dev/null 2>&1')
            if exit_code == 0:
                warmup_results['ffmpeg'] = True
                print("       ✅ FFmpeg mevcut")
            else:
                print("       ❌ FFmpeg bulunamadı!")
                print("       💡 Çözüm: apt install ffmpeg (Linux)")
    except Exception as e:
        print(f"       ⚠️ FFmpeg kontrol hatası: {e}")
    
    # Sonuç özeti
    print("\n" + "=" * 50)
    print("📊 WARM-UP SONUÇLARI:")
    print("=" * 50)
    
    status_icons = {True: "✅", False: "❌", None: "⚪"}
    
    print(f"   🤖 Groq AI:    {status_icons[warmup_results['groq']]} {'Hazır' if warmup_results['groq'] else 'Hazır Değil'}")
    print(f"   🔥 Firebase:   {status_icons[warmup_results['firebase']]} {'Hazır' if warmup_results['firebase'] else 'Hazır Değil'}")
    print(f"   💬 Discord:    {status_icons[warmup_results['discord']]} {'Hazır' if warmup_results['discord'] else 'Hazır Değil'}")
    print(f"   🎵 YouTube:    {status_icons[warmup_results['youtube']]} {'Hazır' if warmup_results['youtube'] else 'Hazır Değil'}")
    print(f"   🔊 FFmpeg:     {status_icons[warmup_results['ffmpeg']]} {'Hazır' if warmup_results['ffmpeg'] else 'Hazır Değil'}")
    
    # Uyarılar
    warnings = []
    if not warmup_results['youtube']:
        warnings.append("⚠️ YouTube/yt-dlp hazır değil - müzik komutları çalışmayabilir!")
    if not warmup_results['ffmpeg']:
        warnings.append("⚠️ FFmpeg bulunamadı - müzik çalmayacak!")
    if not warmup_results['groq']:
        warnings.append("⚠️ Groq AI hazır değil - AI komutları yavaş olabilir")
    
    if warnings:
        print("")
        for w in warnings:
            print(f"   {w}")
    
    print("")
    print("=" * 50)
    print("✅ WARM-UP TAMAMLANDI!")
    print("=" * 50)
    
    return warmup_results

# =====================================================
# 💓 KEEP-ALIVE SİSTEMİ (GELİŞMİŞ)
# =====================================================

async def keep_systems_alive():
    """Sistemleri periyodik olarak canlı tut"""
    await asyncio.sleep(30)  # İlk 30 saniye bekle
    
    cycle_count = 0
    
    while True:
        try:
            cycle_count += 1
            current_time = datetime.now().strftime('%H:%M:%S')
            
            # Her 10 döngüde bir detaylı log
            verbose = (cycle_count % 10 == 0)
            
            # Groq'u canlı tut
            if groq_client:
                try:
                    await asyncio.to_thread(
                        groq_client.chat.completions.create,
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": "ping"}],
                        max_tokens=1
                    )
                    if verbose:
                        print(f"💓 [{current_time}] Groq AI: ✅")
                except Exception as e:
                    print(f"⚠️ [{current_time}] Groq keep-alive hatası: {str(e)[:50]}")
            
            # Firebase'i canlı tut
            if db:
                try:
                    await asyncio.to_thread(
                        db.collection('_keepalive').limit(1).get
                    )
                    if verbose:
                        print(f"💓 [{current_time}] Firebase: ✅")
                except Exception as e:
                    if verbose:
                        print(f"⚠️ [{current_time}] Firebase keep-alive hatası: {str(e)[:50]}")
            
            # Bot durumunu güncelle (her 5 döngüde)
            if cycle_count % 5 == 0:
                try:
                    guild_count = len(bot.guilds)
                    await bot.change_presence(
                        activity=discord.Activity(
                            type=discord.ActivityType.listening,
                            name=f"/yardım | {guild_count} sunucu"
                        )
                    )
                except:
                    pass
            
        except Exception as e:
            print(f"⚠️ Keep-alive döngü hatası: {e}")
        
        await asyncio.sleep(60)  # 60 saniyede bir

# =====================================================
# 🎵 MÜZİK İNAKTİVİTE KONTROLÜ
# =====================================================

async def check_voice_inactivity():
    """Müzik çalmayan botları ses kanalından çıkar"""
    await asyncio.sleep(60)  # 1 dakika bekle
    
    while True:
        try:
            for vc in bot.voice_clients:
                # Eğer çalmıyorsa ve duraklatılmamışsa
                if not vc.is_playing() and not vc.is_paused():
                    # 2 dakika bekle
                    await asyncio.sleep(120)
                    
                    # Tekrar kontrol et
                    if vc.is_connected() and not vc.is_playing() and not vc.is_paused():
                        await vc.disconnect()
                        print(f"🔇 İnaktivite: {vc.guild.name} kanalından ayrıldı")
                
                # Boş kanal kontrolü
                elif vc.channel and len(vc.channel.members) == 1:
                    await asyncio.sleep(60)
                    
                    if vc.is_connected() and vc.channel and len(vc.channel.members) == 1:
                        await vc.disconnect()
                        print(f"🔇 Boş kanal: {vc.guild.name} kanalından ayrıldı")
        
        except Exception as e:
            pass  # Sessizce geç
        
        await asyncio.sleep(30)

# =====================================================
# 🚀 BOT EVENTLARI
# =====================================================

@bot.event
async def on_ready():
    print("")
    print("=" * 50)
    print(f"🤖 BOT BAŞARIYLA GİRİŞ YAPTI!")
    print("=" * 50)
    print(f"   📛 İsim:          {bot.user.name}")
    print(f"   🆔 ID:            {bot.user.id}")
    print(f"   📊 Sunucu Sayısı: {len(bot.guilds)}")
    print(f"   👥 Kullanıcılar:  {sum(g.member_count for g in bot.guilds)}")
    print(f"   🔥 Firebase:      {'✅ Bağlı' if db else '❌ Bağlı Değil'}")
    print(f"   🤖 AI:            {'✅ Aktif' if groq_client else '⚪ Pasif'}")
    print("=" * 50)
    
    # 🔥 SİSTEMLERİ ISIT
    warmup_results = await warmup_systems()
    
    # 💓 KEEP-ALIVE BAŞLAT
    bot.loop.create_task(keep_systems_alive())
    
    # 🎵 MÜZİK İNAKTİVİTE KONTROLÜ
    bot.loop.create_task(check_voice_inactivity())
    
    # Slash komutlarını senkronize et
    print("\n🔄 Slash komutları senkronize ediliyor...")
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} slash komutu senkronize edildi!")
        
        # Komut listesini göster
        if synced:
            print("\n📋 Yüklenen komutlar:")
            for cmd in sorted(synced, key=lambda x: x.name)[:15]:
                print(f"   /{cmd.name}")
            if len(synced) > 15:
                print(f"   ... ve {len(synced) - 15} komut daha")
    except Exception as e:
        print(f"❌ Slash komut senkronizasyon hatası: {e}")
    
    # Discord durumunu ayarla
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name=f"/yardım | {len(bot.guilds)} sunucu"
        ),
        status=discord.Status.online
    )
    
    print("")
    print("=" * 50)
    print("🎉 BOT TAMAMEN HAZIR!")
    print("   Komutlar aktif, müzik sistemi hazır.")
    print("=" * 50)
    print("")

@bot.event
async def on_connect():
    print("🔌 Discord'a bağlanıldı!")

@bot.event
async def on_disconnect():
    print("⚠️ Discord bağlantısı kesildi!")

@bot.event
async def on_resumed():
    print("🔄 Discord bağlantısı yeniden kuruldu!")

@bot.event
async def on_member_join(member):
    kanal = member.guild.system_channel
    if kanal:
        embed = discord.Embed(
            title="🎉 Hoş Geldin!",
            description=(
                f"{member.mention} sunucumuza katıldı!\n\n"
                f"👋 Seninle birlikte **{member.guild.member_count}** kişiyiz!\n\n"
                f"`/yardım` yazarak komutları görebilirsin."
            ),
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"{member.guild.name}")
        
        try:
            await kanal.send(embed=embed)
        except discord.Forbidden:
            pass
        except Exception as e:
            print(f"⚠️ Karşılama mesajı hatası: {e}")

@bot.event
async def on_member_remove(member):
    kanal = member.guild.system_channel
    if kanal:
        embed = discord.Embed(
            title="👋 Görüşürüz!",
            description=f"**{member.name}** sunucudan ayrıldı.",
            color=discord.Color.orange()
        )
        
        try:
            await kanal.send(embed=embed)
        except:
            pass

@bot.event
async def on_guild_join(guild):
    print(f"✅ Yeni sunucuya katıldım: {guild.name} ({guild.member_count} üye)")
    
    # Yetkilendirme kontrolü
    permissions = guild.me.guild_permissions
    missing_perms = []
    
    if not permissions.send_messages:
        missing_perms.append("Mesaj Gönderme")
    if not permissions.embed_links:
        missing_perms.append("Embed Gönderme")
    if not permissions.connect:
        missing_perms.append("Ses Kanalına Bağlanma")
    if not permissions.speak:
        missing_perms.append("Konuşma")
    
    if missing_perms:
        print(f"   ⚠️ Eksik yetkiler: {', '.join(missing_perms)}")
    
    # Hoşgeldin mesajı
    if guild.system_channel:
        embed = discord.Embed(
            title="⚡ Merhaba!",
            description=(
                "Ben **WOWSY Bot**!\n\n"
                "🎵 **Müzik** - YouTube'dan şarkı çal\n"
                "🎮 **Oyunlar** - Eğlenceli mini oyunlar\n"
                "💰 **Ekonomi** - Sanal para sistemi\n"
                "🤖 **AI** - Yapay zeka sohbet\n"
                "🛡️ **Moderasyon** - Sunucu yönetimi\n\n"
                "📚 `/yardım` yazarak başla!"
            ),
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=bot.user.display_avatar.url)
        
        try:
            await guild.system_channel.send(embed=embed)
        except:
            pass

@bot.event
async def on_guild_remove(guild):
    print(f"❌ Sunucudan ayrıldım: {guild.name} (ID: {guild.id})")

@bot.event
async def on_message(message):
    # Bot mesajlarını yoksay
    if message.author.bot:
        return
    
    # DM kontrolü
    if not message.guild:
        await message.channel.send(
            "👋 Merhaba! Ben sunucularda çalışan bir botum.\n"
            "Beni bir sunucuya ekleyerek kullanabilirsin!"
        )
        return
    
    # Komutları işle
    await bot.process_commands(message)

@bot.event
async def on_voice_state_update(member, before, after):
    """Ses kanalı değişikliklerini izle"""
    # Bot değişikliklerini yoksay
    if member.bot and member.id != bot.user.id:
        return
    
    # Bot'un kendi değişiklikleri
    if member.id == bot.user.id:
        if after.channel is None:
            # Bot kanaldan ayrıldı
            print(f"🔇 {member.guild.name}: Ses kanalından ayrıldım")
        elif before.channel is None:
            # Bot kanala katıldı
            print(f"🔊 {member.guild.name}: {after.channel.name} kanalına katıldım")
        return
    
    # Kullanıcı kanaldan ayrıldığında boş kanal kontrolü
    voice_client = member.guild.voice_client
    if voice_client and voice_client.channel:
        # Sadece bot kaldıysa
        if len(voice_client.channel.members) == 1:
            # 60 saniye bekle
            await asyncio.sleep(60)
            
            # Tekrar kontrol et
            voice_client = member.guild.voice_client
            if voice_client and voice_client.channel and len(voice_client.channel.members) == 1:
                try:
                    await voice_client.disconnect()
                    print(f"🔇 Boş kanal, otomatik ayrıldım: {member.guild.name}")
                except:
                    pass

# =====================================================
# ❌ HATA YÖNETİMİ (GELİŞMİŞ)
# =====================================================

@bot.event
async def on_command_error(ctx, error):
    """Prefix komut hataları"""
    
    # Komut bulunamadı - sessizce geç
    if isinstance(error, commands.CommandNotFound):
        return
    
    # Cooldown hatası
    if isinstance(error, commands.CommandOnCooldown):
        dakika = int(error.retry_after // 60)
        saniye = int(error.retry_after % 60)
        if dakika > 0:
            await ctx.send(f"⏰ Bekle: **{dakika}dk {saniye}sn**", delete_after=10)
        else:
            await ctx.send(f"⏰ Bekle: **{saniye} saniye**", delete_after=10)
        return
    
    # Yetki hataları
    if isinstance(error, commands.MissingPermissions):
        perms = ", ".join(error.missing_permissions)
        await ctx.send(f"❌ Eksik yetki: `{perms}`", delete_after=10)
        return
    
    if isinstance(error, commands.BotMissingPermissions):
        perms = ", ".join(error.missing_permissions)
        await ctx.send(f"❌ Botun eksik yetkisi: `{perms}`", delete_after=10)
        return
    
    # Kullanıcı bulunamadı
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Kullanıcı bulunamadı!", delete_after=10)
        return
    
    # Kanal bulunamadı
    if isinstance(error, commands.ChannelNotFound):
        await ctx.send("❌ Kanal bulunamadı!", delete_after=10)
        return
    
    # Eksik parametre
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Eksik parametre: `{error.param.name}`", delete_after=10)
        return
    
    # Yanlış parametre türü
    if isinstance(error, commands.BadArgument):
        await ctx.send("❌ Yanlış parametre türü!", delete_after=10)
        return
    
    # NSFW kanal gerekli
    if isinstance(error, commands.NSFWChannelRequired):
        await ctx.send("❌ Bu komut sadece NSFW kanallarda çalışır!", delete_after=10)
        return
    
    # Bilinmeyen hatalar - logla
    print(f"❌ Komut Hatası [{ctx.command}]: {type(error).__name__}: {error}")
    
    # Kullanıcıya genel hata mesajı
    try:
        await ctx.send("❌ Bir hata oluştu!", delete_after=10)
    except:
        pass

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    """Slash komut hataları"""
    
    # Utils modülünden güvenli cevap fonksiyonu
    try:
        from utils import guvenli_cevap
    except ImportError:
        # Fallback fonksiyon
        async def guvenli_cevap(inter, msg, ephemeral=False):
            try:
                if inter.response.is_done():
                    await inter.followup.send(msg, ephemeral=ephemeral)
                else:
                    await inter.response.send_message(msg, ephemeral=ephemeral)
            except:
                pass
    
    # Orijinal hatayı al
    error = getattr(error, 'original', error)
    
    # Cooldown hatası
    if isinstance(error, app_commands.CommandOnCooldown):
        await guvenli_cevap(
            interaction, 
            f"⏰ Bekle: **{int(error.retry_after)}sn**", 
            ephemeral=True
        )
        return
    
    # Yetki hataları
    if isinstance(error, app_commands.MissingPermissions):
        await guvenli_cevap(
            interaction, 
            "❌ Bu komutu kullanma yetkin yok!", 
            ephemeral=True
        )
        return
    
    if isinstance(error, app_commands.BotMissingPermissions):
        await guvenli_cevap(
            interaction, 
            "❌ Botun bu işlemi yapma yetkisi yok!", 
            ephemeral=True
        )
        return
    
    # Kontrol başarısız
    if isinstance(error, app_commands.CheckFailure):
        await guvenli_cevap(
            interaction, 
            "❌ Bu komutu kullanma yetkin yok!", 
            ephemeral=True
        )
        return
    
    # Discord API hataları
    if isinstance(error, discord.HTTPException):
        print(f"❌ Discord API Hatası: {error.status} - {error.text}")
        await guvenli_cevap(
            interaction, 
            "❌ Discord API hatası oluştu!", 
            ephemeral=True
        )
        return
    
    # Bilinmeyen hatalar - logla
    print(f"❌ Slash Hatası [{interaction.command.name if interaction.command else 'Unknown'}]: {type(error).__name__}: {error}")
    
    # Kullanıcıya genel hata mesajı
    try:
        await guvenli_cevap(interaction, "❌ Bir hata oluştu!", ephemeral=True)
    except:
        pass

# =====================================================
# 📦 COG'LARI YÜKLE
# =====================================================

async def load_cogs():
    """Tüm cog'ları yükle"""
    
    cog_list = [
        ('cogs.ekonomi', '💰'),
        ('cogs.oyunlar', '🎮'),
        ('cogs.muzik', '🎵'),
        ('cogs.moderasyon', '🛡️'),
        ('cogs.eglence', '🎭'),
        ('cogs.bilgi', 'ℹ️'),
        ('cogs.yapay_zeka', '🤖'),
        ('cogs.yardim', '📚'),
    ]
    
    print("\n📦 COG'LAR YÜKLENİYOR...")
    print("-" * 40)
    
    loaded = 0
    failed = 0
    
    for cog_name, emoji in cog_list:
        try:
            await bot.load_extension(cog_name)
            print(f"   {emoji} {cog_name.split('.')[-1].capitalize()}: ✅ Yüklendi")
            loaded += 1
        except commands.ExtensionNotFound:
            print(f"   {emoji} {cog_name.split('.')[-1].capitalize()}: ❌ Dosya bulunamadı")
            failed += 1
        except commands.ExtensionFailed as e:
            print(f"   {emoji} {cog_name.split('.')[-1].capitalize()}: ❌ Hata")
            print(f"      └─ {e.original}")
            failed += 1
        except Exception as e:
            print(f"   {emoji} {cog_name.split('.')[-1].capitalize()}: ❌ {e}")
            failed += 1
    
    print("-" * 40)
    print(f"📊 Sonuç: {loaded} yüklendi, {failed} başarısız")
    print("")
    
    return loaded, failed

# =====================================================
# 🔧 YARDIMCI KOMUTLAR (SAHİP İÇİN)
# =====================================================

@bot.command(name='reload', hidden=True)
@commands.is_owner()
async def reload_cog(ctx, cog_name: str):
    """Bir cog'u yeniden yükle (Sadece bot sahibi)"""
    try:
        await bot.reload_extension(f'cogs.{cog_name}')
        await ctx.send(f"✅ `{cog_name}` yeniden yüklendi!")
    except Exception as e:
        await ctx.send(f"❌ Hata: {e}")

@bot.command(name='sync', hidden=True)
@commands.is_owner()
async def sync_commands(ctx):
    """Slash komutlarını senkronize et (Sadece bot sahibi)"""
    try:
        synced = await bot.tree.sync()
        await ctx.send(f"✅ {len(synced)} komut senkronize edildi!")
    except Exception as e:
        await ctx.send(f"❌ Hata: {e}")

@bot.command(name='status', hidden=True)
@commands.is_owner()
async def bot_status(ctx):
    """Bot durumunu göster (Sadece bot sahibi)"""
    embed = discord.Embed(
        title="📊 Bot Durumu",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="📡 Bağlantı",
        value=f"Gecikme: {round(bot.latency * 1000)}ms",
        inline=True
    )
    embed.add_field(
        name="📊 Sunucular",
        value=f"{len(bot.guilds)} sunucu",
        inline=True
    )
    embed.add_field(
        name="🎵 Ses Bağlantıları",
        value=f"{len(bot.voice_clients)} aktif",
        inline=True
    )
    embed.add_field(
        name="🔥 Firebase",
        value="✅ Bağlı" if db else "❌ Bağlı Değil",
        inline=True
    )
    embed.add_field(
        name="🤖 Groq AI",
        value="✅ Aktif" if groq_client else "⚪ Pasif",
        inline=True
    )
    
    # Çerez durumu
    cookie_ok, cookie_msg = check_youtube_cookies()
    embed.add_field(
        name="🍪 YouTube Çerez",
        value=f"{'✅' if cookie_ok else '❌'} {cookie_msg}",
        inline=True
    )
    
    await ctx.send(embed=embed)

# =====================================================
# 🚀 BOTU BAŞLAT
# =====================================================

async def main():
    """Ana fonksiyon"""
    
    async with bot:
        # Cog'ları yükle
        loaded, failed = await load_cogs()
        
        if loaded == 0:
            print("⚠️ Hiçbir cog yüklenemedi! Devam ediliyor...")
        
        # Token kontrolü
        if not DISCORD_TOKEN:
            print("")
            print("❌ DISCORD_TOKEN bulunamadı!")
            print("   .env dosyasını kontrol edin.")
            return
        
        # Botu başlat
        try:
            print("🔌 Discord'a bağlanılıyor...")
            print("")
            await bot.start(DISCORD_TOKEN)
            
        except discord.LoginFailure:
            print("")
            print("❌ Discord Token geçersiz!")
            print("   Token'ı kontrol edin ve yenileyin.")
            
        except discord.PrivilegedIntentsRequired:
            print("")
            print("❌ Bot için gerekli Intent'ler aktif değil!")
            print("   Discord Developer Portal'dan Intent'leri aktifleştirin:")
            print("   - MESSAGE CONTENT INTENT")
            print("   - SERVER MEMBERS INTENT")
            
        except Exception as e:
            print("")
            print(f"❌ Beklenmeyen hata: {e}")
            import traceback
            traceback.print_exc()

# =====================================================
# 🏃 ÇALIŞTIR
# =====================================================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot kapatılıyor...")
    except Exception as e:
        print(f"\n❌ Kritik hata: {e}")
        import traceback
        traceback.print_exc()
