import logging
from discord.activity import Activity, ActivityType
from discord.ext import commands
from tinydb import Query, where

from modules.eos import calculate_efx_power, calculate_stake_age, calculate_vote_power, get_config, get_cycle, get_staking_details, signed_constitution, update_account, get_proposal
from modules.utils import create_embed, create_table, get_account_name_from_context


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

            data = {
                "title": "**#{0}** {1}".format(proposal['id'], proposal['title']),
                "description": proposal['description'],
                "url": proposal['url'],
                "body": {
                    "proposal costs": proposal['proposal_costs'].replace('EFX', '**EFX**'),
                    "category": proposal['category'],
                    "author": proposal['author'],
                    "cycle": proposal['cycle']
                }
            }

            embed = create_embed(self, data)
            await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    async def dao(self, ctx, *args):
        """General DAO functionalities. Such as showing account details."""

    @dao.command()
    async def account(self, ctx, account_name=None):
        """Get DAO stats for account"""
        account_name = get_account_name_from_context(self.db, ctx, account_name)
        if not account_name:
            return await ctx.send('No EOS account linked to {}'.format(ctx.author.display_name))

        signed = signed_constitution(account_name)
        if not signed:
            return await ctx.send('{} did not sign the constitution!'.format(account_name))
        
        efx_staked, nfx_staked, last_claim_age, last_claim_time = get_staking_details(account_name)
        stake_age = calculate_stake_age(last_claim_age, last_claim_time)  
        efx_power = calculate_efx_power(efx_staked, stake_age)
        vote_power = calculate_vote_power(efx_power, nfx_staked)

        data = {
            "title": "Account details",
            "url": "https://dao.effect.network/account/{}".format(account_name),
            "body": {
                "DAO Account": account_name,
                "EFX staked": efx_staked,
                "NFX staked": nfx_staked,
                "Vote Power": vote_power
            }
        }

        embed = create_embed(self, data, inline=False)
        return await ctx.send(embed=embed)

    @dao.command()
    async def update(self, ctx, account_name=None):
        """Update DAO stats for your account"""
        account_name = get_account_name_from_context(self.db, ctx, account_name)
        if not account_name:
            return await ctx.send('No EOS account linked to this user')

        user = update_account(self.db, ctx.author.id, account_name)
        if not user:
            return await ctx.send('Could not update your account')

        await ctx.send('**Updated user {}**'.format(user['account_name']))

    @dao.command()
    async def unlink(self, ctx):
        """Unlink EOS account"""
        if self.db.remove(where('discord_id') == ctx.message.author.id):
            return await ctx.send('EOS account unlinked!')

        await ctx.send('No linked EOS account found!')

    @commands.command()
    async def cycle(self, ctx):
        """Show cycle stats, how long till the next cycle. etc."""
        config = get_config()
        cycle = get_cycle(config['current_cycle'])
        

        print(config, cycle)
    
    @commands.Cog.listener()
    async def on_ready(self):
        logger.info('Logged in as {0}!'.format(self.bot.user))
        await self.bot.change_presence(activity=Activity(type=ActivityType.watching, name='EFX go to the moon!'))
        
