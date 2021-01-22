from typing import Dict, List

import requests

import utility.args

ARGS = utility.args.parse_args()
MAD_URL = ARGS['madmin_url']
MAD_AUTH = (ARGS['madmin_user'], ARGS['madmin_password']) if ARGS['madmin_user'] else None


def apply_settings():
    requests.get(MAD_URL + '/reload', auth=MAD_AUTH)


def get_areas() -> Dict[str, str]:
    return requests.get(MAD_URL + '/api/area', auth=MAD_AUTH).json().get('results')


def get_area(area_id: int):
    return requests.get(f'{MAD_URL}/api/area/{area_id}', auth=MAD_AUTH).json()


def get_routecalc_routefile(routecalc_id: int) -> List[str]:
    return requests.get(f'{MAD_URL}/api/routecalc/{routecalc_id}', auth=MAD_AUTH).json().get('routefile')


def set_routecalc_routefile(routecalc_id: int, routefile: List[str]):
    requests.patch(f'{MAD_URL}/api/routecalc/{routecalc_id}', auth=MAD_AUTH, json={'routefile': routefile})


def mad_recalc_area(area_id: int):
    requests.post(f'{MAD_URL}/api/area/{area_id}', auth=MAD_AUTH, json={"call": "recalculate"}, headers={'Content-Type': 'application/json-rpc'})


def get_recalc_status() -> List[int]:
    return requests.get(f'{MAD_URL}/recalc_status', auth=MAD_AUTH).json()
