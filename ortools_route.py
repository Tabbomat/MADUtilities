from typing import List, Tuple

import numpy as np
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

import utility.mad_api
import utility.utility


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


def recalc_routecalc(routecalc: List[Tuple[float, float]], arbitrary_endpoints: bool = False) -> List[Tuple[float, float]]:
    num_coords = len(routecalc)

    if arbitrary_endpoints:
        # we need an additional fake point with distance==0 to all others
        num_coords += 1

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(num_coords, 1, num_coords - 1 if arbitrary_endpoints else 0)
    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # calculating distances, since distance matrix is symmetric, only calculate half
    distances = distance_matrix(routecalc)

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
    api = utility.mad_api.Api()
    area_ids = utility.utility.query_area_ids(api, "Please input area ids of areas you want to recalculate separated by comma, or 'all' to recalc all areas:\n")
    do_mad_recalc = input("Do you want to trigger a MAD recalc before using ortools to calculate the routes? (Y/n) ").strip().lower() != 'n'
    for i, area_id in enumerate(area_ids):
        area = api.areas[area_id]
        print(f"Recalculating route for area {area.name} ({i + 1}/{len(area_ids)})")
        if do_mad_recalc:
            print(f"Using MAD to recalculate route")
            area.recalculate()
        # get old routecalc
        old_route = area.routecalc
        # check if area has a route (otherwise we can't and don't need to recalculate)
        if not old_route:
            print("Area has no route.")
            continue
        # calculate new route
        if not do_mad_recalc:
            print("Using ortools to recalculate route")
        # calculate and set new route
        area.routecalc = recalc_routecalc(old_route, area.mode == 'pokestops')
    # apply settings if desired
    if input("Do you want to apply the changes and reload? (y/N)  ").strip().lower() == 'y':
        api.apply_settings()
