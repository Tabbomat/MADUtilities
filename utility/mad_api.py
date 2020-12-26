from typing import Dict, List

import requests

import utility.args

MAD_URL = utility.args.parse_args().madmin_url.rstrip('/')


def apply_settings():
    requests.get(MAD_URL + '/reload')


def get_areas() -> Dict[str, str]:
    return requests.get(MAD_URL + '/api/area').json().get('results')


def get_area(area_id: int):
    return requests.get(f'{MAD_URL}/api/area/{area_id}').json()


def get_routecalc_routefile(routecalc_id: int) -> List[str]:
    return requests.get(f'{MAD_URL}/api/routecalc/{routecalc_id}').json().get('routefile')


def set_routecalc_routefile(routecalc_id: int, routefile: List[str]):
    requests.patch(f'{MAD_URL}/api/routecalc/{routecalc_id}', json={'routefile': routefile})


def mad_recalc_area(area_id: int):
    requests.post(f'{MAD_URL}/api/area/{area_id}', json={"call": "recalculate"}, headers={'Content-Type': 'application/json-rpc'})


def get_recalc_status() -> List[int]:
    return requests.get(f'{MAD_URL}/recalc_status').json()
