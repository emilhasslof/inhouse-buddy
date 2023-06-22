import discord
from discord import app_commands
import asyncio
from os import path
import json
import random
import tabulate

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

testing = True 

# For testing purposes
async def get_random_teams(guild):
    members = []
    async for member in guild.fetch_members(limit=20):
        members.append(member)
    random.shuffle(members)
    radiant = [member.name for member in members[:5]]
    dire = [member.name for member in members[5:10]] 
    return (radiant, dire)

class Match():
    def __init__(self, radiant_channel, dire_channel):
        self.radiant_channel = radiant_channel
        self.dire_channel = dire_channel

class CreateMatchView(discord.ui.View):
    def __init__(self, match):
        self.match = match
        super().__init__(timeout=None)

    @discord.ui.button(label="Lock teams & start", style=discord.ButtonStyle.success)
    async def lock_and_start(self, interaction: discord.Interaction, button: discord.ui.Button):
        print(", ".join([p.name for p in self.match.radiant_channel.members]))
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
        await cancel_match(interaction=interaction, match=self.match)        
        
class LockedMatchView(discord.ui.View):
    def __init__(self, match):
        self.match = match
        super().__init__(timeout=None) 
    
    @discord.ui.button(label="Radiant", style=discord.ButtonStyle.success)
    async def winner_radiant(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.match.winners=self.match.radiant
        self.match.losers=self.match.dire
        embed = interaction.message.embeds[0]
        embed.set_footer(text="This will update stats, please confirm")
        await interaction.response.edit_message(
            embed=embed,
            view=ConfirmView(self.match)
        )

    @discord.ui.button(label="Dire", style=discord.ButtonStyle.success)
    async def winner_dire(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.match.winners=self.match.dire
        self.match.losers=self.match.radiant
        embed = interaction.message.embeds[0]
        embed.set_footer(text="This will update stats, please confirm")
        await interaction.response.edit_message(
            embed=embed,
            view=ConfirmView(self.match)
        )

    @discord.ui.button(label="Cancel Match", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await cancel_match(interaction=interaction, match=self.match)

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
    
    

async def cancel_match(*, interaction, match):
    await interaction.response.edit_message(delete_after=0.1)
    await match.radiant_channel.delete()
    await match.dire_channel.delete()


# ----- Commands ----- 
@tree.command(name="inhouse", description="Prepare an inhouse match", guild=discord.Object(id=123169301094989825))
async def create_match(interaction):
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

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    await tree.sync(guild=discord.Object(id=123169301094989825))

with open("token.txt", "r") as file: 
    token = file.read()
client.run(token)
