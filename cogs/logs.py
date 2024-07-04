                                        # ! INITIALIZATION ! #

                                        # ! IMPORTS ! #

import discord
import config
from discord.ext import commands
from datetime import datetime
import pytz

                                        # ! COG CREATION ! #

class Logs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

                                        # ! BOT INIT ! #

    @commands.Cog.listener()
    async def on_ready(self):
        print('\033[32mLogs Cog Initialized')

                                        # ! LOGS FUNCTION ! #

    async def log(self, interaction: discord.Interaction, command_name):
        embed = discord.Embed(title="Command Execution Log", color=0xff0000, timestamp=pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('America/New_York')).strftime('%B, %dth %Y: %I:%M %p (%H:%M:%S) %Z'))
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
            try:
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
            except discord.NotFound:
                continue
            except discord.HTTPException as e:
                print(f"Error fetching member information for guild {guild.name}: {e}")
                continue
        embed.set_author(name=config.communityBot, icon_url=config.communityBotLogo)
        embed.set_thumbnail(url=config.communityBotLogo)
        embed.set_footer(text=config.communityBot, icon_url=config.communityBotLogo)
        found_log_channel = False
        for guild in self.bot.guilds:
            try:
                member = await guild.fetch_member(interaction.user.id)
                log_channel = discord.utils.get(guild.channels, name='log-channel')
                if log_channel:
                    await log_channel.send(embed=embed)
                    found_log_channel = True
            except discord.HTTPException as e:
                await interaction.response.send_message(f"Error sending log message to {guild.name}: {e}", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"An unexpected error occurred for guild {guild.name}: {e}", ephemeral=True)
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
    await bot.add_cog(Logs(bot),  guilds=[discord.Object(id=759962448491970561)])

                                        # ! INITIALIZATION ! #