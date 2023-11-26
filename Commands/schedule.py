import discord
import sqlite3
from Views.ScheduledMatch import ScheduledMatch
from datetime import datetime, timedelta
from DatabaseHandler import DatabaseHandler

async def schedule_command(interaction, date: str = "", time: str = ""):
    db_handler = DatabaseHandler(interaction.guild_id)

    db_handler.create_tables()
    channel = interaction.channel

    # Create role if not already created
    inhouse_enjoyer = discord.utils.get(interaction.guild.roles, name="Inhouse enjoyer")
    if not inhouse_enjoyer:
        inhouse_enjoyer = await interaction.guild.create_role(name="Inhouse enjoyer")
    
    # Assign role to user if not already assigned
    await interaction.user.add_roles(inhouse_enjoyer)

    # Checking for command arguments
    if (date != "") ^ (time != ""):  # XOR
        await interaction.response.send_message(
            embed=discord.Embed(
                color=discord.Color.dark_red(),
                title="Error",
                description="Please specify both date and time"
            ),
            delete_after=30,
            ephemeral=True
        )
        return
    elif date and time:
        try:
            match_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            db_handler.schedule_match(match_datetime.strftime("%Y-%m-%d %H:%M"))
            # Announce match, mentioning @Inhouse enjoyers
            await interaction.response.send_message(f"<@&{inhouse_enjoyer.id}> Match scheduled for {match_datetime.strftime('%Y-%m-%d %H:%M')}! Sign up to secure your spot!")
        except ValueError:
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=discord.Color.dark_red(),
                    title="Error",
                    description="Invalid date or time format"
                ),
                delete_after=30,
                ephemeral=True
            )
            return
    

    # test mentioning
    #await interaction.response.send_message(f"<@&{inhouse_enjoyer.id}> wassup")

    # Displaying scheduled matches
    future_matches_datetimes = [s for s in db_handler.get_scheduled_matches() 
                                if datetime.strptime(s, "%Y-%m-%d %H:%M") > (datetime.now() - timedelta(hours=1))]
    if len(future_matches_datetimes) == 0:
        await interaction.response.send_message(
            embed=discord.Embed(
                color=discord.Color.dark_red(),
                title="No upcoming matches",
                description="Schedule a match with /schedule YYYY-MM-DD HH:MM"
            ),
            delete_after=30,
            ephemeral=True
        )
        return
    for idx, datetime_string in enumerate(future_matches_datetimes):
        players = db_handler.get_players_signed_up(datetime_string)
        queue = db_handler.get_queue(datetime_string)

        embed = discord.Embed(
            color=discord.Color.dark_red(),
            title=f"Match scheduled for {datetime_string}",
            description="Players: \n " + "\n ".join(players) + ("\n\nQueue: \n " + "\n ".join(queue) if queue else "")
        )
        view = ScheduledMatch(datetime_string=datetime_string, guild_id=interaction.guild_id , db_handler=db_handler)
        if not interaction.response.is_done():
            await interaction.response.send_message(embed=embed, view=view)
        else:
            await channel.send(embed=embed, view=view, delete_after=6000) 

    return