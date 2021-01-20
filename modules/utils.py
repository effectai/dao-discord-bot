from discord import Embed
from tinydb import Query


def cool_number(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0

    ft = '%.{}f%s'.format(1 if magnitude >= 2 else 0)
    return ft % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])


def get_account_name_from_context(db, ctx, account_name):
    if account_name and '<' not in account_name:
        return account_name

    discord_id = ctx.message.author.id
    if ctx.message.mentions:
        discord_id = ctx.message.mentions[0].id

    if discord_id:
        User = Query()
        user = db.search(User.discord_id == discord_id)
        if user:
            return user[0]['account_name']

    return None


def create_dao_embed(account_name, dao_rank):
    embed = Embed(color=color_for_rank(dao_rank))
    embed.set_thumbnail(url='https://avatar.pixeos.art/avatar/{}'.format(account_name))
    embed.add_field(name='Account name', value=account_name, inline=True)
    embed.add_field(name='DAO rank', value=dao_rank, inline=True)
    return embed


def color_for_rank(rank):
    return [
        0x000000,
        0x71E3C0,
        0xF8D247,
        0x57C0F9,
        0x8026F5,
        0xEA36AC,
        0xFB2B11,
        0x181818,
        0xE43AFF,
        0xFF6FEB,
        0xFFA6F1
    ][rank]
