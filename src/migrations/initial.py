from contextlib import closing
import sqlite3

con = sqlite3.connect('db.db')

def migrate():
	with closing(con.cursor()) as cur:
		try:
			# Create tables

			# authors
			cur.execute('''
				create table servers (
					rowid							text primary key not null,
					timestamp					numeric not null
				)''')
			
			# channels
			cur.execute('''
				create table channels (
					rowid							text primary key not null,
					type							text not null,
					timestamp					numeric not null
				)''')
			
			# authors
			cur.execute('''
				create table authors (
					rowid							text primary key not null,
					timestamp					numeric not null
				)''')

			# servers_channels
			cur.execute('''
				create table servers_channels (
					server_id					text not null,
					channel_id				text unique not null,
					timestamp					numeric not null,
					foreign key(server_id) references server(rowid) on delete cascade,
					foreign key(channel_id) references channel(rowid) on delete cascade
				)''')

			# goals
			cur.execute('''
				create table goals (
					rowid							text primary key not null,
					channel_id				text,
					author_id					text,
					content						text not null,
					timestamp					numeric not null,
					foreign key(channel_id) references servers_channels(channel_id),
					foreign key(author_id) references author(rowid)
				)''')
			
			# logs
			cur.execute('''
				create table logs (
					rowid							text primary key not null,
					channel_id				text,
					author_id					text not null,
					content						text not null,
					timestamp					numeric not null,
					foreign key(channel_id) references servers_channels(channel_id),
					foreign key(author_id) references author(rowid)
				)''')
			
			# Save (commit) the changes
			con.commit()
		except Exception as e:
			print(e)