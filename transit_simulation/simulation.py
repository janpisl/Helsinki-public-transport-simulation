"""Main module."""

from loguru import logger
import geopandas as gpd
import numpy as np
from shapely.geometry import LineString, Point


def kmph_to_mps(speed_kms: float):
    """Helper function, given km/h, retun m/s"""
    speed_ms = speed_kms / 3.6
    return speed_ms

def second_to_hour(time_s: float):
    """Helper function, given seconds, return hours"""
    time_h = time_s / 60 / 60
    return time_h



def next_location_along_route(current_location: Point, route: LineString, distance: float):
    """Calculate where the `next_location` is when travelling `distance` along `route` from `location`
    Geometry object assumed to be shapley geometries"""

    current_distance = route.project(current_location)
    next_distance = current_distance + distance
    next_location = route.interpolate(next_distance)

    return next_location


def start_simulation(route_file: str):
    """simulation entry point, handel all simulation functions"""

    # data input
    route = gpd.read_file(route_file)

    # data analysis
    time = calculate_travel_time(route)

    return time

def calculate_travel_time(route) -> float:
    """given a pandas dataframe with line geometry, calculate the total travel time
    of all lines in seconds.
    TODO: do actual simulation :)"""

    # lets's pretend speed is 40 km/h
    route['speed_limit'] = kmph_to_mps(40)

    # length gives the polyline length in meters (or coordiante units?)
    distance = route['geometry'].length

    # highschool physics
    route['travel_time'] = distance / route['speed_limit']

    # sum of the travel time of all polylines
    total_seconds = route['travel_time'].sum()
    return total_seconds
