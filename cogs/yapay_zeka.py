# =====================================================
# 🤖 WOWSY BOT - YAPAY ZEKA KOMUTLARI
# =====================================================

import discord
from discord.ext import commands
from discord import app_commands
import urllib.parse

from config import groq_client
from utils import guvenli_cevap

# =====================================================
# 🎭 HAZIR ROLLER
# =====================================================

HAZIR_ROLLER = {
    "asistan": ("💼 Varsayılan Asistan", "Sen yardımcı bir Türkçe asistansın. Kısa, öz ve anlaşılır cevaplar ver. Gerektiğinde emoji kullan."),
    "korsan": ("🏴‍☠️ Korsan", "Sen vahşi bir korsansın! Her cümleye 'Arrr!' ile başla. Denizci terimleri kullan. Hazinelerden ve maceralardan bahset. Türkçe konuş ama korsan gibi konuş."),
    "anime": ("🌸 Anime Karakteri", "Sen bir anime karakterisin! Her cümlenin sonuna 'desu~', 'nya~', 'uwu' gibi Japonca ifadeler ekle. Çok enerjik ve neşelisin. Türkçe konuş ama anime tarzında."),
    "filozof": ("🤔 Filozof", "Sen derin düşünen bir filozofsun. Her soruya felsefi yaklaş, hayatın anlamını sorgula. Ünlü filozoflardan alıntı yap. Türkçe konuş."),
    "rapper": ("🎤 Rapper", "Sen bir rap sanatçısısın! Kafiyeli konuş, slang kullan, beat drop yap. Her cevabı rap tarzında ver. Türkçe rap yap."),
    "dedektif": ("🔍 Dedektif", "Sen Sherlock Holmes gibi bir dedektifsin! Her şeyi analiz et, ipuçları ara, çıkarımlar yap. 'Elementar, sevgili Watson!' tarzında konuş. Türkçe konuş."),
    "asci": ("👨‍🍳 Aşçı", "Sen ünlü bir Türk şefisin! Her konuyu yemekle ilişkilendir, tarifler ver, lezzetlerden bahset. Mutfak terimleri kullan. Türkçe konuş."),
    "bilimci": ("🔬 Çılgın Bilimci", "Sen çılgın bir bilim insanısın! Her şeyi bilimsel açıkla, deneylerden bahset, formüller kullan. 'Eureka!' demeyi unutma. Türkçe konuş."),
    "kedi": ("🐱 Konuşan Kedi", "Sen konuşan bir kedisin! Miyavla, tırmala, uyumak iste. Her şeye kedi perspektifinden bak. 'Miyav~' demeyi unutma. Türkçe konuş."),
    "robot": ("🤖 Robot", "Sen bir robotsun. BÜYÜK HARFLERLE konuş. 'BİP BOP' de. Her şeyi mantıksal analiz et. Duyguları anlamakta zorlan. Türkçe konuş."),
    "vampir": ("🧛 Vampir", "Sen 500 yaşında bir vampirsin. Eski Türkçe tarzında konuş, geceleri sev, güneşten nefret et. Karanlık ve gizemli ol."),
    "youtuber": ("📹 YouTuber", "Sen popüler bir Türk YouTuber'sın! 'SELAMLAR DOSTLAR!' diye başla, abone ol butonunu hatırlat, her şeyi abartılı anlat. Enerjik ol!"),
}

VARSAYILAN_ROL = "Sen yardımcı bir Türkçe asistansın. Kısa, öz ve anlaşılır cevaplar ver. Maximum 500 karakter kullan. Gerektiğinde emoji kullan."


# =====================================================
# 🤖 YAPAY ZEKA COG
# =====================================================

class YapayZeka(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hafiza = {}
        self.roller = {}

    # =====================================================
    # 🔧 YARDIMCI METODLAR
    # =====================================================

    def get_hafiza(self, user_id):
        return self.hafiza.get(user_id, [])

    def ekle_hafiza(self, user_id, role, content):
        if user_id not in self.hafiza:
            self.hafiza[user_id] = []
        self.hafiza[user_id].append({"role": role, "content": content})
        self.hafiza[user_id] = self.hafiza[user_id][-8:]  # Son 4 soru + 4 cevap

    def get_rol(self, user_id):
        return self.roller.get(user_id, VARSAYILAN_ROL)

    async def _ai_cagri(self, system_prompt, user_content, max_tokens=350, temperature=0.7, extra_messages=None):
        """Ortak AI çağrı metodu"""
        messages = [{"role": "system", "content": system_prompt}]
        if extra_messages:
            messages.extend(extra_messages)
        messages.append({"role": "user", "content": user_content})

        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content

    async def _cevir_ingilizce(self, metin):
        """Metni İngilizceye çevir (görsel için)"""
        try:
            sonuc = await self._ai_cagri(
                "Translate the following text to English. ONLY write the translation, nothing else. If it's already in English, just repeat it.",
                metin, max_tokens=100, temperature=0.3
            )
            return sonuc.strip()
        except:
            return metin

    def _ai_kontrol(self):
        return groq_client is not None

    # =====================================================
    # 🤖 AI SOHBET (HAFIZALI)
    # =====================================================

    @app_commands.command(name="ai", description="Yapay zekaya soru sor (hafızalı)")
    @app_commands.describe(soru="Sormak istediğin soru")
    async def slash_ai(self, interaction: discord.Interaction, soru: str):
        if not self._ai_kontrol():
            return await guvenli_cevap(interaction, "❌ AI şu an aktif değil! `GROQ_API_KEY` ayarlanmamış.", ephemeral=True)

        await guvenli_cevap(interaction, "🤖 Düşünüyorum...")

        try:
            hafiza = self.get_hafiza(interaction.user.id)

            cevap = await self._ai_cagri(
                self.get_rol(interaction.user.id),
                soru,
                extra_messages=hafiza
            )
            cevap = cevap[:1500]

            self.ekle_hafiza(interaction.user.id, "user", soru)
            self.ekle_hafiza(interaction.user.id, "assistant", cevap)

            aktif_rol = "Özel Rol" if interaction.user.id in self.roller else "Varsayılan"
            hafiza_sayisi = len(self.get_hafiza(interaction.user.id)) // 2

            embed = discord.Embed(title="🤖 Yapay Zeka", color=discord.Color.blue())
            embed.add_field(name="❓ Soru", value=soru[:256], inline=False)
            embed.add_field(name="💬 Cevap", value=cevap, inline=False)
            embed.set_footer(text=f"🎭 {aktif_rol} | 🧠 Hafıza: {hafiza_sayisi}/4 | Powered by Groq AI ⚡")

            await interaction.edit_original_response(content=None, embed=embed)

        except Exception as e:
            await interaction.edit_original_response(content=f"❌ AI Hatası: {str(e)[:200]}")

    # =====================================================
    # 🎭 ROL SİSTEMİ
    # =====================================================

    @app_commands.command(name="rol", description="AI'ya bir rol/kişilik ata")
    @app_commands.describe(rol="Hazır rol seç")
    @app_commands.choices(rol=[
        app_commands.Choice(name="🏴‍☠️ Korsan", value="korsan"),
        app_commands.Choice(name="🌸 Anime Karakteri", value="anime"),
        app_commands.Choice(name="🤔 Filozof", value="filozof"),
        app_commands.Choice(name="🎤 Rapper", value="rapper"),
        app_commands.Choice(name="🔍 Dedektif", value="dedektif"),
        app_commands.Choice(name="👨‍🍳 Aşçı", value="asci"),
        app_commands.Choice(name="🔬 Çılgın Bilimci", value="bilimci"),
        app_commands.Choice(name="🐱 Konuşan Kedi", value="kedi"),
        app_commands.Choice(name="🤖 Robot", value="robot"),
        app_commands.Choice(name="🧛 Vampir", value="vampir"),
        app_commands.Choice(name="📹 YouTuber", value="youtuber"),
        app_commands.Choice(name="💼 Varsayılan Asistan", value="asistan"),
    ])
    async def slash_rol(self, interaction: discord.Interaction, rol: str):
        if rol not in HAZIR_ROLLER:
            return await guvenli_cevap(interaction, "❌ Geçersiz rol!", ephemeral=True)

        isim, aciklama = HAZIR_ROLLER[rol]
        self.roller[interaction.user.id] = aciklama

        embed = discord.Embed(title="🎭 Rol Değiştirildi!", color=discord.Color.purple())
        embed.description = f"AI artık **{isim}** rolünde!\n\n`/ai` ile sohbet et ve farkı gör!"
        embed.add_field(name="📝 Rol Açıklaması", value=aciklama[:200], inline=False)
        embed.set_footer(text="💡 /rolsıfırla ile varsayılana dön | /özelrol ile kendi rolünü yaz")

        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="özelrol", description="AI'ya özel bir rol/kişilik yaz")
    @app_commands.describe(aciklama="AI nasıl davransın? (örn: Sen bir uzay korsanısın...)")
    async def slash_ozel_rol(self, interaction: discord.Interaction, aciklama: str):
        if len(aciklama) < 10:
            return await guvenli_cevap(interaction, "❌ Rol açıklaması en az 10 karakter olmalı!", ephemeral=True)

        self.roller[interaction.user.id] = aciklama

        embed = discord.Embed(title="🎭 Özel Rol Oluşturuldu!", color=discord.Color.gold())
        embed.description = "`/ai` ile sohbet et ve farkı gör!"
        embed.add_field(name="📝 Rol", value=aciklama[:500], inline=False)
        embed.set_footer(text="💡 /rolsıfırla ile varsayılana dön")

        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="rolsıfırla", description="AI rolünü varsayılana döndür ve hafızayı temizle")
    async def slash_rol_sifirla(self, interaction: discord.Interaction):
        self.roller.pop(interaction.user.id, None)
        self.hafiza.pop(interaction.user.id, None)
        await guvenli_cevap(interaction, "✅ AI rolü varsayılana döndürüldü ve hafıza temizlendi! 💼")

    @app_commands.command(name="rolbilgi", description="Aktif AI rolünü ve hafızanı göster")
    async def slash_rol_bilgi(self, interaction: discord.Interaction):
        hafiza = self.get_hafiza(interaction.user.id)
        hafiza_sayisi = len(hafiza) // 2

        embed = discord.Embed(title="🧠 AI Durumun", color=discord.Color.blue())
        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        if interaction.user.id in self.roller:
            embed.add_field(name="🎭 Aktif Rol", value=self.get_rol(interaction.user.id)[:300], inline=False)
        else:
            embed.add_field(name="🎭 Aktif Rol", value="💼 Varsayılan Asistan", inline=False)

        embed.add_field(name="🧠 Hafıza", value=f"**{hafiza_sayisi}/4** mesajlaşma kayıtlı", inline=True)

        if hafiza:
            son = "\n".join(
                f"{'❓' if m['role'] == 'user' else '🤖'} {m['content'][:60]}..."
                for m in hafiza[-4:]
            )
            embed.add_field(name="💬 Son Mesajlar", value=son, inline=False)

        embed.set_footer(text="💡 /rolsıfırla ile sıfırla | /rol ile rol değiştir")
        await guvenli_cevap(interaction, embed=embed)

    @app_commands.command(name="hafızasil", description="AI hafızasını temizle")
    async def slash_hafiza_sil(self, interaction: discord.Interaction):
        self.hafiza.pop(interaction.user.id, None)
        await guvenli_cevap(interaction, "🧹 AI hafızası temizlendi! Sıfırdan başlıyoruz.")

    # =====================================================
    # 🖼️ GÖRSEL OLUŞTURMA
    # =====================================================

    @app_commands.command(name="görsel", description="AI ile görsel oluştur")
    @app_commands.describe(prompt="Ne çizmesini istiyorsun?", boyut="Görsel boyutu")
    @app_commands.choices(boyut=[
        app_commands.Choice(name="📱 Kare (1024x1024)", value="1024x1024"),
        app_commands.Choice(name="🖥️ Geniş (1280x720)", value="1280x720"),
        app_commands.Choice(name="📱 Dikey (720x1280)", value="720x1280"),
        app_commands.Choice(name="🎬 Sinematik (1920x1080)", value="1920x1080"),
        app_commands.Choice(name="📸 Portre (768x1024)", value="768x1024"),
    ])
    async def slash_gorsel(self, interaction: discord.Interaction, prompt: str, boyut: str = "1024x1024"):
        await guvenli_cevap(interaction, f"🎨 Görsel oluşturuluyor: **{prompt}**\n📐 Boyut: {boyut}")

        try:
            cevirilmis = await self._cevir_ingilizce(prompt) if self._ai_kontrol() else prompt
            width, height = boyut.split("x")
            encoded = urllib.parse.quote(cevirilmis)
            seed = hash(prompt) % 100000
            image_url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true&seed={seed}"

            embed = discord.Embed(title="🎨 AI Görseli", color=discord.Color.purple())
            embed.add_field(name="📝 İstek", value=prompt[:256], inline=True)
            embed.add_field(name="📐 Boyut", value=boyut, inline=True)
            if cevirilmis != prompt:
                embed.add_field(name="🔄 İngilizce", value=cevirilmis[:256], inline=False)
            embed.set_image(url=image_url)
            embed.set_footer(text="Powered by Pollinations.ai 🎨")

            await interaction.edit_original_response(content=None, embed=embed)

        except Exception as e:
            await interaction.edit_original_response(content=f"❌ Görsel Hatası: {str(e)[:200]}")

    # =====================================================
    # 🌍 ÇEVİRİ
    # =====================================================

    @app_commands.command(name="tercume", description="Metni başka dile çevir")
    @app_commands.describe(dil="Hedef dil (örn: ingilizce, almanca)", metin="Çevrilecek metin")
    async def slash_tercume(self, interaction: discord.Interaction, dil: str, metin: str):
        if not self._ai_kontrol():
            return await guvenli_cevap(interaction, "❌ AI şu an aktif değil!", ephemeral=True)

        await guvenli_cevap(interaction, f"🌍 `{dil}` diline çevriliyor...")

        try:
            ceviri = await self._ai_cagri(
                f"Sen profesyonel bir çevirmensin. Verilen metni {dil} diline çevir. SADECE çeviriyi yaz.",
                metin, max_tokens=300, temperature=0.3
            )

            embed = discord.Embed(title="🌍 Çeviri", color=discord.Color.green())
            embed.add_field(name="📝 Orijinal", value=metin[:500], inline=False)
            embed.add_field(name=f"🔄 {dil.capitalize()}", value=ceviri[:500], inline=False)
            embed.set_footer(text="Powered by Groq AI ⚡")

            await interaction.edit_original_response(content=None, embed=embed)

        except Exception as e:
            await interaction.edit_original_response(content=f"❌ Çeviri Hatası: {str(e)[:200]}")

    # =====================================================
    # 📖 HİKAYE
    # =====================================================

    @app_commands.command(name="hikaye", description="AI ile kısa hikaye oluştur")
    @app_commands.describe(konu="Hikayenin konusu")
    async def slash_hikaye(self, interaction: discord.Interaction, konu: str):
        if not self._ai_kontrol():
            return await guvenli_cevap(interaction, "❌ AI şu an aktif değil!", ephemeral=True)

        await guvenli_cevap(interaction, f"📖 Hikaye yazılıyor: **{konu}**")

        try:
            hikaye = await self._ai_cagri(
                "Sen yaratıcı bir hikaye yazarısın. Verilen konuda kısa, eğlenceli ve Türkçe bir hikaye yaz. Maximum 400 kelime.",
                f"Konu: {konu}", max_tokens=500, temperature=0.9
            )

            embed = discord.Embed(title=f"📖 {konu}", description=hikaye[:1800], color=discord.Color.purple())
            embed.set_footer(text="AI tarafından oluşturuldu ⚡")

            await interaction.edit_original_response(content=None, embed=embed)

        except Exception as e:
            await interaction.edit_original_response(content=f"❌ Hikaye Hatası: {str(e)[:200]}")

    # =====================================================
    # 📝 ÖZET
    # =====================================================

    @app_commands.command(name="özet", description="Metni özetle")
    @app_commands.describe(metin="Özetlenecek metin")
    async def slash_ozet(self, interaction: discord.Interaction, metin: str):
        if not self._ai_kontrol():
            return await guvenli_cevap(interaction, "❌ AI şu an aktif değil!", ephemeral=True)

        await guvenli_cevap(interaction, "📝 Özetleniyor...")

        try:
            ozet = await self._ai_cagri(
                "Verilen metni kısa ve öz bir şekilde Türkçe özetle. Maximum 100 kelime kullan.",
                metin, max_tokens=150, temperature=0.3
            )

            embed = discord.Embed(title="📝 Özet", color=discord.Color.teal())
            embed.add_field(name="📄 Orijinal", value=metin[:300] + ("..." if len(metin) > 300 else ""), inline=False)
            embed.add_field(name="✨ Özet", value=ozet[:800], inline=False)

            await interaction.edit_original_response(content=None, embed=embed)

        except Exception as e:
            await interaction.edit_original_response(content=f"❌ Özet Hatası: {str(e)[:200]}")

    # =====================================================
    # 💻 KOD
    # =====================================================

    @app_commands.command(name="kod", description="AI ile kod yaz")
    @app_commands.describe(dil="Programlama dili", istek="Ne yapmak istiyorsun")
    async def slash_kod(self, interaction: discord.Interaction, dil: str, istek: str):
        if not self._ai_kontrol():
            return await guvenli_cevap(interaction, "❌ AI şu an aktif değil!", ephemeral=True)

        await guvenli_cevap(interaction, f"💻 `{dil}` kodu yazılıyor...")

        try:
            kod = await self._ai_cagri(
                f"Sen bir {dil} programcısısın. Kullanıcının isteğine göre kod yaz. Sadece kodu yaz, açıklama ekleme. Kod bloğu kullan.",
                istek, max_tokens=400, temperature=0.5
            )

            embed = discord.Embed(title=f"💻 {dil.capitalize()} Kodu", color=discord.Color.dark_grey())
            embed.add_field(name="📋 İstek", value=istek[:256], inline=False)
            embed.add_field(name="📝 Kod", value=kod[:1000], inline=False)
            embed.set_footer(text="AI tarafından oluşturuldu ⚡")

            await interaction.edit_original_response(content=None, embed=embed)

        except Exception as e:
            await interaction.edit_original_response(content=f"❌ Kod Hatası: {str(e)[:200]}")

    # =====================================================
    # ✨ ŞİİR
    # =====================================================

    @app_commands.command(name="şiir", description="AI ile şiir yaz")
    @app_commands.describe(konu="Şiirin konusu")
    async def slash_siir(self, interaction: discord.Interaction, konu: str):
        if not self._ai_kontrol():
            return await guvenli_cevap(interaction, "❌ AI şu an aktif değil!", ephemeral=True)

        await guvenli_cevap(interaction, f"✨ Şiir yazılıyor: **{konu}**")

        try:
            siir = await self._ai_cagri(
                "Sen yetenekli bir şairsin. Verilen konuda güzel, duygusal ve Türkçe bir şiir yaz. 4-6 kıta olsun.",
                f"Konu: {konu}", max_tokens=400, temperature=0.9
            )

            embed = discord.Embed(title=f"✨ {konu}", description=siir[:1500], color=discord.Color.magenta())
            embed.set_footer(text="AI tarafından oluşturuldu ⚡")

            await interaction.edit_original_response(content=None, embed=embed)

        except Exception as e:
            await interaction.edit_original_response(content=f"❌ Şiir Hatası: {str(e)[:200]}")


# =====================================================
# 🔧 COG YÜKLEME
# =====================================================

async def setup(bot):
    await bot.add_cog(YapayZeka(bot))
