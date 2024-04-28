import discord
from os import path
import json


class LockedMatch(discord.ui.View):
    def __init__(self, match):
        self.match = match
        super().__init__(timeout=None) 
    
    @discord.ui.button(label="Radiant", style=discord.ButtonStyle.success)
    async def winner_radiant(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.match.can_edit(interaction):
            self.match.winners=self.match.radiant
            self.match.losers=self.match.dire
            embed = interaction.message.embeds[0]
            embed.set_footer(text="This will update stats, please confirm")
            embed.set_footer(text=f"RADIANT WON, please confirm")
            await interaction.response.edit_message(
                embed=embed,
                view=Confirm(self.match)
            )
        else:
            await interaction.response.send_message(f"{interaction.user.name} is not allowed to do this", delete_after=5)

    @discord.ui.button(label="Dire", style=discord.ButtonStyle.success)
    async def winner_dire(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.match.can_edit(interaction):
            self.match.winners=self.match.dire
            self.match.losers=self.match.radiant
            embed = interaction.message.embeds[0]
            embed.set_footer(text=f"DIRE WON, please confirm")
            await interaction.response.edit_message(
                embed=embed,
                view=Confirm(self.match)
            )
        else:
            await interaction.response.send_message(f"{interaction.user.name} is not allowed to do this", delete_after=5)

    @discord.ui.button(label="Cancel Match", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.match.can_edit(interaction):
            await interaction.response.edit_message(
                embed=interaction.message.embeds[0].set_footer(text="This will cancel the match, please confirm"),
                view=ConfirmCancel(self.match)
            )
        else:
            await interaction.response.send_message(f"{interaction.user.name} is not allowed to do this", delete_after=5)


class Confirm(discord.ui.View):
    def __init__(self, match):
        self.match=match
        super().__init__(timeout=None)

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        submit_match_result(guild_id=interaction.guild_id, winners=self.match.winners, losers=self.match.losers)
        await interaction.response.edit_message(
            embed=discord.Embed(
                color=discord.Color.dark_red(),
                title="Congratulations!",
                description=", ".join([p for p in self.match.winners])
            ),
            delete_after=10,
            view=None
        )
        await self.match.radiant_channel.delete()
        await self.match.dire_channel.delete()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
       await interaction.response.edit_message(
           embed=interaction.message.embeds[0].set_footer(text="Who won?"),
           view=LockedMatch(self.match)
       ) 


class ConfirmCancel(discord.ui.View):
    def __init__(self, match):
        self.match=match
        super().__init__(timeout=None)

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.match.cancel(interaction)
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            embed=interaction.message.embeds[0].set_footer(text="Who won?"),
            view=LockedMatch(self.match)
        )

# Update stats in "guild_id.json", unique file for each guild
def submit_match_result(*, guild_id, winners, losers):
    stats = {}
    if path.exists(f"{guild_id}.json"):
        with open(f"{guild_id}.json", "r") as file: 
            stats_json = "\n".join(file.readlines())
        stats = json.loads(stats_json)

    for player in winners:
        if player not in stats: 
            stats[player] = {"wins": 0, "losses": 0, "matches": 0, "winrate": 0, "points": 0, "rank": 0}
        stats[player]["wins"] += 1
        stats[player]["points"] += 1
        stats[player]["matches"] += 1
        stats[player]["winrate"] = round(stats[player]["wins"] / stats[player]["matches"], 2)

    for player in losers:
        if player not in stats: 
            stats[player] = {"wins": 0, "losses": 0, "matches": 0, "winrate": 0, "points": 0, "rank": 0}
        stats[player]["losses"] += 1
        stats[player]["points"] -= 1
        stats[player]["matches"] += 1
        stats[player]["winrate"] = round(stats[player]["wins"] / stats[player]["matches"], 2)

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
