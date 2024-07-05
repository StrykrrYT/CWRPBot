                                        # ! INITIALIZATION ! #

                                        # ! IMPORTS ! #

import discord
import config
import pytz
import datetime
from discord.ext import commands
from discord import app_commands
from cogs.logs import Logs
import sqlite3

                                        # ! COG CREATION ! #

class Kick(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

                                        # ! BOT INIT ! #

    @commands.Cog.listener()
    async def on_ready(self):
        print('\033[32mKick Cog Initialized')

                                        # ! KICK COMMAND ! #

    @app_commands.command(name='kick',description='Kick a member from the server')
    @app_commands.describe(member='Member to kick', reason='Reason for kicking')
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        if any(role.name in config.allowed_roles for role in interaction.user.roles) or interaction.user.guild_permissions.administrator:
            try:
                config.cursor.execute('SELECT COUNT(user_kicks) FROM kick_logs WHERE member_id = ?', (member.id,))
                user_kicks_count = config.cursor.fetchone()[0]
                if user_kicks_count is not None:
                    user_kicks_count += 1
                else:
                    user_kicks_count = 1
                await interaction.guild.kick(member, reason=reason)
                await interaction.response.send_message(f'{member.display_name} Was kicked by {interaction.user.display_name}. For Reason: {reason}', ephemeral=True)
                config.cursor.execute('SELECT member_name FROM kick_logs WHERE member_name = ?', (member.display_name,))
                kick_log = config.cursor.fetchone()
                edt_datetime = pytz.utc.localize(datetime.datetime.utcnow()).astimezone(pytz.timezone('America/New_York')).strftime('%B, %dth %Y: %I:%M %p (%H:%M:%S) %Z')
                if kick_log:
                    try:
                        config.cursor.execute("INSERT INTO kick_logs (member_id, member_name, reason, kickDate, user_kicks) VALUES (?,?,?,?,?)", (member.id, member.display_name,  reason, edt_datetime, user_kicks_count))
                        await interaction.channel.send(f'Kick log updated', delete_after=5)
                        config.conn.commit()
                    except sqlite3.Error as e:
                        await interaction.channel.send(f"SQLite Error: {e}", delete_after=5)
                    except Exception as e:
                        await interaction.channel.send(f"Error: {e}", delete_after=5)
                else:
                    await interaction.channel.send(f"No kick log DB found, creating one", delete_after=5)
                    config.cursor.execute('''CREATE TABLE IF NOT EXISTS kick_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, member_id INTEGER, member_name TEXT, reason TEXT,kickDate TEXT,user_kicks INTEGER)''')
                    await interaction.channel.send('New table created', delete_after=5)
                    config.cursor.execute("INSERT INTO kick_logs (member_id, member_name, reason, kickDate, user_kicks) VALUES (?,?,?,?,?)", (member.id, member.display_name,  reason, edt_datetime, user_kicks_count))
                    config.conn.commit()
                    await interaction.channel.send('New row added', delete_after=5)
                    await interaction.channel.send(f'{member.display_name} Was kicked by {interaction.user.display_name}. For Reason: {reason}', delete_after=5)
            except sqlite3.Error as e:
                await interaction.response.send_message(f"SQLite Error: {e}", ephemeral=True)
                print(f'Error {e}')        
            except Exception as e:
                await interaction.response.send_message(f"Error: {e}", ephemeral=True)
            
        else:
            await interaction.channel.send("You do not have permission to execute this command.", ephemeral=True)
            await Logs(self.bot).log(interaction, "kick")

                                        # ! BOT SETUP ! #

async def setup(bot):
    await bot.add_cog(Kick(bot), guilds=[discord.Object(id=759962448491970561),discord.Object(id=759960762474823701)])

                                        # ! INITIALIZATION ! #