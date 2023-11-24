
import discord
import sqlite3
from DatabaseHandler import DatabaseHandler

class ScheduledMatch(discord.ui.View):
    def __init__(self, *, datetime_string: str, players: list, guild_id: int, 
        db_handler: DatabaseHandler):
        self.datetime_string = datetime_string
        self.players = players
        self.db_handler=db_handler
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Sign Up", style=discord.ButtonStyle.success)
    async def sign_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.name in self.players: #already signed up
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=discord.Color.dark_red(),
                    title="Error",
                    description="You are already signed up"
                ),
                delete_after=30,
                ephemeral=True
            )
            return

        self.players = self.db_handler.sign_up(self.datetime_string, interaction.user.name)

        await interaction.response.edit_message(
            embed=discord.Embed(
                color=discord.Color.dark_red(),
                title=f"Match scheduled for {self.datetime_string}",
                description="Players: \n " + "\n ".join(self.players)
            ),
            view=self
        )

    @discord.ui.button(label="Sign Down", style=discord.ButtonStyle.danger)
    async def sign_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.name not in self.players: #not signed up
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=discord.Color.dark_red(),
                    title="Error",
                    description="You are not signed up"
                ),
                delete_after=30,
                ephemeral=True
            )
            return 

        self.players = self.db_handler.sign_down(self.datetime_string, interaction.user.name)

        await interaction.response.edit_message(
            embed=discord.Embed(
                color=discord.Color.dark_red(),
                title=f"Match scheduled for {self.datetime_string}",
                description="Players: \n " + "\n ".join(self.players) 
            ),
            view=self
        )