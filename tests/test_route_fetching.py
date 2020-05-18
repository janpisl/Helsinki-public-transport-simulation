import transit_simulation.route as route

'''
# Uncomment this only if you have updated d_date and d_time
def test_fetch_route():
    route_id = 1071
    direction = 1
    d_date = "2020-04-29"
    d_time = 16800

    pointlist = route.fetch_route(route_id, direction, d_date, d_time)
    print(pointlist)
'''

'''
# Uncomment this (and comment next) if you want to test only route shape processing
def test_gtfs_shapes():
    print('Loading current GTFS data from HSL')
    shapes = route.fetch_HSL_gtfs_shapes()
    print('Contents of the shapes.txt:')
    print(shapes.head())
    routes = route.process_gtfs_shapes(shapes)
    print('Processed route data:')
    print(routes.head())
'''
    
def test_gtfs_processing():
    print('Fetching data')
    shapes, trips, calendar, routes_df = route.fetch_HSL_gtfs_data()
    print('Contents of the shapes.txt:')
    print(shapes.head())
    routes = route.process_gtfs_shapes(shapes)
    print('Processed route data:')
    print(routes.head())
    schedule = route.process_gtfs_schedule(trips, calendar, routes_df)
    print('Processed schedule data:')
    print(schedule.head())
