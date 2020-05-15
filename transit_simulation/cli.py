"""Console script for transit_simulation."""
import argparse
import sys

from loguru import logger
import transit_simulation as ts


def main():
    """Console script for transit_simulation."""
    parser = argparse.ArgumentParser()

    parser.add_argument'data_dir', help="directory path for input data directory", type=str)
    parser.add_argument'start_time', type=float, default=0)
    parser.add_argument'stop_time', type=float, default=60*10)
    parser.add_argument'tick_len', type=float, default=1, help="the length of a simulation tick in seconds")
    args = parser.parse_args()


    logger.info('starting simulation')
    ts.simulation.start_simulation(
        args.data_dir, args.start_time, args.stop_time, args.tick_len
    )
    logger.info(f'sumulation comleted: {return_value}')



    return return_value


if __name__ == "__main__":

    sys.exit(main())  # pragma: no cover
