# Imports
import discord
import settings
from discord.ext import commands
from cogs.logs import Logs
from settings_files import logging

# Logging Setup
logger = logging.logging.getLogger("bot")

class Sync(commands.Cog):
    def __init__(self, bot: commands.Bot):
        """
        Initialize the Sync cog.

        Args:
            bot (commands.Bot): The bot object.
        """

        self.bot = bot

                                        # ! BOT INIT ! #

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info('\033[32mSync Cog Initialized\033[97m')

                                        # ! SYNC COMMAND ! #        

    @commands.hybrid_command(name='sync', description='Syncs the bot to the current guild.')
    async def sync(self, ctx):
        """
        Syncs the bot to the current guild.

        This command will sync all slash commands to the current guild. If you do not have permission to execute this command, it will send an ephemeral message saying so.

        Parameters:
            ctx (commands.Context): The context of the command invocation.

        Returns:
            None
        """
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
            await Logs(self.bot).log(ctx, "sync")

                                        # ! BOT SETUP ! #

async def setup(bot):
    """
    Add the Sync cog to the bot.

    Args:
        bot: The bot to add the cog to.
    """
    await bot.add_cog(Sync(bot), guilds=[discord.Object(id=guild_id) for guild_id in settings.GUILD_IDS])

                                        # ! INITIALIZATION ! #