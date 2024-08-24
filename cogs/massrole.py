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

class Massrole(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info('\033[32mMassrole Cog Initialized\033[97m')

    @app_commands.command(name='massrole', description='Add a role to all members of a server.')
    @app_commands.describe(member='The member you want to add the role to.', role='The role you want to add to the member.')
    async def massrole(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        """
        Add a role to all members of a server.

        Parameters:
        member (discord.Member): The member you want to add the role to.
        role (discord.Role): The role you want to add to the member.

        Returns:
        None
        """
        try:
          if not self.has_permission(interaction.user, role):
              await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True, delete_after=3)
              await Logs(self.bot).log(interaction, 'Massname')
              return
          result = await self.add_or_remove_role(member, role)
          if result:
              await interaction.response.send_message(f'Added {role.name} to all servers.', ephemeral=True, delete_after=5)
          else:
              await interaction.response.send_message(f'Removed {role.name} from all servers.', ephemeral=True, delete_after=5)
        except Exception as e:
                logger.error(f'Error: {e} at line: {sys.exc_info()[-1].tb_lineno}')

    def has_permission(self, user: discord.Member, role: discord.Role) -> bool:
        # Check if user has the required role or is an administrator
        """
        Check if user has the required role or is an administrator

        Parameters:
        user (discord.Member): The user to check.
        role (discord.Role): The role to check for.

        Returns:
        bool: True if the user has the required role or is an administrator, False otherwise.
        """
        return any(role.name in settings.allowed_roles for role in user.roles) or user.guild_permissions.administrator

    async def add_or_remove_role(self, member: discord.Member, role: discord.Role) -> bool:
        """
        Add or remove role from all servers.

        Parameters:
        member (discord.Member): The member you want to add the role to.
        role (discord.Role): The role you want to add to the member.

        Returns:
        bool: True if the role was added, False if the role was removed.
        """
        for guild in self.bot.guilds:
            new_role = discord.utils.get(guild.roles, name=role.name)
            guild_member = guild.get_member(member.id)
            if new_role and guild_member:
                if new_role in guild_member.roles:
                    await guild_member.remove_roles(new_role)
                    return False
                else:
                    await guild_member.add_roles(new_role)
                    return True
        return False
    
async def setup(bot):
    """
    Add the Massrole cog to the bot.

    Args:
        bot: The bot to add the cog to.
    """
    await bot.add_cog(Massrole(bot), guilds=[discord.Object(id=guild_id) for guild_id in settings.GUILD_IDS])