                                        # ! INITIALIZATION ! #

                                        # ! IMPORTS ! #

import discord
import config
from discord.ext import commands
from discord import app_commands
from cogs.logs import Logs

                                        # ! COG CREATION ! #

class Prefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

                                        # ! BOT INIT ! #

    @commands.Cog.listener()
    async def on_ready(self):
        print('\033[32mPrefix Cog Initialized')

                                        # ! PREFIX COMMAND ! #       

    @app_commands.command(name='prefix',description=f'Assign a new prefix to {config.communityBot}')
    @app_commands.describe(prefix='The new prefix for {config.communityBot}')
    async def prefix(self, interaction: discord.Interaction, prefix: str):
        if any(role.name in config.allowed_roles for role in interaction.user.roles) or interaction.user.guild_permissions.administrator:
            try:
                await self.bot.tree.sync()
                await self.bot.tree.set_prefix(prefix)
                await interaction.response.send_message(f'Prefix changed to {prefix}', ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f'Error: {e}', ephemeral=True)
        else:
            await interaction.response.send_message('You do not have permission to execute this command.', ephemeral=True)
            await Logs(self.bot).log(interaction, 'prefix')

                                        # ! BOT SETUP ! #

async def setup(bot):
    await bot.add_cog(Prefix(bot), guilds=[discord.Object(id=759962448491970561),discord.Object(id=759960762474823701)])

                                        # ! INITIALIZATION ! #