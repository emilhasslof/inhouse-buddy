from os import path
import json


snuslan_id="123169301094989825"
wew_id="745215730592645221"
guild_id = wew_id



def add_win(*, guild_id, players, stats):
    for player in players:
        stats[player]["wins"] += 1
        stats[player]["matches"] += 1

def subtract_win(*, guild_id, players, stats):
    for player in players:
        stats[player]["wins"] = max(stats[player]["wins"] - 1, 0)
        stats[player]["matches"] -= 1

def add_loss(*, guild_id, players, stats):
    for player in players:
        stats[player]["losses"] += 1
        stats[player]["matches"] += 1

def subtract_loss(*, guild_id, players, stats):
    for player in players:
        stats[player]["losses"] = max(stats[player]["losses"] - 1, 0)
        stats[player]["matches"] -= 1


def calculate_stats(stats):
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

        if stats[player]["matches"] == 0:
            stats[player]["winrate"] = 0
        else:
            stats[player]["winrate"] = round(stats[player]["wins"] / stats[player]["matches"], 2)


        stats[player]["points"] = stats[player]["wins"] - stats[player]["losses"]


if path.exists(f"{guild_id}.json"):
    stats = {}
    with open(f"{guild_id}.json", "r") as file: 
        stats_json = "\n".join(file.readlines())
        stats = json.loads(stats_json)
                

        # add win, subtract loss
        #radiant = ["slyver123", "jakob7121", "cricket9584", "jockwe", "mandelmans"]
        radiant = []

        # subtract win, add loss
        #dire = ["kingo.1337", ".skiipa", "sku6808", "lackosia", "jointzart"] 
        dire = []

        for player in radiant + dire:
            if player not in stats: 
                print(f"warning, {player} was not found in stats")
                stats[player] = {"wins": 0, "losses": 0, "matches": 0, "winrate": 0, "points": 0, "rank": 0}

        players = []
        #add_win(guild_id=guild_id, players=players, stats=stats)
        #subtract_loss(guild_id=guild_id, players=players, stats=stats)


        # update score, winrate, rank
        calculate_stats(stats)

    # Overwrite json with new stats
    with open(f"{guild_id}.json", "w") as file:
        stats_json = json.dumps(stats, indent=4)
        file.writelines(stats_json)
