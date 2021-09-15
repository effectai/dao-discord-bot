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


def sync_roles(discord_id, dao_rank):
    logger.info('Syncing Roles for {}, DAO rank {}'.format(discord_id, dao_rank))

    dao_rank_roles = [
        settings.DISCORD_DAO_RANK_1_ID,
        settings.DISCORD_DAO_RANK_2_ID,
        settings.DISCORD_DAO_RANK_3_ID,
        settings.DISCORD_DAO_RANK_4_ID,
        settings.DISCORD_DAO_RANK_5_ID,
        settings.DISCORD_DAO_RANK_6_ID,
        settings.DISCORD_DAO_RANK_7_ID,
        settings.DISCORD_DAO_RANK_8_ID,
        settings.DISCORD_DAO_RANK_9_ID,
        settings.DISCORD_DAO_RANK_10_ID
    ]

    # First remove all removable roles
    user_roles = get_member_and_roles(discord_id).json()['roles']
    for user_role in user_roles:
        if user_role in dao_rank_roles:
            remove_role(discord_id, user_role)

