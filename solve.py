import argparse
from src.utility import queryForObject,coordConversion, load_cr2_image
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

    image = load_cr2_image(args.input)

    stars = detect_stars(image)

    stars = TakeBestKStars(50,stars)

    with astrometry.Solver(
    astrometry.series_5200.index_files(
        cache_directory="astrometry_cache",
        scales={6},
    )) as solver:
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
            print("A solution has been found!")
            print(f"Center RA   {center.ra.to_string(unit=u.hour, sep=':', precision=1)}")
            print(f"Center DEC  {center.dec.to_string(unit=u.degree, sep=':', precision=1)}")
            print(f"Pixel Scale {solution.best_match().scale_arcsec_per_pixel:.3f}\"/px")
        else: 
            print("A solution can't be found :( ")

    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Quick Astrometric DSLR Image Solver")

    parser.add_argument("input", help="Input image file")
    parser.add_argument("-ra", "--ra", help="Right Ascension Guess (eg.12h26m36s)", required=False)
    parser.add_argument("-dec", "--dec", help="Declination Guess (e.g 12d48m53s)", required=False)
    parser.add_argument("-t", "--target", help="Use target hint (Simbad lookup)")
    parser.add_argument("-b", "--blind", action="store_true", help="Use blind solving (no RA/DEC hints)")
    parser.add_argument("-r", "--radius", default=2.0 ,help="Search radius [deg]", required=False)

    args = parser.parse_args()
    main(args)