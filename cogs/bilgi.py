# =====================================================
# ℹ️ WOWSY BOT - BİLGİ KOMUTLARI
# =====================================================

import discord
from discord.ext import commands
from discord import app_commands

from config import db, groq_client
from utils import guvenli_cevap

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
        
        embed.add_field(name="👨‍💻 Geliştirici", value="Ömer", inline=True)
        embed.add_field(name="🏠 Sunucular", value=f"{len(self.bot.guilds)}", inline=True)
        embed.add_field(name="👥 Kullanıcılar", value=f"{sum(g.member_count for g in self.bot.guilds):,}", inline=True)
        embed.add_field(name="🏓 Gecikme", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="🔥 Veritabanı", value="Firebase" if db else "Yok", inline=True)
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
    # ℹ️ PREFIX KOMUTLARI
    # =====================================================

    @commands.command()
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(title="🏓 Pong!", color=discord.Color.green())
        embed.add_field(name="📡 Gecikme", value=f"**{latency}ms**")
        
        await ctx.send(embed=embed)

    @commands.command(aliases=['server', 'guild'])
    async def sunucu(self, ctx):
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
        embed = discord.Embed(title="⚡ WOWSY Bot", color=discord.Color.gold())
        embed.description = "Tek Bot, Sonsuz Eğlence!"
        
        embed.add_field(name="👨‍💻 Geliştirici", value="Ömer", inline=True)
        embed.add_field(name="🏠 Sunucular", value=f"{len(self.bot.guilds)}", inline=True)
        embed.add_field(name="🏓 Gecikme", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        
        if self.bot.user:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await ctx.send(embed=embed)

    @commands.command(aliases=['invite'])
    async def davet(self, ctx):
        embed = discord.Embed(title="🔗 Davet Linki", color=discord.Color.blue())
        embed.description = "[Botu Sunucuna Ekle](https://discord.com/oauth2/authorize?client_id=1485291664502427708)"
        
        await ctx.send(embed=embed)

# =====================================================
# 🔧 COG YÜKLEME
# =====================================================

async def setup(bot):
    await bot.add_cog(Bilgi(bot))