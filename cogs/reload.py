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

class Reload(commands.Cog):
    def __init__(self, bot: commands.Bot):
        """
        Initialize the Reload cog.

        Args:
            bot (commands.Bot): The bot object.
        """

        self.bot = bot
                                        # ! BOT INIT ! #

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info('\033[32mReload Cog Initialized\033[97m')


                                        # ! Reload COMMAND ! #        

    @app_commands.command(name='reload', description='reload a cog')
    async def reload(self, interaction):
        """
        Reloads all cogs in the bot. Useful for updating code without restarting the bot.

        :param interaction: The interaction object
        :return: None
        """
        
        if interaction.user.id == 295430975368986624:
            try:
                current_cog = 'Reload'
                cogs_copy = list(self.bot.cogs.keys())
                for cog in cogs_copy:
                    if cog != current_cog:
                        await self.bot.reload_extension(f'cogs.{cog.lower()}')
                        print(f'Reloaded {cog}')
                await interaction.response.send_message('Reloaded all cogs', ephemeral=True, delete_after=5)
            except Exception as e:
                logger.error(f'Error: {e} at line: {sys.exc_info()[-1].tb_lineno}')
        else:
            await interaction.response.send_message("You do not have permission to execute this command.", ephemeral=True, delete_after=3)
            await Logs(self.bot).log(interaction, "Reload")

                                        # ! BOT SETUP ! #

async def setup(bot):
    """
    Add the Reload cog to the bot.

    Args:
        bot: The bot to add the cog to.
    """
    await bot.add_cog(Reload(bot), guilds=[discord.Object(id=guild_id) for guild_id in settings.GUILD_IDS])

                                        # ! INITIALIZATION ! #
