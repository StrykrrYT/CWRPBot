import os 
import discord
import settings
import asyncio
from settings import *
from mongoengine import *
from discord.ext import commands
from settings_files import logging

logger = logging.logging.getLogger("bot")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
connect(MONGODB_DATABASE, host=MONGODB_HOST, username=MONGODB_USER, password=MONGODB_PASSWORD, authentication_source="admin")



async def __init__():
    logger.info('\033[32mBot Initialized\033[97m')

async def __load__():
    logger.info('\033[90mInitializing Cogs...\033[97m')
    for cog_file in settings.COGS_DIR.glob("*.py"):
            if cog_file.name != "__init__.py":
                await bot.load_extension(f"cogs.{cog_file.name[:-3]}")

                                        # ! START THE BOT ! #

async def __start__():
    await __init__()
    await __load__()
    await bot.start(settings.DISCORD_BOT_TOKEN)

                                        # ! START THE BOT ! #

asyncio.run(__start__())
