import os

import requests


def get_qualified_discord_ids(qualification_id):
    res = requests.get(
        url='http://forceadmin.effect.ai/admin/resource/discord',
        headers={
            'Authorization': '{}'.format(os.environ['FORCE_API_TOKEN'])
        },
        params={
            'count': False,
            'filters[customFilters][qualifications][0]': qualification_id
        },
    )

    if res.status_code == 200:
        return [x['discordId'] for x in res.json()['data']]

    return None
