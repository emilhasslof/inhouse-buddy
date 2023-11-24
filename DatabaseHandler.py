import sqlite3
import discord

class DatabaseHandler:
    def __init__(self, guild_id):
        self.guild_id = guild_id
        self.conn = sqlite3.connect(f"./databases/{guild_id}.db")
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.c = self.conn.cursor()

    def create_tables(self):
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS scheduled_matches (
                datetime TEXT PRIMARY KEY
            )
        """)
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS match_player_signups (
                datetime TEXT,
                player TEXT,
                FOREIGN KEY (datetime) REFERENCES scheduled_matches(datetime)
            )
        """)
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS inhouse_matches (
                datetime TEXT PRIMARY KEY,
                radiant TEXT,
                dire TEXT
            )
        """)
        self.conn.commit()
    
    def get_scheduled_matches(self):
        self.c.execute("SELECT * FROM scheduled_matches")
        return [match[0] for match in self.c.fetchall()]
    
    def get_players_signed_up(self, datetime_string):
        self.c.execute("SELECT * FROM match_player_signups WHERE datetime = ?", (datetime_string,))
        return [x[1] for x in self.c.fetchall()]

    
    def sign_up(self, datetime_string, player):
        """
        Signs up a player for a match. 

        Parameters:
        datetime_string (str): The datetime string of the match
        player (str): The name of the player to sign up

        Returns:
        list: The list of players signed up for the match
        """
        self.c.execute(f"INSERT INTO match_player_signups VALUES (?, ?)", (datetime_string, player))
        self.conn.commit()
        return self.get_players_signed_up(datetime_string) 