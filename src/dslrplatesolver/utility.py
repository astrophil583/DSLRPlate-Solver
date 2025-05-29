from astropy.io import fits
from pathlib import Path
from astropy.wcs import WCS
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
from astroquery.simbad import Simbad
import rawpy
import exifread
from datetime import datetime, timedelta
import os
from fractions import Fraction


def load_image(filepath:str, green = False):
    path = Path(filepath)
    ext = path.suffix.lower()
    if ext in ['.fits', '.fit', '.fts']:  # FITS file
        with fits.open(filepath) as hdul:
            data = hdul[0].data

            # Convert to float32 just to be sure
            if data.ndim == 3 and data.shape[0] == 3:  # (3, H, W)
                rgb = np.moveaxis(data, 0, -1)
                mono = np.mean(rgb, axis=2)
                if green:
                    return rgb[:, :, 1], rgb
                return mono, rgb
            else:
                # Monochrome FITS
                mono = data.astype(np.float32)
                return mono, None
    else:
        with rawpy.imread(filepath) as raw:
            rgb = raw.postprocess(
                use_camera_wb=True,     # or False if you want raw sensor WB
                #no_auto_bright=True,
                #output_bps=16,
                #output_color=rawpy.ColorSpace.raw,
                user_flip=0             # <- disables orientation flip/rotation
            )
            mono = np.mean(rgb, axis=2) 
            if green: 
                return rgb[:,:,1], rgb
            # gray = np.fliplr(gray)
    return mono, rgb

def SaveToFITSwcs(image, dest, wcs, rgb = False, green = False, date = None, exptime = None):
    # This can be called directly after load_cr2_image
    # Convert to float32 or float64 to avoid overflow
    imagedata = image.astype(np.float32)

    # Create primary HDU (Header/Data Unit)
    hdu = fits.PrimaryHDU(imagedata,header=wcs.to_header(relax=True))
    hdul = fits.HDUList([hdu])

    if rgb:

        R, G, B = [imagedata[..., i].astype(np.float32) for i in range(3)]

        primary_hdu = fits.PrimaryHDU(R, header=wcs.to_header(relax=True))
        g_hdu = fits.ImageHDU(G, name="G")
        b_hdu = fits.ImageHDU(B, name="B")

        hdul = fits.HDUList([primary_hdu, g_hdu, b_hdu])

    if green:
        header = wcs.to_header(relax=True)
        header['FILTER'] = 'G'
        hdu = fits.PrimaryHDU(G,header=header)
        hdul = fits.HDUList([hdu])

    if date is not None:
        hdr = hdul[0].header
        iso_timestamp = date.isoformat()
        hdr['DATE-OBS'] = iso_timestamp
        hdr['COMMENT'] = "DATE-OBS added from original EXIF timestamp"
    if exptime is not None:
        hdr = hdul[0].header
        hdr['EXPTIME'] = exptime
        hdr['COMMENT'] = "EXPTIME added from original EXIF timestamp"
    # Save to file
    hdul.writeto(dest, overwrite=True)

def coordConversion(raHMS, decDMS):
    # imput example "12h26m36s", "12d48m53s"
    coord = SkyCoord(ra=raHMS, dec=decDMS, unit=(u.hourangle, u.deg))
    return [coord.ra.deg, coord.dec.deg]
    
def queryForObject(name:str) -> SkyCoord:
    try:
        result = Simbad.query_object(name)
        ra_str = result["RA"][0]        # e.g. '13 29 52.698'
        dec_str = result["DEC"][0]      # e.g. '+47 11 42.93'
        coords = SkyCoord(f"{ra_str} {dec_str}", unit=(u.hourangle, u.deg))
    except:
        coords = SkyCoord.from_name(name)

    return coords

def get_acquisition_time(image_path, deltah = -2):
    try:
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f, stop_tag="EXIF DateTimeOriginal", details=False)
            date_str = str(tags.get("EXIF DateTimeOriginal"))
            tags = exifread.process_file(f, stop_tag="EXIF ExposureTime", details=False)
            exposure = tags.get("EXIF ExposureTime")
            if date_str:
                return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S") + timedelta(hours=deltah), float(Fraction(str(exposure)))
    except Exception as e:
        print("EXIF read failed:", e)

    # Fallback to filesystem creation date
    print("Falling back to filesystem timestamp.")
    stat = os.stat(image_path)
    
    return datetime.fromtimestamp(stat.st_ctime)
