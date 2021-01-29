import logging
import os

import settings

from discord.ext import commands
from tinydb import TinyDB

from bot.dm import DM
from bot.general import General

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s: %(message)s', level=logging.INFO)

if __name__ == '__main__':
    bot = commands.Bot(command_prefix=settings.DISCORD_COMMAND_PREFIX)

    # Init DB
    db = TinyDB('/var/tinydb/db.json')
    # db = TinyDB('db.json')

    # Add Cogs here
    bot.add_cog(DM(bot, db))
    bot.add_cog(General(bot, db))

    # Start bot
    bot.run(os.environ['DISCORD_BOT_TOKEN'])
