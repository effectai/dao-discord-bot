import logging
from discord import Game
from discord.ext import commands

logger = logging.getLogger(__name__)


class General(commands.Cog):
    """General bot functionality"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Pong"""
        await ctx.send(":ping_pong: Pong!")

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info('Logged in as {0}!'.format(self.bot.user))
        await self.bot.change_presence(activity=Game(name='Effect Force'))
