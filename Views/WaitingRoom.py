import discord

class WaitingRoom(discord.ui.View):
    players = []

    def __init__(self, founder: str):
        self.players = []
        self.players.append(founder)
        super().__init__()
    


    @discord.ui.button(label="Join", style=discord.ButtonStyle.success)
    async def sign_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        inhouse_enjoyer = discord.utils.get(interaction.guild.roles, name="Inhouse enjoyer")
        if not interaction.user.name in self.players:
            self.players.append(interaction.user.name)
        if len(self.players) >= 10:
            await interaction.response.send_message(
                embed=discord.Embed(
                        title=f"Inhouse Alert!",
                        description=f"<@&{inhouse_enjoyer.id}> 10 players have joined the waiting room",
                )
            )
        await interaction.response.edit_message(
            embed=discord.Embed(
                title = f"Waiting room\n{len(self.players)}/10 are down to clown",
                description = "\n".join(self.players)
            ) 
        )
        return

    
    @discord.ui.button(label="Leave", style=discord.ButtonStyle.secondary)
    async def leave(self, interaction: discord.Interaction,  button: discord.ui.Button):
        if interaction.user.name in self.players:
            self.players.remove(interaction.user.name)
        await interaction.response.edit_message(
            embed=discord.Embed(
                title = f"{len(self.players)}/10 are down to clown",
                description = "\n".join(self.players)
            ) 
        )
        return

    @discord.ui.button(label="Delete Room", style=discord.ButtonStyle.danger)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(delete_after=1)

