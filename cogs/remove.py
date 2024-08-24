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

class Remove(commands.Cog):
    def __init__(self, bot: commands.Bot):
        """
        Initialize the Remove cog.

        Args:
            bot (commands.Bot): The bot object.
        """
        self.bot = bot
    
                                        # ! BOT INIT ! #

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info('\033[32mRemove Cog Initialized\033[97m')

                                        # ! REMOVE COMMAND ! #

    @app_commands.command(name='remove', description=f'Remove {settings.communityBot} from all servers and clean up all utilities')
    async def remove(self, interaction: discord.Interaction):
        """
        Remove {settings.communityBot} from all servers and clean up all utilities.

        Args:
            interaction (discord.Interaction): The interaction object.

        Raises:
            Exception: If an error occurs while removing commands and cleaning up utilities.

        Returns:
            None
        """
        if interaction.user.id == 295430975368986624:
            try:
                await interaction.response.send_message('Removed commands, cleaned up all utilities, and left all servers.', ephemeral=True)
                for guild in self.bot.guilds:
                    for channel in guild.text_channels:
                        await channel.purge(limit=None, check=lambda m: m.author == self.bot.user, bulk=True)
                    if guild != interaction.guild:
                        await guild.leave()
                await interaction.guild.leave()
            except Exception as e:
                logger.error(f'Error: {e} at line: {sys.exc_info()[-1].tb_lineno}')
        else:
            await interaction.response.send_message("You do not have permission to execute this command.", ephemeral=True)
            await Logs(self.bot).log(interaction, 'remove')

                                        # ! BOT SETUP ! #
async def setup(bot):
    """
    Add the Remove cog to the bot.

    Args:
        bot (commands.Bot): The bot to add the cog to.
    """
    await bot.add_cog(Remove(bot), guilds=[discord.Object(id=guild_id) for guild_id in settings.GUILD_IDS])

                                        # ! INITIALIZATION ! #