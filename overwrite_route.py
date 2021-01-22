import os
import re

import utility.mad_api
from ortools_route import recalc_routecalc

if __name__ == '__main__':
    # get filename for route file
    route_txt = input("path to route file: ").strip()
    while not (route_txt and os.path.isfile(route_txt)):
        route_txt = input("path is invalid, please try again: ").strip()
    # fetch areas
    areas = utility.mad_api.get_areas()
    for area_id, area_name in areas.items():
        print(f'{area_id[area_id.rfind("/") + 1:]:>4}: {area_name}')
    area_id = int(input("Please input area id of area you want to overwrite: "))
    area = utility.mad_api.get_area(area_id)
    routecalc_id = int(area['routecalc'].split('/')[-1])

    # parse route file
    with open(route_txt) as input_file:
        old_route = [line for line in input_file.readlines() if re.match(r'-?\d*\.?\d+,-?\d*\.?\d+', line)]
    print("Using ortools to recalculate route")
    new_route = recalc_routecalc(old_route, area['mode'] == 'pokestops')
    # set new route
    utility.mad_api.set_routecalc_routefile(routecalc_id, new_route)
    # apply settings if desired
    if input("Do you want to apply the changes and reload? (y/N)  ").strip().lower() == 'y':
        utility.mad_api.apply_settings()
