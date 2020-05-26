import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString
import requests
from io import BytesIO
from zipfile import ZipFile
from pathlib import Path

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

def fetch_HSL_gtfs_data():
    '''Returns:
    shape_df: A Pandas dataframe containing the information from the shapes.txt
        file of a GTFS package.
    trips_df: A Pandas dataframe containing the information from the trips.txt
        file of a GTFS package.
    calendar_df: A Pandas dataframe containing the information from the calendar.txt
        file of a GTFS package.
    route_df: A Pandas dataframe containing the information from the routes.txt
        file of a GTFS package.
    
    '''
    url = 'http://dev.hsl.fi/gtfs/hsl.zip'
    
    r = requests.get(url)
    gtfs_zip = ZipFile(BytesIO(r.content))
    shape_df = pd.read_csv(gtfs_zip.open('shapes.txt'))
    trips_df = pd.read_csv(gtfs_zip.open('trips.txt'))
    calendar_df = pd.read_csv(gtfs_zip.open('calendar.txt'))
    route_df = pd.read_csv(gtfs_zip.open('routes.txt'))
    
    return shape_df, trips_df, calendar_df, route_df

def process_gtfs_shapes(shapes_data):
    '''Args:
    shapes_data: A pandas DataFrame containing data of shapes.txt in a gtfs package.
        Practically route ids and points along the route.
    
    Returns:

    routes: A GeoPandas GeoDataFrame containing unique shape ids and the corresponding

        route LineString as geometry.
    '''
    geodata = gpd.GeoDataFrame(shapes_data, geometry=gpd.points_from_xy(shapes_data.shape_pt_lon, shapes_data.shape_pt_lat))
    routes = geodata.groupby(['shape_id'])['geometry'].apply(lambda x: LineString(x.tolist()))
    return routes

def process_gtfs_schedule(trips_df, calendar_df, route_df, simulation_date=pd.to_datetime('today')):
    '''Args:
    trips_df: A Pandas dataframe containing the information from the trips.txt
        file of a GTFS package.
    calendar_df: A Pandas dataframe containing the information from the calendar.txt
        file of a GTFS package.
    route_df: A Pandas dataframe containing the information from the routes.txt
        file of a GTFS package.
    simulation_date: A datetime object defining from which date to fetch the schedule data.
        
    Returns:
    schedule: Pandas dataframe containing shape ids, vehicle departure times and vehicle types
        for agent initalization.'''
    df = trips_df.set_index('service_id').join(calendar_df.set_index('service_id'))
    df.start_date = pd.to_datetime(df.start_date, format='%Y%m%d'); df.end_date = pd.to_datetime(df.end_date, format='%Y%m%d')
    df.loc[df.monday==1, 'weekday'] = 0; df.loc[df.tuesday==1, 'weekday'] = 1; df.loc[df.wednesday==1, 'weekday'] = 2; df.loc[df.thursday==1, 'weekday'] = 3; df.loc[df.friday==1, 'weekday'] = 4; df.loc[df.saturday==1, 'weekday'] = 5; df.loc[df.sunday==1, 'weekday'] = 6
    df = df[(df.weekday==simulation_date.weekday()) & (df.start_date<=simulation_date) & (df.end_date>=simulation_date)]
    
    df['d_time'] = df.trip_id.str[-4:]
    df['d_time'] = pd.to_datetime(df['d_time'], errors='coerce', format='%H%M').dt.time
    
    df = pd.merge(df, route_df[['route_id', 'route_type']], on='route_id', how='left')
    schedule = df.reset_index().loc[:,['shape_id', 'd_time', 'route_type']]
    
    return schedule.dropna()
	
def create_initialization_data(simulation_date=pd.to_datetime('today')):
	'''Args:
    simulation_date: Pandas datetime object defining the date for which the simulation will be run.
    
    Returns:
	route_df: A GeoPandas GeoDataFrame containing unique shape ids and the corresponding
        route LineString as geometry.
    schedule_df: Pandas dataframe containing shape ids, vehicle departure times and vehicle types
        for agent initalization.'''
	shape_df, trips_df, calendar_df, route_df = fetch_HSL_gtfs_data()
	route_df = process_gtfs_shapes(shape_df)
	schedule_df = process_gtfs_schedule(trips_df, calendar_df, route_df, simulation_date=simulation_date)
	
	return route_df, schedule_df


def initialize_random_routes(sample_nr=20, simulation_date=pd.to_datetime('today')): # if the sample_nr is less or equal to 0, all samples are used
    print('Fetching data')
    shapes_df, trips_df, calendar_df, route_df = fetch_HSL_gtfs_data()
    print('Processing data')
    routes = process_gtfs_shapes(shapes_df)

    # read simulation extent from geojson
    data_path = Path("./tests/test_data")
    simulation_extent = gpd.read_file(data_path / 'simulation_extent.geojson')

    # create data frame with routes transformed to metric crs
    geo_routes = gpd.GeoDataFrame(routes, geometry=routes.values, crs='EPSG:4326').to_crs(simulation_extent.crs)

    # clip routes with simulation extent
    routes_clip = gpd.clip(geo_routes, simulation_extent, keep_geom_type=True)

    # select sample_nr of samples in simulation extent
    # if the number of samples is not valid, then all elements are used
    if sample_nr <= 0:
        sample_routes = routes_clip
    else:
        sample_routes = routes_clip.sample(sample_nr)

    # check for MultiLineStrings that are the result of cutting off part of the route by extent polygon
    multilines = sample_routes.loc[sample_routes['geometry'].geom_type.values == 'MultiLineString']
    if multilines.shape[0] > 0:
        # drop multilinestrings from the main table for further processing
        sample_routes = sample_routes.drop(multilines.index)

        multiline_indexes = multilines.index.to_list()

        multiline_geometry = multilines.geometry.values

        # initialize placeholders for new linestrings
        new_indexes =[]
        new_geometry = []

        # split multilinestrings into linestrings
        for i in range(len(multiline_geometry)):
            multi = multiline_geometry[i]
            multicoords = [list(line.coords) for line in multi]
            for j, sublist in enumerate(multicoords):
                new_linestring = LineString(sublist)
                # use only linestrings longer than 1000m
                if new_linestring.length > 1000:
                    new_indexes.append(multiline_indexes[i] + '_' + str(j))
                    new_geometry.append(new_linestring)


        if new_indexes and new_geometry:
            new_linestrings =  gpd.GeoDataFrame(gpd.GeoSeries(new_geometry, new_indexes, crs=sample_routes.crs))
            new_linestrings = new_linestrings.rename(columns={0:'geometry'}).set_geometry('geometry')
            sample_routes = pd.concat([sample_routes, new_linestrings])

        # write generated routes to file
        # output_path = str(data_path / 'random_routes2.geojson')
        # sample_routes.to_file(output_path, driver="GeoJSON")
        
        schedule = process_gtfs_schedule(trips_df, calendar_df, route_df, simulation_date)
        shape_ids = sample_routes.index
        sample_schedule = schedule[schedule.shape_id.isin(shape_ids)]

    return sample_routes, sample_schedule

def initdata_to_files(routes, schedule):
    data_path = Path("./tests/test_data")
    schedule = schedule.set_index('shape_id')

    routes.to_file(str(data_path / 'routes.geojson'), driver="GeoJSON")
    schedule.to_csv(str(data_path / 'schedule.csv'))
    return True
    
def preprocess_initdata_to_files(sample_nr=20, simulation_date=pd.to_datetime('today')):
    data_path = Path("./tests/test_data")
    routes, schedule = initialize_random_routes(sample_nr, simulation_date)
    schedule = schedule.set_index('shape_id')

    routes.to_file(str(data_path / 'routes.geojson'), driver="GeoJSON")
    schedule.to_csv(str(data_path / 'schedule.csv'))
    return True

if __name__ == "__main__":
    def experiment_rt():
        route_id = 1071
        direction = 1
        d_date = "2020-04-29"
        d_time = 16800

        pointlist = fetch_route(route_id, direction, d_date, d_time)
        print(pointlist)
    
    def experiment_gtfs():
        print('Fetching data')
        shapes_df, trips_df, calendar_df, routes_df = fetch_HSL_gtfs_data()
        print('Contents of the shapes.txt:')
        print(shapes_df.head())
        routes = process_gtfs_shapes(shapes_df)
        print('Processed route data:')
        print(routes.head())
        schedule = process_gtfs_schedule(trips_df, calendar_df, routes_df)
        print('Processed schedule data:')
        print(schedule.head())
    
    random_df = initialize_random_routes(60)
    experiment_gtfs()
