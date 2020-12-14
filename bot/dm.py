import asyncio
import logging

from discord.ext import commands

from modules import verification
from modules.eos import get_transaction, verify_transaction
from modules.roles import sync_roles

logger = logging.getLogger(__name__)


class DM(commands.Cog):
    """Functionality that is only active in DM (Direct Message)"""
    db = None

    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild and not message.author.bot:
            user, created = verification.get_or_create_verification_status(self.db, message.author.id)

            if created:
                async with message.channel.typing():
                    await asyncio.sleep(1)
                    await message.channel.send('Hi, I am the Effect.AI verification bot! You can verify your EOS account with me, so you can show your DAO rank in the Effect Discord!')

                async with message.channel.typing():
                    await asyncio.sleep(3)
                    await message.channel.send('Send a transaction of **0.01 EOS** or **1 EFX** to **verify.efx** with memo **{}**'.format(user['code']))

                async with message.channel.typing():
                    await asyncio.sleep(3)
                    await message.channel.send('After you sent your transaction, send me your transaction id. For example: `https://bloks.io/transaction/c1d43dc222811402f4bc024ab6449c2c0be1b36fdb3c18a5c76678b3e3f81937`')
            elif user['account_name']:
                await message.channel.send('You are already verified! Your EOS account is **{}**.'.format(user['account_name']))
            else:
                hash = message.content.replace(' ', '')
                if 'http' in message.content:
                    hash = message.content.split('/')[-1]

                if not len(hash) == 64:
                    return await message.channel.send('That does not seem to be a valid transaction, example of valid transaction: `https://bloks.io/transaction/c1d43dc222811402f4bc024ab6449c2c0be1b36fdb3c18a5c76678b3e3f81937`')

                transaction = get_transaction(hash)
                if not transaction:
                    return await message.channel.send('I could not verify your transaction, if you just made the transaction it can take a minute before I can see it. Try again later.')

                user = verify_transaction(self.db, transaction)
                if not user:
                    return await message.channel.send('I could not verify your transaction, make sure to include the right memo.'.format(user['code']))

                await message.channel.send('**You are now verified!** Your EOS account name is **{}** and DAO rank **{}**.'.format(user['account_name'], user['dao_rank']))
                sync_roles(message.author.id, user['dao_rank'])
