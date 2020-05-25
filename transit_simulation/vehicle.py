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
        self.speed = self.check_agent_speed_limit()

    def origin(self):
        start = self.route.coords[0]
        return Point(start[0], start[1])

    def tick(self):
        self.current_location = move()

    def move(self):
        raise NotImplementedError()

    def check_agent_speed_limit(self):
        speed_data_path = Path("./tests/test_data/speed_data_digi")
        max_speed, _ = read_speed.check_speed_limit_at_location(speed_data_path / "test_speed_data.geojson", self.current_location)
        return max_speed
        
    def check_agent_congested_speed(self, time_of_day):
        '''time_of_day: Hours elapsed since midnight'''
        speed_data_path = Path("./tests/test_data/speed_data_digi")
        speed_limit, n_road_elements = read_speed.check_speed_limit_at_location(speed_data_path / "test_speed_data.geojson", self.current_location)
        congested_speed = congestion.congested_speed(speed_limit, time_of_day, n_road_elements)
        
        return congested_speed

    