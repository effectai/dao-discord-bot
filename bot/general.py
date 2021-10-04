import logging

import discord
from settings.defaults import CATEGORY_IDS, ROLE_IDS
from discord.activity import Activity, ActivityType
from discord.ext import commands
from tinydb import where
import arrow
from bot.admin import Admin

from modules.utils import create_embed, create_table, get_account_name_from_context


logger = logging.getLogger(__name__)


class General(commands.Cog):
    """General bot functionality"""
    db = None

    def __init__(self, bot, db, eos):
        self.bot = bot
        self.db = db
        self.eos = eos

    @commands.command()
    async def ping(self, ctx):
        """Pong"""
        await ctx.send(':ping_pong: Pong!')
    @commands.group(invoke_without_command=True)
    async def proposals(self, ctx, *args):
        """Get proposals on the Effect DAO"""
        
    @proposals.command()
    async def create_channel(self, ctx, id):
        """Create important proposal channels"""
        if not Admin._sender_is_effect_member(ctx):
            return
    
        if int(id) <= 0:
            return await ctx.send("id cannot be smaller than 1.", delete_after=3.0)
        else:
            proposal = self.eos.get_proposal(id=id)[0]
            title = "#{0} {1}".format(proposal['id'], proposal['title'])

            data = {
                "title": title,
                "description": proposal['description'],
                "url": proposal['url'],
                "body": {
                    "Proposal id": proposal['id'],
                    "Status": proposal['status'],
                    "category": proposal['category'],
                    "author": proposal['author'],
                    "cycle": proposal['cycle'],
                    "proposal costs": proposal['proposal_costs'].replace('EFX', '**EFX**'),
                }
            }
            # reformat title so that it matches channel title.
            channel = discord.utils.get(ctx.guild.text_channels, name=title.replace(' ', '-').replace('#', '').lower())
            print(channel)
            if not channel:
                dao_member_role = discord.utils.get(ctx.guild.roles, id=ROLE_IDS['DISCORD_DAO_MEMBER_ID'])
                bot_role = discord.utils.get(ctx.guild.roles, id=ROLE_IDS['BOT_ID'])

                category = discord.utils.get(ctx.guild.categories, id=CATEGORY_IDS['DAO_PROPOSALS'])
                
                await category.set_permissions(dao_member_role, view_channel=True)
                await category.set_permissions(bot_role, view_channel=True)
                await category.set_permissions(ctx.guild.default_role, view_channel=False)

                channel = await ctx.guild.create_text_channel(title, category=category, sync_permissions=True)
                
                embed = create_embed(self, data)
                await channel.send(embed=embed)
            else:
                await ctx.trigger_typing()
                return await ctx.send('Channel already exists.')

    @proposals.command()
    async def list(self, ctx):
        """List all proposals"""
        await ctx.trigger_typing()
        proposals = self.eos.get_proposal(limit=30)
        # only let active and pending proposals through.
        filtered_proposals = [x for x in proposals if x['status'] == 'ACTIVE' or x['status'] == 'PENDING']

        table = create_table(filtered_proposals)
        await ctx.send(f'```Proposals Overview\n\n{table}```')

    @proposals.command()
    async def find(self, ctx, id):
        """Get a proposal for a given id. You can find the id when running the `!proposals list` command"""
        if int(id) <= 0:
            await ctx.send("id cannot be smaller than 1.", delete_after=3.0)
        else:
            await ctx.trigger_typing()
            proposal = self.eos.get_proposal(id=id)[0]

            data = {
                "title": "**#{0}** {1}".format(proposal['id'], proposal['title']),
                "description": proposal['description'],
                "url": proposal['url'],
                "body": {
                    "Proposal id": proposal['id'],
                    "Status": proposal['status'],
                    "category": proposal['category'],
                    "author": proposal['author'],
                    "cycle": proposal['cycle'],
                    "proposal costs": proposal['proposal_costs'].replace('EFX', '**EFX**'),
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

        signed = self.eos.signed_constitution(account_name)
        if not signed:
            return await ctx.send('{} did not sign the constitution!'.format(account_name))
        
        efx_staked, nfx_staked, last_claim_age, last_claim_time = self.eos.get_staking_details(account_name)
        stake_age = self.eos.calculate_stake_age(last_claim_age, last_claim_time)  
        efx_power = self.eos.calculate_efx_power(efx_staked, stake_age)
        vote_power = self.eos.calculate_vote_power(efx_power, nfx_staked)

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

        user = self.eos.update_account(self.db, ctx.author.id, account_name)
        if not user:
            return await ctx.send('Could not update your account')

        return await ctx.send('**Updated user {}**'.format(user['account_name']))

    @dao.command()
    async def unlink(self, ctx):
        """Unlink EOS account"""
        if self.db.remove(where('discord_id') == ctx.message.author.id):
            return await ctx.send('EOS account unlinked!')

        await ctx.send('No linked EOS account found!')

    @commands.command()
    async def cycle(self, ctx):
        """Show cycle stats, how long till the next cycle. etc."""
        config = self.eos.get_config()
        cycle = self.eos.get_cycle(config['current_cycle'])[0]
        
        now = arrow.utcnow()
        started_at = arrow.get(cycle['start_time'])
        started_at_str = started_at.humanize(now, granularity=["day", "hour", "minute"])
        started_at_dt = started_at.format("D MMMM YYYY HH:mm:ss ZZZ")

        ends_at = arrow.get(started_at.timestamp() + config['cycle_duration_sec'])    
        ends_at_str = ends_at.humanize(now, granularity=["day", "hour", "minute"])
        ends_at_dt = ends_at.format("D MMMM YYYY HH:mm:ss ZZZ")

        vote_duration = arrow.get(started_at.timestamp() + config['cycle_voting_duration_sec'])
        vote_duration_str = vote_duration.humanize(now, granularity=["day", "hour", "minute"])
        vote_duration_dt = vote_duration.format("D MMMM YYYY HH:mm:ss ZZZ")
        
        data = {
            "title": "Cycle details",
            "url": "https://dao.effect.network/proposals",
            "body": {
                "Current cycle": config['current_cycle'],
                "Cycle start time": "{0}\n(**{1}**)".format(started_at_dt, started_at_str),
                "Cycle end time": "{0}\n(**{1}**)".format(ends_at_dt, ends_at_str),
                "Voting time": "{0}\n(**{1}**)".format(vote_duration_dt, vote_duration_str),
                "Budget": cycle['budget'][0]['quantity'].replace("EFX", "**EFX**"),
            }
        }
        
        embed = create_embed(self, data, inline=False)
        return await ctx.send(embed=embed)
            
    @commands.Cog.listener()
    async def on_ready(self):
        
        logger.info('Logged in as {0}!'.format(self.bot.user))
        await self.bot.change_presence(activity=Activity(type=ActivityType.watching, name='EFX go to the moon!'))
        
