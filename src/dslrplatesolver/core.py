from types import SimpleNamespace
from pathlib import Path
from .utility import queryForObject, coordConversion, load_image, SaveToFITSwcs
from .detection import detect_stars, TakeBestKStars
import astropy.units as u
from astropy.coordinates import SkyCoord
import astrometry
import json

def _solvefunc(args, json_output=False):
    coords = []

    if not args.blind:
        if (args.ra is None or args.dec is None) and args.target is None:
            raise ValueError("Missing coordinates or target for non-blind solve")
        if args.target is not None:
            coords = queryForObject(args.target)
            coords = coords.ra.deg, coords.dec.deg
        if (args.ra is not None and args.dec is not None):
            coords = coordConversion(args.ra, args.dec)

    results = []

    for file in args.input:
        input_path = Path(file)
        image, imagergb = load_image(file, args.green)
        stars = TakeBestKStars(54, detect_stars(image))

        solver = astrometry.Solver(
            astrometry.series_5200.index_files(
                cache_directory="astrometry_cache",
                scales={6},
            )
        )

        position_hint = None if args.blind else astrometry.PositionHint(
            ra_deg=coords[0],
            dec_deg=coords[1],
            radius_deg=args.radius,
        )

        solution = solver.solve(
            stars=stars,
            size_hint=None,
            position_hint=position_hint,
            solution_parameters=astrometry.SolutionParameters(),
        )

        if solution.has_match():
            center = SkyCoord(ra=solution.best_match().center_ra_deg,
                              dec=solution.best_match().center_dec_deg, unit=(u.deg, u.deg))

            if json_output:
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
                print(json.dumps(result, indent=4))
            else:
                print("A solution has been found!")
                print(f"Center RA   {center.ra.to_string(unit=u.hour, sep=':', precision=1)}")
                print(f"Center DEC  {center.dec.to_string(unit=u.degree, sep=':', precision=1)}")
                print(f"Pixel Scale {solution.best_match().scale_arcsec_per_pixel:.3f}\"/px")
        else:
            print("A solution can't be found :(")
            if json_output:
                print(json.dumps({"success": False, "error": "No match found"}))

        # Output WCS FITS if requested
        if args.output and solution.has_match():
            output_path = Path(args.output) if isinstance(args.output, str) \
                else input_path.with_name(f"{input_path.stem}_solved.fits")

            SaveToFITSwcs(
                imagergb if args.outputrgb else image,
                output_path,
                solution.best_match().astropy_wcs(),
                args.outputrgb
            )

        results.append(solution)

    return results

def solve(input, ra, dec, target, r, blind=False):
    args = SimpleNamespace(
        input=input,
        ra=ra,
        dec=dec,
        target=target,
        radius=r,
        blind=blind,
        output=False,
        outputrgb=False,
        green=False
    )
    return _solvefunc(args)
