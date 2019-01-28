"""
This file houses the image manager.
"""

from ._imports import *

##  ============================================================================

types_dict  = {
    "sci": [], "bkg": [], "wht": [], "var": [], "rms": [], "unc": []
}

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

class image:
    """
    This class is used to house FITS images.
    """

    def __init__( self, file_name, ext=None ):

        self.file_name  = file_name     ##  file name

        self.data       = None          ##  image array (tuple if multi==True)
        self.header     = None          ##  header dict (tuple if multi==True)

        self.telescope  = None          ##  telescope
        self.instrument = None          ##  instrument
        self.filter     = None          ##  filter
        self.author     = None          ##  author
        self.type       = None          ##  sci, wht, var, unc, rms, bkg
        self.frame      = None          ##  1, 2, 3, ..., N
        self.ext        = None          ##  extension index
        self.ext_name   = None          ##  extension name

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

        self.open( file_name, ext=ext )

    ##  ========================================================================

    def open( self, file_name, ext=None ):
        """
        Instantiates the object from a FITS file or FITS cube.
        """

        self.file_name      = file_name
        self.ext            = ext

        ##  Get data and header.

        if ext is None:
            self.data       = fits.getdata( file_name )
            self.header     = fits.getheader( file_name )

        elif ext is not None:
            self.data       = fits.getdata( file_name, ext )
            self.header     = fits.getheader( file_name, ext )

        ##  Get metadata from the header.

        self.telescope  = self.header["telescope"]
        self.instrument = self.header["instrument"]
        self.filter     = self.header["filter"]
        self.author     = self.header["author"]
        self.type       = self.header["type"]
        self.frame      = self.header["frame"]
        self.ext_name   = self.header["extname"]

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

    def display( self ):

        longest = 0
        for key in self.__dict__:
            if len( key ) > longest:
                longest = len( key )

        for key in self.__dict__:
            if key == "data" or key == "header" or key=="wcs":
                continue
            print( key, " "*(longest + 3 - len(key)), self.__dict__[key] )
