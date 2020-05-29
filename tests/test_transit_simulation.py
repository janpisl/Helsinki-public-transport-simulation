#!/usr/bin/env python

"""Tests for `transit_simulation` package."""

import pytest

import geopandas as gpd
import transit_simulation as ts
from shapely.geometry import LineString, Point


@pytest.fixture
def input_data():
    """Sample pytest fixture.
    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')

def test_next_location_along_route():

    route = LineString([(0, 300), (150, 300), (200, 350)])

    # current location in already on a route node
    assert ts.simulation.next_location_along_route(Point(0,300), route, 50) == Point(50,300)
    # current location is on the route, but not on a route node
    assert ts.simulation.next_location_along_route(Point(10,300), route, 50) == Point(60,300)
    assert ts.simulation.next_location_along_route(Point(2,300), route, 50) == Point(52,300)
    # current location is not at all on the route, it is snapped to the route
    # before determining the next location
    assert ts.simulation.next_location_along_route(Point(10,303), route, 50) == Point(60,300)
    # due to float inaccuracies, can't use `==` comparison. doing point-in-polygon check insead
    assert Point(50.5,300).buffer(0.0000001).contains(ts.simulation.next_location_along_route(Point(0,300), route, 50.5))

def test_second_to_hour():
    assert ts.simulation.second_to_hour(3600) == 1

def test_kmh_to_ms():
    assert ts.simulation.kmph_to_mps(3.6) == 1

def test_time_of_day_to_seconds():
    assert ts.simulation.time_of_day_to_seconds("01:00:00") == 60*60
    assert ts.simulation.time_of_day_to_seconds("10:01:01") == 10*60*60 + 60 + 1
    assert isinstance(ts.simulation.time_of_day_to_seconds("10:01:01"), int)

def test_agents_to_gdf():
    agents = [ts.vehicle.MockAgent(LineString([(0,0), (10,10)]))]
    snapshot = ts.simulation.agents_to_gdf(agents)
    assert isinstance(snapshot, gpd.GeoDataFrame)



def test_start_simulation():
    ts.simulation.start_simulation('tests/test_data/simulation_1', 0, 10, 1)
