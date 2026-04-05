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

FAIZ_ORANI = 0.02          # %2 faiz
FAIZ_SURE_SAAT = 6         # Her 6 saatte bir faiz işler
MAX_FAIZ_BIRIKIM = 50000   # Tek seferde max alınabilecek faiz

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

def hesapla_faiz(data):
    """Birikmiş faizi hesapla (henüz ekleme, sadece hesap)"""
    banka = data.get('banka', 0)
    if banka <= 0:
        return 0, 0

    simdi = datetime.now()
    son_faiz_str = data.get('son_faiz')

    if not son_faiz_str:
        return 0, 0

    try:
        son_faiz = datetime.fromisoformat(son_faiz_str)
    except:
        return 0, 0

    gecen_saat = (simdi - son_faiz).total_seconds() / 3600
    faiz_periyot = int(gecen_saat // FAIZ_SURE_SAAT)

    if faiz_periyot <= 0:
        return 0, 0

    # Bileşik faiz hesabı
    toplam_faiz = 0
    gecici_banka = banka
    for _ in range(faiz_periyot):
        kazanc = int(gecici_banka * FAIZ_ORANI)
        toplam_faiz += kazanc
        gecici_banka += kazanc

    toplam_faiz = min(toplam_faiz, MAX_FAIZ_BIRIKIM)
    return toplam_faiz, faiz_periyot

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

        # Bekleyen faiz varsa göster
        bekleyen_faiz, _ = hesapla_faiz(data)

        embed = discord.Embed(title=f"💰 {member.name}", color=discord.Color.gold())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="💵 Cüzdan", value=f"{data['para']:,}💰", inline=True)
        embed.add_field(name="🏦 Banka", value=f"{data.get('banka', 0):,}💰", inline=True)
        embed.add_field(name="💎 Toplam", value=f"{data['para'] + data.get('banka', 0):,}💰", inline=True)

        if bekleyen_faiz > 0:
            embed.add_field(
                name="📈 Bekleyen Faiz",
                value=f"+{bekleyen_faiz:,}💰 (`/faiz` ile topla!)",
                inline=False
            )

        embed.set_footer(text=f"🏦 Faiz oranı: %{int(FAIZ_ORANI*100)} / {FAIZ_SURE_SAAT} saat")
        await guvenli_cevap(interaction, embed=embed)

    # =====================================================
    # 📈 FAİZ SİSTEMİ
    # =====================================================

    @app_commands.command(name="faiz", description="Bankadaki paranın faizini topla")
    async def slash_faiz(self, interaction: discord.Interaction):
        data = get_economy(interaction.user.id)
        banka = data.get('banka', 0)

        if banka <= 0:
            embed = discord.Embed(title="🏦 Faiz", color=discord.Color.red())
            embed.description = "❌ Bankada paran yok ki faiz işlesin!\n`/yatır` ile bankaya para koy, faiz kazanmaya başla."
            await guvenli_cevap(interaction, embed=embed, ephemeral=True)
            return

        # İlk kez faiz topluyorsa başlangıç ayarla
        if not data.get('son_faiz'):
            data['son_faiz'] = datetime.now().isoformat()
            update_economy(interaction.user.id, data)
            embed = discord.Embed(title="🏦 Faiz Sistemi Aktif!", color=discord.Color.green())
            embed.description = (
                f"✅ Faiz sayacın başlatıldı!\n\n"
                f"📊 **Oran:** %{int(FAIZ_ORANI*100)} / {FAIZ_SURE_SAAT} saat\n"
                f"🏦 **Bankadaki paran:** {banka:,}💰\n"
                f"⏰ **{FAIZ_SURE_SAAT} saat sonra** tekrar gel ve faizini topla!"
            )
            await guvenli_cevap(interaction, embed=embed)
            return

        faiz_miktari, periyot = hesapla_faiz(data)

        if faiz_miktari <= 0:
            # Kalan süreyi hesapla
            try:
                son_faiz = datetime.fromisoformat(data['son_faiz'])
                gecen = datetime.now() - son_faiz
                kalan = timedelta(hours=FAIZ_SURE_SAAT) - gecen
                if kalan.total_seconds() > 0:
                    saat = int(kalan.total_seconds() // 3600)
                    dk = int((kalan.total_seconds() % 3600) // 60)
                    sure_text = f"**{saat}s {dk}dk**" if saat > 0 else f"**{dk}dk**"
                else:
                    sure_text = "**az kaldı**"
            except:
                sure_text = "**biraz**"

            embed = discord.Embed(title="🏦 Faiz", color=discord.Color.orange())
            embed.description = (
                f"⏰ Henüz faiz birikmedi!\n"
                f"Bir sonraki faiz için {sure_text} bekle.\n\n"
                f"📊 **Oran:** %{int(FAIZ_ORANI*100)} / {FAIZ_SURE_SAAT} saat\n"
                f"🏦 **Banka:** {banka:,}💰"
            )
            await guvenli_cevap(interaction, embed=embed, ephemeral=True)
            return

        # Faizi bankaya ekle
        data['banka'] += faiz_miktari
        data['son_faiz'] = datetime.now().isoformat()

        # Toplam faiz istatistiği
        data['toplam_faiz_kazanc'] = data.get('toplam_faiz_kazanc', 0) + faiz_miktari

        update_economy(interaction.user.id, data)

        embed = discord.Embed(title="📈 Faiz Toplandı!", color=discord.Color.green())
        embed.description = f"**+{faiz_miktari:,}💰** faiz kazandın!"
        embed.add_field(name="⏱️ Periyot", value=f"{periyot}x ({periyot * FAIZ_SURE_SAAT} saat)", inline=True)
        embed.add_field(name="📊 Oran", value=f"%{int(FAIZ_ORANI*100)} / {FAIZ_SURE_SAAT}sa", inline=True)
        embed.add_field(name="🏦 Yeni Banka", value=f"{data['banka']:,}💰", inline=True)
        embed.add_field(
            name="📉 Toplam Faiz Kazancın",
            value=f"{data.get('toplam_faiz_kazanc', 0):,}💰",
            inline=False
        )
        embed.set_footer(text=f"💡 Bankada ne kadar çok para tutarsan, o kadar çok faiz kazanırsın!")

        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="faiz-bilgi", description="Faiz sistemi hakkında bilgi al")
    async def slash_faiz_bilgi(self, interaction: discord.Interaction):
        data = get_economy(interaction.user.id)
        banka = data.get('banka', 0)

        # Örnek hesaplamalar
        ornek_6s = int(banka * FAIZ_ORANI) if banka > 0 else 0
        ornek_1g = 0
        gecici = banka
        for _ in range(int(24 / FAIZ_SURE_SAAT)):
            k = int(gecici * FAIZ_ORANI)
            ornek_1g += k
            gecici += k

        ornek_7g = 0
        gecici = banka
        for _ in range(int(24 / FAIZ_SURE_SAAT * 7)):
            k = int(gecici * FAIZ_ORANI)
            ornek_7g += k
            gecici += k

        embed = discord.Embed(title="📊 Faiz Sistemi Rehberi", color=discord.Color.blue())
        embed.description = (
            "Bankadaki paran otomatik olarak faiz kazanır!\n"
            "Faizini toplamak için `/faiz` komutunu kullan.\n"
        )
        embed.add_field(
            name="⚙️ Ayarlar",
            value=(
                f"📈 **Oran:** %{int(FAIZ_ORANI*100)} (bileşik faiz)\n"
                f"⏰ **Periyot:** Her {FAIZ_SURE_SAAT} saatte bir\n"
                f"🔝 **Max tek seferde:** {MAX_FAIZ_BIRIKIM:,}💰\n"
            ),
            inline=False
        )

        if banka > 0:
            embed.add_field(
                name=f"💰 Senin Tahminlerin ({banka:,}💰 banka)",
                value=(
                    f"⏱️ {FAIZ_SURE_SAAT} saatte: ~**{ornek_6s:,}💰**\n"
                    f"📅 1 günde: ~**{ornek_1g:,}💰**\n"
                    f"📅 7 günde: ~**{ornek_7g:,}💰**\n"
                ),
                inline=False
            )
        else:
            embed.add_field(
                name="💡 İpucu",
                value="Bankaya para yatırarak faiz kazanmaya başla!\n`/yatır hepsi` ile tüm paranı yatırabilirsin.",
                inline=False
            )

        embed.add_field(
            name="🧠 Nasıl Çalışır?",
            value=(
                "1️⃣ `/yatır` ile bankaya para koy\n"
                "2️⃣ `/faiz` ile faiz sayacını başlat\n"
                "3️⃣ Her 6 saatte bir faiz birikir\n"
                "4️⃣ `/faiz` ile biriken faizi topla\n"
                "5️⃣ Bileşik faiz: faiz de faiz kazanır! 📈"
            ),
            inline=False
        )

        await guvenli_cevap(interaction, embed=embed)

    # =====================================================
    # 🎁 GÜNLÜK
    # =====================================================

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
        base = random.randint(500, 1200)
        bonus = streak * 60
        toplam = base + bonus

        # Bonus şans: %10 ihtimalle 2x
        jackpot = False
        if random.randint(1, 100) <= 10:
            toplam *= 2
            jackpot = True

        data['para'] += toplam
        data['son_gunluk'] = simdi.isoformat()
        update_economy(interaction.user.id, data)

        embed = discord.Embed(
            title="🎁 Günlük Ödül" + (" 🎰 JACKPOT!" if jackpot else ""),
            color=discord.Color.gold() if not jackpot else discord.Color.purple()
        )
        embed.add_field(name="💰 Temel", value=f"+{base}💰", inline=True)
        embed.add_field(name="🔥 Streak Bonus", value=f"+{bonus}💰 ({streak} gün)", inline=True)
        if jackpot:
            embed.add_field(name="🎰 JACKPOT!", value="**2X KAZANÇ!**", inline=True)
        embed.add_field(name="💎 Toplam", value=f"+{toplam}💰", inline=False)
        embed.add_field(name="🎒 Yeni Bakiye", value=f"{data['para']:,}💰", inline=False)

        if streak >= 7:
            embed.set_footer(text=f"🔥 {streak} günlük seri! Harika gidiyorsun!")

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

        para = random.randint(100, 350)
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
            ("💻 Yazılım geliştirdin", 250, 500),
            ("🍕 Pizza dağıttın", 100, 250),
            ("🚗 Uber şoförlüğü yaptın", 150, 300),
            ("📦 Kargo taşıdın", 120, 280),
            ("🎨 Grafik tasarım yaptın", 200, 400),
            ("📱 Uygulama yaptın", 300, 550),
            ("🎵 Müzik prodüksiyonu yaptın", 180, 380),
            ("📸 Fotoğraf çekimi yaptın", 160, 320),
            ("✍️ Makale yazdın", 130, 260),
            ("🔧 Tamircilik yaptın", 140, 290),
            ("🎮 Oyun test ettin", 110, 240),
            ("📊 Veri analizi yaptın", 220, 450),
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

        # Faiz sayacını başlat (eğer yoksa)
        if not data.get('son_faiz'):
            data['son_faiz'] = datetime.now().isoformat()

        update_economy(interaction.user.id, data)

        embed = discord.Embed(title="🏦 Para Yatırma", color=discord.Color.green())
        embed.description = f"**{miktar_int:,}💰** bankaya yatırıldı!"
        embed.add_field(name="💵 Cüzdan", value=f"{data['para']:,}💰", inline=True)
        embed.add_field(name="🏦 Banka", value=f"{data['banka']:,}💰", inline=True)
        embed.set_footer(text="📈 Bankadaki paran faiz kazanıyor! /faiz ile topla.")

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

        embed = discord.Embed(title="��� Para Çekme", color=discord.Color.green())
        embed.description = f"**{miktar_int:,}💰** bankadan çekildi!"
        embed.add_field(name="💵 Cüzdan", value=f"{data['para']:,}💰", inline=True)
        embed.add_field(name="���� Banka", value=f"{data['banka']:,}💰", inline=True)

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

    # =====================================================
    # 🔫 SOYGUN
    # =====================================================

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

        # Cüzdanda yeterli para yoksa
        if target_data['para'] < 200:
            update_economy(interaction.user.id, data)
            banka_parasi = target_data.get('banka', 0)

            if banka_parasi > 0:
                zeki_mesajlar = [
                    f"🧠 **{member.name}** senden daha zeki! Parasını bankaya koymuş, cüzdanı bomboş!",
                    f"🏦 **{member.name}** akıllı davranmış! Tüm parasını bankada saklıyor. Soyacak bir şey yok!",
                    f"😏 **{member.name}** bankacılık biliyor! Cüzdanında {target_data['para']:,}💰 var ama bankada **{banka_parasi:,}💰** yatıyor. Zekice!",
                    f"🎓 **{member.name}** finans dersi verdi sana! Parasını bankada tutuyor, hırsızlara geçit yok!",
                    f"🦊 **{member.name}** tilki gibi kurnaz! Cüzdanını boş bırakıp parasını bankada saklıyor.",
                    f"💡 **{member.name}** aklını kullanıyor! Bankadaki **{banka_parasi:,}💰**'ye dokunamazsın!",
                ]
                mesaj = random.choice(zeki_mesajlar)

                embed = discord.Embed(title="🧠 Bu Kişi Akıllıymış!", color=discord.Color.blue())
                embed.description = mesaj
                embed.set_footer(text="💡 Sen de paranı bankaya koy, soygunlardan koru!")
            else:
                embed = discord.Embed(title="💀 Fakir Hedef!", color=discord.Color.dark_grey())
                embed.description = f"❌ **{member.name}** gerçekten çok fakir, soyacak bir şey yok!"
                embed.add_field(name="💵 Cüzdan", value=f"{target_data['para']:,}💰", inline=True)
                embed.add_field(name="🏦 Banka", value=f"{banka_parasi:,}💰", inline=True)

            await guvenli_cevap(interaction, embed=embed)
            return

        # Soygun denemesi
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
# 🔧 COG YÜKLEME
# =====================================================

async def setup(bot):
    await bot.add_cog(Ekonomi(bot))
