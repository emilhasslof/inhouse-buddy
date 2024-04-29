from utils import *


if path.exists(f"{guild_id}.json"):

    snuslan_id="123169301094989825"
    wew_id="745215730592645221"
    guild_id = wew_id

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
