"""
This file houses the image manager.

Image Types:
    sci     - science image
    bkg     - background image
    wht     - weight image
    var     - variance image
    rms     - root mean square image
    unc     - uncertainty image
"""

from ._imports import *

##  ============================================================================

header  = {
}

##  ============================================================================

class image:
    """
    This class is used to house FITS images.
    """

    def __init__( self, file_name, ext=0, mode="readonly", init=False ):

        self.file_name  = file_name     ##  file name
        self.ext        = ext           ##  extension

        self.fits       = None          ##  fits image object
        self.data       = None          ##  image array (tuple if multi==True)
        self.header     = None          ##  header dict (tuple if multi==True)

        self.telescope  = None          ##  telescope
        self.instrument = None          ##  instrument
        self.filter     = None          ##  filter
        self.author     = None          ##  author
        self.type       = None          ##  sci, wht, var, unc, rms, bkg
        self.frame      = None          ##  1, 2, 3, ..., N
        self.ext        = None          ##  extension index

        self.date       = None          ##  date [day-month-year]
        self.time       = None          ##  time [hour:min:sec]
        self.julian     = None          ##  julian time

        self.wcs        = None          ##  astropy.wcs.WCS object
        self.shape      = None          ##  array shape
        self.x_c        = None          ##  center pixel x
        self.y_c        = None          ##  center pixel y
        self.alpha_c    = None          ##  center pixel ra
        self.delta_c    = None          ##  center pixel dec
        self.theta      = None          ##  orientation in radians

        self.pix_scale  = None          ##  pixel scale
        self.seeing     = None          ##  seeing resolution
        self.exp_time   = None          ##  exposure time [s]
        self.gain       = None          ##  gain [e-/adu]
        self.mag_0      = None          ##  magnitude zeropoint (AB)
        self.mag_0_err  = None          ##  magnitude zeropoint error

        ##  Initialize.

        if init is False:
            self.open( file_name, ext=ext, mode=mode )
        elif init is True:
            self.init( file_name )

    ##  ========================================================================

    def open( self, file_name, ext=0, mode="readonly" ):
        """
        Instantiates the object from a FITS file or FITS cube.
        """

        ##  Get data and header.

        self.file_name      = file_name
        self.ext            = ext

        self.fits       = fits.open( file_name, mode=mode )
        self.data       = self.fits[ext].data
        self.header     = self.fits[ext].header

        ##  Get metadata from the header.

        self.telescope  = self.header["telescope"]
        self.instrument = self.header["instrument"]
        self.filter     = self.header["filter"]
        self.author     = self.header["author"]
        self.type       = self.header["type"]
        self.frame      = self.header["frame"]

        self.date       = self.header["date"]
        self.time       = self.header["time"]

        self.wcs        = WCS( self.header )
        self.shape      = np.shape( self.data )
        self.x_c        = self.wcs.to_header()["CRPIX1"]
        self.y_c        = self.wcs.to_header()["CRPIX2"]
        self.alpha_c    = self.wcs.to_header()["CRVAL1"]
        self.delta_c    = self.wcs.to_header()["CRVAL2"]
        self.theta      = None

        self.pix_scale  = self.header["pix_scale"]
        self.seeing     = self.header["seeing"]
        self.exp_time   = self.header["exp_time"]
        self.gain       = self.header["gain"]
        self.mag_0      = self.header["mag_0"]
        self.mag_0_err  = self.header["mag_0_err"]

    ##  ========================================================================

    def save( self, file_name=None, overwrite=False ):
        """
        Write fits file using the extension.
        """

        ##  Create the HDU.

        primary_hdu = fits.PrimaryHDU( self.data )

        for key in self.header:
            if key.lower() == "extname":
                continue
            try:
                primary_hdu.header.set(
                    key, self.header[key], self.header.comments[ key ]
                )
            except:
                print( "    ...could not add %s to header." % key )

        hdu_list    = fits.HDUList( [primary_hdu] )

        ##  Write to a FITS file.

        if file_name is None:
            file_name = self.file_name

        hdu_list.writeto( file_name, overwrite=False )
        self.open( file_name )

    ##  ========================================================================

    def init( self, file_name=None, overwrite=False ):
        """
        This initializes a fits image.
        """

        ##  Manage file name.

        if file_name is None:
            file_name = "temporary.fits"

        ##  Initialize the FITS HDU.

        primary_hdu = fits.PrimaryHDU( np.zeros(10,10) )
        for key in header:
            primary_hdu.header.set( key, header )
        hdu_list    = fits.HDUList( [primary_hdu] )

        ##  Save the FITS file.

        hdu_list.writeto( fits_file, overwrite=overwrite )

    ##  ========================================================================

    def display( self ):

        longest = 0
        for key in self.__dict__:
            if len( key ) > longest:
                longest = len( key )

        for key in self.__dict__:
            if key == "data" or key == "header" or key=="wcs":
                continue
            print( key, " "*(longest + 3 - len(key)), self.__dict__[key] )

##  ============================================================================
##  ============================================================================

def cube( file_name, type=None ):
    """
    This function puts FITS cubes into a list of photo.image objects.
    """

    images  = []

    for i in range( len(fits.open(file_name)) ):

        im  = photo.image(file_name, i)

        if type is not None:
            if im.type == type:
                images.append( im )
            else:
                continue
        else:
            images.append( im )

    return  images

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

def find_frames( fits_file, alpha, delta ):
    """
    For a list of coordinates (deg), return a list of the best frame in
    which the coordinates are closest to the center.

    Arguments:
        cube    - a list of image objects
        alpha   - sky coordinate 1
        delta   - sky coordinate 2

    Returns:
        frames  - list of best frames
    """

    ##  Open the fits cube.

    images  = cube( fits_file )

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
