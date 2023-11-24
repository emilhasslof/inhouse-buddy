import discord
import LockedMatch

class Confirm(discord.ui.View):
    def __init__(self, match):
        self.match=match
        super().__init__(timeout=None)

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        submit_match_result(guild_id=interaction.guild_id, winners=self.match.winners, losers=self.match.losers)
        await interaction.response.edit_message(
            embed=discord.Embed(
                color=discord.Color.dark_red(),
                title="Congratulations!",
                description=", ".join([p for p in self.match.winners])
            ),
            delete_after=10,
            view=None
        )
        await self.match.radiant_channel.delete()
        await self.match.dire_channel.delete()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
       await interaction.response.edit_message(
           embed=interaction.message.embeds[0].set_footer(text="Who won?"),
           view=LockedMatch(self.match)
       ) 