import time
from typing import Dict, List, Optional, Tuple

import requests

import utility.args


class MadObj:
    def __init__(self, api, obj_id: int):
        assert obj_id >= 0
        self.id = obj_id
        self._data = {}
        self._api = api  # type:Api

    def _update_data(self):
        raise NotImplementedError

    @property
    def raw_data(self) -> dict:
        if not self._data:
            self._update_data()
        return self._data


class Geofence(MadObj):
    def __init__(self, api, geofence_id: int):
        super().__init__(api, geofence_id)
        self._sa = {}

    def _update_data(self):
        self._data = self._api.get_json(f'/api/geofence/{self.id}')

    @property
    def name(self) -> str:
        return self.raw_data['name']

    @property
    def fence_type(self) -> str:
        return self.raw_data['fence_type']

    @property
    def sub_areas(self) -> Dict[str, List[Tuple[float, float]]]:
        if not self._sa:
            self._sa = {}
            name = ''
            points = []
            for line in self.raw_data['fence_data']:  # type:str
                if line[0] == '[' and line[-1] == ']':
                    # save previous sub area
                    if points:
                        self._sa[name] = points
                    name = line[1:-1]
                    points = []
                else:
                    p, q = line.split(',')
                    points.append((float(p), float(q)))
            if points:
                self._sa[name] = points
        return self._sa


class Area(MadObj):
    def __init__(self, api, area_id: int, name: Optional[str] = None):
        super().__init__(api, area_id)
        self._name: Optional[str] = name
        self._sp: List[dict] = []
        self._gi: Optional[Geofence] = None

    def __repr__(self):
        return f"{self.name} ({self.id})"

    def _update_data(self):
        self._data = self._api.get_json(f'/api/area/{self.id}')

    @property
    def init(self) -> bool:
        return self.raw_data['init']

    @property
    def name(self) -> str:
        return self._name or self.raw_data['name']

    @property
    def mode(self):
        return self.raw_data['mode']

    @property
    def geofence_included(self) -> Optional[Geofence]:
        if not self._gi:
            id_ = self.raw_data.get('geofence_included', None)  # type:Optional[str]
            if id_ is None:
                return None
            self._gi = Geofence(self._api, int(id_[id_.rfind('/') + 1:]))
        return self._gi

    def recalculate(self, wait: bool = True, wait_initial: float = 5, wait_interval: float = 1):
        self._api.post(f'/api/area/{self.id}', call="recalculate")
        if wait:
            wait_interval = min(wait_initial, wait_interval)
            if not self.is_recalculating:
                # either, recalculation was incredibly quick (and we will waste wait_initial seconds), or it has not started yet
                wait_start = time.time()
                while time.time() - wait_start < wait_initial:
                    time.sleep(wait_interval)
                    if self.is_recalculating:
                        break
            # at this point recalculation should be running
            while self.is_recalculating:
                time.sleep(wait_interval)

    @property
    def is_recalculating(self) -> bool:
        return self.id in self._api.get_json('/recalc_status')

    @property
    def spawnpoints(self) -> List[dict]:
        if not self._sp:
            self._sp = []
            for index in range(len(self.geofence_included.sub_areas)):
                self._sp.extend(self._api.get_json('/get_spawn_details', area_id=self.id, event_id=1, mode='ALL', index=index))
        return self._sp

    @property
    def routecalc_id(self) -> int:
        id_ = self.raw_data['routecalc']  # type:str
        return int(id_[id_.rfind('/') + 1:])

    @property
    def routecalc(self) -> List[Tuple[float, float]]:
        data = [line.split(',') for line in self._api.get_json(f'/api/routecalc/{self.routecalc_id}')['routefile']]
        return [(float(lat), float(lon)) for lat, lon in data]

    @routecalc.setter
    def routecalc(self, data: List[Tuple[float, float]]):
        data = [','.join(map(str, line)) for line in data]
        self._api.patch(f'/api/routecalc/{self.routecalc_id}', routefile=data)


class Api:
    def __init__(self):
        args = utility.args.parse_args()
        self._mad_url: str = args['madmin_url']
        self._mad_auth = (args['madmin_user'], args['madmin_password']) if args['madmin_user'] else None
        self._areas = {}

    def _update_areas(self):
        areas = self.get_json('/api/area')['results']
        areas = {int(area_id[area_id.rfind('/') + 1:]): name for area_id, name in areas.items()}
        self._areas = {area_id: Area(self, area_id, name) for area_id, name in sorted(areas.items(), key=lambda k: k[0])}

    @property
    def areas(self) -> Dict[int, Area]:
        if not self._areas:
            self._update_areas()
        return self._areas

    def get(self, path: str, **kwargs):
        requests.get(self._mad_url + path, params=kwargs, auth=self._mad_auth)

    def get_json(self, path: str, **kwargs):
        return requests.get(self._mad_url + path, params=kwargs, auth=self._mad_auth).json()

    def post(self, path: str, **kwargs):
        requests.post(self._mad_url + path, json=kwargs, headers={'Content-Type': 'application/json-rpc'}, auth=self._mad_auth)

    def patch(self, path: str, **kwargs):
        requests.patch(self._mad_url + path, json=kwargs, auth=self._mad_auth)

    def apply_settings(self):
        self.get('/reload')
