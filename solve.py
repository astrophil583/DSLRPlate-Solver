import json
import argparse
from pathlib import Path
from types import SimpleNamespace
from src.utility import queryForObject,coordConversion, load_image, SaveToFITSwcs
from src.detection import detect_stars, TakeBestKStars
from astropy.coordinates import SkyCoord
import astropy.units as u
import astrometry


def main(args):
    coords = []
    if not args.blind:
        if (args.ra is None or args.dec is None) and args.target is None:
            print(f"You must enter at least one between:")
            print("- RA/DEC Guess coordinates")
            print("- Target string (Simbad lookup)")
            print("- blind (-b) flag")
            return
        if args.target is not None:
            coords = queryForObject(args.target)
            coords = coords.ra.deg, coords.dec.deg
        if (args.ra is not None and args.dec is not None):
            coords = coordConversion(args.ra, args.dec)
    for file in args.input:

        input_path = Path(file)

        image, imagergb = load_image(file, args.green)

        stars = detect_stars(image)

        stars = TakeBestKStars(54,stars) #50 + 4 in the corners

        solver = astrometry.Solver(
            astrometry.series_5200.index_files(
                cache_directory="astrometry_cache",
                scales={6},
            )
            # + astrometry.series_4100.index_files(
            #     cache_directory="astrometry_cache",
            #     scales={7,8,9,10,11,12},
            # )
        )
        if args.blind is False:
            o_ph = astrometry.PositionHint(
                                    ra_deg=coords[0],
                                    dec_deg=coords[1],
                                    radius_deg=args.radius,
                                )
        else:
            o_ph = None
        solution = solver.solve(
                                stars=stars,
                                size_hint=None,
                                position_hint=o_ph,
                                solution_parameters=astrometry.SolutionParameters(),
        )
        if solution.has_match():
            center = SkyCoord(ra=solution.best_match().center_ra_deg, dec=solution.best_match().center_dec_deg, unit=(u.deg, u.deg))
            
        if args.json:
            if solution.has_match():
                result = {
                    "success": True,
                    "center": {
                        "ra_deg": center.ra.deg,
                        "ra_hms": center.ra.to_string(unit=u.hour, sep=':', precision=1),
                        "dec_deg": center.dec.deg,
                        "dec_dms": center.dec.to_string(unit=u.degree, sep=':', precision=1),
                    },
                    "pixel_scale_arcsecpx": solution.best_match().scale_arcsec_per_pixel
                }
            else:
                result = {
                    "success": False,
                    "error": "Solution not found"
                }
            print(json.dumps(result, indent=4))
        else:
            if solution.has_match():
                print("A solution has been found!")
                print(f"Center RA   {center.ra.to_string(unit=u.hour, sep=':', precision=1)}")
                print(f"Center DEC  {center.dec.to_string(unit=u.degree, sep=':', precision=1)}")
                print(f"Pixel Scale {solution.best_match().scale_arcsec_per_pixel:.3f}\"/px")
            else: 
                print("A solution can't be found :( ")
        if args.output is True:
            output_path = input_path.with_name(f"{input_path.stem}_solved.fits")
        elif isinstance(args.output, str):
            output_path = Path(args.output)

        if args.output and solution.has_match():
            if args.outputrgb is False:
                SaveToFITSwcs(image,output_path,solution.best_match().astropy_wcs())
            else:
                SaveToFITSwcs(imagergb,output_path,solution.best_match().astropy_wcs(), True)

        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Quick Astrometric DSLR Image Solver")

    parser.add_argument("input",nargs='+', help="Input image file")
    parser.add_argument("-ra", "--ra", help="Right Ascension Guess (eg.12h26m36s)", required=False)
    parser.add_argument("-dec", "--dec", help="Declination Guess (e.g 12d48m53s)", required=False)
    parser.add_argument("-t", "--target", help="Use target hint (Simbad lookup)")
    parser.add_argument("-b", "--blind", action="store_true", help="Use blind solving (no RA/DEC hints)")
    parser.add_argument("-r", "--radius", default=2.0 ,help="Search radius [deg]", required=False)
    parser.add_argument("-j", "--json", action="store_true", help="Outputs json data")
    parser.add_argument("-o", "--output",  nargs='?',const=True, help="Outputs a mono WCS fits", required=False)
    parser.add_argument("-orgb", "--outputrgb", action="store_true", help="Oututs an RGB WCS fits", required=False)
    parser.add_argument("-g", "--green", action="store_true", help="Work with the green channel")



    args = parser.parse_args()
    main(args)

    # To use it as a library
    def solve(input, ra, dec, target, r, blind = False):
        args_o = SimpleNamespace(
        input=input,
        ra=ra,
        dec=dec,
        blind=blind,
        target = target,
        radius = r
        )
        main(args_o)