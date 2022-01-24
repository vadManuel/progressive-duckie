from typing import Union

from db import get_channels, remove_channel, upsert_channel
from discord import Embed, TextChannel
from models import Channel

from .audit import audit

hex_color = 0xffbd00


async def config_add(ctx, command=None, channel_name=None):
    server_id = str(ctx.guild.id)
    lower_command = command.lower()

    text_channels = [channel for channel in ctx.guild.channels if isinstance(
        channel, TextChannel)]
    lower_channel_name = channel_name.lower()

    existing_channels = get_channels(server_id=server_id)

    # look for channel names similar to the one provided
    similar_channels = list(filter(
        lambda channel: lower_channel_name in channel.name.lower(), text_channels))

    # looking for exact channel matches
    exact_channels = list(filter(
        lambda channel: lower_channel_name == channel.name.lower(), text_channels))

    # return bad channel if no channel found
    if len(similar_channels) == 0:
        await ctx.send('No channel found with that name.')
        return

    # unique channel name found
    if len(similar_channels) == 1 or len(exact_channels) == 1:
        focused_channel = exact_channels[0] if len(
            exact_channels) == 1 else similar_channels[0]

        focused_channel_id = str(focused_channel.id)

        if command == 'audit':
            raw_audit_channel: Union[Channel, None] = next(
                (channel for channel in existing_channels if channel.type == command), None)

            if raw_audit_channel:
                audit_channel = next(channel for channel in text_channels if str(
                    channel.id) == raw_audit_channel.rowid)

                if audit_channel:
                    await ctx.send(f'There can only exist one `{command}` channel. The current channel is {audit_channel.mention}.')
                    return

        # find first instance of existing_channels that matches focused_channel
        existing_channel: Union[Channel, None] = next(
            (channel for channel in existing_channels if channel.rowid == focused_channel_id), None)

        if existing_channel:
            await ctx.send(f'Channel {focused_channel.mention} already exists as type `{existing_channel.type}`.')
            return

        upsert_channel(server_id=server_id,
                       channel_id=focused_channel_id, type=lower_command)

        await ctx.send(f'Added {focused_channel.mention} as type `{lower_command}`.')
        await audit(ctx, message=f'{ctx.author.mention} added {focused_channel.mention} to `{lower_command}`.')

        return

    # could not find a unique channel name
    embed = Embed(color=hex_color)

    value = 'The following channels have similar names to the one you provided:\n\n'
    value += '\n'.join([f'**{i+1}** {channel.name}' for i,
                        channel in enumerate(similar_channels)])

    embed.add_field(name='Be more specific', value=value, inline=False)

    await ctx.send(embed=embed)


async def config_remove(ctx, command=None, channel_name=None):
    lower_command = command.lower()

    text_channels = [channel for channel in ctx.guild.channels if isinstance(
        channel, TextChannel)]

    lower_channel_name = channel_name.lower()

    channels = get_channels(server_id=ctx.guild.id)
    # look for channel names similar to the one provided
    similar_channels = list(filter(
        lambda channel:
        lower_channel_name in channel.name.lower() and
        any([existing_channel.rowid != str(channel.id)
             for existing_channel in channels]),
        text_channels)
    )
    exact_channels = list(filter(
        lambda channel:
        lower_channel_name == channel.name.lower(),
        text_channels)
    )

    print(similar_channels)
    print(exact_channels)

    # return bad channel if no channel found
    if len(similar_channels) == 0:
        await ctx.send('No channel found with that name.')
        return

    # unique channel name found
    if len(similar_channels) == 1 or len(exact_channels) == 1:
        focused_channel = exact_channels[0] if len(
            exact_channels) == 1 else similar_channels[0]

        existing_channel: Union[Channel, None] = None

        for channel in channels:
            if channel.rowid == str(focused_channel.id):
                existing_channel = channel
                break

        if not existing_channel:
            await ctx.send(f'Channel does not exist.')
            return

        remove_channel(focused_channel.id)
        await ctx.send(f'Removed {focused_channel.mention} from `{lower_command}`.')

        await audit(ctx, message=f'{ctx.author.mention} removed {focused_channel.mention} from `{lower_command}`.')
