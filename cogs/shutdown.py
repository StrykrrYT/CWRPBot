                                        # ! INITIALIZATION ! #

                                        # ! IMPORTS ! #

import discord
import config
from discord.ext import commands
from discord import app_commands
from cogs.logs import Logs 

                                        # ! COG CREATION ! #

class Shutdown(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

                                        # ! BOT INIT ! #

    @commands.Cog.listener()
    async def on_ready(self):
        print('\033[32mShutdown Cog Initialized')

                                        # ! SHUTDOWN COMMAND ! #        

    @app_commands.command(name="shutdown", description='Shutdowns the bot.')
    async def shutdown(self, interaction: discord.Interaction):
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
    await bot.add_cog(Shutdown(bot), guilds=[discord.Object(id=759962448491970561)])

                                        # ! INITIALIZATION ! #
