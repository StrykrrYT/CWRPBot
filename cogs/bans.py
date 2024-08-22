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
from cogs.ban import Ban
from cogs.logs import Logs
from datetime import datetime, timedelta
from discord.ext import commands
from discord import app_commands


                                        # ! COG CREATION ! #

class Bans(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        os.chdir('./')
                                        # ! BOT INIT ! #

    @commands.Cog.listener()
    async def on_ready(self):
        print('\033[32mBans Cog Initialized')

                                        # ! BAN LOGS COMMAND ! #

    @app_commands.command(name='bans', description='View ban logs')
    async def bans(self, interaction: discord.Interaction, page: int=1):
        if any(role.name in config.allowed_roles for role in interaction.user.roles) or interaction.user.guild_permissions.administrator:
            try:
                config.cursor.execute("SELECT * FROM ban_logs")
                ban_logs = config.cursor.fetchall()
                if ban_logs:
                    await interaction.response.send_message('Ban Logs Found:', ephemeral=True, delete_after=0.1)
                    num_per_page = 1
                    pages = (len(ban_logs) - 1) // num_per_page + 1
                    page = max(1, min(page, pages))
                    embed = discord.Embed(title=f"{interaction.guild}", color=0xff0000, timestamp=datetime.now(pytz.timezone('America/New_York')))
                    embed.set_footer(text=f'Page {page}/{pages}')
                    start_idx = (page - 1) * num_per_page
                    end_idx = start_idx + num_per_page
                    ban_logs_page = ban_logs[start_idx:end_idx]

                    message = None  # Initialize message variable

                    for log in ban_logs_page:
                        embed.add_field(name=f"{f'{log[2]} ({log[1]})'}", value="", inline=False)
                        embed.add_field(name="Reason", value=log[3], inline=False)
                        embed.add_field(name="Duration", value=log[4], inline=False)
                        embed.add_field(name="Ban Date", value=log[5], inline=False)
                        embed.add_field(name="Unban Date", value=log[6], inline=False)
                        embed.add_field(name="Total Bans", value=log[7], inline=False)

                        if pages > 1:
                            if message is None:
                                message = await interaction.channel.send(embed=embed)
                            await message.add_reaction('⬅️')
                            await message.add_reaction('➡️')
                            await message.add_reaction('❌')

                        elif pages == 1:
                            if message is None:
                                message = await interaction.channel.send(embed=embed)
                            await message.add_reaction('❌')

                        if log[7] > 2:
                            try:
                                BAN_EMOJI = await interaction.guild.create_custom_emoji(name='BAN_EMOJI', image=open('images/BAN_EMOJI.png', 'rb').read())
                                if message is not None:
                                    await message.add_reaction(BAN_EMOJI)
                            except Exception as e:
                                await interaction.channel.send(f'Error creating BAN_EMOJI: {e}', delete_after=5)
                        elif log[7] < 2:
                            try:
                                await message.remove_reaction(BAN_EMOJI, self.bot.user)
                            except Exception as e:
                                await interaction.channel.send(f'Error: {e} at line: {sys.exc_info()[-1].tb_lineno}', delete_after=5)

                    def check(reaction, user):
                        return user == interaction.user and reaction.message.id == message.id and str(reaction.emoji) in ['⬅️', '➡️', '❌', ':BAN_EMOJI:']

                    current_page = page
                    while True:
                        try:
                            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                            if str(reaction.emoji) == '⬅️':
                                current_page = max(1, current_page - 1)
                            elif str(reaction.emoji) == '➡️':
                                current_page = min(pages, current_page + 1)
                            elif str(reaction.emoji) == '❌':
                                await message.delete()
                                return
                            elif str(reaction.emoji) == BAN_EMOJI:
                                if log[7] > 2:
                                    member = await interaction.guild.fetch_member(log[1])
                                    if member is not None:
                                        await Ban(self.bot).ban(self, member, duration='permanent', reason='Ban Limit Reached, Contact BOD+ to appeal.')
                                        await message.remove_reaction(BAN_EMOJI, self.bot.user)
                                    else:
                                        await interaction.channel.send(f'Unable to find member with ID {log[1]} to ban.')

                            start_idx = (current_page - 1) * num_per_page
                            end_idx = start_idx + num_per_page
                            ban_logs_page = ban_logs[start_idx:end_idx]

                            embed.clear_fields()
                            for log in ban_logs_page:
                                embed.add_field(name=f"{f'{log[2]} ({log[1]})'}", value="", inline=False)
                                embed.add_field(name="Reason", value=log[3], inline=False)
                                embed.add_field(name="Duration", value=log[4], inline=False)
                                embed.add_field(name="Ban Date", value=log[5], inline=False)
                                embed.add_field(name="Unban Date", value=log[6], inline=False)
                                embed.add_field(name="Total Bans", value=log[7], inline=False)
                            embed.set_footer(text=f'Page {current_page}/{pages}')
                            await message.edit(embed=embed)
                            BAN_EMOJI_FINAL = discord.utils.get(message.reactions, emoji=lambda e: str(e.emoji) == 'BAN_EMOJI')
                            await interaction.channel.send(f'Test3: {BAN_EMOJI_FINAL}')
                            if BAN_EMOJI:
                                if discord.utils.get(message.reactions, emoji=BAN_EMOJI) is not None:
                                    if log[7] > 2:
                                        return
                                    else:
                                        await message.remove_reaction(BAN_EMOJI)
                                elif discord.utils.get(message.reactions, emoji=BAN_EMOJI) is None:
                                    if log[7] > 2:
                                        await message.add_reaction(BAN_EMOJI)
                                    else:
                                        return
                            else:
                                if log[7] < 2:
                                    try:
                                        BAN_EMOJI = await interaction.guild.create_custom_emoji(name='BAN_EMOJI', image=open('images/BAN_EMOJI.png', 'rb').read())
                                        if message is not None:
                                            await message.add_reaction(BAN_EMOJI)
                                    except Exception as e:
                                        await interaction.channel.send(f'Error creating BAN_EMOJI: {e}', delete_after=5)
                            await message.remove_reaction(reaction, user)
                        except Exception as e:
                            await interaction.channel.send(f'Error in reaction check: {e} at line: {sys.exc_info()[-1].tb_lineno}', delete_after=5)
                            return

                else:
                    await interaction.response.send_message('No bans have been logged yet.', ephemeral=True)
            except Exception as e:
                await interaction.channel.send(f'Error: {e} at line: {sys.exc_info()[-1].tb_lineno}', delete_after=5)
                return
        else:
            await interaction.response.send_message('You do not have permission to view ban logs.')
            await Logs(self.bot).log(interaction, 'Bans')

                                        # ! DATABASE CONNECTION ! #                           

try:
    config.cursor.execute('''
    CREATE TABLE IF NOT EXISTS ban_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER,
    member_name TEXT,
    reason TEXT,
    duration TEXT,
    banDate TEXT,
    unbanDate TEXT,
    user_bans INTEGER
)
''')
    config.conn.commit()
except sqlite3.Error as e:
    print(f'Error Connecting To Table ban_logs: {e}')

                                        # ! BOT SETUP ! #

async def setup(bot):
    await bot.add_cog(Bans(bot), guilds=[discord.Object(id=759962448491970561),discord.Object(id=759960762474823701)])

                                        # ! INITIALIZATION ! #