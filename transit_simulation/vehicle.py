import uuid
from pathlib import Path

from shapely.geometry import Point

import transit_simulation.read_speed_limit_at_location as read_speed

class Vehicle:
    """
    Base class for vehicle agents
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
        max_speed = read_speed.check_speed_limit_at_location(speed_data_path / "test_speed_data.geojson", self.current_location)
        return max_speed
    


class Bus(Vehicle):
    def __init__(self, route):
        super().__init__(route)

class Car(Vehicle):
    def __init__(self, route):
        super().__init__(route)
    