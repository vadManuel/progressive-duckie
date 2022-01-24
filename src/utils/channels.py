from discord import TextChannel
from db import get_channels
from exceptions import DuplicityError

def get_existing_channel(ctx, channel = None, table_name = None):
	server_id = str(ctx.guild.id)

	try:
		if not channel:
			raise ValueError

		channel_id = int(channel[2:-1])
	except ValueError:
		raise ValueError('Must provide a channel mention.')
	
	existing_channel = ctx.guild.get_channel(int(channel_id))
	text_channels = [channel for channel in ctx.guild.channels if isinstance(channel, TextChannel)]
	
	if not existing_channel or existing_channel not in text_channels:
		raise LookupError('Channel not found.')

	existing_channels = filter(lambda channel: channel.type == table_name, get_channels(server_id=server_id))
	existing_channel_id = str(existing_channel.id)

	if any([existing_channel_id == channel.rowid for channel in existing_channels]):
		# raise duplicate channel exception
		raise DuplicityError(f'Channel already exists as type `{table_name}`.')
	
	return existing_channel