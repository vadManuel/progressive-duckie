from threading import Thread
from typing import Union

from db import get_channels
from discord import Message, TextChannel
from models import Channel


async def audit(ctx, message=None):
    server_id = str(ctx.guild.id)

    text_channels = [channel for channel in ctx.guild.channels if isinstance(
        channel, TextChannel)]

    existing_channels = get_channels(server_id=server_id)

    raw_audit_channel: Union[Channel, None] = next(
        (channel for channel in existing_channels if channel.type == 'audit'), None)

    if raw_audit_channel:
        audit_channel = next(channel for channel in text_channels if str(
            channel.id) == raw_audit_channel.rowid)

        return await audit_channel.send(message)
    
    if isinstance(ctx, TextChannel or Thread):
        return await ctx.send('No audit channel found.', delete_after=5)

    if isinstance(ctx, Message):
        return await ctx.channel.send('No audit channel found.', delete_after=5)



