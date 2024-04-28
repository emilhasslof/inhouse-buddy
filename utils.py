from os import path
import json

snuslan_id="123169301094989825"
wew_id="745215730592645221"
guild_id = snuslan_id

if path.exists(f"{guild_id}.json"):
    stats = {}
    with open(f"{guild_id}.json", "r") as file: 
        stats_json = "\n".join(file.readlines())
        stats = json.loads(stats_json)
                

        # add win, subtract loss
        radiant = ["flyver123", "jakob7121", "cricket9584", "jockwe", "mandelmans"]

        # subtract win, add loss
        dire = ["kingo.1337", ".skiipa", "sku6808", "lackosia", "jointzart"] 

        for player in radiant + dire:
            print(player)

        #update_ranks(stats)

    # Overwrite json with new stats
    with open(f"{guild_id}.json", "w") as file:
        stats_json = json.dumps(stats, indent=4)
        file.writelines(stats_json)


def add_win(*, guild_id, players, stats):
    if player not in stats:
        print(f"warning, {player} was not found in stats")
        return
    for player in players:
        stats[player]["wins"] += 1
        stats[player]["points"] += 1
        stats[player]["matches"] += 1
        stats[player]["winrate"] = round(stats[player]["wins"] / stats[player]["matches"], 2)

def subtract_win(*, guild_id, players):
    if player not in stats:
        print(f"warning, {player} was not found in stats")
        return
    for player in players:
        stats[player]["wins"] -= 1
        stats[player]["points"] -= 1
        stats[player]["matches"] -= 1
        stats[player]["winrate"] = round(stats[player]["wins"] / stats[player]["matches"], 2)

def add_loss(*, guild_id, players):
    for player in players:
        stats[player]["losses"] += 1
        stats[player]["points"] -= 1
        stats[player]["matches"] += 1
        stats[player]["winrate"] = round(stats[player]["wins"] / stats[player]["matches"], 2)

def subtract_loss(*, guild_id, players):
    if player not in stats:
        print(f"warning, {player} was not found in stats")
        return
    for player in players:
        stats[player]["losses"] -= 1
        stats[player]["points"] += 1
        stats[player]["matches"] -= 1
        stats[player]["winrate"] = round(stats[player]["wins"] / stats[player]["matches"], 2)


def update_ranks(stats):
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
