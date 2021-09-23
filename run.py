from bot.reminder import Reminder
from bot.custom_help import CustomHelp
import logging
import os

import settings

from discord.ext import commands
from tinydb import TinyDB

from bot.dm import DM
from bot.general import General
from bot.admin import Admin

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s: %(message)s', level=logging.INFO)

if __name__ == '__main__':
    bot = commands.Bot(command_prefix=settings.DISCORD_COMMAND_PREFIX)
    bot.help_command = CustomHelp()

    # Init DB
    db = TinyDB('/var/tinydb/db.json')
    # db = TinyDB('db.json')

    # Add Cogs here
    bot.add_cog(DM(bot, db))
    bot.add_cog(Reminder(bot, db))
    bot.add_cog(General(bot, db))
    bot.add_cog(Admin(bot, db))

    # Start bot
    bot.run(os.environ['DISCORD_BOT_TOKEN'])
