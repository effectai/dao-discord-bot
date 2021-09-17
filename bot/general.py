import logging
from discord import Game
from discord.ext import commands
from tinydb import Query, where
from timeit import default_timer as timer


from modules.eos import calculate_dao_rank, signed_constitution, update_account, get_proposal
from modules.utils import create_embed, create_table, get_account_name_from_context, create_dao_embed

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
    @commands.group(invoke_without_command=True)
    async def proposals(self, ctx, *args):
        """Get proposals on the Effect DAO"""
        
        print('first arg is: ', args[0])

    @proposals.command()
    async def list(self, ctx):
        """List all proposals"""
        await ctx.trigger_typing()
        table = create_table(get_proposal())
        await ctx.send(f'```Proposals Overview\n\n{table}```')

    @proposals.command()
    async def find(self, ctx, id):
        """Get a proposal for a given id. You can find the id when running the `!proposals list` command"""
        if int(id) <= 0:
            await ctx.send("id cannot be smaller than 1.", delete_after=3.0)
        else:
            await ctx.trigger_typing()
            proposal = get_proposal(id=id)[0]
            embed = create_embed(self, proposal)
            await ctx.send(embed=embed)

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
        dao_embed = create_dao_embed(account_name, dao_rank)
        await ctx.send(embed=dao_embed)

    @commands.command()
    async def update(self, ctx, account_name=None):
        """Update DAO stats for account"""
        account_name = get_account_name_from_context(self.db, ctx, account_name)
        if not account_name:
            return await ctx.send('No EOS account linked to this user')

        user = update_account(self.db, account_name)
        if not user:
            return await ctx.send('Could not update account')

        await ctx.send('**Updated to dao rank {}**'.format(user['dao_rank']))

    @commands.command()
    async def unlink(self, ctx):
        """Unlink EOS account"""
        if self.db.remove(where('discord_id') == ctx.message.author.id):
            return await ctx.send('EOS account unlinked!')

        await ctx.send('No linked EOS account found!')

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info('Logged in as {0}!'.format(self.bot.user))
        await self.bot.change_presence(activity=Game(name='Effect Force'))
