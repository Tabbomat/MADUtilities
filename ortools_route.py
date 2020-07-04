from typing import List

import numpy as np
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

import utility.mad_api


def distance_matrix(coords):
    # see https://stackoverflow.com/a/29546836
    lat, lng = map(np.radians, zip(*coords))
    # calculate differences, essentially x.T - x
    dlat = lat[..., np.newaxis] - lat
    dlng = lng[..., np.newaxis] - lng
    # haversine
    cos_lat = np.cos(lat)
    a = np.sin(dlat / 2.0) ** 2 + np.multiply(np.outer(cos_lat, cos_lat), np.sin(dlng / 2.0) ** 2)
    c = 2 * np.arcsin(np.sqrt(a))
    return 6367 * c


def recalc_routecalc(routecalc: List[str], arbitrary_endpoints: bool = False) -> List[str]:
    # convert '12.345,67.890' to (12.345, 67.890)
    coords = [tuple(map(float, row.split(','))) for row in routecalc]
    num_coords = len(coords)

    if arbitrary_endpoints:
        # we need an additional fake point with distance==0 to all others
        num_coords += 1

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(num_coords, 1, num_coords - 1 if arbitrary_endpoints else 0)
    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # calculating distances, since distance matrix is symmetric, only calculate half
    # distances = [[int(1000 * geopy.distance.distance(from_coords, coords[to_index]).meters) for to_index in range(from_index)] for from_index, from_coords in enumerate(coords)]
    distances = distance_matrix(coords)

    def distance_callback(from_index, to_index):
        if from_index == to_index:
            # distance of a point to itself is 0
            return 0
        if arbitrary_endpoints and (from_index == num_coords - 1 or to_index == num_coords - 1):
            # distance to fake point is always 0, fake point is always last in list
            return 0
        return int(1000000 * distances[from_index][to_index])

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # return original routecalc if ortools failed to find a solution
    if not solution:
        return routecalc

    new_routecalc = []
    index = routing.Start(0)
    # skip fake point
    if arbitrary_endpoints:
        index = solution.Value(routing.NextVar(index))
    while not routing.IsEnd(index):
        new_routecalc.append(routecalc[manager.IndexToNode(index)])
        index = solution.Value(routing.NextVar(index))
    return new_routecalc


if __name__ == '__main__':
    # fetch areas
    areas = utility.mad_api.get_areas()
    for area_id, area_name in areas.items():
        print(f'{area_id[area_id.rfind("/") + 1:]:>4}: {area_name}')
    areas_to_recalc = input("Please input area ids of areas you want to recalculate separated by comma, or 'all' to recalc all areas:\n")
    # check if we want to recalc all areas or only specific ones
    if areas_to_recalc.lower().strip(' \t\r\n\'"') == 'all':
        area_ids = [int(area_id[area_id.rfind('/') + 1:]) for area_id in areas.keys()]
    else:
        area_ids = list(map(int, areas_to_recalc.split(',')))
    for i, area_id in enumerate(area_ids):
        # get old routecalc
        area = utility.mad_api.get_area(area_id)
        routecalc_id = int(area['routecalc'].split('/')[-1])
        mode = area['mode']
        old_route = utility.mad_api.get_routecalc_routefile(routecalc_id)
        print(f"Recalculating route for area {area['name']} ({i + 1}/{len(area_ids)})")
        # calculate new route
        new_route = recalc_routecalc(old_route, mode == 'pokestops')
        # set new route
        utility.mad_api.set_routecalc_routefile(routecalc_id, new_route)
    # apply settings if desired
    apply_settings = input("Do you want to apply the changes and reload? (y/N)  ").strip().lower()
    if apply_settings == 'y':
        utility.mad_api.apply_settings()
