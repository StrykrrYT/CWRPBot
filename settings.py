import os
DEBUG = os.getenv('DEBUG', False)

if DEBUG:
  print("We are in debug")
  from pathlib import Path
  from dotenv import load_dotenv
  env_path = Path('./bot/') / '.env.debug'
  load_dotenv(dotenv_path=env_path)
  from settings_files.development import *
else:
  print("We are in production")
  from settings_files.production import *

import pathlib
BASE_DIR = pathlib.Path(__file__).parent

COGS_DIR = BASE_DIR / 'COGS'