
import discord


class ConfirmCancel(discord.ui.View):
    def __init__(self, match):
        self.match=match
        super().__init__(timeout=None)

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.match.cancel(interaction)
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            embed=interaction.message.embeds[0].set_footer(text="Who won?"),
            view=LockedMatchView(self.match)
        )