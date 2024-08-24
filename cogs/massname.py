# Imports
import settings
import discord
import sys
from cogs.logs import Logs
from discord import app_commands
from discord.ext import commands
from settings_files import logging

# Logging Setup
logger = logging.logging.getLogger('bot')

class Massname(commands.Cog):
    def __init__(self, bot: commands.Bot):
        """
        Initialize the Ban cog.

        Args:
            bot (commands.Bot): The bot object.
        """
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info('\033[32mMassname Cog Initialized\033[97m')

    async def rename_member(self, member: discord.Member, name: str, interaction: discord.Interaction):      
        """
        Rename a member in a community server.
        
        Parameters:
        member (discord.Member): The member to rename.
        name (str): The new name for the member.
        interaction (discord.Interaction): The interaction object.
        """
        await member.edit(nick=name)

    @app_commands.command(name='massname', description='Change members name in all community servers.')
    @app_commands.describe(member='The member whose name you want to change.', name='The name you want to the members name to.')
    async def massname(self, interaction: discord.Interaction, member: discord.Member, name: str):
        """
        Change members name in all community servers.

        Parameters:
        member (discord.Member): The member whose name you want to change.
        name (str): The name you want to the members name to.

        Returns:
        None
        """
        if any(role.name in settings.allowed_roles for role in interaction.user.roles) or interaction.user.guild_permissions.administrator:
            try:
                for guild in self.bot.guilds:
                    member = guild.get_member(member.id)
                    if member:
                        await self.rename_member(member, name, interaction)
                    else:
                        await interaction.response.send_message(f'{member} is not a member of this server.', ephemeral=True, delete_after=5)
                await interaction.response.send_message(f'Renamed {member.display_name} to {name} in all servers', ephemeral=True, delete_after=5)
            except Exception as e:
                logger.error(f'Error: {e} at line: {sys.exc_info()[-1].tb_lineno}')
        else:
            await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True, delete_after=3)
            await Logs(self.bot).log(interaction, 'Massname')

async def setup(bot):
    """
    Add the Massname cog to the bot.

    Args:
        bot: The bot to add the cog to.
    """
    await bot.add_cog(Massname(bot), guilds=[discord.Object(id=guild_id) for guild_id in settings.GUILD_IDS])