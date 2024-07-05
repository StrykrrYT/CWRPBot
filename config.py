import sqlite3

TOKEN = 'MTI1NzQ0NDE4Nzk3NzE1NDY1MQ.Gf2UJH.CdTzTR3kzXr9lmvgf-bBaZHIV_D5wUNr4YrtkA'
GUILD_ID = 759962448491970561
allowed_roles = ["Chief Executive Officer", "Chief Operations Officer", "Discord Manager"]
communityBot = "CountryWideRP Official Bot"
communityBotLogo = "https://cdn.discordapp.com/avatars/295430975368986624/c6eb7ecc3a26fcc6e93ec493efcf1d7a.webp?size=128"
conn = sqlite3.connect('logs.db')
cursor = conn.cursor()
user_bans = {}
user_kicks = {}
user_warns = {}
user_mutes = {}