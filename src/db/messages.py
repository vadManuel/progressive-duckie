import sqlite3
from contextlib import closing
from models import Message

con = sqlite3.connect('db.db')

def upsert(message: Message, table_name: str):
	with closing(con.cursor()) as cur:
		# upsert author
		cur.execute("insert or replace into authors values (?, datetime('now'))", (message.author_id,))

		# Upsert message
		cur.execute("insert or replace into %s values (?, ?, ?, ?, datetime('now'))" % table_name, (
			message.rowid,
			message.channel_id,
			message.author_id,
			message.content
		))

		# Save (commit) the changes
		con.commit()

		# return insert row
		return get(message.rowid, table_name)

def remove(rowid: str, table_name: str):
	with closing(con.cursor()) as cur:
		# remove message
		cur.execute('delete from %s where rowid = ?' % table_name, (rowid,))

		# Save (commit) the changes
		con.commit()

def __make_message_query(table_name: str, extra_clause: str):
	query = f'''
		select
			{table_name}.rowid as rowid,
			servers.rowid as server_id,
			channels.rowid as channel_id,
			authors.rowid as author_id,
			{table_name}.content as content,
			{table_name}.timestamp as timestamp
		from {table_name}
			left join servers_channels using (channel_id)
				left join servers on servers_channels.server_id = servers.rowid
				left join channels on servers_channels.channel_id = channels.rowid
			left join authors on {table_name}.author_id = authors.rowid
		{extra_clause}
	'''
	
	return query

def get(rowid: str, table_name: str):
	with closing(con.cursor()) as cur:
		# build query string
		query = __make_message_query(
			table_name=table_name,
			extra_clause='where {table_name}.rowid = ?'.format(table_name=table_name)
		)

		# query the database
		cur.execute(query, (rowid,))

		row = cur.fetchone()

		return Message(*row)

def get_all(author_id: str, table_name: str):
	with closing(con.cursor()) as cur:
		# build query string
		query = __make_message_query(
			table_name=table_name,
			extra_clause='where {table_name}.author_id = ? order by {table_name}.timestamp'.format(table_name=table_name)
		)

		# query the database
		cur.execute(query, (author_id,))
		rows = cur.fetchall()

		return [Message(*row) for row in rows]