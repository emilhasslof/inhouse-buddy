import discord
from discord import app_commands

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

class TestView(discord.ui.View):
    @discord.ui.button(label="Create Match")
    async def create_match(self, interaction: discord.Interaction, style=discord.ButtonStyle.green):
        pass
    

    @discord.ui.button(label="Start Match")
    async def start(self, interaction: discord.Interaction, style=discord.ButtonStyle.green):
        pass


# ----- Commands ----- 
@tree.command(name = "test", description = "testing slash commands", guild=discord.Object(id=123169301094989825)) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def test_function(interaction):
    await interaction.response.send_message("Test successful")

@tree.command(name="inhouse", description="Organize inhouse matches", guild=discord.Object(id=123169301094989825))
async def inhouse_control(interaction):
    test_view = TestView() 
    await interaction.response.send_message(
        content="This is some content for the message \nnewline here",
        view=test_view
    )


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=123169301094989825))
    print("Ready!")


with open("token.txt", "r") as file: 
    token = file.read()
client.run(token)