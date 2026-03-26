# =====================================================
# 💰 WOWSY BOT - EKONOMİ KOMUTLARI
# =====================================================

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import random

from config import economy_ref, PATRON_ID
from utils import guvenli_cevap

# =====================================================
# 💾 EKONOMİ FONKSİYONLARI
# =====================================================

def get_economy(user_id):
    """Kullanıcının ekonomi verisini al"""
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
    except Exception as e:
        print(f"❌ Veri okuma hatası: {e}")
        return {'para': 1000, 'banka': 0}

def update_economy(user_id, data):
    """Kullanıcının ekonomi verisini güncelle"""
    if not economy_ref:
        return False
    try:
        economy_ref.document(str(user_id)).set(data, merge=True)
        return True
    except Exception as e:
        print(f"❌ Veri yazma hatası: {e}")
        return False

def get_all_economy():
    """Tüm ekonomi verilerini al"""
    if not economy_ref:
        return {}
    try:
        docs = economy_ref.stream()
        return {doc.id: doc.to_dict() for doc in docs}
    except:
        return {}

# =====================================================
# 💰 EKONOMİ COG
# =====================================================

class Ekonomi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =====================================================
    # 💰 SLASH KOMUTLARI
    # =====================================================

    @app_commands.command(name="bakiye", description="Bakiyeni göster")
    @app_commands.describe(member="Kullanıcı (boş bırakırsan kendin)")
    async def slash_bakiye(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        data = get_economy(member.id)
        
        embed = discord.Embed(title=f"💰 {member.name}", color=discord.Color.gold())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="💵 Cüzdan", value=f"{data['para']:,}💰", inline=True)
        embed.add_field(name="🏦 Banka", value=f"{data.get('banka', 0):,}💰", inline=True)
        embed.add_field(name="💎 Toplam", value=f"{data['para'] + data.get('banka', 0):,}💰", inline=True)
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="günlük", description="Günlük ödülünü al (24 saatte bir)")
    async def slash_gunluk(self, interaction: discord.Interaction):
        data = get_economy(interaction.user.id)
        simdi = datetime.now()
        
        # Cooldown kontrolü
        if 'son_gunluk' in data and data['son_gunluk']:
            try:
                son = datetime.fromisoformat(data['son_gunluk'])
                if simdi - son < timedelta(hours=24):
                    kalan = timedelta(hours=24) - (simdi - son)
                    saat = int(kalan.total_seconds() // 3600)
                    dk = int((kalan.total_seconds() % 3600) // 60)
                    await guvenli_cevap(interaction, f"⏰ Bekle! **{saat}s {dk}dk** kaldı.", ephemeral=True)
                    return
            except:
                pass
        
        # Streak sistemi
        if 'streak' not in data:
            data['streak'] = 0
        
        if 'son_gunluk' in data and data['son_gunluk']:
            try:
                son = datetime.fromisoformat(data['son_gunluk'])
                if simdi - son < timedelta(hours=48):
                    data['streak'] += 1
                else:
                    data['streak'] = 1
            except:
                data['streak'] = 1
        else:
            data['streak'] = 1
        
        streak = min(data['streak'], 30)
        base = random.randint(200, 500)
        bonus = streak * 25
        toplam = base + bonus
        
        data['para'] += toplam
        data['son_gunluk'] = simdi.isoformat()
        update_economy(interaction.user.id, data)
        
        embed = discord.Embed(title="🎁 Günlük Ödül", color=discord.Color.gold())
        embed.add_field(name="💰 Temel", value=f"+{base}💰", inline=True)
        embed.add_field(name="🔥 Streak Bonus", value=f"+{bonus}💰 ({streak} gün)", inline=True)
        embed.add_field(name="💎 Toplam", value=f"+{toplam}💰", inline=False)
        embed.add_field(name="🎒 Yeni Bakiye", value=f"{data['para']:,}💰", inline=False)
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="bedava", description="Bedava para al (2 saatte bir)")
    async def slash_bedava(self, interaction: discord.Interaction):
        data = get_economy(interaction.user.id)
        simdi = datetime.now()
        
        if 'son_bedava' in data and data['son_bedava']:
            try:
                son = datetime.fromisoformat(data['son_bedava'])
                if simdi - son < timedelta(hours=2):
                    kalan = timedelta(hours=2) - (simdi - son)
                    dk = int(kalan.total_seconds() // 60)
                    await guvenli_cevap(interaction, f"⏰ Bekle! **{dk} dakika** kaldı.", ephemeral=True)
                    return
            except:
                pass
        
        para = random.randint(50, 150)
        data['para'] += para
        data['son_bedava'] = simdi.isoformat()
        update_economy(interaction.user.id, data)
        
        embed = discord.Embed(title="💸 Bedava Para", color=discord.Color.green())
        embed.description = f"**+{para}💰** kazandın!"
        embed.add_field(name="🎒 Bakiye", value=f"{data['para']:,}💰")
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="çalış", description="Çalışarak para kazan (30 dk'da bir)")
    async def slash_calis(self, interaction: discord.Interaction):
        data = get_economy(interaction.user.id)
        simdi = datetime.now()
        
        if 'son_calis' in data and data['son_calis']:
            try:
                son = datetime.fromisoformat(data['son_calis'])
                if simdi - son < timedelta(minutes=30):
                    kalan = timedelta(minutes=30) - (simdi - son)
                    dk = int(kalan.total_seconds() // 60)
                    await guvenli_cevap(interaction, f"⏰ Dinleniyorsun! **{dk} dakika** bekle.", ephemeral=True)
                    return
            except:
                pass
        
        isler = [
            ("💻 Yazılım geliştirdin", 150, 250),
            ("🍕 Pizza dağıttın", 50, 100),
            ("🚗 Uber şoförlüğü yaptın", 80, 150),
            ("📦 Kargo taşıdın", 60, 120),
            ("🎨 Grafik tasarım yaptın", 120, 200),
            ("📱 Uygulama yaptın", 180, 280),
            ("🎵 Müzik prodüksiyonu yaptın", 100, 180),
            ("📸 Fotoğraf çekimi yaptın", 90, 160),
            ("✍️ Makale yazdın", 70, 130),
        ]
        
        is_secim = random.choice(isler)
        kazanc = random.randint(is_secim[1], is_secim[2])
        data['para'] += kazanc
        data['son_calis'] = simdi.isoformat()
        update_economy(interaction.user.id, data)
        
        embed = discord.Embed(title="💼 Çalışma", color=discord.Color.blue())
        embed.description = f"{is_secim[0]} ve **+{kazanc}💰** kazandın!"
        embed.add_field(name="🎒 Bakiye", value=f"{data['para']:,}💰")
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="yatır", description="Parayı bankaya yatır")
    @app_commands.describe(miktar="Miktar (veya 'hepsi')")
    async def slash_yatir(self, interaction: discord.Interaction, miktar: str):
        data = get_economy(interaction.user.id)
        
        if miktar.lower() in ['hepsi', 'all', 'tümü', 'hep']:
            miktar_int = data['para']
        else:
            try:
                miktar_int = int(miktar)
            except:
                await guvenli_cevap(interaction, "❌ Geçerli bir miktar gir!", ephemeral=True)
                return
        
        if miktar_int <= 0:
            await guvenli_cevap(interaction, "❌ Geçerli bir miktar gir!", ephemeral=True)
            return
        
        if data['para'] < miktar_int:
            await guvenli_cevap(interaction, f"❌ Yeterli paran yok! (Cüzdan: {data['para']:,}💰)", ephemeral=True)
            return
        
        data['para'] -= miktar_int
        data['banka'] = data.get('banka', 0) + miktar_int
        update_economy(interaction.user.id, data)
        
        embed = discord.Embed(title="🏦 Para Yatırma", color=discord.Color.green())
        embed.description = f"**{miktar_int:,}💰** bankaya yatırıldı!"
        embed.add_field(name="💵 Cüzdan", value=f"{data['para']:,}💰", inline=True)
        embed.add_field(name="🏦 Banka", value=f"{data['banka']:,}💰", inline=True)
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="çek", description="Bankadan para çek")
    @app_commands.describe(miktar="Miktar (veya 'hepsi')")
    async def slash_cek(self, interaction: discord.Interaction, miktar: str):
        data = get_economy(interaction.user.id)
        banka = data.get('banka', 0)
        
        if miktar.lower() in ['hepsi', 'all', 'tümü', 'hep']:
            miktar_int = banka
        else:
            try:
                miktar_int = int(miktar)
            except:
                await guvenli_cevap(interaction, "❌ Geçerli bir miktar gir!", ephemeral=True)
                return
        
        if miktar_int <= 0:
            await guvenli_cevap(interaction, "❌ Geçerli bir miktar gir!", ephemeral=True)
            return
        
        if banka < miktar_int:
            await guvenli_cevap(interaction, f"❌ Bankada yeterli para yok! (Banka: {banka:,}💰)", ephemeral=True)
            return
        
        data['banka'] -= miktar_int
        data['para'] += miktar_int
        update_economy(interaction.user.id, data)
        
        embed = discord.Embed(title="💵 Para Çekme", color=discord.Color.green())
        embed.description = f"**{miktar_int:,}💰** bankadan çekildi!"
        embed.add_field(name="💵 Cüzdan", value=f"{data['para']:,}💰", inline=True)
        embed.add_field(name="🏦 Banka", value=f"{data['banka']:,}💰", inline=True)
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="gönder", description="Birine para gönder")
    @app_commands.describe(member="Kime", miktar="Ne kadar")
    async def slash_gonder(self, interaction: discord.Interaction, member: discord.Member, miktar: int):
        if member.bot:
            await guvenli_cevap(interaction, "❌ Botlara para gönderemezsin!", ephemeral=True)
            return
        
        if member == interaction.user:
            await guvenli_cevap(interaction, "❌ Kendine para gönderemezsin!", ephemeral=True)
            return
        
        if miktar < 1:
            await guvenli_cevap(interaction, "❌ Geçerli bir miktar gir!", ephemeral=True)
            return
        
        data = get_economy(interaction.user.id)
        
        if data['para'] < miktar:
            await guvenli_cevap(interaction, f"❌ Yeterli paran yok! (Cüzdan: {data['para']:,}💰)", ephemeral=True)
            return
        
        data['para'] -= miktar
        update_economy(interaction.user.id, data)
        
        target_data = get_economy(member.id)
        target_data['para'] += miktar
        update_economy(member.id, target_data)
        
        embed = discord.Embed(title="💸 Para Transferi", color=discord.Color.green())
        embed.description = f"{interaction.user.mention} → {member.mention}"
        embed.add_field(name="💰 Miktar", value=f"{miktar:,}💰")
        embed.add_field(name="🎒 Kalan Bakiyen", value=f"{data['para']:,}💰")
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="soygun", description="Birini soymaya çalış (riskli!)")
    @app_commands.describe(member="Hedef")
    async def slash_soygun(self, interaction: discord.Interaction, member: discord.Member):
        if member.bot:
            await guvenli_cevap(interaction, "❌ Botları soyamazsın!", ephemeral=True)
            return
        
        if member == interaction.user:
            await guvenli_cevap(interaction, "❌ Kendini soyamazsın!", ephemeral=True)
            return
        
        data = get_economy(interaction.user.id)
        target_data = get_economy(member.id)
        simdi = datetime.now()
        
        if 'son_soygun' in data and data['son_soygun']:
            try:
                son = datetime.fromisoformat(data['son_soygun'])
                if simdi - son < timedelta(hours=1):
                    kalan = timedelta(hours=1) - (simdi - son)
                    dk = int(kalan.total_seconds() // 60)
                    await guvenli_cevap(interaction, f"🚔 Polisler seni arıyor! **{dk} dakika** bekle.", ephemeral=True)
                    return
            except:
                pass
        
        data['son_soygun'] = simdi.isoformat()
        
        if target_data['para'] < 200:
            update_economy(interaction.user.id, data)
            await guvenli_cevap(interaction, f"❌ {member.name} çok fakir, soyacak bir şey yok!")
            return
        
        if random.randint(1, 100) <= 25:
            calinan = random.randint(target_data['para'] // 10, target_data['para'] // 4)
            calinan = min(calinan, 5000)
            
            target_data['para'] -= calinan
            data['para'] += calinan
            
            update_economy(interaction.user.id, data)
            update_economy(member.id, target_data)
            
            embed = discord.Embed(title="🔫 Soygun Başarılı!", color=discord.Color.green())
            embed.description = f"{member.mention}'den **{calinan:,}💰** çaldın!"
            embed.add_field(name="🎒 Bakiyen", value=f"{data['para']:,}💰")
        else:
            ceza = random.randint(200, 500)
            ceza = min(ceza, data['para'])
            
            data['para'] -= ceza
            update_economy(interaction.user.id, data)
            
            embed = discord.Embed(title="🚔 Yakalandın!", color=discord.Color.red())
            embed.description = f"Polis seni yakaladı! **{ceza:,}💰** ceza ödedin!"
            embed.add_field(name="🎒 Bakiyen", value=f"{data['para']:,}💰")
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="zenginler", description="En zenginler listesi")
    async def slash_zenginler(self, interaction: discord.Interaction):
        all_data = get_all_economy()
        
        if not all_data:
            await guvenli_cevap(interaction, "📊 Henüz veri yok!")
            return
        
        siralama = sorted(
            all_data.items(),
            key=lambda x: x[1].get('para', 0) + x[1].get('banka', 0),
            reverse=True
        )[:10]
        
        embed = discord.Embed(title="💎 En Zenginler", color=discord.Color.gold())
        emojiler = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        
        text = ""
        for i, (user_id, user_data) in enumerate(siralama):
            try:
                user = await self.bot.fetch_user(int(user_id))
                toplam = user_data.get('para', 0) + user_data.get('banka', 0)
                text += f"{emojiler[i]} **{user.name}** - {toplam:,}💰\n"
            except:
                pass
        
        embed.description = text if text else "Henüz kimse yok!"
        await guvenli_cevap(interaction, embed=embed)

    # =====================================================
    # 💰 PREFIX KOMUTLARI
    # =====================================================

    @commands.command(aliases=['bal', 'para', 'cüzdan'])
    async def bakiye(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        data = get_economy(member.id)
        
        embed = discord.Embed(title=f"💰 {member.name}", color=discord.Color.gold())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="💵 Cüzdan", value=f"{data['para']:,}💰", inline=True)
        embed.add_field(name="🏦 Banka", value=f"{data.get('banka', 0):,}💰", inline=True)
        embed.add_field(name="💎 Toplam", value=f"{data['para'] + data.get('banka', 0):,}💰", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(aliases=['daily', 'günlük'])
    async def gunluk(self, ctx):
        data = get_economy(ctx.author.id)
        simdi = datetime.now()
        
        if 'son_gunluk' in data and data['son_gunluk']:
            try:
                son = datetime.fromisoformat(data['son_gunluk'])
                if simdi - son < timedelta(hours=24):
                    kalan = timedelta(hours=24) - (simdi - son)
                    saat = int(kalan.total_seconds() // 3600)
                    dk = int((kalan.total_seconds() % 3600) // 60)
                    await ctx.send(f"⏰ Bekle! **{saat}s {dk}dk** kaldı.")
                    return
            except:
                pass
        
        if 'streak' not in data:
            data['streak'] = 0
        
        if 'son_gunluk' in data and data['son_gunluk']:
            try:
                son = datetime.fromisoformat(data['son_gunluk'])
                if simdi - son < timedelta(hours=48):
                    data['streak'] += 1
                else:
                    data['streak'] = 1
            except:
                data['streak'] = 1
        else:
            data['streak'] = 1
        
        streak = min(data['streak'], 30)
        base = random.randint(200, 500)
        bonus = streak * 25
        toplam = base + bonus
        
        data['para'] += toplam
        data['son_gunluk'] = simdi.isoformat()
        update_economy(ctx.author.id, data)
        
        embed = discord.Embed(title="🎁 Günlük Ödül", color=discord.Color.gold())
        embed.add_field(name="💰 Temel", value=f"+{base}💰", inline=True)
        embed.add_field(name="🔥 Streak", value=f"+{bonus}💰 ({streak} gün)", inline=True)
        embed.add_field(name="💎 Toplam", value=f"+{toplam}💰", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(aliases=['free'])
    async def bedava(self, ctx):
        data = get_economy(ctx.author.id)
        simdi = datetime.now()
        
        if 'son_bedava' in data and data['son_bedava']:
            try:
                son = datetime.fromisoformat(data['son_bedava'])
                if simdi - son < timedelta(hours=2):
                    kalan = timedelta(hours=2) - (simdi - son)
                    dk = int(kalan.total_seconds() // 60)
                    await ctx.send(f"⏰ Bekle! **{dk} dakika** kaldı.")
                    return
            except:
                pass
        
        para = random.randint(50, 150)
        data['para'] += para
        data['son_bedava'] = simdi.isoformat()
        update_economy(ctx.author.id, data)
        
        await ctx.send(f"💸 Bedava: **+{para}💰**\n🎒 Bakiye: **{data['para']:,}💰**")

    @commands.command(aliases=['work', 'iş'])
    async def calis(self, ctx):
        data = get_economy(ctx.author.id)
        simdi = datetime.now()
        
        if 'son_calis' in data and data['son_calis']:
            try:
                son = datetime.fromisoformat(data['son_calis'])
                if simdi - son < timedelta(minutes=30):
                    kalan = timedelta(minutes=30) - (simdi - son)
                    dk = int(kalan.total_seconds() // 60)
                    await ctx.send(f"⏰ Dinleniyorsun! **{dk} dakika** bekle.")
                    return
            except:
                pass
        
        isler = [
            ("💻 Yazılım geliştirdin", 150, 250),
            ("🍕 Pizza dağıttın", 50, 100),
            ("🚗 Uber şoförlüğü yaptın", 80, 150),
            ("📦 Kargo taşıdın", 60, 120),
            ("🎨 Grafik tasarım yaptın", 120, 200),
        ]
        
        is_secim = random.choice(isler)
        kazanc = random.randint(is_secim[1], is_secim[2])
        data['para'] += kazanc
        data['son_calis'] = simdi.isoformat()
        update_economy(ctx.author.id, data)
        
        await ctx.send(f"{is_secim[0]} ve **+{kazanc}💰** kazandın!\n🎒 Bakiye: **{data['para']:,}💰**")

    @commands.command(aliases=['deposit'])
    async def yatir(self, ctx, miktar: str):
        data = get_economy(ctx.author.id)
        
        if miktar.lower() in ['hepsi', 'all', 'tümü']:
            miktar_int = data['para']
        else:
            try:
                miktar_int = int(miktar)
            except:
                await ctx.send("❌ Geçerli bir miktar gir!")
                return
        
        if miktar_int <= 0 or data['para'] < miktar_int:
            await ctx.send("❌ Yeterli paran yok!")
            return
        
        data['para'] -= miktar_int
        data['banka'] = data.get('banka', 0) + miktar_int
        update_economy(ctx.author.id, data)
        
        await ctx.send(f"🏦 **{miktar_int:,}💰** bankaya yatırıldı!")

    @commands.command(aliases=['withdraw'])
    async def cek(self, ctx, miktar: str):
        data = get_economy(ctx.author.id)
        banka = data.get('banka', 0)
        
        if miktar.lower() in ['hepsi', 'all', 'tümü']:
            miktar_int = banka
        else:
            try:
                miktar_int = int(miktar)
            except:
                await ctx.send("❌ Geçerli bir miktar gir!")
                return
        
        if miktar_int <= 0 or banka < miktar_int:
            await ctx.send("❌ Bankada yeterli para yok!")
            return
        
        data['banka'] -= miktar_int
        data['para'] += miktar_int
        update_economy(ctx.author.id, data)
        
        await ctx.send(f"💵 **{miktar_int:,}💰** bankadan çekildi!")

    @commands.command(aliases=['give', 'ver', 'transfer'])
    async def gonder(self, ctx, member: discord.Member, miktar: int):
        if member.bot or member == ctx.author:
            await ctx.send("❌ Geçersiz!")
            return
        
        data = get_economy(ctx.author.id)
        
        if miktar < 1 or data['para'] < miktar:
            await ctx.send("❌ Yeterli paran yok!")
            return
        
        data['para'] -= miktar
        update_economy(ctx.author.id, data)
        
        target_data = get_economy(member.id)
        target_data['para'] += miktar
        update_economy(member.id, target_data)
        
        await ctx.send(f"💸 {ctx.author.mention} → {member.mention}: **{miktar:,}💰**")

    @commands.command(aliases=['rob', 'soy'])
    async def soygun(self, ctx, member: discord.Member):
        if member.bot or member == ctx.author:
            await ctx.send("❌ Geçersiz hedef!")
            return
        
        data = get_economy(ctx.author.id)
        target_data = get_economy(member.id)
        simdi = datetime.now()
        
        if 'son_soygun' in data and data['son_soygun']:
            try:
                son = datetime.fromisoformat(data['son_soygun'])
                if simdi - son < timedelta(hours=1):
                    kalan = timedelta(hours=1) - (simdi - son)
                    dk = int(kalan.total_seconds() // 60)
                    await ctx.send(f"🚔 Polisler arıyor! **{dk} dakika** bekle.")
                    return
            except:
                pass
        
        data['son_soygun'] = simdi.isoformat()
        
        if target_data['para'] < 200:
            update_economy(ctx.author.id, data)
            await ctx.send(f"❌ {member.mention} çok fakir!")
            return
        
        if random.randint(1, 100) <= 25:
            calinan = random.randint(target_data['para'] // 10, target_data['para'] // 4)
            calinan = min(calinan, 5000)
            
            target_data['para'] -= calinan
            data['para'] += calinan
            
            update_economy(ctx.author.id, data)
            update_economy(member.id, target_data)
            
            await ctx.send(f"🔫 Soygun başarılı! {member.mention}'den **{calinan:,}💰** çaldın!")
        else:
            ceza = random.randint(200, 500)
            ceza = min(ceza, data['para'])
            data['para'] -= ceza
            update_economy(ctx.author.id, data)
            
            await ctx.send(f"🚔 Yakalandın! **{ceza:,}💰** ceza ödedin!")

    @commands.command(aliases=['lb', 'top', 'leaderboard'])
    async def zenginler(self, ctx):
        all_data = get_all_economy()
        
        if not all_data:
            await ctx.send("📊 Henüz veri yok!")
            return
        
        siralama = sorted(
            all_data.items(),
            key=lambda x: x[1].get('para', 0) + x[1].get('banka', 0),
            reverse=True
        )[:10]
        
        embed = discord.Embed(title="💎 En Zenginler", color=discord.Color.gold())
        emojiler = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        
        text = ""
        for i, (user_id, user_data) in enumerate(siralama):
            user = self.bot.get_user(int(user_id))
            toplam = user_data.get('para', 0) + user_data.get('banka', 0)
            if user:
                text += f"{emojiler[i]} **{user.name}** - {toplam:,}💰\n"
        
        embed.description = text if text else "Henüz kimse yok!"
        await ctx.send(embed=embed)

    # =====================================================
    # 👑 PATRON KOMUTLARI
    # =====================================================

    @commands.command()
    async def hediye(self, ctx, member: discord.Member, miktar: int):
        if ctx.author.id != PATRON_ID:
            await ctx.send("❌ Bu komutu sadece patron kullanabilir!")
            return
        
        data = get_economy(member.id)
        data['para'] += miktar
        update_economy(member.id, data)
        
        await ctx.send(f"✅ {member.mention} hesabına **{miktar:,}💰** yüklendi!\n🎒 Yeni bakiye: **{data['para']:,}💰**")

    @commands.command()
    async def paraal(self, ctx, member: discord.Member, miktar: int):
        if ctx.author.id != PATRON_ID:
            await ctx.send("❌ Bu komutu sadece patron kullanabilir!")
            return
        
        data = get_economy(member.id)
        data['para'] = max(0, data['para'] - miktar)
        update_economy(member.id, data)
        
        await ctx.send(f"✅ {member.mention} hesabından **{miktar:,}💰** alındı!\n🎒 Yeni bakiye: **{data['para']:,}💰**")

    @commands.command()
    async def resetpara(self, ctx, member: discord.Member):
        if ctx.author.id != PATRON_ID:
            await ctx.send("❌ Bu komutu sadece patron kullanabilir!")
            return
        
        data = {'para': 1000, 'banka': 0}
        update_economy(member.id, data)
        
        await ctx.send(f"✅ {member.mention} bakiyesi sıfırlandı! (1000💰)")

# =====================================================
# 🔧 COG YÜKLEME
# =====================================================

async def setup(bot):
    await bot.add_cog(Ekonomi(bot))