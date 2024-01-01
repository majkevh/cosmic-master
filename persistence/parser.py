import argparse
import sys
from preprocess import Preprocess
from persistence import CubicalCPH

def create_parser():
    """
    Create and return an argument parser for the script.
    """
    parser = argparse.ArgumentParser(
        description='Run Persistence Homology Analysis Simulation for Subhalo Galaxies',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('-alg', '--algorithm', type=str, choices={"CCPH", "PP"}, required=True,
                        help='Algorithm to use: "PP" or "CCPH"')
    parser.add_argument('-dt', '--dataset', type=str, choices={"TNG100-1", "TNG100-1-Dark", "TNG50-1", "TNG50-1-Dark", "TNG300-1", "TNG300-1-Dark"}, required=True,
                        help='Illustris TNG Dataset from "https://www.tng-project.org/data/"')
    parser.add_argument('-snap', '--snapshot', type=int, choices=range(100), required=True,
                        help='Redshift snapshot in range 0 to 99')
    parser.add_argument('-mass', '--masses', type=float, required=False,
                        help='Mass threshold to filter small galaxies (unit: 10e10 M*/h)')
    parser.add_argument('-crop', '--crop', type=int, choices=range(1, 101), required=True,
                        help='Portion of simulation to retain (1 to 100)')

    return parser

def main(args):
    """
    Main execution function based on the parsed arguments.
    """
    if args.algorithm == 'PP':
        sym = Preprocess(dataset=args.dataset, snapshot=args.snapshot, crop=args.crop, min_mass=args.masses)
        sym.run()
    elif args.algorithm == 'CCPH':
        sym = CubicalCPH(dataset=args.dataset, snapshot=args.snapshot, crop=args.crop)
        sym.run()

if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()

    if not args:
        parser.print_help(sys.stderr)
        sys.exit(1)

    main(args)
