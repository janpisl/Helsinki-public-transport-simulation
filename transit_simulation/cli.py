"""Console script for transit_simulation."""
import argparse
import sys

from loguru import logger
import transit_simulation.simulation


def main():
    """Console script for transit_simulation."""
    parser = argparse.ArgumentParser()

    parser.add_argument('data_dir', help="input directory for data files", type=str)
    parser.add_argument('--start_time', default = 0,        help="time stamp for start (seconds since epoch)", type=float)
    parser.add_argument('--end_time',   default = 24*60*60, help="simulation termination time (seconds since epoch)", type=float)
    parser.add_argument('--tick_len',   default = 10,       help="simulaiton tick length (seconds)", type=float)
    args = parser.parse_args()


    logger.info('starting simulation')
    return_value = transit_simulation.simulation.start_simulation(
        data_dir = args.data_dir,
        start_time = args.start_time,
        end_time = args.end_time,
        tick_len = args.tick_len
        )
    logger.info(f'sumulation comleted: {return_value}')

    return return_value


if __name__ == "__main__":

    sys.exit(main())  # pragma: no cover
