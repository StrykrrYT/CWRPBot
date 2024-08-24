import os

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN', False)


# MongoDB Configuration
MONGODB_HOST = os.getenv("MONGODB_HOST")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")
MONGODB_USER = os.getenv("MONGODB_USER")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")

# Allowed Roles
allowed_roles = ["Chief Executive Officer", "Chief Operations Officer", "Discord Manager"]
communityBot = "CountryWideRP Official Bot"
communityBotLogo = "https://cdn.discordapp.com/avatars/295430975368986624/c6eb7ecc3a26fcc6e93ec493efcf1d7a.webp?size=128"