import sqlite3
import datetime

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
            CREATE TABLE IF NOT EXISTS match_queue (
                datetime TEXT,
                player TEXT,
                timestamp TEXT,
                FOREIGN KEY (datetime) REFERENCES scheduled_matches(datetime)
            )
        """) 
        self.conn.commit()
    
    def schedule_match(self, datetime_string):
        self.c.execute("INSERT INTO scheduled_matches VALUES (?)", (datetime_string,))
        self.conn.commit()
    
    def get_scheduled_matches(self):
        self.c.execute("SELECT * FROM scheduled_matches")
        return [match[0] for match in self.c.fetchall()]
    
    def get_players_signed_up(self, datetime_string):
        self.c.execute("SELECT * FROM match_player_signups WHERE datetime = ?", (datetime_string,))
        return [x[1] for x in self.c.fetchall()]
    
    def sign_up(self, datetime_string, player):
        self.c.execute(f"INSERT INTO match_player_signups VALUES (?, ?)", (datetime_string, player))
        self.conn.commit()
        return self.get_players_signed_up(datetime_string)
    
    def sign_down(self, datetime_string, player):
        self.c.execute(f"DELETE FROM match_player_signups WHERE datetime = ? AND player = ?", (datetime_string, player))
        self.conn.commit()
        return self.get_players_signed_up(datetime_string)

    def add_to_queue(self, datetime_string, player):
        self.c.execute(f"INSERT INTO match_queue VALUES (?, ?, ?)", (datetime_string, player, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.conn.commit()
        return self.get_queue(datetime_string)

    def pop_from_queue(self, datetime_string): 
        player = self.c.execute(f"SELECT player FROM match_queue WHERE datetime = ? AND timestamp = (SELECT MIN(timestamp) FROM match_queue WHERE datetime = ?)", (datetime_string, datetime_string)).fetchone()[0]
        self.c.execute(f"DELETE FROM match_queue WHERE datetime = ? AND timestamp = (SELECT MIN(timestamp) FROM match_queue WHERE datetime = ?)", (datetime_string, datetime_string))
        self.conn.commit()
        return player


    def get_queue(self, datetime_string):
        self.c.execute("SELECT * FROM match_queue WHERE datetime = ?", (datetime_string,))
        return [x[1] for x in self.c.fetchall()]