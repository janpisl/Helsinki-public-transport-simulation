"""Console script for transit_simulation."""
import argparse
import sys

import transit_simulation as ts

def main():
    """Console script for transit_simulation."""
    parser = argparse.ArgumentParser()
    parser.add_argument('_', nargs='*')
    args = parser.parse_args()

    print("Arguments: " + str(args._))
    print("Replace this message by putting your code into "
          "transit_simulation.cli.main")

    ts.simulate()

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
