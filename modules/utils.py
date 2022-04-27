from array import array
from datetime import datetime
from discord import Embed, Color
from eospy.types import convert_little_endian
from eospy.utils import int_to_hex, string_to_name
from prettytable.prettytable import DOUBLE_BORDER
from tinydb import Query
from prettytable import PrettyTable
import textwrap
from binascii import hexlify


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
    table.field_names = ["Id", "Proposal title", "Author", "Cycle", "Status", "Costs"]
    for row in data:
        # print(row, '\n')
        table.add_row([row['id'], textwrap.shorten(row['title'], width=53, placeholder="..."), row['author'], row['cycle'], row['status'], row['proposal_costs']])
    
    table.align["Costs"] = "r"
    return table

def create_embed(self, data, inline=True):
    embed = Embed(
        color=Color.blurple(),
        title=data['title'],
        url=data['url'],
        timestamp=datetime.now()
    )
    if 'description' in data:
        embed.description = data['description']

    embed.set_footer(icon_url=self.bot.user.avatar_url, text=data['footer_text'])

    for entry in data['body']:
        embed.add_field(name=entry, value=data['body'][entry], inline=inline)

    return embed

def is_BSC_address(address):
    return (len(address) == 42 or len(address) == 40)

def name_to_hex(name):
    return hexlify(convert_little_endian(string_to_name(name), 'Q')).decode()