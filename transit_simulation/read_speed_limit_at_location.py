import sys

import geopandas
import numpy
from shapely.geometry import Point


def check_speed_limit_at_location(speed_input_file, agent_location, buffer_size=100):
	"""
	Checks the speed limit at a given location.

	Parameters:
	speed_input_file: path to road network file with speed attribute
	location: shapely geometry as Point with agent's current location
	buffer_size: buffer size (default value 50m)

	Returns:
	int: speed limit
    int: number of digiroad geometry elements within the buffer
	"""

	# create buffer around location
	point_buffer = agent_location.buffer(buffer_size)

	# read data inside the buffer
	speed_limit_dataframe = geopandas.read_file(filename=speed_input_file, bbox=point_buffer)
	if speed_limit_dataframe.empty:
		# this is to make sure that function returns something even if there is no digiroads in point buffer
		# default values are arbitrary
		return 40, 2

	# find the number of digiroad elements within the buffer
	n_elements = speed_limit_dataframe.shape[0]

	# create geopandas.geoseries from point geometry
	point_geoseries = geopandas.GeoSeries([agent_location])

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
	if numpy.isnan(speed_limit_at_location):
		# not all roads in digiroad dataset have speed limit value
		# in that case default speed limit is returned
		return 40, n_elements

	return speed_limit_at_location, n_elements


if __name__ == "__main__":
	example_location = [385306.0644, 6671652.982]
	agent_location = Point(example_location[0], example_location[1])
	speed_limit = check_speed_limit_at_location(sys.argv[1], agent_location)
