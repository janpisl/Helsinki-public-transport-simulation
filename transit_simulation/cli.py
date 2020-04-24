"""Console script for transit_simulation."""
import argparse
import sys

from loguru import logger
import transit_simulation as ts

def main():
    """Console script for transit_simulation."""
    parser = argparse.ArgumentParser()

    parser.add_argument('route_file', description="input file for route", type=str)
    args = parser.parse_args()


    logger.info('starting simulation')
    return_value = ts.simulate(arg.route_file)
    logger.info(f'sumulation comleted: {return_value}')

    return return_value


if __name__ == "__main__":

    sys.exit(main())  # pragma: no cover
