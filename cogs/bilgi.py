# =====================================================
# ℹ️ WOWSY BOT - BİLGİ KOMUTLARI
# =====================================================

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, date

from config import db, groq_client
from utils import guvenli_cevap

# =====================================================
# 📅 TÜM TARİHLER - HER YIL SADECE BURAYI GÜNCELLE!
# =====================================================
# Yıl başında veya tarihler açıklandığında güncelle, başka yere dokunma!

YIL = 2026  # Mevcut yıl

# YKS Tarihleri (ÖSYM açıkladığında güncelle)
# Format: (Ay, Gün, Saat, Dakika)
YKS_TYT = (6, 20, 10, 15)   # 14 Haziran 10:15
YKS_AYT = (6, 21, 10, 15)   # 15 Haziran 10:15
YKS_YDT = (6, 15, 15, 45)   # 15 Haziran 15:45

# LGS Tarihi (MEB açıkladığında güncelle)
LGS_TARIH = (6, 14)          # 1 Haziran

# Dini Bayramlar (Her yıl değişir - Diyanet'ten kontrol et)
# Format: (Ay, Gün)
RAMAZAN_BAYRAMI = (3, 9)   # 30 Mart (3 gün)
KURBAN_BAYRAMI = (5, 27)     # 6 Haziran (4 gün)

# Okul Tarihleri (MEB açıkladığında güncelle)
KARNE_GUNU = (6, 26)        # 13 Haziran
OKUL_ACILISI = (9, 7)       # 8 Eylül

# Değişken Özel Günler (Her yıl farklı güne denk gelir)
ANNELER_GUNU = (5, 10)      # Mayıs 2. Pazar - 2025: 11 Mayıs
BABALAR_GUNU = (6, 21)      # Haziran 3. Pazar - 2025: 15 Haziran
BLACK_FRIDAY = (11, 27)     # Kasım son Cuma - 2025: 28 Kasım

# =====================================================
# 📅 OTOMATİK TARİH OLUŞTURMA (BU KISMA DOKUNMA!)
# =====================================================

# YKS tarihleri datetime objelerine çevir
YKS_SINAVLARI = {
    "TYT": datetime(YIL, YKS_TYT[0], YKS_TYT[1], YKS_TYT[2], YKS_TYT[3]),
    "AYT": datetime(YIL, YKS_AYT[0], YKS_AYT[1], YKS_AYT[2], YKS_AYT[3]),
    "YDT": datetime(YIL, YKS_YDT[0], YKS_YDT[1], YKS_YDT[2], YKS_YDT[3]),
}

# Özel günler sözlüğü
OZEL_GUNLER = {
    # ═══════════════════════════════════════════════════
    # 🇹🇷 RESMİ TATİLLER (SABİT - HER YIL AYNI)
    # ═══════════════════════════════════════════════════
    "Yılbaşı": {
        "tarih": (1, 1),
        "emoji": "🎆",
        "yillik": True,
        "tam_ad": "Yeni Yıl"
    },
    "23 Nisan": {
        "tarih": (4, 23),
        "emoji": "🇹🇷",
        "yillik": True,
        "tam_ad": "Ulusal Egemenlik ve Çocuk Bayramı"
    },
    "1 Mayıs": {
        "tarih": (5, 1),
        "emoji": "⚒️",
        "yillik": True,
        "tam_ad": "Emek ve Dayanışma Günü"
    },
    "19 Mayıs": {
        "tarih": (5, 19),
        "emoji": "🇹🇷",
        "yillik": True,
        "tam_ad": "Atatürk'ü Anma, Gençlik ve Spor Bayramı"
    },
    "15 Temmuz": {
        "tarih": (7, 15),
        "emoji": "🇹🇷",
        "yillik": True,
        "tam_ad": "Demokrasi ve Milli Birlik Günü"
    },
    "30 Ağustos": {
        "tarih": (8, 30),
        "emoji": "🇹🇷",
        "yillik": True,
        "tam_ad": "Zafer Bayramı"
    },
    "29 Ekim": {
        "tarih": (10, 29),
        "emoji": "🇹🇷",
        "yillik": True,
        "tam_ad": "Cumhuriyet Bayramı"
    },
    
    # ═══════════════════════════════════════════════════
    # 🌙 DİNİ BAYRAMLAR (YUKARIDAN ÇEKİYOR)
    # ═══════════════════════════════════════════════════
    "Ramazan Bayramı": {
        "tarih": RAMAZAN_BAYRAMI,
        "emoji": "🌙",
        "yil": YIL,
        "sure": 3,
        "tam_ad": "Ramazan Bayramı (Şeker Bayramı)"
    },
    "Kurban Bayramı": {
        "tarih": KURBAN_BAYRAMI,
        "emoji": "🐑",
        "yil": YIL,
        "sure": 4,
        "tam_ad": "Kurban Bayramı"
    },
    
    # ═══════════════════════════════════════════════════
    # 💕 ÖZEL GÜNLER
    # ═══════════════════════════════════════════════════
    "Sevgililer Günü": {
        "tarih": (2, 14),
        "emoji": "💕",
        "yillik": True,
        "tam_ad": "Sevgililer Günü (Valentine's Day)"
    },
    "Dünya Kadınlar Günü": {
        "tarih": (3, 8),
        "emoji": "👩",
        "yillik": True,
        "tam_ad": "Dünya Emekçi Kadınlar Günü"
    },
    "Anneler Günü": {
        "tarih": ANNELER_GUNU,
        "emoji": "👩‍👧‍👦",
        "yil": YIL,
        "tam_ad": "Anneler Günü"
    },
    "Babalar Günü": {
        "tarih": BABALAR_GUNU,
        "emoji": "👨‍👧‍👦",
        "yil": YIL,
        "tam_ad": "Babalar Günü"
    },
    "Öğretmenler Günü": {
        "tarih": (11, 24),
        "emoji": "👨‍🏫",
        "yillik": True,
        "tam_ad": "Öğretmenler Günü"
    },
    "Cadılar Bayramı": {
        "tarih": (10, 31),
        "emoji": "🎃",
        "yillik": True,
        "tam_ad": "Cadılar Bayramı (Halloween)"
    },
    "Yeni Yıl Gecesi": {
        "tarih": (12, 31),
        "emoji": "🎉",
        "yillik": True,
        "tam_ad": "Yılbaşı Gecesi"
    },
    
    # ═══════════════════════════════════════════════════
    # 📝 OKUL & SINAV (YUKARIDAN ÇEKİYOR)
    # ═══════════════════════════════════════════════════
    "YKS TYT": {
        "tarih": (YKS_TYT[0], YKS_TYT[1]),
        "emoji": "📝",
        "yil": YIL,
        "saat": f"{YKS_TYT[2]:02d}:{YKS_TYT[3]:02d}",
        "tam_ad": "YKS Temel Yeterlilik Testi"
    },
    "YKS AYT": {
        "tarih": (YKS_AYT[0], YKS_AYT[1]),
        "emoji": "📝",
        "yil": YIL,
        "saat": f"{YKS_AYT[2]:02d}:{YKS_AYT[3]:02d}",
        "tam_ad": "YKS Alan Yeterlilik Testi"
    },
    "LGS": {
        "tarih": LGS_TARIH,
        "emoji": "📝",
        "yil": YIL,
        "tam_ad": "Liselere Geçiş Sınavı"
    },
    "Karne Günü": {
        "tarih": KARNE_GUNU,
        "emoji": "📋",
        "yil": YIL,
        "tam_ad": "Karne Günü (Yaz Tatili Başlangıcı)"
    },
    "Okulların Açılışı": {
        "tarih": OKUL_ACILISI,
        "emoji": "🏫",
        "yil": YIL,
        "tam_ad": "Okulların Açılışı"
    },
    
    # ═══════════════════════════════════════════════════
    # 🛒 DİĞER
    # ═══════════════════════════════════════════════════
    "Black Friday": {
        "tarih": BLACK_FRIDAY,
        "emoji": "🛒",
        "yil": YIL,
        "tam_ad": "Black Friday (Kara Cuma)"
    },
    "Dünya Çevre Günü": {
        "tarih": (6, 5),
        "emoji": "🌍",
        "yillik": True,
        "tam_ad": "Dünya Çevre Günü"
    },
}

# ═══════════════════════════════════════════════════════════
# 🇹🇷 TÜRKÇE TARİH FORMATLAMA
# ═══════════════════════════════════════════════════════════

AY_ISIMLERI = {
    1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan",
    5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos",
    9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
}

GUN_ISIMLERI = {
    0: "Pazartesi", 1: "Salı", 2: "Çarşamba", 3: "Perşembe",
    4: "Cuma", 5: "Cumartesi", 6: "Pazar"
}

def turkce_tarih(tarih):
    """Tarihi Türkçe formatla: 14 Haziran 2025, Cumartesi"""
    gun = tarih.day
    ay = AY_ISIMLERI[tarih.month]
    yil = tarih.year
    gun_adi = GUN_ISIMLERI[tarih.weekday()]
    return f"{gun} {ay} {yil}, {gun_adi}"

def turkce_tarih_kisa(tarih):
    """Kısa Türkçe tarih: 14 Haziran"""
    return f"{tarih.day} {AY_ISIMLERI[tarih.month]}"

# =====================================================
# ℹ️ BİLGİ COG
# =====================================================

class Bilgi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =====================================================
    # ℹ️ SLASH KOMUTLARI
    # =====================================================

    @app_commands.command(name="ping", description="Bot gecikmesini göster")
    async def slash_ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        
        if latency < 100:
            renk = discord.Color.green()
            durum = "🟢 Mükemmel"
        elif latency < 200:
            renk = discord.Color.blue()
            durum = "🔵 İyi"
        elif latency < 400:
            renk = discord.Color.orange()
            durum = "🟠 Orta"
        else:
            renk = discord.Color.red()
            durum = "🔴 Yavaş"
        
        embed = discord.Embed(title="🏓 Pong!", color=renk)
        embed.add_field(name="📡 Gecikme", value=f"**{latency}ms**", inline=True)
        embed.add_field(name="📊 Durum", value=durum, inline=True)
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="sunucu", description="Sunucu bilgilerini göster")
    async def slash_sunucu(self, interaction: discord.Interaction):
        g = interaction.guild
        
        embed = discord.Embed(title=f"📊 {g.name}", color=discord.Color.blue())
        
        if g.icon:
            embed.set_thumbnail(url=g.icon.url)
        
        toplam_uye = g.member_count
        bot_sayisi = len([m for m in g.members if m.bot])
        insan_sayisi = toplam_uye - bot_sayisi
        
        embed.add_field(name="👥 Üyeler", value=f"👤 {insan_sayisi} | 🤖 {bot_sayisi} | 📊 {toplam_uye}", inline=False)
        embed.add_field(name="💬 Kanallar", value=f"💬 {len(g.text_channels)} | 🔊 {len(g.voice_channels)}", inline=True)
        embed.add_field(name="🎭 Roller", value=f"{len(g.roles)}", inline=True)
        embed.add_field(name="😀 Emojiler", value=f"{len(g.emojis)}", inline=True)
        embed.add_field(name="📅 Kuruluş", value=g.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="👑 Sahip", value=g.owner.mention if g.owner else "Bilinmiyor", inline=True)
        embed.add_field(name="🆔 ID", value=g.id, inline=True)
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="kullanıcı", description="Kullanıcı bilgilerini göster")
    @app_commands.describe(member="Kullanıcı")
    async def slash_kullanici(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        
        embed = discord.Embed(title=f"👤 {member}", color=member.color)
        embed.set_thumbnail(url=member.display_avatar.url)
        
        embed.add_field(name="🆔 ID", value=member.id, inline=True)
        embed.add_field(name="🏷️ Tag", value=f"{member.name}#{member.discriminator}", inline=True)
        embed.add_field(name="🤖 Bot?", value="Evet" if member.bot else "Hayır", inline=True)
        
        embed.add_field(name="📅 Hesap Oluşturma", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="📥 Sunucuya Katılma", value=member.joined_at.strftime("%d/%m/%Y") if member.joined_at else "?", inline=True)
        
        if member.premium_since:
            embed.add_field(name="💎 Boost", value=member.premium_since.strftime("%d/%m/%Y"), inline=True)
        
        roles = [r.mention for r in member.roles[1:][:10]]
        if roles:
            embed.add_field(name=f"🎭 Roller ({len(member.roles) - 1})", value=" ".join(roles), inline=False)
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="botbilgi", description="Bot hakkında bilgi")
    async def slash_botbilgi(self, interaction: discord.Interaction):
        embed = discord.Embed(title="⚡ WOWSY Bot", color=discord.Color.gold())
        embed.description = "**Tek Bot, Sonsuz Eğlence!**\n\nMüzik, ekonomi, oyunlar, moderasyon ve yapay zeka - hepsi tek bir botta!"
        
        embed.add_field(name="👨‍💻 Geliştirici", value="WOWSY", inline=True)
        embed.add_field(name="🏠 Sunucular", value=f"{len(self.bot.guilds)}", inline=True)
        embed.add_field(name="👥 Kullanıcılar", value=f"{sum(g.member_count for g in self.bot.guilds):,}", inline=True)
        embed.add_field(name="🏓 Gecikme", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="🤖 AI", value="Groq Llama 3.1" if groq_client else "Pasif", inline=True)
        
        embed.add_field(
            name="📊 Özellikler",
            value="```\n"
                  "🎵 Müzik Sistemi\n"
                  "💰 Ekonomi & Bahis\n"
                  "🎮 9 Farklı Oyun\n"
                  "🛡️ Moderasyon\n"
                  "🤖 Yapay Zeka\n"
                  "🎲 Eğlence\n"
                  "📅 YKS & Sayaçlar\n"
                  "```",
            inline=False
        )
        
        if self.bot.user:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        embed.set_footer(text="⚡ /yardım ile tüm komutları gör!")
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="davet", description="Botu sunucuna davet et")
    async def slash_davet(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🔗 WOWSY Bot'u Davet Et", color=discord.Color.blue())
        embed.description = "Botu sunucuna eklemek için aşağıdaki butona tıkla!"
        
        embed.add_field(
            name="🚀 Davet Linki",
            value="[Sunucuna Ekle](https://discord.com/oauth2/authorize?client_id=1485291664502427708)",
            inline=False
        )
        
        embed.add_field(
            name="⚡ Özellikler",
            value="• 🎵 Müzik\n• 💰 Ekonomi\n• 🎮 Oyunlar\n• 🛡️ Moderasyon\n• 🤖 AI",
            inline=True
        )
        
        embed.add_field(
            name="📊 İstatistikler",
            value=f"• 🏠 {len(self.bot.guilds)} sunucu\n• 👥 {sum(g.member_count for g in self.bot.guilds):,} kullanıcı\n• ⚡ 60+ komut",
            inline=True
        )
        
        if self.bot.user:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="uptime", description="Botun ne zamandır açık olduğunu göster")
    async def slash_uptime(self, interaction: discord.Interaction):
        embed = discord.Embed(title="⏰ Bot Durumu", color=discord.Color.green())
        embed.add_field(name="✅ Durum", value="Çevrimiçi", inline=True)
        embed.add_field(name="🏓 Ping", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="🏠 Sunucular", value=f"{len(self.bot.guilds)}", inline=True)
        
        await guvenli_cevap(interaction, embed=embed)

    # =====================================================
    # 📚 YKS SAYACI
    # =====================================================

    @app_commands.command(name="yks", description="YKS'ye kalan süreyi göster")
    @app_commands.describe(sinav="Hangi sınav?")
    @app_commands.choices(sinav=[
        app_commands.Choice(name="📝 TYT (Temel Yeterlilik)", value="TYT"),
        app_commands.Choice(name="📚 AYT (Alan Yeterlilik)", value="AYT"),
        app_commands.Choice(name="🌍 YDT (Yabancı Dil)", value="YDT"),
        app_commands.Choice(name="📊 Hepsi", value="hepsi"),
    ])
    async def slash_yks(self, interaction: discord.Interaction, sinav: str = "hepsi"):
        simdi = datetime.now()
        
        if sinav == "hepsi":
            embed = discord.Embed(
                title=f"📚 YKS {YIL} Geri Sayım",
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/2232/2232688.png")
            
            for sinav_adi, tarih in YKS_SINAVLARI.items():
                kalan = tarih - simdi
                
                if kalan.total_seconds() <= 0:
                    embed.add_field(
                        name=f"✅ {sinav_adi}",
                        value="Sınav tamamlandı!",
                        inline=False
                    )
                else:
                    gun = kalan.days
                    saat = kalan.seconds // 3600
                    dakika = (kalan.seconds % 3600) // 60
                    
                    # İlerleme çubuğu (365 gün üzerinden)
                    toplam_gun = 365
                    gecen_gun = max(0, toplam_gun - gun)
                    ilerleme = min(gecen_gun / toplam_gun, 1.0)
                    bar_dolu = int(ilerleme * 10)
                    bar = "🟩" * bar_dolu + "⬜" * (10 - bar_dolu)
                    
                    embed.add_field(
                        name=f"📝 {sinav_adi}",
                        value=(
                            f"📅 **{turkce_tarih(tarih)}**\n"
                            f"⏰ Saat: **{tarih.strftime('%H:%M')}**\n"
                            f"⏳ **{gun}** gün, **{saat}** saat, **{dakika}** dakika\n"
                            f"{bar} `%{int(ilerleme*100)}`"
                        ),
                        inline=False
                    )
            
            # Motivasyon mesajı
            tyt_kalan = (YKS_SINAVLARI["TYT"] - simdi).days
            if tyt_kalan > 180:
                motivasyon = "📖 Bolca zamanın var, düzenli çalış!"
            elif tyt_kalan > 90:
                motivasyon = "⚡ Tempo artırma zamanı!"
            elif tyt_kalan > 30:
                motivasyon = "🔥 Son sprint başladı!"
            elif tyt_kalan > 7:
                motivasyon = "💪 Son hafta! Tekrara odaklan!"
            elif tyt_kalan > 0:
                motivasyon = "🍀 Son günler... Sakin ol, başaracaksın!"
            else:
                motivasyon = "✅ Sınavlar bitti, hayırlısı olsun!"
            
            embed.add_field(name="💬 Motivasyon", value=motivasyon, inline=False)
            embed.set_footer(text="📌 Tarihler tahminidir, ÖSYM duyurusunu takip edin!")
            
        else:
            tarih = YKS_SINAVLARI.get(sinav)
            if not tarih:
                await guvenli_cevap(interaction, "❌ Geçersiz sınav!", ephemeral=True)
                return
            
            kalan = tarih - simdi
            
            if kalan.total_seconds() <= 0:
                embed = discord.Embed(
                    title=f"✅ {sinav} {YIL}",
                    description="Sınav tamamlandı!",
                    color=discord.Color.green()
                )
            else:
                gun = kalan.days
                saat = kalan.seconds // 3600
                dakika = (kalan.seconds % 3600) // 60
                saniye = kalan.seconds % 60
                
                toplam_saat = gun * 24 + saat
                toplam_dakika = toplam_saat * 60 + dakika
                
                embed = discord.Embed(
                    title=f"📝 {sinav} {YIL} Geri Sayım",
                    color=discord.Color.blue()
                )
                embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/2232/2232688.png")
                
                embed.add_field(
                    name="📅 Sınav Tarihi",
                    value=f"**{turkce_tarih(tarih)}**\nSaat: **{tarih.strftime('%H:%M')}**",
                    inline=False
                )
                embed.add_field(
                    name="⏳ Kalan Süre",
                    value=(
                        f"```\n"
                        f"📆 {gun:,} gün\n"
                        f"⏰ {saat} saat\n"
                        f"⏱️ {dakika} dakika\n"
                        f"⌛ {saniye} saniye\n"
                        f"```"
                    ),
                    inline=True
                )
                embed.add_field(
                    name="📊 Toplam",
                    value=(
                        f"```\n"
                        f"🕐 {toplam_saat:,} saat\n"
                        f"⏱️ {toplam_dakika:,} dakika\n"
                        f"```"
                    ),
                    inline=True
                )
                
                # Hafta hesabı
                hafta = gun // 7
                kalan_gun = gun % 7
                embed.add_field(
                    name="📅 Hafta Bazında",
                    value=f"**{hafta}** hafta **{kalan_gun}** gün",
                    inline=False
                )
                
                # İlerleme çubuğu
                toplam_gun = 365
                gecen = max(0, toplam_gun - gun)
                ilerleme = min(gecen / toplam_gun, 1.0)
                bar_dolu = int(ilerleme * 20)
                bar = "█" * bar_dolu + "░" * (20 - bar_dolu)
                embed.add_field(
                    name="📊 İlerleme",
                    value=f"`{bar}` %{int(ilerleme*100)}",
                    inline=False
                )
                
                embed.set_footer(text="📌 ÖSYM duyurularını takip etmeyi unutma!")
        
        await guvenli_cevap(interaction, embed=embed)

    @commands.command(aliases=['yks2025', 'sınav', 'tyt', 'ayt'])
    async def yks(self, ctx, sinav: str = "TYT"):
        """YKS'ye kalan süreyi göster"""
        sinav = sinav.upper()
        if sinav not in YKS_SINAVLARI:
            sinav = "TYT"
        
        tarih = YKS_SINAVLARI[sinav]
        simdi = datetime.now()
        kalan = tarih - simdi
        
        if kalan.total_seconds() <= 0:
            await ctx.send(f"✅ **{sinav}** sınavı tamamlandı!")
            return
        
        gun = kalan.days
        saat = kalan.seconds // 3600
        dakika = (kalan.seconds % 3600) // 60
        hafta = gun // 7
        
        embed = discord.Embed(title=f"📝 {sinav} {YIL}", color=discord.Color.blue())
        embed.description = (
            f"📅 **{turkce_tarih(tarih)}**\n"
            f"⏰ Saat: **{tarih.strftime('%H:%M')}**\n\n"
            f"⏳ **{gun}** gün, **{saat}** saat, **{dakika}** dakika kaldı!"
        )
        embed.add_field(
            name="📅 Hafta Bazında",
            value=f"**{hafta}** hafta **{gun % 7}** gün",
            inline=False
        )
        
        # İlerleme çubuğu
        toplam_gun = 365
        gecen = max(0, toplam_gun - gun)
        ilerleme = min(gecen / toplam_gun, 1.0)
        bar_dolu = int(ilerleme * 10)
        bar = "🟩" * bar_dolu + "⬜" * (10 - bar_dolu)
        embed.add_field(
            name="📊 İlerleme",
            value=f"{bar} %{int(ilerleme*100)}",
            inline=False
        )
        
        embed.set_footer(text="📌 ÖSYM duyurularını takip et!")
        
        await ctx.send(embed=embed)

    # =====================================================
    # 📅 ÖZEL GÜNLER SAYACI
    # =====================================================

    @app_commands.command(name="sayaç", description="Özel günlere kalan süreyi göster")
    @app_commands.describe(gun="Hangi özel gün? (boş bırakırsan yaklaşanları gösterir)")
    async def slash_sayac(self, interaction: discord.Interaction, gun: str = None):
        bugun = date.today()
        
        if gun is None:
            # Tüm yaklaşan günleri göster
            yaklasan = []
            
            for isim, bilgi in OZEL_GUNLER.items():
                ay, gun_no = bilgi["tarih"]
                
                if bilgi.get("yillik"):
                    yil = bugun.year
                    hedef = date(yil, ay, gun_no)
                    if hedef < bugun:
                        hedef = date(yil + 1, ay, gun_no)
                else:
                    yil = bilgi.get("yil", bugun.year)
                    hedef = date(yil, ay, gun_no)
                    if hedef < bugun:
                        continue
                
                kalan = (hedef - bugun).days
                emoji = bilgi.get("emoji", "📅")
                yaklasan.append((kalan, isim, emoji, hedef))
            
            # Sırala
            yaklasan.sort(key=lambda x: x[0])
            
            embed = discord.Embed(
                title="📅 Yaklaşan Özel Günler",
                color=discord.Color.purple()
            )
            
            # İlk 12 günü göster
            text = ""
            for i, (kalan, isim, emoji, hedef) in enumerate(yaklasan[:12]):
                if kalan == 0:
                    sure = "🎉 **BUGÜN!**"
                elif kalan == 1:
                    sure = "⭐ **YARIN!**"
                elif kalan < 7:
                    sure = f"🔥 **{kalan} gün** (Bu hafta!)"
                elif kalan < 30:
                    sure = f"📅 **{kalan} gün** ({kalan // 7} hafta)"
                else:
                    sure = f"📆 **{kalan} gün**"
                
                tarih_str = turkce_tarih_kisa(hedef)
                text += f"{emoji} **{isim}**: {sure}\n   └ {tarih_str}\n"
            
            embed.description = text if text else "Yaklaşan özel gün bulunamadı!"
            embed.set_footer(text="💡 /sayaç <gün adı> ile detay gör!")
            
        else:
            # Belirli bir gün ara
            gun_lower = gun.lower()
            bulunan = None
            
            for isim, bilgi in OZEL_GUNLER.items():
                if gun_lower in isim.lower():
                    bulunan = (isim, bilgi)
                    break
            
            if not bulunan:
                # Benzer önerileri bul
                oneriler = [isim for isim in OZEL_GUNLER.keys() if any(c in isim.lower() for c in gun_lower[:3])][:5]
                oneri_text = f"\n💡 Öneriler: {', '.join(oneriler)}" if oneriler else ""
                await guvenli_cevap(
                    interaction, 
                    f"❌ '**{gun}**' bulunamadı!{oneri_text}\n\n📋 Örnek: `ramazan`, `23 nisan`, `yılbaşı`, `kurban`", 
                    ephemeral=True
                )
                return
            
            isim, bilgi = bulunan
            ay, gun_no = bilgi["tarih"]
            emoji = bilgi.get("emoji", "📅")
            
            if bilgi.get("yillik"):
                yil = bugun.year
                hedef = date(yil, ay, gun_no)
                if hedef < bugun:
                    hedef = date(yil + 1, ay, gun_no)
            else:
                yil = bilgi.get("yil", bugun.year)
                hedef = date(yil, ay, gun_no)
            
            kalan = (hedef - bugun).days
            
            if kalan < 0:
                embed = discord.Embed(
                    title=f"{emoji} {isim}",
                    description="Bu etkinlik geçti!",
                    color=discord.Color.greyple()
                )
            else:
                if kalan == 0:
                    renk = discord.Color.gold()
                    durum = "🎉 **BUGÜN!**"
                elif kalan == 1:
                    renk = discord.Color.gold()
                    durum = "⭐ **YARIN!**"
                elif kalan <= 7:
                    renk = discord.Color.green()
                    durum = f"🔥 **{kalan} gün kaldı!** (Bu hafta!)"
                elif kalan <= 30:
                    renk = discord.Color.blue()
                    durum = f"⏳ **{kalan} gün** ({kalan // 7} hafta)"
                else:
                    renk = discord.Color.purple()
                    durum = f"⏳ **{kalan} gün** (~{kalan // 30} ay)"
                
                embed = discord.Embed(
                    title=f"{emoji} {isim}",
                    color=renk
                )
                
                tam_ad = bilgi.get("tam_ad")
                if tam_ad and tam_ad != isim:
                    embed.description = f"*{tam_ad}*"
                
                hedef_datetime = datetime(hedef.year, hedef.month, hedef.day)
                embed.add_field(
                    name="📅 Tarih",
                    value=f"**{turkce_tarih(hedef_datetime)}**",
                    inline=False
                )
                
                if "saat" in bilgi:
                    embed.add_field(name="⏰ Saat", value=bilgi["saat"], inline=True)
                
                if "sure" in bilgi:
                    embed.add_field(name="📆 Tatil Süresi", value=f"{bilgi['sure']} gün", inline=True)
                
                embed.add_field(name="⏳ Kalan", value=durum, inline=False)
                
                # Hafta hesabı
                if kalan > 7:
                    hafta = kalan // 7
                    kalan_gun = kalan % 7
                    embed.add_field(
                        name="📅 Hafta Bazında",
                        value=f"**{hafta}** hafta **{kalan_gun}** gün",
                        inline=True
                    )
                
                # İlerleme çubuğu (yıl bazında)
                if kalan > 0 and kalan < 365:
                    ilerleme = (365 - kalan) / 365
                    bar_dolu = int(ilerleme * 10)
                    bar = "🟩" * bar_dolu + "⬜" * (10 - bar_dolu)
                    embed.add_field(
                        name="📊 Yıl İlerlemesi",
                        value=f"{bar} %{int(ilerleme*100)}",
                        inline=False
                    )
        
        await guvenli_cevap(interaction, embed=embed)

    @slash_sayac.autocomplete('gun')
    async def sayac_autocomplete(self, interaction: discord.Interaction, current: str):
        """Sayaç komutu için otomatik tamamlama"""
        gunler = list(OZEL_GUNLER.keys())
        return [
            app_commands.Choice(name=f"{OZEL_GUNLER[g]['emoji']} {g}", value=g)
            for g in gunler if current.lower() in g.lower()
        ][:25]

    @commands.command(aliases=['özelgün', 'tatil', 'bayram', 'countdown'])
    async def sayac(self, ctx, *, gun: str = None):
        """Özel günlere kalan süreyi göster"""
        bugun = date.today()
        
        if gun is None:
            # Yaklaşan 6 günü göster
            yaklasan = []
            
            for isim, bilgi in OZEL_GUNLER.items():
                ay, gun_no = bilgi["tarih"]
                
                if bilgi.get("yillik"):
                    yil = bugun.year
                    hedef = date(yil, ay, gun_no)
                    if hedef < bugun:
                        hedef = date(yil + 1, ay, gun_no)
                else:
                    yil = bilgi.get("yil", bugun.year)
                    hedef = date(yil, ay, gun_no)
                    if hedef < bugun:
                        continue
                
                kalan = (hedef - bugun).days
                emoji = bilgi.get("emoji", "📅")
                yaklasan.append((kalan, isim, emoji, hedef))
            
            yaklasan.sort(key=lambda x: x[0])
            
            embed = discord.Embed(title="📅 Yaklaşan Özel Günler", color=discord.Color.purple())
            
            text = ""
            for kalan, isim, emoji, hedef in yaklasan[:6]:
                tarih_str = turkce_tarih_kisa(hedef)
                if kalan == 0:
                    text += f"{emoji} **{isim}**: 🎉 BUGÜN!\n"
                elif kalan == 1:
                    text += f"{emoji} **{isim}**: ⭐ YARIN! ({tarih_str})\n"
                else:
                    text += f"{emoji} **{isim}**: {kalan} gün ({tarih_str})\n"
            
            embed.description = text if text else "Yaklaşan gün yok!"
            embed.set_footer(text="💡 !sayac <gün adı> ile detay gör")
            await ctx.send(embed=embed)
            
        else:
            # Belirli gün ara
            gun_lower = gun.lower()
            bulunan = None
            
            for isim, bilgi in OZEL_GUNLER.items():
                if gun_lower in isim.lower():
                    bulunan = (isim, bilgi)
                    break
            
            if not bulunan:
                await ctx.send(f"❌ '**{gun}**' bulunamadı!\n💡 Örnek: `ramazan`, `23 nisan`, `yılbaşı`, `kurban`")
                return
            
            isim, bilgi = bulunan
            ay, gun_no = bilgi["tarih"]
            emoji = bilgi.get("emoji", "📅")
            
            if bilgi.get("yillik"):
                yil = bugun.year
                hedef = date(yil, ay, gun_no)
                if hedef < bugun:
                    hedef = date(yil + 1, ay, gun_no)
            else:
                yil = bilgi.get("yil", bugun.year)
                hedef = date(yil, ay, gun_no)
            
            kalan = (hedef - bugun).days
            hedef_datetime = datetime(hedef.year, hedef.month, hedef.day)
            tarih_str = turkce_tarih(hedef_datetime)
            
            if kalan == 0:
                embed = discord.Embed(
                    title=f"{emoji} {isim}",
                    description=f"🎉 **BUGÜN!**\n📅 {tarih_str}",
                    color=discord.Color.gold()
                )
            elif kalan > 0:
                embed = discord.Embed(
                    title=f"{emoji} {isim}",
                    color=discord.Color.blue()
                )
                embed.add_field(name="📅 Tarih", value=tarih_str, inline=False)
                embed.add_field(name="⏳ Kalan", value=f"**{kalan}** gün", inline=True)
                
                if kalan > 7:
                    embed.add_field(
                        name="📅 Hafta",
                        value=f"**{kalan // 7}** hafta **{kalan % 7}** gün",
                        inline=True
                    )
                
                if "sure" in bilgi:
                    embed.add_field(name="📆 Tatil", value=f"{bilgi['sure']} gün", inline=True)
            else:
                embed = discord.Embed(
                    title=f"{emoji} {isim}",
                    description="Bu etkinlik geçti!",
                    color=discord.Color.greyple()
                )
            
            await ctx.send(embed=embed)

    # =====================================================
    # ℹ️ PREFIX KOMUTLARI
    # =====================================================

    @commands.command()
    async def ping(self, ctx):
        """Bot gecikmesini göster"""
        latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(title="🏓 Pong!", color=discord.Color.green())
        embed.add_field(name="📡 Gecikme", value=f"**{latency}ms**")
        
        await ctx.send(embed=embed)

    @commands.command(aliases=['server', 'guild'])
    async def sunucu(self, ctx):
        """Sunucu bilgilerini göster"""
        g = ctx.guild
        
        embed = discord.Embed(title=f"📊 {g.name}", color=discord.Color.blue())
        
        if g.icon:
            embed.set_thumbnail(url=g.icon.url)
        
        embed.add_field(name="👥 Üyeler", value=g.member_count, inline=True)
        embed.add_field(name="💬 Kanallar", value=len(g.channels), inline=True)
        embed.add_field(name="🎭 Roller", value=len(g.roles), inline=True)
        embed.add_field(name="📅 Kuruluş", value=g.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="👑 Sahip", value=g.owner.mention if g.owner else "?", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(aliases=['user', 'whois', 'kim'])
    async def kullanici(self, ctx, member: discord.Member = None):
        """Kullanıcı bilgilerini göster"""
        member = member or ctx.author
        
        embed = discord.Embed(title=f"👤 {member}", color=member.color)
        embed.set_thumbnail(url=member.display_avatar.url)
        
        embed.add_field(name="🆔 ID", value=member.id, inline=True)
        embed.add_field(name="📅 Katılma", value=member.joined_at.strftime("%d/%m/%Y") if member.joined_at else "?", inline=True)
        embed.add_field(name="🎂 Hesap", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
        
        roles = [r.mention for r in member.roles[1:][:5]]
        if roles:
            embed.add_field(name="🎭 Roller", value=" ".join(roles), inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(aliases=['botinfo', 'info', 'hakkında'])
    async def botbilgi(self, ctx):
        """Bot hakkında bilgi"""
        embed = discord.Embed(title="⚡ WOWSY Bot", color=discord.Color.gold())
        embed.description = "Tek Bot, Sonsuz Eğlence!"
        embed.add_field(name="👨‍💻 Geliştirici", value="WOWSY", inline=True)
        embed.add_field(name="🏠 Sunucular", value=f"{len(self.bot.guilds)}", inline=True)
        embed.add_field(name="🏓 Gecikme", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        
        if self.bot.user:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await ctx.send(embed=embed)

    @commands.command(aliases=['invite'])
    async def davet(self, ctx):
        """Botu sunucuna davet et"""
        embed = discord.Embed(title="🔗 Davet Linki", color=discord.Color.blue())
        embed.description = "[Botu Sunucuna Ekle](https://discord.com/oauth2/authorize?client_id=1485291664502427708)"
        
        await ctx.send(embed=embed)

# =====================================================
# 🔧 COG YÜKLEME
# =====================================================

async def setup(bot):
    await bot.add_cog(Bilgi(bot))
