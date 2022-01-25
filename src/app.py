import platform
import sys
from multiprocessing import Lock

from discord import Intents, TextChannel, Thread
from discord.ext import commands

from bot import (config_add, config_list, config_remove,
                 on_textchannel_message, on_thread_message)
from bot.dm import dm
from config import token
from migrations import migrate
from db import get_channels

# bot config
intents = Intents().all()
bot = commands.Bot(command_prefix='.', intents=intents)

# prevent multiple processes from running at the same time
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
        return await ctx.send('Invalid command.\n\tValid commands: ' + ', '.join(commands))

    # return bad operation if not a valid operation
    if operation not in operations:
        return await ctx.send('Invalid operation.\n\tValid operations: ' + ', '.join(operations))

    if operation in ['list']:
        return await config_list(ctx, command, channel_name)

    if operation in ['add', 'remove']:
        # return bad channel if not a valid channel
        if channel_name is None:
            return await ctx.send('Must specify channel name.')

        if operation == 'add':
            return await config_add(ctx, command, channel_name)

        if operation == 'remove':
            return await config_remove(ctx, command, channel_name)

@bot.event
async def on_message(message):
    # ignore messages from bots
    if message.author.bot:
        return
    
    existing_channels = get_channels(server_id=message.guild.id)
    existing_channel_ids = [channel.rowid for channel in existing_channels]

    if str(message.channel.id) not in existing_channel_ids:
        return

    # delete sticker (etc) messages
    if message.content == None or message.content == '':
        # delete message
        return await message.delete()

    header = message.content.split('\n')[0].strip()

    # delete emoji title messages
    if header[0] == '<' and header[-1] == '>' or header[:len('https://')] == 'https://':
        # delete message
        return await message.delete()

    # process commands
    if message.content[0] == '.':
        return await bot.process_commands(message)
    # messages from TextChannels
    if isinstance(message.channel, TextChannel):
        return await on_textchannel_message(message)
    # messages from Threads
    if isinstance(message.channel, Thread):
        return await on_thread_message(message)

bot.run(token) # start bot
