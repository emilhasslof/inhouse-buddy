import discord
from discord import app_commands

class CreateMatch(discord.ui.View):
    def __init__(self, *, match, testing=False):
        self.match = match
        self.testing = testing
        super().__init__(timeout=None)

    @discord.ui.button(label="Lock teams & start", style=discord.ButtonStyle.success)
    async def lock_and_start(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not (len(self.match.radiant_channel.members) == 5 and len(self.match.dire_channel.members) == 5) and not testing: 
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=discord.Color.dark_red(),
                    title="Error",
                    description="Please make sure both teams have 5 players"
                ),
                delete_after=5
            )
            return 
        
        if self.testing:
            (self.match.radiant, self.match.dire) = await get_random_teams(interaction.guild)
        else:
            self.match.radiant = [member.name for member in self.match.radiant_channel.members]
            self.match.dire = [member.name for member in self.match.dire_channel.members]

        embed = discord.Embed( color=discord.Color.dark_red(), title="Currently playing")
        embed.add_field( name="Radiant", value="\n".join(self.match.radiant))
        embed.add_field( name="Dire", value="\n".join(self.match.dire))
        embed.set_footer(text="Who won?")
        await interaction.response.edit_message( view=LockedMatchView(self.match), embed=embed) 

    @discord.ui.button(label="Cancel Match", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.match.cancel(interaction)
        