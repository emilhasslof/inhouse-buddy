import discord
from Views.CreateMatch import CreateMatch
from Match import Match

async def inhouse_command(interaction: discord.Interaction, testing = False):
    category = interaction.channel.category
    if category:
        radiant_channel = await category.create_voice_channel(name="Radiant")
        dire_channel = await category.create_voice_channel(name="Dire")
    else:
        radiant_channel = await interaction.guild.create_voice_channel(name="Radiant")        
        dire_channel = await interaction.guild.create_voice_channel(name="Dire")

    match = Match(radiant_channel=radiant_channel, dire_channel=dire_channel)
    embed = discord.Embed(
        color=discord.Color.dark_red(),
        description="Join your team channels, then lock the teams to start the match",
        title="Preparing match"
    )
    embed.set_thumbnail(url="https://cdn0.iconfinder.com/data/icons/sports-elements-2/24/Swords-512.png")
    await interaction.response.send_message(
        view=CreateMatch(match=match, testing=testing),
        embed=embed
    )
