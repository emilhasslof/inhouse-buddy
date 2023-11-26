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
        l = list(map(str, player_stats.values()))
        l.insert(0, player)
        if(i < 20):
            rows.append(l)
        else:
            rows_2.append(l)
    
    await interaction.response.send_message(f"```{tabulate.tabulate(rows, header)}```", delete_after=timeout)
    if rows_2:
        await interaction.channel.send(f"```{tabulate.tabulate(rows_2, header)}```", delete_after=timeout)
