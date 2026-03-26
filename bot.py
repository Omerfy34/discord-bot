# =====================================================
# 🚀 WOWSY BOT - ANA DOSYA
# =====================================================

print("🚀 WOWSY BOT BAŞLATILIYOR...")

import os
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
from datetime import datetime
import asyncio

from config import DISCORD_TOKEN, db, groq_client, durum_ozeti

# =====================================================
# 🌐 FLASK WEB SUNUCU
# =====================================================

flask_app = Flask('')

@flask_app.route('/')
def home():
    uptime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>⚡ WOWSY Bot</title>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="30">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            .container {{
                text-align: center;
                padding: 40px;
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            }}
            h1 {{
                font-size: 3.5em;
                margin-bottom: 20px;
                animation: pulse 2s infinite;
            }}
            @keyframes pulse {{
                0%, 100% {{ text-shadow: 0 0 20px #ffd700, 0 0 40px #ffd700; }}
                50% {{ text-shadow: 0 0 40px #ff6b6b, 0 0 80px #ff6b6b; }}
            }}
            .status {{
                display: inline-block;
                padding: 10px 30px;
                background: linear-gradient(90deg, #00c853, #00e676);
                border-radius: 50px;
                font-weight: bold;
                margin: 10px 0;
            }}
            .info {{ margin-top: 20px; opacity: 0.9; }}
            .emoji {{ font-size: 1.3em; margin: 5px 0; }}
            .invite-btn {{
                display: inline-block;
                margin-top: 20px;
                padding: 12px 30px;
                background: linear-gradient(135deg, #5865F2, #7289DA);
                color: white;
                text-decoration: none;
                border-radius: 10px;
                font-weight: bold;
                transition: transform 0.3s;
            }}
            .invite-btn:hover {{ transform: scale(1.05); }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚡ WOWSY BOT ⚡</h1>
            <div class="status">✅ AKTİF VE ÇALIŞIYOR</div>
            <div class="info">
                <p class="emoji">🔥 Firebase {'Bağlı' if db else 'Bağlı Değil'}</p>
                <p class="emoji">🎮 60+ Komut Hazır</p>
                <p class="emoji">🚀 7/24 Online</p>
                <p style="margin-top: 15px; font-size: 0.9em;">
                    Son güncelleme: {uptime}
                </p>
            </div>
            <a href="https://discord.com/oauth2/authorize?client_id=1485291664502427708" target="_blank" class="invite-btn">
                🚀 Sunucuna Ekle
            </a>
        </div>
    </body>
    </html>
    """

@flask_app.route('/health')
def health():
    return "OK", 200

def run_flask():
    flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# =====================================================
# ⚙️ BOT AYARLARI
# =====================================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# =====================================================
# 🚀 BOT EVENTLARI
# =====================================================

@bot.event
async def on_ready():
    print("=" * 50)
    print(f"✅ BOT AKTİF: {bot.user.name}")
    print(f"📊 Sunucu Sayısı: {len(bot.guilds)}")
    print(f"🔥 Firebase: {'Bağlı' if db else 'Bağlı Değil'}")
    print(f"🤖 AI: {'Aktif' if groq_client else 'Pasif'}")
    print("=" * 50)
    
    await bot.change_presence(activity=discord.Game(name="/yardım | ⚡ WOWSY"))
    
    # Slash komutlarını senkronize et
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} slash komutu senkronize edildi!")
    except Exception as e:
        print(f"❌ Slash komut hatası: {e}")

@bot.event
async def on_member_join(member):
    kanal = member.guild.system_channel
    if kanal:
        embed = discord.Embed(
            title="🎉 Hoş Geldin!",
            description=f"{member.mention} sunucumuza katıldı!\n\n`/yardım` yazarak komutları görebilirsin.",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        try:
            await kanal.send(embed=embed)
        except:
            pass

@bot.event
async def on_guild_join(guild):
    print(f"✅ Yeni sunucuya katıldım: {guild.name}")
    if guild.system_channel:
        embed = discord.Embed(
            title="⚡ Merhaba!",
            description="Ben **WOWSY Bot**!\n\n📚 `/yardım` yazarak başla!\n🎮 Oyunlar, müzik, moderasyon ve daha fazlası!",
            color=discord.Color.gold()
        )
        try:
            await guild.system_channel.send(embed=embed)
        except:
            pass

@bot.event
async def on_guild_remove(guild):
    print(f"❌ Sunucudan ayrıldım: {guild.name} (ID: {guild.id})")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)

@bot.event
async def on_voice_state_update(member, before, after):
    """Boş ses kanalından otomatik ayrıl"""
    if member.bot:
        return
    
    voice_client = member.guild.voice_client
    if voice_client is None:
        return
    
    if voice_client.channel and len(voice_client.channel.members) == 1:
        await asyncio.sleep(60)
        
        # Tekrar kontrol et
        voice_client = member.guild.voice_client
        if voice_client and voice_client.channel and len(voice_client.channel.members) == 1:
            await voice_client.disconnect()
            print(f"🔇 Boş kanal, otomatik ayrıldım: {member.guild.name}")

# =====================================================
# ❌ HATA YÖNETİMİ
# =====================================================

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    
    if isinstance(error, commands.CommandOnCooldown):
        dakika = int(error.retry_after // 60)
        saniye = int(error.retry_after % 60)
        if dakika > 0:
            await ctx.send(f"⏰ Bekle: **{dakika}dk {saniye}sn**")
        else:
            await ctx.send(f"⏰ Bekle: **{saniye} saniye**")
        return
    
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bu komutu kullanma yetkin yok!")
        return
    
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌ Botun bu işlemi yapma yetkisi yok!")
        return
    
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Kullanıcı bulunamadı!")
        return
    
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Eksik parametre: `{error.param.name}`")
        return
    
    if isinstance(error, commands.BadArgument):
        await ctx.send("❌ Yanlış parametre türü!")
        return
    
    print(f"❌ Komut Hatası [{ctx.command}]: {error}")

@bot.tree.error
async def on_app_command_error(interaction, error):
    from utils import guvenli_cevap
    
    error = getattr(error, 'original', error)
    
    if isinstance(error, app_commands.CommandOnCooldown):
        await guvenli_cevap(interaction, f"⏰ Bekle: **{int(error.retry_after)}sn**", ephemeral=True)
        return
    
    if isinstance(error, app_commands.MissingPermissions):
        await guvenli_cevap(interaction, "❌ Bu komutu kullanma yetkin yok!", ephemeral=True)
        return
    
    print(f"❌ Slash Hatası: {error}")
    
    try:
        await guvenli_cevap(interaction, "❌ Bir hata oluştu!", ephemeral=True)
    except:
        pass

# =====================================================
# 📦 COG'LARI YÜKLE
# =====================================================

async def load_cogs():
    cog_list = [
        'cogs.ekonomi',
        'cogs.oyunlar',
        'cogs.muzik',
        'cogs.moderasyon',
        'cogs.eglence',
        'cogs.bilgi',
        'cogs.yapay_zeka',
        'cogs.yardim'
    ]
    
    for cog in cog_list:
        try:
            await bot.load_extension(cog)
            print(f"✅ {cog} yüklendi!")
        except Exception as e:
            print(f"❌ {cog} yüklenemedi: {e}")

# =====================================================
# 🚀 BOTU BAŞLAT
# =====================================================

async def main():
    # Web sunucusunu başlat
    keep_alive()
    print("🌐 Web sunucusu başlatıldı!")
    
    # Durum özetini göster
    durum_ozeti()
    
    # Cog'ları yükle
    async with bot:
        try:
            print("📦 Cog'lar yükleniyor...")
            await load_cogs()
            print("✅ Tüm cog'lar yüklendi!")
        except Exception as e:
            print(f"❌ Cog yükleme hatası: {e}")
            import traceback
            traceback.print_exc()
        
        # Botu başlat
        if not DISCORD_TOKEN:
            print("❌ DISCORD_TOKEN bulunamadı!")
            return
        
        try:
            print("🔌 Discord'a bağlanılıyor...")
            await bot.start(DISCORD_TOKEN)
        except discord.LoginFailure:
            print("❌ Discord Token geçersiz!")
        except Exception as e:
            print(f"❌ Bot başlatma hatası: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
