import os
from datetime import datetime

import gpxpy.gpx

import utility.mad_api as mad_api

if __name__ == '__main__':
    areas = mad_api.get_areas()
    for area_id, area_name in areas.items():
        print(f'{area_id[area_id.rfind("/") + 1:]:>4}: {area_name}')
    areas_to_download = input("Please input area ids of areas you want to download separated by comma, or 'all' to download all areas:\n")
    if areas_to_download.lower().strip(' \t\r\n\'"') == 'all':
        area_ids = [int(area_id[area_id.rfind('/') + 1:]) for area_id in areas.keys()]
    else:
        area_ids = list(map(int, areas_to_download.split(',')))
    if not os.path.exists('download'):
        os.makedirs('download')
    for i, area_id in enumerate(area_ids):
        # get old routecalc
        area = mad_api.get_area(area_id)
        routecalc_id = int(area['routecalc'].split('/')[-1])
        print(f"Downloading route for area {area['name']} ({i + 1}/{len(area_ids)})")
        route = mad_api.get_routecalc_routefile(routecalc_id)
        gpx = gpxpy.gpx.GPX()
        # create track
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(gpx_track)
        # create segment
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)
        # create points
        for row in route:
            gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(*map(float, row.split(','))))
        with open(f'download/{area["name"]}_{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.gpx', 'w') as output_file:
            output_file.write(gpx.to_xml())
