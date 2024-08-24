# Imports
import discord
import settings
from cogs.logs import Logs 
from discord.ext import commands
from discord import app_commands
from settings_files import logging

# Logging Setup
logger = logging.logging.getLogger('bot')

class Shutdown(commands.Cog):
    def __init__(self, bot: commands.Bot):
        """
        Initialize the Shutdown cog.

        Args:
            bot (commands.Bot): The bot object.
        """

        self.bot = bot

                                        # ! BOT INIT ! #

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info('\033[32mShutdown Cog Initialized\033[97m')

                                        # ! SHUTDOWN COMMAND ! #        

    @app_commands.command(name="shutdown", description='Shutdowns the bot.')
    async def shutdown(self, interaction: discord.Interaction):
        """
        Shutdowns the bot.

        Args:
            interaction (discord.Interaction): The interaction object

        Raises:
            Exception: If an error occurs while shutting down the bot

        Returns:
            None
        """
        if interaction.user.id == 295430975368986624:
            try:
                await interaction.response.send_message('Shutting down...', ephemeral=True)
                await self.bot.close()
            except Exception as e:
                await interaction.response.send_message(f'Error: {e}', ephemeral=True)
        else:
            await interaction.response.send_message('You do not have permission to shutdown this command.', ephemeral=True)
            await Logs(self.bot).log(interaction, 'shutdown')

                                        # ! BOT SETUP ! #

async def setup(bot):
    """
    Add the Shutdown cog to the bot.

    Args:
        bot (commands.Bot): The bot to add the cog to.
    """
    await bot.add_cog(Shutdown(bot), guilds=[discord.Object(id=guild_id) for guild_id in settings.GUILD_IDS])

                                        # ! INITIALIZATION ! #
