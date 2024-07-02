import discord
from discord.ext import commands
from datetime import datetime

class Logs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('\033[32mLogs Cog Initialized')

    async def log(self, ctx, command_name):
        communityBot = "CountryWideRP Official Bot"
        communityBotLogo = "https://cdn.discordapp.com/avatars/295430975368986624/c6eb7ecc3a26fcc6e93ec493efcf1d7a.webp?size=128"
        embed = discord.Embed(title="Command Execution Log", color=0xff0000, timestamp=datetime.utcnow())
        embed.add_field(name="Command Executed", value=command_name, inline=False)
        embed.add_field(name="Time Of Execution", value=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'), inline=True)
        embed.add_field(name="Date of Arrival", value=f"{ctx.author.joined_at.strftime('%Y-%m-%d %H:%M:%S UTC')}", inline=True)

        embed.add_field(name="User Information", value="\u200b", inline=False)  # Add invisible character for empty field
        embed.add_field(name="Username", value=f"{ctx.author.name}", inline=True)
        embed.add_field(name="User ID", value=f"{ctx.author.id}", inline=True)
        embed.add_field(name="Highest Role", value=f"{ctx.author.top_role.name}" if ctx.author.top_role else "None", inline=True)

        found_log_channel = False
        for guild in self.bot.guilds:
            try:
                member = await guild.fetch_member(ctx.author.id)
                log_channel = discord.utils.get(guild.channels, name='log-channel')
                if log_channel:
                    await log_channel.send(embed=embed)
                    found_log_channel = True
            except discord.HTTPException as e:
                await ctx.send(f"Error sending log message to {guild.name}: {e}", ephemeral=True)
            except Exception as e:
                await ctx.send(f"An unexpected error occurred for guild {guild.name}: {e}", ephemeral=True)

        if not found_log_channel:
            main_guild = discord.utils.get(self.bot.guilds, id=1256747105326989323)
            main_log_channel = discord.utils.get(main_guild.channels, name='log-channel')
            if main_log_channel:
                await main_log_channel.send(embed=embed)
            else:
                await ctx.send("Log channel not found. Unable to log command execution.", ephemeral=True)
                print("Log channel not found. Logging to console:")
                print(embed.to_dict())

def setup(bot):
    bot.add_cog(Logs(bot))