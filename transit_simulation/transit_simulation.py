"""Main module."""

from loguru import logger
import geopandas as gpd
import numpy as np


def kmph_to_mps(speed_kms: float):
    """Helper function, given km/h, retun m/s"""
    speed_ms = speed_kms / 3.6
    return speed_ms

def second_to_hour(time_s: float):
    """Helper function, given seconds, return hours"""
    time_h = time_s / 60 / 60
    return time_h


def start_simulation(route_file: str):
    """simulation entry point, handel all simulation functions"""

    # data input
    route = gpd.read_file(route_file)

    # data analysis
    time = calculate_travel_time(route)

    # result ouput
    logger.info(f'total travel time: {time} seconds')

    return 0

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
