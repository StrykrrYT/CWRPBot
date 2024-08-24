# Imports
import discord
import pytz
import settings
import sys
from cogs.logs import Logs
from datetime import datetime, timedelta
from discord.ext import commands
from discord import app_commands
from mongoengine import *
from settings_files import logging

# Logging Setup
logger = logging.logging.getLogger("bot")

class Kick(commands.Cog):
    def __init__(self, bot: commands.Bot):
        """
        Initialize the Ban cog.

        Args:
            bot (commands.Bot): The bot object.
        """
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
      logger.info('\033[32mKick Cog Initialized\033[97m')

    @app_commands.command(name='kick', description='Kick a member from the server.')
    @app_commands.describe(member='The member you want to ban.', kick_reason='The reason for the kick.')
    async def kick(self, interaction: discord.Interaction, member: discord.Member, kick_reason: str):
        """
        Kick a member from the server.

        Args:
            interaction (discord.Interaction): The interaction object.
            member (discord.Member): The member to kick.
            kick_reason (str): The reason for the kick.

        Returns:
            None
        """
        if any(role.name in settings.allowed_roles for role in interaction.user.roles) or interaction.user.guild_permissions.administrator:  
          try:
              await self.log_kick(interaction, member, kick_reason)
              await self.kick_member(interaction, member, kick_reason)
          except Exception as e:
              logger.error(f'Error: {e} at line: {sys.exc_info()[-1].tb_lineno}')
        else:
            await interaction.response.send_message("You do not have permission to execute this command.", ephemeral=True, delete_after=3)
            await Logs(self.bot).log(interaction, "Kick")

    async def kick_member(self, interaction: discord.Interaction, member: discord.Member, kick_reason: str):
        """
        Kick a member.

        Args:
            interaction (discord.Interaction): The interaction object.
            member (discord.Member): The member to kick.
            Kick_reason (str): The reason for the kick.

        Returns:
            None
        """
        await interaction.guild.kick(member, reason=f'{kick_reason}. Kicked by: {interaction.user.name}.')
        await interaction.response.send_message(f'{member.name} Was kicked for the reason: {kick_reason}.', ephemeral=True)

    async def log_kick(self, interaction: discord.Interaction, member: discord.Member, ban_reason: str):
        """
        Log the kick.

        Args:
            interaction (discord.Interaction): The interaction object.
            member (discord.Member): The member to kick.
            kick_reason (str): The reason for the kick.

        Returns:
            None
        """
        db = get_db()
        KickLogs = db.KickLogs
        user_kick_count = KickLogs.count_documents({"Member_ID": int(member.id)}) + 1

        KickLogs.insert_one({
            "Member_ID": int(member.id),
            "Member_Name": str(member.name),
            "Reason": str(ban_reason),
            "Kick_Date": str(pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('America/New_York')).strftime('%B, %dth %Y: %I:%M %p (%H:%M:%S) %Z')),
            "User_Kicks": int(user_kick_count),
            "Server": str(interaction.guild.name),
            "Kicked_By": str(interaction.user.display_name)
        })

async def setup(bot):
    """
    Add the Ban cog to the bot.

    Args:
        bot: The bot to add the cog to.
    """
    await bot.add_cog(Kick(bot), guilds=[discord.Object(id=guild_id) for guild_id in settings.GUILD_IDS])