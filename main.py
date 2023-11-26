import discord
from discord import app_commands
from os import path
from Commands.stats import stats_command
from Commands.inhouse import inhouse_command
from Commands.schedule import schedule_command


if __name__ == "__main__":

    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)
    snuslan=discord.Object(id=123169301094989825)
    wew=discord.Object(id=745215730592645221)
    list_of_guilds = [snuslan, wew]

    testing = True 

    @client.event
    async def on_ready():
        print(f"We have logged in as {client.user}")
        await tree.sync(guild=snuslan)
        await tree.sync(guild=wew)
        print("Synced commands")

    @tree.command(guilds=list_of_guilds, name="schedule",
        description="""View or join scheduled matches. date: YYYY-MM-DD time: HH:MM => Schedule new match""")
    async def schedule(interaction, date: str = "", time: str = ""):
        await schedule_command(interaction, date, time)

    @tree.command(guilds=list_of_guilds, name="inhouse", description="Prepare an inhouse match" )
    async def inhouse(interaction):
        await inhouse_command(interaction, testing)

    @tree.command(guilds=list_of_guilds, name="inhouse-stats", description="Show inhouse statistics")
    async def stats(interaction):
        await stats_command(interaction, timeout=600) 

    # Dont move this, client.run is blocking forever and needs to at the bottom of the file
    with open("token.txt", "r") as file: 
        token = file.read()
    client.run(token)