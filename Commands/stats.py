import tabulate
import json
import discord


async def stats_command(interaction, timeout):
    stats_json = ""  
    try:
        with open(f"{interaction.guild_id}.json", "r") as file: 
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
    players_ranked = sorted(stats.items(), key=lambda x: x[1]["points"], reverse=True)
    header = list(players_ranked[0][1].keys())
    header.insert(0, "name")
    rows = []
    rows_2 = []
    for i, (player, player_stats) in enumerate(players_ranked):
        player_stats["winrate"] = str(round(player_stats["winrate"], 2) * 100) + "%"
        l = list(map(str, player_stats.values()))
        print(l)
        l[3] = l[3]
        l.insert(0, player)
        if(i < 20):
            rows.append(l)
        else:
            rows_2.append(l)
    await interaction.response.send_message(f"```{tabulate.tabulate(rows, headers=header, stralign='left', numalign='left')}```", delete_after=timeout)
    if rows_2:
        await interaction.response.send_message(f"```{tabulate.tabulate(rows_2, headers=header, stralign='left', numalign='left')}```", delete_after=timeout)
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
