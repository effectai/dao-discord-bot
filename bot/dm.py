import asyncio
import logging

from discord.ext import commands

import settings
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
        if not message.guild and not message.author.bot and settings.DISCORD_COMMAND_PREFIX not in message.content:
            user, created = verification.get_or_create_verification_status(self.db, message.author.id)

            if created:
                async with message.channel.typing():
                    await asyncio.sleep(1)
                    await message.channel.send('Hi, I am the Effect.AI verification bot! You can verify your EOS account with me!')

                async with message.channel.typing():
                    await asyncio.sleep(3)
                    await message.channel.send('**How to verify:** Send a transaction of **0.01 EOS** or **1 EFX** to `verify.efx` with memo `{}`'.format(user['code']))

                async with message.channel.typing():
                    await asyncio.sleep(3)
                    await message.channel.send('After you sent your transaction, send me your transaction id. For example: `https://bloks.io/transaction/484d7b15ac63367fb29258059584a739409f1f7ed1829e05c53050db6485c6f9`')
            elif user['account_name']:
                await message.channel.send('You are already verified! Your EOS account is **{}**.'.format(user['account_name']))
            else:
                tx_hash = message.content.replace(' ', '')
                if 'http' in message.content:
                    tx_hash = message.content.split('/')[-1]

                if not len(tx_hash) == 64:
                    return await message.channel.send('That does not seem to be a valid transaction, example of valid transaction: `https://bloks.io/transaction/484d7b15ac63367fb29258059584a739409f1f7ed1829e05c53050db6485c6f9`')

                transaction = get_transaction(tx_hash)
                if not transaction:
                    return await message.channel.send('I could not verify your transaction, if you just made the transaction it can take a minute before I can see it. Try again later.')

                updated_user, response = verify_transaction(self.db, transaction)
                if not updated_user:
                    return await message.channel.send(response)

                await message.channel.send('**You are now verified!** Your EOS account name is **{}** and DAO rank **{}**.'.format(updated_user['account_name'], updated_user['dao_rank']))
                sync_roles(message.author.id)
