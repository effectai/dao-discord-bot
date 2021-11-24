import logging
import textwrap
import time
from datetime import datetime, timedelta
import eospy.cleos
import os
import eospy.keys
from eospy.types import Abi, Action
from eospy.utils import parse_key_file
import arrow
from modules.utils import is_BSC_address, name_to_hex
from settings.defaults import category
import requests
import pytz
from tinydb import Query

logger = logging.getLogger(__name__)

class EOS():
    def __init__(self):
        self.next_key = None
        self.more_proposals = None
        self.proposals = None
        self.ce = eospy.cleos.Cleos(url='https://jungle3.greymass.com:443')

    def ipfs_request(self, hash):
        req = requests.get(f'https://ipfs.effect.ai/ipfs/{hash}')
        
        # logger.info('[IPFS] {}'.format(req.request.url))
        if req.status_code == 200:
            return req.json()

        return None

    def node_request(self, endpoint, url='https://eos.greymass.com/v1/chain/{}', **kwargs):
        req = requests.post(
            url=url.format(endpoint),
            **kwargs
        )

        # logger.info('[EOS] {}'.format(req.request.url))
        if req.status_code == 200:
            return req.json()

        return None


    def get_transaction(self, transaction_id):
        req = requests.post('https://api.eosflare.io/v1/eosflare/get_transaction', json={
            'id': transaction_id
        })

        if req.status_code == 200:
            data = req.json()
            if 'err_code' not in data:
                return data

        return None

    def search_account (self, acc_name):
        """Check if account exists."""
        address = None
        acc_string = None
        try:
            if is_BSC_address(acc_name):
                address = acc_name[2] if len(acc_name) == 42 else acc_name
                acc_string = (name_to_hex('efxtoken1112') + '00' + address).ljust(64, '0')
            else:
                acc_string = (name_to_hex('efxtoken1112') + '01' + name_to_hex(acc_name)).ljust(64, '0')
            
            config = {
            'code': 'efxaccount11',
            'scope': 'efxaccount11',
            'index_position': 2,
            'key_type': "sha256",
            'lower_bound': acc_string,
            'upper_bound': acc_string,
            'table': 'account',
            'json': True,
            }

            data = self.node_request('get_table_rows', url='https://jungle3.greymass.com:443/v1/chain/{}', json=config)

            if not data['rows']:
                return data['rows'], False

            for row in data['rows']:
                if row['balance']['quantity'].endswith('EFX'):
                    return row, True

        except requests.exceptions.HTTPError as error:
            return error, False


    def transferTo(self, to_acc, amount=100.0000, memo="Happy Hackathon"):
        """Transfers x amounts of EFX to the sender."""

        arguments = {

            "from_id": 9, # vaccount id of faucetbotefx
            "to_id": int(to_acc),
            "quantity": {
                "quantity": f"{amount:.4f} EFX",
                "contract": 'efxtoken1112'
            },
            "memo": memo,
            "sig": None,
            "fee": None
        }
        payload = {
            "account": "efxaccount11",
            "name": "vtransfer",
            "authorization": [{
                "actor": "faucetbotefx",
                "permission": "active",
            }],
        }
        # Converting payload to binary
        data = self.ce.abi_json_to_bin(payload['account'], payload['name'], arguments)
        # Inserting payload binary form as "data" field in original payload
        payload['data'] = data['binargs']
        # final transaction formed
        trx = {"actions": [payload]}
        trx['expiration'] = str(
            (datetime.utcnow() + timedelta(seconds=60)).replace(tzinfo=pytz.UTC))

        key = eospy.keys.EOSKey(os.environ['DISCORD_BOT_PK'])

        return self.ce.push_transaction(trx, key, broadcast=True)

    def verify_transaction(self, db, transaction):
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

                if self.signed_constitution(account_name):

                    user['account_name'] = account_name
                    user['tx'] = hash
                    user['last_update'] = int(time.time())

                    db.update(user, User.code == code)
                    return user, ''
                else:
                    return None, 'You did not sign the constitution yet. Sign the constitution at https://dashboard.effect.ai/dao and send me your transaction again'

        return None, 'I could not verify your transaction, make sure to include the correct memo'

    def get_latest_proposal(self):

        config = {
            'code': "daoproposals",
            'scope': "daoproposals",
            'table': "proposal",
            'json': True,
            'limit': 1,
            'reverse': True,
        }
        data = self.node_request('get_table_rows', json=config)
        if 'rows' in data: return data['rows'][0]
        else: return None

    def clear_proposal(self):
        self.proposals = None

    def get_proposal(self, id=None, limit=20, ipfs=True):

        config = {
            'code': "daoproposals",
            'scope': "daoproposals",
            'table': "proposal",
            'json': True,
            'limit': limit
        }
        cycle_config = self.get_config()

        if id is not None:
            config = {
            'code': "daoproposals",
            'scope': "daoproposals",
            'table': "proposal",
            'json': True,
            'limit': 1,
            'lower_bound': str(id)
            }
            
            data = self.node_request('get_table_rows', json=config)

            if data and ipfs: 
                self.assign_statuses(data['rows'][0], cycle_config)
                self.format_proposal(data['rows'][0])
            return data['rows']

        
        if self.next_key: config['lower_bound'] = self.next_key 
                
        data = self.node_request('get_table_rows', json=config)

        self.more_proposals = data['more']
        self.next_key = data['next_key']

        if not self.proposals:
            self.proposals = data['rows']
        else: 
            self.proposals = [*self.proposals, *data['rows']]

        for proposal in self.proposals:
            
            self.assign_statuses(proposal, cycle_config)

            if proposal['status'] == 'ACTIVE' or proposal['status'] == 'PENDING':
                self.format_proposal(proposal)
    
        # Break statement
        if self.more_proposals: self.get_proposal(id, limit, ipfs)

        return self.proposals


    def assign_statuses(self, proposal, cycle_config):

        if 'status' not in proposal:
            proposal['status'] = 'CLOSED'
            if proposal['state'] == 0:
                if not proposal['cycle']:
                    proposal['status'] = 'DRAFT'
                else:
                    cycle = self.get_cycle(proposal['cycle'])
                    now_dt = arrow.utcnow().datetime
                    # check if cycle start time (including voting duration) datetime is greater than today's datetime
                    if cycle and proposal['cycle'] == cycle_config['current_cycle'] and arrow.get(cycle[0]['start_time']).shift(seconds= +cycle_config['cycle_voting_duration_sec']).datetime > now_dt:
                        proposal['status'] = 'ACTIVE'    
                    elif cycle and arrow.get(cycle[0]['start_time']).shift(seconds= +cycle_config['cycle_voting_duration_sec']).datetime < now_dt:
                        proposal['status'] = 'PROCESSING'
                    elif cycle and int(proposal['cycle']) < int(cycle_config['current_cycle']):
                        proposal['status'] = 'PROCESSING'
                    
                    else: proposal['status'] = 'PENDING'


    def format_proposal(self, proposal):
        content = self.ipfs_request(proposal['content_hash'])
        proposal['url'] = 'https://dao.effect.network/proposals/{0}'.format(proposal['id'])
        proposal_link = ' [read more]({0})'.format(proposal['url'])
        proposal['proposal_costs'] = proposal['pay'][0]['field_0']['quantity']
        proposal['title'] = content['title']
        proposal['description'] = textwrap.shorten(content['body'], width= 250, placeholder=proposal_link)
        proposal['category_name'] = category[proposal['category']]
        
        return proposal

    def get_staking_details(self, account_name):
        data = self.node_request('get_table_rows', json={
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


    def calculate_stake_age(self, last_claim_age, last_claim_time):
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


    def calculate_efx_power(self, efx_staked, stake_age):
        return float(efx_staked + float(stake_age / (200 * 24 * 3600) * efx_staked))

    def calculate_vote_power (self, efx_power = 0, nfx_staked = 0):
        efx = int(efx_power / 20)
        nfx = int(nfx_staked)
        return min(efx, nfx)

    def signed_constitution(self, account_name):
        data = self.node_request('get_table_rows', json={
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

    def get_config(self):
        config_data = self.node_request('get_table_rows', json={
            'code': "daoproposals",
            'index_position': 1,
            'json': True,
            'scope': "daoproposals",
            'show_payer': False,
            'table': "config",
        })

        config = config_data['rows'] if config_data else None
        
        return config[0]

    def get_cycle(self, id=None):
        if id:
            cycle_data = self.node_request('get_table_rows', json={
                'code': "daoproposals",
                'index_position': 1,
                'json': True,
                'reverse': True,
                'scope': "daoproposals",
                'show_payer': False,
                'limit': 1,
                'table': "cycle",
                'lower_bound': f"{id}"         
            })
        
        cycle = cycle_data['rows'] if cycle_data else None

        return cycle


    def update_account(self, db, discord_id, account_name):
        User = Query()
        user = db.search(User.discord_id == discord_id)

        if user and user[0]['account_name']:
            user = user[0]

            user['account_name'] = account_name
            user['last_update'] = int(time.time())

            db.update(user, User.account_name == account_name)
            return user

        return None
