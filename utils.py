from os import path
import json

def add_win(*, players, stats):
    for player in players:
        stats[player]["wins"] += 1

def subtract_win(*, players, stats):
    for player in players:
        stats[player]["wins"] = max(stats[player]["wins"] - 1, 0)

def add_loss(*, players, stats):
    for player in players:
        stats[player]["losses"] += 1

def subtract_loss(*, players, stats):
    for player in players:
        stats[player]["losses"] = max(stats[player]["losses"] - 1, 0)


def calculate_stats(stats):
    for player in stats:
        print(f"Calculating stats for {player}")
        stats[player]["points"] = stats[player]["wins"] - stats[player]["losses"]
        stats[player]["matches"] = stats[player]["wins"] + stats[player]["losses"]
        if stats[player]["matches"] == 0:
            stats[player]["winrate"] = 0
        else:
            stats[player]["winrate"] = stats[player]["wins"] / stats[player]["matches"]

    total_matches = sum([stats[player]["matches"] for player in stats]) / 10
    players_ranked = sorted(stats.items(), key=lambda x: x[1]["points"], reverse=True)
    prev_points = None
    prev_rank = None
    for i, (player, _) in enumerate(players_ranked, start=1):
        stats[player]["participation"] = stats[player]["matches"] / total_matches
        if stats[player]["points"] == prev_points:
            stats[player]["rank"] = prev_rank
        else: 
            stats[player]["rank"] = i

        prev_points = stats[player]["points"]
        prev_rank = stats[player]["rank"]






