import discord
from discord import app_commands
import random
from Views.LockedMatch import LockedMatch

class CreateMatch(discord.ui.View):
    def __init__(self, *, match, testing=False, scheduled_players=None, scheduled_queue=None):
        self.match = match
        self.testing = testing
        scheduled_players = scheduled_players
        scheduled_queue = scheduled_queue
        super().__init__(timeout=None)

    @discord.ui.button(label="Lock teams & start", style=discord.ButtonStyle.success)
    async def lock_and_start(self, interaction: discord.Interaction, button: discord.ui.Button):
        #print(interaction.type) => IntractionType.component
        message_id = interaction.message.id
        await interaction.response.defer()

        if not self.testing and not \
            (len(self.match.radiant_channel.members) == 5 and len(self.match.dire_channel.members) == 5): 
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=discord.Color.dark_red(),
                    title="Error",
                    description="Please make sure both teams have 5 players",
                ),
                delete_after=5,
                ephemeral=True
            )
            return

        # Assign role "Inhouse enjoyer" to all players
        guild = interaction.guild
        role = discord.utils.get(guild.roles, name="Inhouse enjoyer")
        if not role:
            role = await guild.create_role(name="Inhouse enjoyer")
            print("Created role Inhouse enjoyer")

        for member in self.match.radiant_channel.members:
            await member.add_roles(role)
        for member in self.match.dire_channel.members:
            await member.add_roles(role)
       
        self.match.radiant = [member.name for member in self.match.radiant_channel.members]
        self.match.dire = [member.name for member in self.match.dire_channel.members]
        embed = discord.Embed( color=discord.Color.dark_red(), title="Currently playing")
        embed.add_field( name="Radiant", value="\n".join(self.match.radiant))
        embed.add_field( name="Dire", value="\n".join(self.match.dire))
        embed.set_footer(text="Who won?")
        try:
            await interaction.followup.edit_message(message_id = interaction.message.id, embed=embed, view=LockedMatch(self.match))
            print("Edit succesful, hooray!")
            return
        except discord.errors.NotFound:
            await interaction.channel.send(embed=embed, view=LockedMatch(self.match))
        
        # Try deleting the lock teams message
        try:
            await interaction.message.delete()
            await interaction.response.edit_message(content="Match started!", view=None)
        except discord.errors.NotFound:
            await interaction.channel.send(
                embed=discord.Embed(
                    title="NotFound exception",
                    description="bot is little bit fuk but it's being investigated",
                    color=discord.Color.dark_red()
                ),
                ephemeral=True,
                delete_after=10
            )



    @discord.ui.button(label="Cancel Match", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.match.cancel(interaction)
        
# For testing purposes
async def get_random_teams(guild):
    members = []
    async for member in guild.fetch_members(limit=10):
        members.append(member)
    random.shuffle(members)
    radiant = [member.name for member in members]
    dire = [member.name for member in members] 
    return (radiant, dire)
