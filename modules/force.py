import os

import requests


def get_qualified_discord_ids(qualification_ids):
    params = {'count': False}
    for i, qualification_id in enumerate(qualification_ids):
        params['filters[customFilters][qualifications][{}]'.format(i)] = qualification_id

    print(params)

    res = requests.get(
        url='http://forceadmin.effect.ai/admin/resource/discord',
        params=params,
        headers={
            'Authorization': '{}'.format(os.environ['FORCE_API_TOKEN'])
        },
    )

    if res.status_code == 200:
        return [x['discordId'] for x in res.json()['data']]

    return None
