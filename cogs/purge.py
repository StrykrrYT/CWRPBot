                                        # ! INITIALIZATION ! #

                                        # ! IMPORTS ! #

import discord
import config
from discord.ext import commands
from discord import app_commands
from cogs.logs import Logs

                                        # ! COG CREATION ! #

class Purge(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

                                        # ! BOT INIT ! #

    @commands.Cog.listener()
    async def on_ready(self):
        print('\033[32mPurge Cog Initialized')

                                        # ! PURGE COMMAND ! #        
        
    @app_commands.command(name='purge', description="Purges a specified amount of messages from the current channel.")
    @app_commands.describe(amount='Amount of messages to delete')
    async def purge(self, interaction: discord.Interaction, amount: int):
        if any(role.name in config.allowed_roles for role in interaction.user.roles) or interaction.user.guild_permissions.administrator:
            try:
                if amount == 1:
                    await interaction.response.send_message(content=f'Purged {str(amount)} message', ephemeral=True)
                    await interaction.channel.purge(limit=amount)
                else:
                    await interaction.response.send_message(content=f'Purged {str(amount)} messages', ephemeral=True)
                    await interaction.channel.purge(limit=amount)
            except Exception as e:
                await interaction.response.send_message(content=f'Error: {e}', ephemeral=True)
                return
        else:
            await interaction.response.send_message(content=f"You don't have permission to manage messages in this channel.", ephemeral=True)
            await Logs(self.bot).log(interaction, "purge")
            return
        
                                        # ! BOT SETUP ! #
async def setup(bot):
    await bot.add_cog(Purge(bot), guilds=[discord.Object(id=759962448491970561),discord.Object(id=759960762474823701)])

                                        # ! INITIALIZATION ! #
