import random
import string
import time

from tinydb import Query


def generate_verification_code(n):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))


def get_or_create_verification_status(db, discord_id):
    """
    Returns user, created (boolean)
    If user does not yet exists, create entry in db with random code
    """

    User = Query()

    exists = db.search(User.discord_id == discord_id)
    if exists:
        return exists[0], False

    data = {'discord_id': discord_id, 'code': generate_verification_code(6), 'tx': None, 'account_name': None, 'dao_rank': 0, 'last_update': int(time.time())}
    db.insert(data)

    return data, True
