import discord

class Match():
    def __init__(self, radiant_channel, dire_channel):
        self.radiant_channel = radiant_channel
        self.dire_channel = dire_channel
        self.radiant, self.dire, self.winners, self.losers = [], [], [], []

    # returns a list of users allowed to edit the match
    def can_edit(self, interaction):
        role = discord.utils.get(interaction.guild.roles, name="Inhouse Manager")
        inhouse_managers = [member.name for member in role.members]
        return interaction.user.name in self.radiant + self.dire + inhouse_managers or interaction.user.guild_permissions.administrator
    
    async def cancel(self, interaction):
        await interaction.response.edit_message(delete_after=0.1)
        await self.dire_channel.delete()
        await self.radiant_channel.delete()