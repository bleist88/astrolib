
from .__imports__   import *

##  ========================================================================  ##

def find_fits( fits_list, alpha, delta ):
    """
    Iterate through the list of FITS images and search for the sky position
    given and determine the most preferable image for that position.

    Returns:
        fits file (string)          -   best image

    Parameters:
        fits_list (list,strings)    -   images to search through
        alpha (float)               -   sky coordinate 1
        delta (float)               -   sky coordinate 2
    """

    image       = None      # Best image file name (string)
    image_sep   = None      # distance to center pixel

    ## Ensure that list is given.

    if not isinstance( fits_list, (list,tuple) ):

        lst = []
        lst.append( fits_list )

    ## Iterate through list of images and store candidate images in which the
    ## pixel value located at the given sky position is a reasonable value.

    for i in range(len( fits_list )):

        ## Get image data and wcs info.

        data        = fits.getdata( fits_list[i] )
        header      = fits.getheader( fits_list[i] )
        image_wcs   = WCS( header )

        ## Find pixel location of sky position.
        print(alpha, delta)
        position    = np.array([[ alpha, delta ]])

        x           = image_wcs.wcs_world2pix( position, 1 )[0][1]
        y           = image_wcs.wcs_world2pix( position, 1 )[0][0]

        ## Determine the validity of the pixel location and value.
        ## The location of the pixel must be within the shape of the image.
        ## The value of the pixel must not be zero or nan.

        if x > 0 and y > 0 and x < data.shape[0] and y < data.shape[1]:

            if data[ x,y ] != 0.0 and not np.isnan( data[ x,y ] ):

                ## Calculate the separation between the sky position pixel and
                ## the image center pixel.  If no image had been previously
                ## stored, record this info.  If a previous image had been
                ## recorded but this new separation is better, record this info.

                sep =  ( data.shape[0]/2 - x )**2 + ( data.shape[1]/2 - x )**2

                if image is None:

                    image       = fits_list[i]
                    image_sep   = sep

                elif image is not None and sep < image_sep:

                    image       = fits_list[i]
                    image_sep   = sep

    return image

##  ============================================================================

def rescale( data, sigma=3, epsilon=.03, iters=20 ):

    if data is None:
        return None

    ##  Iteratively remove outliers.

    while True:

        iters  -= 1
        mean0   = data.mean()
        std     = data.std()
        data    = data.clip( mean0 - sigma * std, mean0 + .5 * sigma * std )

        if (mean0 - data.mean()) / mean0 > epsilon or iters == 0:
            break

    return data
