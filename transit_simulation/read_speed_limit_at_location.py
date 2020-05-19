import sys

import geopandas
import numpy
from shapely.geometry import Point


def check_speed_limit_at_location(speed_input_file, location, buffer_size=50):
	"""
	Checks the speed limit at a given location.

	Parameters:
	speed_input_file: path to road network file with speed attribute
	location: point coordinates in a list
	buffer_size: buffer size (default value 50m)

	Returns:
	int: speed limit
    int: number of digiroad geometry elements within the buffer
	"""

	# create buffer around location
	point_geometry = Point(location[0], location[1])
	point_buffer = point_geometry.buffer(buffer_size)

	# read data inside the buffer
	speed_limit_dataframe = geopandas.read_file(filename=speed_input_file, bbox=point_buffer)

	# create geopandas.geoseries from point geometry
	point_geoseries = geopandas.GeoSeries([point_geometry])

	# calculate distances between roads and point
	distances_to_point = [point_geoseries.distance(line).values[0] for line in speed_limit_dataframe.geometry]
	# add new column for distances
	speed_limit_dataframe['Distance'] = distances_to_point
	# create dataframe without geometry to find column minimum
	selected_columns = speed_limit_dataframe[['ARVO', 'Distance']].copy()
	# find row index where distance is the smallest
	shortest_distance_idx = selected_columns.idxmin(axis=0, skipna=True)['Distance']
	# read the speed limit value
	speed_limit_at_location = speed_limit_dataframe.at[shortest_distance_idx,'ARVO']
    
    # find the number of digiroad elements within the buffer
    n_elements = speed_limit_dataframe.shape[0]

	return speed_limit_at_location, n_elements


if __name__ == "__main__":
	example_location = [385306.0644, 6671652.982]
	speed_limit = check_speed_limit_at_location(sys.argv[1], example_location)
