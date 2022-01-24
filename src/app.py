import platform
import random
import re
import sys
from datetime import datetime
from multiprocessing import Lock
from typing import Union

from discord import Color, Embed, Intents, TextChannel, Thread
from discord.ext import commands

from bot import audit, config_add, config_remove, dm
from config import token
from db import get_all, get_channels, upsert
from migrations import migrate
from models import Channel, Message

hex_color = 0xffbd00

# bot config
color = Color.from_rgb(r=245, g=191, b=66).value
intents = Intents().all()
bot = commands.Bot(command_prefix='.', intents=intents)

# db config
mutex = Lock()


@bot.event
async def on_ready():
    migrate()

    print('Duckie is running down the street.')


@bot.command(help='Displays information related to the current platform hosting this bot.', brief='Show information about the bot.')
async def info(ctx):
    system = platform.platform()
    python_version = sys.version.replace('\n', '')

    await ctx.send(f'**{bot.user.name} info**\n\t__Platform__: {system}\n\t__Python__: {python_version}\n\t__Prefix__: {bot.command_prefix}\n\t__Intents__: {bot.intents}')


@bot.command(help='This command is only accessible to the server owner. It runs a full restart of the bot. This will not clear the database.', brief='Restarts the bot.')
@commands.is_owner()
async def reboot(ctx):
    await ctx.bot.logout()
    await bot.run('token')


@bot.command(help='Allows for the update of goal and logs channels in the current server. This command is only accessible to admins.', brief='Updates server goal and logs configuration.', usage='<goals | logs> <add | remove | list> <channel name>')
async def config(ctx, command=None, operation=None, channel_name=None):
    if not ctx.author.guild_permissions.administrator:
        return

    commands = ['goals', 'logs', 'audit']
    operations = ['add', 'remove', 'list']

    # return bad command if not a valid command
    if command not in commands:
        await ctx.send('Invalid command.\n\tValid commands: ' + ', '.join(commands))
        return

    # return bad operation if not a valid operation
    if operation not in operations:
        await ctx.send('Invalid operation.\n\tValid operations: ' + ', '.join(operations))
        return

    if operation in ['list']:
        text_channels = [channel for channel in ctx.guild.channels if isinstance(
            channel, TextChannel)]
        existing_channels = get_channels(server_id=str(ctx.guild.id))
        existing_channels = list(filter(
            lambda existing_channel: existing_channel.type == command.lower(), existing_channels))

        embed = Embed(color=hex_color)
        added_any_channel = False

        value = ''

        for i, channel in enumerate(existing_channels):
            existing_channel: Union[TextChannel, None] = next(
                (text_channel for text_channel in text_channels if channel.rowid == str(text_channel.id)), None)

            if existing_channel:
                added_any_channel = True
                value += f'**{i+1}** {existing_channel.name}\n'

        if not added_any_channel:
            value += 'No channels'

        embed.add_field(
            name=f'List of `{command}` channels', value=value, inline=False)

        await ctx.send(embed=embed)
        return

    if operation in ['add', 'remove']:
        # return bad channel if not a valid channel
        if channel_name is None:
            await ctx.send('Must specify channel name.')
            return

        if operation == 'add':
            await config_add(ctx, command, channel_name)
            return

        if operation == 'remove':
            await config_remove(ctx, command, channel_name)
            return


@bot.event
async def on_message(message):
    # ignore messages from bots
    if message.author.bot:
        return
    # process commands
    if message.content[0] == '.':
        return await bot.process_commands(message)
    # ignore messages in threads
    if isinstance(message.channel, Thread):
        return

    delim = 'entry'
    match = re.match(r'^%s\n' % delim, message.content, re.IGNORECASE)

    if match:
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

        thread_name = f'{message.author.name} - {formatted_channel_type} {len(entries)} - {date}'

        thread = await message.create_thread(name=thread_name)

        # ping the author
        await thread.send(f'Welcome to your thread, {message.author.mention}!')

        await dm(message, message=f'{message.author.name} has started a new {channel_type} thread at {thread.mention}!')

        await thread.send(f'I\'ve alerted everyone about your new {channel_type} thread.')

        # randomily pick an emoji
        emoji = random.choice(['🎺', '👀', '🧠', '😎', '💫', '🤙', '💪'])
        await message.add_reaction(emoji)

        await audit(message, f'{message.author.mention} posted a new {channel_type[:-1]} at {message.jump_url}.')


# -------------------------

# read token from config.ini

bot.run(token)
