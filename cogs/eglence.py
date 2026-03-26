# =====================================================
# 🎲 WOWSY BOT - EĞLENCE KOMUTLARI
# =====================================================

import discord
from discord.ext import commands
from discord import app_commands
import random

from utils import guvenli_cevap

# =====================================================
# 🎲 EĞLENCE COG
# =====================================================

class Eglence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =====================================================
    # 🎲 SLASH KOMUTLARI
    # =====================================================

    @app_commands.command(name="avatar", description="Kullanıcının avatarını göster")
    @app_commands.describe(member="Kullanıcı")
    async def slash_avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        
        embed = discord.Embed(title=f"🖼️ {member.name}", color=member.color)
        embed.set_image(url=member.display_avatar.url)
        embed.add_field(name="🔗 Link", value=f"[Avatarı İndir]({member.display_avatar.url})")
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="şaka", description="Rastgele şaka yap")
    async def slash_saka(self, interaction: discord.Interaction):
        sakalar = [
            "Neden bilgisayarlar soğuk algınlığına yakalanmaz? Çünkü Windows'ları kapalıdır! 🤧",
            "Programcı neden gözlük takar? Çünkü C# yapamıyor! 👓",
            "Neden programcılar doğayı sevmez? Çok fazla bug var! 🐛",
            "Discord botu neden yorulmaz? Çünkü uyumaz! 🤖",
            "Bit neden bilgisayara girmiş? Byte almak için! 😂",
            "İnternet neden üzgün? Çünkü çok fazla spam yiyor! 📧",
            "Klavye neden doktora gitti? Çünkü tuşları basıyordu! ⌨️",
            "JavaScript neden terapiye gitti? Çünkü çok fazla callback var! 🔄",
            "Programcı neden karısını terk etti? Çünkü obje odaklı değildi! 💔",
            "HTML neden partiye gitmedi? Çünkü tag'lenmeyi sevmiyor! 🎉",
            "SQL sorgusu bara girmiş, iki tabloya yaklaşmış ve sormuş: 'Join edebilir miyim?' 🍺",
            "Neden Java geliştiricileri gözlük takar? Çünkü C# yapamıyorlar! ☕",
            "Bir recursive fonksiyon bara girmiş. Barmen sormuş: 'Ne içersin?' Fonksiyon: 'Bir recursive fonksiyon bara girmiş...' 🔁",
            "Python neden yılan gibi? Çünkü indent'siz yaşayamaz! 🐍",
            "Neden yazılımcılar karanlıkta çalışır? Çünkü light mode gözlerini yakıyor! 🌙",
        ]
        
        embed = discord.Embed(title="😂 Şaka", description=random.choice(sakalar), color=discord.Color.orange())
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="8ball", description="Sihirli küreye soru sor")
    @app_commands.describe(soru="Sorun")
    async def slash_8ball(self, interaction: discord.Interaction, soru: str):
        cevaplar = [
            ("✅ Evet, kesinlikle!", discord.Color.green()),
            ("✅ Şüphesiz!", discord.Color.green()),
            ("✅ Evet!", discord.Color.green()),
            ("👍 Büyük ihtimalle evet", discord.Color.blue()),
            ("👍 İyi görünüyor", discord.Color.blue()),
            ("🤔 Belki...", discord.Color.orange()),
            ("🤔 Emin değilim", discord.Color.orange()),
            ("🔮 Tekrar sor", discord.Color.purple()),
            ("🔮 Şimdi söyleyemem", discord.Color.purple()),
            ("👎 Pek sanmıyorum", discord.Color.orange()),
            ("❌ Hayır", discord.Color.red()),
            ("❌ Kesinlikle hayır!", discord.Color.red()),
            ("💀 Çok şüpheli", discord.Color.dark_red()),
        ]
        
        cevap, renk = random.choice(cevaplar)
        
        embed = discord.Embed(title="🎱 Sihirli Küre", color=renk)
        embed.add_field(name="❓ Soru", value=soru, inline=False)
        embed.add_field(name="���� Cevap", value=cevap, inline=False)
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="sarıl", description="Birine sarıl")
    @app_commands.describe(member="Sarılacak kişi")
    async def slash_saril(self, interaction: discord.Interaction, member: discord.Member):
        if member == interaction.user:
            await guvenli_cevap(interaction, f"🤗 {interaction.user.mention} kendine sarıldı... Yalnız hissediyor musun? 😢")
        else:
            await guvenli_cevap(interaction, f"🤗 {interaction.user.mention} → {member.mention} 💕")

    @app_commands.command(name="tokatlat", description="Birine tokat at")
    @app_commands.describe(member="Tokatlanacak kişi")
    async def slash_tokatlat(self, interaction: discord.Interaction, member: discord.Member):
        if member == interaction.user:
            await guvenli_cevap(interaction, f"🤦 {interaction.user.mention} kendine tokat attı... Neden?")
        else:
            await guvenli_cevap(interaction, f"👋💥 {interaction.user.mention} → {member.mention} **ŞAAAK!**")

    @app_commands.command(name="zar", description="Zar at")
    async def slash_zar_at(self, interaction: discord.Interaction):
        zar = random.randint(1, 6)
        zar_emojiler = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅']
        
        embed = discord.Embed(title="🎲 Zar Atma", color=discord.Color.blue())
        embed.description = f"**{zar_emojiler[zar-1]}**\n\nSonuç: **{zar}**"
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="yazıtura", description="Yazı tura at")
    async def slash_yazitura(self, interaction: discord.Interaction):
        sonuc = random.choice(["Yazı", "Tura"])
        emoji = "🪙" if sonuc == "Yazı" else "💀"
        
        embed = discord.Embed(title="🪙 Yazı Tura", color=discord.Color.gold())
        embed.description = f"{emoji} **{sonuc}**"
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="seç", description="Seçenekler arasından birini seç")
    @app_commands.describe(secenekler="Seçenekleri virgülle ayır (örn: elma, armut, muz)")
    async def slash_sec(self, interaction: discord.Interaction, secenekler: str):
        liste = [s.strip() for s in secenekler.split(",") if s.strip()]
        
        if len(liste) < 2:
            await guvenli_cevap(interaction, "❌ En az 2 seçenek gir! (virgülle ayır)", ephemeral=True)
            return
        
        secilen = random.choice(liste)
        
        embed = discord.Embed(title="🎯 Seçim", color=discord.Color.purple())
        embed.add_field(name="📋 Seçenekler", value=", ".join(liste), inline=False)
        embed.add_field(name="✨ Seçilen", value=f"**{secilen}**", inline=False)
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="şanslısayı", description="1-100 arası şanslı sayını öğren")
    async def slash_sansli_sayi(self, interaction: discord.Interaction):
        sayi = random.randint(1, 100)
        
        if sayi == 100:
            mesaj = "🎉 **MÜKEMMEL!** Tam 100!"
            renk = discord.Color.gold()
        elif sayi >= 90:
            mesaj = "✨ Çok şanslısın!"
            renk = discord.Color.green()
        elif sayi >= 70:
            mesaj = "👍 Fena değil!"
            renk = discord.Color.blue()
        elif sayi >= 50:
            mesaj = "😐 Ortalama"
            renk = discord.Color.orange()
        elif sayi >= 30:
            mesaj = "😕 Biraz düşük"
            renk = discord.Color.orange()
        else:
            mesaj = "💀 Bugün şanslı günün değil!"
            renk = discord.Color.red()
        
        embed = discord.Embed(title="🍀 Şanslı Sayı", color=renk)
        embed.description = f"**{sayi}**\n\n{mesaj}"
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="aşkmetre", description="İki kişi arasındaki aşkı ölç")
    @app_commands.describe(kisi1="Birinci kişi", kisi2="İkinci kişi")
    async def slash_askmetre(self, interaction: discord.Interaction, kisi1: discord.Member, kisi2: discord.Member):
        # Aynı iki kişi için her zaman aynı sonuç
        seed = min(kisi1.id, kisi2.id) + max(kisi1.id, kisi2.id)
        random.seed(seed)
        oran = random.randint(0, 100)
        random.seed()  # Seed'i sıfırla
        
        if oran >= 90:
            mesaj = "💕 AŞKLA YAŞIYORLAR!"
            renk = discord.Color.red()
        elif oran >= 70:
            mesaj = "❤️ Çok uyumlular!"
            renk = discord.Color.magenta()
        elif oran >= 50:
            mesaj = "💛 İdare eder"
            renk = discord.Color.orange()
        elif oran >= 30:
            mesaj = "💔 Biraz zor"
            renk = discord.Color.greyple()
        else:
            mesaj = "🖤 Hiç uyuşmuyorlar!"
            renk = discord.Color.dark_grey()
        
        embed = discord.Embed(title="💘 Aşk Metre", color=renk)
        embed.description = f"{kisi1.mention} 💕 {kisi2.mention}\n\n**%{oran}** {mesaj}"
        
        await guvenli_cevap(interaction, embed=embed)

    # =====================================================
    # 🎲 PREFIX KOMUTLARI
    # =====================================================

    @commands.command(aliases=['pfp', 'pp', 'profil'])
    async def avatar(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        
        embed = discord.Embed(title=f"🖼️ {member.name}", color=member.color)
        embed.set_image(url=member.display_avatar.url)
        
        await ctx.send(embed=embed)

    @commands.command(aliases=['joke', 'espri'])
    async def saka(self, ctx):
        sakalar = [
            "Neden bilgisayarlar soğuk algınlığına yakalanmaz? Çünkü Windows'ları kapalıdır! 🤧",
            "Programcı neden gözlük takar? Çünkü C# yapamıyor! 👓",
            "Neden programcılar doğayı sevmez? Çok fazla bug var! 🐛",
            "Discord botu neden yorulmaz? Çünkü uyumaz! 🤖",
            "Bit neden bilgisayara girmiş? Byte almak için! 😂",
            "Klavye neden doktora gitti? Çünkü tuşları basıyordu! ⌨️",
        ]
        
        await ctx.send(f"😂 {random.choice(sakalar)}")

    @commands.command(aliases=['8ball', 'soru'])
    async def ball(self, ctx, *, soru):
        cevaplar = [
            "✅ Evet, kesinlikle!",
            "✅ Evet!",
            "👍 Büyük ihtimalle",
            "🤔 Belki...",
            "🔮 Tekrar sor",
            "👎 Pek sanmıyorum",
            "❌ Hayır",
            "❌ Kesinlikle hayır!",
        ]
        
        embed = discord.Embed(title="🎱 Sihirli Küre", color=discord.Color.purple())
        embed.add_field(name="❓ Soru", value=soru, inline=False)
        embed.add_field(name="💬 Cevap", value=random.choice(cevaplar), inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(aliases=['hug'])
    async def saril(self, ctx, member: discord.Member):
        if member == ctx.author:
            await ctx.send(f"🤗 {ctx.author.mention} kendine sarıldı... 😢")
        else:
            await ctx.send(f"🤗 {ctx.author.mention} → {member.mention} 💕")

    @commands.command(aliases=['slap'])
    async def tokatlat(self, ctx, member: discord.Member):
        if member == ctx.author:
            await ctx.send(f"🤦 {ctx.author.mention} kendine tokat attı...")
        else:
            await ctx.send(f"👋💥 {ctx.author.mention} → {member.mention} **ŞAAAK!**")

    @commands.command(aliases=['roll'])
    async def zarat(self, ctx):
        zar = random.randint(1, 6)
        await ctx.send(f"🎲 Zar: **{zar}**")

    @commands.command(aliases=['flip', 'coin'])
    async def yazitura(self, ctx):
        sonuc = random.choice(["Yazı", "Tura"])
        emoji = "🪙" if sonuc == "Yazı" else "💀"
        await ctx.send(f"{emoji} **{sonuc}**")

    @commands.command(aliases=['choose', 'pick'])
    async def sec(self, ctx, *, secenekler):
        liste = [s.strip() for s in secenekler.split(",") if s.strip()]
        
        if len(liste) < 2:
            await ctx.send("❌ En az 2 seçenek gir! (virgülle ayır)")
            return
        
        secilen = random.choice(liste)
        await ctx.send(f"🎯 Seçilen: **{secilen}**")

    @commands.command(aliases=['love', 'aşk'])
    async def askmetre(self, ctx, kisi1: discord.Member, kisi2: discord.Member = None):
        if kisi2 is None:
            kisi2 = ctx.author
        
        seed = min(kisi1.id, kisi2.id) + max(kisi1.id, kisi2.id)
        random.seed(seed)
        oran = random.randint(0, 100)
        random.seed()
        
        await ctx.send(f"💘 {kisi1.mention} 💕 {kisi2.mention}\n\n**%{oran}** aşk!")

# =====================================================
# 🔧 COG YÜKLEME
# =====================================================

async def setup(bot):
    await bot.add_cog(Eglence(bot))