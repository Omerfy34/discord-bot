# =====================================================
# 📚 WOWSY BOT - YARDIM KOMUTLARI
# =====================================================

import discord
from discord.ext import commands
from discord import app_commands

from utils import guvenli_cevap


# =====================================================
# 📚 YARDIM COG
# =====================================================

class Yardim(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =====================================================
    # 📚 SLASH KOMUTLARI
    # =====================================================

    @app_commands.command(name="yardım", description="Tüm komutları göster")
    async def slash_yardim(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="⚡ WOWSY BOT - KOMUTLAR",
            description="**`/`** (slash) komutları kullan!\n\n"
                        "📌 **Slash komutlar** için `/` yaz ve otomatik tamamlama kullan.",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="💰 EKONOMİ",
            value="```\n"
                  "bakiye   - Para görüntüle\n"
                  "günlük   - 24 saat ödül\n"
                  "bedava   - 2 saat ödül\n"
                  "çalış    - 30 dk iş\n"
                  "yatır    - Bankaya yatır\n"
                  "çek      - Bankadan çek\n"
                  "gönder   - Para transferi\n"
                  "soygun   - Hırsızlık (%25)\n"
                  "faiz     - Faiz topla\n"
                  "zenginler- Sıralama\n"
                  "```",
            inline=True
        )
        
        embed.add_field(
            name="🎮 OYUNLAR",
            value="```\n"
                  "hunt     - Avlan (2dk)\n"
                  "fish     - Balık tut (3dk)\n"
                  "slot     - Slot (min:10)\n"
                  "coinflip - Yazı-tura\n"
                  "dice     - Zar bahis\n"
                  "roulette - Rulet\n"
                  "blackjack- 21 kart\n"
                  "crash    - Çarpan oyunu\n"
                  "battle   - PvP savaş\n"
                  "```",
            inline=True
        )
        
        embed.add_field(
            name="🎵 MÜZİK",
            value="```\n"
                  "play  - Müzik çal\n"
                  "pause - Duraklat\n"
                  "devam - Devam ettir\n"
                  "skip  - Atla\n"
                  "stop  - Durdur\n"
                  "leave - Kanaldan çık\n"
                  "queue - Kuyruk göster\n"
                  "join  - Kanala katıl\n"
                  "```",
            inline=True
        )
        
        embed.add_field(
            name="🛡️ MODERASYON",
            value="```\n"
                  "kick    - At\n"
                  "ban     - Yasakla\n"
                  "unban   - Yasak kaldır\n"
                  "sil     - Mesaj sil\n"
                  "timeout - Sustur\n"
                  "uyar    - Uyarı ver\n"
                  "uyarılar- Uyarı listesi\n"
                  "```",
            inline=True
        )
        
        embed.add_field(
            name="🎲 EĞLENCE",
            value="```\n"
                  "avatar  - Profil resmi\n"
                  "şaka    - Rastgele şaka\n"
                  "8ball   - Sihirli küre\n"
                  "sarıl   - Kucaklaş\n"
                  "tokatlat- Tokat at\n"
                  "seç     - Seçim yap\n"
                  "aşkmetre- Aşk ölç\n"
                  "kaçcm   - Boy ölç 😏\n"
                  "gaytest - Gay testi 🏳️‍🌈\n"
                  "iqtest  - IQ testi 🧠\n"
                  "aykut   - Aykut Elmas GIF\n"
                  "```",
            inline=True
        )
        
        embed.add_field(
            name="🤖 YAPAY ZEKA",
            value="```\n"
                  "ai      - Soru sor\n"
                  "rol     - AI rolü seç\n"
                  "özelrol - Özel rol yaz\n"
                  "rolsıfırla- Sıfırla\n"
                  "rolbilgi- Durum göster\n"
                  "görsel  - Görsel oluştur\n"
                  "tercume - Çeviri yap\n"
                  "hikaye  - Hikaye yaz\n"
                  "özet    - Metin özetle\n"
                  "kod     - Kod yaz\n"
                  "şiir    - Şiir yaz\n"
                  "```",
            inline=True
        )
        
        embed.add_field(
            name="ℹ️ BİLGİ & SAYAÇLAR",
            value="```\n"
                  "ping    - Bot gecikmesi\n"
                  "sunucu  - Sunucu bilgisi\n"
                  "kullanıcı- Kullanıcı bilgi\n"
                  "botbilgi- Bot hakkında\n"
                  "davet   - Davet linki\n"
                  "yks     - YKS sayacı 📚\n"
                  "sayaç   - Özel günler 📅\n"
                  "yardım  - Bu menü\n"
                  "```",
            inline=True
        )
        
        embed.set_footer(text="⚡ WOWSY Bot | Geliştirici: WOWSY | /aiyardım ile AI detayları!")
        
        if self.bot.user:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="ekonomi", description="Ekonomi komutlarını göster")
    async def slash_ekonomi_yardim(self, interaction: discord.Interaction):
        embed = discord.Embed(title="💰 EKONOMİ KOMUTLARI", color=discord.Color.gold())
        
        embed.add_field(
            name="📊 Temel Komutlar",
            value="**/bakiye** `[@kullanıcı]` - Para görüntüle\n"
                  "**/günlük** - 24 saatte bir ödül (streak bonusu + %10 jackpot)\n"
                  "**/bedava** - 2 saatte bir ödül\n"
                  "**/çalış** - 30 dakikada bir çalış",
            inline=False
        )
        
        embed.add_field(
            name="🏦 Banka İşlemleri",
            value="**/yatır** `<miktar/hepsi>` - Bankaya yatır\n"
                  "**/çek** `<miktar/hepsi>` - Bankadan çek\n"
                  "**/gönder** `@kullanıcı <miktar>` - Transfer",
            inline=False
        )
        
        embed.add_field(
            name="📈 Faiz Sistemi",
            value="**/faiz** - Birikmiş faizi topla\n"
                  "**/faiz-bilgi** - Faiz sistemi hakkında bilgi\n"
                  "├ 💰 Oran: %2 / 6 saat\n"
                  "├ 📊 Bileşik faiz (faiz de faiz kazanır)\n"
                  "└ 🔝 Max tek seferde: 50,000💰",
            inline=False
        )
        
        embed.add_field(
            name="🔫 Riskli İşlemler",
            value="**/soygun** `@kullanıcı` - %25 başarı, 1 saat cooldown\n"
                  "├ Başarısız olursan 200-500💰 ceza!\n"
                  "└ Hedefin parası bankadaysa: \"Zeki!\" mesajı",
            inline=False
        )
        
        embed.add_field(
            name="📈 Sıralama",
            value="**/zenginler** - En zengin 10 kişi",
            inline=False
        )
        
        embed.set_footer(text="💡 Yeni başlayanlar 1000💰 ile başlar! Bankaya koy, faiz kazan!")
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="oyunlar", description="Oyun komutlarını göster")
    async def slash_oyunlar_yardim(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🎮 OYUN KOMUTLARI", color=discord.Color.purple())
        
        embed.add_field(
            name="🏹 Ücretsiz Oyunlar",
            value="**/hunt** - Hayvan avla (2dk cooldown)\n"
                  "├ 🐀 Fare: 10-30💰\n"
                  "├ 🐇 Tavşan: 20-50💰\n"
                  "├ 🦊 Tilki: 40-80💰\n"
                  "├ 🐺 Kurt: 60-120💰\n"
                  "├ 🐻 Ayı: 100-200💰\n"
                  "├ 🦁 Aslan: 150-300💰\n"
                  "└ 🐉 Ejderha: 400-800💰\n\n"
                  "**/fish** - Balık tut (3dk cooldown)",
            inline=False
        )
        
        embed.add_field(
            name="🎰 Bahis Oyunları",
            value="**/slot** `<bahis>` - Slot makinesi\n"
                  "├ Üçlü: 10x-50x\n"
                  "└ İkili: 2x\n\n"
                  "**/coinflip** `<bahis>` - Yazı-tura (%48)\n\n"
                  "**/dice** `<bahis>` - Zar bahisi\n"
                  "├ 6 = 3x kazanç\n"
                  "├ 5 = 1.5x kazanç\n"
                  "├ 4 = İade (1x)\n"
                  "├ 3 = Kayıp\n"
                  "└ 1-2 = Ekstra ceza! 💀\n\n"
                  "**/roulette** `<bahis> <renk>` - Rulet",
            inline=False
        )
        
        embed.add_field(
            name="🃏 Strateji Oyunları",
            value="**/blackjack** `<bahis>` - 21 kart oyunu\n"
                  "├ 🃏 = Kart çek\n"
                  "└ 🛑 = Dur\n\n"
                  "**/crash** `<bahis>` - Çarpan oyunu\n"
                  "└ 🚀 = Parayı çek (reaction)",
            inline=False
        )
        
        embed.add_field(
            name="⚔️ PvP",
            value="**/battle** `@rakip <bahis>` - Bahisli savaş\n"
                  "Her iki taraf da bahis yatırır, kazanan alır!",
            inline=False
        )
        
        embed.set_footer(text="⚠️ Minimum bahis: 10💰 | Kumar bağımlılığına dikkat!")
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="müzik", description="Müzik komutlarını göster")
    async def slash_muzik_yardim(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🎵 MÜZİK KOMUTLARI", color=discord.Color.red())
        
        embed.add_field(
            name="▶️ Temel Komutlar",
            value="**/play** `<şarkı>` - YouTube'dan müzik çal\n"
                  "**/pause** - Müziği duraklat\n"
                  "**/devam** - Müziği devam ettir\n"
                  "**/skip** - Şarkıyı atla\n"
                  "**/stop** - Müziği durdur",
            inline=False
        )
        
        embed.add_field(
            name="📋 Kuyruk",
            value="**/queue** - Kuyruğu göster\n"
                  "**/np** - Şu an çalan şarkı",
            inline=False
        )
        
        embed.add_field(
            name="🔊 Kanal",
            value="**/join** - Ses kanalına katıl\n"
                  "**/leave** - Ses kanalından ayrıl",
            inline=False
        )
        
        embed.set_footer(text="🎵 YouTube'dan şarkı adı veya link ile arama yapabilirsin!")
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="moderasyon", description="Moderasyon komutlarını göster")
    async def slash_moderasyon_yardim(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🛡️ MODERASYON KOMUTLARI", color=discord.Color.red())
        
        embed.add_field(
            name="👢 Kullanıcı İşlemleri",
            value="**/kick** `@kullanıcı [sebep]` - Sunucudan at\n"
                  "**/ban** `@kullanıcı [sebep]` - Yasakla\n"
                  "**/unban** `<kullanıcı_id>` - Yasağı kaldır",
            inline=False
        )
        
        embed.add_field(
            name="🔇 Susturma",
            value="**/timeout** `@kullanıcı <dakika> [sebep]` - Sustur\n"
                  "**/untimeout** `@kullanıcı` - Susturmayı kaldır",
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Uyarı Sistemi",
            value="**/uyar** `@kullanıcı <sebep>` - Uyarı ver\n"
                  "**/uyarılar** `[@kullanıcı]` - Uyarıları göster\n"
                  "**/uyarısil** `@kullanıcı` - Tüm uyarıları sil",
            inline=False
        )
        
        embed.add_field(
            name="🗑️ Mesaj",
            value="**/sil** `<miktar>` - Mesaj sil (1-100)",
            inline=False
        )
        
        embed.set_footer(text="🛡️ Bu komutlar için yetki gerekir!")
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="aiyardım", description="AI komutlarını göster")
    async def slash_ai_yardim(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🤖 YAPAY ZEKA KOMUTLARI", color=discord.Color.blue())
        
        embed.add_field(
            name="💬 Hafızalı Sohbet",
            value="**/ai** `<soru>` - AI'ya soru sor\n"
                  "├ 🧠 Son 4 mesajlaşmayı hatırlar\n"
                  "├ 🎭 Aktif role göre cevap verir\n"
                  "└ Her kullanıcının ayrı hafızası var",
            inline=False
        )
        
        embed.add_field(
            name="🎭 Rol Sistemi",
            value="**/rol** - 12 hazır rolden birini seç\n"
                  "├ 🏴‍☠️ Korsan | 🌸 Anime | 🤔 Filozof\n"
                  "├ 🎤 Rapper | 🔍 Dedektif | 👨‍🍳 Aşçı\n"
                  "├ 🔬 Bilimci | 🐱 Kedi | 🤖 Robot\n"
                  "└ 🧛 Vampir | 📹 YouTuber | 💼 Asistan\n\n"
                  "**/özelrol** `<açıklama>` - Kendi rolünü yaz\n"
                  "**/rolsıfırla** - Rol ve hafızayı sıfırla\n"
                  "**/rolbilgi** - Aktif rol ve hafıza durumu",
            inline=False
        )
        
        embed.add_field(
            name="🧠 Hafıza Yönetimi",
            value="**/hafızasil** - AI hafızasını temizle\n"
                  "├ Son 4 soru-cevap kayıtlı\n"
                  "└ Sıfırdan başlamak için temizle",
            inline=False
        )
        
        embed.add_field(
            name="🎨 Görsel Oluşturma",
            value="**/görsel** `<prompt>` `[boyut]` - AI ile görsel oluştur\n"
                  "├ 📱 Kare: 1024x1024 (varsayılan)\n"
                  "├ 🖥️ Geniş: 1280x720\n"
                  "├ 📱 Dikey: 720x1280\n"
                  "├ 🎬 Sinematik: 1920x1080\n"
                  "└ 📸 Portre: 768x1024\n\n"
                  "💡 İngilizce prompt daha iyi sonuç verir!\n"
                  "Türkçe yazarsan otomatik çevrilir.",
            inline=False
        )
        
        embed.add_field(
            name="🌍 Çeviri",
            value="**/tercume** `<dil> <metin>` - Metin çevir\n"
                  "Örnek: `/tercume ingilizce Merhaba dünya`",
            inline=False
        )
        
        embed.add_field(
            name="📖 Yaratıcı",
            value="**/hikaye** `<konu>` - Hikaye oluştur\n"
                  "**/şiir** `<konu>` - Şiir yaz\n"
                  "**/kod** `<dil> <istek>` - Kod yaz",
            inline=False
        )
        
        embed.add_field(
            name="📝 Araçlar",
            value="**/özet** `<metin>` - Metni özetle",
            inline=False
        )
        
        embed.set_footer(text="🤖 Powered by Groq AI (Llama 3.1) & Pollinations.ai 🎨")
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="eğlence", description="Eğlence komutlarını göster")
    async def slash_eglence_yardim(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🎲 EĞLENCE KOMUTLARI", color=discord.Color.purple())
        
        embed.add_field(
            name="🖼️ Profil",
            value="**/avatar** `[@kullanıcı]` - Profil resmini göster",
            inline=False
        )
        
        embed.add_field(
            name="🎬 Aykut Elmas",
            value="**/aykut** - Rastgele Aykut Elmas GIF'i (43 GIF)",
            inline=False
        )
        
        embed.add_field(
            name="😂 Şaka & Sihir",
            value="**/şaka** - Rastgele programcı şakası\n"
                  "**/8ball** `<soru>` - Sihirli küreye sor\n"
                  "**/seç** `<seçenek1, seçenek2, ...>` - Seçeneklerden birini seç\n"
                  "**/şanslısayı** - 1-100 arası şanslı sayı",
            inline=False
        )
        
        embed.add_field(
            name="💕 Sosyal",
            value="**/sarıl** `@kullanıcı` - Birine sarıl\n"
                  "**/tokatlat** `@kullanıcı` - Birine tokat at\n"
                  "**/aşkmetre** `@kişi1 @kişi2` - İki kişinin aşk oranı",
            inline=False
        )
        
        embed.add_field(
            name="📏 Testler (18+) 😏",
            value="**/kaçcm** `[@kullanıcı]` - Boy ölçümü 📏\n"
                  "├ Kullanıcıya özel sabit sonuç\n"
                  "├ 1-30 cm arası\n"
                  "└ Eğlenceli yorumlar\n\n"
                  "**/gaytest** `[@kullanıcı]` - Gay testi 🏳️‍🌈\n"
                  "├ %0-100 arası oran\n"
                  "└ Renkli grafik bar\n\n"
                  "**/iqtest** `[@kullanıcı]` - IQ testi 🧠\n"
                  "├ 50-200 arası IQ\n"
                  "└ Einstein karşılaştırması",
            inline=False
        )
        
        embed.add_field(
            name="🎲 Zar & Yazı Tura",
            value="**/zar** - Zar at (1-6)\n"
                  "**/yazıtura** - Yazı mı tura mı?",
            inline=False
        )
        
        embed.set_footer(text="⚠️ Test sonuçları tamamen şaka amaçlıdır!")
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="sayaçlar", description="YKS ve özel gün sayaçlarını göster")
    async def slash_sayaclar_yardim(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📅 SAYAÇ KOMUTLARI", color=discord.Color.blue())
        
        embed.add_field(
            name="📚 YKS Sayacı",
            value="**/yks** - Tüm YKS sınavlarına kalan süre\n"
                  "**/yks TYT** - Sadece TYT'ye kalan\n"
                  "**/yks AYT** - Sadece AYT'ye kalan\n"
                  "**/yks YDT** - Sadece YDT'ye kalan\n\n"
                  "📊 Gösterilen bilgiler:\n"
                  "├ 📅 Tarih ve saat\n"
                  "├ ⏳ Gün, saat, dakika, saniye\n"
                  "├ 📅 Hafta bazında hesaplama\n"
                  "├ 📊 İlerleme çubuğu\n"
                  "└ 💬 Motivasyon mesajları",
            inline=False
        )
        
        embed.add_field(
            name="📅 Özel Günler Sayacı",
            value="**/sayaç** - Yaklaşan tüm özel günler\n"
                  "**/sayaç ramazan** - Ramazan'a kalan\n"
                  "**/sayaç kurban** - Kurban Bayramı'na kalan\n"
                  "**/sayaç 29 ekim** - 29 Ekim'e kalan\n"
                  "**/sayaç yılbaşı** - Yılbaşı'na kalan\n\n"
                  "📋 Dahil olan günler:\n"
                  "├ 🇹🇷 Resmi tatiller (23 Nisan, 19 Mayıs...)\n"
                  "├ 🌙 Dini bayramlar (Ramazan, Kurban)\n"
                  "├ 💕 Özel günler (Sevgililer, Anneler günü...)\n"
                  "├ 📝 Okul/Sınav (YKS, LGS, Karne...)\n"
                  "└ 🎃 Eğlence (Cadılar bayramı, Black Friday...)",
            inline=False
        )
        
        embed.set_footer(text="💡 Autocomplete ile kolayca arama yapabilirsin!")
        
        await guvenli_cevap(interaction, embed=embed)

    # =====================================================
    # 📚 PREFIX KOMUTLARI
    # =====================================================

    @commands.command(aliases=['help', 'komutlar', 'h', 'commands', 'yardim'])
    async def yardım(self, ctx):
        embed = discord.Embed(
            title="⚡ WOWSY BOT - KOMUTLAR",
            description="**`/`** (slash) komutları kullan!",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="💰 EKONOMİ",
            value="`bakiye` `günlük` `bedava` `çalış` `yatır` `çek` `gönder` `soygun` `faiz` `zenginler`",
            inline=False
        )
        
        embed.add_field(
            name="🎮 OYUNLAR",
            value="`hunt` `fish` `slot` `coinflip` `dice` `roulette` `blackjack` `crash` `battle`",
            inline=False
        )
        
        embed.add_field(
            name="🎵 MÜZİK",
            value="`play` `pause` `devam` `skip` `stop` `leave` `queue` `join`",
            inline=False
        )
        
        embed.add_field(
            name="🛡️ MODERASYON",
            value="`kick` `ban` `unban` `sil` `timeout` `untimeout` `uyar` `uyarılar`",
            inline=False
        )
        
        embed.add_field(
            name="🎲 EĞLENCE",
            value="`aykut` `avatar` `şaka` `8ball` `sarıl` `tokatlat` `seç` `aşkmetre` `kaçcm` `gaytest` `iqtest`",
            inline=False
        )
        
        embed.add_field(
            name="🤖 YAPAY ZEKA",
            value="`ai` `rol` `özelrol` `rolsıfırla` `rolbilgi` `görsel` `tercume` `hikaye` `özet` `kod` `şiir`",
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ BİLGİ & SAYAÇLAR",
            value="`ping` `sunucu` `kullanıcı` `botbilgi` `davet` `yks` `sayaç` `yardım`",
            inline=False
        )
        
        embed.set_footer(text="⚡ WOWSY Bot | Detay için /aiyardım, /ekonomi, /oyunlar, /eğlence, /sayaçlar")
        
        if self.bot.user:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await ctx.send(embed=embed)

    @commands.command(aliases=['ekonomiyardım'])
    async def ekonomi(self, ctx):
        embed = discord.Embed(title="💰 EKONOMİ KOMUTLARI", color=discord.Color.gold())
        
        embed.add_field(
            name="📊 Temel",
            value="`/bakiye` - Para görüntüle\n"
                  "`/günlük` - 24 saatte bir\n"
                  "`/bedava` - 2 saatte bir\n"
                  "`/çalış` - 30 dakikada bir",
            inline=True
        )
        
        embed.add_field(
            name="🏦 Banka",
            value="`/yatır <miktar>` - Yatır\n"
                  "`/çek <miktar>` - Çek\n"
                  "`/gönder @kişi <miktar>`\n"
                  "`/faiz` - Faiz topla",
            inline=True
        )
        
        embed.add_field(
            name="📈 Diğer",
            value="`/soygun @kişi` - Riskli!\n"
                  "`/zenginler` - Top 10",
            inline=True
        )
        
        embed.set_footer(text="💡 Bankaya para yatır, faiz kazan!")
        
        await ctx.send(embed=embed)

    @commands.command(aliases=['oyunlaryardım', 'games'])
    async def oyunlar(self, ctx):
        embed = discord.Embed(title="🎮 OYUN KOMUTLARI", color=discord.Color.purple())
        
        embed.add_field(
            name="🆓 Ücretsiz",
            value="`/hunt` - Avlan (2dk)\n"
                  "`/fish` - Balık tut (3dk)",
            inline=True
        )
        
        embed.add_field(
            name="🎰 Bahis",
            value="`/slot <bahis>`\n"
                  "`/coinflip <bahis>`\n"
                  "`/dice <bahis>`\n"
                  "`/roulette <bahis> <renk>`",
            inline=True
        )
        
        embed.add_field(
            name="🃏 Strateji",
            value="`/blackjack <bahis>`\n"
                  "`/crash <bahis>`\n"
                  "`/battle @kişi <bahis>`",
            inline=True
        )
        
        embed.set_footer(text="⚠️ Minimum bahis: 10💰")
        
        await ctx.send(embed=embed)

    @commands.command(aliases=['müzikyardım', 'music'])
    async def müzik(self, ctx):
        embed = discord.Embed(title="🎵 MÜZİK KOMUTLARI", color=discord.Color.red())
        
        embed.add_field(
            name="▶️ Temel",
            value="`/play <şarkı>` - Çal\n"
                  "`/pause` - Duraklat\n"
                  "`/devam` - Devam et\n"
                  "`/skip` - Atla\n"
                  "`/stop` - Durdur",
            inline=True
        )
        
        embed.add_field(
            name="📋 Diğer",
            value="`/queue` - Kuyruk\n"
                  "`/join` - Katıl\n"
                  "`/leave` - Ayrıl\n"
                  "`/np` - Şu an çalan",
            inline=True
        )
        
        await ctx.send(embed=embed)

    @commands.command(aliases=['eğlenceyardım', 'fun'])
    async def eglence(self, ctx):
        embed = discord.Embed(title="🎲 EĞLENCE KOMUTLARI", color=discord.Color.purple())
        
        embed.add_field(
            name="😂 Genel",
            value="`/aykut` - Aykut Elmas GIF\n"
                  "`/avatar` - Profil resmi\n"
                  "`/şaka` - Rastgele şaka\n"
                  "`/8ball <soru>` - Sihirli küre\n"
                  "`/seç <a, b, c>` - Seçim yap",
            inline=True
        )
        
        embed.add_field(
            name="💕 Sosyal",
            value="`/sarıl @kişi`\n"
                  "`/tokatlat @kişi`\n"
                  "`/aşkmetre @k1 @k2`",
            inline=True
        )
        
        embed.add_field(
            name="📏 Testler 😏",
            value="`/kaçcm` - Boy ölçümü\n"
                  "`/gaytest` - Gay testi\n"
                  "`/iqtest` - IQ testi",
            inline=True
        )
        
        embed.set_footer(text="⚠️ Test sonuçları şaka amaçlıdır!")
        
        await ctx.send(embed=embed)

    @commands.command(aliases=['sayaçyardım', 'ykssayaç'])
    async def sayaclar(self, ctx):
        embed = discord.Embed(title="📅 SAYAÇ KOMUTLARI", color=discord.Color.blue())
        
        embed.add_field(
            name="📚 YKS",
            value="`/yks` - TYT'ye kalan\n"
                  "`/yks TYT` - TYT sayacı\n"
                  "`/yks AYT` - AYT sayacı\n"
                  "`/yks hepsi` - Tüm sınavlar",
            inline=True
        )
        
        embed.add_field(
            name="📅 Özel Günler",
            value="`/sayaç` - Yaklaşan günler\n"
                  "`/sayaç ramazan`\n"
                  "`/sayaç kurban`\n"
                  "`/sayaç 29 ekim`\n"
                  "`/sayaç yılbaşı`",
            inline=True
        )
        
        embed.add_field(
            name="📋 Dahil Günler",
            value="🇹🇷 Resmi tatiller\n"
                  "🌙 Dini bayramlar\n"
                  "💕 Özel günler\n"
                  "📝 Sınavlar\n"
                  "🎃 Eğlence",
            inline=True
        )
        
        embed.set_footer(text="💡 /sayaç yazınca autocomplete ile ara!")
        
        await ctx.send(embed=embed)


# =====================================================
# 🔧 COG YÜKLEME
# =====================================================

async def setup(bot):
    await bot.add_cog(Yardim(bot))
