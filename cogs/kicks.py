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

class Kicks(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        os.chdir('C:/Users/terry/Desktop/CWRPBot/')
                                        # ! BOT INIT ! #

    @commands.Cog.listener()
    async def on_ready(self):
        print('\033[32mKicks Cog Initialized')

                                        # ! KICK LOGS COMMAND ! #

    @app_commands.command(name='kicks', description='View kick logs')
    async def kicks(self, interaction, page: int= 1):
        if any(role.name in config.allowed_roles for role in interaction.user.roles) or interaction.user.guild_permissions.administrator:
            try:
                config.cursor.execute('SELECT * FROM kick_logs')
                kick_logs = config.cursor.fetchall()
                if kick_logs:
                    await interaction.response.send_message('Kick Logs Found:', ephemeral=True, delete_after=0.1)
                    num_per_page = 1
                    pages = (len(kick_logs) - 1) // num_per_page + 1
                    page = max(1, min(page, pages))
                    start_idx = (page - 1) * num_per_page
                    end_idx = start_idx + num_per_page
                    kick_logs_page = kick_logs[start_idx:end_idx]
                    embed = discord.Embed(title=f'{interaction.guild}', color=0xff0000, timestamp=datetime.now(pytz.timezone('America/New_York')))
                    for log in kick_logs_page:
                        embed.add_field(name=f'{log[2]} ({log[1]})', value='', inline=False)
                        embed.add_field(name='Reason', value=log[3], inline=False)
                        embed.add_field(name='Kick Date', value=log[4], inline=False)
                        embed.add_field(name='Total Kicks', value=log[5], inline=False)
                        embed.set_footer(text=f'Page {page}/{pages}')
                        if log[5] > 2:
                            BAN_EMOJI = await interaction.guild.create_custom_emoji(name='BAN_EMOJI', image=open('images/BAN_EMOJI.png', 'rb').read())
                            await message.add_reaction(BAN_EMOJI)
                            def check(reaction, user):
                                return user == interaction.user and reaction.message.id == message.id and str(reaction.emoji) in [BAN_EMOJI]
                            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0,)
                            if str(reaction.emoji) == BAN_EMOJI:
                                member = await interaction.guild.fetch_member(log[1])
                                if member is not None:
                                    await Ban(self.bot).ban(self, interaction, member, duration='7d',reason='Kick Limit Reached, Contact BOD+ to appeal.')
                                    await message
                                else:
                                    await interaction.channel.send(f'Unable to find member with ID {log[1]} to ban.')
                        if pages > 1:
                            message = await interaction.channel.send(embed=embed)
                            await message.add_reaction('⬅️')
                            await message.add_reaction('➡️')
                        elif pages == 1:
                            message = await interaction.channel.send(embed=embed)
                            await message.add_reaction('❌')
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
                                    embed.add_field(name=f'{log[2]} ({log[1]})', value='', inline=False)
                                    embed.add_field(name='Reason', value=log[3], inline=False)
                                    embed.add_field(name='Kick Date', value=log[4], inline=False)
                                    embed.add_field(name='Total Kicks', value=log[5], inline=False)
                                    embed.set_footer(text=f'Page {current_page}/{pages}')
                                    await message.edit(embed=embed)
                                    await message.remove_reaction(reaction, user)
                            except Exception as e:
                                await interaction.channel.send(f'Error in reaction check: {e} at line: {sys.exc_info()[-1].tb_lineno}', delete_after=5)
                                return
                else:
                    await interaction.response.send_message('No kicks have been logged yet.', ephemeral=True)
            except Exception as e:
                await interaction.channel.send(f'Error: {e} at line: {sys.exc_info()[-1].tb_lineno}', delete_after=5)
                return
        else:
            await interaction.response.send_message('You do not have permission to view kick logs.')
            await Logs(self.bot).log(interaction, 'Kicks')

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