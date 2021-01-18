import logging
from discord import Game
from discord.ext import commands

from modules.eos import calculate_dao_rank, signed_constitution, update_account
from modules.utils import get_account_name_from_context

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
        account_name = get_account_name_from_context(self.db, ctx, account_name)
        if not account_name:
            return await ctx.send('No EOS account linked to this user')

        signed = signed_constitution(account_name)
        if not signed:
            return await ctx.send('{} did not sign the constitution!'.format(account_name))

        dao_rank = calculate_dao_rank(account_name)
        await ctx.send('{} has DAO rank {}'.format(account_name, dao_rank))

    @commands.command()
    async def update(self, ctx, account_name=None):
        """Update DAO stats for account"""
        account_name = get_account_name_from_context(self.db, ctx, account_name)
        if not account_name:
            return await ctx.send('No EOS account linked to this user')

        user = update_account(self.db, account_name)
        if not user:
            return await ctx.send('Could not update account')

        return await ctx.send('**Updated to dao rank {}'.format(user['dao_rank']))

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info('Logged in as {0}!'.format(self.bot.user))
        await self.bot.change_presence(activity=Game(name='Effect Force'))
