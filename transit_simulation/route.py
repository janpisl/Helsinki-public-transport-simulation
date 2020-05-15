import requests

def fetch_route(bus_route_id, direction, d_date, d_time):
    '''
    Args:
        bus_route_id - identifier of a route
        direction - Direction of the trip, possible values: 0, 1 or -1. -1 indicates that the direction is irrelevant, i.e. in case the route has trips only in one direction.
        date - Departure date of the trip, format: YYYY-MM-DD
        time - Departure time of the trip, format: seconds since midnight of the departure date
    
    Returns:
        route - A list of points describing the shape of the route.
    '''
    api_url = 'https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql'
    query = '''
    {{
        route: fuzzyTrip(route: "HSL:{}", direction: {}, date: "{}", time: {}) {{
            geometry
        }}
    }}
    '''.format(bus_route_id, direction, d_date, d_time)
    request = requests.post(api_url, json={'query': query})
    route = request.json()['data']['route']['geometry']
    
    return route

if __name__ == "__main__":
    route_id = 1071
    direction = 1
    d_date = "2020-04-29"
    d_time = 16800
    
    pointlist = fetch_route(route_id, direction, d_date, d_time)
