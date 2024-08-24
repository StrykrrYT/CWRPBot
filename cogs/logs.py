# Imports
import discord
import pytz
import settings
import sys
from discord.ext import commands
from datetime import datetime
from settings_files import logging

# Logging Setup
logger = logging.logging.getLogger("bot")

class Logs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        """
        Initialize the Logs cog.

        Args:
            bot (commands.Bot): The bot object.
        """

        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info('\033[32mLogs Cog Initialized\033[97m')
    async def log(self, interaction: discord.Interaction, command_name: str) -> None:
        """
        Log the command execution.

        Args:
            interaction (discord.Interaction): The interaction object.
            command_name (str): The name of the command to log.

        Returns:
            None
        """

        try:
          embed = await self.create_log_embed(interaction, command_name)
          await self.send_log_message(interaction, embed)
        except Exception as e:
            logger.error(f'Error: {e} at line: {sys.exc_info()[-1].tb_lineno}')

    async def create_log_embed(self, interaction: discord.Interaction, command_name: str) -> discord.Embed:
        """
        Create a log embed from the interaction and command name.

        Args:
            interaction (discord.Interaction): The interaction object.
            command_name (str): The name of the command to log.

        Returns:
            discord.Embed: The log embed.
        """
        timestamp = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('America/New_York')).strftime('%B %dth %Y: %I:%M %p (%H:%M:%S %Z)')
        embed = discord.Embed(title="Command Execution Log", color=0xff0000, timestamp=datetime.utcnow())
        embed.add_field(name="Command Executed", value=command_name, inline=False)
        embed.add_field(name="Time Of Execution", value=pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('America/New_York')).strftime('%B, %dth %Y: %I:%M %p (%H:%M:%S) %Z'), inline=True)
        embed.add_field(name="Date of Arrival", value=interaction.user.joined_at.astimezone(pytz.timezone('America/New_York')).strftime('%B, %dth %Y: %I:%M %p (%H:%M:%S) %Z'), inline=True)
        embed.add_field(name="", value="", inline=False)
        embed.add_field(name="User Information", value="\u200b", inline=False)
        embed.add_field(name="", value="", inline=False)
        embed.add_field(name="Username", value=f"{interaction.user.display_name}", inline=True)
        embed.add_field(name="User ID", value=f"{interaction.user.id}", inline=True)
        embed.add_field(name="Highest Role", value=f"{interaction.user.top_role.name}" if interaction.user.top_role else "None", inline=True)
        embed.add_field(name="", value="", inline=False)
        embed.add_field(name="Community Servers",value="",inline=False)
        embed.add_field(name="", value="", inline=False)
        inline = len(self.bot.guilds) > 1
        for guild in self.bot.guilds:
          member = await guild.fetch_member(interaction.user.id)
          highest_role = member.top_role.name if member.top_role else "None"
          join_date = member.joined_at.astimezone(pytz.timezone('America/New_York')).strftime('%B, %dth %Y: %I:%M %p (%H:%M:%S) %Z')
          if inline:
              embed.add_field(name="", value="", inline=False)
              embed.add_field(name=guild.name, value="", inline=False)
              embed.add_field(name="", value="", inline=False)
              embed.add_field(name="Highest Role", value=highest_role, inline=True)
              embed.add_field(name="Date of Arrival", value=join_date, inline=True)
          else:
              embed.add_field(name="", value="", inline=False)
              embed.add_field(name=guild.name, inline=False)
              embed.add_field(name="", value="", inline=False)
              embed.add_field(name="Highest Role", value=highest_role, inline=False)
              embed.add_field(name="Date of Arrival", value=join_date, inline=False)
        embed.set_author(name=settings.communityBot, icon_url=settings.communityBotLogo)
        embed.set_thumbnail(url=settings.communityBotLogo)
        embed.set_footer(text=settings.communityBot, icon_url=settings.communityBotLogo)
        

    async def send_log_message(self, interaction: discord.Interaction, embed: discord.Embed) -> None:
        """
        Send a log message to the guilds specified in the GUILD_IDS list.

        Args:
            embed (discord.Embed): The embed to send.

        Returns:
            None
        """
        found_log_channel = False
        for guild in self.bot.guilds:
          member = await interaction.guild.fetch_member(interaction.user.id)
          log_channel = discord.utils.get(guild.channels, name='log-channel')
          if log_channel:
              await log_channel.send(embed=embed)
              found_log_channel = True
        if not found_log_channel:
          main_guild = discord.utils.get(self.bot.guilds, id=1256747105326989323)
          main_log_channel = discord.utils.get(main_guild.channels, name='log-channel')
          if main_log_channel:
              await main_log_channel.send(embed=embed)
          else:
              await interaction.response.send_message("Log channel not found. Unable to log command execution.", ephemeral=True)
              print("Log channel not found. Logging to console:")
              print(embed.to_dict())
                                        # ! BOT SETUP ! #

async def setup(bot):
    """
    Add the Logs cog to the bot.

    Args:
        bot (commands.Bot): The bot to add the cog to.
    """
    await bot.add_cog(Logs(bot),  guilds=[discord.Object(id=guild_id) for guild_id in settings.GUILD_IDS])

                                        # ! INITIALIZATION ! #