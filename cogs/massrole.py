                                        # ! INITIALIZATION ! #

                                        # ! IMPORTS ! #

import config
import discord
import sys
from cogs.logs import Logs
from discord import app_commands
from discord.ext import commands

                                        # ! COG CREATION ! #

class Massrole(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

                                        # ! BOT INIT ! #

    @commands.Cog.listener()
    async def on_ready(self):
        print('\033[32mMassrole Cog Initialized')

                                        # ! MASSROLE COMMAND ! #

    @app_commands.command(name='massrole', description='Add a role to all members of a server.')
    @app_commands.describe(member='The member you want to add the role to.', role='The role you want to add to the member.')

    async def massrole(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        if any(role.name in config.allowed_roles for role in interaction.user.roles) or interaction.user.guild_permissions.administrator:
            try:
                for guild in self.bot.guilds:
                    has_role = False
                    new_role = discord.utils.get(guild.roles, name=role.name)
                    guild_member = guild.get_member(member.id)
                    if new_role and guild_member:
                        if new_role in guild_member.roles:
                            try:
                                await guild_member.remove_roles(new_role)
                                has_role = False
                            except Exception as e:
                                await interaction.channel.send(f'Error at line {sys.exc_info()[-1].tb_lineno}: {e}', delete_after=5)
                        else:
                            try:
                                await guild_member.add_roles(new_role)
                                has_role = True
                            except Exception as e:
                                await interaction.channel.send(f'Error at line {sys.exc_info()[-1].tb_lineno}: {e}', delete_after=5)
                    else:
                        await interaction.response.send_message(f'{role.name} not found in {guild.name} or {member.name} is not a member.', ephemeral=True, delete_after=5)
                    if has_role == True:
                        await interaction.response.send_message(f'Added {new_role.name} to all servers.', ephemeral=True, delete_after=5)
                    else:
                        await interaction.response.send_message(f'Removed {new_role.name} from all servers.', ephemeral=True, delete_after=5)
                await interaction.response.send_message()        
            except Exception as e:
                await interaction.response.send_message(f'Error at line {sys.exc_info()[-1].tb_lineno}: {e}.', ephemeral=True, delete_after=5)
        else:
            await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True, delete_after=3)
            await Logs(self.bot).log(interaction, 'Massrole')

                                        # ! BOT SETUP ! #

async def setup(bot):
    await bot.add_cog(Massrole(bot), guilds=[discord.Object(id=759962448491970561),discord.Object(id=759960762474823701)])

                                        # ! INITIALIZATION ! #