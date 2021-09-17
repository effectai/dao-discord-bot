import logging
import textwrap
import time
from datetime import datetime

from settings.defaults import category
import requests
from tinydb import Query

logger = logging.getLogger(__name__)

def ipfs_request(hash):
    req = requests.get(f'https://ipfs.effect.ai/ipfs/{hash}')
    
    logger.info('[IPFS] {}'.format(req.request.url))
    if req.status_code == 200:
        return req.json()

    return None

def node_request(endpoint, **kwargs):
    req = requests.post(
        url='https://eos.greymass.com/v1/chain/{}'.format(endpoint),
        **kwargs
    )

    logger.info('[EOS] {}'.format(req.request.url))
    if req.status_code == 200:
        return req.json()

    return None


def get_transaction(transaction_id):
    req = requests.post('https://api.eosflare.io/v1/eosflare/get_transaction', json={
        'id': transaction_id
    })

    if req.status_code == 200:
        data = req.json()
        if 'err_code' not in data:
            return data

    return None


def verify_transaction(db, transaction):
    """
    Checks transaction sender and memo, and if there is corresponding code in db
    Returns user if verification success else None
    """

    logger.info('Verifying Transaction {}'.format(transaction))

    hash = transaction['id']
    for action in transaction['trx']['trx']['actions']:
        tx_data = action['data']
        if not 'memo' in tx_data or not tx_data['memo']:
            continue

        account_name = tx_data['from']
        code = tx_data['memo']

        # Check if not already linked discord_id to this account
        User = Query()
        existing_user = db.search(User.account_name == account_name)
        if existing_user and existing_user['tx']:
            return None, 'This account is already linked to a different Discord user'

        user = db.search(User.code == code)
        if user and not user[0]['account_name']:
            user = user[0]

            if signed_constitution(account_name):
                user['account_name'] = account_name
                user['tx'] = hash
                user['dao_rank'] = calculate_dao_rank(account_name)
                user['last_update'] = int(time.time())

                db.update(user, User.code == code)
                return user, ''
            else:
                return None, 'You did not sign the constitution yet. Sign the constitution at https://dashboard.effect.ai/dao and send me your transaction again'

    return None, 'I could not verify your transaction, make sure to include the correct memo'

def get_proposal(id=None):
    data = None
    config = {
        'code': "daoproposals",
        'index_position': 1,
        'json': True,
        'reverse': False,
        'scope': "daoproposals",
        'show_payer': False,
        'table': "proposal",
        'upper_bound': ""         
    }
    
    if id is None:
        config.update({'limit': 10, 'lower_bound': "", "reverse": True})
    else:
        config.update({'limit': 1, 'lower_bound': str(id)})

    data = node_request('get_table_rows', json=config)

    if data:
        for row in data['rows']:
            # format data before returning.
            content = ipfs_request(row['content_hash'])
            row['url'] = 'https://dao.effect.network/proposals/{0}'.format(row['id'])
            proposal_link = ' [read more]({0})'.format(row['url'])
            row['proposal_costs'] = row['pay'][0]['field_0']['quantity'].replace("EFX", "**EFX**")
            row['title'] = content['title']
            row['description'] = textwrap.shorten(content['body'], width= 250, placeholder=proposal_link)
            row['category'] = category[row['category']]

        return data['rows']

def get_staking_details(account_name):
    data = node_request('get_table_rows', json={
        'code': 'efxstakepool',
        'scope': account_name,
        'table': 'stake',
        'json': True
    })

    efx_staked, nfx_staked = 0, 0
    last_claim_age, last_claim_time = 0, datetime.now()
    if data:
        for row in data['rows']:
            if 'EFX' in row['amount']:
                efx_staked = float(row['amount'].replace(' EFX', ''))
                last_claim_time = datetime.strptime(row['last_claim_time'], '%Y-%m-%dT%H:%M:%S')
                last_claim_age = int(row['last_claim_age'])
            elif 'NFX' in row['amount']:
                nfx_staked = float(row['amount'].replace(' NFX', ''))

    return efx_staked, nfx_staked, last_claim_age, last_claim_time


def calculate_stake_age(last_claim_age, last_claim_time):
    stake_age_limit = 1000 * 24 * 3600
    claim_stop_time = datetime.fromtimestamp(1604188799)

    if last_claim_time < claim_stop_time:
        stake_age_limit = 200 * 24 * 3600
        if datetime.now() > claim_stop_time:
            claim_diff = abs(datetime.now() - last_claim_time)
            last_claim_age = min(stake_age_limit, last_claim_age + claim_diff.total_seconds())
            last_claim_time = datetime.now()
            stake_age_limit = 1000 * 24 * 3600

    claim_diff = abs(datetime.now() - last_claim_time)
    return min(stake_age_limit, last_claim_age + claim_diff.total_seconds())


def calculate_power(efx_staked, last_claim_age, last_claim_time):
    stake_age = calculate_stake_age(last_claim_age, last_claim_time)
    return float(efx_staked + float(stake_age / (200 * 24 * 3600) * efx_staked))


def calculate_dao_rank(account_name):
    logger.info('Calculating DAO rank for {}'.format(account_name))

    efx_staked, nfx_staked, last_claim_age, last_claim_time = get_staking_details(account_name)
    power = calculate_power(efx_staked, last_claim_age, last_claim_time)

    requirements = [
        (0, 0),
        (200000, 10000),
        (348326, 15505),
        (606655, 24041),
        (1056569, 37276),
        (1840152, 57797),
        (3204864, 89615),
        (5581687, 138950),
        (9721233, 215443),
        (16930792, 334048),
        (29487176, 517947)
    ]

    current_rank = 0
    for i, (power_required, nfx_stake_required) in enumerate(requirements):
        if power >= power_required and nfx_staked >= nfx_stake_required:
            current_rank = i

    return current_rank


def signed_constitution(account_name):
    data = node_request('get_table_rows', json={
        'code': 'theeffectdao',
        'scope': 'theeffectdao',
        'upper_bound': account_name,
        'lower_bound': account_name,
        'table': 'member',
        'limit': 1,
        'json': True
    })

    if data:
        return data['rows']


def update_account(db, account_name):
    User = Query()
    user = db.search(User.account_name == account_name)

    if user and user[0]['account_name']:
        user = user[0]
        user['dao_rank'] = calculate_dao_rank(account_name)
        db.update(user, User.account_name == account_name)
        return user

    return None
