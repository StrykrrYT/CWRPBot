# Imports
import discord
import settings
from discord.ext import commands
from cogs.logs import Logs
from settings_files import logging

# Logging Setup
logger = logging.logging.getLogger("bot")

class Test(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info('\033[32mTest Cog Initialized\033[97m')

                                        # ! SYNC COMMAND ! #        


    @commands.command(name="test", description="Syncs the bot to the current guild.")
    async def test(self, ctx):
        if any(role.name in settings.allowed_roles for role in ctx.author.roles) or ctx.author.guild_permissions.administrator:
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
            await Logs(self.bot).log(ctx, "test")

                                        # ! BOT SETUP ! #

async def setup(bot):
    await bot.add_cog(Test(bot), guilds=[discord.Object(id=guild_id) for guild_id in settings.GUILD_IDS])

                                        # ! INITIALIZATION ! #