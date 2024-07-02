import discord
from discord.ext import commands
from discord import app_commands

class Delete(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('\033[32mDelete Cog Initialized')

async def setup(bot):
    await bot.add_cog(Delete(bot), guilds=[discord.Object(id=759962448491970561)])