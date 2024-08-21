                                        # ! INITIALIZATION ! #

                                        # ! IMPORTS ! #

import discord
import config
import sys
from discord.ext import commands
from discord import app_commands
from cogs.logs import Logs 

                                        # ! COG CREATION ! #

class Reload(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

                                        # ! BOT INIT ! #

    @commands.Cog.listener()
    async def on_ready(self):
        print('\033[32mReload Cog Initialized')

                                        # ! Reload COMMAND ! #        

    @app_commands.command(name="reload", description='Reloads all cogs')
    async def reload(self, interaction: discord.Interaction):
        if interaction.user.id == 295430975368986624:
            try:
                reloaded_count = 0
                current_cog = self.__class__.__name__
                for cog_name in list(self.bot.extensions):
                    if cog_name != current_cog:
                        try:
                            self.bot.reload_extension(cog_name)
                            print(f'Reloaded {cog_name}')
                            reloaded_count += 1
                        except commands.ExtensionError as e:
                            print(f'Failed to reload {cog_name}: {e}')
                            await interaction.channel.send(f'Failed to reload {cog_name}: {e}')
                await interaction.response.send_message(f'Reloaded {reloaded_count} Cogs', ephemeral=True, delete_after=5)
            except Exception as e:
                await interaction.response.send_message(f'Error at line: {sys.exc_info()[-1].tb_lineno}', ephemeral=True, delete_after=5)

                                        # ! BOT SETUP ! #

async def setup(bot):
    await bot.add_cog(Reload(bot), guilds=[discord.Object(id=759962448491970561),discord.Object(id=759960762474823701)])

                                        # ! INITIALIZATION ! #
