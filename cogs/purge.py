import discord
from discord import app_commands
from discord.ext import commands


class Purge(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('\033[32mPurge Cog Initialized')

    @app_commands.command(name='purge', description='Clean up a specified amount of messages')
    @app_commands.describe(amount='Amount of messages to delete')
    async def purge(self, interaction: discord.Interaction, amount: int):
        if amount <= 0:
            await interaction.response.send_message('Invalid amount. Please specify a positive number of messages to purge.', ephemeral=True)
            return
        
        if not interaction.channel.permissions_for(interaction.author).manage_messages:
            await interaction.response.send_message("You don't have permission to manage messages in this channel.", ephemeral=True)
            return
        
        await interaction.response.send_message(f'Purged {amount} messages', ephemeral=True)
        await interaction.channel.purge(limit=amount)

async def setup(bot):
    await bot.add_cog(Purge(bot), guilds=[discord.Object(id=759962448491970561)])
