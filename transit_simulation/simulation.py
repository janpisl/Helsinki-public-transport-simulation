"""Main module."""

from loguru import logger
import geopandas as gpd
import numpy as np
from shapely.geometry import LineString, Point

EUREF_FIN_TM35_FIN_EPSG  = 'EPSG:102139'

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


def start_simulation(data_dir: str):
    """simulation entry point, handel all simulation functions"""

    environment = {
        'speed_limit': gpd.read_file(f'{data_dir}/env_speed_limit.geojosn').to_crs(EUREF_FIN_TM35_FIN_EPSG)
    }
    # shall be a file with linestirng geometry, each line has uinque id attribute
    # may be used for both generic agetns, and public transport
    # if routes get big, use geopackage instead. But this is convenient for debugging
    routes = gpd.read_file(f'{data_dir}/routes.geojson').to_crs(EUREF_FIN_TM35_FIN_EPSG)

    # table of timestamps (iso8601 sting, or seconds since an epoch)
    schedule = gpd.pd.read_csv(f'{data_dir}/schedule.csv')


    agents = []
    sim_time_max = 500   # how many seconds in a simulation
    tick_len = 1         # how many seconds in a tick
    tick_current = 0
    sim_time = 0
    while sim_time < sim_time_max:

        new_agents = schedule[sim_time <= schedule.start_time < sim_time + tick_len]

        for new_agent in new_agents:
            agents.append(Agent(
                route = routes[new_agent.route_id],
            ))

        for idx, agent in agents:
            agent.tick(tick_len)
            del agents[idx] if agent.done else pass


        sim_time += tick_len


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
