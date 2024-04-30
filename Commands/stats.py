import tabulate
import json
import discord
from utils import calculate_stats


async def stats_command(interaction, timeout):
    stats_json = ""  
    try:
        with open(f"stats/{interaction.guild_id}.json", "r") as file: 
            stats_json = "\n".join(file.readlines())
    except FileNotFoundError:
        await interaction.response.send_message(
            embed=discord.Embed(
                color=discord.Color.dark_red(),
                title="Error",
                description="No stats available"
            ),
            delete_after=30,
            ephemeral=True
        )
        return
    stats = json.loads(stats_json)
    calculate_stats(stats)
    players_ranked = sorted(stats.items(), key=lambda x: x[1]["points"], reverse=True)
    total_matches = sum([stats[player]["matches"] for player in stats]) / 10
    header = list(players_ranked[0][1].keys()) 
    header.insert(0, "name")
    del header[6]
    rows = []
    rows_2 = []
    rows_3 = []
    rows_4 = []
    for i, (player, player_stats) in enumerate(players_ranked):
        player_stats["winrate"] = str(round(player_stats["winrate"] * 100, 1)) + "%"
        player_stats["participation"] = str(round(player_stats["participation"] * 100, 1)) + "%"
        if player_stats['rank'] >= 10:
            rank_name = f"{player_stats['rank']}. {player}"
        else:
            rank_name = f"{player_stats['rank']}.  {player}"
        del player_stats['rank']
        l = list(map(str, player_stats.values()))
        l.insert(0, rank_name)
        if(i < 10):
            rows.append(l)
        elif i < 20:
            rows_2.append(l)
        elif i < 30:
            rows_3.append(l)
        elif i < 40:
            rows_4.append(l)

    await interaction.response.send_message(f"```stats from {total_matches} matches:\n\n{tabulate.tabulate(rows, headers=header, stralign='left', tablefmt='rounded_outline', colalign=('left', 'right', 'right', 'right', 'right', 'right', 'right'))}```", delete_after=timeout)
    if rows_2:
        await interaction.channel.send( \
            f"```{tabulate.tabulate(rows_2, headers=header, stralign='left', tablefmt='rounded_outline', colalign=('left', 'right', 'right', 'right', 'right', 'right', 'right'))}```", delete_after=timeout)
    if rows_3:
        await interaction.channel.send( \
            f"```{tabulate.tabulate(rows_3, headers=header, stralign='left', tablefmt='rounded_outline', colalign=('left', 'right', 'right', 'right', 'right', 'right', 'right'))}```", delete_after=timeout)
    if rows_4:
        await interaction.channel.send( \
            f"```{tabulate.tabulate(rows_4, headers=header, stralign='left', tablefmt='rounded_outline', colalign=('left', 'right', 'right', 'right', 'right', 'right', 'right'))}```", delete_after=timeout)
'''
Example of stats.json:
{
    "__hackerman": {
        "wins": 2,
        "losses": 1,
        "matches": 3,
        "winrate": 0.667,
        "points": 1,
        "rank": 1
    },
    "lackosia": {
        "wins": 0,
        "losses": 1,
        "matches": 1,
        "winrate": 0.0,
        "points": -1,
        "rank": 2
    },
    "roggan.": {
        "wins": 0,
        "losses": 1,
        "matches": 1,
        "winrate": 0.0,
        "points": -1,
        "rank": 2
    }
}
'''
