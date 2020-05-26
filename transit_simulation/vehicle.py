import uuid
from pathlib import Path

from shapely.geometry import Point

import transit_simulation.read_speed_limit_at_location as read_speed
import transit_simulation.congestion_model as congestion


class Bus:
    """
    Describes the Bus object in the simulation
    """
    def __init__(self,route):
        self.id = uuid.uuid4()
        self.route = route
        self.current_location = self.origin()
        self.speed, self.road_elements = self.check_agent_speed_limit()
        self.done = False

    def origin(self):
        start = self.route.coords[0]
        return Point(start[0], start[1])

    def tick(self, tick_len, time_of_day=8):
        self.speed, self.road_elements = self.check_agent_speed_limit()
        speed = self.check_agent_congested_speed(self.speed, self.road_elements, time_of_day)
        distance = speed / 3.6 * tick_len # change km per h to meters per second
        next_location = self.calculate_next_location_along_route(distance)
        if self.current_location.equals(next_location):
            self.done = True
        self.current_location = next_location


    def calculate_next_location_along_route(self, distance):
        """Calculate where the `next_location` is when travelling `distance` along `route` from `location`
        Geometry object assumed to be shapley geometries"""
        current_distance = self.route.project(self.current_location)
        next_distance = current_distance + distance
        next_location = self.route.interpolate(next_distance)
        return next_location

    def check_agent_speed_limit(self):
        speed_data_path = Path("./tests/test_data/speed_data_digi")
        max_speed, el = read_speed.check_speed_limit_at_location(speed_data_path / "keha_speed_data.geojson", self.current_location)
        return max_speed, el
        
    def check_agent_congested_speed(self, speed, road_elements, time_of_day):
        '''time_of_day: Hours elapsed since midnight'''
        congested_speed = congestion.congested_speed(speed, time_of_day, road_elements)
        
        return congested_speed

