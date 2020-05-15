"""Main module."""

from loguru import logger
import geopandas as gpd
import numpy as np
from typing import List
from shapely.geometry import LineString, Point
from transit_simulation.agent import MockAgent, create_agent
from pathlib import Path

EUREF_FIN_TM35_FIN_EPSG  = 'EPSG:102139'
ETRS89_TM35_FIN_EPSG  = 'EPSG:3067'
UTM_ZONE_35N = 'EPSG:32635'
WGS84 = 'EPSG:4326'
GEOM_PROCESSING_CRS = UTM_ZONE_35N

def kmph_to_mps(speed_kms: float):
    """Helper function, given km/h, retun m/s"""
    speed_ms = speed_kms / 3.6
    return speed_ms

def second_to_hour(time_s: float):
    """Helper function, given seconds, return hours"""
    time_h = time_s / 60 / 60
    return time_h



def next_location_along_route(current_location: Point, route: LineString, distance: float) -> Point:
    """Calculate where the `next_location` is when travelling `distance` along `route` from `location`
    Geometry object assumed to be shapley geometries"""

    current_distance = route.project(current_location)
    next_distance = current_distance + distance
    next_location = route.interpolate(next_distance)

    return next_location


def agents_to_gdf(agents:List) -> gpd.GeoDataFrame:
    """Given a list of agents, writes the simulation status (agent states, etc) to `filename`
    The output file is a geo data files from a GeoDataFrame"""
    points = [agent.location for agent in agents]
    snapshot = gpd.GeoDataFrame(geometry = points, crs=GEOM_PROCESSING_CRS)
    return snapshot

def bake_datasets(data_dir: str):
    pass

def start_simulation(data_dir: str, start_time:float, end_time:float, tick_len:float):
    """simulation entry point, handel all simulation functions"""

    # create the output directory, if it doesn't exist yet
    Path(data_dir, 'output').mkdir(parents=True, exist_ok=True)

    logger.debug('reading simulation environment')
    environment = {
        'speed_limit': gpd.read_file(f'{data_dir}/env_speed_limit.geojson').to_crs(GEOM_PROCESSING_CRS)
    }

    # shall be a file with linestirng geometry, each line has uinque id attribute
    # may be used for both generic agetns, and public transport
    # if routes get big, use geopackage instead. But this is convenient for debugging
    logger.debug('reading agent route geometries')
    routes = gpd.read_file(f'{data_dir}/routes.geojson').to_crs(GEOM_PROCESSING_CRS)
    logger.debug(routes.columns)

    # table of timestamps (iso8601 sting, or seconds since an epoch)
    logger.debug('reading agent schedule')
    schedule_df = gpd.pd.read_csv(f'{data_dir}/schedule.csv')


    agents = []          # the list of agents currently in the simulation
    sim_time = start_time         # timulation time, seconds since an epoch
    last_snapshot = 0   # we don't make snapshots on every tick
    logger.debug('starting simulation')
    while sim_time < end_time:
        # check the schelude of new agents and add them to the simulation
        departures = schedule_df[(sim_time <= schedule_df.start_time) & (schedule_df.start_time < sim_time + tick_len)]
        logger.debug(f'simulation time: {sim_time}')
        logger.debug(f'new departures: {len(departures)}')

        for idx, departure in departures.iterrows():
            logger.debug(departure.route_id)
            logger.debug(routes.route_id)
            new_agent = create_agent(
                route = routes[routes.route_id == departure.route_id].geometry.iloc[0 ],
                type = departure.type
            )
            agents.append(new_agent)

        # handle tick and destruction of all currnet agents
        for idx, agent in enumerate(agents):
            agent.tick(tick_len)

            if agent.done:
                del agents[idx]

        # There are agents, and more than 60 seconds since last snapshot

        if (len(agents) != 0) & ((sim_time - last_snapshot) >= 60):
            logger.debug(f'writing snapshot: sim_time: {sim_time}')
            last_snapshot = sim_time
            snapshot = agents_to_gdf(agents)
            snapshot['timestamp'] = sim_time
            # RID:JK: this file preprojection + write is slow.
            snapshot = snapshot.to_crs(WGS84)
            snapshot.to_file(f'{data_dir}/output/snapshot_{sim_time}.geojson', driver="GeoJSON")

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
