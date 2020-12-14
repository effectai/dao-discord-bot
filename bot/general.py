import logging
from discord import Game
from discord.ext import commands
from tinydb import Query

from modules.eos import calculate_dao_rank

logger = logging.getLogger(__name__)


class General(commands.Cog):
    """General bot functionality"""
    db = None

    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    @commands.command()
    async def ping(self, ctx):
        """Pong"""
        await ctx.send(':ping_pong: Pong!')

    @commands.command()
    async def dao(self, ctx, account_name=None):
        """Get DAO stats for account"""

        discord_id = None
        if not account_name:
            discord_id = ctx.message.author.id
        if ctx.message.mentions:
            discord_id = ctx.message.mentions[0].id

        if discord_id:
            User = Query()
            user = self.db.search(User.discord_id == discord_id)
            if not user:
                return await ctx.send('No EOS account linked to this user')

            account_name = user['account_name']

        dao_rank = calculate_dao_rank(account_name)
        await ctx.send('{} has DAO rank {}'.format(account_name if not discord_id else '<@{}>'.format(discord_id), dao_rank))

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info('Logged in as {0}!'.format(self.bot.user))
        await self.bot.change_presence(activity=Game(name='Effect Force'))
