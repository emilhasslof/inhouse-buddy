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

# Holds global variables with information on ongoing matches
# Teams currently playing: 
# (guild_id, "radiant"): [player_names]
# (guild_id, "dire"): [player_names]
# Messages in control channel: 
# (guild_id, "teams_locked_message_id"): message.id
global_vars = {}
testing = True

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
        super().__init__()

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

        embed = discord.Embed(
            color=discord.Color.dark_red(),
            title="Currently playing"
        )
        embed.add_field(
            name="Radiant",
            value="\n".join(self.match.radiant)
        )
        embed.add_field(
            name="Dire",
            value="\n".join(self.match.dire)
        )
        embed.set_footer(text="Who won?")
        await interaction.response.edit_message(
            view=LockedMatchView(self.match),
            embed=embed
        ) 

    @discord.ui.button(label="Cancel Match", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(delete_after=0.1)
        await self.match.radiant_channel.delete()
        await self.match.dire_channel.delete()
        
class LockedMatchView(discord.ui.View):
    def __init__(self, match):
        self.match = match
        super().__init__() 
    
    @discord.ui.button(label="Radiant", style=discord.ButtonStyle.success)
    async def winner_radiant(self, interaction: discord.Interaction, button: discord.ui.Button):
       submit_match_result(guild_id=interaction.guild, winners=self.match.radiant, losers=self.match.dire) 
       cancel_match(interaction=interaction, match=self.match)

    @discord.ui.button(label="Dire", style=discord.ButtonStyle.success)
    async def winner_dire(self, interaction: discord.Interaction, button: discord.ui.Button):
       submit_match_result(guild_id=interaction.guild, winners=self.match.dire, losers=self.match.radiant)
       await cancel_match(interaction=interaction, match=self.match)

    @discord.ui.button(label="Cancel Match", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await cancel_match(interaction=interaction, match=self.match)


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
    await send_stats_message(guild_id=interaction.guild, channel=interaction.channel, timeout=30)



@client.event
async def on_guild_join(guild):
    print(f"Joined {guild.name}!")
    if not await has_control_channel(guild):
        await create_control_channel(guild)
    if not await has_voice_channels(guild):
        await create_voice_channels(guild)
    # check/create channels? Maybe on guild join?


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    # TODO: This check should some place smarter when scaling
    for guild in client.guilds:
        if not await has_control_channel(guild):
            await create_control_channel(guild)
        if not await has_voice_channels(guild):
            await create_voice_channels(guild)

async def has_control_channel(guild):
    control_channel = next((channel for channel in guild.channels if channel.name == "inhouse-control"), None)
    return control_channel is not None
    # control_channel = await guild.fetch_channel(control_channel.id)
    # message = await control_channel.fetch_message(control_channel.last_message_id)
    # if message is None: return False
    # return message.author == client.user

async def create_control_channel(guild):
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(send_messages=False, manage_messages=False, add_reactions=True),
        guild.me: discord.PermissionOverwrite(send_messages=True, manage_messages=True)
    }
    control_channel = await guild.create_text_channel("inhouse-control", overwrites=overwrites)

    message = await control_channel.send("""Welcome to the inhouse control room. Add reactions to control the bot\n
    :lock: : Lock teams and start match\n
    :trophy: : Show stats\n
     \n""")
    await message.add_reaction("🔒")
    await message.add_reaction("🏆")

async def has_voice_channels(guild):
    channels = (channel.name for channel in guild.channels if channel.name == "inhouse-radiant" or channel.name == "inhouse-dire")
    return "inhouse-radiant" in channels and "inhouse-dire" in channels

async def create_voice_channels(guild):
    radiant_channel = await guild.create_voice_channel("inhouse-radiant")
    dire_channel = await guild.create_voice_channel("inhouse-dire")
    return (radiant_channel, dire_channel)

@client.event
async def on_raw_reaction_add(payload):
    global global_vars
    # Bot should not act on its own reactions
    if payload.user_id == client.user.id: return
    try:
        guild = await client.fetch_guild(payload.guild_id)
        control_channel = await client.fetch_channel(payload.channel_id)
        message = await control_channel.fetch_message(payload.message_id)
        member = await guild.fetch_member(payload.user_id)
    except discord.errors.NotFound:
        print("Not found error detected")
        return
    emoji = payload.emoji
    # Make sure we are in the right channel
    if not (control_channel.name == "inhouse-control" and message.author == client.user): return 
    
    await message.remove_reaction(emoji, member)
    teams_locked = global_vars.get((guild.id, "teams_locked_message_id"), 0) != 0
    teams_locked_message_id = global_vars.get((guild.id, "teams_locked_message_id"), 0)
    confirm_message_id = global_vars.get((guild.id, "confirm_message_id"), 0)

    # root message
    if emoji.name == "🔒" and not teams_locked:
        # Immediately put some value to prevent going here again if user spam-clicks
        global_vars[(guild.id, "teams_locked_message_id")] = 1
        await lock_and_start(guild, control_channel)
        return
    elif emoji.name == "🏆":
        await send_stats_message(guild.id, control_channel, timeout=600)
        return

    # teams locked message
    if message.id == teams_locked_message_id and confirm_message_id == 0:
        global_vars[(guild.id, "confirm_message_id")] = 1
        teams_locked_message = await control_channel.fetch_message(teams_locked_message_id)
        confirm_string = ""
        winner = ""
        if emoji.name == "🇷":
            winner = "radiant"
            confirm_string = "This will update statistics, please confirm that Radiant won the match"
        elif emoji.name == "🇩":
            winner = "dire"
            confirm_string = "This will update statistics, please confirm that Dire won the match"
        elif emoji.name == "🚫":
            winner = "cancelled"
            confirm_string = "This will cancel the match, please confirm"
        else:
            # any other emote
            return

        confirm_message = await control_channel.send(confirm_string)
        global_vars[(guild.id, "confirm_message_id")] = confirm_message.id
        global_vars[(guild.id, "winner")] = winner
        await confirm_message.add_reaction("✅")
        await confirm_message.add_reaction("🚫")
        return
    
    # confirmation message
    if message.id == confirm_message_id:
        global_vars[(guild.id, "confirm_message_id")] = 0
        confirm_message = await control_channel.fetch_message(confirm_message_id)
        teams_locked_message = await control_channel.fetch_message(teams_locked_message_id)
        if emoji.name == ("✅"):
            winner = global_vars.get((guild.id, "winner"), "")
            if winner == "cancelled":
                global_vars.clear()
                await teams_locked_message.delete()
                await confirm_message.delete()
                await send_temporary_message("Match cancelled", control_channel, timeout=5)
                return
            submit_match_result(guild.id)
            await teams_locked_message.delete()
            global_vars[guild.id, "teams_locked_message_id"] = 0
            await send_temporary_message(f"Submitting match result, congratulations team {winner}", control_channel, timeout=5)
        elif emoji.name == ("🚫"):
            pass
        else:
            return
        await confirm_message.delete()

# Fetch players from each voice channel and send "teams locked" message in discord
async def lock_and_start(guild, control_channel):
    global global_vars
    guild_id = guild.id
    radiant_channel, dire_channel = await fetch_inhouse__voice_channels(guild)
    if not (len(radiant_channel.members) == 5 and len(dire_channel.members) == 5) and not testing:
        global_vars[(guild_id, "teams_locked_message_id")] = 0
        await send_temporary_message(f"""Both teams need 5 players! Players found:\n
        Radiant: {", ".join([member.name for member in radiant_channel.members])}\n
        Dire: {", ".join([member.name for member in dire_channel.members])} \n""",
        control_channel, timeout=10)
        return
    
    if testing:
        members = []
        async for member in guild.fetch_members(limit=20):
            members.append(member.name)
        random.shuffle(members)
        global_vars[(guild_id, "radiant")] = members[:5]
        global_vars[(guild_id, "dire")] = members[5:10]
    else:
        global_vars[(guild_id, "radiant")] = [member.name for member in radiant_channel.members]
        global_vars[(guild_id, "dire")] = [member.name for member in dire_channel.members]
    
    message = await control_channel.send(f"""Teams locked, good luck!
    ```Radiant: {", ".join(global_vars[(guild.id, "radiant")])}\nDire: {", ".join(global_vars[(guild.id, "dire")])}```
    :regional_indicator_r: Radiant won\n
    :regional_indicator_d: Dire won\n
    :no_entry_sign: Cancel match, no winner\n
    """)
    await message.add_reaction("🇷")
    await message.add_reaction("🇩")
    await message.add_reaction("🚫")
    global_vars[(guild_id, "teams_locked_message_id")] = message.id

# Fetch channels with API call, since channel.members doesn't seem to be populated in the cache
async def fetch_inhouse__voice_channels(guild):
    (radiant_channel, dire_channel) = (None, None)
    guild_channels = await guild.fetch_channels()
    for channel in guild_channels:
        if channel.name == "inhouse-radiant":
            radiant_channel = channel
        elif channel.name == "inhouse-dire":
            dire_channel = channel

    radiant_channel = await client.fetch_channel(radiant_channel.id)
    dire_channel = await client.fetch_channel(dire_channel.id)
    return (radiant_channel, dire_channel)

async def send_temporary_message(text, channel, *, timeout):
    m = await channel.send(text)
    await m.delete(delay=timeout)

async def send_stats_message(guild_id, channel, *, timeout):
    stats_json = ""  
    with open(f"{guild_id}.json", "r") as file: 
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
    

    m = await channel.send(f"```{tabulate.tabulate(rows, header)}```")
    await m.delete(delay=timeout)
    if rows_2:
        m = await channel.send(f"```{tabulate.tabulate(rows_2, header)}```")
        await m.delete(delay=timeout)

# Update stats in "guild_id.json", unique file for each guild
def submit_match_result(*, guild_id, winners, losers):
    # I this is the first match in this guild, create a fresh json instead
    if not path.exists(f"{guild_id}.json"):
        create_match_result(guild_id=guild_id, winners=winners, losers=losers)
        return
    
    # load stats from json
    stats_json = ""  
    with open(f"{guild_id}.json", "r") as file: 
        stats_json = "\n".join(file.readlines())
    stats = json.loads(stats_json)

    # Update stats
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


# Create the initial json file if this is the first match played in this guild
def create_match_result(*, guild_id, winners, losers):
    stats = {}

    for player in winners:
        stats[player] = {
            "wins": 1,
            "losses": 0,
            "matches": 1,
            "winrate": 1,
            "points": 1,
            "rank": 1
        }
    for player in losers:
        stats[player] = {
            "wins": 0,
            "losses": 1,
            "matches": 1,
            "winrate": 0,
            "points": -1,
            "rank": 6
        }

    stats_json = json.dumps(stats, indent=4)
    with open(f"{guild_id}.json", "w") as file:
        file.writelines(stats_json)


with open("token.txt", "r") as file: 
    token = file.read()
client.run(token)
