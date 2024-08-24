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

class Unban(commands.Cog):
  def __init__(self, bot: commands.Bot):
      """
      Initialize the Ban cog.

      Args:
          bot (commands.Bot): The bot object.
      """

      self.bot = bot
    
  @commands.Cog.listener()
  async def on_ready(self):
    logger.info('\033[32mUnban Cog Initialized\033[97m')

  @app_commands.command(name='unban', description='Unban a member for a specified reason.')
  @app_commands.describe(member_id='The members ID you want to unban.', reason='The reason for the unban.')
  async def unban(self, interaction: discord.Interaction, member_id: int, reason: str):
      """
      Unban a member for a specified reason.
  
      Args:
          interaction (discord.Interaction): The interaction object.
          member_id (int): The member ID to unban.
          reason (str): The reason for the unban.
  
      Returns:
          None
      """
      if any(role.name in settings.allowed_roles for role in interaction.user.roles) or interaction.user.guild_permissions.administrator:
        try:
            result = await self.pull_ban_info(interaction, member_id)
            ban_info = result['ban_info']
            ban_id = ban_info["_id"]
            ban_entry = result['ban_entry']
            if ban_entry is not None:
              member_id_ban_entry = ban_entry.user.id
              await self.unban_member(interaction, member_id_ban_entry, reason)
              await interaction.response.send_message(f'{ban_info[1]} Was unbanned for the reason: {reason}.', ephemeral=True)
            else:
                await interaction.channel.send(f'{member_id} Not found in guild bans, checking logs.', delete_after=5)
            unban_date = str(pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('America/New_York')).strftime('%B, %dth %Y: %I:%M %p (%H:%M:%S) %Z'))
            if ban_info is not None:
              await self.log_unban(interaction, ban_info["Member_ID"], ban_info["Member_Name"], reason, ban_info["Duration"], ban_info["Ban_Date"], unban_date, ban_info["Server"], ban_info["Banned_By"])
              await self.update_ban_log(interaction, unban_date, ban_id, member_id)
              await interaction.response.send_message(f'Logs located and updated.', ephemeral=True)
            elif ban_entry and ban_info is None:
              await interaction.response.send_message(f'{member_id} Not found in bans or ban logs.', ephemeral=True)
        except Exception as e:
            logger.error(f'Error: {e} at line: {sys.exc_info()[-1].tb_lineno}')
      else:
          await interaction.response.send_message("You do not have permission to execute this command.", ephemeral=True, delete_after=3)
          await Logs(self.bot).log(interaction, "Unban")

  async def pull_ban_info(self, interaction: discord.Interaction, member_id):
      """
      Pulls ban info from the database.
  
      Args:
          interaction (discord.Interaction): The interaction object.
          member_id (int): The member ID to pull ban info for.
  
      Returns:
          dict: A dictionary containing both ban info and ban entry.
      """
      member_id = int(member_id)  
      db = get_db()
      BanLogs = db.BanLogs
      ban_info = BanLogs.find_one({'Member_ID': member_id, 'Unban_Date': {'$gt': str(pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('America/New_York')).strftime('%B, %dth %Y: %I:%M %p (%H:%M:%S) %Z'))}})
      ban_entry = None
      if ban_info:
          # Retrieve ban_entry from Discord guild bans:  
          banned_members = interaction.guild.bans()
          async for banned_member in banned_members:
              if banned_member.user.id == member_id:
                  ban_entry = banned_member
                  break

      return {
          'ban_info': ban_info,
          'ban_entry': ban_entry
      }
  async def log_unban(self, interaction: discord.Interaction, Member_ID, Member_Name, Unban_Reason, Duration, Ban_Date, Unban_Date, Server, Banned_By):
      """
      Log the ban.
  
      Args:
          interaction (discord.Interaction): The interaction object.
          Member_ID (int): The member ID.
          Member_Name (str): The member name.
          Unban_Reason (str): The reason for the unban.
          Duration (str): The duration of the ban.
          Ban_Date (str): The date the ban was issued.
          Unban_Date (str): The date the ban was lifted.
          Server (str): The name of the server.
          Banned_By (str): The name of the user who lifted the ban.
          Ban_Logs (dict): The ban logs.
      """
      db = get_db()
      UnbanLogs = db.UnbanLogs
      UnbanLogs.insert_one({
          "Member_ID": int(Member_ID),
          "Member_Name": str(Member_Name),
          "Reason": str(Unban_Reason),
          "Duration": str(Duration),
          "Ban_Date": str(Ban_Date),
          "Unban_Date": str(Unban_Date),
          "Server": str(interaction.guild.name),
          "Banned_By": str(Banned_By),
          "Unbanned_By": str(interaction.user.display_name)
      })

  async def update_ban_log(self, interaction: discord.Interaction, unban_date, ban_id, member_id):
      """
      Update the ban log.
  
      Args:
          interaction (discord.Interaction): The interaction object.
          Unban_Date (str): The date the ban was lifted.
      """
      member_id = int(member_id)
      db = get_db()
      BanLogs = db.BanLogs
      query = {'_id': ban_id, 'Member_ID': member_id}
      newvalues = { '$set': {'Unban_Date': unban_date}}
      BanLogs.update_one(query, newvalues)
  
  async def unban_member(self, interaction: discord.Interaction, member_id_ban_entry: int, reason: str):
      """
      Unban a member.
  
      Args:
          interaction (discord.Interaction): The interaction object.
          member_id (int): The member ID to unban.
          reason (str): The reason for the unban.
  
      Returns:
          None
      """
      if member_id_ban_entry: 
        await interaction.guild.unban(discord.Object(id=member_id_ban_entry), reason=f'{reason}. Unbanned by: {interaction.user.name}')

async def setup(bot):
  """
  Add the Ban cog to the bot.

  Args:
      bot: The bot to add the cog to.
  """
  await bot.add_cog(Unban(bot), guilds=[discord.Object(id=guild_id) for guild_id in settings.GUILD_IDS])