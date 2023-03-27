import discord
import asyncio
from os import path
import json
import random
import tabulate

testing = False


intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

# Holds global variables with information on ongoing matches
# Teams currently playing: 
# (guild_id, "radiant"): [player_names]
# (guild_id, "dire"): [player_names]
# Messages in control channel: 
# (guild_id, "teams_locked_message_id"): message.id
global_vars = {}

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
def submit_match_result(guild_id):
    # I this is the first match in this guild, create a fresh json instead
    if not path.exists(f"{guild_id}.json"):
        create_match_result(guild_id)
        return
    
    # load stats from json
    stats_json = ""  
    with open(f"{guild_id}.json", "r") as file: 
        stats_json = "\n".join(file.readlines())
    stats = json.loads(stats_json)

    # determine winners and losers
    winner = global_vars.pop((guild_id, "winner"))
    team_radiant = global_vars.pop((guild_id, "radiant"))
    team_dire = global_vars.pop((guild_id, "dire"))
    winners = []
    losers = []
    if winner == "radiant":
        winners = team_radiant
        losers = team_dire
    elif winner == "dire":
        winners = team_dire
        losers = team_radiant
    else:
        raise Exception("No winner found")
    
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
def create_match_result(guild_id):
    winner = global_vars.pop((guild_id, "winner"))
    stats = {}
    if winner == "radiant":
        winners = global_vars.pop((guild_id, "radiant"))
        losers = global_vars.pop((guild_id, "dire"))
    elif winner == "dire":
        winners = global_vars.pop((guild_id, "dire"))
        losers = global_vars.pop((guild_id, "radiant"))

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
