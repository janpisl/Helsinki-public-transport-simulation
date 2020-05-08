
from loguru import logger

from shapely.geometry import LineString, Point
import transit_simulation.simulation as sim


def create_agent(route:LineString, type:str) -> object:
    assert isinstance(type, str)
    assert isinstance(route, LineString)
    if type == 'mock':
        return MockAgent(route)

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
        self.location = sim.next_location_along_route(self.location, self.route, distance)
