import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, Button, View
from urllib.parse import quote
from utils.logger import logger

# Noms des reviewers et leurs liens de profil Xbox
NAME1 = "My nathoune"
NAME2 = "raver8960"
PROFILE_LINKS = {
    NAME1: "https://www.xbox.com/fr-FR/play/user/My%20nathoune",
    NAME2: "https://www.xbox.com/fr-FR/play/user/raver8960"
}

class CandidatureModal(Modal):
    def __init__(self):
        super().__init__(title="Candidature - Ordre du Grog")
        self.pseudo = TextInput(
            label="Ton pseudo Xbox",
            placeholder="Ex : MonPseudoXBOX",
            max_length=32
        )
        self.add_item(self.pseudo)

        self.choice = TextInput(
            label="Reviewer (1 = My nathoune, 2 = raver8960)",
            placeholder="Tape 1 ou 2 selon qui tu as ajouté",
            max_length=1
        )
        self.add_item(self.choice)

    async def on_submit(self, interaction: discord.Interaction):
        pseudo = self.pseudo.value.strip()
        choix  = self.choice.value.strip()

        if choix not in ("1", "2"):
            return await interaction.response.send_message(
                "❌ Choix invalide : tapez **1** ou **2**.", ephemeral=True
            )

        idx = int(choix) - 1
        reviewer_id = interaction.client.REVIEWERS[idx]
        reviewer    = await interaction.client.fetch_user(reviewer_id)
        candidate   = interaction.user

        # Construire le lien vers le profil Xbox du candidat
        candidate_profile_link = (
            f"https://www.xbox.com/fr-FR/play/user/{quote(pseudo)}"
        )

        # Embed à envoyer au reviewer
        embed = discord.Embed(
            title="🆕 Nouvelle Candidature Ordre du Grog",
            color=discord.Color.blue()
        )
        embed.add_field(name="Pseudo Xbox", value=pseudo, inline=False)
        embed.add_field(
            name="Profil Xbox",
            value=f"[Voir Profil]({candidate_profile_link})",
            inline=False
        )
        embed.add_field(
            name="Reviewer choisi",
            value=(NAME1 if idx == 0 else NAME2),
            inline=False
        )
        embed.add_field(
            name="Candidat Discord",
            value=interaction.user.mention,
            inline=False
        )

        # View avec le bouton "Fait"
        class FaitView(View):
            def __init__(self):
                super().__init__(timeout=None)
                # Ne plus faire self.add_item(...) ici !

            @discord.ui.button(label="Fait", style=discord.ButtonStyle.green)
            async def done(self, interaction: discord.Interaction, button: Button):
                # -> ici interaction est l’Interaction, button est le Button cliqué

                # Attribution du rôle
                guild  = interaction.client.get_guild(interaction.client.GUILD_ID)
                member = guild.get_member(candidate.id)  # candidate capturé dans la closure
                role   = guild.get_role(interaction.client.ROLE_ID)
                if member and role:
                    await member.add_roles(role)

                # Notifier le candidat
                await candidate.send("🍻 Par la mousse sacrée, tu es désormais membre de l’Ordre du Grog !")

                # Mettre à jour le message du reviewer
                await interaction.response.edit_message(
                    content="✅ Candidature traitée et candidat notifié.",
                    embed=None,
                    view=None
                )


        view = FaitView()

        # Envoi de la DM au reviewer
        try:
            await reviewer.send(embed=embed, view=view)
        except Exception as e:
            logger.error(f"Impossible d’envoyer la DM à {reviewer_id} : {e}")

        # Confirmation éphémère au candidat
        await interaction.response.send_message(
            "✅ Ta candidature a bien été envoyée à l’Ordre du Grog !",
            ephemeral=True
        )

class Candidature(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="setup_candidature")
    @commands.has_guild_permissions(administrator=True)
    async def setup_candidature(self, ctx: commands.Context):
        """Installe le bouton de candidature dans le channel dédié."""
        if ctx.channel.id != self.bot.APPLICATION_CH_ID:
            return

        embed = discord.Embed(
            title="📜 Rejoindre l’Ordre du Grog",
            description=(
                "1️⃣ Ajoute en ami **My nathoune** ou **raver8960** via les liens ci-dessous :\n"
                f"- {NAME1} : [Profil Xbox]({PROFILE_LINKS[NAME1]})\n"
                f"- {NAME2} : [Profil Xbox]({PROFILE_LINKS[NAME2]})\n\n"
                "2️⃣ Clique sur le bouton ci-dessous, indique ton **pseudo Xbox** et choisis **1** ou **2** selon qui tu as ajouté."
                "Que la bière coule à flots ! 🍻"
            ),
            color=discord.Color.dark_gold()
        )

        btn = Button(label="Faire une candidature", style=discord.ButtonStyle.blurple)
        async def open_modal(inter: discord.Interaction):
            await inter.response.send_modal(CandidatureModal())
        btn.callback = open_modal

        view = View()
        view.add_item(btn)
        await ctx.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(Candidature(bot))
