import discord
import sqlite3
from Views.ScheduledMatch import ScheduledMatch
from datetime import datetime


async def schedule_command(interaction, date: str = "", time: str = ""):
    conn = sqlite3.connect(f"./databases/{interaction.guild_id}.db")
    conn.execute("PRAGMA foreign_keys = ON")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS scheduled_matches (
            datetime TEXT PRIMARY KEY
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS match_player_signups (
            datetime TEXT,
            player TEXT,
            FOREIGN KEY (datetime) REFERENCES scheduled_matches(datetime)
        )
    """) 
    conn.commit()
    channel = interaction.channel

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
            c.execute(f"INSERT INTO scheduled_matches VALUES (?)", (match_datetime.strftime("%Y-%m-%d %H:%M"),))
            conn.commit()
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

    c.execute("SELECT * FROM scheduled_matches")
    scheduled_matches_datetimes = [match[0] for match in c.fetchall()]
    print(f"scheduled_matches_datetimes: {scheduled_matches_datetimes}")
    if len(scheduled_matches_datetimes) == 0:
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
    for idx, datetime_string in enumerate(scheduled_matches_datetimes):
        players = c.execute("SELECT player FROM match_player_signups WHERE datetime = ?", (datetime_string,)).fetchall()
        players = [player[0] for player in players] # unpack tuples

        embed=discord.Embed(
            color=discord.Color.dark_red(),
            title=f"Match scheduled for {datetime_string}",
            description="Players: \n " + "\n ".join(players))
        view=ScheduledMatch(datetime_string=datetime_string, players=players, guild_id=interaction.guild_id
                            , conn=conn, c=c)
        if idx == 0:
            await interaction.response.send_message(embed=embed, view=view, delete_after=600)
        else:
            await channel.send(embed=embed, view=view, delete_after=600) 
    return