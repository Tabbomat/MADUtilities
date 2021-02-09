import functools
from typing import Dict, List

import requests

import utility.args

ARGS = utility.args.parse_args()
MAD_URL = ARGS['madmin_url']
MAD_AUTH = (ARGS['madmin_user'], ARGS['madmin_password']) if ARGS['madmin_user'] else None


# some_api_function.cache_clear() clears the cache, if necessary

def apply_settings():
    requests.get(MAD_URL + '/reload', auth=MAD_AUTH)


@functools.lru_cache()
def get_areas() -> Dict[str, str]:
    return requests.get(MAD_URL + '/api/area', auth=MAD_AUTH).json().get('results')


@functools.lru_cache()
def get_area_ids() -> List[int]:
    return [int(area_id[area_id.rfind('/') + 1:]) for area_id in get_areas().keys()]


@functools.lru_cache()
def get_area(area_id: int) -> dict:
    return requests.get(f'{MAD_URL}/api/area/{area_id}', auth=MAD_AUTH).json()


def get_routecalc_routefile(routecalc_id: int) -> List[str]:
    return requests.get(f'{MAD_URL}/api/routecalc/{routecalc_id}', auth=MAD_AUTH).json().get('routefile')


def set_routecalc_routefile(routecalc_id: int, routefile: List[str]):
    requests.patch(f'{MAD_URL}/api/routecalc/{routecalc_id}', auth=MAD_AUTH, json={'routefile': routefile})


def mad_recalc_area(area_id: int):
    requests.post(f'{MAD_URL}/api/area/{area_id}', auth=MAD_AUTH, json={"call": "recalculate"}, headers={'Content-Type': 'application/json-rpc'})


def get_recalc_status() -> List[int]:
    return requests.get(f'{MAD_URL}/recalc_status', auth=MAD_AUTH).json()


@functools.lru_cache()
def get_geofence(geofence_id: int) -> dict:
    return requests.get(f'{MAD_URL}/api/geofence/{geofence_id}', auth=MAD_AUTH).json()


@functools.lru_cache()
def get_spawnpoints(area_id: int, index: int = 0, event_id: int = 1) -> List[dict]:
    # result is list of dicts like {"id":123456,"lastnonscan":"2020-12-15 18:43:37","lastscan":"1970-01-01 00:00:00","lat":12.345,"lon":56.789}
    return requests.get(f'{MAD_URL}/get_spawn_details', params={'area_id': area_id, 'event_id': event_id, 'mode': 'ALL', 'index': index}, auth=MAD_AUTH).json()


@functools.lru_cache()
def get_all_spawnpoints(area_id: int, event_id: int = 1) -> List[dict]:
    # similar to get_spawnpoints, but joins data over all possible index values
    result = []
    for index in range(get_number_of_geofences(get_geofence_included_id(area_id))):
        result.extend(get_spawnpoints(area_id, index, event_id))
    return result


@functools.lru_cache()
def get_geofence_included_id(area_id: int) -> int:
    area = get_area(area_id)
    if 'geofence_included' in area.keys():
        geofence_included = area['geofence_included']  # type:str
        return int(geofence_included[geofence_included.rfind('/') + 1:])
    return -1


@functools.lru_cache()
def get_number_of_geofences(geofence_id: int) -> int:
    geofence = get_geofence(geofence_id)
    # each geofence starts with a line containing [name]
    return sum(1 for line in geofence['fence_data'] if line[0] == '[' and line[-1] == ']')
