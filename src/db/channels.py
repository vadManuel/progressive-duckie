import sqlite3
from contextlib import closing
from models import Channel

con = sqlite3.connect('db.db')

def upsert_channel(server_id: str, channel_id: str, type: str):
	with closing(con.cursor()) as cur:
		# upsert server
		cur.execute("insert or replace into servers values (?, datetime('now'))", (server_id,))
		# upsert channel
		cur.execute("insert or replace into channels values (?, ?, datetime('now'))", (channel_id, type))
		# upsert server_channel
		cur.execute("insert or replace into servers_channels values (?, ?, datetime('now'))", (server_id, channel_id))

		# Save (commit) the changes
		con.commit()

def get_channels(server_id: str):
	with closing(con.cursor()) as cur:
		cur.execute('''
			select
				channels.*
			from servers_channels
				left join channels on servers_channels.channel_id = channels.rowid
			where server_id = ?
			order by timestamp
		''', (server_id,))
		rows = cur.fetchall()

		return [Channel(*row) for row in rows]

def remove_channel(rowid: str):
	with closing(con.cursor()) as cur:
		# remove hannel
		cur.execute('delete from channels where rowid = ?', (rowid,))

		# Save (commit) the changes
		con.commit()