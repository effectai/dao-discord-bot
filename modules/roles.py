import settings
import requests
import os
import logging

logger = logging.getLogger(__name__)


def _request(*args, **kwargs):
    kwargs['url'] = 'https://discord.com/api/v8/{}'.format(kwargs['url'])
    headers = {'Authorization': 'Bot {}'.format(os.environ['DISCORD_BOT_TOKEN'])}
    return requests.request(*args, **kwargs, headers=headers)


def get_member_and_roles(discord_id):
    logger.info('Get Guild Member {}'.format(discord_id))
    return _request(method='GET', url='guilds/{}/members/{}'.format(settings.DISCORD_SERVER_ID, discord_id))


def set_role(discord_id, role_id):
    logger.info('Set Role {} for Member {}'.format(role_id, discord_id))
    return _request(method='PUT', url='guilds/{}/members/{}/roles/{}'.format(settings.DISCORD_SERVER_ID, discord_id, role_id))


def remove_role(discord_id, role_id):
    logger.info('Remove Role {} for Member {}'.format(role_id, discord_id))
    return _request(method='DELETE', url='guilds/{}/members/{}/roles/{}'.format(settings.DISCORD_SERVER_ID, discord_id, role_id))

def sync_roles(discord_id):
    logger.info(f'Syncing Roles for {discord_id}')


    # Set applicable roles
    applicable_roles = [settings.DISCORD_DAO_MEMBER_ID]

    for role in applicable_roles:
        set_role(discord_id, role)