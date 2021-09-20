from datetime import datetime
from discord import Embed, Color
from prettytable.prettytable import DOUBLE_BORDER
from tinydb import Query
from prettytable import PrettyTable
import textwrap


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

def create_table(data):
    # max title size: 50 chars.
    # TODO: Need to get actual title from IPFS but think about caching proposals so that you dont have to hit the blockchain everytime.
    table = PrettyTable(border=True, header=True)
    table.set_style(DOUBLE_BORDER)
    table.field_names = ["Id", "Proposal title", "Author", "Cycle", "Category", "Costs"]
    for row in data:
        # print(row, '\n')
        table.add_row([row['id'], textwrap.shorten(row['title'], width=53, placeholder="..."), row['author'], row['cycle'], row['category'], row['proposal_costs']])
    
    table.align["Costs"] = "r"
    return table

def create_embed(self, data):
    embed = Embed(
        color= Color.blurple(),
        title= ("**#{0}**  ".format(data['id'])) + data['title'],
        description= data['description'],
        url= data['url'],
        timestamp= datetime.now()
    )
    embed.set_footer(icon_url=self.bot.user.avatar_url, text="Effect DAO")
    embed.add_field(name="proposal costs", value=data['proposal_costs'].replace('EFX', '**EFX**'))
    embed.add_field(name="category", value=data['category'])
    embed.add_field(name="author", value=data['author'])
    embed.add_field(name="cycle", value=data['cycle'])

    return embed

def create_dao_embed(account_name, efx_staged, nfx_staged, vote_power):
    embed = Embed(
        color= Color.blurple(),
        title= "Account details",
        url= "https://dao.effect.network/account/{}".format(account_name),
    )
    
    embed.set_thumbnail(url='https://avatar.pixeos.art/avatar/{}'.format(account_name))
    embed.add_field(name='DAO Account', value=account_name, inline=False)
    embed.add_field(name='EFX staked', value=efx_staged, inline=False)
    embed.add_field(name='NFX staked', value=nfx_staged, inline=False)
    embed.add_field(name='Vote Power', value=vote_power, inline=False)
    return embed