                                        # ! INITIALIZATION ! #

                                        # ! IMPORTS ! #
import asyncio
import config
import discord
import os
import pytz
import re
import sys
import sqlite3
from cogs.logs import Logs
from datetime import datetime, timedelta
from discord.ext import commands
from discord import app_commands


                                        # ! COG CREATION ! #

class Unban(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

                                        # ! BOT INIT ! #

    @commands.Cog.listener()
    async def on_ready(self):
        print('\033[32mUnban Cog Initialized')

                                        # ! UNBAN COMMAND ! #

    @app_commands.command(name='unban', description='Unban a member for a specified reason.')
    @app_commands.describe(member_id='The members ID you want to unban.', reason='The reason for the unban.')
    async def unban(self, interaction: discord.Interaction, member_id: str, reason: str):
        if any(role.name in config.allowed_roles for role in interaction.user.roles) or interaction.user.guild_permissions.administrator:
            try:
                member_id = int(member_id)
                member_name = ""
                config.cursor.execute("SELECT * FROM ban_logs WHERE member_id = ?", (member_id,))
                ban_info = config.cursor.fetchone()
                banned_members = interaction.guild.bans()
                async for ban_entry in banned_members:
                    if ban_entry.user.id == member_id or (ban_info and ban_info[6] > pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('America/New_York'))):
                        try:
                            await interaction.guild.unban(discord.Object(id=member_id), reason=f'Unbanned by {interaction.user.display_name}')
                            config.cursor.execute('''INSERT INTO unban_logs (member_id, member_name, reason, unbanDate, unbannedBy)VALUES (?, ?, ?, ?, ?)''', (member_id, ban_info[2], reason, pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('America/New_York')).strftime('%B, %dth %Y: %I:%M %p (%H:%M:%S) %Z'), interaction.user.display_name))
                            config.cursor.execute("UPDATE ban_logs SET unbanDate = ? WHERE member_id = ?", (pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('America/New_York')).strftime('%B, %dth %Y: %I:%M %p (%H:%M:%S) %Z'), member_id))
                            config.conn.commit()
                            await interaction.response.send_message(f'{ban_info[2]} Was unbanned by {interaction.user.display_name}. For Reason: {reason}', ephemeral=True)
                        except Exception as e:
                            await interaction.response.send_message(f'Error: {e} at line: {sys.exc_info()[-1].tb_lineno}', ephemeral=True)
                    else:
                        await interaction.response.send_message("No bans found for the specified member ID.", ephemeral=True, delete_after=5)
            except Exception as e:
                await interaction.response.send_message(f'Error: {e} at line: {sys.exc_info()[-1].tb_lineno}', ephemeral=True, delete_after=3)
        else:
            await interaction.response.send_message("You do not have permission to execute this command.", ephemeral=True, delete_after=3)
            await Logs(self.bot).log(interaction, "Unban")
                

                                        # ! BOT SETUP ! #

async def setup(bot):
    await bot.add_cog(Unban(bot), guilds=[discord.Object(id=759962448491970561),discord.Object(id=759960762474823701)])

                                        # ! INITIALIZATION ! #