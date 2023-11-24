import discord
import Confirm, Cancel


class LockedMatch(discord.ui.View):
    def __init__(self, match):
        self.match = match
        super().__init__(timeout=None) 
    
    @discord.ui.button(label="Radiant", style=discord.ButtonStyle.success)
    async def winner_radiant(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.match.can_edit(interaction):
            self.match.winners=self.match.radiant
            self.match.losers=self.match.dire
            embed = interaction.message.embeds[0]
            embed.set_footer(text="This will update stats, please confirm")
            await interaction.response.edit_message(
                embed=embed,
                view=Confirm(self.match)
            )
        else:
            await interaction.response.send_message(f"{interaction.user.name} is not allowed to do this", delete_after=5)

    @discord.ui.button(label="Dire", style=discord.ButtonStyle.success)
    async def winner_dire(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.match.can_edit(interaction):
            self.match.winners=self.match.dire
            self.match.losers=self.match.radiant
            embed = interaction.message.embeds[0]
            embed.set_footer(text="This will update stats, please confirm")
            await interaction.response.edit_message(
                embed=embed,
                view=Confirm(self.match)
            )
        else:
            await interaction.response.send_message(f"{interaction.user.name} is not allowed to do this", delete_after=5)

    @discord.ui.button(label="Cancel Match", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.match.can_edit(interaction):
            await interaction.response.edit_message(
                embed=interaction.message.embeds[0].set_footer(text="This will cancel the match, please confirm"),
                view=ConfirmCancel(self.match)
            )
        else:
            await interaction.response.send_message(f"{interaction.user.name} is not allowed to do this", delete_after=5)