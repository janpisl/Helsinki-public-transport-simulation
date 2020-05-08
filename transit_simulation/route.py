import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString
import requests
from io import BytesIO
from zipfile import ZipFile

def fetch_route_rt(bus_route_id, direction, d_date, d_time):
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

def fetch_HSL_gtfs_shapes():
    '''Returns:
    shape_df: A Pandas dataframe containing the information from the shapes.txt
        file of a GTFS package.
    '''
    url = 'http://dev.hsl.fi/gtfs/hsl.zip'
    
    r = requests.get(url)
    gtfs_zip = ZipFile(BytesIO(r.content))
    shape_df = pd.read_csv(gtfs_zip.open('shapes.txt'))
    
    return shape_df

def process_gtfs_shapes(shapes_data):
    '''Args:
    shapes_data: A pandas DataFrame containing data of shapes.txt in a gtfs package.
        Practically route ids and points along the route.
    
    Returns:
    routes: A GeoPandas GeoDataFrame containing unique route ids and the corresponding
        route LineString as geometry.
    '''
    geodata = gpd.GeoDataFrame(shapes_data, geometry=gpd.points_from_xy(shapes_data.shape_pt_lat, shapes_data.shape_pt_lon))
    routes = geodata.groupby(['shape_id'])['geometry'].apply(lambda x: LineString(x.tolist()))
    return routes


if __name__ == "__main__":
    def experiment_rt():
        route_id = 1071
        direction = 1
        d_date = "2020-04-29"
        d_time = 16800

        pointlist = fetch_route(route_id, direction, d_date, d_time)
        print(pointlist)
    
    def experiment_gtfs():
        shapes = fetch_HSL_gtfs_shapes()
        print('Contents of the shapes.txt:')
        print(shapes.head())
        routes = process_gtfs_shapes(shapes)
        print('Processed route data:')
        print(routes.head())
    
    experiment_gtfs()
