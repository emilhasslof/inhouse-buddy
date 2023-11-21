from datetime import datetime
import discord
from discord import app_commands
import asyncio
from os import path
import json
import random
import tabulate
import sqlite3

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

testing = True 


class Match():
    def __init__(self, radiant_channel, dire_channel):
        self.radiant_channel = radiant_channel
        self.dire_channel = dire_channel
        self.radiant, self.dire, self.winners, self.losers = [], [], [], []

    def can_edit(self, interaction):
        role = discord.utils.get(interaction.guild.roles, name="Inhouse Manager")
        inhouse_managers = [member.name for member in role.members]
        return interaction.user.name in self.radiant + self.dire + inhouse_managers or interaction.user.guild_permissions.administrator
    
    async def cancel(self, interaction):
        await interaction.response.edit_message(delete_after=0.1)
        await self.dire_channel.delete()
        await self.radiant_channel.delete()

class CreateMatchView(discord.ui.View):
    def __init__(self, match):
        self.match = match
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
        
        if testing:
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
        
class LockedMatchView(discord.ui.View):
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
                view=ConfirmView(self.match)
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
                view=ConfirmView(self.match)
            )
        else:
            await interaction.response.send_message(f"{interaction.user.name} is not allowed to do this", delete_after=5)

    @discord.ui.button(label="Cancel Match", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.match.can_edit(interaction):
            await interaction.response.edit_message(
                embed=interaction.message.embeds[0].set_footer(text="This will cancel the match, please confirm"),
                view=ConfirmCancelView(self.match)
            )
        else:
            await interaction.response.send_message(f"{interaction.user.name} is not allowed to do this", delete_after=5)

class ConfirmView(discord.ui.View):
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
           view=LockedMatchView(self.match)
       ) 

class ConfirmCancelView(discord.ui.View):
    def __init__(self, match):
        self.match=match
        super().__init__(timeout=None)

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.match.cancel(interaction)
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            embed=interaction.message.embeds[0].set_footer(text="Who won?"),
            view=LockedMatchView(self.match)
        )

class ScheduledMatchView(discord.ui.View):
    def __init__(self, *, datetime: datetime, players: list, guild_id: int):
        self.datetime = datetime
        self.players = players
        self.conn = sqlite3.connect(f"./databases/{guild_id}.db")
        self.c = self.conn.cursor()
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Sign Up", style=discord.ButtonStyle.success)
    async def sign_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.name in self.players: return
        try:
            print(f"INSERTING ---- datetime: {str(datetime)}" + f"player: {interaction.user.name}")
            # this doesn't work for some reason
            self.c.execute(f"INSERT INTO match_player_signups VALUES (?, ?)", (str(datetime), interaction.user.name))
            self.conn.commit()
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
        if interaction.user.name not in self.players: return
        self.c.execute(f"DELETE FROM match_player_signups WHERE datetime = ? AND player = ?", (str(datetime), interaction.user.name))
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


# ----- Commands ----- 

@tree.command(name="schedule", description=
              """View or join scheduled matches. 
                date: YYYY-MM-DD time: HH:MM => Schedule new match""",
                guild=discord.Object(id=123169301094989825))
async def schedule_match(interaction, date: str = "", time: str = ""):

    conn = sqlite3.connect(f"./databases/{interaction.guild_id}.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS scheduled_matches (datetime TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS match_player_signups (datetime TEXT, player TEXT)")

    channel = interaction.channel

    if (date is not "") ^ (time is not ""):  # XOR
        await interaction.response.send_message(
            embed=discord.Embed(
                color=discord.Color.dark_red(),
                title="Error",
                description="Please specify both date and time"
            ),
            delete_after=30,
            ephemeral=True
        )
        return
    elif date and time:
        try:
            match_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        except ValueError:
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=discord.Color.dark_red(),
                    title="Error",
                    description="Invalid date or time format"
                ),
                delete_after=30,
                ephemeral=True
            )
            return

        c.execute(f"INSERT INTO scheduled_matches VALUES (?)", (match_datetime.strftime("%Y-%m-%d %H:%M"),))
        conn.commit()
    

    c.execute("SELECT * FROM scheduled_matches")
    scheduled_matches_datetimes = [match[0] for match in c.fetchall()]
    scheduled_matches = [{}]
    for datetime in scheduled_matches_datetimes:
        c.execute("SELECT * FROM match_player_signups WHERE datetime = ?", (datetime,))
        fetched = c.fetchall()
        print(f"fetched: {fetched}")
        players = [player[1] for player in fetched]
        print(f"players1: {players}")
        players0 = [player[0] for player in fetched]
        print(f"players0: {players0}")
        scheduled_matches.append({datetime: players})
        await channel.send(
            embed=discord.Embed(
                color=discord.Color.dark_red(),
                title=f"Match scheduled for {datetime}",
                description="Players: \n " + "\n ".join(players) 
            ),
            view=ScheduledMatchView(datetime=datetime, players=players, guild_id=interaction.guild_id)
        )
    return

@tree.command(name="inhouse", description="Prepare an inhouse match", guild=discord.Object(id=123169301094989825))
async def create_match(interaction: discord.Interaction):
    category = interaction.channel.category
    if category:
        radiant_channel = await category.create_voice_channel(name="Radiant")
        dire_channel = await category.create_voice_channel(name="Dire")
    else:
        radiant_channel = await interaction.guild.create_voice_channel(name="Radiant")
        dire_channel = await interaction.guild.create_voice_channel(name="Dire")

    match = Match(radiant_channel=radiant_channel, dire_channel=dire_channel)
    embed = discord.Embed(
        color=discord.Color.dark_red(),
        description="Join your team channels, then lock the teams to start the match",
        title="Preparing match"
    )
    embed.set_thumbnail(url="https://cdn0.iconfinder.com/data/icons/sports-elements-2/24/Swords-512.png")

    await interaction.response.send_message(
        view=CreateMatchView(match),
        embed=embed
    )

@tree.command(name="inhouse-stats", description="Show inhouse statistics", guild=discord.Object(id=123169301094989825))
async def show_stats(interaction):
    await send_stats_message(interaction, timeout=60)


async def send_stats_message(interaction, timeout):
    stats_json = ""  
    with open(f"{interaction.guild_id}.json", "r") as file: 
        stats_json = "\n".join(file.readlines())
    stats = json.loads(stats_json)
    players_ranked = sorted(stats.items(), key=lambda x: x[1]["points"], reverse=True)
    header = list(players_ranked[0][1].keys())
    header.insert(0, "name")
    rows = []
    rows_2 = []
    for i, (player, player_stats) in enumerate(players_ranked):
        l = list(map(str, player_stats.values()))
        l.insert(0, player)
        if(i < 20):
            rows.append(l)
        else:
            rows_2.append(l)
    
    await interaction.response.send_message(f"```{tabulate.tabulate(rows, header)}```", delete_after=timeout)
    if rows_2:
        await interaction.channel.send(f"```{tabulate.tabulate(rows_2, header)}```", delete_after=timeout)

# Update stats in "guild_id.json", unique file for each guild
def submit_match_result(*, guild_id, winners, losers):
    stats = {}
    if path.exists(f"{guild_id}.json"):
        with open(f"{guild_id}.json", "r") as file: 
            stats_json = "\n".join(file.readlines())
        stats = json.loads(stats_json)

    for player in winners:
        if player not in stats: 
            stats[player] = {"wins": 0, "losses": 0, "matches": 0, "winrate": 0, "points": 0, "rank": 0}
        stats[player]["wins"] += 1
        stats[player]["points"] += 1
        stats[player]["matches"] += 1
        stats[player]["winrate"] = round(stats[player]["wins"] / stats[player]["matches"], 3)

    for player in losers:
        if player not in stats: 
            stats[player] = {"wins": 0, "losses": 0, "matches": 0, "winrate": 0, "points": 0, "rank": 0}
        stats[player]["losses"] += 1
        stats[player]["points"] -= 1
        stats[player]["matches"] += 1
        stats[player]["winrate"] = round(stats[player]["wins"] / stats[player]["matches"], 3)

    # Sort players by points and update ranking
    players_ranked = sorted(stats.items(), key=lambda x: x[1]["points"], reverse=True)
    prev_points = None
    prev_rank = None
    for i, (player, _) in enumerate(players_ranked, start=1):
        if stats[player]["points"] == prev_points:
            stats[player]["rank"] = prev_rank
        else: 
            stats[player]["rank"] = i

        prev_points = stats[player]["points"]
        prev_rank = stats[player]["rank"]

    # Overwrite json with new stats
    stats_json = json.dumps(stats, indent=4)
    with open(f"{guild_id}.json", "w") as file:
        file.writelines(stats_json)

# For testing purposes
async def get_random_teams(guild):
    members = []
    async for member in guild.fetch_members(limit=20):
        members.append(member)
    random.shuffle(members)
    radiant = [member.name for member in members[:5]]
    dire = [member.name for member in members[5:10]] 
    return (radiant, dire)

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    await tree.sync(guild=discord.Object(id=123169301094989825))
    print("Synced commands")

with open("token.txt", "r") as file: 
    token = file.read()
client.run(token)
