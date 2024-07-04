                                        # ! INITIALIZATION ! #

                                        # ! IMPORTS ! #

import discord
import config
import pytz
import datetime
from discord.ext import commands
from discord import app_commands
from cogs.logs import Logs

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
        if any(roles in config.allowed_roles for roles in interaction.user.roles or interaction.user.guild_permissions.administrator):
            try:
                config.cursor.execute("SELECT user_kicks FROM kick_logs WHERE member_id = ?", (member.id))
                user_kicks_count = config.cursor.fetchone()
                if user_kicks_count:
                    config.user_kicks[member.id] = user_kicks_count[0] + 1
                else:
                    config.user_kicks[member.id] = 1
                await interaction.response.send_message(f'{member.display_name} Was kicked by {interaction.user.display_name}. For Reason: {reason}', ephemeral=True)
                config.cursor.execute('SELECT name FROM sqlite_master WHERE type = "table" AND name = "kick_logs"')
                kick_log = config.cursor.fetchone()
                edt_datetime = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('America/New_York')).strftime('%B, %dth %Y: %I:%M %p (%H:%M:%S) %Z')
                if kick_log:
                    config.cursor.execute("INSERT INTO kick_logs (member_id, member_name, kickDate, reason, user_kicks) VALUES (?,?,?,?)", (member.id, member.display_name, edt_datetime, reason, config.user_kicks[member.id]))
                    config.conn.commit()
                else:
                    await interaction.response.send_message(f"No kick log DB found, creating one", ephemeral=True)
                    config.cursor.execute('''CREATE TABLE IF NOT EXISTS kick_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, member_id INTEGER, member_name TEXT, reason TEXT,kickDate TEXT,user_kicks INTEGER)''')
                    await interaction.response.send_message('New table created', ephemeral=True)
                    config.cursor.execute("INSERT INTO kick_logs (member_id, member_name, kickDate, reason, user_kicks) VALUES (?,?,?,?)", (member.id, member.display_name, edt_datetime, reason, config.user_kicks[member.id]))
                    config.conn.commit()
                    await interaction.response.send_message('New row added', ephemeral=True)
                    await interaction.response.send_message(f'{member.display_name} Was kicked by {interaction.user.display_name}. For Reason: {reason}', ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"Error: {e}", ephemeral=True)
        else:
            await interaction.response.send_message("You do not have permission to execute this command.", ephemeral=True)
            await Logs(self.bot).log(interaction, "kick")

                                        # ! BOT SETUP ! #

async def setup(bot):
    await bot.add_cog(Kick(bot), guilds=[discord.Object(id=759962448491970561)])

                                        # ! INITIALIZATION ! #