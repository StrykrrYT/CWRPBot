                                        # ! INITIALIZATION ! #

                                        # ! IMPORTS ! #

import discord
import settings
from cogs.logs import Logs
from discord.ext import commands
from discord import app_commands
from settings_files import logging

logger = logging.logging.getLogger('bot')

                                        # ! COG CREATION ! #

class Prefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

                                        # ! BOT INIT ! #

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info('\033[32mPrefix Cog Initialized\033[97m')

                                        # ! PREFIX COMMAND ! #       

    @app_commands.command(name='prefix',description=f'Assign a new prefix to {settings.communityBot}')
    @app_commands.describe(prefix='The new prefix for {settings.communityBot}')
    async def prefix(self, interaction: discord.Interaction, prefix: str):
        if any(role.name in settings.allowed_roles for role in interaction.user.roles) or interaction.user.guild_permissions.administrator:
            try:
                await self.bot.tree.sync()
                await commands.bot_Prefix(prefix)
                await interaction.response.send_message(f'Prefix changed to {prefix}', ephemeral=True)
            except Exception as e:
                logger.error(e)
                await interaction.response.send_message(f'Error: {e}', ephemeral=True)
        else:
            await interaction.response.send_message('You do not have permission to execute this command.', ephemeral=True)
            await Logs(self.bot).log(interaction, 'prefix')

                                        # ! BOT SETUP ! #

async def setup(bot):
    await bot.add_cog(Prefix(bot), guilds=[discord.Object(id=759962448491970561),discord.Object(id=759960762474823701)])

                                        # ! INITIALIZATION ! #