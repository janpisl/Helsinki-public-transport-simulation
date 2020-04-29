import paho.mqtt.client as mqtt
import pdb
import time
import json
from geopy import distance
from loguru import logger

# Vehicles should publish info every 1 sec; if set to 1 sec only, some msgs are missing
WAIT_FOR_MESSAGES = 1.5

def on_connect(client, userdata, flags, rc):
    '''
    The callback for when the client receives a CONNACK response from the server.
    Subsribe to the desired topic upon connecting or raise an exception.
    '''
    if rc == 0:
        logger.debug("Connected successfully")
        bus_route_id = userdata['inputs']['bus_route_id']
        direction = userdata['inputs']['direction']

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("/hfp/v2/journey/ongoing/vp/bus/+/+/{}/{}/#".format(bus_route_id, direction))
    else:
        raise Exception("Failed to connect. Result code "+str(rc))


def on_message(client, userdata, msg):
    '''
    The callback for when a PUBLISH message is received from the server.
    Store vehicle information in a dictionary; If information already exists
    for given vehicle, overwrite with latest info
    '''
    message = json.loads(msg.payload.decode("utf-8"))
    vehicle = message['VP']['veh']
    userdata['messages'][vehicle] = message


def get_bus_info(bus_route_id, direction):
    '''
    Args:
        bus_route_id - identifier of a route
        direction - either 1 or 2
    
    Subscribe to a topic and collect infomation for vehicles
    on a given route in a given direction
    
    Returns:
        userdata['messages'] - dictionary of all buses satisfying conditions
    '''
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    userdata = {
        "inputs" :
            {
            "bus_route_id" : bus_route_id,
            "direction" : direction
        },
        "messages" : 
            {}
    }
    client.user_data_set(userdata)
    client.connect("mqtt.hsl.fi")
    client.loop_start()
    time.sleep(WAIT_FOR_MESSAGES)
    client.loop_stop()

    return userdata['messages']


def nearest_bus(bus_route_id, direction, station):
    '''
    Args:
        bus_route_id - identifier of a route
        direction - either 1 or 2
        station - tuple of coordinates (lat,lon)
    
    Find the nearest bus to a given point

    Returns:
        nearest_bus - vehicle number of the closest bus
        min_distance - geodetic distance in km

    '''

    all_buses = get_bus_info(bus_route_id, direction)
    min_distance = float('inf')
    nearest_bus = None
    for k, v in all_buses.items():
        bus_location = (v['VP']['lat'], v['VP']['long'])
        dist = distance.distance(bus_location, station)
        if dist < min_distance:
            min_distance = dist
            nearest_bus = k
    
    return nearest_bus, min_distance


if __name__ == "__main__":
    nearest_bus, min_distance = nearest_bus(1071,1,(60.17,24.94))
    logger.debug('Nearest vehicle n. {}. Distance {}'.format(nearest_bus, min_distance))
