import discord
import sqlite3
from Views import ScheduledMatch


async def create_schedule_match(tree, guild):
        @tree.command(name="schedule", 
                  description="""View or join scheduled matches. date: YYYY-MM-DD time: HH:MM => Schedule new match""",
                  guild=guild)
        async def schedule_match(interaction, date: str = "", time: str = ""):
            conn = sqlite3.connect(f"./databases/{interaction.guild_id}.db")
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS scheduled_matches (datetime TEXT)")
            c.execute("CREATE TABLE IF NOT EXISTS match_player_signups (datetime TEXT, player TEXT)") 
            conn.commit()
            channel = interaction.channel
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

            c.execute(f"INSERT INTO scheduled_matches VALUES (?)", (match_datetime.strftime("%Y-%m-%d %H:%M"),))
            conn.commit()


            c.execute("SELECT * FROM scheduled_matches")
            scheduled_matches_datetimes = [match[0] for match in c.fetchall()]
            scheduled_matches = [{}]
            for idx, datetime in enumerate(scheduled_matches_datetimes):
                c.execute("SELECT * FROM match_player_signups WHERE datetime = ?", (datetime,))
                fetched = c.fetchall()
                print(f"fetched: {fetched}")
                players = [player[1] for player in fetched]
                print(f"players1: {players}")
                players0 = [player[0] for player in fetched]
                print(f"players0: {players0}")
                scheduled_matches.append({datetime: players})
                embed=discord.Embed(
                    color=discord.Color.dark_red(),
                    title=f"Match scheduled for {datetime}",
                    description="Players: \n " + "\n ".join(players))
                view=ScheduledMatch(datetime=datetime, players=players, guild_id=interaction.guild_id)
                if idx == 0:
                    await interaction.response.send_message(embed=embed, view=view)
                else:
                    await channel.send(embed=embed, view=view) 
            return