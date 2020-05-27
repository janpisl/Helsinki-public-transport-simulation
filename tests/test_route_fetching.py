import transit_simulation.route as route
import vcr


#
# @vcr.use_cassette()
# def test_gtfs_processing():
#     shapes, trips, calendar, routes_df = route.fetch_HSL_gtfs_data()
#     routes = route.process_gtfs_shapes(shapes)
#     schedule = route.process_gtfs_schedule(trips, calendar, routes_df)
