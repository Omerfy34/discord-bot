# =====================================================
# 🛡️ WOWSY BOT - MODERASYON KOMUTLARI
# =====================================================

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import asyncio

from config import warnings_ref
from utils import guvenli_cevap

# =====================================================
# ⚠️ UYARI FONKSİYONLARI
# =====================================================

def get_warnings(user_id):
    """Kullanıcının uyarılarını al"""
    if not warnings_ref:
        return []
    try:
        doc = warnings_ref.document(str(user_id)).get()
        return doc.to_dict().get('list', []) if doc.exists else []
    except:
        return []

def add_warning(user_id, warning):
    """Kullanıcıya uyarı ekle"""
    if not warnings_ref:
        return False
    try:
        warnings = get_warnings(user_id)
        warnings.append(warning)
        warnings_ref.document(str(user_id)).set({'list': warnings})
        return True
    except:
        return False

def clear_warnings(user_id):
    """Kullanıcının tüm uyarılarını sil"""
    if not warnings_ref:
        return False
    try:
        warnings_ref.document(str(user_id)).delete()
        return True
    except:
        return False

# =====================================================
# 🛡️ MODERASYON COG
# =====================================================

class Moderasyon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =====================================================
    # 🛡️ SLASH KOMUTLARI
    # =====================================================

    @app_commands.command(name="kick", description="Kullanıcıyı sunucudan at")
    @app_commands.describe(member="Atılacak kullanıcı", sebep="Sebep")
    async def slash_kick(self, interaction: discord.Interaction, member: discord.Member, sebep: str = "Sebep belirtilmedi"):
        if not interaction.user.guild_permissions.kick_members:
            await guvenli_cevap(interaction, "❌ Bu komutu kullanma yetkin yok!", ephemeral=True)
            return
        
        if member.top_role >= interaction.user.top_role:
            await guvenli_cevap(interaction, "❌ Bu kullanıcıyı atamazsın!", ephemeral=True)
            return
        
        try:
            await member.kick(reason=f"{interaction.user}: {sebep}")
            
            embed = discord.Embed(title="👢 Kullanıcı Atıldı", color=discord.Color.orange())
            embed.add_field(name="👤 Kullanıcı", value=f"{member} ({member.id})", inline=False)
            embed.add_field(name="👮 Yetkili", value=interaction.user.mention, inline=True)
            embed.add_field(name="📝 Sebep", value=sebep, inline=True)
            
            await guvenli_cevap(interaction, embed=embed)
        except Exception as e:
            await guvenli_cevap(interaction, f"❌ Hata: {e}", ephemeral=True)

    @app_commands.command(name="ban", description="Kullanıcıyı yasakla")
    @app_commands.describe(member="Yasaklanacak kullanıcı", sebep="Sebep")
    async def slash_ban(self, interaction: discord.Interaction, member: discord.Member, sebep: str = "Sebep belirtilmedi"):
        if not interaction.user.guild_permissions.ban_members:
            await guvenli_cevap(interaction, "❌ Bu komutu kullanma yetkin yok!", ephemeral=True)
            return
        
        if member.top_role >= interaction.user.top_role:
            await guvenli_cevap(interaction, "❌ Bu kullanıcıyı yasaklayamazsın!", ephemeral=True)
            return
        
        try:
            await member.ban(reason=f"{interaction.user}: {sebep}")
            
            embed = discord.Embed(title="🔨 Kullanıcı Yasaklandı", color=discord.Color.red())
            embed.add_field(name="👤 Kullanıcı", value=f"{member} ({member.id})", inline=False)
            embed.add_field(name="👮 Yetkili", value=interaction.user.mention, inline=True)
            embed.add_field(name="📝 Sebep", value=sebep, inline=True)
            
            await guvenli_cevap(interaction, embed=embed)
        except Exception as e:
            await guvenli_cevap(interaction, f"❌ Hata: {e}", ephemeral=True)

    @app_commands.command(name="unban", description="Kullanıcının yasağını kaldır")
    @app_commands.describe(user_id="Kullanıcı ID'si")
    async def slash_unban(self, interaction: discord.Interaction, user_id: str):
        if not interaction.user.guild_permissions.ban_members:
            await guvenli_cevap(interaction, "❌ Bu komutu kullanma yetkin yok!", ephemeral=True)
            return
        
        try:
            user = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(user)
            await guvenli_cevap(interaction, f"✅ **{user.name}** yasağı kaldırıldı!")
        except:
            await guvenli_cevap(interaction, "❌ Kullanıcı bulunamadı veya yasaklı değil!", ephemeral=True)

    @app_commands.command(name="sil", description="Mesaj sil")
    @app_commands.describe(miktar="Silinecek mesaj sayısı (1-100)")
    async def slash_sil(self, interaction: discord.Interaction, miktar: int):
        if not interaction.user.guild_permissions.manage_messages:
            await guvenli_cevap(interaction, "❌ Bu komutu kullanma yetkin yok!", ephemeral=True)
            return
        
        if miktar < 1 or miktar > 100:
            await guvenli_cevap(interaction, "❌ 1-100 arası bir sayı gir!", ephemeral=True)
            return
        
        await guvenli_cevap(interaction, f"🗑️ **{miktar}** mesaj siliniyor...", ephemeral=True)
        
        try:
            deleted = await interaction.channel.purge(limit=miktar)
            await interaction.channel.send(f"🗑️ **{len(deleted)}** mesaj silindi!", delete_after=3)
        except Exception as e:
            await interaction.followup.send(f"❌ Hata: {e}", ephemeral=True)

    @app_commands.command(name="timeout", description="Kullanıcıyı sustur")
    @app_commands.describe(member="Susturulacak kullanıcı", dakika="Süre (dakika)", sebep="Sebep")
    async def slash_timeout(self, interaction: discord.Interaction, member: discord.Member, dakika: int, sebep: str = "Sebep belirtilmedi"):
        if not interaction.user.guild_permissions.moderate_members:
            await guvenli_cevap(interaction, "❌ Bu komutu kullanma yetkin yok!", ephemeral=True)
            return
        
        if member.top_role >= interaction.user.top_role:
            await guvenli_cevap(interaction, "❌ Bu kullanıcıyı susturamazsın!", ephemeral=True)
            return
        
        if dakika < 1 or dakika > 40320:
            await guvenli_cevap(interaction, "❌ Süre 1 dakika ile 28 gün arası olmalı!", ephemeral=True)
            return
        
        try:
            await member.timeout(timedelta(minutes=dakika), reason=f"{interaction.user}: {sebep}")
            
            embed = discord.Embed(title="🔇 Kullanıcı Susturuldu", color=discord.Color.orange())
            embed.add_field(name="👤 Kullanıcı", value=member.mention, inline=True)
            embed.add_field(name="⏱️ Süre", value=f"{dakika} dakika", inline=True)
            embed.add_field(name="📝 Sebep", value=sebep, inline=False)
            
            await guvenli_cevap(interaction, embed=embed)
        except Exception as e:
            await guvenli_cevap(interaction, f"❌ Hata: {e}", ephemeral=True)

    @app_commands.command(name="untimeout", description="Kullanıcının susturmasını kaldır")
    @app_commands.describe(member="Kullanıcı")
    async def slash_untimeout(self, interaction: discord.Interaction, member: discord.Member):
        if not interaction.user.guild_permissions.moderate_members:
            await guvenli_cevap(interaction, "❌ Bu komutu kullanma yetkin yok!", ephemeral=True)
            return
        
        try:
            await member.timeout(None)
            await guvenli_cevap(interaction, f"✅ {member.mention} susturması kaldırıldı!")
        except Exception as e:
            await guvenli_cevap(interaction, f"❌ Hata: {e}", ephemeral=True)

    @app_commands.command(name="uyar", description="Kullanıcıyı uyar")
    @app_commands.describe(member="Uyarılacak kullanıcı", sebep="Uyarı sebebi")
    async def slash_uyar(self, interaction: discord.Interaction, member: discord.Member, sebep: str):
        if not interaction.user.guild_permissions.moderate_members:
            await guvenli_cevap(interaction, "❌ Bu komutu kullanma yetkin yok!", ephemeral=True)
            return
        
        warning = {
            'sebep': sebep,
            'tarih': datetime.now().strftime("%d/%m/%Y %H:%M"),
            'yetkili': str(interaction.user.id),
            'yetkili_isim': str(interaction.user)
        }
        
        add_warning(member.id, warning)
        warnings = get_warnings(member.id)
        
        embed = discord.Embed(title="⚠️ Uyarı Verildi", color=discord.Color.yellow())
        embed.add_field(name="👤 Kullanıcı", value=member.mention, inline=True)
        embed.add_field(name="👮 Yetkili", value=interaction.user.mention, inline=True)
        embed.add_field(name="📝 Sebep", value=sebep, inline=False)
        embed.add_field(name="📊 Toplam Uyarı", value=f"{len(warnings)} uyarı", inline=True)
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="uyarılar", description="Kullanıcının uyarılarını göster")
    @app_commands.describe(member="Kullanıcı")
    async def slash_uyarilar(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        warnings = get_warnings(member.id)
        
        if not warnings:
            await guvenli_cevap(interaction, f"✅ {member.mention} hiç uyarı almamış!")
            return
        
        embed = discord.Embed(title=f"⚠️ {member.name} - Uyarılar", color=discord.Color.yellow())
        embed.set_thumbnail(url=member.display_avatar.url)
        
        for i, w in enumerate(warnings[-10:], 1):
            tarih = w.get('tarih', 'Bilinmiyor')
            sebep = w.get('sebep', 'Sebep yok')
            yetkili = w.get('yetkili_isim', 'Bilinmiyor')
            embed.add_field(
                name=f"#{i} - {tarih}",
                value=f"📝 {sebep}\n👮 {yetkili}",
                inline=False
            )
        
        embed.set_footer(text=f"Toplam: {len(warnings)} uyarı")
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="uyarısil", description="Kullanıcının tüm uyarılarını sil")
    @app_commands.describe(member="Kullanıcı")
    async def slash_uyarisil(self, interaction: discord.Interaction, member: discord.Member):
        if not interaction.user.guild_permissions.administrator:
            await guvenli_cevap(interaction, "❌ Bu komutu sadece adminler kullanabilir!", ephemeral=True)
            return
        
        clear_warnings(member.id)
        await guvenli_cevap(interaction, f"✅ {member.mention} tüm uyarıları silindi!")

    # =====================================================
    # 🛡️ PREFIX KOMUTLARI
    # =====================================================

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, sebep="Sebep belirtilmedi"):
        if member.top_role >= ctx.author.top_role:
            await ctx.send("❌ Bu kullanıcıyı atamazsın!")
            return
        
        await member.kick(reason=f"{ctx.author}: {sebep}")
        
        embed = discord.Embed(title="👢 Kullanıcı Atıldı", color=discord.Color.orange())
        embed.add_field(name="👤 Kullanıcı", value=f"{member}", inline=True)
        embed.add_field(name="���� Sebep", value=sebep, inline=True)
        
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, sebep="Sebep belirtilmedi"):
        if member.top_role >= ctx.author.top_role:
            await ctx.send("❌ Bu kullanıcıyı yasaklayamazsın!")
            return
        
        await member.ban(reason=f"{ctx.author}: {sebep}")
        
        embed = discord.Embed(title="🔨 Kullanıcı Yasaklandı", color=discord.Color.red())
        embed.add_field(name="👤 Kullanıcı", value=f"{member}", inline=True)
        embed.add_field(name="📝 Sebep", value=sebep, inline=True)
        
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            await ctx.send(f"✅ **{user.name}** yasağı kaldırıldı!")
        except:
            await ctx.send("❌ Kullanıcı bulunamadı veya yasaklı değil!")

    @commands.command(aliases=['temizle', 'clear', 'purge'])
    @commands.has_permissions(manage_messages=True)
    async def sil(self, ctx, miktar: int):
        if miktar < 1 or miktar > 100:
            await ctx.send("❌ 1-100 arası bir sayı gir!")
            return
        
        deleted = await ctx.channel.purge(limit=miktar + 1)
        msg = await ctx.send(f"🗑️ **{len(deleted) - 1}** mesaj silindi!")
        await asyncio.sleep(3)
        try:
            await msg.delete()
        except:
            pass

    @commands.command(aliases=['mute', 'sustur'])
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, dakika: int, *, sebep="Sebep belirtilmedi"):
        if member.top_role >= ctx.author.top_role:
            await ctx.send("❌ Bu kullanıcıyı susturamazsın!")
            return
        
        await member.timeout(timedelta(minutes=dakika), reason=f"{ctx.author}: {sebep}")
        
        embed = discord.Embed(title="🔇 Kullanıcı Susturuldu", color=discord.Color.orange())
        embed.add_field(name="👤 Kullanıcı", value=member.mention, inline=True)
        embed.add_field(name="⏱️ Süre", value=f"{dakika} dakika", inline=True)
        embed.add_field(name="📝 Sebep", value=sebep, inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(aliases=['unmute'])
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member):
        await member.timeout(None)
        await ctx.send(f"✅ {member.mention} susturması kaldırıldı!")

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def uyar(self, ctx, member: discord.Member, *, sebep):
        warning = {
            'sebep': sebep,
            'tarih': datetime.now().strftime("%d/%m/%Y %H:%M"),
            'yetkili': str(ctx.author.id),
            'yetkili_isim': str(ctx.author)
        }
        
        add_warning(member.id, warning)
        warnings = get_warnings(member.id)
        
        embed = discord.Embed(title="⚠️ Uyarı Verildi", color=discord.Color.yellow())
        embed.add_field(name="👤 Kullanıcı", value=member.mention, inline=True)
        embed.add_field(name="📝 Sebep", value=sebep, inline=True)
        embed.add_field(name="📊 Toplam", value=f"{len(warnings)} uyarı", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(aliases=['uyarılar', 'warnings'])
    async def uyarilar(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        warnings = get_warnings(member.id)
        
        if not warnings:
            await ctx.send(f"✅ {member.mention} hiç uyarı almamış!")
            return
        
        embed = discord.Embed(title=f"⚠️ {member.name} - Uyarılar", color=discord.Color.yellow())
        
        for i, w in enumerate(warnings[-10:], 1):
            tarih = w.get('tarih', 'Bilinmiyor')
            sebep = w.get('sebep', 'Sebep yok')
            embed.add_field(name=f"#{i} - {tarih}", value=sebep, inline=False)
        
        embed.set_footer(text=f"Toplam: {len(warnings)} uyarı")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def uyarisil(self, ctx, member: discord.Member):
        clear_warnings(member.id)
        await ctx.send(f"✅ {member.mention} tüm uyarıları silindi!")

# =====================================================
# 🔧 COG YÜKLEME
# =====================================================

async def setup(bot):
    await bot.add_cog(Moderasyon(bot))