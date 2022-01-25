
import re
from datetime import datetime
from random import choice
from typing import Union

from db import get_all, get_channels, upsert
from models import Channel, Message

from bot import audit
from utils import ordinal_number


async def on_thread_message(message):
    delim = 'log'
    match = re.match(r'^%s\n' % delim, message.content, re.IGNORECASE)
    
    if not match:
        return

    content = '\n'.join(message.content.split('\n')[1:])
    
    print(content)

async def on_textchannel_message(message):
    header = message.content.split('\n')[0]

    # if match:
    rowid = str(message.id)
    author_id = str(message.author.id)
    server_id = str(message.author.guild.id)
    channel_id = str(message.channel.id)

    # get channels
    existing_channels = get_channels(server_id=server_id)
    existing_channel: Union[Channel, None] = next(
        (channel for channel in existing_channels if channel.rowid == channel_id), None)

    if not existing_channel:
        return

    channel_type = existing_channel.type

    # await message.channel.trigger_typing()

    m = Message(
        rowid=rowid,
        server_id=server_id,
        channel_id=channel_id,
        author_id=author_id,
        content=message.content
    )

    entry = upsert(m, table_name=channel_type)
    entries = get_all(author_id, table_name=channel_type)

    # timestamp to datetime and then to month day
    timestamp = datetime.strptime(entry.timestamp, '%Y-%m-%d %H:%M:%S')
    # preventing 0 padding of day
    date = timestamp.strftime('%b') + f' {timestamp.day}'

    # formatted channel type
    formatted_channel_type = channel_type.title()[:-1]

    # thread_name = f'{message.author.name} - {formatted_channel_type} {len(entries)} - {date}'
    thread_name = f'{header} - {date}'

    thread = await message.create_thread(name=thread_name)

    # add current user to thread
    await thread.add_user(message.author)
    
    # ping the author
    await thread.send(f'Welcome to your thread, {message.author.name}! You are on your {ordinal_number(len(entries))} entry.')
    # await thread.send(f'Welcome to your thread, {message.author.name}!')

    # randomily pick an emoji
    emoji = choice(['🎺', '👀', '🧠', '😎', '💫', '🤙', '💪'])
    await message.add_reaction(emoji)

    await audit(message, f'{message.author.mention} posted a new {channel_type[:-1]} at {message.jump_url}.')
