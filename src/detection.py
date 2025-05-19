import numpy as np
from skimage.filters import threshold_otsu, gaussian
from skimage.measure import label, regionprops
from skimage.morphology import remove_small_objects
# for fits bintable
from astropy.io import fits
import numpy as np

# This is actually a very simple source extraction algorithm, it's based on percentile and sci-kit image tools. Needs improvement but it works fine.
#TODO: consider using DAOStarFinder

def detect_stars(image:np.ndarray, blur_sigma=1.0, min_area=20) -> np.ndarray:
    """
    Detect stars in a grayscale image.
    
    Returns a list of (x, y) coordinates for detected stars.
    """
    # Smooth image to reduce noise
    smoothed = gaussian(image, sigma=blur_sigma)

    # Automatically compute a threshold using np percentile method
    thresh = np.percentile(smoothed, 99.92)
    binary = smoothed > thresh

    # Remove tiny noisy spots
    cleaned = remove_small_objects(binary, min_size=min_area)

    # Label connected components
    labeled = label(cleaned)

    # Get star centroids
    stars = []
    brightness = []

    for region in regionprops(labeled, intensity_image=image):
        if region.area < min_area:
            continue  
        y, x = region.centroid
        # print(f"Star at ({x:.1f}, {y:.1f}), area: {region.area}")
        stars.append((x, y))  # Note: (x, y) order
        brightness.append(region.mean_intensity * region.area)

    # Adding fake stars at the corners to give the correct image size to the solver. 
    h, w = image.shape[:2]
    corner_coords = [
        (0, 0),
        (w - 1, 0),
        (0, h - 1),
        (w - 1, h - 1),
    ]

    for coord in corner_coords:
        stars.append(coord)
        brightness.append(1e9)

    stars = np.array(stars)
    brightness = np.array(brightness) 


    return np.concatenate([np.array(stars), brightness[:,np.newaxis]],axis=1)

def TakeBestKStars(K:int, stars:np.ndarray):
    starsortedindices = np.argsort(stars[:,2])[::-1][:K]
    return stars[starsortedindices]
