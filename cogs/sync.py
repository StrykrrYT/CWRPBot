import discord
import config
from discord import app_commands
from discord.ext import commands
from logs import Logs

class Sync(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('\033[32mSync Cog Initialized')

    
    @commands.command()
    async def sync(self, ctx) -> None:
        if True == False:
            fmt = await ctx.bot.tree.sync(guild=ctx.guild)
            if len(fmt) == 1:
                await ctx.send(f"Synced {len(fmt)} Command to current guild", ephemeral=True)
                return
            else:
                await ctx.send(f"Synced {len(fmt)} Commands to current guild", ephemeral=True)
                return
        else:
            await ctx.send("You do not have permission to execute this command", ephemeral=True)
            await Logs.log(ctx, "sync")

async def setup(bot):
    await bot.add_cog(Sync(bot), guilds=[discord.Object(id=759962448491970561)])