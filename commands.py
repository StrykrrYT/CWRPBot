import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pytz
import asyncio
import re
import sqlite3

load_dotenv()

# SQLite setup
try:
    conn = sqlite3.connect('logs.db')
    print("Successfully connected to bans_logs database")
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ban_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER,
    member_name TEXT,
    reason TEXT,
    duration TEXT,
    banDate TEXT,
    unbanDate TEXT,
    user_bans INTEGER
)
''')
    conn.commit()
except sqlite3.Error as e:
    print(f"Error connecting to SQLite database: {e}")

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')    

communityBot = "CountryWideRP Official Bot"
communityBotLogo = "https://cdn.discordapp.com/avatars/295430975368986624/c6eb7ecc3a26fcc6e93ec493efcf1d7a.webp?size=128"
user_bans = {}
user_kicks = {}
user_warns = {}
user_mutes = {}

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
edt_datetime = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('America/New_York')).strftime('%B, %dth %Y: %I:%M %p (%H:%M:%S) %Z')

# ? Logging System ? #

async def log_command_execution(ctx, command_name):
    embed = discord.Embed(title="Command Execution Log", color=0xff0000, timestamp=datetime.now())
    embed.add_field(name="Command Executed", value=command_name, inline=False)
    embed.add_field(name="Time Of Execution", value=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'), inline=True)
    embed.add_field(name="Date of Arrival", value=f"{ctx.author.joined_at.strftime('%Y-%m-%d %H:%M:%S UTC')}", inline=True)

    # * User Information * #
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name="User Information", value="", inline=False)
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name="Username", value=f"{ctx.author.name}", inline=True)
    embed.add_field(name="User ID", value=f"{ctx.author.id}", inline=True)
    embed.add_field(name="Highest Role", value=f"{ctx.author.top_role.name}", inline=True if ctx.author.top_role else False)
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name="Community Servers",value="",inline=False)
    embed.add_field(name="", value="", inline=False)

    # ? Gather Community Servers Information * #
    inline = len(bot.guilds) > 1
    for guild in bot.guilds:
        try:
            member = await guild.fetch_member(ctx.author.id)
            highest_role = member.top_role.name if member.top_role else "None"
            join_date = member.joined_at.strftime('%Y-%m-%d %H:%M:%S UTC')

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

    embed.set_author(name=communityBot, icon_url=communityBotLogo)
    embed.set_thumbnail(url=communityBotLogo)
    embed.set_footer(text=communityBot, icon_url=communityBotLogo)

    # * Send the log embed * #
    found_log_channel = False
    for guild in bot.guilds:
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
        main_guild = discord.utils.get(bot.guilds, id=1256747105326989323)
        main_log_channel = discord.utils.get(main_guild.channels, name='log-channel')
        if main_log_channel:
            await main_log_channel.send(embed=embed)
        else:
            await ctx.send("Log channel not found. Unable to log command execution.", ephemeral=True)
            print("Log channel not found. Logging to console:")
            print(embed.to_dict())
    


# * Community Wide Commands * #

@bot.hybrid_command(description='Mass name across all of community')
async def massname(ctx: commands.Context, target_user: discord.Member, new_name: str):
    if ctx.guild.me.guild_permissions.change_nickname:
        for guild in bot.guilds:
            if guild.me.guild_permissions.change_nickname or guild.me.guild_permissions.administrator:
                member = guild.get_member(target_user.id)
                if member:
                    try:
                        await member.edit(nick=new_name)
                        await ctx.send(f'Renamed {member.display_name} to {new_name} in {guild.name}')
                    except discord.Forbidden:
                        await ctx.send(f'Bot does not have permission to rename users in {guild.name}')
                    except discord.HTTPException as e:
                        await ctx.send(f'Failed to rename {member.display_name} in {guild.name}: {e}')
                else:
                    await ctx.send(f'User {target_user.display_name} not found in {guild.name}')
            else:
                await ctx.send(f'Bot does not have permission to manage nicknames in {guild.name}')
    else:
        await ctx.send('Bot does not have permission to change nicknames.')

@bot.hybrid_command(description='Mass role across all of community')
async def massrole(ctx: commands.Context, target_user: discord.Member, *, role_name: str):
    try:
        for guild in bot.guilds:
            if guild.me.guild_permissions.manage_roles or guild.me.guild_permissions.administrator:
                new_role = discord.utils.get(guild.roles, name=role_name)
                if new_role:
                    member = guild.get_member(target_user.id)
                    if member:
                        try:
                            await member.add_roles(new_role)
                            await ctx.send(f'Added {new_role.name} to {member.display_name} in {guild.name}')
                        except discord.Forbidden:
                            await ctx.send(f'Bot does not have permission to manage roles in {guild.name}')
                        except discord.HTTPException as e:
                            await ctx.send(f'Failed to add {new_role.name} to {member.display_name} in {guild.name}: {e}')
                    else:
                        await ctx.send(f'User {target_user.display_name} not found in {guild.name}')
                else:
                    await ctx.send(f'Role {role_name} not found in {guild.name}')
            else:
                await ctx.send(f'Bot does not have permission to manage roles in {guild.name}')
    except Exception as e:
        await ctx.send(f'Error: {e}')     


# ! Administration Commands ! #

@bot.hybrid_command(description='Clean up a specified amount of messages')
async def purge(ctx,amount:int):
    await ctx.send(f'Purged {amount} messages', ephemeral=True)
    await ctx.channel.purge(limit=amount)

@bot.hybrid_command(description='Ban a user for a specified duration')
async def ban(ctx, member: discord.Member, duration, *, ban_reason):
    if ctx.message.author.guild_permissions.ban_members:
        duration_regex = re.match(r'^(\d+)([smhdwMy]|mo|permanent)$', duration)
        if duration_regex:
            amount = int(duration_regex.group(1))
            unit = duration_regex.group(2)
            
            if unit == 's':
                delta = timedelta(seconds=amount)
                unit_str = 'Second' if amount == 1 else 'Seconds'
            elif unit == 'm':
                delta = timedelta(minutes=amount)
                unit_str = 'Minute' if amount == 1 else 'Minutes'
            elif unit == 'h':
                delta = timedelta(hours=amount)
                unit_str = 'Hour' if amount == 1 else 'Hours'
            elif unit == 'd':
                delta = timedelta(days=amount)
                unit_str = 'Day' if amount == 1 else 'Days'
            elif unit == 'w':
                delta = timedelta(weeks=amount)
                unit_str = 'Week' if amount == 1 else 'Weeks'
            elif unit == 'mo':
                delta = timedelta(days=amount * 30)
                unit_str = 'Month' if amount == 1 else 'Months'
            elif unit == 'y':
                delta = timedelta(days=amount * 365)
                unit_str = 'Year' if amount == 1 else 'Years'
            elif unit == 'permanent':
                delta = None
                unit_str = 'permanent'
            
            if delta is None:
                unban_date = "Permanent Ban"
            else:
                unban_date = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('America/New_York')).strftime('%B, %dth %Y: %I:%M %p (%H:%M:%S) %Z')

            cursor.execute("SELECT user_bans FROM ban_logs WHERE member_id = ?", (member.id,))
            user_bans_count = cursor.fetchone()
            if user_bans_count:
                user_bans[member.id] = user_bans_count[0] + 1
            else:
                user_bans[member.id] = 1

            ban_log = {
                'member_id': member.id,
                'member_name': member.display_name,
                'reason': ban_reason,
                'duration': f"{amount} {unit_str}" if unit != 'permanent' else 'permanent',
                'banDate': edt_datetime,
                'unbanDate': unban_date,
                'user_bans': user_bans[member.id]
            }

            cursor.execute("""
            INSERT INTO ban_logs (member_id, member_name, reason, duration, banDate, unbanDate, user_bans)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (member.id, member.display_name, ban_reason, ban_log['duration'], ban_log['banDate'], ban_log['unbanDate'], ban_log['user_bans']))
            conn.commit()

            if delta is None:
                await ctx.guild.ban(member, reason=f"{ban_reason} (Permanent ban)")
                await ctx.send(f"{member} has been permanently banned. Reason: {ban_reason}.", ephemeral=True)
            else:
                await ctx.guild.ban(member, reason=f"{ban_reason} (Temporary ban for {amount} {unit_str})")
                await ctx.send(f"{member} has been temporarily banned for {amount} {unit_str}. Reason: {ban_reason}.", ephemeral=True)
                await asyncio.sleep(delta.total_seconds())
                await ctx.guild.unban(member, reason="Temporary ban expired.")
                await ctx.send(f"{member}'s temporary ban has expired.", delete_after=5)

        else:
            await ctx.send("Invalid duration format. Use 1s, 1m, 1h, 1d, 1mo, 1y, or permanent.")
    else:
        await ctx.send("You do not have permission to execute this command", ephemeral=True)
        await log_command_execution(ctx, "ban")

@bot.hybrid_command(description='Ban Logs')
async def bans(ctx, page: int = 1):
    if ctx.message.author.guild_permissions.ban_members:
        cursor.execute("SELECT * FROM ban_logs")
        ban_logs = cursor.fetchall()
        if ban_logs:
            num_per_page = 1
            pages = (len(ban_logs) - 1) // num_per_page + 1
            page = max(1, min(page, pages))
            start_idx = (page - 1) * num_per_page
            end_idx = start_idx + num_per_page

            ban_logs_page = ban_logs[start_idx:end_idx]

            embed = discord.Embed(title=f"{ctx.guild.name}", color=0xff0000, timestamp=datetime.now(pytz.timezone('America/New_York')))
            for log in ban_logs_page:
                member = ctx.guild.get_member(log[1])
                member_name = log[2]

                embed.add_field(name=f"{member_name} ({log[1]})", value="", inline=False)
                embed.add_field(name="Reason", value=log[3], inline=False)
                embed.add_field(name="Duration", value=log[4], inline=False)
                embed.add_field(name="Ban Date", value=log[5], inline=False)
                embed.add_field(name="Unban Date", value=log[6], inline=False)
                embed.add_field(name="Total Bans", value=log[7], inline=False)
                if log[7] > 2:
                    if member:
                        await ctx.guild.ban(member, reason="Ban Limit Reached, Contact BOD+ to appeal.")
                    else:
                        await ctx.send(f"Unable to find member with ID '{log[1]}' to ban.")

            embed.set_footer(text=f"Page {page}/{pages}")
            message = await ctx.send(embed=embed)
            if pages > 1:
                await message.add_reaction('⬅️')
                await message.add_reaction('➡️')

            def check(reaction, user):
                return user == ctx.author and reaction.message.id == message.id and str(reaction.emoji) in ['⬅️', '➡️']

            current_page = page
            while True:
                try:
                    reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
                    if str(reaction.emoji) == '⬅️':
                        current_page = max(1, current_page - 1)
                    elif str(reaction.emoji) == '➡️':
                        current_page = min(pages, current_page + 1)

                    start_idx = (current_page - 1) * num_per_page
                    end_idx = start_idx + num_per_page
                    ban_logs_page = ban_logs[start_idx:end_idx]

                    embed.clear_fields()
                    for log in ban_logs_page:
                        member = ctx.guild.get_member(log[1])

                        embed.add_field(name=f"{member_name}", value="", inline=False)
                        embed.add_field(name="Reason:", value=log[3], inline=False)
                        embed.add_field(name="Duration:", value=log[4], inline=False)
                        embed.add_field(name="Ban Date:", value=log[5], inline=False)
                        embed.add_field(name="Unban Date:", value=log[6], inline=False)
                        embed.add_field(name="Total Bans:", value=log[7], inline=False)
                        if log[7] > 2:
                            if member:
                                await ctx.guild.ban(member, reason="Ban Limit Reached, Contact BOD+ to appeal.")
                            else:
                                await ctx.send(f"Unable to find member with ID '{log[1]}' to ban.")

                    embed.set_footer(text=f"Page {current_page}/{pages}")
                    await message.edit(embed=embed)
                    await message.remove_reaction(reaction, user)
                except asyncio.TimeoutError:
                    break

        else:
            await ctx.send("No bans have been logged yet.")
    else:
        await ctx.send("You do not have permission to view ban logs.")
        await log_command_execution(ctx, "bans")

@bot.hybrid_command(description='Unban a member')
async def unban(ctx, member_id: str, *, unban_reason: str):
    member_id = int(member_id)
    if ctx.author.guild_permissions.ban_members:
        cursor.execute("SELECT * FROM ban_logs WHERE member_id = ? AND unbanDate > ?", (member_id, datetime.utcnow()))
        ban_info = cursor.fetchone()
        
        if ban_info:
            member_name = ban_info[1]
            try:
                await ctx.guild.unban(discord.Object(id=member_id), reason=f"Unbanned by {ctx.author.display_name}")
                await ctx.send(f'{member_name} Was unbanned by {ctx.author.display_name}. For Reason: {unban_reason}', ephemeral=True)
                edt_datetime = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('America/New_York')).strftime('%B, %dth %Y: %I:%M %p (%H:%M:%S) %Z')
                cursor.execute("UPDATE ban_logs SET unbanDate = ? WHERE member_id = ?", (edt_datetime, member_id))
                conn.commit()
            except Exception as e:
                await ctx.send(f"Error: {e}", ephemeral=True)
        else:
            await ctx.send("No bans found for the specified member ID.")
    else:
        await ctx.send("You do not have permission to execute this command.", ephemeral=True)

@bot.hybrid_command(name='kick', description='Kick a member')
async def kick(ctx, member: discord.Member, *, reason):
    if ctx.author.guild_permissions.kick_members:
        try:
            cursor.execute("SELECT user_kicks FROM kick_logs WHERE member_id = ?", (member.id,))
            user_kicks_count = cursor.fetchone()
            if user_kicks_count:
                user_kicks[member.id] = user_kicks_count[0] + 1
            else:
                user_kicks[member.id] = 1
            #await member.kick(reason=reason)
            await ctx.send(f'{member.display_name} Was kicked by {ctx.author.display_name}. For Reason: {reason}', ephemeral=True)
            cursor.execute('SELECT name FROM sqlite_master WHERE type = "table" AND name = "kick_logs"')
            kick_log = cursor.fetchone()
            edt_datetime = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('America/New_York')).strftime('%B, %dth %Y: %I:%M %p (%H:%M:%S) %Z')
            if kick_log:
                cursor.execute("INSERT INTO kick_logs (member_id, member_name, kickDate, reason, user_kicks) VALUES (?,?,?,?)", (member.id, member.display_name, edt_datetime, reason, user_kicks[member.id]))
                conn.commit()
            else:
                  await ctx.send(f"No kick log DB found, creating one", ephemeral=True)
                  cursor.execute('''CREATE TABLE IF NOT EXISTS kick_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, member_id INTEGER, member_name TEXT, reason TEXT,kickDate TEXT,user_kicks INTEGER)''')
                  await ctx.send('New table created', ephemeral=True)
                  cursor.execute("INSERT INTO kick_logs (member_id, member_name, kickDate, reason, user_kicks) VALUES (?,?,?,?)", (member.id, member.display_name, edt_datetime, reason, user_kicks[member.id]))
                  conn.commit()
                  await ctx.send('New row added', ephemeral=True)
                  await ctx.send(f'{member.display_name} Was kicked by {ctx.author.display_name}. For Reason: {reason}', ephemeral=True)
        except Exception as e:
            await ctx.send(f"Error: {e}", ephemeral=True)
    else:
        await ctx.send("You do not have permission to execute this command.", ephemeral=True)
        await log_command_execution(ctx, "kick")

@bot.hybrid_command(description='View kick logs')
async def kicks(ctx, page: int = 1):
    if ctx.message.author.guild_permissions.kick_members:
        cursor.execute("SELECT * FROM kick_logs")
        kick_logs = cursor.fetchall()
        if kick_logs:
            num_per_page = 1
            pages = (len(kick_logs) - 1) // num_per_page + 1
            page = max(1, min(page, pages))
            start_idx = (page - 1) * num_per_page
            end_idx = start_idx + num_per_page

            kick_logs_page = kick_logs[start_idx:end_idx]

            embed = discord.Embed(title=f"{ctx.guild.name}", color=0xff0000, timestamp=datetime.now(pytz.timezone('America/New_York')))
            for log in kick_logs_page:
                member = ctx.guild.get_member(log[1])
                member_name = log[2]

                embed.add_field(name=f"{member_name} ({log[1]})", value="", inline=False)
                embed.add_field(name="Reason", value=log[3], inline=False)
                embed.add_field(name="Kick Date", value=log[4], inline=False)
                embed.add_field(name="Total Kicks", value=log[5], inline=False)
                if log[5] > 2:
                    if member:
                        await ban(member, duration='7d', ban_reason="Kick Limit Reached, Contact BOD+ to appeal.")
                        await ctx.send(f'{member.display_name} Was automatically banned by {communityBot}. For Reason: Kick limit reached.", ephemeral=True)')
                    else:
                        await ctx.send(f"Unable to find member with ID '{log[1]}' to kick.")

            embed.set_footer(text=f"Page {page}/{pages}")
            message = await ctx.send(embed=embed)
            if pages > 1:
                await message.add_reaction('⬅️')
                await message.add_reaction('➡️')

            def check(reaction, user):
                return user == ctx.author and reaction.message.id == message.id and str(reaction.emoji) in ['⬅️', '➡️']

            current_page = page
            while True:
                try:
                    reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
                    if str(reaction.emoji) == '⬅️':
                        current_page = max(1, current_page - 1)
                    elif str(reaction.emoji) == '➡️':
                        current_page = min(pages, current_page + 1)

                    start_idx = (current_page - 1) * num_per_page
                    end_idx = start_idx + num_per_page
                    kick_logs_page = kick_logs[start_idx:end_idx]

                    embed.clear_fields()
                    for log in kick_logs_page:
                        member = ctx.guild.get_member(log[1])

                        embed.add_field(name=f"{member_name} ({log[1]})", value="", inline=False)
                        embed.add_field(name="Reason", value=log[3], inline=False)
                        embed.add_field(name="Kick Date", value=log[4], inline=False)
                        embed.add_field(name="Total Kicks", value=log[5], inline=False)
                        if log[5] > 2:
                            if member:
                                await ban(member, duration='7d', ban_reason="Kick Limit Reached, Contact BOD+ to appeal.")
                                await ctx.send(f'{member.display_name} Was automatically banned by {communityBot}. For Reason: Kick limit reached.", ephemeral=True)')
                            else:
                                await ctx.send(f"Unable to find member with ID '{log[1]}' to kick.")

                    embed.set_footer(text=f"Page {current_page}/{pages}")
                    await message.edit(embed=embed)
                    await message.remove_reaction(reaction, user)
                except asyncio.TimeoutError:
                    break

        else:
            await ctx.send("No kicks have been logged yet.")
    else:
        await ctx.send("You do not have permission to view kick logs.")
        await log_command_execution(ctx, "Kicks")
    
# * Utility Commands * #

@bot.hybrid_command(description='Sync all commands')
async def sync(ctx: commands.Context):
    if ctx.author.id == 295430975368986624:
        try:
            await ctx.send("Synced Commands", ephemeral=True)
            await bot.tree.sync()
            await bot.tree.sync(guild=ctx.guild)  
        except Exception as e:
            await ctx.send(f'Error: {e}', ephemeral=True)
    else:
        await ctx.send("You do not have permission to execute this command", ephemeral=True)
        await log_command_execution(ctx, "sync")

@bot.hybrid_command(description='Change the prefix for the bot')
async def prefix(ctx: commands.Context, new_prefix: str):
    await bot.tree.sync()
    await bot.tree.set_prefix(new_prefix)
    await ctx.send(f'Prefix changed to {new_prefix}', ephemeral=True)


# ! Bot Termination Command ! #
@bot.hybrid_command(description='Remove {communityBot} from all servers and clean up all utilities')
async def remove(ctx: commands.Context):
    if ctx.author.id == 295430975368986624:
        try:
            # ? Delete bot messages in the current channel ? #
            deleted_count = 0
            async for message in ctx.channel.history(limit=100):
                if message.author == bot.user:
                    await message.delete()
                    deleted_count += 1
            await ctx.send(f"Deleted {deleted_count} {communityBot} messages.", ephemeral=True)

            # ? Remove all bot commands ? #
            for command in list(bot.commands):
                bot.remove_command(command.name)
            await ctx.send("Removed all bot commands.", ephemeral=True)

            # ? Leave all servers (guilds) ? #
            
            for guild in bot.guilds:
                try:
                    await guild.leave()
                    await ctx.send(f"Removed {communityBot} from all Community servers.", ephemeral=True)
                except Exception as e:
                    await ctx.send(f"Failed to remove bot from {guild.name}: {e}")
        
        except Exception as e:
            await ctx.send(f"An error occurred during cleanup: {e}")
    
    else:
        await ctx.send("You do not have permission to execute this command.")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.tree.sync()

bot.run(DISCORD_TOKEN)