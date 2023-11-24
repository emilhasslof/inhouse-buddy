
import discord
import sqlite3
from datetime import datetime


class ScheduledMatch(discord.ui.View):
    def __init__(self, *, datetime: datetime, players: list, guild_id: int, 
                 conn: sqlite3.Connection, c: sqlite3.Cursor):
        self.datetime = datetime
        self.players = players
        self.conn = conn 
        self.c = c
        super().__init__(timeout=None)
        print(f"initialized view, datetime: {datetime}")
    
    @discord.ui.button(label="Sign Up", style=discord.ButtonStyle.success)
    async def sign_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.name in self.players: 
            interaction.response.send_message(
                embed=discord.Embed(
                    color=discord.Color.dark_red(),
                    title="Error",
                    description="You are already signed up"
                ),
                delete_after=30,
                ephemeral=True
            )
            return
        try:
            print(f"INSERTING ---- datetime: {self.datetime}" + f" player: {interaction.user.name}")
            self.c.execute(f"INSERT INTO match_player_signups VALUES (?, ?)", (self.datetime, interaction.user.name))
            self.conn.commit()
            players_in_database = self.c.execute(f"SELECT * FROM match_player_signups WHERE datetime = ?", (self.datetime,)).fetchall()
            print(f"players_in_database: {players_in_database}")
        except Exception as e:
            print(e)

        self.players.append(interaction.user.name)
        await interaction.response.edit_message(
            embed=discord.Embed(
                color=discord.Color.dark_red(),
                title=f"Match scheduled for {self.datetime}",
                description="Players: \n " + "\n ".join(self.players)
            ),
            view=self
        )

    @discord.ui.button(label="Sign Down", style=discord.ButtonStyle.danger)
    async def sign_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.name not in self.players:
            interaction.response.send_message(
                embed=discord.Embed(
                    color=discord.Color.dark_red(),
                    title="Error",
                    description="You are not signed up"
                ),
                delete_after=30,
                ephemeral=True
            )
            return 

        self.c.execute(f"DELETE FROM match_player_signups WHERE datetime = ? AND player = ?", (self.datetime, interaction.user.name))
        self.conn.commit()
        self.players.remove(interaction.user.name)
        await interaction.response.edit_message(
            embed=discord.Embed(
                color=discord.Color.dark_red(),
                title=f"Match scheduled for {self.datetime}",
                description="Players: \n " + "\n ".join(self.players) 
            ),
            view=self
        )