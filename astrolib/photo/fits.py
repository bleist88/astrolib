
from ._imports import *

##  ========================================================================  ##

def find_best_frame( fits_file, alpha, delta ):
    """
    This function returns the frame number for which the "alpha" and "delta"
    provided are closest to the center.

    Returns:
        frame:              int32       - best frame

    Parameters:
        fits_list:          [string]    -   images to search through
        alpha:              float       -   sky coordinate 1
        delta:              float       -   sky coordinate 2
    """

    ##  Open a fits cube of image objects.

    images  = photo.cube( fits_file, type="sci" )

    ##  For each photo.image, create an array of distances between.

    distances   = np.zeros( (len(alpha), len(images)) )
    im_frames   = [ im.frame for im in images ]

    for i in range( len(images) ):
        distances[:,i]  = np.sqrt(
            (alpha - images[i].alpha_c)**2 + (delta - images[i].delta_c)**2
        )

    ##  Create frames array.

    frames = np.zeros( len(alpha), dtype="int32" )

    for i in range( frames.size ):

        io.progress( i, frames.size, alert="Finding best frames." )

        frames[i]   = im_frames[
            int( np.where( distances[i] == np.min(distances[i]) )[0] )
        ]

    return  frames

    # ##  Create a dictionary of distances to the center.
    #
    # frame       = None
    # distance    = None
    #
    # ##  Iterate through the cube extensions.  Look through only "sci" types.
    # ##  Retrieve the center pixel value and find the distance to the given.
    #
    # for i in range( len(fits_cube) ):
    #
    #     if fits_cube[i].header["type"] != "sci":
    #         continue
    #
    #     alpha_c = fits_cube[i].header["CRVAL1"]
    #     delta_c = fits_cube[i].header["CRVAL2"]
    #
    #     D   = np.sqrt( (alpha - alpha_c)**2 + (delta - delta_c)**2 )
    #
    #     if frame is None:
    #         frame       = fits_cube[i].header["frame"]
    #         distance    = D
    #     elif D < distance:
    #         frame       = fits_cube[i].header["frame"]
    #         distance    = D
    #
    # return  frame

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

##  ============================================================================

##  This was previously used in the find_fits() function which is now the
##  find_best_frame() function.

## Iterate through list of images and store candidate images in which the
## pixel value located at the given sky position is a reasonable value.
#
# for i in range(len( fits_list )):
#
#     ## Get image data and wcs info.
#
#     data        = fits.getdata( fits_list[i] )
#     header      = fits.getheader( fits_list[i] )
#     image_wcs   = WCS( header )
#
#     ## Find pixel location of sky position.
#     print(alpha, delta)
#     position    = np.array([[ alpha, delta ]])
#
#     x           = image_wcs.wcs_world2pix( position, 1 )[0][1]
#     y           = image_wcs.wcs_world2pix( position, 1 )[0][0]
#
#     ## Determine the validity of the pixel location and value.
#     ## The location of the pixel must be within the shape of the image.
#     ## The value of the pixel must not be zero or nan.
#
#     if x > 0 and y > 0 and x < data.shape[0] and y < data.shape[1]:
#
#         if data[ x,y ] != 0.0 and not np.isnan( data[ x,y ] ):
#
#             ## Calculate the separation between the sky position pixel and
#             ## the image center pixel.  If no image had been previously
#             ## stored, record this info.  If a previous image had been
#             ## recorded but this new separation is better, record this info.
#
#             sep =  ( data.shape[0]/2 - x )**2 + ( data.shape[1]/2 - x )**2
#
#             if image is None:
#
#                 image       = fits_list[i]
#                 image_sep   = sep
#
#             elif image is not None and sep < image_sep:
#
#                 image       = fits_list[i]
#                 image_sep   = sep
#
# return image
