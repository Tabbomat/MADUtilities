import os
from datetime import datetime

import gpxpy.gpx

import utility.mad_api
import utility.utility

if __name__ == '__main__':
    api = utility.mad_api.Api()
    area_ids = utility.utility.query_area_ids(api, "Please input area ids of areas you want to download separated by comma, or 'all' to download all areas:\n")
    if not os.path.exists('download'):
        os.makedirs('download')
    for i, area_id in enumerate(area_ids):
        area = api.areas[area_id]
        print(f"Downloading route for area {area.name} ({i + 1}/{len(area_ids)})")
        route = area.routecalc
        gpx = gpxpy.gpx.GPX()
        # create track
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(gpx_track)
        # create segment
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)
        # create points
        for row in route:
            gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(*row))
        with open(f'download/{area.name}_{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.gpx', 'w') as output_file:
            output_file.write(gpx.to_xml())
