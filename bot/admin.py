import logging
from discord.ext import commands

import settings
from modules.force import get_qualified_discord_ids
from modules.roles import set_role

logger = logging.getLogger(__name__)


class Admin(commands.Cog):
    """Admin functionality"""
    db = None

    def __init__(self, bot, db, eos):
        self.bot = bot
        self.db = db
        self.eos = eos

    @staticmethod
    def _sender_is_effect_member(ctx):
        for role in ctx.author.roles:
            if str(role.id) == settings.DISCORD_EFFECT_TEAM_ROLE_ID:
                return True

        return False

    @commands.command()
    async def qualify(self, ctx, qualification_ids, role):
        if not Admin._sender_is_effect_member(ctx):
            return

        qualification_ids = qualification_ids.split(',')
        role_id = role.replace('<@', '').replace('>', '').replace('&', '')
        discord_ids = get_qualified_discord_ids(qualification_ids)
        if not discord_ids:
            return await ctx.send('No Discord users on Force with this qualification.')

        for discord_id in discord_ids:
            set_role(discord_id, role_id)
            await ctx.send('Assigned role to <@{}>'.format(discord_id))

        return await ctx.send('Done!')