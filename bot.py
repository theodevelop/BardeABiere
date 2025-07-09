import os
import json
import platform
import discord
from discord.ext import commands
from dotenv import load_dotenv

from flask import Flask
from threading import Thread

from utils.logger import logger

# ─── Config & Logger ─────────────────────────────────────────────────────────
load_dotenv()

PREFIX             = os.getenv("PREFIX", "$")
DISCORD_TOKEN      = os.getenv("DISCORD_TOKEN")
GUILD_ID           = int(os.getenv("GUILD_ID", 0))
VOICE_CHANNEL_ID   = int(os.getenv("VOICE_CHANNEL_ID", 0))
APPLICATION_CH_ID  = int(os.getenv("APPLICATION_CHANNEL_ID", 0))
ROLE_ID            = int(os.getenv("ROLE_ID", 0))


# ─── Bot Class ────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class BardeABiere(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=commands.when_mentioned_or(PREFIX),
            intents=intents,
            help_command=None,
            activity=discord.Activity(
                type=discord.ActivityType.playing, 
                name="Sea of Thieves 🏴‍☠️"
                ),
            **kwargs
        )
        self.GUILD_ID = GUILD_ID
        self.VOICE_CHANNEL_ID = VOICE_CHANNEL_ID
        self.APPLICATION_CH_ID = APPLICATION_CH_ID
        self.ROLE_ID = ROLE_ID
        self.REVIEWERS = [
            int(os.getenv("USER1_ID")),
            int(os.getenv("USER2_ID"))
        ]
        self.logger = logger

    async def setup_hook(self):
        self.logger.info(f"Bot démarrage sur Python {platform.python_version()} / discord.py {discord.__version__}")
        await self.load_all_cogs()

    async def load_all_cogs(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and not filename.startswith("_"):
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                    self.logger.info(f"Cog chargé : {filename}")
                except Exception as e:
                    self.logger.error(f"Echec chargement {filename} : {e}")

    async def on_ready(self):
        self.logger.info(f"Connecté en tant que {self.user} (id={self.user.id})")
        await self.tree.sync()

# ─── Bot start ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    bot = BardeABiere()

    # ─── Hébergement Replit : démarrage du webserver Flask ──────────────────
    app = Flask(__name__)

    @app.route("/")
    def home():
        return "Barde a Biere is alive!"

    def run_web():
        # Replit exposera le port 3000 par défaut
        app.run(host="0.0.0.0", port=3000)

    # On lance Flask dans un thread parallèle
    Thread(target=run_web).start()

    # ─── Lancement du bot Discord ──────────────────────────────────────────

    bot.run(DISCORD_TOKEN)
