# =====================================================
# 👑 WOWSY BOT - PATRON KOMUTLARI
# =====================================================

import discord
from discord.ext import commands
from datetime import datetime
import asyncio
import random

from config import PATRON_ID, economy_ref, db

# =====================================================
# 💾 EKONOMİ FONKSİYONLARI
# =====================================================

def get_economy(user_id):
    if not economy_ref:
        return {'para': 1000, 'banka': 0}
    try:
        doc = economy_ref.document(str(user_id)).get()
        if doc.exists:
            return doc.to_dict()
        else:
            data = {'para': 1000, 'banka': 0}
            economy_ref.document(str(user_id)).set(data)
            return data
    except:
        return {'para': 1000, 'banka': 0}

def update_economy(user_id, data):
    if not economy_ref:
        return False
    try:
        economy_ref.document(str(user_id)).set(data, merge=True)
        return True
    except:
        return False

def get_all_economy():
    if not economy_ref:
        return {}
    try:
        docs = economy_ref.stream()
        return {doc.id: doc.to_dict() for doc in docs}
    except:
        return {}

# =====================================================
# 🔐 PATRON KONTROLÜ
# =====================================================

def patron_check():
    async def predicate(ctx):
        if ctx.author.id != PATRON_ID:
            await ctx.send("❌ Bu komut sadece bot sahibine özel!", delete_after=5)
            return False
        return True
    return commands.check(predicate)

# =====================================================
# 👑 PATRON COG
# =====================================================

class Patron(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.gizli_mod = False
        self.patron_modu = False
        self.baslangic = datetime.now()

    # =====================================================
    # 📊 SUNUCU YÖNETİMİ
    # =====================================================

    @commands.command(name='servers', aliases=['sunucular'])
    @patron_check()
    async def servers(self, ctx):
        """Tüm sunucu listesi (ID'li)"""
        guilds = sorted(self.bot.guilds, key=lambda g: g.member_count, reverse=True)
        
        embed = discord.Embed(
            title=f"🏠 Sunucular ({len(guilds)})",
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )
        
        text = ""
        for i, guild in enumerate(guilds[:20], 1):
            text += f"`{i}.` **{guild.name}**\n"
            text += f"   👥 {guild.member_count} üye | 🆔 `{guild.id}`\n"
        
        if len(guilds) > 20:
            text += f"\n... ve **{len(guilds) - 20}** sunucu daha"
        
        embed.description = text
        embed.add_field(
            name="📊 Toplam",
            value=f"👥 **{sum(g.member_count for g in guilds):,}** kullanıcı",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name='sunucuuyeler', aliases=['serverusers', 'uyeler'])
    @patron_check()
    async def sunucu_uyeler(self, ctx, sunucu_id: int):
        """Sunucudaki tüm üyeleri ID ile listele"""
        guild = self.bot.get_guild(sunucu_id)
        
        if not guild:
            await ctx.send("❌ Sunucu bulunamadı!")
            return
        
        # Üyeleri al
        members = sorted(guild.members, key=lambda m: m.joined_at or datetime.min, reverse=True)
        
        embeds = []
        text = ""
        count = 0
        
        for member in members[:50]:
            line = f"`{member.id}` | **{member.name}**"
            if member.bot:
                line += " 🤖"
            line += "\n"
            
            if len(text) + len(line) > 1000:
                embed = discord.Embed(
                    title=f"👥 {guild.name} Üyeleri",
                    description=text,
                    color=discord.Color.blue()
                )
                embeds.append(embed)
                text = ""
            
            text += line
            count += 1
        
        # Son embed
        if text:
            embed = discord.Embed(
                title=f"👥 {guild.name} Üyeleri ({count}/{guild.member_count})",
                description=text,
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"🆔 Sunucu ID: {guild.id} | İlk 50 üye gösteriliyor")
            embeds.append(embed)
        
        for e in embeds[:3]:  # Max 3 embed
            await ctx.send(embed=e)

    @commands.command(name='sunucuara', aliases=['searchserver'])
    @patron_check()
    async def sunucu_ara(self, ctx, *, isim: str):
        """Sunucu adına göre ara"""
        isim_lower = isim.lower()
        bulunan = [g for g in self.bot.guilds if isim_lower in g.name.lower()]
        
        if not bulunan:
            await ctx.send(f"❌ '{isim}' içeren sunucu bulunamadı!")
            return
        
        embed = discord.Embed(
            title=f"🔍 Arama: '{isim}'",
            color=discord.Color.blue()
        )
        
        text = ""
        for guild in bulunan[:10]:
            text += f"🏠 **{guild.name}**\n"
            text += f"   🆔 `{guild.id}` | 👥 {guild.member_count} üye\n"
        
        embed.description = text
        embed.set_footer(text=f"{len(bulunan)} sonuç bulundu")
        
        await ctx.send(embed=embed)

    # =====================================================
    # 💰 EKONOMİ YÖNETİMİ (ID İLE)
    # =====================================================

    @commands.command(name='paraekle', aliases=['addmoney', 'para+'])
    @patron_check()
    async def paraekle(self, ctx, user_id: int, miktar: int):
        """Kullanıcıya para ekle (ID ile)"""
        if miktar <= 0:
            await ctx.send("❌ Miktar pozitif olmalı!")
            return
        
        try:
            user = await self.bot.fetch_user(user_id)
        except discord.NotFound:
            await ctx.send("❌ Kullanıcı bulunamadı!")
            return
        
        data = get_economy(user_id)
        data['para'] = data.get('para', 0) + miktar
        update_economy(user_id, data)
        
        embed = discord.Embed(title="💰 Para Eklendi", color=discord.Color.green())
        embed.add_field(name="👤 Kullanıcı", value=f"**{user.name}**\n`{user.id}`", inline=True)
        embed.add_field(name="💵 Miktar", value=f"+{miktar:,}💰", inline=True)
        embed.add_field(name="🎒 Yeni Bakiye", value=f"{data['para']:,}💰", inline=True)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"👑 {ctx.author.name} tarafından")
        
        await ctx.send(embed=embed)

    @commands.command(name='parasil', aliases=['removemoney', 'para-'])
    @patron_check()
    async def parasil(self, ctx, user_id: int, miktar: int):
        """Kullanıcıdan para sil (ID ile)"""
        if miktar <= 0:
            await ctx.send("❌ Miktar pozitif olmalı!")
            return
        
        try:
            user = await self.bot.fetch_user(user_id)
        except discord.NotFound:
            await ctx.send("❌ Kullanıcı bulunamadı!")
            return
        
        data = get_economy(user_id)
        data['para'] = max(0, data.get('para', 0) - miktar)
        update_economy(user_id, data)
        
        embed = discord.Embed(title="💸 Para Silindi", color=discord.Color.red())
        embed.add_field(name="👤 Kullanıcı", value=f"**{user.name}**\n`{user.id}`", inline=True)
        embed.add_field(name="💵 Miktar", value=f"-{miktar:,}💰", inline=True)
        embed.add_field(name="🎒 Yeni Bakiye", value=f"{data['para']:,}💰", inline=True)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"👑 {ctx.author.name} tarafından")
        
        await ctx.send(embed=embed)

    @commands.command(name='sıfırla', aliases=['reset', 'ekonomisifirla'])
    @patron_check()
    async def sifirla(self, ctx, user_id: int):
        """Kullanıcının ekonomisini sıfırla (ID ile)"""
        try:
            user = await self.bot.fetch_user(user_id)
        except discord.NotFound:
            await ctx.send("❌ Kullanıcı bulunamadı!")
            return
        
        data = {'para': 0, 'banka': 0}
        update_economy(user_id, data)
        
        embed = discord.Embed(title="🔄 Ekonomi Sıfırlandı", color=discord.Color.orange())
        embed.add_field(name="👤 Kullanıcı", value=f"**{user.name}**\n`{user.id}`", inline=True)
        embed.add_field(name="💰 Para", value="0💰", inline=True)
        embed.add_field(name="🏦 Banka", value="0💰", inline=True)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"👑 {ctx.author.name} tarafından")
        
        await ctx.send(embed=embed)

    @commands.command(name='ekonomitoplam', aliases=['totalmoney'])
    @patron_check()
    async def ekonomitoplam(self, ctx):
        """Toplam ekonomi miktarı"""
        all_data = get_all_economy()
        
        toplam_para = sum(d.get('para', 0) for d in all_data.values())
        toplam_banka = sum(d.get('banka', 0) for d in all_data.values())
        toplam = toplam_para + toplam_banka
        
        embed = discord.Embed(title="📊 Ekonomi Toplam", color=discord.Color.gold())
        embed.add_field(name="💵 Cüzdanlarda", value=f"{toplam_para:,}💰", inline=True)
        embed.add_field(name="🏦 Bankalarda", value=f"{toplam_banka:,}💰", inline=True)
        embed.add_field(name="💎 Toplam", value=f"{toplam:,}💰", inline=True)
        embed.add_field(name="👥 Kullanıcı", value=f"{len(all_data):,} kişi", inline=True)
        embed.add_field(name="📈 Ortalama", value=f"{toplam // max(len(all_data), 1):,}💰", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name='ekonomidagilim', aliases=['moneydist'])
    @patron_check()
    async def ekonomidagilim(self, ctx):
        """Para dağılımı"""
        all_data = get_all_economy()
        
        if not all_data:
            await ctx.send("📊 Henüz veri yok!")
            return
        
        kategoriler = {
            '💀 0-1K': 0,
            '🔴 1K-10K': 0,
            '🟠 10K-50K': 0,
            '🟡 50K-100K': 0,
            '🟢 100K-500K': 0,
            '🔵 500K-1M': 0,
            '💎 1M+': 0,
        }
        
        for data in all_data.values():
            toplam = data.get('para', 0) + data.get('banka', 0)
            if toplam < 1000:
                kategoriler['💀 0-1K'] += 1
            elif toplam < 10000:
                kategoriler['🔴 1K-10K'] += 1
            elif toplam < 50000:
                kategoriler['🟠 10K-50K'] += 1
            elif toplam < 100000:
                kategoriler['🟡 50K-100K'] += 1
            elif toplam < 500000:
                kategoriler['🟢 100K-500K'] += 1
            elif toplam < 1000000:
                kategoriler['🔵 500K-1M'] += 1
            else:
                kategoriler['💎 1M+'] += 1
        
        embed = discord.Embed(title="📊 Para Dağılımı", color=discord.Color.blue())
        
        text = ""
        toplam_kisi = len(all_data)
        for kategori, sayi in kategoriler.items():
            yuzde = (sayi / toplam_kisi) * 100 if toplam_kisi > 0 else 0
            bar_dolu = int(yuzde / 10)
            bar = "█" * bar_dolu + "░" * (10 - bar_dolu)
            text += f"{kategori}: `{bar}` **{sayi}** (%{yuzde:.1f})\n"
        
        embed.description = text
        embed.set_footer(text=f"Toplam: {toplam_kisi} kullanıcı")
        
        await ctx.send(embed=embed)

    @commands.command(name='faizayarla', aliases=['setinterest'])
    @patron_check()
    async def faizayarla(self, ctx, oran: float):
        """Faiz oranını değiştir"""
        if oran < 0 or oran > 50:
            await ctx.send("❌ Oran %0 ile %50 arasında olmalı!")
            return
        
        try:
            from cogs import ekonomi
            ekonomi.FAIZ_ORANI = oran / 100
            await ctx.send(f"✅ Faiz oranı **%{oran}** olarak ayarlandı!")
        except:
            await ctx.send(f"⚠️ Faiz oranı ayarlanamadı, ama değer: %{oran}")

    # =====================================================
    # 📢 MESAJLAŞMA (ID İLE)
    # =====================================================

    @commands.command(name='duyuru', aliases=['announce'])
    @patron_check()
    async def duyuru(self, ctx, *, mesaj: str):
        """Tüm sunuculara duyuru gönder"""
        basarili = 0
        basarisiz = 0
        
        embed = discord.Embed(
            title="📢 WOWSY Bot Duyurusu",
            description=mesaj,
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )
        embed.set_footer(text="WOWSY Bot • Resmi Duyuru")
        
        if self.bot.user:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        msg = await ctx.send(f"📤 {len(self.bot.guilds)} sunucuya gönderiliyor...")
        
        for guild in self.bot.guilds:
            try:
                kanal = guild.system_channel
                if not kanal or not kanal.permissions_for(guild.me).send_messages:
                    for ch in guild.text_channels:
                        if ch.permissions_for(guild.me).send_messages:
                            kanal = ch
                            break
                
                if kanal:
                    await kanal.send(embed=embed)
                    basarili += 1
                else:
                    basarisiz += 1
            except:
                basarisiz += 1
            
            await asyncio.sleep(0.5)
        
        await msg.edit(content=f"✅ Duyuru gönderildi!\n📊 Başarılı: **{basarili}** | Başarısız: **{basarisiz}**")

    @commands.command(name='dm', aliases=['özelmesaj', 'dmgonder'])
    @patron_check()
    async def dm_gonder(self, ctx, user_id: int, *, mesaj: str):
        """Kullanıcıya DM gönder (ID ile)"""
        try:
            user = await self.bot.fetch_user(user_id)
        except discord.NotFound:
            await ctx.send("❌ Kullanıcı bulunamadı!")
            return
        
        try:
            await ctx.message.delete()
        except:
            pass
        
        try:
            embed = discord.Embed(
                title="📬 WOWSY Bot'tan Mesaj",
                description=mesaj,
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            embed.set_footer(text="Bu mesaj bot sahibi tarafından gönderildi")
            
            await user.send(embed=embed)
            await ctx.author.send(f"✅ **{user.name}** (`{user.id}`) kullanıcısına DM gönderildi!")
        except discord.Forbidden:
            await ctx.author.send(f"❌ **{user.name}** (`{user.id}`) DM'leri kapalı!")
        except Exception as e:
            await ctx.author.send(f"❌ Hata: {e}")

    @commands.command(name='sunucumesaj', aliases=['servermsg'])
    @patron_check()
    async def sunucu_mesaj(self, ctx, sunucu_id: int, *, mesaj: str):
        """Belirli sunucuya mesaj gönder (ID ile)"""
        guild = self.bot.get_guild(sunucu_id)
        
        if not guild:
            await ctx.send("❌ Sunucu bulunamadı!")
            return
        
        embed = discord.Embed(
            title="📢 WOWSY Bot Mesajı",
            description=mesaj,
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        try:
            kanal = guild.system_channel
            if not kanal:
                for ch in guild.text_channels:
                    if ch.permissions_for(guild.me).send_messages:
                        kanal = ch
                        break
            
            if kanal:
                await kanal.send(embed=embed)
                await ctx.send(f"✅ **{guild.name}** (`{guild.id}`) sunucusuna mesaj gönderildi!")
            else:
                await ctx.send("❌ Yazılabilir kanal bulunamadı!")
        except Exception as e:
            await ctx.send(f"❌ Hata: {e}")

    # =====================================================
    # 📊 BOT İSTATİSTİKLERİ
    # =====================================================

    @commands.command(name='botstat', aliases=['botstats', 'stats'])
    @patron_check()
    async def botstat(self, ctx):
        """Detaylı bot istatistikleri"""
        uptime = datetime.now() - self.baslangic
        saat = int(uptime.total_seconds() // 3600)
        dakika = int((uptime.total_seconds() % 3600) // 60)
        
        embed = discord.Embed(
            title="📊 Bot İstatistikleri",
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )
        
        embed.add_field(name="🏠 Sunucular", value=f"**{len(self.bot.guilds)}** sunucu", inline=True)
        embed.add_field(name="👥 Kullanıcılar", value=f"**{sum(g.member_count for g in self.bot.guilds):,}** kişi", inline=True)
        embed.add_field(name="🏓 Ping", value=f"**{round(self.bot.latency * 1000)}ms**", inline=True)
        embed.add_field(name="⏰ Uptime", value=f"**{saat}s {dakika}dk**", inline=True)
        embed.add_field(name="🎵 Ses", value=f"**{len(self.bot.voice_clients)}** aktif", inline=True)
        embed.add_field(name="📦 Cog'lar", value=f"**{len(self.bot.cogs)}** yüklü", inline=True)
        embed.add_field(name="🔥 Firebase", value="✅ Bağlı" if db else "❌ Pasif", inline=True)
        embed.add_field(name="👑 Patron Modu", value="✅ Aktif" if self.patron_modu else "⚪ Pasif", inline=True)
        embed.add_field(name="👻 Gizli Mod", value="✅ Aktif" if self.gizli_mod else "⚪ Pasif", inline=True)
        
        if self.bot.user:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await ctx.send(embed=embed)

    @commands.command(name='kullanıcı', aliases=['userlookup', 'userinfo', 'kullanicibul'])
    @patron_check()
    async def kullanici_bilgi(self, ctx, user_id: int):
        """Kullanıcı bilgisi (ID ile)"""
        try:
            user = await self.bot.fetch_user(user_id)
        except discord.NotFound:
            await ctx.send("❌ Kullanıcı bulunamadı!")
            return
        
        embed = discord.Embed(title=f"👤 {user.name}", color=discord.Color.blue())
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="🆔 ID", value=f"`{user.id}`", inline=True)
        embed.add_field(name="🏷️ Tag", value=f"{user.name}#{user.discriminator}", inline=True)
        embed.add_field(name="🤖 Bot?", value="Evet" if user.bot else "Hayır", inline=True)
        embed.add_field(name="📅 Hesap", value=user.created_at.strftime("%d/%m/%Y"), inline=True)
        
        # Ekonomi bilgisi
        data = get_economy(user.id)
        embed.add_field(
            name="💰 Ekonomi",
            value=f"Cüzdan: {data.get('para', 0):,}💰\nBanka: {data.get('banka', 0):,}💰",
            inline=True
        )
        
        # Ortak sunucular
        ortak = []
        for g in self.bot.guilds:
            member = g.get_member(user.id)
            if member:
                ortak.append(f"🏠 **{g.name}** (`{g.id}`)")
        
        if ortak:
            embed.add_field(
                name=f"🏠 Ortak Sunucular ({len(ortak)})",
                value="\n".join(ortak[:5]) + ("\n..." if len(ortak) > 5 else ""),
                inline=False
            )
        else:
            embed.add_field(name="🏠 Sunucular", value="Ortak sunucu yok", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name='sunucu', aliases=['serverlookup', 'serverinfo'])
    @patron_check()
    async def sunucu_bilgi(self, ctx, sunucu_id: int):
        """Sunucu bilgisi (ID ile)"""
        guild = self.bot.get_guild(sunucu_id)
        
        if not guild:
            await ctx.send("❌ Sunucu bulunamadı veya bot bu sunucuda değil!")
            return
        
        embed = discord.Embed(title=f"🏠 {guild.name}", color=discord.Color.blue())
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(name="🆔 ID", value=f"`{guild.id}`", inline=True)
        embed.add_field(name="👥 Üyeler", value=f"{guild.member_count:,}", inline=True)
        embed.add_field(name="👑 Sahip", value=f"{guild.owner.name if guild.owner else '?'}\n`{guild.owner_id}`", inline=True)
        embed.add_field(name="💬 Kanallar", value=f"💬 {len(guild.text_channels)} | 🔊 {len(guild.voice_channels)}", inline=True)
        embed.add_field(name="🎭 Roller", value=len(guild.roles), inline=True)
        embed.add_field(name="📅 Kuruluş", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
        
        if guild.me and guild.me.joined_at:
            embed.add_field(name="🤖 Katılma", value=guild.me.joined_at.strftime("%d/%m/%Y"), inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name='sesaktif', aliases=['voiceactive'])
    @patron_check()
    async def ses_aktif(self, ctx):
        """Aktif müzik oturumları"""
        voice_clients = self.bot.voice_clients
        
        if not voice_clients:
            await ctx.send("🔇 Aktif ses bağlantısı yok!")
            return
        
        embed = discord.Embed(
            title=f"🎵 Aktif Ses ({len(voice_clients)})",
            color=discord.Color.green()
        )
        
        for vc in voice_clients:
            durum = "▶️ Çalıyor" if vc.is_playing() else ("⏸️ Duraklatıldı" if vc.is_paused() else "⏹️ Boşta")
            embed.add_field(
                name=f"🏠 {vc.guild.name}",
                value=f"🆔 `{vc.guild.id}`\n🔊 {vc.channel.name}\n{durum}\n👥 {len(vc.channel.members)} kişi",
                inline=True
            )
        
        await ctx.send(embed=embed)

    # =====================================================
    # ⚙️ BOT AYARLARI
    # =====================================================

    @commands.command(name='durum', aliases=['setstatus', 'activity'])
    @patron_check()
    async def durum_degistir(self, ctx, *, mesaj: str):
        """Bot durumunu değiştir"""
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name=mesaj
            )
        )
        await ctx.send(f"✅ Durum değiştirildi: **{mesaj}**")

    @commands.command(name='patronmodu', aliases=['ownermode'])
    @patron_check()
    async def patron_modu_toggle(self, ctx):
        """Patron modunu aç/kapat"""
        self.patron_modu = not self.patron_modu
        
        if self.patron_modu:
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name="👑 PATRON MODU"
                ),
                status=discord.Status.dnd
            )
            await ctx.send("👑 **PATRON MODU AKTİF!**")
        else:
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.listening,
                    name=f"/yardım | {len(self.bot.guilds)} sunucu"
                ),
                status=discord.Status.online
            )
            await ctx.send("⚪ Patron modu kapatıldı.")

    @commands.command(name='gizlimod', aliases=['invisible'])
    @patron_check()
    async def gizli_mod_toggle(self, ctx):
        """Gizli modu aç/kapat"""
        self.gizli_mod = not self.gizli_mod
        
        if self.gizli_mod:
            await self.bot.change_presence(status=discord.Status.invisible)
            await ctx.send("👻 **GİZLİ MOD AKTİF!** (Bot çevrimdışı görünüyor)")
        else:
            await self.bot.change_presence(status=discord.Status.online)
            await ctx.send("✅ Gizli mod kapatıldı, bot çevrimiçi.")

    # =====================================================
    # 🎪 EĞLENCE & TROLL (ID İLE)
    # =====================================================

    @commands.command(name='fake', aliases=['fakemsg'])
    @patron_check()
    async def fake_mesaj(self, ctx, member: discord.Member, *, mesaj: str):
        """Sahte mesaj gönder (webhook) - Aynı sunucuda olmalı"""
        try:
            webhook = await ctx.channel.create_webhook(name=member.display_name)
            
            await webhook.send(
                content=mesaj,
                username=member.display_name,
                avatar_url=member.display_avatar.url
            )
            
            await webhook.delete()
            
            try:
                await ctx.message.delete()
            except:
                pass
                
        except discord.Forbidden:
            await ctx.send("❌ Webhook oluşturma yetkim yok!")
        except Exception as e:
            await ctx.send(f"❌ Hata: {e}")

    @commands.command(name='troll')
    @patron_check()
    async def troll(self, ctx, user_id: int):
        """Kullanıcıyı troll et (DM'den 10 gif spam) - ID ile"""
        try:
            user = await self.bot.fetch_user(user_id)
        except discord.NotFound:
            await ctx.author.send("❌ Kullanıcı bulunamadı! ID'yi kontrol et.")
            return
        
        troll_gifs = [
            "https://media.tenor.com/x8v1oNUOmg4AAAAM/rickroll-roll.gif",
            "https://media.tenor.com/bNCvZnTNHHsAAAAM/aykut-elmas-durkut.gif",
            "https://media.tenor.com/Wlz1OVCItDUAAAAM/aykut-elmas-dans.gif",
            "https://media.tenor.com/hfNJdB1b6MMAAAAM/aykut-elmas-aykut.gif",
            "https://media.tenor.com/zsI4q8qBCZwAAAAM/nasip-nasipte.gif",
            "https://media.tenor.com/eaCL6E8SFxYAAAAM/aykut-elmas-para.gif",
            "https://media.tenor.com/RKXOy9flSh0AAAAM/aykut-elmas-leblebi.gif",
            "https://media.tenor.com/NiDJhO8HzSYAAAAM/aykut-elmas-dans.gif",
            "https://media.tenor.com/3TvCNHdZtK8AAAAi/shocked-funny.gif",
            "https://media.tenor.com/YHFsqP1KpS8AAAAM/projery-projery03.gif",
        ]
        
        try:
            await ctx.message.delete()
        except:
            pass
        
        try:
            await user.send(f"🎪 **Trolleniyorsun!** 😈")
            
            basarili = 0
            for i in range(10):
                try:
                    gif = random.choice(troll_gifs)
                    await user.send(gif)
                    basarili += 1
                    await asyncio.sleep(0.8)
                except:
                    break
            
            await ctx.author.send(f"✅ **{user.name}** (`{user.id}`) DM'den trollendi!\n📊 {basarili}/10 gif gönderildi")
            
        except discord.Forbidden:
            await ctx.author.send(f"❌ **{user.name}** (`{user.id}`) DM'leri kapalı, trollenemedi!")
        except Exception as e:
            await ctx.author.send(f"❌ Troll hatası: {e}")

    # =====================================================
    # 📊 RAPORLAR
    # =====================================================

    @commands.command(name='gunlukrapor', aliases=['dailyreport'])
    @patron_check()
    async def gunluk_rapor(self, ctx):
        """Günlük kullanım raporu"""
        embed = discord.Embed(
            title="📊 Günlük Rapor",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        uptime = datetime.now() - self.baslangic
        
        embed.add_field(name="⏰ Aktif Süre", value=f"{int(uptime.total_seconds() // 3600)}s {int((uptime.total_seconds() % 3600) // 60)}dk", inline=True)
        embed.add_field(name="🏠 Sunucular", value=f"{len(self.bot.guilds)}", inline=True)
        embed.add_field(name="👥 Kullanıcılar", value=f"{sum(g.member_count for g in self.bot.guilds):,}", inline=True)
        embed.add_field(name="🎵 Ses Oturumu", value=f"{len(self.bot.voice_clients)}", inline=True)
        embed.add_field(name="🏓 Ping", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        
        all_data = get_all_economy()
        toplam_para = sum(d.get('para', 0) + d.get('banka', 0) for d in all_data.values())
        embed.add_field(name="💰 Toplam Ekonomi", value=f"{toplam_para:,}💰", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name='aktifkullanicilar', aliases=['activeusers'])
    @patron_check()
    async def aktif_kullanicilar(self, ctx):
        """En aktif kullanıcılar (ekonomi bazlı) - ID'li"""
        all_data = get_all_economy()
        
        if not all_data:
            await ctx.send("📊 Henüz veri yok!")
            return
        
        siralama = sorted(
            all_data.items(),
            key=lambda x: x[1].get('para', 0) + x[1].get('banka', 0),
            reverse=True
        )[:10]
        
        embed = discord.Embed(title="🏆 En Aktif Kullanıcılar", color=discord.Color.gold())
        
        text = ""
        for i, (user_id, data) in enumerate(siralama, 1):
            try:
                user = await self.bot.fetch_user(int(user_id))
                toplam = data.get('para', 0) + data.get('banka', 0)
                text += f"`{i}.` **{user.name}** (`{user_id}`)\n     💰 {toplam:,}💰\n"
            except:
                text += f"`{i}.` ID: `{user_id}` - {data.get('para', 0) + data.get('banka', 0):,}💰\n"
        
        embed.description = text if text else "Veri yok"
        await ctx.send(embed=embed)

    @commands.command(name='sunucubuyume', aliases=['servergrowth'])
    @patron_check()
    async def sunucu_buyume(self, ctx):
        """Sunucu büyüme bilgisi"""
        guilds = sorted(self.bot.guilds, key=lambda g: g.me.joined_at if g.me and g.me.joined_at else datetime.min, reverse=True)
        
        embed = discord.Embed(title="📈 Son Katılan Sunucular", color=discord.Color.green())
        
        text = ""
        for guild in guilds[:10]:
            if guild.me and guild.me.joined_at:
                tarih = guild.me.joined_at.strftime("%d/%m/%Y")
                text += f"🏠 **{guild.name}**\n   🆔 `{guild.id}` | 👥 {guild.member_count} üye | 📅 {tarih}\n"
        
        embed.description = text if text else "Veri yok"
        embed.set_footer(text=f"Toplam: {len(self.bot.guilds)} sunucu")
        
        await ctx.send(embed=embed)

    # =====================================================
    # 📋 YARDIM
    # =====================================================

    @commands.command(name='patronyardım', aliases=['ownerhelp', 'phelp'])
    @patron_check()
    async def patron_yardim(self, ctx):
        """Patron komutları yardım"""
        embed = discord.Embed(
            title="👑 Patron Komutları",
            description="Sadece bot sahibine özel komutlar\n**Tüm komutlar ID bazlı çalışır!**",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="📊 Sunucu Yönetimi",
            value=(
                "`!servers` - Tüm sunucu listesi (ID'li)\n"
                "`!sunucu <id>` - Sunucu bilgisi\n"
                "`!sunucuuyeler <id>` - Sunucu üyeleri (ID'li)\n"
                "`!sunucuara <isim>` - Sunucu ara"
            ),
            inline=False
        )
        
        embed.add_field(
            name="💰 Ekonomi Yönetimi",
            value=(
                "`!paraekle <user_id> miktar` - Para ekle\n"
                "`!parasil <user_id> miktar` - Para sil\n"
                "`!sıfırla <user_id>` - Ekonomi sıfırla\n"
                "`!ekonomitoplam` - Toplam para\n"
                "`!ekonomidagilim` - Dağılım\n"
                "`!faizayarla oran` - Faiz ayarla"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📢 Mesajlaşma",
            value=(
                "`!duyuru mesaj` - Tüm sunuculara\n"
                "`!dm <user_id> mesaj` - DM gönder (ID ile)\n"
                "`!sunucumesaj <server_id> mesaj` - Sunucuya mesaj"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📊 İstatistikler",
            value=(
                "`!botstat` - Bot durumu\n"
                "`!kullanıcı <user_id>` - Kullanıcı bilgisi (ID ile)\n"
                "`!sesaktif` - Aktif sesler\n"
                "`!gunlukrapor` - Günlük rapor\n"
                "`!aktifkullanicilar` - Aktif kullanıcılar\n"
                "`!sunucubuyume` - Büyüme"
            ),
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Ayarlar",
            value=(
                "`!durum mesaj` - Durum değiştir\n"
                "`!patronmodu` - Patron modu\n"
                "`!gizlimod` - Görünmez mod"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🎪 Eğlence",
            value=(
                "`!fake @kişi mesaj` - Sahte mesaj (aynı sunucu)\n"
                "`!troll <user_id>` - Troll et (DM, ID ile)"
            ),
            inline=False
        )
        
        embed.set_footer(text="💡 ID bulmak için: Sağ tık → Kimliği Kopyala")
        
        await ctx.send(embed=embed)

# =====================================================
# 🔧 COG YÜKLEME
# =====================================================

async def setup(bot):
    await bot.add_cog(Patron(bot))
