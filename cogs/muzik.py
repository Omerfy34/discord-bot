# =====================================================
# 🎵 WOWSY BOT - MÜZİK KOMUTLARI (LAVALINK + WAVELINK)
# =====================================================

import discord
from discord.ext import commands
from discord import app_commands
import wavelink
from typing import cast
import random

from utils import guvenli_cevap

# =====================================================
# 🎵 YARDIMCI FONKSİYONLAR
# =====================================================

def format_duration(milliseconds: int) -> str:
    """Milisaniyeyi dakika:saniye formatına çevir"""
    if not milliseconds or milliseconds == 0:
        return "🔴 CANLI"
    
    seconds = milliseconds // 1000
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"

def create_embed(title: str, description: str, color=discord.Color.blue()) -> discord.Embed:
    """Standart embed oluştur"""
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text="⚡ WOWSY Bot")
    return embed

# =====================================================
# 🎵 MÜZİK COG
# =====================================================

class Muzik(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self) -> None:
    """Cog yüklendiğinde Lavalink node'ları bağla"""
    nodes = [
        wavelink.Node(
            uri="http://lavalink.clxud.pro:2333",
            password="youshallnotpass",
            identifier="Clxud-1"
        ),
        wavelink.Node(
            uri="http://lavalink.jirayu.net:13592",
            password="youshallnotpass",
            identifier="Jirayu-1"
        ),
        wavelink.Node(
            uri="http://node1.kartadharta.xyz:443",
            password="kdlavalink",
            identifier="Karta-1"
        )
    ]
        
        try:
            await wavelink.Pool.connect(nodes=nodes, client=self.bot)
            print("✅ Lavalink node'ları bağlandı!")
        except Exception as e:
            print(f"⚠️ Lavalink bağlantı hatası: {e}")

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload) -> None:
        """Lavalink node hazır olduğunda"""
        print(f"✅ Lavalink node hazır: {payload.node.identifier}")

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
        """Şarkı başladığında bildirim gönder"""
        player: wavelink.Player | None = payload.player
        if not player:
            return

        track: wavelink.Playable = payload.track

        embed = discord.Embed(
            title="🎵 Şimdi Çalıyor",
            description=f"**[{track.title}]({track.uri})**",
            color=discord.Color.green()
        )
        
        embed.add_field(name="⏱️ Süre", value=format_duration(track.length), inline=True)
        embed.add_field(name="👤 Yazar", value=track.author, inline=True)
        
        if hasattr(track, 'requester') and track.requester:
            embed.add_field(name="🎧 İsteyen", value=track.requester.mention, inline=True)
        
        if track.artwork:
            embed.set_thumbnail(url=track.artwork)

        if player.channel:
            channel = self.bot.get_channel(player.channel.id)
            if channel and isinstance(channel, discord.TextChannel):
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload) -> None:
        """Şarkı bittiğinde"""
        player: wavelink.Player | None = payload.player
        if not player:
            return
        
        if player.queue.is_empty and not player.autoplay:
            await player.disconnect()

    # =====================================================
    # 🎵 SLASH KOMUTLARI
    # =====================================================

    @app_commands.command(name="play", description="Müzik çal")
    @app_commands.describe(şarkı="Şarkı adı veya YouTube/Spotify linki")
    async def slash_play(self, interaction: discord.Interaction, şarkı: str):
        """Şarkı çal (slash komut)"""
        if not interaction.user.voice:
            await interaction.response.send_message("❌ Önce bir ses kanalına katıl!", ephemeral=True)
            return
        
        await interaction.response.defer()

        channel = interaction.user.voice.channel
        
        player: wavelink.Player = cast(
            wavelink.Player,
            interaction.guild.voice_client or await channel.connect(cls=wavelink.Player)
        )

        if player.channel != channel:
            await player.move_to(channel)

        tracks: wavelink.Search = await wavelink.Playable.search(şarkı)
        
        if not tracks:
            await interaction.followup.send("❌ Sonuç bulunamadı!")
            return

        if isinstance(tracks, wavelink.Playlist):
            added: int = await player.queue.put_wait(tracks)
            
            embed = create_embed(
                "📋 Playlist Eklendi",
                f"**{tracks.name}**\n{added} şarkı kuyruğa eklendi!",
                discord.Color.blue()
            )
            await interaction.followup.send(embed=embed)
        else:
            track: wavelink.Playable = tracks[0]
            track.extras = {"requester": interaction.user}
            
            await player.queue.put_wait(track)
            
            if not player.playing:
                embed = create_embed(
                    "🎵 Şimdi Çalıyor",
                    f"**[{track.title}]({track.uri})**",
                    discord.Color.green()
                )
                embed.add_field(name="⏱️ Süre", value=format_duration(track.length), inline=True)
                if track.artwork:
                    embed.set_thumbnail(url=track.artwork)
            else:
                embed = create_embed(
                    "➕ Kuyruğa Eklendi",
                    f"**[{track.title}]({track.uri})**",
                    discord.Color.blue()
                )
                embed.add_field(name="📋 Sıra", value=f"#{len(player.queue)}", inline=True)
                embed.add_field(name="⏱️ Süre", value=format_duration(track.length), inline=True)
                if track.artwork:
                    embed.set_thumbnail(url=track.artwork)
            
            await interaction.followup.send(embed=embed)

        if not player.playing:
            await player.play(player.queue.get(), volume=80)

    @app_commands.command(name="pause", description="Müziği duraklat")
    async def slash_pause(self, interaction: discord.Interaction):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        
        if not player or not player.connected:
            await interaction.response.send_message("❌ Bot ses kanalında değil!", ephemeral=True)
            return
        
        if player.paused:
            await interaction.response.send_message("❌ Müzik zaten duraklatılmış!", ephemeral=True)
            return
        
        await player.pause(True)
        await interaction.response.send_message("⏸️ Müzik duraklatıldı!")

    @app_commands.command(name="devam", description="Müziği devam ettir")
    async def slash_devam(self, interaction: discord.Interaction):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        
        if not player or not player.connected:
            await interaction.response.send_message("❌ Bot ses kanalında değil!", ephemeral=True)
            return
        
        if not player.paused:
            await interaction.response.send_message("❌ Müzik zaten çalıyor!", ephemeral=True)
            return
        
        await player.pause(False)
        await interaction.response.send_message("▶️ Müzik devam ediyor!")

    @app_commands.command(name="skip", description="Şarkıyı atla")
    async def slash_skip(self, interaction: discord.Interaction):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        
        if not player or not player.connected:
            await interaction.response.send_message("❌ Bot ses kanalında değil!", ephemeral=True)
            return
        
        if not player.playing:
            await interaction.response.send_message("❌ Çalan şarkı yok!", ephemeral=True)
            return
        
        await player.skip(force=True)
        await interaction.response.send_message("⏭️ Şarkı atlandı!")

    @app_commands.command(name="stop", description="Müziği durdur ve kuyruğu temizle")
    async def slash_stop(self, interaction: discord.Interaction):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        
        if not player or not player.connected:
            await interaction.response.send_message("❌ Bot ses kanalında değil!", ephemeral=True)
            return
        
        player.queue.clear()
        await player.stop()
        await interaction.response.send_message("⏹️ Müzik durduruldu ve kuyruk temizlendi!")

    @app_commands.command(name="leave", description="Ses kanalından ayrıl")
    async def slash_leave(self, interaction: discord.Interaction):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        
        if not player:
            await interaction.response.send_message("❌ Zaten ses kanalında değilim!", ephemeral=True)
            return
        
        await player.disconnect()
        await interaction.response.send_message("👋 Ses kanalından ayrıldım!")

    @app_commands.command(name="queue", description="Müzik kuyruğunu göster")
    async def slash_queue(self, interaction: discord.Interaction):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        
        if not player or not player.connected:
            await interaction.response.send_message("❌ Bot ses kanalında değil!", ephemeral=True)
            return
        
        if not player.current and player.queue.is_empty:
            await interaction.response.send_message("📭 Kuyruk boş!", ephemeral=True)
            return
        
        embed = discord.Embed(title="📋 Müzik Kuyruğu", color=discord.Color.blue())
        
        if player.current:
            current = player.current
            embed.add_field(
                name="🎵 Şu An Çalıyor",
                value=f"**[{current.title}]({current.uri})**\n⏱️ {format_duration(current.length)}",
                inline=False
            )
        
        if not player.queue.is_empty:
            queue_list = []
            for i, track in enumerate(list(player.queue)[:10], 1):
                title = track.title[:40] + "..." if len(track.title) > 40 else track.title
                queue_list.append(f"**{i}.** [{title}]({track.uri}) - `{format_duration(track.length)}`")
            
            if len(player.queue) > 10:
                queue_list.append(f"\n*... ve {len(player.queue) - 10} şarkı daha*")
            
            embed.add_field(
                name="📜 Sıradaki Şarkılar",
                value="\n".join(queue_list),
                inline=False
            )
        
        embed.set_footer(text=f"Toplam: {len(player.queue)} şarkı kuyrukta")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="np", description="Şu an çalan şarkıyı göster")
    async def slash_np(self, interaction: discord.Interaction):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        
        if not player or not player.connected:
            await interaction.response.send_message("❌ Bot ses kanalında değil!", ephemeral=True)
            return
        
        if not player.current:
            await interaction.response.send_message("❌ Şu an çalan şarkı yok!", ephemeral=True)
            return
        
        track = player.current
        
        embed = discord.Embed(
            title="🎵 Şu An Çalıyor",
            description=f"**[{track.title}]({track.uri})**",
            color=discord.Color.green()
        )
        
        progress = int((player.position / track.length) * 20) if track.length else 0
        progress_bar = "█" * progress + "░" * (20 - progress)
        
        embed.add_field(
            name="⏱️ İlerleme",
            value=f"`{format_duration(player.position)} {progress_bar} {format_duration(track.length)}`",
            inline=False
        )
        
        embed.add_field(name="👤 Yazar", value=track.author, inline=True)
        embed.add_field(name="🔊 Ses", value=f"{player.volume}%", inline=True)
        embed.add_field(name="📋 Kuyruk", value=f"{len(player.queue)} şarkı", inline=True)
        
        if track.artwork:
            embed.set_thumbnail(url=track.artwork)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="volume", description="Ses seviyesini ayarla")
    @app_commands.describe(seviye="Ses seviyesi (0-200)")
    async def slash_volume(self, interaction: discord.Interaction, seviye: int):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        
        if not player or not player.connected:
            await interaction.response.send_message("❌ Bot ses kanalında değil!", ephemeral=True)
            return
        
        if seviye < 0 or seviye > 200:
            await interaction.response.send_message("❌ Ses seviyesi 0-200 arasında olmalı!", ephemeral=True)
            return
        
        await player.set_volume(seviye)
        await interaction.response.send_message(f"🔊 Ses seviyesi: **{seviye}%**")

    @app_commands.command(name="shuffle", description="Kuyruğu karıştır")
    async def slash_shuffle(self, interaction: discord.Interaction):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        
        if not player or not player.connected:
            await interaction.response.send_message("❌ Bot ses kanalında değil!", ephemeral=True)
            return
        
        if player.queue.is_empty or len(player.queue) < 2:
            await interaction.response.send_message("❌ Karıştırılacak yeterli şarkı yok!", ephemeral=True)
            return
        
        player.queue.shuffle()
        await interaction.response.send_message(f"🔀 Kuyruk karıştırıldı! ({len(player.queue)} şarkı)")

    @app_commands.command(name="qclear", description="Müzik kuyruğunu temizle")
    async def slash_qclear(self, interaction: discord.Interaction):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        
        if not player or not player.connected:
            await interaction.response.send_message("❌ Bot ses kanalında değil!", ephemeral=True)
            return
        
        count = len(player.queue)
        player.queue.clear()
        await interaction.response.send_message(f"🗑️ Kuyruk temizlendi! ({count} şarkı silindi)")
    # =====================================================
    # 🎵 PREFIX KOMUTLARI (Mevcut Komutların Korunması)
    # =====================================================

    @commands.command(aliases=['p', 'çal', 'oynat'])
    async def play(self, ctx: commands.Context, *, query: str):
        """Müzik çal (prefix komut)"""
        if not ctx.author.voice:
            await ctx.send("❌ Önce bir ses kanalına katıl!")
            return
        
        msg = await ctx.send(f"🔍 Aranıyor: **{query}**")
        
        channel = ctx.author.voice.channel
        player: wavelink.Player = cast(
            wavelink.Player,
            ctx.guild.voice_client or await channel.connect(cls=wavelink.Player)
        )

        if player.channel != channel:
            await player.move_to(channel)

        tracks: wavelink.Search = await wavelink.Playable.search(query)
        
        if not tracks:
            await msg.edit(content="❌ Sonuç bulunamadı!")
            return

        if isinstance(tracks, wavelink.Playlist):
            added: int = await player.queue.put_wait(tracks)
            embed = create_embed(
                "📋 Playlist Eklendi",
                f"**{tracks.name}**\n{added} şarkı kuyruğa eklendi!",
                discord.Color.blue()
            )
            await msg.edit(content=None, embed=embed)
        else:
            track: wavelink.Playable = tracks[0]
            track.extras = {"requester": ctx.author}
            await player.queue.put_wait(track)
            
            if not player.playing:
                embed = create_embed(
                    "🎵 Şimdi Çalıyor",
                    f"**[{track.title}]({track.uri})**",
                    discord.Color.green()
                )
                embed.add_field(name="⏱️ Süre", value=format_duration(track.length))
                if track.artwork:
                    embed.set_thumbnail(url=track.artwork)
            else:
                embed = create_embed(
                    "➕ Kuyruğa Eklendi",
                    f"**[{track.title}]({track.uri})**",
                    discord.Color.blue()
                )
                embed.add_field(name="📋 Sıra", value=f"#{len(player.queue)}")
            
            await msg.edit(content=None, embed=embed)

        if not player.playing:
            await player.play(player.queue.get(), volume=80)

    @commands.command(aliases=['duraklat', 'dur'])
    async def pause(self, ctx: commands.Context):
        """Müziği duraklat"""
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        
        if not player or not player.connected:
            await ctx.send("❌ Bot ses kanalında değil!")
            return
        
        if player.paused:
            await ctx.send("❌ Müzik zaten duraklatılmış!")
            return
        
        await player.pause(True)
        await ctx.send("⏸️ Müzik duraklatıldı!")

    @commands.command(aliases=['resume', 'devam'])
    async def devam_et(self, ctx: commands.Context):
        """Müziği devam ettir"""
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        
        if not player or not player.connected:
            await ctx.send("❌ Bot ses kanalında değil!")
            return
        
        if not player.paused:
            await ctx.send("❌ Müzik zaten çalıyor!")
            return
        
        await player.pause(False)
        await ctx.send("▶️ Müzik devam ediyor!")

    @commands.command(aliases=['atla', 's', 'next'])
    async def skip(self, ctx: commands.Context):
        """Şarkıyı atla"""
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        
        if not player or not player.connected:
            await ctx.send("❌ Bot ses kanalında değil!")
            return
        
        if not player.playing:
            await ctx.send("❌ Çalan şarkı yok!")
            return
        
        await player.skip(force=True)
        await ctx.send("⏭️ Şarkı atlandı!")

    @commands.command(aliases=['kapat', 'durdur'])
    async def stop(self, ctx: commands.Context):
        """Müziği durdur ve kuyruğu temizle"""
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        
        if not player or not player.connected:
            await ctx.send("❌ Bot ses kanalında değil!")
            return
        
        player.queue.clear()
        await player.stop()
        await ctx.send("⏹️ Müzik durduruldu ve kuyruk temizlendi!")

    @commands.command(aliases=['çık', 'dc', 'disconnect', 'ayrıl'])
    async def leave(self, ctx: commands.Context):
        """Ses kanalından ayrıl"""
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        
        if not player:
            await ctx.send("❌ Zaten ses kanalında değilim!")
            return
        
        await player.disconnect()
        await ctx.send("👋 Ses kanalından ayrıldım!")

    @commands.command(aliases=['q', 'kuyruk', 'sıra', 'liste'])
    async def queue(self, ctx: commands.Context):
        """Müzik kuyruğunu göster"""
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        
        if not player or not player.connected:
            await ctx.send("❌ Bot ses kanalında değil!")
            return
        
        if not player.current and player.queue.is_empty:
            await ctx.send("📭 Kuyruk boş!")
            return
        
        embed = discord.Embed(title="📋 Müzik Kuyruğu", color=discord.Color.blue())
        
        if player.current:
            current = player.current
            embed.add_field(
                name="🎵 Şu An Çalıyor",
                value=f"**[{current.title}]({current.uri})**\n⏱️ {format_duration(current.length)}",
                inline=False
            )
        
        if not player.queue.is_empty:
            queue_list = []
            for i, track in enumerate(list(player.queue)[:10], 1):
                title = track.title[:40] + "..." if len(track.title) > 40 else track.title
                queue_list.append(f"**{i}.** [{title}]({track.uri}) - `{format_duration(track.length)}`")
            
            if len(player.queue) > 10:
                queue_list.append(f"\n*... ve {len(player.queue) - 10} şarkı daha*")
            
            embed.add_field(
                name="📜 Sıradaki Şarkılar",
                value="\n".join(queue_list),
                inline=False
            )
        
        embed.set_footer(text=f"Toplam: {len(player.queue)} şarkı kuyrukta")
        await ctx.send(embed=embed)

    @commands.command(aliases=['katıl', 'gel', 'connect'])
    async def join(self, ctx: commands.Context):
        """Ses kanalına katıl"""
        if not ctx.author.voice:
            await ctx.send("❌ Önce bir ses kanalına katıl!")
            return
        
        channel = ctx.author.voice.channel
        player: wavelink.Player = cast(
            wavelink.Player,
            ctx.guild.voice_client or await channel.connect(cls=wavelink.Player)
        )
        
        if player.channel == channel:
            await ctx.send(f"✅ Zaten **{channel.name}** kanalındayım!")
        else:
            await player.move_to(channel)
            await ctx.send(f"🔊 **{channel.name}** kanalına taşındım!")

    @commands.command(aliases=['nowplaying', 'şuan'])
    async def np(self, ctx: commands.Context):
        """Şu an çalan şarkıyı göster"""
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        
        if not player or not player.connected:
            await ctx.send("❌ Bot ses kanalında değil!")
            return
        
        if not player.current:
            await ctx.send("❌ Şu an çalan şarkı yok!")
            return
        
        track = player.current
        
        embed = discord.Embed(
            title="🎵 Şu An Çalıyor",
            description=f"**[{track.title}]({track.uri})**",
            color=discord.Color.green()
        )
        
        progress = int((player.position / track.length) * 20) if track.length else 0
        progress_bar = "█" * progress + "░" * (20 - progress)
        
        embed.add_field(
            name="⏱️ İlerleme",
            value=f"`{format_duration(player.position)} {progress_bar} {format_duration(track.length)}`",
            inline=False
        )
        
        embed.add_field(name="👤 Yazar", value=track.author, inline=True)
        embed.add_field(name="🔊 Ses", value=f"{player.volume}%", inline=True)
        
        if track.artwork:
            embed.set_thumbnail(url=track.artwork)
        
        await ctx.send(embed=embed)

    @commands.command(aliases=['ses', 'vol'])
    async def volume(self, ctx: commands.Context, volume: int):
        """Ses seviyesini ayarla"""
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        
        if not player or not player.connected:
            await ctx.send("❌ Bot ses kanalında değil!")
            return
        
        if volume < 0 or volume > 200:
            await ctx.send("❌ Ses seviyesi 0-200 arasında olmalı!")
            return
        
        await player.set_volume(volume)
        await ctx.send(f"🔊 Ses seviyesi: **{volume}%**")

    @commands.command(aliases=['karıştır', 'karistir'])
    async def shuffle(self, ctx: commands.Context):
        """Kuyruğu karıştır"""
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        
        if not player or not player.connected:
            await ctx.send("❌ Bot ses kanalında değil!")
            return
        
        if player.queue.is_empty or len(player.queue) < 2:
            await ctx.send("❌ Karıştırılacak yeterli şarkı yok!")
            return
        
        player.queue.shuffle()
        await ctx.send(f"🔀 Kuyruk karıştırıldı! ({len(player.queue)} şarkı)")

    @commands.command(aliases=['qclear', 'kuyruktemizle', 'sıfırla'])
    async def clearqueue(self, ctx: commands.Context):
        """Müzik kuyruğunu temizle"""
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        
        if not player or not player.connected:
            await ctx.send("❌ Bot ses kanalında değil!")
            return
        
        count = len(player.queue)
        player.queue.clear()
        await ctx.send(f"🗑️ Kuyruk temizlendi! ({count} şarkı silindi)")

# =====================================================
# 🔧 COG YÜKLEME
# =====================================================

async def setup(bot: commands.Bot):
    await bot.add_cog(Muzik(bot))
