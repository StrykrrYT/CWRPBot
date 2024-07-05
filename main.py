                                        # ! INITIALIZATION ! #

                                        # ! IMPORTS ! #

import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set logging level to INFO or DEBUG for more detailed output

import discord
import config
import asyncio
import os
import sqlite3
from discord import app_commands
from discord.ext import commands

                                        #! BOT BUILDING ! #

intents = discord.Intents.default()
intents.message_content = True
APPLICATION_ID = '1257444187977154651'
client = commands.Bot(command_prefix='!', intents=intents, application_id=APPLICATION_ID)

                                        # ! BOT INIT ! #

async def __init__():
    print('\033[37m------------------')
    print('\033[90mBot Initializing')
    print('\033[37m------------------')

                                        # ! LOAD ALL COGS ! #
                                        
async def __load__():
    print(f'\033[90mLoading Cogs...')
    for file in os.listdir('./cogs'):
        if file.endswith('.py'):
            await client.load_extension(f'cogs.{file[:-3]}')
    print('\033[37m------------------')

                                        # ! START THE BOT ! #

async def __start__():
    await __init__()
    await __load__()
    await client.start(config.TOKEN)
    await __sync__()

async def __sync__():
    print('\033[90mSyncing Commands...')
    print('\033[37m------------------')
    tmt = await client.tree.sync()
    if len(tmt) == 1:
        print(f'\033[32mSynced \33[33m{len(tmt)} \033[32mCommand')
    elif len(tmt) == 0:
        print(f'\33[31mSynced No Commands')
    else:
        print(f'\033[32mSynced \33[33m{len(tmt)} \033[32mCommands')

                                        # ! START THE BOT ! #

asyncio.run(__start__())

                                        # ! INITIALIZATION ! #