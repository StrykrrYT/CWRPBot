                                        # ! INITIALIZATION ! #

                                        # ! IMPORTS ! #

import discord
import config
from discord.ext import commands
from discord import app_commands
from cogs.logs import Logs

                                        # ! COG CREATION ! #

class Remove(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
                                        # ! BOT INIT ! #

    @commands.Cog.listener()
    async def on_ready(self):
        print('\033[32mRemove Cog Initialized')

                                        # ! REMOVE COMMAND ! #

    @app_commands.command(name='remove', description='Remove {communityBot} from all servers and clean up all utilities')
    async def remove(self, interaction: discord.Interaction):
        if interaction.user.id == 295430975368986624:
            try:
                deleted_count = 0
                async for message in interaction.channel.history(limit=100):
                    if message.author == self.bot.user:
                        await message.delete()
                        deleted_count += 1
                await interaction.response.send_message(f'Deleted {deleted_count} {config.communityBot} messages.', ephemeral=True)
                for command in list(self.bot.commands):
                    self.bot.remove_command(command.name)
                await interaction.response.send_message('Removed all bot commands.', ephemeral=True)
                for guild in self.bot.guilds:
                    try:
                        await guild.leave()
                        await interaction.response.send_message(f'Removed {config.communityBot} from all Community servers.', ephemeral=True)
                    except Exception as e:
                        await interaction.response.send_message(f'Failed to remove bot from {guild.name}: {e}', ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f'An error occurred during cleanup: {e}', ephemeral=True)
        else:
            await interaction.response.send_message('You do not have permission to execute this command.', ephemeral=True)
            await Logs(self.bot).log(interaction, 'remove')

                                        # ! BOT SETUP ! #
async def setup(bot):
    await bot.add_cog(Remove(bot), guilds=[discord.Object(id=759962448491970561),discord.Object(id=759960762474823701)])

                                        # ! INITIALIZATION ! #