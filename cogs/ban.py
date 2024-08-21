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

class Ban(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
                                        # ! BOT INIT ! #

    @commands.Cog.listener()
    async def on_ready(self):
        print('\033[32mBan Cog Initialized')

                                        # ! BAN COMMAND ! #

    @app_commands.command(name='ban', description='Ban a member for a specified amount of time.')
    @app_commands.describe(member='The member you want to ban.', duration='The amount of time to ban the member', ban_reason='The reason for the ban.')
    async def ban(self, interaction: discord.Interaction, member: discord.Member, duration: str, ban_reason: str):
        if any(role.name in config.allowed_roles for role in interaction.user.roles) or interaction.user.guild_permissions.administrator:
            try:
                duration_regex = re.match(r'^(\d+)([smhdwMy]|mo|permanent)$', duration)
                if duration_regex:
                    amount = int(duration_regex.group(1))
                    unit = duration_regex.group(2) 
                    if unit == 's':
                        delta = timedelta(seconds=amount)
                        unit_str = 'Second' if amount == 1 else 'Seconds'
                    elif unit == 'm':
                        delta = timedelta(minutes=amount)
                        unit_str = 'Minute' if amount == 1 else 'Minutes'
                    elif unit == 'h':
                        delta = timedelta(hours=amount)
                        unit_str = 'Hour' if amount == 1 else 'Hours'
                    elif unit == 'd':
                        delta = timedelta(days=amount)
                        unit_str = 'Day' if amount == 1 else 'Days'
                    elif unit == 'w':
                        delta = timedelta(weeks=amount)
                        unit_str = 'Week' if amount == 1 else 'Weeks'
                    elif unit == 'mo':
                        delta = timedelta(days=amount * 30)
                        unit_str = 'Month' if amount == 1 else 'Months'
                    elif unit == 'y':
                        delta = timedelta(days=amount * 365)
                        unit_str = 'Year' if amount == 1 else 'Years'
                    elif unit == 'permanent':
                        delta = None
                        unit_str = 'permanent'
                    config.cursor.execute('SELECT COUNT(user_bans) FROM ban_logs WHERE member_id = ?', (member.id,))
                    user_ban_count = config.cursor.fetchone()[0]
                    if user_ban_count is not None:
                        user_ban_count += 1
                    if user_ban_count is None:
                        user_ban_count = 1
                    if delta is None:
                        config.cursor.execute('''INSERT INTO ban_logs (member_id, member_name, reason, duration, banDate, unbanDate, user_bans)VALUES (?, ?, ?, ?, ?, ?, ?)''', (member.id, member.display_name, ban_reason, f'{amount} {unit_str}', pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('America/New_York')).strftime('%B, %dth %Y: %I:%M %p (%H:%M:%S) %Z'), edt_formatted.strftime('%B, %dth %Y: %I:%M %p (%H:%M:%S) %Z'), user_ban_count))
                        config.conn.commit()
                        await interaction.guild.ban(member, reason=f'{ban_reason} (Permanent ban)')
                        await interaction.response.send_message(f'{member} has been permanently banned. Reason: {ban_reason}.', ephemeral=True)
                        edt_formatted = 'Permanent Ban'
                    if delta is not None:
                        edt_formatted = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('America/New_York')) + delta
                        config.cursor.execute('''INSERT INTO ban_logs (member_id, member_name, reason, duration, banDate, unbanDate, user_bans)VALUES (?, ?, ?, ?, ?, ?, ?)''', (member.id, member.display_name, ban_reason, f'{amount} {unit_str}', pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('America/New_York')).strftime('%B, %dth %Y: %I:%M %p (%H:%M:%S) %Z'), edt_formatted.strftime('%B, %dth %Y: %I:%M %p (%H:%M:%S) %Z'), user_ban_count))
                        config.conn.commit()
                        await interaction.guild.ban(member, reason=f'{ban_reason} (Temporary ban for {amount} {unit_str})')
                        await interaction.response.send_message(f'{member} has been temporarily banned for {amount} {unit_str}. Reason: {ban_reason}.', ephemeral=True)
                        await asyncio.sleep(delta.total_seconds())
                        await interaction.guild.unban(member, reason='Temporary ban expired.')
                        await interaction.channel.send(f'{member}' + 's temporary ban has expired.', delete_after=5)
                else:
                    await interaction.response.send_message('Invalid duration format. Use 1s, 1m, 1h, 1d, 1mo, 1y, or permanent.')
            except Exception as e:
                await interaction.response.send_message(f'Error: {e} at line: {sys.exc_info()[-1].tb_lineno}', ephemeral=True)
        else:
            await interaction.response.send_message('You do not have permission to execute this command', ephemeral=True)
            await Logs(self.bot).log(interaction, 'Ban')

                                        # ! BOT SETUP ! #

async def setup(bot):
    await bot.add_cog(Ban(bot), guilds=[discord.Object(id=759962448491970561),discord.Object(id=759960762474823701)])

                                        # ! INITIALIZATION ! #