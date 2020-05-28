import uuid
from pathlib import Path

from shapely.geometry import Point
from shapely.geometry import LineString, Point

from loguru import logger
import transit_simulation.read_speed_limit_at_location as read_speed
import transit_simulation.congestion_model as congestion


def create_agent(route:LineString, agent_type:int, data_dir:Path=None) -> object:
    """returns an initialized agent object given route geometry, and the
    agetn type from the schdule file"""
    assert isinstance(agent_type, int)
    assert isinstance(route, LineString)
    # agent type numbers based on HSL GTFS route types
    if (agent_type == 0) | (700 <= agent_type < 800):
        return Bus(route, data_dir)
    if agent_type == -1:
        return MockAgent(route)
        
    logger.debug(f"unknown agent_type, using MockAgent. agent_type: {agent_type}")
    return MockAgent(route)


class Bus:
    """
    Describes the Bus object in the simulation
    """
    def __init__(self,route:LineString, data_dir):
        self.id = uuid.uuid4()
        self.route = route
        self.data_dir = Path(data_dir)
        self.location = self.origin()
        self.speed, self.road_elements = Bus.check_agent_speed_limit(self.location, self.data_dir)
        self.done = False

    def origin(self):
        start = self.route.coords[0]
        return Point(start[0], start[1])

    def tick(self, tick_len, time_of_day=8):
        self.speed, self.road_elements = Bus.check_agent_speed_limit(self.location, self.data_dir)
        speed = self.check_agent_congested_speed(self.speed, self.road_elements, time_of_day)
        distance = speed / 3.6 * tick_len # change km per h to meters per second
        next_location = Bus.calculate_next_location_along_route(self.location, self.route, distance)
        if self.location.equals(next_location):
            self.done = True
        self.location = next_location


    def calculate_next_location_along_route(current_location:Point, route:LineString, distance:float):
        """Calculate where the `next_location` is when travelling `distance` along `route` from `location`
        Geometry object assumed to be shapley geometries"""
        current_distance = route.project(current_location)
        next_distance = current_distance + distance
        next_location = route.interpolate(next_distance)
        return next_location

    def check_agent_speed_limit(current_location:Point, data_dir:Path):
        speed_data_path = data_dir / "speed_limits.geojson"
        max_speed, el = read_speed.check_speed_limit_at_location(speed_data_path, current_location)
        return max_speed, el

    def check_agent_congested_speed(self, speed, road_elements, time_of_day):
        '''time_of_day: Hours elapsed since midnight'''
        congested_speed = congestion.congested_speed(speed, time_of_day, road_elements)

        return congested_speed


class MockAgent():
    """A fake agent used in the higher level simulation logic development.
    A place holder until actual agents are implemented"""

    def __init__(self, route:LineString):
        super(MockAgent, self).__init__()
        assert isinstance(route, LineString)
        self.route = route
        self.done = False
        self.type = 'mock'
        self.location = Point(route.coords[0])

    def tick(self,tick_len):

        speed = 10 # meters per second
        distance = speed * tick_len
        self.location = MockAgent.calculate_next_location_along_route(self.location, self.route, distance)

    def calculate_next_location_along_route(current_location, route, distance):
        """Calculate where the `next_location` is when travelling `distance` along `route` from `location`
        Geometry object assumed to be shapley geometries"""
        current_distance = route.project(current_location)
        next_distance = current_distance + distance
        next_location = route.interpolate(next_distance)
        return next_location
