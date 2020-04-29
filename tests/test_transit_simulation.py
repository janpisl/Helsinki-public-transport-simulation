#!/usr/bin/env python

"""Tests for `transit_simulation` package."""

import pytest

import geopandas as gpd
from transit_simulation import simulation as ts
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
    assert ts.next_location_along_route(Point(0,300), route, 50) == Point(50,300)
    # current location is on the route, but not on a route node
    assert ts.next_location_along_route(Point(10,300), route, 50) == Point(60,300)
    assert ts.next_location_along_route(Point(2,300), route, 50) == Point(52,300)
    # current location is not at all on the route, it is snapped to the route
    # before determining the next location
    assert ts.next_location_along_route(Point(10,303), route, 50) == Point(60,300)
    # due to float inaccuracies, can't use `==` comparison. doing point-in-polygon check insead
    assert Point(50.5,300).buffer(0.0000001).contains(ts.next_location_along_route(Point(0,300), route, 50.5))

def test_second_to_hour():
    assert ts.second_to_hour(3600) == 1

def test_kmh_to_ms():
    assert ts.kmph_to_mps(3.6) == 1

def test_calculate_travel_time():

    # read the test route shapefile from the test data directory
    route = gpd.read_file('tests/test_data/test_route_1/test_route_1.shp')

    # there is one route in the dataset (one polyline).
    assert len(route) == 1

    # the test route is about 4.5 km. The unit should be meters
    assert 4000 < route['geometry'].length.sum() < 5000

    travel_time = ts.calculate_travel_time(route)
    time_h = ts.second_to_hour(travel_time)

    # travel 4.5 km at 40 km/h takes about 0.11 hours
    assert 0.10 < time_h < 0.12
