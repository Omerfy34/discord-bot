# =====================================================
# 🚀 WOWSY BOT - ANA DOSYA
# =====================================================

import os
import sys
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import asyncio
import traceback

print("")
print("🚀 WOWSY BOT BAŞLATILIYOR...")
print("")

# =====================================================
# ⚙️ CONFIG YÜKLEME
# =====================================================

try:
    from config import (
        DISCORD_TOKEN,
        db,
        groq_client,
        durum_ozeti,
        baslangic_kontrolu,
        check_youtube_cookies,
        COOKIE_FILE
    )
    print("✅ Config yüklendi!")
except ImportError as e:
    print(f"❌ Config yüklenemedi: {e}")
    traceback.print_exc()
    sys.exit(1)

# =====================================================
# ⚙️ BOT AYARLARI
# =====================================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None,
    case_insensitive=True
)

# =====================================================
# 🔥 WARM-UP SİSTEMİ
# =====================================================

async def warmup_systems():
    """Sistemleri ısıt - ilk komutların hızlı çalışması için"""
    print("")
    print("🔥 WARM-UP BAŞLIYOR...")
    print("-" * 40)

    # 1. Groq AI
    if groq_client:
        print("   🤖 Groq AI ısıtılıyor...")
        for i in range(2):
            try:
                await asyncio.to_thread(
                    groq_client.chat.completions.create,
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": f"warmup {i}"}],
                    max_tokens=5
                )
                await asyncio.sleep(0.3)
            except Exception as e:
                print(f"      ⚠️ Deneme {i+1} hatası: {str(e)[:30]}")
        print("   ✅ Groq AI hazır!")
    else:
        print("   ⚪ Groq AI atlandı (yapılandırılmamış)")

    # 2. Firebase
    if db:
        print("   🔥 Firebase ısıtılıyor...")
        try:
            await asyncio.to_thread(db.collection('_warmup').limit(1).get)
            print("   ✅ Firebase hazır!")
        except Exception as e:
            print(f"   ⚠️ Firebase hatası: {str(e)[:30]}")
    else:
        print("   ⚪ Firebase atlandı (yapılandırılmamış)")

    # 3. YouTube / yt-dlp
    print("   🎵 YouTube kontrol ediliyor...")
    try:
        import yt_dlp
        print(f"   ✅ yt-dlp v{yt_dlp.version.__version__}")

        # Çerez kontrolü
        cookie_ok, cookie_msg = check_youtube_cookies()
        if cookie_ok:
            print(f"   ✅ Çerezler: {cookie_msg}")
        else:
            print(f"   ⚠️ Çerezler: {cookie_msg}")
    except Exception as e:
        print(f"   ⚠️ yt-dlp hatası: {e}")

    # 4. Deno kontrolü
    print("   🦕 Deno kontrol ediliyor...")
    try:
        import subprocess
        result = subprocess.run(['deno', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"   ✅ {version}")
        else:
            print("   ⚠️ Deno çalışmıyor")
    except FileNotFoundError:
        print("   ⚠️ Deno yüklü değil (YouTube çalışmayabilir)")
    except Exception as e:
        print(f"   ⚠️ Deno hatası: {e}")

    print("-" * 40)
    print("✅ WARM-UP TAMAMLANDI!")
    print("")

# =====================================================
# 💓 KEEP-ALIVE SİSTEMİ
# =====================================================

async def keep_systems_alive():
    """Sistemleri periyodik olarak canlı tut"""
    await asyncio.sleep(60)

    cycle = 0
    while True:
        try:
            cycle += 1

            # Groq
            if groq_client:
                try:
                    await asyncio.to_thread(
                        groq_client.chat.completions.create,
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": "ping"}],
                        max_tokens=1
                    )
                except:
                    pass

            # Firebase
            if db:
                try:
                    await asyncio.to_thread(db.collection('_keepalive').limit(1).get)
                except:
                    pass

            # Her 5 döngüde durum güncelle
            if cycle % 5 == 0:
                try:
                    await bot.change_presence(
                        activity=discord.Activity(
                            type=discord.ActivityType.listening,
                            name=f"/yardım | {len(bot.guilds)} sunucu"
                        )
                    )
                except:
                    pass

            # Her 10 döngüde log
            if cycle % 10 == 0:
                current_time = datetime.now().strftime('%H:%M:%S')
                print(f"💓 [{current_time}] Aktif - {len(bot.guilds)} sunucu, {len(bot.voice_clients)} ses")

        except Exception as e:
            print(f"⚠️ Keep-alive hatası: {e}")

        await asyncio.sleep(60)

# =====================================================
# 🎵 MÜZİK İNAKTİVİTE KONTROLÜ
# =====================================================

async def check_voice_inactivity():
    """Boş ses kanallarından çık"""
    await asyncio.sleep(120)

    while True:
        try:
            for vc in bot.voice_clients:
                # Boş kanal kontrolü
                if vc.channel and len(vc.channel.members) == 1:
                    try:
                        await vc.disconnect()
                        print(f"🔇 Boş kanal: {vc.guild.name}")
                    except:
                        pass

                # İnaktivite kontrolü (çalmıyor ve duraklatılmamış)
                elif not vc.is_playing() and not vc.is_paused():
                    await asyncio.sleep(120)
                    if vc.is_connected() and not vc.is_playing() and not vc.is_paused():
                        try:
                            await vc.disconnect()
                            print(f"🔇 İnaktivite: {vc.guild.name}")
                        except:
                            pass
        except:
            pass

        await asyncio.sleep(60)

# =====================================================
# 🚀 BOT EVENTLARI
# =====================================================

@bot.event
async def on_ready():
    print("")
    print("=" * 50)
    print("✅ BOT BAŞARIYLA GİRİŞ YAPTI!")
    print("=" * 50)
    print(f"   📛 İsim:      {bot.user.name}")
    print(f"   🆔 ID:        {bot.user.id}")
    print(f"   📊 Sunucular: {len(bot.guilds)}")
    print(f"   👥 Kullanıcı: {sum(g.member_count for g in bot.guilds)}")
    print(f"   🔥 Firebase:  {'✅ Bağlı' if db else '⚪ Pasif'}")
    print(f"   🤖 Groq AI:   {'✅ Aktif' if groq_client else '⚪ Pasif'}")
    print("=" * 50)

    # Sunucu listesi
    if bot.guilds:
        print("")
        print("📋 Sunucular:")
        for guild in bot.guilds[:10]:
            print(f"   • {guild.name} ({guild.member_count} üye)")
        if len(bot.guilds) > 10:
            print(f"   ... ve {len(bot.guilds) - 10} sunucu daha")

    # Warm-up
    await warmup_systems()

    # Background task'ları başlat
    bot.loop.create_task(keep_systems_alive())
    bot.loop.create_task(check_voice_inactivity())

    # Slash komutları senkronize et
    print("🔄 Slash komutları senkronize ediliyor...")
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} slash komutu senkronize edildi!")

        # Komut listesi
        if synced:
            print("")
            print("📋 Komutlar:")
            for cmd in sorted(synced, key=lambda x: x.name)[:15]:
                print(f"   /{cmd.name}")
            if len(synced) > 15:
                print(f"   ... ve {len(synced) - 15} komut daha")
    except Exception as e:
        print(f"❌ Slash komut hatası: {e}")

    # Durum ayarla
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
    print("   Tüm komutlar aktif.")
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
    print("🔄 Bağlantı yeniden kuruldu!")

@bot.event
async def on_member_join(member):
    """Yeni üye karşılama"""
    kanal = member.guild.system_channel
    if kanal:
        embed = discord.Embed(
            title="🎉 Hoş Geldin!",
            description=(
                f"{member.mention} sunucumuza katıldı!\n\n"
                f"👋 Seninle birlikte **{member.guild.member_count}** kişiyiz!\n"
                f"`/yardım` yazarak komutları görebilirsin."
            ),
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=member.guild.name)

        try:
            await kanal.send(embed=embed)
        except discord.Forbidden:
            pass
        except Exception as e:
            print(f"⚠️ Karşılama hatası: {e}")

@bot.event
async def on_member_remove(member):
    """Üye ayrıldığında"""
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
    """Yeni sunucuya katılınca"""
    print(f"✅ Yeni sunucu: {guild.name} ({guild.member_count} üye)")

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
    """Sunucudan ayrılınca"""
    print(f"❌ Sunucudan ayrıldım: {guild.name} (ID: {guild.id})")

@bot.event
async def on_message(message):
    """Mesaj geldiğinde"""
    if message.author.bot:
        return
    
    # Prefix komutları işle
    await bot.process_commands(message)

@bot.event
async def on_voice_state_update(member, before, after):
    """Ses kanalı değişikliklerini izle"""
    # Bot kendi değişiklikleri
    if member.id == bot.user.id:
        return

    # Kullanıcı kanaldan ayrıldığında boş kanal kontrolü
    voice_client = member.guild.voice_client
    if voice_client and voice_client.channel:
        # Sadece bot kaldıysa
        if len(voice_client.channel.members) == 1:
            await asyncio.sleep(30)

            # Tekrar kontrol et
            voice_client = member.guild.voice_client
            if voice_client and voice_client.channel and len(voice_client.channel.members) == 1:
                try:
                    await voice_client.disconnect()
                    print(f"🔇 Boş kanal, ayrıldım: {member.guild.name}")
                except:
                    pass

# =====================================================
# ❌ HATA YÖNETİMİ - SLASH KOMUTLAR
# =====================================================

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    """Slash komut hataları - SADECE LOGLA, MESAJ GÖNDERME"""

    # Orijinal hatayı al
    error = getattr(error, 'original', error)

    # Discord hataları - sessizce geç
    if isinstance(error, discord.NotFound):
        return

    if isinstance(error, discord.HTTPException):
        return

    # Cooldown - sadece bu durumda mesaj gönder
    if isinstance(error, app_commands.CommandOnCooldown):
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"⏰ Bekle: **{int(error.retry_after)}sn**",
                    ephemeral=True
                )
        except:
            pass
        return

    # Yetki hatası
    if isinstance(error, app_commands.MissingPermissions):
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Bu komutu kullanma yetkin yok!",
                    ephemeral=True
                )
        except:
            pass
        return

    # Diğer hatalar - SADECE LOGLA, MESAJ GÖNDERME (çift mesaj sorununu önler)
    cmd_name = interaction.command.name if interaction.command else "Unknown"
    print(f"❌ Slash Hatası [{cmd_name}]: {type(error).__name__}: {error}")

# =====================================================
# 📦 COG'LARI YÜKLE
# =====================================================

async def load_cogs():
    """Tüm cog'ları yükle"""

    cog_list = [
        ('cogs.ekonomi', '💰 Ekonomi'),
        ('cogs.oyunlar', '🎮 Oyunlar'),
        ('cogs.muzik', '🎵 Müzik'),
        ('cogs.moderasyon', '🛡️ Moderasyon'),
        ('cogs.eglence', '🎭 Eğlence'),
        ('cogs.bilgi', 'ℹ️ Bilgi'),
        ('cogs.yapay_zeka', '🤖 Yapay Zeka'),
        ('cogs.yardim', '📚 Yardım'),
        ('cogs.patron', '👑 Patron'),
    ]

    print("")
    print("📦 COG'LAR YÜKLENİYOR...")
    print("-" * 40)

    loaded = 0
    failed = 0

    for cog_path, cog_name in cog_list:
        try:
            await bot.load_extension(cog_path)
            print(f"   ✅ {cog_name}")
            loaded += 1
        except commands.ExtensionNotFound:
            print(f"   ❌ {cog_name}: Dosya bulunamadı")
            failed += 1
        except commands.ExtensionFailed as e:
            print(f"   ❌ {cog_name}: {e.original}")
            failed += 1
        except Exception as e:
            print(f"   ❌ {cog_name}: {e}")
            failed += 1

    print("-" * 40)
    print(f"📊 Sonuç: {loaded} yüklendi, {failed} başarısız")

    return loaded, failed

# =====================================================
# 🚀 ANA FONKSİYON
# =====================================================

async def main():
    """Ana fonksiyon"""

    print("📋 Başlangıç kontrolleri yapılıyor...")

    # Kontroller
    if not baslangic_kontrolu():
        print("")
        print("⛔ Kritik hatalar var! Bot başlatılamıyor.")
        return

    print("✅ Kontroller başarılı!")

    # Durum özeti
    durum_ozeti()

    # Bot başlat
    async with bot:
        # Cog'ları yükle
        loaded, failed = await load_cogs()

        if loaded == 0:
            print("")
            print("⚠️ Hiçbir cog yüklenemedi!")

        # Token kontrolü
        if not DISCORD_TOKEN:
            print("")
            print("❌ DISCORD_TOKEN bulunamadı!")
            print("   .env dosyasını kontrol edin.")
            return

        # Discord'a bağlan
        try:
            print("")
            print("🔌 Discord'a bağlanılıyor...")
            print("")
            await bot.start(DISCORD_TOKEN)

        except discord.LoginFailure:
            print("")
            print("❌ Discord Token geçersiz!")
            print("   Discord Developer Portal'dan yeni token alın.")

        except discord.PrivilegedIntentsRequired:
            print("")
            print("❌ Intent'ler aktif değil!")
            print("   Discord Developer Portal'dan aktifleştirin:")
            print("   - MESSAGE CONTENT INTENT")
            print("   - SERVER MEMBERS INTENT")

        except Exception as e:
            print("")
            print(f"❌ Bağlantı hatası: {type(e).__name__}: {e}")
            traceback.print_exc()

# =====================================================
# 🏃 ÇALIŞTIR
# =====================================================

if __name__ == "__main__":
    try:
        print("🔧 Asyncio başlatılıyor...")
        print("")
        asyncio.run(main())
        print("")
        print("✅ Bot düzgün şekilde kapandı")

    except KeyboardInterrupt:
        print("")
        print("👋 Bot kapatılıyor (Ctrl+C)...")

    except SystemExit as e:
        if e.code and e.code != 0:
            print(f"⚠️ Sistem çıkışı (kod: {e.code})")

    except Exception as e:
        print("")
        print("=" * 60)
        print("❌ KRİTİK HATA:")
        print("=" * 60)
        print(f"   Tip: {type(e).__name__}")
        print(f"   Mesaj: {e}")
        print("")
        print("📋 Stack Trace:")
        traceback.print_exc()
        print("")
        print("💡 Olası çözümler:")
        print("   1. .env dosyasını kontrol edin")
        print("   2. Discord token'ı yenileyin")
        print("   3. pip install -U discord.py")
        print("=" * 60)
        sys.exit(1)
