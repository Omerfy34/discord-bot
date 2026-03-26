# =====================================================
# 🛠️ WOWSY BOT - YARDIMCI FONKSİYON
# =====================================================

import discord

# =====================================================
# 🛡️ GÜVENLİ CEVAP FONKSİYONU
# =====================================================

async def guvenli_cevap(interaction: discord.Interaction, icerik=None, embed=None, ephemeral=False):
    """Interaction'a güvenli şekilde cevap ver"""
    try:
        if not interaction.response.is_done():
            if embed:
                await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
            elif icerik:
                await interaction.response.send_message(icerik, ephemeral=ephemeral)
        else:
            if embed:
                await interaction.followup.send(embed=embed, ephemeral=ephemeral)
            elif icerik:
                await interaction.followup.send(icerik, ephemeral=ephemeral)
        return True
    except Exception as e:
        print(f"Cevap hatası: {e}")
        return False