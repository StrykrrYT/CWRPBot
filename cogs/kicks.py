                                        # ! INITIALIZATION ! #

                                        # ! IMPORTS ! #

import discord
import config
import sqlite3
import pytz
import asyncio
import re
from datetime import datetime, timedelta
from discord.ext import commands
from discord import app_commands
from cogs.logs import Logs

                                        # ! COG CREATION ! #

class Kicks(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

                                        # ! BOT INIT ! #

    @commands.Cog.listener()
    async def on_ready(self):
        print('\033[32mKicks Cog Initialized')

                                        # ! KICK LOGS COMMAND ! #

    @app_commands.command(name='kicks',description='View kick logs')
    async def kicks(self,interaction: discord.Interaction, page: int = 1):
        try:
            if any(role.name in config.allowed_roles for role in interaction.user.roles) or interaction.user.guild_permissions.administrator:
                await interaction.response.send_message('Kick Logs Found:', ephemeral=True, delete_after=0.1)
                config.cursor.execute('SELECT * FROM kick_logs')
                kick_logs = config.cursor.fetchall()
                if kick_logs:
                    num_per_page = 1
                    pages = (len(kick_logs) - 1) // num_per_page + 1
                    page = max(1, min(page, pages))
                    start_idx = (page - 1) * num_per_page
                    end_idx = start_idx + num_per_page
                    kick_logs_page = kick_logs[start_idx:end_idx]
                    timestamp = datetime.now(pytz.timezone('America/New_York'))
                    embed = discord.Embed(title=f'{interaction.guild}', color=0xff0000, timestamp=timestamp)
                    for log in kick_logs_page:
                        member = await interaction.guild.fetch_member(log[1])
                        member_name = log[2]
                        embed.add_field(name=f'{member_name} ({log[1]})', value='', inline=False)
                        embed.add_field(name='Reason', value=log[3], inline=False)
                        embed.add_field(name='Kick Date', value=log[4], inline=False)
                        embed.add_field(name='Total Kicks', value=log[5], inline=False)   
                        if log[5] > 2 and member is not None:
                            duration = '10s'
                            ban_reason = 'Kick Limit Reached, Contact BOD+ to appeal.'
                            duration_regex = re.match(r'^(\d+)([smhdwMy]|mo|permanent)$', duration)
                            if duration_regex:
                                amount = int(duration_regex.group(1))
                                unit = duration_regex.group(2)
                                if unit == 's':
                                    delta = timedelta(seconds=amount)
                                    unit_str = 'Second' if amount == 1 else 'Seconds'
                                elif unit == 'd':
                                    delta = timedelta(days=amount)
                                    unit_str = 'Day' if amount == 1 else 'Days'
                            await interaction.guild.ban(member, reason='Kick Limit Reached, Contact BOD+ to appeal.')
                            edt_formatted = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('America/New_York')) + delta
                            edt_datetime = edt_formatted.strftime('%B, %dth %Y: %I:%M %p (%H:%M:%S) %Z') 
                            config.cursor.execute('SELECT COUNT(user_bans) FROM ban_logs WHERE member_id = ?', (member.id,))
                            user_bans = config.cursor.fetchone()[0]
                            if user_bans is not None:
                                user_bans += 1
                            else:
                                user_bans = 1
                            config.cursor.execute("INSERT INTO ban_logs (member_id, member_name, reason, duration, banDate, unbanDate, user_bans) VALUES (?, ?, ?, ?, ?, ?, ?)", (member.id, member.display_name, ban_reason, f"{amount} {unit_str}", pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('America/New_York')).strftime('%B, %dth %Y: %I:%M %p (%H:%M:%S) %Z'), edt_datetime, user_bans))
                            config.conn.commit()
                            await interaction.channel.send(f'{member.display_name} Was automatically banned by for {amount} {unit_str} by {config.communityBot}. For Reason: {ban_reason}', delete_after=5)
                            await asyncio.sleep(delta.total_seconds())
                            await interaction.guild.unban(member, reason="Temporary ban expired.")
                            await interaction.channel.send(f"{member.display_name}'s temporary ban has expired.", delete_after=5)
                        else:
                                await interaction.channel.send(f'Unable to find member with ID {log[1]} to ban.', delete_after=5)
                    embed.set_footer(text=f'Page {page}/{pages}')
                    if pages > 1:
                        message = await interaction.channel.send(embed=embed)
                        await message.add_reaction('⬅️')
                        await message.add_reaction('➡️')
                    def check(reaction, user):
                        return user == interaction.user and reaction.message.id == message.id and str(reaction.emoji) in ['⬅️', '➡️']
                    current_page = page
                    while True:
                        try:
                            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                            if str(reaction.emoji) == '⬅️':
                                current_page = max(1, current_page - 1)
                            elif str(reaction.emoji) == '➡️':
                                current_page = min(pages, current_page + 1)
                            start_idx = (current_page - 1) * num_per_page
                            end_idx = start_idx + num_per_page
                            kick_logs_page = kick_logs[start_idx:end_idx]
                            embed.clear_fields()
                            for log in kick_logs_page:
                                member = await interaction.guild.fetch_member(log[1])
                                member_name = log[2]
                                embed.add_field(name=f'{member_name} ({log[1]})', value='', inline=False)
                                embed.add_field(name='Reason', value=log[3], inline=False)
                                embed.add_field(name='Kick Date', value=log[4], inline=False)
                                embed.add_field(name='Total Kicks', value=log[5], inline=False)   
                                if log[5] > 2 and member is not None:
                                    duration = '10s'
                                    ban_reason = 'Kick Limit Reached, Contact BOD+ to appeal.'
                                    duration_regex = re.match(r'^(\d+)([smhdwMy]|mo|permanent)$', duration)
                                    if duration_regex:
                                        amount = int(duration_regex.group(1))
                                        unit = duration_regex.group(2)
                                        if unit == 's':
                                            delta = timedelta(seconds=amount)
                                            unit_str = 'Second' if amount == 1 else 'Seconds'
                                        elif unit == 'd':
                                            delta = timedelta(days=amount)
                                            unit_str = 'Day' if amount == 1 else 'Days'
                                    await interaction.guild.ban(member, reason='Kick Limit Reached, Contact BOD+ to appeal.')
                                    edt_formatted = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('America/New_York')) + delta
                                    edt_datetime = edt_formatted.strftime('%B, %dth %Y: %I:%M %p (%H:%M:%S) %Z') 
                                    config.cursor.execute('SELECT COUNT(user_bans) FROM ban_logs WHERE member_id = ?', (member.id,))
                                    user_bans = config.cursor.fetchone()[0]
                                    if user_bans is not None:
                                        user_bans += 1
                                    else:
                                        user_bans = 1
                                    config.cursor.execute("INSERT INTO ban_logs (member_id, member_name, reason, duration, banDate, unbanDate, user_bans) VALUES (?, ?, ?, ?, ?, ?, ?)", (member.id, member.display_name, ban_reason, f"{amount} {unit_str}", pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('America/New_York')).strftime('%B, %dth %Y: %I:%M %p (%H:%M:%S) %Z'), edt_datetime, user_bans))
                                    config.conn.commit()
                                    await interaction.channel.send(f'{member.display_name} Was automatically banned by for {amount} {unit_str} by {config.communityBot}. For Reason: {ban_reason}', delete_after=5)
                                    await asyncio.sleep(delta.total_seconds())
                                    await interaction.guild.unban(member, reason="Temporary ban expired.")
                                    await interaction.channel.send(f"{member.display_name}'s temporary ban has expired.", delete_after=5)
                                else:
                                        await interaction.channel.send(f'Unable to find member with ID {log[1]} to ban.', delete_after=5)
                            embed.set_footer(text=f'Page {current_page}/{pages}')
                            await message.edit(embed=embed)
                            await message.remove_reaction(reaction, user)
                        except asyncio.TimeoutError:
                            break
                else:
                    await interaction.response.send_message('No kicks have been logged yet.', ephemeral=True)
            else:
                await interaction.response.send_message('You do not have permission to view kick logs.')
                await Logs(self.bot).log(interaction, 'Kicks')
        except Exception as e:
                await interaction.channel.send(f'Error: {e}', delete_after=5)

                                        # ! DATABASE CONNECTION ! #                           

try:
    config.cursor.execute('''
    CREATE TABLE IF NOT EXISTS kick_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER,
    member_name TEXT,
    reason TEXT,
    kickDate TEXT,
    user_kicks INTEGER
)
''')
    config.conn.commit()
except sqlite3.Error as e:
    print(f'Error Connecting To Table kick_logs: {e}')

                                        # ! BOT SETUP ! #

async def setup(bot):
    await bot.add_cog(Kicks(bot), guilds=[discord.Object(id=759962448491970561),discord.Object(id=759960762474823701)])

                                        # ! INITIALIZATION ! #