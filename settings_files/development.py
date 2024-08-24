from ._global import *

GUILD_IDS = os.getenv("GUILD_IDS")

GUILD_IDS = [int(guild_id) for guild_id in GUILD_IDS.split(",")]