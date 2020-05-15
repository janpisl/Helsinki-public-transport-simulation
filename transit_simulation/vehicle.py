import uuid

class Vehicle:
    """
    Base class for vehicle agents
    """
    def __init__(self,route):
        self.id = uuid.uuid4()
        self.current_location = self.origin(route)
        self.route = route

    def origin(self, route):
    """This will just be a one-liner
    """

    def tick(self):
        self.current_location = move()

    def move(self):
        raise NotImplementedError()
    


class Bus(Vehicle):
    def __init__(self, route):
        super().__init__(route)

class Car(Vehicle):
    def __init__(self, route):
        super().__init__(route)
    