import discord

async def guvenli_cevap(interaction, mesaj=None, embed=None, ephemeral=False, view=None):
    try:
        if interaction.response.is_done():
            await interaction.followup.send(content=mesaj, embed=embed, ephemeral=ephemeral, view=view)
        else:
            await interaction.response.send_message(content=mesaj, embed=embed, ephemeral=ephemeral, view=view)
    except:
        pass

async def guvenli_defer(interaction, ephemeral=False):
    try:
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=ephemeral)
            return True
    except:
        pass
    return False

async def guvenli_edit(interaction, mesaj=None, embed=None, view=None):
    try:
        await interaction.edit_original_response(content=mesaj, embed=embed, view=view)
        return True
    except:
        pass
    return False
