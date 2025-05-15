from astropy.io import fits
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
from astroquery.simbad import Simbad
import rawpy

def load_cr2_image(filepath):
    with rawpy.imread(filepath) as raw:
        rgb = raw.postprocess(
            use_camera_wb=True,     # or False if you want raw sensor WB
            #no_auto_bright=True,
            #output_bps=16,
            #output_color=rawpy.ColorSpace.raw,
            user_flip=0             # <- disables orientation flip/rotation
        )
        gray = np.mean(rgb, axis=2) 
        # gray = np.fliplr(gray)
    return gray

def SaveToFITS(image, dest):
    # This can be called directly after load_cr2_image
    # Convert to float32 or float64 to avoid overflow
    gray_fits = image.astype(np.float32)

    # Create primary HDU (Header/Data Unit)
    hdu = fits.PrimaryHDU(gray_fits)
    hdul = fits.HDUList([hdu])

    # Save to file
    hdul.writeto(dest, overwrite=True)

def coordConversion(raHMS, decDMS):
    # imput example "12h26m36s", "12d48m53s"
    coord = SkyCoord(ra=raHMS, dec=decDMS, unit=(u.hourangle, u.deg))
    return [coord.ra.deg, coord.dec.deg]
    
def queryForObject(name:str):
    try:
        result = Simbad.query_object(name)
        ra_str = result["RA"][0]        # e.g. '13 29 52.698'
        dec_str = result["DEC"][0]      # e.g. '+47 11 42.93'
        coords = SkyCoord(f"{ra_str} {dec_str}", unit=(u.hourangle, u.deg))
    except:
        coords = SkyCoord.from_name(name)

    return coords
