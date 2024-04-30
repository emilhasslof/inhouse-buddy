from utils import *
import os
from copy import deepcopy

snuslan = 123169301094989825
guild_id = snuslan
if not path.exists(f"stats/{guild_id}.json"):
    with open(f"stats/{guild_id}.json", "w") as file:
        file.write("{}")


stats = {}
with open(f"stats/{guild_id}.json", "r") as file: 
    stats_json = "\n".join(file.readlines())
    stats = json.loads(stats_json)

radiant = ["slyver123", "jakob7121", "cricket9584", "jockwe", "mandelmans"]
dire = ["kingo.1337", ".skiipa", "sku6808", "lackosia", "jointzart"] 

for player in radiant + dire:
    if player not in stats: 
        stats[player] = {"wins": 0, "losses": 0}

initial_stats = deepcopy(stats)
calculate_stats(initial_stats)

calculate_stats(stats)
        
add_win(players=radiant, stats=stats)
add_loss(players=dire, stats=stats)

add_win(players=radiant, stats=stats)
add_loss(players=dire, stats=stats)

#calculate_stats(stats)

assert stats["slyver123"]["winstreak"] == 2, f"expected 2, got {stats['slyver123']['winstreak']}"
assert stats["jointzart"]["winstreak"] == -2, f"expected -2, got {stats['jointzart']['winstreak']}"

add_win(players=dire, stats=stats)
add_loss(players=radiant, stats=stats)
calculate_stats(stats)

assert stats["slyver123"]["winstreak"] == -1, f"expected -1, got {stats['slyver123']['winstreak']}"
assert stats["kingo.1337"]["winstreak"] == 1, f"expected 1, got {stats['kingo.1337']['winstreak']}"

assert stats["slyver123"]["wins"] - initial_stats["slyver123"]["wins"] == 2, f"{stats['slyver123']['wins']} - {initial_stats['slyver123']['wins']} should be equal to 2" 
assert stats["slyver123"]["losses"] - initial_stats["slyver123"]["losses"] == 1, f"{stats['slyver123']['losses']} - {initial_stats['slyver123']['losses']} should be equal to 1"
assert stats["slyver123"]["matches"] - initial_stats["slyver123"]["matches"] == 3, f"{stats['slyver123']['matches']} - {initial_stats['slyver123']['matches']} should be equal to 3"
subtract_win(players=radiant, stats=stats)
subtract_loss(players=dire, stats=stats)

subtract_win(players=radiant, stats=stats)
subtract_loss(players=dire, stats=stats)

subtract_win(players=dire, stats=stats)
subtract_loss(players=radiant, stats=stats)

calculate_stats(stats)

assert stats["slyver123"]["wins"] == initial_stats["slyver123"]["wins"], "slyver123 should have equal wins"
assert stats["slyver123"]["losses"] == initial_stats["slyver123"]["losses"], "slyver123 should have equal losses"
assert stats["slyver123"]["matches"] == initial_stats["slyver123"]["matches"], "slyver123 should have equal matches"
assert stats["slyver123"]["winrate"] == initial_stats["slyver123"]["winrate"], "slyver123 should have the same winrate"

stats = {}
for player in radiant + dire:
    stats[player] = {"wins": 0, "losses": 0}

for _ in range(420):
    add_win(players=radiant, stats=stats)
    add_loss(players=dire, stats=stats)
for _ in range(69):
    add_win(players=dire, stats=stats)
    add_loss(players=radiant, stats=stats)
calculate_stats(stats)
total_matches = sum([stats[player]["matches"] for player in radiant + dire]) / 10
assert total_matches == 420 + 69, "Total matches should be 420 + 69"
assert stats["mandelmans"]["winstreak"] == -69, f"expected 69, got {stats['mandelmans']['winstreak']}"
assert stats["jointzart"]["winstreak"] == 69, f"expected 69, got {stats['jointzart']['winstreak']}"

print("All tests passed")
