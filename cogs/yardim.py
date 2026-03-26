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
            description="Hem **`/`** (slash) hem **`!`** (prefix) komutları kullanabilirsin!\n\n"
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
                  "```",
            inline=True
        )
        
        embed.add_field(
            name="🤖 YAPAY ZEKA",
            value="```\n"
                  "ai      - Soru sor\n"
                  "tercume - Çeviri yap\n"
                  "hikaye  - Hikaye oluştur\n"
                  "özet    - Metin özetle\n"
                  "kod     - Kod yaz\n"
                  "şiir    - Şiir yaz\n"
                  "```",
            inline=True
        )
        
        embed.add_field(
            name="ℹ️ BİLGİ",
            value="```\n"
                  "ping    - Bot gecikmesi\n"
                  "sunucu  - Sunucu bilgisi\n"
                  "kullanıcı- Kullanıcı bilgi\n"
                  "botbilgi- Bot hakkında\n"
                  "davet   - Davet linki\n"
                  "yardım  - Bu menü\n"
                  "```",
            inline=True
        )
        
        embed.set_footer(text="⚡ WOWSY Bot | Geliştirici: Ömer | /ekonomi veya /oyunlar ile detay al!")
        
        if self.bot.user:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="ekonomi", description="Ekonomi komutlarını göster")
    async def slash_ekonomi_yardim(self, interaction: discord.Interaction):
        embed = discord.Embed(title="💰 EKONOMİ KOMUTLARI", color=discord.Color.gold())
        
        embed.add_field(
            name="📊 Temel Komutlar",
            value="**/bakiye** `[@kullanıcı]` - Para görüntüle\n"
                  "**/günlük** - 24 saatte bir ödül (streak bonusu)\n"
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
            name="🔫 Riskli İşlemler",
            value="**/soygun** `@kullanıcı` - %25 başarı, 1 saat cooldown\n"
                  "Başarısız olursan 200-500💰 ceza!",
            inline=False
        )
        
        embed.add_field(
            name="📈 Sıralama",
            value="**/zenginler** - En zengin 10 kişi",
            inline=False
        )
        
        embed.set_footer(text="💡 Yeni başlayanlar 1000💰 ile başlar!")
        
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
                  "**/coinflip** `<bahis>` - Yazı-tura (%48)\n"
                  "**/dice** `<bahis>` - Zar (6=5x, 5=3x, 4=1.5x)\n"
                  "**/roulette** `<bahis> <renk>` - Rulet",
            inline=False
        )
        
        embed.add_field(
            name="🃏 Strateji Oyunları",
            value="**/blackjack** `<bahis>` - 21 kart oyunu\n"
                  "├ 'ç' = Kart çek\n"
                  "└ 'd' = Dur\n\n"
                  "**/crash** `<bahis>` - Çarpan oyunu\n"
                  "└ 'ç' = Parayı çek",
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
            name="💬 Sohbet",
            value="**/ai** `<soru>` - AI'ya soru sor\n"
                  "Her türlü soruyu sorabilirsin!",
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
        
        embed.set_footer(text="🤖 Powered by Groq AI (Llama 3.1)")
        
        await guvenli_cevap(interaction, embed=embed)

    # =====================================================
    # 📚 PREFIX KOMUTLARI
    # =====================================================

    @commands.command(aliases=['help', 'komutlar', 'h', 'commands', 'yardim'])
    async def yardım(self, ctx):
        embed = discord.Embed(
            title="⚡ WOWSY BOT - KOMUTLAR",
            description="Hem **`/`** (slash) hem **`!`** (prefix) komutları kullanabilirsin!",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="💰 EKONOMİ",
            value="`bakiye` `günlük` `bedava` `çalış` `yatır` `çek` `gönder` `soygun` `zenginler`",
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
            value="`avatar` `şaka` `8ball` `sarıl` `tokatlat` `seç` `aşkmetre`",
            inline=False
        )
        
        embed.add_field(
            name="🤖 YAPAY ZEKA",
            value="`ai` `tercume` `hikaye` `özet` `şiir`",
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ BİLGİ",
            value="`ping` `sunucu` `kullanıcı` `botbilgi` `davet` `yardım`",
            inline=False
        )
        
        embed.set_footer(text="⚡ WOWSY Bot | Detay için /ekonomi, /oyunlar, /müzik")
        
        if self.bot.user:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await ctx.send(embed=embed)

    @commands.command(aliases=['ekonomiyardım'])
    async def ekonomi(self, ctx):
        embed = discord.Embed(title="💰 EKONOMİ KOMUTLARI", color=discord.Color.gold())
        
        embed.add_field(
            name="📊 Temel",
            value="`!bakiye` - Para görüntüle\n"
                  "`!günlük` - 24 saatte bir\n"
                  "`!bedava` - 2 saatte bir\n"
                  "`!çalış` - 30 dakikada bir",
            inline=True
        )
        
        embed.add_field(
            name="🏦 Banka",
            value="`!yatır <miktar>` - Yatır\n"
                  "`!çek <miktar>` - Çek\n"
                  "`!gönder @kişi <miktar>`",
            inline=True
        )
        
        embed.add_field(
            name="📈 Diğer",
            value="`!soygun @kişi` - Riskli!\n"
                  "`!zenginler` - Top 10",
            inline=True
        )
        
        await ctx.send(embed=embed)

    @commands.command(aliases=['oyunlaryardım', 'games'])
    async def oyunlar(self, ctx):
        embed = discord.Embed(title="🎮 OYUN KOMUTLARI", color=discord.Color.purple())
        
        embed.add_field(
            name="🆓 Ücretsiz",
            value="`!hunt` - Avlan (2dk)\n"
                  "`!fish` - Balık tut (3dk)",
            inline=True
        )
        
        embed.add_field(
            name="🎰 Bahis",
            value="`!slot <bahis>`\n"
                  "`!coinflip <bahis>`\n"
                  "`!dice <bahis>`\n"
                  "`!roulette <bahis> <renk>`",
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
            value="`!play <şarkı>` - Çal\n"
                  "`!pause` - Duraklat\n"
                  "`!devam` - Devam et\n"
                  "`!skip` - Atla\n"
                  "`!stop` - Durdur",
            inline=True
        )
        
        embed.add_field(
            name="📋 Diğer",
            value="`!queue` - Kuyruk\n"
                  "`!join` - Katıl\n"
                  "`!leave` - Ayrıl\n"
                  "`!np` - Şu an çalan",
            inline=True
        )
        
        await ctx.send(embed=embed)

# =====================================================
# 🔧 COG YÜKLEME
# =====================================================

async def setup(bot):
    await bot.add_cog(Yardim(bot))