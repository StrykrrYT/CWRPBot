                                        # ! INITIALIZATION ! #

                                        # ! IMPORTS ! #

import discord
import config
import sqlite3
import pytz
import asyncio
from datetime import datetime
from discord.ext import commands
from discord import app_commands
from cogs.logs import Logs

                                        # ! CREATING COG ! #

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
        if any(roles in config.allowed_roles for roles in interaction.user.roles or interaction.user.guild):
            config.cursor.execute("SELECT * FROM kick_logs")
            kick_logs = config.cursor.fetchall()
            if kick_logs:
                num_per_page = 1
                pages = (len(kick_logs) - 1) // num_per_page + 1
                page = max(1, min(page, pages))
                start_idx = (page - 1) * num_per_page
                end_idx = start_idx + num_per_page
                kick_logs_page = kick_logs[start_idx:end_idx]
                embed = discord.Embed(title=f"{interaction.guild}", color=0xff0000, timestamp=pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('America/New_York')).strftime('%B, %dth %Y: %I:%M %p (%H:%M:%S) %Z'))
                for log in kick_logs_page:
                    member = interaction.guild.get_member(log[1])
                    member_name = log[2]
                    embed.add_field(name=f"{member_name} ({log[1]})", value="", inline=False)
                    embed.add_field(name="Reason", value=log[3], inline=False)
                    embed.add_field(name="Kick Date", value=log[4], inline=False)
                    embed.add_field(name="Total Kicks", value=log[5], inline=False)
                    if log[5] > 2:
                        if member:
                            await interaction.guild.ban(member, duration='7d', ban_reason="Kick Limit Reached, Contact BOD+ to appeal.")
                            await interaction.response.send_message(f'{member.display_name} Was automatically banned by {config.communityBot}. For Reason: Kick limit reached.", ephemeral=True)')
                        else:
                            await interaction.response.send_message(f"Unable to find member with ID '{log[1]}' to kick.")
                embed.set_footer(text=f"Page {page}/{pages}")
                message = await interaction.response.send_message(embed=embed)
                if pages > 1:
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
                            member = interaction.guild.get_member(log[1])
                            embed.add_field(name=f"{member_name} ({log[1]})", value="", inline=False)
                            embed.add_field(name="Reason", value=log[3], inline=False)
                            embed.add_field(name="Kick Date", value=log[4], inline=False)
                            embed.add_field(name="Total Kicks", value=log[5], inline=False)
                            if log[5] > 2:
                                if member:
                                    await interaction.guild.ban(member, duration='7d', ban_reason="Kick Limit Reached, Contact BOD+ to appeal.")
                                    await interaction.response.send_message(f'{member.display_name} Was automatically banned by {config.communityBot}. For Reason: Kick limit reached.", ephemeral=True)')
                                else:
                                    await interaction.response.send_message(f"Unable to find member with ID '{log[1]}' to kick.")
                        embed.set_footer(text=f"Page {current_page}/{pages}")
                        await message.edit(embed=embed)
                        await message.remove_reaction(reaction, user)
                    except asyncio.TimeoutError:
                        break
            else:
                await interaction.response.send_message("No kicks have been logged yet.")
        else:
            await interaction.response.send_message("You do not have permission to view kick logs.")
            await Logs(self.bot).log(interaction, "Kicks")

                                        # ! DATABASE CONNECTION ! #                           

try:
    config.cursor.execute('''
    CREATE TABLE IF NOT EXISTS kick_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER,
    member_name TEXT,
    reason TEXT,
    duration TEXT,
    kickDate TEXT,
    user_kicks INTEGER,
)
''')
    config.conn.commit()
except sqlite3.Error as e:
    print(f"Error Connecting To Table kick_logs: {e}")

async def setup(bot):
    await bot.add_cog(Kicks(bot), guilds=[discord.Object(id=759962448491970561)])

                                        # ! INITIALIZATION ! #