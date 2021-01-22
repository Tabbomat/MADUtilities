# MADUtilities

This is a collection of scripts used to manage [MAD](https://github.com/Map-A-Droid/MAD).

## ortools_route.py

This script interactively recalculates your routes using [OR-Tools](https://developers.google.com/optimization). OR-Tools requires 64 bit python. If your MAD installation runs on a 32 bit server (for example Raspberry Pi), you can run this script on a 64 bit machine to optimize your routes.

## overwrite_route.py

This script takes a route from a local text file (lines of `latitude, longitude`), optimizes the route with OR-Tools and overwrites the route of one area with this new route.

## download_route.py

This script allows you to download your routes as gpx files.