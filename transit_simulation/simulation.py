"""Main module."""

from loguru import logger
import geopandas as gpd
import numpy as np
from typing import List
from shapely.geometry import LineString, Point
from transit_simulation.vehicle import create_agent
from assert_types import assert_types

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

def time_of_day_to_seconds(timestamp:str):
    """Given a string of format 'hh:mm:ss', return the number of seconds since start of day (00:00:00)
    This format is used in the schedule.csv input data file"""
    assert isinstance(timestamp, str)
    timestamp = timestamp.split(':')
    assert len(timestamp) == 3
    timestamp = int(timestamp[0]) *60*60 + int(timestamp[1]) * 60 + int(timestamp[2])
    assert 0 <= timestamp <= 86400 # number of seconds in a day
    return timestamp

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


def start_simulation(data_dir: str, start_time:float, end_time:float, tick_len:float):
    """simulation entry point, handel all simulation functions. This function is
    called from the comandline utility"""


    # shall be a file with linestirng geometry, each line has uinque id attribute
    # may be used for both generic agetns, and public transport
    # if routes get big, use geopackage instead. But this is convenient for debugging
    logger.info('reading agent route geometries')
    routes = gpd.read_file(f'{data_dir}/routes.geojson').to_crs(GEOM_PROCESSING_CRS)
    logger.debug(routes.columns)

    # table of timestamps (iso8601 time without date) for departing agents
    logger.debug('reading agent schedule')
    schedule_df = gpd.pd.read_csv(f'{data_dir}/schedule.csv', comment='#')
    # convert time to seconds since start of day, to suit simulation
    schedule_df['d_time'] = schedule_df['d_time'].apply(time_of_day_to_seconds)

    sim_time = start_time       # timulation time, seconds since an epoch
    agents = []                 # the list of agents currently in the simulation
    snapshots = []              # for aggregating agent histories

    logger.debug('entering main simulation loop')
    while sim_time < end_time:
        # check the schelude of new agents and add them to the simulation
        departures = schedule_df[(sim_time <= schedule_df.d_time) & (schedule_df.d_time < sim_time + tick_len)]

        for idx, schd_entry in departures.iterrows():
            logger.debug(f"departing agent: {schd_entry.shape_id}, route: {routes.shape_id}")
            new_agent = create_agent(
                route = routes[routes.shape_id == schd_entry.shape_id].geometry.iloc[0 ],
                agent_type = schd_entry.route_type
            )
            agents.append(new_agent)

        # handle tick and destruction of all currnet agents
        for idx, agent in enumerate(agents):
            agent.tick(tick_len)

            if agent.done:
                del agents[idx]

        if len(agents) != 0:
            snapshot = agents_to_gdf(agents)
            snapshot['timestamp'] = sim_time
            # useful for debugging, gut creates HUGE amouns of files
            # snapshot.to_file(f'{data_dir}/snapshot_{sim_time}.gpkg', driver='GPKG')
            snapshots.append(snapshot)

        sim_time += tick_len

    logger.info("Post-processing simulation data")
    logger.info("number of snapshots: " + str(len(snapshots)))
    result = gpd.pd.concat(snapshots)
    logger.info(f'writing result data: {data_dir}/snapshots.[geojson, gpkg]')
    result.to_file(f'{data_dir}/snapshots.gpkg', driver="GPKG")
    result.to_file(f'{data_dir}/snapshots.geojson', driver="GeoJSON")


    return True
