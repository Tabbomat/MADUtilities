import utility.mad_api


def query_area_ids(api: utility.mad_api.Api, promt: str, mode: str = None):
    mode = (mode or "").strip(' \t\r\n\'"').lower()
    # fetch areas
    for area in api.areas.values():
        if mode == '' or mode == 'all' or area.mode in mode:
            print(f'{area.id}: {area.name}')
    areas_to_recalc = input(promt)
    # check if we want all areas or only specific ones
    if areas_to_recalc.lower().strip(' \t\r\n\'"') == 'all':
        return sorted(k for k, a in api.areas.items() if mode == '' or mode == 'all' or a.mode in mode)
    else:
        return list(map(int, areas_to_recalc.split(',')))
