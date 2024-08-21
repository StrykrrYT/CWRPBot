                                        # ! INITIALIZATION ! #

                                        # ! IMPORTS ! #

import config
import discord
import sys
from cogs.logs import Logs
from discord import app_commands
from discord.ext import commands

                                        # ! COG CREATION ! #

class Massname(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

                                        # ! BOT INIT ! #

    @commands.Cog.listener()
    async def on_ready(self):
        print('\033[32mMassrole Cog Initialized')

                                        # ! MASSNAME COMMAND ! #

    @app_commands.command(name='massname', description='Change members name in all community servers.')
    @app_commands.describe(member='The member whose name you want to change.', name='The name you want to the members name to.')
    async def massrole(self, interaction: discord.Interaction, member: discord.Member, name: str):
        if any(role.name in config.allowed_roles for role in interaction.user.roles) or interaction.user.guild_permissions.administrator:
            try:
                for guild in self.bot.guilds:
                    member = guild.get_member(member.id)
                    if member:
                        try:
                            await member.edit(nick=name)
                        except Exception as e:
                            await interaction.response.send_message(f'Error at line: {sys.exc_info()[-1].tb_lineno}: {e}', ephemeral=True, delete_after=5)
                    else:
                        await interaction.response.send_message(f'{member} is not a member of this server.', ephemeral=True, delete_after=5)
                await interaction.response.send_message(f'Renamed {member.display_name} to {name} in all servers', ephemeral=True, delete_after=5)
            except Exception as e:
                await interaction.response.send_message(f'Error at line: {sys.exc_info()[-1].tb_lineno}: {e}', ephemeral=True, delete_after=5)
        else:
            await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True, delete_after=3)
            await Logs(self.bot).log(interaction, 'Massname')

                                        # ! BOT SETUP ! #

async def setup(bot):
    await bot.add_cog(Massname(bot), guilds=[discord.Object(id=759962448491970561),discord.Object(id=759960762474823701)])

                                        # ! INITIALIZATION ! #