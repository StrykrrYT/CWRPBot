                                        # ! INITIALIZATION ! #

                                        # ! IMPORTS ! #

import discord
import config
from discord import app_commands
from discord.ext import commands
from cogs.logs import Logs

                                        # ! COG CREATION ! #

class Sync(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

                                        # ! BOT INIT ! #

    @commands.Cog.listener()
    async def on_ready(self):
        print('\033[32mSync Cog Initialized')

                                        # ! SYNC COMMAND ! #        

    @commands.hybrid_command(name='sync', description='Syncs the bot to the current guild.')
    async def sync(self, ctx):
        if any(role.name in config.allowed_roles for role in ctx.author.roles) or ctx.author.guild_permissions.administrator:
            fmt = await self.bot.tree.sync(guild=ctx.guild)
            try:
                if len(fmt) == 1:
                    await ctx.send(f"Synced {len(fmt)} Command to current guild", ephemeral=True)
                else:
                    await ctx.send(f"Synced {len(fmt)} Commands to current guild", ephemeral=True)
            except Exception as e:
                await ctx.send(f"Error: {e}", ephemeral=True)
        else:
            await ctx.send("You do not have permission to execute this command", ephemeral=True)
            await Logs(self.bot).log(ctx, "sync")

                                        # ! BOT SETUP ! #

async def setup(bot):
    await bot.add_cog(Sync(bot), guilds=[discord.Object(id=759962448491970561),discord.Object(id=759960762474823701)])

                                        # ! INITIALIZATION ! #