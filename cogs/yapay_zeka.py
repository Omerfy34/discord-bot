# =====================================================
# 🤖 WOWSY BOT - YAPAY ZEKA KOMUTLARI
# =====================================================

import discord
from discord.ext import commands
from discord import app_commands

from config import groq_client
from utils import guvenli_cevap

# =====================================================
# 🤖 YAPAY ZEKA COG
# =====================================================

class YapayZeka(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =====================================================
    # 🤖 SLASH KOMUTLARI
    # =====================================================

    @app_commands.command(name="ai", description="Yapay zekaya soru sor")
    @app_commands.describe(soru="Sormak istediğin soru")
    async def slash_ai(self, interaction: discord.Interaction, soru: str):
        if not groq_client:
            await guvenli_cevap(interaction, "❌ AI şu an aktif değil! `GROQ_API_KEY` ayarlanmamış.", ephemeral=True)
            return
        
        await guvenli_cevap(interaction, "🤖 Düşünüyorum...")
        
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "Sen yardımcı bir Türkçe asistansın. Kısa, öz ve anlaşılır cevaplar ver. Maximum 500 karakter kullan. Gerektiğinde emoji kullan."
                    },
                    {
                        "role": "user",
                        "content": soru
                    }
                ],
                max_tokens=250,
                temperature=0.7
            )
            
            cevap = response.choices[0].message.content[:1500]
            
            embed = discord.Embed(title="🤖 Yapay Zeka", color=discord.Color.blue())
            embed.add_field(name="❓ Soru", value=soru[:256], inline=False)
            embed.add_field(name="💬 Cevap", value=cevap, inline=False)
            embed.set_footer(text="Powered by Groq AI ⚡")
            
            await interaction.edit_original_response(content=None, embed=embed)
            
        except Exception as e:
            await interaction.edit_original_response(content=f"❌ AI Hatası: {str(e)[:200]}")

    @app_commands.command(name="tercume", description="Metni başka dile çevir")
    @app_commands.describe(dil="Hedef dil (örn: ingilizce, almanca, fransızca)", metin="Çevrilecek metin")
    async def slash_tercume(self, interaction: discord.Interaction, dil: str, metin: str):
        if not groq_client:
            await guvenli_cevap(interaction, "❌ AI şu an aktif değil!", ephemeral=True)
            return
        
        await guvenli_cevap(interaction, f"🌍 `{dil}` diline çevriliyor...")
        
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": f"Sen profesyonel bir çevirmensin. Verilen metni {dil} diline çevir. SADECE çeviriyi yaz, başka açıklama ekleme."
                    },
                    {
                        "role": "user",
                        "content": metin
                    }
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            ceviri = response.choices[0].message.content[:1000]
            
            embed = discord.Embed(title="🌍 Çeviri", color=discord.Color.green())
            embed.add_field(name="📝 Orijinal", value=metin[:500], inline=False)
            embed.add_field(name=f"🔄 {dil.capitalize()}", value=ceviri[:500], inline=False)
            embed.set_footer(text="Powered by Groq AI ⚡")
            
            await interaction.edit_original_response(content=None, embed=embed)
            
        except Exception as e:
            await interaction.edit_original_response(content=f"❌ Çeviri Hatası: {str(e)[:200]}")

    @app_commands.command(name="hikaye", description="AI ile kısa hikaye oluştur")
    @app_commands.describe(konu="Hikayenin konusu")
    async def slash_hikaye(self, interaction: discord.Interaction, konu: str):
        if not groq_client:
            await guvenli_cevap(interaction, "❌ AI şu an aktif değil!", ephemeral=True)
            return
        
        await guvenli_cevap(interaction, f"📖 Hikaye yazılıyor: **{konu}**")
        
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "Sen yaratıcı bir hikaye yazarısın. Verilen konuda kısa, eğlenceli ve Türkçe bir hikaye yaz. Maximum 400 kelime."
                    },
                    {
                        "role": "user",
                        "content": f"Konu: {konu}"
                    }
                ],
                max_tokens=500,
                temperature=0.9
            )
            
            hikaye = response.choices[0].message.content[:1800]
            
            embed = discord.Embed(title=f"📖 {konu}", color=discord.Color.purple())
            embed.description = hikaye
            embed.set_footer(text="AI tarafından oluşturuldu ⚡")
            
            await interaction.edit_original_response(content=None, embed=embed)
            
        except Exception as e:
            await interaction.edit_original_response(content=f"❌ Hikaye Hatası: {str(e)[:200]}")

    @app_commands.command(name="özet", description="Metni özetle")
    @app_commands.describe(metin="Özetlenecek metin")
    async def slash_ozet(self, interaction: discord.Interaction, metin: str):
        if not groq_client:
            await guvenli_cevap(interaction, "❌ AI şu an aktif değil!", ephemeral=True)
            return
        
        await guvenli_cevap(interaction, "📝 Özetleniyor...")
        
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "Verilen metni kısa ve öz bir şekilde Türkçe özetle. Maximum 100 kelime kullan."
                    },
                    {
                        "role": "user",
                        "content": metin
                    }
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            ozet = response.choices[0].message.content[:800]
            
            embed = discord.Embed(title="📝 Özet", color=discord.Color.teal())
            embed.add_field(name="📄 Orijinal", value=metin[:300] + "..." if len(metin) > 300 else metin, inline=False)
            embed.add_field(name="✨ Özet", value=ozet, inline=False)
            
            await interaction.edit_original_response(content=None, embed=embed)
            
        except Exception as e:
            await interaction.edit_original_response(content=f"❌ Özet Hatası: {str(e)[:200]}")

    @app_commands.command(name="kod", description="AI ile kod yaz")
    @app_commands.describe(dil="Programlama dili", istek="Ne yapmak istiyorsun")
    async def slash_kod(self, interaction: discord.Interaction, dil: str, istek: str):
        if not groq_client:
            await guvenli_cevap(interaction, "❌ AI şu an aktif değil!", ephemeral=True)
            return
        
        await guvenli_cevap(interaction, f"💻 `{dil}` kodu yazılıyor...")
        
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": f"Sen bir {dil} programcısısın. Kullanıcının isteğine göre kod yaz. Sadece kodu yaz, açıklama ekleme. Kod bloğu kullan."
                    },
                    {
                        "role": "user",
                        "content": istek
                    }
                ],
                max_tokens=400,
                temperature=0.5
            )
            
            kod = response.choices[0].message.content[:1500]
            
            embed = discord.Embed(title=f"💻 {dil.capitalize()} Kodu", color=discord.Color.dark_grey())
            embed.add_field(name="📋 İstek", value=istek[:256], inline=False)
            embed.add_field(name="📝 Kod", value=kod[:1000], inline=False)
            embed.set_footer(text="AI tarafından oluşturuldu ⚡")
            
            await interaction.edit_original_response(content=None, embed=embed)
            
        except Exception as e:
            await interaction.edit_original_response(content=f"❌ Kod Hatası: {str(e)[:200]}")

    @app_commands.command(name="şiir", description="AI ile şiir yaz")
    @app_commands.describe(konu="Şiirin konusu")
    async def slash_siir(self, interaction: discord.Interaction, konu: str):
        if not groq_client:
            await guvenli_cevap(interaction, "❌ AI şu an aktif değil!", ephemeral=True)
            return
        
        await guvenli_cevap(interaction, f"✨ Şiir yazılıyor: **{konu}**")
        
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "Sen yetenekli bir şairsin. Verilen konuda güzel, duygusal ve Türkçe bir şiir yaz. 4-6 kıta olsun."
                    },
                    {
                        "role": "user",
                        "content": f"Konu: {konu}"
                    }
                ],
                max_tokens=400,
                temperature=0.9
            )
            
            siir = response.choices[0].message.content[:1500]
            
            embed = discord.Embed(title=f"✨ {konu}", color=discord.Color.magenta())
            embed.description = siir
            embed.set_footer(text="AI tarafından oluşturuldu ⚡")
            
            await interaction.edit_original_response(content=None, embed=embed)
            
        except Exception as e:
            await interaction.edit_original_response(content=f"❌ Şiir Hatası: {str(e)[:200]}")

    # =====================================================
    # 🤖 PREFIX KOMUTLARI
    # =====================================================

    @commands.command(aliases=['sor', 'chat', 'gpt', 'yapay'])
    async def ai(self, ctx, *, soru):
        if not groq_client:
            await ctx.send("❌ AI şu an aktif değil! `GROQ_API_KEY` ayarlanmamış.")
            return
        
        msg = await ctx.send("🤖 Düşünüyorum...")
        
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "Sen yardımcı bir Türkçe asistansın. Kısa, öz ve anlaşılır cevaplar ver. Maximum 500 karakter kullan."
                    },
                    {
                        "role": "user",
                        "content": soru
                    }
                ],
                max_tokens=250,
                temperature=0.7
            )
            
            cevap = response.choices[0].message.content[:1500]
            
            embed = discord.Embed(title="🤖 Yapay Zeka", color=discord.Color.blue())
            embed.add_field(name="❓ Soru", value=soru[:256], inline=False)
            embed.add_field(name="💬 Cevap", value=cevap, inline=False)
            embed.set_footer(text="Powered by Groq AI ⚡")
            
            await msg.edit(content=None, embed=embed)
            
        except Exception as e:
            await msg.edit(content=f"❌ AI Hatası: {str(e)[:200]}")

    @commands.command(aliases=['çevir', 'translate', 'cevir'])
    async def tercume(self, ctx, dil: str, *, metin):
        if not groq_client:
            await ctx.send("❌ AI şu an aktif değil!")
            return
        
        msg = await ctx.send(f"🌍 `{dil}` diline çevriliyor...")
        
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": f"Sen profesyonel bir çevirmensin. Verilen metni {dil} diline çevir. SADECE çeviriyi yaz."
                    },
                    {
                        "role": "user",
                        "content": metin
                    }
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            ceviri = response.choices[0].message.content[:1000]
            
            embed = discord.Embed(title="🌍 Çeviri", color=discord.Color.green())
            embed.add_field(name="📝 Orijinal", value=metin[:500], inline=False)
            embed.add_field(name=f"🔄 {dil.capitalize()}", value=ceviri[:500], inline=False)
            
            await msg.edit(content=None, embed=embed)
            
        except Exception as e:
            await msg.edit(content=f"❌ Çeviri Hatası: {str(e)[:200]}")

    @commands.command(aliases=['story'])
    async def hikaye(self, ctx, *, konu):
        if not groq_client:
            await ctx.send("❌ AI şu an aktif değil!")
            return
        
        msg = await ctx.send(f"📖 Hikaye yazılıyor: **{konu}**")
        
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "Sen yaratıcı bir hikaye yazarısın. Verilen konuda kısa, eğlenceli Türkçe hikaye yaz. Max 400 kelime."
                    },
                    {
                        "role": "user",
                        "content": f"Konu: {konu}"
                    }
                ],
                max_tokens=500,
                temperature=0.9
            )
            
            hikaye_text = response.choices[0].message.content[:1800]
            
            embed = discord.Embed(title=f"📖 {konu}", color=discord.Color.purple())
            embed.description = hikaye_text
            
            await msg.edit(content=None, embed=embed)
            
        except Exception as e:
            await msg.edit(content=f"❌ Hikaye Hatası: {str(e)[:200]}")

    @commands.command(aliases=['summarize'])
    async def ozet(self, ctx, *, metin):
        if not groq_client:
            await ctx.send("❌ AI şu an aktif değil!")
            return
        
        msg = await ctx.send("📝 Özetleniyor...")
        
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "Verilen metni kısa ve öz Türkçe özetle. Max 100 kelime."
                    },
                    {
                        "role": "user",
                        "content": metin
                    }
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            ozet_text = response.choices[0].message.content[:800]
            
            embed = discord.Embed(title="📝 Özet", color=discord.Color.teal())
            embed.description = ozet_text
            
            await msg.edit(content=None, embed=embed)
            
        except Exception as e:
            await msg.edit(content=f"❌ Özet Hatası: {str(e)[:200]}")

    @commands.command(aliases=['poem'])
    async def siir(self, ctx, *, konu):
        if not groq_client:
            await ctx.send("❌ AI şu an aktif değil!")
            return
        
        msg = await ctx.send(f"✨ Şiir yazılıyor: **{konu}**")
        
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "Sen yetenekli bir şairsin. Verilen konuda güzel, duygusal Türkçe şiir yaz."
                    },
                    {
                        "role": "user",
                        "content": f"Konu: {konu}"
                    }
                ],
                max_tokens=400,
                temperature=0.9
            )
            
            siir_text = response.choices[0].message.content[:1500]
            
            embed = discord.Embed(title=f"✨ {konu}", color=discord.Color.magenta())
            embed.description = siir_text
            
            await msg.edit(content=None, embed=embed)
            
        except Exception as e:
            await msg.edit(content=f"❌ Şiir Hatası: {str(e)[:200]}")

# =====================================================
# 🔧 COG YÜKLEME
# =====================================================

async def setup(bot):
    await bot.add_cog(YapayZeka(bot))