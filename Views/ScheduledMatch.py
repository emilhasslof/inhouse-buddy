
import discord
import sqlite3
from DatabaseHandler import DatabaseHandler
from Match import Match
from Views.CreateMatch import CreateMatch

class ScheduledMatch(discord.ui.View):
    def __init__(self, *, datetime_string: str, guild_id: int, db_handler: DatabaseHandler):
        self.datetime_string = datetime_string
        self.db_handler=db_handler
        self.players = db_handler.get_players_signed_up(datetime_string)
        self.queue = db_handler.get_queue(datetime_string)
        super().__init__(timeout=None)

        #testing
        print(f"ScheduledMatch created. Players: {self.players}, Time: {self.datetime_string}")
    
    @discord.ui.button(label="Sign Up", style=discord.ButtonStyle.success)
    async def sign_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.players = self.db_handler.get_players_signed_up(self.datetime_string)
        if interaction.user.name in self.players: #already signed up
            await interaction.response.defer()
            return

        if len(self.players) < 10:
            self.players = self.db_handler.sign_up(self.datetime_string, interaction.user.name)
        else:
            self.queue = self.db_handler.add_to_queue(self.datetime_string, interaction.user.name)  

        await interaction.response.edit_message(
            embed=discord.Embed(
                color=discord.Color.dark_red(),
                title=f"Match scheduled for {self.datetime_string}",
                description="Players: \n " + "\n ".join(self.players) + 
                    ("\n\nQueue: \n " + "\n ".join(self.queue) if self.queue else "")
            ),
            view=self
        )

        if self.players == 10:
            await interaction.channel.send("""
                @inhousers It's on! Match scheduled for {self.datetime_string} is now full! 
                Further signups will be added to the queue.
                                           """)

    @discord.ui.button(label="Sign Down", style=discord.ButtonStyle.danger)
    async def sign_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.players = self.db_handler.get_players_signed_up(self.datetime_string)
        if interaction.user.name not in self.players + self.queue: #not signed up
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

        if (interaction.user.name in self.players):
            self.players = self.db_handler.sign_down(self.datetime_string, interaction.user.name)

        # If there is a queue, pop the first player and add to players
        if len(self.players) == 9 and self.queue:
            self.players = self.db_handler.sign_up(datetime_string=self.datetime_string, 
                                                   player=self.db_handler.pop_from_queue(self.datetime_string))  

        await interaction.response.edit_message(
            embed=discord.Embed(
                color=discord.Color.dark_red(),
                title=f"Match scheduled for {self.datetime_string}",
                description="Players: \n " + "\n ".join(self.players) 
            ),
            view=self
        )


    @discord.ui.button(label="Play Now", style=discord.ButtonStyle.blurple)
    async def play_now(self, interaction: discord.Interaction, button: discord.ui.Button):
        category = interaction.channel.category
        if category:
            radiant_channel = await category.create_voice_channel(name=f"{self.datetime_string} - Radiant")
            dire_channel = await category.create_voice_channel(name=f"{self.datetime_string} - Dire")
        else:
            radiant_channel = await interaction.guild.create_voice_channel(name=f"{self.datetime_string} - Radiant")
            dire_channel = await interaction.guild.create_voice_channel(name=f"{self.datetime_string} - Dire")
        

        match = Match(radiant_channel=radiant_channel, dire_channel=dire_channel)
        embed = discord.Embed(
            color=discord.Color.dark_red(),
            title=f"Preparing match scheduled for {self.datetime_string}",
            description=("Join your team channels, then lock the teams to start the match" +  
            "\n\nPlayers: \n " + "\n ".join(self.players) + 
            ("\n\nQueue: \n " + "\n ".join(self.queue) if self.queue else ""))
        )
        embed.set_thumbnail(url="https://cdn0.iconfinder.com/data/icons/sports-elements-2/24/Swords-512.png")
        await interaction.response.send_message(
            view=CreateMatch(match=match, scheduled_players=self.players, scheduled_queue=self.queue),
            embed=embed
        )