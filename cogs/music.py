import asyncio, discord
from discord.ext import commands, tasks
from utils.youtube import get_audio_url
from utils.logger import logger

from discord import PCMVolumeTransformer, FFmpegPCMAudio

YOUTUBE_URL = "https://youtu.be/a3uSClD-fdM?si=cE1dAMp7qaYlMYIN"
FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.audio_url: str | None = None
        self.ensure_playing.start()

    def cog_unload(self):
        self.ensure_playing.cancel()

    async def ensure_voice(self) -> discord.VoiceClient:
        guild = self.bot.get_guild(self.bot.GUILD_ID)
        vc = discord.utils.get(self.bot.voice_clients, guild=guild)
        if vc is None or not vc.is_connected():
            channel = guild.get_channel(self.bot.VOICE_CHANNEL_ID)
            vc = await channel.connect()
        return vc

    @tasks.loop(seconds=30)
    async def ensure_playing(self):
        try:
            vc = await self.ensure_voice()
            if not vc.is_playing():
                # Extraction du flux hors de l'event-loop
                if self.audio_url is None:
                    loop = asyncio.get_running_loop()
                    self.audio_url = await loop.run_in_executor(
                        None, get_audio_url, YOUTUBE_URL
                    )
                    logger.info("Audio URL récupérée.")
                raw_source = FFmpegPCMAudio(self.audio_url, **FFMPEG_OPTIONS)
                source = PCMVolumeTransformer(raw_source, volume=0.5)
                vc.play(source, after=lambda e: logger.error(f"[Music] play error: {e}") if e else None)
                logger.info("Lecture lancée.")
        except Exception as e:
            logger.error(f"[Music Cog] Erreur dans ensure_playing: {e}")

    @ensure_playing.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Music(bot))
