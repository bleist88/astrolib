"""
This file houses the image manager.
"""

from ._imports import *

##  ============================================================================

class image:

    def __init__( self, file_name, **params ):

        self.file_name  = file_name     ##  file name (.im extension)

        self.telescope  = None          ##  telescope
        self.instrument = None          ##  instrument
        self.filter     = None          ##  filter
        self.author     = None          ##  author

        self.date       = None          ##  date [day-month-year]
        self.time       = None          ##  time [hour:min:sec]
        self.julian     = None          ##  julian time
        self.comments   = []            ##  comments

        self.data       = None          ##  image array (tuple if multi==True)
        self.header     = None          ##  header dict (tuple if multi==True)
        self.multi      = False         ##  does it consist of mult. images?
        self.type       = None          ##  image type

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
        self.flux_unit  = None          ##  flux unit of data array
        self.mag_0      = None          ##  magnitude zeropoint (AB)
        self.mag_0_err  = None          ##  magnitude zeropoint error

        ##  Open file if one already exists.

        if os.path.isfile( file_name ):
            self.open( file_name )

        ##  Take any kwargs from **params.

        for key in params:
            if key in self.__dict__:
                self.__dict__[key]  = params[key]

    ##  ========================================================================

    def save( self, saveas=None, overwrite=False ):
        """
        Saves the object into a .npz file.
        """

        ##  File options.

        if saveas is None:
            saveas = self.file_name

        if overwrite is False and os.path.isfile( saveas ):
            raise   Exception( "%s already exists." % saveas )

        ##  Write all members to a dictionary.

        members     = {}

        for key in self.__dict__:
            members[ key ]  = self.__dict__[ key ]

        ##  Special Conditions:
        ##  1.  wcs can't be serialized
        ##  2.  header must be stored as a string

        members["wcs"]      = None
        members["header"]   = str( members["header"] )

        ##  Serialize to a file.

        np.savez( saveas, **members )
        os.rename( saveas + ".npz", saveas )

    def open( self, file_name ):
        """
        Instantiates the object from a .npz file.
        """

        members = np.load( file_name )

        for key in members:
            self.__dict__[ key ]    = members[ key ]

        ##  Special Conditions:
        ##  1.  wcs can't be serialized
        ##  2.  header must be stored as a string

        self.header     = str( self.header )

        try:
            self.wcs    = WCS( self.header )
        except:
            print("Couldn't create image.wcs from header.")
            self.wcs    = None

    def from_fits( self, fits_file, **params ):
        """
        Instantiates the object from a FITS file.
        """

        self.data       = fits.getdata( fits_file )
        self.header     = str( fits.getheader( fits_file ) )
        self.wcs        = WCS( self.header )

        for key in params:
            if key in self.__dict__:
                self.__dict__[key]  = params[key]
