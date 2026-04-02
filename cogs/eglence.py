# =====================================================
# 🎲 WOWSY BOT - EĞLENCE KOMUTLARI
# =====================================================

import discord
from discord.ext import commands
from discord import app_commands
import random

from utils import guvenli_cevap

# =====================================================
# 📏 KAÇ CM VERİLERİ
# =====================================================

CM_MESAJLARI = {
    (0, 5): ["Mikroskop lazım 🔬", "F", "Nano teknoloji 😭", "Görünmüyor bile", "RIP 💀"],
    (5, 10): ["Hayal kırıklığı...", "Eh işte 😐", "Pes etme!", "Karakterin güzeldir en azından", "Küçük ama gösterişli? 🤏"],
    (10, 15): ["Ortalama Türk 🇹🇷", "İdare eder", "Fena değil", "Standart paket", "Orta karar 👍"],
    (15, 20): ["Güzel güzel 👍", "Ortalamanın üstü!", "Helal olsun", "Yeterli yeterli", "Gıpta ile bakıyorlar 👀"],
    (20, 25): ["BÜYÜK! 😳", "Tebrikler!", "Genetik piyangosu", "Chad 🗿", "Saygı duyulur 🫡"],
    (25, 35): ["EFSANE! 🏆", "İmkansız!", "Şüpheli...", "Hile mi bu?", "MONSTER 👹", "Silah ruhsatı lazım! 🔫"],
}

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
            "Neden senior yazılımcılar ormanda yürümeyi sever? Çünkü orada hiç 'merge conflict' yok, sadece doğal dallar (branches) var. 🌲",
            "CSS dosyası neden terapiye gider? Çünkü parent'ı ile olan ilişkisi çok karmaşık ve sürekli overflow yaşıyor. 🎨",
            "Docker neden çok havalı? Çünkü 'Benim makinemde çalışıyordu' bahanesini yasal hale getirdi. 🐋",
            "Bir yazılımcı neden asla evlenemez? Çünkü her şeyi Localhost'ta çalışıyor sanıyor. 🏠",
            "Junior: 'Kodu yazdım ama neden çalışmıyor bilmiyorum.' Senior: 'Kodu yazdım ve neden çalışıyor hiçbir fikrim yok.' 🧙‍♂️",
            "Git ve Evlilik arasındaki benzerlik nedir? İkisinde de bir hata yaptığında commit etmekten korkarsın. 💍",
            "Yapay zeka işimizi elimizden mi alacak? Hayır, müşteriler ne istediğini anlatamadığı sürece güvendeyiz. 🤖",
            "Bir SQL sorgusu bara girmiş, iki tabloya yaklaşmış ve sormuş: 'Join edebilir miyiz?' 🍺",
            "Python neden yılan gibi? Çünkü indent'siz yaşayamaz! 🐍",
            "Neden yazılımcılar karanlıkta çalışır? Çünkü light mode gözlerini yakıyor! 🌙",
            "İnternet neden üzgün? Çünkü çok fazla spam yiyor! 📧",
            "JavaScript neden terapiye gitti? Çünkü çok fazla callback var! 🔄",
            "HTML neden partiye gitmedi? Çünkü tag'lenmeyi sevmiyor! 🎉",
            "Programcı neden karısını terk etti? Çünkü obje odaklı değildi! 💔",
            "Recursive fonksiyon bara girmiş. Barmen: 'Ne içersin?' Fonksiyon: 'Recursive fonksiyon bara girmiş...' 🔁",
            "Yazılımcı duşta neden öldü? Şampuan kutusunda: 'Islat, şampuanla, durula, tekrarla' yazıyordu. Sonsuz döngüye girdi. 🧼",
            "Donanım (Hardware), yazılıma vuramadığın zaman tekmelediğin kısımdır. 💻",
            "Gerçek programcılar ağlamaz, sadece debug moduna geçerler. 😢",
            "Bir yazılımcının 0'dan 10'a kadar sayması ne kadar sürer? 11 saniye, çünkü 0'dan başlar. 🔢",
            "Linux kullanıcısı neden yoldan çıktı? 'Drive' bulunamadı hatası aldığı için. 🐧",
            "C++ geliştiricileri neden gözlük takar? Çünkü referansları göremiyorlar. 👓",
            "Java geliştiricileri neden her şeyi çok karmaşık anlatır? Çünkü her şey bir 'AbstractMethodBeanFactory'dir. ☕",
            "Backend geliştiricisi plaja giderse ne der? 'Görüntü kötü ama API çok hızlı çalışıyor.' 🌊",
            "Yazılımcıların en sevdiği spor nedir? Bug avcılığı. 🏹",
            "Neden 1 bit bilgisayara girmiş? Byte almak için! 😂",
            "Programcı neden gözlük takar? Çünkü C# (C-Sharp) yapamıyor! 👓",
            "Bir test uzmanı (QA) bara girer; koşarak girer, takla atarak girer, 99999 tane bira ister, kertenkele ısmarlar... 🍺",
            "Frontend'ci neden mutsuz? Tasarımcı 'pixel perfect' istediği için. 📐",
            "Microservice mimarisi nedir? Bir hatayı 20 farklı sunucuya dağıtma sanatıdır. ☁️",
            "Neden Node.js geliştiricileri kahve sevmez? Zaten sürekli event loop içindeler. ☕",
            "Klavye neden doktora gitti? Çünkü tuşları basıyordu! ⌨️",
            "Kodum çalışıyor: 'Ben bir dahiyim.' Kodum çalışmıyor: 'Ben bir salağım.' Döngü devam ediyor. 🔄",
            "Yazılımcı: 'Bende çalışıyor.' Müşteri: 'Biz senin bilgisayarını mı satın alıyoruz?' 💻",
            "Bir yazılımcı için 'yakında' kelimesi 2 saat ile 6 ay arasını temsil eder. ⏳",
            "StackOverflow kapansa dünya ekonomisi 15 dakikada çöker. 📉"
            "Geçen gün bir fırıncıya gittim, 'Ekmek taze mi?' dedim. 'Yok, yarının ekmeği' dedi. Geleceği yedik iyi mi? 🥖",
            "Adamın biri varmış, ikinci gün ölmüş. Neden? Çünkü ilk gün çok yorulmuş! 🤦‍♂️",
            "Sinemada önümdeki adam keldi, kafasına şaplak attım 'Naber lan Rıfat' dedim. 'Rıfat değilim' dedi. 'Vay be Rıfat, hem kel olmuşsun hem de ismini değiştirmişsin' dedim. 😂",
            "Soru: Havlayan saatlere ne denir? Cevap: Watch-dog! 🐶⌚",
            "Yağmur yağmış, yerler ıslanmış. Peki ya gökler? Gökler ağlamış... 🌧️",
            "Doktor: 'Beyefendi, günde bir elma yerseniz doktordan uzak durursunuz.' Hasta: 'E ama ben size geldim?' Doktor: 'Ben elma değilim ki!' 🍎",
            "Adamın biri kitap okurken ölmüş. Neden? Satır başına gelmiş! 📚",
            "Soru: Temel neden her sabah evden çıkarken kapıya bakarmış? Cevap: Eşik atlamak için! 🏠",
            "Garson: 'Beyefendi, çorbanızda sinek var!' Müşteri: 'Bağırma, şimdi herkes ister!' 🥣",
            "Soru: En çok kar yağan ilimiz hangisidir? Cevap: Kar-aman! ❄️",
            "Oğlum: 'Baba, evlenmek ne kadar tutar?' Baba: 'Bilmiyorum oğlum, ben hâlâ ödüyorum.' 💍",
            "Soru: İki domates yolda yürüyormuş, birinin üzerinden araba geçmiş. Diğeri ne demiş? Cevap: 'Yürü gidelim salça!' 🍅",
            "Adamın biri kazmış, karısı da tencereymiş... Neyse bu çok soğuk oldu. 🧊",
            "Soru: En hızlı sayı hangisidir? Cevap: 10. Çünkü onun 'on'u (önü) açık! 🔟",
            "Dün bir şaka yaptım, herkes güldü. Bugün yaptım, kimse gülmedi. Meğer şakanın son kullanma tarihi geçmiş. 🗓️",
            "Soru: Kalemi olan adama ne denir? Cevap: Kalem-şör! 🖋️",
            "Adamın kafasına radyo düşmüş, bir şey olmamış. Neden? Çünkü radyo hafif müzik çalıyormuş! 🎶",
            "Soru: Hangi masada yemek yenmez? Cevap: Ders masasında! 📝",
            "Küçük bir çocuk annesine sormuş: 'Anne, melekler uçar mı?' Anne: 'Evet yavrum.' Çocuk: 'Ama bizim hizmetçi uçmuyor?' Anne: 'O melek değil ki.' Çocuk: 'Ama babam ona meleğim diyor?' Anne: 'O zaman şimdi uçacak!' 👼",
            "Soru: Limon ne zaman sıkılır? Cevap: Yalnız kaldığında! 🍋",
            "Adamın biri gömleğini ütülüyormuş, telefon çalmış. Ütüyü kulağına götürmüş! Diğer kulağı neden yanmış? Çünkü ambulansı aramaya çalışmış! 📞",
            "Soru: Adamın biri Hindistan'da yürüyormuş, kafasına 'budha' düşmüş. Ne demiş? Cevap: 'Başımıza budha mı gelecekti?' 🧘‍♂️",
            "Soru: Hangi teneşirle yazı yazılmaz? Cevap: Müşteri memnuniyetsizliği yaşayan cenaze teneşiriyle! (Tamam, bu biraz karanlık oldu) ⚰️",
            "Öğretmen: 'Cümle içinde 'ayak' kelimesini kullan.' Öğrenci: 'Annem mutfakta ayak-üstü yemek yiyor.' 🦶",
            "Soru: Mantarlar neden şemsiye şeklindedir? Cevap: Yağmurda ıslanmamak için! 🍄",
            "Adamın biri restorana gitmiş, 'Bana bir yer ayırın' demiş. Garson da 'Buyurun, şurası ayır' demiş. 🍽️",
            "Soru: Sineğin büyüğüne ne denir? Cevap: El-sinek! (Hani el-feneri gibi) 🦟",
            "Küçük su damlası annesine ne demiş? 'Anne, ben ne zaman sel olacağım?' 💧",
            "Soru: En dertli meyve hangisidir? Cevap: 'Ah'lat! 🍐",
            "Adamın biri yolda yürürken bir cüzdan bulmuş, içinde hiç para yokmuş ama sahibi varmış. Neden? Cüzdanın üstünde 'Vesikalık' yazıyormuş! 🖼️",
            "Soru: Elektrik kesilince ne olur? Cevap: Karanlık olur! (Daha ne bekliyordun?) 💡",
            "Bir gün iki delik yolda yürüyormuş, biri diğerine demiş ki: 'Amma da açığız ha!' 🕳️",
            "Soru: Hiç bitmeyen hüzne ne denir? Cevap: Hüzün-baz! 🎭",
            "Baba: 'Karne nasıl oğlum?' Çocuk: 'Okulun en popüleri benim baba, bütün hocalar bana takmış!' 🎓",
            "Soru: Kediler neden bilgisayar kullanamaz? Cevap: Mouse'u yedikleri için! 🐭",
            "Adamın biri her sabah banyoda şarkı söylüyormuş. Komşusu sormuş: 'Sesin çok güzel mi?' Adam: 'Yok, sadece şampuanın arkasındaki sözleri okuyorum.' 🧼"
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
        embed.add_field(name="💬 Cevap", value=cevap, inline=False)
        
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
        seed = min(kisi1.id, kisi2.id) + max(kisi1.id, kisi2.id)
        random.seed(seed)
        oran = random.randint(0, 100)
        random.seed()
        
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
    # 📏 KAÇ CM
    # =====================================================

    @app_commands.command(name="kaçcm", description="Kaç cm olduğunu öğren 😏")
    @app_commands.describe(member="Kimin? (boş bırakırsan kendin)")
    async def slash_kaccm(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        
        random.seed(member.id)
        cm = random.randint(1, 30)
        random.seed()
        
        mesaj = "???"
        for (min_cm, max_cm), mesajlar in CM_MESAJLARI.items():
            if min_cm <= cm < max_cm:
                mesaj = random.choice(mesajlar)
                break
        
        bar_uzunluk = cm // 3
        bar = "=" * bar_uzunluk + "D" if cm > 0 else "."
        
        if cm < 10:
            renk = discord.Color.red()
        elif cm < 15:
            renk = discord.Color.orange()
        elif cm < 20:
            renk = discord.Color.green()
        else:
            renk = discord.Color.gold()
        
        embed = discord.Embed(title=f"📏 {member.name}'in Boyutu", color=renk)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="📐 Görsel", value=f"```\n8{bar}\n```", inline=False)
        embed.add_field(name="📊 Uzunluk", value=f"**{cm} cm**", inline=True)
        embed.add_field(name="💬 Yorum", value=mesaj, inline=True)
        
        if cm < 5:
            karsilastirma = "🔬 Mikrop boyutu"
        elif cm < 10:
            karsilastirma = "📱 Telefon boyutu"
        elif cm < 15:
            karsilastirma = "🥒 Salatalık boyutu"
        elif cm < 20:
            karsilastirma = "🍌 Muz boyutu"
        elif cm < 25:
            karsilastirma = "🥖 Ekmek boyutu"
        else:
            karsilastirma = "🗼 Kule boyutu"
        
        embed.add_field(name="📏 Karşılaştırma", value=karsilastirma, inline=False)
        embed.set_footer(text="⚠️ Sonuçlar tamamen rastgeledir ve şaka amaçlıdır!")
        
        await guvenli_cevap(interaction, embed=embed)

    @commands.command(aliases=['cm', 'dick', 'size', 'boy', 'pipi'])
    async def kaccm(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        
        random.seed(member.id)
        cm = random.randint(1, 30)
        random.seed()
        
        mesaj = "???"
        for (min_cm, max_cm), mesajlar in CM_MESAJLARI.items():
            if min_cm <= cm < max_cm:
                mesaj = random.choice(mesajlar)
                break
        
        bar = "=" * (cm // 3) + "D" if cm > 0 else "."
        
        if cm < 10:
            renk = discord.Color.red()
        elif cm < 15:
            renk = discord.Color.orange()
        elif cm < 20:
            renk = discord.Color.green()
        else:
            renk = discord.Color.gold()
        
        embed = discord.Embed(title=f"📏 {member.name}", color=renk)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.description = f"```\n8{bar}\n```"
        embed.add_field(name="📊 Sonuç", value=f"**{cm} cm**", inline=True)
        embed.add_field(name="💬 Yorum", value=mesaj, inline=True)
        embed.set_footer(text="⚠️ Şaka amaçlıdır!")
        
        await ctx.send(embed=embed)

    # =====================================================
    # 🏳️‍🌈 GAY TEST
    # =====================================================

    @app_commands.command(name="gaytest", description="Ne kadar gay olduğunu öğren 🏳️‍🌈")
    @app_commands.describe(member="Kim test edilsin?")
    async def slash_gaytest(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        
        random.seed(member.id + 1337)
        oran = random.randint(0, 100)
        random.seed()
        
        if oran < 10:
            mesaj = "Taş gibi düz 📏"
            renk = discord.Color.blue()
            emoji_bar = "⬜"
        elif oran < 25:
            mesaj = "Oldukça hetero 👔"
            renk = discord.Color.blue()
            emoji_bar = "🟦"
        elif oran < 40:
            mesaj = "Biraz merak var sanki 🤔"
            renk = discord.Color.green()
            emoji_bar = "🟩"
        elif oran < 55:
            mesaj = "Bi-curious vibes 👀"
            renk = discord.Color.purple()
            emoji_bar = "🟪"
        elif oran < 70:
            mesaj = "Esnek takılıyor 🌈"
            renk = discord.Color.gold()
            emoji_bar = "🟨"
        elif oran < 85:
            mesaj = "Rainbow energy! 🏳️‍🌈"
            renk = discord.Color.from_rgb(255, 105, 180)
            emoji_bar = "🟧"
        else:
            mesaj = "FULL GAY! 💅✨"
            renk = discord.Color.from_rgb(255, 0, 128)
            emoji_bar = "🏳️‍🌈"
        
        bar_dolu = oran // 10
        bar = emoji_bar * bar_dolu + "⬜" * (10 - bar_dolu)
        
        embed = discord.Embed(title="🏳️‍🌈 Gay Test", color=renk)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="👤 Kullanıcı", value=member.mention, inline=False)
        embed.add_field(name="📊 Oran", value=f"**%{oran}**", inline=True)
        embed.add_field(name="💬 Sonuç", value=mesaj, inline=True)
        embed.add_field(name="📈 Grafik", value=bar, inline=False)
        embed.set_footer(text="⚠️ Tamamen şaka amaçlıdır! Herkes değerlidir! 💕")
        
        await guvenli_cevap(interaction, embed=embed)

    @commands.command(aliases=['gay', 'gaylik', 'lgbttest'])
    async def gaytest(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        
        random.seed(member.id + 1337)
        oran = random.randint(0, 100)
        random.seed()
        
        if oran < 20:
            mesaj = "Düz 📏"
        elif oran < 40:
            mesaj = "Biraz merak var 🤔"
        elif oran < 60:
            mesaj = "Bi-curious 👀"
        elif oran < 80:
            mesaj = "Rainbow vibes 🌈"
        else:
            mesaj = "FULL GAY! 🏳️‍🌈"
        
        bar_dolu = oran // 10
        bar = "🏳️‍🌈" * bar_dolu + "⬜" * (10 - bar_dolu)
        
        embed = discord.Embed(title="🏳️‍🌈 Gay Test", color=discord.Color.from_rgb(255, 105, 180))
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="👤 Kullanıcı", value=member.mention, inline=True)
        embed.add_field(name="📊 Oran", value=f"**%{oran}**", inline=True)
        embed.add_field(name="💬 Sonuç", value=mesaj, inline=False)
        embed.add_field(name="📈 Grafik", value=bar, inline=False)
        embed.set_footer(text="⚠️ Şaka amaçlıdır!")
        
        await ctx.send(embed=embed)

    # =====================================================
    # 🧠 IQ TEST
    # =====================================================

    @app_commands.command(name="iqtest", description="IQ seviyeni öğren 🧠")
    @app_commands.describe(member="Kim test edilsin?")
    async def slash_iqtest(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        
        random.seed(member.id + 9999)
        iq = random.randint(50, 200)
        random.seed()
        
        if iq >= 180:
            mesaj = "🧠 ÜSTÜN ZEKA! Einstein seviyesi!"
            renk = discord.Color.gold()
        elif iq >= 150:
            mesaj = "✨ Dahi! Mensa seni bekliyor!"
            renk = discord.Color.purple()
        elif iq >= 130:
            mesaj = "🎓 Çok zeki! Üstün başarılı!"
            renk = discord.Color.blue()
        elif iq >= 110:
            mesaj = "📚 Ortalamanın üstü! Akıllı!"
            renk = discord.Color.green()
        elif iq >= 90:
            mesaj = "👍 Normal zeka seviyesi"
            renk = discord.Color.greyple()
        elif iq >= 70:
            mesaj = "😅 Biraz çalışman lazım..."
            renk = discord.Color.orange()
        else:
            mesaj = "🤡 Telefonu ters tutuyorsun galiba"
            renk = discord.Color.red()
        
        embed = discord.Embed(title="🧠 IQ Test", color=renk)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="👤 Kullanıcı", value=member.mention, inline=True)
        embed.add_field(name="🧠 IQ", value=f"**{iq}**", inline=True)
        embed.add_field(name="💬 Sonuç", value=mesaj, inline=False)
        embed.set_footer(text="⚠️ Şaka amaçlıdır, gerçek IQ testine benzemez!")
        
        await guvenli_cevap(interaction, embed=embed)

    @commands.command(aliases=['iq', 'zeka'])
    async def iqtest(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        
        random.seed(member.id + 9999)
        iq = random.randint(50, 200)
        random.seed()
        
        if iq >= 150:
            mesaj = "🧠 DAHİ!"
        elif iq >= 120:
            mesaj = "📚 Çok zeki!"
        elif iq >= 100:
            mesaj = "👍 Normal"
        elif iq >= 80:
            mesaj = "😅 Eh işte..."
        else:
            mesaj = "🤡 Bruh"
        
        embed = discord.Embed(title="🧠 IQ Test", color=discord.Color.blue())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="👤 Kullanıcı", value=member.mention, inline=True)
        embed.add_field(name="🧠 IQ", value=f"**{iq}**", inline=True)
        embed.add_field(name="💬 Sonuç", value=mesaj, inline=False)
        embed.set_footer(text="⚠️ Şaka amaçlıdır!")
        
        await ctx.send(embed=embed)

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
            "Neden senior yazılımcılar ormanda yürümeyi sever? Çünkü orada hiç 'merge conflict' yok, sadece doğal dallar (branches) var. 🌲",
            "CSS dosyası neden terapiye gider? Çünkü parent'ı ile olan ilişkisi çok karmaşık ve sürekli overflow yaşıyor. 🎨",
            "Docker neden çok havalı? Çünkü 'Benim makinemde çalışıyordu' bahanesini yasal hale getirdi. 🐋",
            "Bir yazılımcı neden asla evlenemez? Çünkü her şeyi Localhost'ta çalışıyor sanıyor. 🏠",
            "Junior: 'Kodu yazdım ama neden çalışmıyor bilmiyorum.' Senior: 'Kodu yazdım ve neden çalışıyor hiçbir fikrim yok.' 🧙‍♂️",
            "Git ve Evlilik arasındaki benzerlik nedir? İkisinde de bir hata yaptığında commit etmekten korkarsın. 💍",
            "Yapay zeka işimizi elimizden mi alacak? Hayır, müşteriler ne istediğini anlatamadığı sürece güvendeyiz. 🤖",
            "Bir SQL sorgusu bara girmiş, iki tabloya yaklaşmış ve sormuş: 'Join edebilir miyiz?' 🍺",
            "Python neden yılan gibi? Çünkü indent'siz yaşayamaz! 🐍",
            "Neden yazılımcılar karanlıkta çalışır? Çünkü light mode gözlerini yakıyor! 🌙",
            "İnternet neden üzgün? Çünkü çok fazla spam yiyor! 📧",
            "JavaScript neden terapiye gitti? Çünkü çok fazla callback var! 🔄",
            "HTML neden partiye gitmedi? Çünkü tag'lenmeyi sevmiyor! 🎉",
            "Programcı neden karısını terk etti? Çünkü obje odaklı değildi! 💔",
            "Recursive fonksiyon bara girmiş. Barmen: 'Ne içersin?' Fonksiyon: 'Recursive fonksiyon bara girmiş...' 🔁",
            "Yazılımcı duşta neden öldü? Şampuan kutusunda: 'Islat, şampuanla, durula, tekrarla' yazıyordu. Sonsuz döngüye girdi. 🧼",
            "Donanım (Hardware), yazılıma vuramadığın zaman tekmelediğin kısımdır. 💻",
            "Gerçek programcılar ağlamaz, sadece debug moduna geçerler. 😢",
            "Bir yazılımcının 0'dan 10'a kadar sayması ne kadar sürer? 11 saniye, çünkü 0'dan başlar. 🔢",
            "Linux kullanıcısı neden yoldan çıktı? 'Drive' bulunamadı hatası aldığı için. 🐧",
            "C++ geliştiricileri neden gözlük takar? Çünkü referansları göremiyorlar. 👓",
            "Java geliştiricileri neden her şeyi çok karmaşık anlatır? Çünkü her şey bir 'AbstractMethodBeanFactory'dir. ☕",
            "Backend geliştiricisi plaja giderse ne der? 'Görüntü kötü ama API çok hızlı çalışıyor.' 🌊",
            "Yazılımcıların en sevdiği spor nedir? Bug avcılığı. 🏹",
            "Neden 1 bit bilgisayara girmiş? Byte almak için! 😂",
            "Programcı neden gözlük takar? Çünkü C# (C-Sharp) yapamıyor! 👓",
            "Bir test uzmanı (QA) bara girer; koşarak girer, takla atarak girer, 99999 tane bira ister, kertenkele ısmarlar... 🍺",
            "Frontend'ci neden mutsuz? Tasarımcı 'pixel perfect' istediği için. 📐",
            "Microservice mimarisi nedir? Bir hatayı 20 farklı sunucuya dağıtma sanatıdır. ☁️",
            "Neden Node.js geliştiricileri kahve sevmez? Zaten sürekli event loop içindeler. ☕",
            "Klavye neden doktora gitti? Çünkü tuşları basıyordu! ⌨️",
            "Kodum çalışıyor: 'Ben bir dahiyim.' Kodum çalışmıyor: 'Ben bir salağım.' Döngü devam ediyor. 🔄",
            "Yazılımcı: 'Bende çalışıyor.' Müşteri: 'Biz senin bilgisayarını mı satın alıyoruz?' 💻",
            "Bir yazılımcı için 'yakında' kelimesi 2 saat ile 6 ay arasını temsil eder. ⏳",
            "StackOverflow kapansa dünya ekonomisi 15 dakikada çöker. 📉"
            "Geçen gün bir fırıncıya gittim, 'Ekmek taze mi?' dedim. 'Yok, yarının ekmeği' dedi. Geleceği yedik iyi mi? 🥖",
            "Adamın biri varmış, ikinci gün ölmüş. Neden? Çünkü ilk gün çok yorulmuş! 🤦‍♂️",
            "Sinemada önümdeki adam keldi, kafasına şaplak attım 'Naber lan Rıfat' dedim. 'Rıfat değilim' dedi. 'Vay be Rıfat, hem kel olmuşsun hem de ismini değiştirmişsin' dedim. 😂",
            "Soru: Havlayan saatlere ne denir? Cevap: Watch-dog! 🐶⌚",
            "Yağmur yağmış, yerler ıslanmış. Peki ya gökler? Gökler ağlamış... 🌧️",
            "Doktor: 'Beyefendi, günde bir elma yerseniz doktordan uzak durursunuz.' Hasta: 'E ama ben size geldim?' Doktor: 'Ben elma değilim ki!' 🍎",
            "Adamın biri kitap okurken ölmüş. Neden? Satır başına gelmiş! 📚",
            "Soru: Temel neden her sabah evden çıkarken kapıya bakarmış? Cevap: Eşik atlamak için! 🏠",
            "Garson: 'Beyefendi, çorbanızda sinek var!' Müşteri: 'Bağırma, şimdi herkes ister!' 🥣",
            "Soru: En çok kar yağan ilimiz hangisidir? Cevap: Kar-aman! ❄️",
            "Oğlum: 'Baba, evlenmek ne kadar tutar?' Baba: 'Bilmiyorum oğlum, ben hâlâ ödüyorum.' 💍",
            "Soru: İki domates yolda yürüyormuş, birinin üzerinden araba geçmiş. Diğeri ne demiş? Cevap: 'Yürü gidelim salça!' 🍅",
            "Adamın biri kazmış, karısı da tencereymiş... Neyse bu çok soğuk oldu. 🧊",
            "Soru: En hızlı sayı hangisidir? Cevap: 10. Çünkü onun 'on'u (önü) açık! 🔟",
            "Dün bir şaka yaptım, herkes güldü. Bugün yaptım, kimse gülmedi. Meğer şakanın son kullanma tarihi geçmiş. 🗓️",
            "Soru: Kalemi olan adama ne denir? Cevap: Kalem-şör! 🖋️",
            "Adamın kafasına radyo düşmüş, bir şey olmamış. Neden? Çünkü radyo hafif müzik çalıyormuş! 🎶",
            "Soru: Hangi masada yemek yenmez? Cevap: Ders masasında! 📝",
            "Küçük bir çocuk annesine sormuş: 'Anne, melekler uçar mı?' Anne: 'Evet yavrum.' Çocuk: 'Ama bizim hizmetçi uçmuyor?' Anne: 'O melek değil ki.' Çocuk: 'Ama babam ona meleğim diyor?' Anne: 'O zaman şimdi uçacak!' 👼",
            "Soru: Limon ne zaman sıkılır? Cevap: Yalnız kaldığında! 🍋",
            "Adamın biri gömleğini ütülüyormuş, telefon çalmış. Ütüyü kulağına götürmüş! Diğer kulağı neden yanmış? Çünkü ambulansı aramaya çalışmış! 📞",
            "Soru: Adamın biri Hindistan'da yürüyormuş, kafasına 'budha' düşmüş. Ne demiş? Cevap: 'Başımıza budha mı gelecekti?' 🧘‍♂️",
            "Soru: Hangi teneşirle yazı yazılmaz? Cevap: Müşteri memnuniyetsizliği yaşayan cenaze teneşiriyle! (Tamam, bu biraz karanlık oldu) ⚰️",
            "Öğretmen: 'Cümle içinde 'ayak' kelimesini kullan.' Öğrenci: 'Annem mutfakta ayak-üstü yemek yiyor.' 🦶",
            "Soru: Mantarlar neden şemsiye şeklindedir? Cevap: Yağmurda ıslanmamak için! 🍄",
            "Adamın biri restorana gitmiş, 'Bana bir yer ayırın' demiş. Garson da 'Buyurun, şurası ayır' demiş. 🍽️",
            "Soru: Sineğin büyüğüne ne denir? Cevap: El-sinek! (Hani el-feneri gibi) 🦟",
            "Küçük su damlası annesine ne demiş? 'Anne, ben ne zaman sel olacağım?' 💧",
            "Soru: En dertli meyve hangisidir? Cevap: 'Ah'lat! 🍐",
            "Adamın biri yolda yürürken bir cüzdan bulmuş, içinde hiç para yokmuş ama sahibi varmış. Neden? Cüzdanın üstünde 'Vesikalık' yazıyormuş! 🖼️",
            "Soru: Elektrik kesilince ne olur? Cevap: Karanlık olur! (Daha ne bekliyordun?) 💡",
            "Bir gün iki delik yolda yürüyormuş, biri diğerine demiş ki: 'Amma da açığız ha!' 🕳️",
            "Soru: Hiç bitmeyen hüzne ne denir? Cevap: Hüzün-baz! 🎭",
            "Baba: 'Karne nasıl oğlum?' Çocuk: 'Okulun en popüleri benim baba, bütün hocalar bana takmış!' 🎓",
            "Soru: Kediler neden bilgisayar kullanamaz? Cevap: Mouse'u yedikleri için! 🐭",
            "Adamın biri her sabah banyoda şarkı söylüyormuş. Komşusu sormuş: 'Sesin çok güzel mi?' Adam: 'Yok, sadece şampuanın arkasındaki sözleri okuyorum.' 🧼"
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
