# =====================================================
# 🎮 WOWSY BOT - OYUN KOMUTLARI
# =====================================================

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import random
import asyncio

from config import economy_ref
from utils import guvenli_cevap

# =====================================================
# 💾 EKONOMİ FONKSİYONLARI (OYUNLAR İÇİN)
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

# =====================================================
# 🎮 OYUNLAR COG
# =====================================================

class Oyunlar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =====================================================
    # 🏹 AVLANMA
    # =====================================================

    @app_commands.command(name="hunt", description="Hayvan avla (2dk bekleme)")
    async def slash_hunt(self, interaction: discord.Interaction):
        data = get_economy(interaction.user.id)
        simdi = datetime.now()
        
        if 'son_hunt' in data and data['son_hunt']:
            try:
                son = datetime.fromisoformat(data['son_hunt'])
                if simdi - son < timedelta(minutes=2):
                    kalan = timedelta(minutes=2) - (simdi - son)
                    sn = int(kalan.total_seconds())
                    await guvenli_cevap(interaction, f"🏹 Silahını temizliyorsun! **{sn} saniye** bekle.", ephemeral=True)
                    return
            except:
                pass
        
        data['son_hunt'] = simdi.isoformat()
        
        if random.randint(1, 100) <= 15:
            update_economy(interaction.user.id, data)
            embed = discord.Embed(title="🏹 Avlanma", color=discord.Color.orange())
            embed.description = "💨 Hayvan kaçtı! Bir şey avlayamadın..."
            await guvenli_cevap(interaction, embed=embed)
            return
        
        hayvanlar = {
            '🐀': (10, 30, "Fare"),
            '🐇': (20, 50, "Tavşan"),
            '🦊': (40, 80, "Tilki"),
            '🐺': (60, 120, "Kurt"),
            '🐻': (100, 200, "Ayı"),
            '🦁': (150, 300, "Aslan"),
            '🐉': (400, 800, "Ejderha")
        }
        weights = [25, 22, 18, 15, 10, 7, 3]
        
        emoji, (min_p, max_p, isim) = random.choices(list(hayvanlar.items()), weights=weights)[0]
        para = random.randint(min_p, max_p)
        
        data['para'] += para
        update_economy(interaction.user.id, data)
        
        if isim == "Ejderha":
            renk = discord.Color.gold()
            desc = f"🎉 **EFSANE!** Bir **{isim}** {emoji} avladın!"
        elif isim in ["Aslan", "Ayı"]:
            renk = discord.Color.purple()
            desc = f"✨ **NADİR!** Bir **{isim}** {emoji} avladın!"
        else:
            renk = discord.Color.green()
            desc = f"Bir **{isim}** {emoji} avladın!"
        
        embed = discord.Embed(title="🏹 Avlanma", color=renk)
        embed.description = desc
        embed.add_field(name="💰 Kazanç", value=f"+{para}💰", inline=True)
        embed.add_field(name="🎒 Bakiye", value=f"{data['para']:,}💰", inline=True)
        
        await guvenli_cevap(interaction, embed=embed)

    @commands.command(aliases=['av'])
    async def hunt(self, ctx):
        data = get_economy(ctx.author.id)
        simdi = datetime.now()
        
        if 'son_hunt' in data and data['son_hunt']:
            try:
                son = datetime.fromisoformat(data['son_hunt'])
                if simdi - son < timedelta(minutes=2):
                    kalan = timedelta(minutes=2) - (simdi - son)
                    sn = int(kalan.total_seconds())
                    await ctx.send(f"🏹 Silahını temizliyorsun! **{sn} saniye** bekle.")
                    return
            except:
                pass
        
        data['son_hunt'] = simdi.isoformat()
        
        if random.randint(1, 100) <= 15:
            update_economy(ctx.author.id, data)
            await ctx.send("💨 Hayvan kaçtı! Bir şey avlayamadın...")
            return
        
        hayvanlar = {
            '🐀': (10, 30, "Fare"),
            '🐇': (20, 50, "Tavşan"),
            '🦊': (40, 80, "Tilki"),
            '🐺': (60, 120, "Kurt"),
            '🐻': (100, 200, "Ayı"),
            '🦁': (150, 300, "Aslan"),
            '🐉': (400, 800, "Ejderha")
        }
        weights = [25, 22, 18, 15, 10, 7, 3]
        
        emoji, (min_p, max_p, isim) = random.choices(list(hayvanlar.items()), weights=weights)[0]
        para = random.randint(min_p, max_p)
        
        data['para'] += para
        update_economy(ctx.author.id, data)
        
        embed = discord.Embed(title="🏹 Avlanma", color=discord.Color.green())
        embed.description = f"Bir **{isim}** {emoji} avladın!"
        embed.add_field(name="💰 Kazanç", value=f"+{para}💰", inline=True)
        embed.add_field(name="🎒 Bakiye", value=f"{data['para']:,}💰", inline=True)
        
        await ctx.send(embed=embed)

    # =====================================================
    # 🎣 BALIK TUTMA
    # =====================================================

    @app_commands.command(name="fish", description="Balık tut (3dk bekleme)")
    async def slash_fish(self, interaction: discord.Interaction):
        data = get_economy(interaction.user.id)
        simdi = datetime.now()
        
        if 'son_balik' in data and data['son_balik']:
            try:
                son = datetime.fromisoformat(data['son_balik'])
                if simdi - son < timedelta(minutes=3):
                    kalan = timedelta(minutes=3) - (simdi - son)
                    dk = int(kalan.total_seconds() // 60)
                    sn = int(kalan.total_seconds() % 60)
                    await guvenli_cevap(interaction, f"🎣 Oltanı hazırlıyorsun! **{dk}dk {sn}sn** bekle.", ephemeral=True)
                    return
            except:
                pass
        
        data['son_balik'] = simdi.isoformat()
        
        baliklar = [
            ('🗑️', 'Çöp', 0, 0, 12),
            ('🦐', 'Karides', 5, 20, 18),
            ('🐟', 'Balık', 20, 50, 25),
            ('🐠', 'Tropikal Balık', 40, 80, 18),
            ('🦑', 'Kalamar', 60, 120, 12),
            ('🐙', 'Ahtapot', 100, 180, 8),
            ('🦈', 'Köpekbalığı', 200, 400, 5),
            ('🐋', 'Balina', 600, 1200, 2),
        ]
        
        agirliklar = [b[4] for b in baliklar]
        yakalanan = random.choices(baliklar, weights=agirliklar)[0]
        emoji, isim, min_p, max_p, _ = yakalanan
        
        if min_p == 0:
            para = 0
            mesaj = f"💔 Sadece **{isim}** {emoji} çıktı..."
            renk = discord.Color.greyple()
        else:
            para = random.randint(min_p, max_p)
            data['para'] += para
            if isim == 'Balina':
                mesaj = f"🎉 **EFSANE!** Bir **{isim}** {emoji} yakaladın!"
                renk = discord.Color.gold()
            elif isim in ['Köpekbalığı', 'Ahtapot']:
                mesaj = f"✨ **NADİR!** Bir **{isim}** {emoji} yakaladın!"
                renk = discord.Color.purple()
            else:
                mesaj = f"Bir **{isim}** {emoji} yakaladın!"
                renk = discord.Color.blue()
        
        update_economy(interaction.user.id, data)
        
        embed = discord.Embed(title="🎣 Balık Tutma", color=renk)
        embed.description = mesaj
        if para > 0:
            embed.add_field(name="💰 Kazanç", value=f"+{para}💰", inline=True)
        embed.add_field(name="🎒 Bakiye", value=f"{data['para']:,}💰", inline=True)
        
        await guvenli_cevap(interaction, embed=embed)

    @commands.command(aliases=['balık', 'fishing'])
    async def fish(self, ctx):
        data = get_economy(ctx.author.id)
        simdi = datetime.now()
        
        if 'son_balik' in data and data['son_balik']:
            try:
                son = datetime.fromisoformat(data['son_balik'])
                if simdi - son < timedelta(minutes=3):
                    kalan = timedelta(minutes=3) - (simdi - son)
                    dk = int(kalan.total_seconds() // 60)
                    sn = int(kalan.total_seconds() % 60)
                    await ctx.send(f"🎣 Oltanı hazırlıyorsun! **{dk}dk {sn}sn** bekle.")
                    return
            except:
                pass
        
        data['son_balik'] = simdi.isoformat()
        
        baliklar = [
            ('🗑️', 'Çöp', 0, 0, 12),
            ('🦐', 'Karides', 5, 20, 18),
            ('🐟', 'Balık', 20, 50, 25),
            ('🐠', 'Tropikal', 40, 80, 18),
            ('🦑', 'Kalamar', 60, 120, 12),
            ('🐙', 'Ahtapot', 100, 180, 8),
            ('🦈', 'Köpekbalığı', 200, 400, 5),
            ('🐋', 'Balina', 600, 1200, 2),
        ]
        
        agirliklar = [b[4] for b in baliklar]
        yakalanan = random.choices(baliklar, weights=agirliklar)[0]
        emoji, isim, min_p, max_p, _ = yakalanan
        
        if min_p == 0:
            update_economy(ctx.author.id, data)
            await ctx.send(f"💔 Sadece **{isim}** {emoji} çıktı...")
            return
        
        para = random.randint(min_p, max_p)
        data['para'] += para
        update_economy(ctx.author.id, data)
        
        await ctx.send(f"🎣 Bir **{isim}** {emoji} yakaladın! **+{para}💰**\n🎒 Bakiye: **{data['para']:,}💰**")

    # =====================================================
    # 🎰 SLOT
    # =====================================================

    @app_commands.command(name="slot", description="Slot makinesi oyna")
    @app_commands.describe(bahis="Bahis miktarı (min: 10, max: 50000)")
    async def slash_slot(self, interaction: discord.Interaction, bahis: int):
        data = get_economy(interaction.user.id)
        
        if bahis < 10:
            await guvenli_cevap(interaction, "❌ Minimum bahis: **10💰**", ephemeral=True)
            return
        
        if bahis > 50000:
            await guvenli_cevap(interaction, "❌ Maximum bahis: **50,000💰**", ephemeral=True)
            return
        
        if data['para'] < bahis:
            await guvenli_cevap(interaction, f"❌ Yeterli paran yok! (Cüzdan: {data['para']:,}💰)", ephemeral=True)
            return
        
        data['para'] -= bahis
        emojiler = ['🍒', '🍋', '🍊', '🍇', '💎', '7️⃣']
        sans = random.randint(1, 100)
        
        if sans <= 2:
            secilen = random.choice(emojiler)
            sonuc = [secilen, secilen, secilen]
            if secilen == '💎':
                carpan = 50
            elif secilen == '7️⃣':
                carpan = 30
            elif secilen == '🍇':
                carpan = 15
            else:
                carpan = 10
            odul = bahis * carpan
            data['para'] += odul
            mesaj = f"🎉 **JACKPOT!** ({carpan}x)\n+{odul:,}💰"
            renk = discord.Color.gold()
        elif sans <= 18:
            secilen = random.choice(emojiler)
            diger = random.choice([e for e in emojiler if e != secilen])
            sonuc = [secilen, secilen, diger]
            random.shuffle(sonuc)
            carpan = 2
            odul = bahis * carpan
            data['para'] += odul
            mesaj = f"✨ **İkili!** ({carpan}x)\n+{odul:,}💰"
            renk = discord.Color.green()
        else:
            sonuc = random.sample(emojiler, 3)
            mesaj = f"😢 Kaybettin!\n-{bahis:,}💰"
            renk = discord.Color.red()
        
        update_economy(interaction.user.id, data)
        
        embed = discord.Embed(title="🎰 SLOT MAKİNESİ", color=renk)
        embed.description = f"**╔══════════╗**\n**║** {sonuc[0]} **│** {sonuc[1]} **│** {sonuc[2]} **║**\n**╚══════════╝**\n\n{mesaj}"
        embed.add_field(name="💰 Bakiye", value=f"{data['para']:,}💰")
        embed.set_footer(text=f"Bahis: {bahis:,}💰 | 💎=50x | 7️⃣=30x | 🍇=15x | Diğer=10x")
        
        await guvenli_cevap(interaction, embed=embed)

    @commands.command()
    async def slot(self, ctx, bahis: int = 10):
        data = get_economy(ctx.author.id)
        
        if bahis < 10:
            await ctx.send("❌ Minimum bahis: **10💰**")
            return
        
        if data['para'] < bahis:
            await ctx.send("❌ Yeterli paran yok!")
            return
        
        data['para'] -= bahis
        emojiler = ['🍒', '🍋', '🍊', '🍇', '💎', '7️⃣']
        sans = random.randint(1, 100)
        
        if sans <= 2:
            secilen = random.choice(emojiler)
            sonuc = [secilen, secilen, secilen]
            if secilen == '💎':
                carpan = 50
            elif secilen == '7️⃣':
                carpan = 30
            else:
                carpan = 10
            odul = bahis * carpan
            data['para'] += odul
            mesaj = f"🎉 **JACKPOT!** +{odul:,}💰"
            renk = discord.Color.gold()
        elif sans <= 18:
            secilen = random.choice(emojiler)
            diger = random.choice([e for e in emojiler if e != secilen])
            sonuc = [secilen, secilen, diger]
            random.shuffle(sonuc)
            odul = bahis * 2
            data['para'] += odul
            mesaj = f"✨ **İkili!** +{odul:,}💰"
            renk = discord.Color.green()
        else:
            sonuc = random.sample(emojiler, 3)
            mesaj = f"😢 Kaybettin! -{bahis:,}💰"
            renk = discord.Color.red()
        
        update_economy(ctx.author.id, data)
        
        embed = discord.Embed(title="🎰 SLOT", color=renk)
        embed.description = f"**[ {' | '.join(sonuc)} ]**\n\n{mesaj}"
        embed.add_field(name="💰 Bakiye", value=f"{data['para']:,}💰")
        
        await ctx.send(embed=embed)

    # =====================================================
    # 🪙 COINFLIP (DAHA AZ TEKRAR EDEN)
    # =====================================================

    @app_commands.command(name="coinflip", description="Yazı-tura bahis oyunu")
    @app_commands.describe(bahis="Bahis miktarı (min: 10)")
    async def slash_coinflip(self, interaction: discord.Interaction, bahis: int):
        data = get_economy(interaction.user.id)
        
        if bahis < 10:
            await guvenli_cevap(interaction, "❌ Minimum bahis: **10💰**", ephemeral=True)
            return
        
        if data['para'] < bahis:
            await guvenli_cevap(interaction, f"❌ Yeterli paran yok! (Cüzdan: {data['para']:,}💰)", ephemeral=True)
            return
        
        data['para'] -= bahis
        
        # Önceki sonucu kontrol et (varsa)
        onceki = data.get('son_coinflip_sonuc', None)
        
        # %70 ihtimalle farklı sonuç çıksın
        if onceki and random.randint(1, 100) <= 70:
            # Öncekinin tersi
            sonuc = "TURA" if onceki == "YAZI" else "YAZI"
        else:
            # Tamamen rastgele
            sonuc = random.choice(["YAZI", "TURA"])
        
        # Kazanma ihtimali %48 (adil)
        if random.randint(1, 100) <= 48:
            # Kazandın - gösterilen sonuç senin lehine
            odul = bahis * 2
            data['para'] += odul
            emoji = "🪙"
            mesaj = f"🎉 Kazandın! **+{odul:,}💰**"
            renk = discord.Color.green()
        else:
            # Kaybettin
            emoji = "💀"
            mesaj = f"😢 Kaybettin! **-{bahis:,}💰**"
            renk = discord.Color.red()
        
        # Son sonucu kaydet
        data['son_coinflip_sonuc'] = sonuc
        
        update_economy(interaction.user.id, data)
        
        embed = discord.Embed(title="🪙 Coinflip", color=renk)
        embed.description = f"{emoji} **{sonuc}**\n\n{mesaj}"
        embed.add_field(name="💰 Bakiye", value=f"{data['para']:,}💰")
        embed.set_footer(text=f"Bahis: {bahis:,}💰 | Kazanma şansı: %48")
        
        await guvenli_cevap(interaction, embed=embed)

    @commands.command(aliases=['cf', 'yazıtura'])
    async def coinflip(self, ctx, bahis: int):
        data = get_economy(ctx.author.id)
        
        if bahis < 10:
            await ctx.send("❌ Minimum bahis: **10💰**")
            return
        
        if data['para'] < bahis:
            await ctx.send("❌ Yeterli paran yok!")
            return
        
        data['para'] -= bahis
        
        onceki = data.get('son_coinflip_sonuc', None)
        
        if onceki and random.randint(1, 100) <= 70:
            sonuc = "TURA" if onceki == "YAZI" else "YAZI"
        else:
            sonuc = random.choice(["YAZI", "TURA"])
        
        if random.randint(1, 100) <= 48:
            odul = bahis * 2
            data['para'] += odul
            await ctx.send(f"🪙 **{sonuc}** - Kazandın! **+{odul:,}💰**\n🎒 Bakiye: **{data['para']:,}💰**")
        else:
            await ctx.send(f"💀 **{sonuc}** - Kaybettin! **-{bahis:,}💰**\n🎒 Bakiye: **{data['para']:,}💰**")
        
        data['son_coinflip_sonuc'] = sonuc
        update_economy(ctx.author.id, data)

    # =====================================================
    # 🎲 ZAR (YENİ SİSTEM)
    # =====================================================

    @app_commands.command(name="dice", description="Zarla bahis - Yüksek sayı kazan!")
    @app_commands.describe(bahis="Bahis miktarı (min: 10)")
    async def slash_dice(self, interaction: discord.Interaction, bahis: int):
        data = get_economy(interaction.user.id)
        
        if bahis < 10:
            await guvenli_cevap(interaction, "❌ Minimum bahis: **10💰**", ephemeral=True)
            return
        
        if data['para'] < bahis:
            await guvenli_cevap(interaction, f"❌ Yeterli paran yok! (Cüzdan: {data['para']:,}💰)", ephemeral=True)
            return
        
        data['para'] -= bahis
        zar = random.randint(1, 6)
        zar_emojiler = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅']
        zar_emoji = zar_emojiler[zar - 1]
        
        if zar == 6:
            carpan = 3
            odul = bahis * carpan
            data['para'] += odul
            mesaj = f"🎉 **ALTIN 6!** ({carpan}x)\n+{odul:,}💰"
            renk = discord.Color.gold()
        elif zar == 5:
            carpan = 1.5
            odul = int(bahis * carpan)
            data['para'] += odul
            mesaj = f"✨ **Güzel!** ({carpan}x)\n+{odul:,}💰"
            renk = discord.Color.green()
        elif zar == 4:
            carpan = 1
            odul = bahis  # Bahis geri dönüyor
            data['para'] += odul
            mesaj = f"👍 **İdare eder!** ({carpan}x)\nBahis iade: +{odul:,}💰"
            renk = discord.Color.blue()
        elif zar in [1, 2]:
            # 1-2: Ekstra ceza
            ceza_ek = bahis // 2  # Bahisin yarısı kadar ekstra
            data['para'] = max(0, data['para'] - ceza_ek)  # Ekstra düş
            mesaj = f"💀 **ÇOK KÖTÜ!** ({zar})\nEkstra ceza: -{bahis + ceza_ek:,}💰"
            renk = discord.Color.dark_red()
        else:  # 3
            mesaj = f"😢 Kaybettin!\n-{bahis:,}💰"
            renk = discord.Color.red()
        
        update_economy(interaction.user.id, data)
        
        embed = discord.Embed(title="🎲 Zar Bahis", color=renk)
        embed.description = f"**{zar_emoji} = {zar}**\n\n{mesaj}"
        embed.add_field(name="💰 Bakiye", value=f"{data['para']:,}💰")
        embed.set_footer(text="6=3x | 5=1.5x | 4=İade | 3=Kayıp | 1-2=Ekstra Ceza!")
        
        await guvenli_cevap(interaction, embed=embed)

    @commands.command(aliases=['zar'])
    async def dice(self, ctx, bahis: int):
        data = get_economy(ctx.author.id)
        
        if bahis < 10:
            await ctx.send("❌ Minimum bahis: **10💰**")
            return
        
        if data['para'] < bahis:
            await ctx.send("❌ Yeterli paran yok!")
            return
        
        data['para'] -= bahis
        zar = random.randint(1, 6)
        
        if zar == 6:
            odul = bahis * 3
            data['para'] += odul
            mesaj = f"🎲 **{zar}** - ALTIN 6! **+{odul:,}💰**"
        elif zar == 5:
            odul = int(bahis * 1.5)
            data['para'] += odul
            mesaj = f"🎲 **{zar}** - Güzel! **+{odul:,}💰**"
        elif zar == 4:
            odul = bahis
            data['para'] += odul
            mesaj = f"🎲 **{zar}** - İade! **+{odul:,}💰**"
        elif zar in [1, 2]:
            ceza_ek = bahis // 2
            data['para'] = max(0, data['para'] - ceza_ek)
            mesaj = f"🎲 **{zar}** - ÇOK KÖTÜ! Ekstra ceza: **-{bahis + ceza_ek:,}💰**"
        else:
            mesaj = f"🎲 **{zar}** - Kaybettin! **-{bahis:,}💰**"
        
        update_economy(ctx.author.id, data)
        await ctx.send(f"{mesaj}\n🎒 Bakiye: **{data['para']:,}💰**")

    # =====================================================
    # 🎡 RULET
    # =====================================================

    @app_commands.command(name="roulette", description="Rulet oyna")
    @app_commands.describe(bahis="Bahis miktarı (min: 10)", renk="Renk seç")
    @app_commands.choices(renk=[
        app_commands.Choice(name="🔴 Kırmızı (2x)", value="kırmızı"),
        app_commands.Choice(name="⚫ Siyah (2x)", value="siyah"),
        app_commands.Choice(name="🟢 Yeşil (14x)", value="yeşil")
    ])
    async def slash_roulette(self, interaction: discord.Interaction, bahis: int, renk: str):
        data = get_economy(interaction.user.id)
        
        if bahis < 10:
            await guvenli_cevap(interaction, "❌ Minimum bahis: **10💰**", ephemeral=True)
            return
        
        if data['para'] < bahis:
            await guvenli_cevap(interaction, f"❌ Yeterli paran yok! (Cüzdan: {data['para']:,}💰)", ephemeral=True)
            return
        
        data['para'] -= bahis
        
        sans = random.randint(1, 100)
        if sans <= 5:
            sonuc = 'yeşil'
            emoji = '🟢'
        elif sans <= 52:
            sonuc = 'kırmızı'
            emoji = '🔴'
        else:
            sonuc = 'siyah'
            emoji = '⚫'
        
        if sonuc == renk:
            if sonuc == 'yeşil':
                carpan = 14
            else:
                carpan = 2
            odul = bahis * carpan
            data['para'] += odul
            mesaj = f"🎉 Kazandın! ({carpan}x)\n+{odul:,}💰"
            renk_embed = discord.Color.green()
        else:
            mesaj = f"😢 Kaybettin!\n-{bahis:,}💰"
            renk_embed = discord.Color.red()
        
        update_economy(interaction.user.id, data)
        
        embed = discord.Embed(title="🎡 Rulet", color=renk_embed)
        embed.description = f"{emoji} **{sonuc.upper()}**\n\n{mesaj}"
        embed.add_field(name="🎯 Seçimin", value=renk.capitalize(), inline=True)
        embed.add_field(name="💰 Bakiye", value=f"{data['para']:,}💰", inline=True)
        
        await guvenli_cevap(interaction, embed=embed)

    @commands.command(aliases=['rulet'])
    async def roulette(self, ctx, bahis: int, renk: str):
        renk = renk.lower()
        if renk in ['kırmızı', 'k', 'red', 'r']:
            renk = 'kırmızı'
        elif renk in ['siyah', 's', 'black', 'b']:
            renk = 'siyah'
        elif renk in ['yeşil', 'y', 'green', 'g']:
            renk = 'yeşil'
        else:
            await ctx.send("❌ Renk seç: `kırmızı`, `siyah` veya `yeşil`")
            return
        
        data = get_economy(ctx.author.id)
        
        if bahis < 10:
            await ctx.send("❌ Minimum bahis: **10💰**")
            return
        
        if data['para'] < bahis:
            await ctx.send("❌ Yeterli paran yok!")
            return
        
        data['para'] -= bahis
        
        sans = random.randint(1, 100)
        if sans <= 5:
            sonuc = 'yeşil'
            emoji = '🟢'
        elif sans <= 52:
            sonuc = 'kırmızı'
            emoji = '🔴'
        else:
            sonuc = 'siyah'
            emoji = '⚫'
        
        if sonuc == renk:
            if sonuc == 'yeşil':
                odul = bahis * 14
            else:
                odul = bahis * 2
            data['para'] += odul
            mesaj = f"🎉 Kazandın! **+{odul:,}💰**"
        else:
            mesaj = f"😢 Kaybettin! **-{bahis:,}💰**"
        
        update_economy(ctx.author.id, data)
        await ctx.send(f"🎡 {emoji} **{sonuc.upper()}**\n{mesaj}\n🎒 Bakiye: **{data['para']:,}💰**")

    # =====================================================
    # 🃏 BLACKJACK (REACTİON İLE)
    # =====================================================

    @app_commands.command(name="blackjack", description="21 kart oyunu")
    @app_commands.describe(bahis="Bahis miktarı (min: 10)")
    async def slash_blackjack(self, interaction: discord.Interaction, bahis: int):
        data = get_economy(interaction.user.id)
        
        if bahis < 10:
            await guvenli_cevap(interaction, "❌ Minimum bahis: **10💰**", ephemeral=True)
            return
        
        if data['para'] < bahis:
            await guvenli_cevap(interaction, f"❌ Yeterli paran yok! (Cüzdan: {data['para']:,}💰)", ephemeral=True)
            return
        
        data['para'] -= bahis
        
        kartlar = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        semboller = ['♠', '♥', '♦', '♣']
        
        def kart_cek():
            return random.choice(kartlar), random.choice(semboller)
        
        def hesapla(el):
            toplam = 0
            as_sayisi = 0
            for kart, _ in el:
                if kart in ['J', 'Q', 'K']:
                    toplam += 10
                elif kart == 'A':
                    toplam += 11
                    as_sayisi += 1
                else:
                    toplam += int(kart)
            while toplam > 21 and as_sayisi > 0:
                toplam -= 10
                as_sayisi -= 1
            return toplam
        
        def el_goster(el):
            return ' '.join([f"`{k}{s}`" for k, s in el])
        
        oyuncu = [kart_cek(), kart_cek()]
        kurpiye = [kart_cek(), kart_cek()]
        oyuncu_toplam = hesapla(oyuncu)
        
        if oyuncu_toplam == 21:
            carpan = 2.5
            odul = int(bahis * carpan)
            data['para'] += odul
            update_economy(interaction.user.id, data)
            
            embed = discord.Embed(title="🃏 BLACKJACK!", color=discord.Color.gold())
            embed.description = f"**🎴 Elin:** {el_goster(oyuncu)} = **21**\n\n🎉 **BLACKJACK!** (2.5x)\n+{odul:,}💰"
            embed.add_field(name="💰 Bakiye", value=f"{data['para']:,}💰")
            await guvenli_cevap(interaction, embed=embed)
            return
        
        embed = discord.Embed(title="🃏 Blackjack", color=discord.Color.blue())
        embed.add_field(name="🎴 Senin Elin", value=f"{el_goster(oyuncu)} = **{oyuncu_toplam}**", inline=False)
        embed.add_field(name="🎩 Kurpiye", value=f"`{kurpiye[0][0]}{kurpiye[0][1]}` `❓`", inline=False)
        embed.add_field(name="💰 Bahis", value=f"{bahis:,}💰", inline=True)
        embed.set_footer(text="🃏 = Kart Çek | 🛑 = Dur (30 saniye)")
        
        await guvenli_cevap(interaction, embed=embed)
        
        # Mesajı al ve reaction ekle
        msg = await interaction.original_response()
        await msg.add_reaction('🃏')
        await msg.add_reaction('🛑')
        
        def check(reaction, user):
            return (user.id == interaction.user.id and 
                    str(reaction.emoji) in ['🃏', '🛑'] and
                    reaction.message.id == msg.id)
        
        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=30)
                
                if str(reaction.emoji) == '🃏':
                    # Kart çek
                    oyuncu.append(kart_cek())
                    oyuncu_toplam = hesapla(oyuncu)
                    
                    embed = discord.Embed(title="🃏 Blackjack", color=discord.Color.blue())
                    embed.add_field(name="🎴 Senin Elin", value=f"{el_goster(oyuncu)} = **{oyuncu_toplam}**", inline=False)
                    embed.add_field(name="🎩 Kurpiye", value=f"`{kurpiye[0][0]}{kurpiye[0][1]}` `❓`", inline=False)
                    embed.set_footer(text="🃏 = Kart Çek | 🛑 = Dur")
                    
                    await msg.edit(embed=embed)
                    await msg.remove_reaction(reaction, user)
                    
                    if oyuncu_toplam > 21:
                        update_economy(interaction.user.id, data)
                        embed = discord.Embed(title="🃏 Blackjack", color=discord.Color.red())
                        embed.add_field(name="🎴 Senin Elin", value=f"{el_goster(oyuncu)} = **{oyuncu_toplam}**", inline=False)
                        embed.description = f"💥 **BATTIN!**\n-{bahis:,}💰"
                        embed.add_field(name="💰 Bakiye", value=f"{data['para']:,}💰")
                        await msg.clear_reactions()
                        await msg.edit(embed=embed)
                        return
                    
                    if oyuncu_toplam == 21:
                        break
                else:
                    # Dur
                    break
                    
            except asyncio.TimeoutError:
                update_economy(interaction.user.id, data)
                embed = discord.Embed(title="🃏 Blackjack", color=discord.Color.red())
                embed.description = f"⏰ **Süre doldu!**\n-{bahis:,}💰"
                embed.add_field(name="💰 Bakiye", value=f"{data['para']:,}💰")
                await msg.clear_reactions()
                await msg.edit(embed=embed)
                return
        
        # Kurpiye oynuyor
        kurpiye_toplam = hesapla(kurpiye)
        while kurpiye_toplam < 17:
            kurpiye.append(kart_cek())
            kurpiye_toplam = hesapla(kurpiye)
        
        if kurpiye_toplam > 21:
            carpan = 2
            odul = bahis * carpan
            data['para'] += odul
            sonuc = f"🎉 **Kurpiye battı!** (2x)\n+{odul:,}💰"
            renk = discord.Color.green()
        elif oyuncu_toplam > kurpiye_toplam:
            carpan = 2
            odul = bahis * carpan
            data['para'] += odul
            sonuc = f"🎉 **Kazandın!** (2x)\n+{odul:,}💰"
            renk = discord.Color.green()
        elif oyuncu_toplam < kurpiye_toplam:
            sonuc = f"😢 **Kaybettin!**\n-{bahis:,}💰"
            renk = discord.Color.red()
        else:
            data['para'] += bahis
            sonuc = f"🤝 **Berabere!**\nBahis iade edildi."
            renk = discord.Color.greyple()
        
        update_economy(interaction.user.id, data)
        
        embed = discord.Embed(title="🃏 Blackjack - Sonuç", color=renk)
        embed.add_field(name="🎴 Senin Elin", value=f"{el_goster(oyuncu)} = **{oyuncu_toplam}**", inline=False)
        embed.add_field(name="🎩 Kurpiye", value=f"{el_goster(kurpiye)} = **{kurpiye_toplam}**", inline=False)
        embed.description = sonuc
        embed.add_field(name="💰 Bakiye", value=f"{data['para']:,}💰")
        
        await msg.clear_reactions()
        await msg.edit(embed=embed)

    @commands.command(aliases=['bj', '21'])
    async def blackjack(self, ctx, bahis: int):
        await ctx.send("💡 Blackjack için `/blackjack` slash komutunu kullan!")

    # =====================================================
    # 🚀 CRASH (DÜZELTİLMİŞ)
    # =====================================================

    @app_commands.command(name="crash", description="Çarpan yükselir, patlamadan çek!")
    @app_commands.describe(bahis="Bahis miktarı (min: 10)")
    async def slash_crash(self, interaction: discord.Interaction, bahis: int):
        data = get_economy(interaction.user.id)
        
        if bahis < 10:
            await guvenli_cevap(interaction, "❌ Minimum bahis: **10💰**", ephemeral=True)
            return
        
        if data['para'] < bahis:
            await guvenli_cevap(interaction, f"❌ Yeterli paran yok! (Cüzdan: {data['para']:,}💰)", ephemeral=True)
            return
        
        data['para'] -= bahis
        
        # Patlama noktası belirleme (daha dengeli)
        sans = random.randint(1, 100)
        if sans <= 40:
            patlama = round(random.uniform(1.05, 1.4), 2)
        elif sans <= 70:
            patlama = round(random.uniform(1.35, 2.2), 2)
        elif sans <= 90:
            patlama = round(random.uniform(2.0, 4.0), 2)
        elif sans <= 97:
            patlama = round(random.uniform(3.5, 7.0), 2)
        else:
            patlama = round(random.uniform(6.0, 12.0), 2)
        
        carpan = 1.00
        
        embed = discord.Embed(title="🚀 Crash", color=discord.Color.green())
        embed.description = f"📈 Çarpan: **{carpan}x**\n💰 Bahis: **{bahis:,}💰**\n💵 Potansiyel: **{int(bahis * carpan):,}💰**\n\n🚀 **Reaction ile çek:** (30sn)"
        
        await guvenli_cevap(interaction, embed=embed)
        
        # Mesajı al ve reaction ekle
        msg = await interaction.original_response()
        await msg.add_reaction('🚀')
        
        def check(reaction, user):
            return (user.id == interaction.user.id and 
                    str(reaction.emoji) == '🚀' and
                    reaction.message.id == msg.id)
        
        cekildi = False
        patladi = False
        
        while carpan < patlama and not cekildi:
            await asyncio.sleep(0.9)
            
            # Çarpan artışı (daha yavaş)
            artis = random.uniform(0.05, 0.25)
            carpan = round(carpan + artis, 2)
            
            # Patladı mı kontrolü
            if carpan >= patlama:
                patladi = True
                break
            
            if carpan < 1.5:
                renk = discord.Color.green()
            elif carpan < 2.5:
                renk = discord.Color.blue()
            elif carpan < 4.0:
                renk = discord.Color.gold()
            else:
                renk = discord.Color.purple()
            
            potansiyel = int(bahis * carpan)
            
            embed = discord.Embed(title="🚀 Crash", color=renk)
            embed.description = f"📈 Çarpan: **{carpan}x**\n💰 Bahis: **{bahis:,}💰**\n💵 Potansiyel: **{potansiyel:,}💰**\n\n🚀 **Reaction ile çek!**"
            
            try:
                await msg.edit(embed=embed)
            except:
                pass
            
            # Reaction kontrolü (non-blocking)
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=0.8)
                cekildi = True
                break
            except asyncio.TimeoutError:
                continue
        
        # Sonuç
        if patladi and not cekildi:
            # Patladı
            update_economy(interaction.user.id, data)
            
            embed = discord.Embed(title="🚀 Crash", color=discord.Color.red())
            embed.description = f"💥 **PATLADI!** ({patlama}x'de)\n\n😢 **-{bahis:,}💰** kaybettin!"
            embed.add_field(name="💰 Bakiye", value=f"{data['para']:,}💰")
            
            try:
                await msg.clear_reactions()
            except:
                pass
            await msg.edit(embed=embed)
            
        elif cekildi:
            # Çekildi
            odul = int(bahis * carpan)
            data['para'] += odul
            kar = odul - bahis
            update_economy(interaction.user.id, data)
            
            embed = discord.Embed(title="🚀 Crash", color=discord.Color.green())
            embed.description = f"✅ **{carpan}x** çarpanında çektin!\n\n🎉 **+{kar:,}💰** kar!\nToplam: +{odul:,}💰"
            embed.add_field(name="💰 Bakiye", value=f"{data['para']:,}💰")
            embed.set_footer(text=f"Patlama noktası: {patlama}x idi")
            
            try:
                await msg.clear_reactions()
            except:
                pass
            await msg.edit(embed=embed)

    @commands.command()
    async def crash(self, ctx, bahis: int):
        await ctx.send("💡 Crash için `/crash` slash komutunu kullan!")

    # =====================================================
    # ⚔️ BATTLE
    # =====================================================

    @app_commands.command(name="battle", description="Bahisli PvP savaş")
    @app_commands.describe(member="Rakip", bahis="Bahis miktarı (min: 50)")
    async def slash_battle(self, interaction: discord.Interaction, member: discord.Member, bahis: int = 100):
        if member.bot:
            await guvenli_cevap(interaction, "❌ Botlarla savaşamazsın!", ephemeral=True)
            return
        
        if member == interaction.user:
            await guvenli_cevap(interaction, "❌ Kendinle savaşamazsın!", ephemeral=True)
            return
        
        if bahis < 50:
            await guvenli_cevap(interaction, "❌ Minimum bahis: **50💰**", ephemeral=True)
            return
        
        data1 = get_economy(interaction.user.id)
        data2 = get_economy(member.id)
        
        if data1['para'] < bahis:
            await guvenli_cevap(interaction, f"❌ Yeterli paran yok! (Gereken: {bahis:,}💰)", ephemeral=True)
            return
        
        if data2['para'] < bahis:
            await guvenli_cevap(interaction, f"❌ {member.name}'in yeterli parası yok! (Gereken: {bahis:,}💰)", ephemeral=True)
            return
        
        data1['para'] -= bahis
        data2['para'] -= bahis
        toplam_odul = bahis * 2
        
        await guvenli_cevap(interaction, 
            f"⚔️ **SAVAŞ BAŞLIYOR!**\n"
            f"💰 Ödül Havuzu: **{toplam_odul:,}💰**\n\n"
            f"❤️ {interaction.user.name}: 100 HP\n"
            f"❤️ {member.name}: 100 HP"
        )
        
        can1, can2 = 100, 100
        
        while can1 > 0 and can2 > 0:
            await asyncio.sleep(1.2)
            
            h1 = random.randint(15, 35)
            h2 = random.randint(15, 35)
            
            if random.randint(1, 100) <= 10:
                h1 = int(h1 * 1.5)
                krit1 = " 💥"
            else:
                krit1 = ""
                
            if random.randint(1, 100) <= 10:
                h2 = int(h2 * 1.5)
                krit2 = " 💥"
            else:
                krit2 = ""
            
            can2 = max(0, can2 - h1)
            can1 = max(0, can1 - h2)
            
            bar1 = "🟥" * (can1 // 10) + "⬛" * (10 - can1 // 10)
            bar2 = "🟥" * (can2 // 10) + "⬛" * (10 - can2 // 10)
            
            await interaction.edit_original_response(
                content=f"⚔️ **SAVAŞ!**\n"
                        f"💰 Ödül: **{toplam_odul:,}💰**\n\n"
                        f"{interaction.user.name}: {bar1} {can1}HP (-{h2}{krit2})\n"
                        f"{member.name}: {bar2} {can2}HP (-{h1}{krit1})"
            )
        
        if can1 > can2:
            kazanan = interaction.user
            kaybeden = member
            data1['para'] += toplam_odul
        elif can2 > can1:
            kazanan = member
            kaybeden = interaction.user
            data2['para'] += toplam_odul
        else:
            data1['para'] += bahis
            data2['para'] += bahis
            update_economy(interaction.user.id, data1)
            update_economy(member.id, data2)
            
            embed = discord.Embed(title="⚔️ SAVAŞ BİTTİ!", color=discord.Color.greyple())
            embed.description = f"🤝 **BERABERE!**\nBahisler iade edildi."
            await interaction.edit_original_response(content=None, embed=embed)
            return
        
        update_economy(interaction.user.id, data1)
        update_economy(member.id, data2)
        
        embed = discord.Embed(title="⚔️ SAVAŞ BİTTİ!", color=discord.Color.gold())
        embed.add_field(name="🏆 Kazanan", value=kazanan.mention, inline=True)
        embed.add_field(name="💀 Kaybeden", value=kaybeden.mention, inline=True)
        embed.add_field(name="💰 Ödül", value=f"+{toplam_odul:,}💰", inline=True)
        
        await interaction.edit_original_response(content=None, embed=embed)

    @commands.command(aliases=['savaş', 'pvp', 'duel'])
    async def battle(self, ctx, member: discord.Member, bahis: int = 100):
        await ctx.send(f"💡 Battle için `/battle @{member.name} {bahis}` slash komutunu kullan!")

# =====================================================
# 🔧 COG YÜKLEME
# =====================================================

async def setup(bot):
    await bot.add_cog(Oyunlar(bot))
