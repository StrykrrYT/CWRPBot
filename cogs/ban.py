# Imports
import asyncio
import discord
import pytz
import re
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

class Ban(commands.Cog):
    def __init__(self, bot: commands.Bot):
        """
        Initialize the Ban cog.

        Args:
            bot (commands.Bot): The bot object.
        """
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
      logger.info('\033[32mBan Cog Initialized\033[97m')


    @app_commands.command(name='ban', description='Ban a member for a specified amount of time.')
    @app_commands.describe(member='The member you want to ban.', duration='The amount of time to ban the member', ban_reason='The reason for the ban.')
    async def ban(self, interaction: discord.Interaction, member: discord.Member, duration: str, ban_reason: str):
        """
        Ban a member for a specified amount of time.

        Args:
            interaction (discord.Interaction): The interaction object.
            member (discord.Member): The member to ban.
            duration (str): The duration of the ban.
            ban_reason (str): The reason for the ban.

        Returns:
            None
        """
        if any(role.name in settings.allowed_roles for role in interaction.user.roles) or interaction.user.guild_permissions.administrator:  
          try:
              parsed_duration = await self.parse_duration(interaction, duration)
              if parsed_duration != 'Never':
                format_ban_duration = await self.format_ban_duration(parsed_duration)
                unban_date = await self.calculate_unban_date(parsed_duration)
              else:
                  unban_date = 'Never'
                  format_ban_duration = 'Permanent'
              await self.log_ban(interaction, member, ban_reason, format_ban_duration, unban_date)
              await self.ban_member(interaction, member, ban_reason, parsed_duration, format_ban_duration)
          except Exception as e:
              logger.error(f'Error: {e} at line: {sys.exc_info()[-1].tb_lineno}')
        else:
            await interaction.response.send_message("You do not have permission to execute this command.", ephemeral=True, delete_after=3)
            await Logs(self.bot).log(interaction, "Ban")

    async def parse_duration(self, interaction: discord.Interaction, duration: str) -> timedelta:
        """
        Parse a duration string and return a timedelta object.

        Args:
            duration (str): The duration string to parse.

        Returns:
            timedelta: The parsed timedelta object.

        Raises:
            ValueError: If the duration string is invalid.
        """
        if duration.lower() == 'permanent':
            delta = 'Never'
            return delta
        duration_regex = re.match(r'^(\d+)([smhdwMy]|mo|y)$', duration)
        if not duration_regex:
            await interaction.channel.send('Invalid duration format. Please use s (seconds), m (minutes), h (hours), d (days), w (weeks), mo (months), or y (years).', delete_after=10)
        amount = int(duration_regex.group(1))
        unit = duration_regex.group(2)
        if unit == 's':
            delta = timedelta(seconds=amount)
        elif unit == 'm':
            delta = timedelta(minutes=amount)
        elif unit == 'h':
            delta = timedelta(hours=amount)
        elif unit == 'd':
            delta = timedelta(days=amount)
        elif unit == 'w':
            delta = timedelta(weeks=amount)
        elif unit == 'mo':
            delta = timedelta(days=amount * 30)
        elif unit == 'y':
            delta = timedelta(days=amount * 365)
        return delta

    async def format_ban_duration(self, parsed_duration) -> str:
        """
        Format a timedelta object as a string.

        Args:
            delta (timedelta): The timedelta object to format.

        Returns:
            str: The formatted string.
        """
        days = parsed_duration.days
        hours = parsed_duration.seconds // 3600
        minutes = (parsed_duration.seconds // 60) % 60
        seconds = parsed_duration.seconds % 60

        if days >= 365:
            amount = days // 365
            unit_str = "year" if amount == 1 else "years"
        elif days >= 30:
            amount = days // 30
            unit_str = "month" if amount == 1 else "months"
        elif days >= 7:
            weeks = days // 7
            remaining_days = days % 7
            if remaining_days == 0:
                amount = weeks
                unit_str = "week" if amount == 1 else "weeks"
            else:
                amount = f"{weeks} weeks and {remaining_days} days"
                unit_str = ""
        else:
            amount = days
            unit_str = "day" if amount == 1 else "days"

        return f'{amount} {unit_str}'

    async def calculate_unban_date(self, delta: timedelta) -> datetime:
        """
        Calculate the unban date based on the given timedelta.

        Args:
            delta (timedelta): The timedelta to add to the current date.

        Returns:
            datetime: The unban date.
        """
        if delta is None:
            return None

        return pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('America/New_York')) + delta

    async def log_ban(self, interaction: discord.Interaction, member: discord.Member, ban_reason: str, format_ban_duration: str, unban_date: datetime):
        """
        Log the ban.

        Args:
            interaction (discord.Interaction): The interaction object.
            member (discord.Member): The member to ban.
            ban_reason (str): The reason for the ban.
            delta (timedelta): The duration of the ban.
            unban_date (datetime): The unban date.

        Returns:
            None
        """
        db = get_db()
        BanLogs = db.BanLogs
        user_ban_count = BanLogs.count_documents({"Member_ID": int(member.id)}) + 1

        BanLogs.insert_one({
            "Member_ID": int(member.id),
            "Member_Name": str(member.name),
            "Reason": str(ban_reason),
            "Duration": str(format_ban_duration) if unban_date != 'Never' else 'Permanent',
            "Ban_Date": str(pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('America/New_York')).strftime('%B, %dth %Y: %I:%M %p (%H:%M:%S) %Z')),
            "Unban_Date": str(unban_date.strftime('%B, %dth %Y: %I:%M %p (%H:%M:%S) %Z')) if unban_date != 'Never' else 'Never',
            "User_Bans": int(user_ban_count),
            "Server": str(interaction.guild.name),
            "Banned_By": str(interaction.user.display_name)
        })

    async def ban_member(self, interaction: discord.Interaction, member: discord.Member, ban_reason: str, delta: timedelta, format_ban_duration: str):
        """
        Ban a member and log the ban.

        Args:
            interaction (discord.Interaction): The interaction object.
            member (discord.Member): The member to ban.
            ban_reason (str): The reason for the ban.
            delta (timedelta): The duration of the ban.

        Returns:
            None
        """
        if format_ban_duration =='Permanent':
            await interaction.guild.ban(member, reason=f'{ban_reason} (Permanent ban). Banned by: {interaction.user.name}.') 
            await interaction.response.send_message(f'{member.name} Was banned for the reason: {ban_reason}. (Permanent Ban)', ephemeral=True)
        else:
            await interaction.guild.ban(member, reason=f'{ban_reason} (Temporary Ban for: {format_ban_duration}) Banned by: {interaction.user.name}.')
            await interaction.response.send_message(f'{member.name} Was banned for the reason: {ban_reason}. (Temporary Ban for: {format_ban_duration})', ephemeral=True)
            await self.unban(interaction, member, delta)

    async def unban(self, interaction: discord.Interaction, member, delta: timedelta):
        await asyncio.sleep(delta.total_seconds())
        await interaction.guild.unban(member, reason='Temporary ban expired.')
        await interaction.channel.send(f'{member.name}' + 's temporary ban has expired.', delete_after=5)

async def setup(bot):
    """
    Add the Ban cog to the bot.

    Args:
        bot: The bot to add the cog to.
    """
    await bot.add_cog(Ban(bot), guilds=[discord.Object(id=guild_id) for guild_id in settings.GUILD_IDS])