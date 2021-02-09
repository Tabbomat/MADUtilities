import os
import re

import utility.mad_api
from ortools_route import recalc_routecalc

if __name__ == '__main__':
    api = utility.mad_api.Api()
    # get filename for route file
    route_txt = input("path to route file: ").strip()
    while not (route_txt and os.path.isfile(route_txt)):
        route_txt = input("path is invalid, please try again: ").strip()
    # print area overview
    for area in api.areas.values():
        print(f'{area.id:>4}: {area.name}')
    area_id = int(input("Please input area id of area you want to overwrite: "))
    area = api.areas[area_id]
    # parse route file
    with open(route_txt) as input_file:
        old_route = [(float(m.group(1)), float(m.group(2))) for m in map(lambda line: re.match(r'(-?\d*\.?\d+),(-?\d*\.?\d+)', line), input_file.readlines()) if m]
    print("Using ortools to recalculate route")
    # calculate and set new route
    area.routecalc = recalc_routecalc(old_route, area.mode == 'pokestops')
    # apply settings if desired
    if input("Do you want to apply the changes and reload? (y/N)  ").strip().lower() == 'y':
        api.apply_settings()
