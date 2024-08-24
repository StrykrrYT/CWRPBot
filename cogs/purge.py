# Imports
import discord
import settings
import sys
from cogs.logs import Logs
from discord.ext import commands
from discord import app_commands
from settings_files import logging

# Logging Setup
logger = logging.logging.getLogger('bot')

class Purge(commands.Cog):
    def __init__(self, bot: commands.Bot):
        """
        Initialize the Purge cog.

        Args:
            bot (commands.Bot): The bot object.
        """

        self.bot = bot

                                        # ! BOT INIT ! #

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info('\033[32mPurge Cog Initialized\033[97m')

                                        # ! PURGE COMMAND ! #        
        
    @app_commands.command(name='purge', description="Purges a specified amount of messages from the current channel.")
    @app_commands.describe(amount='Amount of messages to delete')
    async def purge(self, interaction: discord.Interaction, amount: int):
        """
        Purges a specified amount of messages from the current channel.

        Args:
            amount (int): The amount of messages to delete.

        Raises:
            Exception: If an error occurs while purging messages.

        Returns:
            None
        """
        if any(role.name in settings.allowed_roles for role in interaction.user.roles) or interaction.user.guild_permissions.administrator:
            try:
                if amount == 1:
                    await interaction.response.send_message(content=f'Purged {str(amount)} message', ephemeral=True)
                else:
                    await interaction.response.send_message(content=f'Purged {str(amount)} messages', ephemeral=True)
                messages = []
                async for message in interaction.channel.history(limit=amount):
                    messages.append(message)
                await interaction.channel.purge(limit=amount, bulk=True)
            except Exception as e:
                logger.error(f'Error: {e} at line: {sys.exc_info()[-1].tb_lineno}')
        else:
            await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True, delete_after=3)
            await Logs(self.bot).log(interaction, "purge")
        
                                        # ! BOT SETUP ! #
async def setup(bot):
    """
    Add the Purge cog to the bot.

    Args:
        bot (commands.Bot): The bot object.
    """
    await bot.add_cog(Purge(bot), guilds=[discord.Object(id=guild_id) for guild_id in settings.GUILD_IDS])

                                        # ! INITIALIZATION ! #
