import logging
import textwrap
import time
from datetime import datetime

from settings.defaults import category
import requests
from tinydb import Query

logger = logging.getLogger(__name__)

class EOS():
    def __init__(self):
        self.next_key = None
        self.more_proposals = None
        self.proposals = None
    
    def ipfs_request(self, hash):
        req = requests.get(f'https://ipfs.effect.ai/ipfs/{hash}')
        
        logger.info('[IPFS] {}'.format(req.request.url))
        if req.status_code == 200:
            return req.json()

        return None

    def node_request(self, endpoint, **kwargs):
        req = requests.post(
            url='https://eos.greymass.com/v1/chain/{}'.format(endpoint),
            **kwargs
        )

        logger.info('[EOS] {}'.format(req.request.url))
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

    def get_all_proposals(self):
        """"""
        config = {
            'code': "daoproposals",
            'scope': "daoproposals",
            'table': "proposal",
            'json': True,
            'limit': 20
        }

        if self.next_key: config['lower_bound'] = self.next_key 
        
        data = self.node_request('get_table_rows', json=config)
        
        self.more_proposals = data['more']
        self.next_key = data['next_key']

        if not self.proposals:
            print("")
            self.proposals = data['rows']
        else: 
            self.proposals = [*self.proposals, *data['rows']]

        for proposal in self.proposals:
            status = None
            if not proposal['status']:
                status = 'CLOSED'
            if proposal['state'] == 0:
                if not proposal['cycle']:
                    status = 'DRAFT'
                else:
                    if proposal['cycle'] == self.get_config()['current_cycle']:


                        """
                        if (proposalCycle && proposal.cycle === this.$dao.proposalConfig.current_cycle && this.$moment(proposalCycle.start_time + 'Z').add(this.$dao.proposalConfig.cycle_voting_duration_sec, 'seconds').isAfter()) {
                            status = 'ACTIVE'
                        } else if (proposalCycle && this.$moment(proposalCycle.start_time + 'Z').add(this.$dao.proposalConfig.cycle_voting_duration_sec, 'seconds').isBefore()) {
                            status = 'PROCESSING'
                        } else if (proposalCycle && proposal.cycle < this.currentCycle) {
                           status = 'PROCESSING'
                        } else {
                           status = 'PENDING'
                        }
                        """

                        # ACTIVE
                    elif True:
                        # Processing 
                    elif True:
                        # Processing
                    else:
                        # PENDING

        # Break statement
        if self.more_proposals: self.get_all_proposals()



    def get_proposal(self, id=None, ipfs=True, limit=10):
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
            config.update({'limit': limit, 'lower_bound': "", "reverse": True})
        else:
            config.update({'limit': 1, 'lower_bound': str(id)})

        data = self. node_request('get_table_rows', json=config)
        if data:
            for row in data['rows']:
                # format data before returning.
                if ipfs:        
                    content = self.ipfs_request(row['content_hash'])
                    row['url'] = 'https://dao.effect.network/proposals/{0}'.format(row['id'])
                    proposal_link = ' [read more]({0})'.format(row['url'])
                    row['proposal_costs'] = row['pay'][0]['field_0']['quantity']
                    row['title'] = content['title']
                    row['description'] = textwrap.shorten(content['body'], width= 250, placeholder=proposal_link)
                    row['category'] = category[row['category']]

            return data['rows']

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
