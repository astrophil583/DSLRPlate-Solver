import argparse
from .core import _solvefunc

def main():
    parser = argparse.ArgumentParser(description="Quick Astrometric DSLR Image Solver")

    parser.add_argument("input", nargs='+', help="Input image file")
    parser.add_argument("-ra", "--ra", help="Right Ascension Guess (e.g. 12h26m36s)")
    parser.add_argument("-dec", "--dec", help="Declination Guess (e.g. 12d48m53s)")
    parser.add_argument("-t", "--target", help="Use target hint (Simbad lookup)")
    parser.add_argument("-b", "--blind", action="store_true", help="Use blind solving (no RA/DEC hints)")
    parser.add_argument("-r", "--radius", default=2.0, help="Search radius [deg]")
    parser.add_argument("-j", "--json", action="store_true", help="Outputs JSON data")
    parser.add_argument("-o", "--output", nargs='?', const=True, help="Output mono WCS FITS")
    parser.add_argument("-orgb", "--outputrgb", action="store_true", help="Output RGB WCS FITS")
    parser.add_argument("-g", "--green", action="store_true", help="Use green channel")

    args = parser.parse_args()
    _solvefunc(args, json_output=args.json)
