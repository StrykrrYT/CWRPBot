                                        # ! INITIALIZATION ! #

                                        # ! IMPORTS ! #
import asyncio
import config
import discord
import os
import pytz
import re
import sys
import sqlite3
from cogs.logs import Logs
from datetime import datetime, timedelta
from discord.ext import commands
from discord import app_commands


                                        # ! COG CREATION ! #

class Unbans(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        os.chdir('C:/Users/terry/Desktop/CWRPBot/')
                                        # ! BOT INIT ! #

    @commands.Cog.listener()
    async def on_ready(self):
        print('\033[32mUnbans Cog Initialized')

                                        # ! UNBAN LOGS COMMAND ! #


                                        # ! DATABASE CONNECTION ! #                           

try:
    config.cursor.execute('''
    CREATE TABLE IF NOT EXISTS unban_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER,
    member_name TEXT,
    reason TEXT,
    unbanDate TEXT,
    unbannedBy TEXT
)
''')
    config.conn.commit()
except sqlite3.Error as e:
    print(f'Error Connecting To Table unban_logs: {e}')

                                        # ! BOT SETUP ! #

async def setup(bot):
    await bot.add_cog(Unbans(bot), guilds=[discord.Object(id=759962448491970561),discord.Object(id=759960762474823701)])

                                        # ! INITIALIZATION ! #