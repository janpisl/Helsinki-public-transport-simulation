from flask import Flask
app = Flask(__name__)

import transit_simulation as ts

@app.route('/')
def heartbeat():
    return "transit simulation API endpoint is running"


# app.route determines what the URL of the
@app.route('/predict_arrival/<route_id>/<station_id>')
def API_start_simulation(route_id, station_id):
    """Simulation API endpoint. Gven a route id and station id, predicts the
    arrival time of the next bus at the station"""
    # TODO: this is not yet an actually useful simulation
    result = dict()
    result['total_travel_time'] = ts.simulation.start_simulation('tests/test_data/test_route_1/test_route_1.geojson')
    result['route_id'] = route_id
    result['station_id'] = station_id
    return result
