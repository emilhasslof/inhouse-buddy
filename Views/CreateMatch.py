import discord
from discord import app_commands
from datetime import datetime
import random
from Views.LockedMatch import LockedMatch

class CreateMatch(discord.ui.View):
    def __init__(self, *, match, client: discord.Client, interaction: discord.Interaction, testing=False, scheduled_players=None, scheduled_queue=None, parent_embed=None):
        self.match = match
        self.testing = testing
        self.parent_embed=parent_embed
        scheduled_players = scheduled_players
        scheduled_queue = scheduled_queue
        super().__init__(timeout=None)

        print(f"{client} from CreateMatch")
        @client.event
        async def on_voice_state_update(member, before, after):
            if after.channel is self.match.radiant_channel or after.channel is self.match.dire_channel:
                print(testing)
                if len(self.match.radiant_channel.members) == 5 and len(self.match.dire_channel.members) == 5 or testing:
                    radiant = [member.name for member in self.match.radiant_channel.members]
                    dire = [member.name for member in self.match.dire_channel.members]
                    await interaction.channel.send(
                        embed=discord.Embed(
                            color=discord.Color.dark_red(),
                            title="10 players detected, are these teams correct?",
                            description="Radiant: " + '\n'.join([member.name for member in self.match.radiant_channel.members]) + \
                                "\nDire:" + '\n'.join([member.name for member in self.match.dire_channel.members])
                        ),
                        view=ConfirmLock(match=self.match, client=client, interaction=interaction, parent=self)
                    )
                    

    @discord.ui.button(label="Lock teams & start", style=discord.ButtonStyle.success)
    async def lock_and_start(self, interaction: discord.Interaction, button: discord.ui.Button):
        #print(interaction.type) => IntractionType.component
        message_id = interaction.message.id
        if not interaction.response.is_done():
            await interaction.response.defer()
        button.disabled = True
        await interaction.followup.edit_message(interaction.message.id, view=self, embed=self.parent_embed)

        if not self.testing and not \
            (len(self.match.radiant_channel.members) == 5 and len(self.match.dire_channel.members) == 5): 
            await interaction.channel.send(
                embed=discord.Embed(
                    color=discord.Color.dark_red(),
                    title="Error",
                    description="Please make sure both teams have 5 players",
                ),
                delete_after=5
            )
            button.disabled = False
            await interaction.followup.edit_message(interaction.message.id, view=self, embed=self.parent_embed)
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
        embed = discord.Embed(color=discord.Color.dark_red(), title="Currently playing")
        embed.add_field( name="Radiant", value="\n".join(self.match.radiant))
        embed.add_field( name="Dire", value="\n".join(self.match.dire))
        embed.set_footer(text="Who won?")
        before = datetime.now()
        await interaction.channel.send(embed=embed, view=LockedMatch(self.match))
        
        # Try deleting the lock teams message
        try:
            await interaction.message.delete()
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
        

class ConfirmLock(discord.ui.View):
    def __init__(self, match, interaction, client: discord.Client, parent: CreateMatch):
        self.match = match
        self.interaction = interaction
        self.parent = parent
        super().__init__(timeout=None)

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.success)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.parent.lock_and_start(interaction, button)

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            embed=discord.Embed(
                color=discord.Color.dark_red(),
                title="Teams not locked",
                description="Please reorganize the teams"
            ),
            view=CreateMatch(match=self.match, interaction=self.interaction)
        )
# For testing purposes
async def get_random_teams(guild):
    members = []
    async for member in guild.fetch_members(limit=10):
        members.append(member)
    random.shuffle(members)
    radiant = [member.name for member in members]
    dire = [member.name for member in members] 
    return (radiant, dire)
