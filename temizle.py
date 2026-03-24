import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot: {bot.user.name}")
    print("="*40)
    print("🗑️ Eski slash komutlar temizleniyor...")
    
    # Global temizle
    bot.tree.clear_commands(guild=None)
    await bot.tree.sync()
    print("✅ Global komutlar temizlendi!")
    
    # Her sunucu için temizle
    for guild in bot.guilds:
        bot.tree.clear_commands(guild=guild)
        await bot.tree.sync(guild=guild)
        print(f"✅ {guild.name} temizlendi!")
    
    print("="*40)
    print("✅ TAMAM!")
    print("Şimdi bu pencereyi kapat ve bot.py çalıştır!")
    print("="*40)
    
    await bot.close()

bot.run(TOKEN)