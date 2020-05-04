import uuid

class Vehicle:
    """
    Base class for vehicle agents
    """
    def __init__(self, origin, destination):
        self.id = uuid.uuid4()
        self.current_location = origin
        self.route = self.find_route(origin, destination)

    def tick(self):
        self.current_location = move()

    def move(self):
        raise NotImplementedError()
    
    def find_route(self, origin, destination):
        raise NotImplementedError()


class Bus(Vehicle):
    def __init__(self, origin, destination):
        super().__init__(origin, destination)

class Car(Vehicle):
    def __init__(self, origin, destination):
        super().__init__(origin, destination)
    